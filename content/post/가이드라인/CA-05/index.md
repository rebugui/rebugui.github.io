---
title: "[2026 주요정보통신기반시설] CA-05 인스턴스서비스정책관리"
slug: "2026-주정통/CA-05"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "인스턴스 생성 또는 접근 권한 설정 여부 점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Cloud
---

# CA-05 인스턴스서비스정책관리

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | CA-05 |
| **점검내용** | 인스턴스 생성 또는 접근 권한 설정 여부 점검 |
| **점검대상** | 클라우드 플랫폼 |
| **판단기준** | 양호: 인스턴스 접근 권한이 적절하게 부여된 경우 |
| **판단기준** | 취약: 인스턴스 접근 권한이 적절하게 부여되지 않은 경우 |
| **조치방법** | 인스턴스 생성 및 접근 권한을 관리자 계정에 별도로 부여 |

---
## 상세 설명

### 1. 항목 개요

클라우드 인스턴스는 가상 머신(VM), 컨테이너, 데이터베이스, 마이크로서비스 등 다양한 형태의 컴퓨팅 리소스를 의미합니다. 이러한 인스턴스에 대한 접근 권한이 적절하게 관리되지 않으면, 비인가자가 중요 시스템과 데이터에 접근할 수 있게 되어 심각한 보안 사고로 이어질 수 있습니다.

### 2. 왜 이 항목이 필요한가요?

**보안 위협 시나리오:**
1. **권한 과대 부여**: 일반 운영자에게 인스턴스 생성/삭제 권한을 부여하면, 실수로 중요 인스턴스를 삭제하거나 악의적인 행위를 할 수 있습니다
2. **무분별한 접근 허용**: 불필요한 사용자에게 인스턴스 접근 권한이 부여되면, 내부 정보 유출 위험이 증가합니다
3. **관리 권한 남용**: 최고 관리자 권한을 가진 계정이 탈취당할 경우, 모든 인스턴스를 장악당할 수 있습니다

**실제 사례**
- 권한이 없는 직원이 실수로 운영 서버 인스턴스를 삭제하여 서비스 중단 사고 발생
- 퇴사자의 계정이 삭제되지 않아 인스턴스에 접근하여 데이터 유출

### 3. 점검 대상

- 모든 클라우드 플랫폼 (AWS, Azure, GCP, Naver Cloud, Kakao Cloud 등)
- EC2, Azure VM, GCE 등 가상 머신 인스턴스
- 컨테이너 인스턴스 (ECS, EKS, AKS, GKE 등)
- 데이터베이스 인스턴스 (RDS, Azure SQL, Cloud SQL 등)

### 4. 판단 기준

| 구분 | 기준 |
|------|------|
| **양호** | 인스턴스 접근 권한이 직무와 역할에 맞게 적절하게 부여된 경우 |
| **취약** | 인스턴스 접근 권한이 적절하게 부여되지 않아 불필요한 접근이 가능한 경우 |

### 5. 점검 방법

#### Step 1: 인스턴스 접근 권한 확인

```bash
# AWS CLI 예시
# EC2 인스턴스 목록 및 접근 권한 확인
aws ec2 describe-instances

# IAM 사용자별 EC2 접근 권한 확인
aws iam list-users
aws iam get-user-policy --user-name username --policy-name policy-name

# Azure CLI 예시
# VM 목록 확인
az vm list

# 사용자별 역할 할당 확인
az role assignment list --assignee user@example.com
```

#### Step 2: 불필요한 권한 식별

다음과 같은 권한을 식별합니다:
- 직무에 필요하지 않은 인스턴스 접근 권한
- 모든 인스턴스에 대한 무제한 접근 권한
- 인스턴스 생성/삭제 권한을 가진 일반 운영자 계정
- 퇴사자, 전직자의 인스턴스 접근 권한

### 6. 조치 방법

#### Step 1: 인스턴스 접근 권한 정비

```yaml
# AWS IAM 정책 예시 - 특정 인스턴스만 접근 허용
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "ec2:DescribeInstanceStatus"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ec2:StartInstances",
        "ec2:StopInstances",
        "ec2:RebootInstances"
      ],
      "Resource": "arn:aws:ec2:region:account-id:instance/instance-id"
    }
  ]
}
```

```bash
# AWS CLI - 특정 인스턴스에만 접근 권한 부여
aws iam put-user-policy \
  --user-name username \
  --policy-name EC2LimitedAccess \
  --policy-document file://policy.json
```

```bash
# Azure CLI - 특정 VM에만 Contributor 역할 부여
az role assignment create \
  --assignee user@example.com \
  --role Contributor \
  --scope /subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.Compute/virtualMachines/{vm-name}
```

#### Step 2: 최소 권한 원칙 적용

1. **역할 분리**: 인스턴스 생성/삭제 권한과 운영 권한 분리
2. **리소스별 권한**: 특정 인스턴스 또는 리소스 그룹에만 권한 부여
3. **시간 기반 권한**: 임시 권한 부여 (Just-In-Time Access)

```bash
# AWS - 태그 기반 접근 제어 예시
# Production 태그가 있는 인스턴스는 승인된 관리자만 접근 가능
{
  "Effect": "Deny",
  "Action": "ec2:*",
  "Resource": "*",
  "Condition": {
    "StringEquals": {
      "ec2:ResourceTag/Environment": "Production"
    }
  }
}
```

#### Step 3: 인스턴스별 접근 제어 설정

```bash
# AWS - 보안 그룹을 통한 접근 제어
# 특정 IP에서만 인스턴스 접근 허용
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxxxxx \
  --protocol tcp \
  --port 22 \
  --cidr 203.0.113.0/24
```

### 7. 조치 시 주의사항

| 주의사항 | 설명 |
|----------|------|
| **업무 영향도 확인** | 권한 변경 전 해당 사용자의 업무에 미치는 영향 확인 |
| **테스트 환경 검증** | 운영 환경 적용 전 테스트 환경에서 권한 검증 |
| **권한 변경 로그 기록** | 권한 변경 이력을 철저히 기록 |
| **긴급 상황 대비** | 긴급 시 권한을 신속하게 복구할 수 있는 절차 마련 |

### 8. 참고 자료

- **AWS IAM Best Practices**: https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html
- **Azure RBAC Documentation**: https://docs.microsoft.com/azure/role-based-access-control/
- **GCP IAM Documentation**: https://cloud.google.com/iam/docs
- **CIS Amazon Web Services Foundations Benchmark**: Section 1.1 (Identity and Access Management)

---

## 요약

**인스턴스서비스정책관리**는 클라우드 환경에서 가장 중요한 권한 관리 항목입니다. 최소 권한 원칙(Least Privilege)을 준수하여 직무에 필요한 최소한의 인스턴스 접근 권한만 부여하고, 정기적인 권한 검토를 통해 불필요한 권한을 제거해야 합니다.

**핵심 액션 아이템**
1. 인스턴스별 접근 권한 식별 및 정비
2. 최소 권한 원칙 적용 (직무별 권한 분리)
3. 리소스 태그를 활용한 세분화된 접근 제어
4. 정기적인 권한 검토 (반기별 권장)
