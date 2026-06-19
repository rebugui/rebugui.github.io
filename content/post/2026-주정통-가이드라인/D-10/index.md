---
title: "[2026 주요정보통신기반시설] D-10 원격에서 DB 서버로의 접속 제한"
slug: "2026-주정통/D-10"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "지정된IP주소만DB서버에접근가능하도록설정되어있는지점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Database
draft: true
---

# 원격에서 DB 서버로의 접속 제한

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | D-10 |
| **점검내용** | 지정된IP주소만DB서버에접근가능하도록설정되어있는지점검 |
| **점검대상** | Windows OS, Oracle DB, MySQL, Altibase, Tibero, PostgreSQL등 |
| **양호기준** | DB서버에지정된IP주소에서만접근가능하도록제한한경우 |
| **취약기준** | DB서버에지정된IP주소에서만접근가능하도록제한하지않은경우 |
| **조치방법** | DB서버에대해지정된IP주소에서만접근가능하도록설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: DB 서버에 지정된 IP 주소에서만 접근 가능하도록 제한한 경우
- **취약**: DB 서버에 지정된 IP 주소에서만 접근 가능하도록 제한하지 않은 경우

#### 경계 케이스 (Edge Case) 처리 방법
- **모든 IP 허용**: 취약 판단
- **특정 IP 제한**: 양호 판단
- **특정 대역(192.168.1.0/24) 제한**: 양호 판단

#### 권장 설정값
- **접근 제한**: 특정 IP 또는 네트워크 대역으로 제한
- **불필요한 원격 접속**: 차단

### 2. 점검 방법

#### Oracle DB

```bash
# sqlnet.ora 파일 확인
cat $ORACLE_HOME/network/admin/sqlnet.ora | grep tcp.validnode_checking
```

#### MySQL

```sql
-- 모든 호스트에서 접속 가능한 계정 확인
SELECT user, host FROM mysql.user WHERE host = '%';
```

#### Altibase

```sql
-- IP Access Control 설정 확인
iSQL> SELECT name, value1 FROM v$property WHERE name LIKE 'ACCESS_CONTROL_%';
```

#### PostgreSQL

```bash
# pg_hba.conf 파일 확인
cat /var/lib/pgsql/data/pg_hba.conf
```

### 3. 조치 방법

#### Windows OS - 방화벽 설정

1. 시작 > 제어판 > 시스템 및 보안 > Windows Defender 방화벽 > 고급 설정
2. 고급 보안이 포함된 Windows Defender 방화벽 > 인바운드 규칙
3. 원격 데스크톱 - 사용자 모드 (TCP-In) 속성 > 영역
4. 원격 IP 주소 > 다음 IP 주소 > 허용할 IP 추가

#### Oracle DB - sqlnet.ora 설정

```bash
# oracle 계정으로 로그인
su - oracle

# sqlnet.ora 파일 수정
vi $ORACLE_HOME/network/admin/sqlnet.ora
```

**설정 추가:**
```ini
tcp.validnode_checking = yes
tcp.invited_nodes = (127.0.0.1, 192.168.1.100, 192.168.1.0/24)
```

**Listener 재시작:**
```bash
$ORACLE_HOME/bin/lsnrctl stop
$ORACLE_HOME/bin/lsnrctl start
```

#### MySQL - Host 기반 권한 설정

```sql
-- 모든 클라이언트에서 접속 가능하도록 설정된 계정을 특정 IP로 변경
UPDATE user SET host = '접속 IP' WHERE user = '계정명' AND host = '%';

-- 또는 특정 IP 대역 허용
CREATE USER 'username'@'192.168.1.%' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON database.* TO 'username'@'192.168.1.%';

FLUSH PRIVILEGES;
```

#### Altibase - IP Access Control

```bash
# altibase.properties 파일 수정
vi $ALTIBASE_HOME/conf/altibase.properties
```

**설정 추가:**
```properties
# access list=deny    0.0.0.0       0.0.0.0
# list=permit         192.168.3.0   255.255.255.0
# list=permit         192.168.1.0   255.255.255.0
# list=permit         192.168.1.131 255.255.255.255
```

**설정 확인:**
```sql
iSQL> SELECT name, value1 FROM v$property WHERE name LIKE 'ACCESS_CONTROL_%';
```

#### PostgreSQL - pg_hba.conf 설정

```bash
# postgresql.conf 파일 수정
vi /var/lib/pgsql/data/postgresql.conf
```

```ini
listen_addresses = '192.168.1.100,localhost'
```

```bash
# pg_hba.conf 파일 수정
vi /var/lib/pgsql/data/pg_hba.conf
```

```
# IPv4 local connections:
host    all             all             192.168.1.0/24          md5
host    database        username        192.168.1.100/32        md5
```

```bash
# PostgreSQL 재시작
systemctl restart postgresql
```

#### Tibero - Listener IP 제한

```bash
# $TB_SID.tip 파일 수정
vi /tibero/tibero5/config/database.tip
```

**설정 추가:**
```properties
LSNR_INVITED_IP=192.168.1.1;192.168.2.0/24;192.1.0.0/16
```

**실시간 적용 (서버 재시작 없이):**
```sql
ALTER SYSTEM LISTENER PARAMETER RELOAD;
```

### 4. 참고 자료

#### IP 주소 기반 접속 제한의 중요성

**보안 위협:**
- 인터넷을 통한 무차별 대입 공격 노출
- 지리적 제한 없는 전 세계적 공격 표적
- 비인가 접속 시도 증가

**보안 효과:**
- 지리적 제한: 특정 위치에서만 접속 허용
- 네트워크 세그먼트 제한: 내부 네트워크에서만 접속 허용
- 공격 표적 축소: 인터넷에서의 무차별 공격 방지

#### 권장 접속 정책

1. **관리자 접속**: 특정 관리 PC에서만 허용
2. **애플리케이션 서버**: WAS 서버 IP에서만 허용
3. **백업 서버**: 백업 서버 IP에서만 허용
4. **모니터링 서버**: 모니터링 툴 서버 IP에서만 허용

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.