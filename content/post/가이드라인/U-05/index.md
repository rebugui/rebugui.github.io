---
title: "[2026 주요정보통신기반시설] U-05 root 이외의 UID가 '0' 금지"
slug: "2026-주정통/U-05"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "사용자 계정 정보가 저장된 파일(/etc/passwd, /etc/shadow 등)에 root(UID=0) 계정과 동일한 UID를 가진 계정이 존재 여부 점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-05 root 이외의 UID가 '0' 금지

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-05 |
| **점검내용** | 사용자 계정 정보가 저장된 파일(/etc/passwd, /etc/shadow 등)에 root(UID=0) 계정과 동일한 UID를 가진 계정이 존재 여부 점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX 등 |
| **양호기준** | root 계정과 동일한 UID를 갖는 계정이 존재하지 않는 경우 |
| **취약기준** | root 계정과 동일한 UID를 갖는 계정이 존재하는 경우 |
| **조치방법** | UID가 0으로 설정된 계정을 0 이외의 중복되지 않은 UID로 변경 또는 불필요한 계정인 경우 제거 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: root 계정과 동일한 UID를 갖는 계정이 존재하지 않는 경우
- **취약**: root 계정과 동일한 UID를 갖는 계정이 존재하는 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| root만 UID 0 | 양호 | 정상적인 관리자 권한 |
| root + 일반사용자 UID 0 | 취약 | 일반 사용자에게 root 권한 부여 |
| root + 관리자 계정 UID 0 | 취약 | 감사 모호, 책임 소재 불명 |
| root + 숨겨진 백도어 UID 0 | 취약 | 탐지 불가, 시스템 완전 장악 |
| UID 중복(0 아님) | 주의 | 파일 권한 문제 발생 가능 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| 모든 OS | root UID | 0 | 최고 관리자 |
| Linux | 시스템 계정 | 1-999 | 데몬 및 서비스 |
| Linux | 일반 사용자 | 1000-60000 | 일반 사용자 범위 |
| AIX | 시스템 계정 | 1-99 | 시스템 데몬 |
| Solaris | 일반 사용자 | 100-60000 | 일반 사용자 범위 |

### 2. 점검 방법

#### Solaris, Linux, AIX, HP-UX 점검

```bash
# /etc/passwd 파일에서 UID가 0인 계정 확인
cat /etc/passwd | awk -F: '$3 == 0 {print $1,$3}'

# 또는
awk -F: '($3 == 0) {print}' /etc/passwd
```

**양호 출력 예시 (root만 존재):**
```text
root 0
```

**취약 출력 예시 (root 외 다른 계정 존재):**
```text
root 0
testuser 0
admin 0
```

### 3. 조치 방법

#### Solaris, Linux, AIX, HP-UX 공통

1. **UID 0인 계정 확인**
   ```bash
   # 모든 UID 0 계정 목록 확인
   cat /etc/passwd | awk -F: '$3 == 0 {print $1}'
   ```

2. **UID 변경 (usermod 명령어 사용)**
   ```bash
   # 사용 중인 계정의 UID 변경
   usermod -u <새로운_UID> <사용자이름>

   # 예: testuser 계정의 UID를 1000으로 변경
   usermod -u 1000 testuser
   ```

3. **UID 변경 (/etc/passwd 파일 직접 편집)**

   usermod 명령어를 통한 조치가 적용되지 않는 경우 /etc/passwd 파일을 직접 편집합니다.

   ```bash
   # 파일 백업
   cp /etc/passwd /etc/passwd.bak

   # 에디터로 파일 열기
   vi /etc/passwd
   ```

   변경 전: `testuser:x:0:100:Test User:/home/testuser:/bin/bash`
   변경 후: `testuser:x:1000:100:Test User:/home/testuser:/bin/bash`

4. **불필요한 계정 제거**
   ```bash
   # 계정 제거
   userdel <사용자이름>

   # 홈 디렉터리까지 제거
   userdel -r <사용자이름>
   ```

5. **변경 사항 확인**
   ```bash
   # UID 0인 계정 재확인
   cat /etc/passwd | awk -F: '$3 == 0 {print $1,$3}'

   # 결과가 root만 나오면 양호
   root 0
   ```

#### AIX 특이사항

```bash
# SMIT를 통한 UID 변경 (권장)
smit chuser

# 또는 lsuser/chuser 명령어
lsuser -a id ALL
chuser id=1000 testuser
```

### 4. UID 중복 확인

```bash
# UID 중복 확인
awk -F: '{print $3}' /etc/passwd | sort | uniq -d
```

중복된 UID가 있으면 해당 UID가 출력됩니다. 출력이 없으면 중복이 없는 것입니다.

### 5. /etc/passwd 파일 구조

```
계정명:비밀번호:UID:GID:GECOS:홈디렉터리:로그인셸
  |      |      |   |    |       |          |
  |      |      |   |    |       |          +-- 7. 로그인 셸 (/bin/bash 등)
  |      |      |   |    |       +------------- 6. 홈 디렉터리 (/home/user)
  |      |      |   |    +--------------------- 5. 코멘트/GECOS (Full Name 등)
  |      |      |   +-------------------------- 4. GID (Group ID)
  |      |      +------------------------------ 3. UID (User ID) ← 중요
  |      +------------------------------------- 2. 비밀번호 (x=쉐도우 사용)
  +-------------------------------------------- 1. 계정명
```

### 6. 표준 UID 범위

**Linux Systemd 기반**

| UID 범위 | 설명 | 비고 |
|----------|------|------|
| 0 | root 계정 | 최고 관리자 |
| 1-200 | 시스템 계정 (정적) | 시스템에서 사용자 개입 없이 생성 |
| 201-999 | 시스템 계정 (동적) | 패키지 설치 시 동적으로 생성 |
| 1000-60000 | 일반 사용자 계정 | 일반 사용자 할당 |

**전통적 Linux/Unix**

| UID 범위 | 설명 | 비고 |
|----------|------|------|
| 0 | root 계정 | 최고 관리자 |
| 1-99 | 시스템 계정 | 시스템 데몬 등 |
| 100-499 | 동적 시스템 계정 | 패키지 설치 시 생성 |
| 500-60000 | 일반 사용자 계정 | 일반 사용자 할당 |
| 65535 | nobody 계정 | 비인증 사용자 |

### 7. 주요 시스템 계정 UID

| 계정명 | UID | GID | 설명 |
|--------|-----|-----|------|
| root | 0 | 0 | 최고 관리자 |
| daemon | 1 | 1 | 시스템 데몬 |
| bin | 2 | 2 | 바이너리 파일 소유자 |
| sys | 3 | 3 | 시스템 파일 소유자 |
| adm | 4 | 4 | 관리 계정 |
| lp | 6 | 6 | 프린터 스풀러 |

### 8. 참고 자료

- Linux Standard Base (LSB) - UID Assignment: https://refspecs.linuxfoundation.org/lsb.shtml
- Unix-like operating system - UID and GID: https://en.wikipedia.org/wiki/User_identifier
- CIS Benchmarks - Ensure no duplicate UIDs: https://www.cisecurity.org/benchmark
- NIST 800-53: AC-6 (Least Privilege)

### 9. 스크립트

- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
