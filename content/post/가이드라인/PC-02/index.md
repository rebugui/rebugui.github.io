---
title: "[2026 주요정보통신기반시설] PC-02 비밀번호 관리 정책 설정"
slug: "2026-주정통/PC-02"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "비밀번호설정정책이복잡성을만족하는지점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - PC
---

# 비밀번호 관리 정책 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | PC-02 |
| **점검내용** | 비밀번호설정정책이복잡성을만족하는지점검 |
| **점검대상** | Windows 10, Windows 11 |
| **양호기준** | 복잡성을만족하는비밀번호정책이설정된경우 |
| **취약기준** | 비밀번호를 사용하지 않거나, 추측하기 쉬운 문자조합으로 이루어진 짧은 자릿수의 비밀번호를 설정된경우 |
| **조치방법** | 비밀번호정책을해당기관의보안정책에적합하게설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 복잡성을 만족하는 비밀번호 정책이 설정된 경우
  - 최소 암호 길이: 8 문자 이상
  - 암호 복잡성 요구사항: 사용함
- **취약**: 비밀번호를 사용하지 않거나, 추측하기 쉬운 문자조합으로 이루어진 짧은 자릿수의 비밀번호가 설정된 경우

#### 경계 케이스 (Edge Case) 처리 방법
- **최소 암호 길이가 7 이하**: 취약으로 판단
- **암호 복잡성 요구사항이 비활성화**: 취약으로 판단
- **일부 계정만 Null 비밀번호 허용**: 전체적으로 취약으로 판단

#### 권장 설정값
- **최소 암호 길이**: 8 문자 (권장), 10 문자 (높은 보안)
- **암호는 복잡성을 만족해야 함**: 사용
- **복잡성 요구사항**: 다음 4가지 문자 범주 중 최소 3가지 포함
  - 영문 대문자 (A~Z)
  - 영문 소문자 (a~z)
  - 숫자 (0~9)
  - 특수문자 (!@#$%^&* 등)

### 2. 점검 방법

#### Windows 10, 11에서의 점검

**GUI 확인:**
```
Step 1) 시작 > Windows 관리 도구(Windows Tools) > 로컬 보안 정책
Step 2) 보안 설정 > 계정 정책 > 암호 정책
Step 3) 다음 항목 확인
        - 최소 암호 길이
        - 암호는 복잡성을 만족해야 함
```

**PowerShell 확인:**
```powershell
# 암호 정책 확인
net accounts

# 복잡성 요구사항 확인 (레지스트리)
Get-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Lsa" -Name "PasswordComplexity"
```

### 3. 조치 방법

#### 1. 최소 암호 길이 설정

**GUI 설정:**
```
Step 1) 로컬 보안 정책 > 계정 정책 > 암호 정책
Step 2) '최소 암호 길이' 더블클릭
Step 3) 값을 '8' 이상으로 설정
Step 4) 적용 > 확인
```

**PowerShell 설정:**
```powershell
# 최소 암호 길이 8로 설정
secedit /export /cfg config.inf
(Get-Content config.inf) -replace 'PasswordComplexity = 0', 'PasswordComplexity = 1' | Set-Content config.inf
(Get-Content config.inf) -replace 'MinimumPasswordLength = \d+', 'MinimumPasswordLength = 8' | Set-Content config.inf
secedit /configure /db secedit.sdb /cfg config.inf /areas SECURITYPOLICY
Remove-Item config.inf
```

#### 2. 암호 복잡성 요구사항 활성화

**GUI 설정:**
```
Step 1) 로컬 보안 정책 > 계정 정책 > 암호 정책
Step 2) '암호는 복잡성을 만족해야 함' 더블클릭
Step 3) '사용' 선택
Step 4) 적용 > 확인
```

**명령 프롬프트/PowerShell 설정:**
```cmd
secedit /configure /db secedit.sdb /cfg "%TEMP%\secpol.cfg" /areas SECURITYPOLICY
```

### 4. 참고 자료

#### 비밀번호 복잡성 정책의 중요성

**보안 위협:**
- **무차별 대입 공격(Brute Force)**: 단순한 비밀번호는 짧은 시간 안에 탈취됨
- **사전 공격(Dictionary Attack)**: '123456', 'password' 같은 흔한 비밀번호는 쉽게 탈취됨
- **추측 공격**: 생일, 전화번호, 계정명 등 쉽게 추측할 수 있는 정보로 만든 비밀번호 위험

**비밀번호 설계 원칙:**
- Null(공백) 비밀번호 사용 금지
- 문자 또는 숫자만으로 구성 금지
- 사용자 ID와 같거나 유사한 비밀번호 금지
- 연속적인 문자나 숫자 사용 금지 (예: 1111, 1234, abcd)
- 주기성 비밀번호 재사용 금지
- 전화번호, 생일과 같이 추측하기 쉬운 개인정보 사용 금지

**안전한 비밀번호 생성 팁:**
- 문구 기반 비밀번호: 쉬운 문장의 첫 글자를 조합 (예: "My Dog Likes To Eat Pizza!" → "MdL2eP!")
- 비밀번호 관리자 사용
- 이중 인증 활성화

**금지된 비밀번호 예시:**
- Null, 계정과 같거나 유사한 스트링
- 'root', 'rootroot', 'root123', '123root'
- 'admin', 'admin123', '123admin', 'osadmin'

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.