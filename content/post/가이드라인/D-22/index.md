---
title: "[2026 주요정보통신기반시설] D-22 데이터베이스의 자원 제한 기능을 TRUE로 설정"
slug: "2026-주정통/D-22"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "데이터베이스자원제한(Resource Limit)기능이활성화되어있는지점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Database
---

# 데이터베이스의 자원 제한 기능을 TRUE로 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | D-22 |
| **점검내용** | 데이터베이스자원제한(Resource Limit)기능이활성화되어있는지점검 |
| **점검대상** | Oracle DB, Tibero등 |
| **양호기준** | resource_limit 파라미터가 TRUE로 설정된 경우 |
| **취약기준** | resource_limit 파라미터가 FALSE로 설정된 경우 |
| **조치방법** | resource_limit 파라미터를 TRUE로 설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: resource_limit 파라미터가 TRUE로 설정된 경우
- **취약**: resource_limit 파라미터가 FALSE로 설정된 경우

#### 경계 케이스 (Edge Case) 처리 방법
- **resource_limit = FALSE**: 취약 판단
- **resource_limit = TRUE**: 양호 판단
- **자원 제한 Profile 설정**: 양호 판단

#### 권장 설정값
- **resource_limit**: TRUE

### 2. 점검 방법

```sql
-- Oracle, Tibero
SELECT name, value FROM v$parameter WHERE name = 'resource_limit';

-- 값이 TRUE여야 양호
```

### 3. 조치 방법

```sql
-- 자원 제한 활성화
ALTER SYSTEM SET resource_limit = TRUE SCOPE = BOTH;

-- 또는 init.ora에 추가
RESOURCE_LIMIT = TRUE
```

### 4. 참고 자료

#### 자원 제한(Resource Limit) 기능

**제한 가능한 자원:**
- CPU 사용 시간
- 세션 지속 시간
- 연결 가능 세션 수
- 읽기 가능한 블록 수
- Private SGA 공간

**보안 위협 (비활성화 시):**
- 특정 사용자의 과도한 자원 사용으로 시스템 전체 성능 저하
- DoS 공격에 취약
- 자원 고갈로 서비스 거부 가능

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.