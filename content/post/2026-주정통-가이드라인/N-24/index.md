---
title: "[2026 주요정보통신기반시설] N-24 N-24: 사용하지 않는 인터페이스 비활성화"
slug: "2026-주정통/N-24"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "사용하지않는인터페이스가비활성화상태인지점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Network
draft: true
---

# N-24: 사용하지 않는 인터페이스 비활성화

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | N-24 |
| **점검내용** | 사용하지않는인터페이스가비활성화상태인지점검 |
| **점검대상** | Cisco, Alteon, Juniper, Piolink등 |
| **판단기준** | 양호: 사용하지않는인터페이스가비활성화된경우 |
| **판단기준** | 취약: 사용하지않는인터페이스가비활성화되지않은경우 |
| **조치방법** | 네트워크장비에서사용하지않는모든인터페이스비활성화설정 |

---
## 상세 설명

### 개요

사용하지 않는 인터페이스 비활성화 항목은 네트워크 장비에서 사용하지 않는 인터페이스가 비활성화(shutdown) 상태인지 점검하는 항목입니다. 불필요한 인터페이스를 통해 비인가자가 네트워크에 접근하는 것을 원천적으로 차단해야 합니다.

### 필요성

**보안 위협**

사용하지 않는 인터페이스를 비활성화하지 않을 경우 다음과 같은 위협에 노출됩니다.

1. **물리적 접근 위험**: 사용하지 않는 포트에 연결하여 비인가자가 불법적으로 네트워크에 접근할 수 있습니다.

2. **네트워크 정보 유출**: 활성화된 인터페이스를 통해 네트워크 정보를 수집할 수 있습니다.

3. **네트워크 손상**: 비인가자가 네트워크 장비의 설정을 변경하거나 손상시킬 수 있습니다.

### 점검 방법

#### Cisco IOS 장비

**Step 1) 사용하지 않는 인터페이스 확인**

```
Router> enable
Router# show interface
```

- 비활성화한 인터페이스: `Administratively down`으로 표시
- 활성화되어 있지만 연결되지 않은 인터페이스: `up/down` 또는 `down/down`로 표시

#### Radware Alteon 장비

**Step 1) 사용하지 않는 인터페이스 확인**

```
Main# /cfg/dump
Main# /info/link
```

#### Juniper Junos 장비

**Step 1) 사용하지 않는 인터페이스 확인**

```
[edit]
user@host# show interface terse
```

비활성화한 인터페이스는 `admin` 열이 `down`으로 표시됩니다.

#### Piolink PLOS 장비

**Step 1) 사용하지 않는 인터페이스 확인**

```
switch# show running-config
switch# show port
```

### 조치 방법

#### Cisco IOS

**Step 2) 사용하지 않는 인터페이스 비활성화 (shutdown)**

```
Router# config terminal
Router(config)# interface <인터페이스>
Router(config-if)# shutdown
```

**예시**:

```
Router(config)# interface FastEthernet0/1
Router(config-if)# shutdown
```

#### Radware Alteon

**Step 2) 사용하지 않는 인터페이스 비활성화 (dis)**

```
Main# /cfg/port <포트>/dis
Main# apply
```

#### Juniper Junos

**Step 2) 사용하지 않는 인터페이스 비활성화 (disable)**

```
[edit]
user@host# edit interfaces
[edit interfaces]
user@host# set <인터페이스> disable
```

**예시**:

```
[edit interfaces]
user@host# set ge-0/0/1 disable
```

#### Piolink PLOS

**Step 2) 사용하지 않는 인터페이스 비활성화**

```
switch# configure
switch(config)# port <포트> status disable
switch(config)# apply
```

### 주의사항

1. **사용 중인 포트 확인**: 사용 중인 포트를 실수로 비활성화하지 않도록 주의가 필요합니다.

2. **문서화**: 어떤 인터페이스를 비활성화했는지 문서화하여 추후 문제 발생 시 원인 파악이 용이하도록 해야 합니다.

3. **정기적 점검**: 새로운 인터페이스 추가나 구성 변경 시 불필요한 인터페이스가 활성화되지 않았는지 정기적으로 점검해야 합니다.

4. **포트 보안**: 비활성화된 포트에도 물리적 보안(잠금, 감시 등)이 필요할 수 있습니다.

**권장 사항**:
- 모든 사용하지 않는 인터페이스 비활성화
- 신규 인터페이스는 기본적으로 비활성화 상태로 구성
- 정기적(월 1회 이상) 인터페이스 사용 현황 점검
- 인터페이스 비활성화 이력 문서화
