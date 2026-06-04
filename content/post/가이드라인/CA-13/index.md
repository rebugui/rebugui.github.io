---
title: "[2026 주요정보통신기반시설] CA-13 클라우드서비스사용자계정로깅설정"
slug: "2026-주정통/CA-13"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "사용자 계정 로깅 설정 여부 점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Cloud
---

# CA-13 클라우드서비스사용자계정로깅설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | CA-13 |
| **점검내용** | 사용자 계정 로깅 설정 여부 점검 |
| **점검대상** | 클라우드 플랫폼 |
| **판단기준** | 양호: 사용자 계정 로깅 설정이 기관 정책에 따라 설정된 경우 |
| **판단기준** | 취약: 사용자 계정 로깅 설정이 기관 정책에 따라 설정되지 않은 경우 |
| **조치방법** | 사용자 계정 로깅 설정 |

---
## 상세 설명

### 1. 항목 개요

클라우드 환경에서 사용자 계정 활동 로깅(CloudTrail, Audit Logs 등)은 보안 모니터링의 핵심입니다. 누가, 언제, 어디서, 어떤 작업을 수행했는지에 대한 기록은 보안 사고 조사, 규정 준수, 이상 징후 탐지에 필수적입니다.

### 2. 왜 이 항목이 필요한가요?

**보안 위협 시나리오:**
1. **비인가 접근 탐지**: 이상한 지역/시간대에서의 로그인 시도 감지
2. **권한 남용 확인**: 관리자 권한의 부적절한 사용 감지
3. **사고 조사**: 침해사고 발생 시 공격 경로와 영향 범위 분석
4. **규정 준수**: 개인정보보호법, 금융규정 등에서 로그 기록 의무화

**실제 사례**
- 2019년: 캡틴 컴퓨터(Capital One) 데이터 유출 사고 시 CloudTrail 로그를 통해 공격자의 활동 추적
- AWS 관리자 계정 탈취 사고 시 로그 분석을 통해 피해 범위 확인

### 3. 점검 대상

- 모든 클라우드 플랫폼 (AWS, Azure, GCP, Naver Cloud, Kakao Cloud 등)
- 관리자 콘솔 접속 로그
- API 호출 로그
- 리소스 변경 로그
- 인증/인가 로그

### 4. 판단 기준

| 구분 | 기준 |
|------|------|
| **양호** | 사용자 계정 로깅이 기관 정책(보관 기간, 로그 수준 등)에 따라 설정된 경우 |
| **취약** | 사용자 계정 로깅이 비활성화되거나 기관 정책에 맞지 않게 설정된 경우 |

### 5. 점검 방법

#### Step 1: AWS CloudTrail 설정 확인

```bash
# AWS CLI 예시
# CloudTrail 트레일 확인
aws cloudtrail describe-trails

# 모든 리전에 로깅되는지 확인
aws cloudtrail describe-trails \
  --query "trailList[?IsMultiRegionTrail==`true`].{Name:Name,S3BucketName:S3BucketName,IsMultiRegionTrail:IsMultiRegionTrail}"

# 로그 파일 검증 활성화 확인
aws cloudtrail describe-trails \
  --query "trailList[?LogFileValidationEnabled==`true`]"

# CloudTrail 로그 암호화 확인
aws cloudtrail describe-trails \
  --query "trailList[].{Name:Name,KmsKeyId:KmsKeyId}"
```

#### Step 2: Azure Activity Logs 확인

```bash
# Azure CLI 예시
# Activity Log 확인
az monitor activity-log list

# Log Analytics Workspace에 연결 확인
az monitor log-analytics workspace list

# 진단 설정 확인
az monitor diagnostic-settings list
```

#### Step 3: GCP Cloud Audit Logs 확인

```bash
# GCP CLI 예시
# 감사 로그 활성화 확인
gcloud logging buckets list

# 로그 싱크 설정 확인
gcloud logging sinks list

# Admin Activity, Data Access 로그 확인
gcloud logging read "logName=cloudaudit.googleapis.com%2Factivity" --limit 5
```

### 6. 조치 방법

#### Step 1: AWS CloudTrail 설정

```bash
# S3 버킷 생성 (로그 저장용)
aws s3api create-bucket \
  --bucket my-cloudtrail-logs-123456789012 \
  --region ap-northeast-2

# 버킷 정책 설정 (CloudTrail만 쓰기 가능)
aws s3api put-bucket-policy \
  --bucket my-cloudtrail-logs-123456789012 \
  --policy file://bucket-policy.json
```

