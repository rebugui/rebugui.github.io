---
title: "[2026 주요정보통신기반시설] N-30 N-30: CDP 서비스 차단"
slug: "2026-주정통/N-30"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "CDP서비스를차단하는지점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Network
---

# N-30: CDP 서비스 차단

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | N-30 |
| **점검내용** | CDP서비스를차단하는지점검 |
| **점검대상** | Cisco등 |
| **판단기준** | 양호: CDP서비스를차단하는경우 |
| **판단기준** | 취약: CDP서비스를차단하지않는경우 |
| **조치방법** | Ÿ 장비별CDP서비스제한설정 Ÿ CDP는 Cisco 전용 프로토콜이지만 일부 다른 벤더도 지원하며, CDP와 유사한 IEEE 표준인 LLDP(Link Layer Discovery Protocol, IEEE 802.1AB)도불필요할경우비활성화 |

---
## 상세 설명

### 개요

CDP 서비스 차단 항목은 Cisco Discovery Protocol(CDP) 서비스가 비활성화되어 있는지 점검하는 항목입니다. CDP는 장비 정보를 노출할 수 있으므로 불필요한 경우 차단해야 합니다.

### 필요성

**보안 위협**

CDP를 차단하지 않을 경우 다음과 같은 위협에 노출됩니다.

1. **정보 유출**: 비인가자가 Cisco 장비의 IOS 버전, 모델, 디바이스 정보를 획득할 수 있습니다.

2. **DoS 공격**: Routing Protocol Attack을 통해 네트워크 장비의 서비스 거부 공격이 가능합니다.

**CDP란?**

Cisco 제품의 관리를 목적으로 만든 프로토콜로, 같은 네트워크에 있는 장비들과 정보를 공유하고 같은 세그먼트에 있는 다른 라우터에 IOS version, Model, device 등의 정보를 제공합니다.

### 점검 및 조치 방법

#### Cisco IOS

**점검**: `cdp run`, global cdp 설정 확인

```
Router# show running-config
Router# show cdp
```

**조치**: CDP 서비스 차단 설정

```
Router# config terminal
```

**전체 라우터에서 CDP 비활성화**:

```
Router(config)# no cdp run
```

**특정 인터페이스에서 CDP 비활성화**:

```
Router(config)# interface FastEthernet0/1
Router(config-if)# no cdp enable
```

> **참고**: CDP를 라우터 전체에서 사용하지 못하도록 하기 위해서는 `no cdp run` 명령어를 사용하며, 특정 인터페이스에서 사용하지 못하도록 하려면 `no cdp enable` 명령어를 사용합니다.

### 주의사항

1. **LLDP도 고려**: CDP와 유사한 IEEE 표준인 LLDP(Link Layer Discovery Protocol, IEEE 802.1AB)도 불필요한 경우 비활성화해야 합니다.

2. **VoIP 구성**: 인터넷 전화(VoIP) 구성 방식에 따라 IP 전화기와 스위치가 CDP 또는 LLDP를 사용할 수 있으므로 주의가 필요합니다.

**권장 설정**:
- 일반적인 경우: CDP 비활성화
- VoIP 환경: 필요한 인터페이스에서만 CDP 활성화
