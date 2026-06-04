---
title: "[2026 주요정보통신기반시설] D-16 Windows 인증 모드 사용"
slug: "2026-주정통/D-16"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "MSSQL인증모드가Windows인증모드또는혼합모드중어떤것인지점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Database
---

# Windows 인증 모드 사용

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | D-16 |
| **점검내용** | MSSQL인증모드가Windows인증모드또는혼합모드중어떤것인지점검 |
| **점검대상** | MSSQL |
| **양호기준** | Windows인증모드또는혼합모드사용시sa계정비활성화한경우 |
| **취약기준** | 혼합모드사용시sa계정이활성화된경우 |
| **조치방법** | Windows인증모드사용또는sa계정비활성화 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: Windows 인증 모드 또는 혼합 모드 사용 시 sa 계정이 비활성화된 경우
- **취약**: 혼합 모드 사용 시 sa 계정이 활성화된 경우

#### 경계 케이스 (Edge Case) 처리 방법
- **Windows 인증 모드만 사용**: 양호 판단
- **혼합 모드 + sa 비활성화**: 양호 판단
- **혼합 모드 + sa 활성화**: 취약 판단

#### 권장 설정값
- **인증 모드**: Windows 인증 모드 (권장)
- **sa 계정**: 비활성화

### 2. 점검 방법

#### T-SQL로 인증 모드 확인

```sql
EXEC xp_instance_regread N'HKEY_LOCAL_MACHINE',
    N'Software\Microsoft\MSSQLServer\MSSQLServer',
    N'LoginMode';
```

**결과 해석:**
- 1: Windows 인증 모드 (양호)
- 2: 혼합 모드 (sa 계정 확인 필요)

#### sa 계정 상태 확인

```sql
SELECT name, is_disabled FROM sys.server_principals WHERE name = 'sa';
```

### 3. 조치 방법

#### Step 1) Windows 인증 모드 활성화

1. SQL Server Management Studio 실행
2. 해당 서버 우클릭 > 속성 > 보안
3. 서버 인증 > **Windows 인증 모드(W)** 선택
4. 확인 클릭
5. SQL Server 서비스 재시작

#### Step 2) sa 계정 비활성화 (혼합 모드 사용 시)

```sql
-- sa 계정 비활성화
ALTER LOGIN sa DISABLE;

-- 또는 sa 계정 이름 변경 (권장)
ALTER LOGIN sa WITH NAME = [다른이름];
```

#### Step 3) 강력한 암호 설정 (혼합 모드 사용 시)

```sql
-- sa 계정 비밀번호 변경
ALTER LOGIN sa WITH PASSWORD = '강력한비밀번호!@#123';
GO

-- 암호 정책 적용
ALTER LOGIN sa WITH CHECK_POLICY = ON, CHECK_EXPIRATION = ON;
GO
```

### 4. 참고 자료

#### 인증 모드 비교

| 특징 | Windows 인증 모드 | 혼합 모드 |
|------|------------------|----------|
| 보안 | 높음 (Kerberos) | 낮음 (SQL 인증 취약) |
| sa 계정 | 비활성화 | 활성화 가능 |
| 계정 관리 | AD 통합 | 별도 관리 |
| 암호 정책 | Windows 정책 | 별도 설정 필요 |
| 권장 여부 | 권장 | 비권장 |

#### Windows 인증 모드의 장점

**보안 강화:**
- Kerberos 프로토콜: 강력한 보안 제공
- 중앙 집중식 관리: Active Directory 통합
- 계정 잠금 및 암호 만료: Windows 보안 정책 활용
- sa 계정 공격 차단: SQL 계정 추측 공격 방지

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.