# EC2 Handler for Abnormal Creation

<br>

## Goal
Automatically stop or terminate EC2 instances when the number of created instances exceeds a predefined threshold.

<br>

## Solution
### Overview

1. Event occurs
2. Event recorded in CloudTrail logs
3. Logs saved in CloudWatch and metrics extracted
4. CloudWatch alarm triggered
5. SNS sends email notification
6. Lambda function executes (automated response)

<br>

### Lambda Function Creation

**Path:** Lambda → Functions → Create function

- Author from scratch
- Function name: `EC2AbnormalCreation_EC2Handler`
- Runtime: Python 3.9
- Architecture: x86_64
- Create function

<br>

### Lambda Function Permission Settings

**Path:** Configuration → Permissions → Select role under Role name → Add permissions

Attach the following policy named `EC2AbnormalCreation-EC2-Policy`:

```json
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

<br>

### Lambda Function SNS Integration

**Path:** Lambda → Functions → Select function → Function overview → Add trigger

- **Source:** SNS
- **SNS topic:** `AbnormalEC2RunInstances`
- The Lambda function is triggered when the `AbnormalEC2RunInstances` alarm is published.

<br>

## Results
### EC2 Instance
- Automatically stops recently created instances when an alarm is triggered.

![image](https://github.com/user-attachments/assets/831498fa-6432-4091-8dc7-c751e91c2900)


<br>

### CloudWatch Log
**Path:** Lambda → Functions → Select function → Monitor → View CloudWatch Logs

![image2](https://github.com/user-attachments/assets/6d7db2b4-c451-4fb1-bb83-580203abbd94)

- Successfully discovered recently created instances.
- Successfully stopped the discovered instances.

<br>

## Expected Benefits
- Automated initial incident response
- Reduced operational burden for manual intervention
- Useful for post-incident forensic analysis
