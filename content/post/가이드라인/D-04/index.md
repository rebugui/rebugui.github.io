---
title: "[2026 주요정보통신기반시설] D-04 데이터베이스 관리자 권한을 꼭 필요한 계정 및 그룹에 대해서만 허용"
slug: "2026-주정통/D-04"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "관리자권한이필요한계정및그룹에만관리자권한을부여하였는지점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Database
---

# 데이터베이스 관리자 권한을 꼭 필요한 계정 및 그룹에 대해서만 허용

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | D-04 |
| **점검내용** | 관리자권한이필요한계정및그룹에만관리자권한을부여하였는지점검 |
| **점검대상** | Oracle DB, MSSQL, MySQL, Altibase, Tibero, PostgreSQL, Cubrid등 |
| **양호기준** | 관리자권한이필요한계정및그룹에만관리자권한이부여된경우 |
| **취약기준** | 관리자권한이필요없는계정및그룹에관리자권한이부여된경우 |
| **조치방법** | 관리자권한이필요한계정및그룹에만관리자권한부여 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 관리자 권한이 필요한 계정 및 그룹에만 관리자 권한이 부여된 경우
- **취약**: 관리자 권한이 필요 없는 계정 및 그룹에 관리자 권한이 부여된 경우

#### 경계 케이스 (Edge Case) 처리 방법
- **일반 사용자에게 DBA 권한 부여**: 취약 판단
- **sysadmin 역할 멤버 과다**: 취약 판단
- **SUPER 권한 과다 부여**: 취약 판단

#### 권장 설정값
- **관리자 권한**: 필수 계정에만 부여

### 2. 점검 방법

#### Oracle DB

```sql
-- SYSDBA 권한 점검
SELECT username FROM v$pwfile_users
WHERE SYSDBA = 'TRUE' AND username != 'INTERNAL';
```

#### MSSQL

```sql
-- sysadmin 역할의 멤버 확인
EXEC sp_helpsrvrolemember 'sysadmin';
```

#### MySQL

```sql
-- SUPER 권한이 부여된 계정 확인
SELECT GRANTEE FROM INFORMATION_SCHEMA.USER_PRIVILEGES
WHERE PRIVILEGE_TYPE = 'SUPER';
```

### 3. 조치 방법

#### Oracle DB

```sql
-- 권한 회수
REVOKE <권한> FROM <계정명>;

-- 테이블별 권한 부여
GRANT <권한> ON <테이블명> TO <계정명>;
```

#### MSSQL

```sql
-- sysadmin 역할에서 제거
EXEC sp_dropsrvrolemember 'user_name', 'sysadmin';
```

#### MySQL

```sql
-- SUPER 권한 회수
REVOKE SUPER ON *.* FROM '<계정명>';
FLUSH PRIVILEGES;
```

### 4. 참고 자료

#### 관리자 권한 종류

**Oracle DB:**
- SYSDBA: 데이터베이스 시작, 종료, 복구 등 최고 권한
- DBA Role: 데이터베이스 관리자 권한

**MSSQL:**
- sysadmin: 서버의 모든 작업 수행 가능한 고정 서버 역할

**MySQL:**
- SUPER: 모든 관리 작업 수행 가능한 권한

**보안 위협:**
- 권한 남용
- 계정 유출 시 전체 데이터베이스 장악 위험
- 감사 어려움

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.