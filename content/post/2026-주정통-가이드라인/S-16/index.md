---
title: "[2026 주요정보통신기반시설] S-16 NAT 설정"
slug: "2026-주정통/S-16"
date: 2026-02-05T09:56:12+09:00
lastmod: 2026-02-05T09:56:12+09:00
description: "외부 공개 필요성이 없는 정보시스템에 NAT 설정 여부를 점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Security
---

# S-16 NAT 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | S-16 |
| **점검내용** | 외부 공개 필요성이 없는 정보시스템에 NAT 설정 여부를 점검 |
| **점검대상** | 방화벽, VPN 등 |
| **양호기준** | 외부 공개 필요성이 없는 서버, 단말기 등 정보시스템에 대해 NAT 설정을 적용한 경우 |
| **취약기준** | 외부 공개 필요성이 없는 서버, 단말기 등 정보시스템에 대해 NAT 설정을 적용하지 않은 경우 |
| **조치방법** | 외부 공개 필요성이 없는 정보시스템에 대해 공인 IP 지정 여부를 확인하여 사설 IP로 변경한 후 보안 장비에서 NAT 설정을 적용 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준

**양호**
- 외부 공개 필요성이 없는 서버, 단말기 등 정보시스템에 대해 NAT 설정을 적용한 경우
- 내부 사설 IP를 사용하는 경우

**취약**
- 외부 공개 필요성이 없는 서버, 단말기 등 정보시스템에 대해 NAT 설정을 적용하지 않은 경우
- 내부 시스템에 공인 IP 직접 할당

#### 경계 케이스 (Edge Case) 처리 방법

1. **공개 서비스**
   - 웹 서버, 메일 서버 등은 Static NAT 필요
   - DMZ에 배치 후 별도 정책 적용

2. **레거시 시스템**
   - 공인 IP 고정 필요시 방화벽 정책으로 보완

#### 권장 설정값

- 내부 IP: 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16 (사설 IP 대역)
- NAT 방식: PAT (Port Address Translation) 권장
- 공개 서비스: Static NAT (DMZ)

### 2. 점검 방법

**Step 1) 공인 IP 확인 사이트 (포털 등)에 접속하여 사용 중인 단말의 IP 확인**

```bash
# 1. 내부 IP 확인
ipconfig  # Windows
ifconfig  # Linux
# IP Address: 192.168.1.100 (사설 IP)

# 2. 외부에서 보이는 IP 확인
# 웹브라우저에서 https://www.findip.com/ 접속
# 또는
curl ifconfig.me
# 203.0.113.1 (공인 IP)

# 3. 결과 해석
# 내부 IP(사설)와 외부 IP(공인)가 다르면 NAT 적용됨
# 내부 IP가 공인 IP 대역이면 NAT 미적용 (취약)
```

**Step 2) 공인 IP 대역 확인**

```bash
# 공인 IP 대역 (예시)
# 1.0.0.0 ~ 1.255.255.255 (APNIC)
# 203.0.113.0 ~ 203.0.113.255 (TEST-NET-3)

# 사설 IP 대역 (RFC 1918)
# 10.0.0.0 ~ 10.255.255.255 (10.0.0.0/8)
# 172.16.0.0 ~ 172.31.255.255 (172.16.0.0/12)
# 192.168.0.0 ~ 192.168.255.255 (192.168.0.0/16)
```

### 3. 조치 방법

**Step 1) 외부 공개 필요성이 없는 정보시스템에 대해 사설 IP로 변경**

```bash
# 1. 현재 IP 설정 확인
ipconfig /all
# IPv4 Address. . . . . . . . . . . : 203.0.113.100(공인)

# 2. 사설 IP로 변경
# IPv4 Address. . . . . . . . . . . : 192.168.1.100(사설)
# Subnet Mask . . . . . . . . . . . : 255.255.255.0
# Default Gateway . . . . . . . . . : 192.168.1.1
```

**Step 2) 보안 장비에서 NAT 설정 적용**

**Cisco ASA NAT 설정:**

```bash
# 1. 내부 네트워크 정의
object network INTERNAL_NET
  subnet 192.168.1.0 255.255.255.0

# 2. 외부 인터페이스 PAT 설정
nat (inside,outside) after-auto source dynamic any interface

# 3. 특정 서버를 위한 Static NAT (필요시)
object network WEB_SERVER
  host 192.168.1.10
nat (inside,outside) static interface service tcp www www

# 4. NAT 확인
show xlate
show nat
```

**Palo Alto Firewall NAT 설정:**

```bash
# 1. Source NAT 설정
# Network > NAT > Source NAT

# Name: Internal_to_Internet
# Source Address: 192.168.1.0/24
# Translation Type: Dynamic IP
# Translated Address: interface (outside)

# 2. Static NAT (웹 서버)
# Network > NAT > Static NAT

# Name: Web_Server
# Original Address: 192.168.1.10
# Translated Address: 203.0.113.10
# Service: tcp/80

# 3. 커밋
commit
```

### 4. 참고 자료

**NAT(Network Address Translation)란?**

- 네트워크 주소 변환 기술
- 사설 IP 주소를 공인 IP 주소로 변환
- 내부 네트워크 구조를 외부에 숨김

**NAT 종류**

1. **Static NAT (정적 NAT)**
   - 1:1 매핑 (사설 IP → 공인 IP)
   - 웹 서버, 메일 서버 등 공개 서비스에 사용

2. **Dynamic NAT (동적 NAT)**
   - 사설 IP 풀 → 공인 IP 풀 동적 매핑
   - 일반적인 인터넷 접속에 사용

3. **PAT (Port Address Translation)**
   - 여러 사설 IP → 하나의 공인 IP + 포트 번호
   - 가장 일반적으로 사용됨 (NAT Overload)

**주의사항**
- 일반적인 경우 영향이 없습니다.
- **필요한 서비스**: 웹 서버, 메일 서버 등 공개 서비스는 Static NAT가 필요합니다.
- **DNS 설정**: 공개 서버의 DNS A 레코드를 공인 IP로 설정하세요.
- **포트 포워딩**: 특정 포트만 내부로 포워딩하세요.
- **로그 기록**: NAT 변환 로그를 기록하여 추적 가능하게 하세요.
- **테스트**: NAT 적용 후 서비스 연결을 테스트하세요.
- **대부분의 네트워크 보안 제품들은 NAT 기술을 기본으로 채택하고 있으므로 내부 사설 IP 부여 정책에 맞춰 적용하도록 합니다.**

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.