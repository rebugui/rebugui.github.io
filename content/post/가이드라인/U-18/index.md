---
title: "[2026 주요정보통신기반시설] U-18 /etc/shadow 파일 소유자 및 권한 설정"
slug: "2026-주정통/U-18"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "/etc/shadow파일권한적절성여부점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-18 /etc/shadow 파일 소유자 및 권한 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-18 |
| **점검내용** | /etc/shadow파일권한적절성여부점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX등 |
| **양호기준** | /etc/shadow파일의소유자가root이고,권한이400이하인경우 |
| **취약기준** | /etc/shadow파일의소유자가root가아니거나,권한이400이하가아닌경우 |
| **조치방법** | /etc/shadow파일소유자및권한변경설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: `/etc/shadow` 파일의 소유자가 root이고, 권한이 400 이하인 경우
- **취약**: `/etc/shadow` 파일의 소유자가 root가 아니거나, 권한이 400 이하가 아닌 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| 소유자 root, 권한 400 | 양호 | 가장 권장되는 설정 |
| 소유자 root, 권한 000 | 양호 | root만 읽기 가능 |
| 소유자 root, 권한 600 | 취약 | 소유자 쓰기 권한 있음 |
| 소유자 root, 권한 644 | 취약 | 일반 사용자 읽기 가능 |
| 소유자가 root가 아님 | 취약 | 즉시 수정 필요 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| Linux, Solaris | 권한 | 400 | 소유자 읽기 전용 |
| AIX | 권한 | 400 | /etc/security/passwd |
| HP-UX (일반) | 권한 | 400 | /etc/shadow |
| HP-UX (TCB) | 권한 | 400 | /tcb/files/auth |

### 2. 점검 방법

#### Solaris, Linux 점검

```bash
# /etc/shadow 파일 소유자 및 권한 확인
ls -l /etc/shadow
```

**양호 출력 예시:**
```text
-r-------- 1 root root 2048 Jan 20 10:00 /etc/shadow
# 소유자: root, 권한: 400 (양호)
```

**취약 출력 예시:**
```text
-rw-r--r-- 1 root root 2048 Jan 20 10:00 /etc/shadow
# 권한: 644 (취약)

-rw------- 1 admin1 root 2048 Jan 20 10:00 /etc/shadow
# 소유자: admin1 (취약)
```

#### AIX 점검

AIX는 `/etc/security/passwd` 파일에 비밀번호 정보를 저장합니다.

```bash
ls -l /etc/security/passwd
```

#### HP-UX 점검

HP-UX는 일반 모드에서는 `/etc/shadow`를 사용하지 않을 수 있으며, Trusted Mode(TCB)를 사용할 경우 `/tcb/files/auth/` 디렉터리 하위에 계정별로 저장됩니다.

```bash
# 일반 모드
ls -l /etc/shadow

# Trusted Mode (TCB)
ls -ld /tcb/files/auth
```

### 3. 조치 방법

#### Solaris, Linux 설정

```bash
# 1. /etc/shadow 파일 소유자 변경
chown root /etc/shadow

# 2. /etc/shadow 파일 권한 변경
chmod 400 /etc/shadow

# 3. 변경 확인
ls -l /etc/shadow
```

#### AIX 설정

```bash
# 1. /etc/security/passwd 소유자 변경
chown root /etc/security/passwd

# 2. /etc/security/passwd 권한 변경
chmod 400 /etc/security/passwd
```

#### HP-UX 설정

**Shadow 패스워드 사용 시:**
```bash
chown root /etc/shadow
chmod 400 /etc/shadow
```

**Trusted Mode 사용 시:**
```bash
chown root /tcb/files/auth
chmod 400 /tcb/files/auth
```

### 4. 참고 자료

- **/etc/passwd vs /etc/shadow**:
  - `/etc/passwd`: 누구나 읽을 수 있어야 함 (권한 644). 사용자 기본 정보 저장.
  - `/etc/shadow`: root만 읽을 수 있어야 함 (권한 400). 비밀번호 해시 저장.

- [CIS Benchmark - Ensure /etc/shadow is configured](https://www.cisecurity.org/cis-benchmarks/)
- [NIST AC-6, SC-28 - Access Enforcement, Protection of Information at Rest](https://csrc.nist.gov/projects/risk-management/risk-management-encyclopedia)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.