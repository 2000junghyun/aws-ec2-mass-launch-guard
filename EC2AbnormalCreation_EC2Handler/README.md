# EC2 Handler for Abnormal Creation

<br>

<aside>
💡 **목표:** 사전에 설정된 EC2 인스턴스 생성 임계치 초과 시 자동으로 EC2 인스턴스 중지/종료

</aside>

## Problem Statement

- **Cost Explosion**
- **Detection and Response Delay**
- **Secondary Attacks via Infrastructure**

<br>

## Solution Overview

1. Event occurs
2. Event recorded in CloudTrail logs
3. Logs saved in CloudWatch and metrics extracted
4. CloudWatch alarm triggered
5. SNS sends email notification
6. Lambda function executes (automated response)

<br>

## Lambda Function Creation

**Path:** Lambda → Functions → Create function

- Author from scratch
- Function name: `EC2AbnormalCreation_EC2Handler`
- Runtime: Python 3.9
- Architecture: x86_64
- Create function

<br>

## Lambda Function Permission Settings

**Path:** Configuration → Permissions → Select role under Role name → Add permissions

Attach the following policy named `EC2AbnormalCreation-EC2-Policy`:

```json
json
CopyEdit
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "VisualEditor0",
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "ec2:TerminateInstances",
        "ec2:StopInstances"
      ],
      "Resource": "*"
    }
  ]
}
```
