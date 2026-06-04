---
title: "[2026 주요정보통신기반시설] U-48 expn, vrfy 명령어 제한"
slug: "2026-주정통/U-48"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "SMTP서비스사용시expn,vrfy명령어사용금지설정여부점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-48 expn, vrfy 명령어 제한

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-48 |
| **점검내용** | SMTP서비스사용시expn,vrfy명령어사용금지설정여부점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX등 |
| **양호기준** | noexpn, novrfy옵션이설정된경우 |
| **취약기준** | noexpn, novrfy옵션이설정되어있지않은경우 |
| **조치방법** | 메일서비스를사용하지않는경우서비스중지및비활성화설정, 메일서비스사용시메일서비스설정파일에noexpn,novrfy또는goaway옵션추가설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: EXPN, VRFY 명령어가 비활성화된 경우
- **취약**: EXPN, VRFY 명령어가 활성화된 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| PrivacyOptions에 noexpn,novrfy | 양호 | 명령어 차단 |
| VRFY로 계정 열거 가능 | 취약 | 정보 노출 |
| EXPN으로 메일링 리스트 노출 | 취약 | 사용자 정보 유출 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| Sendmail | PrivacyOptions | noexpn,novrfy 포함 | /etc/mail/sendmail.cf |
| Postfix | disable_vrfy_command | yes | /etc/postfix/main.cf |

### 2. 점검 방법

#### Linux, Solaris 점검

EXPN/VRFY 명령어로 사용자 계정 정보가 노출되지 않도록 차단해야 합니다.

```bash
# 1. Sendmail 설정 확인
echo "=== 1. Sendmail PrivacyOptions ==="
grep -i "PrivacyOptions" /etc/mail/sendmail.cf

# 2. Postfix 설정 확인
echo "=== 2. Postfix VRFY ==="
postconf disable_vrfy_command

# 3. VRFY 명령어 테스트
echo "=== 3. VRFY Test ==="
(echo "VRFY root"; echo "QUIT") | nc localhost 25 2>/dev/null | head -5
```

**양호 출력 예시:**
```text
=== 1. Sendmail PrivacyOptions ===
O PrivacyOptions=authwarnings,noexpn,novrfy,restrictqrun
=== 2. Postfix VRFY ===
disable_vrfy_command = yes
=== 3. VRFY Test ===
502 5.5.2 VRFY command disabled
```

**취약 출력 예시:**
```text
=== 1. Sendmail PrivacyOptions ===
O PrivacyOptions=authwarnings
=== 3. VRFY Test ===
252 2.0.0 root
```

### 3. 조치 방법

#### Sendmail 설정

1. **noexpn, novrfy 옵션 추가**
   ```bash
   # /etc/mail/sendmail.cf 수정
   vi /etc/mail/sendmail.cf

   # 추가/수정:
   O PrivacyOptions=authwarnings,noexpn,novrfy,restrictqrun

   # sendmail 재시작
   systemctl restart sendmail
   ```

#### Postfix 설정

1. **VRFY 비활성화**
   ```bash
   # /etc/postfix/main.cf
   echo "disable_vrfy_command = yes" >> /etc/postfix/main.cf

   # 재시작
   systemctl restart postfix
   ```

2. **확인**
   ```bash
   (echo "VRFY root"; echo "QUIT") | nc localhost 25
   # "502 5.5.2 VRFY command disabled" 메시지 확인
   ```

### 4. 참고 자료

- CIS Benchmark for Linux: SMTP 보안 권고
- NIST SP 800-53: AC-17 (공격 완화)
- RFC 5321: SMTP 명령어 사양
- man pages: sendmail(8), postconf(5)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.