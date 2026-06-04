---
title: "[2026 주요정보통신기반시설] D-01 기본계정의 비밀번호, 정책 등을 변경하여 사용"
slug: "2026-주정통/D-01"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "DBMS기본계정의초기비밀번호및권한정책을변경하여사용하는지점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Database
---

# 기본계정의 비밀번호, 정책 등을 변경하여 사용

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | D-01 |
| **점검내용** | DBMS기본계정의초기비밀번호및권한정책을변경하여사용하는지점검 |
| **점검대상** | Oracle DB, MSSQL, MySQL, Altibase, Tibero, PostgreSQL, Cubrid 등 |
| **양호기준** | 기본계정의초기비밀번호를변경하거나잠금설정한경우 |
| **취약기준** | 기본계정의초기비밀번호를변경하지않거나잠금설정을하지않은경우 |
| **조치방법** | 기본(관리자)계정의초기비밀번호및권한정책변경 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 기본 계정의 초기 비밀번호를 변경하거나 잠금 설정한 경우
- **취약**: 기본 계정의 초기 비밀번호를 변경하지 않거나 잠금 설정을 하지 않은 경우

#### 경계 케이스 (Edge Case) 처리 방법
- **초기 비밀번호 사용 중**: 취약 판단
- **계정 잠금(LOCK) 설정**: 양호 판단
- **비밀번호 변경 완료**: 양호 판단

#### 권장 설정값
- **기본 계정 비밀번호**: 초기 비밀번호에서 변경 완료
- **불필요한 기본 계정**: 잠금 또는 삭제

### 2. 점검 방법

#### Oracle DB
```sql
-- 기본 계정 사용 여부 및 정책 확인
SELECT USERNAME, ACCOUNT_STATUS, PROFILE FROM DBA_USERS;
```

#### MSSQL
```sql
-- sa 계정 확인
SELECT name, is_disabled FROM sys.server_principals WHERE name = 'sa';
```

#### MySQL
```sql
-- 사용자 계정 확인
SELECT user, host FROM mysql.user;
```

#### PostgreSQL
```bash
# postgres 계정으로 접속
sudo -u postgres psql
# 비밀번호 확인
\du
```

### 3. 조치 방법

#### Oracle DB

**기본 계정 비밀번호 변경**
```sql
-- 비밀번호 변경
ALTER USER <기본 계정명> IDENTIFIED BY <신규 비밀번호>;

-- 계정 잠금 설정
ALTER USER <기본 계정명> ACCOUNT LOCK;
```

**Oracle DB 기본 계정 정보:**

| User | Password | User | Password |
|------|----------|------|----------|
| scott | tiger | system | manager |
| dbsnmp | dbsnmp | sys | changeon_install |

#### MSSQL

```sql
-- sa 계정 비밀번호 변경
ALTER LOGIN sa WITH PASSWORD = '신규 비밀번호';

-- sa 계정 비활성화 (다른 계정 사용 시)
ALTER LOGIN sa DISABLE;
```

#### MySQL

**MySQL 8.0**
```sql
ALTER USER 'root'@'localhost' IDENTIFIED BY '신규 비밀번호';
FLUSH PRIVILEGES;
```

#### PostgreSQL

```bash
# postgres 계정 비밀번호 변경
sudo -u postgres psql
ALTER USER postgres WITH PASSWORD '신규 비밀번호';
\q
```

### 4. 참고 자료

#### DBMS별 기본 계정 및 초기 비밀번호

**Oracle:**
- sys/change_on_install
- system/manager
- scott/tiger

**MSSQL:**
- sa/{blank 또는 password}

**MySQL:**
- root/{blank 또는 root}

**PostgreSQL:**
- postgres/postgres

**보안 위협:**
- 초기 비밀번호 유출: DBMS 설치 시 기본으로 설정된 비밀번호는 인터넷에 공개
- 무단 접근 가능: 비인가자가 기본 계정과 초기 비밀번호로 쉽게 접근
- 데이터 유출 위험: 관리자 권한을 가진 기본 계정이 탈취되면 모든 데이터 접근

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.