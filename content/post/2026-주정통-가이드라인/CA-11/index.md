---
title: "[2026 주요정보통신기반시설] CA-11 관계형데이터베이스암호화설정"
slug: "2026-주정통/CA-11"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "관계형 데이터베이스 암호화 설정 여부 점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Cloud
---

# CA-11 관계형데이터베이스암호화설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | CA-11 |
| **점검내용** | 관계형 데이터베이스 암호화 설정 여부 점검 |
| **점검대상** | 클라우드 플랫폼 |
| **판단기준** | 양호: 관계형 데이터베이스 암호화가 적용된 경우 |
| **판단기준** | 취약: 관계형 데이터베이스 암호화가 적용되지 않은 경우 |
| **조치방법** | 관계형 데이터베이스 암호화 기능 활성화 설정 |

---
## 상세 설명

### 1. 항목 개요

클라우드 관계형 데이터베이스 서비스(RDS, Cloud SQL, Azure SQL 등)는 저장 데이터 암호화(Encryption at Rest) 기능을 제공합니다. 이 기능은 데이터베이스의 스토리지, 자동 백업, 읽기 전용 복제본, 스냅샷 등을 자동으로 암호화하여 데이터 유출 시에도 내용을 확인할 수 없도록 보호합니다.

### 2. 왜 이 항목이 필요한가요?

**보안 위협 시나리오:**
1. **스토리지 유출**: 하드 디스크 탈취나 스토리지 시스템 침해로 데이터 유출
2. **백업 파일 유출**: 암호화되지 않은 백업 파일이 유출되어 데이터 노출
3. **스냅샷 노출**: 공유된 스냅샷이 암호화되지 않아 민감 정보 노출
4. **규정 준수**: 개인정보보호법, 금융규정 등에서 암호화 의무화

**실제 사례**
- 2020년: 암호화되지 않은 데이터베이스 백업 파일이 유출되어 수만 명의 환자 정보 노출
- 클라우드 스냅샷이 실수로 공개되어 암호화되지 않은 데이터베이스 복제본이 공개

### 3. 점검 대상

- 모든 클라우드 플랫폼 (AWS, Azure, GCP, Naver Cloud, Kakao Cloud 등)
- Amazon RDS (MySQL, PostgreSQL, MariaDB, Oracle, SQL Server)
- Amazon Aurora
- Azure SQL Database
- Google Cloud SQL
- Naver Cloud DB
- 기타 관계형 데이터베이스 서비스

### 4. 판단 기준

| 구분 | 기준 |
|------|------|
| **양호** | 데이터베이스 스토리지 암호화가 활성화된 경우 |
| **취약** | 데이터베이스 스토리지 암호화가 비활성화된 경우 |

### 5. 점검 방법

#### Step 1: 암호화 설정 확인

```bash
# AWS CLI 예시
# RDS 인스턴스 암호화 확인
aws rds describe-db-instances \
  --query "DBInstances[].{DBInstanceIdentifier:DBInstanceIdentifier,StorageEncrypted:StorageEncrypted,KmsKeyId:KmsKeyId}"

# Aurora 클러스터 암호화 확인
aws rds describe-db-clusters \
  --query "DBClusters[].{DBClusterIdentifier:DBClusterIdentifier,StorageEncrypted:StorageEncrypted}"

# 암호화되지 않은 인스턴스 필터링
aws rds describe-db-instances \
  --query "DBInstances[?StorageEncrypted==`false`].{DBInstanceIdentifier:DBInstanceIdentifier,Engine:Engine}"
```

```bash
# Azure CLI 예시
# SQL Database 투명 데이터 암호화 확인
az sql db show \
  --name database-name \
  --server server-name \
  --resource-group group-name \
  --query "transparentDataEncryption"

# 모든 데이터베이스의 TDE 상태 확인
az sql db list --server server-name --resource-group group-name \
  --query "[].{Name:name,TDE:transparentDataEncryption.status}"
```

```bash
# GCP CLI 예시
# Cloud SQL 인스턴스 암호화 확인
gcloud sql instances describe instance-name \
  --format="table(name, diskEncryptionStatus)"

# 모든 인스턴스의 암호화 상태 확인
gcloud sql instances list --format="table(name,diskEncryptionStatus)"
```

#### Step 2: 백업 암호화 확인

```bash
# AWS - RDS 스냅샷 암호화 확인
aws rds describe-db-snapshots \
  --snapshot-type automated \
  --query "DBSnapshots[].{DBSnapshotIdentifier:DBSnapshotIdentifier,Encrypted:Encrypted}"

# 암호화되지 않은 스냅샷 찾기
aws rds describe-db-snapshots \
  --snapshot-type automated \
  --query "DBSnapshots[?Encrypted==`false`].DBSnapshotIdentifier"
```

### 6. 조치 방법

#### Step 1: 새 데이터베이스 암호화 활성화

```bash
# AWS - 새로운 RDS 인스턴스 생성 시 암호화 활성화
aws rds create-db-instance \
  --db-instance-identifier mydb \
  --db-instance-class db.t3.micro \
  --engine mysql \
  --master-username admin \
  --master-user-password mypassword \
  --allocated-storage 20 \
  --storage-encrypted \
  --kms-key-id alias/my-key

# Aurora 클러스터 생성 시 암호화 활성화
aws rds create-db-cluster \
  --db-cluster-identifier myaurora \
  --engine aurora-mysql \
  --master-username admin \
  --master-user-password mypassword \
  --storage-encrypted \
  --kms-key-id alias/my-key
```

