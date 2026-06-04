---
title: "[2026 주요정보통신기반시설] HV-09 NTP 및 시각 동기화 설정"
slug: "2026-주정통/HV-09"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "NTP설정을통한시간동기화여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Virtualization
---

# HV-09 NTP 및 시각 동기화 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | HV-09 |
| **점검내용** | NTP설정을통한시간동기화여부점검 |
| **점검대상** | VMware ESXi, vCenter, XenServer, KVM, Nutanix 등 |
| **판단기준** | 양호: NTP서버와시간동기화설정을적용한경우 |
| **판단기준** | 취약: NTP서버와시간동기화설정을적용하지않은경우 |
| **조치방법** | NTP설정및시각동기화설정 |

---
## 상세 설명

### 1. 항목 개요

NTP(Network Time Protocol)는 네트워크를 통해 컴퓨터 시계를 동기화하는 프로토콜입니다. 가상화 장비의 정확한 시간 동기화는 보안 로그 분석, 장애 추적, 감사 추적의 핵심 요소입니다.

가상화 환경에서는 여러 대의 가상 머신이 물리적 호스트에서 실행되며, 각 시스템의 시간이 동기화되지 않으면 다음과 같은 문제가 발생할 수 있습니다.

### 2. 왜 이 항목이 필요한가요?

**시간 동기화의 중요성:**

1. **보안 로그 분석**
   - 공격 시간 파악 불가
   - 다중 시스템 공격 추적 어려움
   - 법적 증거로서의 로그 신뢰성 저하

2. **장애 조사 및 복구**
   - 장애 발생 시간 불일치
   - 선후 관계 파악 불가
   - 원인 규명 지연

3. **보안 정책 강제**
   - 인증서 유효성 검사 실패
   - Kerberos 인증 오류
   - 계정 잠금 정책 오작동

4. **감사 규정 준수**
   - 감사 추적 불가
   - 규정 준수 위반

**위험 시나리오:**

```
공격자가 웹 서버(ESXi #1) 공격 → 14:05:10
→ 데이터베이스 서버(ESXi #2) 접속 → 14:05:30 (실제 14:10:30)
→ 백업 서버(ESXi #3) 데이터 탈취 → 14:06:00 (실제 14:15:00)

시스템별 시간이 다르면 공격 경로 추적 불가!
```

### 3. 점검 대상

- VMware ESXi
- VMware vCenter
- Citrix XenServer
- KVM (RHEL, CentOS, Ubuntu 등)
- Nutanix AHV

### 4. 판단 기준

- **양호**: NTP 서버와 시간 동기화 설정을 적용한 경우
- **취약**: NTP 서버와 시간 동기화 설정을 적용하지 않은 경우

### 5. 점검 방법

#### VMware ESXi

1. Web 콘솔 접속
   ```
   https://<VMware ESXi IP>
   ```

2. **호스트** > **관리** > **시스템** > **시간 및 날짜**로 이동

3. **NTP 서비스** 상태 확인

4. NTP 서버 목록 확인

5. CLI 확인:
   ```bash
   esxcli system time get
   esxcli network firewall ruleset list | grep ntp
   ```

#### VMware vCenter

1. vCenter Server 관리 페이지 접속
   ```
   https://<주소>:5480/
   ```

2. **시간** > **시간 동기화** 메뉴

3. NTP 설정 여부 확인

#### KVM

1. chrony 서비스 상태 확인
   ```bash
   systemctl status chronyd
   ```

2. NTP 동기화 상태 확인
   ```bash
   chronyc tracking
   chronyc sources
   ```

3. ntpd 사용 시
   ```bash
   systemctl status ntpd
   ntpq -p
   ```

#### XenServer

1. XenCenter 접속

2. **Network and Management Interface** > **Network Time (NTP)** 확인

3. NTP 서버 목록 확인

#### Nutanix

