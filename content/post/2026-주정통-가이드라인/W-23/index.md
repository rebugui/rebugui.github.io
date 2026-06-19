---
title: "[2026 주요정보통신기반시설] W-23 공유 서비스에 대한 익명 접근 제한 설정"
slug: "2026-주정통/W-23"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "공유 서비스의 익명(Anonymous) 접속 허용 여부 점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Windows
draft: true
---

# W-23 공유 서비스에 대한 익명 접근 제한 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | W-23 |
| **점검내용** | 공유 서비스의 익명(Anonymous) 접속 허용 여부 점검 |
| **점검대상** | Windows NT, 2000, 2003, 2008, 2012, 2016, 2019, 2022 |
| **양호기준** | 공유 서비스를 사용하지 않거나, 익명 인증 사용 안 함으로 설정된 경우 |
| **취약기준** | 공유 서비스를 사용하며, 익명 인증 사용함으로 설정된 경우 |
| **조치방법** | 공유 서비스를 사용하지 않는 경우 서비스 중지, 사용할 경우 익명 인증 사용 안 함 설정 적용 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: FTP 및 파일 공유에서 익명 접속이 차단된 경우
- **취약**: FTP 또는 공유 폴더에 익명 사용자 접근이 허용된 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| FTP 익명 인증만 활성화 | 취약 | 즉시 비활성화 필요 |
| 파일 공유 익명 접속만 허용 | 취약 | Null Session 공격 위험 |
| 읽기 전용 익명 접속 | 취약 | 정보 유출 가능성 |
| 내부망에서만 익명 접속 허용 | 주의 | IP 제한이 있어도 우회 가능 |
| 복합기 스캔-to-Folder 용도 | 주의 | 서비스 계정 사용 권장 |
| IPC$에 익명 접속 가능 | 취약 | SAM 계정 열거 위험 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| FTP 서비스 | 익명 인증 | 사용 안 함 | 기본 인증만 사용 |
| 파일 공유 | 익명 열거 | 거부 | RestrictAnonymousSAM = 1 |
| 파일 공유 | Null Session 피어 | 제한 | RestrictNullSessAccess = 1 |
| 로컬 보안 정책 | Everyone 권한 적용 | 사용 안 함 | 익명 사용자 제한 |

### 2. 점검 방법

#### Windows FTP 서비스 점검

FTP 익명 인증이 활성화되면 아이디/비밀번호 없이 로그인이 가능하여 무단 파일 전송 경로로 악용될 수 있습니다.

```powershell
# IIS FTP 익명 인증 상태 확인
Import-Module WebAdministration
Get-WebConfiguration -Filter "/system.ftpServer/security/authentication/anonymousAuthentication" -PSPath "IIS:\"
```

**양호 출력 예시:**
```text
enabled : False
```

**취약 출력 예시:**
```text
enabled : True
```

```powershell
# 로컬 보안 정책 확인 (공유 익명 접근)
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
값 없음
```

```powershell
# Null Session 공유 확인
Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters" -Name "NullSessionShares" -ErrorAction SilentlyContinue
```

```cmd
# telnet으로 FTP 익명 로그인 테스트
telnet [FTP서버IP] 21
# 사용자: anonymous
# 비밀번호: (없음 또는 임의 이메일)
```

### 3. 조치 방법

#### Windows FTP 및 공유 서비스 설정

1. **FTP 익명 인증 비활성화**
   ```powershell
   # IIS FTP 익명 인증 비활성화
   Set-WebConfigurationProperty -Filter "/system.ftpServer/security/authentication/anonymousAuthentication" -PSPath "IIS:\" -Name "Enabled" -Value $false

   # 기본 인증 활성화 확인
   Set-WebConfigurationProperty -Filter "/system.ftpServer/security/authentication/basicAuthentication" -PSPath "IIS:\" -Name "Enabled" -Value $true
   ```

2. **익명 열거 제한 (레지스트리)**
   ```powershell
   # 익명 열거 제한 설정
   Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Lsa" -Name "RestrictAnonymous" -Value 1 -Type DWord
   Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Lsa" -Name "RestrictAnonymousSAM" -Value 1 -Type DWord
   ```

3. **Null Session 공유 제거**
   ```powershell
   # Null Session 공유 목록 제거
   Remove-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters" -Name "NullSessionShares" -ErrorAction SilentlyContinue
   ```

4. **IPC$ 익명 접근 제한 강화**
   ```powershell
   # 명명된 파이프와 공유에 대한 익명 액세스 제한
   Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters" -Name "RestrictNullSessAccess" -Value 1 -Type DWord
   ```

5. **IIS 관리자에서 설정 (GUI)**
   ```
   [FTP 익명 인증]
   1. IIS 관리자 실행 > FTP 사이트 선택
   2. "FTP 인증" 더블클릭
   3. "익명 인증" 선택 > [사용 안 함]

   [로컬 보안 정책]
   1. 시작 > 실행 > secpol.msc
   2. 로컬 정책 > 보안 옵션
   3. "네트워크 액세스: SAM 계정 및 공유의 익명 열거 허용 안 함" > [사용]으로 설정
   4. "네트워크 액세스: 익명 사용자의 Everyone 권한 적용 허용" > [사용 안 함]으로 설정
   ```

### 4. 참고 자료

- [Microsoft Docs: 익명 액세스 제한](https://docs.microsoft.com/ko-kr/windows/security/threat-protection/security-policy-settings/network-access-restrict-anonymous-access-to-named-pipes-and-shares)
- [Microsoft Docs: FTP 인증 설정](https://docs.microsoft.com/ko-kr/iis/configuration/system.applicationhost/sites/site/ftpserver/security/authentication/)
- [CIS Microsoft Windows Benchmark](https://www.cisecurity.org/benchmark/microsoft_windows_server)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.