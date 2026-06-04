---
title: "[2026 주요정보통신기반시설] W-36 복구 콘솔 비활성화"
slug: "2026-주정통/W-36"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "원격 터미널 접속 Timeout 설정 여부 점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Windows
---

# W-36 복구 콘솔 비활성화

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | W-36 |
| **점검내용** | 원격 터미널 접속 Timeout 설정 여부 점검 |
| **점검대상** | Windows 2000, 2003, 2008, 2012, 2016, 2019, 2022 |
| **양호기준** | 원격 제어 시 Timeout 제어 설정을 30분 이하로 설정한 경우 |
| **취약기준** | 원격 제어 시 Timeout 제어 설정을 적용하지 않거나 30분 초과로 설정한 경우 |
| **조치방법** | Timeout 제어 설정 적용 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 복구 콘솔의 자동 로그온이 금지되어 있고, 시스템 부팅 메뉴에서 불필요하게 노출되지 않는 경우
- **취약**: 복구 콘솔 자동 로그온이 설정되어 있거나, 누구나 제약 없이 복구 모드를 실행할 수 있는 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| "자동 관리 로그온 허용" 사용 안 함 | 양호 | 인증 필수 |
| "자동 관리 로그온 허용" 사용 | 취약 | 암호 없이 접근 가능 |
| recoveryenabled = No | 양호 | 자동 복구 비활성화 |
| recoveryenabled = Yes | 주의 | 정상 부팅 시 장애 가능 |
| BitLocker 활성화 | 양호 | 물리적 접근 방어 |
| BIOS/UEFI 패스워드 설정 | 양호 | 부팅 제어 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| 로컬 보안 정책 | 자동 관리 로그온 허용 | 사용 안 함 | 비밀번호 요구 |
| BCD | recoveryenabled | No(필요시) | 자동 복구 제한 |
| 물리적 보안 | 서버실 접근 통제 | 필수 | 기본 보안 |
| 디스크 암호화 | BitLocker | 사용 | 데이터 보호 |

### 2. 점검 방법

#### Windows 복구 콘솔 점검

복구 콘솔이 무분별하게 사용되면, 물리적 접근이 가능한 공격자가 시스템을 장악할 수 있습니다.

```powershell
# 로컬 보안 정책 확인 (Windows 2003 이하)
Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Control\LSA" -Name "DisableRecoveryConsole" -ErrorAction SilentlyContinue
```

```cmd
# bcdedit 확인 (Windows 2008 이상)
bcdedit /enum
```

**양호 출력 예시:**
```text
recoveryenabled    No
또는
Windows Boot Loader에 복구 관련 항목 없음
```

**취약 출력 예시:**
```text
recoveryenabled    Yes
```

```powershell
# 복구 콘솔 자동 로그온 정책 확인
# (구형 OS에 해당, 신규 OS에는 해당 정책 없음)
Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Setup\RecoveryConsole" -Name "SecurityLevel" -ErrorAction SilentlyContinue
```

### 3. 조치 방법

#### Windows 서버 설정

1. **복구 콘솔 자동 로그온 비활성화 (구형 OS)**
   ```
   1. 시작 > 실행 > secpol.msc
   2. 로컬 정책 > 보안 옵션
   3. "복구 콘솔: 자동 관리 로그온 허용" > [사용 안 함]
   ```

2. **BCD 설정 (최신 OS)**
   ```cmd
   # 자동 복구 비활성화
   bcdedit /set {default} recoveryenabled No

   # 확인
   bcdedit /enum {current}
   ```

3. **고급 부팅 옵션 제한 (최신 OS)**
   ```cmd
   # 고급 부팅 옵션 메뉴 비활성화
   bcdedit /set {bootmgr} displaybootmenu No

   # 재부팅 시간 단축
   bcdedit /timeout 10
   ```

4. **BitLocker 활성화 (권장 대안)**
   ```powershell
   # C: 드라이브 BitLocker 활성화
   Enable-BitLocker -MountPoint "C:" -UsedSpaceOnly -EncryptionMethod XtsAes256

   # TPM + PIN 프로비저닝
   # (BIOS에서 TPM 활성화 필요)
   ```

### 4. 참고 자료

- [Microsoft Docs: BitLocker 개요](https://docs.microsoft.com/ko-kr/windows/security/information-protection/bitlocker/bitlocker-overview)
- [CIS Benchmark: 18.5.2.1 Ensure 'Boot recovery on a system failure' is set to 'Disabled' (if possible)](https://www.cisecurity.org/)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.