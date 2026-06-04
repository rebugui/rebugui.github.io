---
title: "[2026 주요정보통신기반시설] D-09 일정횟수의 로그인 실패 시에 대한 잠금 정책 설정"
slug: "2026-주정통/D-09"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "DBMS설정중일정횟수의로그인실패시계정잠금정책에대한설정이되어있는지점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Database
---

# 일정횟수의 로그인 실패 시에 대한 잠금 정책 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | D-09 |
| **점검내용** | DBMS설정중일정횟수의로그인실패시계정잠금정책에대한설정이되어있는지점검 |
| **점검대상** | Oracle DB, Altibase, Tibero등 |
| **양호기준** | 로그인시도횟수를제한하는값을설정한경우 |
| **취약기준** | 로그인시도횟수를제한하는값을설정하지않은경우 |
| **조치방법** | 로그인시도횟수제한값설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 로그인 시도 횟수를 제한하는 값을 설정한 경우
- **취약**: 로그인 시도 횟수를 제한하는 값을 설정하지 않은 경우

#### 경계 케이스 (Edge Case) 처리 방법
- **FAILED_LOGIN_ATTEMPTS = UNLIMITED**: 취약 판단
- **FAILED_LOGIN_ATTEMPTS 설정 안 함**: 취약 판단
- **FAILED_LOGIN_ATTEMPTS > 10**: 취약 판단 (너무 높음)

#### 권장 설정값
- **FAILED_LOGIN_ATTEMPTS**: 3~5회
- **PASSWORD_LOCK_TIME**: 1/1440 (1분) 또는 UNLIMITED

### 2. 점검 방법

#### Oracle DB

```sql
-- PROFILE 설정 확인
SELECT profile, resource_name, limit
FROM dba_profiles
WHERE resource_name = 'FAILED_LOGIN_ATTEMPTS';

-- 사용자별 PROFILE 확인
SELECT username, profile FROM dba_users;
```

#### Altibase

```sql
-- 비밀번호 정책 확인
SELECT * FROM system_.sys_users_;
```

#### Tibero

```sql
-- PROFILE 설정 확인
SELECT * FROM dba_profiles
WHERE resource_name = 'FAILED_LOGIN_ATTEMPTS';
```

### 3. 조치 방법

#### Oracle DB

```sql
-- 실패 로그인 횟수 제한 설정
ALTER PROFILE DEFAULT LIMIT FAILED_LOGIN_ATTEMPTS 5;

-- 계정 잠금 시간 설정 (자동으로 해제되지 않음)
ALTER PROFILE DEFAULT LIMIT PASSWORD_LOCK_TIME UNLIMITED;

-- 또는 특정 일수 후 자동 해제
ALTER PROFILE DEFAULT LIMIT PASSWORD_LOCK_TIME 1; -- 1일 후 해제
```

#### Altibase

```sql
-- 실패 로그인 횟수 제한 설정
ALTER USER testuser LIMIT (FAILED_LOGIN_ATTEMPTS 5);
```

#### Tibero

```sql
-- PROFILE 생성
CREATE PROFILE prof LIMIT
    FAILED_LOGIN_ATTEMPTS 5
    PASSWORD_LOCK_TIME 1/1440;  -- 1분간 잠금

-- 사용자에게 PROFILE 적용
ALTER USER username PROFILE prof;
```

### 4. 참고 자료

#### 파라미터 설명

**FAILED_LOGIN_ATTEMPTS:**
- **의미**: 계정 잠금까지 허용되는 실패 횟수
- **권장값**: 3~5회
- **기본값**: UNLIMITED (무제한 - 취약)

**PASSWORD_LOCK_TIME:**
- **의미**: 계정이 잠금되는 기간
- **권장값**: 1/1440 (1분) 또는 1 (1일)
- **UNLIMITED**: 관리자가 수동으로 해제할 때까지 잠금

#### 보안 위협

**무차별 대입 공격(Brute Force):**
- 모든 가능한 조합을 시도하여 비밀번호 추측
- 로그인 실패 횟수 제한으로 방지 가능

**사전 대입 공격(Dictionary Attack):**
- 자주 사용되는 비밀번호 목록으로 시도
- 로그인 실패 횟수 제한으로 방지 가능

#### 잠긴 계정 해제 방법

**Oracle DB:**
```sql
-- 계정 잠금 해제
ALTER USER username ACCOUNT UNLOCK;
```

**Altibase:**
```sql
-- 계정 잠금 해제
ALTER USER username ACCOUNT UNLOCK;
```

**Tibero:**
```sql
-- 계정 잠금 해제
ALTER USER username ACCOUNT UNLOCK;
```

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.