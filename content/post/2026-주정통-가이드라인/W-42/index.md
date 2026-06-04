---
title: "[2026 주요정보통신기반시설] W-42 이벤트 로그 관리 설정"
slug: "2026-주정통/W-42"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "이벤트 로그 파일 용량 및 보관 기간 설정 점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Windows
---

# W-42 이벤트 로그 관리 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | W-42 |
| **점검내용** | 이벤트 로그 파일 용량 및 보관 기간 설정 점검 |
| **점검대상** | Windows NT, 2000, 2003, 2008, 2012, 2016, 2019, 2022 |
| **양호기준** | 최대 로그 크기 '10,240KB 이상'으로 설정, '90일 이후 이벤트 덮어씀'을 설정한 경우 |
| **취약기준** | 최대 로그 크기 '10,240KB 미만'으로 설정, 이벤트 덮어씀 기간이 '90일 이하로 설정된 경우 |
| **조치방법** | 최대 로그 크기 '10,204KB', '90일 이후 이벤트 덮어씀' 설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 주요 로그(Application, Security, System)의 최대 크기가 충분(10MB 이상)하고, "필요한 경우 이벤트 덮어쓰기" 등으로 설정되어 있는 경우
- **취약**: 로그 크기가 너무 작거나(권장 미만), 보관 정책이 미흡한 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| 로그 크기 20MB 이상 | 양호 | 넉넉한 공간 |
| 로그 크기 10MB 미만 | 취약 | 공간 부족 우려 |
| 덮어쓰기 설정됨 | 양호 | 서비스 중단 없음 |
| 이벤트를 덮어쓰지 않음 | 취약 | 로그 꽉 찰 시 문제 |
| 보관 기간 미설정 | 주의 | 설정 필요 |
| C: 드라이브 부족 | 주의 | 별도 파티션 권장 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| 이벤트 로그 | 최대 크기(KB) | 20480 (20MB) 이상 | KISA 권고: 10,240KB |
| 이벤트 로그 | 보관 정책 | 필요 시 덮어쓰기 | 자동 관리 |
| 이벤트 로그 | 로그 경로 | 별도 파티션 권장 | D:\Logs\ 등 |
| 중앙 집중화 | SIEM/Syslog | 사용 권장 | 외부 전송 |

### 2. 점검 방법

#### Windows 이벤트 로그 점검

이벤트 로그 용량이 부족하면 중요 보안 이벤트가 기록되지 않거나(Lost), 너무 빨리 덮어씌워질 수 있습니다.

```cmd
# 이벤트 로그 설정 확인 (wevtutil)
wevtutil gl Security
wevtutil gl System
wevtutil gl Application
```

**양호 출력 예시:**
```text
name: Security
logFilePath: %SystemRoot%\System32\Winevt\Logs\Security.evtx
maxSize: 20971520 (20MB)
retention: false
autoBackup: false
```

**취약 출력 예시:**
```text
maxSize: 524288 (512KB)
또는
retention: true (로그 꽉 찰 시 문제 발생 가능)
```

```powershell
# PowerShell로 확인
Get-EventLog -List | Select-Object Log, MaximumKilobytes, MinimumRetentionDays, OverflowAction
```

### 3. 조치 방법

#### Windows 이벤트 로그 설정

1. **이벤트 로그 크기 설정 (GUI)**
   ```
   1. 이벤트 뷰어 실행 (eventvwr.msc)
   2. [Windows 로그] > [보안] 우클릭 > [속성]
   3. **최대 로그 크기(KB)**: 20480 (20MB) 입력
   4. **최대 로그 크기에 도달할 때**:
      - [v] 필요한 경우 이벤트 덮어쓰기(가장 오래된 이벤트부터)
   5. [확인]
   6. [시스템], [응용 프로그램]에 대해서도 동일하게 설정
   ```

2. **이벤트 로그 크기 설정 (PowerShell)**
   ```powershell
   # 보안 로그 크기 설정 (20MB = 20480 KB)
   Limit-EventLog -LogName Security -MaximumSize 20MB

   # 시스템 로그
   Limit-EventLog -LogName System -MaximumSize 20MB

   # 응용 프로그램 로그
   Limit-EventLog -LogName Application -MaximumSize 20MB
   ```

3. **이벤트 로그 경로 변경 (별도 파티션)**
   ```powershell
   # 레지스트리로 경로 변경
   $logPath = "D:\Logs\Security.evtx"
   Set-ItemProperty -Path "HKLM\SYSTEM\CurrentControlSet\Services\EventLog\Security" -Name "File" -Value $logPath
   ```

4. **GPO(그룹 정책)로 일괄 설정**
   ```
   1. 그룹 정책 관리자 (gpmc.msc) 실행
   2. 컴퓨터 구성 > 정책 > 관리 템플릿 > Windows 구성 요소 > 이벤트 로그 서비스
   3. [보안], [시스템], [응용 프로그램] 각각 설정
   4. "로그 파일의 최대 크기(KB)" 설정
   5. "로그 처리 방법" 설정
   ```

### 4. 참고 자료

- [Microsoft Docs: 이벤트 로그](https://docs.microsoft.com/ko-kr/windows/win32/eventlog/event-logging)
- [CIS Benchmark: 18.9.32.1.2 Ensure 'Application: Specify the maximum log file size (KB)' is set to 'Enabled: 32,768 or greater'](https://www.cisecurity.org/)
- [NIST SP 800-92: Guide to Computer Security Log Management](https://csrc.nist.gov/publications/detail/sp/800-92/final)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.