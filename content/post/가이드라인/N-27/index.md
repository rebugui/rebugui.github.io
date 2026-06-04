---
title: "[2026 주요정보통신기반시설] N-27 N-27: 웹 서비스 차단"
slug: "2026-주정통/N-27"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "웹 서비스를 이용하여 네트워크 장비를 관리할 경우, 웹 서비스를 비활성화하거나 허용된 IP에서만 접속할수있게ACL을적용하였는지점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Network
---

# N-27: 웹 서비스 차단

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | N-27 |
| **점검내용** | 웹 서비스를 이용하여 네트워크 장비를 관리할 경우, 웹 서비스를 비활성화하거나 허용된 IP에서만 접속할수있게ACL을적용하였는지점검 |
| **점검대상** | Cisco등 |
| **판단기준** | 양호: 불필요한웹서비스를차단하거나허용된IP에서만웹서비스관리페이지에접속이가능한경우 |
| **판단기준** | 취약: 불필요한웹서비스를차단하지않은경우 |
| **조치방법** | HTTP서비스차단또는HTTP서버를관리하는관리자접속IP설정 |

---
## 상세 설명

### 개요

웹 서비스 차단 항목은 네트워크 장비의 웹 관리 인터페이스(HTTP/HTTPS)가 불필요하게 활성화되어 있지 않은지, 또는 허용된 IP에서만 접속하도록 ACL이 적용되어 있는지 점검하는 항목입니다.

### 필요성

**보안 위협**

웹 서비스를 적절히 제한하지 않을 경우 다음과 같은 위협에 노출됩니다.

1. **웹 취약점 공격**: SQL Injection, Command Injection 등 알려진 웹 취약점을 통해 장비가 장악될 수 있습니다.

2. **비밀번호 대입 공격**: 자동화된 도구를 통해 비밀번호를 추측하는 공격이 가능합니다.

3. **시스템 무단 변경**: 관리자 권한을 획득하여 시스템 설정을 무단으로 변경할 수 있습니다.

4. **서비스 중단**: 장비 설정을 변경하여 서비스 거부 상태를 유발할 수 있습니다.

### 점검 방법

#### Cisco IOS 장비

**Step 1) 불필요한 웹서비스 확인**

```
Router> enable
Router# show running-config
```

`ip http server`, `ip http secure-server` 설정을 확인합니다.

### 조치 방법

#### Cisco IOS

**Step 2) 불필요한 웹서비스 차단**

```
Router# config terminal
Router(config)# no ip http server
Router(config)# no ip http secure-server
```

**HTTP WEB_EXEC 서비스 비활성화 (HTTP 서비스 사용 시)**:

```
Router(config)# ip http active-session-modules exclude_webexec
Router(config)# ip http secure-active-session-modules exclude_webexec
```

#### Radware Alteon

**Step 2) 불필요한 웹서비스 차단**

```
Main# /cfg/sys/access/https/https dis
Main# /cfg/sys/access/http dis
Main# apply
```

> **참고**: HTTP는 Alteon 29.5 버전부터 지원하지 않습니다.

#### Juniper Junos

**Step 2) 불필요한 웹서비스 차단**

```
[edit]
user@host# delete system services web-management
user@host# commit
```

#### Piolink PLOS

**Step 2) 불필요한 웹서비스 차단**

```
switch# configure
switch(config)# management-access
switch(config-management-access)# http status disable
switch(config-management-access)# https status disable
switch(config)# apply
```

### 주의사항

1. **HTTPS 우선**: 웹 관리 인터페이스를 사용해야 하는 경우 HTTPS만 사용하고 HTTP는 차단해야 합니다.

2. **ACL 적용**: 웹 서비스를 사용해야 하는 경우 반드시 ACL을 적용하여 허용된 IP에서만 접속하도록 설정해야 합니다.

3. **WEB_EXEC 비활성화**: IOS 상의 HTTP 서버를 사용해야 한다면 HTTP WEB_EXEC 서비스를 비활성화하여 위험을 감소시킬 수 있습니다.

**권장 설정**:
- 일반적인 경우: HTTP/HTTPS 서비스 모두 비활성화
- 사용이 필요한 경우: HTTPS만 사용 + ACL 적용 + WEB_EXEC 비활성화
