---
title: "[2026 주요정보통신기반시설] U-20 /etc/(x)inetd.conf 파일 소유자 및 권한 설정"
slug: "2026-주정통/U-20"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "/etc/(x)inetd.conf파일권한적절성여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
draft: true
---

# U-20 /etc/(x)inetd.conf 파일 소유자 및 권한 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-20 |
| **점검내용** | /etc/(x)inetd.conf파일권한적절성여부점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX등 |
| **양호기준** | /etc/(x)inetd.conf파일의소유자가root이고,권한이600이하인경우 |
| **취약기준** | /etc/(x)inetd.conf파일의소유자가root가아니거나,권한이600이하가아닌경우 |
| **조치방법** | /etc/(x)inetd.conf파일소유자및권한변경설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: `/etc/inetd.conf` 또는 `/etc/xinetd.conf` 파일과 `/etc/xinetd.d/` 디렉터리 내 설정 파일들의 소유자가 root이고, 권한이 600 이하인 경우
- **취약**: 해당 파일들의 소유자가 root가 아니거나, 권한이 600을 초과하는 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| 소유자 root, 권한 600 | 양호 | 가장 권장되는 설정 |
| 소유자 root, 권한 644 | 취약 | 일반 사용자 읽기 가능 |
| 소유자 root, 권한 666 | 취약 | 누구나 수정 가능 |
| 소유자가 root가 아님 | 취약 | 즉시 수정 필요 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| 모든 OS | 소유자 | root | root만 소유자 |
| 모든 OS | 권한 | 600 | root만 읽기/쓰기 가능 |
| Linux (xinetd) | xinetd.d/* | 600 | 모든 서비스 설정 파일 |

### 2. 점검 방법

#### Solaris, Linux (inetd 사용 시), AIX, HP-UX 점검

```bash
# /etc/inetd.conf 파일 점검
ls -l /etc/inetd.conf
```

#### Linux (xinetd 사용 시) 점검

```bash
# /etc/xinetd.conf 파일 점검
ls -l /etc/xinetd.conf

# /etc/xinetd.d/ 디렉터리 내 모든 파일 점검
ls -l /etc/xinetd.d/*
```

**양호 출력 예시:**
```text
-rw------- 1 root root 2048 Jan 20 10:00 /etc/xinetd.conf
-rw------- 1 root root 1024 Jan 20 10:00 /etc/xinetd.d/ftp
```

**취약 출력 예시:**
```text
-rw-r--r-- 1 root root 2048 Jan 20 10:00 /etc/xinetd.conf
# 권한: 644 (취약)

-rw------- 1 admin1 root 2048 Jan 20 10:00 /etc/xinetd.conf
# 소유자: admin1 (취약)
```

### 3. 조치 방법

#### Solaris, AIX, HP-UX, Linux (inetd) 설정

```bash
# 1. /etc/inetd.conf 파일 소유자 변경
chown root /etc/inetd.conf

# 2. /etc/inetd.conf 파일 권한 변경
chmod 600 /etc/inetd.conf
```

#### Linux (xinetd) 설정

```bash
# 1. /etc/xinetd.conf 파일 소유자 및 권한 변경
chown root /etc/xinetd.conf
chmod 600 /etc/xinetd.conf

# 2. xinetd.d 디렉터리 내 모든 파일 권한 변경
chown root /etc/xinetd.d/*
chmod 600 /etc/xinetd.d/*
```

### 4. 참고 자료

**inetd/xinetd 슈퍼 데몬:**
- inetd/xinetd는 슈퍼 데몬이라고 불리며, Telnet, FTP, Finger 등 다양한 네트워크 서비스 요청을 받아 해당 서비스를 실행시켜주는 역할을 합니다.
- 최근에는 보안상의 이유로 비활성화하거나 SSH 등으로 대체하는 추세입니다.

| 항목 | inetd | xinetd |
|-----|-------|--------|
| 설정 파일 | /etc/inetd.conf | /etc/xinetd.conf, /etc/xinetd.d/* |
| 개선 사항 | 기본 기능 | 접근 제어, 로깅 강화 |

- [CIS Benchmark - Ensure rsh server is not enabled](https://www.cisecurity.org/cis-benchmarks/)
- [NIST CM-7, SC-7 - Least Functionality, Network Protection](https://csrc.nist.gov/projects/risk-management/risk-management-encyclopedia)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.