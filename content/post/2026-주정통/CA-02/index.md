---
title: "[2026 주요정보통신기반시설] CA-02 사용자정책관리"
slug: "2026-주정통/CA-02"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "사용자 계정에 적절한 권한 부여 여부 점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Cloud
---

# CA-02 사용자정책관리

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | CA-02 |
| **점검내용** | 사용자 계정에 적절한 권한 부여 여부 점검 |
| **점검대상** | Cloud Platform |
| **판단기준** | 양호: 사용자/그룹의 목적에 맞게 역할/권한이 할당된 경우 |
| **판단기준** | 취약: 사용자/그룹을 목적에 맞지 않게 역할/권한이 할당된 경우 |
| **조치방법** | 사용자/그룹의 역할/권한을 목적에 맞게 설정 |

---
## 상세 설명

### 1. 항목 개요

사용자정책관리는 클라우드 환경에서 각 사용자에게 **"최소 권한의 원칙(Principle of Least Privilege)"**에 따라 적절한 권한만 부여하는 것을 의미합니다. 모든 사용자에게 필요 이상의 권한을 부여하면, 계정이 탈취되었을 때 피해 범위가 확대될 수 있습니다.

### 2. 왜 이 항목이 필요한가요?

**과도한 권한 부여의 위험성**
- 개발자에게 운영 관리자 권한이 부여되면, 실수로 프로덕션 환경을 파괴할 수 있습니다
- 일반 직원에게 모든 데이터에 접근 권한이 있으면, 악의적인 내부자가 중요 데이터를 유출할 수 있습니다
- 관리자 권한을 가진 계정이 해킹되면, 전체 시스템이 장악당할 수 있습니다

**최소 권한의 원칙**
> "사용자는 자신의 업무를 수행하는 데 필요한 최소한의 권한만 가져야 한다"

이 원칙은 보안의 기본 원칙으로, 클라우드 환경에서 더욱 중요합니다.

### 3. 점검 대상

- 모든 클라우드 플랫폼 사용자 계정
- 사용자 그룹 및 역할(Role)
- IAM(Identity and Access Management) 정책

### 4. 판단 기준

| 구분 | 기준 |
|------|------|
| **양호** | 사용자/그룹의 목적에 맞게 역할/권한이 할당된 경우 |
| **취약** | 사용자/그룹을 목적에 맞지 않게 역할/권한이 할당된 경우 |

### 5. 점검 방법

#### Step 1: 사용자별 권한 현황 파악

```bash
# AWS IAM 사용자별 권한 확인
aws iam list-users
aws iam list-attached-user-policies --user-name username
aws iam list-user-policies --user-name username

# Azure 사용자 역할 확인
az role assignment list --assignee user@domain.com
```

#### Step 2: 부적절한 권한 식별

다음과 같은 경우를 부적절한 권한 할당으로 간주합니다:
- 일반 사용자에게 관리자 권한이 부여된 경우
- 업무와 무관한 서비스에 접근 권한이 있는 경우
- 모든 리소스에 접근 가능한 와일드카드(*) 권한이 부여된 경우
- 퇴사자의 권한이 그대로 남아있는 경우

#### Step 3: 권한 검토

| 사용자 유형 | 예상 권한 범위 |
|------------|--------------|
| 시스템 관리자 | 모든 리소스 관리 권한 |
| 개발자 | 개발/테스트 환경 리소스 접근 권한 |
| 운영자 | 프로덕션 환경 리소스 모니터링 및 제어 권한 |
| 일반 사용자 | 자신의 데이터에만 접근 권한 |

### 6. 조치 방법

#### Step 1: 계정 및 그룹 확인 후 불필요한 권한 제거

```yaml
# AWS IAM 정책 예시 (최소 권한 부여)
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::my-bucket/*"
    }
  ]
}
```

#### Step 2: 별도의 계정을 생성하여 서비스 운영에 활용

**중요**: 콘솔 최상위 관리자(최초 가입 계정)는 서비스 운영에 활용 금지

1. **최상위 관리자 계정(루트 계정) 분리**
   - 긴급 상황에서만 사용
   - 일상적인 운영 작업에는 사용하지 않음
   - MFA 필수 활성화

2. **운영용 관리자 계정 생성**
   ```bash
   # AWS에서 운영용 관리자 계정 생성
   aws iam create-user --user-name admin-user
   aws iam attach-user-policy --user-name admin-user --policy-arn arn:aws:iam::aws:policy/AdministratorAccess
   ```

3. **1인 1계정 원칙 준수**
   - 공용 계정 사용 지양
   - 각 사용자별 개별 계정 생성
   - 개별 계정에 적절한 권한 부여

#### Step 3: 역할(Role) 기반 권한 관리

```yaml
# 역할 기반 접근 제어(RBAC) 구성 예시
# 개발자 역할
DeveloperRole:
  Permissions:
    - s3:ReadWrite
    - ec2:StartStopInstances
  Scope:
    - Environment: Development
    - Region: ap-northeast-2

# 운영자 역할
OperatorRole:
  Permissions:
    - ec2:DescribeInstances
    - cloudwatch:*
  Scope:
    - Environment: Production
```

### 7. 조치 시 주의사항

| 주의사항 | 설명 |
|----------|------|
| **업무 영향도 확인** | 권한 변경 전 해당 사용자의 업무에 미치는 영향 검토 |
| **테스트 환경 검증** | 운영 환경 적용 전 테스트 환경에서 권한 변경 검증 |
| **단계적 적용** | 한 번에 많은 권한을 변경하지 않고, 단계적으로 진행 |
| **롤백 계획 수립** | 문제 발생 시 이전 권한으로 복구할 수 있는 절차 마련 |
| **문서화** | 권한 변경 이력과 사유를 문서화하여 감사 대비 |

### 8. 참고 자료

- **NIST SP 800-53**: AC-6 (Least Privilege)
- **CIS Controls**: 4.3 (Authorize, Monitor, and Audit All Remote Access)
- **AWS Well-Architected Framework**: Security Pillar - IAM Best Practices
- **Azure Security Benchmark**: Identity and Access Management

---

## 요약

**사용자정책관리**는 클라우드 보안에서 가장 중요한 항목 중 하나입니다. 최소 권한의 원칙에 따라 각 사용자에게 필요한 권한만 부여하고, 정기적인 권한 검토를 통해 불필요한 권한을 제거해야 합니다. 특히 최상위 관리자 계정은 비상시에만 사용하고, 일상적인 운영은 별도로 생성한 계정으로 수행해야 합니다.

**핵심 액션 아이템**
1. 모든 사용자의 권한 현황 정기적으로 검토 (연 2회 이상 권장)
2. 최소 권한 원칙에 따라 불필요한 권한 제거
3. 최상위 관리자 계정 분리 및 비상시에만 사용
4. 1인 1계정 원칙 준수
5. 역할(Role) 기반 권한 관리 체계 도입
