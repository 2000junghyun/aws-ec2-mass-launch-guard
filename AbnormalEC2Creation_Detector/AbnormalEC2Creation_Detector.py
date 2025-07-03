import json
import boto3
import os
import time
from datetime import datetime, timedelta, timezone
from dateutil import parser

# AWS 클라이언트 초기화
logs_client = boto3.client('logs')
lambda_client = boto3.client('lambda')
sts_client = boto3.client('sts')

# 환경 변수
CLOUDTRAIL_LOG_GROUP_NAME = os.environ.get('CLOUDTRAIL_LOG_GROUP_NAME')
IAM_HANDLER_LAMBDA_NAME = os.environ.get('IAM_HANDLER_LAMBDA_NAME')
ACCESS_KEY_HANDLER_LAMBDA_NAME = os.environ.get('ACCESS_KEY_HANDLER_LAMBDA_NAME')

# 계정 ID 조회 (userArn 생성 시 사용)
ACCOUNT_ID = sts_client.get_caller_identity().get('Account')


def lambda_handler(event, context):
    print(f"Received event: {json.dumps(event)}")

    try:
        # SNS 메시지 파싱
        sns_message = json.loads(event['Records'][0]['Sns']['Message'])
        alarm_time = parser.isoparse(sns_message['StateChangeTime'])

        # 로그 조회 시간 범위 (5분 전 ~ 알람 시간)
        end_time_ms = int(alarm_time.timestamp() * 1000)
        start_time_ms = int((alarm_time - timedelta(minutes=5)).timestamp() * 1000)

        print(f"Alarm at {alarm_time.isoformat()}")
        print(f"Query window: {datetime.fromtimestamp(start_time_ms / 1000, tz=timezone.utc)} ~ {datetime.fromtimestamp(end_time_ms / 1000, tz=timezone.utc)}")

    except Exception as e:
        print(f"[!] Error parsing SNS message: {e}")
        return {'statusCode': 400, 'body': json.dumps('Invalid SNS message.')}

    # Logs Insights 쿼리
    query_string = """
        fields @timestamp, userIdentity.arn as userArn, userIdentity.userName as userName, userIdentity.accessKeyId as accessKeyID
        | filter eventName = 'RunInstances'
        | sort @timestamp desc
        | limit 10
    """

    try:
        query_id = logs_client.start_query(
            logGroupName=CLOUDTRAIL_LOG_GROUP_NAME,
            startTime=start_time_ms,
            endTime=end_time_ms,
            queryString=query_string
        )['queryId']
        print(f"Started query: {query_id}")

        # 최대 30초 대기
        response = None
        wait_time = 0
        while (response is None or response['status'] in ['Running', 'Scheduled']) and wait_time < 30:
            time.sleep(1)
            wait_time += 1
            response = logs_client.get_query_results(queryId=query_id)

        print(f"Query status: {response['status']}")

        if response['status'] != 'Complete':
            raise Exception("Logs query did not complete in time.")

        # 사용자 정보 파싱
        users = set()
        for result in response['results']:
            user = {}
            for field in result:
                if field['field'] == 'userArn' and field['value']:
                    user['userArn'] = field['value']
                elif field['field'] == 'userName' and field['value']:
                    user['userName'] = field['value']
                elif field['field'] == 'accessKeyID' and field['value']:
                    user['accessKeyId'] = field['value']

            # userArn 보완 생성 (없을 경우)
            if 'userArn' not in user and 'userName' in user:
                user['userArn'] = f"arn:aws:iam::{ACCOUNT_ID}:user/{user['userName']}"

            if user:
                users.add(json.dumps(user, sort_keys=True))

        if not users:
            print("[+] No suspicious users found.")
            return {'statusCode': 200, 'body': json.dumps('No suspicious users found.')}

        print(f"[+] Found users: {users}")

        # 대응 Lambda 호출
        for user_str in users:
            user_data = json.loads(user_str)

            if IAM_HANDLER_LAMBDA_NAME:
                try:
                    print(f"→ Calling IAM Handler: {user_data['userArn']}")
                    lambda_client.invoke(
                        FunctionName=IAM_HANDLER_LAMBDA_NAME,
                        InvocationType='Event',
                        Payload=json.dumps(user_data).encode('utf-8')
                    )
                except Exception as e:
                    print(f"[!] IAM handler error for {user_data.get('userArn', 'Unknown')}: {e}")

            if ACCESS_KEY_HANDLER_LAMBDA_NAME and 'accessKeyId' in user_data:
                try:
                    print(f"→ Calling AccessKey Handler: {user_data['accessKeyId']}")
                    lambda_client.invoke(
                        FunctionName=ACCESS_KEY_HANDLER_LAMBDA_NAME,
                        InvocationType='Event',
                        Payload=json.dumps(user_data).encode('utf-8')
                    )
                except Exception as e:
                    print(f"[!] AccessKey handler error for {user_data.get('accessKeyId', 'Unknown')}: {e}")

    except Exception as e:
        print(f"[!] Error during query or function invoke: {e}")
        return {'statusCode': 500, 'body': json.dumps('Internal server error.')}

    return {'statusCode': 200, 'body': json.dumps('Detection complete. Actions invoked.')}