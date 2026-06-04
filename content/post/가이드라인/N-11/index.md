---
title: "[2026 주요정보통신기반시설] N-11 원격 로그 서버 사용"
slug: "2026-주정통/N-11"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "네트워크 장비의 로그를 별도의 원격 로그 서버에 보관하도록 설정하였는지를 점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Network
---

# N-11 원격 로그 서버 사용

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | N-11 |
| **점검내용** | 네트워크 장비의 로그를 별도의 원격 로그 서버에 보관하도록 설정하였는지를 점검 |
| **점검대상** | Cisco, Alteon, Juniper, Piolink 등 |
| **양호기준** | 별도의 로그 서버를 통해 로그를 관리하는 경우 |
| **취약기준** | 별도의 로그 서버가 없는 경우 |
| **조치방법** | Syslog 등을 이용하여 로그 저장 설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준

**양호**
- 별도의 로그 서버를 통해 로그를 관리하는 경우
- Syslog 서버가 구성되어 로그가 전송되는 경우

**취약**
- 별도의 로그 서버가 없는 경우
- 로그가 장비 내부에만 저장되는 경우

#### 경계 케이스 (Edge Case) 처리 방법

1. **로그 서버 장애**
   - 위험: 로그 서버 장애 시 로그 소실
   - 대책: 로그 서버 이중화 구성

2. **네트워크 분리**
   - 문제: 로그 전송 트래픽으로 대역폭 소모
   - 해결: 별도의 관리망 구성 또는 QoS 설정

3. **로그 보안**
   - 위험: 로그 전송 중 도청 가능성
   - 대책: Syslog over TLS/SSL 사용 또는 VPN 전송

#### 권장 설정값

**Syslog 설정:**
- 로그 레벨: informational 또는 notice
- Syslog Facility: local6 또는 local7
- 전송 프로토콜: UDP (기본) 또는 TCP (신뢰성 필요 시)
- 로그 보관 기간: 최소 6개월 이상 (법적 요구사항 준수)
- 로그 서버: 이중화 구성 권장

### 2. 점검 방법

**Cisco IOS 장비:**

```bash
# Step 1) Logging 설정 확인
Router> enable
Router# show running-config

# 다음 설정을 확인합니다:
# - logging on
# - logging <syslog 서버 IP>
# - logging trap <severity level>

# Step 2) Log 정보 확인
Router# show logging

# Syslog logging 여부와 로그 내용을 확인합니다.
# 출력 예시:
# Syslog logging: Enabled (0 messages dropped, 0 flushes, 0 overruns)
#     Console logging: Level debugging, 45 messages logged
#     Monitor logging: Level debugging, 0 messages logged
#     Buffer logging: Level debugging, 45 messages logged
#     Trap logging: Level informational, 46 message lines logged
#         Logging to 192.168.3.1, 46 message lines logged
```

**Radware Alteon 장비:**

```bash
# Step 1) syslog host 설정 확인
Main# /cfg/dump

# /syslog/host 설정을 확인합니다.
```

**Juniper Junos 장비:**

```bash
# Step 1) syslog 설정 확인
user@host> configure
[edit]
user@host# show system syslog

# host 설정 및 any any 또는 특정 facility 설정을 확인합니다.
```

**Piolink PLOS 장비:**

```bash
# Step 1) logging 서버 설정 확인
# configure terminal
(config)# show running-config

# logging server 설정을 확인합니다.
```

### 3. 조치 방법

**Cisco IOS:**

```bash
# Step 1) 라우터 로깅 설정
Router# config terminal

# 1) 로깅 활성화
Router(config)# logging on

# 2) Severity Level 설정
Router(config)# logging trap informational

# Severity Level (심각도 수준):
# - emergency (0): 시스템 사용 불가
# - alert (1): 즉시 조치 필요
# - critical (2): 긴급 상태
# - error (3): 오류 상태
# - warning (4): 경고 상태
# - notification (5): 통지 필요
# - informational (6): 정보성 메시지
# - debugging (7): 디버깅 메시지

# 3) Syslog 서버 설정
Router(config)# logging 192.168.3.1

# 4) Syslog Facility 설정
Router(config)# logging facility local6

# Facility 종류: local0 ~ local7

# 5) 로그 전송 인터페이스 설정
Router(config)# logging source-interface loopback0

# 완성된 설정 예시:
Router(config)# logging on
Router(config)# logging trap informational
Router(config)# logging 192.168.3.1
Router(config)# logging facility local6
Router(config)# logging source-interface loopback0
```

**Radware Alteon:**

```bash
# Step 1) Syslog 설정
Main# /cfg
Main# /sys

# 첫 번째 Syslog 서버 설정
Main# /syslog/host 192.168.3.1

# 두 번째 Syslog 서버 설정 (이중화)
Main# /syslog/host2 192.168.3.2

# 저장 및 적용
Main# apply
Main# save
```

**Juniper Junos:**

```bash
# Step 1) Syslog 설정
user@host> configure
[edit]
user@host# edit system syslog

# 파일로 로그 저장
[edit system syslog]
user@host# set file messages any error

# 원격 Syslog 서버로 전송
[edit system syslog]
user@host# set host 192.168.0.245 any any

# 로그 아카이빙 설정
[edit system syslog]
user@host# set archive files 5 size 5m world-readable

# - files 5: 파일 수를 5개로 제한
# - size 5m: 최대 크기를 5MB로 제한
# - world-readable: 모든 사용자가 읽기 가능

# 적용
user@host# commit
```

**Piolink PLOS:**

```bash
# Step 1) Logging 서버 설정
# configure terminal
(config)# logging server enable
(config)# logging server 192.168.3.1 all info
```

### 4. 참고 자료

**원격 로그 서버란?**
- 정의: 정보시스템의 로그를 통합적으로 보관하는 서버
- 프로토콜: Syslog (UDP 포트 514, TCP 포트 514)
- 목적: 보안 사고 조사, 장애 원인 분석, 시스템 모니터링

**보안 위협 (원격 로그 서버 미사용 시):**
1. 로그 삭제 위험: 공격자가 장비 장악 후 로그 삭제로 추적 방해
2. 로그 변조: 보안 사고 증거 인멸을 위한 로그 변조
3. 저장 공간 부족: 장비 내부 저장 공간 부족으로 로그 손실
4. 장비 장애 시 로그 소실: 장비 장애 발생 시 로그도 함께 소실

**주의사항:**
1. 성능 영향: 상세한 로깅은 라우터 성능에 영향을 미칠 수 있음
2. 네트워크 대역폭: 로그 전송 트래픽 고려
3. 로그 보안: Syslog 서버 자체 보안 강화 및 암호화 전송 고려
4. 저장 공간: 로그 서버 충분한 저장 공간 확보 및 주기적 백업
5. 로그 보관 기간: 기관 보안 정책에 따른 보관 기간 준수
6. 로그 분석: SIEM 도입으로 실시간 모니터링 권장
7. 이중화: Syslog 서버 이중화로 로그 소실 방지
8. 시간 동기화: 모든 장비와 로그 서버의 NTP 동기화 필수

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.