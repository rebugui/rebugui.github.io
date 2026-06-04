---
title: "[2026 주요정보통신기반시설] CA-10 스토리지리소스퍼블릭접근관리"
slug: "2026-주정통/CA-10"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "스토리지 리소스에 모든 인터넷 사용자 접근 권한의 차단 여부 점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Cloud
---

# CA-10 스토리지리소스퍼블릭접근관리

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | CA-10 |
| **점검내용** | 스토리지 리소스에 모든 인터넷 사용자 접근 권한의 차단 여부 점검 |
| **점검대상** | 클라우드 플랫폼 |
| **판단기준** | 양호: 스토리지 리소스에 불필요한 규칙이 존재하지 않고 접근 제어 정책을 주기적으로 검토하는 경우 |
| **판단기준** | 취약: 스토리지 리소스에 불필요한 규칙이 존재하거나 접근 제어 정책을 비주기적으로 검토하는 경우 |
| **조치방법** | 스토리지 리소스에 모든 인터넷 사용자 접근 권한 차단 설정 |

---
## 상세 설명

### 1. 항목 개요

클라우드 스토리지(S3, Azure Blob Storage, GCP Cloud Storage 등)는 편리한 데이터 저장 및 공유 기능을 제공하지만, 잘못된 접근 제어 설정으로 인해 대규모 데이터 유출 사고가 발생하고 있습니다. 특히 "퍼블릭 액세스" 설정은 전 세계 누구나 데이터에 접근할 수 있게 만들어 가장 위험한 설정입니다.

### 2. 왜 이 항목이 필요한가요?

**보안 위협 시나리오:**
1. **퍼블릭 S3 버킷**: 실수로 S3 버킷을 퍼블릭으로 설정하여 수천만 명의 개인정보 유출
2. **잘못된 ACL 설정**: 특정 사용자가 아닌 "AllUsers" 그룹에 읽기 권한 부여
3. **Bucket Policy 오류**: 조건문 실수로 모든 사용자에게 접근 권한 부여
4. **미인식 퍼블릭 접근**: 테스트용으로 만든 버킷이 그대로 퍼블릭으로 방치

**실제 사례**
- 2017년: 미국 방위산업체의 S3 버킷이 퍼블릭으로 노출되어 6만 건 이상의 기밀 문서 유출
- 2018년: 정치적 분석 회사의 S3 버킷이 퍼블릭으로 노출되어 2억 3천만 명 이상의 미국 유권자 정보 유출
- 2019년: 금융 서비스 회사의 S3 버킷이 퍼블릭으로 노출되어 1억 5천만 명의 금융 데이터 유출

### 3. 점검 대상

- 모든 클라우드 플랫폼 (AWS, Azure, GCP, Naver Cloud, Kakao Cloud 등)
- S3 버킷 (AWS)
- Azure Blob Storage
- GCP Cloud Storage 버킷
- Naver Cloud Object Storage
- 기타 오브젝트 스토리지

### 4. 판단 기준

| 구분 | 기준 |
|------|------|
| **양호** | 스토리지 리소스에 불필요한 퍼블릭 접근 권한이 없고, 접근 제어 정책을 주기적으로 검토하는 경우 |
| **취약** | 스토리지 리소스에 퍼블릭 접근 권한이 있거나, 접근 제어 정책을 비주기적으로 검토하는 경우 |

### 5. 점검 방법

#### Step 1: 퍼블릭 액세스 설정 확인

```bash
# AWS CLI 예시
# 모든 S3 버킷의 퍼블릭 액세스 설정 확인
aws s3 ls

# 버킷별 퍼블릭 액세스 설정 확인
aws s3api get-bucket-policy-status --bucket bucket-name

# 모든 버킷의 ACL 설정 확인
for bucket in $(aws s3 ls | awk '{print $3}'); do
    echo "Bucket: $bucket"
    aws s3api get-bucket-acl --bucket $bucket
    echo "---"
done

# 버킷 정책 확인
aws s3api get-bucket-policy --bucket bucket-name

# 모든 버킷의 퍼블릭 액세스 블록 설정 확인
for bucket in $(aws s3 ls | awk '{print $3}'); do
    echo "Bucket: $bucket"
    aws s3api get-public-access-block --bucket $bucket
    echo "---"
done
```

