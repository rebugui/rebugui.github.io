---
title: "[2026 주요정보통신기반시설] N-06 VTY 접근(ACL) 설정"
slug: "2026-주정통/N-06"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "원격 터미널(VTY)을 통해 네트워크 장비 접근 시 지정된 IP에서만 접근할 수 있도록 설정되어 있는지 점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Network
---

# N-06 VTY 접근(ACL) 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | N-06 |
| **점검내용** | 원격 터미널(VTY)을 통해 네트워크 장비 접근 시 지정된 IP에서만 접근할 수 있도록 설정되어 있는지 점검 |
| **점검대상** | Cisco, Alteon, Passport, Juniper, Piolink 등 |
| **양호기준** | 가상터미널(VTY) 접근을 제한하는 ACL을 설정한 경우 |
| **취약기준** | 가상터미널(VTY) 접근을 제한하는 ACL을 설정하지 않은 경우 |
| **조치방법** | 가상터미널(VTY)에 특정 IP 주소만 접근할 수 있도록 설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준

**양호**
- 가상터미널(VTY) 접근을 제한하는 ACL을 설정한 경우
- 특정 IP 주소 또는 대역에서만 접근을 허용한 경우

**취약**
- 가상터미널(VTY) 접근을 제한하는 ACL을 설정하지 않은 경우
- 모든 IP에서 접근을 허용한 경우

#### 경계 케이스 (Edge Case) 처리 방법

1. **원격 접속 차단 위험**
   - 위험: ACL 설정 시 자신의 IP 누락으로 접속 차단
   - 대책: 설정 전 현재 사용하는 모든 관리자 IP 확인
   - 순서: ACL에 관리자 IP 추가 → 설정 적용 → 접속 테스트

2. **VPN 및 재택 근무**
   - 유동 IP: VPN 풀 대역 전체 허용 또는 동적 DNS 활용
   - 화이트리스트: VPN 서버 IP 또는 사설 대역 허용

3. **긴급 상황 대비**
   - 비상 접속 경로: 콘솔 포트는 ACL 영향 없음
   - out-of-band 관리: 별도의 관리 네트워크 구성 권장

#### 권장 설정값

**Cisco IOS ACL 설정:**
- ACL 번호: 1-99 (표준), 100-199 (확장)
- 허용 IP: 관리자 PC, 관리 서버, VPN 대역
- 기본 정책: deny any (모든 접근 차단)

**Juniper Junos 필터 설정:**
- 필터 타입: firewall family inet filter
- 적용 위치: loopback 인터페이스(lo0)
- 허용 프로토콜: SSH, HTTPS만 허용 (Telnet, HTTP 차단)

### 2. 점검 방법

**Cisco IOS 장비:**

```bash
# Step 1) Access List 설정 및 VTY 적용 여부 확인
Router> enable
Router# show running-config

# 확인할 내용:
# - access-class가 VTY 라인에 적용되어 있는지
# - ACL이 특정 IP만 허용하고 있는지

# 예시 출력:
# line vty 0 4
#  access-class 10 in
#  login
#  password 7 xxxxxxxx
#
# access-list 10 permit 192.168.1.100
# access-list 10 permit 192.168.1.0 0.0.0.255
# access-list 10 deny any log
```

**Radware Alteon 장비:**

```bash
# Step 1) Telnet 또는 SSH 사용자 접속 IP 설정 확인
Main# /cfg
Main# /sys
Main# /access
Main# /mgmt

# Access Policies에서 허용된 IP 주소를 확인합니다.
```

**Passport 장비:**

```bash
# Step 1) Telnet 또는 SSH 접속 IP 설정 확인
# config sys access-policy
config/sys/access-policy# show

# 접근 정책(policy)별 허용 IP(host)를 확인합니다.
```

**Juniper Junos 장비:**

```bash
# Step 1) firewall filter 설정 및 루프백 인터페이스 적용 확인
user@host> configure
[edit]
user@host# show

# loopback 인터페이스(lo0)에 필터가 적용되어 있는지 확인합니다.
user@host# show interfaces lo0

# 예시 출력:
# unit 0 {
#     family inet {
#         filter input mgmt-access;
#     }
# }
```

**Piolink PLOS 장비:**

