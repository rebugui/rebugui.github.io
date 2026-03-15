---
title: "[2026 주요정보통신기반시설] PC-08 대상 시스템이 Windows 서버를 제외한 다른 OS로 멀티 부팅이 가능하지 않도록 설정"
slug: "2026-주정통/PC-08"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "사용자PC에하나의OS설치여부점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - PC
---

# 대상 시스템이 Windows 서버를 제외한 다른 OS로 멀티 부팅이 가능하지 않도록 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | PC-08 |
| **점검내용** | 사용자PC에하나의OS설치여부점검 |
| **점검대상** | Windows 10, Windows 11 |
| **양호기준** | PC내에하나의OS만설치된경우 |
| **취약기준** | PC내에2개이상의OS가설치된경우 |
| **조치방법** | 하나의OS만설치하여운영함 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: PC 내에 하나의 OS만 설치된 경우
- **취약**: PC 내에 2개 이상의 OS가 설치된 경우

#### 경계 케이스 (Edge Case) 처리 방법
- **Windows Server**: 이 항목에서 제외
- **Recovery 파티션**: OS로 간주하지 않음
- **가상머신**: 호스트 OS만 확인, VM 내부 OS는 제외
- **WSL**: Windows Subsystem for Linux는 제외

#### 권장 설정값
- **설치된 OS**: 1개만

### 2. 점검 방법

#### Windows 10, 11에서의 점검

**시스템 구성(msconfig) 확인:**
```
Step 1) 시작 > 실행 > 'msconfig' 입력
Step 2) [부팅] 탭 선택
Step 3) 설치된 운영체제 목록 확인
```

**PowerShell 확인:**
```powershell
# 부팅 항목 확인
bcdedit /enum

# 부팅 로더 데이터 확인
Get-WmiObject -Class Win32_OperatingSystem | Select-Object Caption, Version, BootDevice

# 디스크 및 파티션 정보
Get-Partition | Select-Object DriveLetter, Type, IsActive, IsBoot
```

### 3. 조치 방법

#### 1. 시스템 구성에서 사용하지 않는 OS 삭제

```
Step 1) msconfig 실행 > [부팅] 탭
Step 2) 사용하지 않는 OS 선택
Step 3) [삭제] 클릭
```

#### 2. bcdedit을 통한 부팅 항목 삭제

**PowerShell/명령 프롬프트:**
```cmd
REM 관리자 권한 명령 프롬프트
REM 부팅 항목 확인
bcdedit /enum

REM 특정 부팅 항목 삭제 (식별자 필요)
bcdedit /delete {identifier} /cleanup
```

### 4. 참고 자료

#### 멀티 부팅의 보안 위협

**보안 위협:**
- **파일 시스템 접근 우회**: 다른 OS로 부팅하면 주요 OS의 보안 설정을 우회 가능
- **보안 장치 우회**: 주요 OS의 방화벽, 백신, 보안 정책을 우회하여 데이터 접근
- **데이터 유출**: NTFS 권한 설정을 우회하여 파일 접근 가능
- **감사 회피**: 부팅된 OS에서 감사 로그가 남지 않을 수 있음

**대안:**
- 가상머신 사용 (VMware, VirtualBox, Hyper-V)
- Windows Sandbox
- WSL 2 (Windows Subsystem for Linux)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.