---
title: "[2026 주요정보통신기반시설] CA-17 로그보관기간설정"
slug: "2026-주정통/CA-17"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "클라우드 서비스 로그 보관 기간을 기관 정책에 맞게 보관 여부 점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Cloud
---

# CA-17 로그보관기간설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | CA-17 |
| **점검내용** | 클라우드 서비스 로그 보관 기간을 기관 정책에 맞게 보관 여부 점검 |
| **점검대상** | 클라우드 플랫폼 |
| **판단기준** | 양호: 클라우드 서비스 로그 보관 기간을 기관 정책에 맞게 수립된 경우 |
| **판단기준** | 취약: 클라우드 서비스 로그 보관 기간을 기관 정책에 맞게 수립되지 않은 경우 |
| **조치방법** | 클라우드 서비스 로그 보관 기간을 기관 정책에 맞게 수립 설정 |

---
## 상세 설명

### 1. 항목 개요

클라우드 환경에서 발생하는 다양한 로그(CloudTrail, CloudWatch Logs, VPC Flow Logs, Audit Logs 등)는 보안 사고 조사, 규정 준수, 시스템 최적화에 필수적입니다. 적절한 로그 보관 기간을 설정하지 않으면, 과거 사고의 원인을 분석할 수 없거나 법적 요구사항을 충족하지 못할 수 있습니다.

### 2. 왜 이 항목이 필요한가요?

**보안 위협 및 규정 준수:**
1. **사고 조사**: 침해사고 발생 시 공격 경로와 시점 분석
2. **규정 준수**: 개인정보보호법(3년), 금융규정(5년) 등 법적 요구사항
3. **포렌식**: 디지털 포렌식을 위한 증거 보존
4. **비용 최적화**: 불필요하게 긴 보관 기간은 스토리지 비용 증가

**실제 사례**
- 6개월 전의 로그가 삭제되어 데이터 유출 사고의 원인 파악 불가
- 금융규정상 5년 보관이 필요한데 1년만 보관하여 규정 위반

### 3. 점검 대상

- CloudWatch Logs
- CloudTrail Logs (S3에 저장)
- VPC Flow Logs
- RDS/Aurora Logs
- Azure Monitor Logs
- GCP Cloud Audit Logs
- Object Storage 로그

### 4. 판단 기준

| 구분 | 기준 |
|------|------|
| **양호** | 로그 보관 기간이 기관 정책 및 법적 요구사항에 맞게 설정된 경우 |
| **취약** | 로그 보관 기간이 설정되지 않거나 너무 짧은 경우 |

### 5. 점검 방법

#### Step 1: CloudWatch Logs 보관 기간 확인

```bash
# AWS CLI 예시
# 모든 로그 그룹의 보관 기간 확인
aws logs describe-log-groups \
  --query "logGroups[].{logGroupName:logGroupName,retentionInDays:retentionInDays}"

# 보관 기간이 설정되지 않은 로그 그룹 확인
aws logs describe-log-groups \
  --query "logGroups[?retentionInDays==null].logGroupName"
```

#### Step 2: S3 버킷 라이프사이클 확인

```bash
# S3 버킷 라이프사이클 정책 확인
aws s3api get-bucket-lifecycle-configuration --bucket my-logs-bucket

# 모든 로그 버킷의 라이프사이클 확인
for bucket in $(aws s3 ls | grep logs | awk '{print $3}'); do
    echo "Bucket: $bucket"
    aws s3api get-bucket-lifecycle-configuration --bucket $bucket 2>/dev/null || echo "No lifecycle policy"
    echo "---"
done
```

#### Step 3: Azure Log Analytics 보관 정책 확인

```bash
# Azure CLI 예시
# 작업 영역 보관 정책 확인
az monitor log-analytics workspace show \
  --name myworkspace \
  --resource-group myresourcegroup \
  --query "retentionInDays"

# 모든 작업 영역 확인
az monitor log-analytics workspace list \
  --query "[].{name:name,resourceGroup:resourceGroup,retention:retentionInDays}"
```

#### Step 4: GCP Logging 보관 정책 확인

