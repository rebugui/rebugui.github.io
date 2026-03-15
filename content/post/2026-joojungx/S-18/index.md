---
title: "[2026 주요정보통신기반시설] S-18 최소한의 서비스만 제공"
slug: "2026-주정통/S-18"
date: 2026-02-05T09:56:12+09:00
lastmod: 2026-02-05T09:56:12+09:00
description: "보안장비에서 필요한 서비스만 제공하고 있는지 점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Security
---

# S-18 최소한의 서비스만 제공

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | S-18 |
| **점검내용** | 보안장비에서 필요한 서비스만 제공하고 있는지 점검 |
| **점검대상** | 방화벽, VPN, 웹방화벽 등 |
| **양호기준** | All Deny 설정 및 보안장비에 최소 서비스만 허용하는 경우 |
| **취약기준** | All Deny 미설정 또는 보안장비에 불필요한 서비스를 허용하는 경우 |
| **조치방법** | 보안장비에 최소 서비스만 허용하도록 설정함 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준

**양호**
- All Deny 설정 및 보안장비에 최소 서비스만 허용하는 경우
- 기본 정책이 모든 트래픽 차단인 경우

**취약**
- All Deny 미설정 또는 보안장비에 불필요한 서비스를 허용하는 경우
- All Allow 등 개방형 정책이 설정된 경우

#### 경계 케이스 (Edge Case) 처리 방법

1. **레거시 서비스**
   - 필요한 포트만 명시적 허용
   - 정기적인 재검토

2. **임시 서비스**
   - 만료일 설정 필수
   - 사용 후 즉시 삭제

#### 권장 설정값

- 기본 정책: All Deny (모든 트래픽 차단)
- 허용 서비스: 업무에 필요한 최소한의 서비스만
- 허용 포트: HTTP(80), HTTPS(443), DNS(53), SMTP(25) 등

### 2. 점검 방법

**Step 1) 방화벽에서 허용되지 않은 포트 접속 확인**

```bash
# 1. 방화벽 정책 확인
show access-list

# 취약 예시 (All Allow)
access-list outside_in permit ip any any  ← 문제!

# 양호 예시 (All Deny)
access-list outside_in deny ip any any
access-list outside_in permit tcp any host 203.0.113.10 eq 80
access-list outside_in permit tcp any host 203.0.113.10 eq 443

# 2. 허용된 서비스 목록 확인
# - 웹: 80/tcp, 443/tcp
# - 메일: 25/tcp, 587/tcp
# - DNS: 53/tcp, 53/udp
# - VPN: 1194/udp, 443/tcp

# 3. 불필요한 포트 확인
nmap -p- 203.0.113.10
# 열린 포트가 업무에 필요한 포트만 있는지 확인
```

### 3. 조치 방법

**Step 1) 방화벽 기본 정책인 All Deny 설정**

**Cisco ASA All Deny 설정:**

```bash
# 1. 기본 정책 설정
access-list OUTSIDE_IN deny ip any any

# 2. 필요한 서비스만 명시적 허용
# 웹 서비스
access-list OUTSIDE_IN permit tcp any host 203.0.113.10 eq 80
access-list OUTSIDE_IN permit tcp any host 203.0.113.10 eq 443

# 메일 서비스
access-list OUTSIDE_IN permit tcp any host 203.0.113.11 eq 25
access-list OUTSIDE_IN permit tcp any host 203.0.113.11 eq 587

# DNS 서비스
access-list OUTSIDE_IN permit udp any host 203.0.113.12 eq 53
access-list OUTSIDE_IN permit tcp any host 203.0.113.12 eq 53

# 3. 정책 적용
access-group OUTSIDE_IN in interface outside

# 4. 확인
show access-list
```

**Step 2) 불필요한 서비스 차단**

```bash
# 1. 현재 허용된 서비스 분석
show access-list

# 2. 불필요한 서비스 식별
# - 테스트용 서비스
# - 더 이상 사용하지 않는 서비스
# - 업무와 무관한 서비스

# 3. 불필요한 서비스 제거
no access-list OUTSIDE_IN permit tcp any host 203.0.113.10 eq 8080

# 4. 문서화
# 제거한 서비스, 제거 사유, 일자 기록
```

### 4. 참고 자료

**일반적으로 허용하는 서비스**

| 서비스 | 프로토콜 | 포트 | 비고 |
|--------|----------|------|------|
| 웹(HTTP) | TCP | 80 | SSL/TLS 권장 |
| 웹(HTTPS) | TCP | 443 | 필수 |
| 메일(SMTP) | TCP | 25 | 릴레이 제한 필요 |
| 메일 제출 | TCP | 587 | 인증 필수 |
| DNS | TCP/UDP | 53 | 쿼리만 허용 |
| FTP | TCP | 20, 21 | SFTP 권장 |
| SSH | TCP | 22 | 관리용만 허용 |
| VPN(IPsec) | UDP | 500, 4500 | VPN 서비스만 |
| NTP | UDP | 123 | 신뢰된 서버만 |

**차단해야 할 서비스**

| 서비스 | 포트 | 위험도 | 비고 |
|--------|------|--------|------|
| Telnet | TCP 23 | 높음 | 평문 통신, SSH로 대체 |
| HTTP(비암호화) | TCP 80 | 중간 | HTTPS로 대체 |
| FTP(비암호화) | TCP 20, 21 | 중간 | SFTP로 대체 |
| RDP | TCP 3389 | 높음 | VPN+RDP 권장 |
| SMB | TCP 445 | 높음 | 내부 전용 |
| NetBIOS | TCP 137-139 | 높음 | 내부 전용 |
| SQL Direct | TCP 1433, 3306 | 높음 | 애플리케이션 경유 |
| ICMP | - | 중간 | 필요시 크기 제한 |

**주의사항**
- 허용되지 않은 접속은 모두 차단됩니다.
- **영향도 분석**: 서비스 차단 전 반드시 영향도를 분석하세요.
- **테스트**: 테스트 환경에서 먼저 검증하세요.
- **담당자 협의**: 해당 서비스 이용자와 협의하세요.
- **모니터링**: 차단 후 로그를 모니터링하여 문제 확인하세요.
- **예외 처리**: 필요한 경우 예외 규칙을 명시적으로 추가하세요.
- **문서화**: 모든 허용/차단 규칙을 문서화하세요.

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.