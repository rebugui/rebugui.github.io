---
title: "[2026 주요정보통신기반시설] CA-08 가상네트워크리소스관리"
slug: "2026-주정통/CA-08"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "내부 클라우드 리소스 접근 시 접근통제 적용 여부 점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Cloud
---

# CA-08 가상네트워크리소스관리

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | CA-08 |
| **점검내용** | 내부 클라우드 리소스 접근 시 접근통제 적용 여부 점검 |
| **점검대상** | 클라우드 플랫폼 |
| **판단기준** | 양호: 각 서비스 리소스에 공인 IP 주소가 존재하지 않고, 적절한 권한이 부여된 경우 |
| **판단기준** | 취약: 각 서비스 리소스에 공인 IP 주소가 존재하거나, 적절한 권한이 부여되지 않은 경우 |
| **조치방법** | 서비스 리소스에 공인 IP 주소 제거 및 관리자만 접근할 수 있도록 접근 권한 설정 |

---
## 상세 설명

### 1. 항목 개요

클라우드 환경에서 내부 리소스(데이터베이스, 캐시, 내부 API 등)에 불필요한 공인 IP 주소가 할당되면 외부에서 직접 접근이 가능해져 보안 위협에 노출됩니다. 이 항목은 내부 리소스에 공인 IP를 제거하고 사설 네트워크 내에서만 통신하도록 설정하여 외부 공격으로부터 보호하는 것을 목표로 합니다.

### 2. 왜 이 항목이 필요한가요?

**보안 위협 시나리오:**
1. **공인 IP 노출**: 내부 데이터베이스에 공인 IP가 할당되어 인터넷에서 직접 접속 가능
2. **무차별 대입 공격**: 공인 IP를 스캔하여 데이터베이스 포트에 대한 무차별 대입 공격 시도
3. **권한 상승**: 공인 IP를 통해 접속한 공격자가 취약점을 이용해 관리자 권한 획득
4. **데이터 유출**: 내부 리소스가 외부에 노출되어 중요 데이터 유출

**실제 사례**
- 공인 IP가 할당된 MongoDB 데이터베이스가 랜섬웨어 공격으로 데이터 암호화
- 공인 IP를 통해 접속 가능한 Redis 서버가 악용되어 암호화폐화 채굴에 활용

### 3. 점검 대상

- 모든 클라우드 플랫폼 (AWS, Azure, GCP, Naver Cloud, Kakao Cloud 등)
- 가상 머신 인스턴스
- 데이터베이스 (RDS, Cloud SQL, Azure SQL 등)
- 캐시 서비스 (ElastiCache, Redis 등)
- 로드 밸런서 내부 대상
- 컨테이너 및 쿠버네티스 클러스터

### 4. 판단 기준

| 구분 | 기준 |
|------|------|
| **양호** | 내부 리소스에 공인 IP가 없고, 사설 네트워크 내에서만 통신하며 적절한 접근 권한이 부여된 경우 |
| **취약** | 내부 리소스에 불필요한 공인 IP가 할당되어 있거나, 접근 권한이 적절하지 않은 경우 |

### 5. 점검 방법

#### Step 1: 공인 IP 할당 현황 확인

```bash
# AWS CLI 예시
# 공인 IP를 가진 인스턴스 확인
aws ec2 describe-instances \
  --query "Reservations[].Instances[?PublicIpAddress!=null].{InstanceId:InstanceId,PublicIp:PublicIpAddress,PrivateIp:PrivateIpAddress}"

# RDS 인스턴스의 퍼블릭 액세스 확인
aws rds describe-db-instances \
  --query "DBInstances[].{DBInstanceIdentifier:DBInstanceIdentifier,PubliclyAccessible:PubliclyAccessible,Endpoint:Endpoint.Address}"

# ElastiCache의 퍼블릭 액세스 확인
aws elasticache describe-cache-clusters \
  --show-cache-node-info \
  --query "CacheClusters[].{CacheClusterId:CacheClusterId,Engine:Engine,CacheNodes:CacheNodes[?Endpoint.Address!=`null`]}"
```

