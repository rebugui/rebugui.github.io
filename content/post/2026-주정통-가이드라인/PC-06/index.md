---
title: "[2026 주요정보통신기반시설] PC-06 비인가 상용 메신저 사용 금지"
slug: "2026-주정통/PC-06"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "사용자PC에서상용메신저사용여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - PC
draft: true
---

# 비인가 상용 메신저 사용 금지

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | PC-06 |
| **점검내용** | 사용자PC에서상용메신저사용여부점검 |
| **점검대상** | Windows 10, Windows 11 |
| **양호기준** | WindowsMessenger가실행중지된상태이거나상용메신저가설치되지않은경우 |
| **취약기준** | WindowsMessenger가실행중이거나상용메신저가설치된경우 |
| **조치방법** | 'WindowsMessenger를실행하지않음'설정및상용메신저삭제 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: Windows Messenger가 실행 중지된 상태이거나 상용 메신저가 설치되지 않은 경우
- **취약**: Windows Messenger가 실행 중이거나 상용 메신저가 설치된 경우

#### 경계 케이스 (Edge Case) 처리 방법
- **업무용으로 승인된 메신저**: 예외 처리 필요
- **메신저가 설치되어 있지만 실행 중이 아닌 경우**: 여전히 취약 판단 (제거 권장)
- **Windows Messenger 기능만 비활성화된 경우**: 양호로 판단

#### 권장 설정값
- **Windows Messenger**: 실행하지 않음
- **상용 메신저**: 설치되지 않음 또는 제거

### 2. 점검 방법

#### Windows 10, 11에서의 점검

**설치된 메신저 프로그램 확인:**
```
Step 1) 시작 > 설정 > 앱 > 설치된 앱
Step 2) 설치된 앱 목록에서 메신저 관련 프로그램 검색
```

**PowerShell 확인:**
```powershell
# 설치된 앱 목록에서 메신저 확인
Get-AppxPackage | Where-Object {$_.Name -match "Messaging|Kakao|Nateon|Skype"} | Select-Object Name, Version

# 레지스트리에서 설치된 프로그램 확인
Get-ItemProperty -Path "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*" | Where-Object {$_.DisplayName -match "Messenger|Kakao|Nateon|Skype"} | Select-Object DisplayName, DisplayVersion, InstallLocation
```

### 3. 조치 방법

#### 1. Windows Messenger 실행 제한

**그룹 정책 편집기 설정 (Windows Pro/Enterprise):**
```
Step 1) 시작 > 실행 > 'gpedit.msc' 입력
Step 2) 컴퓨터 구성 > 관리 템플릿 > Windows 구성 요소 > Windows Messenger
Step 3) 'Windows Messenger를 실행 허용 안 함' 설정을 '사용'으로 설정
Step 4) 적용 > 확인
```

**레지스트리 설정:**
```cmd
reg add "HKLM\SOFTWARE\Policies\Microsoft\Messenger\Client" /v PreventRun /t REG_DWORD /d 1 /f
```

**PowerShell:**
```powershell
# 관리자 권한 PowerShell 실행
Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Messenger\Client" -Name "PreventRun" -Value 1 -Type DWord
```

#### 2. 상용 메신저 프로그램 제거

**GUI 제거:**
```
Step 1) 시작 > 설정 > 앱 > 설치된 앱
Step 2) 제거할 메신저 프로그램 검색
Step 3) 프로그램 선택 > 제거 클릭
```

**PowerShell 제거:**
```powershell
# Appx 패키지 제거 (Windows Store 앱)
Get-AppxPackage "*Messaging*" | Remove-AppxPackage

# 레지스트리 정보를 이용한 프로그램 제거 (일반 프로그램)
# 프로그램의 UninstallString 확인 후 실행
$uninstallString = (Get-ItemProperty -Path "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*\*" | Where-Object {$_.DisplayName -like "*Messenger*"}).UninstallString
if ($uninstallString) {
    Invoke-Expression $uninstallString
}
```

### 4. 참고 자료

#### 비인가 상용 메신저의 보안 위협

**보안 위협:**
- **정보 유출**: 메신저를 통해 파일을 전송하거나 대화 내용을 공유할 때 중요한 정보가 외부로 유출
- **악성코드 유입 차단**: 메신저를 통해 전달되는 파일이나 링크는 악성코드의 주요 전파 경로
- **계정 탈취**: 메신저 계정이 탈취되면 개인 대화 내용이 노출되거나 피싱 공격에 악용

**대상 메신저 프로그램:**
- 네이트온
- 카카오톡 PC 버전
- Skype
- Windows Messenger
- 기타 업무 외 용도의 메신저

**대안:**
- 업무용으로 승인된 메신저 사용
- 기업용 협업 도구 (Microsoft Teams, Slack 등)
- 보안이 검증된 사내 메신저

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.