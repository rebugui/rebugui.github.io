---
title: "[2026 주요정보통신기반시설] N-35 N-35: identd 서비스 차단"
slug: "2026-주정통/N-35"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "identd서비스를차단하는지점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Network
draft: true
---

# N-35: identd 서비스 차단

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | N-35 |
| **점검내용** | identd서비스를차단하는지점검 |
| **점검대상** | Cisco등 |
| **판단기준** | 양호: identd서비스를차단하는경우 |
| **판단기준** | 취약: identd서비스를차단하지않는경우 |
| **조치방법** | idnetd서비스비활성화 |

---
## 상세 설명

### 개요

identd 서비스 차단 항목은 불필요한 identd(Identification Protocol Daemon) 서비스를 차단하여 잠재적인 취약점 및 공격에 노출을 방지하는 항목입니다.

### 필요성

**보안 위협**

identd 서비스는 TCP 세션의 사용자 식별이 가능하여 비인가자에게 사용자 정보가 노출될 수 있습니다.

**identd란?**

특정 TCP 연결을 시작한 사용자의 신원을 확인하는 서비스(113/TCP)입니다. 사용자가 서버로 TCP 연결을 시작하면 서버는 클라이언트의 identd 서비스에 TCP 세션의 포트 번호를 보내 클라이언트 운영 체제와 사용자 ID를 조회할 수 있습니다.

> **참고**: 클라이언트의 정보에 의존하기 때문에 인증 또는 접근 제어 용도로 사용할 수 없습니다. IOS 12.2 이상은 Default로 차단되어 있습니다.

### 점검 및 조치 방법

#### Cisco IOS

**점검**: identd 서비스 확인

```
Router# show running-config
```

**조치**: Global Configuration 모드에서 비활성화

```
Router# config terminal
Router(config)# no ip identd
```

> **참고**: 기본적으로 `ip identd` 설정을 별도로 설정하지 않으면 비활성화 상태이며, 구성에서 `no ip identd` 명령어가 표시되지 않습니다.

**권장 설정**:
- 모든 장비에서 identd 서비스 비활성화
