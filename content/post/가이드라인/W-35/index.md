---
title: "[2026 주요정보통신기반시설] W-35 익명 로그온 허용 제거"
slug: "2026-주정통/W-35"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "불필요한 ODBC/OLE-DB 데이터 소스와 드라이버 제거 여부 점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Windows
---

# W-35 익명 로그온 허용 제거

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | W-35 |
| **점검내용** | 불필요한 ODBC/OLE-DB 데이터 소스와 드라이버 제거 여부 점검 |
| **점검대상** | Windows NT, 2000, 2003, 2008, 2012, 2016, 2019, 2022 |
| **양호기준** | 시스템 DSN 부분의 데이터 소스를 현재 사용하고 있는 경우 |
| **취약기준** | 시스템 DSN 부분의 데이터 소스를 현재 사용하고 있지 않은 경우 |
| **조치방법** | 사용하지 않는 불필요한 ODBC 데이터 소스 제거 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: "SAM 계정 및 공유의 익명 열거 허용 안 함" 정책이 적용된 경우
- **취약**: 해당 정책이 설정되지 않거나 "허용"된 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| RestrictAnonymousSAM = 1 | 양호 | 익명 열거 차단됨 |
| RestrictAnonymousSAM = 0 | 취약 | 익명 열거 허용됨 |
| RestrictAnonymous = 2 | 양호 | 강화된 보안 (일부 호환성 주의) |
| RestrictAnonymous = 0 | 취약 | 익명 액세스 허용됨 |
| 도메인 컨트롤러 | 주의 | 추가 설정 확인 필요 |
| Everyone 권한 적용 허용 | 취약 | W-07 연계 조치 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| 로컬 보안 정책 | SAM 계정의 익명 열거 허용 안 함 | 사용 | 익명 사용자의 SAM 접근 차단 |
| 로컬 보안 정책 | SAM 계정 및 공유의 익명 열거 허용 안 함 | 사용 | 강화된 보안 |
| 레지스트리 | RestrictAnonymous | 1 | 익명 열거 제한 |
| 레지스트리 | RestrictAnonymousSAM | 1 | SAM 및 공유 열거 제한 |
| 로컬 보안 정책 | Everyone 권한 적용 허용 | 사용 안 함 | W-07 참조 |

### 2. 점검 방법

#### Windows 서버 점검

익명 사용자가 시스템의 계정 목록을 조회할 수 없도록 제한해야 합니다. 이는 무차별 대입 공격의 사전 정보 수집을 방지합니다.

```powershell
# 로컬 보안 정책 확인 (레지스트리)
Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Control\Lsa" -Name "RestrictAnonymous" -ErrorAction SilentlyContinue
Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Control\Lsa" -Name "RestrictAnonymousSAM" -ErrorAction SilentlyContinue
```

**양호 출력 예시:**
```text
RestrictAnonymous       : 1
RestrictAnonymousSAM    : 1
```

**취약 출력 예시:**
```text
RestrictAnonymous       : 0
또는
(속성 없음)
```

```cmd
# 로컬 보안 정책 확인 (GUI)
secpol.msc
# 로컬 정책 > 보안 옵션 > 다음 정책 확인:
# "네트워크 액세스: SAM 계정의 익명 열거 허용 안 함"
# "네트워크 액세스: SAM 계정 및 공유의 익명 열거 허용 안 함"
```

### 3. 조치 방법

#### Windows 서버 설정

1. **레지스트리로 익명 열거 제한 설정**
   ```powershell
   # RestrictAnonymous 설정
   Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Lsa" -Name "RestrictAnonymous" -Value 1 -Type DWord

   # RestrictAnonymousSAM 설정
   Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Lsa" -Name "RestrictAnonymousSAM" -Value 1 -Type DWord
   ```

2. **로컬 보안 정책 설정 (GUI)**
   ```
   1. 시작 > 실행 > secpol.msc
   2. 로컬 정책 > 보안 옵션
   3. "네트워크 액세스: SAM 계정 및 공유의 익명 열거 허용 안 함" 더블클릭
   4. [사용] 선택 > [확인]
   5. "네트워크 액세스: SAM 계정의 익명 열거 허용 안 함" 더블클릭
   6. [사용] 선택 > [확인]
   ```

3. **gpupdate로 정책 적용**
   ```cmd
   gpupdate /force
   ```

4. **시스템 재부팅 (필요시)**
   ```powershell
   Restart-Computer
   ```

### 4. 참고 자료

- [Microsoft Docs: RestrictAnonymous](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/network-access-do-not-allow-anonymous-enumeration-of-sam-accounts)
- [CIS Benchmark: 18.5.13.1 Ensure 'Network access: Do not allow anonymous enumeration of SAM accounts' is set to 'Enabled'](https://www.cisecurity.org/)
- [Microsoft Security Advisory: Anonymous Access Restrictions](https://docs.microsoft.com/ko-kr/windows/security/threat-protection/security-policy-settings/network-access-restrict-anonymous-access-to-named-pipes-and-shares)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.