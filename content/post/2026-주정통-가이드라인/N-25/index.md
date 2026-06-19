---
title: "[2026 주요정보통신기반시설] N-25 N-25: TCP Keepalive 서비스 설정"
slug: "2026-주정통/N-25"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "TCP Keepalive서비스를사용하는지점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Network
draft: true
---

# N-25: TCP Keepalive 서비스 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | N-25 |
| **점검내용** | TCP Keepalive서비스를사용하는지점검 |
| **점검대상** | Cisco등 |
| **판단기준** | 양호: TCP Keepalive서비스를설정한경우 |
| **판단기준** | 취약: TCP Keepalive서비스를설정하지않은경우 |
| **조치방법** | 네트워크장비에서TCPKeepalive서비스를사용하도록설정 |

---
## 상세 설명

### 개요

TCP Keepalive 서비스 설정 항목은 네트워크 장비의 TCP 연결이 유휴 상태일 때 주기적으로 연결 상태를 확인하고, 비정상 종료된 연결을 해제하는 기능을 설정하는 항목입니다. 유휴 TCP 세션은 무단 접근 및 하이재킹 공격에 취약하므로 이를 방지해야 합니다.

### 필요성

**보안 위협**

TCP Keepalive를 설정하지 않을 경우 다음과 같은 위협에 노출됩니다.

1. **유휴 세션 하이재킹**: 장시간 유휴 상태인 TCP 세션을 하이재킹당할 수 있습니다.

2. **리소스 낭비**: 비정상 종료된 연결이 계속 유지되어 리소스를 낭비합니다.

3. **무단 접근**: 유휴 세션을 악용하여 무단 접근이 가능할 수 있습니다.

**TCP Keepalive란?**

TCP 연결이 유효한지 확인하기 위해 유휴 연결에 주기적으로 응답을 요구하는 패킷을 전송하고, 원격 호스트가 일정 시간 동안 응답이 없으면 연결을 끊는 기능입니다.

### 점검 방법

#### Cisco IOS 장비

**Step 1) TCP Keepalive 서비스 설정 확인**

```
Router> enable
Router# show running-config
```

`service tcp-keepalives-in` 및 `service tcp-keepalives-out` 설정을 확인합니다.

### 조치 방법

#### Cisco IOS

**Step 2) 들어오는 TCP 연결에 Keepalive 설정**

```
Router# config terminal
Router(config)# service tcp-keepalives-in
```

**Step 3) 나가는 TCP 연결에 Keepalive 설정**

```
Router# config terminal
Router(config)# service tcp-keepalives-out
```

### 주의사항

1. **양방향 설정**: 들어오는 연결과 나가는 연결 모두에 설정하는 것을 권장합니다.

2. **Keepalive 간격**: 기본 Keepalive 간격과 시간 초과값은 장비마다 다를 수 있습니다.

3. **네트워크 환경**: 안정적인 네트워크 환경에서는 설정이 문제가 되지 않지만, 불안정한 환경에서는 너무 짧은 간격으로 설정하면 정상적인 연결이 끊어질 수 있습니다.

**권장 설정**:
- `service tcp-keepalives-in`: 활성화
- `service tcp-keepalives-out`: 활성화
