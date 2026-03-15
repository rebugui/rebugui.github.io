---
title: "[2026 주요정보통신기반시설] W-46 SAM 파일 접근 통제 설정"
slug: "2026-주정통/W-46"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "SAM파일접근통제설정여부점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Windows
---

# W-46 SAM 파일 접근 통제 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | W-46 |
| **점검내용** | SAM파일접근통제설정여부점검 |
| **점검대상** | Windows NT, 2000, 2003, 2008, 2012, 2016, 2019, 2022 |
| **판단기준** | 양호: SAM파일접근권한에Administrator,System그룹만모든권한으로설정된경우 |
| **판단기준** | 취약: SAM파일접근권한에Administrator,System그룹외다른그룹에권한이설정된경우 |
| **조치방법** | SAM파일권한확인후Administrator,System그룹외다른그룹에설정된권한제거 |

---
## 상세 설명

### 1. 항목 개요

이 항목은 Windows의 핵심 계정 데이터베이스인 **SAM(Security Account Manager) 파일**에 대한 **접근 권한**이 적절하게 제한되어 있는지 점검합니다. SAM 파일에는 모든 로컬 사용자 계정과 암호 해시값이 저장되어 있어, 가장 중요한 보호 대상입니다.

### 2. 왜 이 항목이 필요한가요?

**계정 정보 유출 방지**
- **오프라인 공격 방어**: 공격자가 SAM 파일을 복사해 가면, 오프라인 상에서 'John the Ripper'나 'Hashcat' 등의 도구로 암호를 크랙할 수 있습니다.
- **Pass-the-Hash**: SAM 파일에서 추출한 NTLM 해시값을 이용해 비밀번호를 몰라도 시스템에 로그인하는 공격이 가능합니다.

**보안 위협 시나리오**
1. 공격자가 웹 서버의 취약점(웹쉘 업로드 등)으로 일반 사용자 권한 획득
2. `C:\Windows\System32\config` 폴더에 접근 시도
3. SAM 파일 권한이 허술하여(Users 그룹 읽기 허용) 파일을 외부로 유출
4. 공격자 PC에서 SAM 파일을 분석하여 Administrator 암호 획득

### 3. 점검 대상

- Windows NT, 2000, 2003, 2008, 2012, 2016, 2019, 2022 서버

### 4. 판단 기준

| 구분 | 기준 |
|------|------|
| **양호** | SAM 파일에 Administrator, SYSTEM 그룹만 접근 권한이 있고, 비인가 그룹(Everyone, Users 등)의 권한이 제거된 경우 |
| **취약** | SAM 파일에 일반 사용자 그룹의 접근 권한이 남아있는 경우 |

### 5. 점검 방법

#### 방법 1: 탐색기 확인
```
1. 경로 이동: `C:\Windows\System32\config`
2. `SAM` 파일 우클릭 > [속성] > [보안] 탭
3. 권한 목록 확인
   - **Administrators**: 모든 권한
   - **SYSTEM**: 모든 권한
   - (그 외 그룹이 있는지 확인)
```
*참고: 실행 중인 OS에서는 SAM 파일이 잠겨 있어 직접 접근이 불가능할 수 있으나, 백업된 SAM 파일(RegBack 등)이나 권한 설정 자체는 확인 가능합니다.*

#### 방법 2: 명령줄 확인 (ICACLS)
```cmd
icacls C:\Windows\System32\config\SAM
```

### 6. 조치 방법

불필요한 그룹(Users, Power Users, Everyone 등)의 권한을 제거하고, 관리자 및 시스템 권한만 유지합니다.

#### 방법 1: 탐색기 설정 (권장)
```
1. `C:\Windows\System32\config` 폴더로 이동
2. `SAM`, `SAM.LOG`, `SECURITY` 등 관련 파일 선택
3. 우클릭 > [속성] > [보안] > [편집]
4. **Administrators** 및 **SYSTEM**을 제외한 모든 그룹 선택 후 [제거]
5. 확인
```

### 7. 조치 시 주의사항

| 주의사항 | 설명 |
|----------|------|
| **백업 파일 관리** | `C:\Windows\System32\config\RegBack` 폴더나 별도의 백업 폴더에 있는 SAM 파일 복사본도 동일하게 권한을 점검해야 합니다. 공격자는 원본보다 백업본을 노리는 경우가 많습니다. |
| **VSS(섀도 복사본)** | Volume Shadow Copy를 통해 잠겨 있는 SAM 파일을 추출하는 기법(VSSAdmin 등)에 대비해, VSS 접근 권한 관리도 함께 고려해야 합니다. |

### 8. 참고 자료

- [Microsoft Docs: Security Account Manager](https://docs.microsoft.com/en-us/windows/win32/secauthn/security-account-manager-portal)

---

## 요약

**W-46 SAM파일접근통제설정**은 계정 정보가 담긴 '보물지도'를 지키는 것입니다. SAM 파일은 그 어떤 경우에도 일반 사용자에게 노출되어서는 안 됩니다.
