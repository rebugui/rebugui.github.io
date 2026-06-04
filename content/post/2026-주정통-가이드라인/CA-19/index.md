---
title: "[2026 주요정보통신기반시설] CA-19 가상리소스이상징후알림설정"
slug: "2026-주정통/CA-19"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "가상 리소스 이상 징후 알림 설정 여부 점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Cloud
---

# CA-19 가상리소스이상징후알림설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | CA-19 |
| **점검내용** | 가상 리소스 이상 징후 알림 설정 여부 점검 |
| **점검대상** | 클라우드 플랫폼 |
| **판단기준** | 양호: 가상 리소스 이상 징후 알림 설정이 적용된 경우 |
| **판단기준** | 취약: 가상 리소스 이상 징후 알림 설정이 적용되지 않은 경우 |
| **조치방법** | 가상 리소스 이상 징후 알림 설정 |

---
## 상세 설명

### 1. 항목 개요

클라우드 환경에서 이상 징후 알림 설정은 보안 사고를 조기에 탐지하고 신속하게 대응하는 핵심입니다. CPU 과다 사용, 비정상적인 네트워크 트래픽, 실패한 로그인 시도, 보안 그룹 변경 등의 이상 징후를 실시간으로 감지하고 알림을 받아야 합니다.

### 2. 왜 이 항목이 필요한가요?

**보안 위협 시나리오:**
1. **암호화폐화 채굴**: CPU 사용량 급증으로 악성 프로세스 탐지
2. **DDoS 공격**: 네트워크 트래픽 급증으로 공격 탐지
3. **무차별 대입 공격**: SSH/MySQL 로그인 실패 횟수 증가
4. **데이터 유출**: 대량의 S3 다운로드 시도 감지
5. **비인가 변경**: 보안 그룹, IAM 정책 변경 탐지

**실제 사례**
- 암호화폐화 채굴 악성코드가 2주간 실행되었는데 알림이 없어 비용 5천만 원 발생
- 관리자 계정 탈취 후 데이터 유출이 3일간 지속되었는데 탐지 못함

### 3. 점검 대상

- 모든 클라우드 리소스 (EC2, RDS, S3, Lambda 등)
- CloudWatch Alarms
- AWS Config Rules
- GuardDuty
- Security Hub

### 4. 판단 기준

| 구분 | 기준 |
|------|------|
| **양호** | 주요 리소스에 대해 이상 징후 알림이 설정되어 있고, 적절한 채널로 전송되는 경우 |
| **취약** | 이상 징후 알림이 설정되지 않았거나, 알림을 받는 사람이 없는 경우 |

### 5. 점검 방법

#### Step 1: CloudWatch Alarms 확인

```bash
# AWS CLI 예시
# 모든 알람 확인
aws cloudwatch describe-alarms

# 활성화된 알람만 확인
aws cloudwatch describe-alarms \
  --state-value ALARM

# 특정 리소스의 알람 확인
aws cloudwatch describe-alarms \
  --alarm-names prefix/*

# 알람의 알림 대상 확인
aws cloudwatch describe-alarms \
  --query "MetricAlarms[].{AlarmName:AlarmName,AlarmActions:AlarmActions,OKActions:OKActions}"
```

#### Step 2: GuardDuty 활성화 확인

```bash
# GuardDuty 활성화 확인
aws guardduty get-detector --detector-id 12abc34d567e8fa901bc2d34e56789f0

# GuardDuty findings 확인
aws guardduty list-findings --detector-id detector-id
```

#### Step 3: SNS Topic 구독 확인

```bash
# SNS Topic 확인
aws sns list-topics

# Topic 구독 확인
aws sns list-subscriptions-by-topic --topic-arn arn:aws:sns:region:account-id:topic-name
```

### 6. 조치 방법

#### Step 1: CloudWatch Alarms 설정

```bash
# EC2 CPU 사용량 알람
aws cloudwatch put-metric-alarm \
  --alarm-name EC2HighCPU \
  --alarm-description "Alert when CPU exceeds 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=InstanceId,Value=i-xxxxxxxx

# 메모리 사용량 알람 (CloudWatch Agent 필요)
aws cloudwatch put-metric-alarm \
  --alarm-name EC2HighMemory \
  --alarm-description "Alert when memory usage exceeds 90%" \
  --metric-name mem_used_percent \
  --namespace CWAgent \
  --statistic Average \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 90 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=InstanceId,Value=i-xxxxxxxx

# 디스크 공간 부족 알람
aws cloudwatch put-metric-alarm \
  --alarm-name EC2LowDiskSpace \
  --alarm-description "Alert when disk usage exceeds 85%" \
  --metric-name disk_used_percent \
  --namespace CWAgent \
  --statistic Average \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 85 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=InstanceId,Value=i-xxxxxxxx,Name=MountPath,Value=/
```

#### Step 2: 네트워크 트래픽 알람

