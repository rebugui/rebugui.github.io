---
title: "[2026 주요정보통신기반시설] W-16 공유 권한 및 사용자 그룹 설정"
slug: "2026-주정통/W-16"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "공유디렉터리내Everyone권한존재여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Windows
---

# W-16 공유 권한 및 사용자 그룹 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | W-16 |
| **점검내용** | 공유디렉터리내Everyone권한존재여부점검 |
| **점검대상** | Windows NT, 2000, 2003, 2008, 2012, 2016, 2019, 2022 |
| **양호기준** | 일반공유디렉터리가없거나공유디렉터리접근권한에Everyone권한이없는경우 |
| **취약기준** | 일반공유디렉터리의접근권한에Everyone권한이있는경우 |
| **조치방법** | 공유디렉터리접근권한에서Everyone권한제거후필요한계정추가 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 일반 공유 디렉터리가 없거나, 공유 디렉터리 접근 권한에 Everyone 권한이 없는 경우
- **취약**: 일반 공유 디렉터리의 접근 권한에 Everyone 권한이 있는 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| 숨김 공유($) | 주의 | 관리용 공유(C$, Admin$)는 제외. 일반 공유만 점검 |
| 백업 소프트웨어 | 주의 | 백업을 위해 Everyone 공유 사용 시 대안 필요 |
| 레거시 애플리케이션 | 주의 | 구형 앱에서 Everyone 권한 필요 가능 |
| Authenticated Users | 양호 | Everyone 대신 Authenticated Users 사용 권장 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| 모든 서버 | Everyone 권한 | 제거 | 인증 없는 접근 차단 |
| 모든 서버 | Authenticated Users | Read 또는 Modify | 인증된 사용자만 |
| 모든 서버 | 특정 사용자/그룹 | 필요한 최소 권한만 | 최소 권한 원칙 |

### 2. 점검 방법

#### Windows 서버 점검

네트워크 공유 폴더의 권한을 점검하여, Everyone 그룹에게 부여된 과도한 권한을 제거해야 합니다.

```bash
# PowerShell - 모든 공유 폴더 확인
Get-SmbShare | Where-Object {$_.Name -notlike "*$"} | Select-Object Name, Path

# Everyone 권한이 있는 공유 확인
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

**양호 출력 예시:**
```text
(출력 없음)
```
Everyone 권한이 있는 공유가 없으면 양호

**취약 출력 예시:**
```text
공유: SharedFolder, 경로: C:\SharedFolder
공유: Data, 경로: D:\Data
```
Everyone 권한이 있는 공유가 있으면 취약

### 3. 조치 방법

#### Windows 서버 설정

1. **Everyone 권한 제거 (PowerShell)**
   ```powershell
   # 특정 공유 폴더의 Everyone 권한 제거
   $SharePath = "C:\SharedFolder"
   $Acl = Get-Acl $SharePath
   $Acl.Access | Where-Object {$_.IdentityReference -eq "Everyone"} | ForEach-Object {
       $Acl.RemoveAccessRule($_)
   }
   Set-Acl $SharePath $Acl
   ```

2. **GUI로 권한 수정**
   ```
   시작 > 실행 > fsmgmt.msc
   공유 폴더 선택
   속성 > 공유 탭 > 권한
   Everyone 권한 제거
   필요한 계정 또는 그룹 추가 및 권한 설정
   ```

3. **권장 권한 부여**
   ```
   Everyone 제거 후 다음과 같이 설정:
   - 관리자: Full Control
   - 일반 사용자: Read 또는 Modify
   - Authenticated Users: Read (필요시)
   ```

### 4. 참고 자료

- [Microsoft Docs: 파일 공유 보안](https://docs.microsoft.com/ko-kr/windows-server/storage/file-server/file-server-security)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.