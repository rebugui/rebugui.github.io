---
title: "[2026 주요정보통신기반시설] PC-12 Windows 자동 로그인 점검"
slug: "2026-주정통/PC-12"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "Windows자동로그인이비활성화여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - PC
---

# Windows 자동 로그인 점검

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | PC-12 |
| **점검내용** | Windows자동로그인이비활성화여부점검 |
| **점검대상** | Windows 10, Windows 11 |
| **양호기준** | Windows자동로그인이비활성화된경우 |
| **취약기준** | Windows자동로그인이활성화된경우 |
| **조치방법** | Windows자동로그인비활성화설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: Windows 자동 로그인이 비활성화된 경우
- **취약**: Windows 자동 로그인이 활성화된 경우

#### 경계 케이스 (Edge Case) 처리 방법
- **AutoAdminLogon = '1'인 경우**: 취약 (자동 로그인 활성화)
- **AutoAdminLogon = '0'인 경우**: 양호 (자동 로그인 비활성화)
- **레지스트리 값이 없는 경우**: 양호로 판단

#### 권장 설정값
- **AutoAdminLogon**: 0 (비활성화)

### 2. 점검 방법

#### Windows 10, 11에서의 점검

**레지스트리 확인:**
```cmd
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v AutoAdminLogon
```

**PowerShell 확인:**
```powershell
Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" -Name "AutoAdminLogon" -ErrorAction SilentlyContinue
```

### 3. 조치 방법

#### 1. 레지스트리에서 자동 로그인 비활성화

**명령 프롬프트:**
```cmd
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v AutoAdminLogon /t REG_SZ /d 0 /f
```

**PowerShell:**
```powershell
# 관리자 권한 PowerShell 실행
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" -Name "AutoAdminLogon" -Value "0" -Type String
```

#### 2. 관련 레지스트리 값 삭제

```powershell
# 사용자 이름, 비밀번호 등 관련 값 삭제
Remove-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" -Name "DefaultUserName" -ErrorAction SilentlyContinue
Remove-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" -Name "DefaultPassword" -ErrorAction SilentlyContinue
Remove-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" -Name "DefaultDomainName" -ErrorAction SilentlyContinue
```

### 4. 참고 자료

#### Windows 자동 로그인의 보안 위협

**보안 위협:**
- **물리적 접근 방지**: PC에 접근할 수 있는 사람은 누구나 시스템에 접근 가능
- **비인가 접근 방지**: 로그인 자격 증명 없이 시스템 사용 가능
- **데이터 유출 방지**: 중요 파일, 개인정보 유출 위험

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.