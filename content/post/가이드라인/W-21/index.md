---
title: "[2026 주요정보통신기반시설] W-21 암호화되지 않는 FTP 서비스 비활성화"
slug: "2026-주정통/W-21"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "시스템내 FTP 서비스 구동여부 점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Windows
---

# W-21 암호화되지 않는 FTP 서비스 비활성화

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | W-21 |
| **점검내용** | 시스템내 FTP 서비스 구동여부 점검 |
| **점검대상** | Windows NT, 2000, 2003, 2008, 2012, 2016, 2019, 2022 |
| **양호기준** | FTP 서비스를 사용하지 않거나 Secure FTP(SFTP/FTPS) 서비스를 사용하는 경우 |
| **취약기준** | 암호화되지 않는 FTP 서비스를 사용하는 경우 |
| **조치방법** | FTP 서비스가 필요하지 않으면 서비스 중지, 부득이하게 사용할 경우 SFTP/FTPS 응용프로그램 사용 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: FTP 서비스가 비활성화되어 있거나, 암호화된 FTP(SFTP/FTPS)를 사용하는 경우
- **취약**: 평문 FTP 서비스가 활성화되어 있어 계정 정보와 데이터가 노출될 위험이 있는 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| FTP 서비스 설치되어 있으나 중지된 상태 | 양호 | 서비스가 실행되고 있지 않으면 양호로 판단 |
| IIS FTP 기능만 설치되어 있으나 사이트 미구성 | 양호 | 실제 FTP 사이트가 시작되지 않았으면 양호 |
| SFTP만 사용(FTP 포트 21 닫힘) | 양호 | SSH 기반의 암호화된 파일 전송만 사용 |
| 내부망 전용 FTP 서버 | 주의 | 내부망이라도 스니핑 위험이 있으므로 SFTP 권장 |
| FTP over SSL(FTPS) 사용 | 양호 | 990 포트 등 암호화된 FTP 사용 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| 모든 서버 | FTP 서비스 상태 | 중지 또는 사용 안 함 | 파일 전송이 불필요한 경우 |
| 파일 전송 필요 시 | 대체 프로토콜 | SFTP(SSH) 또는 FTPS | 암호화 통신 필수 |
| 방화벽 | FTP 포트 | 21/TCP 차단 | 인바운드 방화벽에서 차단 권장 |

### 2. 점검 방법

#### Windows 서버 점검

FTP 서비스는 평문으로 인증 정보와 데이터를 전송하므로 스니핑 공격에 취약합니다. 반드시 사용 여부를 확인하고 불필요한 경우 중지해야 합니다.

```cmd
# FTP 서비스 상태 확인
sc query "MSFtpsvc"

# 또는
Get-Service | Where-Object {$_.Name -like "*FTP*"}
```

**양호 출력 예시:**
```text
SERVICE_NAME: MSFtpsvc
        STATE              : 1 STOPPED
또는
서비스를 찾을 수 없음
```

**취약 출력 예시:**
```text
SERVICE_NAME: MSFtpsvc
        STATE              : 4 RUNNING
```

```cmd
# FTP 포트(21) 리스닝 확인
netstat -an | findstr ":21 "
```

**취약 출력 예시:**
```text
TCP    0.0.0.0:21            0.0.0.0:0              LISTENING
```

```powershell
# IIS FTP 사이트 확인 (PowerShell)
Import-Module WebAdministration
Get-Website | Where-Object {$_.Name -like "*FTP*"}
```

### 3. 조치 방법

#### Windows 서버 설정

1. **FTP 서비스 중지**
   ```cmd
   # 서비스 중지
   net stop MSFtpsvc

   # 또는 PowerShell
   Stop-Service -Name "MSFtpsvc" -Force
   ```

2. **시작 유형 변경 (사용 안 함)**
   ```cmd
   # 시작 유형 변경
   sc config MSFtpsvc start= disabled

   # 또는 PowerShell
   Set-Service -Name "MSFtpsvc" -StartupType Disabled
   ```

3. **IIS 관리자에서 FTP 사이트 제거 (GUI)**
   ```
   1. 시작 > 관리 도구 > IIS(인터넷 정보 서비스) 관리자 실행
   2. 연결 > 서버 노드 확장 > [FTP 사이트] 선택
   3. 중지할 FTP 사이트 우클릭 > [중지]
   4. 제거가 필요한 경우 우클릭 > [제거]
   ```

4. **FTP 서비스 역할/기능 제거**
   ```powershell
   # Windows Server 2012 이상
   Remove-WindowsFeature Web-Ftp-Server

   # Windows Server 2008
   servermanagercmd -remove Web-Ftp-Server
   ```

5. **방화벽 규칙 삭제**
   ```cmd
   # FTP 인바운드 규칙 삭제
   netsh advfirewall firewall delete rule name="FTP Server"

   # FTP 서비스 삭제
   netsh advfirewall firewall delete rule name="FTP Server Traffic (TCP 21)"
   ```

### 4. 참고 자료

- [Microsoft Docs: FTP 서비스 구성](https://docs.microsoft.com/ko-kr/iis/configuration/system.applicationhost/sites/site/ftpserver)
- [KISA: 인터넷 보안 가이드라인](https://www.kisa.or.kr/)
- [NIST SP 800-53: SC-8 Transmission Confidentiality and Integrity](https://csrc.nist.gov/projects/security-configuration-checklist)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.