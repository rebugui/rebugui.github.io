---
title: "[2026 주요정보통신기반시설] CA-07 VPC네트워크서브넷관리"
slug: "2026-주정통/CA-07"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "단일 가상 네트워크 내 Public/Private 서브넷을 혼용하여 사용하는지 여부 점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Cloud
draft: true
---

# CA-07 VPC네트워크서브넷관리

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | CA-07 |
| **점검내용** | 단일 가상 네트워크 내 Public/Private 서브넷을 혼용하여 사용하는지 여부 점검 |
| **점검대상** | 클라우드 플랫폼 |
| **판단기준** | 양호: 공개용 네트워크와 내부 네트워크를 분리한 경우 |
| **판단기준** | 취약: 공개용 네트워크와 내부 네트워크를 분리하지 않은 경우 |
| **조치방법** | 각 서브넷별 네트워크 리소스 설정 |

---
## 상세 설명

### 1. 항목 개요

VPC(Virtual Private Cloud) 내에서 서브넷은 IP 주소 범위를 분할하는 네트워크 영역입니다. **Public 서브넷**은 인터넷 게이트웨이를 통해 직접 인터넷과 통신할 수 있는 네트워크이고, **Private 서브넷**은 NAT 게이트웨이나 VPN을 통해서만 접근할 수 있는 내부 네트워크입니다. 이 두 서브넷을 적절하게 분리하지 않으면 내부 리소스가 외부에 노출될 수 있습니다.

### 2. 왜 이 항목이 필요한가요?

**보안 위협 시나리오:**
1. **Public 서브넷에 내부 리소스 배치**: 데이터베이스나 내부 애플리케이션을 Public 서브넷에 배치하면 인터넷에서 직접 접근 가능
2. **잘못된 라우팅 설정**: Private 서브넷의 트래픽이 인터넷 게이트웨이를 통해 외부로 유출
3. **보안 그룹 설정 오류**: Public 서브넷과 Private 서브넷 간의 격리가 제대로 이루어지지 않음

**실제 사례**
- Public 서브넷에 배치된 데이터베이스가 인터넷에서 직접 접속 가능하여 대규모 데이터 유출 사고 발생
- Private 서브넷의 인스턴스에 퍼블릭 IP가 할당되어 외부에서 직접 접속 가능

### 3. 점검 대상

- 모든 클라우드 플랫폼 (AWS, Azure, GCP, Naver Cloud, Kakao Cloud 등)
- VPC 및 서브넷 구성
- 인터넷 게이트웨이 및 NAT 게이트웨이
- 라우팅 테이블

### 4. 판단 기준

| 구분 | 기준 |
|------|------|
| **양호** | 공개용 네트워크(Public 서브넷)와 내부 네트워크(Private 서브넷)가 철저히 분리된 경우 |
| **취약** | 공개용 네트워크와 내부 네트워크가 분리되지 않아 Private 리소스가 외부에 노출된 경우 |

### 5. 점검 방법

#### Step 1: VPC 및 서브넷 구성 확인

```bash
# AWS CLI 예시
# VPC 목록 확인
aws ec2 describe-vpcs

# 서브넷 목록 확인
aws ec2 describe-subnets

# Public 서브넷 식별 (인터넷 게이트웨이가 연결된 서브넷)
aws ec2 describe-route-tables --query "RouteTables[?Routes[?GatewayId!='null']]"

# Private 서브넷 식별 (NAT 게이트웨이가 연결된 서브넷)
aws ec2 describe-route-tables --query "RouteTables[?Routes[?NatGatewayId!='null']]"
```

```bash
# Azure CLI 예시
# VNet 및 서브넷 확인
az network vnet list
az network vnet subnet list --vnet-name vnet-name

# Public IP가 할당된 리소스 확인
az network public-ip list
```

```bash
# GCP CLI 예시
# VPC 및 서브넷 확인
gcloud compute networks list
gcloud compute networks subnets list

# Private IP Google Access 설정 확인
gcloud compute networks subnets describe subnet-name --region region
```

#### Step 2: 서브넷별 리소스 배치 확인

```bash
# AWS - 서브넷별 인스턴스 확인
aws ec2 describe-instances --query "Reservations[].Instances[].{InstanceId:InstanceId,SubnetId:SubnetId,PrivateIpAddress:PrivateIpAddress,PublicIpAddress:PublicIpAddress}"

# Public IP를 가진 인스턴스 식별
aws ec2 describe-instances --query "Reservations[].Instances[?PublicIpAddress!=null]"
```

#### Step 3: 라우팅 테이블 확인

```bash
# AWS - 라우팅 테이블 확인
aws ec2 describe-route-tables --route-table-ids rtb-xxxxxxxx

# Public 서브넷의 라우팅 테이블 (0.0.0.0/0 -> igw-xxxxxxx)
# Private 서브넷의 라우팅 테이블 (0.0.0.0/0 -> nat-xxxxxxx)
```

### 6. 조치 방법

#### Step 1: Public/Private 서브넷 분리 설계

