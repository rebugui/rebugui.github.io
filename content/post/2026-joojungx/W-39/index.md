---
title: "[2026 주요정보통신기반시설] W-39 백신 프로그램 업데이트"
slug: "2026-주정통/W-39"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "사용 백신 프로그램의 최신 업데이트 여부 점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Windows
---

# W-39 백신 프로그램 업데이트

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | W-39 |
| **점검내용** | 사용 백신 프로그램의 최신 업데이트 여부 점검 |
| **점검대상** | Windows NT, 2000, 2003, 2008, 2012, 2016, 2019, 2022 |
| **양호기준** | 백신 프로그램이 최신 엔진/패턴으로 업데이트되어 있고, 자동 업데이트가 설정된 경우 |
| **취약기준** | 백신 프로그램이 설치되지 않았거나, 업데이트가 장기간(보통 1주 이상) 지연된 경우 |
| **조치방법** | 백신 프로그램 환경설정 메뉴를 통해 DB 및 엔진의 최신 업데이트를 하도록 설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 백신 프로그램의 엔진 및 패턴(바이러스 정의 파일)이 최신 버전으로 업데이트되어 있고, 자동 업데이트가 설정된 경우
- **취약**: 백신 프로그램이 설치되지 않았거나, 업데이트가 장기간 지연된 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| 업데이트 1일 이내 | 양호 | 최신 상태 유지 |
| 업데이트 1주 이내 | 주의 | 허용 가능하나 개선 권장 |
| 업데이트 1개월 이상 | 취약 | 보안 위험 상태 |
| 백신 프로그램 미설치 | 취약 | 즉시 설치 필요 |
| 라이선스 만료 | 취약 | 업데이트 중단 |
| 엔진만 업데이트됨 | 주의 | 패턴도 함께 업데이트 필요 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| 백신 업데이트 | 자동 업데이트 | 사용(매일) | 인터넷 연결 환경 |
| 백신 업데이트 | 업데이트 주기 | 매일 | 실시간 권장 |
| 백신 업데이트 | 엔진 업데이트 | 함께 사용 | 엔진+패턴 모두 |
| 중앙 관리 | 관리 서버 | 구축 권장 | 다수 서버 환경 |
| 스캔 | 실시간 감시 | 사용 | 상시 감시 |

### 2. 점검 방법

#### Windows 백신 프로그램 점검

백신 프로그램이 최신 엔진과 패턴으로 업데이트되어 있는지 확인하여 신종 악성코드로부터 시스템을 보호해야 합니다.

```powershell
# Windows Defender 상태 확인 (Windows Defender 사용 시)
Get-MpComputerStatus | Select-Object AntivirusEnabled, QuickScanAge, FullScanAge, AntivirusSignatureLastUpdated
```

**양호 출력 예시:**
```text
AntivirusEnabled               : True
AntivirusSignatureLastUpdated : 2024-01-15 오전 10:30:00
QuickScanAge                  : 0
FullScanAge                   : 1.00:00:00
```

**취약 출력 예시:**
```text
AntivirusEnabled               : False
또는
AntivirusSignatureLastUpdated : 2023-12-01 (오래된 업데이트)
```

```powershell
# 타사 백신 프로그램 업데이트 확인 (예: AhnLab, V3 등)
# 각 벤더사에서 제공하는 CLI 또는 레지스트리 확인 필요
Get-ItemProperty "HKLM:\SOFTWARE\AhnLab\Ahn-V3" -Name "PatternVersion" -ErrorAction SilentlyContinue
```

```cmd
# 백신 서비스 상태 확인
sc query "WinDefend"
```

### 3. 조치 방법

#### Windows 백신 프로그램 설정

1. **Windows Defender 업데이트 설정**
   ```
   1. 시작 > 설정 > 업데이트 및 보안 > Windows 보안
   2. "바이러스 및 위협 방지" 선택
   3. "바이러스 및 위협 방지 업데이트" 섹션 확인
   4. [업데이트 확인] 클릭
   ```

2. **자동 업데이트 설정 (PowerShell)**
   ```powershell
   # Windows Defender 업데이트 실행
   Update-MpSignature

   # 스케줄링된 업데이트 설정
   Set-MpPreference -SignatureScheduleDay Everyday -SignatureScheduleTime 2 -SignatureUpdateInterval 4
   ```

3. **타사 백신 프로그램 자동 업데이트 설정**
   ```
   [일반적인 설정 방법]
   1. 백신 프로그램 실행
   2. 설정 > 업데이트 메뉴
   3. "자동 업데이트 사용" 체크
   4. 업데이트 주기: "매일" 또는 "실시간" 선택
   5. [확인]
   ```

4. **중앙 관리 서버 구축 (다수 서버 환경)**
   - 각 백신 벤더사에서 제공하는 중앙 관리 서버(Management Server) 구축
   - 인터넷이 되는 관리 서버가 패턴을 수신
  - 내부 서버들은 관리 서버로부터 패턴 수신

5. **수동 업데이트 (완전 폐쇄망)**
   - 벤더 사이트에서 최신 업데이트 파일 다운로드
   - USB 등으로 반입하여 수동 설치

### 4. 참고 자료

- [KISA 보호나라: 주요 백신 다운로드](https://www.boho.or.kr/kr/sub.do?menuNo=201460)
- [Microsoft Docs: Windows Defender 업데이트](https://docs.microsoft.com/ko-kr/microsoft-365/security/defender-endpoint/manage-updates-baselines-windows-defender-antivirus)
- [CIS Benchmark: 18.5.22.1 Ensure 'Microsoft Defender Antivirus' is 'Installed' and 'Enabled'](https://www.cisecurity.org/)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.