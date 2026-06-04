---
title: "[2026 주요정보통신기반시설] W-04 계정 잠금 임계값 설정"
slug: "2026-주정통/W-04"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "계정 잠금 임계값의 설정 여부 점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Windows
---

# W-04 계정 잠금 임계값 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | W-04 |
| **점검내용** | 계정 잠금 임계값의 설정 여부 점검 |
| **점검대상** | Windows NT, 2000, 2003, 2008, 2012, 2016, 2019, 2022 |
| **양호기준** | 계정 잠금 임계값이 5 이하의 값으로 설정된 경우 |
| **취약기준** | 계정 잠금 임계값이 5 초과의 값으로 설정된 경우 |
| **조치방법** | 계정 잠금 임계값을 5 이하의 값으로 설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 계정 잠금 임계값이 5 이하의 값으로 설정된 경우
- **취약**: 계정 잠금 임계값이 5 초과의 값으로 설정된 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| 임계값 0회 | 취약 | 무제한 시도 가능 |
| 임계값 3~5회 | 양호 | 권장 설정 |
| 임계값 6회 이상 | 취약 | 공격 성공 확률 증가 |
| Administrator 계정 제외 | 주의 | DOS 공격 방지 고려 |
| 잠금 기간 0분 | 양호 | 관리자만 해제 가능 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| 일반 서버 | 계정 잠금 임계값 | 5회 | 일반적인 사무실 환경 |
| 공개 서버 | 계정 잠금 임계값 | 3회 | 높은 보안 요구사항 |
| 계정 잠금 기간 | 30분 | 자동 잠금 해제 시간 | |
| 잠금 관찰 시간 | 10분 | 실패 횟수 리셋 시간 | |

### 2. 점검 방법

#### 로컬 보안 정책 확인

```
1. 시작 > 실행 > secpol.msc 입력
2. 계정 정책 > 계정 잠금 정책
3. "계정 잠금 임계값" 확인
```

- **5회 이하**: 양호
- **6회 이상 또는 0(무제한)**: 취약

#### 명령 프롬프트 확인

```cmd
net accounts
```

**양호 출력 예시:**
```text
잠금 임계값: 5
잠금 기간(분): 30
잠금 관찰 시간(분): 10
```

**취약 출력 예시:**
```text
잠금 임계값: 0
잠금 기간(분): 30
잠금 관찰 시간(분): 10
```

#### PowerShell 확인

```powershell
# 계정 잠금 정책 확인
net accounts

# 계정 잠금 임계값만 확인
$LockoutThreshold = (net accounts | Select-String "잠금 임계값").ToString().Split(':')[1].Trim()
Write-Host "계정 잠금 임계값: $LockoutThreshold"

if ([int]$LockoutThreshold -le 5 -and [int]$LockoutThreshold -gt 0) {
    Write-Host "양호: 5회 이하로 설정됨" -ForegroundColor Green
} else {
    Write-Host "취약: 5회 초과 또는 0(무제한)" -ForegroundColor Red
}
```

### 3. 조치 방법

#### 방법 1: 로컬 보안 정책 설정 (권장)

```
Step 1) 시작 > 제어판 > 관리 도구 > 로컬 보안 정책
Step 2) 계정 정책 > 계정 잠금 정책
Step 3) "계정 잠금 임계값" 더블클릭
Step 4) 값으로 3~5 사이의 값 입력 (권장: 5)
Step 5) 확인 클릭
```

**권장 설정값:**
- 계정 잠금 임계값: 5회
- 계정 잠금 기간: 30분
- 잠금 관찰 시간: 10분

#### 방법 2: 명령 프롬프트 설정

```cmd
net accounts /lockoutthreshold:5
```

관련 정책 함께 설정:
```cmd
net accounts /lockoutthreshold:5 /lockoutwindow:10 /lockoutduration:30
```

설정 확인:
```cmd
net accounts
```

#### 방법 3: PowerShell 설정

```powershell
# 계정 잠금 임계값을 5로 설정
net accounts /lockoutthreshold:5

# 관련 정책 함께 설정
net accounts /lockoutthreshold:5 /lockoutwindow:10 /lockoutduration:30

# 설정 확인
net accounts
```

#### 방법 4: 그룹 정책(GPO) 설정

도메인 환경에서는 GPO를 통해 일괄 적용:

```
1. 그룹 정책 관리 콘솔(gpedit.msc 또는 gpmc.msc)
2. 컴퓨터 구성 > 정책 > Windows 설정 > 보안 설정 > 계정 정책 > 계정 잠금 정책
3. "계정 잠금 임계값" 설정
```

### 4. 계정 잠금 정책 상세

| 설정 항목 | 설명 | 권장값 |
|-----------|------|--------|
| 계정 잠금 임계값 | 계정이 잠기기까지의 실패 횟수 | 5회 |
| 계정 잠금 기간 | 계정이 잠겨 있는 시간 (0=관리자만 해제) | 30분 |
| 잠금 관찰 시간 | 실패 횟수가 리셋되는 시간 | 10분 |

**설정 시나리오 예시:**
- 사용자가 5회 연속 실패 → 계정 30분간 잠김
- 10분 내 실패 횟수가 리셋되면 다시 0부터 카운트
- 30분 후 자동으로 잠금 해제 또는 관리자가 수동 해제

### 5. 계정 잠금 해제 방법

**PowerShell:**
```powershell
# 특정 사용자 계정 잠금 해제
Unlock-ADAccount -Identity "사용자ID"  # 도메인 환경
net user "사용자ID" /active:yes         # 로컬 계정
```

**GUI:**
```
1. 컴퓨터 관리 > 로컬 사용자 및 그룹 > 사용자
2. 잠긴 계정 우클릭 > 속성
3. "계정 잠김 해제" 체크 > 확인
```

### 6. 잠금 모니터링

```powershell
# 최근 계정 잠금 이벤트 확인 (이벤트 ID 4740)
Get-WinEvent -FilterHashtable @{
    LogName='Security';
    ID=4740;
    StartTime=(Get-Date).AddDays(-7)
} -MaxEvents 10 | Format-List
```

### 7. 주의사항

| 주의사항 | 설명 |
|----------|------|
| Administrator 예외 | 기본적으로 Administrator 계정은 잠기지 않도록 설정 가능 |
| 서비스 계정 고려 | 서비스 계정의 경우 잠금 시 서비스 중단 가능성 |
| 사용자 안내 | 사용자에게 계정 잠금 정책 안내 필요 |
| 잠금 해제 절차 | 관리자를 통한 계정 잠금 해제 절차 수립 |

### 8. DOS 공격 방어

계정 잠금 정책의 악용을 방지하기 위한 추가 조치:

1. Administrator 계정 잠금 제외
2. 계정 잠금 기간 설정 (자동 해제)
3. 잠금 이벤트 모니터링
4. 다단계 인증(MFA) 도입

### 9. 참고 자료

- Microsoft Docs - Account Lockout Policy: https://docs.microsoft.com/ko-kr/windows/security/threat-protection/security-policy-settings/account-lockout-policy
- CIS Benchmark - Account Lockout Threshold
- NIST SP 800-53: AC-7 (Unsuccessful Login Attempts)
- KISA 주요정보통신기반시설 취약점 진단 가이드

### 10. 스크립트

- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
