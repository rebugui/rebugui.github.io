---
title: "[2026 주요정보통신기반시설] U-21 /etc/(r)syslog.conf 파일 소유자 및 권한 설정"
slug: "2026-주정통/U-21"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "/etc/(r)syslog.conf 파일 권한 적절성 여부 점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
draft: true
---

# U-21 /etc/(r)syslog.conf 파일 소유자 및 권한 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-21 |
| **점검내용** | /etc/(r)syslog.conf 파일 권한 적절성 여부 점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX 등 |
| **양호기준** | /etc/(r)syslog.conf 파일의 소유자가 root(또는 bin, sys)이고, 권한이 640 이하인 경우 |
| **취약기준** | /etc/(r)syslog.conf 파일의 소유자가 root(또는 bin, sys)가 아니거나, 권한이 640 이하가 아닌 경우 |
| **조치방법** | /etc/(r)syslog.conf 파일 소유자 및 권한 변경 설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 파일의 소유자가 root(또는 bin, sys)이고, 권한이 640 이하인 경우
- **취약**: 파일의 소유자가 root(또는 bin, sys)가 아니거나, 권한이 640 보다 높은 경우 (예: 644, 666 등)

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| syslog.conf와 rsyslog.conf가 모두 존재하는 경우 | 양호 | 최신 리눅스에서는 rsyslog.conf가 사용되며, syslog.conf는 레거시용일 수 있음. 두 파일 모두 점검 필요 |
| 소유자가 bin 또는 sys인 경우 | 양호 | Solaris 등 일부 유닉스 시스템에서는 정상적인 소유자 |
| 권한이 600인 경우 | 양호 | 640보다 더 엄격한 권한으로 허용 |
| 심볼릭 링크인 경우 | 주의 | 원본 파일의 권한을 확인해야 함 |
| /etc/rsyslog.d/ 디렉터리가 있는 경우 | 점검 필요 | 추가 설정 파일들의 권한도 확인 권장 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| Linux | 파일 소유자 | root | rsyslog.conf 또는 syslog.conf |
| Linux | 파일 권한 | 640 (rw-r-----) | 소유자만 읽기/쓰기, 그룹은 읽기만 |
| Solaris/AIX/HP-UX | 파일 소유자 | root 또는 bin/sys | syslog.conf |
| Solaris/AIX/HP-UX | 파일 권한 | 640 (rw-r-----) | 일반 사용자 접근 차단 |

### 2. 점검 방법

#### Linux 점검

최신 Linux 시스템은 대부분 `rsyslog`를 사용하며 설정 파일은 `/etc/rsyslog.conf`입니다. 구형 시스템은 `/etc/syslog.conf`를 사용할 수 있습니다.

```bash
# 설정 파일 목록 확인
ls -l /etc/syslog.conf /etc/rsyslog.conf 2>/dev/null
```

**양호 출력 예시:**
```text
-rw-r----- 1 root root 1463 Jan 20 10:00 /etc/rsyslog.conf
```
(소유자 root, 권한 640 이하)

**취약 출력 예시:**
```text
-rw-r--r-- 1 root root 1463 Jan 20 10:00 /etc/rsyslog.conf
```
(권한 644 - 일반 사용자도 읽기 가능)

**취약 출력 예시 2:**
```text
-rw-rw-rw- 1 user root 1463 Jan 20 10:00 /etc/rsyslog.conf
```
(소유자가 root가 아님, 권한 666)

#### Solaris, AIX, HP-UX 점검

대부분 `/etc/syslog.conf` 파일을 사용합니다.

```bash
ls -l /etc/syslog.conf
```

**양호 출력 예시:**
```text
-rw-r----- 1 root sys 1024 Jan 20 10:00 /etc/syslog.conf
```
(소유자 root 또는 sys, 권한 640 이하)

### 3. 조치 방법

#### Linux 설정

1. **파일 소유자를 root로 변경**
   ```bash
   chown root /etc/rsyslog.conf
   ```

2. **파일 권한을 640으로 변경**
   ```bash
   chmod 640 /etc/rsyslog.conf
   ```

3. **rsyslog.d 디렉터리 내 파일들도 점검 (선택 사항)**
   ```bash
   chown root:root /etc/rsyslog.d/*.conf
   chmod 640 /etc/rsyslog.d/*.conf
   ```

#### Solaris, AIX, HP-UX 설정

1. **파일 소유자를 root로 변경**
   ```bash
   chown root /etc/syslog.conf
   ```

2. **파일 권한을 640으로 변경**
   ```bash
   chmod 640 /etc/syslog.conf
   ```

3. **서비스 재시작 (설정 변경 시)**
   ```bash
   # Linux (rsyslog)
   systemctl restart rsyslog

   # Solaris
   svcadm restart system-log

   # AIX
   refresh -s syslogd

   # HP-UX
   /sbin/init.d/syslogd restart
   ```

### 4. 참고 자료

- **CIS Benchmarks**: 4.2.1.2 Ensure rsyslog is configured to send logs to a remote log host
- **NIST 800-53**: AU-9 (Protection of Audit Logs), AU-12 (Audit Trail Review)
- **rsyslog 공식 문서**: https://www.rsyslog.com/doc/
- **man page**: `man rsyslog.conf`, `man syslog.conf`

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.