```bash
# Azure CLI 예시
# 퍼블릭 IP를 가진 VM 확인
az vm list --show-details --query "[?publicIps!=null]"

# Azure Database 퍼블릭 액세스 확인
az mysql server show --name server-name --resource-group group-name
az postgres server show --name server-name --resource-group group-name
```

```bash
# GCP CLI 예시
# 퍼블릭 IP를 가진 인스턴스 확인
gcloud compute instances list --filter="networkInterfaces.accessConfigs[*].natIP:*"

# Cloud SQL 퍼블릭 IP 확인
gcloud sql instances describe instance-name
```

#### Step 2: 내부 리소스 식별

내부용으로만 사용되어야 하는 리소스를 식별합니다:
- 데이터베이스 (MySQL, PostgreSQL, MongoDB, Redis 등)
- 캐시 서비스 (Memcached, Redis)
- 메시지 큐 (RabbitMQ, Kafka)
- 내부 API 서버
- 관리 도구 (Grafana, Kibana, Prometheus 등)

#### Step 3: 네트워크 접근 경로 확인

```bash
# AWS - 보안 그룹 규칙 확인
aws ec2 describe-security-groups \
  --group-ids sg-xxxxxxxx \
  --query "SecurityGroups[0].IpPermissions"

# 0.0.0.0/0으로 열린 포트 확인
aws ec2 describe-security-groups \
  --filters Name=ip-permission.cidr,Values="0.0.0.0/0" \
  --query "SecurityGroups[].{GroupId:GroupId,GroupName:GroupName,IpPermissions:IpPermissions}"
```

### 6. 조치 방법

#### Step 1: 공인 IP 주소 제거

```bash
# AWS - EC2 인스턴스에서 퍼블릭 IP 해제
# 방법 1: Elastic IP 해제
aws ec2 disassociate-address --association-id eipassoc-xxxxxxxx
aws ec2 release-address --allocation-id eipalloc-xxxxxxxx

# 방법 2: 인스턴스를 Private 서브넛으로 이동
# 1) 새로운 Private 서브넷 생성 (퍼블릭 IP 자동 할당 비활성화)
aws ec2 create-subnet \
  --vpc-id vpc-xxxxxxxx \
  --cidr-block 10.0.2.0/24

# 2) 인스턴스 중지
aws ec2 stop-instances --instance-ids i-xxxxxxxx

# 3) 인스턴스를 Private 서브넛으로 이동
aws ec2 modify-instance-attribute \
  --instance-id i-xxxxxxxx \
  --subnet-id subnet-private

# 4) 인스턴스 시작
aws ec2 start-instances --instance-ids i-xxxxxxxx
```

```bash
# AWS - RDS 퍼블릭 액세스 비활성화
aws rds modify-db-instance \
  --db-instance-identifier mydb \
  --no-publicly-accessible \
  --apply-immediately
```

```bash
# Azure - VM 퍼블릭 IP 제거
az network nic ip-config update \
  --nic-name nic-name \
  --name ipconfig-name \
  --resource-group group-name \
  --remove publicIpAddress

# Azure Database 퍼블릭 액세스 비활성화
az mysql server update \
  --name server-name \
  --resource-group group-name \
  --set publicNetworkAccess=Disabled
```

```bash
# GCP - 인스턴스 퍼블릭 IP 제거
gcloud compute instances delete-access-config instance-name \
  --access-config-name="external-nat" \
  --zone zone-name
```

#### Step 2: 사설 네트워크 통신 설정

