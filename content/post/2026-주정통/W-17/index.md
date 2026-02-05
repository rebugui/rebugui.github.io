---
title: "[2026 주요정보통신기반시설] W-17 하드디스크 기본 공유 제거"
slug: "2026-주정통/W-17"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "하드디스크기본공유제거여부점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Windows
---

# W-17 하드디스크 기본 공유 제거

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | W-17 |
| **점검내용** | 하드디스크기본공유제거여부점검 |
| **점검대상** | Windows NT, 2000, 2003, 2008, 2012, 2016, 2019, 2022 |
| **양호기준** | 레지스트리의AutoShareServer(WinNT:AutoShareWks)가0이며기본공유가존재하지않는경우 |
| **취약기준** | AutoShareServer가1이거나기본공유가존재하는경우 |
| **조치방법** | 기본공유중지후레지스트리값설정(IPC$,일반공유제외) |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: AutoShareServer(AutoShareWks)가 0이며 기본 공유(C$, D$, Admin$)가 존재하지 않는 경우
- **취약**: AutoShareServer가 1이거나 기본 공유가 존재하는 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| IPC$ 공유 | 양호 | IPC$는 네트워크 통신에 필수적이므로 제거하지 않음 |
| Active Directory 도메인 컨트롤러 | 주의 | AD 환경에서는 관리 기능에 영향 주의 필요 |
| 원격 관리 필요 | 주의 | 원격 관리 도구 사용 시 기본 공유 필요 가능 |
| 레지스트리 값 없음 | 취약 | 기본값은 1(사용)임 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| 독립 서버 | AutoShareWks | 0 | 워크스테이션 |
| 일반 서버 | AutoShareServer | 0 | 서버 OS |
| 도메인 컨트롤러 | AutoShareServer | 1 | AD 관리용 |
| IPC$ | 유지 | 필수 | 네트워크 통신용 |

### 2. 점검 방법

#### Windows 서버 점검

Windows가 자동으로 생성하는 관리용 공유(Administrative Shares)인 C$, D$, Admin$ 등을 제거하여 시스템 보안을 강화해야 합니다.

```bash
# PowerShell - 관리용 공유 확인
Get-SmbShare | Where-Object {$_.Name -like "*$"}

# 레지스트리 확인
Get-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters" -Name "AutoShareWks" -ErrorAction SilentlyContinue
Get-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters" -Name "AutoShareServer" -ErrorAction SilentlyContinue
```

**양호 출력 예시:**
```text
AutoShareServer : 0
또는
AutoShareWks : 0
```
값이 0이면 기본 공유 사용 안 함으로 양호

**취약 출력 예시:**
```text
AutoShareServer : 1
또는
AutoShareWks : 1
또는
C$, D$, ADMIN$ 공유가 존재
```
값이 1이거나 기본 공유가 있으면 취약

### 3. 조치 방법

#### Windows 서버 설정

1. **레지스트리 설정 (워크스테이션)**
   ```powershell
   # 관리자 권한 PowerShell 실행
   Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters" -Name "AutoShareWks" -Value 0 -Type DWord
   ```

2. **레지스트리 설정 (서버)**
   ```powershell
   # 관리자 권한 PowerShell 실행
   Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters" -Name "AutoShareServer" -Value 0 -Type DWord
   ```

3. **명령 프롬프트 설정**
   ```cmd
   reg add "HKLM\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters" /v AutoShareServer /t REG_DWORD /d 0 /f
   ```

4. **기존 공유 제거**
   ```powershell
   # C$ 공유 제거
   Remove-SmbShare -Name "C$" -Force

   # Admin$ 공유 제거
   Remove-SmbShare -Name "ADMIN$" -Force
   ```

5. **시스템 재시작**
   ```powershell
   # 설정 적용을 위해 시스템 재부팅 권장
   Restart-Computer
   ```

### 4. 참고 자료

- [Microsoft Docs: 서버 관리를 위한 기본 공유](https://docs.microsoft.com/ko-ko/troubleshoot/windows-server/networking/default-administrative-shares)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.