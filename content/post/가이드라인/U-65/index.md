---
title: "[2026 주요정보통신기반시설] U-65 NTP 및 시각 동기화 설정"
slug: "2026-주정통/U-65"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "NTP 및 시각 동기화 설정 여부 점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-65 NTP 및 시각 동기화 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-65 |
| **점검내용** | NTP 및 시각 동기화 설정 여부 점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX 등 |
| **양호기준** | NTP 및 시각 동기화 설정이 기준에 따라 적용된 경우 |
| **취약기준** | NTP 및 시각 동기화 설정이 기준에 따라 적용되어 있지 않은 경우 |
| **조치방법** | NTP 설정 및 동기화 주기 설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: NTP 또는 Chrony 데몬이 동작 중이며, 외부 타임 서버와 동기화(Sync) 상태인 경우
- **취약**: NTP 서비스가 없거나, 동기화가 이루어지지 않는 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| ntpd/chronyd 실행 중 | 양호 | 서비스 활성 |
| * 또는 + 표시 | 양호 | 동기화 완료 |
| ? 표시 | 취약 | 동기화 실패 |
| rdate만 사용 | 주의 | 주기적 실행 필요 |
| 폐쇄망 환경 | 주의 | 내부 NTP 서버 필요 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| Linux | ntpd | enabled (systemctl) | NTP 서비스 |
| Linux | chronyd | enabled (systemctl) | 최신 Linux 기본 |
| NTP | server | pool.ntp.org 또는 국가별 pool | /etc/ntp.conf |
| Chrony | server | pool.ntp.org | /etc/chrony.conf |

### 2. 점검 방법

#### Linux 점검

서버의 시스템 시간이 표준 시간과 동기화되어 있는지 점검합니다. 정확한 시간 설정은 로그 분석의 정확성을 보장하고, 암호화 통신(Kerberos, TLS 등)의 유효성을 유지하는 데 필수적입니다.

```bash
# 1. NTP 서비스 상태 확인
echo "=== 1. NTP Service Status ==="
systemctl is-active ntpd chronyd 2>/dev/null
systemctl is-enabled ntpd chronyd 2>/dev/null

# 2. NTP 동기화 상태 확인 (ntpd)
echo "=== 2. NTP Sync Status (ntpq) ==="
ntpq -p 2>/dev/null

# 3. Chrony 동기화 상태 확인
echo "=== 3. Chrony Sync Status ==="
chronyc sources 2>/dev/null
chronyc tracking 2>/dev/null

# 4. 프로세스 확인
echo "=== 4. NTP Process ==="
ps -ef | grep -E "ntpd|chronyd" | grep -v grep

# 5. 현재 시간 및 시간대 확인
echo "=== 5. Current Time ==="
date
timedatectl status
```

**양호 출력 예시:**
```text
=== 1. NTP Service Status ===
chronyd: active (running)
chronyd: enabled
=== 3. Chrony Sync Status ===
MS Name/IP address         Stratum Poll Reach LastRx Last sample
===============================================================================
^* time.cloudflare.com           3   6   377    45   +123us[ +234us] +/-   17ms
=== 5. Current Time ===
System clock synchronized: yes
              NTP service: active
```

**취약 출력 예시:**
```text
=== 1. NTP Service Status ===
ntpd: inactive (dead)
ntpd: disabled
=== 2. NTP Sync Status (ntpq) ===
ntpq: read: Connection refused
=== 5. Current Time ===
System clock synchronized: no
              NTP service: inactive
```

### 3. 조치 방법

#### NTP 설정 (Linux, Unix)

1. **NTP 패키지 설치**
   ```bash
   # RHEL/CentOS
   yum install ntp

   # Ubuntu/Debian
   apt install ntp
   ```

2. **/etc/ntp.conf 편집**
   ```bash
   vi /etc/ntp.conf

   # 한국 NTP 서버 추가
   server 0.kr.pool.ntp.org iburst
   server 1.kr.pool.ntp.org iburst
   server 2.kr.pool.ntp.org iburst
   server 3.kr.pool.ntp.org iburst

   # 또는 글로벌 pool
   server pool.ntp.org iburst
   ```

3. **서비스 시작**
   ```bash
   systemctl enable ntpd
   systemctl start ntpd

   # 상태 확인
   ntpq -p
   ```

#### Chrony 설정 (최신 Linux 권장)

1. **Chrony 패키지 설치**
   ```bash
   # RHEL/CentOS 7/8, Rocky Linux
   yum install chrony

   # Ubuntu/Debian
   apt install chrony
   ```

2. **/etc/chrony.conf 편집**
   ```bash
   vi /etc/chrony.conf

   # 한국 NTP 서버 추가
   server 0.kr.pool.ntp.org iburst
   server 1.kr.pool.ntp.org iburst
   server 2.kr.pool.ntp.org iburst
   ```

3. **서비스 시작**
   ```bash
   systemctl enable chronyd
   systemctl start chronyd

   # 상태 확인
   chronyc sources
   chronyc tracking
   ```

#### rdate (Legacy - 비권장)

```bash
# crontab에 등록하여 주기적 실행
crontab -e

# 매일 자정에 시간 동기화
0 0 * * * /usr/bin/rdate -s time.bora.net
```

#### 폐쇄망 환경

내부망(폐쇄망) 환경에서는 외부 NTP 서버에 접속할 수 없으므로, 내부 네트워크에 자체적인 Master NTP 서버를 구축하고 나머지 서버들이 이를 바라보게 설정해야 합니다.

```bash
# /etc/ntp.conf (내부 서버)
server internal-ntp-server.example.com iburst
```

### 4. 참고 자료

- CIS Benchmark for Linux: NTP 설정 권고
- NIST SP 800-53: AU-8 (시간 서비스)
- RFC 5905: Network Time Protocol Version 4
- NTP Pool Project: https://www.ntppool.org/

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.