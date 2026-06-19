---
title: "[2026 주요정보통신기반시설] D-06 DB 사용자 계정을 개별적으로 부여하여 사용"
slug: "2026-주정통/D-06"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "DB접근시사용자별로서로다른계정을사용하여접근하는지점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Database
draft: true
---

# DB 사용자 계정을 개별적으로 부여하여 사용

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | D-06 |
| **점검내용** | DB접근시사용자별로서로다른계정을사용하여접근하는지점검 |
| **점검대상** | Oracle DB, MSSQL, MySQL, Altibase, Tibero, PostgreSQL등 |
| **양호기준** | 사용자별계정을사용하고있는경우 |
| **취약기준** | 공용계정을사용하고있는경우 |
| **조치방법** | 사용자별계정생성및권한부여 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 사용자별 계정을 사용하고 있는 경우
- **취약**: 공용 계정(Shared Account)을 사용하고 있는 경우

#### 경계 케이스 (Edge Case) 처리 방법
- **공용 계정 사용 중**: 취약 판단
- **개별 계정 부여 완료**: 양호 판단
- **공용 계정 삭제 완료**: 양호 판단

#### 권장 설정값
- **계정 정책**: 모든 사용자에게 개별 계정 부여
- **권한 부여**: 최소 권한 원칙 적용

### 2. 점검 방법

#### Oracle DB

```sql
-- 모든 계정 확인
SELECT username FROM dba_users ORDER BY username;
```

#### MSSQL

```sql
-- 로그인 계정 확인
SELECT name FROM sys.server_principals WHERE type = 'S';
```

#### MySQL

```sql
-- 사용자 계정 확인
SELECT user, host FROM mysql.user;
```

#### Altibase

```sql
-- 계정 확인
SELECT * FROM system_.sys_users_;
```

#### Tibero

```sql
-- 계정 확인
SELECT * FROM dba_users;
```

#### PostgreSQL

```sql
-- 모든 사용자 확인
SELECT * FROM pg_shadow;
-- 또는
\du
```

### 3. 조치 방법

#### Oracle DB

```sql
-- 공용 계정 삭제
DROP USER '공용 계정' CASCADE;

-- 사용자별 계정 생성
CREATE USER '<계정명>' IDENTIFIED BY '<비밀번호>';

-- 기본 권한 부여
GRANT connect, resource TO [계정명];

-- 또는 필요한 최소 권한만 부여
GRANT CREATE SESSION TO [계정명];
GRANT SELECT, INSERT, UPDATE, DELETE ON schema.table TO [계정명];
```

#### MSSQL

```sql
-- 공용 계정 삭제
EXEC sp_droplogin '공용 계정';

-- 로그인 생성
CREATE LOGIN '생성 계정' WITH PASSWORD = '비밀번호';

-- 데이터베이스 사용자 생성
CREATE USER '생성 계정' FOR LOGIN '생성 계정' WITH DEFAULT_SCHEMA = '생성 계정';

-- 데이터베이스 역할에 추가
EXEC sp_addrolemember 'db_owner', '생성 계정';
```

#### MySQL

```sql
-- 공용 계정 삭제
DROP USER <계정명>@<호스트명 또는 IP>;

-- 사용자 계정 생성
CREATE USER '<계정명>'@'<호스트명 또는 IP>' IDENTIFIED BY '비밀번호';

-- 특정 데이터베이스의 특정 테이블에 권한 부여
GRANT SELECT, INSERT ON DB이름.테이블명 TO '<계정명>'@'<호스트명 또는 IP>';

-- 특정 데이터베이스의 모든 테이블에 모든 권한 부여
GRANT ALL PRIVILEGES ON DB이름.* TO '<계정명>'@'<호스트명 또는 IP>';

FLUSH PRIVILEGES;
```

#### Altibase

```sql
-- 공용 계정 삭제
DROP USER <계정명> CASCADE;

-- 사용자별 계정 생성
CREATE USER <계정명> IDENTIFIED BY <비밀번호>;
```

#### Tibero

```sql
-- 공용 계정 삭제
DROP USER [삭제할 계정] CASCADE;

-- 사용자별 계정 생성
CREATE USER [계정명] IDENTIFIED BY [비밀번호];

-- 권한 부여
GRANT CONNECT, RESOURCE TO [계정명];
```

#### PostgreSQL

```sql
-- 불필요한 계정 삭제
DROP ROLE '삭제할 계정';

-- 계정 생성
CREATE USER '생성할 계정' WITH PASSWORD '비밀번호';

-- 권한 부여
ALTER ROLE '계정명' SUPERUSER;
ALTER ROLE '계정명' CREATEDB;

-- 또는 특정 데이터베이스 권한 부여
GRANT ALL PRIVILEGES ON DATABASE "DB이름" TO "계정명";
```

### 4. 참고 자료

#### 공용 계정의 보안 위협

**감사 문제:**
- 로그에 개별 사용자 식별 불가
- 비인가 활동 추적 불가
- 보안 사고 시 책임 소재 파악 불가

**보안 문제:**
- 여러 사용자가 동일한 자격증명 사용
- 비밀번호 변경 및 관리 어려움
- 계정 유출 시 영향 범위 확대

#### 최소 권한 원칙

```sql
-- 읽기 전용 계정
CREATE USER app_read IDENTIFIED BY 'password';
GRANT SELECT ON schema.* TO app_read;

-- 쓰기 권한 계정
CREATE USER app_write IDENTIFIED BY 'password';
GRANT SELECT, INSERT, UPDATE ON schema.* TO app_write;

-- 관리자 계정
CREATE USER app_admin IDENTIFIED BY 'strong_password';
GRANT ALL PRIVILEGES ON schema.* TO app_admin;
```

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.