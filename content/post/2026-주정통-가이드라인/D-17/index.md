---
title: "[2026 주요정보통신기반시설] D-17 Audit Table은 데이터베이스 관리자 계정으로 접근하도록 제한"
slug: "2026-주정통/D-17"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "감사(Audit)Table에DBA또는관리자이외의계정이접근할수없도록설정되어있는지점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Database
---

# Audit Table은 데이터베이스 관리자 계정으로 접근하도록 제한

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | D-17 |
| **점검내용** | 감사(Audit)Table에DBA또는관리자이외의계정이접근할수없도록설정되어있는지점검 |
| **점검대상** | Oracle DB, Altibase, Tibero등 |
| **양호기준** | Audit Table에 DBA 또는 관리자만 접근 가능한 경우 |
| **취약기준** | Audit Table에 일반 사용자도 접근 가능한 경우 |
| **조치방법** | Audit Table 접근 권한을 DBA 또는 관리자로만 제한 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: Audit Table에 DBA 또는 관리자만 접근 가능한 경우
- **취약**: Audit Table에 일반 사용자도 접근 가능한 경우

#### 경계 케이스 (Edge Case) 처리 방법
- **일반 사용자에게 AUD$ 권한 부여**: 취약 판단
- **PUBLIC에 감사 테이블 권한**: 취약 판단
- **DBA만 접근 가능**: 양호 판단

#### 권장 설정값
- **Audit Table 접근**: DBA 또는 AUDIT_ADMIN 역할만 허용

### 2. 점검 방법

#### Oracle DB & Tibero

```sql
-- Audit Table 권한 확인
SELECT table_name, grantee, privilege
FROM dba_tab_privs
WHERE table_name IN ('AUD$', 'FGA_LOG$', 'DBA_AUDIT_TRAIL',
    'DBA_FGA_AUDIT_TRAIL', 'AUDIT_ACTIONS')
AND grantee NOT IN ('SYS', 'SYSTEM', 'DBA', 'AUDIT_ADMIN');
```

#### Altibase

```sql
-- Audit 테이블 접근 권한 확인
SELECT * FROM system_.sys_table_privs_
WHERE table_name LIKE 'AUDIT%'
AND grantee NOT IN ('SYSTEM', 'SYS');
```

### 3. 조치 방법

#### Oracle DB & Tibero

```sql
-- 불필요한 Audit Table 접근 권한 회수
REVOKE SELECT ON SYS.AUD$ FROM username;
REVOKE SELECT ON SYS.FGA_LOG$ FROM username;
REVOKE SELECT ON SYS.DBA_AUDIT_TRAIL FROM username;

-- DBA 역할에만 접근 권한 부여 확인
GRANT SELECT ON SYS.AUD$ TO DBA;
```

#### Altibase

```sql
-- Audit 테이블 접근 권한 제한
REVOKE SELECT ON system_.audit$_ FROM username;

-- 필요한 경우 DBA에게만 권한 부여
GRANT SELECT ON system_.audit$_ TO SYSTEM;
```

### 4. 참고 자료

#### 감사(Audit) Table의 중요성

**감사 기록 내용:**
- 접속 시도 (성공/실패)
- 권한 변경
- 스키마 수정 (DDL)
- 데이터 조작 (DML)
- 보안 정책 위반

**보안 위협:**
- 감사 정보 노출로 보안 사고 패턴 분석 가능
- 감사 로그 무단 삭제로 보안 사고 은폐 가능
- 감사 기록 조작으로 법적 증거 훼손 가능

#### 감사 데이터 보호

**접근 제한:**
- Audit Table은 DBA 또는 AUDIT_ADMIN 역할만 접근 가능
- 일반 사용자에게 감사 데이터 조회 권한 부여 금지
- 감사 데이터는 읽기 전용으로 유지

**백업 및 보관:**
```sql
-- 감사 데이터 정기적 백업
EXPDP system/password DIRECTORY=dp_dir DUMPFILE=audit.dmp TABLES=SYS.AUD$

-- 장기 보관을 위한 아카이빙
```

**데이터 무결성:**
- Audit Table은 수정 불가능하게 설정
- Trigger를 통한 감사 로그 수정 방지
- 감사 데이터 자체에 대한 감사 활성화

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.