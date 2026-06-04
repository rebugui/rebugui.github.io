---
title: "[2026 주요정보통신기반시설] U-04 비밀번호 파일 보호"
slug: "2026-주정통/U-04"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "시스템의 사용자 계정(root, 일반 사용자) 정보가 저장된 파일(/etc/passwd, /etc/shadow 등)에 사용자 계정 비밀번호가 암호화 저장 여부 점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-04 비밀번호 파일 보호

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-04 |
| **점검내용** | 시스템의 사용자 계정(root, 일반 사용자) 정보가 저장된 파일(/etc/passwd, /etc/shadow 등)에 사용자 계정 비밀번호가 암호화 저장 여부 점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX 등 |
| **양호기준** | 쉐도우 비밀번호를 사용하거나, 비밀번호를 암호화하여 저장하는 경우 |
| **취약기준** | 쉐도우 비밀번호를 사용하지 않고, 비밀번호를 암호화하여 저장하지 않는 경우 |
| **조치방법** | 비밀번호 암호화 저장/관리 설정 (pwconv 명령어 등 활용) |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 쉐도우 비밀번호를 사용하거나, 비밀번호를 암호화하여 저장하는 경우
- **취약**: 쉐도우 비밀번호를 사용하지 않고, 비밀번호를 암호화하여 저장하지 않는 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| /etc/passwd 두 번째 필드가 'x' | 양호 | 쉐도우 비밀번호 사용 중 |
| /etc/passwd에 해시 문자열($1$, $6$) | 취약 | 암호화되어 있어도 노출 위험 |
| /etc/shadow 파일 권한 600 | 양호 | root만 읽기 가능 |
| /etc/shadow 파일 권한 644 | 취약 | 일반 사용자도 읽기 가능 |
| /etc/shadow 파일 없음 | 취약 | 쉐도우 비밀번호 미사용 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| Linux/Unix | /etc/passwd 필드2 | x | 쉐도우 사용 |
| Linux/Unix | /etc/shadow 권한 | 600 또는 400 | root만 읽기 |
| Linux/Unix | /etc/shadow 소유자 | root:root | root 소유 |
| Solaris | /etc/shadow 권한 | 400 | root만 읽기 |
| HP-UX | Trusted Mode | 권장 | /tcb/files/auth/에 저장 |

### 2. 점검 방법

#### Linux/Unix/Solaris/HP-UX 점검

```bash
# /etc/passwd 파일의 두 번째 필드 확인
cat /etc/passwd | head -5

# /etc/shadow 파일 존재 및 권한 확인
ls -l /etc/shadow

# root 계정의 실제 비밀번호가 /etc/shadow에 있는지 확인
sudo grep "^root:" /etc/shadow
```

**양호 출력 예시 (쉐도우 비밀번호 사용):**
```text
# /etc/passwd
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin

# /etc/shadow 권한
-r-------- 1 root root 1234 Jan 20 10:00 /etc/shadow

# /etc/shadow 내용
root:$6$abc123def456...:18500:0:99999:7:::
```

**취약 출력 예시 (비밀번호가 포함됨):**
```text
# /etc/passwd
root:$6$abc123def456...:0:0:root:/root:/bin/bash
daemon:!:1:1:daemon:/usr/sbin:/usr/sbin/nologin
```

**취약 출력 예시 (/etc/shadow 없음):**
```text
ls: cannot access '/etc/shadow': No such file or directory
```

#### AIX 점검

```bash
# /etc/security/passwd 파일 확인
cat /etc/security/passwd
```

**양호 출력 예시:**
```text
root:
        password = abc123def456...
        lastupdate = 18500000

daemon:
        password = *
```

### 3. 조치 방법

#### Linux/Solaris/HP-UX 설정

1. **/etc/passwd 파일 확인**
   ```bash
   cat /etc/passwd | grep root
   ```

   두 번째 필드가 'x'로 표시되는지 확인

2. **쉐도우 비밀번호 적용**
   ```bash
   # 쉐도우 비밀번호로 변환
   sudo pwconv
   ```

3. **/etc/shadow 파일 권한 확인**
   ```bash
   ls -l /etc/shadow
   chmod 600 /etc/shadow
   chown root:root /etc/shadow
   ```

**주의**: Solaris 11은 pwunconv 명령어가 존재하지 않음

#### HP-UX 설정 (Trusted Mode)

**Trusted Mode로 전환 (권장):**
```bash
# Trusted Mode로 전환
/usr/lbin/tsconvert -r

# UnTrusted Mode로 전환
/usr/lbin/tsconvert -r
```

**주의**: Trusted Mode 전환 시 파일 시스템 구조가 변경될 수 있으므로 충분한 테스트 필요

#### AIX 설정

AIX는 기본적으로 /etc/security/passwd 파일에 비밀번호를 암호화하여 저장하므로 별도의 조치가 필요하지 않습니다.

```bash
# 암호화 여부 확인
cat /etc/security/passwd
```

### 4. 쉐도우 비밀번호 파일 구조

**/etc/passwd 파일 구조**

| 필드 | 설명 | 예시 |
|------|------|------|
| 1 | 계정명 | root |
| 2 | 비밀번호 플레이스홀더 | x |
| 3 | UID | 0 |
| 4 | GID | 0 |
| 5 | 코멘트/GECOS | root |
| 6 | 홈 디렉터리 | /root |
| 7 | 로그인 셸 | /bin/bash |

**/etc/shadow 파일 구조**

| 필드 | 설명 | 예시 |
|------|------|------|
| 1 | 계정명 | root |
| 2 | 암호화된 비밀번호 | $6$rounds=5000$... |
| 3 | 마지막 비밀번호 변경일 | 18500 |
| 4 | 최소 비밀번호 사용일 | 0 |
| 5 | 최대 비밀번호 사용일 | 99999 |
| 6 | 비밀번호 만료 경고일 | 7 |
| 7 | 비밀번호 만료 후 계정 비활성화일 | |
| 8 | 계정 만료일 | |
| 9 | 예약 필드 | |

### 5. 암호화 알고리즘 식별

| 접두사 | 알고리즘 | 비고 |
|--------|---------|------|
| $1$ | MD5 | 사용 권장하지 않음 |
| $2a$ | Blowfish | 사용 권장하지 않음 |
| $5$ | SHA-256 | 권장 |
| $6$ | SHA-512 | 가장 권장 (Linux 기본값) |
| $y$ | yescrypt | 최신 알고리즘 |
| $7$ | scrypt | 최신 알고리즘 |

### 6. 참고 자료

- Linux Information Project - Shadow Passwords: https://www.linfo.org/shadow.html
- CIS Benchmarks - Account and Access Control: https://www.cisecurity.org/benchmark
- NIST SP 800-53: SC-13 (Cryptographic Protection)
- KISA 주요정보통신기반시설 취약점 진단 가이드

### 7. 스크립트

- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
