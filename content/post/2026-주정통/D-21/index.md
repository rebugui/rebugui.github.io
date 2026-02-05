---
title: "[2026 주요정보통신기반시설] D-21 인가되지 않은 GRANT OPTION 사용 제한"
slug: "2026-주정통/D-21"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "GRANT OPTION 권한이 인가되지 않은 사용자에게 부여되어 있는지 점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Database
---

# 인가되지 않은 GRANT OPTION 사용 제한

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | D-21 |
| **점검내용** | GRANT OPTION 권한이 인가되지 않은 사용자에게 부여되어 있는지 점검 |
| **점검대상** | Oracle DB, Tibero, PostgreSQL등 |
| **양호기준** | GRANT OPTION이 관리자에게만 부여된 경우 |
| **취약기준** | GRANT OPTION이 일반 사용자에게도 부여된 경우 |
| **조치방법** | 일반 사용자의 GRANT OPTION 권한 회수 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: GRANT OPTION이 관리자에게만 부여된 경우
- **취약**: GRANT OPTION이 일반 사용자에게도 부여된 경우

#### 경계 케이스 (Edge Case) 처리 방법
- **일반 사용자에게 GRANT OPTION**: 취약 판단
- **관리자에게만 GRANT OPTION**: 양호 판단
- **권한 확산 방지됨**: 양호 판단

#### 권장 설정값
- **GRANT OPTION**: 관리자만 부여

### 2. 점검 방법

#### Oracle DB & Tibero

```sql
-- GRANT OPTION이 부여된 권한 확인
SELECT grantee, owner, table_name, grantor, privilege
FROM dba_tab_privs
WHERE grantable = 'YES'
AND grantee NOT IN ('SYS', 'SYSTEM', 'DBA');

-- 시스템 권한의 GRANT OPTION 확인
SELECT grantee, privilege, admin_option
FROM dba_sys_privs
WHERE admin_option = 'YES'
AND grantee NOT IN ('SYS', 'SYSTEM', 'DBA');
```

#### PostgreSQL

```sql
-- GRANT OPTION 확인
SELECT grantor, grantee, table_schema, table_name, privilege, is_grantable
FROM information_schema.role_table_grants
WHERE is_grantable = 'YES';
```

### 3. 조치 방법

#### Oracle DB & Tibero

```sql
-- GRANT OPTION 제거 후 재부여
REVOKE <권한> ON <Object> FROM user;
GRANT <권한> ON <Object> TO user;

-- 예시
REVOKE SELECT ON sensitive_table FROM general_user;
GRANT SELECT ON sensitive_table TO general_user;
```

#### PostgreSQL

```sql
-- GRANT OPTION 제거
REVOKE GRANT OPTION FOR SELECT ON table_name FROM user;

-- 또는 권한 회수 후 재부여
REVOKE ALL PRIVILEGES ON table_name FROM user;
GRANT SELECT ON table_name TO user;
```

### 4. 참고 자료

#### GRANT OPTION의 이해

**GRANT OPTION:**
- 권한을 받은 사용자가 다른 사용자에게 동일한 권한을 부여할 수 있는 권한
- 권한 확산의 주요 경로

**보안 위협:**
- 권한 확산: 사용자가 다른 사용자에게 권한을 부여
- 권한 상승: 일반 사용자가 관리자 권한 획득 가능
- 감사 어려움: 권한 부여 경로 추적 불가

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.