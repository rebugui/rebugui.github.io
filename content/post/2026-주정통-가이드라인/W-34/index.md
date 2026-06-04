---
title: "[2026 주요정보통신기반시설] W-34 Telnet 서비스 비활성화"
slug: "2026-주정통/W-34"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "Telnet 서비스 활성화 및 취약한 인증 사용 여부 점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Windows
---

# W-34 Telnet 서비스 비활성화

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | W-34 |
| **점검내용** | Telnet 서비스 활성화 및 취약한 인증 사용 여부 점검 |
| **점검대상** | Windows NT, 2000, 2003, 2008, 2012 |
| **양호기준** | Telnet 서비스가 구동되어 있지 않거나 인증 방법이 NTLM인 경우 |
| **취약기준** | Telnet 서비스가 구동되어 있으며 인증 방법이 NTLM이 아닌 경우 |
| **조치방법** | 불필요시 서비스 중지/사용 안 함 설정, 사용시 인증 방법으로 NTLM만 사용 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: Telnet 서비스가 비활성화되어 있거나 설치되어 있지 않은 경우
- **취약**: Telnet 서비스가 '실행 중'인 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| Telnet 서비스 중지됨 | 양호 | 안전한 상태 |
| Telnet 서비스 실행 중 | 취약 | 즉시 중지 필요 |
| 시작 유형 '수동' | 주의 | 비활성화 권장 |
| Telnet Client만 설치됨 | 주의 | 불필요하면 제거 |
| OpenSSH 사용 중 | 양호 | 안전한 대안 |
| 레거시 장비 연결용 | 주의 | SSH로 마이그레이션 권장 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| Telnet 서비스 | 상태 | 중지 | 불필요한 서비스 |
| Telnet 서비스 | 시작 유형 | 사용 안 함 | 자동 시작 방지 |
| Telnet Client | 기능 | 제거 권장 | 불필요 시 |
| 대체 서비스 | OpenSSH Server | 사용 | 암호화 원격 접속 |
| 방화벽 | TCP 23 | 차단 | Telnet 포트 |

### 2. 점검 방법

#### Windows Telnet 서비스 점검

Telnet은 모든 데이터를 평문으로 전송하므로, 패킷 스니핑을 통해 계정 정보와 명령어가 탈취될 수 있습니다.

```powershell
# Telnet 서비스 상태 확인
Get-Service -Name "TlntSvr" -ErrorAction SilentlyContinue | Select-Object Name, Status, StartType
```

**양호 출력 예시:**
```text
Name     Status  StartType
----     ------  ---------
TlntSvr  Stopped Disabled
또는
(서비스 없음)
```

**취약 출력 예시:**
```text
Name     Status  StartType
----     ------  ---------
TlntSvr  Running Automatic
```

```cmd
# Telnet 포트 리스닝 확인
netstat -an | findstr ":23"
```

**취약 출력 예시:**
```text
TCP    0.0.0.0:23            0.0.0.0:0              LISTENING
```

```powershell
# Telnet 기능 설치 여부 확인
Get-WindowsFeature -Name Telnet-Server
```

### 3. 조치 방법

#### Windows 서버 설정

1. **Telnet 서비스 중지**
   ```powershell
   # Telnet 서비스 중지
   Stop-Service -Name "TlntSvr" -Force

   # 시작 유형 변경
   Set-Service -Name "TlntSvr" -StartupType Disabled
   ```

2. **Telnet 서비스 기능 제거 (Windows Server 2012 이상)**
   ```powershell
   # Telnet 서비스 제거
   Remove-WindowsFeature -Name Telnet-Server

   # Telnet 클라이언트도 함께 제거 (권장)
   Remove-WindowsFeature -Name Telnet-Client
   ```

3. **서비스 관리자에서 중지 (GUI)**
   ```
   1. 시작 > 실행 > services.msc
   2. "Telnet" 서비스 더블클릭
   3. 시작 유형: [사용 안 함] 선택
   4. 서비스 상태: [중지] 클릭
   5. [확인]
   ```

4. **서버 관리자에서 기능 제거 (GUI)**
   ```
   1. 서버 관리자 > 관리 > 역할 및 기능 제거
   2. 기능 목록에서 "Telnet Server" 체크 해제
   3. 제거 진행
   ```

5. **OpenSSH Server 설치 (대안)**
   ```powershell
   # OpenSSH Server 기능 추가 (Windows Server 2019 이상)
   Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0

   # sshd 서비스 시작 및 자동 시작 설정
   Start-Service sshd
   Set-Service -Name sshd -StartupType Automatic
   ```

6. **방화벽 규칙 차단**
   ```powershell
   # Telnet 방화벽 규칙 차단
   Disable-NetFirewallRule -DisplayName "*Telnet*"
   ```

### 4. 참고 자료

- [Microsoft Docs: Telnet Operations](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/telnet)
- [CIS Benchmark: 18.5.19.1 Ensure 'Telnet Client' is set to 'Disabled' or 'Not Installed'](https://www.cisecurity.org/)
- [RFC 854: Telnet Protocol Specification](https://tools.ietf.org/html/rfc854)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.