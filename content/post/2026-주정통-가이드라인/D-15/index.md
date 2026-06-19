---
title: "[2026 주요정보통신기반시설] D-15 관리자 이외의 사용자가 오라클 리스너의 접속을 통해 리스너 로그 및 trace 파일에 대한 변경 제한"
slug: "2026-주정통/D-15"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "관리자이외의사용자가리스너로그및trace파일에접근할수있는지점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Database
draft: true
---

# 관리자 이외의 사용자가 오라클 리스너의 접속을 통해 리스너 로그 및 trace 파일에 대한 변경 제한

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | D-15 |
| **점검내용** | 관리자이외의사용자가리스너로그및trace파일에접근할수있는지점검 |
| **점검대상** | Oracle DB |
| **양호기준** | 관리자만리스너로그및trace파일에접근가능하도록권한이설정된경우 |
| **취약기준** | 일반사용자도리스너로그및trace파일에접근가능하도록권한이설정된경우 |
| **조치방법** | 관리자만접근가능하도록파일권한변경 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 관리자만 리스너 로그 및 trace 파일에 접근 가능하도록 권한이 설정된 경우
- **취약**: 일반 사용자도 리스너 로그 및 trace 파일에 접근 가능하도록 권한이 설정된 경우

#### 경계 케이스 (Edge Case) 처리 방법
- **파일 권한 644 이상**: 취약 판단
- **그룹/其他人 읽기 권한**: 취약 판단
- **관리자 전용 권한(600/640)**: 양호 판단

#### 권장 설정값
- **로그 파일**: 640 (rw-r-----) 또는 600 (rw-------)
- **Trace 파일**: 640 또는 600
- **디렉터리**: 750 (rwxr-x---)

### 2. 점검 방법

```bash
# Listener 로그 파일 권한 확인
ls -l $ORACLE_HOME/network/log/listener.log

# Trace 파일 권한 확인
ls -l $ORACLE_HOME/network/trace/listener*.trc

# 디렉터리 권한 확인
ls -ld $ORACLE_HOME/network/log
ls -ld $ORACLE_HOME/network/trace
```

### 3. 조치 방법

#### Step 1) 파일 소유자 확인

```bash
# oracle 사용자가 소유자인지 확인
ls -l $ORACLE_HOME/network/log/listener.log

# 출력 예: -rw-r----- 1 oracle oinstall ...
```

#### Step 2) 파일 권한 변경

```bash
# Listener 로그 파일
chmod 640 $ORACLE_HOME/network/log/listener.log
# 또는
chmod 600 $ORACLE_HOME/network/log/listener.log

# Trace 파일
chmod 640 $ORACLE_HOME/network/trace/*.trc
# 또는
chmod 600 $ORACLE_HOME/network/trace/*.trc

# 디렉터리 권한
chmod 750 $ORACLE_HOME/network/log
chmod 750 $ORACLE_HOME/network/trace
```

#### Step 3) ADMIN_RESTRICTIONS 설정

**listener.ora에 다음 설정 추가:**
```ini
ADMIN_RESTRICTIONS_<listener_name> = ON
```

이 설정은 LSNRCTL을 통한 리스너 설정 변경을 제한합니다.

#### Step 4) LOG_DIRECTORY 설정

**listener.ora에서 로그 디렉터리 지정:**
```ini
LOG_DIRECTORY_<listener_name> = /oracle/home/network/log
TRACE_DIRECTORY_<listener_name> = /oracle/home/network/trace
```

#### Step 5) Listener 재시작

```bash
# Listener 재시작
lsnrctl reload

# 또는
lsnrctl stop
lsnrctl start
```

### 4. 참고 자료

#### 파일 위치

```
$ORACLE_HOME/network/log/listener.log
$ORACLE_HOME/network/trace/listener.trc
$ORACLE_HOME/network/trace/<SID>_listener.trc
```

#### 로그 파일의 중요성

**listener.log:**
- 접속 시도 기록
- 성공/실패 기록
- IP 주소 정보
- 보안 사고 조사 자료

**trace 파일:**
- 상세한 동작 정보
- 오류 기록
- 문제 해결을 위한 디버깅 정보
- 성능 분석 자료

#### 로그 관리 정책

**로그 로테이션 설정:**
```bash
# Listener에서 로그 로테이션 설정
LSNRCTL> SET LOG_STATUS ON
LSNRCTL> SET LOG_FILE <listener_name>
```

**주기적 로그 백업 및 삭제:**
```bash
# Listener 로그 백업
cp $ORACLE_HOME/network/log/listener.log /backup/listener.log.$(date +%Y%m%d)

# 로그 초기화 (Listener 중지 후)
> $ORACLE_HOME/network/log/listener.log
```

#### 보안 위협

**부적절한 권한 설정 시 위험:**
- 감사 정보 노출로 접속 패턴 분석 가능
- 로그 파일 무단 삭제로 보안 사고 은폐 가능
- trace 파일 정보 노출로 시스템 내부 구조 유출

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.