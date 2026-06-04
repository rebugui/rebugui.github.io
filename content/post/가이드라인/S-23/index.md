---
title: "[2026 주요정보통신기반시설] S-23 유해트래픽 탐지/차단 정책 설정"
slug: "2026-주정통/S-23"
date: 2026-02-05T09:56:12+09:00
lastmod: 2026-02-05T09:56:12+09:00
description: "유해트래픽 탐지/차단 정책 적용 여부 점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Security
---

# S-23 유해트래픽 탐지/차단 정책 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | S-23 |
| **점검내용** | 유해트래픽 탐지/차단 정책 적용 여부 점검 |
| **점검대상** | 방화벽, VPN, IDS, IPS, Anti-DDoS, 웹방화벽 등 |
| **양호기준** | 유해트래픽 탐지/차단 패턴이 적용된 경우 |
| **취약기준** | 유해트래픽 탐지/차단 패턴이 적용되지 않은 경우 |
| **조치방법** | 유해트래픽 탐지/차단 정책 설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준

**양호**
- 유해트래픽 탐지/차단 패턴이 적용된 경우

**취약**
- 유해트래픽 탐지/차단 패턴이 적용되지 않은 경우

#### 경계 케이스 (Edge Case) 처리 방법

1. **오탈(False Positive) 관리**
   - 임계값 조정: 너무 낮으면 오탐 증가
   - 화이트리스트: 정상 IP/서비스 등록

2. **성능 vs 보안**
   - 트래픽 급증 시: 장비 성능 고려
   - 차단优先: 탐지 후 차단 (IPS 모드)

#### 권장 설정값

- SYN/sec: 10,000
- UDP/sec: 5,000
- ICMP/sec: 1,000
- HTTP req/sec: 5,000
- Port Scan: 10 포트/1분

### 2. 점검 방법

**Flooding 공격 점검:**

```bash
# Step 1) TCP/UDP/ICMP Flooding 공격에 대한 탐지 및 차단 패턴 적용 여부 점검
# 방화벽 설정 확인
show running-config | include flood
show running-config | include rate-limit

# Step 2) 인터넷 진입구간에 위치한 DDoS 차단시스템에 차단정책 등록 여부 점검
# Anti-DDoS 시스템 정책 확인
show ddos-protection
```

**Scan 공격 점검:**

```bash
# Step 1) Port Scan에 대한 탐지 및 차단 패턴 적용 여부 점검
show running-config | include scan
show IPS signatures | include port.scan

# Step 2) 인터넷 진입 구간에 위치한 DDoS 차단시스템에 차단 정책 등록 여부 점검
```

**해킹툴 공격 점검:**

```bash
# Step 1) 악성코드에 대한 탐지 및 차단 패턴 적용 여부 점검
show IPS signatures
show antivirus status

# Step 2) 주요 해킹 툴에 대한 탐지 및 차단 정책 등록 여부 점검
```

### 3. 조치 방법

**Flooding 공격 방어 설정:**

```bash
# SYN Flood Protection
# Network > Profiles > Flood Protection > TCP Flood
# - Alarm Rate: 10,000
# - Activate Rate: 15,000
# - Max Rate: 20,000
# - Action: Random Drop

# UDP Flood Protection
# - Alarm Rate: 5,000 pps
# - Activate Rate: 10,000 pps
# - Max Rate: 15,000 pps
# - Action: Drop

# ICMP Flood Protection
# - Alarm Rate: 1,000 pps
# - Activate Rate: 5,000 pps
# - Action: Drop
```

**Scan 공격 방어 설정:**

```bash
# Port Scan Detection
# Security > Profiles > Anti-Spyware > Anti-Spyware Profile
# - Scan Threshold: 10 ports in 10 seconds
# - Action: Block
# - Log: Enable

# 방화벽 규칙
access-list OUTSIDE_IN permit tcp any any eq www established
access-list OUTSIDE_IN deny ip any any log
```

**해킹툴 공격 방어 설정:**

```bash
# IPS 공격 시그니처 활성화
# Security > Profiles > Intrusion Prevention

# 1. SQL Injection 방어
# - Signature: SQL-Injection-Detection
# - Action: Block
# - Severity: High

# 2. XSS 방어
# - Signature: XSS-Attack-Detection
# - Action: Block
# - Severity: High

# 3. 공격 도구 탐지
# - Metasploit, SQLMap, Nmap, Nessus
```

### 4. 참고 자료

**차단 정책 수립 절차**
1. 정책 분석: 서비스 특성 파악, 정상 트래픽 패턴 분석
2. 정책 설정: 탐지 규칙 설정, 차단 조치 설정
3. 테스트: 정상 트래픽 테스트, 공격 시뮬레이션
4. 운영: 모니터링, 로그 분석, 정책 튜닝

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.