```bash
# Step 1) Security system access policy configuration 확인
# configure terminal
(config)# show running-config

# access policy 및 rule 설정을 확인합니다.
```

### 3. 조치 방법

**Cisco IOS:**

```bash
# Step 1) ACL 생성
Router# config terminal
Router(config)# access-list 10 permit 192.168.1.100
Router(config)# access-list 10 permit 192.168.1.0 0.0.0.255
Router(config)# access-list 10 deny any log

# Step 2) VTY 라인에 ACL 적용
Router(config)# line vty 0 4
Router(config-line)# access-class 10 in

# 완성된 설정 예시:
Router(config)# access-list 10 permit 192.168.1.100
Router(config)# access-list 10 permit 192.168.1.0 0.0.0.255
Router(config)# access-list 10 deny any log
Router(config)# line vty 0 4
Router(config-line)# access-class 10 in
Router(config-line)# login local
Router(config-line)# transport input ssh
```

**Radware Alteon:**

```bash
# Step 1) 관리용 IP 접속 설정
Main# /cfg
Main# /sys
Main# /access
Main# /mgmt
Main# /add

Enter Management Network Address: 192.168.1.0
Enter Management Network Mask: 255.255.255.0
Main# apply
Main# save
```

**Passport:**

```bash
# Step 1) Access Policy 설정
# config sys access-policy
config/sys/access-policy# enable true
config/sys/access-policy# policy 1 create
config/sys/access-policy/policy/1# enable true
config/sys/access-policy/policy/1# accesslevel rwa
config/sys/access-policy/policy/1# host 192.168.1.100
config/sys/access-policy/policy/1# service ssh enable
```

**Juniper Junos:**

```bash
# Step 1) 접속 허용 IP 목록(prefix-list) 생성
[edit policy-options]
user@host# set prefix-list mgmt-networks 192.168.1.100/32
user@host# set prefix-list mgmt-networks 192.168.1.0/24

# Step 2) firewall filter 설정
[edit firewall family inet filter mgmt-access]
user@host# set term deny-mgmt from source-address 0.0.0.0/0
user@host# set term deny-mgmt from source-prefix-list mgmt-networks except
user@host# set term deny-mgmt from protocol tcp
user@host# set term deny-mgmt from destination-port ssh
user@host# set term deny-mgmt then log
user@host# set term deny-mgmt then discard

# Step 3) 허용 규칙
user@host# set term allow-accepted then accept

# Step 4) 루프백 인터페이스에 필터 적용
[edit interfaces lo0 unit 0 family inet]
user@host# set filter input mgmt-access
```

**Piolink PLOS:**

```bash
# Step 1) SSH 서비스에 ACL 설정
# configure terminal
(config)# security
(config-security)# system
(config-security-system)# access
(config-security-system-access)# rule 1
(config-security-system-access-rule[1])# protocol tcp
(config-security-system-access-rule[1])# source-ip 192.168.1.100
(config-security-system-access-rule[1])# dest-port 22
(config-security-system-access-rule[1])# interface any
(config-security-system-access-rule[1])# policy accept

# Step 2) 기본 접근 정책을 차단으로 설정
(config-security-system-access)# default-policy deny
```

### 4. 참고 자료

**ACL 설정 순서 (Cisco IOS):**
1. ACL은 위에서부터 순차적으로 적용
2. 허용할 IP를 먼저 설정
3. 마지막에 `deny any` 배치
4. 로그 기록: `deny any log`로 접근 시도 모니터링

**보안 강화 방법:**
1. SSH만 허용: `transport input ssh`
2. 로컬 인증 사용: `login local`
3. 로그 기록: `logging buffered`, `syslog` 서버 전송
4. 정기적 검토: 불필요한 IP 제거

**VTY 접근 원칙:**
- 기반시설 시스템: VTY 접근 원칙적 금지
- 부득이한 경우: 허용된 시스템만 접근 가능
- 대체 안: out-of-band 관리망 구성

**주의사항:**
1. ACL 설정 전 현재 관리자 IP 모두 확인
2. 원격 접속 시 자신의 IP를 ACL에 먼저 추가
3. `deny any log`로 접근 시도 로그 기록
4. 허용된 IP 목록 정기적 검토
5. 콘솔 포트는 ACL 영향 없음 (비상시 대비)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.