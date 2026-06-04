---
title: "[2026 주요정보통신기반시설] W-14 원격 터미널 접속 가능한 사용자 그룹 제한"
slug: "2026-주정통/W-14"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "원격터미널사용자그룹내비인가자포함여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Windows
---

# W-14 원격 터미널 접속 가능한 사용자 그룹 제한

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | W-14 |
| **점검내용** | 원격터미널사용자그룹내비인가자포함여부점검 |
| **점검대상** | Windows 2003, 2008, 2012, 2016, 2019, 2022 |
| **양호기준** | (관리자계정을제외한)원격접속이가능한계정을생성하여타사용자의원격접속을제한하고, 원격접속사용자그룹에불필요한계정이등록되어있지않은경우 |
| **취약기준** | (관리자계정을제외한)원격접속이가능한별도의계정이존재하지않는경우 |
| **조치방법** | 관리자계정과이외의계정을생성,권한을제한사용설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 관리자 계정을 제외한 별도의 RDP 전용 계정을 생성하고, 불필요한 계정이 Remote Desktop Users 그룹에 없는 경우
- **취약**: 관리자 계정만으로 원격 접속이 가능하거나, 불필요한 계정이 원격 접속 가능한 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| 관리자 계정 직접 사용 | 주의 | 관리자 계정 대신 별도 RDP 계정 사용 권장 |
| 서버 관리 도구 | 주의 | 일부 관리 도구는 RDP 필요. 최소 권한 계정 권장 |
| 도메인 컨트롤러 | 주의 | Domain Admins가 기본으로 RDP 접속 가능 |
| Remote Desktop Users 그룹 | 양호 | 이 그룹에 속한 사용자만 RDP 접속 가능 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| 모든 서버 | Remote Desktop Users | 최소 인원 | 별도 RDP 전용 계정만 포함 |
| 보안 강화 서버 | RDP 포트 변경 | 3389 외 포트 | 포트 스캔 방지 |
| 모든 서버 | NLA(네트워크 수준 인증) | 사용 | 인증 전 연결 제한 |

### 2. 점검 방법

#### Windows 서버 점검

원격 데스크톱 서비스(RDP)를 통해 접속할 수 있는 사용자를 제한하여, 비인가자의 원격 접속을 방지해야 합니다.

```bash
# PowerShell - Remote Desktop Users 그룹 구성원 확인
Get-LocalGroupMember -Name "Remote Desktop Users"

# 또는
net localgroup "Remote Desktop Users"
```

**양호 출력 예시:**
```text
Name              Value
----              -----
RDP_User1         S-1-5-21-...-1001
RDP_User2         S-1-5-21-...-1002
```
별도 RDP 전용 계정만 포함된 경우 양호

**취약 출력 예시:**
```text
Name              Value
----              -----
Administrator     S-1-5-21-...-500
User1             S-1-5-21-...-1001
User2             S-1-5-21-...-1002
Domain Users      S-1-5-21-...-513
```
불필요한 계정이 포함된 경우 취약

### 3. 조치 방법

#### Windows 서버 설정

1. **RDP 전용 계정 생성**
   ```powershell
   # RDP 전용 계정 생성
   $Password = ConvertTo-SecureString "ComplexPassword123!" -AsPlainText -Force
   New-LocalUser -Name "RDP_User" -Password $Password -Description "RDP 전용 계정"

   # Remote Desktop Users 그룹에 추가
   Add-LocalGroupMember -Group "Remote Desktop Users" -Member "RDP_User"
   ```

2. **불필요한 계정 제거**
   ```powershell
   # Remote Desktop Users 그룹에서 불필요한 계정 제거
   Remove-LocalGroupMember -Group "Remote Desktop Users" -Member "불필요한사용자"
   ```

3. **원격 설정 (GUI)**
   ```
   시작 > 제어판 > 시스템 > 원격 설정
   '원격' 탭 > '이 컴퓨터에 대한 원격 연결 허용'
   '사용자 선택'에서 허용할 사용자 지정
   ```

4. **네트워크 수준 인증(NLA) 활성화**
   ```
   시작 > 실행 > systempropertiesremote
   '네트워크 수준 인증을 사용하여 원격 연결' 체크
   ```

5. **RDP 포트 변경 (선택 사항)**
   ```powershell
   # 레지스트리로 포트 변경 (기본 3389)
   Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" -Name "PortNumber" -Value 33389 -Type DWord
   ```

### 4. 참고 자료

- [Microsoft Docs: 원격 데스크톱 보안](https://docs.microsoft.com/ko-kr/windows-server/remote/remote-desktop-services/clients/remote-desktop-allow-access)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.