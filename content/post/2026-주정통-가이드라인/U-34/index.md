---
title: "[2026 주요정보통신기반시설] U-34 Finger 서비스 비활성화"
slug: "2026-주정통/U-34"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "Finger 서비스 비활성화 여부 점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
draft: true
---

# U-34 Finger 서비스 비활성화

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-34 |
| **점검내용** | Finger 서비스 비활성화 여부 점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX 등 |
| **양호기준** | Finger 서비스가 비활성화된 경우 |
| **취약기준** | Finger 서비스가 활성화된 경우 |
| **조치방법** | Finger 서비스 비활성화 설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: Finger 서비스가 비활성화된 경우 (프로세스 미실행, 포트 미리스닝)
- **취약**: Finger 서비스가 활성화된 경우 (프로세스 실행 중, 포트 79 listening)

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| /etc/xinetd.d/finger에 disable = yes | 양호 | xinetd에서 비활성화됨 |
| /etc/inetd.conf에서 주석 처리(#) | 양호 | inetd에서 비활성화됨 |
| finger-server 패키지 미설치 | 양호 (권장) | 패키지가 없으면 안전함 |
| TCP 79 포트 listening | 취약 | Finger 서비스 활성화됨 |
| finger 프로세스 실행 중 | 취약 | Finger 데몬 활성화됨 |
| cfingerd, efingerd 대체 데몬 | 점검 필요 | 대체 구현체도 비활성화 권장 |

#### 권장 설정값

| 항목 | 권장 설정 | 비고 |
|------------|---------------|------|
| finger 서비스 상태 | 비활성화 (disabled) | |
| finger-server 패키지 | 삭제 권장 | 불필요한 서비스 제거 |
| /etc/xinetd.d/finger | disable = yes | RHEL/CentOS |
| /etc/inetd.conf | #finger ... (주석) | Solaris/HP-UX/AIX |
| TCP 포트 79 | listening하지 않음 | |

### 2. 점검 방법

#### Linux, Solaris, AIX, HP-UX 점검

```bash
# 1. Finger 프로세스 확인
ps aux | grep -i finger | grep -v grep

# 2. Finger 포트 (79) 확인
netstat -tuln 2>/dev/null | grep :79
# 또는
ss -tuln 2>/dev/null | grep :79

# 3. xinetd 설정 확인 (Linux)
if [ -f /etc/xinetd.d/finger ]; then
    cat /etc/xinetd.d/finger | grep disable
fi

# 4. inetd.conf 확인 (Solaris, HP-UX, AIX)
if [ -f /etc/inetd.conf ]; then
    grep -E "^finger" /etc/inetd.conf | grep -v "^#"
fi

# 5. 패키지 확인 (Linux)
rpm -qa | grep finger
dpkg -l | grep finger
```

**양호 출력 예시 (xinetd):**
```text
disable = yes
```

**양호 출력 예시 (포트):**
```text
(출력 없음 - TCP 79 포트가 열려있지 않음)
```

**취약 출력 예시 (xinetd):**
```text
disable = no
```

**취약 출력 예시 (inetd.conf):**
```text
finger stream tcp nowait nobody /usr/sbin/in.fingerd in.fingerd
```

### 3. 조치 방법

#### 1. xinetd 사용 시 (Linux)

```bash
# Finger 서비스 비활성화
cat > /etc/xinetd.d/finger << 'EOF'
service finger
{
        disable = yes
        socket_type = stream
        wait = no
        user = nobody
        server = /usr/sbin/in.fingerd
        log_on_success += HOST DURATION
        log_on_failure += HOST
}
EOF

# xinetd 재시작
systemctl restart xinetd
# 또는
service xinetd restart
```

#### 2. inetd 사용 시 (Solaris, HP-UX, AIX)

```bash
# /etc/inetd.conf에서 finger 라인 주석 처리
sed -i 's/^finger/#finger/' /etc/inetd.conf

# inetd 재시작
kill -HUP $(cat /var/run/inetd.pid) 2>/dev/null
# 또는
pkill -HUP inetd
```

#### 3. 패키지 완전 삭제 (권장)

```bash
# RHEL/CentOS
yum remove finger-server
# 또는
rpm -e finger-server

# Debian/Ubuntu
apt-get remove finger
apt-get purge finger

# Solaris
pkgrm SUNWfcfu

# AIX
removep finger
```

### 4. 참고 자료

- **CIS Controls**: CC9.2 불필요한 서비스 비활성화
- **NIST 800-53**: CM-7 (최소화된 시스템 구성 유지)
- **ISO 27001:2013**: A.12.1.2 (시스템 변경 관리)
- **K-ISMS**: 2.5.1 (불필요한 서비스 제거)
- **RFC 1288**: Finger User Information Protocol

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.