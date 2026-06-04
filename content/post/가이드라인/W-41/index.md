---
title: "[2026 주요정보통신기반시설] W-41 NTP 및 시각 동기화 설정"
slug: "2026-주정통/W-41"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "NTP 및 시각 동기화 설정 여부 점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Windows
---

# W-41 NTP 및 시각 동기화 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | W-41 |
| **점검내용** | NTP 및 시각 동기화 설정 여부 점검 |
| **점검대상** | Windows NT, 2000, 2003, 2008, 2012, 2016, 2019, 2022 |
| **양호기준** | NTP 및 시각 동기화를 설정한 경우 |
| **취약기준** | NTP 및 시각 동기화를 설정하지 않은 경우 |
| **조치방법** | NTP 및 시각 동기화 설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 외부 NTP 서버 또는 내부 Time Server와 주기적으로 동기화하도록 설정된 경우
- **취약**: 시간 동기화 설정이 되어 있지 않거나, 오차가 큰 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| NTP 서버 구성됨 | 양호 | 동기화 설정됨 |
| Local CMOS Clock | 취약 | 동기화 미설정 |
| 동기화 1일 이상 지연 | 취약 | 시간 오차 큼 |
| 도메인 컨트롤러 | 양호 | 자동 동기화 (AD 환경) |
| 방화벽 차단됨 | 취약 | UDP 123 차단 |
| 수동으로 시간 설정 | 취약 | 일일하지 않음 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| NTP 서버 | time.windows.com | 사용 | 기본 Microsoft NTP |
| NTP 서버 | time.google.com | 사용 | Google NTP |
| NTP 서버 | time.kriss.re.kr | 사용 | 한국 표준과학연구원 |
| 동기화 주기 | 7일 마다(기본) | 사용 | 자동 동기화 |
| 방화벽 | UDP 123 | 아웃바운드 허용 | NTP 포트 |

### 2. 점검 방법

#### Windows 시간 동기화 점검

시스템 시간이 신뢰할 수 있는 NTP 서버와 동기화되어 있어야, 정확한 로그 분석과 보안 인증이 가능합니다.

```cmd
# NTP 설정 확인
w32tm /query /status
```

**양호 출력 예시:**
```text
Leap Indicator: 0(no warning)
Stratum: 3 (secondary reference - syncd by radio)
Precision: -6 (15.625ms)
Root Delay: 0.0398125s
Root Dispersion: 0.00791634s
ReferenceId: 0x97B71C37 (source IP:  151.101.114.114)
Last Successful Sync Time: 2024-01-15 오전 10:30:00
Source: time.windows.com,0x8
```

**취약 출력 예시:**
```text
Last Successful Sync Time: 2023-12-01 (오래된 동기화)
또는
Source: Local CMOS Clock
```

```cmd
# w32tm 설정 확인
w32tm /query /configuration
```

```cmd
# 방화벽 UDP 123 확인
netsh advfirewall firewall show rule name="AllProfiles NTP-Server-Out"
```

### 3. 조치 방법

#### Windows 시간 동기화 설정

1. **GUI로 NTP 서버 설정**
   ```
   1. 제어판 > 날짜 및 시간 > [인터넷 시간] 탭
   2. [설정 변경] 클릭
   3. [v] 인터넷 시간 서버와 동기화
   4. 서버: time.windows.com 또는 time.kriss.re.kr 입력
   5. [지금 업데이트] 클릭
   6. [확인]
   ```

2. **명령줄로 NTP 설정**
   ```cmd
   # NTP 서버 목록 설정
   w32tm /config /manualpeerlist:"time.windows.com,0x8 time.google.com,0x8" /syncfromflags:MANUAL /update

   # 동기화 강제 수행
   w32tm /resync
   ```

3. **AD 도메인 환경**
   ```
   [기본 설정]
   Active Directory 환경에서는 자동으로 도메인 컨트롤러(PDC Emulator)와 시간을 동기화합니다.

   [PDC Emulator에서만 외부 NTP 설정 필요]
   1. 도메인 컨트롤러에서 명령 프롬프트 관리자 권한으로 실행
   2. w32tm /config /manualpeerlist:"time.kriss.re.kr,0x8" /syncfromflags:MANUAL /update
   3. w32tm /resync
   ```

4. **방화벽 NTP 포트 허용**
   ```cmd
   # UDP 123 아웃바운드 허용
   netsh advfirewall firewall add rule name="NTP-Server-Out" dir=out action=allow protocol=UDP localport=any remoteport=123
   ```

### 4. 참고 자료

- [Microsoft Docs: Windows Time Service 도구 및 설정](https://docs.microsoft.com/ko-kr/windows-server/networking/windows-time-service/windows-time-service-tools-and-settings)
- [KRISS: 한국 표준시각 서비스](https://www.kriss.re.kr/)
- [NIST: Internet Time Service](https://www.nist.gov/pml/time-and-frequency-division/internet-time-service)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.