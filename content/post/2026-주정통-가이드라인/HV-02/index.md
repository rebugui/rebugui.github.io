---
title: "[2026 주요정보통신기반시설] HV-02 가상화장비 > 1. 계정관리"
slug: "2026-주정통/HV-02"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "허용할호스트에대한접속IP제한설정여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Virtualization
draft: true
---

# 가상화장비 > 1. 계정관리

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | HV-02 |
| **점검내용** | 허용할호스트에대한접속IP제한설정여부점검 |
| **점검대상** | VMware ESXi, vCenter, XenServer, KVM, Nutanix 등 |
| **판단기준** | 양호: 허용된IP에서만관리콘솔및원격접속이가능하도록제한된경우 |
| **판단기준** | 취약: 허용된IP에서만관리콘솔및원격접속이가능하도록제한되지않은경우 |
| **조치방법** | 호스트에서제공하는방화벽애플리케이션을이용하여서비스접속허용IP등록설정 |

---
## 상세 설명

### 개요

**가상화장비 외부접속차단**은 가상화 장비의 관리 콘솔 및 원격 접속 서비스에 대해 특정 IP 주소에서만 접근을 허용하도록 제한하는 보안 조치입니다. 이는 네트워크 수준에서 접근 통제를 수행하여 비인가자의 무단 접근을 원천적으로 차단합니다.

### 필요성

가상화 장비는 인프라의 핵심 시스템으로, 외부에서의 무단 접근을 방지하는 것이 매우 중요합니다. 접속 IP 제한이 필요한 이유는 다음과 같습니다:

1. **무차별 대입 공격 방지**: 전 세계 어디에서든 SSH나 웹 콘솔에 접근할 수 있으면 무차별 대입 공격에 노출
2. **공격 표면 감소**: 허용된 IP에서만 접근 가능하도록 하여 잠재적 공격 경로 최소화
3. **관리 효율성**: 특정 관리자 PC나 관리 서버에서만 접근을 허용하여 관리 체계화
4. **보안 사고 예방**: 탈취된 계정 정보가 있더라도 허용되지 않은 IP에서는 접속 불가

### 주요 개념

- **TCP Wrapper**: 호스트 기반의 네트워킹 ACL(Access Control List) 시스템
- **IPTables**: 리눅스 커널 방화벽이 제공하는 테이블들과 그것을 저장하는 체인, 규칙들을 구성할 수 있게 해주는 서비스
- **FirewallD**: Linux 운영체제를 위한 방화벽 관리 도구

### 점검 방법

#### VMware ESXi, vCenter

**웹 콘솔 접속 IP 제한 설정 확인**

1. Web 콘솔 페이지 접속 (`https://<VMware ESXi IP>`)
2. 네트워킹 > 방화벽 규칙으로 이동
3. [ESXi] SSH 서버의 '허용된 IP 주소' 확인
4. [vSphere] 웹 클라이언트의 '허용된 IP 주소' 확인

```bash
# 확인할 항목
- SSH 서버 허용 IP: 특정 IP로 제한되어 있는지
- 웹 클라이언트 허용 IP: 특정 IP로 제한되어 있는지
```

#### XenServer, KVM

**IPTables를 통한 접근 통제 확인**

1. 호스트 접속
2. IPTables 정책 목록 확인

```bash
$ iptables -nL --line-number

Chain INPUT (policy ACCEPT)
num  target     prot opt source               destination
1    xapi_nbd_input_chain tcp  --  0.0.0.0/0            0.0.0.0/0            tcp dpt:10809
2    ACCEPT     47   --  0.0.0.0/0            0.0.0.0/0
3    RH-Firewall-1-INPUT all  --  0.0.0.0/0            0.0.0.0/0
...
```

3. SSH(22포트), 웹(80/443포트)에 대한 접속 IP 제한 규칙 확인

#### Nutanix

1. Controller VM에 접속하여 설정 확인

```bash
sudo cat /etc/hosts.allow | grep -v "^#"
```

2. 허용된 SSH IP 목록 확인

### 조치 방법

#### VMware ESXi, vCenter

1. IP 제한 설정이 적용되어 있지 않은 경우 vSphere Web Client(SSH 서버) > 설정 편집 > '다음 네트워크의 연결만 허용' 선택
2. 접속 허용 IP 입력 (예: `192.168.1.100, 192.168.1.0/24`)

```
허용 IP 예시:
- 단일 IP: 192.168.100.1
- IP 대역: 192.168.100.0/24
- 복수 IP: 192.168.100.1, 192.168.100.2
```

#### XenServer, KVM

**IPTables를 통한 SSH 접속 제한**

1. SSH 원격 접속을 허용된 IP로만 제한

```bash
# 허용 IP 추가
$ iptables -I RH-Firewall-1-INPUT 1 -p tcp -s <허용 IP> --dport 22 -j ACCEPT

# 그 외 IP 차단
$ iptables -I RH-Firewall-1-INPUT 2 -p tcp -s 0.0.0.0/0 --dport 22 -j DROP
```

2. 변경된 정책 저장 및 서비스 재시작

```bash
$ service iptables save
$ service iptables restart
```

**웹 서비스 접속 제한도 동일한 방식으로 적용**

```bash
# HTTPS(443) 접속 제한
$ iptables -I RH-Firewall-1-INPUT 1 -p tcp -s <허용 IP> --dport 443 -j ACCEPT
$ iptables -I RH-Firewall-1-INPUT 2 -p tcp -s 0.0.0.0/0 --dport 443 -j DROP
```

#### Nutanix

1. `hosts.allow` 파일 수정

```bash
sudo vi /srv/salt/security/CVM/network/hosts.allow
```

2. 다음 내용 추가

```bash
sshd: 192.168.100.1 : ALLOW
sshd: 192.168.100.0/255.255.255.0 : ALLOW
```

3. 변경 설정 적용

```bash
sudo salt-call state.sls security/CVM/networkCVM
```

### 주의사항

- **조치 시 영향**: IPTables의 기본정책을 DROP으로 변경하는 경우에는 애플리케이션간의 연결 현황을 확인 후 변경 필요
- **관리자 IP 변경**: 관리자 IP가 변경될 경우 반드시 방화벽 규칙 업데이트 필요
- **원격 접속 차단 위험**: 자신의 IP를 제외하면 시스템에 접속할 수 없으므로 주의

### 추가 팁

1. **VPN 활용**: VPN을 통해 관리 네트워크에 접속한 후 가상화 장비에 접속하는 구조 권장
2. **Jump Server**: 접속을 위한 점프 서버(Bastion Host)를 두고, 그 서버에서만 접속 허용
3. **정기적 검토**: 허용 IP 목록을 정기적으로 검토하여 불필요한 IP 제거
4. **문서화**: 허용 IP 목록과 관리자를 매핑하여 문서화
