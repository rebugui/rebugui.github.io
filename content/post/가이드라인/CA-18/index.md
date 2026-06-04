---
title: "[2026 주요정보통신기반시설] CA-18 백업사용여부"
slug: "2026-주정통/CA-18"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "클라우드 리소스에 대한 백업 수행 여부 점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Cloud
---

# CA-18 백업사용여부

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | CA-18 |
| **점검내용** | 클라우드 리소스에 대한 백업 수행 여부 점검 |
| **점검대상** | 클라우드 플랫폼 |
| **판단기준** | 양호: 클라우드 리소스를 기관 정책에 따라 주기적으로 백업이 수행된 경우 |
| **판단기준** | 취약: 클라우드 리소스를 기관 정책에 따라 주기적으로 백업이 수행되지 않은 경우 |
| **조치방법** | 클라우드 리소스를 주기적으로 백업 설정 |

---
## 상세 설명

### 1. 항목 개요

클라우드 환경에서도 백업은 데이터 보호와 비즈니스 연속성의 핵심입니다. 인스턴스 장애, 데이터베이스 손상, 데이터 삭제, 리전 장애 등 다양한 시나리오에서 백업은 빠른 복구와 데이터 손실 방지를 위해 필수적입니다.

### 2. 왜 이 항목이 필요한가요?

**데이터 손실 시나리오:**
1. **실수로 데이터 삭제**: 관리자의 실수로 중요 데이터 삭제
2. **악성코드 감염**: 랜섬웨어로 데이터 암호화
3. **하드웨어 장애**: 스토리지 장애로 데이터 손실
4. **리전 장애**: 전체 리전의 가용성 저하 (AWS us-east-1 장애 등)
5. **자연재해**: 화재, 지진, 홍수 등 물리적 재해

**실제 사례**
- 2021년: 코드 삭제 실수로 백업이 없어 회사 폐업
- 2017년: AWS S3 버킷 삭제 실수로 데이터 영구 손실
- 2020년: 랜섬웨어 공격으로 백업 없이 전체 데이터 손실

### 3. 점검 대상

- EC2 인스턴스 / VM
- RDS, Cloud SQL, Azure SQL 등 데이터베이스
- EBS, Managed Disk 등 블록 스토리지
- S3, Blob Storage 등 오브젝트 스토리지
- VPC 구성

### 4. 판단 기준

| 구분 | 기준 |
|------|------|
| **양호** | 주기적 자동 백업이 설정되고, 정기적으로 복구 테스트가 수행되는 경우 |
| **취약** | 백업이 설정되지 않았거나, 수동으로만 백업되는 경우 |

### 5. 점검 방법

#### Step 1: EC2 인스턴스 백업 확인

```bash
# AWS CLI 예시
# AMI(인스턴스 이미지) 확인
aws ec2 describe-images \
  --owners self \
  --query "Images[].{ImageId:ImageId,Name:Name,CreationDate:CreationDate}"

# 스냅샷 확인
aws ec2 describe-snapshots \
  --owner-ids self \
  --query "Snapshots[].{SnapshotId:SnapshotId,VolumeId:VolumeId,StartTime:StartTime}"

# Lifecycle Manager 확인
aws dlm describe-lifecycle-policies
```

#### Step 2: RDS 백업 확인

```bash
# RDS 백업 보관 기간 확인
aws rds describe-db-instances \
  --query "DBInstances[].{DBInstanceIdentifier:DBInstanceIdentifier,BackupRetentionPeriod:BackupRetentionPeriod}"

# DB 스냅샷 확인
aws rds describe-db-snapshots \
  --snapshot-type manual \
  --query "DBSnapshots[].{DBSnapshotIdentifier:DBSnapshotIdentifier,SnapshotCreateTime:SnapshotCreateTime}"
```

#### Step 3: Azure VM 백업 확인

```bash
# Azure CLI 예시
# Recovery Services Vault 확인
az backup vault list

# VM 백업 작업 확인
az backup job list --resource-group myresourcegroup --vault-name myvault
```

### 6. 조치 방법

#### Step 1: EC2 인스턴스 백업

```bash
# 수동 AMI 생성
aws ec2 create-image \
  --instance-id i-xxxxxxxx \
  --name "my-instance-backup-$(date +%Y%m%d)" \
  --description "Daily backup of my instance"

# EBS 스냅샷 생성
aws ec2 create-snapshot \
  --volume-id vol-xxxxxxxx \
  --description "Daily snapshot of root volume"
```

