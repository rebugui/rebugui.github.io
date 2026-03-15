---
title: "[2026 주요정보통신기반시설] W-20 NetBIOS 바인딩 서비스 구동 점검"
slug: "2026-주정통/W-20"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "NetBIOS바인딩서비스구동여부점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Windows
---

# W-20 NetBIOS 바인딩 서비스 구동 점검

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | W-20 |
| **점검내용** | NetBIOS바인딩서비스구동여부점검 |
| **점검대상** | Windows NT, 2000, 2003, 2008, 2012, 2016, 2019, 2022 |
| **양호기준** | TCP/IP와NetBIOS간의바인딩이제거되어있는경우 |
| **취약기준** | TCP/IP와NetBIOS간의바인딩이제거되어있지않은경우 |
| **조치방법** | 네트워크제어판을이용하여TCP/IP와NetBIOS 간의바인딩(binding)제거 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: TCP/IP와 NetBIOS 간의 바인딩이 제거되어 있는 경우 (NetBIOS over TCP/IP 사용 안 함)
- **취약**: TCP/IP와 NetBIOS 간의 바인딩이 제거되어 있지 않은 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| 파일 공유(컴퓨터 이름) | 주의 | IP 주소를 이용한 공유는 가능하지만 컴퓨터 이름으로 접근 제한 |
| 레거시 애플리케이션 | 주의 | NetBIOS 이름을 필수적으로 사용하는 구형 앱 작동 중지 가능 |
| DNS 미구성 | 주의 | NetBIOS 비활성화 시 DNS 설정이 정확해야 함 |
| 레지스트리 값 0 | 취약 | DHCP 서버 설정 따름 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| 모든 Windows 서버 | NetBIOS over TCP/IP | 사용 안 함 | 인터넷 연결 서버 필수 |
| 모든 Windows 서버 | NetbiosOptions | 2 | 레지스트리 값 |
| 사설 네트워크 | NetBIOS | 사용 허용 | 내부 네트워크만 |

### 2. 점검 방법

#### Windows 서버 점검

NetBIOS over TCP/IP 기능을 비활성화하여 시스템 정보 노출을 차단하고 네트워크 보안을 강화해야 합니다.

```bash
# PowerShell - 레지스트리 확인
Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Services\NetBT\Parameters\Interfaces\*"

# 또는 ipconfig로 확인
ipconfig /all
```

**양호 출력 예시:**
```text
NetbiosOptions : 2
또는
NetBIOS over Tcpip . . . . . . . . : Disabled
```
값이 2이면 '사용 안 함'으로 양호

**취약 출력 예시:**
```text
NetbiosOptions : 0
또는
NetbiosOptions : 1
또는
NetBIOS over Tcpip . . . . . . . . : Enabled
```
값이 0 또는 1이면 취약

### 3. 조치 방법

#### Windows 서버 설정

1. **네트워크 어댑터 속성 변경 (GUI - 권장)**
   ```
   시작 > 실행 > ncpa.cpl
   사용하는 네트워크 어댑터 우클릭 > 속성
   Internet Protocol Version 4 (TCP/IPv4) 선택 > 속성
   [고급] 버튼 클릭
   [WINS] 탭 선택
   "NetBIOS 설정"에서 "NetBIOS over TCP/IP 사용 안 함" 선택
   확인 > 확인 > 닫기
   ```

2. **레지스트리 수정 (PowerShell)**
   ```powershell
   # 모든 네트워크 인터페이스에 대해 NetBIOS 비활성화 (값 2)
   $interfaces = Get-ChildItem "HKLM:\SYSTEM\CurrentControlSet\Services\NetBT\Parameters\Interfaces"
   foreach ($interface in $interfaces) {
       Set-ItemProperty -Path $interface.PSPath -Name "NetbiosOptions" -Value 2
   }
   ```

3. **명령 프롬프트로 확인**
   ```cmd
   # 설정 확인
   ipconfig /all | findstr /i "NetBIOS"
   ```

4. **DHCP 서버를 이용한 일괄 적용 (선택 사항)**
   ```
   DHCP 서버 옵션 중 '001 Microsoft Disable Netbios Option' 값을 '0x2'로 설정
   클라이언트가 IP를 할당받을 때 자동으로 비활성화
   ```

### 4. 참고 자료

- [Microsoft Docs: NetBIOS over TCP/IP 비활성화](https://docs.microsoft.com/ko-kr/troubleshoot/windows-server/networking/disable-netbios-tcp-ip)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.