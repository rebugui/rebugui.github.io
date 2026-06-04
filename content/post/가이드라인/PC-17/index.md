---
title: "[2026 주요정보통신기반시설] PC-17 CD, DVD, USB 메모리 등과 같은 미디어의 자동 실행 방지 등 이동식 미디어에 대한 보안 대책 수립"
slug: "2026-주정통/PC-17"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "이동식미디어에대한보안대책수립여부점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - PC
---

# CD, DVD, USB 메모리 등과 같은 미디어의 자동 실행 방지 등 이동식 미디어에 대한 보안 대책 수립

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | PC-17 |
| **점검내용** | 이동식미디어에대한보안대책수립여부점검 |
| **점검대상** | Windows 10, Windows 11 |
| **양호기준** | 미디어사용시자동실행되지않고내부적으로관리절차를수립하여이행된경우 |
| **취약기준** | 미디어사용시자동실행되거나내부적으로관리절차가수립되지않은경우 |
| **조치방법** | 미디어자동실행방지설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 미디어 사용 시 자동 실행되지 않고 내부적으로 관리 절차를 수립하여 이행된 경우
- **취약**: 미디어 사용 시 자동 실행되거나 내부적으로 관리 절차가 수립되지 않은 경우

#### 경계 케이스 (Edge Case) 처리 방법
- **NoDriveTypeAutoRun = 0xDD (221)**: 기본값, 취약 판단
- **NoDriveTypeAutoRun = 0xFF (255)**: 모두 끔, 양호 판단
- **자동 실행 끄기 정책이 사용함으로 설정**: 양호

#### 권장 설정값
- **모든 미디어 및 장치에 자동 실행 사용**: 체크 해제
- **자동 실행 끄기**: 사용함

### 2. 점검 방법

#### Windows 10, 11에서의 점검

**제어판 확인:**
```
Step 1) 시작 > Windows Tools > 제어판
Step 2) 하드웨어 및 소리 > 자동 실행
```

**PowerShell 확인:**
```powershell
# 자동 실행 상태 확인
Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer" -Name "NoDriveTypeAutoRun" -ErrorAction SilentlyContinue
```

### 3. 조치 방법

#### 1. 제어판에서 자동 실행 비활성화

```
Step 1) 제어판 > 하드웨어 및 소리 > 자동 실행
Step 2) '모든 미디어 및 장치에 자동 실행 사용(U)' 체크 해제
Step 3) 저장(S) 클릭
```

#### 2. 레지스트리로 설정

```cmd
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer" /v NoDriveTypeAutoRun /t REG_DWORD /d 0xFF /f
```

### 4. 참고 자료

#### 이동식 미디어의 보안 위협

**Autorun.inf를 악용한 공격:**
- 악성 USB 제작
- 루트 디렉터리에 autorun.inf 배치
- USB 연결 시 자동 실행

**주요 보안 사고:**
- 2008년 Downadup(Conficker): USB AutoRun 악용
- 2010년 스타克斯넷(Stuxnet): USB 전파

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.