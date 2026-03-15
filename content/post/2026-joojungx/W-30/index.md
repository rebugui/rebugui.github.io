---
title: "[2026 주요정보통신기반시설] W-30 SNMP 서비스 Trap 및 GET Operation 설정"
slug: "2026-주정통/W-30"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "SNMP 서비스 Community String 적절성 점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Windows
---

# W-30 SNMP 서비스 Trap 및 GET Operation 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | W-30 |
| **점검내용** | SNMP 서비스 Community String 적절성 점검 |
| **점검대상** | Windows 2000, 2003, 2008, 2012, 2016, 2019, 2022 |
| **양호기준** | SNMP 서비스를 사용하지 않거나 Community String이 public, private이 아닌 경우 |
| **취약기준** | SNMP 서비스를 사용하며, Community String이 public, private인 경우 |
| **조치방법** | 불필요시 서비스 중지/사용 안 함, 사용시 기본 Community String 변경 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: SNMP 패킷 수신을 특정 호스트(IP)로 제한한 경우
- **취약**: 모든 호스트로부터의 SNMP 패킷을 받아들이도록 설정된 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| "모든 호스트"로부터 수신 허용 | 취약 | 즉시 제한 필요 |
| "다음 호스트"로부터 수신 설정 | 양호 | IP 제한됨 |
| PermittedManagers에 IP 등록됨 | 양호 | 화이트리스트 구성 |
| 로컬호스트(127.0.0.1)만 등록 | 주의 | 관리 시스템에 따라 추가 필요 |
| SNMP Trap 수신처 미지정 | 주의 | 알림 수신 불가 |
| NMS 서버 IP 등록됨 | 양호 | 정상 구성 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| SNMP 보안 | 패킷 수신 소스 | 다음 호스트로부터 | IP 제한 |
| PermittedManagers | 관리 서버 IP | NMS 서버 IP | 화이트리스트 |
| SNMP Trap | 수신처 | 지정된 Trap 대상 | 관리 서버 |
| 로컬호스트 | 127.0.0.1 | 등록 권장 | 자체 모니터링 |

### 2. 점검 방법

#### Windows SNMP 서비스 점검

SNMP 서비스의 접근 제어 설정을 확인하여, 인가되지 않은 호스트에서의 시스템 정보 조회를 차단해야 합니다.

```powershell
# SNMP 허용 관리자 목록 확인
Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Services\SNMP\Parameters\PermittedManagers" -ErrorAction SilentlyContinue
```

**양호 출력 예시:**
```text
1 : 192.168.1.100
2 : 127.0.0.1
```

**취약 출력 예시:**
```text
(속성 없음 - 모든 호스트 허용)
또는
값 없음
```

```cmd
# SNMP 서비스 속성 확인 (GUI)
services.msc
# SNMP Service > 속성 > [보안] 탭 > "다음 호스트로부터의 SNMP 패킷 받아들이기" 선택 여부 확인
```

### 3. 조치 방법

#### Windows 서버 설정

1. **SNMP 패킷 수신 호스트 제한 (레지스트리)**
   ```powershell
   # 허용된 관리자 목록에 NMS 서버 IP 추가
   New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\SNMP\Parameters\PermittedManagers" -Name "1" -Value "192.168.1.100" -PropertyType String -Force

   # 로컬호스트 추가 (자체 모니터링용)
   New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\SNMP\Parameters\PermittedManagers" -Name "2" -Value "127.0.0.1" -PropertyType String -Force
   ```

2. **SNMP 서비스 속성 설정 (GUI)**
   ```
   1. 시작 > 실행 > services.msc
   2. SNMP Service 속성 > [보안] 탭
   3. "모든 호스트로부터의 SNMP 패킷 받아들이기" 체크 해제
   4. "다음 호스트로부터의 SNMP 패킷 받아들이기" 선택
   5. [추가] 클릭
   6. 허용할 호스트의 IP 주소 또는 이름 입력 (예: 192.168.1.100)
   7. [확인]
   ```

3. **서비스 재시작**
   ```powershell
   # SNMP 서비스 재시작
   Restart-Service -Name "SNMP"
   ```

### 4. 참고 자료

- [Microsoft Docs: SNMP 구성](https://docs.microsoft.com/ko-kr/windows/win32/snmp/snmp-configuration)
- [CIS Benchmark: 18.5.16.2 Ensure 'SNMP Permit Managers' is set to 'Specific Managers' and Not 'Public'](https://www.cisecurity.org/)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.