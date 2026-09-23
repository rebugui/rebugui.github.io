---
title: "[2026 주요정보통신기반시설] D-08 안전한 암호화 알고리즘 사용"
slug: "2026-주정통/D-08"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-09-23
description: "해시알고리즘SHA-256이상의암호화알고리즘을사용하는지점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Database
draft: false
---

# 안전한 암호화 알고리즘 사용

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | D-08 |
| **점검내용** | 해시알고리즘SHA-256이상의암호화알고리즘을사용하는지점검 |
| **점검대상** | Oracle DB, MSSQL, MySQL, Tibero, PostgreSQL등 |
| **양호기준** | 해시알고리즘SHA-256이상의암호화알고리즘을사용하고있는경우 |
| **취약기준** | 해시알고리즘SHA-256미만의암호화알고리즘을사용하고있는경우 |
| **조치방법** | SHA-256이상의암호화알고리즘적용 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준과 적용 범위
- 위의 가이드라인 원문은 DBMS 인증 해시 버전 확인을 위한 점검 기준입니다. **SHA-256이라는 이름만으로 애플리케이션 비밀번호 저장이 안전해지는 것은 아닙니다.**
- 비밀번호 저장에는 사용자별 고유 솔트와 조정 가능한 비용을 가진 전용 알고리즘을 사용해야 합니다. 빠른 일반 SHA-256/SHA-512 단독 해시는 오프라인 추측에 취약합니다.

#### 경계 케이스 (Edge Case) 처리 방법
- **MD5/SHA-1 기반의 오래된 DBMS 인증 방식**: 지원 버전과 인증 플러그인, 이전 계획 확인
- **SHA-256/SHA-512 기반의 DBMS 내장 인증 방식**: 버전·프로토콜·설정에 따라 점검하며 단순 알고리즘 이름만으로 애플리케이션 비밀번호 저장 방식까지 양호하다고 판단하지 않음

#### 권장 설정값
- DBMS 계정: 공급사가 지원하는 최신 인증 방식(예: PostgreSQL `scram-sha-256`)을 확인해 적용
- 애플리케이션 비밀번호: 고유 솔트와 적절한 비용을 설정한 Argon2id, scrypt, bcrypt 또는 PBKDF2 사용

### 2. 점검 방법

#### Oracle DB

```sql
-- 비밀번호 암호화 버전 확인
SELECT username, password_versions FROM dba_users;
```

**결과 해석:**
- **11G, 12C 등**: 지원 인증 버전과 클라이언트 호환성을 점검하고 공급사의 현재 권고에 맞는 버전으로 전환합니다. 해시 이름만으로 계정 보호 수준을 단정하지 않습니다.

#### MSSQL

```sql
-- SQL Server 로그인에 저장된 해시 버전 점검(값 자체는 민감 정보로 취급)
SELECT name, password_hash FROM sys.sql_logins;
```

SQL Server의 내부 로그인 해시 형식은 버전에 따라 다릅니다. 일반 애플리케이션에서 SHA-512를 직접 한 번 적용하는 방식과 혼동하지 마세요.

#### MySQL

```sql
-- 기본 인증 플러그인 확인
SHOW VARIABLES LIKE 'default_authentication_plugin';

-- 사용자별 인증 플러그인 확인
SELECT user, host, plugin FROM mysql.user;
```

**결과 해석:**
- **mysql_native_password**: 오래된 인증 플러그인으로 지원 버전과 이전 계획을 확인
- **caching_sha2_password/sha256_password**: MySQL의 인증 프로토콜·플러그인입니다. 일반적인 비밀번호 저장용 단일 SHA-256 해시로 구현하라는 뜻이 아닙니다.

### 3. 조치 방법

#### Oracle DB

**sqlnet.ora 파일 수정**

```bash
# Unix/Linux
vi $ORACLE_HOME/network/admin/sqlnet.ora

# Windows
메모장으로 %ORACLE_HOME%\network\admin\sqlnet.ora 열기
```

**설정 추가:**
```ini
SQLNET.ALLOWED_LOGON_VERSION_SERVER = 12
SQLNET.ALLOWED_LOGON_VERSION_CLIENT = 12
```

**변경 사항 적용:**
```bash
# Listener 재시작
lsnrctl reload

# 또는 데이터베이스 재시작
sqlplus / as sysdba
SQL> shutdown immediate
SQL> startup
```

#### MySQL

사용 중인 MySQL 버전과 클라이언트가 지원하는 인증 플러그인을 확인하고 공급사의 이전 절차를 따르세요. MySQL 8.4에서는 `caching_sha2_password`가 기본 인증 플러그인이고 `sha256_password`는 폐기 예정입니다. 미지원 버전에 플러그인 설치 명령을 그대로 적용하거나 인증 방식 이름만 보고 안전한 비밀번호 저장이라고 판단하지 마세요. 계정 변경 전 호환성과 복구 경로를 검증하고 비밀번호는 명령문·게시물에 평문으로 남기지 않습니다.

[MySQL 8.4 Reference Manual: Caching SHA-2 Pluggable Authentication](https://dev.mysql.com/doc/refman/8.4/en/caching-sha2-pluggable-authentication.html)

#### PostgreSQL

**postgresql.conf 설정:**
```ini
# 암호화 알고리즘 설정
password_encryption = scram-sha-256
```

**비밀번호 변경:**
`password_encryption`의 변경은 기존 비밀번호를 즉시 바꾸지 않습니다. 해당 역할의 SCRAM 지원 여부와 클라이언트 호환성을 확인한 뒤 안전한 관리 절차로 비밀번호를 갱신하세요. 비밀번호 값을 명령문이나 문서에 평문으로 기록하지 마세요.

### 4. 참고 자료

#### 암호화 알고리즘별 특징

**DBMS 인증 방식 점검 시 유의사항:**

Oracle, SQL Server, MySQL은 버전·패치 수준·인증 플러그인에 따라 계정 해시 형식이 달라질 수 있습니다. 위의 조회 결과와 공급사의 해당 버전 문서를 대조해 지원 여부와 이전 계획을 결정하세요. DBMS 인증 프로토콜에 포함된 SHA-2를 애플리케이션 비밀번호에 단독 적용하는 방식과 혼동하지 않습니다.

#### 권장 비밀번호 저장 알고리즘

애플리케이션 비밀번호에는 사용자별 고유 솔트와 충분한 비용을 적용한 **Argon2id**(우선), **scrypt**, **bcrypt**(기존 환경), **PBKDF2**(FIPS 요구 환경)를 사용합니다. 범용 SHA-256/SHA-512 단독 해시는 빠른 추측을 허용하므로 비밀번호 저장 알고리즘으로 권장하지 않습니다. 파일 무결성 검사에 쓰는 SHA-2 해시나 DBMS 인증 프로토콜과 구별해야 합니다.

**비밀번호 저장에 피할 방식:**
- MD5, SHA-1, SHA-256, SHA-512를 단독으로 한 번 해시하거나 평문을 저장하는 방식은 사용하지 않습니다.
- 알고리즘 이름뿐 아니라 솔트·비용 설정과 최신 라이브러리 지원 여부를 확인합니다.

[OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html) · [NIST SP 800-63B-4 비밀번호 검증기 요건](https://pages.nist.gov/800-63-4/sp800-63b.html#passwordver)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.