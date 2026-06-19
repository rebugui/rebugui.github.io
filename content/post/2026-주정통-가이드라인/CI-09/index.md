---
title: "[2026 주요정보통신기반시설] CI-09 약한비밀번호정책(Weak Password Policy)"
slug: "2026-주정통/CI-09"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "웹 애플리케이션 내 로그인 폼 등 비밀번호를 설정하는 단계에서 약한 강도의 문자열 사용 여부를 점검하고, 비밀번호 복잡성 요구사항(최소 길이, 대문자 및 소문자, 숫자 및 특수문자 포함 등)을 준수 여부 점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Web
draft: true
---

# 약한비밀번호정책(Weak Password Policy)

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | CI-09 |
| **점검내용** | 웹 애플리케이션 내 로그인 폼 등 비밀번호를 설정하는 단계에서 약한 강도의 문자열 사용 여부를 점검하고, 비밀번호 복잡성 요구사항(최소 길이, 대문자 및 소문자, 숫자 및 특수문자 포함 등)을 준수 여부 점검 |
| **점검대상** | 웹 애플리케이션 소스코드 |
| **양호기준** | 관리자 및 사용자 계정의 비밀번호가 유추하기 어려운 값으로 설정되어 있거나 높은 복잡성의 비밀번호 정책이 설정되어 있는 경우 |
| **취약기준** | 관리자 및 사용자 계정의 비밀번호가 유추하기 쉬운 값으로 설정되어 있거나 낮은 복잡성의 비밀번호 정책이 설정되어 있는 경우 |
| **조치방법** | 높은 복잡성의 비밀번호 설정 기준을 확립하며, 계정 및 비밀번호의 체크 로직 추가 구현 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 관리자 및 사용자 계정의 비밀번호가 유추하기 어려운 값으로 설정되어 있거나 높은 복잡성의 비밀번호 정책이 설정되어 있는 경우
- **취약**: 관리자 및 사용자 계정의 비밀번호가 유추하기 쉬운 값으로 설정되어 있거나 낮은 복잡성의 비밀번호 정책이 설정되어 있는 경우

#### 경계 케이스 (Edge Case) 처리 방법
- 일반적인 경우 영향 없음
- 너무 엄격한 정책은 사용자 경험 저하
- 비밀번호 복잡성과 사용성의 균형 필요

#### 권장 설정값
- 최소 길이: 8자 이상
- 문자 종류: 2종류 이상 조합 + 최소 10자리, 또는 3종류 이상 조합 + 최소 8자리
- 문자 종류: 영문 대문자, 영문 소문자, 숫자, 특수문자
- 연속적인 숫자나 생일, 전화번호 등 추측하기 쉬운 개인정보 사용 금지

### 2. 점검 방법

#### Step 1: 취약한 계정 확인
```
웹 애플리케이션 내 추측 가능한 계정이나 비밀번호를 통하여 로그인이 가능한 계정이 존재 여부 확인
```

**취약한 ID 예시:**
- admin, administrator, manager, guest, root, user

**취약한 비밀번호 예시:**
- abcd, 1234, 1111, test, password, (빈 비밀번호), ID와 동일한 비밀번호

#### Step 2: 비밀번호 복잡성 요구사항 확인
```
회원가입 및 사용자 정보 수정 페이지 내 비밀번호 설정 시 높은 복잡도를 요구하는지 확인
```

### 3. 조치 방법

#### 1. 비밀번호 복잡성 정책 수립

**권장 정책:**
1. **문자 종류 조합**
   - 2종류 이상 조합 + 최소 10자리 이상
   - 또는 3종류 이상 조합 + 최소 8자리 이상

2. **추가 요구사항**
   - 연속적인 숫자나 생일, 전화번호 등 추측하기 쉬운 개인정보 사용 금지
   - ID와 유사한 비밀번호 금지
   - 비밀번호 유효기간 설정 (반기별 1회 이상 변경 권고)
   - 최근 사용 비밀번호 재사용 금지

#### 2. 비밀번호 검증 로직 구현

**Java 예시 (서버):**
```java
public static boolean isValid(String password) {
    if (password == null || password.length() < 8) {
        return false;
    }

    boolean hasUpperCase = !password.equals(password.toLowerCase());
    boolean hasLowerCase = !password.equals(password.toUpperCase());
    boolean hasDigit = password.matches(".*\\d.*");
    boolean hasSpecial = !password.matches("[A-Za-z0-9]*");

    int categoryCount = 0;
    if (hasUpperCase) categoryCount++;
    if (hasLowerCase) categoryCount++;
    if (hasDigit) categoryCount++;
    if (hasSpecial) categoryCount++;

    // 최소 3종류 이상 조합
    return categoryCount >= 3;
}
```

#### 3. 비밀번호 변경 실패 횟수 제한

```java
// 비밀번호 입력 실패 3회 초과 시 계정 잠금
if (failedAttempts >= 3) {
    account.setLocked(true);
    account.setLockTime(LocalDateTime.now());
    accountRepository.save(account);
    throw new AccountLockedException("계정이 잠겼습니다. 관리자에게 문의하세요.");
}
```

#### 4. 자주 사용되는 비밀번호 차단

```java
// 자주 사용되는 비밀번호 목록 (예: 10,000개 비밀번호)
private Set<String> commonPasswords = loadCommonPasswords();

public boolean isCommonPassword(String password) {
    return commonPasswords.contains(password.toLowerCase());
}
```

### 4. 참고 자료

**취약한 비밀번호 TOP 10 (2023):**
1. password
2. 123456
3. 12345678
4. qwerty
5. abc123
6. 123456789
7. 111111
8. 1234567
9. iloveyou
10. adobe123

**비밀번호 정책 규정 예시:**

```
[비밀번호 정책]

1. 길이: 최소 8자 이상
2. 조합: 다음 4종류 중 최소 3종류 포함
   - 영문 대문자 (A-Z)
   - 영문 소문자 (a-z)
   - 숫자 (0-9)
   - 특수문자 (!@#$%^&* 등)
3. 금지: ID와 동일한 비밀번호, 연속된 숫자, 생일, 전화번호
4. 유효기간: 90일
5. 재사용: 최근 3개 비밀번호 재사용 금지
6. 실패 제한: 5회 연속 실패 시 계정 잠금 (30분)
```

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.