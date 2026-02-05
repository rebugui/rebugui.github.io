---
title: "[2026 주요정보통신기반시설] U-01 root 계정 원격 접속 제한"
slug: "2026-주정통/U-01"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "시스템 정책에 root 계정의 원격 터미널 접속 차단 설정이 적용 여부 점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-01 root 계정 원격 접속 제한

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-01 |
| **점검내용** | 시스템 정책에 root 계정의 원격 터미널 접속 차단 설정이 적용 여부 점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX 등 |
| **양호기준** | 원격 터미널 서비스를 사용하지 않거나, 사용 시 root 직접 접속을 차단한 경우 |
| **취약기준** | 원격 터미널 서비스 사용 시 root 직접 접속을 허용한 경우 |
| **조치방법** | 원격 접속 시 root 계정으로 접속할 수 없도록 설정 파일 내용 수정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 원격 터미널 서비스를 사용하지 않거나, 사용 시 root 직접 접속을 차단한 경우
- **취약**: 원격 터미널 서비스 사용 시 root 직접 접속을 허용한 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| PermitRootLogin prohibit-password | 부분 양호 | 키 기반 인증만 허용, 완전 차단 권장 |
| PermitRootLogin forced-commands-only | 부분 양호 | 지정 명령어만 실행, 완전 차단 권장 |
| Telnet 서비스 사용 중 | 취약 | 암호화되지 않은 프로토콜로 root 접속 허용 |
| SSH 서비스 미사용 | 양호 | 원격 접속 경로 자체가 없음 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| Linux/Unix | SSH PermitRootLogin | no | 완전 차단 |
| Solaris | /etc/default/login CONSOLE | /dev/console | 콘솔만 허용 |
| AIX | /etc/security/user rlogin | false | root 원격 접속 차단 |
| HP-UX | /etc/securetty | tty만 포함 | pts 항목 제거 |

### 2. 점검 방법

#### Linux/Unix SSH 점검

SSH는 원격 접속의 표준 프로토콜로, root 계정의 직접 접속을 차단해야 무차별 대입 공격으로부터 시스템을 보호할 수 있습니다.

```bash
# SSH 설정 파일에서 root 접속 허용 여부 확인
cat /etc/ssh/sshd_config | grep -E "^PermitRootLogin"
```

**양호 출력 예시:**
```text
PermitRootLogin no
```

**취약 출력 예시:**
```text
PermitRootLogin yes
```

#### Telnet 점검 (Linux)

Telnet은 암호화되지 않은 프로토콜로, 원천적으로 사용을 권장하지 않습니다.

```bash
# Telnet 서비스 실행 여부 확인
systemctl status telnet.socket
netstat -tlnp | grep :23

# securetty 파일 확인
cat /etc/securetty
```

**양호 출력 예시 (pts 항목 없음):**
```text
console
tty1
tty2
# pts/0
# pts/1
```

**취약 출력 예시:**
```text
console
tty1
pts/0
pts/1
```

### 3. 조치 방법

#### Linux SSH 설정

1. **SSH 설정 파일 백업**
   ```bash
   cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak.$(date +%Y%m%d)
   ```

2. **PermitRootLogin 설정 변경**
   ```bash
   vi /etc/ssh/sshd_config
   ```

   변경 전: `PermitRootLogin yes`
   변경 후: `PermitRootLogin no`

3. **설정 문법 확인 및 서비스 재시작**
   ```bash
   sshd -t
   systemctl restart sshd
   ```

#### Linux Telnet 설정

1. **Telnet 서비스 비활성화 (권장)**
   ```bash
   systemctl stop telnet.socket
   systemctl disable telnet.socket
   ```

2. **사용 시 securetty 파일 수정**
   ```bash
   vi /etc/securetty
   # pts/0, pts/1 등 주석 처리 또는 삭제
   ```

#### Solaris SSH 설정

1. **SSH 설정 파일 수정**
   ```bash
   vi /etc/ssh/sshd_config
   PermitRootLogin no
   ```

2. **서비스 재시작**
   ```bash
   svcadm restart svc:/network/ssh:default
   ```

#### AIX 설정

1. **SSH 설정 수정**
   ```bash
   vi /etc/ssh/sshd_config
   PermitRootLogin no
   ```

2. **Telnet 차단 설정**
   ```bash
   vi /etc/security/user
   root:
           rlogin = false
   ```

3. **서비스 재시작**
   ```bash
   stopsrc -s sshd
   startsrc -s sshd
   ```

#### HP-UX 설정

1. **SSH 설정 수정**
   ```bash
   vi /opt/ssh/etc/sshd_config
   PermitRootLogin no
   ```

2. **securetty 파일 확인**
   ```bash
   vi /etc/securetty
   # 콘솔(tty)만 허용, pts 항목 제거
   ```

3. **서비스 재시작**
   ```bash
   /sbin/init.d/sshd stop
   /sbin/init.d/sshd start
   ```

### 4. 참고 자료

- OpenSSH 공식 매뉴얼: https://www.openssh.com/manual.html
- CIS Benchmarks (Ubuntu 20.04): https://www.cisecurity.org/benchmark/ubuntu_linux_20_04
- NIST SP 800-53 Rev 5: AC-6 (Least Privilege)
- KISA 주요정보통신기반시설 취약점 진단 가이드

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.