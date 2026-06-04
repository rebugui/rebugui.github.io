---
title: "[2026 주요정보통신기반시설] N-23 N-23: DDoS 공격 방어 설정 또는 DDoS 장비 사용"
slug: "2026-주정통/N-23"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "DDoS공격방어설정을적용하거나DDoS대응장비를사용하는지점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Network
---

# N-23: DDoS 공격 방어 설정 또는 DDoS 장비 사용

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | N-23 |
| **점검내용** | DDoS공격방어설정을적용하거나DDoS대응장비를사용하는지점검 |
| **점검대상** | Cisco, Juniper등 |
| **판단기준** | 양호: 경계라우터에서DDoS공격방어설정을하거나DDoS대응장비를사용하는경우 |
| **판단기준** | 취약: 경계라우터에서DDoS공격방어설정을하지않거나DDoS대응장비를사용하지않는경우 |
| **조치방법** | DDoS공격방어설정점검 |

---
## 상세 설명

### 개요

DDoS 공격 방어 설정 또는 DDoS 장비 사용 항목은 경계 라우터에 DDoS 공격 방어 설정을 적용하거나 별도의 DDoS 대응 장비를 사용하는지 점검하는 항목입니다. DDoS 공격 발생 시 피해를 최소화하기 위한 대응책을 마련해야 합니다.

### 필요성

**보안 위협**

DDoS 공격 방어 대책이 없을 경우 다음과 같은 피해가 발생할 수 있습니다.

1. **서비스 거부**: 합법적인 사용자의 서비스 이용이 불가능해집니다.

2. **시스템 리소스 고갈**: 네트워크 대역폭, CPU, 메모리 등의 리소스가 소진됩니다.

3. **서버 손상**: 장기간의 공격으로 서버가 손상되거나 충돌할 수 있습니다.

4. **비용 증가**: 트래픽 초과로 발생하는 비용이 급증할 수 있습니다.

**DDoS란?**

Distributed Denial of Service의 약자로, 해커에 의해 감염된 다수의 좀비 PC로부터 다량의 트래픽이 특정 서버로 유입되어 시스템, 네트워크의 가용성을 저해시켜 서비스를 방해하는 공격입니다.

### 점검 방법

#### Cisco IOS 장비

**Step 1) DDoS 방어 설정 요소 확인**

```
Router> enable
Router# show running-config
```

다음 설정 요소를 확인합니다:
- Rate limiting 설정
- TCP Intercept 설정
- ACL 기반 트래픽 필터링

#### Juniper Junos 장비

**Step 1) DDoS 방어 설정 요소 확인**

```
[edit]
user@host# show configuration
```

Firewall filter, CoS (Class of Service) 설정을 확인합니다.

### 조치 방법

#### 공통

**Step 1) DDoS 공격 방어 기법 적용**

스푸핑 방지 필터링(N-22) 등을 제외한 DDoS 공격 방어 설정은 DDoS 공격 발생 시 공격 유형과 상황을 고려하여 적용합니다.

**1. ACL (Access Control List)**

- 스푸핑 방지 필터링을 사전 적용 (N-22)
- DDoS 공격 유형에 따라 공격 대상 IP 주소, 프로토콜, 포트를 임시 차단

**2. Rate Limiting**

특정 유형의 트래픽에 대역폭과 일정 시간 동안 전송량을 제한합니다.

- DDoS 공격 유형에 따라 UDP, ICMP, TCP SYN 패킷의 대역폭을 제한
- 다른 서비스에 필요한 대역폭을 확보

> **주의**: 하드웨어 기반 전용 모듈이 없는 경우 정책 수에 따라 라우터의 CPU 부하가 증가할 수 있습니다.

**3. TCP Intercept**

TCP 연결 요청(SYN)을 대신 수신하여 서버를 보호하는 기능입니다.

#### Cisco IOS - Rate Limiting 설정 예시

```
Router# configure terminal
Router(config)# access-list 101 permit udp any any eq 53
Router(config)# access-list 102 permit icmp any any
Router(config)# access-list 103 permit tcp any any established
```

**Rate Limit 적용**:

```
Router(config)# interface <인터페이스>
Router(config-if)# rate-limit input access-group 101 256000 512000 512000 conform-action transmit exceed-action drop
```

#### Cisco IOS - TCP Intercept 설정 예시

```
Router# configure terminal
Router(config)# ip tcp intercept list 110
Router(config)# access-list 110 permit tcp any <보호할 서버 IP> eq 80
Router(config)# access-list 110 permit tcp any <보호할 서버 IP> eq 443
```

**TCP Intercept 모드 설정**:

```
Router(config)# ip tcp intercept mode intercept
```

### 주의사항

1. **성능 영향**: 필터링 적용 시 사용하는 ACL은 라우터 성능에 많은 영향을 미치므로 주의해야 합니다.

2. **상황에 맞는 대응**: DDoS 공격 유형에 따라 적절한 방어 기법을 선택해야 합니다.

3. **전문 장비 고려**: 대규모 DDoS 공격에 대비하여 별도의 DDoS 방어 장비나 클라우드 기반 DDoS 방어 서비스 사용을 고려해야 합니다.

4. **사전 테스트**: DDoS 방어 설정을 적용하기 전에 테스트 환경에서 검증해야 합니다.

5. **정기적 검토**: 새로운 DDoS 공격 기법에 대응하기 위해 방어 정책을 정기적으로 검토하고 업데이트해야 합니다.

**권장 사항**:
- 경계 라우터: Rate Limiting, TCP Intercept 기본 설정
- 대규모 트래픽: 전용 DDoS 방어 장비 또는 서비스 사용
- 공격 탐지: 네트워크 트래픽 모니터링 시스템 구축
- 대응 절차: DDoS 공격 대응 매뉴얼 수립
