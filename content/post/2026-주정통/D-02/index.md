---
title: "[2026 주요정보통신기반시설] D-02 데이터베이스의 불필요 계정을 제거하거나, 잠금 설정 후 사용"
slug: "2026-주정통/D-02"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "DBMS에존재하는계정중DB관리나운용에사용하지않는불필요한계정이존재하는지점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Database
---

# 데이터베이스의 불필요 계정을 제거하거나, 잠금 설정 후 사용

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | D-02 |
| **점검내용** | DBMS에존재하는계정중DB관리나운용에사용하지않는불필요한계정이존재하는지점검 |
| **점검대상** | Oracle DB, MSSQL, MySQL, Altibase, Tibero, PostgreSQL, Cubrid등 |
| **양호기준** | 계정정보를확인하여불필요한계정이없는경우 |
| **취약기준** | 인가되지않은계정,퇴직자계정,테스트계정등불필요한계정이존재하는경우 |
| **조치방법** | 계정별용도를파악한후불필요한계정삭제 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 계정 정보를 확인하여 불필요한 계정이 없는 경우
- **취약**: 인가되지 않은 계정, 퇴직자 계정, 테스트 계정 등 불필요한 계정이 존재하는 경우

#### 경계 케이스 (Edge Case) 처리 방법
- **데모 계정(SCOTT, ADAMS 등)**: 취약 판단
- **퇴사자 계정**: 취약 판단
- **테스트 계정**: 운영 환경에서 취약 판단
- **계정 잠금(LOCK) 설정**: 양호 판단

#### 권장 설정값
- **불필요한 계정**: 삭제 또는 잠금 설정

### 2. 점검 방법

#### Oracle DB
```sql
-- 모든 사용자 확인
SELECT USERNAME, ACCOUNT_STATUS, PROFILE FROM DBA_USERS;
```

#### MSSQL
```sql
-- 모든 로그인 확인
SELECT name, type_desc, is_disabled FROM sys.server_principals WHERE type = 'S';
```

#### MySQL
```sql
-- 모든 사용자 확인
SELECT user, host FROM mysql.user;
```

#### PostgreSQL
```sql
-- 모든 사용자 확인
SELECT * FROM pg_user;
-- 또는
SELECT username, usesuper FROM pg_shadow;
```

### 3. 조치 방법

#### Oracle DB

```sql
-- 불필요한 계정 삭제
DROP USER [삭제할 계정] CASCADE;

-- 계정 잠금 설정
ALTER USER [계정명] ACCOUNT LOCK;
```

#### MSSQL

```sql
-- 불필요한 계정 삭제
DROP LOGIN [삭제할 계정];

-- 또는
EXEC sp_droplogin '삭제할 계정';
```

#### MySQL

```sql
-- 불필요한 계정 삭제
DROP USER '삭제할 계정'@'호스트명 또는 IP';
FLUSH PRIVILEGES;
```

#### PostgreSQL

```sql
-- 불필요한 계정 삭제
DROP ROLE '삭제할 계정';
-- 또는
DROP USER '삭제할 계정';
```

### 4. 참고 자료

#### Oracle DB 기본 데모 계정

| 계정명 | 초기 비밀번호 | 용도 |
|--------|--------------|------|
| SCOTT | TIGER | 데모 계정 |
| ADAMS | WOOD | 데모 계정 |
| CLARK | CLTH | 데모 계정 |
| BLAKE | PAPER | 데모 계정 |
| JONES | STEEL | 데모 계정 |
| PM | PM | 데모 계정 |

**보안 위협:**
- 데모 계정의 초기 비밀번호는 잘 알려져 있음
- 해커가 데모 계정으로 DB 접속 후 데이터 탈취 가능
- 불필요한 계정은 공격 표면 증가

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.