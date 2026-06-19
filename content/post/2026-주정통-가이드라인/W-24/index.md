---
title: "[2026 주요정보통신기반시설] W-24 FTP 접근 제어 설정"
slug: "2026-주정통/W-24"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "FTP 접속 가능한 IP 주소 지정 여부 점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Windows
draft: true
---

# W-24 FTP 접근 제어 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | W-24 |
| **점검내용** | FTP 접속 가능한 IP 주소 지정 여부 점검 |
| **점검대상** | Windows NT, 2000, 2003, 2008, 2012, 2016, 2019, 2022 |
| **양호기준** | 특정 IP 주소에서만 FTP 서버에 접속하도록 접근 제어 설정을 적용한 경우 |
| **취약기준** | 특정 IP 주소에서만 FTP 서버에 접속하도록 접근 제어 설정을 적용하지 않는 경우 |
| **조치방법** | 특정 IP 주소에서만 FTP 서버에 접속하도록 접근 제어 설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: FTP 서비스에 IP 주소 기반 접근 제어(IP Restriction)가 설정되어 특정 IP만 접속 가능한 경우
- **취약**: 모든 IP 주소(0.0.0.0/0)에서 FTP 접속이 가능한 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| 허용 IP가 127.0.0.1만 있는 경우 | 주의 | 로컬 접속만 가능하나 실제 운영 환경 고려 필요 |
| 특정 IP 대역(예: 192.168.1.0/24) 허용 | 양호 | 내부망 대역 제한 |
| 방화벽에서만 IP 제한됨 | 양호 | 네트워크 레벨에서 접근 제어 |
| 거부 목록(Blocklist)만 구성 | 취약 | 명시적 허용(Allowlist) 정책 권장 |
| VPN 서버 IP만 허용 | 양호 | VPN 경유 접속만 허용 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| IIS FTP | IP 제한 기본 정책 | 거부(Deny All) | 명시적 허용만 접속 가능 |
| IIS FTP | 허용 IP | 관리자 PC, 관련 서버 IP | 화이트리스트 방식 |
| 방화벽 | 인바운드 규칙 | 특정 IP로 제한 | Windows 방화벽 또는 외부 방화벽 |
| FTP 포트 | 21/TCP | 허용 IP로 제한 | 필요시 PASV 포트도 제한 |

### 2. 점검 방법

#### Windows 서버 점검

FTP 포트는 무차별 대입 공격의 주요 표적이 되므로, 반드시 IP 기반 접근 제어가 설정되어 있어야 합니다.

```powershell
# IIS FTP IP 제한 설정 확인
Import-Module WebAdministration
Get-WebConfiguration -Filter "/system.ftpServer/security/ipSecurity" -PSPath "IIS:\"
```

**양호 출력 예시:**
```text
allowUnlisted : False
```

**취약 출력 예시:**
```text
allowUnlisted : True
```

```cmd
# Windows 방화벽 FTP 규칙 확인
netsh advfirewall firewall show rule name="FTP Server"
```

```powershell
# 방화벽 규칙의 원격 IP 확인
Get-NetFirewallRule -Displayname "*FTP*" | Get-NetFirewallAddressFilter | Select-Object -Property RemoteAddress
```

```cmd
# FTP 포트 리스닝 및 바인딩 확인
netstat -an | findstr ":21"
```

### 3. 조치 방법

#### Windows 서버 설정

1. **IIS FTP IP 제한 설정**
   ```powershell
   # IP 제한 기본 정책을 '거부'로 설정
   Set-WebConfigurationProperty -Filter "/system.ftpServer/security/ipSecurity" -PSPath "IIS:\" -Name "allowUnlisted" -Value $false

   # 허용할 IP 추가 (단일 IP)
   Add-WebConfiguration -Filter "/system.ftpServer/security/ipSecurity" -PSPath "IIS:\" -Value @{ipAddress="192.168.1.100";allowed="true"}

   # 허용할 IP 대역 추가
   Add-WebConfiguration -Filter "/system.ftpServer/security/ipSecurity" -PSPath "IIS:\" -Value @{ipAddress="192.168.1.0";subnetMask="255.255.255.0";allowed="true"}
   ```

2. **Windows 방화벽 IP 제한**
   ```cmd
   # FTP 인바운드 규칙의 원격 IP 제한
   netsh advfirewall firewall set rule name="FTP Server" new remoteip="192.168.1.100,192.168.1.200"

   # 또는 특정 IP 대역 허용
   netsh advfirewall firewall set rule name="FTP Server" new remoteip="192.168.1.0/24"
   ```

3. **IIS 관리자에서 설정 (GUI)**
   ```
   1. IIS 관리자 실행 > FTP 사이트 선택
   2. "FTP IPv4 주소 및 도메인 제한" 더블클릭
   3. 우측 작업 창에서 "기능 설정 편집" 클릭
   4. "지정되지 않은 클라이언트에 대한 액세스": [거부] 선택 > 확인
   5. 우측 "허용 항목 추가" 클릭
   6. 접속을 허용할 IP 주소 또는 범위 입력
   7. [확인]
   ```

4. **Windows 방화벽 GUI 설정**
   ```
   1. 고급 보안이 포함된 Windows Defender 방화벽 실행
   2. 인바운드 규칙 > FTP Server 관련 규칙 더블클릭
   3. [영역] 탭 선택
   4. 원격 IP 주소: "다음 IP 주소" 선택
   5. [추가] 버튼으로 허용할 IP 입력
   6. [확인]
   ```

### 4. 참고 자료

- [Microsoft Docs: IIS FTP IP 보안](https://docs.microsoft.com/ko-kr/iis/configuration/system.applicationhost/sites/site/ftpserver/security/ipsecurity/)
- [Microsoft Docs: 방화벽 규칙 설정](https://docs.microsoft.com/ko-kr/windows/security/threat-protection/windows-firewall/create-an-inbound-port-rule)
- [CIS Benchmark: 9.2.1 Ensure 'Windows Firewall' is enabled](https://www.cisecurity.org/)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.