```json
// bucket-policy.json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AWSCloudTrailAclCheck",
      "Effect": "Allow",
      "Principal": {
        "Service": "cloudtrail.amazonaws.com"
      },
      "Action": "s3:GetBucketAcl",
      "Resource": "arn:aws:s3:::my-cloudtrail-logs-123456789012"
    },
    {
      "Sid": "AWSCloudTrailWrite",
      "Effect": "Allow",
      "Principal": {
        "Service": "cloudtrail.amazonaws.com"
      },
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::my-cloudtrail-logs-123456789012/AWSLogs/123456789012/*",
      "Condition": {
        "StringEquals": {
          "s3:x-amz-acl": "bucket-owner-full-control"
        }
      }
    }
  ]
}
```

```bash
# CloudTrail 트레일 생성 (모든 리전 로깅)
aws cloudtrail create-trail \
  --name my-trail \
  --s3-bucket-name my-cloudtrail-logs-123456789012 \
  --include-global-service-events \
  --is-multi-region-trail

# 로그 파일 검증 활성화
aws cloudtrail update-trail \
  --name my-trail \
  --enable-log-file-validation

# CloudTrail 로그 암호화 활성화
aws cloudtrail update-trail \
  --name my-trail \
  --kms-key-id arn:aws:kms:ap-northeast-2:123456789012:key/12345678-1234-1234-1234-123456789012

# 트레일 시작 로깅
aws cloudtrail start-logging --name my-trail
```

#### Step 2: CloudTrail 데이터 이벤트 로깅

```bash
# S3 객체 수준 API 호출 로깅
aws cloudtrail put-event-selectors \
  --trail-name my-trail \
  --event-selectors '
  [
    {
      "ReadWriteType": "All",
      "IncludeManagementEvents": true,
      "DataResources": [
        {
          "Type": "AWS::S3::Object",
          "Values": ["arn:aws:s3:::my-bucket/"]
        }
      ]
    }
  ]
'

# Lambda 함수 호출 로깅
aws cloudtrail put-event-selectors \
  --trail-name my-trail \
  --event-selectors '
  [
    {
      "ReadWriteType": "All",
      "IncludeManagementEvents": true,
      "DataResources": [
        {
          "Type": "AWS::Lambda::Function",
          "Values": ["arn:aws:lambda:ap-northeast-2:123456789012:function:*"]
        }
      ]
    }
  ]
'
```

#### Step 3: Azure Monitor Diagnostic Settings 설정

```bash
# Log Analytics Workspace 생성
az monitor log-analytics workspace create \
  --resource-group myResourceGroup \
  --workspace-name myWorkspace \
  --location koreacentral

# Activity Log를 Log Analytics로 전송
az monitor diagnostic-settings create \
  --name myDiagnosticSettings \
  --resource /subscriptions/subscription-id \
  --workspace myWorkspace \
  --logs '[
    {"category": "AuditLogs", "enabled": true},
    {"category": "SignInLogs", "enabled": true}
  ]'
```

#### Step 4: GCP Cloud Audit Logs 설정

```bash
# 로그 싱크 생성 (Pub/Sub을 통한 실간 전송)
gcloud logging sinks create my-sink \
  pubsub.googleapis.com/projects/my-project/topics/my-topic \
  --log-filter='logName="cloudaudit.googleapis.com/activity" OR logName="cloudaudit.googleapis.com/data_access"'

# 로그 라우터 싱크 생성 (Cloud Storage)
gcloud logging sinks create my-storage-sink \
  storage.googleapis.com/my-bucket \
  --log-filter='logName="cloudaudit.googleapis.com/*"' \
  --include-children

# BigQuery로 로그 내보내기
gcloud logging sinks create my-bq-sink \
  bigquery.googleapis.com/projects/my-project/datasets/my_dataset \
  --log-filter='logName="cloudaudit.googleapis.com/activity"'
```

### 7. 로그 분석 및 알림 설정

#### AWS CloudWatch Logs를 통한 분석

