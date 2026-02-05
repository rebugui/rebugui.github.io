---
title: "[2026 주요정보통신기반시설] U-06 사용자 계정 su 기능 제한"
slug: "2026-주정통/U-06"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "su명령어사용을허용하는사용자를지정한그룹이설정여부점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-06 사용자 계정 su 기능 제한

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-06 |
| **점검내용** | su명령어사용을허용하는사용자를지정한그룹이설정여부점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX등 |
| **양호기준** | su명령어를특정그룹에속한사용자만사용하도록제한된경우 (일반사용자계정없이root계정만사용하는경우su명령어사용제한불필요) |
| **취약기준** | su명령어를모든사용자가사용하도록설정된경우 |
| **조치방법** | PAM모듈설정또는su명령어허용그룹생성후su명령어일반사용자권한제거하도록설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: su 명령어를 특정 그룹(wheel 그룹 등)에 속한 사용자만 사용하도록 제한된 경우
- **취약**: su 명령어를 모든 사용자가 사용하도록 설정된 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| 일반 사용자 계정 없이 root만 사용 | 양호 | su 제한 불필요 |
| wheel 그룹에 관리자만 포함 | 양호 | 정상적인 제한 상태 |
| wheel 그룹에 없는 사용자가 su 사용 가능 | 취약 | 제한 설정 미작동 |
| PAM 모듈 미사용 시 su 권한 4750 | 양호 | 그룹 제한됨 |
| PAM 모듈 미사용 시 su 권한 4755 | 취약 | 모든 사용자 사용 가능 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| Linux (PAM) | /etc/pam.d/su | auth required pam_wheel.so use_uid | wheel 그룹만 허용 |
| Solaris/AIX | su 권한 | 4750 (rwsr-x---) | wheel 그룹 소유 |
| HP-UX | su 권한 | 4750 (rwsr-x---) | wheel 그룹 소유 |

### 2. 점검 방법

#### Solaris, Linux, AIX, HP-UX 점검

su 명령어는 사용자 계정을 전환할 수 있는 강력한 명령어로, 특히 root 계정으로의 전환을 제한해야 합니다.

```bash
# 1. /etc/group 파일에서 wheel 그룹(su 명령어 사용 그룹) 확인
cat /etc/group | grep wheel

# 2. su 명령어의 그룹 및 권한 확인
ls -l /usr/bin/su
```

**양호 출력 예시:**
```text
# wheel 그룹 확인
wheel:x:10:root,admin1

# su 권한 확인 (PAM 사용 시)
-rwsr-xr-x. 1 root root 34904 Jan 15 10:30 /usr/bin/su
# (PAM 설정으로 제한된 경우)

# su 권한 확인 (PAM 미사용 시)
-rwsr-x---. 1 root wheel 34904 Jan 15 10:30 /usr/bin/su
# (wheel 그룹만 실행 가능)
```

**취약 출력 예시:**
```text
# wheel 그룹 미설정 또는 빔
wheel:x:10:

# su 권한 취약 (모든 사용자 실행 가능)
-rwsr-xr-x. 1 root root 34904 Jan 15 10:30 /usr/bin/su
# (PAM 설정 없음)
```

#### Linux PAM 모듈 사용 시 점검

```bash
# /etc/pam.d/su 파일에서 su 명령어 허용 그룹 확인
cat /etc/pam.d/su | grep pam_wheel
```

**양호 출력 예시:**
```text
auth sufficient pam_rootok.so
auth required pam_wheel.so use_uid
# 또는
auth required pam_wheel.so group=wheel
```

**취약 출력 예시:**
```text
# pam_wheel.so 설정이 주석 처리되거나 없음
# auth required pam_wheel.so use_uid
```

### 3. 조치 방법

#### Solaris, AIX, HP-UX 설정

1. **wheel 그룹 생성 (존재하지 않는 경우)**
   ```bash
   groupadd wheel
   ```

2. **su 명령어 그룹 변경**
   ```bash
   chgrp wheel /usr/bin/su
   ```

3. **su 명령어 권한 변경**
   ```bash
   chmod 4750 /usr/bin/su
   ```

4. **wheel 그룹에 su 명령 허용 계정 등록**
   ```bash
   usermod -G wheel <username>

   # 또는 /etc/group 파일 직접 수정
   # wheel:x:10:root,admin
   ```

#### Linux (PAM 모듈 미사용 시) 설정

1. **wheel 그룹 생성**
   ```bash
   groupadd wheel
   ```

2. **su 명령어 그룹 변경**
   ```bash
   chgrp wheel /usr/bin/su
   ```

3. **su 명령어 권한 변경**
   ```bash
   chmod 4750 /usr/bin/su
   ```

4. **계정을 wheel 그룹에 추가**
   ```bash
   usermod -G wheel <username>
   ```

#### Linux (PAM 모듈 사용 시) 설정

1. **/etc/group 파일에서 wheel 그룹 확인**
   ```bash
   cat /etc/group | grep wheel
   ```

2. **/etc/pam.d/su 파일에 다음 내용 추가 또는 확인**
   ```bash
   vi /etc/pam.d/su

   # 다음 라인 추가 (없는 경우)
   auth required pam_wheel.so use_uid
   # 또는
   auth required pam_wheel.so group=wheel
   ```

3. **서비스 재시작 (불필요)**
   ```bash
   # PAM 설정은 즉시 적용됨
   ```

### 4. 참고 자료

- [Red Hat - Configuring Administrative Access](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/)
- [Ubuntu - RootSudo Community Help Wiki](https://help.ubuntu.com/community/RootSudo)
- [CIS Benchmark - Ensure access to the su command is restricted](https://www.cisecurity.org/cis-benchmarks/)
- [NIST AC-6 - Least Privilege](https://csrc.nist.gov/projects/universal-cybersecurity-controls/least-privilege)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.