```bash
# Azure CLI 예시
# Storage 계정의 퍼블릭 액세스 확인
az storage account show \
  --name storageaccountname \
  --resource-group group-name \
  --query "allowBlobPublicAccess"

# 컨테이너의 퍼블릭 액세스 확인
az storage container show-permission \
  --name container-name \
  --account-name storageaccountname
```

```bash
# GCP CLI 예시
# 버킷의 퍼블릭 액세스 확인
gsutil iam get gs://bucket-name

# allUsers 또는 allAuthenticatedUsers가 있는지 확인
gsutil iam get gs://bucket-name | grep -E "allUsers|allAuthenticatedUsers"
```

#### Step 2: 퍼블릭 접근 가능한 버킷 스캔

```python
# 파이썬을 활용한 퍼블릭 S3 버킷 스캐너
import boto3

s3 = boto3.client('s3')

def check_public_buckets():
    public_buckets = []
    response = s3.list_buckets()

    for bucket in response['Buckets']:
        bucket_name = bucket['Name']

        try:
            # 버킷 정책 확인
            policy = s3.get_bucket_policy(Bucket=bucket_name)
            policy_str = str(policy['Policy'])

            if 'allUsers' in policy_str or '*' in policy_str:
                public_buckets.append(bucket_name)

        except Exception as e:
            pass

        try:
            # ACL 확인
            acl = s3.get_bucket_acl(Bucket=bucket_name)
            for grant in acl['Grants']:
                if 'URI' in grant.get('Grantee', {}):
                    if 'allUsers' in grant['Grantee']['URI']:
                        public_buckets.append(bucket_name)
        except Exception as e:
            pass

    return public_buckets

if __name__ == "__main__":
    public = check_public_buckets()
    print(f"퍼블릭 접근 가능한 버킷: {len(public)}개")
    for bucket in public:
        print(f"- {bucket}")
```

### 6. 조치 방법

#### Step 1: 퍼블릭 액세스 차단

```bash
# AWS - S3 버킷 퍼블릭 액세스 차단
# 모든 퍼블릭 액세스 블록 설정
aws s3api put-public-access-block \
  --bucket bucket-name \
  --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

# 계정 수준에서 모든 버킷에 퍼블릭 액세스 차단
aws s3control put-public-access-block \
  --account-id 123456789012 \
  --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
```

```bash
# AWS - 기존 퍼블릭 ACL 제거
# 버킷 ACL을 private으로 설정
aws s3api put-bucket-acl \
  --bucket bucket-name \
  --acl private

# 객체 ACL을 private으로 설정
aws s3api put-object-acl \
  --bucket bucket-name \
  --key object-name \
  --acl private
```

```bash
# Azure - Storage 계정의 퍼블릭 액세스 비활성화
az storage account update \
  --name storageaccountname \
  --resource-group group-name \
  --allow-blob-public-access false

# 컨테이너를 private으로 설정
az storage container set-permission \
  --name container-name \
  --account-name storageaccountname \
  --public-access off
```

```bash
# GCP - 버킷의 퍼블릭 액세스 제거
# allUsers 또는 allAuthenticatedUsers 제거
gsutil iam ch -d allUsers gs://bucket-name
gsutil iam ch -d allAuthenticatedUsers gs://bucket-name
```

#### Step 2: 접근 제어 정책 설정

```json
// AWS S3 Bucket Policy 예시 - 특정 IP만 허용
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowOnlyFromSpecificIP",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::123456789012:user/username"
      },
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::bucket-name",
        "arn:aws:s3:::bucket-name/*"
      ],
      "Condition": {
        "IpAddress": {
          "aws:SourceIp": [
            "203.0.113.0/24",
            "198.51.100.0/24"
          ]
        }
      }
    }
  ]
}
```

```bash
# 버킷 정책 적용
aws s3api put-bucket-policy \
  --bucket bucket-name \
  --policy file://bucket-policy.json
```

```json
// AWS S3 Bucket Policy 예시 - VPC 엔드포인트만 허용
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowOnlyFromVPC",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::bucket-name",
        "arn:aws:s3:::bucket-name/*"
      ],
      "Condition": {
        "StringNotEquals": {
          "aws:SourceVpce": "vpce-xxxxxxxx"
        }
      }
    }
  ]
}
```

