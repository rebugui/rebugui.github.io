---
title: "[2026 주요정보통신기반시설] CA-03 MFA(Multi-Factor Authentication)설정"
slug: "2026-주정통/CA-03"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "2차 인증을 통해 사용자 계정의 보안을 강화 여부 점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Cloud
draft: true
---

# CA-03 MFA(Multi-Factor Authentication)설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | CA-03 |
| **점검내용** | 2차 인증을 통해 사용자 계정의 보안을 강화 여부 점검 |
| **점검대상** | 클라우드 플랫폼 |
| **판단기준** | 양호: 각 계정별 2차 인증이 설정된 경우 |
| **판단기준** | 취약: 각 계정별 2차 인증이 설정되지 않은 경우 |
| **조치방법** | 인증번호, OTP 등을 통한 2차 인증 설정 |

---
## 상세 설명

### 1. 항목 개요

**MFA(Multi-Factor Authentication, 다중 인증)**은 사용자 인증 시 두 가지 이상의 인증 요소를 요구하는 보안 방식입니다. 비밀번호(1차 인증)만으로는 충분하지 않기 때문에, 추가적인 인증 수단(2차 인증)을 통해 계정 보안을 강화합니다.

### 2. 왜 이 항목이 필요한가요?

**비밀번호만으로는 부족합니다**

| 공격 유형 | 설명 | 위험도 |
|----------|------|--------|
| **무차별 대입 공격** | 모든 가능한 비밀번호 조합을 시도 | 상 |
| **사전 공격** | 자주 사용되는 비밀번호 목록으로 시도 | 상 |
| **피싱** | 가짜 로그인 페이지로 비밀번호 탈취 | 상 |
| **키로깅** | 키보드 입력 정보를 몰래 수집 | 중 |

**MFA의 보안 효과**
- 비밀번호가 탈취되어도 2차 인증이 없으면 접근 불가
- 해커가 물리적인 2차 인증 수단을 가질 확률은 극히 낮음
- 99.9% 이상의 자동화된 공격 차단 가능

**실제 사례**
Microsoft에 따르면 MFA를 활성화하면 계정 탈취 위험이 **99.9% 감소**한다고 합니다.

### 3. 점검 대상

- 모든 클라우드 관리 콘솔 접근 계정 (특히 관리자 권한 계정)
- IAM 사용자 계정
- 루트(최상위 관리자) 계정

### 4. 판단 기준

| 구분 | 기준 |
|------|------|
| **양호** | 각 계정별 2차 인증이 설정된 경우 |
| **취약** | 각 계정별 2차 인증이 설정되지 않은 경우 |

### 5. 점검 방법

#### Step 1: MFA 설정 현황 확인

```bash
# AWS에서 MFA 설정 현황 확인
aws iam list-virtual-mfa-devices
aws iam get-account-summary | grep mfa

# Azure에서 MFA 설정 확인
az ad user show --user-id user@domain.com --query '[id,displayName,strongAuthenticationDetail]'
```

#### Step 2: 각 계정별 MFA 설정 여부 확인

클라우드 콘솔에서 다음 내용을 확인합니다:
- IAM 사용자별 MFA 장치 할당 여부
- 루트 계정 MFA 활성화 여부
- MFA 유형 (하드웨어 토큰, 소프트웨어 앱, SMS 등)

### 6. 조치 방법

#### Step 1: 2차 인증 설정

**MFA 인증 요소 3가지 유형**

| 유형 | 예시 | 설명 |
|------|------|------|
| **지식(Knowledge)** | 비밀번호, PIN | 사용자가 아는 것 |
| **소유(Possession)** | OTP 앱, 하드웨어 토큰, SMS | 사용자가 가진 것 |
| **속성(Inherence)** | 지문, 얼굴인식, 홍채인식 | 사용자의 고유한 특성 |

**MFA 설정 방법별 비교**

| 방법 | 장점 | 단점 | 보안성 |
|------|------|------|--------|
| **OTP 앱** | | | |
| (Google Authenticator 등) | - 네트워크 불필요<br>- 무료<br>- 쉬운 설정 | - 기기 분실 시 문제 | 높음 |
| **SMS 인증** | - 설정 쉬움<br>- 별도 앱 불필요 | - SMS 가로채기 가능<br>- 신호 수신 불가 지역 있음 | 중간 |
| **하드웨어 토큰** | - 보안성 최고<br>- 물리적 분리 | - 비용 발생<br>- 분실 시 복구 어려움 | 최상 |

**AWS CLI에서 MFA 설정 예시**

```bash
# 1. 가상 MFA 장치 생성
aws iam create-virtual-mfa-device --virtual-mfa-device-name AdminMFADevice

# 2. 사용자에게 MFA 장치 할당
aws iam enable-mfa-device --user-name admin-user --serial-number arn:aws:iam::123456789012:mfa/AdminMFADevice --authentication-code1 123456 --authentication-code2 789012
```

**Azure Portal에서 MFA 설정**
1. Azure Portal 접속 → Azure Active Directory
2. 사용자 선택 → 다단계 인증
3. 다단계 인증 사용 → 설정
4. 인증 방법 선택 (전화, SMS, 모바일 앱 등)

#### Step 2: 모든 관리자 계정에 MFA 필수 적용

```yaml
# AWS IAM 정책: MFA 없이 콘솔 접근 차단
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "BlockConsoleAccessWithoutMFA",
      "Effect": "Deny",
      "Action": "*",
      "Resource": "*",
      "Condition": {
        "Bool": {
          "aws:MultiFactorAuthPresent": "false"
        }
      }
    }
  ]
}
```

#### Step 3: 정기적인 MFA 설정 검토

- 분기별 MFA 설정 현황 확인
- 신규 계정 생성 시 MFA 설정 강제
- MFA 장치 분실/교체 프로시저 마련

### 7. 조치 시 주의사항

| 주의사항 | 설명 |
|----------|------|
| **관리자 계정 우선 적용** | 관리자 권한 계정부터 MFA 설정 (최우선) |
| **복구 코드 보관** | OTP 앱 초기화 시 사용할 복구 코드 안전하게 보관 |
| **기기 변경 프로시저** | MFA 기기 분실/교체 시 접속 복구 절차 마련 |
| **사용자 교육** | MFA 사용법, 복구 방법 등 사용자 교육 실시 |
| **여러 MFA 방법 혼용** | 주 MFA + 백업 MFA (예: OTP 앱 + SMS) 설정 권장 |

### 8. 참고 자료

- **NIST SP 800-63B**: Digital Identity Guidelines
- **CIS Controls**: 16.12 (Use Multi-Factor Authentication for All Accounts)
- **AWS IAM Best Practices**: Use MFA for the AWS account root user and IAM users
- **Microsoft Security**: Multi-factor authentication

---

## 요약

**MFA 설정**은 클라우드 계정 보안을 위한 가장 효과적인 조치입니다. 비밀번호만으로는 충분하지 않으며, 2차 인증을 통해 계정 탈취 위험을 99.9% 이상 감소시킬 수 있습니다. 특히 관리자 권한을 가진 계정에는 MFA가 필수적이며, 가능한 한 보안성이 높은 OTP 앱이나 하드웨어 토큰을 사용하는 것이 좋습니다.

**핵심 액션 아이템**
1. 루트 계정 및 모든 관리자 계정에 MHA 필수 설정
2. 일반 사용자 계정에도 MFA 적용 권장
3. OTP 앱 기반 MFA 사용 (SMS보다 보안성 높음)
4. MFA 복구 코드 안전하게 보관
5. 정기적인 MFA 설정 현황 검토