1. 웹 콘솔 접속
   ```
   https://<Nutanix 웹 콘솔 IP>:9440
   ```

2. **Settings** > **NTP Servers** 선택

3. NTP 서버 설정 확인

4. CLI 확인:
   ```bash
   ncli cluster get-ntp-servers
   ```

### 6. 조치 방법

#### VMware ESXi

**1) 웹 콘솔 설정**

1. **호스트** > **관리** > **시스템** > **시간 및 날짜**로 이동

2. **NTP 서비스 사용** 체크

3. **NTP 서버 편집** 클릭

4. NTP 서버 추가:
   ```
   ntp.kisa.or.kr
   time.bora.net
   time.google.com
   ```

5. 저장 후 서비스 시작

**2) CLI 설정**

```bash
# NTP 서비스 시작
esxcli network firewall ruleset set --ruleset-id ntpClient --enabled true
esxcli network firewall ruleset set --ruleset-id ntpClient --allowed-all true

# NTP 서버 추가
esxcli system ntp set --server ntp.kisa.or.kr
esxcli system ntp set --server time.bora.net

# NTP 서비스 시작
esxcli system ntp set --enabled true
```

#### VMware vCenter

1. vCenter Server 관리 페이지 접속
   ```
   https://<주소>:5480/
   ```

2. **시간** > **시간 동기화** 선택

3. **NTP 서버 사용** 체크

4. NTP 서버 추가:
   ```
   ntp.kisa.or.kr
   time.bora.net
   ```

5. **저장** 후 **서비스 재시작**

#### KVM

**1) chrony 설정 (RHEL 7/CentOS 7 이상 권장)**

1. chrony 설치
   ```bash
   yum install chrony
   # 또는
   apt install chrony
   ```

2. `/etc/chrony.conf` 파일 수정
   ```bash
   vi /etc/chrony.conf
   ```

3. NTP 서버 추가/수정:
   ```
   server ntp.kisa.or.kr iburst
   server time.bora.net iburst
   server time.google.com iburst

   # 로그 설정
   logdir /var/log/chrony
   ```

4. 서비스 시작 및 부팅 시 자동 시작
   ```bash
   systemctl start chronyd
   systemctl enable chronyd
   ```

5. 동기화 상태 확인
   ```bash
   chronyc tracking
   chronyc sources
   ```

**2) ntpd 설정 (구버전)**

1. ntpd 설치
   ```bash
   yum install ntp
   ```

2. `/etc/ntp.conf` 파일 수정
   ```bash
   vi /etc/ntp.conf
   ```

3. NTP 서버 추가/수정:
   ```
   server ntp.kisa.or.kr iburst
   server time.bora.net iburst
   ```

4. 서비스 시작
   ```bash
   systemctl start ntpd
   systemctl enable ntpd
   ```

#### XenServer

1. XenCenter 접속

2. **Network and Management Interface** > **Network Time (NTP)**

3. **Provide NTP Servers Manually** 선택

4. NTP 서버 입력:
   ```
   ntp.kisa.or.kr
   time.bora.net
   ```

5. **OK** 클릭

#### Nutanix

**1) 웹 콘솔 설정**

1. 웹 콘솔 접속
   ```
   https://<Nutanix 웹 콘솔 IP>:9440
   ```

2. **Settings** > **NTP Servers** 선택

3. NTP 서버 입력:
   ```
   ntp.kisa.or.kr
   time.bora.net
   time.google.com
   ```

4. **Add** 클릭

**2) 타임존 설정**

1. Controller VM 접속

2. 타임존 설정
   ```bash
   ncli cluster set-timezone timezone="Asia/Seoul"
   ```

3. 모든 호스트 타임존 변경
   ```bash
   hostssh "date; mv /etc/localtime /etc/localtime.bak; ln -s /usr/share/zoneinfo/Asia/Seoul /etc/localtime"
   ```

4. 시간 확인
   ```bash
   date
   ```

