---
title: "[2026 주요정보통신기반시설] N-38 N-38: mask-reply 차단"
slug: "2026-주정통/N-38"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "mask-reply를차단하는지점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Network
---

# N-38: mask-reply 차단

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | N-38 |
| **점검내용** | mask-reply를차단하는지점검 |
| **점검대상** | Cisco등 |
| **판단기준** | 양호: mask-reply를차단하는경우 |
| **판단기준** | 취약: mask-reply를차단하지않은경우 |
| **조치방법** | 각인터페이스에서mask-reply비활성화 |

---
## 상세 설명

### 개요

mask-reply 차단 항목은 내부 네트워크의 서브넷 마스크 정보를 요청하는 ICMP 메시지에 네트워크 장비가 응답하지 않도록 mask-reply를 차단 설정하는 항목입니다.

### 필요성

**보안 위협**

mask-reply를 차단하지 않는 경우 비인가자에게 내부 서브 네트워크의 서브넷 마스크 정보가 노출될 수 있습니다.

**mask-reply란?**

네트워크 장비는 ICMP Address Mask Request 메시지에 대한 응답으로 인터페이스의 서브넷 마스크 정보를 제공합니다.

### 점검 및 조치 방법

#### Cisco IOS

**점검 1**: mask-reply 차단 여부 확인

```
Router# show running-config
```

**점검 2**: `show ip interface` 실행 결과에서 ICMP Address mask-reply 차단 여부 확인

```
Router# show ip interface
```

출력 예시:
```
Serial1/0 is up, line protocol is up
  ICMP mask replies are never sent
```

**조치**: Interface Configuration 모드에서 비활성화

```
Router# config terminal
Router(config)# interface <인터페이스>
Router(config-if)# no ip mask-reply
```

> **참고**: 기본적으로 `ip mask-reply` 명령은 비활성화 상태이기 때문에 구성 내용에서 `no ip mask-reply` 명령이 표시되지 않습니다.

**권장 설정**:
- 모든 인터페이스에서 mask-reply 비활성화