```bash
# AWS Backup을 통한 자동 백업
# 백업 계획 생성
aws backup create-backup-plan \
  --backup-plan '{
    "BackupPlan": {
      "BackupPlanName": "EISBackupPlan",
      "Rules": [
        {
          "RuleName": "DailyBackups",
          "ScheduleExpression": "cron(0 5 ? * * *)",
          "StartWindowMinutes": 60,
          "TargetBackupVault": "Default",
          "Lifecycle": {
            "DeleteAfterDays": 35
          }
        },
        {
          "RuleName": "WeeklyBackups",
          "ScheduleExpression": "cron(0 5 ? * 1 *)",
          "TargetBackupVault": "Default",
          "Lifecycle": {
            "MoveToColdStorageAfterDays": 30,
            "DeleteAfterDays": 365
          }
        }
      ]
    }
  }'

# 백업 계획에 리소스 태그 추가
aws backup tag-resources \
  --resource-arns arn:aws:ec2:ap-northeast-2:123456789012:instance/i-xxxxxxxx \
  --tags Backup=Daily
```

#### Step 2: DLM (Data Lifecycle Manager) 설정

```bash
# DLM 정책 생성 (EBS 스냅샷 자동화)
aws dlm create-lifecycle-policy \
  --description "Daily EBS snapshots" \
  --state ENABLED \
  --execution-role-arn arn:aws:iam::123456789012:role/AWSDataLifecycleManagerDefaultRole \
  --policy-details '{
    "ResourceTypes": ["VOLUME"],
    "TargetTags": [{"Key": "Backup", "Value": "Daily"}],
    "Schedules": [{
      "Name": "DailySnapshots",
      "CreateRule": {
        "Interval": 24,
        "IntervalUnit": "HOURS",
        "Times": ["05:00"]
      },
      "RetainRule": {
        "Count": 7
      },
      "CopyTags": true
    }]
  }'

# AMI 라이프사이클 정책
aws dlm create-lifecycle-policy \
  --description "Daily AMI backups" \
  --state ENABLED \
  --execution-role-arn arn:aws:iam::123456789012:role/AWSDataLifecycleManagerDefaultRole \
  --policy-details '{
    "ResourceTypes": ["INSTANCE"],
    "TargetTags": [{"Key": "Backup", "Value": "Daily"}],
    "Schedules": [{
      "Name": "DailyAMIs",
      "CreateRule": {
        "Interval": 24,
        "IntervalUnit": "HOURS",
        "Times": ["05:00"]
      },
      "RetainRule": {
        "Count": 7
      },
      "FastRestoreRule": {
        "Count": 1,
        "Interval": 0,
        "IntervalUnit": "HOURS"
      }
    }]
  }'
```

#### Step 3: RDS 자동 백업 설정

```bash
# RDS 백업 보관 기간 설정 (1~35일)
aws rds modify-db-instance \
  --db-instance-identifier mydb \
  --backup-retention-period 7 \
  --backup-window "05:00-06:00" \
  --maintenance-window "Mon:06:00-Mon:07:00" \
  --apply-immediately

# DB 스냅샷 생성
aws rds create-db-snapshot \
  --db-instance-identifier mydb \
  --db-snapshot-identifier mydb-snapshot-$(date +%Y%m%d)

# 최신 스냅샷에서 복구
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier mydb-restored \
  --db-snapshot-identifier mydb-snapshot-20250120
```

#### Step 4: S3 버전 관리 및 중복 삭제

```bash
# S3 버전 관리 활성화
aws s3api put-bucket-versioning \
  --bucket my-bucket \
  --versioning-configuration Status=Enabled

# S3 객체 잠금 활성화 (WORM - Write Once Read Many)
aws s3api put-object-lock-configuration \
  --bucket my-bucket \
  --object-lock-configuration '{
    "ObjectLockEnabled": "Enabled",
    "Rule": {
      "DefaultRetention": {
        "Mode": "GOVERNANCE",
        "Days": 30
      }
    }
  }'

# 교차 리전 복제(CRR) 설정
aws s3api put-bucket-replication \
  --bucket source-bucket \
  --replication-configuration file://replication-config.json
```

```json
// replication-config.json
{
  "Role": "arn:aws:iam::123456789012:role/replication-role",
  "Rules": [
    {
      "Status": "Enabled",
      "Priority": 1,
      "Filter": {},
      "Destination": {
        "Bucket": "arn:aws:s3:::destination-bucket",
        "ReplicationTime": {
          "Status": "Enabled",
          "Time": {
            "Minutes": 15
          }
        },
        "Metrics": {
          "Status": "Enabled"
        },
        "StorageClass": "STANDARD"
      },
      "DeleteMarkerReplication": {
        "Status": "Enabled"
      }
    }
  ]
}
```

#### Step 5: Azure VM 백업

