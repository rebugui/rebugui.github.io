---
title: "[2026 주요정보통신기반시설] N-28 N-28: TCP/UDP Small 서비스 차단"
slug: "2026-주정통/N-28"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "TCP/UDPSmall서비스가제한되어있는지점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Network
---

# N-28: TCP/UDP Small 서비스 차단

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | N-28 |
| **점검내용** | TCP/UDPSmall서비스가제한되어있는지점검 |
| **점검대상** | Cisco등 |
| **판단기준** | 양호: TCP/UDPSmall서비스가제한된경우 |
| **판단기준** | 취약: TCP/UDPSmall서비스가제한되지않은경우 |
| **조치방법** | TCP/UDP Small Service제한설정 |

---
## 상세 설명

### 개요

TCP/UDP Small 서비스 차단 항목은 네트워크 장비의 불필요한 Small 서비스(echo, discard, daytime, chargen 등)가 비활성화되어 있는지 점검하는 항목입니다. 이러한 서비스는 DoS 공격의 대상이 될 수 있으므로 차단해야 합니다.

### 필요성

**보안 위협**

TCP/UDP Small 서비스를 차단하지 않을 경우 다음과 같은 위협에 노출됩니다.

1. **DoS 공격 대상**: echo, discard, daytime, chargen 등의 서비스는 DoS 공격에 악용될 수 있습니다.

2. **리플레이 공격**: chargen과 echo 서비스를 조합하여 리플레이 공격을 수행할 수 있습니다.

### TCP/UDP Small 서비스 종류

- **echo**: 에코 서비스 (포트 7/TCP, UDP)
- **discard**: 폐기 서비스 (포트 9/TCP, UDP)
- **daytime**: 날짜/시간 서비스 (포트 13/TCP, UDP)
- **chargen**: 문자 생성 서비스 (포트 19/TCP, UDP)

### 점검 방법

#### Cisco IOS 장비

**Step 1) Small 서비스 설정 확인**

```
Router> enable
Router# show running-config
```

`service tcp-small-servers`, `service udp-small-servers` 설정을 확인합니다.

> **참고**: IOS 11.3 이상에서는 기본적으로 서비스가 제거된 상태이므로 Small 서버들이 Default로 Disable되어 있습니다. 낮은 버전의 경우는 직접 설정해주어야 합니다.

### 조치 방법

#### Cisco IOS

**Step 2) TCP Small 서비스 차단**

```
Router# config terminal
Router(config)# no service tcp-small-servers
```

**Step 3) UDP Small 서비스 차단**

```
Router# config terminal
Router(config)# no service udp-small-servers
```

### 주의사항

1. **IOS 버전 확인**: IOS 11.3 이상은 기본적으로 비활성화되어 있습니다. 낮은 버전을 사용하는 경우 반드시 비활성화해야 합니다.

2. **사용 여부 확인**: 이러한 Small 서비스는 일반적으로 거의 사용하지 않으므로 안전하게 비활성화할 수 있습니다.

**권장 설정**:
- 모든 장비에서 TCP/UDP Small 서비스 비활성화
