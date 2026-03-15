---
title: "[2026 주요정보통신기반시설] N-08 VTY 접속 시 안전한 프로토콜 사용"
slug: "2026-주정통/N-08"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "네트워크 장비 정책에 암호화 프로토콜(SSH)을 이용한 터미널 접근만 허용하도록 설정되어 있는지 점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Network
---

# N-08 VTY 접속 시 안전한 프로토콜 사용

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | N-08 |
| **점검내용** | 네트워크 장비 정책에 암호화 프로토콜(SSH)을 이용한 터미널 접근만 허용하도록 설정되어 있는지 점검 |
| **점검대상** | Cisco, Alteon, Juniper, Piolink 등 |
| **양호기준** | 장비 정책에 VTY 접근 시 암호화 프로토콜(SSH) 이용한 접근만 허용하고 있는 경우 |
| **취약기준** | 장비 정책에 VTY 접근 시 평문 프로토콜(Telnet) 이용한 접근을 허용하고 있는 경우 |
| **조치방법** | 암호화 프로토콜만 VTY에 접근할 수 있도록 설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준

**양호**
- VTY 접근 시 SSH만 허용하고 Telnet을 차단한 경우
- SSH 버전 2를 사용하는 경우

**취약**
- VTY 접근 시 Telnet을 허용하고 있는 경우
- SSH가 활성화되지 않은 경우

#### 경계 케이스 (Edge Case) 처리 방법

1. **SSH 미지원 레거시 장비**
   - 대체 안: out-of-band 관리망 구성
   - 임시 조치: VPN을 통한 터널링 사용
   - 장비 교체: SSH 지원 장비로 교체 권장

2. **SSH 설정 전 Telnet 의존**
   - 위험: SSH 설정 후 Telnet 즉시 차단 시 접속 불가
   - 순서: SSH 설정 → SSH 접속 테스트 → Telnet 차단
   - 주의: 모든 관리자에게 사전 공지

3. **키 관리 및 복구**
   - RSA 키 손실: SSH 서비스 중단
   - 백업: 키 파일 백업 및 재생성 절차 준비

#### 권장 설정값

**SSH 설정:**
- SSH 버전: 2 (버전 1은 취약)
- RSA 키 길이: 최소 2048비트 (권장), 최소 1024비트
- 인증 시간 초과: 120초 이내
- 인증 재시도 횟수: 3회 이하
- 암호화 알고리즘: AES-256 권장

### 2. 점검 방법

**Cisco IOS 장비:**

```bash
# Step 1) SSH 활성화 확인
Router> enable
Router# show ip ssh

# 출력 예시:
# SSH Enabled - version 2.0
# Authentication timeout: 120 secs; Authentication retries: 3

# 비활성화 시:
# %SSH has not been enabled

# Step 2) VTY 라인의 transport 설정 확인
Router# show running-config | include transport
# transport input ssh  (양호)
# transport input telnet ssh  (취약 - Telnet 허용)
# transport input all  (취약 - 모든 프로토콜 허용)

# Step 3) Cisco IOS 이미지 확인
Router# show version

# k9(3DES) 또는 Security 이미지 사용 확인
# 예: 7200p-ipbasek9-mz.152-4.M11.bin
```

**Radware Alteon 장비:**

```bash
# Step 1) SSH 활성화 확인
Main# /cfg
Main# /sys/sshd

# SSH 데몬 활성화 상태 확인
```

**Juniper Junos 장비:**

```bash
# Step 1) SSH 및 Telnet 서비스 상태 확인
user@host> configure
[edit]
user@host# show system services

# SSH는 활성화, Telnet은 비활성화되어 있어야 함
# 예시:
# ssh {
#     protocol-version v2;
# }
# telnet은 설정되어 있지 않아야 함
```

**Piolink PLOS 장비:**

```bash
# Step 1) SSH 및 Telnet 상태 확인
# configure terminal
(config)# management-access
(config-management-access)# show

# SSH: enable, Telnet: disable 확인
```

### 3. 조치 방법

**Cisco IOS:**

```bash
# Step 1) 호스트명 설정
Router# config terminal
Router(config)# hostname Router-A

# Step 2) 도메인명 설정
Router(config)# ip domain-name example.com

# Step 3) RSA 키 생성 (최소 2048비트 권장)
Router(config)# crypto key generate rsa
The name for the keys will be: Router-A.example.com
Choose the size of the key modulus in the range of 360 to 4096 for your
  General Purpose Keys. Choosing a key modulus greater than 512 may take
  a few minutes.

How many bits in the modulus [512]: 2048

# Step 4) SSH 설정
Router(config)# ip ssh time-out 120
Router(config)# ip ssh version 2
Router(config)# ip ssh authentication-retries 3

# Step 5) VTY 라인에 SSH만 사용 설정
Router(config)# line vty 0 4
Router(config-line)# transport input ssh
Router(config-line)# login local

# 주의: transport input ssh는 SSH만 허용하고 Telnet은 차단합니다.
```

**Radware Alteon:**

```bash
# Step 1) SSH 활성화
Main# /cfg
Main# /sys/sshd
Main# /sys/sshd ena
Main# /sys/sshd on
Main# apply
Main# save

# Step 2) Telnet 비활성화 (선택사항)
Main# /cfg
Main# /sys/telnetd
Main# /sys/telnetd dis
Main# apply
Main# save
```

**Juniper Junos:**

```bash
# Step 1) SSH 활성화
user@host> configure
[edit]
root# set system services ssh protocol-version v2
[edit]
root# commit

# Step 2) Telnet 비활성화
[edit]
root# delete system services telnet
[edit]
root# commit

# Step 3) root 로그인 비활성화 (보안 권장)
[edit system services ssh]
root# set root-login deny
```

**Piolink PLOS:**

```bash
# Step 1) SSH 활성화
# configure terminal
(config)# management-access
(config-management-access)# ssh status enable
(config-management-access)# apply

# Step 2) Telnet 비활성화
(config)# management-access
(config-management-access)# telnet status disable
(config-management-access)# apply
```

### 4. 참고 자료

**스니핑(Sniffing) 공격이란?**
- 정의: 네트워크상의 트래픽을 도청하는 행위
- 위험: Telnet은 평문으로 전송되어 계정, 비밀번호 유출
- 대책: SSH 사용으로 암호화

**SSH vs Telnet 비교:**

| 항목 | Telnet | SSH |
|------|--------|-----|
| 데이터 전송 | 평문 | 암호화 |
| 포트 | 23 | 22 |
| 보안 | 취약 | 안전 |
| 인증 | 비밀번호 only | 비밀번호 + 공개키 |

**SSH 설정 순서 (중요):**
1. SSH 설정 (호스트명, 도메인명, RSA 키 생성)
2. SSH 접속 테스트 (새 창에서 테스트)
3. Telnet 차단 (transport input ssh)

**주요 주의사항:**
1. SSH 버전 2 사용 (버전 1은 취약)
2. RSA 키는 최소 2048비트 이상
3. Telnet 차단 전 SSH 접속 테스트 필수
4. 기존 Telnet 세션은 유지될 수 있으므로 모든 관리자에게 안내
5. 모든 관리자 클라이언트가 SSH 지원 확인
6. N-06(VTY 접근 ACL 설정)과 연계 적용 권장
7. 정기적 보안 패치로 SSH 서버 취약점 방지

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.