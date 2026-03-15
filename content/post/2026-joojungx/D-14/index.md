---
title: "[2026 주요정보통신기반시설] D-14 데이터베이스의 주요 설정파일, 비밀번호 파일 등과 같은 주요 파일들의 접근권한이 적절하게 설정"
slug: "2026-주정통/D-14"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "데이터베이스주요파일의접근권한이적절하게설정되어있는지점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Database
---

# 데이터베이스의 주요 설정파일, 비밀번호 파일 등과 같은 주요 파일들의 접근권한이 적절하게 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | D-14 |
| **점검내용** | 데이터베이스주요파일의접근권한이적절하게설정되어있는지점검 |
| **점검대상** | Oracle DB, MySQL, PostgreSQL, Cubrid등 |
| **양호기준** | DB관리자만접근가능하도록권한이설정된경우 |
| **취약기준** | 불필요한사용자도접근가능하도록권한이설정된경우 |
| **조치방법** | DB관리자만접근가능하도록파일권한변경 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: DB 관리자만 접근 가능하도록 권한이 설정된 경우
- **취약**: 불필요한 사용자도 접근 가능하도록 권한이 설정된 경우

#### 경계 케이스 (Edge Case) 처리 방법
- **파일 권한 777**: 취약 판단
- **其他人(all users) 읽기 권한**: 취약 판단
- **관리자 전용 권한(600/640)**: 양호 판단

#### 권장 설정값

| 파일 유형 | 권장 권한 (Unix/Linux) | 권장 권한 (Windows) |
|-----------|----------------------|-------------------|
| 설정 파일 | 640 (rw-r-----) 또는 600 | Administrators, SYSTEM, Owner 전용 |
| 디렉터리 | 750 (rwxr-x---) 또는 755 | Administrators, SYSTEM, Owner 전용 |
| 실행 파일 | 750 (rwxr-x---) | Administrators, SYSTEM |
| 비밀번호 파일 | 600 (rw-------) | Administrators만 |

### 2. 점검 방법

#### Oracle DB - Unix/Linux

```bash
# 실행 파일
ls -l $ORACLE_HOME/bin/oracle        # 권장: 755
ls -l $ORACLE_HOME/bin/*              # 권장: 750 (svrmgrl, lsnrctl 등)

# 네트워크 설정
ls -ld $ORACLE_HOME/network           # 권장: 755
ls -l $ORACLE_HOME/network/admin/*    # 권장: 644 (tnsnames.ora 등)

# 데이터베이스 설정
ls -l $ORACLE_HOME/dbs/init.ora       # 권장: 640
ls -l $ORACLE_HOME/dbs/init<SID>.ora  # 권장: 640
```

#### Oracle DB - SQL

```sql
-- 데이터베이스 파일 위치 확인
SELECT value FROM v$parameter WHERE name='spfile';
SELECT 'Control Files: '||value FROM v$parameter WHERE name='control_files';
SELECT 'Logfile: '||member FROM v$logfile;
SELECT 'Datafile: '||name FROM v$datafile;
```

#### MySQL

```bash
# 설정 파일 권한 확인
ls -l /etc/my.cnf
```

#### PostgreSQL

```bash
# 주요 설정 파일 권한 확인
ls -l $datadir/postgresql.conf
ls -l $datadir/pg_hba.conf
ls -l ~/.psql_history
```

### 3. 조치 방법

#### Oracle DB - Unix/Linux

```bash
# 네트워크 설정 파일
chmod 644 $ORACLE_HOME/network/admin/tnsnames.ora
chmod 644 $ORACLE_HOME/network/admin/sqlnet.ora
chmod 644 $ORACLE_HOME/network/admin/listener.ora

# 데이터베이스 설정 파일
chmod 640 $ORACLE_HOME/dbs/init<SID>.ora

# 비밀번호 파일
chmod 600 $ORACLE_HOME/dbs/orapw<SID>
```

#### Oracle DB - Windows

- orapw<SID> 파일의 접근 권한은 Administrators, SYSTEM, Owner에게만 부여
- 다른 그룹의 권한 제거

#### MySQL - Unix/Linux

```bash
# 설정 파일 권한 설정 (600 또는 640)
chmod 600 /etc/my.cnf
# 또는
chmod 640 /etc/my.cnf

# 각 홈 디렉터리의 my.cnf
chmod 600 ~/.my.cnf
```

#### MySQL - Windows

- 설정 파일의 접근 권한은 Administrators, SYSTEM, Owner에게만 부여
- 기타 다른 그룹의 권한 제거

#### PostgreSQL - Unix/Linux

```bash
# 환경설정 파일
chmod 640 $datadir/postgresql.conf

# DB 접속 통제 설정 파일
chmod 640 $datadir/pg_hba.conf
chmod 640 $datadir/pg_ident.conf

# 히스토리 파일
chmod 600 ~/.psql_history

# Log 파일
chmod 640 [log_directory]/pg_log/*.log
```

#### PostgreSQL - Windows

- 주요 환경설정 파일의 접근 권한은 Administrators, SYSTEM, Owner에게만 부여
- 기타 다른 그룹의 권한 제거

#### Cubrid

```bash
# 설정 파일 권한 설정 (600 또는 640)
chmod 640 $CUBRID_DATABASES/conf/cubrid.conf
# 또는
chmod 600 $CUBRID_DATABASES/conf/cubrid.conf
```

### 4. 참고 자료

#### 주요 파일 목록

**Oracle DB:**
- `$ORACLE_HOME/dbs/orapw<SID>` - 비밀번호 파일
- `$ORACLE_HOME/dbs/init<SID>.ora` - 초기화 파라미터 파일
- `$ORACLE_HOME/network/admin/listener.ora` - 리스너 설정
- `$ORACLE_HOME/network/admin/tnsnames.ora` - 접속 설명
- `$ORACLE_HOME/network/admin/sqlnet.ora` - 네트워크 설정

**MySQL:**
- `/etc/my.cnf` 또는 `/etc/mysql/my.cnf` - 설정 파일
- `/var/lib/mysql/` - 데이터 디렉터리
- `~/.my.cnf` - 사용자별 설정

**PostgreSQL:**
- `$datadir/postgresql.conf` - 서버 설정
- `$datadir/pg_hba.conf` - 클라이언트 인증
- `$datadir/pg_ident.conf` - 사용자 이름 매핑
- `~/.psql_history` - 명령어 히스토리

#### 보안 위협

**부적절한 파일 권한의 위험:**
- 비밀번호 파일 노출로 DB 무단 접근 가능
- 설정 파일 노출으로 시스템 구조 정보 유출
- 설정 파일 무단 변경으로 서비스 거부 가능

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.