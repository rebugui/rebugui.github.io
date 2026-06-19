---
title: "[2026 주요정보통신기반시설] D-23 xp_cmdshell 사용 제한"
slug: "2026-주정통/D-23"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "xp_cmdshell 확장 저장 프로시저의 활성화 여부 및 권한 설정 점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Database
draft: true
---

# xp_cmdshell 사용 제한

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | D-23 |
| **점검내용** | xp_cmdshell 확장 저장 프로시저의 활성화 여부 및 권한 설정 점검 |
| **점검대상** | MSSQL |
| **양호기준** | xp_cmdshell이 비활성화되거나 public 실행 권한이 제거된 경우 |
| **취약기준** | xp_cmdshell이 활성화되고 public에게 실행 권한이 부여된 경우 |
| **조치방법** | xp_cmdshell 비활성화 또는 public 실행 권한 제거 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: xp_cmdshell이 비활성화되거나 public 실행 권한이 제거된 경우
- **취약**: xp_cmdshell이 활성화되고 public에게 실행 권한이 부여된 경우

#### 경계 케이스 (Edge Case) 처리 방법
- **xp_cmdshell 활성화 + public 권한**: 취약 판단
- **xp_cmdshell 비활성화**: 양호 판단
- **xp_cmdshell 활성화 + public 권한 제거**: 양호 판단

#### 권장 설정값
- **xp_cmdshell**: 비활성화 (0)
- **public 실행 권한**: 제거

### 2. 점검 방법

```sql
-- xp_cmdshell 활성화 여부 확인
SELECT name, value FROM sys.configurations WHERE name = 'xp_cmdshell';
```

**결과 해석:**
- value = 1: 활성화
- value = 0: 비활성화 (양호)

### 3. 조치 방법

#### xp_cmdshell 비활성화

**T-SQL로 설정:**
```sql
EXEC sp_configure 'show advanced options', 1;
RECONFIGURE;
EXEC sp_configure 'xp_cmdshell', 0;
RECONFIGURE;
```

#### xp_cmdshell 사용이 필요한 경우

**Step 1) public 실행 권한 제거**
```sql
REVOKE EXECUTE ON master.dbo.xp_cmdshell FROM public;
```

**Step 2) 서비스 계정의 sysadmin 권한 제거**
- SSMS > 보안 > 로그인 > 서비스 계정 선택
- 속성 > 서버 역할 > sysadmin 권한 제거

### 4. 참고 자료

#### xp_cmdshell의 이해

**기능:**
- Windows Command Prompt 명령 실행
- 운영체제 수준 작업 수행

**보안 위협:**
- SQL 주입을 통한 시스템 명령 실행 가능
- 공격자가 OS 권한 획득 가능
- 데이터베이스 서버 완전 장악 위험

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.