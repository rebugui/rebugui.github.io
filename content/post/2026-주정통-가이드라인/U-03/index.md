---
title: "[2026 주요정보통신기반시설] U-03 계정 잠금 임계값 설정"
slug: "2026-주정통/U-03"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "사용자 계정 로그인 실패 시 계정 잠금 임계값이 설정 여부 점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
draft: true
---

# U-03 계정 잠금 임계값 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-03 |
| **점검내용** | 사용자 계정 로그인 실패 시 계정 잠금 임계값이 설정 여부 점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX 등 |
| **양호기준** | 계정 잠금 임계값이 10회 이하의 값으로 설정된 경우 |
| **취약기준** | 계정 잠금 임계값이 설정되어 있지 않거나, 10회 이하의 값으로 설정되지 않은 경우 |
| **조치방법** | 계정 잠금 임계값을 10회 이하로 설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 계정 잠금 임계값이 10회 이하의 값으로 설정된 경우
- **취약**: 계정 잠금 임계값이 설정되어 있지 않거나, 10회 이하의 값으로 설정되지 않은 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| 임계값이 0으로 설정 | 취약 | 0회 실패 시 잠금은 정상 운영 불가 |
| 잠금 시간 무제한 | 양호 | unlock_time=0, 관리자 수동 해제 필요 |
| root 계정 제외 설정 | 주의 | no_magic_root 사용 시 root 계정 잠금 제외 |
| 일부 계정만 적용 | 취약 | 전체 계정에 정책 일관되게 적용 필요 |
| 임계값 음수 | 취약 | 시스템 오류, 즉시 수정 필요 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| 일반 서버 | deny | 5~10회 | 일반적인 사무실 환경 |
| 공개 서버(DMZ) | deny | 3~5회 | 높은 보안 요구사항 |
| 내부 개발 서버 | deny | 10회 | 개발 편의성 고려 |
| 클라우드 서버 | deny | 3~5회 | 인터넷 노출 환경 |
| unlock_time | unlock_time | 600초(10분) | 자동 잠금 해제 시간 |

### 2. 점검 방법

#### Linux (pam_tally2) 점검

```bash
cat /etc/pam.d/system-auth | grep "pam_tally2"
```

**양호 출력 예시:**
```text
auth required /lib/security/pam_tally2.so deny=10 unlock_time=120 no_magic_root
```

**취약 출력 예시:**
```text
(출력 없음)
```

#### Linux (faillock) 점검

```bash
# authselect 사용 환경
authselect current
cat /etc/security/faillock.conf | grep deny
```

**양호 출력 예시:**
```text
Profile ID: sssd
Enabled features:
- with-faillock

deny = 10
unlock_time = 120
```

#### Solaris 점검

```bash
# Solaris 5.9 미만
cat /etc/default/login | grep RETRIES

# Solaris 5.9 이상
cat /etc/security/policy.conf | grep LOCK_AFTER_RETRIES
```

**양호 출력 예시:**
```text
RETRIES=10
LOCK_AFTER_RETRIES=YES
```

#### AIX 점검

```bash
cat /etc/security/user | grep loginretries
```

**양호 출력 예시:**
```text
default:
        loginretries = 3
```

#### HP-UX 점검

```bash
# 11.v2 이하
cat /tcb/files/auth/system/default | grep u_maxtries

# 11.v3 이상
cat /etc/default/security | grep AUTH_MAXTRIES
```

**양호 출력 예시:**
```text
u_maxtries#3
AUTH_MAXTRIES=3
```

### 3. 조치 방법

#### Linux (pam_tally2) 설정

1. **/etc/pam.d/system-auth 파일 수정**
   ```bash
   vi /etc/pam.d/system-auth
   ```

   ```
   auth required /lib/security/pam_tally2.so deny=10 unlock_time=120 no_magic_root
   account required /lib/security/pam_tally2.so no_magic_root reset
   ```

#### Linux (authselect/faillock) 설정 (RHEL 8 이상 권장)

1. **faillock 기능 활성화**
   ```bash
   authselect enable-feature with-faillock
   authselect current
   ```

2. **/etc/security/faillock.conf 파일 수정**
   ```bash
   vi /etc/security/faillock.conf
   ```

   ```
   silent
   deny = 10
   unlock_time = 120
   ```

#### Linux (pam_faillock) 설정

1. **/etc/pam.d/system-auth 파일 수정**
   ```bash
   vi /etc/pam.d/system-auth
   ```

   ```
   auth required pam_faillock.so preauth silent audit deny=10 unlock_time=120
   auth sufficient pam_unix.so
   auth required pam_faillock.so authfail audit deny=10 unlock_time=120
   ```

2. **/etc/pam.d/password-auth 파일 수정**
   ```bash
   vi /etc/pam.d/password-auth
   ```

   ```
   auth required pam_faillock.so preauth silent audit deny=10 unlock_time=120
   ```

#### Solaris 설정

1. **5.9 미만 버전**
   ```bash
   vi /etc/default/login
   RETRIES=10
   ```

2. **5.9 이상 버전**
   ```bash
   vi /etc/security/policy.conf
   LOCK_AFTER_RETRIES=YES
   UNLOCK_AFTER=2m
   ```

#### AIX 설정

```bash
vi /etc/security/user
```

```
default:
    loginretries = 3
```

#### HP-UX 설정

1. **11.v2 이하 버전**
   ```bash
   vi /tcb/files/auth/system/default
   u_maxtries#3
   ```

2. **11.v3 이상 버전**
   ```bash
   vi /etc/default/security
   AUTH_MAXTRIES=3
   ```

### 4. 계정 잠금 해제 방법

**Linux (pam_tally2)**
```bash
# 특정 사용자 계정 잠금 해제
pam_tally2 --user=username --reset

# 전체 사용자 계정 잠금 해제
pam_tally2 --reset
```

**Linux (faillock)**
```bash
# 특정 사용자 계정 잠금 해제
faillock --user username --reset

# 전체 사용자 계정 잠금 해제
faillock --reset
```

**AIX**
```bash
# 실패 횟수 초기화
chsec -f /etc/security/lastlog -a "unsuccessful_login_count=0" -s username
```

### 5. 참고 자료

- Red Hat: Account Locking - https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/
- Ubuntu: PAM Configuration - https://ubuntu.com/server/docs/security-pam
- CIS Controls: 16.9 Account Lockout Failed Logon Attempts
- NIST 800-53: IA-5, AC-7

### 6. 스크립트

- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
