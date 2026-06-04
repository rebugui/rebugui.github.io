---
title: "[2026 주요정보통신기반시설] D-26 데이터베이스의 접근, 변경, 삭제 등의 감사 기록이 기관의 감사 기록 적합하도록 설정"
slug: "2026-주정통/D-26"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "데이터베이스감사(Auditing)기록이기관의감사기록보관정책에적합하게설정되어있는지점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Database
---

# 데이터베이스의 접근, 변경, 삭제 등의 감사 기록이 기관의 감사 기록 적합하도록 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | D-26 |
| **점검내용** | 데이터베이스감사(Auditing)기록이기관의감사기록보관정책에적합하게설정되어있는지점검 |
| **점검대상** | Oracle DB, MSSQL, MySQL, PostgreSQL등 모든 DBMS |
| **양호기준** | 감사 기록이 기관의 정책에 맞게 보관되는 경우 |
| **취약기준** | 감사 기록이 부적절하게 보관되거나 감사가 비활성화된 경우 |
| **조치방법** | 데이터베이스 감사 활성화 및 적절한 보관 정책 설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 감사 기록이 기관의 정책에 맞게 보관되는 경우
- **취약**: 감사 기록이 부적절하게 보관되거나 감사가 비활성화된 경우

#### 경계 케이스 (Edge Case) 처리 방법
- **감사 비활성화**: 취약 판단
- **감사 기록 보관 기간 미준수**: 취약 판단
- **감사 활성화 + 적절한 보관**: 양호 판단

#### 권장 설정값
- **감사 활성화**: 모든 중요 작업 감사
- **보관 기간**: 1년 이상 (일반), 3년 이상 (보안), 7년 이상 (법적 준수)

### 2. 점검 방법

#### Oracle DB

```sql
-- 감사 활성화 상태 확인
SELECT * FROM dba_audit_trail
WHERE rownum <= 10;

-- 감사 설정 확인
SELECT * FROM dba_obj_audit_opts;
SELECT * FROM dba_priv_audit_opts;
```

#### MSSQL

```sql
-- 감사 정보 확인
SELECT * FROM sys.server_audits;
SELECT * FROM sys.server_audit_specifications;
```

#### MySQL

```sql
-- 일반 쿼리 로그 확인
SHOW VARIABLES LIKE 'general_log%';

-- 감사 플러그인 확인 (MySQL Enterprise)
SHOW PLUGINS WHERE Name = 'audit_log';
```

#### PostgreSQL

```sql
-- 로그 설정 확인
SHOW log_statement;
SHOW logging_collector;
```

### 3. 조치 방법

#### Oracle DB

```sql
-- 감사 활성화
AUDIT ALL BY username BY ACCESS;

-- 특정 권한 감사
AUDIT CREATE ANY TABLE, DROP ANY TABLE BY ACCESS;

-- 감사 기록 확인
SELECT * FROM dba_audit_trail
WHERE username = 'username'
ORDER BY timestamp DESC;
```

#### MSSQL

```sql
-- 감사 활성화
CREATE SERVER AUDIT audit_name TO FILE (FILEPATH = 'C:\Audit\');

-- 감사 사양 생성
CREATE SERVER AUDIT SPECIFICATION audit_spec
FOR SERVER AUDIT audit_name
ADD (SUCCESSFUL_LOGIN_GROUP);

-- 감사 활성화
ALTER SERVER AUDIT audit_name WITH (STATE = ON);
```

#### MySQL

```sql
-- 일반 쿼리 로그 활성화
SET GLOBAL general_log = 'ON';

-- 감사 플러그인 설치 (MySQL Enterprise)
INSTALL PLUGIN audit_log SONAME 'audit_log.so';
```

#### PostgreSQL

```sql
-- postgresql.conf 설정
shared_preload_libraries = 'pgaudit'
logging_collector = on
log_directory = 'pg_log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_statement = 'all'  -- none, ddl, mod, all
```

### 4. 참고 자료

#### 감사 기록 내용

**최소 항목:**
1. 사용자 식별자
2. 접속 시간
3. 수행한 작업
4. 접근한 객체
5. 성공/실패 여부
6. IP 주소

#### 감사 로그 보관 정책

**로그 로테이션:**
```bash
# Oracle Listener 로그 로테이션
lsnrctl SET LOG_STATUS ON

# 정기적 백업 및 삭제
# 주간, 월간 단위로 보관
```

**보관 기간 설정:**
- 일반 감사 로그: 1년 이상
- 보안 관련 로그: 3년 이상
- 법적 준수 필요: 7년 이상

#### 감사의 중요성

**보안 사고 조사:**
- 보안 사고 발생 시 원인 분석
- 증거 확보
- 재발 방지

**보안 위협 (미감사 시):**
- 보안 사고 조사 불가
- 규정 준수 위반
- 책임 소재 파악 불가

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.