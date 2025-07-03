import boto3
import json
import os
import datetime

# AWS 클라이언트 초기화
ec2_client = boto3.client('ec2')

def lambda_handler(event, context):
    try:
        # CloudWatch 경보 이벤트 파싱
        # 경보는 SNS를 통해 JSON 문자열을 전송
        sns_message = json.loads(event['Records'][0]['Sns']['Message'])
        alarm_name = sns_message.get('AlarmName', 'N/A')
        new_state_value = sns_message.get('NewStateValue', 'N/A')
        reason = sns_message.get('NewStateReason', 'N/A')

        print(f"Alarm '{alarm_name}' changed to {new_state_value}. Reason: {reason}")

        # 최근 생성된 인스턴스를 찾아 중지/종료
        terminated_ids = handle_ec2_instances()

        print(f"Terminated instances: {terminated_ids if terminated_ids else 'None'}")

    except Exception as e:
        print(f"An error occurred in Lambda execution: {e}")

    return {
        'statusCode': 200,
        'body': json.dumps('EC2 instance termination function executed successfully.')
    }

def handle_ec2_instances():
    terminated_ids = []
    try:
        response = ec2_client.describe_instances(
            Filters=[
                {'Name': 'instance-state-name', 'Values': ['running', 'pending']},
            ]
        )

        now_utc = datetime.datetime.now(datetime.timezone.utc)

        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                launch_time = instance['LaunchTime']

                # 최근 15분 이내에 생성된 인스턴스 식별
                if now_utc - launch_time < datetime.timedelta(minutes=15):
                    print(f"Found recently launched instance: {instance_id} (Launch Time: {launch_time})")
                    try:
                        # 인스턴스 종료: terminate_instances 사용
                        # 인스턴스 중지: stop_instances 사용
                        ec2_client.stop_instances(InstanceIds=[instance_id])
                        terminated_ids.append(instance_id)
                        print(f"Terminated instance: {instance_id}")
                    except Exception as e:
                        print(f"Error terminating instance {instance_id}: {e}")
    except Exception as e:
        print(f"Error describing or terminating instances: {e}")
    return terminated_ids