---
title: "[2026 주요정보통신기반시설] N-33 N-33: Proxy ARP 차단"
slug: "2026-주정통/N-33"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "ProxyARP를차단하는지점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Network
---

# N-33: Proxy ARP 차단

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | N-33 |
| **점검내용** | ProxyARP를차단하는지점검 |
| **점검대상** | Cisco, Juniper등 |
| **판단기준** | 양호: ProxyARP를차단하는경우 |
| **판단기준** | 취약: ProxyARP를차단하지않는경우 |
| **조치방법** | 각인터페이스에서ProxyARP비활성화설정 |

---
## 상세 설명

### 개요

Proxy ARP 차단 항목은 Proxy ARP 기능을 비활성화하여 IP와 MAC이 관련된 호스트에 대해 정상적인 통신을 유지하는 항목입니다.

### 필요성

**보안 위협**

Proxy ARP를 차단하지 않을 경우 악의적인 사용자가 보낸 거짓 IP와 MAC 정보를 보관하게 되며, 이로 인해 호스트 간 정상적인 통신이 이루어지지 않을 수 있습니다.

**Proxy ARP란?**

동일 서브넷에서 다른 호스트를 대신하여 ARP Request에 응답하는 기술입니다.

### 점검 및 조치 방법

#### Cisco IOS

**조치**: Interface Configuration 모드에서 비활성화

```
Router# config terminal
Router(config)# interface <인터페이스>
Router(config-if)# no ip proxy-arp
```

### 주의사항

1. **사전 조사**: 게이트웨이 또는 서브넷 마스크를 잘못 설정한 호스트가 네트워크 장비의 Proxy ARP에 의해 통신하는 상태인 경우를 고려하여 사전 조사가 필요합니다.

2. **일반적 사용**: 대부분의 환경에서 Proxy ARP는 불필요하므로 비활성화하는 것이 일반적입니다.

**권장 설정**:
- 대부분의 인터페이스에서 Proxy ARP 비활성화
- 특수한 환경에서만 필요한 경우에만 활성화
