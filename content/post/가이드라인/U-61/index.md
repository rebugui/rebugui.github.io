---
title: "[2026 주요정보통신기반시설] U-61 SNMP Access Control 설정"
slug: "2026-주정통/U-61"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "SNMP접근제어설정여부점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-61 SNMP Access Control 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-61 |
| **점검내용** | SNMP접근제어설정여부점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX등 |
| **양호기준** | SNMP서비스를사용하지않는경또는접근제어설정을적용한경우 |
| **취약기준** | SNMP서비스를사용하며접근제어설정을적용하지않은경우 |
| **조치방법** | SNMP서비스를사용하지않는경우서비스중지및비활성화설정, SNMP서비스사용시접근제어필요시SNMP접근제어설정적용 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: Community String 뒤에 IP 제한이 설정된 경우
- **취약**: Community String 뒤에 IP 제한이 없는 경우 (모든 곳에서 접근 가능)

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| 'public' default | 취약 | 모두 접근 가능 |
| 특정 IP만 허용 | 양호 | IP 제한 |
| localhost만 허용 | 양호 | 로컬만 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| SNMP | rocommunity | commstring IP | IP 제한 |
| SNMP | rwcommunity | commstring 127.0.0.1 | 로컬만 |

### 2. 점검 방법

#### Linux 점검

```bash
# 1. SNMP ACL 확인
echo "=== 1. SNMP Access Control ==="
grep -E "rocommunity|rwcommunity" /etc/snmp/snmpd.conf
```

**양호 출력 예시:**
```text
=== 1: SNMP Access Control ===
rocommunity Hard2Guess! 192.168.1.5
rocommunity Hard2Guess! localhost
```

**취약 출력 예시:**
```text
=== 1: SNMP Access Control ===
com2sec notConfigUser  default       public
rocommunity public
```

### 3. 조치 방법

#### IP 기반 접근 제어

```bash
# /etc/snmp/snmpd.conf 수정
vi /etc/snmp/snmpd.conf

# 변경 전:
# rocommunity public

# 변경 후:
rocommunity Hard2Guess! 192.168.1.5
rocommunity Hard2Guess! localhost

systemctl restart snmpd
```

### 4. 참고 자료

- CIS Benchmark for SNMP: ACL 설정 권고
- NIST SP 800-53: AC-3 (접근 제어 정책)
- man pages: snmpd.conf(5), snmpd(8)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.