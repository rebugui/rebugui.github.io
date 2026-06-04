---
title: "[2026 주요정보통신기반시설] U-28 접속 IP 및 포트 제한"
slug: "2026-주정통/U-28"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "허용할 호스트에 대한 접속 IP 주소 제한 및 포트 제한 설정 여부 점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-28 접속 IP 및 포트 제한

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-28 |
| **점검내용** | 허용할 호스트에 대한 접속 IP 주소 제한 및 포트 제한 설정 여부 점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX 등 |
| **양호기준** | 접속을 허용할 특정 호스트에 대한 IP 주소 및 포트 제한을 설정한 경우 |
| **취약기준** | 접속을 허용할 특정 호스트에 대한 IP 주소 및 포트 제한을 설정하지 않은 경우 |
| **조치방법** | OS에 기본으로 제공하는 방화벽 애플리케이션이나 TCP Wrapper를 사용하여 접근 허용 IP 등록 설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: TCP Wrapper(`/etc/hosts.allow`, `/etc/hosts.deny`)를 사용하거나 IPtables/Firewalld 등 호스트 방화벽을 사용하여 접근 통제를 설정한 경우
- **취약**: 위와 같은 접근 통제 설정이 적용되어 있지 않은 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| /etc/hosts.allow에 ALL:ALL | 취약 | 모든 접속 허용 - 제한 없음 |
| /etc/hosts.deny에만 ALL:ALL | 주의 | 기본 차단이나 hosts.allow에 허용 규칙 필요 |
| /etc/hosts.allow가 비어있음 | 취약 | 허용 규칙이 없으면 모두 차단됨 |
| sshd:192.168.1.100만 있음 | 양호 | 특정 IP만 SSH 허용 |
| 방화벽에 DROP 정책만 있음 | 취약 | 모든 트래픽 차단 - 서비스 불가 |
| INPUT ACCEPT만 있는 iptables | 취약 | 모든 접속 허용 |
| firewalld public zone | 취약 (기본값) | 모든 IP에서 SSH 등 허용 |
| rich rule로 IP 제한 | 양호 | 특정 IP만 접속 허용 |

#### 권장 설정값

| 도구 | 설정 파일/명령 | 권장 설정 | 비고 |
|------------|---------------|------|------|
| TCP Wrapper | /etc/hosts.deny | ALL: ALL | 기본 모두 차단 |
| TCP Wrapper | /etc/hosts.allow | sshd: 192.168.1.100 | 특정 IP만 허용 |
| iptables | INPUT 체인 | 기본 정책 DROP, 필요한 서비스만 ACCEPT | Whitelist 방식 |
| firewalld | zone | 특정 IP에만 서비스 허용 (rich rule) | RHEL 7+ |
| SSH | Port 변경 | 22번 포트가 아닌 다른 포트 사용 | 포트 스캔 방지 |

### 2. 점검 방법

#### TCP Wrapper 설정 확인 (Linux, Solaris, AIX, HP-UX)

```bash
# /etc/hosts.deny 확인
cat /etc/hosts.deny
# 내용에 'ALL:ALL'이 있어야 함

# /etc/hosts.allow 확인
cat /etc/hosts.allow
# 허용할 서비스와 IP가 명시되어 있는지 확인
```

**양호 출력 예시 (hosts.deny):**
```text
ALL: ALL
```

**양호 출력 예시 (hosts.allow):**
```text
sshd: 192.168.1.100 192.168.1.0/24
vsftpd: 192.168.1.50
```

**취약 출력 예시 (hosts.allow):**
```text
ALL: ALL
# 또는 비어있음
```

#### IPtables 설정 확인 (Linux)

```bash
iptables -L -n -v
```

**양호 출력 예시:**
```text
Chain INPUT (policy DROP 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination
  100  8000 ACCEPT     tcp  --  *      *       192.168.1.100        0.0.0.0/0           tcp dpt:22
   50  4000 ACCEPT     tcp  --  *      *       0.0.0.0/0            0.0.0.0/0           tcp dpt:80
```

**취약 출력 예시:**
```text
Chain INPUT (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination
```
(기본 정책이 ACCEPT이고 제한 규칙 없음)

#### Firewalld 설정 확인 (RHEL 7+)

```bash
firewall-cmd --list-all
```

**양호 출력 예시:**
```text
public (active)
  rich rules:
    rule family="ipv4" source address="192.168.1.100" service name="ssh" accept
```

**취약 출력 예시:**
```text
public (active)
  services: ssh dhcpv6-client
# 모든 IP에서 SSH 허용됨
```

### 3. 조치 방법

#### TCP Wrapper 설정 (Linux, Solaris, AIX, HP-UX)

1. **`/etc/hosts.deny` (모두 차단)**
   ```bash
   vi /etc/hosts.deny

   ALL: ALL
   ```

2. **`/etc/hosts.allow` (필요한 IP 허용)**
   ```bash
   vi /etc/hosts.allow

   # SSH는 관리자 IP(192.168.1.100)만 허용
   sshd: 192.168.1.100

   # 또는 대역 허용
   sshd: 192.168.1.

   # 여러 서비스 허용
   in.ftpd, in.telnetd: 192.168.1.50
   ```

#### IPtables 설정 (Linux)

```bash
# 1. 기본 정책을 DROP으로 설정
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# 2. 관리자 IP만 SSH 허용
iptables -A INPUT -s 192.168.1.100 -p tcp --dport 22 -j ACCEPT

# 3. Web 서비스 허용 (모든 IP에서)
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# 4. established 연결 허용
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# 5. loopback 허용
iptables -A INPUT -i lo -j ACCEPT

# 6. 설정 저장
service iptables save
# 또는
iptables-save > /etc/sysconfig/iptables
```

#### Firewalld 설정 (RHEL 7+)

```bash
# 1. 기존 ssh 서비스 제거
firewall-cmd --permanent --remove-service=ssh

# 2. Rich Rule 추가 (특정 IP만 SSH 허용)
firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="192.168.1.100" service name="ssh" accept'

# 3. 설정 적용
firewall-cmd --reload

# 4. 확인
firewall-cmd --list-all
```

### 4. 참고 자료

- **CIS Benchmarks**: 4.2.1, 4.2.2 Configure iptables/firewall
- **NIST 800-53**: SC-7 (Network Protection), SC-8 (Transmission Confidentiality)
- **TCP Wrapper**: Wietse Venema가 개발한 호스트 기반 ACL 시스템
- **man page**: `man hosts.allow`, `man iptables`, `man firewalld`

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.