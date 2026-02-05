---
title: "[2026 주요정보통신기반시설] CA-04 클라우드계정비밀번호정책관리"
slug: "2026-주정통/CA-04"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "비밀번호 설정 정책의 복잡성 만족 여부 점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Cloud
---

# CA-04 클라우드계정비밀번호정책관리

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | CA-04 |
| **점검내용** | 비밀번호 설정 정책의 복잡성 만족 여부 점검 |
| **점검대상** | 클라우드 플랫폼 |
| **판단기준** | 양호: 복잡성을 만족하는 비밀번호 정책을 설정하고 로그인 시도 제한을 설정한 경우 |
| **판단기준** | 취약: 복잡성을 만족하지 않는 비밀번호를 사용하거나 로그인 시도 제한을 설정하지 않은 경우 |
| **조치방법** | 비밀번호 정책을 해당 기관의 보안 정책에 적합하게 설정 |

---
## 상세 설명

### 1. 항목 개요

클라우드 계정 비밀번호 정책 관리는 강력한 비밀번호 정책을 수립하고 로그인 시도 제한을 설정하여 비밀번호 추측 공격을 방지하는 것을 목적으로 합니다. 약한 비밀번호는 해커들이 가장 먼저 시도하는 침입 경로입니다.

### 2. 왜 이 항목이 필요한가요?

**비밀번호 탈취 공격의 현실**

| 공격 유형 | 공격 방식 | 평균 소요 시간 |
|----------|----------|----------------|
| **무차별 대입 공격** | 가능한 모든 조합 시도 | 8자리 영숫자: 수일~수주 |
| **사전 공격** | 자주 사용되는 비밀번호 사전으로 시도 | 수분~수시간 |
| **크리덴셜 스터핑** | 유출된 ID/비밀번호로 다른 사이트 시도 | 즉시 |
| **패턴 분석** | 사용자 패턴(생일, 전화번호 등) 추측 | 수분~수시간 |

**취약한 비밀번호의 위험성**

```
가장 많이 사용되는 취약한 비밀번호 TOP 10 (2024):
1. 123456
2. admin
3. 12345678
4. 123456789
5. 12345
6. password
7. 1234567890
8. 1234567
9. qwerty
10. 1q2w3e4r!
```

이러한 비밀번호는 몇 초 만에 추측할 수 있습니다.

### 3. 점검 대상

- 모든 클라우드 플랫폼 계정 비밀번호 정책
- 비밀번호 복잡성 요구사항
- 로그인 시도 제한 설정

### 4. 판단 기준

| 구분 | 기준 |
|------|------|
| **양호** | 복잡성을 만족하는 비밀번호 정책을 설정하고 로그인 시도 제한을 설정한 경우 |
| **취약** | 복잡성을 만족하지 않는 비밀번호를 사용하거나 로그인 시도 제한을 설정하지 않은 경우 |

**비밀번호 복잡성 기준**
- 영문자, 숫자 및 특수문자를 2개 조합: 10자리 이상
- 영문자, 숫자 및 특수문자를 3개 조합: 8자리 이상

### 5. 점검 방법

#### Step 1: 비밀번호 정책 확인

```bash
# AWS 계정 비밀번호 정책 확인
aws iam get-account-password-policy

# Azure AD 비밀번호 정책 확인
az ad policy show --policy-id password-policy

# Google Workspace 비밀번호 정책 확인
gsuite admin에서 확인 필요
```

#### Step 2: 로그인 시도 제한 설정 확인

```bash
# AWS에서 로그인 시도 제한 확인
# CloudTrail 로그를 통해 로그인 실패 패턴 확인
aws cloudtrail lookup-events --lookup-attributes AttributeKey=EventName,AttributeValue=ConsoleLogin

# Azure에서 로그인 시도 제한 확인
az monitor activity-log list --caller user@domain.com
```

#### Step 3: 비밀번호 복잡성 검증

| 검증 항목 | 확인 내용 |
|----------|----------|
| 최소 길이 | 8~10자리 이상 |
| 문자 조합 | 영문대소문자, 숫자, 특수문자 혼용 |
| 반복 제한 | 동일 문자 연속 3회 이상 금지 |
| 예측 불가 | 사용자 정보(생일, 전화번호 등) 사용 금지 |
| 주기 변경 | 90일~180일 주기 변경 권장 |

### 6. 조치 방법

#### Step 1: 클라우드 콘솔 계정에 대한 비밀번호 정책 설정

**AWS IAM 비밀번호 정책 설정 예시**

```bash
# AWS 계정 비밀번호 정책 설정
aws iam update-account-password-policy \
  --minimum-password-length 12 \
  --require-symbols \
  --require-numbers \
  --require-uppercase-characters \
  --require-lowercase-characters \
  --allow-users-to-change-password \
  --max-password-age 90 \
  --password-reuse-prevention 5 \
  --hard-expiry
```

