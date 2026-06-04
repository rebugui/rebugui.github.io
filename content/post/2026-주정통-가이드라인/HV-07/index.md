---
title: "[2026 주요정보통신기반시설] HV-07 계정 잠금 임계값 설정"
slug: "2026-주정통/HV-07"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "로그인계정에대한비밀번호관리정책설정여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Virtualization
---

# HV-07 계정 잠금 임계값 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | HV-07 |
| **점검내용** | 로그인계정에대한비밀번호관리정책설정여부점검 |
| **점검대상** | VMware ESXi, vCenter, KVM 등 |
| **판단기준** | 양호: 로그인시도실패횟수에따른계정잠금설정이적용된경우 |
| **판단기준** | 취약: 로그인시도실패횟수에따른계정잠금설정이적용되지않은경우 |
| **조치방법** | 로그인시도실패횟수제한설정 |

---
## 상세 설명

### 1. 항목 개요

계정 잠금 정책(Account Lockout Policy)은 일정 횟수 이상 로그인에 실패할 경우 계정을 자동으로 잠그는 보안 기능입니다. 이는 **무차별 대입 공격(Brute Force Attack)**과 **사전 대입 공격(Dictionary Attack)**으로부터 계정을 보호하는 핵심 방어 기제입니다.

가상화 장비의 관리자 계정이 무차별 대입 공격으로 탈취될 경우, 공격자는 전체 가상화 인프라를 장악할 수 있게 됩니다. 계정 잠금 정책은 이러한 공격을 기술적으로 차단합니다.

### 2. 왜 이 항목이 필요한가요?

**보안 위협 시나리오:**

1. **계정 잠금 미설정 시**
   ```
   공격자 → SSH/vSphere 웹 콘솔 스캔
   → root/admin 계정 발견
   → 무차별 대입 공격 시작 (초당 100~1000회 시도)
   → 수시간~수일 내 비밀번호 탈취
   → 가상화 플랫폼 장악
   → 모든 가상 머신 암호화/삭제
   ```

2. **계정 잠금 설정 시**
   ```
   공격자 → 무차별 대입 공격 시작
   → 5회 실패 후 계정 자동 잠금
   → 추가 공격 불가
   → 관리자에게 잠금 알림
   → 공격 차단
   ```

**계정 잠금 정책의 중요성:**

1. **무차별 대입 공격 차단**: 자동화된 공격 도구 차단
2. **공격 시간 지연**: 공격자가 다른 공격 방법 모색 필요
3. **보안 알림**: 계정 잠금 시 관리자에게 알림 전송 가능
4. **감사 추적**: 잠금 기록을 통해 공격 시도 파악

### 3. 점검 대상

- VMware ESXi
- VMware vCenter
- KVM (RHEL, CentOS, Ubuntu 등)

### 4. 판단 기준

- **양호**: 로그인 시도 실패 횟수에 따른 계정 잠금 설정이 적용된 경우
  - 실패 횟수: 5회 이하
  - 잠금 시간: 10분(600초) 이상

- **취약**: 로그인 시도 실패 횟수에 따른 계정 잠금 설정이 적용되지 않은 경우

### 5. 점검 방법

#### VMware ESXi

1. Web 콘솔 접속
   ```
   https://<VMware ESXi IP>
   ```

2. **관리** > **설정** > **시스템** > **고급 설정**으로 이동

3. `Security.AccountLockFailures` 설정값 확인

4. `Security.AccountUnlockTime` 설정값 확인

**양호 기준:**
- `Security.AccountLockFailures`: 5 이하
- `Security.AccountUnlockTime`: 600 (10분) 이상

#### VMware vCenter

**vCenter 6.5:**

1. vSphere Client 접속

2. **관리** > **Single Sign On** > **구성** > **Policies** > **잠금정책(Lockout Policy)**

3. 다음 설정 확인:
   - 실패한 최대 로그인 시도 횟수
   - 실패 시간 간격
   - 잠금 해제 시간

**vCenter 8.0:**

1. vSphere Client 접속

2. **관리** > **Single Sign On** > **구성** > **로컬 계정** > **잠금정책(Lockout Policy)**

3. 계정 잠금 설정 확인

#### KVM (RHEL 8 이후)

1. PAM 설정 파일 확인
   ```bash
   cat /etc/security/faillock.conf
   ```

2. system-auth 파일 확인
   ```bash
   cat /etc/pam.d/system-auth | grep pam_faillock
   ```

3. 계정 잠금 정책 확인

### 6. 조치 방법

#### VMware ESXi

**1) 계정 잠금 실패 횟수 설정**

1. **관리** > **설정** > **시스템** > **고급 설정**으로 이동

2. `Security.AccountLockFailures` 선택 후 **옵션 편집** 클릭

3. 값 설정: `5`

4. 저장

**2) 계정 잠금 해제 시간 설정**

1. `Security.AccountUnlockTime` 선택 후 **옵션 편집** 클릭

2. 값 설정: `600` (10분)

3. 저장

**설정 예시:**
```
Security.AccountLockFailures = 5
Security.AccountUnlockTime = 600
```

#### VMware vCenter

**vCenter 6.5:**

1. vSphere Client 접속

2. **관리** > **Single Sign On** > **구성** > **Policies** > **잠금정책(Lockout Policy)**

3. 다음과 같이 설정:
   - **실패한 최대 로그인 시도 횟수**: 5
   - **실패 시간 간격**: 3분
   - **잠금 해제 시간**: 10분

4. **저장** 클릭

