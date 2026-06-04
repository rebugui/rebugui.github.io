---
title: "[2026 주요정보통신기반시설] U-24 사용자, 시스템 환경변수 파일 소유자 및 권한 설정"
slug: "2026-주정통/U-24"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "홈 디렉터리 내의 환경변수 파일에 대한 소유자 및 접근권한이 관리자 또는 해당 계정으로 설정 여부 점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-24 사용자, 시스템 환경변수 파일 소유자 및 권한 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-24 |
| **점검내용** | 홈 디렉터리 내의 환경변수 파일에 대한 소유자 및 접근권한이 관리자 또는 해당 계정으로 설정 여부 점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX 등 |
| **양호기준** | 홈 디렉터리 환경변수 파일 소유자가 root 또는 해당 계정으로 지정되어 있고, 홈 디렉터리 환경변수 파일에 root 계정과 소유자만 쓰기 권한이 부여된 경우 |
| **취약기준** | 홈 디렉터리 환경변수 파일 소유자가 root 또는 해당 계정이 아닌 경우 또는 타사용자 쓰기 권한이 부여된 경우 |
| **조치방법** | 환경변수 파일의 일반 사용자 쓰기 권한 제거 설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 홈 디렉터리 내 환경변수 파일의 소유자가 해당 계정(또는 root)이고, 타 사용자(Group, Other)의 쓰기 권한이 제거된 경우
- **취약**: 홈 디렉터리 내 환경변수 파일의 소유자가 다른 사용자이거나, 타 사용자(Group, Other)의 쓰기 권한이 부여된 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| 권한이 600 또는 644인 경우 | 양호 | 소유자만 쓰기 가능하면 안전함 |
| 권한이 664 또는 666인 경우 | 취약 | 그룹 또는 기타 사용자가 쓰기 가능 |
| 소유자가 root인 일반 사용자 환경 파일 | 주의 | 불필요한 경우 소유자를 해당 사용자로 변경 |
| /root/.bashrc 소유자가 root가 아님 | 취약 | root 환경 파일은 반드시 root 소유 |
| 쉘별로 다른 환경 파일 (.cshrc, .kshrc 등) | 점검 필요 | 사용하는 모든 쉘의 환경 파일 점검 |
| 시스템 전체 환경 파일 (/etc/profile) | 별도 점검 | U-16, U-18 등에서 다룸 |

#### 권장 설정값

| 환경 | 파일 경로 | 권장 소유자 | 권장 권한 | 비고 |
|------|------------|---------------|------|------|
| 사용자 홈 | ~/.bashrc, ~/.bash_profile | 해당 사용자 | 644 또는 600 | Bash 사용자 |
| 사용자 홈 | ~/.profile, ~/.kshrc | 해당 사용자 | 644 또는 600 | Korn/Bourne Shell |
| 사용자 홈 | ~/.cshrc, ~/.login | 해당 사용자 | 644 또는 600 | C Shell |
| 사용자 홈 | ~/.bash_logout | 해당 사용자 | 644 또는 600 | 로그아웃 스크립트 |
| root 홈 (/root 또는 /) | .bashrc, .profile | root | 600 | 최고 보안 |
| 사용자 홈 | .ssh/ | 해당 사용자 | 700 | SSH 설정 디렉터리 |
| 사용자 홈 | .ssh/authorized_keys | 해당 사용자 | 600 | SSH 공개키 |

### 2. 점검 방법

#### Linux, Solaris, AIX, HP-UX 점검

각 사용자의 홈 디렉터리를 순회하며 환경 변수 파일의 권한을 확인해야 합니다.

```bash
# 특정 사용자(예: oracle)의 홈 디렉터리 파일 확인
ls -la /home/oracle/.*

# root 사용자의 홈 디렉터리 파일 확인
ls -la /root/.*

# 모든 사용자의 환경 파일 일괄 점검
for user in $(cut -d: -f1 /etc/passwd); do
    homedir=$(getent passwd "$user" | cut -d: -f6)
    if [ -d "$homedir" ]; then
        echo "=== $user ($homedir) ==="
        ls -la "$homedir"/.bashrc "$homedir"/.bash_profile "$homedir"/.profile "$homedir"/.cshrc 2>/dev/null
    fi
done
```

**양호 출력 예시:**
```text
-rw-r--r-- 1 user1 staff 1024 Jan 20 10:00 .bashrc
-rw------- 1 user1 staff 2048 Jan 20 10:00 .bash_profile
-rw-r--r-- 1 root root 1234 Jan 20 10:00 /root/.bashrc
```

**취약 출력 예시:**
```text
-rwxrwxrwx 1 user1 staff 1024 Jan 20 10:00 .bashrc
-rw-rw-rw- 1 user1 staff 2048 Jan 20 10:00 .bash_profile
-rw-rw-r-- 1 admin root 1234 Jan 20 10:00 /root/.bashrc
```
(권한 777, 666 - 타인이 수정 가능; /root/.bashrc 소유자가 admin)

### 3. 조치 방법

#### Linux, Solaris, AIX, HP-UX 설정

1. **환경 변수 파일의 소유자를 해당 사용자(또는 root)로 변경**
   ```bash
   chown user1:staff /home/user1/.bashrc
   chown root:root /root/.bashrc
   ```

2. **타 사용자의 쓰기 권한 제거**
   ```bash
   chmod o-w /home/user1/.bashrc
   chmod g-w /home/user1/.bashrc
   ```

3. **일괄 권한 변경 (권장 설정)**
   ```bash
   chmod 644 /home/user1/.bashrc
   chmod 600 /home/user1/.bash_profile
   chmod 600 /root/.bashrc
   ```

4. **모든 사용자 환경 파일 일괄 조치 스크립트**
   ```bash
   for user in $(cut -d: -f1 /etc/passwd); do
       homedir=$(getent passwd "$user" | cut -d: -f6)
       if [ -d "$homedir" ]; then
           # 소유자 변경
           chown "$user" "$homedir"/.bashrc "$homedir"/.bash_profile "$homedir"/.profile 2>/dev/null
           # 권한 변경 (쓰기 권한 제거)
           chmod go-w "$homedir"/.bashrc "$homedir"/.bash_profile "$homedir"/.profile 2>/dev/null
       fi
   done
   ```

### 4. 참고 자료

- **CIS Benchmarks**: 6.1.12 Find world-writable user files
- **NIST 800-53**: AC-3 (Access Enforcement), AC-6 (Least Privilege)
- **man page**: `man bash`, `man shells`

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.