---
title: "[2026 주요정보통신기반시설] W-11 로컬 로그온 허용"
slug: "2026-주정통/W-11"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "불필요한계정의로컬로그온을허용여부점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Windows
---

# W-11 로컬 로그온 허용

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | W-11 |
| **점검내용** | 불필요한계정의로컬로그온을허용여부점검 |
| **점검대상** | Windows NT, 2000, 2003, 2008, 2012, 2016, 2019, 2022 |
| **양호기준** | 로컬로그온허용정책에Administrators,IUSR_만존재하는경우 |
| **취약기준** | 로컬로그온허용정책에Administrators,IUSR_외다른계정및그룹이존재하는경우 |
| **조치방법** | Administrators,IUSR_외다른계정및그룹의로컬로그온제한 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 로컬 로그온 허용 정책에 Administrators, IUSR_ 만 존재하는 경우
- **취약**: 로컬 로그온 허용 정책에 Administrators, IUSR_ 외 다른 계정 및 그룹이 존재하는 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| 서비스 계정 | 주의 | 서비스 실행을 위한 계정인지 확인 필요 |
| 백업 소프트웨어 계정 | 주의 | 백업을 위해 필요한 경우 예외 가능 |
| 도메인 컨트롤러 | 양호 | 도메인 컨트롤러에서는 추가 계정이 필요할 수 있음 |
| 관리자 그룹 | 양호 | Administrators 그룹은 기본 포함 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| 일반 서버 | 로컬 로그온 허용 | Administrators, IUSR_ | 최소 권한 원칙 |
| 웹 서버 | 로컬 로그온 허용 | Administrators, IUSR_, IIS_IUSRS | IIS 서비스용 |
| 도메인 컨트롤러 | 로컬 로그온 허용 | Administrators, Enterprise Admins, Domain Admins | 도메인 관리 |

### 2. 점검 방법

#### Windows 서버 점검

로컬 로그온 허용 권한을 관리자 계정과 필수 서비스 계정으로 제한하여, 시스템 콘솔에 대한 물리적/직접 접근을 통제해야 합니다.

```bash
# PowerShell - 로컬 로그온 허용 정책 확인
secedit /export /cfg config.inf
Get-Content config.inf | Select-String "SeInteractiveLogonRight"
```

**양호 출력 예시:**
```text
SeInteractiveLogonRight = Administrators,IUSR_
```
필수 구성원만 포함된 경우 양호

**취약 출력 예시:**
```text
SeInteractiveLogonRight = Administrators,IUSR_,Users,Guests
```
불필요한 그룹이 포함된 경우 취약

### 3. 조치 방법

#### Windows 서버 설정

1. **로컬 보안 정책 설정 (GUI)**
   ```
   시작 > 제어판 > 관리 도구 > 로컬 보안 정책
   로컬 정책 > 사용자 권한 할당
   '로컬 로그온 허용' 더블클릭
   Administrators, IUSR_ 외 다른 계정 및 그룹 제거
   확인 클릭
   ```

2. **서비스 계정 확인**
   ```powershell
   # 특정 사용자로 실행되는 서비스 확인
   Get-WmiObject Win32_Service | Where-Object {
       $_.StartName -like "DOMAIN\username"
   } | Select-Object Name, StartName, State
   ```

3. **그룹 정책(GPO) 설정 (도메인 환경)**
   ```
   GPO 편집기(gpedit.msc 또는 gpmc.msc)
   컴퓨터 구성 > 정책 > Windows 설정 > 보안 설정 > 로컬 정책 > 사용자 권한 할당
   '로컬 로그온 허용' 설정
   필요한 계정 및 그룹만 추가
   ```

### 4. 참고 자료

- [Microsoft Docs: 사용자 권한 할당](https://docs.microsoft.com/ko-kr/windows/security/threat-protection/security-policy-settings/user-rights-assignment)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.