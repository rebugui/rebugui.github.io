---
title: "[2026 주요정보통신기반시설] W-28 터미널 서비스 암호화 수준 설정"
slug: "2026-주정통/W-28"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "원격 데스크톱 서비스 암호화 수준 적절성 점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Windows
---

# W-28 터미널 서비스 암호화 수준 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | W-28 |
| **점검내용** | 원격 데스크톱 서비스 암호화 수준 적절성 점검 |
| **점검대상** | Windows NT, 2000, 2003, 2008, 2012, 2016, 2019, 2022 |
| **양호기준** | 원격 데스크톱 서비스를 사용하지 않거나, 사용 시 암호화 수준을 '클라이언트와 호환 가능(중간)' 이상으로 설정한 경우 |
| **취약기준** | 원격 데스크톱 서비스를 사용하고 암호화 수준이 '낮음'으로 설정된 경우 |
| **조치방법** | 원격 데스크톱 서비스의 가동을 '중지' 및 '사용 안 함' 설정을 하거나, 부득이하게 사용할 경우 암호화 수준 설정 적용 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: RDP 암호화 수준이 '클라이언트 호환 가능' 또는 '높음', 'FIPS 호환'으로 설정된 경우
- **취약**: RDP 암호화 수준이 '낮음'으로 설정된 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| RDP 서비스 비활성화 | 양호 | 암호화 필요 없음 |
| MinEncryptionLevel = 2 | 양호 | 클라이언트 호환 가능 (128비트) |
| MinEncryptionLevel = 3 | 양호 | 높음 수준 암호화 |
| MinEncryptionLevel = 4 | 양호 | FIPS 140-1 호환 |
| MinEncryptionLevel = 1 | 취약 | 낮음 수준 (56비트) |
| 구성되지 않음 | 주의 | 기본값 적용 확인 필요 |
| 레거시 클라이언트 연결 필요 | 주의 | 호환성 고려 필요 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| 레지스트리 | MinEncryptionLevel | 2 (클라이언트 호환 가능) | 128비트 암호화 |
| 레지스트리 | MinEncryptionLevel | 3 (높음) | 최대 256비트 |
| 레지스트리 | MinEncryptionLevel | 4 (FIPS 호환) | FIPS 140-1 준수 |
| 그룹 정책 | 암호화 수준 | 클라이언트 호환 가능 | 대부분 환경 적합 |
| 그룹 정책 | 암호화 수준 | 높음 | 최신 클라이언트만 |

### 2. 점검 방법

#### Windows RDP 서비스 점검

RDP 통신이 암호화되지 않거나 낮은 수준으로 암호화되면, 스니핑 공격을 통해 세션 데이터가 노출될 수 있습니다.

```powershell
# RDP 암호화 수준 레지스트리 확인
Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" -Name "MinEncryptionLevel"
```

**양호 출력 예시:**
```text
MinEncryptionLevel : 2
또는
MinEncryptionLevel : 3
또는
MinEncryptionLevel : 4
```

**취약 출력 예시:**
```text
MinEncryptionLevel : 1
```

```cmd
# 그룹 정책 확인 (GUI)
gpedit.msc
# 컴퓨터 구성 > 관리 템플릿 > Windows 구성 요소 > 원격 데스크톱 서비스 > 원격 데스크톱 세션 호스트 > 보안
# "클라이언트 연결 암호화 수준 설정" 확인
```

```powershell
# RDP 서비스 상태 확인
Get-Service -Name "TermService" | Select-Object Name, Status, StartType
```

### 3. 조치 방법

#### Windows 서버 설정

1. **레지스트리로 암호화 수준 설정**
   ```powershell
   # 클라이언트 호환 가능 (128비트) - 권장
   Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" -Name "MinEncryptionLevel" -Value 2 -Type DWord

   # 높음 수준
   Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" -Name "MinEncryptionLevel" -Value 3 -Type DWord

   # FIPS 호환
   Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" -Name "MinEncryptionLevel" -Value 4 -Type DWord
   ```

2. **그룹 정책으로 설정 (GUI)**
   ```
   1. 시작 > 실행 > gpedit.msc
   2. 컴퓨터 구성 > 관리 템플릿 > Windows 구성 요소 > 원격 데스크톱 서비스 > 원격 데스크톱 세션 호스트 > 보안
   3. "클라이언트 연결 암호화 수준 설정" 더블클릭
   4. [사용] 선택
   5. 암호화 수준: "클라이언트 호환 가능" 또는 "높음" 선택
   6. [확인]
   ```

3. **RDP 서비스 사용하지 않는 경우 비활성화**
   ```powershell
   # RDP 서비스 중지
   Stop-Service -Name "TermService" -Force

   # 시작 유형 변경 (사용 안 함)
   Set-Service -Name "TermService" -StartupType Disabled

   # 방화벽 RDP 규칙 차단
   Disable-NetFirewallRule -DisplayGroup "원격 데스크톱"
   ```

4. **서비스 재시작**
   ```powershell
   # RDP 서비스 재시작 (설정 적용을 위해)
   Restart-Service -Name "TermService"
   ```

### 4. 참고 자료

- [Microsoft Docs: RDP 암호화 수준 구성](https://docs.microsoft.com/ko-kr/troubleshoot/windows-server/remote/configure-server-encryption-level)
- [CIS Benchmark: 18.9.81.1.2 Ensure 'Set client connection encryption level' is set to 'Enabled' and 'High Level']](https://www.cisecurity.org/)
- [NIST SP 800-52: Guidelines on the Design and Implementation of Secure Applications Using TLS](https://csrc.nist.gov/publications/detail/sp/800-52/rev-2/final)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.