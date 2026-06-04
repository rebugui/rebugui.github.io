---
title: "[2026 주요정보통신기반시설] S-21 SNMP 서비스 확인"
slug: "2026-주정통/S-21"
date: 2026-02-05T09:56:12+09:00
lastmod: 2026-02-05T09:56:12+09:00
description: "SNMP 서비스 사용 여부 점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Security
---

# S-21 SNMP 서비스 확인

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | S-21 |
| **점검내용** | SNMP 서비스 사용 여부 점검 |
| **점검대상** | 방화벽, VPN, IDS, IPS, Anti-DDoS, 웹방화벽 등 |
| **양호기준** | 불필요한 SNMP 서비스를 사용하지 않을 경우 |
| **취약기준** | 불필요한 SNMP 서비스를 사용할 경우 |
| **조치방법** | 불필요한 경우 SNMP 서비스 중지 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준

**양호**
- 불필요한 SNMP 서비스를 사용하지 않을 경우
- SNMP 서비스가 비활성화된 경우

**취약**
- 불필요한 SNMP 서비스를 사용할 경우
- SNMP가 활성화되어 있으나 실제 사용하지 않는 경우

#### 경계 케이스 (Edge Case) 처리 방법

1. **NMS 연동 필요시**
   - SNMPv3 사용 (암호화 지원)
   - 접근 제어 강화

2. **대안 모니터링 가능**
   - SSH/CLI를 통한 모니터링
   - Syslog를 통한 이벤트 수집

#### 권장 설정값

- 기본 정책: SNMP 서비스 비활성화
- 사용시: SNMPv3만 사용 (v1/v2c는 취약)
- Community String: 12자 이상 복잡성

### 2. 점검 방법

**Step 1) 보안 장비의 SNMP 설정 메뉴에서 확인**

```bash
# Cisco ASA
show running-config | include snmp
# snmp-server enable traps
# snmp-server host inside 192.168.1.10 public
# ↑ SNMP가 활성화된 경우

# Palo Alto Firewall
show running-config snmp
# ↑ SNMP 설정 확인

# Web 방화벽
# System > Configuration > SNMP
# Status: Enable/Disable 확인
```

**Step 2) SNMP 서비스 사용 필요성 확인**

```bash
# 확인 질문
# 1. 현재 NMS(Network Management System)를 사용 중인가?
# 2. SNMP를 통해 모니터링이 필요한 장비인가?
# 3. 대안(SSH, Syslog 등)을 사용할 수 있는가?
# 4. SNMP를 실제로 사용하고 있는가?
```

### 3. 조치 방법

**Step 1) 불필요하다면 SNMP 서비스를 중지**

**SNMP 서비스 중지 (Cisco ASA):**

```bash
# 1. SNMP 설정 제거
no snmp-server enable traps
no snmp-server host inside 192.168.1.10
no snmp-server community public

# 2. 확인
show running-config | include snmp
# (설정이 표시되지 않아야 함)

# 3. 저장
write memory
```

**SNMP 서비스 중지 (Palo Alto Firewall):**

```bash
# 1. Web GUI 설정
# Device > Setup > Management > SNMP
# - SNMP Client: Disable

# 2. CLI 설정
delete snmp v2c community <community-name>
delete snmp v3 user <username>

# 3. 커밋
commit
```

**Step 2) 관리를 위해 NMS 솔루션과의 연동이 필요하다면 SNMP 설정**

**SNMP 설정 (사용이 필요한 경우):**

```bash
# 1. SNMPv3 사용 권장 (암호화 지원)
# Cisco ASA 예시
snmp-server group SNMPv3-GROUP v3 priv
snmp-server user admin SNMPv3-GROUP v3 auth sha <password> priv aes 128 <password>
snmp-server host inside 192.168.1.10 informs version 3 priv admin

# 2. SNMPv2c 사용 시 강력한 Community String 설정
snmp-server community <StrongCommunityString> RO  # Read Only
snmp-server host inside 192.168.1.10 <StrongCommunityString>

# 3. 접근 제어
# - 특정 IP만 허용
# - Read Only 권한만 부여
# - ACL 적용
```

### 4. 참고 자료

**SNMP(Simple Network Management Protocol)란?**

- 네트워크 장비를 원격으로 관리하기 위한 프로토콜
- UDP 포트 161(SNMP queries), 162(SNMP traps) 사용

**버전별 특징:**
- **SNMPv1/v2c**: Community String 기반 인증, 평문 전송 (취약)
- **SNMPv3**: 암호화 및 인증 지원 (보안 강화됨)

**보안 문제점:**
- Community String이 평문으로 전송 (v1, v2c)
- 무차별 대입 공격 취약
- DoS 공격에 취약
- 많은 알려진 취약점 존재

**대안 모니터링 방법**

```bash
# SNMP 대신 사용할 수 있는 모니터링 방법

# 1. CLI/API
# - SSH를 통한 명령어 실행
# - REST API 사용
# - 예: show cpu, show memory

# 2. Syslog
# - 로그 전송
# - 이벤트 모니터링

# 3. NetFlow/sFlow
# - 트래픽 분석
# - 프로토콜 분석

# 4. SNMP Proxy
# - 별도 서버에서만 SNMP 허용
# - 보안 강화된 중계 서버
```

**주의사항**
- 일반적인 경우 영향이 없습니다.
- **영향도 확인**: SNMP를 사용하는 시스템(NMS)이 있는지 확인하세요.
- **대안 마련**: SNMP 대신 다른 모니터링 방법을 마련하세요.
- **테스트**: SNMP 중지 후 모니터링 기능을 테스트하세요.
- **문서화**: SNMP 중지 사유를 문서화하세요.
- **필요시 SNMPv3**: SNMP 사용이 필요하면 반드시 SNMPv3를 사용하세요.

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.