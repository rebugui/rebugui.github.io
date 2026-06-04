---
title: "[2026 주요정보통신기반시설] U-58 불필요한 SNMP 서비스 구동 점검"
slug: "2026-주정통/U-58"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "SNMP서비스활성화여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-58 불필요한 SNMP 서비스 구동 점검

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-58 |
| **점검내용** | SNMP서비스활성화여부점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX등 |
| **양호기준** | SNMP서비스를사용하지않는경우 |
| **취약기준** | SNMP서비스를사용하는경우 |
| **조치방법** | SNMP서비스를사용하지않는경우서비스중지및비활성화설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: SNMP 서비스가 비활성화된 경우 (모니터링 불필요 시)
- **취약**: SNMP 서비스가 활성화된 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| 모니터링 필요 | 주의 | SNMPv3 사용 권장 |
| SNMPv1/v2c 활성화 | 취약 | 평문 Community String |
| SNMPv3 활성화 | 양호 | 암호화 지원 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| Linux | snmpd | disabled (systemctl) | 불필요 시 비활성화 |

### 2. 점검 방법

#### Linux 점검

```bash
# 1. SNMP 서비스 상태
echo "=== 1. SNMP Service ==="
systemctl is-active snmpd 2>/dev/null
systemctl is-enabled snmpd 2>/dev/null

# 2. 포트 listening 확인
echo "=== 2. SNMP Port ==="
netstat -tuln | grep :161
```

**양호 출력 예시:**
```text
=== 1. SNMP Service ===
snmpd: inactive (dead)
```

**취약 출력 예시:**
```text
=== 1. SNMP Service ===
snmpd: active (running)
```

### 3. 조치 방법

#### SNMP 비활성화

```bash
systemctl stop snmpd
systemctl disable snmpd
```

### 4. 참고 자료

- CIS Benchmark for Linux: SNMP 비활성화 권고
- NIST SP 800-53: CM-7 (시스템 최소화)
- man pages: snmpd(8)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.