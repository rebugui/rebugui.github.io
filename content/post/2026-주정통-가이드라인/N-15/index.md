---
title: "[2026 주요정보통신기반시설] N-15 N-15: NTP 및 시각 동기화 설정"
slug: "2026-주정통/N-15"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "네트워크장비의NTP서버연동및시간동기화설정적용여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Network
draft: true
---

# N-15: NTP 및 시각 동기화 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | N-15 |
| **점검내용** | 네트워크장비의NTP서버연동및시간동기화설정적용여부점검 |
| **점검대상** | Cisco, Alteon, Juniper등 |
| **판단기준** | 양호: NTP서버를통한시스템간실시간시간동기화가설정된경우 |
| **판단기준** | 취약: NTP서버와연동되어있지않아시스템간실시간시간동기화설정이되어있지않은경우 |
| **조치방법** | NTP사용시신뢰할수있는서버로설정 |

---
## 상세 설명

### 개요

NTP(Network Time Protocol) 및 시각 동기화 설정 항목은 네트워크 장비가 신뢰할 수 있는 NTP 서버와 시간을 동기화하도록 설정하는 항목입니다. 정확한 시간 동기화는 로그 분석, 보안 사고 조사, 시스템 간 연계 작업에 필수적입니다.

### 필요성

**보안 위협**

시간 동기화가 미흡할 경우 다음과 같은 문제가 발생합니다.

1. **로그 분석 어려움**: 시스템 간 시간 차이로 인해 이벤트 간의 인과 관계 파악이 어렵습니다.

2. **신뢰성 저하**: 보안 사고 및 장애 발생 시 로그에 대한 신뢰도 확보가 미흡해집니다.

3. **법적 증거 약화**: 법적 절차에서 로그의 증거 가치가 떨어질 수 있습니다.

4. **포렌식 실패**: 침해 사고 시 정확한 타임라인을 구성할 수 없습니다.

**NTP란?**

NTP(Network Time Protocol)는 네트워크상의 컴퓨터 간 시간 동기화를 위한 프로토콜로, UTC(Coordinated Universal Time)를 기준으로 정확한 시간 정보를 제공합니다.

### 점검 방법

#### Cisco IOS 장비

**Step 1) NTP 서버 설정 확인**

```
Router> enable
Router# show running-config
```

`ntp server` 설정을 확인합니다.

```
Router# show ntp associations
```

NTP 동기화 상태를 확인합니다.

#### Radware Alteon 장비

**Step 1) NTP 서버 설정 확인**

```
Main# /cfg/dump
```

`/sys/ntp` 설정을 확인합니다.

#### Juniper Junos 장비

**Step 1) NTP 서비스 설정 확인**

```
user@host> configure
[edit]
user@host# show
```

`system ntp` 설정을 확인합니다.

### 조치 방법

#### Cisco IOS

**Step 2) NTP 서버 설정**

```
Router# config terminal
Router(config)# ntp server <NTP 서버 IP>
```

**예시**:

```
Router(config)# ntp server 10.0.0.1
Router(config)# ntp server 10.0.0.2 prefer
```

`prefer` 키워드는 해당 서버를 우선 서버로 지정합니다.

**시간대 설정**:

```
Router(config)# clock timezone KST 9
```

#### Radware Alteon

**Step 2) NTP 설정**

```
Main# /cfg
Main# /sys/ntp
```

```
Main# /on
Main# /prisrvr <NTP 서버 IP>
Main# /interval <동기화 주기>
Main# /tzone +9:00
Main# apply
Main# save
```

- `interval`: 동기화 주기 (초 단위)
- `tzone +9:00`: 한국 표준시 (UTC+9)

#### Juniper Junos

**Step 2) NTP 서버와 부트 서버 설정**

```
user@host> configure
[edit]
user@host# edit system ntp
[edit system ntp]
```

**NTP 서버 설정**:

```
user@host# set server <NTP 서버 IP>
```

**NTP 부트 서버 설정**:

```
user@host# set boot-server <NTP 부트 서버 IP>
```

> **중요**: 네트워크 장비와 NTP 서버 간 시간 차이가 1000초(약 17분) 이상 다르면 시간 동기화를 하지 않기 때문에, 부팅 단계에서 정확한 시간을 확보하도록 부트 서버를 구성해야 합니다.

### 주의사항

1. **신뢰할 수 있는 NTP 서버**: 공인 NTP 서버 또는 기관 내부 NTP 서버를 사용해야 합니다.

2. **다중 NTP 서버**: 최소 2개 이상의 NTP 서버를 설정하여 안정성을 확보해야 합니다.

3. **ACL 설정**: IOS 12.2 이전 버전을 사용하는 장비에는 NTP 서버에 대한 접근 통제(ACL) 설정이 필요합니다.

4. **시간대 설정**: 장비의 시간대를 올바르게 설정해야 로그 분석 시 혼란을 방지할 수 있습니다.

5. **동기화 상태 모니터링**: 정기적으로 `show ntp associations` 또는 `show ntp status` 명령어로 동기화 상태를 확인해야 합니다.

6. **NTP 보안**: 가능한 경우 NTP 인증을 사용하여 스푸핑 공격을 방지해야 합니다.

**권장 설정**:
- NTP 서버: 최소 2개 이상
- 동기화 주기: 3600초(1시간) 이하
- 시간대: KST (UTC+9)
- 인증: NTP authentication 활성화 권장
