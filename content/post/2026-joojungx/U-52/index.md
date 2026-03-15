---
title: "[2026 주요정보통신기반시설] U-52 Telnet 서비스 비활성화"
slug: "2026-주정통/U-52"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "원격접속시Telnet프로토콜사용여부점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-52 Telnet 서비스 비활성화

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-52 |
| **점검내용** | 원격접속시Telnet프로토콜사용여부점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX등 |
| **양호기준** | 원격접속시Telnet프로토콜을비활성화하고있는경우 |
| **취약기준** | 원격접속시Telnet프로토콜을사용하는경우 |
| **조치방법** | Telnet,FTP등안전하지않은서비스사용을중지하고SSH설치및사용하도록설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: Telnet 서비스가 비활성화되고 SSH만 사용하는 경우
- **취약**: Telnet 서비스가 활성화된 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| Telnet 활성화 (평문) | 취약 | 암호 노출 위험 |
| SSH만 사용 | 양호 | 암호화 대체 |
| 포트 23 listening | 취약 | Telnet 서비스 실행 중 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| Linux | telnet | disabled (systemctl) | 비활성화 |
| Linux | sshd | enabled (systemctl) | SSH 사용 |
| inetd/xinetd | telnet | disable = yes 또는 주석 | 설정 파일 |

### 2. 점검 방법

#### Linux 점검

Telnet은 평문으로 통신하므로 반드시 SSH로 대체해야 합니다.

```bash
# 1. Telnet 서비스 상태 확인
echo "=== 1. Telnet Service ==="
systemctl is-active telnet.socket 2>/dev/null
systemctl is-enabled telnet.socket 2>/dev/null

# 2. 포트 listening 확인
echo "=== 2. Port 23 ==="
netstat -tuln | grep :23

# 3. xinetd 설정 확인
echo "=== 3. xinetd Telnet ==="
grep -E "disable\s*=" /etc/xinetd.d/telnet 2>/dev/null
```

**양호 출력 예시:**
```text
=== 1. Telnet Service ===
telnet.socket: inactive (dead)
telnet.socket: disabled
=== 2: Port 23 ===
(결과 없음)
```

**취약 출력 예시:**
```text
=== 1. Telnet Service ===
telnet.socket: active (running)
=== 2. Port 23 ===
tcp        0      0 0.0.0.0:23              0.0.0.0:*                   LISTEN
```

### 3. 조치 방법

#### Linux (systemd) 설정

1. **Telnet 서비스 중지**
   ```bash
   # 서비스 중지
   systemctl stop telnet.socket
   systemctl disable telnet.socket

   # 패키지 삭제
   yum remove telnet-server
   # 또는
   apt remove telnetd
   ```

2. **SSH 설치 (대안)**
   ```bash
   yum install openssh-server
   systemctl enable sshd
   systemctl start sshd
   ```

#### inetd/xinetd 설정

1. **주석 처리 또는 비활성화**
   ```bash
   # /etc/inetd.conf
   sed -i 's/^telnet/#telnet/' /etc/inetd.conf
   kill -HUP $(cat /var/run/inetd.pid)

   # 또는 xinetd
   sed -i 's/disable = no/disable = yes/' /etc/xinetd.d/telnet
   systemctl restart xinetd
   ```

### 4. 참고 자료

- CIS Benchmark for Linux: Telnet 비활성화 권고
- NIST SP 800-53: SC-8 (전송 기밀성)
- SSH Protocol: RFC 4254
- man pages: telnet(1), sshd(8)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.