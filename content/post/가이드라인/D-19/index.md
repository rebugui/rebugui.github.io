---
title: "[2026 주요정보통신기반시설] D-19 OS_ROLES, REMOTE_OS_AUTHENTICATION, REMOTE_OS_ROLES를 FALSE로 설정"
slug: "2026-주정통/D-19"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "OS_ROLES, REMOTE_OS_AUTHENTICATION, REMOTE_OS_ROLES파라미터값이FALSE로설정되어있는지점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Database
---

# OS_ROLES, REMOTE_OS_AUTHENTICATION, REMOTE_OS_ROLES를 FALSE로 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | D-19 |
| **점검내용** | OS_ROLES, REMOTE_OS_AUTHENTICATION, REMOTE_OS_ROLES파라미터값이FALSE로설정되어있는지점검 |
| **점검대상** | Oracle DB |
| **양호기준** | 모든 파라미터가 FALSE로 설정된 경우 |
| **취약기준** | 하나 이상의 파라미터가 TRUE로 설정된 경우 |
| **조치방법** | 모든 파라미터를 FALSE로 설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 모든 파라미터가 FALSE로 설정된 경우
- **취약**: 하나 이상의 파라미터가 TRUE로 설정된 경우

#### 경계 케이스 (Edge Case) 처리 방법
- **OS_ROLES = TRUE**: 취약 판단
- **REMOTE_OS_AUTHENT = TRUE**: 취약 판단
- **REMOTE_OS_ROLES = TRUE**: 취약 판단
- **모든 파라미터 = FALSE**: 양호 판단

#### 권장 설정값
- **OS_ROLES**: FALSE
- **REMOTE_OS_AUTHENT**: FALSE
- **REMOTE_OS_ROLES**: FALSE

### 2. 점검 방법

```sql
-- OS_ROLES 확인
SHOW PARAMETER os_roles;
SELECT value FROM v$parameter WHERE name = 'os_roles';

-- REMOTE_OS_AUTHENTICATION 확인
SHOW PARAMETER remote_os_authent;
SELECT value FROM v$parameter WHERE name = 'remote_os_authent';

-- REMOTE_OS_ROLES 확인
SHOW PARAMETER remote_os_roles;
SELECT value FROM v$parameter WHERE name = 'remote_os_roles';
```

### 3. 조치 방법

#### init.ora 파일 수정

```bash
vi $ORACLE_HOME/admin/pfile/init.ora
```

**설정 추가/수정:**
```ini
OS_ROLES = FALSE
REMOTE_OS_AUTHENT = FALSE
REMOTE_OS_ROLES = FALSE
```

**인스턴스 재시작:**
```sql
SHUTDOWN IMMEDIATE;
STARTUP;
```

#### SPFILE 사용 시

Oracle 9i 이상에서는 SPFILE을 재생성해야 합니다:

```sql
-- 파라미터 변경
ALTER SYSTEM SET os_roles = FALSE SCOPE = SPFILE;
ALTER SYSTEM SET remote_os_authent = FALSE SCOPE = SPFILE;
ALTER SYSTEM SET remote_os_roles = FALSE SCOPE = SPFILE;

-- 인스턴스 재시작
SHUTDOWN IMMEDIATE;
STARTUP;
```

#### 설정 확인

```sql
-- 모든 파라미터 값 확인
SELECT name, value, description
FROM v$parameter
WHERE name IN ('os_roles', 'remote_os_authent', 'remote_os_roles');

-- 모든 값이 FALSE여야 양호
```

### 4. 참고 자료

#### 파라미터 설명

**OS_ROLES:**
- **FALSE (권장)**: Oracle 데이터베이스가 사용자 Role을 관리
- **TRUE**: OS가 Role을 부여 (보안 위험)

**REMOTE_OS_AUTHENT:**
- **FALSE (권장)**: 원격 OS 인증 비활성화
- **TRUE**: 원격 OS 인증 허용 (보안 위험)

**REMOTE_OS_ROLES:**
- **FALSE (권장)**: 원격 OS Role 비활성화
- **TRUE**: 원격 OS Role 허용 (보안 위험)

#### 보안 위협

**OS 의존적 인증의 위험:**
- OS 계정 탈취 시 데이터베이스 무단 접근 가능
- 원격 OS 인증을 통한 무단 접속 경로 제공
- Role 관리의 복잡성으로 보안 정책 위반 가능성 증가

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.