---
title: "[2026 주요정보통신기반시설] W-44 원격으로 액세스할 수 있는 레지스트리 경로"
slug: "2026-주정통/W-44"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "원격레지스트리서비스사용여부점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Windows
---

# W-44 원격으로 액세스할 수 있는 레지스트리 경로

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | W-44 |
| **점검내용** | 원격레지스트리서비스사용여부점검 |
| **점검대상** | Windows NT, 2000, 2003, 2008, 2012, 2016, 2019, 2022 |
| **판단기준** | 양호: Remote Registry Service가중지된경우 |
| **판단기준** | 취약: Remote Registry Service가사용중인경우 |
| **조치방법** | 불필요시서비스중지및사용안함으로설정 |

---
## 상세 설명

### 1. 항목 개요

이 항목은 **Remote Registry(원격 레지스트리)** 서비스가 활성화되어 있는지 점검합니다. 이 서비스는 원격 시스템에서 레지스트리를 조회하거나 수정할 수 있게 해주지만, 보안상 매우 위험한 통로가 될 수 있습니다.

### 2. 왜 이 항목이 필요한가요?

**원격 제어의 양면성**
- **편의성**: 관리자가 일일이 서버에 RDP로 접속하지 않고도 레지스트리 설정을 변경할 수 있어 편리합니다.
- **위험성**: 공격자도 동일한 경로를 통해 레지스트리를 조작하여 악성 프로그램을 시작 프로그램에 등록하거나, 보안 설정을 무력화할 수 있습니다.

**보안 위협 시나리오**
1. 공격자가 취약한 계정 정보를 획득
2. Remote Registry 서비스가 켜진 서버에 접속
3. `HKLM\Software\Microsoft\Windows\CurrentVersion\Run` 키에 악성코드 경로 등록
4. 서버 재부팅 시 악성코드 자동 실행

### 3. 점검 대상

- Windows NT, 2000, 2003, 2008, 2012, 2016, 2019, 2022 서버

### 4. 판단 기준

| 구분 | 기준 |
|------|------|
| **양호** | Remote Registry 서비스가 '중지' 되어 있고, 시작 유형이 '사용 안 함'인 경우 |
| **취약** | Remote Registry 서비스가 '실행 중' 이거나, 시작 유형이 '자동'인 경우 |

### 5. 점검 방법

#### 방법 1: 서비스 관리자 확인
```
1. 시작 > 실행 > services.msc
2. "Remote Registry" 서비스 찾기
3. 상태(Status) 및 시작 유형(Startup Type) 확인
```

#### 방법 2: 명령줄 확인
```powershell
Get-Service RemoteRegistry | Select-Object Name, Status, StartType
```

### 6. 조치 방법

불필요한 경우 서비스를 중지하고 비활성화합니다.

#### 방법 1: 서비스 비활성화 (권장)
```
1. 시작 > 실행 > services.msc
2. "Remote Registry" 서비스 더블클릭
3. 시작 유형: **[사용 안 함]** 선택
4. 서비스 상태: **[중지]** 클릭
5. 확인
```

#### 방법 2: PowerShell 사용
```powershell
Set-Service -Name RemoteRegistry -StartupType Disabled -Status Stopped
```

### 7. 조치 시 주의사항

| 주의사항 | 설명 |
|----------|------|
| **중앙 관리 도구** | SCCM(System Center Configuration Manager)이나 일부 자산 관리 솔루션, 취약점 진단 스캐너가 이 서비스를 사용하여 정보를 수집할 수 있습니다. 이 경우 서비스를 활성화하되, 방화벽(TCP 445 등)으로 접근 가능한 IP를 엄격히 제한해야 합니다. |
| **Active Directory** | 도메인 컨트롤러나 AD 관련 작업에서는 일부 필요할 수 있으나, 일반적으로는 보안을 위해 끄는 것이 권장됩니다. |

### 8. 참고 자료

- [Microsoft Docs: Remote Registry Service](https://docs.microsoft.com/en-us/windows/win32/sysinfo/remote-registry-service)

---

## 요약

**W-44 원격으로액세스할수있는레지스트리경로**는 원격에서 내 심장부(레지스트리)를 건드리지 못하게 차단하는 설정입니다. 특별한 관리 도구를 쓰지 않는다면 꺼두는 것이 안전합니다.
