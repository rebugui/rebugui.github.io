---
title: "[2026 주요정보통신기반시설] N-31 N-31: Directed-broadcast 차단"
slug: "2026-주정통/N-31"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "Directed-broadcast를차단하는지점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Network
---

# N-31: Directed-broadcast 차단

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | N-31 |
| **점검내용** | Directed-broadcast를차단하는지점검 |
| **점검대상** | Cisco, Alteon, Passport등 |
| **판단기준** | 양호: Directed Broadcasts를차단하는경우 |
| **판단기준** | 취약: Directed Broadcasts를차단하지않는경우 |
| **조치방법** | 장치별로Directed Broadcasts제한설정 |

---
## 상세 설명

### 개요

Directed-broadcast 차단 항목은 IP Directed Broadcast를 차단하여 Smurf 공격 등의 DoS 공격을 방지하는 항목입니다.

### 필요성

**보안 위협**

Directed Broadcast를 차단하지 않을 경우 Smurf 공격에 노출됩니다. IP Directed-Broadcast는 Unicast IP 패킷이 특정 서브넷에 도착했을 때 Link-Layer Broadcast로 전환되는 것을 허용하며, 이는 악의적으로 이용되어 Smurf 공격에 사용될 수 있습니다.

**Smurf 공격이란?**

IP Broadcast나 기타 인터넷 운용 측면을 이용하여 인터넷망을 공격하는 행위로, Broadcast에 대한 응답받을 IP 주소를 변조하여 해당 IP 주소 호스트에 DoS 공격을 감행하는 공격 기법입니다.

### 점검 및 조치 방법

#### Cisco IOS

**점검**: Directed-Broadcast 설정 확인

```
Router# show running-config
```

**조치**: Interface Configuration 모드에서 비활성화

```
Router# config terminal
Router(config)# interface <인터페이스>
Router(config-if)# no ip directed-broadcast
```

#### Radware Alteon

**점검**: `dirbr`에서 disable 설정 확인

**조치**: dirbr 서비스 비활성화

```
# cfg/l3/frwd
# dirbr disable
# apply
# save
```

#### Passport

**점검**: config에서 ip directed-broadcast 설정 확인

**조치**: directed-broadcast 서비스 비활성화

```
# config vlan <vid>
# ip directed-broadcast disable
```

### 주의사항

1. **모든 인터페이스에 적용**: 외부(인터넷) 인터페이스뿐만 아니라 모든 인터페이스에 적용하는 것을 권장합니다.

**권장 설정**:
- 모든 인터페이스에서 Directed Broadcast 차단
