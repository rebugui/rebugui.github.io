---
title: "[2026 주요정보통신기반시설] U-45 메일 서비스 버전 점검"
slug: "2026-주정통/U-45"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "취약한버전의메일서비스이용여부점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-45 메일 서비스 버전 점검

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-45 |
| **점검내용** | 취약한버전의메일서비스이용여부점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX등 |
| **양호기준** | 메일서비스버전이최신버전인경우 |
| **취약기준** | 메일서비스버전이최신버전이아닌경우 |
| **조치방법** | 메일서비스를사용하지않는경우서비스중지및비활성화설정, 메일서비스사용시패치관리정책을수립하여주기적으로패치적용설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 메일 서비스가 최신 보안 패치가 적용된 경우
- **취약**: 메일 서비스가 구버전이거나 알려진 취약점이 있는 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| Sendmail 8.15.2 이상 | 양호 | 최신 안정 버전 |
| Sendmail 8.11.x 이하 | 취약 | 심각한 취약점 존재 |
| Postfix 3.0 이상 | 양호 | 현대적 MTA |
| 오픈 릴레이 상태 | 취약 | 스팸 발송 악용 |
| 배너에 버전 노출 | 주의 | 정보 노출 위험 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| All MTA | 버전 | 최신 보안 패치 적용 | 주요 업데이트 |
| Postfix | smtpd_banner | 배너 정보 최소화 | /etc/postfix/main.cf |
| Sendmail | PrivacyOptions | noexpn,novrfy | /etc/mail/sendmail.cf |
| All MTA | 릴레이 제한 | 로컬/인증만 허용 | 스팸 방지 |

### 2. 점검 방법

#### Linux 점검

메일 서비스 버전을 확인하고 최신 보안 패치가 적용되었는지 점검해야 합니다.

```bash
# 1. 메일 서비스 버전 확인
echo "=== 1. Mail Service Version ==="
sendmail -d0.1 -bt < /dev/null 2>&1 | grep Version
postconf mail_version 2>/dev/null
exim -bV 2>/dev/null | grep "Exim version"

# 2. 포트 listening 확인
echo "=== 2. SMTP Port ==="
netstat -tuln | grep :25

# 3. SMTP 배너 확인
echo "=== 3. SMTP Banner ===
(echo "QUIT"; sleep 1) | nc localhost 25 2>/dev/null | head -5

# 4. 릴레이 테스트
echo "=== 4. Relay Test (Manual) ==="
# 외부에서 테스트 필요 (nmap --script smtp-open-relay)
```

**양호 출력 예시:**
```text
=== 1. Mail Service Version ===
Version 8.15.2
2.3.5
=== 3. SMTP Banner ===
220 mail.example.com ESMTP Postfix
```

**취약 출력 예시:**
```text
=== 1. Mail Service Version ===
Version 8.11.7
=== 3. SMTP Banner ===
220 target-server ESMTP Sendmail 8.11.7/8.11.6
```

### 3. 조치 방법

#### 패치 적용

1. **RHEL/CentOS**
   ```bash
   yum update sendmail
   yum update postfix
   yum update exim
   ```

2. **Ubuntu/Debian**
   ```bash
   apt update
   apt upgrade sendmail postfix exim4
   ```

3. **서비스 재시작**
   ```bash
   systemctl restart postfix
   # 또는
   systemctl restart sendmail
   ```

#### 배너 숨김

1. **Postfix 설정**
   ```bash
   # /etc/postfix/main.cf
   smtpd_banner = $myhostname ESMTP

   systemctl restart postfix
   ```

2. **Sendmail 설정**
   ```bash
   # /etc/mail/sendmail.cf
   O SmtpGreetingMessage=mail.example.com ESMTP
   ```

### 4. 참고 자료

- CIS Benchmark for Linux: 메일 서비스 보안 권고
- NIST SP 800-53: SI-2 (취약점 보완)
- Postfix Documentation: 설정 가이드
- Sendmail Security: CVE 정보

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.