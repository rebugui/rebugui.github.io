---
title: "[2026 주요정보통신기반시설] S-19 이상징후 탐지 모니터링 수행"
slug: "2026-주정통/S-19"
date: 2026-02-05T09:56:12+09:00
lastmod: 2026-02-05T09:56:12+09:00
description: "보안장비에 이상 징후 탐지 모니터링을 수행하고 있는지 점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Security
---

# S-19 이상징후 탐지 모니터링 수행

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | S-19 |
| **점검내용** | 보안장비에 이상 징후 탐지 모니터링을 수행하고 있는지 점검 |
| **점검대상** | 방화벽, VPN, IDS, IPS, Anti-DDoS, 웹방화벽 등 |
| **양호기준** | 이상징후 탐지 모니터링을 수행하고 있는 경우 |
| **취약기준** | 이상징후 탐지 모니터링을 수행하고 있지 않은 경우 |
| **조치방법** | 이상징후 탐지 시 담당자/관리자가 즉시 확인할 수 있도록 모니터링 수행 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준

**양호**
- 이상징후 탐지 모니터링을 수행하고 있는 경우
- 알람 시스템 구축 및 운영 중

**취약**
- 이상징후 탐지 모니터링을 수행하고 있지 않은 경우
- 알람 수신 체계 미구축

#### 경계 케이스 (Edge Case) 처리 방법

1. **오탈(False Positive) 관리**
   - 임계값 조정: 너무 낮으면 오탐 증가
   - 화이트리스트: 정상 IP/서비스 등록

2. **24/7 모니터링 불가**
   - 근무 시간 모니터링
   - 비근무시간 알람만 받는 체계

#### 권장 설정값

- 알람 수신: 이메일, SMS, 대시보드
- 모니터링 주기: 실시간 (24/7 권장)
- 대응 시간: Critical 15분, High 30분 내

### 2. 점검 방법

**Step 1) 보안 장비의 이상징후 탐지 모니터링 기능 설정 확인**

```bash
# 1. 알람 기능 확인
# System > Configuration > Alerts

# 2. 알림 방식 확인
# - 이메일 (Email)
# - SMS
# - SNMP Trap
# - Syslog

# 3. 알람 수신자 확인
# - 담당자 이메일
# - 관리자 연락처
# - 24/7 모니터링 센터
```

**Step 2) Syslog를 통해 모니터링 시스템으로 전송하는 경우 해당 시스템의 모니터링 기능 설정 확인**

```bash
# SIEM(Security Information and Event Management) 시스템
# - Splunk
# - ELK Stack
# - QRadar
# - LogRhythm

# 설정 확인
# - 수집 로그: 보안 장비 로그
# - Correlation Rule: 이상 징후 탐지 규칙
# - 알람: 이메일, SMS, 대시보드
```

### 3. 조치 방법

**Step 1) 보안 장비 이상징후에 대해 실시간 모니터링 실시**

**알람 설정 예시:**

```bash
# 1. 이메일 알람 설정
# System > Configuration > Alerts > Email
- SMTP Server: smtp.company.com
- Sender: security@company.com
- Recipients: security-team@company.com
- Severity: Critical, High

# 2. SMS 알람 설정
# System > Configuration > Alerts > SMS
- SMS Gateway: sms.gateway.com
- Recipients: +82-10-XXXX-XXXX, +82-10-YYYY-YYYY
- Severity: Critical only

# 3. SNMP Trap 설정
# System > Configuration > Alerts > SNMP
- SNMP Manager: 192.168.100.10
- Community String: (복잡한 문자열)
- Trap Version: v2c or v3
```

**이상 징후 탐지 규칙 설정:**

```bash
# 1. 대량 데이터 전송 탐지
# Rule: 휴일/야간에 1GB 이상 전송 시 알람
# Condition: (Time: 22:00-06:00 OR Weekend) AND (Data Transfer > 1GB)
# Action: Alert + Log + Block (optional)

# 2. 비정상적 로그인 시도 탐지
# Rule: 5회 이상 실패 후 성공 시 알람
# Condition: (Failed Login > 5) AND (Success Login within 10 min)
# Action: Alert + Account Lock

# 3. 포트 스캔 탐지
# Rule: 10개 이상 포트 스캔 시 알람
# Condition: (Different Ports > 10) AND (Time Window: 1 min)
# Action: Alert + Block Source IP

# 4. DDoS 공격 탐지
# Rule: 초당 1000개 이상 요청 시 알람
# Condition: (Requests per second > 1000)
# Action: Alert + Rate Limit
```

### 4. 참고 자료

**이상 징후(Anomaly Detection)란?**

- 정상적인 행동 패턴에서 벗어나는 활동을 탐지
- 기계 학습, 통계적 분석 등을 활용

**탐지 대상**
1. **내부자 위협**
   - 휴일/야간에 비정상적 접근
   - 대량 데이터 다운로드
   - 업무 외 시스템 접근

2. **외부 공격**
   - DDoS 공격
   - 포트 스캔
   - 무차별 대입 공격

3. **시스템 이상**
   - CPU/메모리 과부하
   - 비정상적인 트래픽 증가
   - 장애 징후

**모니터링 수행 절차**

```bash
# 1. 24/7 모니터링
# - 상시 모니터링 팀 운영
# - 야간/주말 당직제
# - 3교대 근무 (권장)

# 2. 알람 수신 및 대응
# Step 1: 알람 수신
# Step 2: 내용 확인
# Step 3: 심각도 판단
# Step 4: 대응 조치
# Step 5: 결과 보고

# 3. 대응 시간 목표 (SLA)
# - Critical: 15분 이내
# - High: 30분 이내
# - Medium: 1시간 이내
# - Low: 4시간 이내
```

**주의사항**
- 일반적인 경우 영향이 없습니다.
- **오탐(False Positive) 최소화**: 너무 민감한 설정은 오탐을 증가시킵니다.
- **알람 피로**: 너무 많은 알람은 중요한 알람을 놓치게 합니다.
- **테스트**: 정기적으로 알람 시스템을 테스트하세요.
- **연락망 관리**: 긴급 연락망을 최신으로 유지하세요.
- **대응 절차**: 알람 수신 후 대응 절차를 문서화하세요.
- **후속 조치**: 모든 알람은 후속 조치 및 문서화가 필요합니다.

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.