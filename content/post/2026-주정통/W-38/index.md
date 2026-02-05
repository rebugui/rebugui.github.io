---
title: "[2026 주요정보통신기반시설] W-38 주기적 보안 패치 및 벤더 권고 사항 적용"
slug: "2026-주정통/W-38"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "최신 보안 패치 적용 여부 점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Windows
---

# W-38 주기적 보안 패치 및 벤더 권고 사항 적용

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | W-38 |
| **점검내용** | 최신 보안 패치 적용 여부 점검 |
| **점검대상** | Windows NT, 2000, 2003, 2008, 2012, 2016, 2019, 2022 |
| **양호기준** | 패치 절차를 수립하여 주기적으로 패치를 확인 및 설치하는 경우 |
| **취약기준** | 패치 절차가 수립되어 있지 않거나 주기적으로 패치를 설치하지 않는 경우 |
| **조치방법** | 주기적인 보안 패치 확인 및 설치 적용 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 보안 패치 적용 정책/절차가 수립되어 있고, 주기에 맞춰 패치 적용 여부를 확인 및 조치하는 경우
- **취약**: 별도의 패치 관리 절차가 없거나, 장기간 패치가 누락된 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| 패치 절차서 보유 | 양호 | 관리 체계 수립 |
| WSUS 구축 운영 | 양호 | 중앙 관리 |
| 수동 업데이트만 수행 | 주의 | 자동화 권장 |
| 1개월 내 패치 완료 | 양호 | 일반적 허용 범위 |
| 3개월 이상 패치 누락 | 취약 | 보안 위험 |
| 긴급 패치 절차 | 양호 | Zero-Day 대응 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| 업데이트 소스 | WSUS 또는 Windows Update | 중앙 관리 | 기업 환경 |
| 업데이트 주기 | 검사 주기 | 매일 | 자동 검사 |
| 업데이트 설치 | 자동 설치 | 승인 후 자동 | 테스트 환경 확인 후 |
| 패치 절차 | 문서화 | 보유 | 절차서 수립 |
| 긴급 패치 | 절차 | 별도 보유 | Zero-Day 대응 |

### 2. 점검 방법

#### Windows 서버 점검

보안 패치를 주기적으로 확인하고 적용하는 관리 체계가 수립되어 있는지 확인합니다.

```powershell
# 최근 업데이트 설치 내역 확인
Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 20
```

**양호 출력 예시:**
```text
Source        Description      HotFixID      InstalledOn
------        -----------      --------      -----------
DESKTOP-...   Update           KB5034441     2024-01-15 00:00:00
DESKTOP-...   Update           KB5034439     2024-01-10 00:00:00
...최신 패치들이 최근 1~2개월 내에 설치됨
```

**취약 출력 예시:**
```text
(3개월 이상 된 패치만 존재하거나 패치 미존재)
```

```powershell
# Windows 업데이트 설정 확인
Get-ItemProperty "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU" -ErrorAction SilentlyContinue
```

```cmd
# WSUS 클라이언트 설정 확인
reg query "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate" /v WUServer
```

### 3. 조치 방법

#### 패치 관리 체계 수립

1. **패치 관리 절차 수립**
   ```
   [1단계: 정보 수집]
   - Microsoft 보안 공지(MSRC) 메일링 구독
   - KISA 보안공지 주기적 확인

   [2단계: 영향도 평가]
   - 해당 패치의 시스템 영향도 분석
   - 재부팅 필요 여부 확인

   [3단계: 테스트 적용]
   - 개발/테스트 서버에 먼저 설치
   - 애플리케이션 호환성 테스트

   [4단계: 운영 적용]
   - 유지보수 시간대에 적용
   - 서비스 모니터링

   [5단계: 결과 확인]
   - 설치 로그 확인
   - 이상 징후 모니터링 및 문서화
   ```

2. **WSUS 구축 (기업 환경)**
   ```powershell
   # WSUS 서버 지정
   Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate" -Name "WUServer" -Value "http://wsus-server:8530"
   Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate" -Name "WUStatusServer" -Value "http://wsus-server:8530"

   # 자동 업데이트 설정
   Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU" -Name "UseWUServer" -Value 1
   Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU" -Name "AUOptions" -Value 4
   Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU" -Name "ScheduledInstallDay" -Value 0
   Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU" -Name "ScheduledInstallTime" -Value 3
   ```

3. **PowerShell을 통한 업데이트 확인**
   ```powershell
   # PSWindowsUpdate 모듈 사용
   Install-Module -Name PSWindowsUpdate -Force
   Get-WindowsUpdate -MicrosoftUpdate
   ```

### 4. 참고 자료

- [KISA: 정보보호 및 개인정보보호 관리체계(ISMS-P) 인증 기준 - 2.10.2 시스템 보안 패치](https://www.kisa.or.kr/)
- [Microsoft Security Response Center](https://msrc.microsoft.com/update-guide/)
- [NIST SP 800-40 Rev 3: Creating a Patch and Vulnerability Management Program](https://csrc.nist.gov/publications/detail/sp/800-40/rev-3/final)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.