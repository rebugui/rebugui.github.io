---
title: "[2026 주요정보통신기반시설] W-18 불필요한 서비스 제거"
slug: "2026-주정통/W-18"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "불필요한서비스가동여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Windows
draft: true
---

# W-18 불필요한 서비스 제거

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | W-18 |
| **점검내용** | 불필요한서비스가동여부점검 |
| **점검대상** | Windows NT, 2000, 2003, 2008, 2012, 2016, 2019, 2022 |
| **양호기준** | 일반적으로불필요한서비스(아래목록참조)가중지된경우 |
| **취약기준** | 일반적으로불필요한서비스(아래목록참조)가구동중인경우 |
| **조치방법** | 서비스중지후'사용안함'설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 일반적으로 불필요한 서비스가 중지된 경우
- **취약**: 일반적으로 불필요한 서비스가 구동 중인 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| 서비스 종속성 | 주의 | 다른 서비스가 의존하는지 확인 필요 |
| 필수 서비스 | 양호 | 시스템 운영에 필수적인 서비스는 유지 |
| 시작 유형 '수동' | 양호 | 필요할 때만 시작되도록 설정 |
| 도메인 컨트롤러 | 주의 | AD 관련 서비스는 필수적 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| 모든 서버 | 불필요한 서비스 | 사용 안 함 | 시작 유형 |
| 모든 서버 | Telnet | 사용 안 함 | 평문 통신 (W-34) |
| 모든 서버 | SNMP | 사용 안 함 | 보안 취약 (W-29~31) |
| 모든 서버 | Messenger | 사용 안 함 | 스팸 악용 가능 |

### 2. 점검 방법

#### Windows 서버 점검

Windows 서버에 불필요한 서비스가 실행되고 있는지 점검하고, 이를 제거하거나 비활성화하여 공격 표면을 줄여야 합니다.

```bash
# PowerShell - 실행 중인 서비스 확인
Get-Service | Where-Object {$_.Status -eq 'Running'} | Select-Object Name, DisplayName

# 불필요한 서비스 확인
Get-Service -Name "Alerter", "ClipSrv", "Messenger", "RemoteRegistry" -ErrorAction SilentlyContinue
```

**양호 출력 예시:**
```text
(불필요한 서비스가 중지되거나 존재하지 않음)
```
불필요한 서비스가 중지된 경우 양호

**취약 출력 예시:**
```text
Name           DisplayName
----           -----------
Messenger      Messenger
RemoteRegistry Remote Registry Service
```
불필요한 서비스가 실행 중인 경우 취약

### 3. 조치 방법

#### Windows 서버 설정

1. **서비스 중지 및 비활성화 (PowerShell)**
   ```powershell
   # 서비스 중지
   Stop-Service -Name "Messenger" -Force

   # 시작 유형 변경 (사용 안 함)
   Set-Service -Name "Messenger" -StartupType Disabled
   ```

2. **여러 서비스 일괄 처리**
   ```powershell
   # 불필요한 서비스 목록
   $ServicesToStop = @("Alerter", "ClipSrv", "Messenger", "RemoteRegistry")
   foreach ($Service in $ServicesToStop) {
       Stop-Service -Name $Service -Force -ErrorAction SilentlyContinue
       Set-Service -Name $Service -StartupType Disabled -ErrorAction SilentlyContinue
   }
   ```

3. **명령 프롬프트 설정**
   ```cmd
   REM 서비스 중지
   net stop Messenger

   REM 시작 유형 변경 (사용 안 함)
   sc config Messenger start= disabled
   ```

4. **GUI로 설정**
   ```
   시작 > 제어판 > 서비스
   해당 서비스 선택 > 속성
   시작 유형: '사용 안 함'
   서비스 상태: '중지'
   ```

5. **서비스 종속성 확인**
   ```powershell
   # 특정 서비스에 의존하는 서비스 확인
   Get-Service | Where-Object {$_.RequiredServices -like "*Server*"} | Select-Object Name
   ```

### 4. 참고 자료

- [Microsoft Docs: 서비스 및 서비스 계정 보안 계획](https://technet.microsoft.com/ko-kr/library/dd547941.aspx)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.