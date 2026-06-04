---
title: "[2026 주요정보통신기반시설] W-40 정책에 따른 시스템 로깅 설정"
slug: "2026-주정통/W-40"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "시스템 로깅 설정 여부 및 적절성 점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Windows
---

# W-40 정책에 따른 시스템 로깅 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | W-40 |
| **점검내용** | 시스템 로깅 설정 여부 및 적절성 점검 |
| **점검대상** | Windows NT, 2000, 2003, 2008, 2012, 2016, 2019, 2022 |
| **양호기준** | 감사 정책 권고 기준에 따라 감사 설정이 되어 있는 경우 |
| **취약기준** | 감사 정책 권고 기준에 따라 감사 설정이 되어 있지 않은 경우 |
| **조치방법** | 이벤트에 대한 감사 설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 주요 감사 항목(로그온, 계정 관리, 정책 변경 등)에 대해 성공(Success) 및 실패(Failure) 감사가 설정된 경우
- **취약**: 감사 정책이 설정되어 있지 않거나(감사 안 함), 필수 항목이 누락된 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| 성공만 감사 설정 | 주의 | 실패 시도 확인 불가 |
| 실패만 감사 설정 | 주의 | 정상 접속 로그 부족 |
| 성공+실패 모두 설정 | 양호 | 추적성 완비 |
| 감사 안 함 | 취약 | 로그 미기록 |
| 개체 액세스 감사 | 주의 | 로그 양 많음, 선택적 사용 |
| 권한 사용 감사 | 주의 | 로그 양 많음, 선택적 사용 |

#### 권장 설정값

| 분류 | 정책 항목 | 설정 권장 | 설명 |
|---|---|---|---|
| 계정 관리 | 계정 관리 감사 | 성공, 실패 | 사용자 생성/삭제, 패스워드 변경 |
| 로그온 | 로그온 이벤트 감사 | 성공, 실패 | 로컬/원격 접속 시도 |
| | 계정 로그온 이벤트 감사 | 성공, 실패 | 도메인 컨트롤러 인증 |
| 정책 변경 | 정책 변경 감사 | 성공, 실패 | 권한 할당, 감사 정책 변경 |
| 개체 액세스 | 개체 액세스 감사 | 실패(선택) | 파일/레지스트리 접근 |
| 권한 사용 | 권한 사용 감사 | 실패(선택) | 권한을 사용한 작업 |

### 2. 점검 방법

#### Windows 감사 정책 점검

시스템 이벤트를 로그에 기록하여, 해킹 사고 시 추적성을 확보해야 합니다.

```cmd
# 감사 정책 확인 (auditpol)
auditpol /get /category:*
```

**양호 출력 예시:**
```text
Category/Subcategory                      Setting
----------------------------------------- ---------
Account Logon ...                       Success and Failure
Account Management ...                   Success and Failure
Policy Change ...                        Success and Failure
...
```

**취약 출력 예시:**
```text
Category/Subcategory                      Setting
----------------------------------------- ---------
Account Logon ...                       No Auditing
Account Management ...                   No Auditing
```

```powershell
# PowerShell로 감사 정책 확인
Get- AuditPolicy | Format-Table
```

```cmd
# 로컬 보안 정책 확인 (GUI)
secpol.msc
# 로컬 정책 > 감사 정책
```

### 3. 조치 방법

#### Windows 감사 정책 설정

1. **감사 정책 설정 (PowerShell)**
   ```powershell
   # 계정 로그온 이벤트 감사 (성공, 실패)
   AuditPol /set /subcategory:"Logon" /success:enable /failure:enable

   # 계정 관리 감사 (성공, 실패)
   AuditPol /set /subcategory:"Account Management" /success:enable /failure:enable

   # 정책 변경 감사 (성공, 실패)
   AuditPol /set /subcategory:"Audit Policy Change" /success:enable /failure:enable

   # 권한 사용 감사 (실패만, 선택적)
   AuditPol /set /subcategory:"Use of privileged rights" /success:disable /failure:enable
   ```

2. **로컬 보안 정책 설정 (GUI)**
   ```
   1. 시작 > 실행 > secpol.msc
   2. 로컬 정책 > 감사 정책
   3. 정책 더블릴릭 > [다음 사항 감사]
   4. [v] 성공
   5. [v] 실패
   6. [확인]
   ```

3. **핵심 감사 항목 목록**
   ```
   [필수 권장 항목]
   - 계정 관리 감사: 성공, 실패
   - 로그온 이벤트 감사: 성공, 실패
   - 계정 로그온 이벤트 감사: 성공, 실패
   - 정책 변경 감사: 성공, 실패
   - 개체 액세스 감사: 실패(선택)
   - 권한 사용 감사: 실패(선택)
   ```

4. **gpupdate로 정책 적용**
   ```cmd
   gpupdate /force
   ```

### 4. 참고 자료

- [Microsoft Docs: 보안 감사 정책 설정 참조](https://docs.microsoft.com/ko-kr/windows/security/threat-protection/auditing/basic-security-audit-policy-settings)
- [CIS Benchmark: 18.9.70.1 Ensure 'Audit: Force audit policy subcategory settings (Windows Vista or later) to override audit policy category settings' is set to 'Enabled'](https://www.cisecurity.org/)
- [NIST SP 800-92: Guide to Computer Security Log Management](https://csrc.nist.gov/publications/detail/sp/800-92/final)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.