```bash
# AWS - VPC 내부 통신을 위한 보안 그룹 설정
# 데이터베이스 보안 그룹 생성
aws ec2 create-security-group \
  --group-name database-private-sg \
  --description "Private database security group" \
  --vpc-id vpc-xxxxxxxx

# 애플리케이션 서버 보안 그룹에서만 접근 허용
aws ec2 authorize-security-group-ingress \
  --group-id sg-database \
  --protocol tcp \
  --port 3306 \
  --source-group sg-application

# SSH는 관리자 IP에서만 허용 (VPN을 통해서만)
aws ec2 authorize-security-group-ingress \
  --group-id sg-database \
  --protocol tcp \
  --port 22 \
  --cidr 10.0.0.0/16
```

#### Step 3: VPC Peering 또는 Private Link 설정

```bash
# AWS - VPC Peering을 통한 격리된 네트워크 연결
# Peering 연결 생성
aws ec2 create-vpc-peering-connection \
  --vpc-id vpc-aaaaaaaa \
  --peer-vpc-id vpc-bbbbbbbb \
  --peer-region ap-northeast-2

# Peering 연결 수락
aws ec2 accept-vpc-peering-connection \
  --vpc-peering-connection-id pcx-xxxxxxxx

# 라우팅 테이블에 Peering 경로 추가
aws ec2 create-route \
  --route-table-id rtb-aaaaaaaa \
  --destination-cidr-block 10.1.0.0/16 \
  --vpc-peering-connection-id pcx-xxxxxxxx
```

```bash
# AWS - PrivateLink를 통한 격리된 API 접근
# VPC Endpoint 생성
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-xxxxxxxx \
  --service-name com.amazonaws.ap-northeast-2.rds \
  --vpc-endpoint-type Interface \
  --subnet-ids subnet-private \
  --security-group-ids sg-private
```

#### Step 4: VPN 또는 Bastion Host를 통한 관리 접속

```bash
# AWS - Bastion Host (Jump Box) 배치
# Bastion Host용 보안 그룹
aws ec2 create-security-group \
  --group-name bastion-host-sg \
  --description "Security group for bastion host" \
  --vpc-id vpc-xxxxxxxx

# 관리자 IP에서만 SSH 허용
aws ec2 authorize-security-group-ingress \
  --group-id sg-bastion \
  --protocol tcp \
  --port 22 \
  --cidr 203.0.113.0/24

# 내부 리소스에서 Bastion Host로만 접근 허용
aws ec2 authorize-security-group-ingress \
  --group-id sg-database \
  --protocol tcp \
  --port 22 \
  --source-group sg-bastion
```

### 7. 조치 시 주의사항

| 주의사항 | 설명 |
|----------|------|
| **서비스 중단 방지** | 공인 IP 제거 전 반드시 사설 네트워크 경로 확인 |
| **애플리케이션 설정** | 데이터베이스 연결 문자열을 사설 IP로 변경 |
| **DNS 설정** | 내부 DNS를 사용하여 사설 IP로 리졸루션 |
| **접속 테스트** | 변경 후 반드시 내부 통신 테스트 수행 |
| **모니터링** | 네트워크 연결 상태 지속 모니터링 |

### 8. 참고 자료

- **AWS PrivateLink Documentation**: https://docs.aws.amazon.com/vpc/latest/privatelink/
- **Azure Private Link Documentation**: https://docs.microsoft.com/azure/private-link/
- **GCP Private Service Connect**: https://cloud.google.com/vpc/docs/private-service-connect
- **CIS Amazon Web Services Foundations Benchmark**: Section 4 (Networking)

---

## 요약

**가상네트워크리소스관리**는 클라우드 리소스를 외부 공격으로부터 보호하는 핵심 항목입니다. 내부 리소스에서 불필요한 공인 IP를 제거하고 사설 네트워크 내에서만 통신하도록 설정하여 보안을 강화해야 합니다. 관리 접속이 필요한 경우 VPN 또는 Bastion Host를 통해서만 허용해야 합니다.

**핵심 액션 아이템**
1. 내부 리소스의 공인 IP 주소 제거
2. 사설 네트워크(VPC) 내에서만 통신하도록 설정
3. 보안 그룹으로 내부 리소스 접근 제한
4. VPN 또는 Bastion Host를 통한 관리 접속만 허용
