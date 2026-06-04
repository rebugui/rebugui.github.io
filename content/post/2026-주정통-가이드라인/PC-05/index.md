---
title: "[2026 주요정보통신기반시설] PC-05 불필요한 서비스 제거"
slug: "2026-주정통/PC-05"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "사용하지앓는서비스나기본으로설치되어실행되고있는서비스여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - PC
---

# 불필요한 서비스 제거

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | PC-05 |
| **점검내용** | 사용하지앓는서비스나기본으로설치되어실행되고있는서비스여부점검 |
| **점검대상** | Windows 10, Windows 11 |
| **양호기준** | 일반적으로불필요한서비스(아래목록참조)가중지된경우 |
| **취약기준** | 일반적으로불필요한서비스(아래목록참조)가중지되지않은경우 |
| **조치방법** | 불필요한서비스중지설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 일반적으로 불필요한 서비스가 중지된 경우
- **취약**: 일반적으로 불필요한 서비스가 중지되지 않은 경우

#### 경계 케이스 (Edge Case) 처리 방법
- **시작 유형이 '수동'인 경우**: 서비스가 실행 중이지 않으면 양호로 판단
- **시작 유형이 '자동'이지만 서비스가 중지된 경우**: 재부팅 시 자동으로 시작되므로 취약 판단
- **특정 서비스가 필요한 환경**: 예외 목록 관리 필요

#### 권장 설정값
- **불필요한 서비스 시작 유형**: 사용 안 함 (Disabled)

### 2. 점검 방법

#### Windows 10, 11에서의 점검

**GUI 확인:**
```
Step 1) 시작 > 모든 앱 > Windows Tools > 서비스
또는
Step 1) 시작 > 실행 > 'services.msc' 입력
Step 2) 서비스 목록에서 불필요한 서비스 확인
Step 3) 해당 서비스 선택 > 속성
Step 4) 시작 유형 및 서비스 상태 확인
```

**PowerShell 확인:**
```powershell
# 서비스 상태 확인
Get-Service | Where-Object {$_.DisplayName -match "Alerter|Clipbook|Messenger"} | Select-Object Name, DisplayName, Status, StartType

# 특정 서비스 확인
Get-WmiObject -Class Win32_Service | Where-Object {$_.StartMode -eq "Auto"} | Select-Object Name, DisplayName, State, StartMode
```

### 3. 조치 방법

#### 1. GUI를 통한 서비스 중지

```
Step 1) 서비스 목록에서 해당 서비스 선택
Step 2) 우클릭 > 속성 또는 더블클릭
Step 3) 서비스 중지 버튼 클릭
Step 4) 시작 유형 > '사용 안 함' 선택
Step 5) 확인 클릭
```

#### 2. PowerShell을 통한 서비스 중지

```powershell
# 관리자 권한 PowerShell 실행

# 서비스 중지
Stop-Service -Name "서비스명" -Force

# 시작 유형을 사용 안 함으로 변경
Set-Service -Name "서비스명" -StartupType Disabled

# 예: Remote Registry 서비스 중지
Stop-Service -Name "RemoteRegistry" -Force
Set-Service -Name "RemoteRegistry" -StartupType Disabled
```

#### 3. sc.exe 명령어를 통한 서비스 중지

```cmd
REM 관리자 권한 명령 프롬프트

REM 서비스 중지
sc stop "서비스명"

REM 시작 유형 변경 (사용 안 함: disabled)
sc config "서비스명" start= disabled

REM 예: Remote Registry 서비스 중지
sc stop "RemoteRegistry"
sc config "RemoteRegistry" start= disabled
```

### 4. 참고 자료

#### 일반적으로 불필요한 서비스 목록

| 서비스명 | 기능 및 설명 |
|---------|-------------|
| **Alerter** | 네트워크상에서 사용자와 컴퓨터에 관리용 경고 메시지를 전송 |
| **Automatic Updates** | 중요한 윈도우 업데이트를 다운로드하고 설치 (수동 패치 적용 시 불필요) |
| **Clipbook** | 서버 내 Clipbook을 다른 클라이언트와 공유 |
| **Computer Browser** | 네트워크에 있는 모든 컴퓨터의 목록을 업데이트하고 관리 |
| **DHCP Client** | IP 주소를 DHCP 서버로부터 동적으로 획득 (고정 IP 사용 시 불필요) |
| **Distributed Link Tracking Client** | NTFS 파일 간의 연결을 관리 (Active Directory 미구성 시 불필요) |
| **Messenger** | 클라이언트와 서버 사이에 netsend 및 경고 서비스 메시지 전송 |
| **Remote Registry** | 원격 사용자가 레지스트리 설정 수정 |
| **Simple TCP/IP Services** | Echo, Discard, Character Gen 등의 네트워크 서비스 |

**보안 위협:**
- **시스템 자원 낭비**: 불필요한 서비스가 CPU, 메모리, 디스크 I/O를 소모
- **공격 표면 증가**: 실행 중인 서비스가 많을수록 취약점이 늘어남
- **포트 기반 공격**: 불필요한 서비스가 열어둔 포트를 통해 침입 가능

**주의사항:**
- 테스트 환경에서 먼저 적용 후 운영 환경에 적용
- 서비스 사용 여부를 신중하게 평가
- Microsoft 가이드에 따라 전략적으로 적용

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.