**비밀번호 정책 파라미터 설명**

| 파라미터 | 권장값 | 설명 |
|----------|--------|------|
| 최소 길이 | 12자리 이상 | 길수록 보안성 향상 |
| 대문자 필수 | true | 보안 강화 |
| 소문자 필수 | true | 보안 강화 |
| 숫자 필수 | true | 보안 강화 |
| 특수문자 필수 | true | 보안 강화 |
| 최대 사용 기간 | 90일 | 주기 변경 |
| 재사용 방지 | 5개 이전 | 이전 비밀번호 재사용 금지 |
| 만료 강제 | true | 만료 후 강제 변경 |

**Azure AD 비밀번호 정책 설정**

```powershell
# Azure PowerShell을 통한 비밀번호 정책 설정
Set-MsolPasswordPolicy -DomainName contoso.com -ValidityPeriod 90 -NotificationDays 14

# 또는 Azure Portal에서 설정
# Azure Active Directory > Properties > Password policy
```

#### Step 2: 로그인 시도 제한 설정

**무차별 대입 공격 방지를 위한 설정**

| 설정 항목 | 권장값 | 설명 |
|----------|--------|------|
| 최대 시도 횟수 | 5회 | 연속 실패 허용 횟수 |
| 잠금 시간 | 15분~30분 | 잠금 유지 시간 |
| CAPTCHA | 3회 실패 후 | 자동화된 공격 방지 |
| IP 기반 제한 | 동일 IP에서 시간당 제한 | 분산 공격 방지 |

**AWS CloudTrail + Lambda를 활용한 로그인 시도 제한 예시**

```python
import boto3
import json

def lambda_handler(event, context):
    # 로그인 실패 이벤트 확인
    if event['detail']['eventName'] == 'ConsoleLogin' and event['detail']['errorMessage']:
        user_name = event['detail']['userIdentity']['userName']
        source_ip = event['detail']['sourceIPAddress']

        # 실패 횟수 확인 (DynamoDB 또는 Redis 활용)
        # 실패 횟수가 5회 이상인 경우 계정 잠금

        # SNS를 통해 관리자에게 알림
        sns = boto3.client('sns')
        sns.publish(
            TopicArn='arn:aws:sns:region:account:security-alerts',
            Message=f'로그인 실패 과다: {user_name} from {source_ip}',
            Subject='Security Alert'
        )
```

#### Step 3: 비밀번호 정책 정기 검토

```yaml
비밀번호 정책 검토 체크리스트:
  - 복잡성 요구사항: 8자리 이상, 문자 조합
  - 변경 주기: 90일 권장
  - 재사용 제한: 최근 5개 비밀번호 사용 불가
  - 만료 알림: 만료 14일 전 사용자에게 알림
  - 임시 비밀번호: 첫 로그인 시 강제 변경
```

### 7. 조치 시 주의사항

| 주의사항 | 설명 |
|----------|------|
| **사용자 편의성 고려** | 너무 복잡한 정책은 사용자가 비밀번호를 적어두게 됨 |
| **비밀번호 관리자 권장** | 복잡한 비밀번호를 안전하게 저장할 수 있는 도구 사용 권장 |
| **변경 주기 과도하게 짧지 않게** | 너무 자주 변경하면 사용자가 단순한 패턴 사용 |
| **길이 > 복잡성** | 특수문자 강요보다는 길이를 늘리는 것이 보안에 더 효과적 |
| **MFA와 병행** | 비밀번호 정책만으로는 부족, MHA와 함께 사용 |

### 8. 참고 자료

- **NIST SP 800-63B**: Digital Identity Guidelines (Section 5.1.1.2)
- **CIS Controls**: 4.4 (Use Unique Passwords)
- **OWASP**: Authentication Cheat Sheet
- **Microsoft**: Password Guidance (최신 가이드라인)

---

## 요약

**클라우드계정비밀번호정책관리**는 비밀번호 탈취 공격을 방지하기 위한 기본적인 보안 조치입니다. 최소 10자리 이상의 길이와 문자 조합(영문대소문자, 숫자, 특수문자)을 요구하고, 로그인 시도 제한을 설정하여 무차별 대입 공격을 방지해야 합니다. 최근 보안 트렌드는 복잡성보다는 길이를 강조하고 있으며, 비밀번호만으로는 충분하지 않으므로 MFA와 반드시 함께 사용해야 합니다.

**핵심 액션 아이템**
1. 최소 12자리 이상 비밀번호 정책 설정
2. 영문대소문자, 숫자, 특수문자 조합 필수
3. 90일 주기 비밀번호 변경 정책
4. 로그인 실패 5회 시 계정 잠금 설정
5. MFA와 함께 사용하여 보안 강화
