---
title: "[2026 주요정보통신기반시설] W-29 SNMP 서비스 커뮤니티 스트링 설정"
slug: "2026-주정통/W-29"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "SNMP 서비스 구동 여부 점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Windows
---

# W-29 SNMP 서비스 커뮤니티 스트링 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | W-29 |
| **점검내용** | SNMP 서비스 구동 여부 점검 |
| **점검대상** | Windows 2000, 2003, 2008, 2012, 2016, 2019, 2022 |
| **양호기준** | 커뮤니티 스트링을 기본값(public, private)이 아닌 복잡한 값으로 설정한 경우 |
| **취약기준** | 커뮤니티 스트링을 기본값(public, private)으로 설정한 경우 |
| **조치방법** | 불필요시 서비스 중지/사용 안 함, 사용시 기본 Community String 변경 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: SNMP 커뮤니티 스트링이 기본값(public, private, admin 등)이 아닌 복잡한 값으로 설정된 경우
- **취약**: 기본 커뮤니티 스트링(public, private)이 사용 중인 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| SNMP 서비스 설치되지 않음 | 양호 | 서비스 미사용 |
| 커뮤니티 스트링 "public" 사용 | 취약 | 기본값으로 즉시 변경 필요 |
| 커뮤니티 스트링 "private" 사용 | 취약 | 기본값으로 즉시 변경 필요 |
| 복잡한 문자열 사용 (영+숫+특) | 양호 | 보안 강화 |
| 쓰기 권한 커뮤니티 존재 | 주의 | 읽기 전용 권장 |
| SNMP v3 사용 | 양호 | 인증/암호화 지원 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| 커뮤니티 스트링 | 읽기 전용 | 영문+숫자+특수문자 조합 12자 이상 | 예: SnMP_R0!d2024 |
| 커뮤니티 스트링 | 쓰기 권한 | 권장하지 않음 | 필수시 더 복잡하게 |
| SNMP 버전 | 프로토콜 버전 | SNMP v3 | 인증/암호화 지원 |
| 서비스 상태 | SNMP Service | 필요 시만 실행 | 불필요시 중지 |

### 2. 점검 방법

#### Windows SNMP 서비스 점검

SNMP 커뮤니티 스트링은 SNMP 통신의 비밀번호와 같습니다. 기본값이 사용되면 시스템 정보가 무단으로 노출될 수 있습니다.

```powershell
# SNMP 커뮤니티 스트링 레지스트리 확인
Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Services\SNMP\Parameters\ValidCommunities" -ErrorAction SilentlyContinue
```

**양호 출력 예시:**
```text
SecureString123! : 4
또는
(속성 없음 - SNMP 미사용)
```

**취약 출력 예시:**
```text
public  : 4
private : 8
```

```cmd
# SNMP 서비스 상태 확인
sc query SNMP
```

```powershell
# SNMP 서비스 설치 여부 확인
Get-Service -Name "SNMP" -ErrorAction SilentlyContinue
```

```cmd
# SNMP 포트 확인
netstat -an | findstr ":161"
```

### 3. 조치 방법

#### Windows 서버 설정

1. **커뮤니티 스트링 변경 (레지스트리)**
   ```powershell
   # 기존 public 커뮤니티 제거
   Remove-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\SNMP\Parameters\ValidCommunities" -Name "public" -ErrorAction SilentlyContinue
   Remove-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\SNMP\Parameters\ValidCommunities" -Name "private" -ErrorAction SilentlyContinue

   # 새로운 복잡한 커뮤니티 스트링 추가 (읽기 전용: 4)
   Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\SNMP\Parameters\ValidCommunities" -Name "SecureSnMP2024!" -Value 4 -Type DWord
   ```

2. **SNMP 서비스 속성 설정 (GUI)**
   ```
   1. 시작 > 실행 > services.msc
   2. SNMP Service 속성 > [보안] 탭
   3. 기존의 'public', 'private' 등 선택 > [제거]
   4. [추가] 클릭
      - 커뮤니티 권한: 읽기 전용
      - 커뮤니티 이름: 복잡한 문자열 입력 (예: SnMP_R0!d2024)
   5. [확인]
   ```

3. **SNMP 서비스 미사용 시 비활성화**
   ```powershell
   # SNMP 서비스 중지
   Stop-Service -Name "SNMP" -Force

   # 시작 유형 변경
   Set-Service -Name "SNMP" -StartupType Disabled

   # 방화벽 규칙 차단
   Disable-NetFirewallRule -DisplayGroup "SNMP Server"
   ```

4. **서비스 재시작**
   ```powershell
   # SNMP 서비스 재시작 (설정 적용)
   Restart-Service -Name "SNMP"
   ```

### 4. 참고 자료

- [Microsoft Docs: SNMP 보안 구성](https://docs.microsoft.com/ko-kr/windows/win32/snmp/snmp-security-configuration)
- [CIS Benchmark: 18.5.16.1 Ensure 'SNMP Communities' is set to 'Complex' and Not Public](https://www.cisecurity.org/)
- [RFC 3414: User-based Security Model (USM) for version 3 of the SNMP](https://tools.ietf.org/html/rfc3414)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.