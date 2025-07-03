# EC2 Handler for Abnormal Creation

<br>

## Problem Statement

| **Cost Explosion** | Creating a large number of EC2 instances can result in hundreds to thousands of dollars in charges within a single day. |
| --- | --- |
| **Detection and Response Delay** | Even if abnormal activity is detected, resources may already be running or charges may have been incurred. |
| **Secondary Attacks via Infrastructure** | The created instances can be used for scanning external systems, DDoS attacks, cryptocurrency mining, and more. |

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
