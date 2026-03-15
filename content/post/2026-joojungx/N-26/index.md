---
title: "[2026 주요정보통신기반시설] N-26 N-26: Finger 서비스 차단"
slug: "2026-주정통/N-26"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "네트워크장비서비스중Finger서비스를비활성화하고있는지점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Network
---

# N-26: Finger 서비스 차단

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | N-26 |
| **점검내용** | 네트워크장비서비스중Finger서비스를비활성화하고있는지점검 |
| **점검대상** | Cisco, Juniper등 |
| **판단기준** | 양호: Finger서비스를차단하는경우 |
| **판단기준** | 취약: Finger서비스를차단하지않는경우 |
| **조치방법** | 장비별Finger서비스제한설정 |

---
## 상세 설명

### 개요

Finger 서비스 차단 항목은 네트워크 장비의 Finger 서비스(사용자 정보 확인 서비스)가 비활성화되어 있는지 점검하는 항목입니다. Finger 서비스는 네트워크 외부에서 사용자 정보를 조회할 수 있어 보안에 취약하므로 반드시 차단해야 합니다.

### 필요성

**보안 위협**

Finger 서비스를 차단하지 않을 경우 다음과 같은 위협에 노출됩니다.

1. **사용자 정보 노출**: 로그인한 계정 ID, 접속 IP 등 중요 정보가 노출됩니다.

2. **접속 상태 노출**: 장비의 접속 상태가 외부에서 파악될 수 있습니다.

3. **무단 접근 시도**: VTY 사용 현황을 원격에서 파악하여 무단 접근을 시도할 위험이 있습니다.

**Finger란?**

사용자 정보 확인 서비스로, 접속된 시스템에 등록된 사용자뿐만 아니라 네트워크를 통해 연결된 다른 시스템에 등록된 사용자들에 대한 자세한 정보를 보여주는 서비스입니다.

### 점검 방법

#### Cisco IOS 장비

**Step 1) Finger 서비스 설정 확인**

```
Router> enable
Router# show running-config
```

`service finger` 또는 `ip finger` 설정을 확인합니다.

> **참고**: Cisco IOS 12.1(5) 및 12.1(5)T 이상은 기본적으로 비활성화되어 있습니다.

#### Juniper Junos 장비

**Step 1) Finger 서비스 설정 확인**

```
user@host> configure
[edit]
user@host# show
```

`system services` 레벨에서 `finger` 설정을 확인합니다.

### 조치 방법

#### Cisco IOS

**Step 2) Finger 서비스 비활성화**

```
Router# config terminal
Router(config)# no service finger
```

또는

```
Router(config)# no ip finger
```

> **참고**: 최근 출시되는 IOS는 `no service finger` 명령 대신 `no ip finger` 명령을 사용하기도 합니다.

#### Juniper Junos

**Step 2) Finger 서비스 비활성화**

```
[edit system services]
user@host# delete finger
[edit system services]
user@host# commit
```

### 주의사항

1. **IOS 버전 확인**: IOS 12.1(5) 이상은 기본적으로 비활성화되어 있습니다.

2. **대안 없음**: Finger 서비스는 보안에 매우 취약하므로 사용할 수 있는 대안이 없습니다. 반드시 비활성화해야 합니다.

**권장 설정**:
- 모든 장비에서 Finger 서비스 비활성화
