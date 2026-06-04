---
title: "[2026 주요정보통신기반시설] U-66 정책에 따른 시스템 로깅 설정"
slug: "2026-주정통/U-66"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "내부 정책에 따른 시스템 로깅 설정 여부 점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-66 정책에 따른 시스템 로깅 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-66 |
| **점검내용** | 내부 정책에 따른 시스템 로깅 설정 여부 점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX 등 |
| **양호기준** | 로그 기록 정책이 보안 정책에 따라 설정되어 수립되어 있으며, 로그를 남기고 있는 경우 |
| **취약기준** | 로그 기록 정책 미수립 또는 정책에 따라 설정되어 있지 않거나, 로그를 남기고 있지 않은 경우 |
| **조치방법** | 로그 기록 정책을 수립하고, 정책에 따라 (r)syslog.conf 파일을 설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: rsyslog.conf 또는 syslog.conf에 주요 로그 시설(Facility)에 대한 기록 설정이 되어 있고 서비스가 실행 중인 경우
- **취약**: 로깅 설정이 없거나, 주요 이벤트가 기록되지 않는 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| authpriv.* 기록됨 | 양호 | 인증 로그 |
| *.info 기록됨 | 양호 | 일반 정보 |
| 로그 파일이 비어있음 | 취약 | 기록 안됨 |
| rsyslogd 실행 중 | 양호 | 서비스 활성 |
| 원격 로그 서버 전송 | 양호 | 중앙 집중 로깅 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| Linux | authpriv.* | /var/log/secure | 인증 로그 |
| Linux | *.info | /var/log/messages | 시스템 메시지 |
| Linux | mail.* | /var/log/maillog | 메일 로그 |
| Linux | cron.* | /var/log/cron | 스케줄 로그 |
| Linux | *.emerg | :omusrmsg:* | 긴급 알림 |
| 원격 | *.* | @@log-server:514 | TCP 전송 |

### 2. 점검 방법

#### Linux 점검

시스템에서 발생하는 주요 이벤트(인증 실패, 메일, 크론, 커널 등)를 빠짐없이 기록하여 보안 침해 사고 발생 시 추적 단서를 확보해야 합니다.

```bash
# 1. syslog/rsyslog 서비스 상태 확인
echo "=== 1. Syslog Service ==="
systemctl is-active rsyslog syslog 2>/dev/null
systemctl is-enabled rsyslog syslog 2>/dev/null

# 2. 설정 파일 확인
echo "=== 2. rsyslog.conf ==="
cat /etc/rsyslog.conf 2>/dev/null | grep -v "^#" | grep -v "^$" | head -20
cat /etc/syslog.conf 2>/dev/null | grep -v "^#" | grep -v "^$" | head -20

# 3. 주요 로그 파일 확인
echo "=== 3. Log Files ==="
ls -l /var/log/secure /var/log/messages /var/log/syslog /var/log/maillog /var/log/cron 2>/dev/null

# 4. 로그 파일 내용 확인 (최근 5줄)
echo "=== 4. Log Content (Recent) ==="
tail -5 /var/log/secure 2>/dev/null
tail -5 /var/log/messages 2>/dev/null
```

**양호 출력 예시:**
```text
=== 1. Syslog Service ===
rsyslog: active (running)
rsyslog: enabled
=== 2. rsyslog.conf ===
authpriv.*                                              /var/log/secure
*.info;mail.none;authpriv.none;cron.none                /var/log/messages
mail.*                                                  -/var/log/maillog
cron.*                                                  /var/log/cron
*.emerg                                                 :omusrmsg:*
=== 3. Log Files ===
-rw------- 1 root root 123456 Jan 20 10:00 /var/log/secure
-rw-r----- 1 root adm 789012 Jan 20 10:00 /var/log/syslog
```

**취약 출력 예시:**
```text
=== 1. Syslog Service ===
rsyslog: inactive (dead)
=== 2. rsyslog.conf ===
(설정이 없거나 주요 facility 기록 설정 없음)
=== 3. Log Files ===
ls: /var/log/secure: No such file or directory
```

### 3. 조치 방법

#### rsyslog 설정 (Linux)

1. **/etc/rsyslog.conf 편집**
   ```bash
   vi /etc/rsyslog.conf

   # 다음 내용 추가 또는 확인:
   # 인증 관련 로그 (로그인 성공/실패, sudo 등) - 필수
   authpriv.*                                              /var/log/secure

   # 시스템 메시지 (정보 수준 이상)
   *.info;mail.none;authpriv.none;cron.none                /var/log/messages

   # 메일 로그
   mail.*                                                  -/var/log/maillog

   # 크론 로그
   cron.*                                                  /var/log/cron

   # 긴급 메시지 (모든 사용자에게 알림)
   *.emerg                                                 :omusrmsg:*

   # 부팅 메시지
   kern.*                                                  /var/log/dmesg
   ```

2. **서비스 재시작**
   ```bash
   systemctl restart rsyslog
   systemctl status rsyslog
   ```

3. **로그 파일 생성 확인**
   ```bash
   # 로그 파일 확인
   ls -l /var/log/secure /var/log/messages /var/log/maillog /var/log/cron

   # 로그 기록 테스트
   logger "This is a test log message"
   tail /var/log/messages
   ```

#### 원격 로그 전송 (권장)

로컬 로그 파일은 해커에 의해 삭제될 수 있으므로, 별도의 통합 로그 서버로 전송하는 것이 좋습니다.

```bash
# /etc/rsyslog.conf에 추가
vi /etc/rsyslog.conf

# UDP 전송 (빠름 but 신뢰성 낮음)
*.* @192.168.10.10:514

# 또는 TCP 전송 (신뢰성 높음)
*.* @@192.168.10.10:514

# TLS 암호화 전송 (최신 권장)
# 별도 인증서 설정 필요

systemctl restart rsyslog
```

#### logrotate 설정

로그 파일이 너무 커지지 않도록 로테이션 설정을 확인합니다.

```bash
# /etc/logrotate.conf 확인
cat /etc/logrotate.conf

# 주요 설정 예시:
# weekly
# rotate 4
# create
# dateext

# 테스트
logrotate -d /etc/logrotate.conf
```

### 4. 참고 자료

- CIS Benchmark for Linux: syslog 설정 권고
- NIST SP 800-53: AU-3 (감사 기록 내용), AU-4 (감사 기록 보관)
- RFC 5424: The Syslog Protocol
- man pages: rsyslog.conf(5), syslog.conf(5)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.