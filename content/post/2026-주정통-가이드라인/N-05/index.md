---
title: "[2026 주요정보통신기반시설] N-05 사용자·명령어별 권한 설정"
slug: "2026-주정통/N-05"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "네트워크 장비 사용자의 업무에 따라 계정별로 장비 관리 권한을 차등(관리자 권한은 최소한의 계정만 허용) 부여하고 있는지 점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Network
---

# N-05 사용자·명령어별 권한 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | N-05 |
| **점검내용** | 네트워크 장비 사용자의 업무에 따라 계정별로 장비 관리 권한을 차등(관리자 권한은 최소한의 계정만 허용) 부여하고 있는지 점검 |
| **점검대상** | Cisco, Alteon, Juniper, Piolink 등 |
| **양호기준** | 업무에 맞게 계정의 권한이 차등 부여된 경우 |
| **취약기준** | 업무에 맞게 계정의 권한이 차등 부여되지 않은 경우 |
| **조치방법** | 업무에 맞게 계정별 권한 차등(관리자 권한 최소화) 부여 ※ 한 명의 관리자가 네트워크 장비를 관리할 경우는 해당하지 않음 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준

**양호**
- 업무에 맞게 계정의 권한이 차등 부여된 경우
- 관리자 권한이 최소한의 계정에만 부여된 경우

**취약**
- 업무에 맞게 계정의 권한이 차등 부여되지 않은 경우
- 모든 계정에 동일한 관리자 권한이 부여된 경우

#### 경계 케이스 (Edge Case) 처리 방법

1. **1인 관리자 환경**
   - 예외 인정: 한 명의 관리자만 있는 소규모 환경
   - 권장: 최소 2개 이상의 관리자 계정 유지 (비상시 대비)

2. **권한 분리 기능 미지원 장비**
   - 대체 안: 읽기 전용 계정과 설정 변경 계정 분리
   - AAA 서버 연동으로 중앙 권한 관리 권장

3. **임시 권한 부여**
   - 필요시: 일시적 권한 상향 및 작업 후 즉시 복원
   - 기록: 권한 변경 이력 및 사유 로깅

#### 권장 설정값

**Cisco IOS 권한 레벨:**
- 레벨 0-1: 사용자 EXEC 모드 (기본 조회만 가능)
- 레벨 2-14: 사용자 정의 레벨 (명령어별 권한 제어)
- 레벨 15: Privileged EXEC 모드 (전체 권한)

**Radware Alteon 권한 레벨:**
| 계정 | 권한 | 설명 |
|------|------|------|
| User | 조회 | 상태 정보 및 통계 확인만 가능 |
| SLB Operator | SLB 운영 | SLB 운영 메뉴 사용 |
| Operator | 운영 | 모든 스위치 기능 관리 |
| Administrator | 관리자 | 모든 권한 (superuser) |

**Juniper Junos 권한 클래스:**
| Class | 권한 |
|-------|------|
| read-only | view |
| operator | clear, network, reset, trace, view |
| superuser | all |

### 2. 점검 방법

**Cisco IOS 장비:**

```bash
# Step 1) 사용자 권한 레벨 확인
Router> enable
Router# show privilege

# 현재 사용자의 권한 레벨을 확인합니다.

# Step 2) 생성된 사용자 계정 확인
Router# show running-config | include username

# 각 사용자의 privilege 레벨을 확인합니다.

# Step 3) 명령어별 권한 수준 확인
Router# show privilege

# 특정 명령어의 권한 요구 레벨을 확인합니다.
```

**Radware Alteon 장비:**

```bash
# Step 1) 사용자 계정 및 권한 확인
Main# /cfg
Main# /sys
Main# /user

# 각 계정별 권한 레벨(user, slboper, l4oper, oper, slbadmin, l4admin, admin)을 확인합니다.
```

**Juniper Junos 장비:**

```bash
# Step 1) login class 설정 확인
user@host> configure
[edit system login]
user@host# show

# login class별 권한(permission)이 분리되어 있는지 확인합니다.
```

**Piolink PLOS 장비:**

```bash
# Step 1) 사용자 계정 및 권한 확인
# configure terminal
(config)# show running-config

# 슈퍼 유저(root)와 일반 유저의 권한이 분리되어 있는지 확인합니다.
```

### 3. 조치 방법

**Cisco IOS:**

```bash
# Step 1) 사용자별 권한 수준 지정
Router# config terminal
Router(config)# username <ID> privilege [1-15] secret <PASS>

# 예시: 운영자 계정 (레벨 1)
Router(config)# username operator privilege 1 secret <PASS>

# 예시: 관리자 계정 (레벨 15)
Router(config)# username admin privilege 15 secret <PASS>

# Step 2) 명령어별 권한 수준 지정
Router(config)# privilege exec level [1-15] <명령어>

# 중요한 명령어에는 레벨 15 적용
Router(config)# privilege exec level 15 configure
Router(config)# privilege exec level 15 debug
Router(config)# privilege exec level 15 reload

# Step 3) 특정 레벨 사용자를 위한 명령어 허용
Router(config)# privilege exec level 5 show ip interface brief
Router(config)# privilege exec level 5 ping
```

**Radware Alteon:**

```bash
# Step 1) 계정별 비밀번호 설정
Main# /cfg
Main# /sys
Main# /user

# 각 권한 레벨별 비밀번호 설정
Main# /usrpw          # user 계정
Main# /slboperpw      # SLB operator 계정
Main# /opw            # operator 계정
Main# /admpw          # administrator 계정

Main# apply
Main# save
```

**Juniper Junos:**

```bash
# Step 1) login class 정의
[edit system login]
user@host# set class read-only permissions view

user@host# set class operator permissions clear
user@host# set class operator permissions network
user@host# set class operator permissions reset
user@host# set class operator permissions trace
user@host# set class operator permissions view

user@host# set class superuser permissions all

# Step 2) 특정 명령어 제한 (operator 클래스)
[edit system login class operator]
user@host# set deny-commands "configure"
user@host# set deny-commands "request system"

# Step 3) 사용자에 클래스 할당
[edit system login]
user@host# set user <username> class operator
user@host# set user <username> authentication plain-text-password
```

**Piolink PLOS:**

```bash
# Step 1) 일반 사용자 계정 생성
# configure terminal
(config)# username <username> privilege <level>

# Step 2) 관리자 계정 생성
(config)# username <admin> privilege 15
```

### 4. 참고 자료

**권한 분리 모델:**

1. **최소 권한 원칙 (Principle of Least Privilege)**
   - 사용자에게 업무 수행에 필요한 최소한의 권한만 부여
   - 불필요한 권한은 제거하여 보안 강화

2. **책임 분리 (Separation of Duties)**
   - 장비 구성 변경(superuser)과 모니터링(read-only) 분리
   - 감사자 계정: 로그 확인만 가능

3. **권한 계층 구조**
   - 1단계: 일반 사용자 (기본 조회만)
   - 2단계: 운영자 (기본 운영 및 모니터링)
   - 3단계: 관리자 (전체 권한)

**권장 계정 구조:**
- 최소 2개 이상의 관리자 계정 (비상시 대비)
- 운영자 계정: 모니터링 및 기본 운영만 가능
- 감사자 계정: 로그 확인만 가능
- 임시 관리 계정: 필요시에만 권한 상향

**주의사항:**
1. 관리자 권한을 가진 계정은 최소한으로 유지
2. 사용자 역할 변화 시 권한 정기 검토 및 조정
3. 모든 관리 명령어 실행 내역 로깅
4. 장비별 권한 관리 기능 확인 필요
5. 1인 관리자 환경은 예외 인정

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.