---
title: "[2026 주요정보통신기반시설] N-16 N-16: Timestamp 로그 설정"
slug: "2026-주정통/N-16"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "네트워크장비설정중timestamp를설정하여로그시간을기록할수있게하였는지점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Network
---

# N-16: Timestamp 로그 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | N-16 |
| **점검내용** | 네트워크장비설정중timestamp를설정하여로그시간을기록할수있게하였는지점검 |
| **점검대상** | Cisco등 |
| **판단기준** | 양호: timestamp로그설정이되어있는경우 |
| **판단기준** | 취약: timestamp로그설정이되어있지않은경우 |
| **조치방법** | 로그에시간정보가기록될수있도록timestamp로그설정 |

---
## 상세 설명

### 개요

Timestamp 로그 설정 항목은 네트워크 장비의 로그 메시지에 정확한 시간 정보가 기록되도록 설정하는 항목입니다. Timestamp는 로그의 신뢰성을 확보하고, 공격 및 침입 시도에 대한 분석을 가능하게 합니다.

### 필요성

**보안 위협**

Timestamp를 설정하지 않을 경우 다음과 같은 문제가 발생합니다.

1. **분석 불가**: 로그에 시간이 기록되지 않아 공격 및 침입 시도에 관한 정보를 정확히 분석할 수 없습니다.

2. **신뢰성 상실**: 로그 기록에 대한 신뢰성을 잃게 되어 법적 증거로 사용하기 어렵습니다.

3. **타임라인 구성 불가**: 보안 사고 발생 시 정확한 시간 순서대로 사건을 재구성할 수 없습니다.

**Timestamp란?**

네트워크 장비 로그 메시지에 관리자가 지정한 형식으로 시간 정보를 남기도록 하는 설정입니다.

### 점검 방법

#### Cisco IOS 장비

**Step 1) service timestamps 설정 확인**

```
Router> enable
Router# show running-config
```

`service timestamps` 설정을 확인합니다.

```
Router# show logging
```

로그 메시지에 시간 정보가 포함되어 있는지 확인합니다.

### 조치 방법

#### Cisco IOS

**Step 2) timestamp 로그 설정**

**1. UTC 시간대로 밀리초 단위까지 표시**

```
Router# config terminal
Router(config)# service timestamps log datetime msec show-timezone
```

**2. 로컬 시간대로 밀리초 단위까지 표시**

```
Router(config)# clock timezone KST 9
Router(config)# service timestamps log datetime msec localtime show-timezone
```

**파라미터 설명**:
- `log`: 로그 메시지에 timestamp 추가
- `datetime`: 날짜와 시간 형식 사용
- `msec`: 밀리초 단위까지 표시
- `localtime`: 로컬 시간대 사용 (미지정 시 UTC)
- `show-timezone`: 시간대 정보 표시

**설정 예시**:

```
Router(config)# service timestamps log datetime msec localtime show-timezone
Router(config)# service timestamps debug datetime msec localtime show-timezone
```

### 주의사항

1. **시간대 설정**: `clock timezone` 명령어로 장비의 시간대를 올바르게 설정해야 합니다.

2. **NTP 연계**: N-15(NTP 및 시각 동기화 설정) 항목과 연계하여 정확한 시간을 유지해야 합니다.

3. **시간 형식**: 기관의 표준에 따라 UTC 또는 로컬 시간대를 선택해야 합니다.

4. **밀리초 단위**: 정밀한 분석을 위해 밀리초 단위 표시를 권장합니다.

5. **로그와 디버그**: `log`와 `debug` 모두에 timestamp를 설정하는 것을 권장합니다.

6. **시간 동기화**: 장비 간 시간 차이를 최소화하기 위해 모든 장비에 동일한 timestamp 설정을 적용해야 합니다.

**권장 설정**:

```
Router(config)# clock timezone KST 9
Router(config)# service timestamps log datetime msec localtime show-timezone
Router(config)# service timestamps debug datetime msec localtime show-timezone
```

이렇게 설정하면 로그 메시지가 다음과 같이 표시됩니다:

```
*Mar 1 00:01:22.315 KST: %SYS-5-CONFIG_I: Configured from console by console
```
