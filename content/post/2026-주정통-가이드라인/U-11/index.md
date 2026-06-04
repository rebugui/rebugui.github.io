---
title: "[2026 주요정보통신기반시설] U-11 사용자 Shell 점검"
slug: "2026-주정통/U-11"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "로그인이불필요한계정(adm, sys,daemon등)에쉘부여여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-11 사용자 Shell 점검

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-11 |
| **점검내용** | 로그인이불필요한계정(adm, sys,daemon등)에쉘부여여부점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX등 |
| **양호기준** | 로그인이필요하지않은계정에/bin/false(/sbin/nologin)쉘이부여된경우 |
| **취약기준** | 로그인이필요하지않은계정에/bin/false(/sbin/nologin)쉘이부여되지않은경우 |
| **조치방법** | 로그인이필요하지않은계정에대해/bin/false(/sbin/nologin)쉘부여설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 로그인이 필요하지 않은 계정에 /bin/false 또는 /sbin/nologin 쉘이 부여된 경우
- **취약**: 로그인이 필요하지 않은 계정에 /bin/false 또는 /sbin/nologin 쉘이 부여되지 않은 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| 시스템 계정에 nologin 설정 | 양호 | 정상적인 설정 |
| 시스템 계정에 /bin/bash 설정 | 취약 | 로그인 가능 위험 |
| 서비스 계정(mysql 등)에 nologin | 양호 | 서비스 전용 계정 |
| FTP 계정에 /bin/false | 주의 | FTP 접속도 불가 |
| 일반 사용자에 nologin | 취약 | 로그인 불가 상태 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| 모든 OS | 시스템 계정 쉘 | /sbin/nologin | 로그인 차단 |
| 모든 OS | 일반 사용자 쉘 | /bin/bash | 로그인 허용 |
| 모든 OS | FTP 계정 쉘 | /sbin/nologin | 일부 FTP에서 접속 가능 |
| 모든 OS | 서비스 계정 쉘 | /sbin/nologin | mysql, apache 등 |

### 2. 점검 방법

#### Solaris, Linux, AIX, HP-UX 점검

로그인이 불필요한 계정(daemon, bin, sys, adm 등)에 로그인 쉘이 부여되어 있지 않은지 확인해야 합니다.

```bash
# /etc/passwd 파일에서 로그인이 불필요한 계정의 쉘 확인
cat /etc/passwd | grep -E '^(daemon|bin|sys|adm|lp|mail|uucp|operator|games|gopher|ftp|nobody):'

# 또는 awk 사용
awk -F: '($3 < 500) && ($NF !~ /(nologin|false)/) {print $0}' /etc/passwd
```

**양호 출력 예시:**
```text
daemon:x:2:2:daemon:/sbin:/sbin/nologin
bin:x:1:1:bin:/bin:/sbin/nologin
sys:x:3:3:sys:/dev:/sbin/nologin
adm:x:4:4:adm:/var/adm:/sbin/nologin
```

**취약 출력 예시:**
```text
daemon:x:2:2:daemon:/sbin:/bin/bash
bin:x:1:1:bin:/bin:/bin/sh
sys:x:3:3:sys:/dev:/bin/bash
```

#### 종합 점검 스크립트

```bash
#!/bin/bash
# 시스템 계정 쉘 점검 스크립트

echo "시스템 계정 로그인 쉘 점검"

vulnerable_found=0

while IFS=: read -r username x uid gid gecos home shell; do
    if [ "$uid" -lt 500 ]; then
        if [ "$username" != "root" ]; then
            if [[ ! "$shell" =~ *nologin* ]] && [[ ! "$shell" =~ *false* ]]; then
                echo "[취약] $username (UID: $uid, Shell: $shell)"
                vulnerable_found=1
            fi
        fi
    fi
done < /etc/passwd

if [ $vulnerable_found -eq 0 ]; then
    echo "[양호] 모든 시스템 계정에 적절한 쉘이 설정되었습니다."
fi
```

### 3. 조치 방법

#### Solaris, Linux, AIX, HP-UX 공통 설정

1. **단일 계정 쉘 변경**
   ```bash
   # /sbin/nologin 사용 (권장)
   usermod -s /sbin/nologin <username>

   # 또는 /bin/false 사용
   usermod -s /bin/false <username>

   # 예시: daemon 계정에 nologin 설정
   usermod -s /sbin/nologin daemon
   ```

2. **다중 계정 일괄 변경**
   ```bash
   # 모든 시스템 계정에 nologin 설정 (root 제외)
   while IFS=: read -r username x uid gid gecos home shell; do
       if [ "$uid" -lt 500 ] && [ "$username" != "root" ]; then
           if [[ ! "$shell" =~ *nologin* ]] && [[ ! "$shell" =~ *false* ]]; then
               usermod -s /sbin/nologin "$username"
           fi
       fi
   done < /etc/passwd
   ```

3. **특정 계정만 변경**
   ```bash
   # 로그인이 불필요한 계정 목록
   for account in daemon bin sys adm lp mail uucp operator games gopher ftp nobody; do
       if id "$account" >/dev/null 2>&1; then
           usermod -s /sbin/nologin "$account"
       fi
   done
   ```

#### /bin/false vs /sbin/nologin 선택

| 항목 | /bin/false | /sbin/nologin |
|-----|-----------|--------------|
| 메시지 출력 | 없음 | "This account is currently not available." |
| 로그 기록 | 기본 없음 | 있음 (syslog) |
| FTP 접속 | 불가 | 일부 설정에서 가능 |
| 사용자 경험 | 연결이 끊김 | 명확한 거부 메시지 |

### 4. 참고 자료

- [Red Hat Security Guide - User Accounts](https://access.redhat.com/documentation/)
- [Debian Administrator's Manual - User Management](https://www.debian.org/doc/)
- [CIS Benchmark - Ensure no login shell exists for system accounts](https://www.cisecurity.org/cis-benchmarks/)
- [NIST AC-3 - Access Enforcement](https://csrc.nist.gov/projects/risk-management/risk-management-encyclopedia)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.