#### Step 3: VPC 엔드포인트를 통한 격리된 접근

```bash
# AWS - S3 VPC 엔드포인트 생성
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-xxxxxxxx \
  --service-name com.amazonaws.ap-northeast-2.s3 \
  --vpc-endpoint-type Interface \
  --subnet-ids subnet-private-1 subnet-private-2 \
  --security-group-ids sg-endpoint

# 버킷 정책으로 VPC 엔드포인트에서만 접근 허용
aws s3api put-bucket-policy \
  --bucket bucket-name \
  --policy file://vpc-only-policy.json
```

#### Step 4: CloudFront를 통한 CDN 및 접근 제어

```bash
# AWS - CloudFront Origin Access Control 생성
aws cloudfront create-origin-access-control \
  --origin-access-control-config "Name=OAC-for-S3,Description='Origin Access Control for S3',SigningProtocol=sigv4,SigningBehavior=always,OriginAccessControlOriginType=s3"

# CloudFront 배포 생성
aws cloudfront create-distribution \
  --distribution-config file://cloudfront-config.json

# S3 버킷 정책으로 CloudFront만 접근 허용
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowCloudFront",
      "Effect": "Allow",
      "Principal": {
        "Service": "cloudfront.amazonaws.com"
      },
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::bucket-name/*",
      "Condition": {
        "StringEquals": {
          "AWS:SourceArn": "arn:aws:cloudfront::123456789012:distribution/distribution-id"
        }
      }
    }
  ]
}
```

### 7. 암호화 설정 추가

```bash
# AWS - S3 버킷 기본 암호화 설정
aws s3api put-bucket-encryption \
  --bucket bucket-name \
  --server-side-encryption-configuration '{
    "Rules": [
      {
        "ApplyServerSideEncryptionByDefault": {
          "SSEAlgorithm": "AES256"
        }
      }
    ]
  }'

# 버전 관리 활성화
aws s3api put-bucket-versioning \
  --bucket bucket-name \
  --versioning-configuration Status=Enabled

# 객체 잠금 활성화 (WORM - Write Once Read Many)
aws s3api put-object-lock-configuration \
  --bucket bucket-name \
  --object-lock-configuration '{
    "ObjectLockEnabled": "Enabled",
    "Rule": {
      "DefaultRetention": {
        "Mode": "GOVERNANCE",
        "Days": 30
      }
    }
  }'
```

### 8. 조치 시 주의사항

| 주의사항 | 설명 |
|----------|------|
| **애플리케이션 영향** | 퍼블릭 접근을 차단하면 애플리케이션에서 접근 불가능할 수 있음 |
| **CDN 사용 시** | 정적 컨텐츠는 CloudFront를 통해서만 제공하도록 설정 |
| **로그 분석** | S3 Access Log를 활성화하여 접근 패턴 모니터링 |
| **감사 경고** | Macie, Security Hub를 활용한 퍼블릭 접근 감시 |
| **정기적 검토** | 분기별 버킷 정책 및 ACL 검토 |

### 9. 참고 자료

- **AWS S3 Security Best Practices**: https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html
- **Protecting data with encryption**: https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucket-encryption.html
- **Azure Storage Security Recommendations**: https://docs.microsoft.com/azure/storage/common/storage-security-recommendations
- **GCP Cloud Storage Security**: https://cloud.google.com/storage/docs/security-best-practices

---

## 요약

**스토리지리소스퍼블릭접근관리**는 클라우드 데이터 보안의 가장 기본적이고 중요한 항목입니다. 스토리지 버킷의 퍼블릭 액세스를 차단하고, VPC 엔드포인트, CloudFront, IAM 정책 등을 활용하여 필요한 사용자만 접근할 수 있도록 제한해야 합니다. 대규모 데이터 유출 사고를 방지하기 위해 반드시 퍼블릭 액세스를 차단하세요.

**핵심 액션 아이템**
1. 모든 S3 버킷의 퍼블릭 액세스 차단
2. ACL 대신 Bucket Policy 및 IAM 사용
3. VPC 엔드포인트를 통한 격리된 접근
4. CloudFront + OAC를 통한 안전한 CDN 구성
5. 버킷 암호화 및 버전 관리 활성화