```bash
# EC2 네트워크 인바운드 알람 (DDoS 탐지)
aws cloudwatch put-metric-alarm \
  --alarm-name EC2HighInboundTraffic \
  --alarm-description "Alert on high inbound traffic (possible DDoS)" \
  --metric-name NetworkIn \
  --namespace AWS/EC2 \
  --statistic Sum \
  --period 60 \
  --evaluation-periods 3 \
  --threshold 10000000000 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=InstanceId,Value=i-xxxxxxxx

# EC2 네트워크 아웃바운드 알람 (데이터 유출 탐지)
aws cloudwatch put-metric-alarm \
  --alarm-name EC2HighOutboundTraffic \
  --alarm-description "Alert on high outbound traffic (possible data exfiltration)" \
  --metric-name NetworkOut \
  --namespace AWS/EC2 \
  --statistic Sum \
  --period 60 \
  --evaluation-periods 5 \
  --threshold 5000000000 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=InstanceId,Value=i-xxxxxxxx
```

#### Step 3: SNS Topic 및 구독 생성

```bash
# SNS Topic 생성
aws sns create-topic --name CloudWatchAlarms

# Topic ARN 저장
TOPIC_ARN="arn:aws:sns:ap-northeast-2:123456789012:CloudWatchAlarms"

# 이메일 구독 추가
aws sns subscribe \
  --topic-arn $TOPIC_ARN \
  --protocol email \
  --notification-endpoint admin@example.com

# SMS 구독 추가
aws sns subscribe \
  --topic-arn $TOPIC_ARN \
  --protocol sms \
  --notification-endpoint +821012345678

# HTTPS 구독 추가 (Slack, Webhook 등)
aws sns subscribe \
  --topic-arn $TOPIC_ARN \
  --protocol https \
  --notification-endpoint https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

#### Step 4: 알람에 SNS 연결

```bash
# 알람에 SNS Topic 연결
aws cloudwatch put-metric-alarm \
  --alarm-name EC2HighCPU \
  --alarm-description "Alert when CPU exceeds 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=InstanceId,Value=i-xxxxxxxx \
  --alarm-actions $TOPIC_ARN \
  --OK-actions $TOPIC_ARN
```

#### Step 5: GuardDuty 활성화

```bash
# GuardDuty 활성화
aws guardduty create-detector --enable

# GuardDuty SNS 알림 설정
aws guardduty create-publishing-destination \
  --detector-id detector-id \
  --destination-arn $TOPIC_ARN \
  --kms-key-arn arn:aws:kms:ap-northeast-2:123456789012:key/12345678-1234-1234-1234-123456789012

# IP Set 추가 (신뢰할 수 있는 IP)
aws guardduty create-ip-set \
  --detector-id detector-id \
  --activate \
  --ip-set-file file://trusted-ips.txt \
  --location us-east-1 \
  --name TrustedIPs

# Threat Intel Set 추가
aws guardduty create-threat-intel-set \
  --detector-id detector-id \
  --activate \
  --threat-intel-set-file file://threat-intel.txt \
  --location us-east-1 \
  --name ThreatIntel
```

#### Step 6: AWS Config Rules 설정

```bash
# 보안 그룹 변경 감지
aws configservice put-config-rule \
  --config-rule-name SecurityGroupChanges \
  --source EventSource=aws.config \
  --sourceIdentifier "SecurityGroupChanges" \
  --scope ComplianceResourceTypes="AWS::EC2::SecurityGroup"

# 관리자 계정 변경 감지
aws configservice put-config-rule \
  --config-rule-name IAMPolicyChanges \
  --source EventSource=aws.config \
  --sourceIdentifier "IAMPolicyChanges"

# 암호화되지 않은 S3 버킷 감지
aws configservice put-config-rule \
  --config-rule-name UnencryptedS3Buckets \
  --source EventSource=aws.config \
  --sourceIdentifier "S3_BUCKET_SERVER_SIDE_ENCRYPTION_ENABLED"
```

#### Step 7: Security Hub 활성화

```bash
# Security Hub 활성화
aws securityhub enable-security-hub

# Security Hub 알림 설정 (EventBridge 규칙)
aws events put-rule \
  --name SecurityHubFindings \
  --event-pattern '{
    "source": ["aws.securityhub"],
    "detail-type": ["Security Hub Findings - Imported"]
  }'

# SNS Topic 연결
aws events put-targets \
  --rule SecurityHubFindings \
  --targets Id=$TOPIC_ARN
```

#### Step 8: Lambda를 통한 고급 알림

```python
# Lambda 함수를 통한 Slack 알림
import json
import urllib3
import os

http = urllib3.PoolManager()
SLACK_WEBHOOK = os.environ['SLACK_WEBHOOK']

