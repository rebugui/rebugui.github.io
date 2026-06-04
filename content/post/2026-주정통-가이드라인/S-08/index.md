---
title: "[2026 주요정보통신기반시설] S-08 세션종료시간 설정"
slug: "2026-주정통/S-08"
date: 2026-02-05T09:56:12+09:00
lastmod: 2026-02-05T09:56:12+09:00
description: "보안장비의 정책에 Session Timeout 설정을 적용하였는지 점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Security
---

# S-08 세션종료시간 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | S-08 |
| **점검내용** | 보안장비의 정책에 Session Timeout 설정을 적용하였는지 점검 |
| **점검대상** | 방화벽, VPN, IDS, IPS, Anti-DDoS, 웹방화벽 등 |
| **양호기준** | Session Timeout을 설정한 경우 |
| **취약기준** | Session Timeout을 설정하지 않은 경우 |
| **조치방법** | Session Timeout 시간을 설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준

**양호**
- Session Timeout을 설정한 경우

**취약**
- Session Timeout을 설정하지 않은 경우

#### 경계 케이스 (Edge Case) 처리 방법

1. **장시간 작업 필요**
   - 별도 관리자 계정 생성: 긴 Timeout 설정
   - 작업 완료 후 즉시 로그아웃

2. **자동화 스크립트**
   - API 키 인증: 세션 타임아웃 면제
   - 별도 토큰 만료 시간 설정

#### 권장 설정값

- Console/SSH: 5~10분
- Web GUI: 10~15분
- VPN: 15~30분
- 보안성 최우선: 모든 접속 5분 이하

### 2. 점검 방법

**Step 1) 벤더별 설정값 확인**

대부분의 보안 장비는 기본으로 Session Timeout이 설정되어 있습니다. 장비별 설정 메뉴에서 확인합니다.

**Step 2) Console, SSL, VPN, SSH 등의 모든 원격 접근에 대한 Session Timeout 설정 확인**

```bash
# 설정 파일 확인 (장비별 상이)
# 예시: 방화벽 설정
show system session timeout

# 예시: Web GUI 확인
# System > Configuration > Session Timeout
```

**확인 포인트:**
- Console 접속 시 Session Timeout 설정 여부
- SSH 접속 시 Session Timeout 설정 여부
- Web GUI 접속 시 Session Timeout 설정 여부
- VPN 접속 시 Session Timeout 설정 여부
- Idle Timeout 값이 적절한지 확인 (일반적으로 5~15분 권장)

### 3. 조치 방법

**Step 1) 보안 장비가 제공하는 Session Timeout 기능 활성화 설정**

**Web 방화벽 예시:**

```bash
# Web GUI 설정
# System > Configuration > Session Management > Timeout

# Console Timeout: 10분
# SSH Timeout: 10분
# Web GUI Timeout: 15분
# VPN Timeout: 30분
```

**방화벽 예시 (CLI):**

```bash
# Cisco ASA
timeout xlate 3:00:00
timeout conn 1:00:00 half-closed 0:10:00 udp 0:02:00 icmp 0:00:02
timeout sunrpc 0:10:00 h323 0:05:00 h225 1:00:00 mgcp 0:05:00
timeout sip 0:30:00 sip_media 0:00:00
timeout sip-invite 0:30:00
timeout sip-disconnect 0:00:00

# Session timeout 설정
timeout session 0:10:00
```

**Step 2) 접속 방식별 Timeout 설정**

```bash
# 1. Console 접속 Timeout
console timeout 10

# 2. SSH 접속 Timeout
ssh timeout 10

# 3. HTTP/HTTPS 접속 Timeout
http server timeout 15
https server timeout 15

# 4. Idle Timeout (입력 없는 시간)
idle-timeout 10
```

**Step 3) 권장 설정 값**

```bash
# 보안성과 편의성의 균형
- Console/SSH: 5~10분
- Web GUI: 10~15분
- VPN: 15~30분

# 보안성 최우선
- 모든 접속: 5분 이하
```

### 4. 참고 자료

- 각 보안 장비 벤더사 매뉴얼 참조
- Cisco ASA Configuration Guide
- Palo Alto Firewall Administration Guide

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.