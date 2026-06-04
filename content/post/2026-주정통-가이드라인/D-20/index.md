---
title: "[2026 주요정보통신기반시설] D-20 인가되지 않은 Object Owner의 제한"
slug: "2026-주정통/D-20"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "Object Owner가 SYS, SYSTEM, 관리자 계정 등으로 제한되어 있는지 점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Database
---

# 인가되지 않은 Object Owner의 제한

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | D-20 |
| **점검내용** | Object Owner가 SYS, SYSTEM, 관리자 계정 등으로 제한되어 있는지 점검 |
| **점검대상** | Oracle DB, Altibase, Tibero, PostgreSQL등 |
| **양호기준** | Object Owner가 SYS, SYSTEM, 관리자 계정 등으로 제한된 경우 |
| **취약기준** | Object Owner가 일반 사용자에게도 존재하는 경우 |
| **조치방법** | Object Owner를 관리자 계정으로 제한 및 불필요한 권한 회수 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: Object Owner가 SYS, SYSTEM, 관리자 계정 등으로 제한된 경우
- **취약**: Object Owner가 일반 사용자에게도 존재하는 경우

#### 경계 케이스 (Edge Case) 처리 방법
- **일반 사용자가 Object Owner**: 취약 판단
- **관리자 계정만 Object Owner**: 양호 판단
- **응용프로그램 계정이 Object Owner**: 취약 판단

#### 권장 설정값
- **Object Owner**: SYS, SYSTEM, 관리자 계정만 허용

### 2. 점검 방법

#### Oracle DB

```sql
-- Object Owner 확인 쿼리
SELECT DISTINCT owner FROM dba_objects
WHERE owner NOT IN (
    'SYS', 'SYSTEM', 'MDSYS', 'CTXSYS', 'ORDSYS', 'ORDPLUGINS',
    'AURORA$JIS$UTILITY$', 'HR', 'ODM', 'ODM_MTR', 'OE',
    'APDBA', 'OLAPSYS', 'OSE$HTTP$ADMIN', 'OUTLN', 'LBACSYS',
    'MTSYS', 'PM', 'PUBLIC', 'QS', 'QS_ADM', 'QS_CB', 'QS_CBADM',
    'DBSNMP', 'QS_CS', 'QS_ES', 'QS_OS', 'QS_WS', 'RMAN',
    'SH', 'WKSYS', 'WMSYS', 'XDB'
)
AND owner NOT IN (
    SELECT grantee FROM dba_role_privs WHERE granted_role = 'DBA'
);
```

**결과 해석:** 결과가 반환되지 않으면 양호

#### Altibase

```sql
-- 일반 사용자 Object Owner 확인
SELECT user_name, object_id, privilege_id
FROM system_.sys_grant_object_
WHERE user_name NOT IN ('SYS', 'SYSTEM');
```

#### Tibero

```sql
-- Object별 소유자 확인
SELECT owner, object_name, object_type, created
FROM dba_objects
WHERE owner NOT IN ('SYS', 'SYSTEM', 'OUTLN')
ORDER BY owner, object_type;
```

#### PostgreSQL

```sql
-- Object 소유자 확인
SELECT n.nspname as schema,
       c.relname as object,
       u.usename as owner
FROM pg_class c
JOIN pg_namespace n ON c.relnamespace = n.oid
JOIN pg_user u ON c.relowner = u.usesysid
WHERE u.usename NOT IN ('postgres')
  AND c.relkind IN ('r', 'v', 'S')
ORDER BY u.usename, n.nspname, c.relname;
```

### 3. 조치 방법

#### Oracle DB

```sql
-- 특정 권한 회수
REVOKE <권한> ON <Object> FROM <user>;

-- 모든 권한 회수
REVOKE ALL PRIVILEGES ON <소유자>.<테이블명> FROM <사용자>;

-- 객체 소유권을 관리자 계정으로 변경
ALTER TABLE <기존소유자>.<테이블명> OWNER TO <관리자계정>;
```

#### Altibase

```sql
-- 특정 Object에 대한 권한 회수
REVOKE <권한> ON <Object> FROM <소유자>;

-- 모든 권한 회수
REVOKE ALL ON table_name FROM user_name;
```

#### Tibero

```sql
-- Object 권한 회수
REVOKE <권한> ON <Object> FROM <user>;

-- WITH GRANT OPTION으로 부여된 권한 회수
REVOKE ALL ON departments FROM scott CASCADE;

-- 테이블 소유권 변경
ALTER TABLE <기존소유자>.<테이블명> OWNER TO <새소유자>;
```

#### PostgreSQL

```sql
-- 테이블 소유권 변경
ALTER TABLE <스키마명>.<테이블명> OWNER TO <관리자계정>;

-- 뷰 소유권 변경
ALTER VIEW <스키마명>.<뷰명> OWNER TO <관리자계정>;

-- 시퀀스 소유권 변경
ALTER SEQUENCE <스키마명>.<시퀀스명> OWNER TO <관리자계정>;
```

### 4. 참고 자료

#### Object Owner의 이해

**Object Owner 권한:**
- 테이블, 뷰, 인덱스, 프로시저 등의 객체에 모든 권한 보유
- 객체 수정, 삭제 가능
- 다른 사용자에게 권한 부여 가능

**보안 위협:**
- 데이터 무결성 훼손: 인가되지 않은 사용자가 중요한 데이터를 임의로 수정, 삭제
- 권한 상승 경로 제공: 일반 사용자 계정을 통해 관리자 권한 획득 가능
- 정보 유출 위험: 중요한 데이터베이스 객체에 대한 무단 접근
- 감사 회피: 감사 로그를 회피하거나 삭제 가능

#### 조치 시 주의사항

- 응용 프로그램 영향 확인
- 백업 필수
- 서비스 중단 최소화
- 권한 사용 여부 확인

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.