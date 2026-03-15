---
title: "[2026 주요정보통신기반시설] CA-06 네트워크서비스정책관리"
slug: "2026-주정통/CA-06"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "가상 네트워크 서비스 리소스 생성 또는 접근 권한 설정 여부 점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Cloud
---

# CA-06 네트워크서비스정책관리

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | CA-06 |
| **점검내용** | 가상 네트워크 서비스 리소스 생성 또는 접근 권한 설정 여부 점검 |
| **점검대상** | 클라우드 플랫폼 |
| **판단기준** | 양호: 네트워크 서비스 리소스 접근 권한이 적절하게 부여된 경우 |
| **판단기준** | 취약: 네트워크 서비스 리소스 접근 권한이 적절하게 부여되지 않은 경우 |
| **조치방법** | 네트워크 서비스 리소스 생성 및 접근 권한을 관리자 계정에 별도로 부여 |

---
## 상세 설명

### 1. 항목 개요

클라우드 네트워크 서비스는 VPC(가상 사설 클라우드), 서브넷, 라우팅 테이블, 방화벽(보안 그룹), 로드 밸런서, DNS, NAT 게이트웨이, VPN 등 다양한 네트워크 리소스를 포함합니다. 이러한 네트워크 리소스에 대한 접근 권한이 적절하게 관리되지 않으면, 비인가자가 네트워크 구성을 변경하거나 내부 시스템에 침입할 수 있습니다.

### 2. 왜 이 항목이 필요한가요?

**보안 위협 시나리오:**
1. **네트워크 구성 변경**: 권한이 없는 사용자가 방화벽 규칙을 변경하여 외부 공격에 노출
2. **중간자 공격**: DNS 설정을 조작하여 트래픽을 악의적인 서버로 우회
3. **네트워크 스니핑**: 로드 밸런서 설정을 변경하여 민감한 트래픽을 가로챔
4. **서비스 거부**: 라우팅 테이블을 삭제하여 네트워크 서비스 중단

**실제 사례**
- 권한이 없는 사용자가 실수로 보안 그룹 규칙을 삭제하여 데이터베이스가 인터넷에 노출
- 악의적인 내부자가 NAT 게이트웨이 설정을 변경하여 모든 트래픽을 외부로 유출

### 3. 점검 대상

- 모든 클라우드 플랫폼 (AWS, Azure, GCP, Naver Cloud, Kakao Cloud 등)
- VPC 및 서브넷
- 방화벽 및 보안 그룹
- 로드 밸런서
- DNS (Route 53, Azure DNS, Cloud DNS 등)
- NAT 게이트웨이 및 인터넷 게이트웨이
- VPN Gateway 및 Direct Connect
- 라우팅 테이블

### 4. 판단 기준

| 구분 | 기준 |
|------|------|
| **양호** | 네트워크 서비스 리소스 접근 권한이 직무와 역할에 맞게 적절하게 부여된 경우 |
| **취약** | 네트워크 서비스 리소스 접근 권한이 적절하게 부여되지 않아 불필요한 변경이 가능한 경우 |

### 5. 점검 방법

#### Step 1: 네트워크 리소스 접근 권한 확인

```bash
# AWS CLI 예시
# VPC 및 네트워크 리소스 목록 확인
aws ec2 describe-vpcs
aws ec2 describe-subnets
aws ec2 describe-security-groups
aws ec2 describe-route-tables

# IAM 사용자별 네트워크 권한 확인
aws iam get-user-policy --user-name username --policy-name policy-name

# Azure CLI 예시
# VNet 및 네트워크 리소스 확인
az network vnet list
az network nsg list
az network lb list

# GCP CLI 예시
# VPC 및 방화벽 규칙 확인
gcloud compute networks list
gcloud compute firewall-rules list
```

#### Step 2: 불필요한 권한 식별

다음과 같은 권한을 식별합니다:
- 네트워크 구성 변경 권한을 가진 일반 운영자
- 모든 VPC에 대한 무제한 접근 권한
- 방화벽 규칙 수정 권한을 가진 비보안팀
- DNS 레코드 수정 권한을 가진 불필요한 계정

### 6. 조치 방법

#### Step 1: 네트워크 서비스 접근 권한 정비

