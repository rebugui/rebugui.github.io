---
title: "[2026 주요정보통신기반시설] W-31 SNMP 서비스 Trap 수신 지정"
slug: "2026-주정통/W-31"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "SNMP 패킷 Access Control(접근제어) 설정 여부 점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Windows
---

# W-31 SNMP 서비스 Trap 수신 지정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | W-31 |
| **점검내용** | SNMP 패킷 Access Control(접근제어) 설정 여부 점검 |
| **점검대상** | Windows 2000, 2003, 2008, 2012, 2016, 2019, 2022 |
| **양호기준** | SNMP 서비스를 사용하지 않거나 특정 호스트로부터 SNMP 패킷 받아들이기가 설정된 경우 |
| **취약기준** | 모든 호스트로부터 SNMP 패킷 받아들이기가 설정된 경우 |
| **조치방법** | 불필요시 서비스 중지/사용 안 함, 사용시 SNMP 패킷 수령 호스트 지정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: SNMP Trap 수신처가 NMS(네트워크 관리 시스템) 서버 등 지정된 곳으로만 설정된 경우
- **취약**: Trap 수신처가 미지정이거나, 불명확한 호스트가 등록된 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| Trap 수신처 미지정 | 주의 | 알림 수신 불가 |
| NMS 서버 IP 등록됨 | 양호 | 정상 구성 |
| 여러 Trap 수신처 등록 | 양호 | 다중 NMS 환경 |
| 잘못된 IP 등록됨 | 취약 | 즉시 수정 필요 |
| 커뮤니티 불일치 | 주의 | NMS와 동일하게 설정 |
| Trap 미사용 (폴링만) | 양호 | 모니터링 방식에 따라 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| Trap 커뮤니티 | 커뮤니티 이름 | 읽기 전용 커뮤니티와 동일 | NMS와 일치 |
| Trap 대상 | 수신처 IP | NMS 서버 IP | 192.168.1.100 등 |
| Trap 설정 | Trap 버전 | SNMP v2c 또는 v3 | v3 권장 |
| Trap 전송 | 포트 | UDP 162 | 기본 포트 |

### 2. 점검 방법

#### Windows SNMP 서비스 점검

SNMP Trap 메시지가 지정된 관리 서버로만 전송되도록 설정되어 있는지 확인합니다.

```powershell
# SNMP Trap 설정 확인
Get-ChildItem "HKLM:\SYSTEM\CurrentControlSet\Services\SNMP\Parameters\TrapConfiguration" -ErrorAction SilentlyContinue
```

**양호 출력 예시:**
```text
    Hive: HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\SNMP\Parameters\TrapConfiguration
Name                           Property
----                           --------
public_community               1 : 192.168.1.100
                               2 : 192.168.1.101
```

**취약 출력 예시:**
```text
(속성 없음 - Trap 수신처 미지정)
```

```cmd
# SNMP 서비스 속성 확인 (GUI)
services.msc
# SNMP Service > 속성 > [트랩] 탭 > "트랩 대상" 확인
```

### 3. 조치 방법

#### Windows 서버 설정

1. **SNMP Trap 수신처 설정 (레지스트리)**
   ```powershell
   # 트랩 설정 경로 생성
   $TrapPath = "HKLM:\SYSTEM\CurrentControlSet\Services\SNMP\Parameters\TrapConfiguration\public"
   if (!(Test-Path $TrapPath)) { New-Item -Path $TrapPath -Force }

   # 트랩 대상 IP 추가
   New-ItemProperty -Path $TrapPath -Name "1" -Value "192.168.1.100" -PropertyType String -Force
   New-ItemProperty -Path $TrapPath -Name "2" -Value "192.168.1.101" -PropertyType String -Force
   ```

2. **SNMP 서비스 속성 설정 (GUI)**
   ```
   1. 시작 > 실행 > services.msc
   2. SNMP Service 속성 > [트랩] 탭
   3. 커뮤니티 이름 입력 후 [목록에 추가]
   4. "트랩 대상" 섹션에서 [추가] 클릭
   5. NMS 서버의 호스트 이름 또는 IP 주소 입력
   6. [확인]
   ```

3. **서비스 재시작**
   ```powershell
   # SNMP 서비스 재시작
   Restart-Service -Name "SNMP"
   ```

### 4. 참고 자료

- [Microsoft Docs: SNMP 트랩 구성](https://docs.microsoft.com/ko-kr/windows/win32/snmp/snmp-configuration)
- [CIS Benchmark: SNMP Trap Configuration](https://www.cisecurity.org/)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.