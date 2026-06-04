---
title: "[2026 주요정보통신기반시설] PC-03 복구 콘솔에서 자동 로그온을 금지하도록 설정"
slug: "2026-주정통/PC-03"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "Windows복구콘솔자동로그인설정이허용여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - PC
---

# 복구 콘솔에서 자동 로그온을 금지하도록 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | PC-03 |
| **점검내용** | Windows복구콘솔자동로그인설정이허용여부점검 |
| **점검대상** | Windows 10, Windows 11 |
| **양호기준** | 복구콘솔자동로그온허용이'사용안함'으로설정된경우 |
| **취약기준** | 복구콘솔자동로그온허용이'사용'으로설정된경우 |
| **조치방법** | 복구콘솔자동로그온허용'사용안함'으로설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 복구 콘솔 자동 로그온 허용이 '사용 안 함'으로 설정된 경우
- **취약**: 복구 콘솔 자동 로그온 허용이 '사용'으로 설정된 경우

#### 경계 케이스 (Edge Case) 처리 방법
- **레지스트리 값이 0인 경우**: 양호 (사용 안 함)
- **레지스트리 값이 1인 경우**: 취약 (사용)
- **레지스트리 키가 존재하지 않는 경우**: 기본값이 사용 안 함이므로 양호로 판단

#### 권장 설정값
- **복구 콘솔: 자동 관리 로그온 허용**: 사용 안 함
- **레지스트리 값**: SecurityLevel = 0

### 2. 점검 방법

#### Windows 10, 11에서의 점검

**GUI 확인:**
```
Step 1) 시작 > 모든 앱 > Windows Tools > 로컬 보안 정책
Step 2) 보안 설정 > 로컬 정책 > 보안 옵션
Step 3) '복구 콘솔: 자동 관리 로그온 허용' 항목 확인
```

**레지스트리 확인:**
```cmd
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Setup\RecoveryConsole" /v SecurityLevel
```

**PowerShell 확인:**
```powershell
Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Setup\RecoveryConsole" -Name "SecurityLevel" -ErrorAction SilentlyContinue
```

### 3. 조치 방법

#### 1. 로컬 보안 정책을 통한 설정

**GUI 설정:**
```
Step 1) 시작 > 모든 앱 > Windows Tools > 로컬 보안 정책
Step 2) 보안 설정 > 로컬 정책 > 보안 옵션
Step 3) '복구 콘솔: 자동 관리 로그온 허용' 속성 더블클릭
Step 4) '사용 안 함' 선택
Step 5) 확인 클릭
```

#### 2. 레지스트리를 통한 설정

**명령 프롬프트:**
```cmd
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Setup\RecoveryConsole" /v SecurityLevel /t REG_DWORD /d 0 /f
```

**PowerShell:**
```powershell
# 관리자 권한 PowerShell 실행
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Setup\RecoveryConsole" -Name "SecurityLevel" -Value 0 -Type DWord
```

### 4. 참고 자료

#### 복구 콘솔 자동 로그온의 보안 위협

**보안 위협:**
- **비인가자의 관리자 권한 탈취**: 복구 콘솔 자동 로그온 설정은 시스템 액세스 허가 전 Administrator 계정의 비밀번호 제공 여부를 결정
- **시스템 파일 조작**: 복구 콘솔을 통해 시스템 핵심 파일을 수정, 삭제, 교체 가능
- **보안 설정 우회**: 일반 Windows 환경에서의 보안 정책을 우회하여 시스템에 접근 가능

**현대적인 관점:**
- 최신 Windows 10, 11에서는 "복구 콘솔" 개념이 진화하여 Windows 복구 환경(WinRE)으로 대체
- WinRE에서도 동일한 보안 원칙 적용: 비인가자의 쉬운 접근 방지, 복구 환경 진입 시 적절한 인증 요구

**추가 보안 대책:**
- BIOS/UEFI 암호 설정
- 하드 디스크 암호화 (BitLocker)
- 물리적 보안 강화
- 부팅 미디어 관리

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.