```bash
# GCP CLI 예시
# 로그 버킷 보관 정책 확인
gcloud logging buckets list

# 특정 로그 버킷의 보관 기간 확인
gcloud logging buckets describe _Default --location global
```

### 6. 조치 방법

#### Step 1: CloudWatch Logs 보관 기간 설정

```bash
# 로그 그룹별 보관 기간 설정 (1년 = 365일)
aws logs put-retention-policy \
  --log-group-name /aws/lambda/my-function \
  --retention-in-days 365

# 보관 기간 옵션:
# 1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653

# 중요 로그는 장기 보관 (5년)
aws logs put-retention-policy \
  --log-group-name /aws/rds/instance/mydb/slowquery \
  --retention-in-days 1827

# 모든 로그 그룹에 보관 기간 설정
for loggroup in $(aws logs describe-log-groups --query "logGroups[].logGroupName" --output text); do
    echo "Setting retention for $loggroup"
    aws logs put-retention-policy \
      --log-group-name "$loggroup" \
      --retention-in-days 90
done
```

#### Step 2: S3 라이프사이클 정책 설정

```bash
# S3 버킷 라이프사이클 정책 생성
cat > lifecycle-policy.json <<EOF
{
  "Rules": [
    {
      "Id": "CloudTrailLogsLifecycle",
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
}
EOF

# 라이프사이클 정책 적용
aws s3api put-bucket-lifecycle-configuration \
  --bucket my-cloudtrail-logs \
  --lifecycle-configuration file://lifecycle-policy.json
```

#### Step 3: VPC Flow Logs 보관 기간 설정

```bash
# VPC Flow Logs를 CloudWatch Logs로 전송 시 보관 기간 설정
aws logs put-retention-policy \
  --log-group-name /aws/vpc/flowlogs/my-vpc \
  --retention-in-days 90

# VPC Flow Logs를 S3로 전송 시 라이프사이클 정책 설정
cat > flow-lifecycle-policy.json <<EOF
{
  "Rules": [
    {
      "Id": "FlowLogsLifecycle",
      "Status": "Enabled",
      "Prefix": "vpcflowlogs/",
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "STANDARD_IA"
        },
        {
          "Days": 90,
          "StorageClass": "GLACIER_IR"
        }
      ],
      "Expiration": {
        "Days": 365
      }
    }
  ]
}
EOF

aws s3api put-bucket-lifecycle-configuration \
  --bucket my-flowlogs-bucket \
  --lifecycle-configuration file://flow-lifecycle-policy.json
```

#### Step 4: Azure Log Analytics 보관 정책 설정

```bash
# 기본 보관 정책 설정 (90일)
az monitor log-analytics workspace update \
  --name myworkspace \
  --resource-group myresourcegroup \
  --retention-time 90

# 장기 보관 (2년 = 730일)
az monitor log-analytics workspace update \
  --name myworkspace \
  --resource-group myresourcegroup \
  --retention-time 730 \
  --max-retention-time 730
```

#### Step 5: GCP Cloud Logging 보관 정책 설정

```bash
# 기본 로그 버킷 보관 기간 수정 (30일)
gcloud logging buckets update _Default \
  --location global \
  --retention-days 30

# 새로운 로그 버킷 생성 (1년 보관)
gcloud logging buckets create my-logs-bucket \
  --location global \
  --retention-days 365

# 로그 싱크를 사용한 장기 보관 (Cloud Storage)
gcloud logging sinks create my-archival-sink \
  storage.googleapis.com/my-logs-archive \
  --log-filter='logName="projects/my-project/logs/*"' \
  --include-children

# Cloud Storage 버킷 라이프사이클 설정
gsutil lifecycle set lifecycle-config.json gs://my-logs-archive
```

```json
// lifecycle-config.json
{
  "lifecycle": {
    "rule": [
      {
        "action": {
          "type": "SetStorageClass",
          "storageClass": "ARCHIVE"
        },
        "condition": {
          "age": 90
        }
      },
      {
        "action": {
          "type": "Delete"
        },
        "condition": {
          "age": 2555
        }
      }
    ]
  }
}
```

