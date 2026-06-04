---
title: "[2026 주요정보통신기반시설] N-36 N-36: Domain Lookup 차단"
slug: "2026-주정통/N-36"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "Domain Lookup을차단하는지점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Network
---

# N-36: Domain Lookup 차단

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | N-36 |
| **점검내용** | Domain Lookup을차단하는지점검 |
| **점검대상** | Cisco등 |
| **판단기준** | 양호: Domain Lookup을차단하는경우 |
| **판단기준** | 취약: DomainLookup을차단하지않은경우 |
| **조치방법** | Domain Lookup비활성화 |

---
## 상세 설명

### 개요

Domain Lookup 차단 항목은 명령어를 잘못 입력할 때 발생하는 불필요한 Domain Lookup을 차단하는 항목입니다.

### 필요성

**보안 위협**

불필요한 DNS broadcast traffic이 발생하고 사용자 대기 시간이 발생합니다.

**Domain Lookup이란?**

Cisco 장비는 Privileged Exec 모드에서 명령어가 아닌 문자열을 입력하면 호스트 이름으로 간주하고 Domain Lookup을 시도합니다. DNS를 설정하지 않은 경우 DNS Broadcast Query를 수행하며, 1분여간 사용자 입력을 받지 않습니다.

### 점검 및 조치 방법

#### Cisco IOS

**점검**: `no ip domain-lookup` 설정 확인

```
Router# show running-config
```

**조치**: Global Configuration 모드에서 비활성화

```
Router# config terminal
Router(config)# no ip domain lookup
```

또는

```
Router(config)# no ip domain-lookup
```

> **참고**: IOS 12.2 버전부터 `ip domain-lookup`을 `ip domain lookup`으로 변경하며 두 명령어 모두 지원합니다.

**권장 설정**:
- Domain Lookup 비활성화 권장
