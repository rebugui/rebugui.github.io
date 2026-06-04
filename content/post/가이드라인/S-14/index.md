---
title: "[2026 주요정보통신기반시설] S-14 NTP 및 시각 동기화 설정"
slug: "2026-주정통/S-14"
date: 2026-02-05T09:56:12+09:00
lastmod: 2026-02-05T09:56:12+09:00
description: "보안장비의 NTP 및 시간 동기화 설정 적용 여부 점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Security
---

# S-14 NTP 및 시각 동기화 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | S-14 |
| **점검내용** | 보안장비의 NTP 및 시간 동기화 설정 적용 여부 점검 |
| **점검대상** | 방화벽, VPN, IDS, IPS, Anti-DDoS, 웹방화벽 등 |
| **양호기준** | NTP 및 시간 동기화 설정이 되어있는 경우 |
| **취약기준** | NTP 및 시간 동기화 설정이 되어있지 않은 경우 |
| **조치방법** | 보안장비 시간 설정에서 NTP 및 시간 동기화 설정 확인 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준

**양호**
- NTP 및 시간 동기화 설정이 되어있는 경우
- 최소 2개 이상의 NTP 서버 설정

**취약**
- NTP 및 시간 동기화 설정이 되어있지 않은 경우
- 수동으로 시간을 설정하는 경우

#### 경계 케이스 (Edge Case) 처리 방법

1. **네트워크 격리 환경**
   - 내부 NTP 서버 구축
   - 정기적인 시간 동기화 수행

2. **NTP 서버 연결 불가**
   - 수동 시간 설정 임시 조치
   - 네트워크 복구 후 NTP 설정

#### 권장 설정값

- NTP 버전: 4 (최신)
- 시간대: Asia/Seoul (UTC+9)
- NTP 서버: 최소 2개 이상 (이중화)

### 2. 점검 방법

**Step 1) 보안 장비 설정 메뉴에서 NTP 프로토콜 연동 확인**

```bash
# Cisco ASA 예시
show ntp
# Clock is synchronized, stratum 3
#   Server 192.168.100.10 is running, authenticated

# Web 방화벽 예시
# System > Configuration > Time > NTP
# NTP Status: Enable
# NTP Server: ntp.kisa.or.kr
# Last Sync: 2024-01-20 10:15:30
```

**Step 2) 현재 시간 확인**

```bash
# 현재 시간 확인
show clock
# 10:15:30.123 KST Sat Jan 20 2024

# NTP 동기화 상태 확인
show ntp associations
#   address         ref clock        st  when  poll reach  delay  offset    disp
# ~192.168.100.10   .GPS.            1    10    64   377   1.234  -0.567    0.123
# *sys.peer (master), # selected (candidate), + peer (eligible)
```

### 3. 조치 방법

**Step 1) 보안 장비 설정 메뉴에서 NTP 서버 연동 설정**

**Cisco ASA NTP 설정:**

```bash
# 1. NTP 서버 설정
ntp server 192.168.100.10 prefer
ntp server 192.168.100.11

# 2. NTP 인증 설정 (선택사항)
ntp authentication-key 1 md5 encrypted <encrypted_key>
ntp authenticate
ntp trusted-key 1

# 3. 시간대 설정
clock timezone KST 9

# 4. NTP 동기화 확인
show ntp status
```

**Web 방화벽 NTP 설정:**

```bash
# Web GUI 설정
# System > Configuration > Time > NTP

# 1. NTP 활성화
- Enable NTP: Yes

# 2. NTP 서버 추가
- Primary Server: ntp.kisa.or.kr
- Secondary Server: time.bora.net
- Tertiary Server: time.google.com

# 3. NTP 버전 설정
- NTP Version: 4

# 4. 갱신 주기 설정
- Update Interval: 3600 seconds (1 hour)

# 5. 시간대 설정
- Timezone: Asia/Seoul (UTC+9)
```

**Step 2) 공인 NTP 서버 사용**

국내 공인 NTP 서버를 사용합니다:

```bash
# 한국 공인 NTP 서버
# 1. 한국인터넷진흥원(KISA)
ntp.kisa.or.kr

# 2. 한국과학기술원(KAIST)
ntp.kaist.ac.kr

# 3. 한국연구망(KREONET)
time.kreonet.net

# 4. 구글
time.google.com

# 5. 클라우드 플레어
time.cloudflare.com

# 프라이빗 NTP 서버 구축 (권장)
# 기관 내부에 프라이빗 NTP 서버 구축
# - 보안 강화
# - 외부 의존도 최소화
# - 일관된 시간 동기화
```

### 4. 참고 자료

**NTP(Network Time Protocol)란?**

- 네트워크를 통해 컴퓨터 시스템 간의 시간을 정확하게 동기화하는 프로토콜
- 1985년 RFC 958으로 제안되어 현재 RFC 5905(NTPv4) 사용
- 인터넷상의 시간 서버로부터 정확한 시간을 받아옴

**NTP 서버 계층 구조**

```
Stratum 1: GPS/라디오 시계 (공인 NTP 서버)
    ↓
Stratum 2: Stratum 1과 동기화 (기관 NTP 서버)
    ↓
Stratum 3: Stratum 2와 동기화 (보안 장비)
    ↓
내부 서버 (Stratum 4)
```

**주의사항**
- 일반적인 경우 영향이 없습니다.
- **NTP 서버 선택**: 신뢰할 수 있는 공인 NTP 서버를 사용하세요.
- **시간대 설정**: 정확한 시간대(Asia/Seoul, UTC+9)를 설정하세요.
- **프라이빗 NTP**: 보안을 위해 기관 내부에 프라이빗 NTP 서버 구축을 권장합니다.
- **중복 서버**: 최소 2개 이상의 NTP 서버를 설정하여 가용성 확보하세요.
- **인증 사용**: 가능한 경우 NTP 인증을 사용하여 위변조 방지하세요.
- **정기 확인**: 주기적으로 시간 동기화 상태를 확인하세요.
- **계절성 시간**: 일광 절약 시간(DST) 사용 시 주의가 필요합니다.

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.