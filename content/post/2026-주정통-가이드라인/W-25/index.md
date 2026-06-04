---
title: "[2026 주요정보통신기반시설] W-25 DNS Zone Transfer 설정"
slug: "2026-주정통/W-25"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "DNS Zone Transfer 차단 설정 여부 점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Windows
---

# W-25 DNS Zone Transfer 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | W-25 |
| **점검내용** | DNS Zone Transfer 차단 설정 여부 점검 |
| **점검대상** | Windows NT, 2000, 2003, 2008, 2012, 2016, 2019, 2022 |
| **양호기준** | 1) DNS 서비스가 비활성화인 경우 2) 영역 전송 허용을 하지 않는 경우 3) 특정 서버로만 설정되어 있는 경우 |
| **취약기준** | 위 3개 기준 중 하나라도 해당하지 않는 경우 |
| **조치방법** | 불필요시 서비스 중지/사용 안 함 설정, 사용하는 경우 영역 전송을 특정 서버로 제한하거나 '영역 전송 허용' 체크 해제 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: DNS Zone Transfer가 비활성화되거나, 신뢰하는 Secondary DNS 서버로만 제한된 경우
- **취약**: 모든 IP 주소에서 Zone Transfer가 가능한 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| DNS 서비스 설치되지 않음 | 양호 | Zone Transfer 위험 없음 |
| 영역 전송 "모든 서버"로 설정 | 취약 | 누구나 Zone 정보 획득 가능 |
| 영역 전송 "다음 서버로만" 설정 | 양호 | 지정된 Secondary DNS만 전송 |
| 영역 전송 "다음 서버로만"이나 IP 없음 | 취약 | 실제 전송 대상이 없는 상태 |
| Active Directory 통합 영역 | 양호 | AD 복제 메커니즘 사용 |
| NSLOOKUP으로 Zone Transfer 거부됨 | 양호 | "Query refused" 응답 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| DNS 영역 속성 | 영역 전송 | 허용 안 함 또는 다음 서버로만 | 보안 설정 |
| 영역 전송 허용 대상 | Secondary DNS IP | 192.168.1.10 등 | 신뢰하는 DNS만 |
| 방화벽 | TCP 53 포트 | 허용 IP로 제한 | Zone Transfer용 포트 |
| 영역 전송 | 알림 설정 | Secondary DNS만 | 보안 강화 |

### 2. 점검 방법

#### Windows DNS 서버 점검

DNS Zone Transfer가 제한되지 않으면, 공격자가 도메인 내 모든 호스트 정보를 획득하여 네트워크 구조를 파악할 수 있습니다.

```powershell
# DNS 영역 전송 설정 확인
Get-DnsServerPrimaryZone -Name "example.com" | Select-Object SecureSecondaries, Secondaries
```

**양호 출력 예시:**
```text
SecureSecondaries : TransferToSecureServers
Secondaries       : {192.168.1.10}
또는
SecureSecondaries : NoTransfer
```

**취약 출력 예시:**
```text
SecureSecondaries : TransferToAnyServer
```

```cmd
# nslookup으로 Zone Transfer 테스트
nslookup
server [DNS서버IP]
ls -d [도메인명]
```

**양호 출력 예시:**
```text
*** Unimplemented command.
또는
*** Query refused
```

**취약 출력 예시:**
```text
[도메인 전체 레코드 목록이 출력됨]
```

```powershell
# DNS 서비스 설치 여부 확인
Get-WindowsFeature -Name DNS
```

### 3. 조치 방법

#### Windows DNS 서버 설정

1. **DNS 영역 전송 비활성화**
   ```powershell
   # 영역 전송 완전 차단
   Set-DnsServerPrimaryZone -Name "example.com" -SecureSecondaries NoTransfer

   # 또는
   $zone = Get-DnsServerPrimaryZone -Name "example.com"
   $zone.SecureSecondaries = "NoTransfer"
   Set-DnsServerPrimaryZone -InputObject $zone
   ```

2. **특정 서버로만 영역 전송 제한**
   ```powershell
   # Secondary DNS 서버 IP로만 전송 제한
   Set-DnsServerPrimaryZone -Name "example.com" -SecureSecondaries TransferToSecureServers -SecondaryServers "192.168.1.10"

   # 여러 Secondary DNS 지정
   Set-DnsServerPrimaryZone -Name "example.com" -SecureSecondaries TransferToSecureServers -SecondaryServers @("192.168.1.10","192.168.1.11")
   ```

3. **DNS 관리자에서 설정 (GUI)**
   ```
   1. 시작 > 관리 도구 > DNS 실행
   2. 정방향 조회 영역 > 해당 도메인 우클릭 > 속성
   3. [영역 전송] 탭 선택
   4. Case A (보조 DNS 없음):
      - "영역 전송 허용" 체크 해제
   5. Case B (보조 DNS 있음):
      - "영역 전송 허용" 체크
      - "다음 서버로만" 선택
      - [편집] 클릭 후 Secondary DNS IP 주소 입력
   6. [확인]
   ```

4. **서비스 중지 (DNS 사용하지 않는 경우)**
   ```powershell
   # DNS 서비스 중지
   Stop-Service -Name DNS -Force

   # 시작 유형 변경
   Set-Service -Name DNS -StartupType Disabled
   ```

5. **방화벽에서 TCP 53 포트 제한**
   ```cmd
   # DNS Zone Transfer 포트(TCP 53) 제한
   netsh advfirewall firewall add rule name="DNS Zone Transfer" dir=in action=allow protocol=TCP localport=53 remoteip=192.168.1.10
   ```

### 4. 참고 자료

- [Microsoft Docs: DNS 영역 전송 관리](https://docs.microsoft.com/ko-kr/windows-server/networking/dns/manage/manage-zone-transfer)
- [IETF RFC 1035: Domain Names - Implementation and Specification](https://tools.ietf.org/html/rfc1035)
- [CIS Benchmark: Ensure 'DNS Server' is configured securely](https://www.cisecurity.org/)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.