**vCenter 8.0:**

1. vSphere Client 접속

2. **관리** > **Single Sign On** > **구성** > **로컬 계정** > **잠금정책(Lockout Policy)**

3. 계정 잠금 설정:
   - **Login failures before lockout**: 5
   - **Failure interval**: 3 (분)
   - **Unlock time**: 10 (분)

4. **저장** 클릭

#### KVM (RHEL 8 이후)

**1) faillock.conf 설정**

1. `/etc/security/faillock.conf` 파일 수정
   ```bash
   vi /etc/security/faillock.conf
   ```

2. 다음 설정 추가/수정:
   ```
   deny = 5
   even_deny_root
   unlock_time = 600
   ```

**2) system-auth PAM 설정**

1. `/etc/pam.d/system-auth` 파일 수정
   ```bash
   vi /etc/pam.d/system-auth
   ```

2. auth 섹션에 다음 추가:
   ```
   auth required pam_faillock.so preauth silent audit deny=5 unlock_time=600
   auth sufficient pam_unix.so nullok_secure
   auth required pam_faillock.so authfail audit deny=5 unlock_time=600
   account required pam_faillock.so
   ```

3. password-auth 파일도 동일하게 수정
   ```bash
   vi /etc/pam.d/password-auth
   ```

4. 설정 적용을 위해 sshd 서비스 재시작
   ```bash
   systemctl restart sshd
   ```

### 7. 계정 잠금 정책 파라미터

#### VMware ESXi

| 파라미터 | 설명 | 권장값 |
|---------|------|--------|
| Security.AccountLockFailures | 계정 잠금까지 실패 횟수 | 5 |
| Security.AccountUnlockTime | 계정 잠금 해제 시간(초) | 600 (10분) |

#### VMware vCenter

| 파라미터 | 설명 | 권장값 |
|---------|------|--------|
| Login failures before lockout | 계정 잠금까지 실패 횟수 | 5 |
| Failure interval | 실패 카운트 시간 윈도우(분) | 3 |
| Unlock time | 계정 잠금 유지 시간(분) | 10 |

#### Linux PAM faillock

| 파라미터 | 설명 | 권장값 |
|---------|------|--------|
| deny | 계정 잠금까지 실패 횟수 | 5 |
| unlock_time | 계정 잠금 해제 시간(초) | 600 |
| even_deny_root | root 계정도 잠금 | 설정 권장 |

### 8. 계정 잠금 정책 모범 사례

**1) 실패 횟수: 3~5회**
- 너무 낮으면 정상 사용자 불편
- 너무 높으면 보안 약화
- 5회 권장

**2) 잠금 시간: 10~30분**
- 너무 짧으면 재공격 가능
- 너무 길면 서비스 거부 가능
- 10분 권장

**3) 잠금 알림**
- 계정 잠금 시 이메일/SMS 알림
- 보안팀에 자동 알림

**4) 관리자 계정 잠금**
- root/admin 계정도 동일 정책 적용
- 잠금 시 다른 관리자 계정으로 해제

**5) 영구 잠금 사용 않음**
- 영구 잠금은 서비스 거부 공격 가능성
- 자동 해제 기능 사용

### 9. 계정 잠금 해제 방법

#### VMware ESXi

1. Web 콘솔 접속

2. 다른 관리자 계정으로 로그인

3. **호스트** > **관리** > **보안 및 사용자** > **사용자**

4. 잠금된 계정 선택 > **잠금 해제** 클릭

#### VMware vCenter

1. vSphere Client 접속

2. 다른 관리자 계정으로 로그인

3. **관리** > **Single Sign On** > **구성** > **로컬 계정**

4. 잠금된 계정 선택 > **잠금 해제** 클릭

#### KVM

1. root 계정으로 로그인

2. 잠금된 사용자 계정 잠금 해제
   ```bash
   faillock --user <username> --reset
   ```

3. 모든 사용자 잠금 해제
   ```bash
   pam_tally2 --reset
   ```

### 10. 조치 시 주의사항

- 계정 잠금 정책 설정 시 반드시 **2개 이상의 관리자 계정** 확보
- 단일 관리자 계정만 존재할 경우, 계정 잠금으로 시스템 관리 불가
- 정책 변경 전 반드시 **백업 관리자 계정** 생성
- 잠금 시간은 너무 길지 않게 설정 (서비스 거부 방지)
- 계정 잠금 해제 절차 문서화
- 정기적 계정 잠금 로그 검토

### 11. 계정 잠금 로그 모니터링

#### VMware ESXi

```bash
# 계정 잠금 로그 확인
grep "Account locked" /var/log/auth.log
grep "Failed password" /var/log/auth.log
```

#### KVM

```bash
# 계정 잠금 로그 확인
grep "pam_faillock" /var/log/secure
faillock --user <username>
```

### 12. 추가 보안 조치

1. **geoIP 차단**: 특정 국가 접속 차단
2. **IP 화이트리스트**: 관리자 접속 IP 제한 (HV-02)
3. **MFA 도입**: 다중 인증 적용
4. **SIEM 연동**: 계정 잠금 이벤트 실시간 모니터링

## 요약

계정 잠금 정책은 **5회 실패 시 10분간 계정 잠금** 기준을 권장합니다. 무차별 대입 공격으로부터 가상화 장비를 보호하는 핵심 보안 설정이므로 반드시 적용해야 합니다. 단일 관리자 계정 환경에서는 백업 계정을 먼저 생성한 후 정책을 적용해야 합니다.
