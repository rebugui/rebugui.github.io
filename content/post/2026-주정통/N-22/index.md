---
title: "[2026 주요정보통신기반시설] N-22 N-22: Spoofing 방지 필터링 적용"
slug: "2026-주정통/N-22"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "사설 네트워크, 루프백 등 특수 용도로 배정하여 라우팅이 불가능한 IP주소를 스푸핑 방지 필터링(Anti-Spoofing Filtering)을적용하여차단하는지점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Network
---

# N-22: Spoofing 방지 필터링 적용

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | N-22 |
| **점검내용** | 사설 네트워크, 루프백 등 특수 용도로 배정하여 라우팅이 불가능한 IP주소를 스푸핑 방지 필터링(Anti-Spoofing Filtering)을적용하여차단하는지점검 |
| **점검대상** | Cisco, Juniper등 |
| **판단기준** | 양호: 경계라우터또는보안장비에스푸핑방지필터링을적용한경우 |
| **판단기준** | 취약: 경계라우터또는보안장비에스푸핑방지필터링을적용하지않은경우 |
| **조치방법** | 경계라우터또는보안장비에서스푸핑방지필터링적용 |

---
## 상세 설명

### 개요

Spoofing 방지 필터링 적용 항목은 경계 라우터나 보안 장비에서 IP 스푸핑 방지 필터링(Anti-Spoofing Filtering)을 적용하는 항목입니다. 사설 네트워크, 루프백 등 특수 용도의 IP 주소를 소스로 하는 트래픽을 차단합니다.

### 필요성

**보안 위협**

IP 스푸핑 방지 필터링을 적용하지 않을 경우 다음과 같은 위협에 노출됩니다.

1. **IP 스푸핑 기반 DoS 공격**: 위조된 소스 IP 주소를 사용하는 DoS 공격이 가능합니다.

2. **서비스 거부**: 공격 트래픽이 네트워크 장비의 처리 용량을 초과하여 정상적인 서비스가 불가능해집니다.

3. **익명성 공격**: 공격자가 출처를 위조하여 추적을 어렵게 만듭니다.

**IP Spoofing이란?**

호스트의 원본 주소가 아닌 다른 소스 주소로 IP 데이터그램을 조작하는 기법입니다.

### 점검 방법

#### Cisco IOS 장비

**Step 1) IP spoofing 방지 설정 확인**

```
Router> enable
Router# show running-config
```

인터페이스에 적용된 ACL을 확인하여 스푸핑 방지 필터링이 있는지 확인합니다.

#### Juniper Junos 장비

**Step 1) Firewall Filters 설정 확인**

```
[edit]
user@host# show configuration
```

루프백 인터페이스나 외부 인터페이스에 스푸핑 방지 필터가 적용되어 있는지 확인합니다.

### 조치 방법

#### Cisco IOS

**Step 2) 스푸핑 방지 필터링 ACL 구성**

ACL 번호는 100~199 구간을 사용하여 Extended access-list를 사용합니다.

```
Router# configure terminal
```

**특수 용도 주소 차단 (RFC 6890 참조)**:

```
Router(config)# access-list <ACL 번호> deny ip 0.0.0.0 0.255.255.255 any
Router(config)# access-list <ACL 번호> deny ip 10.0.0.0 0.255.255.255 any
Router(config)# access-list <ACL 번호> deny ip 127.0.0.0 0.255.255.255 any
Router(config)# access-list <ACL 번호> deny ip 169.254.0.0 0.0.255.255 any
Router(config)# access-list <ACL 번호> deny ip 172.16.0.0 0.15.255.255 any
Router(config)# access-list <ACL 번호> deny ip 192.0.2.0 0.0.0.255 any
Router(config)# access-list <ACL 번호> deny ip 192.168.0.0 0.0.255.255 any
Router(config)# access-list <ACL 번호> deny ip 224.0.0.0 15.255.255.255 any
Router(config)# access-list <ACL 번호> permit ip any any
```

**특수 용도 주소 설명**:

| IP 대역 | 용도 | RFC |
|---------|------|-----|
| 0.0.0.0/8 | 자체 네트워크 (This host on this network) | RFC1122 |
| 10.0.0.0/8 | 사설 네트워크 (Private-Use) | RFC1918 |
| 127.0.0.0/8 | 루프백 (Loopback) | RFC1122 |
| 169.254.0.0/16 | 링크 로컬 (Link Local) | RFC3927 |
| 172.16.0.0/12 | 사설 네트워크 (Private-Use) | RFC1918 |
| 192.0.2.0/24 | 예제 등 문서에서 사용 (TEST-NET-1) | RFC5737 |
| 192.168.0.0/16 | 사설 네트워크 (Private-Use) | RFC1918 |
| 224.0.0.0/4 | 멀티캐스트 (Multicast) | RFC5771 |

**Step 3) 서비스 제공업체(SP)와 연결된 인터페이스에 ACL 적용**

```
Router(config)# interface serial <인터페이스>
Router(config-if)# ip access-group <ACL 번호> in
```

> **주의**: 인터넷과 연결된 외부 인터페이스의 `in` 방향(인그레스)에 적용해야 합니다.

#### Juniper Junos

**Step 2) 스푸핑 방지 필터링 Firewall Filters 구성**

**Step 3) IP 대역 지정**

```
[edit policy-options]
user@host# set prefix-list <prefix-name> 0.0.0.0/8
user@host# set prefix-list <prefix-name> 10.0.0.0/8
user@host# set prefix-list <prefix-name> 127.0.0.0/8
user@host# set prefix-list <prefix-name> 169.254.0.0/16
user@host# set prefix-list <prefix-name> 172.16.0.0/12
user@host# set prefix-list <prefix-name> 192.0.2.0/24
user@host# set prefix-list <prefix-name> 192.168.0.0/16
user@host# set prefix-list <prefix-name> 224.0.0.0/4
```

**Step 4) 방화벽 필터 설정**

```
[edit firewall family inet filter <filter-name>]
user@host# edit term <term-name-1>
[edit firewall family inet filter <filter-name> term <term-name-1>]
user@host# set from source-address <prefix-name>
user@host# set then discard
```

**Step 5) 기본 허용 규칙 추가**

```
[edit firewall family inet filter <filter-name>]
user@host# set term <term-name-2> then accept
```

**인터페이스에 필터 적용**:

```
[edit]
user@host# set interfaces <인터페이스> unit <유닛> family inet filter input <filter-name>
```

### 주의사항

1. **인터페이스 확인**: 반드시 외부(인터넷) 인터페이스에만 적용해야 합니다. 내부 인터페이스에 적용하면 사설 IP를 사용하는 내부 트래픽이 차단됩니다.

2. **로그 설정**: ACL 로그가 과도하게 발생할 경우 CPU 사용률이 증가할 수 있으므로, 로그 설정을 비활성화하거나 로그 레벨을 조정해야 합니다.

3. **BCP 38 준수**: 이 설정은 RFC 2827 (BCP 38) "Network Ingress Filtering: Defeating Denial of Service Attacks which employ IP Source Address Spoofing"을 따르는 것입니다.

4. **정기적 검토**: 네트워크 구성 변경 시 스푸핑 방지 필터링이 적절히 적용되는지 확인해야 합니다.

**권장 설정**:
- 경계 라우터의 외부 인터페이스에 필수 적용
- 모든 RFC 6890 특수 용도 주소 차단
- 로그는 필요한 경우에만 활성화 (CPU 부하 주의)
