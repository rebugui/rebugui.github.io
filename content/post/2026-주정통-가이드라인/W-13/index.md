---
title: "[2026 주요정보통신기반시설] W-13 콘솔 로그온 시 로컬 계정에서 빈 암호 사용 제한"
slug: "2026-주정통/W-13"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "콘솔로그인시빈비밀번호사용가능여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Windows
draft: true
---

# W-13 콘솔 로그온 시 로컬 계정에서 빈 암호 사용 제한

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | W-13 |
| **점검내용** | 콘솔로그인시빈비밀번호사용가능여부점검 |
| **점검대상** | Windows 2003, 2008, 2012, 2016, 2019, 2022 |
| **양호기준** | '콘솔로그온시로컬계정에서빈암호사용제한'정책이'사용'인경우 |
| **취약기준** | '콘솔로그온시로컬계정에서빈암호사용제한'정책이'사용안함'인경우 |
| **조치방법** | '계정:콘솔로그온시로컬계정에서빈암호사용제한'정책을'사용'으로설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: '계정: 콘솔 로그온 시 로컬 계정에서 빈 암호 사용 제한' 정책이 '사용'인 경우
- **취약**: '계정: 콘솔 로그온 시 로컬 계정에서 빈 암호 사용 제한' 정책이 '사용 안 함'인 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| 원격 데스크톱 | 양호 | 이 정책은 로컬 콘솔뿐만 아니라 RDP에도 적용됨 |
| 도메인 계정 | 주의 | 도메인 계정은 도메인 정책 따름 |
| 자동 로그온 | 취약 | 빈 암호로 자동 로그온 가능하면 취약 |
| 레지스트리 값 없음 | 취약 | 기본값은 '사용 안 함'임 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| 모든 Windows 서버 | 빈 암호 사용 제한 | 사용 | 모든 계정은 비밀번호 필수 |

### 2. 점검 방법

#### Windows 서버 점검

빈 비밀번호를 가진 계정이 시스템에 로그온하는 것을 방지하여, 무인증 접근을 차단해야 합니다.

```bash
# PowerShell - 레지스트리 확인
Get-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Lsa" -Name "LimitBlankPasswordUse"
```

**양호 출력 예시:**
```text
LimitBlankPasswordUse : 1
```
값이 1이면 '사용'으로 양호

**취약 출력 예시:**
```text
LimitBlankPasswordUse : 0
또는
값이 존재하지 않음
```
값이 0이거나 없으면 '사용 안 함'으로 취약

### 3. 조치 방법

#### Windows 서버 설정

1. **레지스트리 설정**
   ```powershell
   # 관리자 권한 PowerShell 실행
   Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Lsa" -Name "LimitBlankPasswordUse" -Value 1 -Type DWord

   # 설정 확인
   Get-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Lsa" -Name "LimitBlankPasswordUse"
   ```

2. **명령 프롬프트 설정**
   ```cmd
   reg add "HKLM\SYSTEM\CurrentControlSet\Control\Lsa" /v LimitBlankPasswordUse /t REG_DWORD /d 1 /f
   ```

3. **로컬 보안 정책 설정 (GUI)**
   ```
   시작 > 제어판 > 관리 도구 > 로컬 보안 정책
   로컬 정책 > 보안 옵션
   '계정: 콘솔 로그온 시 로컬 계정에서 빈 암호 사용 제한' 더블클릭
   '사용' 선택
   ```

4. **빈 비밀번호 계정 확인**
   ```powershell
   # 빈 비밀번호 계정 확인
   Get-LocalUser | Where-Object {$_.PasswordRequired -eq $false} | Select-Object Name, Enabled
   ```

### 4. 참고 자료

- [Microsoft Docs: 빈 암호 제한](https://docs.microsoft.com/ko-kr/windows/security/threat-protection/security-policy-settings/accounts)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.