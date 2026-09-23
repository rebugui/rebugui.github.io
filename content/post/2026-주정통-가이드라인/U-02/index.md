---
title: "[2026 주요정보통신기반시설] U-02 비밀번호 관리 정책 설정"
slug: "2026-주정통/U-02"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-09-23
description: "비밀번호 관리 정책 설정 여부 점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
draft: false
---

# U-02 비밀번호 관리 정책 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-02 |
| **점검내용** | 비밀번호 관리 정책 설정 여부 점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX 등 |
| **양호기준** | 비밀번호 복잡성, 사용기간, 이력 기억 정책이 설정된 경우 |
| **취약기준** | 비밀번호 관리 정책이 설정되지 않은 경우 |
| **조치방법** | root 계정을 포함한 사용자 계정의 비밀번호를 영문, 숫자, 특수문자를 포함하여 최소 8자리 이상 및 최소 사용기간 1일, 최대 사용기간 90일, 최근 비밀번호 기억 4회 이상으로 설정 |

---
> **심사 기준과 일반 권고는 구분합니다.** 위의 90일·문자 조합은 이 글에 인용된 점검 항목의 서술이며 적용 원전의 판본·페이지는 여기서 확인되지 않았습니다. 아래 설정 예시는 기관에 이 기준이 실제로 적용될 때만 참고하고 그대로 실행하지 마세요. 현행 [NIST SP 800-63B-4](https://pages.nist.gov/800-63-4/sp800-63b.html#passwordver)는 문자 종류 강제나 침해 증거 없는 정기 변경을 요구하지 않습니다. 일반 권고로는 충분한 길이, 흔하거나 유출된 비밀번호 차단, 시도 제한, MFA와 침해 시 변경을 우선합니다.

## 상세 설명

### 1. 판단 기준

#### 인용된 점검 기준(적용 대상 한정)
- **원문상 양호**: 인용된 복잡성·사용기간·이력 정책이 모두 실제로 적용되는 경우
- **원문상 취약**: 적용 대상인데 요구 정책이 누락된 경우. 적용 여부가 확인되지 않았다는 이유만으로 보편적으로 취약하다고 판단하지 않습니다.

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| 복잡성 정책만 미설정 | 적용 기준 확인 | 별도 심사 기준에 요구되는 경우에만 평가 |
| 사용기간만 미설정 | 적용 기준 확인 | 주기 변경이 필수인지 판본·범위 확인 |
| enforce_for_root 미적용 | 주의 | root 계정에 정책 미적용 여부 확인 |
| PAM 모듈 순서 오류 | 취약 | 정책이 실제로 동작하지 않음 |

#### 정책 값 예시(해당 심사 기준이 적용될 때만)

다음 수치는 모든 Unix 계열의 보편적 권장값이 아닙니다. 조직에 실제 적용되는 요구사항과 벤더 지원 범위를 확인한 뒤, 각 플랫폼의 인증 정책을 선택하세요.

| 환경 | 항목 | 글에 인용된 기준의 예시값 |
|------|------|--------------------------|
| Linux(RHEL) | PASS_MAX_DAYS / PASS_MIN_DAYS | 90 / 1 |
| Linux(RHEL) | minlen / 문자 종류 / remember | 8 / 각 종류 1자 / 4 |
| Solaris | PASSLENGTH / MAXDAYS | 8 / 90 |
| AIX | maxage | 12주 |
| HP-UX | PASSWORD_MAXDAYS | 90 |

### 2. 점검 방법

#### Linux (Redhat/CentOS) 점검

```bash
# 비밀번호 사용기간 확인
cat /etc/login.defs | grep -E "PASS_MAX_DAYS|PASS_MIN_DAYS"

# 비밀번호 복잡성 확인
cat /etc/security/pwquality.conf | grep -E "minlen|dcredit|ucredit|lcredit|ocredit"

# 비밀번호 기억 확인
cat /etc/security/pwhistory.conf | grep remember

# PAM 설정 확인
cat /etc/pam.d/system-auth | grep -E "pam_pwquality.so|pam_pwhistory.so"
```

**설정 출력 예시(해당 기준 적용 환경):**
```text
PASS_MAX_DAYS 90
PASS_MIN_DAYS 1
minlen = 8
remember = 4
```

비밀번호 만료가 요구되지 않는 환경에서는 `PASS_MAX_DAYS 99999`만으로 취약이라 단정하지 않습니다. PAM 정책, 인증 제공자, 유출 비밀번호 차단과 MFA의 실제 적용 상태를 함께 검토하세요.

#### Linux (Debian/Ubuntu) 점검

```bash
# 비밀번호 복잡성 확인
cat /etc/security/pwquality.conf | grep -E "minlen|dcredit|ucredit|lcredit|ocredit"

# PAM 설정 확인
cat /etc/pam.d/common-password | grep -E "pam_pwquality.so|pam_pwhistory.so"
```

#### Solaris 점검

```bash
cat /etc/default/passwd | grep -E "PASSLENGTH|MINDIGIT|MINUPPER|MINLOWER|MINSPECIAL|MAXDAYS|MINDAYS|HISTORY"
```

#### AIX 점검

```bash
cat /etc/security/user | grep -A 20 "default:" | grep -E "minage|maxage|minalpha|minother|minspecialchar|minlen|mindiff|histsize"
```

#### HP-UX 점검

```bash
cat /etc/default/security | grep -E "MIN_PASSWORD_LENGTH|PASSWORD_MIN_|PASSWORD_MAXDAYS|PASSWORD_MINDAYS|HISTORY"
```

### 3. 조치 방법(별도 90일 기준이 실제 적용되는 경우에만)

이하의 90일·문자 조합 설정은 위 인용 기준에 맞춘 **조건부 예시**입니다. 원전 판본·페이지 및 적용 대상 확인 없이 일괄 적용하면 비밀번호 만료로 계정 잠금이나 제어 업무 중단이 발생할 수 있습니다. 운영 변경 승인을 받고 영향 및 복구 절차를 확인한 뒤 설정하세요.

#### Linux (Redhat/CentOS) 설정

1. **/etc/login.defs 파일에 사용기간 설정**
   ```bash
   vi /etc/login.defs
   ```

   ```
   PASS_MAX_DAYS 90
   PASS_MIN_DAYS 1
   ```

2. **/etc/security/pwquality.conf 파일에 복잡성 정책 설정**
   ```bash
   vi /etc/security/pwquality.conf
   ```

   ```
   minlen = 8
   dcredit = -1
   ucredit = -1
   lcredit = -1
   ocredit = -1
   enforce_for_root
   ```

3. **/etc/security/pwhistory.conf 파일에 비밀번호 기억 설정**
   ```bash
   vi /etc/security/pwhistory.conf
   ```

   ```
   enforce_for_root
   remember=4
   ```

4. **PAM 설정 확인**
   ```bash
   vi /etc/pam.d/system-auth
   ```

   pam_pwquality.so와 pam_pwhistory.so 모듈이 pam_unix.so 모듈 위에 위치해야 함

#### Linux (Debian/Ubuntu) 설정

1. **pwquality.conf 설정**
   ```bash
   vi /etc/security/pwquality.conf
   ```

   ```
   minlen = 8
   dcredit = -1
   ucredit = -1
   lcredit = -1
   ocredit = -1
   enforce_for_root
   ```

2. **PAM 설정 확인**
   ```bash
   vi /etc/pam.d/common-password
   ```

#### Solaris 설정

```bash
vi /etc/default/passwd
```

```
HISTORY=4
PASSLENGTH=8
MINDIGIT=1
MINUPPER=1
MINLOWER=1
MINSPECIAL=1
MAXDAYS=90
MINDAYS=1
```

#### AIX 설정

```bash
vi /etc/security/user
```

default 섹션:
```
default :
    minage = 1
    maxage = 12
    minalpha = 2
    minother = 2
    minspecialchar = 1
    minlen = 8
    mindiff = 4
    histsize = 4
```

#### HP-UX 설정

```bash
vi /etc/default/security
```

```
MIN_PASSWORD_LENGTH=8
PASSWORD_MIN_UPPER_CASE_CHARS=1
PASSWORD_MIN_LOWER_CASE_CHARS=1
PASSWORD_MIN_DIGIT_CASE_CHARS=1
PASSWORD_MIN_SPECIAL_CASE_CHARS=1
PASSWORD_MAXDAYS=90
PASSWORD_MINDAYS=1
HISTORY=4
```

### 4. 참고 자료

- Linux PAM 설정 가이드: https://linux.die.net/man/5/pam.conf
- pwquality.conf 매뉴얼: https://linux.die.net/man/5/pwquality.conf
- CIS Benchmarks (RHEL 8): https://www.cisecurity.org/benchmark/red_hat_enterprise_linux_8
- NIST SP 800-53: IA-5 (Authenticator Management)
- [NIST SP 800-63B-4: Password Verifiers](https://pages.nist.gov/800-63-4/sp800-63b.html#passwordver)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.