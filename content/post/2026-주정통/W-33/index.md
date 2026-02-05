---
title: "[2026 주요정보통신기반시설] W-33 SMTP 서비스 인증 설정"
slug: "2026-주정통/W-33"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "HTTP/FTP/SMTP 서비스 배너 차단 적용 여부 점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Windows
---

# W-33 SMTP 서비스 인증 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | W-33 |
| **점검내용** | HTTP/FTP/SMTP 서비스 배너 차단 적용 여부 점검 |
| **점검대상** | Windows NT, 2000, 2003, 2008, 2012, 2016, 2019, 2022 |
| **양호기준** | HTTP, FTP, SMTP 접속 시 배너 정보가 보이지 않는 경우 |
| **취약기준** | HTTP, FTP, SMTP 접속 시 배너 정보가 보이는 경우 |
| **조치방법** | 사용하지 않는 경우 IIS 서비스 중지/사용 안 함, 사용시 속성값 수정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: SMTP 서비스가 비활성화되어 있거나, 익명 접속이 차단되고 인증이 설정된 경우
- **취약**: SMTP 서비스에서 익명 접속이 허용되어 Open Relay로 악용 가능한 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| 익명 액세스 활성화 | 취약 | Open Relay 위험 |
| 기본 인증만 활성화 | 양호 | 인증 필수 |
| 릴레이 "모든 컴퓨터" 허용 | 취약 | 스팸 발송 경로 |
| 릴레이 "목록에 있는 컴퓨터만" | 양호 | IP 제한됨 |
| TLS 암호화 활성화 | 양호 | 보안 강화 |
| SMTP 서비스 중지 | 양호 | 불필요한 경우 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| SMTP 인증 | 익명 액세스 | 사용 안 함 | 필수 |
| SMTP 인증 | 기본 인증 | 사용 | TLS와 함께 권장 |
| SMTP 인증 | Windows 통합 인증 | 사용 | 내부망 환경 |
| 릴레이 제한 | 릴레이 허용 | 목록에 있는 컴퓨터만 | IP 화이트리스트 |
| TLS | 암호화 | 사용 | 기본 인증 시 필수 |

### 2. 점검 방법

#### Windows SMTP 서비스 점검

SMTP 서비스가 익명 접속을 허용하면 스팸 메일 발송 경로로 악용될 수 있습니다. 반드시 인증이 필요하도록 설정해야 합니다.

```cmd
# telnet으로 SMTP 릴레이 테스트
telnet [SMTP서버IP] 25
```

```text
EHLO test.com
MAIL FROM:<attacker@bad.com>
RCPT TO:<victim@target.com>
```

**양호 출력 예시:**
```text
530 5.7.1 Client was not authenticated
```

**취약 출력 예시:**
```text
250 2.1.0 OK
```

```powershell
# SMTP 서비스 상태 확인
Get-Service -Name "SMTPSVC" -ErrorAction SilentlyContinue | Select-Object Name, Status, StartType
```

```cmd
# SMTP 포트 확인
netstat -an | findstr ":25"
```

### 3. 조치 방법

#### Windows SMTP 서비스 설정

1. **SMTP 인증 설정 (IIS 6.0 관리자)**
   ```
   1. 시작 > 관리 도구 > IIS 6.0 관리자 실행
   2. [SMTP Virtual Server] 우클릭 > 속성
   3. [액세스] 탭 > [인증] 클릭
   4. "익명 액세스" 체크 해제 (가장 중요)
   5. "기본 인증" 체크
   6. "TLS 암호화" 체크 (권장)
   7. [확인]
   ```

2. **릴레이 제한 설정**
   ```
   1. 동일한 속성 창에서 [액세스] 탭 > [릴레이] 클릭
   2. "아래 목록 제외하고 모두(모든 컴퓨터)" 대신 "목록에 있는 컴퓨터만" 선택
   3. [추가] 클릭하여 릴레이를 허용할 내부 서버 IP만 등록
   4. [확인]
   ```

3. **SMTP 서비스 비활성화 (사용하지 않는 경우)**
   ```powershell
   # SMTP 서비스 중지
   Stop-Service -Name "SMTPSVC" -Force

   # 시작 유형 변경
   Set-Service -Name "SMTPSVC" -StartupType Disabled

   # 방화벽 규칙 차단
   Disable-NetFirewallRule -DisplayGroup "SMTP Server"
   ```

4. **서비스 재시작**
   ```powershell
   # SMTP 서비스 재시작
   Restart-Service -Name "SMTPSVC"
   ```

### 4. 참고 자료

- [Microsoft Docs: SMTP 릴레이 제한](https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2008-R2-and-2008/cc772058(v=ws.10))
- [CIS Benchmark: 18.5.18.1 Ensure 'SMTP Server' is set to 'Disabled' or 'Secure'](https://www.cisecurity.org/)
- [RFC 5321: Simple Mail Transfer Protocol](https://tools.ietf.org/html/rfc5321)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.