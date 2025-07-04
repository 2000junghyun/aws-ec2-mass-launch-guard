# Access Key Hander for Abnormal EC2 Creation

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
- Function name: `EC2AbnormalCreation_AccessKeyHandler`
- Runtime: Python 3.9
- Architecture: x86_64
- Create function

<br>

### Lambda Function Permission Settings

**Path:** Configuration → Permissions → Select the role under Role name → Add permissions

Attach the following policy named `EC2AbnormalCreation-IAM-Policy`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "VisualEditor0",
      "Effect": "Allow",
      "Action": [
        "iam:UpdateAccessKey",
        "iam:ListAccessKeys"
      ],
      "Resource": "*"
    }
  ]
}

```

<br>

## Results
### CloudWatch Log

<img width="385" alt="image7" src="https://github.com/user-attachments/assets/6c6a435b-f94b-4434-9735-6a17d2a6b716" />


- Successfully received information from `AbnormalEC2Creation_Detector`
- Executed Access Key deactivation

<br>

### IAM User Policy

<img width="1230" alt="image8" src="https://github.com/user-attachments/assets/d066c426-ff26-4ed9-9767-aa5632b25769" />


- Confirmed Access Key has been deactivated

<br>

## Expected Benefits

- Immediately disables compromised Access Keys used in attacks to prevent further abuse
- Quickly blocks abnormal API calls to minimize system damage
- Reduces operator response time through automated incident handling
