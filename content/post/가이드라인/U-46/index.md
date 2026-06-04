---
title: "[2026 주요정보통신기반시설] U-46 일반 사용자의 메일 서비스 실행 방지"
slug: "2026-주정통/U-46"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "SMTP서비스사용시일반사용자의q옵션제한여부점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-46 일반 사용자의 메일 서비스 실행 방지

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-46 |
| **점검내용** | SMTP서비스사용시일반사용자의q옵션제한여부점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX등 |
| **양호기준** | 일반사용자의메일서비스실행방지가설정된경우 |
| **취약기준** | 일반사용자의메일서비스실행방지가설정되어있지않은경우 |
| **조치방법** | 메일서비스를사용하지않는경우서비스중지및비활성화설정, 메일서비스사용시메일서비스의q옵션제한설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: restrictqrun 옵션이 설정된 경우
- **취약**: restrictqrun 옵션이 설정되지 않은 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| PrivacyOptions에 restrictqrun | 양호 | 큐 처리 제한 |
| 일반 사용자가 sendmail -q 실행 가능 | 취약 | 큐 조작 가능 |
| sendmail SUID root | 취약 | 권한 상승 위험 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| Sendmail | PrivacyOptions | restrictqrun 포함 | /etc/mail/sendmail.cf |
| Postfix | smtpd_*_restrictions | 적절한 제한 설정 | /etc/postfix/main.cf |

### 2. 점검 방법

#### Linux, Solaris 점검

일반 사용자가 메일 큐를 임의로 조작할 수 없도록 제한해야 합니다.

```bash
# 1. Sendmail 설정 확인
echo "=== 1. Sendmail PrivacyOptions ==="
grep -i "PrivacyOptions" /etc/mail/sendmail.conf 2>/dev/null
grep -i "O PrivacyOptions" /etc/mail/sendmail.cf 2>/dev/null

# 2. sendmail 권한 확인
echo "=== 2. sendmail Permissions ==="
ls -l /usr/sbin/sendmail /usr/lib/sendmail 2>/dev/null
```

**양호 출력 예시:**
```text
=== 1. Sendmail PrivacyOptions ===
O PrivacyOptions=authwarnings,noexpn,novrfy,restrictqrun
```

**취약 출력 예시:**
```text
=== 1. Sendmail PrivacyOptions ===
O PrivacyOptions=authwarnings
```

### 3. 조치 방법

#### Sendmail 설정

1. **restrictqrun 옵션 추가**
   ```bash
   # /etc/mail/sendmail.cf 또는 /etc/mail/sendmail.conf 수정
   vi /etc/mail/sendmail.cf

   # 추가/수정:
   O PrivacyOptions=authwarnings,noexpn,novrfy,restrictqrun

   # sendmail 재시작
   systemctl restart sendmail
   ```

### 4. 참고 자료

- CIS Benchmark for Linux: Sendmail 보안 권고
- NIST SP 800-53: AC-6 (최소 권한)
- Sendmail Configuration: PrivacyOptions 설명

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.