### 7. 권장 NTP 서버

| NTP 서버 | 운영기관 | 설명 |
|---------|----------|------|
| ntp.kisa.or.kr | KISA | 한국인터넷진흥원 운영 |
| time.bora.net | 한국과학기술원 KAIST | 한국 공용 NTP |
| time.google.com | Google | 글로벌 NTP |
| pool.ntp.org | NTP Pool Project | 전 세계 NTP 풀 |
| kr.pool.ntp.org | NTP Pool Project | 한국 NTP 풀 |

### 8. NTP 설정 모범 사례

**1) NTP 서버 선택**
- 내부 NTP 서버 우선 (보안 권장)
- 인터넷 NTP 서버는 3개 이상 설정
- 지리적으로 가까운 서버 선택
- 신뢰할 수 있는 공인 NTP 서버 사용

**2) 내부 NTP 서버 구성**
```
[가상화 장비]
    ↓
[내부 NTP 서버]
    ↓
[공인 NTP 서버]
```

**3) 타임존 설정**
- 한국: `Asia/Seoul` (UTC+9)
- 모든 호스트 동일 타임존 설정
- 가상 머신도 동일 타임존 권장

**4) NTP 보안**
- NTP 인증 설정 (NTP Authentication)
- NTP 접속 제한 (방화벽)
- NTP 서버 IP 화이트리스트

### 9. NTP 동기화 상태 확인

#### VMware ESXi

```bash
# NTP 서비스 상태
esxcli system ntp get

# NTP 동기화 상태
esxcli system ntp test

# 시간 확인
esxcli system time get
```

#### KVM

```bash
# chrony 동기화 상태
chronyc tracking

# NTP 서버 목록
chronyc sources

# 동기화 상세 정보
chronyc sourcestats
```

#### Nutanix

```bash
# NTP 서버 목록
ncli cluster get-ntp-servers

# 시간 확인
date
```

### 10. 시간 동기화 문제 해결

**문제 1: 시간이 크게 차이남**

```bash
# 수동 시간 설정 (주의: 가상 머신 중지 권장)
date -s "2025-01-20 14:30:00"

# VMware ESXi
esxcli system time set -y 2025 -m 01 -d 20 -H 14 -M 30 -S 00
```

**문제 2: NTP 동기화 안됨**

1. 방화벽 확인
   ```bash
   # UDP 123 포트 확인
   netstat -an | grep 123
   ```

2. NTP 서비스 재시작
   ```bash
   systemctl restart chronyd
   ```

3. NTP 서버 도달성 확인
   ```bash
   ping ntp.kisa.or.kr
   telnet ntp.kisa.or.kr 123
   ```

### 11. 주의사항

- **NTP 서비스는 UDP 123 포트** 사용: 방화벽에서 허용 필요
- **대역폭**: NTP 트래픽은 매우 적음 (초당 수 바이트)
- **가상 머신 시간**: 호스트 시간 동기화 권장
- **타임존 일치**: 모든 시스템 동일 타임존 설정
- **정기적 확인**: 월 1회 이상 시간 동기화 상태 확인

### 12. 가상화 환경 특별 고려사항

**VMware Tools/가상화 에이전트**
- 가상 머신 시간 동기화 기능 제공
- 호스트 시간 동기화와 충돌 가능
- 둘 중 하나만 사용 권장

**시간 드리프트(Time Drift)**
- 가상 머신은 시간 드리프트 발생 가능
- 정기적 NTP 동기화로 해결

## 요약

모든 가상화 장비는 **NTP 서버와 시간 동기화**를 필수로 적용해야 합니다. 권장 NTP 서버는 **`ntp.kisa.or.kr`**, **`time.bora.net`**이며, 가능하면 **내부 NTP 서버**를 구축하여 사용하는 것이 보안상 좋습니다. 정확한 시간 동기화는 보안 로그 분석과 침해 사고 조사의 필수 조건입니다.
