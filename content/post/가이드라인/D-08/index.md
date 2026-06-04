---
title: "[2026 주요정보통신기반시설] D-08 안전한 암호화 알고리즘 사용"
slug: "2026-주정통/D-08"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "해시알고리즘SHA-256이상의암호화알고리즘을사용하는지점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Database
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

#### 기본 판단 기준
- **양호**: 해시 알고리즘 SHA-256 이상의 암호화 알고리즘을 사용하고 있는 경우
- **취약**: 해시 알고리즘 SHA-256 미만의 암호화 알고리즘을 사용하고 있는 경우

#### 경계 케이스 (Edge Case) 처리 방법
- **MD5 사용**: 취약 판단
- **SHA-1 사용**: 취약 판단
- **SHA-256 사용**: 양호 판단
- **SHA-512 사용**: 양호 판단

#### 권장 설정값
- **최소 알고리즘**: SHA-256 이상
- **권장 알고리즘**: SHA-512, bcrypt, Argon2

### 2. 점검 방법

#### Oracle DB

```sql
-- 비밀번호 암호화 버전 확인
SELECT username, password_versions FROM dba_users;
```

**결과 해석:**
- **11G**: SHA-1 사용 (취약)
- **12C**: SHA-512, AES 사용 (양호)

#### MSSQL

```sql
-- 저장된 비밀번호 해시 값 확인
SELECT name, password_hash FROM sys.sql_logins;
```

MSSQL 2012 이상에서는 32bit Salt를 적용한 SHA-512 해시 알고리즘을 사용하므로 양호합니다.

#### MySQL

```sql
-- 기본 인증 플러그인 확인
SHOW VARIABLES LIKE 'default_authentication_plugin';

-- 사용자별 인증 플러그인 확인
SELECT user, host, plugin FROM mysql.user;
```

**결과 해석:**
- **mysql_native_password**: 취약
- **caching_sha2_password**: 양호 (SHA-256 기반)
- **sha256_password**: 양호

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

**MySQL 8.0 이상으로 업그레이드 권장**

```bash
# my.cnf 설정 확인
[mysqld]
default_authentication_plugin=caching_sha2_password
```

**기존 사용자 비밀번호 재설정:**
```sql
-- SHA-256 기반 인증으로 비밀번호 변경
ALTER USER 'username'@'localhost' IDENTIFIED WITH caching_sha2_password BY 'newpassword';
```

**SHA-256 플러그인 사용 (MySQL 5.7):**
```sql
-- sha256_password 플러그인 활성화
INSTALL PLUGIN sha256_password SONAME 'sha256_password.so';

-- 사용자 생성
CREATE USER 'username'@'localhost' IDENTIFIED WITH sha256_password BY 'password';
```

#### PostgreSQL

**postgresql.conf 설정:**
```ini
# 암호화 알고리즘 설정
password_encryption = scram-sha-256
```

**비밀번호 변경:**
```sql
-- 비밀번호 변경 시 설정된 알고리즘으로 암호화
ALTER USER username WITH PASSWORD 'newpassword';
```

### 4. 참고 자료

#### 암호화 알고리즘별 특징

**Oracle DB:**
| 버전 | 알고리즘 | 보안 수준 |
|------|---------|----------|
| 10g | MD5 | 취약 (사용 권장 X) |
| 11g | SHA-1 | 취약 (사용 권장 X) |
| 12c | SHA-512, AES | 양호 |

**MSSQL:**
| 버전 | 알고리즘 | 보안 수준 |
|------|---------|----------|
| 2012 이상 | SHA-512 (32-bit Salt) | 양호 |

**MySQL:**
| 버전 | 알고리즘 | 보안 수준 |
|------|---------|----------|
| 5.7 이하 | 권장하지 않음 | 취약 |
| 8.0 이상 | SHA-256 기반 caching_sha2_password | 양호 |

#### 권장 암호화 알고리즘

**비밀번호 저장용 해시 알고리즘:**
1. **Argon2**: 최신 권장 알고리즘 (메모리 경연 쟁점)
2. **bcrypt**: 오랜 기간 검증된 안전한 알고리즘
3. **PBKDF2**: NIST 권장 알고리즘
4. **SHA-256/SHA-512**: 범용적으로 사용되는 안전한 알고리즘

**사용하지 말아야 할 알고리즘:**
1. **MD5**: 충돌 공격에 취약
2. **SHA-1**: 2017년 이후 권장하지 않음
3. **일방향 해시 없음**: 평문 저장은 절대 금지

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.