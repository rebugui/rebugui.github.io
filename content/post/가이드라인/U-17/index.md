---
title: "[2026 주요정보통신기반시설] U-17 시스템 시작 스크립트 권한 설정"
slug: "2026-주정통/U-17"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "시스템시작스크립트파일권한적절성여부점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-17 시스템 시작 스크립트 권한 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-17 |
| **점검내용** | 시스템시작스크립트파일권한적절성여부점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX등 |
| **양호기준** | 시스템시작스크립트파일의소유자가root이고,일반사용자의쓰기권한이제거된경우 |
| **취약기준** | 시스템시작스크립트파일의소유자가root가아니거나,일반사용자의쓰기권한이부여된경우 |
| **조치방법** | 시스템시작스크립트파일소유자및권한변경설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 시스템 시작 스크립트 파일의 소유자가 root이고, 일반 사용자의 쓰기 권한이 제거된 경우
- **취약**: 시스템 시작 스크립트 파일의 소유자가 root가 아니거나, 일반 사용자의 쓰기 권한이 부여된 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| 소유자 root, 권한 755 | 양호 | 일반 사용자 실행 가능 |
| 소유자 root, 권한 744 | 양호 | 소유자만 모든 권한 |
| 소유자가 root가 아님 | 취약 | 즉시 수정 필요 |
| 일반 사용자 쓰기 권한 있음 | 취약 | 제거 필요 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| Linux (init) | 권한 | 755 또는 744 | root 소유, 기타 쓰기 제거 |
| Linux (systemd) | 권한 | 644 또는 755 | root 소유, 기타 쓰기 제거 |
| Solaris | 권한 | 755 또는 744 | root 소유, 기타 쓰기 제거 |
| AIX | 권한 | 755 또는 744 | root 소유, 기타 쓰기 제거 |
| HP-UX | 권한 | 755 또는 744 | root 소유, 기타 쓰기 제거 |

### 2. 점검 방법

#### Solaris 점검

```bash
# 점검
ls -al `readlink -f /etc/rc*.d/ | sed 's/$/*/'`
```

#### Linux (init) 점검

```bash
# 점검
ls -al `readlink -f /etc/rc.d/*/* | sed 's/$/*/'`
```

#### Linux (systemd) 점검

```bash
# 점검
ls -al /etc/systemd/system/*
ls -al /lib/systemd/system/*
```

#### AIX 점검

```bash
# 점검
find /etc/rc.d/*/* -type l -exec ls -l {} +
```

#### HP-UX 점검

```bash
# 점검
find /sbin/rc*.d/ -type l -exec ls -l {} +
```

**양호 출력 예시:**
```text
-rwxr-xr-x 1 root root 2048 Jan 20 10:00 /etc/rc.d/rc.local
-rw-r--r-- 1 root root 1024 Jan 20 10:00 /etc/systemd/system/service.service
```

**취약 출력 예시:**
```text
-rwxrwxrwx 1 root root 2048 Jan 20 10:00 /etc/rc.d/rc.local
# 일반 사용자 쓰기 권한 있음 (취약)
```

### 3. 조치 방법

#### Solaris, Linux, AIX, HP-UX 공통 설정

```bash
# 1. 소유자 변경
chown root <filename>

# 2. 일반 사용자 쓰기 권한 제거
chmod o-w <filename>
```

#### Linux (systemd) 설정

```bash
# 1. 소유자 변경
chown root /etc/systemd/system/<filename>

# 2. 일반 사용자 쓰기 권한 제거
chmod o-w /etc/systemd/system/<filename>
```

### 4. 참고 자료

**시스템 시작 스크립트 위치:**

| 시스템 | 시작 스크립트 위치 |
|--------|-----------------|
| Linux (init) | /etc/rc.d/init.d/, /etc/rc*.d/ |
| Linux (systemd) | /etc/systemd/system/, /lib/systemd/system/ |
| Solaris | /etc/init.d/, /etc/rc*.d/ |
| AIX | /etc/rc.d/ |
| HP-UX | /sbin/init.d/ |

- [CIS Benchmark - Ensure system startup scripts are root-owned](https://www.cisecurity.org/cis-benchmarks/)
- [NIST CM-7 - Least Functionality](https://csrc.nist.gov/projects/risk-management/risk-management-encyclopedia)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.