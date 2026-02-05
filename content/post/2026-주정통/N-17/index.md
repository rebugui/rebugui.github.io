---
title: "[2026 주요정보통신기반시설] N-17 N-17: SNMP 서비스 확인"
slug: "2026-주정통/N-17"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "네트워크장비의SNMP서비스를사용하지않는경우비활성화상태인지점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Network
---

# N-17: SNMP 서비스 확인

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | N-17 |
| **점검내용** | 네트워크장비의SNMP서비스를사용하지않는경우비활성화상태인지점검 |
| **점검대상** | Cisco, Alteon, Passport, Juniper, Piolink등 |
| **판단기준** | 양호: 사용하지않는SNMP서비스를비활성화한경우 |
| **판단기준** | 취약: 사용하지않는SNMP서비스를비활성화하지않은경우 |
| **조치방법** | 장비별제공하는최신취약점정보를파악후최신패치및업그레이드를수행 |

---
## 상세 설명

### 개요

SNMP 서비스 확인 항목은 네트워크 장비에서 사용하지 않는 SNMP 서비스가 비활성화되어 있는지 점검하는 항목입니다. 불필요한 SNMP 서비스는 공격자의 진입 경로가 될 수 있으므로 반드시 비활성화해야 합니다.

### 필요성

**보안 위협**

불필요한 SNMP 서비스를 비활성화하지 않을 경우 다음과 같은 위협에 노출됩니다.

1. **설정 파일 열람**: 비인가자가 SNMP를 통해 장비 설정 정보를 열람할 수 있습니다.

2. **설정 수정**: MIB(Management Information Base) 정보를 조작하여 네트워크 설정을 변경할 수 있습니다.

3. **정보 수집**: 네트워크 토폴로지, 장비 정보 등을 수집하여 공격에 활용할 수 있습니다.

4. **관리자 권한 획득**: SNMP 취약점을 악용하여 관리자 권한을 획득할 수 있습니다.

5. **DoS 공격**: SNMP 서비스를 통해 서비스 거부 공격을 수행할 수 있습니다.

**SNMP란?**

- **Simple Network Management Protocol**: TCP/IP 기반 네트워크상의 각 호스트에서 정기적으로 여러 정보를 자동으로 수집하여 네트워크 관리를 하기 위한 프로토콜
- **버전**: v1, v2c, v3 세 가지 버전
  - v1, v2c: 평문 전송 (스니핑 가능)
  - v3: HMAC-MD5 또는 HMAC-SHA 알고리즘 기반의 인증 제공

### 점검 방법

#### Cisco IOS 장비

**Step 1) SNMP 설정 확인**

```
Router> enable
Router# show running-config
```

`snmp-server` 관련 설정을 확인합니다.

**Step 2) SNMP 서비스 동작 확인**

```
Router# show snmp
```

- SNMP 서비스가 활성화: SNMP 정보 출력
- SNMP 서비스가 비활성화: `%SNMP agent not enabled` 메시지

#### Radware Alteon 장비

**Step 1) SNMP 서비스 확인**

```
Main# /cfg/dump
Main# /cfg/sys/access/snmp
```

#### Passport 장비

**Step 1) SNMP 서비스 확인**

SNMP 설정을 확인하고 불필요한 경우 서비스를 중지합니다.

#### Juniper Junos 장비

**Step 1) SNMP 서비스 설정 확인**

```
user@host# show snmp
```

#### Piolink PLOS 장비

**Step 1) SNMP 설정 확인**

```
switch# show running-config
```

### 조치 방법

#### Cisco IOS

**Step 3) SNMP 서비스 비활성화**

```
Router# config terminal
Router(config)# no snmp-server
```

이 명령은 모든 SNMP 서비스를 비활성화합니다.

#### Radware Alteon

**Step 2) SNMP 접근 비활성화**

```
Main# /cfg/sys/access/snmp
```

```
Current SNMP access: disabled
```

#### Juniper Junos

**Step 2) SNMP Community 제거**

```
user@host> configure
[edit]
user@host# delete snmp community public
```

### 주의사항

1. **필요성 확인**: SNMP 서비스를 실제로 사용하지 않는 경우에만 비활성화해야 합니다.

2. **모니터링 영향**: SNMP 기반의 네트워크 모니터링 시스템을 사용하는 경우 비활성화 시 모니터링이 중단됩니다.

3. **SNMPv3 사용 권장**: SNMP 서비스를 사용해야 하는 경우 SNMPv3 사용을 강력히 권장합니다.
   - SNMPv1/v2c: 평문 전송 (취약)
   - SNMPv3: 암호화 및 인증 지원 (권장)

4. **Community String 변경**: N-18(SNMP Community String 복잡성 설정)을 참조하여 Community String을 변경해야 합니다.

5. **ACL 적용**: N-19(SNMP ACL 설정)을 참조하여 SNMP 접근을 제한해야 합니다.

6. **보안 패치**: 최신 취약점 정보를 파악 후 최신 패치 및 업그레이드를 수행해야 합니다.

**권장 사항**:
- 사용하지 않는 경우: SNMP 서비스 비활성화
- 사용해야 하는 경우:
  - SNMPv3 사용 (암호화 및 인증)
  - Community String 복잡성 기준 준수
  - ACL을 통한 접근 제한
  - 최신 펌웨어 유지
