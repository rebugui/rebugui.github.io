---
title: "[2026 주요정보통신기반시설] CA-16 오브젝트스토리지버킷로깅설정"
slug: "2026-주정통/CA-16"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "Object 스토리지 버킷 로깅 설정 여부 점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Cloud
---

# CA-16 오브젝트스토리지버킷로깅설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | CA-16 |
| **점검내용** | Object 스토리지 버킷 로깅 설정 여부 점검 |
| **점검대상** | 클라우드 플랫폼 |
| **판단기준** | 양호: Object 스토리지 버킷 로깅 설정이 기관 정책에 따라 설정된 경우 |
| **판단기준** | 취약: Object 스토리지 버킷 로깅 설정이 기관 정책에 따라 설정되지 않은 경우 |
| **조치방법** | Object 스토리지 버킷 로깅 설정 |

---
## 상세 설명

### 1. 항목 개요

오브젝트 스토리지(S3, Azure Blob Storage, GCP Cloud Storage 등)의 버킷 로깅은 누가, 언제, 어떤 객체에 접근했는지 기록합니다. 이를 통해 데이터 유출, 무단 삭제, 비정상적인 접근 등의 보안 사고를 탐지하고 조사할 수 있습니다.

### 2. 왜 이 항목이 필요한가요?

**보안 위협 시나리오:**
1. **데이터 유출 탐지**: 대량의 데이터 다운로드 시도 감지
2. **비인가 접속 탐지**: 승인되지 않은 사용자의 접근 시도
3. **데이터 변조 감지**: 객체의 무단 삭제/수정 내역 추적
4. **규정 준수**: 개인정보 접근 기록 의무화

**실제 사례**
- 2018년: 테스트 버킷의 접근 로그를 분석하여 비인가 접근 시도 발견
- S3 버킷의 데이터가 삭제되었는데 로그가 없어 원인 파악 불가

### 3. 점검 대상

- 모든 오브젝트 스토리지 (S3, Azure Blob Storage, GCP Cloud Storage 등)
- 버킷 접근 로그
- 객체 수준 로그

### 4. 판단 기준

| 구분 | 기준 |
|------|------|
| **양호** | Object 스토리지 버킷 로깅이 기관 정책에 따라 설정된 경우 |
| **취약** | Object 스토리지 버킷 로깅이 비활성화된 경우 |

### 5. 점검 방법

#### Step 1: AWS S3 로깅 설정 확인

```bash
# AWS CLI 예시
# 버킷 로깅 설정 확인
aws s3api get-bucket-logging --bucket my-bucket

# 모든 버킷의 로깅 상태 확인
for bucket in $(aws s3 ls | awk '{print $3}'); do
    echo "Bucket: $bucket"
    aws s3api get-bucket-logging --bucket $bucket
    echo "---"
done
```

#### Step 2: Azure Blob Storage 로깅 확인

```bash
# Azure CLI 예시
# Storage 계정 로깅 확인
az storage account show \
  --name mystorageaccount \
  --resource-group myresourcegroup \
  --query "{accessTier:accessTier,kind:kind}"
```

#### Step 3: GCP Cloud Storage 로깅 확인

```bash
# GCP CLI 예시
# 버킷 로깅 확인
gsutil logging get gs://my-bucket

# 액세스 로그 확인
gcloud logging read "resource.type=gcs_bucket" \
  --filter="resource.labels.bucket_name=my-bucket"
```

### 6. 조치 방법

#### Step 1: AWS S3 버킷 로깅 설정

```bash
# 로그용 버킷 생성 (다른 버킷에 저장 권장)
aws s3api create-bucket \
  --bucket my-bucket-logs \
  --region ap-northeast-2

# 로그용 버킷 정책 설정 (버킷 소유자만 접근)
cat > bucket-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowLogDelivery",
      "Effect": "Allow",
      "Principal": {
        "Service": "logging.s3.amazonaws.com"
      },
      "Action": [
        "s3:PutObject"
      ],
      "Resource": [
        "arn:aws:s3:::my-bucket-logs/*"
      ]
    }
  ]
}
EOF

aws s3api put-bucket-policy \
  --bucket my-bucket-logs \
  --policy file://bucket-policy.json

# 대상 버킷에 로깅 활성화
aws s3api put-bucket-logging \
  --bucket my-bucket \
  --bucket-logging-status '{
    "LoggingEnabled": {
      "TargetBucket": "my-bucket-logs",
      "TargetPrefix": "log/",
      "TargetGrants": [
        {
          "Grantee": {
            "Type": "CanonicalUser",
            "DisplayName": "log-delivery"
          },
          "Permission": "WRITE"
        },
        {
          "Grantee": {
            "Type": "CanonicalUser",
            "DisplayName": "log-delivery"
          },
          "Permission": "READ_ACP"
        }
      ]
    }
  }'
```

