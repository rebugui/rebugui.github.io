---
title: "[2026 주요정보통신기반시설] N-20 N-20: SNMP Community 권한 설정"
slug: "2026-주정통/N-20"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "SNMPCommunity에필요하지않은쓰기권한을허용하는지점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Network
---

# N-20: SNMP Community 권한 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | N-20 |
| **점검내용** | SNMPCommunity에필요하지않은쓰기권한을허용하는지점검 |
| **점검대상** | Cisco, Alteon, Passport, Juniper, Piolink등 |
| **판단기준** | 양호: SNMP커뮤니티권한이읽기전용(RO)인경우 |
| **판단기준** | 취약: SNMP커뮤니티권한이불필요하게읽기쓰기(RW)인경우 |
| **조치방법** | SNMP Community String권한설정(RW권한삭제권고) |

---
## 상세 설명

### 개요

SNMP Community 권한 설정 항목은 SNMP Community에 불필요한 쓰기(RW) 권한이 부여되어 있는지 점검하는 항목입니다. 일반적으로 모니터링 목적으로는 읽기 전용(RO) 권한만으로 충분하며, 불필요한 RW 권한을 제거해야 합니다.

### 필요성

**보안 위협**

불필요하게 RW 권한이 설정된 경우 다음과 같은 위협에 노출됩니다.

1. **설정 정보 변경**: 공격자가 Community String을 탈취하면 SNMP를 통해 네트워크 설정 정보를 변경할 수 있습니다.

2. **내부망 침투**: 라우팅 테이블 수정이나 터널링 설정을 통해 내부망에 침투할 수 있습니다.

3. **서비스 거부**: 네트워크 장비 설정을 변경하여 서비스 거부 상태를 유발할 수 있습니다.

**SNMP Community 권한 종류**

- **RO (Read Only)**: 네트워크 설정값에 대한 열람만 가능
- **RW (Read Write)**: 열람 및 수정 가능

### 점검 방법

#### Cisco IOS 장비

**Step 1) SNMP 설정 확인**

```
Router> enable
Router# show running-config
```

`snmp-server community` 설정에서 RO/RW 권한을 확인합니다.

```
Router(config)# snmp-server community <String> RO
Router(config)# snmp-server community <String> RW
```

#### Passport 장비

**Step 1) SNMP community 권한 확인**

```
# config snmp
```

#### Radware Alteon 장비

**Step 1) SNMP access 확인**

```
Main# /cfg/sys/access/snmp
```

```
Current SNMP access: read-write
```

#### Juniper Junos 장비

**Step 1) SNMP community 권한 확인**

```
[edit]
user@host# show
```

```
snmp {
    community <Community> {
        authorization read-only;
    }
}
```

#### Piolink PLOS 장비

**Step 1) SNMP policy 확인**

```
switch# configure
switch(config)# snmp
switch(config-snmp)# show policy
```

### 조치 방법

#### Cisco IOS

**Step 2) SNMP Community String 권한 설정 (RW 권한 삭제 권고)**

```
Router# config terminal
```

**읽기 전용 권한 설정**:

```
Router(config)# snmp-server community <String> RO
```

**읽기/쓰기 권한 설정 (필요한 경우에만)**:

```
Router(config)# snmp-server community <String> RW
```

> **권장**: 일반적으로 RO 권한만으로 충분하며, RW 권한은 삭제하는 것을 권고합니다.

#### Passport

**Step 2) SNMP Community String 권한 설정**

```
# config snmp-v3 community create <Comm Idx> <name> <security> [tag <value>]
# config snmp-v3 group-member create <user name> <model> [<group name>]
# config snmp-v3 group-access create <group name> <prefix> <model> <level>
# config snmp-v3 group-access view <group name> <prefix> <model> <level> [read <value>] [write <value>] [notify <value>]
```

#### Radware Alteon

**Step 2) SNMP access 설정 변경**

```
Main# /cfg/sys/access/snmp
```

```
Current SNMP access: read-write
Enter new SNMP access (disabled/read-only/read-write) [d/r/w]: r
Main# apply
Main# save
```

- `d`: disabled (비활성화)
- `r`: read-only (읽기 전용)
- `w`: read-write (읽기/쓰기)

#### Juniper Junos

**Step 2-4) SNMP Community 권한 설정**

**읽기 쓰기 권한을 설정한 SNMP Community 삭제**:

```
[edit snmp]
user@host# delete community <Community>
```

**읽기 전용 권한으로 SNMP Community 설정**:

```
[edit snmp]
user@host# set community <Community> authorization read-only
```

**SNMPv3는 SNMP 그룹에 읽기 쓰기 권한 제거**:

```
[edit snmp v3 vacm access]
user@host# delete group <그룹> default-context-prefix security-model <보안모델> security-level <보안 레벨> write-view
```

#### Piolink PLOS

**Step 2) SNMP policy 설정**

```
switch# configure
switch(config)# snmp
switch(config-snmp)# policy read-only
switch(config-snmp)# apply
```

### 주의사항

1. **최소 권한 원칙**: 일반적으로 RO 권한만으로 충분하므로, 불필요한 RW 권한은 삭제해야 합니다.

2. **RW 권한 필요 시**: 네트워크 관리 도구에서 설정 변경이 필요한 경우에만 RW 권한을 부여하고, 반드시 ACL과 함께 사용해야 합니다.

3. **RO/RW 분리**: 모니터링용 Community String은 RO로, 설정 변경용은 RW로 분리하고 각각 다른 Community String을 사용해야 합니다.

4. **N-19 연계**: SNMP ACL 설정과 함께 적용하여 RW 권한이 있는 Community String의 접근을 특정 IP로 제한해야 합니다.

5. **정기적 검토**: RW 권한이 필요한지 정기적으로 검토하고 불필요한 경우 제거해야 합니다.

**권장 설정**:
- 모니터링: RO 권한 + ACL
- 설정 변경: RW 권한 + ACL (최소한의 IP만 허용)
- Community String: RO와 RW에 다른 값 사용
