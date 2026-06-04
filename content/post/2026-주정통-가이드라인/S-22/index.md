---
title: "[2026 주요정보통신기반시설] S-22 SNMP Community String 복잡성 설정"
slug: "2026-주정통/S-22"
date: 2026-02-05T09:56:12+09:00
lastmod: 2026-02-05T09:56:12+09:00
description: "SNMP Community String이 유추하기 어렵게 설정되어 있는지 점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Security
---

# S-22 SNMP Community String 복잡성 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | S-22 |
| **점검내용** | SNMP Community String이 유추하기 어렵게 설정되어 있는지 점검 |
| **점검대상** | 방화벽, VPN, IDS, IPS, Anti-DDoS, 웹방화벽 등 |
| **양호기준** | SNMP 서비스를 사용하지 않거나, 유추하기 어려운 Community String을 설정한 경우 |
| **취약기준** | Community String을 기본값으로 사용하고 있거나, 유추하기 쉬운 Community String을 설정한 경우 |
| **조치방법** | 유추하기 어려운 Community String을 설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준

**양호**
- SNMP 서비스를 사용하지 않거나, 유추하기 어려운 Community String을 설정한 경우
- Community String이 12자 이상이고 복잡한 경우

**취약**
- Community String을 기본값으로 사용하고 있거나, 유추하기 쉬운 Community String을 설정한 경우
- 기본값(public, private) 사용

#### 경계 케이스 (Edge Case) 처리 방법

1. **SNMPv3 사용 환경**
   - Community String 미사용
   - 사용자 인증 기반

2. **레거시 장비**
   - 장비가 긴 Community String 지원 제한
   - 최대한 복잡하게 설정

#### 권장 설정값

- 최소 길이: 12자 이상 (권장 16자)
- 복잡성: 영문 대소문자, 숫자, 특수문자 조합
- 예시: K9$xP2@mQ5#vL

### 2. 점검 방법

**Step 1) 보안 장비의 SNMP 설정 메뉴에서 Community String 확인**

```bash
# Cisco ASA
show running-config | include snmp-server community
# snmp-server community public RO    ← 취약 (기본값)
# snmp-server community private RW   ← 취약 (기본값)

# Palo Alto Firewall
show config | match community
# ↑ Community String 확인

# Web 방화벽
# System > Configuration > SNMP
# Community String: ******** (표시됨)
```

**Step 2) 취약한 Community String 확인**

```bash
# 취약한 예시
# - public (RO 기본값)
# - private (RW 기본값)
# - admin
# - password
# - cisco
# - companyname
# - 1234
# - test
# - 약한 패턴 (단순 반복 등)
```

### 3. 조치 방법

**Step 1) 보안 장비는 SNMP 취약성이 존재하므로 누구나 추측하기 어렵고 의미가 없는 문자열, 영문자 혼합으로 변경**

**강력한 Community String 설정:**

```bash
# 1. 기존 설정 제거
# Cisco ASA
no snmp-server community public
no snmp-server community private

# 2. 강력한 Community String 설정
snmp-server community K9$xP2@mQ5#vL7!n RO
snmp-server community R8&wQ9@zP3#mK6$n RW  ← RW는 정말 필요한 경우만

# 3. 특정 IP만 접속 허용
snmp-server host inside 192.168.1.10 K9$xP2@mQ5#vL7!n

# 4. 확인
show running-config | include snmp-server community
```

**Palo Alto Firewall Community String 변경:**

```bash
# 1. Web GUI 설정
# Device > Setup > Management > SNMP

# 2. Community String 변경
# - Old: public
# - New: Xn8$vQ2@pM5#kL9!z

# 3. SNMPv3 설정 (더 나은 선택)
# - User: admin
# - Authentication Protocol: SHA
# - Auth Password: (강력한 비밀번호)
# - Privacy Protocol: AES
# - Priv Password: (강력한 비밀번호)

# 4. 커밋
commit
```

**Step 2) SNMPv3로의 업그레이드**

**SNMPv3 사용 권장:**

```bash
# SNMPv3 장점
# - 암호화 지원 (Privacy)
# - 인증 지원 (Authentication)
# - Community String 미사용
# - 높은 보안성

# Cisco ASA SNMPv3 설정
snmp-server group SNMPv3-GROUP v3 priv
snmp-server user admin SNMPv3-GROUP v3 auth sha AuthP@ssw0rd123 priv aes 128 PrivP@ssw0rd123
snmp-server host inside 192.168.1.10 informs version 3 priv admin

# Palo Alto Firewall SNMPv3 설정
# Device > Setup > Management > SNMP
# - SNMP Version: v3
# - User: snmpadmin
# - Auth Password: (강력한 비밀번호)
# - Priv Password: (강력한 비밀번호)
```

### 4. 참고 자료

**강력한 Community String 작성 가이드**

**복잡성 요구사항:**

```bash
# 1. 최소 길이: 12자 이상 (권장 16자 이상)
# 2. 문자 종류: 3가지 이상 혼합
#    - 영문 대문자 (A-Z)
#    - 영문 소문자 (a-z)
#    - 숫자 (0-9)
#    - 특수문자 (!@#$%^&* 등)
# 3. 예측 불가: 의미 없는 난수 조합
# 4. 유일성: 다른 시스템과 중복 금지
```

**좋은 예시:**

```bash
# 강력한 Community String
K9$xP2@mQ5#vL7!n
Xn8$vQ2@pM5#kL9!zR3
Rw9&kQ3@zM7#pJ6!xN2

# 특징
# - 16자 이상
# - 영문 대소문자, 숫자, 특수문자 혼합
# - 의미 없는 난수
# - 유추 불가
```

**나쁜 예시:**

```bash
# 취약한 Community String
public          ← 기본값
private         ← 기본값
admin           ← 유추 쉬움
password        ← 유추 쉬움
cisco123        ← 회사명 + 숫자
test2024        ← 의미 있는 단어
abc123          ← 너무 짧음
```

**추가 보안 조치**

```bash
# 1. 접근 제어
# - 특정 IP만 허용
# - 관리 네트워크만 접속 허용
# - ACL 적용

# 2. RO 권한만 사용
# - RW는 정말 필요한 경우만
# - 가능한 RO만 사용

# 3. SNMPv3로 마이그레이션
# - 장기적으로 v3로 전환
# - 점진적 마이그레이션

# 4. 정기 변경
# - Community String 주기적 변경
# - 6개월~1년 주기
```

**주의사항**
- 일반적인 경우 영향이 없습니다.
- **영향도 확인**: Community String 변경 시 NMS 등 연동 시스템에 영향을 미칩니다.
- **변경 전 협의**: NMS 관리자와 변경 일정을 협의하세요.
- **동시 변경**: 모든 장비의 Community String을 동시에 변경하세요.
- **백업**: 변경 전 설정을 백업하세요.
- **테스트**: 변경 후 SNMP 동작을 테스트하세요.
- **SNMPv3 고려**: 새로운 구축은 SNMPv3를 사용하세요.

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.