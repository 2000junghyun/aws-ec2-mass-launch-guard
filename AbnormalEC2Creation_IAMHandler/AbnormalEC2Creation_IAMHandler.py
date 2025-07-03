import boto3
import json

iam_client = boto3.client('iam')

def lambda_handler(event, context):
    print("[*] EC2AbnormalCreation_IAMHandler invoked.")
    print(f"[+] Raw event: {json.dumps(event)}")

    user_name = event.get('userName')
    if not user_name:
        print("[!] userName not provided.")
        return {'statusCode': 400, 'body': 'userName missing.'}

    print(f"[+] Processing user: {user_name}")

    try:
        # 1. Attached (Managed) 정책 제거
        attached_policies = iam_client.list_attached_user_policies(UserName=user_name)['AttachedPolicies']
        for policy in attached_policies:
            policy_name = policy['PolicyName']
            print(f"→ Detaching managed policy: {policy_name}")
            iam_client.detach_user_policy(
                UserName=user_name,
                PolicyArn=policy['PolicyArn']
            )

        # 2. Inline 정책 제거
        inline_policies = iam_client.list_user_policies(UserName=user_name)['PolicyNames']
        for policy_name in inline_policies:
            print(f"→ Deleting inline policy: {policy_name}")
            iam_client.delete_user_policy(
                UserName=user_name,
                PolicyName=policy_name
            )

        # 3. EC2 권한 차단용 인라인 정책 삽입
        deny_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Deny",
                    "Action": [
                        "ec2:RunInstances",
                        "ec2:StartInstances",
                        "ec2:RebootInstances",
                        "ec2:CreateTags"
                    ],
                    "Resource": "*"
                }
            ]
        }

        print(f"→ Applying EC2 deny inline policy to {user_name}")
        iam_client.put_user_policy(
            UserName=user_name,
            PolicyName="DenyEC2Permissions",
            PolicyDocument=json.dumps(deny_policy)
        )

        print("[+] EC2-related permissions removed successfully.")
        return {
            'statusCode': 200,
            'body': f'EC2 permissions removed for user {user_name}.'
        }

    except Exception as e:
        print(f"[!] Error processing IAM permissions: {e}")
        return {'statusCode': 500, 'body': 'Internal server error.'}