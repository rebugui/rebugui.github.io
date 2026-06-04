---
title: "[2026 주요정보통신기반시설] N-19 N-19: SNMP ACL 설정"
slug: "2026-주정통/N-19"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "SNMP 서비스 사용 시 네트워크 장비 ACL(Access List)을 설정하여 SNMP 접속 대상 호스트를 지정하여접근이가능한IP를제한하였는지점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Network
---

# N-19: SNMP ACL 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | N-19 |
| **점검내용** | SNMP 서비스 사용 시 네트워크 장비 ACL(Access List)을 설정하여 SNMP 접속 대상 호스트를 지정하여접근이가능한IP를제한하였는지점검 |
| **점검대상** | Cisco, Alteon, Passport, Juniper, Piolink등 |
| **판단기준** | 양호: SNMP서비스를비활성화하거나SNMP접근을제한하는ACL을설정한경우 |
| **판단기준** | 취약: SNMP접근을제한하는ACL을설정하지않은경우 |
| **조치방법** | SNMP 접근에대한ACL(Access List)설정 |

---
## 상세 설명

### 개요

SNMP ACL 설정 항목은 SNMP 서비스 사용 시 ACL(Access Control List)을 설정하여 특정 IP 주소에서만 SNMP 접근을 허용하는 항목입니다. 임의의 호스트에서 SNMP 접근을 차단하여 네트워크 정보의 노출을 제한합니다.

### 필요성

**보안 위협**

SNMP ACL을 설정하지 않을 경우 다음과 같은 위협에 노출됩니다.

1. **Community String 추측 공격**: 공격자가 무작위 대입 공격으로 Community String을 추측할 수 있습니다.

2. **MIB 정보 수정**: 라우팅 정보를 변경하거나 네트워크 장비의 설정을 변조할 수 있습니다.

3. **내부망 침투**: 터널링 설정을 통해 내부망에 침투할 수 있습니다.

4. **정보 수집**: 네트워크 토폴로지, 장비 정보 등을 수집하여 추가 공격에 활용할 수 있습니다.

### 점검 방법

#### Cisco IOS 장비

**Step 1) SNMP 설정 확인**

```
Router> enable
Router# show running-config
```

`snmp-server community` 설정에 ACL이 적용되어 있는지 확인합니다.

**Step 2) Access-List 설정 확인**

```
Router# show running-config
```

ACL 번호와 내용을 확인합니다.

### 조치 방법

#### Cisco IOS

**Step 3) Access-List 설정 및 SNMP에 적용**

```
Router# config terminal
```

1. **ACL 생성**:

```
Router(config)# access-list <ACL 번호> permit <IP 주소>
Router(config)# access-list <ACL 번호> deny any log
```

**예시**:

```
Router(config)# access-list 10 permit 192.168.1.100
Router(config)# access-list 10 permit 192.168.2.0 0.0.0.255
Router(config)# access-list 10 deny any log
```

2. **SNMP Community에 ACL 적용**:

```
Router(config)# snmp-server community <Community String> <ACL 번호>
```

**예시**:

```
Router(config)# snmp-server community Snmp@C0mm!2024 10
```

3. **수정이 필요한 경우 기존 설정 삭제 후 재설정**:

```
Router(config)# no snmp-server community public
Router(config)# snmp-server community <새 Community String> <ACL 번호>
```

**완성된 설정 예시**:

```
Router(config)# access-list 10 permit 192.168.1.100
Router(config)# access-list 10 permit 192.168.2.0 0.0.0.255
Router(config)# access-list 10 deny any log
Router(config)# snmp-server community Snmp@C0mm!2024 RO 10
Router(config)# snmp-server community Wr1te@C0mm!2024 RW 10
```

- `RO` (Read-Only): 읽기 전용
- `RW` (Read-Write): 읽기/쓰기

#### 기타 장비

**Radware Alteon / Passport / Juniper / Piolink**

각 장비별로 SNMP 접근 제어 기능을 제공합니다. 장비 매뉴얼을 참조하여 다음과 같은 설정을 적용합니다:

1. 관리 스테이션 IP 주소 등록
2. SNMP 접근 허용 규칙 설정
3. 기타 모든 접근 차단

### 주의사항

1. **최소 권한 원칙**: 읽기 전용(RO)과 읽기/쓰기(RW) Community String을 분리하고, RW 권한은 최소한의 IP만 허용해야 합니다.

2. **ACL 순서**: ACL은 위에서부터 순차적으로 적용되므로, 허용할 IP를 먼저 설정하고 마지막에 `deny any`를 배치해야 합니다.

3. **로그 기록**: `deny any log`와 같이 로그를 남기도록 설정하여 접근 시도를 모니터링해야 합니다.

4. **관리자 IP 확인**: 현재 관리자가 사용하는 IP 주소를 모두 ACL에 포함해야 접속이 차단되지 않습니다.

5. **정기적 검토**: 허용된 IP 목록을 정기적으로 검토하고 불필요한 IP는 제거해야 합니다.

6. **N-18 연계**: SNMP Community String 복잡성 설정과 함께 적용하면 보안 효과가 더욱 강화됩니다.

**권장 설정**:
- 읽기 전용 Community String: 네트워크 관리 스테이션 IP만 허용
- 읽기/쓰기 Community String: 최소한의 신뢰할 수 있는 IP만 허용
- ACL 로그: 모든 거부된 접근 시도 로깅
- 정기적 검토: 월 1회 이상 허용 IP 목록 검토