def lambda_handler(event, context):
    # 알람 이벤트 파싱
    alarm_name = event['AlarmName']
    reason = event['NewStateReason']
    metric = event['Trigger']['MetricName']
    namespace = event['Trigger']['Namespace']
    dimension = event['Trigger']['Dimensions'][0]

    # Slack 메시지 생성
    message = {
        "text": f"🚨 CloudWatch Alarm",
        "attachments": [{
            "color": "danger" if event['NewStateValue'] == "ALARM" else "good",
            "fields": [
                {"title": "Alarm Name", "value": alarm_name, "short": False},
                {"title": "Metric", "value": f"{namespace}/{metric}", "short": True},
                {"title": "Reason", "value": reason, "short": False},
                {"title": "Dimension", "value": f"{dimension['name']}={dimension['value']}", "short": True}
            ]
        }]
    }

    # Slack으로 전송
    response = http.request(
        'POST',
        SLACK_WEBHOOK,
        body=json.dumps(message),
        headers={'Content-Type': 'application/json'}
    )

    return {'statusCode': 200}
```

```bash
# Lambda 함수 생성
aws lambda create-function \
  --function-name CloudWatchAlarmSlack \
  --runtime python3.9 \
  --role arn:aws:iam::123456789012:role/LambdaExecutionRole \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://function.zip \
  --environment Variables={SLACK_WEBHOOK=https://hooks.slack.com/services/YOUR/WEBHOOK/URL}

# CloudWatch Alarms에 Lambda 연결
aws lambda add-permission \
  --function-name CloudWatchAlarmSlack \
  --statement-id CloudWatchAlarmSlack \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn arn:aws:events:ap-northeast-2:123456789012:rule/CloudWatchAlarmRule
```

### 7. 모니터링 대시보드

```bash
# CloudWatch 대시보드 생성
aws cloudwatch put-dashboard \
  --dashboard-name SecurityMonitoring \
  --dashboard-body file://dashboard.json
```

```json
// dashboard.json
{
  "widgets": [
    {
      "type": "metric",
      "x": 0,
      "y": 0,
      "width": 6,
      "height": 3,
      "properties": {
        "metrics": [
          ["AWS/EC2", "CPUUtilization", "InstanceId", "i-xxxxxxxx"],
          [".", "NetworkIn", ".", "."],
          [".", "NetworkOut", ".", "."]
        ],
        "period": 300,
        "stat": "Average",
        "region": "ap-northeast-2",
        "title": "EC2 Metrics"
      }
    }
  ]
}
```

### 8. 알림 우선순위 설정

| 우선순위 | 알람 유형 | 응답 시간 | 알림 채널 |
|---------|---------|----------|----------|
| **P1 (긴급)** | GuardDuty Critical, 보안 그룹 변경, 관리자 권한 변경 | 15분 | SMS, Slack, Email |
| **P2 (높음)** | CPU/메모리 90% 이상, 디스크 95% 이상, 네트워크 이상 | 1시간 | Slack, Email |
| **P3 (중간)** | CPU/메모리 80% 이상, 디스크 85% 이상 | 업무 시간 | Slack |
| **P4 (낮음)** | 정기 백업 성공, 일반 운영 이벤트 | 일일 리포트 | Email |

### 9. 조치 시 주의사항

| 주의사항 | 설명 |
|----------|------|
| **알림 피로** | 불필요한 알림 줄이기, 적절한 임계값 설정 |
| **오탐(False Positive)** | 정상적인 상황에서 알림이 울리지 않도록 조정 |
| **온콜(On-Call) 운영** | 24/7 대응 체계 구축 |
| **에스컬레이션** | P1 알람 미응답 시 상위 관리자에게 전달 |
| **알림 테스트** | 분기별 알림 시스템 테스트 수행 |

### 10. 참고 자료

- **AWS CloudWatch Alarms**: https://docs.aws.amazon.com/AmazonCloudWatch/latest/UserGuide/AlarmThatSendsEmail.html
- **AWS GuardDuty Documentation**: https://docs.aws.amazon.com/guardduty/
- **AWS Security Hub**: https://docs.aws.amazon.com/security-hub/

---

## 요약

**가상리소스이상징후알림설정**은 클라우드 보안 사고를 조기에 탐지하고 신속하게 대응하는 핵심 항목입니다. CloudWatch Alarms, GuardDuty, Security Hub, Config Rules 등을 활용하여 CPU, 메모리, 네트워크, 보안 이벤트 등을 모니터링하고 SNS, Slack, SMS를 통해 실시간 알림을 받으세요. 알림 피로를 방지하기 위해 적절한 임계값 설정과 우선순위 분류가 필요합니다.

**핵심 액션 아이템**
1. CPU/메모리/디스크 사용량 알람 설정
2. 네트워크 트래픽 이상 탐지 (DDoS, 데이터 유출)
3. GuardDuty 활성화로 위협 탐지
4. Security Hub로 중앙 보안 모니터링
5. SNS, Slack, SMS를 통한 실시간 알림
6. 알림 우선순위(P1~P4) 설정