### 7. 로그 보관 기간 가이드라인

| 로그 유형 | 최소 보관 기간 | 권장 보관 기간 | 비고 |
|----------|---------------|---------------|------|
| **CloudTrail/감사 로그** | 365일 | 2555일 (7년) | 포렌식, 규정 준수 |
| **VPC Flow Logs** | 30일 | 90일 | 네트워크 분석 |
| **CloudWatch Logs (애플리케이션)** | 7일 | 90일 | 장애 조사 |
| **데이터베이스 로그** | 30일 | 180일 | 성능 분석 |
| **오브젝트 스토리지 로그** | 30일 | 90일 | 접근 감사 |
| **보안 로그** | 90일 | 365일 | 보안 사고 조사 |

### 8. 비용 최적화 전략

```
┌─────────────────────────────────────────────────────────────┐
│                    로그 라이프사이클                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [Hot Data]    [Warm Data]      [Cold Data]      [Delete]   │
│                                                             │
│  0-30일       30-90일          90-365일         365일 이후   │
│  ↓           ↓                ↓                ↓           │
│  CloudWatch   Standard_IA      Glacier          삭제        │
│  Logs                         Deep Archive                 │
│                                                             │
│  (빈번 액세스)   (가끔 액세스)      (거의 액세스 없음)        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 9. 자동화된 로그 아카이빙

```python
# Lambda 함수를 활용한 자동 로그 아카이빙
import boto3
import datetime

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # 90일 이상 된 로그를 Glacier로 이동
    bucket = 'my-cloudtrail-logs'
    prefix = 'AWSLogs/'

    # S3 객체 목록 조회
    objects = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)

    for obj in objects.get('Contents', []):
        last_modified = obj['LastModified']
        age_days = (datetime.datetime.now(datetime.timezone.utc) - last_modified).days

        if age_days >= 90:
            # Glacier로 전환
            s3.restore-object(
                Bucket=bucket,
                Key=obj['Key'],
                RestoreRequest={
                    'Days': 30,
                    'GlacierJobParameters': {'Tier': 'Standard'}
                }
            )
            print(f"Restored {obj['Key']} from Glacier")
```

### 10. 조치 시 주의사항

| 주의사항 | 설명 |
|----------|------|
| **법적 요구사항** | 개인정보보호법, 금융규정 등에 따른 최소 보관 기간 준수 |
| **스토리지 비용** | 장기 보관은 비용 증가, 비용 최적화 필요 |
| **로그 무결성** | WORM(Write Once Read Many) 스토리지 사용 권장 |
| **데이터 삭제** | 보관 기간 만료 후 즉시 삭제 여부 검토 |
| **조사 중인 로그** | 보관 기간 만료라도 조사 중인 로그는 보존 |

### 11. 참고 자료

- **AWS CloudTrail Log File Validation**: https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-validation-intro.html
- **AWS S3 Lifecycle Management**: https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html
- **Azure Log Analytics Retention**: https://docs.microsoft.com/azure/azure-monitor/logs/manage-log-storage
- **GCP Logging Retention**: https://cloud.google.com/logging/docs/retention

---

## 요약

**로그보관기간설정**은 클라우드 보안 사고 조사와 규정 준수를 위한 필수 항목입니다. 법적 요구사항(개인정보보호법 3년, 금융규정 5년 등)에 맞게 로그 보관 기간을 설정하고, S3 라이프사이클, CloudWatch Logs 보관 정책 등을 활용하여 비용을 최적화하세요. 중요한 로그는 장기 보관하고, 비용 절감을 위해 적절한 스토리지 클래스(STANDARD_IA, Glacier, Deep Archive)를 활용하세요.

**핵심 액션 아이템**
1. CloudWatch Logs 보관 기간 설정 (최소 90일)
2. S3 라이프사이클 정책으로 장기 보관 및 비용 최적화
3. CloudTrail/감사 로그는 7년(2555일) 보관 권장
4. 로그 분류별 차등 보관 기간 설정
5. 정기적 로그 보관 정책 검토
