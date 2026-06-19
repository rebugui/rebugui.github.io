---
title: "[2026 주요정보통신기반시설] W-54 DoS 공격 방어 레지스트리 설정"
slug: "2026-주정통/W-54"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "DoS공격방어레지스트리설정여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Windows
draft: true
---

# W-54 DoS 공격 방어 레지스트리 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | W-54 |
| **점검내용** | DoS공격방어레지스트리설정여부점검 |
| **점검대상** | Windows NT, 2000, 2003, 2008, 2012, 2016, 2019, 2022 |
| **판단기준** | 양호: 아래4가지DoS방어레지스트리를설정한경우 Ÿ SynAttackProtect→1이상 Ÿ EnableDeadGWDetect→0 Ÿ KeepAliveTime →300,000 Ÿ NoNameReleaseOnDemand→1 |
| **판단기준** | 취약: DoS방어레지스트리값이설정되어있지않은경우 |
| **조치방법** | 레지스트리값을추가또는수정 |

---
## 상세 설명

### 1. 항목 개요

이 항목은 **TCP/IP 스택**의 레지스트리 설정을 조정하여, **DoS(Denial of Service, 서비스 거부)** 공격, 특히 **Syn Flood** 공격과 같은 네트워크 부하 공격에 대한 내성을 강화하는지 점검합니다.

### 2. 왜 이 항목이 필요한가요?

**가용성 확보 및 네트워크 공격 방어**
- **Syn Flood 방어**: 공격자가 연결 요청(SYN)만 보내고 응답(ACK)을 하지 않아 서버의 대기 큐(Backlog)를 가득 채우는 공격을 막기 위해, 연결 대기 시간을 줄이거나 임계치를 초과하면 빠른 처리를 하도록 설정합니다.
- **Dead Gateway 탐지 방지**: 공격자가 게이트웨이를 위장하여 트래픽을 가로채는 것을 막습니다.

**보안 위협 시나리오**
1. 공격자가 좀비 PC를 이용해 서버 80포트로 무수히 많은 SYN 패킷 전송
2. 서버는 SYN_RECEIVED 상태로 연결을 대기하느라 리소스 소진
3. 정상 사용자의 접속 요청을 처리하지 못해 서비스 마비

### 3. 점검 대상

- Windows NT, 2000, 2003, 2008, 2012, 2016, 2019, 2022 서버

### 4. 판단 기준

| 구분 | 기준 |
|------|------|
| **양호** | 아래 4가지 보안 설정 값이 적절하게 적용된 경우 |
| **취약** | 해당 레지스트리 값이 없거나, 권장 값으로 설정되지 않은 경우 |

**<주요 점검 항목 및 권장 값>**
1. **SynAttackProtect**: `1` 이상 (SYN 공격 방어 활성화)
2. **EnableDeadGWDetect**: `0` (죽은 게이트웨이 탐지 비활성화)
3. **KeepAliveTime**: `300,000` (5분, 세션 유지 확인 시간 단축)
4. **NoNameReleaseOnDemand**: `1` (NetBIOS 이름 해제 요청 거부)

### 5. 점검 방법

#### 방법 1: 레지스트리 편집기 확인
```
1. 시작 > 실행 > regedit
2. 경로: HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters
3. 우측 패널에서 위 4가지 항목(DWORD)의 값 확인
```

### 6. 조치 방법

레지스트리 값을 생성하거나 수정하여 공격 방어 기능을 활성화합니다.

#### 방법 1: 레지스트리 편집기 사용
경로: `HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters`

| 값 이름 (DWORD) | 권장 값 | 설명 |
|---|---|---|
| **SynAttackProtect** | **1** (또는 2) | 1: 재전송 횟수 줄임, 2: 지연된 소켓 할당(더 강력) |
| **EnableDeadGWDetect** | **0** | 게이트웨이 변경 공격 방지 |
| **KeepAliveTime** | **300000** | 300,000ms = 5분 (기본값 2시간은 너무 김) |
| **NoNameReleaseOnDemand** | **1** | 악의적인 이름 해제 요청 방어 |

*참고: Windows Server 2003 SP1 이후부터는 `SynAttackProtect`가 기본적으로 작동하도록 커널이 개선되었으나, 명시적으로 설정하는 것이 권장됩니다.*

### 7. 조치 시 주의사항

| 주의사항 | 설명 |
|----------|------|
| **애플리케이션 영향** | `KeepAliveTime`을 너무 짧게 줄이면, 정상적인 장기 유휴 세션(예: DB 연결)이 끊길 수 있습니다. 환경에 맞춰 조정하세요. |
| **레지스트리 백업** | 레지스트리 수정 전 반드시 백업(내보내기)을 수행해야 합니다. 잘못된 설정은 네트워크 통신 장애를 유발할 수 있습니다. |

### 8. 참고 자료

- [Microsoft Docs: TCP/IP & NBT configuration parameters for Windows XP/2003](https://docs.microsoft.com/en-us/troubleshoot/windows-client/networking/tcpip-and-nbt-configuration-parameters)

---

## 요약

**W-54 DoS공격방어레지스트리설정**은 Windows의 기초 체력을 키우는 작업입니다. 네트워크 홍수(Flood)가 밀려와도 쉽게 쓰러지지 않도록 TCP/IP 파라미터를 튜닝하세요.
