---
title: "[2026 주요정보통신기반시설] U-60 SNMP Community String 복잡성 설정"
slug: "2026-주정통/U-60"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "SNMP CommunityString복잡성설정여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
draft: true
---

# U-60 SNMP Community String 복잡성 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-60 |
| **점검내용** | SNMP CommunityString복잡성설정여부점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX등 |
| **양호기준** | SNMP Community String 기본값인 'public', 'private'이 아닌 영문자, 숫자 포함 10자리 이상또는영문자,숫자,특수문자포함8자리이상인경우 (SNMPv3의경우별도인증기능을사용하고,해당비밀번호가복잡도를만족하는경우양호) |
| **취약기준** | 아래의내용중하나라도해당되는경우 1. SNMP Community String 기본값인'public', 'private'일경우 2.영문자,숫자포함10자리미만인경우 3.영문자,숫자,특수문자포함8자리미만인경우 |
| **조치방법** | SNMP서비스를사용하지않는경우서비스중지및비활성화설정, SNMP 서비스 사용 시 SNMP Community String 기본값인 'public', 'private'이 아닌 영문자, 숫자포함10자리이상또는영문자,숫자,특수문자포함8자리이상으로설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: Community String이 10자 이상(영문+숫자) 또는 8자 이상(영문+숫자+특수문자)인 경우
- **취약**: Community String이 'public', 'private'이거나 8자 미만인 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| 'public' 사용 | 취약 | 기본값 |
| 'private' 사용 | 취약 | 기본값 |
| 10자 이상 복잡성 | 양호 | 권장 |
| SNMPv3 사용 | 양호 | 암호화 인증 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| SNMPv2c | Community String | 영문+숫자+특수문자 8자 이상 | 복잡성 |
| SNMPv3 | authPriv | HMAC-SHA256 + AES | 암호화 |

### 2. 점검 방법

#### Linux 점검

```bash
# 1. Community String 확인
echo "=== 1. SNMP Community String ==="
grep -E "rocommunity|rwcommunity" /etc/snmp/snmpd.conf | grep -v "^#"
```

**양호 출력 예시:**
```text
=== 1: SNMP Community String ===
rocomplex8v#9dL2@s 127.0.0.1
```

**취약 출력 예시:**
```text
=== 1: SNMP Community String ===
rocommunity public
rwcommunity private
```

### 3. 조치 방법

#### Community String 변경

```bash
# /etc/snmp/snmpd.conf 수정
vi /etc/snmp/snmpd.conf

# 기본값 제거 후 추가:
rocommunity X8v#9dL2@s 192.168.1.10
rwcommunity Y9m$kL0*p@ss 127.0.0.1

systemctl restart snmpd
```

### 4. 참고 자료

- CIS Benchmark for SNMP: Community String 강화 권고
- NIST SP 800-53: IA-5 (인증 정책)
- man pages: snmpd.conf(5)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.