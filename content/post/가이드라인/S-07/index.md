---
title: "[2026 주요정보통신기반시설] S-07 보안장비 보안접속"
slug: "2026-주정통/S-07"
date: 2026-02-05T09:56:12+09:00
lastmod: 2026-02-05T09:56:12+09:00
description: "보안장비 접속 시 암호화 프로토콜을 이용한 접속 여부 점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Security
---

# S-07 보안장비 보안접속

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | S-07 |
| **점검내용** | 보안장비 접속 시 암호화 프로토콜을 이용한 접속 여부 점검 |
| **점검대상** | 방화벽, VPN, IDS, IPS, Anti-DDoS, 웹방화벽 등 |
| **양호기준** | 보안장비 접속 시 암호화 통신을 하는 경우 |
| **취약기준** | 보안장비 접속 시 암호화 통신을 하지 않는 경우 |
| **조치방법** | 보안장비 접속 시, 가능하다면 SSL 등의 암호화 접속 활용 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준

**양호**
- 보안장비 접속 시 암호화 통신(SSH, HTTPS 등)을 하는 경우

**취약**
- 보안장비 접속 시 암호화 통신을 하지 않는 경우(Telnet, HTTP 사용)

#### 경계 케이스 (Edge Case) 처리 방법

1. **레거시 장비**
   - 암호화 프로토콜 지원 불가: 별도 보안 조치 권장
   - VPN 터널 내에서만 접속 허용

2. **마이그레이션 기간**
   - 단계적 전환: 테스트 환경에서 먼저 적용
   - 운영 환경: 유지보수 창에 적용

#### 권장 설정값

- SSH: 포트 22, SSHv2 사용
- HTTPS: 포트 443, TLS 1.2 이상
- Telnet: 비활성화
- HTTP: 비활성화 또는 HTTPS로 리다이렉트

### 2. 점검 방법

**Step 1) HTTPS 또는 SSH를 통한 접속 확인**

```bash
# SSH 접속 확인
ssh admin@<보안장비_IP>

# HTTPS 접속 확인
# 브라우저에서 https://<보안장비_IP> 접속
```

**확인 포인트:**
- SSH 포트(22)가 활성화되어 있는지 확인
- HTTPS 포트(443)가 활성화되어 있는지 확인
- HTTP(80), Telnet(23) 포트가 비활성화되어 있는지 확인

```bash
# 포트 확인 (Linux)
nmap -p 22,23,80,443 <보안장비_IP>

# 예상 결과
# 22/tcp open  ssh       ← 양호
# 23/tcp closed telnet   ← 양호
# 80/tcp closed http     ← 양호
# 443/tcp open https     ← 양호
```

### 3. 조치 방법

**Step 1) 보안 장비 접속 시 SSL, HTTPS 등의 암호화 접속 활용**

**SSH 설정 가이드:**

```bash
# 1. SSH 서비스 활성화 (장비별 설정 메뉴에서)
# System > Configuration > SSH > Enable

# 2. SSH 버전 설정 (SSHv2 사용 권장)
Protocol 2

# 3. 인증 방법 설정
# 공개키 인증 또는 비밀번호 인증 선택

# 4. 접속 허용 IP 설정 (필요시)
PermitRootLogin no
AllowUsers admin@<관리자_IP>
```

**HTTPS 설정 가이드:**

```bash
# 1. SSL/TLS 인증서 설치
# System > Configuration > SSL > Certificate

# 2. HTTPS 서비스 활성화
# System > Configuration > HTTP > HTTPS Enable

# 3. HTTP 포트 비활성화 또는 HTTPS로 리다이렉트
# System > Configuration > HTTP > Redirect to HTTPS
```

**Step 2) Telnet/HTTP 서비스 비활성화**

```bash
# Telnet 서비스 중지
# System > Configuration > Telnet > Disable

# HTTP 서비스 중지
# System > Configuration > HTTP > Disable
```

**Step 3) 암호화 강도 설정**

```bash
# SSL/TLS 버전 설정 (TLS 1.2 이상 권장)
# System > Configuration > SSL > TLS Version

# 암호화 스위트(Cipher Suite) 설정
# 강력한 암호화 알고리즘만 사용
AES256-SHA
RSA-WITH-AES-256-CBC-SHA
```

### 4. 참고 자료

- SSH 프로토콜: https://www.ssh.com/
- TLS/SSL 프로토콜: https://tools.ietf.org/html/rfc8446

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.