---
title: "[2026 주요정보통신기반시설] W-05 해독 가능한 암호화를 사용하여 암호 저장 해제"
slug: "2026-주정통/W-05"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "해독가능한암호화사용여부점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Windows
---

# W-05 해독 가능한 암호화를 사용하여 암호 저장 해제

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | W-05 |
| **점검내용** | 해독가능한암호화사용여부점검 |
| **점검대상** | Windows NT, 2000, 2003, 2008, 2012, 2016, 2019, 2022 |
| **양호기준** | '해독가능한암호화를사용하여암호저장'정책이'사용안함'으로설정된경우 |
| **취약기준** | '해독가능한암호화를사용하여암호저장'정책이'사용'으로설정된경우 |
| **조치방법** | '해독가능한암호화를사용하여암호저장'을'사용안함'으로설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: '해독 가능한 암호화를 사용하여 암호 저장' 정책이 '사용 안 함'으로 설정된 경우
- **취약**: '해독 가능한 암호화를 사용하여 암호 저장' 정책이 '사용'으로 설정된 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| CHAP 인증 사용 환경 | 주의 | CHAP는 원본 비밀번호가 필요하므로 해독 가능한 암호화 필요. 대안 마련 필요 |
| 도메인 컨트롤러 | 주의 | 도메인 환경에서는 GPO로 일괄 적용 권장 |
| 기존 비밀번호 | 주의 | 사용자가 비밀번호를 변경할 때만 정책 적용됨 |
| 레지스트리 값 없음 | 취약 | 기본값은 '사용'임 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| 모든 Windows 서버 | 해독 가능한 암호화를 사용하여 암호 저장 | 사용 안 함 | CHAP 사용 시 예외 |

### 2. 점검 방법

#### Windows 서버 점검

해독 가능한 암호화를 사용하여 암호 저장 정책은 비밀번호의 복호화 가능 여부를 결정하는 중요한 보안 설정입니다. 이 정책이 활성화되면 SAM 데이터베이스 노출 시 모든 비밀번호가 탈취될 수 있습니다.

```bash
# PowerShell - 레지스트리 확인
Get-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Lsa" -Name "DisableReversibleEncryption"

# 또는 secedit로 확인
secedit /export /cfg config.inf
Get-Content config.inf | Select-String "ClearTextPassword"
```

**양호 출력 예시:**
```text
DisableReversibleEncryption : 1
```
값이 1이면 '사용 안 함'으로 양호

**취약 출력 예시:**
```text
DisableReversibleEncryption : 0
또는
값이 존재하지 않음
```
값이 0이거나 없으면 '사용'으로 취약

### 3. 조치 방법

#### Windows 서버 설정

1. **레지스트리 설정**
   ```powershell
   # 관리자 권한 PowerShell 실행
   Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Lsa" -Name "DisableReversibleEncryption" -Value 1 -Type DWord

   # 설정 확인
   Get-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Lsa" -Name "DisableReversibleEncryption"
   ```

2. **명령 프롬프트 설정**
   ```cmd
   reg add "HKLM\SYSTEM\CurrentControlSet\Control\Lsa" /v DisableReversibleEncryption /t REG_DWORD /d 1 /f
   ```

3. **로컬 보안 정책 설정 (GUI)**
   ```
   시작 > 제어판 > 관리 도구 > 로컬 보안 정책
   계정 정책 > 암호 정책
   "해독 가능한 암호화를 사용하여 암호 저장" 더블클릭
   "사용 안 함" 선택
   ```

4. **그룹 정책(GPO) 설정 (도메인 환경)**
   ```
   GPO 편집기(gpedit.msc 또는 gpmc.msc)
   컴퓨터 구성 > 정책 > Windows 설정 > 보안 설정 > 계정 정책 > 암호 정책
   "해독 가능한 암호화를 사용하여 암호 저장" 설정
   "사용 안 함" 선택
   ```

5. **서비스 재시작**
   ```powershell
   # 설정 적용을 위해 시스템 재부팅 권장
   Restart-Computer
   ```

### 4. 참고 자료

- [Microsoft Docs: 암호 정책](https://docs.microsoft.com/ko-kr/windows/security/threat-protection/security-policy-settings/password-policy)
- [NIST SP 800-63B: 디지털 아이덴티티 가이드라인](https://pages.nist.gov/800-63-3/sp800-63b.html)
- [CIS Controls: 자격 증명 보호](https://www.cisecurity.org/controls/)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.