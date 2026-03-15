---
title: "[2026 주요정보통신기반시설] D-11 DBA 이외의 인가되지 않은 사용자가 시스템 테이블에 접근할 수 없도록 설정"
slug: "2026-주정통/D-11"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "시스템테이블에일반사용자계정이접근할수없도록설정되어있는지점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Database
---

# DBA 이외의 인가되지 않은 사용자가 시스템 테이블에 접근할 수 없도록 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | D-11 |
| **점검내용** | 시스템테이블에일반사용자계정이접근할수없도록설정되어있는지점검 |
| **점검대상** | Oracle DB, MSSQL, MySQL, Altibase, Tibero, PostgreSQL등 |
| **양호기준** | 시스템테이블에DBA만접근가능하도록설정되어있는경우 |
| **취약기준** | 시스템테이블에DBA외일반사용자계정이접근가능하도록설정되어있는경우 |
| **조치방법** | 시스템테이블에일반사용자계정이접근할수없도록설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 시스템 테이블에 DBA만 접근 가능하도록 설정되어 있는 경우
- **취약**: 시스템 테이블에 DBA 외 일반 사용자 계정이 접근 가능하도록 설정되어 있는 경우

#### 경계 케이스 (Edge Case) 처리 방법
- **일반 사용자에게 SELECT_CATALOG_ROLE**: 취약 판단
- **PUBLIC에게 시스템 테이블 권한 부여**: 취약 판단
- **DBA 역할만 시스템 테이블 접근**: 양호 판단

#### 권장 설정값
- **시스템 테이블 접근**: DBA만 허용

### 2. 점검 방법

#### Oracle DB & Tibero

```sql
SELECT grantee, privilege, owner, table_name
FROM dba_tab_privs
WHERE (owner = 'SYS' OR table_name LIKE 'DBA\_%')
AND privilege <> 'EXECUTE'
AND grantee NOT IN ('PUBLIC', 'AQ_ADMINISTRATOR_ROLE', 'AQ_USER_ROLE',
'AURORA$JIS$UTILITY$', 'OSE$HTTP$ADMIN', 'TRACESVR', 'CTXSYS', 'DBA',
'DELETE_CATALOG_ROLE', 'EXECUTE_CATALOG_ROLE', 'EXP_FULL_DATABASE',
'GATHER_SYSTEM_STATISTICS', 'HS_ADMIN_ROLE', 'IMP_FULL_DATABASE',
'LOGSTDBY_ADMINISTRATOR', 'MDSYS', 'ODM', 'OEM_MONITOR', 'OLAPSYS',
'ORDSYS', 'OUTLN', 'RECOVERY_CATALOG_OWNER', 'SELECT_CATALOG_ROLE',
'SNMPAGENT', 'SYSTEM', 'WKSYS', 'WKUSER', 'WMSYS', 'WM_ADMIN_ROLE',
'XDB', 'LBACSYS', 'PERFSTAT', 'XDBADMIN')
AND grantee NOT IN (SELECT grantee FROM dba_role_privs WHERE granted_role = 'DBA')
ORDER BY grantee;
```

**결과 해석:** 결과가 나오지 않아야 양호

#### MSSQL

```sql
-- 시스템 테이블 접근 권한 확인
SELECT USER_NAME(p.grantee_principal_id) AS principal_name,
    d.class_desc, p.permission_name, d.name AS object_name
FROM sys.database_permissions p
INNER JOIN sys.database_principals d ON p.major_id = d.principal_id
WHERE d.type = 'S';
```

#### MySQL

```sql
-- 사용자 계정에 부여된 권한 확인
SHOW GRANTS FOR 'username'@'host';
```

#### Altibase

```sql
-- system_ 외 접근 계정 확인
SELECT * FROM system_.sys_tables_;
```

#### PostgreSQL

```sql
-- 사용자 및 역할 권한 정보 조회
SELECT * FROM information_schema.role_table_grants
WHERE table_schema IN ('pg_catalog', 'information_schema');
```

### 3. 조치 방법

#### Oracle DB & Tibero

```sql
-- 불필요한 테이블 접근 권한 회수
REVOKE SELECT ON SYS.dba_users FROM username;
REVOKE SELECT ON SYS.dba_tables FROM username;
REVOKE ALL ON SYS.v_$session FROM username;
```

#### MSSQL

```sql
-- 시스템 테이블 접근 권한 제거
REVOKE SELECT ON sys.tables FROM username;
REVOKE SELECT ON sys.objects FROM username;
```

#### MySQL

```sql
-- 접근이 필요한 데이터베이스 및 테이블에만 권한 적용
GRANT SELECT, INSERT, UPDATE ON database.table TO 'username'@'host';

-- mysql 데이터베이스 접근 제한
REVOKE ALL PRIVILEGES ON mysql.* FROM 'username'@'host';
```

#### Altibase

```sql
-- 불필요한 계정 접근 해제
REVOKE SELECT ON system_.sys_users_ FROM username;
```

#### PostgreSQL

```sql
-- pg_catalog, information_schema 스키마 접근 권한 제거
REVOKE ALL ON ALL TABLES IN SCHEMA pg_catalog FROM username;
REVOKE ALL ON ALL TABLES IN SCHEMA information_schema FROM username;
```

### 4. 참고 자료

#### 시스템 테이블의 중요성

**시스템 테이블(Meta Tables) 포함 정보:**
- 사용자 계정 정보
- 테이블 구조
- 권한 정보
- 시스템 설정
- 감사 로그

**보안 위협:**
- 메타 정보 유출로 전체 시스템 구조 노출
- 사용자 권한 정보 노출로 권한 상승 공격 가능
- 시스템 설정 변경으로 서비스 거부 가능
- 감사 로그 조작으로 보안 사고 은폐 가능

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.