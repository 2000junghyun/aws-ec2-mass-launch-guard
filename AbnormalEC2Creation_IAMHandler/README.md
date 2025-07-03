# IAM Policy Hander for Abnormal EC2 Creation

<br>

## Problems
- Massive costs incurred in a short period due to large-scale EC2 instance creation
- High likelihood that resources are already running or charges have been incurred even after anomaly detection
- Created instances can be exploited for secondary attacks such as external system scanning, DDoS, or cryptocurrency mining

<br>

## Solution
### Create Lambda Function
**Lambda > Functions > Create function**

- Author from scratch
- Function name: `EC2AbnormalCreation_IAMHandler`
- Runtime: Python 3.9
- Architecture: x86_64
- Create function

<br>

### Lambda Function Permission Settings

**Path:** Configuration → Permissions → Select role under Role name → Add permissions

Attach the following policy named `EC2AbnormalCreation-IAM-Policy`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "VisualEditor0",
      "Effect": "Allow",
      "Action": [
        "iam:PutUserPolicy",
        "iam:ListAttachedUserPolicies",
        "iam:DeleteUserPolicy",
        "iam:AttachUserPolicy",
        "iam:ListUserPolicies",
        "iam:DetachUserPolicy"
      ],
      "Resource": "arn:aws:iam::439024478232:user/*"
    }
  ]
}

```

<br>

## Results
### CloudWatch Log

![image5](https://github.com/user-attachments/assets/60c53c06-a59b-4701-a2bd-b5bb5acb4d38)


- Successfully received information from `AbnormalEC2Creation_Detector`
- Executed IAM policy modification

<br>

### IAM user policy

<img width="1234" alt="image6" src="https://github.com/user-attachments/assets/74ebfdaf-9a89-4317-9bc6-7165eed0a3cf" />


- Removed existing EC2-related permissions
- Created explicit Deny policy
