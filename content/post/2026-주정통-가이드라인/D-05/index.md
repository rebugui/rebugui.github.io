---
title: "[2026 주요정보통신기반시설] D-05 비밀번호 재사용에 대한 제약 설정"
slug: "2026-주정통/D-05"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "비밀번호변경시이전비밀번호를재사용할수없도록비밀번호제약설정이되어있는지점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Database
---

# 비밀번호 재사용에 대한 제약 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | D-05 |
| **점검내용** | 비밀번호변경시이전비밀번호를재사용할수없도록비밀번호제약설정이되어있는지점검 |
| **점검대상** | Oracle DB, Altibase, Tibero등 |
| **양호기준** | 비밀번호재사용제한설정을적용한경우 |
| **취약기준** | 비밀번호재사용제한설정을적용하지않은경우 |
| **조치방법** | PASSWORD_REUSE_TIME, PASSWORD_REUSE_MAX파라미터설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 비밀번호 재사용 제한 설정을 적용한 경우
- **취약**: 비밀번호 재사용 제한 설정을 적용하지 않은 경우

#### 경계 케이스 (Edge Case) 처리 방법
- **PASSWORD_REUSE_MAX = UNLIMITED**: 취약 판단
- **PASSWORD_REUSE_TIME = UNLIMITED**: 양호 판단 (영구적 재사용 금지)
- **PASSWORD_REUSE_MAX < 5**: 취약 판단

#### 권장 설정값
- **PASSWORD_REUSE_TIME**: 365일 (또는 UNLIMITED)
- **PASSWORD_REUSE_MAX**: 10

### 2. 점검 방법

#### Oracle DB

```sql
-- 재사용 제한 설정 확인
SELECT * FROM dba_profiles
WHERE resource_name IN ('PASSWORD_REUSE_TIME', 'PASSWORD_REUSE_MAX');
```

#### Tibero

```sql
-- PROFILE 설정 확인
SELECT * FROM dba_profiles
WHERE resource_name IN ('PASSWORD_REUSE_TIME', 'PASSWORD_REUSE_MAX');
```

### 3. 조치 방법

#### Oracle DB

```sql
-- DEFAULT PROFILE 수정
ALTER PROFILE DEFAULT LIMIT
    password_reuse_time 365
    password_reuse_max 10;
```

#### Tibero

```sql
-- PROFILE 생성
CREATE PROFILE prof LIMIT
    password_reuse_time UNLIMITED
    password_reuse_max 10;

-- 사용자에게 프로파일 적용
ALTER USER <계정명> PROFILE prof;
```

### 4. 참고 자료

#### 비밀번호 재사용 제한 파라미터

**PASSWORD_REUSE_TIME:**
- 의미: 이전 비밀번호를 다시 사용할 수 없는 기간
- 단위: 일(Days)
- UNLIMITED: 영구적으로 재사용 불가

**PASSWORD_REUSE_MAX:**
- 의미: 지정된 횟수만큼 이전 비밀번호 재사용 불가
- 단위: 횟수

**보안 위협:**
- 형식적 비밀번호 변경 방지
- 비밀번호 노출 시 지속적인 위험 방지

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.