#### Step 2: S3 객체 수준 로깅 (CloudTrail)

```bash
# CloudTrail을 통한 S3 객체 수준 로깅
aws cloudtrail put-event-selectors \
  --trail-name my-trail \
  --event-selectors '[
    {
      "ReadWriteType": "All",
      "IncludeManagementEvents": true,
      "DataResources": [
        {
          "Type": "AWS::S3::Object",
          "Values": ["arn:aws:s3:::my-bucket/*"]
        }
      ]
    }
  ]'

# 특정 버킷의 데이터 이벤트만 로깅
aws cloudtrail put-event-selectors \
  --trail-name my-trail \
  --event-selectors '[
    {
      "ReadWriteType": "All",
      "IncludeManagementEvents": false,
      "DataResources": [
        {
          "Type": "AWS::S3::Object",
          "Values": ["arn:aws:s3:::sensitive-bucket/*"]
        }
      ]
    }
  ]'
```

#### Step 3: S3 서버 액세스 로그를 CloudWatch로 전송

```bash
# S3 액세스 로그를 CloudWatch Logs로 전송
# Lambda 함수를 통한 로그 처리

# Lambda 함수 역할 생성
aws iam create-role \
  --role-name S3LogProcessingRole \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "lambda.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

# 정책 연결
aws iam attach-role-policy \
  --role-name S3LogProcessingRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# Lambda 함수 배포 (Python 코드)
# s3-to-cloudwatch.py

# Lambda 함수 생성
aws lambda create-function \
  --function-name S3LogProcessor \
  --runtime python3.9 \
  --role arn:aws:iam::123456789012:role/S3LogProcessingRole \
  --handler s3-to-cloudwatch.lambda_handler \
  --zip-file fileb://function.zip
```

```python
# s3-to-cloudwatch.py (Lambda 함수)
import boto3
import gzip
import json

cloudwatch = boto3.client('logs')

def lambda_handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        # S3 객체 다운로드
        s3 = boto3.client('s3')
        response = s3.get_object(Bucket=bucket, Key=key)

        # gzip 압축 해제
        log_data = gzip.decompress(response['Body'].read()).decode('utf-8')

        # CloudWatch Logs로 전송
        cloudwatch.put_log_events(
            logGroupName='/aws/s3/access-logs',
            logStreamName=bucket,
            logEvents=[
                {
                    'timestamp': int(context.aws_request_id, 16),
                    'message': log_data
                }
            ]
        )

    return {'statusCode': 200}
```

#### Step 4: Azure Blob Storage 로깅

```bash
# Storage 계정 진단 설정
az monitor diagnostic-settings create \
  --name my-diagnostic-settings \
  --resource /subscriptions/subscription-id/resourceGroups/myresourcegroup/providers/Microsoft.Storage/storageAccounts/mystorageaccount \
  --storage-account mystorageaccount \
  --logs '[
    {"category": "StorageRead", "enabled": true},
    {"category": "StorageWrite", "enabled": true},
    {"category": "StorageDelete", "enabled": true}
  ]'

# Log Analytics로 전송
az monitor diagnostic-settings create \
  --name my-diagnostic-settings \
  --resource /subscriptions/subscription-id/resourceGroups/myresourcegroup/providers/Microsoft.Storage/storageAccounts/mystorageaccount \
  --workspace myworkspace \
  --logs '[
    {"category": "StorageRead", "enabled": true},
    {"category": "StorageWrite", "enabled": true},
    {"category": "StorageDelete", "enabled": true}
  ]'
```

#### Step 5: GCP Cloud Storage 로깅

```bash
# 액세스 로그 활성화
gsutil logging set on gs://my-bucket -b gs://my-bucket-logs

# Cloud Audit Logs로 전송
gcloud logging sinks create my-sink \
  bigquery.googleapis.com/projects/my-project/datasets/my_dataset \
  --log-filter='resource.type=gcs_bucket AND resource.labels.bucket_name="my-bucket"'

# Cloud Storage 로그를 Cloud Logging으로 전송
gcloud services enable logging.googleapis.com
```

