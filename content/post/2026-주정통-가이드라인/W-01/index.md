---
title: "[2026 주요정보통신기반시설] W-01 Administrator 계정 이름 변경 등 보안성 강화"
slug: "2026-주정통/W-01"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "윈도우 최상위 관리자 계정인 Administrator의 계정명 변경 또는 보안을 고려한 비밀번호 설정 여부 점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Windows
---

# W-01 Administrator 계정 이름 변경 등 보안성 강화

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | W-01 |
| **점검내용** | 윈도우 최상위 관리자 계정인 Administrator의 계정명 변경 또는 보안을 고려한 비밀번호 설정 여부 점검 |
| **점검대상** | Windows NT, 2000, 2003, 2008, 2012, 2016, 2019, 2022 |
| **양호기준** | Administrator 기본 계정 이름을 변경하거나 강화된 비밀번호를 적용한 경우 |
| **취약기준** | Administrator 기본 계정 이름을 변경하지 않거나 단순 비밀번호를 적용한 경우 |
| **조치방법** | Administrator 기본 계정 이름 변경 및 보안성이 있는 비밀번호 설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: Administrator 기본 계정 이름을 변경했거나, 강화된 비밀번호를 적용한 경우
- **취약**: Administrator 기본 계정 이름을 변경하지 않았거나, 단순 비밀번호를 적용한 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| Administrator만 존재 | 취약 | 기본 계정명 사용 중 |
| Administrator + 비밀번호 복잡 | 부분 양호 | 계정명 미변경, 비밀번호만 강화 |
| 계정명 변경 + 복잡한 비밀번호 | 양호 | 완전 보안 강화 |
| Administrator 비활성화 + 다른 관리자 | 양호 | 기본 계정 사용 안 함 |
| SID *-500 계정명 변경 | 양호 | 실제 Administrator 계정 이름 변경 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| Windows | Administrator 계정명 | 유추 불가한 이름 | SvcAdmin_Main, SysAdmin_Production 등 |
| Windows | 비밀번호 길이 | 12자 이상 | 영문 대소문자, 숫자, 특수문자 조합 |
| Windows | 로컬 보안 정책 | 계정 이름 변경 | secpol.msc 또는 GPO |
| 도메인 | GPO | 일괄 적용 | 도메인 컨트롤러에서 설정 |

### 2. 점검 방법

#### Windows GUI 점검

```
1. 시작 > 실행 > lusrmgr.msc 입력 (로컬 사용자 및 그룹)
2. 사용자 폴더 클릭
3. Administrator 계정이 존재하는지 확인
```

#### 명령 프롬프트 점검

```cmd
net user
```

**취약 출력 예시 (Administrator 존재):**
```text
\\SERVER의 사용자 계정

-------------------------------------------------------------------------------
Administrator            Guest                    testuser
```

#### PowerShell 점검

```powershell
Get-LocalUser | Where-Object {$_.SID -like "*-500"}
```

**취약 출력 예시:**
```text
Name   Enabled Description
----   ------- -----------
Administrator True  기본 제공 관리자 계정
```

**양호 출력 예시:**
```text
Name    Enabled Description
----    ------- -----------
SuperAdmin True    사용자 계정
```

### 3. 조치 방법

#### 방법 1: 로컬 보안 정책 사용 (권장)

```
Step 1) 시작 > 제어판 > 관리 도구 > 로컬 보안 정책
Step 2) 로컬 정책 > 보안 옵션
Step 3) '계정: Administrator 계정 이름 바꾸기' 항목 더블클릭
Step 4) 유추하기 어려운 계정 이름으로 변경
```

**추천 관리자 계정명 예시:**
- ~~admin~~ (너무 일반적)
- ~~administrator~~ (기본값)
- ~~root~~ (리눅스에서 사용)
- SvcAdmin_Main, SysAdmin_Production, Mgmt_Account_01

#### 방법 2: 컴퓨터 관리 사용

```
Step 1) 시작 > 프로그램 > 관리 도구 > 컴퓨터 관리
Step 2) 로컬 사용자 및 그룹 > 사용자
Step 3) Administrator 계정 우클릭 > 이름 바꾸기
Step 4) 새로운 이름 입력
```

#### 방법 3: PowerShell 사용

```powershell
# Administrator 계정 이름 변경
Rename-LocalUser -Name "Administrator" -NewName "새관리자계정명"

# 변경 확인
Get-LocalUser
```

#### 강화된 비밀번호 설정

```powershell
# 복잡한 비밀번호 설정
$NewPassword = ConvertTo-SecureString "복잡한비밀번호123!" -AsPlainText -Force
Set-LocalUser -Name "새관리자계정명" -Password $NewPassword
```

**비밀번호 복잡성 요구사항:**
- 최소 12자 이상
- 영문 대소문자, 숫자, 특수문자 조합
- 사전에 나오는 단어 사용 금지
- 개인정보(생일, 전화번호 등) 포함 금지

### 4. 그룹 정책(GPO) 설정

도메인 환경에서는 GPO를 통해 일괄 적용:

```
1. 그룹 정책 관리 콘솔(gpedit.msc 또는 gpmc.msc)
2. 컴퓨터 구성 > 정책 > Windows 설정 > 보안 설정 > 로컬 정책 > 보안 옵션
3. "계정: Administrator 계정 이름 바꾸기" 설정
```

### 5. 주의사항

| 주의사항 | 설명 |
|----------|------|
| 계정명 변경 기록 유지 | 변경한 계정명을 별도로 보안하게 기록 관리 |
| 안전 모드 고려 | 안전 모드에서도 사용 가능한 계정명을 기억 |
| 여러 관리자 운영 | 2명 이상의 관리자가 필요한 경우 별도 계정 생성 |
| 비밀번호 주기적 변경 | 관리자 비밀번호 정기적(90일마다) 변경 |
| 비밀번호 공유 금지 | 관리자 계정 비밀번호 절대 공유 금지 |

### 6. 참고 자료

- Microsoft 보안 기술 자문: https://learn.microsoft.com/ko-kr/windows-server/identity/ad-ds/manage/component-updates/admin-account-rename
- CIS Benchmarks - Rename Administrator Account
- NIST SP 800-53: AC-2, IA-2
- KISA 주요정보통신기반시설 취약점 진단 가이드

### 7. 스크립트

- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
