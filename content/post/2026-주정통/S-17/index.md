---
title: "[2026 주요정보통신기반시설] S-17 DMZ 설정"
slug: "2026-주정통/S-17"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "내부 네트워크와 외부 서비스 네트워크(DMZ)를 구분하고 있는지 점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Security
---

# S-17 DMZ 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | S-17 |
| **점검내용** | 내부 네트워크와 외부 서비스 네트워크(DMZ)를 구분하고 있는지 점검 |
| **점검대상** | 방화벽, VPN 등 |
| **양호기준** | DMZ를 구성하여 내부 네트워크를 보호하는 경우 |
| **취약기준** | DMZ를 구성하지 않고 사설망에서 외부 공개 서비스를 제공하는 경우 |
| **조치방법** | DMZ를 구성하여 내부 네트워크와 외부 서비스 네트워크 분리<br>물리적(망분리)으로 내부 네트워크와 외부 서비스 네트워크가 분리되어 있으면 해당 없음 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준

**양호**
- DMZ를 구성하여 내부 네트워크를 보호하는 경우
- DMZ에서 내부 네트워크로의 접근이 차단된 경우

**취약**
- DMZ를 구성하지 않고 사설망에서 외부 공개 서비스를 제공하는 경우
- 내부 네트워크와 외부 서비스 네트워크가 분리되지 않은 경우

**해당 없음**
- 물리적 망분리로 내부 네트워크와 외부 서비스 네트워크가 분리된 경우

#### 경계 케이스 (Edge Case) 처리 방법

1. **물리적 망분리 환경**
   - 해당 없음으로 처리
   - 별도 DMZ 구성 불필요

2. **소규모 네트워크**
   - VLAN으로 논리적 분리 가능
   - 방화벽 규칙으로 보안 강화

#### 권장 설정값

- DMZ 네트워크: 별도 네트워크 대역 (예: 192.168.2.0/24)
- 방화벽: 이중 방화벽 구성 권장
- DMZ→내부 차단: 모든 트래픽 차단 (필요시 예외)

### 2. 점검 방법

**Step 1) 네트워크 구성도 또는 방화벽 설정 확인**

```bash
# 1. 네트워크 인터페이스 확인
show interface
# Interface inside: 192.168.1.1 (내부)
# Interface dmz: 192.168.2.1 (DMZ)
# Interface outside: 203.0.113.1 (외부)

# 2. 방화벽 규칙 확인
show access-list
# access-list OUTSIDE_IN permit tcp any host 203.0.113.10 eq www
# access-list DMZ_TO_INSIDE deny ip any any  ← DMZ→내부 차단
```

### 3. 조치 방법

**Step 1) DMZ 구성 방법**

**방법 1: 삼각 방화벽 설정 (Three-legged Firewall)**

```bash
# 네트워크 구성
# 인터넷
#   ↓
# 방화벽 (3개 인터페이스)
#   ├─ 외부 (outside): 203.0.113.1
#   ├─ DMZ (dmz): 192.168.2.1
#   └─ 내부 (inside): 192.168.1.1

# Cisco ASA 설정 예시
# 1. 인터페이스 설정
interface GigabitEthernet0/0
  nameif outside
  security-level 0
  ip address 203.0.113.1 255.255.255.0

interface GigabitEthernet0/1
  nameif dmz
  security-level 50
  ip address 192.168.2.1 255.255.255.0

interface GigabitEthernet0/2
  nameif inside
  security-level 100
  ip address 192.168.1.1 255.255.255.0

# 2. 방화벽 규칙 설정
# 외부 → DMZ (허용)
access-list OUTSIDE_IN permit tcp any host 203.0.113.10 eq www
access-group OUTSIDE_IN in interface outside

# DMZ → 내부 (차단)
access-list DMZ_TO_INSIDE deny ip any any
access-group DMZ_TO_INSIDE in interface dmz

# 내부 → DMZ (필요시 허용)
access-list INSIDE_TO_DMZ permit tcp 192.168.1.0 255.255.255.0 host 192.168.2.10 eq ssh
access-group INSIDE_TO_DMZ in interface inside
```

**Step 2) DMZ 보안 정책 설정**

```bash
# 1. 네트워크 분리
# - 외부: 203.0.113.0/24
# - DMZ: 192.168.2.0/24
# - 내부: 192.168.1.0/24

# 2. 방화벽 규칙

# 외부 → DMZ
permit tcp any host 203.0.113.10 eq 80    # 웹
permit tcp any host 203.0.113.11 eq 25   # 메일
permit tcp any host 203.0.113.12 eq 53   # DNS

# DMZ → 내부 (모두 차단)
deny ip any any

# 내부 → DMZ (필요시만 허용)
permit tcp 192.168.1.0/24 host 192.168.2.10 eq 22  # SSH 관리
```

### 4. 참고 자료

**DMZ(Demilitarized Zone)란?**

- 내부 네트워크(Trusted)와 외부 네트워크(Untrusted) 사이의 완충 지대
- 외부에 공개하는 서비스를 배치하는 별도의 네트워크 구간

**DMZ에 배치하는 서비스**
- 웹 서버
- 메일 서버
- DNS 서버
- FTP 서버
- VPN 게이트웨이
- 기타 외부 공개 서비스

**주의사항**
- 일반적인 경우 영향이 없습니다.
- **필요한 서비스 허용**: 내부 네트워크에서 DMZ 서버로의 관리 접속은 허용해야 합니다.
- **데이터베이스 연결**: 웹 서버가 내부 DB에 접속해야 하는 경우 특정 포트만 허용하세요.
- **로그 기록**: DMZ와 내부맥 간의 모든 트래픽을 로깅하세요.
- **정기 검토**: DMZ 서버의 보안 설정을 정기적으로 검토하세요.
- **백업**: DMZ 서버도 정기적으로 백업하세요.
- **모니터링**: DMZ 서버의 이상 징후를 실시간으로 모니터링하세요.

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.