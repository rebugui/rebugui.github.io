---
title: "[2026 주요정보통신기반시설] U-36 r계열 서비스 비활성화"
slug: "2026-주정통/U-36"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "r-command서비스비활성화여부점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-36 r계열 서비스 비활성화

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-36 |
| **점검내용** | r-command서비스비활성화여부점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX등 |
| **양호기준** | 불필요한r계열서비스가비활성화된경우 |
| **취약기준** | 불필요한r계열서비스가활성화된경우 |
| **조치방법** | 불필요한r계열서비스중지및비활성화설정 (NET Backup 등특별한용도로사용하지않는다면shell(514), login(513), exec(512)서비스중지) |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: rlogin (513/TCP), rsh (514/TCP), rexec (512/TCP) 서비스가 비활성화된 경우
- **취약**: rlogin, rsh, rexec 서비스 중 하나라도 활성화된 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| NET Backup 등 레거시 솔루션 사용 중 | 주의 | 실사용 여부 확인 후 비활성화 권장 |
| /etc/hosts.equiv 파일 존재 | 취약 | r계열 서비스 사용 중일 가능성 높음 |
| $HOME/.rhosts 파일 존재 | 취약 | 사용자별 r계열 서비스 사용 중 |
| inetd.conf에서 주석 처리됨 | 양호 | 서비스 비활성화 상태 |
| xinetd.d에서 disable = yes | 양호 | 서비스 비활성화 상태 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| Linux (xinetd) | rlogin | disable = yes | /etc/xinetd.d/rlogin |
| Linux (xinetd) | rsh | disable = yes | /etc/xinetd.d/rsh |
| Linux (xinetd) | rexec | disable = yes | /etc/xinetd.d/rexec |
| Solaris (inetd) | login | #주석 처리 | /etc/inetd.conf |
| Solaris (inetd) | shell | #주석 처리 | /etc/inetd.conf |
| Solaris (inetd) | exec | #주석 처리 | /etc/inetd.conf |

### 2. 점검 방법

#### Linux 점검

r계열 서비스(rlogin, rsh, rexec)는 SSH로 대체되었으며, 암호화되지 않은 평문 통신으로 인해 심각한 보안 취약점을 가집니다. 이 서비스들이 활성화되어 있는지 확인해야 합니다.

```bash
# xinetd 기반 서비스 확인
for svc in rlogin rsh rexec; do
    if [ -f "/etc/xinetd.d/$svc" ]; then
        echo "=== $svc ==="
        grep -E "disable\s*=" /etc/xinetd.d/$svc
    fi
done

# inetd 기반 서비스 확인 (Solaris, AIX, HP-UX)
if [ -f /etc/inetd.conf ]; then
    echo "=== /etc/inetd.conf ==="
    grep -E "^(login|shell|exec)" /etc/inetd.conf
fi

# .rhosts 파일 확인
echo "=== .rhosts files ==="
find /home -name ".rhosts" 2>/dev/null
ls -l /etc/hosts.equiv 2>/dev/null
```

**양호 출력 예시:**
```text
=== rlogin ===
disable = yes
=== rsh ===
disable = yes
=== rexec ===
disable = yes
=== /etc/inetd.conf ===
#login  stream  tcp6    nowait  root    /usr/sbin/in.rlogind in.rlogind
#shell   stream  tcp6    nowait  root    /usr/sbin/in.rshd   in.rshd
```

**취약 출력 예시:**
```text
=== rlogin ===
disable = no
=== /etc/inetd.conf ===
login  stream  tcp6    nowait  root    /usr/sbin/in.rlogind in.rlogind
shell  stream  tcp6    nowait  root    /usr/sbin/in.rshd   in.rshd
```

#### Solaris, AIX, HP-UX 점검

```bash
# inetd.conf 확인
cat /etc/inetd.conf | grep -E "^(login|shell|exec)"

# 또는 inetimp로 서비스 상태 확인 (Solaris)
inetimp -l

# 포트 listening 확인
netstat -an | grep -E ":(512|513|514)"
```

### 3. 조치 방법

#### Linux (xinetd) 설정

1. **xinetd 기반 서비스 비활성화**
   ```bash
   # r계열 서비스 비활성화
   for service in rlogin rsh rexec; do
       if [ -f "/etc/xinetd.d/$service" ]; then
           sed -i.bak 's/disable = no/disable = yes/' "/etc/xinetd.d/$service"
           echo "Disabled $service"
       fi
   done

   # 서비스 재시작
   systemctl restart xinetd
   ```

2. **설정 확인**
   ```bash
   for svc in rlogin rsh rexec; do
       grep "disable" /etc/xinetd.d/$svc
   done
   ```

#### Solaris, AIX, HP-UX (inetd) 설정

1. **inetd.conf 주석 처리**
   ```bash
   # 백업 생성
   cp /etc/inetd.conf /etc/inetd.conf.bak

   # r계열 서비스 주석 처리
   sed -i 's/^\(login\|shell\|exec\)/#\1/' /etc/inetd.conf

   # inetd 재시작
   kill -HUP $(cat /var/run/inetd.pid 2>/dev/null)
   # 또는
   pkill -HUP inetd
   ```

2. **서비스 중지 확인**
   ```bash
   netstat -an | grep -E ":(512|513|514)"
   # 결과가 없어야 함
   ```

#### 3. SSH로 마이그레이션

1. **SSH 키 기반 인증 설정**
   ```bash
   # 키 생성
   ssh-keygen -t rsa -b 4096

   # 키 복사
   ssh-copy-id user@target-server

   # 이후 비밀번호 없이 접속 가능
   ssh target-server "command"
   ```

2. **레거시 스크립트 수정**
   ```bash
   # 기존: rsh target-server command
   # 변경: ssh target-server "command"

   # 기존: rcp file target-server:/path
   # 변경: scp file target-server:/path
   ```

3. **서비스 재시작**
   ```bash
   # systemd
   systemctl restart sshd
   systemctl status sshd
   ```

### 4. 참고 자료

- CIS Benchmark for Linux: rlogin, rsh, rexec 비활성화 권고
- NIST SP 800-53: SC-8 (전송 기밀성)
- KISA 보안 가이드라인: r계열 서비스 보안 권고사항
- man pages: rsh(1), rlogin(1), rexec(3), ssh(1)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.