```bash
# CloudTrail을 CloudWatch Logs로 전송
aws cloudtrail create-trail \
  --name my-trail-cw \
  --s3-bucket-name my-cloudtrail-logs-123456789012 \
  --cloud-watch-logs-log-group-name CloudTrail/APIActivity \
  --cloud-watch-logs-role-arn arn:aws:iam::123456789012:role/CloudTrail_CloudWatchLogs_Role

# 의심스러운 활동 알람 생성
aws cloudwatch put-metric-alarm \
  --alarm-name "UnauthorizedAPIAttempt" \
  --alarm-description "Alert on Unauthorized API attempts" \
  --metric-name UnauthorizedOperation \
  --namespace AWS/CloudTrail \
  --statistic Sum \
  --period 300 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 1
```

#### CloudWatch Logs Insights 쿼리 예시

```
# 관리자 계정의 API 호출 현황
fields @timestamp, userIdentity.principalId, eventName, sourceIPAddress
| filter userIdentity.type = 'IAMUser' and userIdentity.principalId like '%admin%'
| sort @timestamp desc
| limit 100

# 특정 IP에서의 의심스러운 활동
fields @timestamp, userIdentity.principalId, eventName, sourceIPAddress, userAgent
| filter sourceIPAddress not like '203.0.113.%'
| sort @timestamp desc

# 보안 그룹 변경 활동
fields @timestamp, userIdentity.principalId, eventName, requestParameters
| filter eventName like /AuthorizeSecurityGroup/ or eventName like /RevokeSecurityGroup/
| sort @timestamp desc
```

### 8. 로그 보관 기간 설정

```bash
# CloudWatch Logs 보관 기간 설정 (90일)
aws logs put-retention-policy \
  --log-group-name CloudTrail/APIActivity \
  --retention-in-days 90

# S3 버킷 수명 주기 정책 설정
aws s3api put-bucket-lifecycle-configuration \
  --bucket my-cloudtrail-logs-123456789012 \
  --lifecycle-configuration '{
    "Rules": [
      {
        "Id": "CloudTrailLogs",
        "Status": "Enabled",
        "Prefix": "AWSLogs/",
        "Transitions": [
          {
            "Days": 30,
            "StorageClass": "STANDARD_IA"
          },
          {
            "Days": 90,
            "StorageClass": "GLACIER"
          },
          {
            "Days": 365,
            "StorageClass": "DEEP_ARCHIVE"
          }
        ],
        "Expiration": {
          "Days": 2555  # 7년
        }
      }
    ]
  }'
```

### 9. 조치 시 주의사항

| 주의사항 | 설명 |
|----------|------|
| **저장소 비용** | 로그 데이터가 많으므로 비용 최적화 필요 (Life Cycle Policy) |
| **개인정보 보호** | 로그에 포함된 개인정보 마스킹 처리 고려 |
| **로그 무결성** | 로그 파일 검증 활성화, WORM(Write Once Read Many) 스토리지 사용 |
| **접근 통제** | 로그 접근 권한을 최소화 (보안팀, 감사팀만 접근) |
| **정기적 검토** | 분기별 로그 수집 및 보관 정책 검토 |

### 10. 참고 자료

- **AWS CloudTrail Documentation**: https://docs.aws.amazon.com/cloudtrail/
- **Azure Monitor Documentation**: https://docs.microsoft.com/azure/azure-monitor/
- **GCP Cloud Audit Logs**: https://cloud.google.com/logging/docs/audit/
- **NIST SP 800-92**: Guide to Computer Security Log Management

---

## 요약

**클라우드서비스사용자계정로깅설정**은 클라우드 보안의 눈과 귀와 같습니다. 모든 관리자 활동, API 호출, 리소스 변경을 로깅하여 보안 사고를 탐지하고 조사할 수 있어야 합니다. CloudTrail, Azure Monitor, Cloud Audit Logs 등 클라우드 제공사의 로깅 서비스를 활성화하고, 로그를 안전하게 보관하며 정기적으로 분석하여 이상 징후를 조기에 발견하세요.

**핵심 액션 아이템**
1. 모든 리전에 대해 CloudTrail/감사 로그 활성화
2. 로그 파일 검증 및 암호화 활성화
3. 관리 이벤트뿐만 아니라 데이터 이벤트도 로깅
4. CloudWatch Logs/Log Analytics로 중앙 집중화
5. 로그 보관 기간 설정 (최소 90일, 권장 1년 이상)
6. 이상 징후 알림 설정
