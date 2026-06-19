---
title: "[2026 주요정보통신기반시설] W-19 불필요한 IIS 서비스 구동 점검"
slug: "2026-주정통/W-19"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "불필요한IIS서비스구동여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Windows
draft: true
---

# W-19 불필요한 IIS 서비스 구동 점검

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | W-19 |
| **점검내용** | 불필요한IIS서비스구동여부점검 |
| **점검대상** | Windows NT, 2000, 2003, 2008, 2012, 2016, 2019, 2022 |
| **양호기준** | IIS서비스를사용하지않는경우또는필요에의해IIS서비스를사용하는경우 |
| **취약기준** | IIS서비스를불필요하게사용하는경우 |
| **조치방법** | IIS서비스가불필요한경우IIS서비스중지 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: IIS 서비스를 사용하지 않거나, 서비스가 중지되어 있는 경우
- **취약**: 불필요한 IIS 서비스가 구동 중인 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| 웹 서버 용도 | 양호 | 웹 서비스 제공 목적이면 정상 |
| Exchange/WSUS | 양호 | 웹 인터페이스 사용 시 IIS 필요 |
| SharePoint | 양호 | SharePoint는 IIS 기반 서비스 |
| 관리 도구 | 주의 | IIS Manager를 통한 원격 관리 가능 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| 비웹 서버 | World Wide Web Publishing Service | 사용 안 함 | 불필요한 웹 서비스 제거 |
| 비웹 서버 | IIS Admin Service | 사용 안 함 | 또는 IIS 완전 제거 |
| 웹 서버 | IIS | 사용 | 보안 설정 강화 필요 |

### 2. 점검 방법

#### Windows 서버 점검

웹 서비스가 필요하지 않은 시스템에서 IIS 서비스가 실행되고 있는지 점검하여 불필요한 공격 표면을 제거해야 합니다.

```bash
# PowerShell - IIS 서비스 확인
get-service "W3SVC", "IISADMIN" -ErrorAction SilentlyContinue

# 또는 포트 확인 (TCP 80)
netstat -na | findstr ":80"
```

**양호 출력 예시:**
```text
서비스를 찾을 수 없음
또는
Status    Name
------    ----
Stopped   W3SVC
Stopped   IISADMIN
```
IIS 서비스가 중지되거나 없으면 양호

**취약 출력 예시:**
```text
Status    Name
------    ----
Running   W3SVC
Running   IISADMIN
```
IIS 서비스가 실행 중이면 취약

### 3. 조치 방법

#### Windows 서버 설정

1. **서비스 중지 및 비활성화 (PowerShell)**
   ```powershell
   # World Wide Web Publishing Service 중지
   Stop-Service -Name W3SVC -Force
   Set-Service -Name W3SVC -StartupType Disabled
   ```

2. **명령 프롬프트 설정**
   ```cmd
   sc stop W3SVC
   sc config W3SVC start= disabled
   ```

3. **GUI로 설정**
   ```
   시작 > 실행 > services.msc
   "World Wide Web Publishing Service" 더블클릭
   시작 유형: "사용 안 함" 선택
   서비스 상태: "중지" 클릭 > 확인
   ```

4. **IIS 기능 제거 (가장 확실함)**
   ```powershell
   # PowerShell로 IIS 제거
   Uninstall-WindowsFeature -Name Web-Server -Restart
   ```

5. **서버 관리자로 제거**
   ```
   서버 관리자 > 관리 > 역할 및 기능 제거
   서버 역할 선택에서 "Web Server (IIS)" 체크 해제
   마법사 진행하여 제거 완료 및 재부팅
   ```

### 4. 참고 자료

- [Microsoft Docs: IIS 관리](https://docs.microsoft.com/ko-kr/iis/)
- [KISA 주요정보통신기반시설 취약점 진단 가이드라인](https://www.kisa.or.kr/)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.