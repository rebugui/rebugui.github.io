---
title: "[2026 주요정보통신기반시설] D-03 비밀번호의 사용기간 및 복잡도를 기관의 정책에 맞도록 설정"
slug: "2026-주정통/D-03"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "기관정책에맞게비밀번호사용기간및복잡도설정이적용되어있는지점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Database
---

# 비밀번호의 사용기간 및 복잡도를 기관의 정책에 맞도록 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | D-03 |
| **점검내용** | 기관정책에맞게비밀번호사용기간및복잡도설정이적용되어있는지점검 |
| **점검대상** | Oracle DB, MSSQL, MySQL, Altibase, Tibero, PostgreSQL등 |
| **양호기준** | 기관정책에맞게비밀번호사용기간및복잡도설정이적용된경우 |
| **취약기준** | 기관정책에맞게비밀번호사용기간및복잡도설정이적용되지않은경우 |
| **조치방법** | 기관정책에맞게비밀번호사용기간및복잡도정책설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 기관 정책에 맞게 비밀번호 사용기간 및 복잡도 설정이 적용된 경우
- **취약**: 기관 정책에 맞게 비밀번호 사용기간 및 복잡도 설정이 적용되지 않은 경우

#### 경계 케이스 (Edge Case) 처리 방법
- **비밀번호 복잡도 정책 미설정**: 취약 판단
- **비밀번호 수명 무제한**: 취약 판단
- **복잡도 요구사항 미충족**: 취약 판단

#### 권장 설정값
- **비밀번호 최소 길이**: 8자 이상
- **문자 조합**: 영문 대소문자, 숫자, 특수문자 중 최소 3가지 조합
- **비밀번호 수명**: 90일

### 2. 점검 방법

#### Oracle DB
```sql
-- 프로파일 설정 확인
SELECT * FROM dba_profiles WHERE profile = 'DEFAULT';
```

#### MSSQL
```sql
-- 로그인별 비밀번호 정책 확인
SELECT name, is_policy_checked FROM sys.sql_logins;
```

#### MySQL
```sql
-- 비밀번호 정책 확인
SHOW VARIABLES LIKE 'validate_password%';
SHOW VARIABLES LIKE 'default_password_lifetime';
```

### 3. 조치 방법

#### Oracle DB

```sql
-- 비밀번호 정책 설정
ALTER PROFILE <프로파일명> LIMIT
    FAILED_LOGIN_ATTEMPTS 3
    PASSWORD_LIFE_TIME 90
    PASSWORD_REUSE_TIME 30
    PASSWORD_VERIFY_FUNCTION verify_function
    PASSWORD_GRACE_TIME 5;
```

#### MySQL

```sql
-- 비밀번호 정책 설정
SET GLOBAL validate_password.policy = 'MEDIUM';
SET GLOBAL validate_password.length = 8;
SET GLOBAL validate_password.mixed_case_count = 1;
SET GLOBAL validate_password.number_count = 1;
SET GLOBAL validate_password.special_char_count = 1;
SET GLOBAL default_password_lifetime = 90;
```

### 4. 참고 자료

#### 비밀번호 정책 구성 요소

**비밀번호 복잡도:**
- 최소 길이: 8자 이상
- 문자 종류: 영문 대문자, 소문자, 숫자, 특수문자 중 최소 3가지 조합
- 사용자명과 상이성

**비밀번호 수명:**
- 사용 기간: 90일
- 만료 경고 기간: 7일
- 변경 강제

**보안 위협:**
- 무차별 대입 공격
- 사전 대입 공격
- 비밀번호 크래킹

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.