---
title: "[2026 주요정보통신기반시설] W-07 Everyone 사용 권한을 익명 사용자에게 적용"
slug: "2026-주정통/W-07"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "'Everyone사용권한을익명사용자에적용'정책의설정여부점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Windows
---

# W-07 Everyone 사용 권한을 익명 사용자에게 적용

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | W-07 |
| **점검내용** | 'Everyone사용권한을익명사용자에적용'정책의설정여부점검 |
| **점검대상** | Windows 2003, 2008, 2012, 2016, 2019, 2022 |
| **양호기준** | 'Everyone사용권한을익명사용자에게적용'정책이'사용안함'으로되어있는경우 |
| **취약기준** | 'Everyone사용권한을익명사용자에게적용'정책이'사용'으로되어있는경우 |
| **조치방법** | 'Everyone사용권한을익명사용자에게적용'정책을'사용안함'으로설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: '네트워크 액세스: 익명 사용자의 Everyone 권한 시뮬레이션' 정책이 '사용 안 함'으로 되어 있는 경우
- **취약**: '네트워크 액세스: 익명 사용자의 Everyone 권한 시뮬레이션' 정책이 '사용'으로 되어 있는 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| 레거시 응용프로그램 | 주의 | 일부 구형 응용프로그램에서 익명 접근 필요 가능. 대안 마련 필요 |
| 백업 소프트웨어 | 주의 | 일부 백업 도구가 Everyone 공유 사용. 확인 후 대안 필요 |
| 파일 공유 확인 | 주의 | Everyone 권한이 있는 공유 폴더 함께 점검 필요 |
| 레지스트리 값 없음 | 취약 | 기본값은 '사용'임 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| 모든 Windows 서버 | 익명 사용자의 Everyone 권한 시뮬레이션 | 사용 안 함 | Everyone 대신 Authenticated Users 사용 |

### 2. 점검 방법

#### Windows 서버 점검

익명 사용자가 Everyone 그룹의 권한을 획득하지 못하도록 방지하여 인증되지 않은 네트워크 접근을 차단해야 합니다.

```bash
# PowerShell - 레지스트리 확인
Get-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Lsa" -Name "EveryoneIncludesAnonymous"

# 또는 secedit로 확인
secedit /export /cfg config.inf
Get-Content config.inf | Select-String "EveryoneIncludesAnonymous"
```

**양호 출력 예시:**
```text
EveryoneIncludesAnonymous : 0
```
값이 0이면 '사용 안 함'으로 양호

**취약 출력 예시:**
```text
EveryoneIncludesAnonymous : 1
또는
값이 존재하지 않음
```
값이 1이거나 없으면 '사용'으로 취약

### 3. 조치 방법

#### Windows 서버 설정

1. **레지스트리 설정**
   ```powershell
   # 관리자 권한 PowerShell 실행
   Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Lsa" -Name "EveryoneIncludesAnonymous" -Value 0 -Type DWord

   # 설정 확인
   Get-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Lsa" -Name "EveryoneIncludesAnonymous"
   ```

2. **명령 프롬프트 설정**
   ```cmd
   reg add "HKLM\SYSTEM\CurrentControlSet\Control\Lsa" /v EveryoneIncludesAnonymous /t REG_DWORD /d 0 /f
   ```

3. **로컬 보안 정책 설정 (GUI)**
   ```
   시작 > 제어판 > 관리 도구 > 로컬 보안 정책
   로컬 정책 > 보안 옵션
   "네트워크 액세스: 익명 사용자의 Everyone 권한 시뮬레이션" 더블클릭
   "사용 안 함" 선택
   ```

4. **그룹 정책(GPO) 설정 (도메인 환경)**
   ```
   GPO 편집기(gpedit.msc 또는 gpmc.msc)
   컴퓨터 구성 > 정책 > Windows 설정 > 보안 설정 > 로컬 정책 > 보안 옵션
   "네트워크 액세스: 익명 사용자의 Everyone 권한 시뮬레이션" 설정
   "사용 안 함" 선택
   ```

5. **Everyone 권한 공유 폴더 점검 및 제거**
   ```powershell
   # Everyone 권한이 있는 공유 폴더 확인
   Get-SmbShare | ForEach-Object {
       $SharePath = $_.Path
       if ($SharePath) {
           $Acl = Get-Acl $SharePath
           $EveryoneAccess = $Acl.Access | Where-Object {$_.IdentityReference -eq "Everyone"}
           if ($EveryoneAccess) {
               Write-Host "공유: $($_.Name), 경로: $SharePath" -ForegroundColor Yellow
           }
       }
   }
   ```

6. **서비스 재시작**
   ```powershell
   # 설정 적용을 위해 서버 재부팅 권장
   Restart-Computer
   ```

### 4. 참고 자료

- [Microsoft Docs: 네트워크 액세스 보안 옵션](https://docs.microsoft.com/ko-ko/windows/security/threat-protection/security-policy-settings/network-access-security-policy-settings)
- [CIS Benchmark: 익명 열거 제한](https://www.cisecurity.org/benchmark/windows_server)
- [KISA 주요정보통신기반시설 취약점 진단 가이드라인](https://www.kisa.or.kr/)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.