---
title: "[2026 주요정보통신기반시설] W-22 FTP 디렉토리 접근 권한 설정"
slug: "2026-주정통/W-22"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "FTP 홈디렉터리의 접근권한 적절성 점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Windows
---

# W-22 FTP 디렉토리 접근 권한 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | W-22 |
| **점검내용** | FTP 홈디렉터리의 접근권한 적절성 점검 |
| **점검대상** | Windows NT, 2000, 2003, 2008, 2012, 2016, 2019, 2022 |
| **양호기준** | FTP 홈디렉터리에 Everyone 권한이 없는 경우 |
| **취약기준** | FTP 홈디렉터리에 Everyone 권한이 있는 경우 |
| **조치방법** | FTP 홈디렉터리에서 Everyone 권한 삭제, 각 사용자에게 적절한 권한 부여 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: FTP 홈 디렉터리에 Everyone 그룹에 부여된 권한이 없는 경우
- **취약**: FTP 홈 디렉터리에 Everyone 그룹에 쓰기/수정 권한이 부여된 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| Everyone에 읽기 권한만 있음 | 주의 | 정보 유출 가능성 있으므로 제거 권장 |
| Everyone에 완전 제어 권한 | 취약 | 매우 위험하며 즉시 제거 필요 |
| Everyone 권한 없으나 BUILTIN\Users에 쓰기 권한 | 취약 | 모든 인증된 사용자에게 쓰기 권한 부여와 동일 |
| 익명 사용자(IUSR)에 쓰기 권한 | 취약 | 인증 없는 사용자가 파일 업로드 가능 |
| 관리자만 접근 권한 보유 | 양호 | Administrators 그룹만 권한 보유 |
| IIS_IUSRS 그룹에 읽기 권한 | 양호 | FTP 서비스 운영에 필요한 최소 권한 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| FTP 루트 디렉터리 | Everyone 권한 | 제거 | 불필요한 권한 완전 삭제 |
| FTP 루트 디렉터리 | Administrators | 완전 제어 | 시스템 관리자만 전체 권한 |
| FTP 루트 디렉터리 | IIS_IUSRS | 읽기 및 실행 | FTP 서비스 계정 최소 권한 |
| 사용자별 디렉토리 | 해당 사용자 | 읽기, 쓰기 | 개별 사용자 홈 디렉터리에만 권한 부여 |

### 2. 점검 방법

#### Windows 서버 점검

FTP 디렉토리에 과도한 권한이 부여되면 무단 파일 업로드, 웹쉘 설치, 데이터 변조 등의 공격에 악용될 수 있습니다.

```cmd
# FTP 기본 홈 디렉터리 권한 확인
icacls "C:\inetpub\ftproot"
```

**양호 출력 예시:**
```text
C:\inetpub\ftproot
NT AUTHORITY\SYSTEM:(OI)(CI)(F)
BUILTIN\Administrators:(OI)(CI)(F)
BUILTIN\IIS_IUSRS:(OI)(CI)(RX)
```

**취약 출력 예시:**
```text
C:\inetpub\ftproot
Everyone:(OI)(CI)(F)
또는
BUILTIN\Users:(OI)(CI)(M)
```

```powershell
# PowerShell로 권한 확인
Get-Acl "C:\inetpub\ftproot" | Format-List
```

```cmd
# IIS FTP 권한 부여 규칙 확인 (PowerShell)
Import-Module WebAdministration
Get-WebConfiguration -Filter "/system.ftpServer/security/authorization" -PSPath "IIS:\"
```

### 3. 조치 방법

#### Windows 서버 설정

1. **Everyone 권한 제거**
   ```cmd
   # Everyone 권한 제거
   icacls "C:\inetpub\ftproot" /remove "Everyone"

   # 상속 비활성화 및 명시적 권한 설정
   icacls "C:\inetpub\ftproot" /inheritance:d
   ```

2. **IIS 서비스 계정 권한 설정**
   ```cmd
   # IIS_IUSRS에 읽기 및 실행 권한 부여
   icacls "C:\inetpub\ftproot" /grant "BUILTIN\IIS_IUSRS:(OI)(CI)(RX)"

   # 관리자에게 완전 제어 권한 확인
   icacls "C:\inetpub\ftproot" /grant "BUILTIN\Administrators:(OI)(CI)(F)"
   ```

3. **개별 사용자별 권한 부여 (필요시)**
   ```cmd
   # 특정 사용자에게 읽기/쓰기 권한 부여
   icacls "C:\inetpub\ftproot\UserFolder" /grant "DOMAIN\Username:(OI)(CI)(RW)"
   ```

4. **IIS 관리자에서 FTP 권한 설정 (GUI)**
   ```
   1. IIS 관리자 실행 > FTP 사이트 선택
   2. "FTP 권한 부여 규칙" 더블클릭
   3. "모든 사용자" 규칙 선택 > [제거]
   4. [허용 규칙 추가] 클릭
   5. "지정한 사용자 또는 그룹" 선택
   6. 허용할 사용자 또는 그룹 입력
   7. 권한(읽기/쓰기) 선택 > [확인]
   ```

5. **익명 인증 비활성화 (연계 조치)**
   ```
   1. IIS 관리자 > FTP 사이트 선택
   2. "FTP 인증" 더블클릭
   3. "익명 인증" 선택 > [사용 안 함]
   4. "기본 인증" [사용] 상태 확인
   ```

### 4. 참고 자료

- [Microsoft Docs: IIS FTP 보안](https://docs.microsoft.com/ko-kr/iis/configuration/system.applicationhost/sites/site/ftpserver/security/)
- [Microsoft Docs: icacls 명령](https://docs.microsoft.com/ko-kr/windows-server/administration/windows-commands/icacls)
- [NIST SP 800-53: AC-3 Access Enforcement](https://csrc.nist.gov/projects/security-configuration-checklist)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.