```
┌─────────────────────────────────────────────────────────┐
│                        VPC                               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────┐         ┌──────────────────┐     │
│  │  Public Subnet   │         │ Private Subnet   │     │
│  │  (10.0.1.0/24)   │         │  (10.0.2.0/24)   │     │
│  ├──────────────────┤         ├──────────────────┤     │
│  │                  │         │                  │     │
│  │  - Web Server    │         │  - Application  │     │
│  │  - Load Balancer │         │  - Database     │     │
│  │  - NAT Gateway   │         │  - Cache        │     │
│  │                  │         │                  │     │
│  │  [Public IP]     │         │  [Private IP]   │     │
│  │       │          │         │       │          │     │
│  │       ▼          │         │       ▼          │     │
│  │  Internet Gateway│         │  NAT Gateway    │     │
│  │       │          │         │       │          │     │
│  └───────┼──────────┘         └───────┼──────────┘     │
│          │                            │                │
│          ▼                            ▼                │
│       Internet                    Internet             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

#### Step 2: Public 서브넷 구성

```bash
# AWS - Public 서브넷 생성
aws ec2 create-subnet \
  --vpc-id vpc-xxxxxxxx \
  --cidr-block 10.0.1.0/24 \
  --availability-zone ap-northeast-2a

# 인터넷 게이트웨이 생성 및 VPC 연결
aws ec2 create-internet-gateway
aws ec2 attach-internet-gateway \
  --vpc-id vpc-xxxxxxxx \
  --internet-gateway-id igw-xxxxxxxx

# 라우팅 테이블 생성 및 Public 서브넷 연결
aws ec2 create-route-table --vpc-id vpc-xxxxxxxx
aws ec2 associate-route-table \
  --route-table-id rtb-public \
  --subnet-id subnet-public

# 인터넷으로의 라우팅 추가
aws ec2 create-route \
  --route-table-id rtb-public \
  --destination-cidr-block 0.0.0.0/0 \
  --gateway-id igw-xxxxxxxx

# 퍼블릭 IP 자동 할당 활성화
aws ec2 modify-subnet-attribute \
  --subnet-id subnet-public \
  --map-public-ip-on-launch
```

#### Step 3: Private 서브넷 구성

```bash
# AWS - Private 서브넷 생성
aws ec2 create-subnet \
  --vpc-id vpc-xxxxxxxx \
  --cidr-block 10.0.2.0/24 \
  --availability-zone ap-northeast-2a

# NAT 게이트웨이 생성 (Public 서브넷에 배치)
aws ec2 allocate-address --domain vpc
aws ec2 create-nat-gateway \
  --subnet-id subnet-public \
  --allocation-id eipalloc-xxxxxxxx

# Private 서브넷용 라우팅 테이블 생성
aws ec2 create-route-table --vpc-id vpc-xxxxxxxx
aws ec2 associate-route-table \
  --route-table-id rtb-private \
  --subnet-id subnet-private

# NAT 게이트웨이를 통한 인터넷 라우팅
aws ec2 create-route \
  --route-table-id rtb-private \
  --destination-cidr-block 0.0.0.0/0 \
  --nat-gateway-id nat-xxxxxxxx

# 퍼블릭 IP 자동 할당 비활성화
aws ec2 modify-subnet-attribute \
  --subnet-id subnet-private \
  --no-map-public-ip-on-launch
```

#### Step 4: 보안 그룹으로 네트워크 격리 강화

```bash
# Public 서브넷용 보안 그룹 (웹 서버)
aws ec2 create-security-group \
  --group-name web-server-sg \
  --description "Security group for web servers in public subnet" \
  --vpc-id vpc-xxxxxxxx

# HTTP/HTTPS만 허용
aws ec2 authorize-security-group-ingress \
  --group-id sg-web-server \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-id sg-web-server \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0
```

```bash
# Private 서브넷용 보안 그룹 (데이터베이스)
aws ec2 create-security-group \
  --group-name database-sg \
  --description "Security group for databases in private subnet" \
  --vpc-id vpc-xxxxxxxx

# Public 서브넷에서만 접근 허용
aws ec2 authorize-security-group-ingress \
  --group-id sg-database \
  --protocol tcp \
  --port 3306 \
  --source-group sg-web-server

# SSH는 관리자 IP에서만 허용
aws ec2 authorize-security-group-ingress \
  --group-id sg-database \
  --protocol tcp \
  --port 22 \
  --cidr 203.0.113.0/24
```

### 7. 조치 시 주의사항

| 주의사항 | 설명 |
|----------|------|
| **네트워크 설계** | 애플리케이션 아키텍처에 맞게 Public/Private 서브넷 설계 |
| **가용성 영역 분리** | 여러 가용성 영역(AZ)에 서브넷 분산 배치 |
| **IP 주소 계획** | 향후 확장을 고려한 CIDR 블록 설계 |
| **라우팅 테스트** | 변경 후 네트워크 통신 테스트 필수 |

### 8. 참고 자료

- **AWS VPC Documentation**: https://docs.aws.amazon.com/vpc/
- **Azure Virtual Network Documentation**: https://docs.microsoft.com/azure/virtual-network/
- **GCP VPC Documentation**: https://cloud.google.com/vpc/docs
- **CIS Amazon Web Services Foundations Benchmark**: Section 4 (Networking)

---

## 요약

**VPC네트워크서브넷관리**는 클라우드 네트워크 보안의 기초입니다. Public 서브넷에는 인터넷에서 접근해야 하는 리소스만 배치하고, Private 서브넷에는 데이터베이스와 내부 애플리케이션을 배치하여 네트워크 계층에서 보안을 강화해야 합니다.

**핵심 액션 아이템**
1. Public/Private 서브넷 철저한 분리
2. Public 서브넷: 웹 서버, 로드 밸런서, NAT 게이트웨이 배치
3. Private 서브넷: 데이터베이스, 애플리케이션 서버, 캐시 배치
4. 라우팅 테이블과 보안 그룹으로 네트워크 격리 강화
