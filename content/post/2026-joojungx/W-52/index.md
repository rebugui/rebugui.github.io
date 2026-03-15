---
title: "[2026 주요정보통신기반시설] W-52 Autologon 기능 제어"
slug: "2026-주정통/W-52"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "Autologon기능제어설정여부점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Windows
---

# W-52 Autologon 기능 제어

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | W-52 |
| **점검내용** | Autologon기능제어설정여부점검 |
| **점검대상** | Windows NT, 2000, 2003, 2008, 2012, 2016, 2019, 2022 |
| **판단기준** | 양호: AutoAdminLogon값이없거나0으로설정된경우 |
| **판단기준** | 취약: AutoAdminLogon값이1로설정된경우 |
| **조치방법** | 해당레지스트리값이존재하는경우0으로설정 |

---
## 상세 설명

### 1. 항목 개요

이 항목은 Windows가 부팅될 때 암호를 묻지 않고 **자동으로 로그인(Autologon)**하는 기능이 활성화되어 있는지 점검합니다. 키오스크나 광고용 디스플레이가 아닌 **서버**에서는 절대 사용해서는 안 되는 기능입니다.

### 2. 왜 이 항목이 필요한가요?

**물리적 보안 및 인증 우회 방지**
- **인증 무력화**: 자동 로그인이 설정되어 있으면, 공격자가 서버실에 들어와 재부팅만 하면 즉시 관리자 권한을 획득할 수 있습니다.
- **평문 암호 노출**: 자동 로그인을 위해 레지스트리에 저장하는 `DefaultPassword` 값은 평문(Clear Text)으로 저장되므로, 레지스트리 조회만으로도 관리자 암호를 탈취할 수 있습니다.

**보안 위협 시나리오**
1. 공격자가 물리적 접근 권한 획득 또는 원격 데스크톱 연결 시도
2. 서버 재부팅 시 별도 인증 없이 바탕화면 진입
3. 레지스트리(`Winlogon`) 값을 조회하여 저장된 평문 패스워드 획득

### 3. 점검 대상

- Windows NT, 2000, 2003, 2008, 2012, 2016, 2019, 2022 서버

### 4. 판단 기준

| 구분 | 기준 |
|------|------|
| **양호** | `AutoAdminLogon` 값이 없거나 `0`으로 설정되어 있는 경우 |
| **취약** | `AutoAdminLogon` 값이 `1`로 설정되어 자동 로그인이 활성화된 경우 |

### 5. 점검 방법

#### 방법 1: 레지스트리 편집기 확인
```
1. 시작 > 실행 > regedit
2. 경로 이동: HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon
3. **AutoAdminLogon** 값 확인
   - **0** 또는 **없음**: 양호
   - **1**: 취약
```

#### 방법 2: Sysinternals Autologon 도구
- Sysinternals의 `Autologon.exe`를 실행하여 현재 상태 확인 가능

### 6. 조치 방법

자동 로그인 기능을 끄고, 레지스트리에 저장된 평문 암호를 삭제합니다.

#### 방법 1: 레지스트리 수정 (권장)
```
1. 레지스트리 편집기(regedit) 실행
2. 경로: HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon
3. **AutoAdminLogon** 데이터를 **0**으로 수정
4. **DefaultPassword** 값이 있다면 **삭제** (평문 암호 제거)
```

#### 방법 2: UserAccounts (netplwiz) 도구 사용
```
1. 시작 > 실행 > netplwiz (또는 control userpasswords2)
2. **"사용자 이름과 암호를 입력해야 이 컴퓨터를 사용할 수 있음"** 체크 박스에 [v] 체크
3. 확인
```

### 7. 조치 시 주의사항

| 주의사항 | 설명 |
|----------|------|
| **키오스크/DID** | 공공장소의 안내 시스템 등 특수 목적 단말기인 경우 자동 로그인이 필요할 수 있습니다. 이 경우 물리적 보안(포트 차단, 함체 잠금)을 강화하고 일반 사용자 계정(Guest 권한)을 사용해야 합니다. |
| **DefaultUserName** | `DefaultUserName` 값은 마지막 로그인한 사용자 ID를 기억하는 기능이므로, 보안상 크게 문제되지는 않으나 W-10(마지막 사용자 이름 표시 안 함) 항목과 연관이 있습니다. |

### 8. 참고 자료

- [Microsoft Docs: How to turn on automatic logon in Windows](https://docs.microsoft.com/en-us/troubleshoot/windows-server/user-profiles-and-logon/turn-on-automatic-logon)

---

## 요약

**W-52 Autologon기능제어**는 서버의 현관문을 활짝 열어두는 행위를 막습니다. 암호 없이 들어갈 수 있는 서버는 이미 보안이 뚫린 것과 같습니다.
