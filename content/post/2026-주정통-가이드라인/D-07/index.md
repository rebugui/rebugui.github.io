---
title: "[2026 주요정보통신기반시설] D-07 root 권한으로 서비스 구동 제한"
slug: "2026-주정통/D-07"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "서비스구동시root계정또는root권한으로구동되는지점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Database
draft: true
---

# root 권한으로 서비스 구동 제한

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | D-07 |
| **점검내용** | 서비스구동시root계정또는root권한으로구동되는지점검 |
| **점검대상** | Oracle DB, MySQL, Altibase, Cubrid등 |
| **양호기준** | DBMS가root계정또는root권한이아닌별도의계정및권한으로구동되고있는경우 |
| **취약기준** | DBMS가root계정또는root권한으로구동되고있는경우 |
| **조치방법** | DBMS구동계정변경 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: DBMS가 root 계정 또는 root 권한이 아닌 별도의 계정 및 권한으로 구동되고 있는 경우
- **취약**: DBMS가 root 계정 또는 root 권한으로 구동되고 있는 경우

#### 경계 케이스 (Edge Case) 처리 방법
- **root로 구동 중**: 취약 판단
- **전용 일반 계정으로 구동**: 양호 판단
- **프로세스 소유자가 DBMS 전용 계정**: 양호 판단

#### 권장 설정값
- **Oracle DB**: oracle 사용자로 구동
- **MySQL**: mysql 사용자로 구동
- **Altibase**: altibase 사용자로 구동
- **Cubrid**: cubrid 사용자로 구동

### 2. 점검 방법

#### Oracle DB

```bash
# Oracle 프로세스 확인
ps -ef | grep ora_ | grep -v grep

# Oracle Listener 프로세스 사용자 확인
ps -ef | grep tnslsnr
```

#### MySQL

```bash
# MySQL 프로세스 확인
ps -ef | grep mysqld

# MySQL 설정 파일에서 사용자 확인
cat /etc/my.cnf | grep user
# 또는
cat /etc/my.cnf.d/mysql-server.cnf | grep user
```

#### Altibase

```bash
# Altibase 프로세스 확인
ps -ef | grep altibase | grep -v grep

# Altibase 디렉터리 소유자 확인
ls -ld $ALTIBASE_HOME
```

#### Cubrid

```bash
# Cubrid 프로세스 확인
ps -ef | egrep 'cub_master|cub_broker|cub_manager' | grep -v grep
```

### 3. 조치 방법

#### Oracle DB

```bash
# Oracle 사용자로 전환
su - oracle

# Listener 중지
lsnrctl stop

# SQL*Plus로 DB 중지
sqlplus / as sysdba
SQL> shutdown immediate
SQL> exit

# Oracle 소프트웨어 디렉터리 권한 확인
ls -l $ORACLE_HOME

# root 소유의 파일이 있는 경우 oracle 사용자로 변경
chown -R oracle:oinstall $ORACLE_HOME
chmod -R 755 $ORACLE_HOME

# oracle 사용자로 Listener 시작
su - oracle
lsnrctl start

# 데이터베이스 시작
sqlplus / as sysdba
SQL> startup
SQL> exit
```

#### MySQL

```bash
# 설정 파일 편집
vi /etc/my.cnf
# 또는
vi /etc/my.cnf.d/mysql-server.cnf
```

```ini
[mysqld]
user=mysql
```

```bash
# MySQL 서비스 재시작
systemctl restart mysqld
# 또는
service mysqld restart

# 데이터 디렉터리 소유자 확인
ls -ld /var/lib/mysql

# mysql 사용자로 변경되어 있어야 함
chown -R mysql:mysql /var/lib/mysql
chmod 750 /var/lib/mysql
```

#### Altibase

```bash
# Altibase 전용 계정으로 소유자 변경
chown -R altibase:altibase $ALTIBASE_HOME

# 적절한 권한 부여
chmod -R 750 $ALTIBASE_HOME

# altibase 사용자로 전환
su - altibase

# Altibase 시작
server start
```

#### Cubrid

```bash
# 실행 중인 프로세스 확인
ps -ef | egrep 'cub_master|cub_broker|cub_manager' | grep -v grep

# 재설치 또는 데이터 이관 후 cubrid 계정으로 구동
su - cubrid

# 데이터베이스 시작
cubrid server start demodb

# 브로커 시작
cubrid broker start
```

### 4. 참고 자료

#### root 권한 구동의 위험성

**보안 위협:**
- DBMS 취약점 발견 시 공격자가 즉시 root 권한 획득
- 데이터베이스 파일뿐만 아니라 시스템 전체 파일 접근 가능
- 악성코드 실행 및 시스템 설정 변경 가능

**운영 위험:**
- 실수로 시스템 파일 삭제 가능
- 권한 문제로 보안 정책 위반
- 감사 및 규정 준수 문제

#### DBMS 전용 계정 생성

```bash
# Oracle 사용자 생성
groupadd -g 1000 oinstall
groupadd -g 1001 dba
useradd -u 1000 -g oinstall -G dba oracle
passwd oracle

# MySQL 사용자 생성
useradd -r -s /sbin/nologin mysql

# Altibase 사용자 생성
useradd altibase
passwd altibase

# Cubrid 사용자 생성
useradd cubrid
passwd cubrid
```

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.