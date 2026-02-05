---
title: "[2026 주요정보통신기반시설] N-18 N-18: SNMP Community String 복잡성 설정"
slug: "2026-주정통/N-18"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "SNMP 서비스사용시Community String을 기본설정(public, private)으로사용하고있는지점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Network
---

# N-18: SNMP Community String 복잡성 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | N-18 |
| **점검내용** | SNMP 서비스사용시Community String을 기본설정(public, private)으로사용하고있는지점검 |
| **점검대상** | Cisco, Alteon, Passport, Juniper, Piolink등 |
| **판단기준** | 양호: SNMP 서비스를 비활성화하거나 SNMP Community String을 복잡성 기준(영어 대·소문자, 숫자,특수문자중3종류이상을조합하여8자리이상)에맞게설정한경우 |
| **판단기준** | 취약: SNMP Community String을 기본설정(public, private)으로사용하고있거나,복잡성기준에 맞지않게설정한경우 |
| **조치방법** | public, private 외복잡성기준에맞는CommunityString을설정 ※ SNMP Community String 복잡성 기준: 영어 대·소문자, 숫자, 특수문자 중 3종류 이상을 조합하여8자리이상으로구성 |

---
## 상세 설명

### 개요

SNMP Community String 복잡성 설정 항목은 SNMP 서비스 사용 시 Community String을 기본 설정(public, private)이 아닌 복잡한 값으로 설정하는 항목입니다. Community String은 일종의 비밀번호이므로 강력한 복잡성 기준을 준수해야 합니다.

### 필요성

**보안 위협**

기본 Community String을 사용할 경우 다음과 같은 위협에 노출됩니다.

1. **무단 접근**: 공격자가 쉽게 Community String을 유추하여 SNMP에 무단 접근할 수 있습니다.

2. **정보 노출**: MIB 정보를 통해 네트워크 구성, 장비 정보 등이 노출됩니다.

3. **설정 변경**: 공격자가 네트워크 장비의 설정을 변경하거나 장애를 유발할 수 있습니다.

**Community String 복잡성 기준**

영어 대·소문자, 숫자, 특수문자 중 3종류 이상을 조합하여 8자리 이상으로 구성해야 합니다.

### 점검 방법

#### Cisco IOS 장비

**Step 1) SNMP 설정 확인**

```
Router> enable
Router# show running-config
```

`snmp-server community` 설정을 확인합니다.

기본값 확인:
- `public`: 읽기 전용 기본값
- `private`: 읽기/쓰기 기본값

#### Radware Alteon / Passport 장비

**Step 1) SNMP Community String 설정 확인**

```
Main# /cfg/sys/ssnmp
```

`rcomm`(read community)와 `wcomm`(write community) 설정을 확인합니다.

#### Juniper Junos 장비

**Step 1) SNMP Community String 확인**

```
[edit]
user@host# show
```

`snmp community` 설정을 확인합니다.

#### Piolink PLOS 장비

**Step 1) SNMP Community String 확인**

```
switch# show running-config
```

`snmp community` 설정을 확인합니다.

### 조치 방법

#### Cisco IOS

**Step 2) Community String 변경**

```
Router# config terminal
Router(config)# snmp-server community <Community String>
```

**복잡성 기준을 준수하는 예시**:

```
Router(config)# snmp-server community Snmp@C0mm!2024
```

> **주의**: 기존 Community String을 삭제하려면:
> ```
> Router(config)# no snmp-server community public
> Router(config)# no snmp-server community private
> ```

#### Radware Alteon

**Step 2) Community String 설정**

```
Main# /cfg/sys/ssnmp
```

```
Main# /rcomm - SNMP read community string 설정 (최대 32자, 기본값: public)
Main# /wcomm - SNMP write community string 설정 (최대 32자, 기본값: private)
Main# apply
Main# save
```

#### Passport

**Step 2) Community String 설정**

```
# config snmp-v3 community commname <Comm Idx> new-commname <value>
```

#### Juniper Junos

**Step 2) Community String 설정**

```
[edit]
user@host# set snmp community <Community String> authorization read-only
```

또는

```
user@host# set snmp community <Community String> authorization read-write
```

#### Piolink PLOS

**Step 2) Community String 설정**

```
switch# configure
switch(config)# snmp
switch(config-snmp)# community <Community String>
switch(config-snmp)# status enable
switch(config-snmp)# apply
```

### 주의사항

1. **복잡성 기준 준수**: 영어 대·소문자, 숫자, 특수문자 중 3종류 이상을 조합하여 8자리 이상으로 구성해야 합니다.

2. **기본값 변경**: `public`, `private` 등 기본값은 반드시 변경해야 합니다.

3. **읽기/쓰기 분리**: 읽기 전용(read-only)과 읽기/쓰기(read-write) Community String을 다르게 설정해야 합니다.

4. **정기적 변경**: 주기적으로 Community String을 변경해야 합니다.

5. **N-19 연계**: SNMP ACL 설정과 함께 적용하면 보안 효과가 더욱 강화됩니다.

6. **SNMPv3 사용 권장**: 가능한 경우 SNMPv3를 사용하여 암호화된 통신을 해야 합니다.

**복잡성 기준 충족 예시**:
- `Snmp@C0mm!2024` (영문 대소문자 + 숫자 + 특수문자, 14자리)
- `n3tw0rk#M0n1t0r` (영문 대소문자 + 숫자 + 특수문자, 16자리)
- `Sec!urity@KISA2024` (영문 대소문자 + 숫자 + 특수문자, 17자리)

**불량 예시**:
- `public` (기본값)
- `private` (기본값)
- `password123` (영문 소문자 + 숫자만)
- `admin!` (8자리 미만)
