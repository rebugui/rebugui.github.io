---
title: "[2026 주요정보통신기반시설] CA-09 접근제어설정관리"
slug: "2026-주정통/CA-09"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "불필요한 접근 정책 존재 여부 점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Cloud
---

# CA-09 접근제어설정관리

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | CA-09 |
| **점검내용** | 불필요한 접근 정책 존재 여부 점검 |
| **점검대상** | 클라우드 플랫폼 |
| **판단기준** | 양호: 접근 제어 정책을 주기적으로 검토하고 불필요한 규칙이 존재하지 않는 경우 |
| **판단기준** | 취약: 접근 제어 정책을 비주기적으로 검토하고 불필요한 규칙이 존재하는 경우 |
| **조치방법** | 접근 제어 정책 주기적 검토 및 불필요한 정책 제거 |

---
## 상세 설명

### 1. 항목 개요

클라우드 방화벽(보안 그룹, 네트워크 ACL, 방화벽 규칙 등)의 접근 제어 정책은 시간이 지남에 따라 누적되어 관리되지 않는 불필요한 규칙이 많아지게 됩니다. 이러한 "僵尸 규칙(Zombie Rules)"은 보안 위협을 증가시키고 관리 복잡성을 높입니다. 주기적인 검토와 정리가 필요합니다.

### 2. 왜 이 항목이 필요한가요?

**보안 위협 시나리오:**
1. **과도하게 열린 포트**: 테스트용으로 열어둔 포트가 그대로 방치되어 공격 경로가 됨
2. **0.0.0.0/0 규칙**: 모든 IP에서 접근을 허용하는 규칙이 불필요하게 존재
3. **폐기된 리소스용 규칙**: 삭제된 인스턴스나 서비스를 위한 규칙이 그대로 존재
4. **너무 넓은 IP 범위**: 특정 국가나 지역을 제한하지 않고 전 세계 접근을 허용

**실제 사례**
- 테스트용으로 열어둔 Redis 포트(6379)가 0.0.0.0/0으로 열려있어 랜섬웨어 공격 받음
- 3년 전 폐기된 프로젝트의 데이터베이스 포트가 그대로 열려있어 데이터 유출

### 3. 점검 대상

- 모든 클라우드 플랫폼 (AWS, Azure, GCP, Naver Cloud, Kakao Cloud 등)
- 보안 그룹(Security Group)
- 네트워크 ACL(Network Access Control List)
- 클라우드 방화벽(Cloud Firewall)
- VPC 방화벽 규칙

### 4. 판단 기준

| 구분 | 기준 |
|------|------|
| **양호** | 접근 제어 정책을 주기적으로 검토하고, 불필요한 규칙이 존재하지 않는 경우 |
| **취약** | 접근 제어 정책을 비주기적으로 검토하거나, 불필요한 규칙이 존재하는 경우 |

### 5. 점검 방법

#### Step 1: 열린 포트 및 IP 범위 확인

```bash
# AWS CLI 예시
# 모든 보안 그룹의 규칙 확인
aws ec2 describe-security-groups

# 0.0.0.0/0으로 열린 인바운드 규칙 확인
aws ec2 describe-security-groups \
  --filters Name=ip-permission.cidr,Values="0.0.0.0/0" \
  --query "SecurityGroups[].{GroupId:GroupId,GroupName:GroupName,IpPermissions:IpPermissions}"

# 특정 포트(예: 22, 3306, 6379)가 열린 규칙 확인
aws ec2 describe-security-groups \
  --filters Name=ip-permission.from-port,Values="22" \
  --query "SecurityGroups[].{GroupId:GroupId,IpPermissions:IpPermissions}"
```

```bash
# Azure CLI 예시
# NSG 규칙 확인
az network nsg list --query "[].{Name:name,Location:location,ResourceGroup:resourceGroup}"
az network nsg rule list --nsg-name nsg-name --resource-group group-name

# 모든 IP 허용 규칙 확인
az network nsg rule list --nsg-name nsg-name --resource-group group-name \
  --query "[?access=='Allow' && sourceAddressPrefix=='*']"
```

```bash
# GCP CLI 예시
# 방화벽 규칙 확인
gcloud compute firewall-rules list

# 모든 소스 IP 허용 규칙 확인
gcloud compute firewall-rules list --filter="sourceRanges:*"
```

#### Step 2: 사용하지 않는 보안 그룹 식별

```bash
# AWS - 인스턴스에 연결되지 않은 보안 그룹 확인
aws ec2 describe-network-interfaces \
  --query "NetworkInterfaces[].Groups[].GroupId" \
  | sort | uniq > used_sgs.txt

aws ec2 describe-security-groups \
  --query "SecurityGroups[].GroupId" \
  | sort | uniq > all_sgs.txt

# 사용하지 않는 보안 그룹 찾기
grep -v -f used_sgs.txt all_sgs.txt
```

#### Step 3: 규칙 사용 현황 분석

```bash
# AWS VPC Reachability Analyzer를 통한 규칙 분석
# 분석 생성
aws ec2 create-network-insights-path \
  --source ip-xxx.xxx.xxx.xxx \
  --destination ip-yyy.yyy.yyy.yyy \
  --protocol TCP \
  --destination-port 3306

# 분석 결과 확인
aws ec2 describe-network-insights-analyses \
  --network-insights-path-id path-xxxxxxxx
```

### 6. 조치 방법

#### Step 1: 불필요한 방화벽 규칙 제거