```yaml
# AWS IAM 정책 예시 - 읽기 전용 네트워크 접근
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeVpcs",
        "ec2:DescribeSubnets",
        "ec2:DescribeSecurityGroups",
        "ec2:DescribeRouteTables",
        "ec2:DescribeNetworkAcls"
      ],
      "Resource": "*"
    }
  ]
}
```

```yaml
# AWS IAM 정책 예시 - 네트워크 관리자 전용 권한
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:*Vpc*",
        "ec2:*Subnet*",
        "ec2:*SecurityGroup*",
        "ec2:*RouteTable*",
        "ec2:*NetworkAcl*",
        "ec2:*InternetGateway*",
        "ec2:*NatGateway*"
      ],
      "Resource": "*"
    }
  ]
}
```

```bash
# AWS CLI - 네트워크 관리자에게만 권한 부여
aws iam put-user-policy \
  --user-name network-admin \
  --policy-name NetworkAdminPolicy \
  --policy-document file://network-admin-policy.json

# 일반 운영자에게는 읽기 권한만 부여
aws iam put-user-policy \
  --user-name operator \
  --policy-name NetworkReadOnlyPolicy \
  --policy-document file://network-readonly-policy.json
```

#### Step 2: 네트워크 리소스별 접근 제어

```bash
# AWS - 특정 VPC에만 권한 제한
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:Describe*"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ec2:ModifyVpcAttribute",
        "ec2:DeleteVpc"
      ],
      "Resource": "arn:aws:ec2:region:account-id:vpc/vpc-id"
    }
  ]
}
```

```bash
# Azure - 특정 VNet에만 네트워크 기여자 권한 부여
az role assignment create \
  --assignee user@example.com \
  --role Network Contributor \
  --scope /subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.Network/virtualNetworks/{vnet-name}
```

```bash
# GCP - 특정 VPC에만 네트워크 관리자 권한 부여
gcloud projects add-iam-policy-binding project-id \
  --member=user:user@example.com \
  --role=roles/compute.networkAdmin \
  --condition=expression="resource.name.contains('projects/project-id/global/networks/vpc-name'"
```

#### Step 3: 방화벽 및 보안 그룹 권한 제한

```yaml
# AWS - 보안 그룹 관리는 보안팀에만 허용
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "SecurityGroupManagement",
      "Effect": "Allow",
      "Action": [
        "ec2:AuthorizeSecurityGroupIngress",
        "ec2:AuthorizeSecurityGroupEgress",
        "ec2:RevokeSecurityGroupIngress",
        "ec2:RevokeSecurityGroupEgress",
        "ec2:CreateSecurityGroup",
        "ec2:DeleteSecurityGroup"
      ],
      "Resource": "arn:aws:ec2:*:*:security-group/*",
      "Condition": {
        "StringEquals": {
          "aws:PrincipalTag/Department": "Security"
        }
      }
    }
  ]
}
```

### 7. 조치 시 주의사항

| 주의사항 | 설명 |
|----------|------|
| **네트워크 변경 영향 분석** | 네트워크 구성 변경은 전체 시스템에 영향을 미치므로 철저한 영향 분석 필요 |
| **변경 관리 프로세스** | 네트워크 리소스 변경 시 승인 프로세스 의무화 |
| **권한 변경 테스트** | 운영 환경 적용 전 테스트 환경에서 검증 |
| **긴급 복구 절차** | 네트워크 장애 시 신속한 복구를 위한 절차 마련 |

### 8. 참고 자료

- **AWS VPC Best Practices**: https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Best_Practices.html
- **Azure Network Security Best Practices**: https://docs.microsoft.com/azure/security/fundamentals/network-best-practices
- **GCP Network Best Practices**: https://cloud.google.com/networking/docs/best-practices
- **CIS Amazon Web Services Foundations Benchmark**: Section 2 (Networking)

---

## 요약

**네트워크서비스정책관리**는 클라우드 환경에서 네트워크 리소스를 보호하는 핵심 항목입니다. 네트워크 구성 변경 권한을 소수의 신뢰할 수 있는 네트워크 관리자에게만 부여하고, 일반 운영자에게는 읽기 권한만 제공하여 무단 변경을 방지해야 합니다.

**핵심 액션 아이템**
1. 네트워크 리소스별 접근 권한 식별 및 정비
2. 네트워크 관리자와 일반 운영자 권한 철저히 분리
3. 방화벽/보안 그룹 변경 권한은 보안팀에만 부여
4. 네트워크 변경 시 승인 프로세스 의무화
