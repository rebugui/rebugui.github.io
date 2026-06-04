---
title: "[2026 주요정보통신기반시설] N-04 계정 잠금 임계값 설정"
slug: "2026-주정통/N-04"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "사용자 계정에 대해 로그인 실패 임계값이 설정되어 있는지 점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Network
---

# N-04 계정 잠금 임계값 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | N-04 |
| **점검내용** | 사용자 계정에 대해 로그인 실패 임계값이 설정되어 있는지 점검 |
| **점검대상** | Cisco, Alteon, Passport, Juniper, Piolink 등 |
| **양호기준** | 로그인 실패 임계값이 5회 이하의 값으로 설정된 경우 |
| **취약기준** | 로그인 실패 임계값이 설정되어 있지 않거나, 5회 초과의 값으로 설정된 경우 |
| **조치방법** | 로그인 실패 임계값을 5회 이하로 설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준

**양호**
- 로그인 실패 임계값이 5회 이하의 값으로 설정된 경우

**취약**
- 로그인 실패 임계값이 설정되어 있지 않거나, 5회 초과의 값으로 설정된 경우

#### 경계 케이스 (Edge Case) 처리 방법

1. **레거시 장비**
   - 계정 잠금 기능 미지원: 가능한 경우 AAA 서버 연동 권장
   - 대체 안: 로그 모니터링 강화, IP 기반 차단

2. **관리자 계정 잠금**
   - 위험: 모든 관리자 계정이 잠금될 가능성
   - 대책: 최소 2개 이상의 관리자 계정 유지, 비상시 접근 경로 확보

3. **DoS 공격 악용**
   - 위험: 공격자가 의도적으로 계정 잠금 유도
   - 대책: 잠금 시간 적정 설정(5-10분), 화이트리스트 IP 관리

#### 권장 설정값

- 로그인 실패 횟수: 3회 (최대 5회)
- 계정 잠금 시간: 5분 (300초)
- 실패 카운트 시간 범위: 60초
- 로그인 시도 간 지연: 10초

### 2. 점검 방법

**Cisco IOS 장비:**

```bash
# Step 1) 현재 설정된 보안 정책 확인
Router> enable
Router# show running-config

# `login block-for` 사용 여부를 확인합니다.

# Step 2) 로그인 실패 임계값 설정 확인
Router# show login

# 출력 예시:
# No login-delay has been applied.
# No quiet-mode access list has been configured.
# Login Successful for the last time: 00:15:23 ago
# Total failed logins: 0
```

**Juniper Junos 장비:**

```bash
# Step 1) retry-options 설정 확인
user@host> configure
[edit]
user@host# show system login retry-options

# tries-before-disconnect 및 lockout-period 설정을 확인합니다.
```

**Radware Alteon 장비:**

```bash
# Step 1) 로그인 보안 설정 확인
Main# /cfg/dump

# 보안 관련 설정에서 로그인 임계값을 확인합니다.
```

**Passport 장비:**

```bash
# Step 1) 계정 잠금 정책 확인
# show config

# 사용자 계정별 잠금 설정을 확인합니다.
```

### 3. 조치 방법

**Cisco IOS:**

```bash
# Step 1) login block-for 설정
Router# config terminal
Router(config)# login block-for 300 attempts 3 within 60

# 파라미터 설명:
# - 300: 계정 잠금 시간 (초 단위, 5분)
# - attempts 3: 잠금까지 허용할 실패 횟수
# - within 60: 실패 횟수를 카운트할 시간 범위 (초 단위)

# Step 2) 로그인 지연 시간 설정 (선택사항)
Router(config)# login delay 10

# Step 3) quiet-mode 접근 ACL 설정 (선택사항)
Router(config)# login quiet-mode access-class 10

# quiet-mode 중에도 접근을 허용할 관리자 IP를 설정합니다.
```

**Juniper Junos:**

```bash
# Step 1) 로그인 실패 임계값 설정
user@host> configure
[edit system login retry-options]
user@host# set tries-before-disconnect 3

# Step 2) 계정 잠금 시간 설정
[edit system login retry-options]
user@host# set lockout-period 300

# Step 3) 설정 확인
user@host# show
tries-before-disconnect 3;
lockout-period 300;
```

**Radware Alteon:**

```bash
# Step 1) 로그인 보안 설정
Main# /cfg
Main# /sys
Main# /security

# Step 2) 로그인 임계값 설정
# 장비별 지원 기능에 따라 설정
Main# apply
Main# save
```

**Passport:**

```bash
# Step 1) 계정 잠금 정책 설정
# config sys security
config/sys/security# login-attempts 3
config/sys/security# lockout-time 300
```

### 4. 참고 자료

**주요 공격 유형:**

1. **무차별 대입 공격 (Brute Force Attack)**
   - 가능한 모든 비밀번호 조합을 시도
   - 대책: 임계값 설정으로 공격 시간 증가

2. **사전 대입 공격 (Dictionary Attack)**
   - 자주 사용되는 비밀번호 목록 이용
   - 대책: 임계값 + 복잡성 정책 병행

**주요 장비별 계정 잠금 기능:**

| 장비 | 명령어 | 기능 |
|------|--------|------|
| Cisco IOS | login block-for | 실패 횟수 기반 잠금 |
| Juniper Junos | tries-before-disconnect | 연결 끊기 후 잠금 |
| Radware Alteon | /cfg/sys/security | 보안 정책 설정 |
| Piolink PLOS | security login-lock | 계정 잠금 기능 |

**주의사항:**
1. 임계값은 3회 권장 (최대 5회)
2. 잠금 시간은 5-10분이 적절
3. 관리자 계정이 잠금될 경우를 대비한 별도 계정 필수
4. 잠금 발생 로그는 정기적으로 모니터링
5. 장비별 기능 지원 여부 확인 필요

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.