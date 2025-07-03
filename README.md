# aws-ec2-mass-launch-guard

<br>

## Incident Response Flow for Abnormal EC2 Instance Creation

**[1] CloudWatch Alarm (RunInstancesCount)**

- Condition: Detect N or more `RunInstances` API calls within 5 minutes
- Status: Switches to **ALARM**

<br>

↓ (Alarm triggers notification)

<br>

**[2] SNS Topic: `EC2AbnormalCreationAlert`**

- **Subscriber 1 → Lambda: `AbnormalEC2Creation_EC2Handler`**
    - Queries recently created instances (`boto3: describe_instances`)
    - Stops or terminates instances if conditions met (`boto3: stop_instances` / `terminate_instances`)
    - *Action:* Stop/terminate EC2 instances
- **Subscriber 2 → Lambda: `AbnormalEC2Creation_Detector` (Orchestrator)**
    - Analyzes CloudTrail logs (`lookup_events` / `filter_log_events`)
    - Identifies abnormal users and compromised Access Keys
    - Calls downstream security control Lambda functions

<br>

↓ (Called by orchestrator Lambda)

<br>

**[3] Response Action Branching**

- **Lambda: `EC2AbnormalCreation_IAMHandler`**
    - Applies Deny policies to the user (`boto3: iam.put_user_policy`)
    - *Action:* Restrict IAM permissions
- **Lambda: `EC2AbnormalCreation_AccessKeyHandler`**
    - Deactivates compromised Access Keys (`boto3: iam.update_access_key`)
    - *Action:* Disable leaked Access Keys
