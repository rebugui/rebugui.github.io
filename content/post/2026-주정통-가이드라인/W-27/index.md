---
title: "[2026 주요정보통신기반시설] W-27 최신 Windows OS Build 버전 적용"
slug: "2026-주정통/W-27"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "최신 Build 적용 여부 점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Windows
draft: true
---

# W-27 최신 Windows OS Build 버전 적용

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | W-27 |
| **점검내용** | 최신 Build 적용 여부 점검 |
| **점검대상** | Windows NT, 2000, 2003, 2008, 2012, 2016, 2019, 2022 |
| **양호기준** | 최신 Build가 설치되어 있으며 적용 절차 및 방법이 수립된 경우 |
| **취약기준** | 최신 Build가 설치되지 않거나, 적용 절차 및 방법이 수립되지 않은 경우 |
| **조치방법** | 설치에 따른 영향도 확인 후 최신 Build 설치(설치 후 시스템 재시작 필요) |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 최신 서비스 팩 및 보안 업데이트가 적용되어 있고, 패치 관리 절차가 수립된 경우
- **취약**: 보안 업데이트가 누락되어 있거나, 패치 관리 체계가 없는 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| 최신 Cumulative Update 설치됨 | 양호 | 최신 보안 패치 적용 상태 |
| 1개월 이내 업데이트 | 양호 | 일반적으로 허용 가능한 범위 |
| 3개월 이상 업데이트 누락 | 취약 | 보안 위험 상태 |
| 지원 종료(OS EOS) 운영 중 | 취약 | 보안 패치 제공 중단 |
| WSUS를 통한 업데이트 | 양호 | 중앙 관리 체계 있음 |
| 수동 업데이트만 수행 | 주의 | 자동화 권장 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| Windows Update | 자동 업데이트 | 자동(재부팅 알림) | 인터넷 연결 환경 |
| WSUS | 업데이트 소스 | WSUS 서버 | 기업 환경 |
| 업데이트 주기 | 검사 주기 | 매일 | 자동 검사 설정 |
| 재부팅 | 자동 재부팅 | 사용 안 함(알림만) | 서비스 장애 방지 |
| 패치 관리 | 절차서 | 보유 | 테스트-운영 프로세스 |

### 2. 점검 방법

#### Windows 서버 점검

운영체제의 최신 보안 패치 적용 여부를 확인하여 알려진 취약점으로부터 시스템을 보호해야 합니다.

```cmd
# 시스템 정보 및 핫픽스 확인
systeminfo | findstr /B /C:"OS" /C:"Hotfix"
```

**양호 출력 예시:**
```text
OS Name:                   Microsoft Windows Server 2019 Standard
OS Version:                10.0.17763 N/A Build 17763
OS Configuration:          Standalone Server
Hotfix(s):                 10 Hotfix(s) Installed.
                            [01]: KB5034441
                            [02]: KB5034439
                            ...
```

**취약 출력 예시:**
```text
Hotfix(s):                 N/A
또는
오래된 KB 번호들만 존재 (최근 3개월 내 패치 없음)
```

```powershell
# PowerShell로 최근 업데이트 확인
Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 10 | Format-Table HotFixID, InstalledOn, Description
```

```powershell
# Windows 업데이트 설정 확인
Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update" -Name "AUOptions" -ErrorAction SilentlyContinue
```

```cmd
# OS 버전 및 빌드 번호 확인
ver
```

### 3. 조치 방법

#### Windows 서버 설정

1. **Windows Update 실행 (인터넷 연결 시)**
   ```
   1. 시작 > 설정 > 업데이트 및 보안 > Windows 업데이트
   2. [업데이트 확인] 클릭
   3. 검색된 중요/보안 업데이트 설치
   4. 필요시 시스템 재부팅
   ```

2. **PowerShell로 업데이트 설치**
   ```powershell
   # PSWindowsUpdate 모듈 설치 (필요시)
   Install-Module -Name PSWindowsUpdate -Force

   # 업데이트 검색 및 설치
   Get-WindowsUpdate -AcceptAll -Install -AutoReboot
   ```

3. **특정 업데이트 수동 설치**
   ```cmd
   # Microsoft Update Catalog에서 다운로드한 MSU 파일 설치
   wusa.exe "C:\Updates\Windows10.0-KB5034441-x64.msu" /quiet /norestart
   ```

4. **WSUS 구성 (기업 환경)**
   ```powershell
   # WSUS 서버 지정
   Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate" -Name "WUServer" -Value "http://wsus-server:8530"
   Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate" -Name "WUStatusServer" -Value "http://wsus-server:8530"

   # 자동 업데이트 설정
   Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU" -Name "UseWUServer" -Value 1
   ```

5. **업데이트 자동 설치 설정**
   ```powershell
   # 자동 업데이트 구성 (4 = 자동 다운로드 및 설치)
   Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update" -Name "AUOptions" -Value 4 -Type DWord

   # 매일 업데이트 검사
   Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update" -Name "ScheduledInstallDay" -Value 0
   Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update" -Name "ScheduledInstallTime" -Value 3
   ```

6. **서비스 재시작**
   ```powershell
   # Windows Update 서비스 재시작
   Restart-Service -Name wuauserv
   ```

### 4. 참고 자료

- [Microsoft Security Response Center](https://msrc.microsoft.com/update-guide/)
- [KISA 보안공지](https://www.krcert.or.kr/data/secNoticeList.do)
- [Microsoft Docs: Windows Update for Business](https://docs.microsoft.com/ko-kr/windows/deployment/update/waas-manage-updates-wfb)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.