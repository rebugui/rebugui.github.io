---
title: "[2026 주요정보통신기반시설] N-32 N-32: Source Routing 차단"
slug: "2026-주정통/N-32"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "Source Routing을차단하는지점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Network
---

# N-32: Source Routing 차단

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | N-32 |
| **점검내용** | Source Routing을차단하는지점검 |
| **점검대상** | Cisco, Juniper등 |
| **판단기준** | 양호: ip-source-route를차단하는경우 |
| **판단기준** | 취약: ip-source-route를차단하지않는경우 |
| **조치방법** | 각인터페이스에서ip-source-route차단설정 |

---
## 상세 설명

### 개요

Source Routing 차단 항목은 IP Source Routing을 차단하여 IP 스푸핑 공격을 방지하는 항목입니다. Source Routing은 공격자가 패킷 경로를 조작할 수 있으므로 차단해야 합니다.

### 필요성

**보안 위협**

Source Routing을 차단하지 않을 경우 다음과 같은 위협에 노출됩니다.

1. **패킷 가로채기**: 공격자가 Source Routing 된 패킷을 네트워크 내부에 발송할 수 있으며, 수신된 패킷에 반응하는 메시지를 가로챌 수 있습니다.

2. **신뢰 관계 위장**: 사용자 호스트를 마치 신뢰 관계에 있는 호스트와 통신하는 것처럼 만들 수 있습니다.

**Source Routing이란?**

송신 측에서 라우팅 경로 정보를 송신 데이터에 포함해 라우팅시키는 방법으로, 패킷이 전송되는 경로를 각각의 시스템이나 네트워크에 설정된 라우팅 경로를 통하지 않고 패킷 발송자가 설정할 수 있는 기능입니다.

### 점검 및 조치 방법

#### Cisco IOS

**조치**: Global Configuration 모드에서 비활성화

```
Router# config terminal
Router(config)# no ip source-route
```

#### Juniper Junos

**점검**: ip source route 설정 확인

```
user@host# show route
```

**조치**:

```
[edit]
user@host# set chassis no-source-route
```

> **참고**: Junos 8.5 버전 이후부터 기본적으로 IPv4 소스 라우팅이 비활성화되어 있습니다.

### 주의사항

1. **IPv6 고려**: IPv6 Source Routing도 차단해야 합니다.

**권장 설정**:
- 모든 장비에서 IP Source Routing 비활성화
