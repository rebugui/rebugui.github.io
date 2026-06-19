---
title: "[2026 주요정보통신기반시설] N-29 N-29: Bootp 서비스 차단"
slug: "2026-주정통/N-29"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "BOOTP서비스의차단여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Network
draft: true
---

# N-29: Bootp 서비스 차단

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | N-29 |
| **점검내용** | BOOTP서비스의차단여부점검 |
| **점검대상** | Cisco, Alteon, Juniper등 |
| **판단기준** | 양호: BOOTP서비스가제한된경우 |
| **판단기준** | 취약: BOOTP서비스가제한되지않은경우 |
| **조치방법** | 장비별BOOTP서비스제한설정 |

---
## 상세 설명

### 개요

Bootp 서비스 차단 항목은 BOOTP(Bootstrap Protocol) 서비스가 비활성화되어 있는지 점검하는 항목입니다. BOOTP는 네트워크 부팅을 위한 프로토콜로, 비인가자가 OS 정보에 접근하는 것을 방지해야 합니다.

### 필요성

**보안 위협**

BOOTP 서비스를 차단하지 않을 경우 다음과 같은 위협에 노출됩니다.

1. **OS 사본 유출**: 다른 라우터 상의 OS 사본에 접근할 수 있습니다.

2. **악성코드 삽입**: OS 소프트웨어 복사본을 다운로드하여 시스템 취약점을 악용하거나 악성코드를 삽입할 수 있습니다.

3. **자동 재부팅**: 라우터를 자동 재부팅하는 취약점이 존재하므로 서비스를 차단하여 방어해야 합니다.

**BOOTP란?**

네트워크를 이용하여 사용자가 OS를 로드할 수 있게 하며, 자동으로 IP 주소를 받게 하고, 부팅 파일 정보를 서버로부터 요청하여 부팅하는 데 사용하는 프로토콜입니다.

### 점검 및 조치 방법

#### Cisco IOS

**점검**: `ip bootp server` 설정 확인

```
Router# show running-config
```

**조치**: BOOTP 차단 설정

```
Router# config terminal
Router(config)# no ip bootp server
```

**DHCP 서비스는 유지하고 BOOTP만 차단하는 경우**:

```
Router(config)# ip dhcp bootp ignore
```

#### Radware Alteon

**점검**: `bootp disable` 설정 확인

**조치**: BOOTP 차단 설정

```
Main# /cfg/sys/bootp dis
Main# apply
```

#### Juniper Junos

**점검**: bootp 서비스 설정 확인

```
user@switch> show configuration
user@switch> show interfaces detail
```

**조치**: DHCP 서버 IP 주소와 서버가 연결된 스위치에 대한 인터페이스 지정 옵션 제거

```
user@switch> configure
[edit forwarding-options helpers bootp]
user@switch# no set interface <인터페이스 포트> server <주소>
```

### 주의사항

1. **DHCP와의 관계**: DHCP 서비스(서버 및 릴레이)를 유지하면서 BOOTP만 차단할 수 있습니다.

2. **자동 재부팅 취약점**: 라우터를 자동 재부팅하는 취약점이 있으므로 서비스를 차단하여 방어하는 것을 권고합니다.

**권장 설정**:
- BOOTP 서비스 비활성화
