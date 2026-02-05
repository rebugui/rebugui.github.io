---
title: "[2026 주요정보통신기반시설] PC-18 원격 지원을 금지하도록 정책을 설정"
slug: "2026-주정통/PC-18"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "원격지원을사용하지않도록하는지설정여부점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - PC
---

# 원격 지원을 금지하도록 정책을 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | PC-18 |
| **점검내용** | 원격지원을사용하지않도록하는지설정여부점검 |
| **점검대상** | Windows 10, Windows 11 |
| **양호기준** | 원격지원이'사용안함'으로설정된경우 |
| **취약기준** | 원격지원이'사용'으로설정된경우 |
| **조치방법** | 원격지원서비스비활성화 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 원격 지원이 '사용 안 함'으로 설정된 경우
- **취약**: 원격 지원이 '사용'으로 설정된 경우

#### 경계 케이스 (Edge Case) 처리 방법
- **fAllowToGetHelp = 0**: 양호 (비활성화)
- **fAllowToGetHelp = 1**: 취약 (활성화)

#### 권장 설정값
- **원격 지원**: 사용 안 함

### 2. 점검 방법

#### Windows 10, 11에서의 점검

```
Step 1) 시작 > 설정 > 시스템 > 원격 데스크톱
Step 2) '원격 지원' 설정 확인
```

**PowerShell 확인:**
```powershell
Get-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Remote Assistance" -Name "fAllowToGetHelp" -ErrorAction SilentlyContinue
```

### 3. 조치 방법

#### 1. 설정 앱에서 비활성화

```
Step 1) 시작 > 설정 > 시스템 > 원격 데스크톱
Step 2) '원격 지원 초대 허용' 체크 해제
```

#### 2. 레지스트리로 비활성화

```cmd
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Remote Assistance" /v fAllowToGetHelp /t REG_DWORD /d 0 /f
```

**PowerShell:**
```powershell
# 관리자 권한 PowerShell 실행
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Remote Assistance" -Name "fAllowToGetHelp" -Value 0 -Type DWord
```

### 4. 참고 자료

#### 원격 지원의 보안 위협

**보안 위협:**
- **비인가 접근 방지**: 악의적인 목적의 원격 접근 방지
- **시스템 장악 방지**: 원격에서 시스템 제어권 탈취 방지
- **피싱 공격**: 기술 지원을 사칭한 공격

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.