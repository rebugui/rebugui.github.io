---
title: "[2026 주요정보통신기반시설] U-44 tftp, talk 서비스 비활성화"
slug: "2026-주정통/U-44"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "tftp, talk, ntalk서비스의활성화여부점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-44 tftp, talk 서비스 비활성화

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-44 |
| **점검내용** | tftp, talk, ntalk서비스의활성화여부점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX등 |
| **양호기준** | tftp, talk, ntalk서비스가비활성화된경우 |
| **취약기준** | tftp, talk, ntalk서비스가활성화된경우 |
| **조치방법** | 불필요한tftp, talk, ntalk서비스비활성화설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: tftp, talk, ntalk 서비스가 비활성화된 경우
- **취약**: tftp, talk, ntalk 서비스 중 하나라도 활성화된 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| PXE 부팅에 TFTP 사용 | 주의 | 방화벽 접근 제어 필요 |
| TFTP 활성화 (인증 없음) | 취약 | 파일 전송 악용 가능 |
| talk 서비스 활성화 | 취약 | 사용자 정보 노출 |
| ntalk 서비스 활성화 | 취약 | 새로운 talk 프로토콜 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| Linux (xinetd) | tftp | disable = yes | 파일 전송 |
| Linux (xinetd) | talk | disable = yes | 실시간 메시징 |
| Linux (xinetd) | ntalk | disable = yes | 새 talk 프로토콜 |
| inetd | tftp | #주석 처리 | /etc/inetd.conf |

### 2. 점검 방법

#### Linux 점검

TFTP는 인증 없이 파일 전송이 가능하므로 보안에 매우 취약합니다. Talk 서비스도 사용자 정보를 노출시킵니다.

```bash
# 1. xinetd 기반 서비스 확인
echo "=== 1. xinetd Services ==="
for svc in tftp talk ntalk; do
    if [ -f "/etc/xinetd.d/$svc" ]; then
        echo "--- $svc ---"
        grep -E "disable\s*=" /etc/xinetd.d/$svc
    fi
done

# 2. inetd 기반 서비스 확인
if [ -f /etc/inetd.conf ]; then
    echo "=== 2. /etc/inetd.conf ==="
    grep -E "^(tftp|talk|ntalk)" /etc/inetd.conf
fi

# 3. 포트 listening 확인
echo "=== 3. Listening Ports ==="
netstat -tuln | grep -E ":(69|517|518)"
# 69: tftp, 517/518: talk/ntalk
```

**양호 출력 예시:**
```text
=== 1. xinetd Services ===
--- tftp ---
disable = yes
--- talk ---
disable = yes
=== 2. /etc/inetd.conf ===
#tftp  dgram   udp     wait    root  /usr/sbin/in.tftpd in.tftpd
```

**취약 출력 예시:**
```text
=== 1. xinetd Services ===
--- tftp ---
disable = no
=== 3. Listening Ports ===
udp        0      0 0.0.0.0:69              0.0.0.0:*
```

### 3. 조치 방법

#### Linux (xinetd) 설정

1. **서비스 비활성화**
   ```bash
   # TFTP, Talk 비활성화
   for svc in tftp talk ntalk; do
       if [ -f "/etc/xinetd.d/$svc" ]; then
           sed -i.bak 's/disable = no/disable = yes/' "/etc/xinetd.d/$svc"
           echo "Disabled $svc"
       fi
   done

   # xinetd 재시작
   systemctl restart xinetd
   ```

2. **inetd 주석 처리**
   ```bash
   sed -i 's/^\(tftp\|talk\|ntalk\)/#\1/' /etc/inetd.conf
   kill -HUP $(cat /var/run/inetd.pid 2>/dev/null)
   ```

3. **확인**
   ```bash
   netstat -tuln | grep -E ":(69|517|518)"
   # 결과가 없어야 함
   ```

### 4. 참고 자료

- CIS Benchmark for Linux: 불필요한 서비스 비활성화 권고
- NIST SP 800-53: CM-7 (시스템 최소화)
- TFTP RFC 1350: 프로토콜 사양
- man pages: tftp(1), in.tftpd(8), talk(1)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.