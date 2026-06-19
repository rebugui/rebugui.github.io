---
title: "[2026 주요정보통신기반시설] W-53 이동식 미디어 포맷 및 꺼내기 허용"
slug: "2026-주정통/W-53"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "관리자이외NTFS미디어포맷및꺼내기허용여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Windows
draft: true
---

# W-53 이동식 미디어 포맷 및 꺼내기 허용

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | W-53 |
| **점검내용** | 관리자이외NTFS미디어포맷및꺼내기허용여부점검 |
| **점검대상** | Windows NT, 2000, 2003, 2008, 2012, 2016, 2019, 2022 |
| **판단기준** | 양호: '이동식미디어포맷및꺼내기허용'정책이'Administrators'로되어있는경우 |
| **판단기준** | 취약: '이동식미디어포맷및꺼내기허용'정책이'Administrators'로되어있지않은경우 |
| **조치방법** | '이동식NTFS 미디어꺼내기허용'정책을'Administrators'로설정 |

---
## 상세 설명

### 1. 항목 개요

이 항목은 USB, 외장 하드 등 **이동식 미디어(Removable Media)**를 **포맷(Format)**하거나 **꺼내기(Eject)**할 수 있는 권한을 누구에게 줄 것인지 점검합니다. 

### 2. 왜 이 항목이 필요한가요?

**데이터 보호 및 가용성 유지**
- **실수 방지**: 일반 사용자가 실수로 서버에 연결된 백업용 외장 하드를 포맷해버리는 사고를 방지합니다.
- **악의적 행위 차단**: 내부자가 중요 데이터가 담긴 디스크를 포맷하여 데이터를 파괴하거나, 무단으로 디스크를 분리하여 서비스를 중단시키는 것을 막습니다.

**보안 위협 시나리오**
1. 운영 중인 서버에 데이터 백업용 USB 드라이브가 연결되어 있음
2. 로컬에 로그인한 일반 사용자(또는 침해당한 계정)가 "이 디스크를 포맷하시겠습니까?" 팝업에서 [예]를 클릭
3. 백업 데이터 소실

### 3. 점검 대상

- Windows NT, 2000, 2003, 2008, 2012, 2016, 2019, 2022 서버

### 4. 판단 기준

| 구분 | 기준 |
|------|------|
| **양호** | "장치: 이동식 미디어 포맷 및 꺼내기 허용" 정책이 **Administrators**로 설정된 경우 |
| **취약** | 해당 정책이 **Administrators 및 Power Users** 또는 **Administrators 및 Interactive Users**로 설정되어 일반 사용자도 가능한 경우 |

### 5. 점검 방법

#### 방법 1: 로컬 보안 정책 확인
```
1. 시작 > 실행 > secpol.msc
2. 로컬 정책 > 보안 옵션
3. **"장치: 이동식 미디어 포맷 및 꺼내기 허용"** 정책 확인
   - **Administrators**: 양호
   - 그 외: 취약
```

#### 방법 2: 레지스트리 확인
```powershell
Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" -Name "AllocateDASD"
```
- `0` (Administrators): 양호
- `1` (Administrators and Power Users) 또는 `2` (Administrators and Interactive Users): 취약

### 6. 조치 방법

이동식 미디어 관리 권한을 시스템 관리자로 제한합니다.

#### 방법 1: 로컬 보안 정책 설정 (권장)
```
1. 시작 > 실행 > secpol.msc
2. 로컬 정책 > 보안 옵션
3. **"장치: 이동식 미디어 포맷 및 꺼내기 허용"** 더블클릭
4. **[관리자(Administrators)]** 선택
5. 확인
```

### 7. 조치 시 주의사항

| 주의사항 | 설명 |
|----------|------|
| **CD-ROM 꺼내기** | 이 정책은 플로피 디스크나 CD-ROM 드라이브를 꺼내는 권한도 제어합니다. (최근 서버는 ODD가 거의 없어 영향이 적음) |
| **원격 데스크톱** | RDP 세션에서는 로컬 드라이브 포맷 메뉴가 제한될 수 있으나, 정책적으로 명확히 설정하는 것이 안전합니다. |

### 8. 참고 자료

- [Microsoft Docs: Devices: Allowed to format and eject removable media](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/devices-allowed-to-format-and-eject-removable-media)

---

## 요약

**W-53 이동식미디어포맷및꺼내기허용**는 "포맷"이라는 위험한 버튼을 관리자만 누를 수 있게 잠그는 설정입니다.