```bash
# Recovery Services Vault 생성
az backup vault create \
  --name myvault \
  --resource-group myresourcegroup \
  --location koreacentral

# VM 백업 활성화
az backup protection enable-for-vm \
  --resource-group myresourcegroup \
  --vault-name myvault \
  --vm myvm \
  --policy-name defaultpolicy

# 백업 정책 생성 (매일 백업, 30일 보관)
az backup policy create \
  --name mybackuppolicy \
  --vault-name myvault \
  --resource-group myresourcegroup \
  --backup-management-type AzureIaasVM \
  --policy-schedule "daily=5:00" \
  --retention-daily 30 \
  --retention-weekly 12 \
  --retention-monthly 24 \
  --retention-yearly 10
```

#### Step 6: GCP Cloud SQL 백업

```bash
# 자동 백업 설정
gcloud sql instances patch instance-name \
  --backup-start-time 05:00 \
  --backup-enabled

# 수동 백업 생성
gcloud sql backups create backup-$(date +%Y%m%d) \
  --instance instance-name \
  --description "Daily backup"

# 백업에서 복구
gcloud sql instances restore instance-name \
  --backup-id backup-id
```

### 7. 백업 전략

#### 3-2-1 백업 규칙

```
┌─────────────────────────────────────────────────────────────┐
│                    3-2-1 백업 규칙                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  3 - 데이터의 사본을 3개 유지                                 │
│  ↓                                                           │
│  1) 원본 데이터                                               │
│  2) 로컬 백업 (스냅샷)                                       │
│  3) 원격 백업 (다른 리전)                                     │
│                                                             │
│  2 - 2개의 다른 스토리지 미디어에 저장                         │
│  ↓                                                           │
│  1) 디스크 스토리지 (EBS, Managed Disk)                       │
│  2) 오브젝트 스토리지 (S3, Blob Storage)                     │
│                                                             │
│  1 - 1개의 사본은 오프사이트(다른 리전)에 저장                 │
│  ↓                                                           │
│  1) 교차 리전 복제(CRR), 리전 간 백업                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 8. 복구 테스트 (Disaster Recovery Drill)

```bash
# 정기적인 복구 테스트 수행

# 1) 최신 스냅샷에서 새로운 볼륨 생성
aws ec2 create-volume \
  --snapshot-id snap-xxxxxxxx \
  --availability-zone ap-northeast-2a

# 2) 테스트 인스턴스에 볼륨 연결
aws ec2 attach-volume \
  --volume-id vol-yyyyyyyy \
  --instance-id i-test \
  --device /dev/sdf

# 3) 데이터 무결성 확인
# 4) 테스트 리소스 삭제
```

### 9. 백업 모니터링 및 알림

```bash
# CloudWatch 알람 생성
aws cloudwatch put-metric-alarm \
  --alarm-name "BackupFailure" \
  --alarm-description "Alert on backup failures" \
  --metric-name BackupJobStatus \
  --namespace AWS/Backup \
  --statistic Sum \
  --period 300 \
  --threshold 1 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --evaluation-periods 1
```

### 10. 조치 시 주의사항

| 주의사항 | 설명 |
|----------|------|
| **비용 관리** | 불필요한 백업 삭제, 생명주기 정책으로 비용 최적화 |
| **암호화** | 백업 데이터도 암호화 필수 |
| **복구 테스트** | 정기적 복구 테스트로 백업 유효성 검증 |
| **문서화** | 복구 절차 문서화 및 운영자 교육 |
| **격리** | 백업 데이터는 프로덕션과 격리하여 보관 |

### 11. 참고 자료

- **AWS Backup Documentation**: https://docs.aws.amazon.com/aws-backup/
- **Azure Backup Documentation**: https://docs.microsoft.com/azure/backup/
- **GCP Backup and DR**: https://cloud.google.com/backup-disaster-recovery

---

## 요약

**백업사용여부**는 클라우드 환경의 데이터 보호와 비즈니스 연속성을 위한 필수 항목입니다. AWS Backup, Azure Backup, Cloud SQL 백업 등 클라우드 제공사의 백업 서비스를 활용하여 자동화된 백업을 설정하세요. 3-2-1 백업 규칙을 준수하고 정기적으로 복구 테스트를 수행하여 백업의 유효성을 검증해야 합니다.

**핵심 액션 아이템**
1. EC2/VM 자동 백업 설정 (AMI, 스냅샷)
2. RDS/Cloud SQL 자동 백업 활성화
3. 3-2-1 백업 규칙 준수 (3개 사본, 2개 미디어, 1개 오프사이트)
4. 교차 리전 복제로 재해 복구 강화
5. 분기별 복구 테스트 수행
