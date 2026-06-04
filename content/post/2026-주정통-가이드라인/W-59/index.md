---
title: "[2026 주요정보통신기반시설] W-59 LAN Manager 인증 수준"
slug: "2026-주정통/W-59"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "LANManager인증수준적절성점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Windows
---

# W-59 LAN Manager 인증 수준

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | W-59 |
| **점검내용** | LANManager인증수준적절성점검 |
| **점검대상** | Windows NT, 2000, 2003, 2008, 2012, 2016, 2019, 2022 |
| **판단기준** | 양호: "LAN Manager인증수준" 정책에"NTLMv2응답만보냄"이설정되어있는경우 |
| **판단기준** | 취약: "LAN Manager인증수준" 정책에"LM"및"NTLM"인증이설정되어있는경우 |
| **조치방법** | - Windows 2000 : LANManager인증7수준->NTLMv2응답만보내기 - Windows 2003, 2008, 2012, 2016, 2019 : 네트워크보안:LANManager인증수준->NTMLv2응답만보내기 |

---
## 상세 설명

### 1. 항목 개요

이 항목은 Windows 시스템이 네트워크 인증 시 사용할 **프로토콜 수준**을 정의합니다. **LAN Manager (LM)** 및 **NTLM v1**은 암호화 강도가 약해 쉽게 해킹되므로, 더 안전한 **NTLM v2**만 사용하도록 설정해야 합니다.

### 2. 왜 이 항목이 필요한가요?

**인증 정보 탈취 방지**
- **취약한 프로토콜 차단**: LM 해시는 대소문자를 구분하지 않고 14자리로 끊어서 저장하는 구조적 취약점이 있어, 몇 초 만에 크랙될 수 있습니다. NTLM v1 역시 Rainbow Table 공격에 취약합니다.
- **재전송 공격 방지**: NTLM v2는 서버가 보내는 챌린지 값에 타임스탬프 등을 섞어 사용하여 재전송 공격(Replay Attack)을 어렵게 만듭니다.

**보안 위협 시나리오**
1. 공격자가 네트워크 중간자(Man-in-the-Middle) 위치 선점
2. 구형 클라이언트(또는 잘못 설정된 서버)가 LM/NTLM v1으로 인증 시도
3. 공격자가 패킷을 캡처하여 'Responder' 등의 도구로 해시 획득 및 크랙
4. 사용자 비밀번호 평문 획득

### 3. 점검 대상

- Windows NT, 2000, 2003, 2008, 2012, 2016, 2019, 2022 서버

### 4. 판단 기준

| 구분 | 기준 |
|------|------|
| **양호** | "LAN Manager 인증 수준"이 **NTLMv2 응답만 보냄(LM 및 NTLM 거부)** 이상으로 설정된 경우 |
| **취약** | "LM 및 NTLM 응답 보내기" 등으로 설정되어 취약한 프로토콜을 허용하는 경우 |

### 5. 점검 방법

#### 방법 1: 로컬 보안 정책 확인
```
1. 시작 > 실행 > secpol.msc
2. 로컬 정책 > 보안 옵션
3. **"네트워크 보안: LAN Manager 인증 수준"** 정책 확인
   - **NTLMv2 응답만 보냄**: 양호
   - **LM 및 NTLM 응답 보내기**: 취약
```

#### 방법 2: 레지스트리 확인
```powershell
Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Control\Lsa" -Name "LmCompatibilityLevel"
```
- `3`, `4`, `5`: 양호 (3 이상 권장)
- `0`, `1`, `2`: 취약

### 6. 조치 방법

가장 강력한 인증 수준인 NTLM v2만 사용하도록 설정합니다.

#### 방법 1: 로컬 보안 정책 설정 (권장)
```
1. 시작 > 실행 > secpol.msc
2. 로컬 정책 > 보안 옵션
3. **"네트워크 보안: LAN Manager 인증 수준"** 더블클릭
4. **[NTLMv2 응답만 보냄. LM 및 NTLM 거부]** 선택
5. 확인
```

### 7. 조치 시 주의사항

| 주의사항 | 설명 |
|----------|------|
| **레거시 장비 호환성** | 아주 오래된 NAS, 복합기(프린터), 또는 Windows XP/2000 이하 시스템과 파일 공유를 해야 한다면 NTLMv2를 지원하지 않을 수 있습니다. 이 경우 펌웨어 업데이트를 하거나 예외 처리가 필요합니다. |
| **Kerberos** | Active Directory 환경에서는 기본적으로 Kerberos를 사용하므로 이 설정이 직접적인 영향을 덜 주지만, IP 기반 접속이나 로컬 계정 인증 시에는 NTLM이 사용되므로 필수적인 보안 설정입니다. |

### 8. 참고 자료

- [Microsoft Docs: Network security: LAN Manager authentication level](https://docs.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/network-security-lan-manager-authentication-level)

---

## 요약

**W-59 LANManager인증수준**은 암호 인증의 '언어'를 업그레이드하는 것입니다. 20년 전의 낡고 허술한 언어(LM)는 버리고, 최신 언어(NTLMv2)로만 대화하세요.
