# User Detector for Abnormal EC2 Creation

<br>

## Problems
- Without **`AbnormalEC2Creation_Detector`**, SNS alerts alone are insufficient to accurately identify malicious users.
- The handler holds **broad IAM permissions**, which pose significant risks if not tightly controlled.
- Without proper detection, it may execute actions against unintended or unauthorized principals.
- This can lead to **privilege misuse** and potential **security breaches**.

<br>

## Solution
### Overview
1. Event is triggered
2. Event is logged in **CloudTrail**
3. Logs are saved in **CloudWatch Logs**, and metrics are extracted
4. **CloudWatch Alarm** is triggered
5. **SNS** sends an email notification
6. Lambda function is executed

<br>

### Create Lambda Function
**Path:** Lambda → Functions → Create function
- **Author from scratch**
- **Function name:** `EC2AbnormalCreation_Detector`
- **Runtime:** Python 3.9
- **Architecture:** x86_64
- Click **Create function**

<br>

### Set Lambda Permissions
**Path:** Configuration → Permissions → Click the role under "Role name" → Add permissions
`EC2AbnormalCreation-CloudWatch-Policy`
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "VisualEditor0",
      "Effect": "Allow",
      "Action": [
        "logs:DescribeLogStreams",
        "logs:GetLogEvents",
        "logs:FilterLogEvents"
      ],
      "Resource": "arn:aws:logs:<REGION>:<AWS-ID>:log-group:<CloudTrail log group name>:*"
    }
  ]
}
```

<br>

`EC2AbnormalCreation-Lambda-Policy`
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "VisualEditor0",
      "Effect": "Allow",
      "Action": "lambda:InvokeFunction",
      "Resource": [
        "arn:aws:lambda:<REGION>:<AWS-ID>:function:EC2AbnormalCreation_IAMHandler",
        "arn:aws:lambda:<REGION>:<AWS-ID>:function:EC2AbnormalCreation_AccessKeyHandler"
      ]
    }
  ]
}
```

<br>

### Set Lambda Environment Variables
**Path:** Configuration → Environment variables → Edit → Add environment variable
| **Key** | **Value** |
| --- | --- |
| `CLOUDTRAIL_LOG_GROUP_NAME` | Name of the CloudTrail log group |
| `IAM_HANDLER_LAMBDA_NAME` | `EC2AbnormalCreation_IAMHandler` |
| `ACCESS_KEY_HANDLER_LAMBDA_NAME` | `EC2AbnormalCreation_AccessKeyHandler` |

<br>

### Integrate Lambda with SNS
**Path:** Lambda → Functions → Select the function → Function overview → Add trigger
- **Source:** SNS
- **SNS Topic:** `AbnormalEC2RunInstances`
- The Lambda function is triggered when an alarm is published to the `AbnormalEC2RunInstances` topic.

<br>

## Results
### CloudWatch Log
<img width="766" alt="image3" src="https://github.com/user-attachments/assets/a3bee786-db93-4615-8d82-2bd1207d7bc3" />
Extracted information:

- `accessKeyID`
- `userArn`
- `userName`

<br>

## Expected Benefits
- Enables rapid response by accurately identifying malicious users and unauthorized entities
- Significantly reduces security risks by preventing misuse of overly broad IAM permissions
- Effectively lowers the likelihood of security incidents through detection and automated remediation

<br>

## Troubleshooting

### CloudWatch Log Insight

- Verify that the query runs correctly:

```sql
fields @timestamp, userIdentity.arn as userArn, userIdentity.userName as userName, userIdentity.accessKeyId as accessKeyID
| filter eventName = 'RunInstances'
| sort @timestamp desc
| limit 10
```
<img width="1683" alt="image4" src="https://github.com/user-attachments/assets/8a2a761a-8b38-40a8-b30a-23052202a80b" />


<br>

### Verify with Extended Time Range for Log Retrieval

```python
# First attempt: Query logs from 12 hours before until alarm time
end_time_ms = int(alarm_time.timestamp() * 1000)
start_time_ms = int((alarm_time - timedelta(hours=12)).timestamp() * 1000)

# Second attempt: Query logs from 5 minutes before until alarm time
end_time_ms = int(alarm_time.timestamp() * 1000)
start_time_ms = int((alarm_time - timedelta(minutes=5)).timestamp() * 1000)
```
