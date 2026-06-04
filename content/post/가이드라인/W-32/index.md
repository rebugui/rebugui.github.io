---
title: "[2026 주요정보통신기반시설] W-32 기본 공유(C D Admin IPC20 20 12 61 79 80 81 701 33 98 100 204 250 395 398 399 400 제거"
slug: "2026-주정통/W-32"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "Windows 기본 관리 공유 제거 여부 점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Windows
---

# W-32 기본 공유(C$, D$, Admin$, IPC$) 제거

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | W-32 |
| **점검내용** | Windows 기본 관리 공유 제거 여부 점검 |
| **점검대상** | Windows 2000, 2003, 2008, 2012, 2016, 2019, 2022 |
| **양호기준** | AutoShareServer 값이 0으로 설정되어 있고, 기본 공유(C$, D$ 등)가 제거된 경우 |
| **취약기준** | AutoShareServer 값이 1이거나 없으며, 기본 공유가 존재하는 경우 |
| **조치방법** | 레지스트리의 AutoShareServer 값을 0으로 설정하고 기본 공유 제거 (IPC$는 예외) |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: AutoShareServer 레지스트리 값이 0이고, C$, D$, Admin$ 등 기본 공유가 제거된 경우
- **취약**: AutoShareServer 값이 1(또는 없음)이고, 기본 공유가 활성화된 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| C$, D$ 제거됨 | 양호 | 드라이브 공유 제거됨 |
| Admin$만 존재 | 주의 | 일부 백업 소프트웨어 필요 |
| IPC$ 존재 | 양호 | 필수 공유, 유지 필요 |
| AutoShareServer = 0 | 양호 | 재부팅 후에도 제거 유지 |
| IPC$ 익명 접근 가능 | 취약 | W-23 연계 조치 필요 |
| 도메인 컨트롤러 | 주의 | SYSVOL 공유 등 필요 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| 레지스트리 | AutoShareServer | 0 | 서버용 공유 비활성화 |
| 레지스트리 | AutoShareWks | 0 | 워크스테이션용 공유 비활성화 |
| IPC$ | 상태 | 유지 | 시스템 필수 공유 |
| IPC$ 익명 접근 | 권한 | 제한 | RestrictNullSessAccess = 1 |

### 2. 점검 방법

#### Windows 서버 점검

Windows는 자동으로 드라이브 공유(C$, D$ 등)를 생성합니다. 이는 공격자의 Lateral Movement 경로로 악용될 수 있습니다.

```cmd
# 현재 공유 목록 확인
net share
```

**양호 출력 예시:**
```text
공유 이름   리소스                            备注
-------------------------------------------------------------------------------
IPC$       Remote IPC                        원격 IPC
공유 명이 없습니다.
```

**취약 출력 예시:**
```text
공유 이름   리소스                            备注
-------------------------------------------------------------------------------
C$         C:\                               기본 공유
D$         D:\                               기본 공유
ADMIN$     C:\Windows                        원격 관리
IPC$       Remote IPC                        원격 IPC
```

```powershell
# AutoShareServer 레지스트리 확인
Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters" -Name "AutoShareServer" -ErrorAction SilentlyContinue
```

**양호 출력 예시:**
```text
AutoShareServer : 0
```

**취약 출력 예시:**
```text
AutoShareServer : 1
또는
(속성 없음)
```

### 3. 조치 방법

#### Windows 서버 설정

1. **AutoShareServer 레지스트리 설정**
   ```powershell
   # AutoShareServer 값 설정 (서버용)
   Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters" -Name "AutoShareServer" -Value 0 -Type DWord

   # AutoShareWks 값 설정 (워크스테이션용)
   Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters" -Name "AutoShareWks" -Value 0 -Type DWord
   ```

2. **현재 활성화된 공유 제거**
   ```cmd
   # C$ 공유 제거
   net share C$ /delete

   # D$ 공유 제거
   net share D$ /delete

   # Admin$ 공유 제거 (필요시)
   net share Admin$ /delete

   # 주의: IPC$는 제거하지 마세요
   ```

3. **서버 서비스 재시작**
   ```powershell
   # LanmanServer 서비스 재시작
   Restart-Service -Name "LanmanServer"
   ```

4. **IPC$ 익명 접근 제한 (연계 조치)**
   ```powershell
   # 명명된 파이프와 공유에 대한 익명 액세스 제한
   Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters" -Name "RestrictNullSessAccess" -Value 1 -Type DWord
   ```

### 4. 참고 자료

- [Microsoft Docs: Windows에서 관리 공유 제거](https://docs.microsoft.com/ko-kr/troubleshoot/windows-server/networking/remove-administrative-shares)
- [CIS Benchmark: 18.5.16.1 Ensure 'Domain member: Digitally encrypt or sign secure channel data (always)' is set to 'Enabled'](https://www.cisecurity.org/)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.