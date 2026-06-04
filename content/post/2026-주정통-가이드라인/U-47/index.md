---
title: "[2026 주요정보통신기반시설] U-47 스팸 메일 릴레이 제한"
slug: "2026-주정통/U-47"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "SMTP서버의릴레이기능제한여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-47 스팸 메일 릴레이 제한

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-47 |
| **점검내용** | SMTP서버의릴레이기능제한여부점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX등 |
| **양호기준** | 릴레이제한이설정된경우 |
| **취약기준** | 릴레이제한이설정되어있지않은경우 |
| **조치방법** | 메일서비스를사용하지않는경우서비스중지및비활성화설정, 메일서비스사용시릴레이방지설정또는릴레이대상접근제어설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 오픈 릴레이가 차단되고 인증된 사용자/내부 IP만 릴레이 가능한 경우
- **취약**: 오픈 릴레이 상태로任何人이 메일을 중계할 수 있는 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| mynetworks에 외부 IP 포함 | 취약 | 오픈 릴레이 가능성 |
| smtpd_relay_restrictions 미설정 | 취약 | 기본값이 헐거울 수 있음 |
| SASL 인증 활성화 | 양호 | 인증된 사용자만 릴레이 |
| IP 화이트리스트 | 양호 | 신뢰된 IP만 허용 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| Postfix | mynetworks | 127.0.0.0/8, 내부대역 | /etc/postfix/main.cf |
| Postfix | smtpd_relay_restrictions | permit_mynetworks, permit_sasl_authenticated, defer_unauth_destination | 릴레이 제한 |
| Sendmail | access.db | RELAY 허용 IP만 등록 | /etc/mail/access |

### 2. 점검 방법

#### Linux 점검

오픈 릴레이 상태를 확인하여 스팸 발송에 악용되지 않도록 해야 합니다.

```bash
# 1. Postfix 릴레이 설정 확인
echo "=== 1. Postfix Relay Settings ==="
postconf mynetworks
postconf smtpd_relay_restrictions

# 2. Sendmail 릴레이 설정 확인
echo "=== 2. Sendmail Relay Settings ==="
grep -E "^[^#]" /etc/mail/access | grep RELAY

# 3. 수동 릴레이 테스트 (로컬에서)
echo "=== 3. Relay Test (Local) ==="
# 외부에서: telnet target-server 25
# MAIL FROM:<spam@evil.com>
# RCPT TO:<victim@external.com>
```

**양호 출력 예시:**
```text
=== 1. Postfix Relay Settings ===
mynetworks = 127.0.0.0/8, 192.168.1.0/24
smtpd_relay_restrictions = permit_mynetworks, permit_sasl_authenticated, defer_unauth_destination
```

**취약 출력 예시:**
```text
=== 1. Postfix Relay Settings ===
mynetworks = 0.0.0.0/0
```

### 3. 조치 방법

#### Postfix 설정

1. **릴레이 제한 설정**
   ```bash
   # /etc/postfix/main.cf 수정
   vi /etc/postfix/main.cf

   # 추가/수정:
   mynetworks = 127.0.0.0/8, 192.168.1.0/24
   smtpd_relay_restrictions = permit_mynetworks, permit_sasl_authenticated, defer_unauth_destination

   # 재시작
   systemctl restart postfix
   ```

2. **SASL 인증 활성화**
   ```bash
   # /etc/postfix/main.cf
   smtpd_sasl_auth_enable = yes
   smtpd_sasl_type = dovecot
   smtpd_sasl_path = private/auth
   ```

#### Sendmail 설정

1. **access.db 설정**
   ```bash
   # /etc/mail/access
   echo "Connect:192.168.1       RELAY" >> /etc/mail/access
   echo "Connect:localhost       RELAY" >> /etc/mail/access
   echo "Connect:127.0.0.1        RELAY" >> /etc/mail/access

   makemap hash /etc/mail/access < /etc/mail/access
   systemctl restart sendmail
   ```

### 4. 참고 자료

- CIS Benchmark for Linux: 메일 릴레이 제한 권고
- NIST SP 800-53: AC-4 (정보 흐름 제어)
- Postfix Documentation: 릴레이 제어
- RFC 5321: SMTP 릴레이 사양

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.