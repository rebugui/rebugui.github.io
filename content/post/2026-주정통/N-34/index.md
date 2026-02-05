---
title: "[2026 주요정보통신기반시설] N-34 N-34: ICMP unreachable, Redirect 차단"
slug: "2026-주정통/N-34"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "ICMP unreachable, ICMP redirect를차단하는지점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Network
---

# N-34: ICMP unreachable, Redirect 차단

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | N-34 |
| **점검내용** | ICMP unreachable, ICMP redirect를차단하는지점검 |
| **점검대상** | Cisco, Juniper등 |
| **판단기준** | 양호: ICMP unreachable, ICMP redirect를차단하는경우 |
| **판단기준** | 취약: ICMP unreachable, ICMP redirect를차단하지않는경우 |
| **조치방법** | 각인터페이스에서ICMPunreachables, ICMP redirects비활성화 |

---
## 상세 설명

### 개요

ICMP unreachable, Redirect 차단 항목은 ICMP unreachable과 ICMP redirect 메시지를 차단하여 DoS 공격을 방지하고 라우팅 테이블이 변경되는 것을 차단하는 항목입니다.

### 필요성

**보안 위협**

1. **ICMP Unreachable**: 공격자의 스캔 공격을 통해 시스템의 운영 상태 정보가 노출될 수 있습니다. 연속적으로 ICMP port-unreachable frame을 보내서 시스템 성능을 저하 또는 마비시킬 수 있습니다.

2. **ICMP Redirect**: 호스트 패킷 경로를 재지정하는 과정에서 특정 목적지로 가기 위해 고의로 패킷 경로를 변경하여 가로챌 수 있습니다.

### 점검 및 조치 방법

#### Cisco IOS

**점검**: 각 인터페이스에서 설정 확인

```
Router# show running-config
```

**조치**: Interface Configuration 모드에서 비활성화

```
Router# config terminal
Router(config)# interface <인터페이스>
Router(config-if)# no ip unreachables
Router(config-if)# no ip redirects
Router(config-if)# end
```

> **참고**: Null Interface는 `no ip unreachables` 외 다른 모든 명령어는 무시됩니다.

#### Juniper Junos

**점검**: ICMP unreachables, ICMP redirects 적용 확인

```
user@host# show
```

**조치**: ICMP redirect 차단

전체 장비에서 ICMP redirect 비활성화:

```
[edit system]
user@host# set no-redirects
```

또는 특정 인터페이스에서 ICMP Redirect 비활성화:

```
[edit interfaces]
user@host# set <인터페이스> unit <유닛> family <패밀리> no-redirects
```

### 주의사항

1. **경로 탐색 영향**: 특정 경로를 찾을 때 많은 시간이 경과될 수 있으므로 주의가 필요합니다.

2. **Global 명령어 주의**: Global Configuration 모드의 `ip icmp redirects` 명령어는 ICMP redirection 메시지 유형을 호스트 또는 서브넷으로 지정하는 명령어로 ICMP redirection 차단과 무관합니다.

**권장 설정**:
- 외부(인터넷) 인터페이스: ICMP unreachable/redirect 차단 권장
- 내부 인터페이스: 필요한 경우에만 허용