```bash
# Azure - SQL Database 생성 시 TDE 활성화
az sql db create \
  --name database-name \
  --server server-name \
  --resource-group group-name \
  --transparent-data-encryption true
```

```bash
# GCP - Cloud SQL 인스턴스 생성 시 암호화 활성화
gcloud sql instances create instance-name \
  --tier db-n1-standard-1 \
  --database-version MYSQL_5_7 \
  --region us-central1 \
  --disk-encryption-key projects/my-project/locations/us-central1/keyRings/my-key-ring/cryptoKeys/my-key
```

#### Step 2: 기존 데이터베이스 암호화 적용

**AWS RDS의 경우:**
RDS 인스턴스는 생성 후 암호화를 직접 활성화할 수 없습니다. 스냅샷을 생성하고 새 인스턴스를 복원해야 합니다.

```bash
# 1) 암호화되지 않은 인스턴스의 스냅샷 생성
aws rds create-db-snapshot \
  --db-instance-identifier mydb \
  --db-snapshot-identifier mydb-snapshot

# 2) 스냅샷 복사 시 암호화 적용
aws rds copy-db-snapshot \
  --source-db-snapshot-identifier mydb-snapshot \
  --target-db-snapshot-identifier mydb-snapshot-encrypted \
  --kms-key-id alias/my-key

# 3) 암호화된 스냅샷에서 새 인스턴스 복원
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier mydb-encrypted \
  --db-snapshot-identifier mydb-snapshot-encrypted

# 4) 트래픽을 새 인스턴스로 전환
# (DNS 레코드 변경 또는 애플리케이션 설정 수정)

# 5) 이전 인스턴스 삭제
aws rds delete-db-instance \
  --db-instance-identifier mydb \
  --skip-final-snapshot
```

#### Step 3: CMK(Customer Managed Key) 사용

```bash
# AWS - KMS 키 생성
aws kms create-key \
  --description "RDS encryption key" \
  --key-usage ENCRYPT_DECRYPT

# 키에 별칭 부여
aws kms create-alias \
  --alias-name alias/rds-key \
  --target-key-id key-id

# 키 정책 설정
aws kms put-key-policy \
  --key-id key-id \
  --policy-name default \
  --policy file://key-policy.json
```

```json
// key-policy.json 예시
{
  "Version": "2012-10-17",
  "Id": "rds-key-policy",
  "Statement": [
    {
      "Sid": "Enable IAM User Permissions",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::123456789012:user/admin"
      },
      "Action": "kms:*",
      "Resource": "*"
    },
    {
      "Sid": "Allow RDS to use the key",
      "Effect": "Allow",
      "Principal": {
        "Service": "rds.amazonaws.com"
      },
      "Action": [
        "kms:Encrypt",
        "kms:Decrypt",
        "kms:ReEncrypt*",
        "kms:GenerateDataKey*",
        "kms:DescribeKey"
      ],
      "Resource": "*"
    }
  ]
}
```

### 7. 암호화 방식 이해

| 암호화 유형 | 설명 | 키 관리 |
|------------|------|---------|
| **AWS KMS 기본 키** | AWS가 관리하는 키로 자동으로 암호화 | AWS 관리 |
| **CMK(Customer Managed Key)** | 사용자가 직접 관리하는 키 | 사용자 관리 |
| **Cloud HSM** | 하드웨어 보안 모듈을 사용한 암호화 | 하드웨어 보안 모듈 |

### 8. 조치 시 주의사항

| 주의사항 | 설명 |
|----------|------|
| **다운타임** | AWS RDS는 스냅샷 복원 방식으로 인해 다운타임 발생 |
| **성능 영향** | 암호화는 일반적으로 1-5%의 성능 저하가 있음 |
| **키 회전** | KMS 키 주기적 회전(Yearly) 권장 |
| **키 삭제 방지** | KMS 키 삭제 시 데이터 복구 불가능 |
| **백업 확인** | 모든 백업과 스냅샷도 암호화되는지 확인 |

### 9. 참고 자료

- **AWS RDS Encryption**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Overview.Encryption.html
- **Azure SQL Database TDE**: https://docs.microsoft.com/azure/azure-sql/database/transparent-data-encryption-tde-overview
- **GCP Cloud SQL Encryption**: https://cloud.google.com/sql/docs/mysql/encryption
- **AWS KMS Documentation**: https://docs.aws.amazon.com/kms/

---

## 요약

**관계형데이터베이스암호화설정**은 데이터베이스에 저장된 민감 정보를 보호하는 필수 항목입니다. 클라우드 데이터베이스 서비스는 스토리지 수준의 암호화를 제공하므로 이를 활성화하여 스토리지 유출, 백업 유출, 스냅샷 유출 등의 위협으로부터 데이터를 보호해야 합니다. 가능하다면 CMK(Customer Managed Key)를 사용하여 키를 직접 관리하는 것을 권장합니다.

**핵심 액션 아이템**
1. 모든 데이터베이스 인스턴스 암호화 활성화
2. 백업 및 스냅샷 암호화 확인
3. CMK(Customer Managed Key) 사용으로 키 관리 강화
4. 키 회전(Key Rotation) 정책 수립
5. 암호화를 고려하여 설계 (신규 데이터베이스 생성 시)
