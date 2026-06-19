---
title: "[2026 주요정보통신기반시설] D-18 응용프로그램 또는 DBA 계정의 Role이 Public으로 설정되지 않도록 조정"
slug: "2026-주정통/D-18"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "DBA Role이나중요한권한이 Public Role에부여되어있는지점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Database
draft: true
---

# 응용프로그램 또는 DBA 계정의 Role이 Public으로 설정되지 않도록 조정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | D-18 |
| **점검내용** | DBA Role이나중요한권한이 Public Role에부여되어있는지점검 |
| **점검대상** | Oracle DB, Altibase, Tibero, Cubrid등 |
| **양호기준** | DBA Role이나중요한권한이 Public Role에부여되어있지않은경우 |
| **취약기준** | DBA Role이나중요한권한이 Public Role에부여된경우 |
| **조치방법** | Public Role에서 DBA Role 및 중요한 권한 제거 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: DBA Role이나 중요한 권한이 Public Role에 부여되어 있지 않은 경우
- **취약**: DBA Role이나 중요한 권한이 Public Role에 부여된 경우

#### 경계 케이스 (Edge Case) 처리 방법
- **DBA Role이 Public에 부여**: 취약 판단
- **EXECUTE_CATALOG_ROLE이 Public에 부여**: 취약 판단
- **기본 CONNECT 권한만 Public에 부여**: 양호 판단

#### 권장 설정값
- **Public Role 권한**: 최소 권한만 부여

### 2. 점검 방법

#### Oracle DB

```sql
-- Public에 부여된 Role 확인
SELECT granted_role FROM dba_role_privs WHERE grantee = 'PUBLIC';

-- 특히 DBA Role이 Public에 부여되었는지 확인
SELECT granted_role FROM dba_role_privs
WHERE grantee = 'PUBLIC' AND granted_role = 'DBA';
```

#### Altibase

```sql
-- Object 권한, 시스템 권한이 Public에게 부여되어 있는지 확인
SELECT * FROM system_.sys_users_;
SELECT * FROM system_.sys_grant_object_;
SELECT * FROM system_.sys_grant_system_;

-- GRANTEE_ID가 0인 경우 Public에 부여된 권한
```

#### Tibero

```sql
-- 사용자 Role 부여 확인
SELECT * FROM dba_role_privs;
SELECT * FROM user_role_privs;
```

#### Cubrid

```sql
-- Public Role 권한 확인
-- 시스템 테이블에서 Public Role에 부여된 권한 확인
```

### 3. 조치 방법

#### Oracle DB

```sql
-- PUBLIC 그룹의 Role 권한 취소
REVOKE [Role name] FROM PUBLIC;

-- 예시: EXECUTE_CATALOG_ROLE 취소
REVOKE EXECUTE_CATALOG_ROLE FROM PUBLIC;

-- 예시: DBA Role이 PUBLIC에 부여된 경우 취소
REVOKE DBA FROM PUBLIC;
```

#### Altibase

```sql
-- 불필요 권한 회수
REVOKE <권한> ON <Object> FROM [계정명];

-- 예시
REVOKE SELECT ON system_table FROM PUBLIC;
```

#### Tibero

```sql
-- 불필요 권한 회수
REVOKE <권한> FROM [계정명];

-- Role 취소
REVOKE DBA FROM PUBLIC;
```

### 4. 참고 자료

#### Public Role의 이해

**Public Role:**
- 모든 데이터베이스 사용자가 기본적으로 가지는 Role
- Public에 부여된 권한은 모든 사용자가 상속

**보안 위협:**
- DBA Role이 Public에 부여되면 모든 사용자가 관리자 권한 획득
- 중요한 권한이 Public에 부여되면 권한 확산

#### 주요 Role 설명 (Oracle DB)

- **DBA**: 데이터베이스 관리자 권한 (최고 권한)
- **EXECUTE_CATALOG_ROLE**: 데이터 딕셔너리 조회 권한
- **DELETE_CATALOG_ROLE**: 데이터 딕셔너리 삭제 권한
- **SELECT_CATALOG_ROLE**: 데이터 딕셔너리 선택 권한

#### 모범 사례

**Public Role 최소 권한:**
- Public Role에는 기본적인 CONNECT 권한만 부여
- 시스템 테이블 접근 권한은 Public에서 제거
- EXECUTE 권한은 필요한 프로시저에만 부여

**권장 취소 권한:**
```sql
-- Oracle에서 권장되는 Public Role에서 취소할 권한
REVOKE EXECUTE ON sys.utl_file FROM PUBLIC;
REVOKE EXECUTE ON sys.utl_tcp FROM PUBLIC;
REVOKE EXECUTE ON sys.utl_smtp FROM PUBLIC;
REVOKE EXECUTE ON sys.utl_http FROM PUBLIC;
```

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.