### 7. 로그 분석 및 알림 설정

#### CloudWatch Logs Insights 쿼리 예시

```
# S3 액세스 패턴 분석
fields @timestamp, bucket, key, operation, requester
| filter @logStream like /access-logs/
| parse @message "* * * * * * * *" as bucket, owner, operation, key, request_id, status, error, bytes
| stats count() by operation, requester
| sort count desc

# 대량 데이터 다운로드 탐지
fields @timestamp, bucket, key, bytes, requester
| filter @logStream like /access-logs/ and operation == "REST.GET.OBJECT"
| parse @message "* * * * * * * *" as bucket, owner, operation, key, request_id, status, error, bytes
| stats sum(bytes) as total_bytes by requester
| filter total_bytes > 1000000000  # 1GB 이상
| sort total_bytes desc

# 비인가 접근 시도
fields @timestamp, bucket, key, operation, status, error
| filter @logStream like /access-logs/ and status != 200
| parse @message "* * * * * * * *" as bucket, owner, operation, key, request_id, status, error, bytes
| stats count() by error, operation
| sort count desc
```

### 8. S3 이벤트 알림 설정

```bash
# S3 이벤트 알림 생성 (SNS)
aws s3api put-bucket-notification-configuration \
  --bucket my-bucket \
  --notification-configuration '{
    "TopicConfigurations": [
      {
        "TopicArn": "arn:aws:sns:ap-northeast-2:123456789012:MyTopic",
        "Events": ["s3:ObjectCreated:*", "s3:ObjectRemoved:*"]
      }
    ]
  }'

# Lambda 함수 트리거 설정
aws s3api put-bucket-notification-configuration \
  --bucket my-bucket \
  --notification-configuration '{
    "LambdaFunctionConfigurations": [
      {
        "LambdaFunctionArn": "arn:aws:lambda:ap-northeast-2:123456789012:function:MyFunction",
        "Events": ["s3:ObjectCreated:*"]
      }
    ]
  }'
```

### 9. Macie를 통한 데이터 보안 모니터링

```bash
# AWS Macie 활성화 (민감 데이터 탐지)
aws macie2 enable-macie

# Macie 세션 생성
aws macie2 create-findings-filter \
  --action ARCHIVE \
  --name "HighSeverityFindings" \
  --finding-criteria '{
    "criterion": {
      "severity.description": {
        "eq": ["High"]
      }
    }
  }'
```

### 10. 조치 시 주의사항

| 주의사항 | 설명 |
|----------|------|
| **로그 비용** | S3 로그는 리퀘스트 수에 비례하여 비용 발생 |
| **로그 버킷 분리** | 로그는 별도 버킷에 저장 권장 |
| **접근 통제** | 로그 버킷은 보안팀만 접근 허용 |
| **로그 암호화** | 로그 버킷 암호화 필수 |
| **정기적 검토** | 분기별 로그 수집 정책 검토 |

### 11. 참고 자료

- **AWS S3 Server Access Logging**: https://docs.aws.amazon.com/AmazonS3/latest/userguide/ServerLogs.html
- **Azure Storage Logging**: https://docs.microsoft.com/azure/storage/common/storage-monitor-storage-account
- **GCP Cloud Storage Access Logs**: https://cloud.google.com/storage/docs/access-logs

---

## 요약

**오브젝트스토리지버킷로깅설정**은 오브젝트 스토리지의 모든 접근과 활동을 기록하여 보안 사고를 탐지하고 조사하는 핵심 항목입니다. S3 버킷 로깅, CloudTrail 데이터 이벤트, Azure 진단 설정, GCP Cloud Audit Logs 등을 활성화하여 누가 데이터에 접근했는지 추적할 수 있어야 합니다. 대량 다운로드, 비인가 접근 등의 이상 징후를 탐지하는 알림 설정도 함께 구현하세요.

**핵심 액션 아이템**
1. S3 버킷 로깅 활성화 및 별도 버킷에 저장
2. CloudTrail 데이터 이벤트 로깅
3. CloudWatch Logs/Log Analytics로 중앙 집중화
4. 대량 다운로드, 비인가 접근 알림 설정
5. 정기적 로그 검토 및 분석
