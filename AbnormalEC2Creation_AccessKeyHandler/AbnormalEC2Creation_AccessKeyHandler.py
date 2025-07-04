import json
import boto3

iam = boto3.client('iam')

def lambda_handler(event, context):
    print(f"[+] Received event: {json.dumps(event)}")

    access_key_id = event.get('accessKeyId')
    user_name = event.get('userName')

    if not access_key_id or not user_name:
        print("[!] Missing accessKeyId or userName in event.")
        return {'statusCode': 400, 'body': 'Missing required information.'}

    try:
        # 해당 access key 비활성화
        iam.update_access_key(
            UserName=user_name,
            AccessKeyId=access_key_id,
            Status='Inactive'
        )

        print(f"[+] Access key {access_key_id} deactivated for user {user_name}")
        return {
            'statusCode': 200,
            'body': f'Access key {access_key_id} deactivated for user {user_name}'
        }

    except iam.exceptions.NoSuchEntityException:
        print("[!] The specified user or access key does not exist.")
        return {'statusCode': 404, 'body': 'User or access key not found.'}

    except Exception as e:
        print(f"[!] Error: {e}")
        return {'statusCode': 500, 'body': 'Internal server error.'}