```bash
# AWS - 보안 그룹 규칙 제거
# 규칙 제거 전 규칙 ID 확인
aws ec2 describe-security-groups --group-ids sg-xxxxxxxx

# 인바운드 규칙 제거
aws ec2 revoke-security-group-ingress \
  --group-id sg-xxxxxxxx \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0

# 아웃바운드 규칙 제거
aws ec2 revoke-security-group-egress \
  --group-id sg-xxxxxxxx \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0
```

```bash
# Azure - NSG 규칙 제거
az network nsg rule delete \
  --nsg-name nsg-name \
  --name rule-name \
  --resource-group group-name
```

```bash
# GCP - 방화벽 규칙 삭제
gcloud compute firewall-rules delete rule-name
```

#### Step 2: IP 주소 범위 제한

```bash
# AWS - 특정 IP 또는 IP 범위로 규칙 수정
# 기존 규칙 제거
aws ec2 revoke-security-group-ingress \
  --group-id sg-xxxxxxxx \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0

# 특정 IP로만 접근 허용
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxxxxx \
  --protocol tcp \
  --port 22 \
  --cidr 203.0.113.0/24
```

#### Step 3: 최소 권한 원칙 적용

```bash
# AWS - 특정 보안 그룹에서만 접근 허용
# 애플리케이션 서버의 보안 그룹에서만 데이터베이스 접근 허용
aws ec2 authorize-security-group-ingress \
  --group-id sg-database \
  --protocol tcp \
  --port 3306 \
  --source-group sg-application

# SSH는 관리자 네트워크에서만 허용
aws ec2 authorize-security-group-ingress \
  --group-id sg-database \
  --protocol tcp \
  --port 22 \
  --cidr 10.0.0.0/16
```

#### Step 4: 정기적인 접근 제어 정책 검토

```bash
# AWS - 보안 그룹 규칙 감사 보고서 생성
# AWS Config를 활용한 규칙 감사
aws configservice start-config-rule-evaluation --config-rule-name rule-name

# AWS Trusted Advisor를 통한 보안 권장사항 확인
aws support describe-trusted-advisor-checks --language en
```

#### Step 5: 자동화된 규칙 관리

```python
# 파이썬을 활용한 불필요한 규칙 자동 감지 스크립트
import boto3
from datetime import datetime, timedelta

ec2 = boto3.client('ec2')

def find_unused_security_groups():
    # 90일 이상 사용되지 않은 보안 그룹 찾기
    unused_sgs = []
    response = ec2.describe_network_interfaces()

    used_sg_ids = set()
    for interface in response['NetworkInterfaces']:
        for group in interface['Groups']:
            used_sg_ids.add(group['GroupId'])

    all_sgs = ec2.describe_security_groups()
    for sg in all_sgs['SecurityGroups']:
        if sg['GroupId'] not in used_sg_ids:
            unused_sgs.append(sg)

    return unused_sgs

if __name__ == "__main__":
    unused = find_unused_security_groups()
    print(f"사용하지 않는 보안 그룹: {len(unused)}개")
    for sg in unused:
        print(f"- {sg['GroupId']}: {sg['GroupName']}")
```

### 7. 접근 제어 정책 검토 체크리스트

| 점검 항목 | 확인 내용 |
|----------|----------|
| **0.0.0.0/0 규칙** | 모든 IP에서 접근을 허용하는 규칙이 불필요하게 존재하는가? |
| **불필요한 포트** | 사용하지 않는 포트가 열려있는가? (예: Telnet 23, FTP 21) |
| **사용하지 않는 SG** | 인스턴스에 연결되지 않은 보안 그룹이 있는가? |
| **중복 규칙** | 동일한 기능을 하는 중복된 규칙이 있는가? |
| **너무 넓은 IP 범위** | 특정 국가나 지역으로 제한할 수 있는가? |
| **폐기 리소스용 규칙** | 삭제된 리소스를 위한 규칙이 남아있는가? |
| **규칙 순서** | 규칙 평가 순서가 적절한가? |
| **로그 및 모니터링** | 거부된 접근 시도를 로깅하고 있는가? |

### 8. 조치 시 주의사항

| 주의사항 | 설명 |
|----------|------|
| **영향도 분석** | 규칙 삭제 전 반드시 영향도 분석 수행 |
| **테스트 환경 검증** | 운영 환경 적용 전 테스트 환경에서 검증 |
| **규칙 변경 로그** | 모든 규칙 변경 이력을 기록 |
| **롤백 절차** | 문제 발생 시 신속한 롤백 절차 마련 |
| **정기적 검토** | 분기별 또는 반기별 규칙 검토 수행 |

### 9. 참고 자료

- **AWS Security Group Best Practices**: https://docs.aws.amazon.com/vpc/latest/userguide/VPC_SecurityGroups.html
- **Azure NSG Documentation**: https://docs.microsoft.com/azure/virtual-network/network-security-groups-overview
- **GCP Firewall Rules Documentation**: https://cloud.google.com/vpc/docs/firewalls
- **CIS Amazon Web Services Foundations Benchmark**: Section 4 (Networking)

---

## 요약

**접근제어설정관리**는 클라우드 방화벽의 효율성과 보안성을 유지하는 핵심 항목입니다. 0.0.0.0/0과 같은 과도하게 열린 규칙을 제거하고, 최소 권한 원칙에 따라 필요한 IP와 포트에만 접근을 허용해야 합니다. 정기적인 검토와 자동화된 관리를 통해 불필요한 규칙을 제거하여 보안을 강화하세요.

**핵심 액션 아이템**
1. 0.0.0.0/0으로 열린 불필요한 규칙 제거
2. 사용하지 않는 보안 그룹 및 방화벽 규칙 삭제
3. IP 주소 범위를 관리자 네트워크로 제한
4. 분기별 접근 제어 정책 검토 수행
