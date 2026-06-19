---
title: "[2026 주요정보통신기반시설] D-25 주기적 보안 패치 및 벤더 권고 사항 적용"
slug: "2026-주정통/D-25"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "최신 보안 패치 및 벤더 권고 사항이 적용되어 있는지 점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Database
draft: true
---

# 주기적 보안 패치 및 벤더 권고 사항 적용

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | D-25 |
| **점검내용** | 최신 보안 패치 및 벤더 권고 사항이 적용되어 있는지 점검 |
| **점검대상** | Oracle DB, MSSQL, MySQL, PostgreSQL등 모든 DBMS |
| **양호기준** | 최신 보안 패치가 적용된 경우 |
| **취약기준** | 보안 패치가 미적용된 취약점이 존재하는 경우 |
| **조치방법** | 주기적 보안 패치 및 벤더 권고 사항 적용 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 최신 보안 패치가 적용된 경우
- **취약**: 보안 패치가 미적용된 취약점이 존재하는 경우

#### 경계 케이스 (Edge Case) 처리 방법
- **최신 버전 미사용**: 취약 판단
- **알려진 취약점 미패치**: 취약 판단
- **최신 보안 패치 적용**: 양호 판단

#### 권장 설정값
- **패치 주기**: 분기별 또는 벤더 권고 시 즉시

### 2. 점검 방법

#### Oracle DB

```sql
-- 버전 확인
SELECT banner FROM v$version WHERE banner LIKE 'Oracle%';

-- Patch Set 확인
SELECT * FROM v$version;
```

최신 버전: http://www.oracle.com/technetwork/database/enterprise-edition/downloads/index.html

#### MSSQL

```sql
-- 버전 확인
SELECT @@version;

-- 상세 버전 정보
SELECT SERVERPROPERTY('productversion') AS ProductVersion,
    SERVERPROPERTY('productlevel') AS ProductLevel,
    SERVERPROPERTY('edition') AS Edition;
```

최신 버전: https://support.microsoft.com/kb/321185

#### MySQL

```sql
-- 버전 확인
SELECT VERSION();
```

최신 버전: http://downloads.mysql.com/archives.php

### 3. 조치 방법

#### 패치 관리 절차

**1. 패치 모니터링**
- 벤더 보안 권고 사항 주기적 확인
- 보안 취약점 데이터베이스(CVE, NVD) 모니터링
- 벤더 보안 알림 구독

**2. 패치 테스트**
- 테스트 환경에서 패치 적용 테스트
- 애플리케이션 호환성 확인
- 성능 영향 평가

**3. 패치 적용**
- 유지보수 시간대에 패치 적용
- 전체 백업 후 패치 수행
- 패치 적용 결과 검증

**4. 문서화**
- 패치 적용 기록 유지
- 변경 사항 문서화
- 롤백 절차 준비

### 4. 참고 자료

#### 주요 벤더 보안 권고

| 벤더 | 보안 권고 URL |
|------|--------------|
| Oracle | https://www.oracle.com/security-alerts/ |
| Microsoft | https://msrc.microsoft.com/advisory |
| MySQL | http://www.oracle.com/technetwork/topics/security/ |
| PostgreSQL | https://www.postgresql.org/support/security/ |
| Tibero | 벤더 포털 확인 |

#### 보안 패치의 중요성

**보안 취약점 수정:**
- 알려진 보안 문제 해결
- 새로운 보안 기능 추가
- 안정성 향상: 버그 수정 및 성능 개선

**보안 위협 (미패치 시):**
- 알려진 취약점 악용으로 시스템 장악 가능
- 데이터 유출 및 파괴 위험
- 규정 준수 위반

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.