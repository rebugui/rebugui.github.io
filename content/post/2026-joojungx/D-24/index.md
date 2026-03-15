---
title: "[2026 주요정보통신기반시설] D-24 Registry Procedure 권한 제한"
slug: "2026-주정통/D-24"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "Registry Procedure에 public 권한이 부여되어 있는지 점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Database
---

# Registry Procedure 권한 제한

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | D-24 |
| **점검내용** | Registry Procedure에 public 권한이 부여되어 있는지 점검 |
| **점검대상** | MSSQL |
| **양호기준** | Registry Procedure 실행 권한이 제한된 경우 |
| **취약기준** | Registry Procedure 실행 권한이 public에게 부여된 경우 |
| **조치방법** | public의 Registry Procedure 실행 권한 제거 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: Registry Procedure 실행 권한이 제한된 경우
- **취약**: Registry Procedure 실행 권한이 public에게 부여된 경우

#### 경계 케이스 (Edge Case) 처리 방법
- **public에 Registry Procedure 권한**: 취약 판단
- **관리자에게만 권한**: 양호 판단

#### 권장 설정값
- **Registry Procedure 권한**: 관리자만 부여

### 2. 점검 방법

```sql
-- public에게 부여된 Registry Procedure 권한 확인
SELECT USER_NAME(p.grantee_principal_id) AS principal_name,
    p.class_desc, p.permission_name
FROM sys.database_permissions p
INNER JOIN sys.database_principals d ON p.major_id = d.principal_id
WHERE d.name IN ('xp_regread', 'xp_regwrite', 'xp_regdeletekey')
AND USER_NAME(p.grantee_principal_id) = 'public';
```

### 3. 조치 방법

```sql
-- public 권한 회수
REVOKE EXECUTE ON master.dbo.xp_regread FROM public;
REVOKE EXECUTE ON master.dbo.xp_regwrite FROM public;
REVOKE EXECUTE ON master.dbo.xp_regdeletekey FROM public;
REVOKE EXECUTE ON master.dbo.xp_regdeletestring FROM public;
REVOKE EXECUTE ON master.dbo.xp_regdeletevalue FROM public;
REVOKE EXECUTE ON master.dbo.xp_regaddmultistring FROM public;
REVOKE EXECUTE ON master.dbo.xp_regremovemultistring FROM public;
```

### 4. 참고 자료

#### Registry Procedure 종류

**주요 Registry Procedure:**
- **xp_regread**: 레지스트리 값 읽기
- **xp_regwrite**: 레지스트리 값 쓰기
- **xp_regdeletekey**: 레지스트리 키 삭제
- **xp_regdeletestring**: 레지스트리 문자열 값 삭제
- **xp_regdeletevalue**: 레지스트리 값 삭제

**보안 위협:**
- 레지스트리 무단 수정으로 시스템 설정 변경
- 보안 설정 변경으로 시스템 취약화
- 악성코드 자동 실행 설정 가능

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.