---
title: "[2026 주요정보통신기반시설] U-59 안전한 SNMP 버전 사용"
slug: "2026-주정통/U-59"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "안전한SNMP버전사용여부점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-59 안전한 SNMP 버전 사용

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-59 |
| **점검내용** | 안전한SNMP버전사용여부점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX등 |
| **양호기준** | SNMP서비스를v3이상으로사용하는경우 |
| **취약기준** | SNMP서비스를v2이하로사용하는경우 |
| **조치방법** | SNMP서비스를사용하지않는경우서비스중지및비활성화설정, SNMP서비스사용시SNMP버전을v3이상으로적용하도록설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: SNMPv3만 활성화된 경우
- **취약**: SNMPv1/v2c가 활성화된 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| SNMPv1/v2c 활성화 | 취약 | 평문 전송 |
| SNMPv3만 활성화 | 양호 | 암호화/인증 |
| 레거시 장비 호환 | 주의 | v2c 부득시 사용 시 보안 강화 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| SNMP | 버전 | v3 only | 암호화 |
| SNMPv3 | authPriv | HMAC-SHA + AES | 인증+암호화 |

### 2. 점검 방법

#### Linux 점검

```bash
# 1. SNMP 설정 확인
echo "=== 1. SNMP Version ==="
grep -E "^(com2sec|rouser|rwuser)" /etc/snmp/snmpd.conf
grep -v "^#" /etc/snmp/snmpd.conf | grep -v "^$"

# 2. Community String 확인
echo "=== 2. Community String ==="
grep rocommunity /etc/snmp/snmpd.conf
```

**양호 출력 예시:**
```text
=== 1: SNMP Version ===
rouser snmpuser authPriv -V3
```

**취약 출력 예시:**
```text
=== 2: Community String ===
rocommunity public
```

### 3. 조치 방법

#### SNMPv3 설정

```bash
# 1. SNMPv3 사용자 생성
net-snmp-create-v3-user -ro -A authpass -X privpass -a SHA -x AES snmpuser

# 2. /etc/snmp/snmpd.conf 수정
vi /etc/snmp/snmpd.conf

# 추가:
rouser snmpuser authPriv -V3

# v1/v2c 비활성화 (주석 처리)
# rocommunity public

systemctl restart snmpd
```

### 4. 참고 자료

- CIS Benchmark for Network Infrastructure: SNMPv3 권장
- NIST SP 800-53: SC-8 (전송 기밀성)
- RFC 3414: SNMPv3 사양

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.