---
title: "[2026 주요정보통신기반시설] PC-04 공유 폴더 제거"
slug: "2026-주정통/PC-04"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "기본 공유 폴더(C$, D$, Admin$), 미사용 공유 폴더가 존재하는지 점검하고 공유 폴더를 사용하는 경우 공유폴더접근권한에'Everyone'이존재하거나접근을위한비밀번호설정여부점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - PC
---

# 공유 폴더 제거

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | PC-04 |
| **점검내용** | 기본 공유 폴더(C$, D$, Admin$), 미사용 공유 폴더가 존재하는지 점검하고 공유 폴더를 사용하는 경우 공유폴더접근권한에'Everyone'이존재하거나접근을위한비밀번호설정여부점검 |
| **점검대상** | Windows 10, Windows 11 |
| **양호기준** | 불필요한공유폴더가존재하지않거나공유폴더에접근권한및비밀번호가설정된경우 |
| **취약기준** | 불필요한공유폴더가존재하거나접근권한및비밀번호설정없이공유폴더가사용된경우 |
| **조치방법** | 공유폴더불필요시삭제, 공유폴더필요하면적절한접근권한부여및비밀번호설정, 조치후'AutoShareWks'값변경으로자동공유방지 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 불필요한 공유 폴더가 존재하지 않거나 공유 폴더에 접근 권한 및 비밀번호가 설정된 경우
- **취약**: 불필요한 공유 폴더가 존재하거나 접근 권한 및 비밀번호 설정 없이 공유 폴더가 사용된 경우

#### 경계 케이스 (Edge Case) 처리 방법
- **기본 공유(C$, D$, Admin$)가 존재하지만 AutoShareWks=0인 경우**: 재부팅 시 다시 생성되므로 취약 판단
- **Everyone 권한이 존재하지만 읽기 전용인 경우**: 여전히 취약 판단
- **숨김 공유 폴더($结尾)**: 목록에 표시되지 않으므로 별도 점검 필요

#### 권장 설정값
- **기본 공유 폴더(C$, D$, Admin$)**: 제거
- **AutoShareWks 레지스트리 값**: 0 (자동 공유 방지)
- **일반 공유 폴더의 Everyone 권한**: 제거
- **접근 권한**: 인가된 사용자에게만 적절한 권한 부여
- **비밀번호 설정**: 필수

### 2. 점검 방법

#### Windows 10, 11에서의 점검

**공유 폴더 확인:**
```
Step 1) 시작 > 모든 앱 > Windows Tools > 컴퓨터 관리
Step 2) 공유 폴더 > 공유
또는
Step 1) 시작 > 실행 > 'fsmgmt.msc' 입력
```

**PowerShell 확인:**
```powershell
# 모든 공유 폴더 확인
Get-SmbShare

# 기본 공유 폴더 확인
Get-SmbShare | Where-Object {$_.Name -match '\$$'}

# Everyone 권한 확인
Get-SmbShare | ForEach-Object {
    $share = $_
    Get-SmbShareAccess -Name $share.Name | Where-Object {$_.AccountName -eq 'Everyone'} | Select-Object @{N='ShareName';E={$share.Name}}, AccountName, AccessRight
}
```

### 3. 조치 방법

#### 1. 기본 공유 폴더 제거

**GUI 제거:**
```
Step 1) 컴퓨터 관리 > 공유 폴더 > 공유
Step 2) 해당 공유 폴더 우클릭 > 공유 중지
```

**PowerShell 제거:**
```powershell
# 관리자 권한 PowerShell 실행
Remove-SmbShare -Name "C$" -Force
Remove-SmbShare -Name "D$" -Force
Remove-SmbShare -Name "ADMIN$" -Force
```

#### 2. 레지스트리 설정으로 자동 공유 방지

**명령 프롬프트:**
```cmd
reg add "HKLM\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters" /v AutoShareWks /t REG_DWORD /d 0 /f
```

**PowerShell:**
```powershell
# AutoShareWks 값을 0으로 설정 (재부팅 후 기본 공유 자동 생성 방지)
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters" -Name "AutoShareWks" -Value 0 -Type DWord
```

#### 3. 일반 공유 폴더 관리

**Everyone 권한 제거:**
```powershell
# 특정 공유 폴더에서 Everyone 권한 제거
Revoke-SmbShareAccess -Name "공유이름" -AccountName "Everyone" -Force
```

**권한 부여:**
```powershell
# 특정 사용자에게 읽기 권한 부여
Grant-SmbShareAccess -Name "공유이름" -AccountName "사용자명" -AccessRight Read -Force

# 특정 사용자에게 모든 권한 부여
Grant-SmbShareAccess -Name "공유이름" -AccountName "사용자명" -AccessRight Full -Force
```

#### 4. 암호로 보호된 공유 활성화

**GUI 설정:**
```
Step 1) 시작 > 설정 > 네트워크 및 인터넷
Step 2) 고급 네트워크 설정 > 고급 공유 설정
Step 3) 모든 네트워크 > '암호로 보호된 공유' 켬 설정
```

### 4. 참고 자료

#### 공유 폴더의 보안 위협

**보안 위협:**
- **정보 유출**: 공유 폴더는 내부 네트워크의 주요 정보 유출 경로
- **악성코드 유포**: 공유 폴더를 통해 악성코드가 네트워크 전체로 확산
- **무단 접근**: 적절한 접근 제어가 없는 공유 폴더는 보안 허점

**기본 공유 폴더의 위험성:**
- **C$**: C 드라이브 전체를 네트워크에 개방
- **D$**: D 드라이브 전체를 네트워크에 개방
- **ADMIN$**: Windows 설치 폴더를 네트워크에 개방
- 실행창에서 `\\192.168.16.xxx\C$` 입력으로 직접 접근 가능

**추가 보안 대책:**
- 방화벽에서 포트 차단 (135/TCP, 139/TCP, 445/TCP)
- SMB 버전 제한 (SMBv1 비활성화, SMB 3.0+ 사용)
- 네트워크 세그먼트 분리

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.