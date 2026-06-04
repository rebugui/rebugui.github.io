---
title: "[2026 주요정보통신기반시설] W-06 관리자 그룹에 최소한의 사용자 포함"
slug: "2026-주정통/W-06"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "관리자그룹에불필요한사용자의포함여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Windows
---

# W-06 관리자 그룹에 최소한의 사용자 포함

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | W-06 |
| **점검내용** | 관리자그룹에불필요한사용자의포함여부점검 |
| **점검대상** | Windows NT, 2000, 2003, 2008, 2012, 2016, 2019, 2022 |
| **양호기준** | Administrators그룹에불필요한관리자계정이존재하지않는경우 |
| **취약기준** | Administrators그룹에불필요한관리자계정이존재하는경우 |
| **조치방법** | Administrators그룹에포함된불필요한계정제거 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: Administrators 그룹의 구성원을 필수 인원으로만 제한하거나, 불필요한 관리자 계정이 존재하지 않는 경우
- **취약**: Administrators 그룹에 불필요한 관리자 계정이 존재하는 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| 도메인 관리자(Domain Admins) | 양호 | 도메인 컨트롤러의 Administrators 그룹에 Domain Admins가 포함된 것은 정상 |
| 서비스 계정 | 주의 | 서비스 실행을 위한 계정인지 확인 필요. 관리자 권한이 불필요하다면 제거 |
| 기본 제공 Administrator | 양호 | 기본 Administrator 계정은 유지 필요 (이름 변경 권장) |
| 예약된 작업 계정 | 주의 | 작업 스케줄러에 등록된 작업이 있는지 확인 필요 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| 독립 서버 | Administrators 구성원 수 | 1~2명 | 긴급 상황 대비 |
| 도메인 컨트롤러 | Domain Admins 구성원 수 | 2~3명 | 도메인 관리 |
| 엔터프라이즈 관리 | Enterprise Admins 구성원 수 | 1~2명 | 포리스트 관리 |

### 2. 점검 방법

#### Windows 서버 점검

관리자 그룹에 과도한 사용자가 포함되어 있는지 점검하여 권한 상승 취약점을 방지해야 합니다.

```bash
# PowerShell - 관리자 그룹 구성원 확인
Get-LocalGroupMember -Name "Administrators"

# 또는
net localgroup Administrators
```

**양호 출력 예시:**
```text
Name              Value
----              -----
Administrator     S-1-5-21-...-500
Domain Admins     S-1-5-21-...-512
```
필수 구성원만 포함된 경우 양호

**취약 출력 예시:**
```text
Name              Value
----              -----
Administrator     S-1-5-21-...-500
Domain Admins     S-1-5-21-...-512
User1             S-1-5-21-...-1001
User2             S-1-5-21-...-1002
User3             S-1-5-21-...-1003
```
불필요한 사용자가 다수 포함된 경우 취약

### 3. 조치 방법

#### Windows 서버 설정

1. **관리자 그룹 구성원 검토**
   ```powershell
   # 현재 관리자 그룹 구성원 확인
   Get-LocalGroupMember -Name "Administrators" | Format-Table -AutoSize
   ```

2. **불필요한 구성원 제거**
   ```powershell
   # 특정 사용자를 관리자 그룹에서 제거
   Remove-LocalGroupMember -Group "Administrators" -Member "불필요한사용자"

   # 제거 확인
   Get-LocalGroupMember -Name "Administrators"
   ```

3. **명령 프롬프트로 제거**
   ```cmd
   net localgroup Administrators "불필요한사용자" /delete
   ```

4. **GUI로 제거**
   ```
   시작 > 프로그램 > 관리 도구 > 컴퓨터 관리
   로컬 사용자 및 그룹 > 그룹
   Administrators 그룹 선택 > 속성
   제거할 구성원 선택 > 제거
   확인 클릭
   ```

5. **서비스 재시작**
   ```powershell
   # 제거된 계정이 실행하던 서비스가 있는지 확인
   Get-WmiObject Win32_Service | Where-Object {$_.StartName -like "제거된계정"}
   ```

### 4. 참고 자료

- [Microsoft Docs: 기본 그룹](https://docs.microsoft.com/ko-kr/windows-server/identity/ad-ds/manage/understand-groups)
- [NIST SP 800-53: AC-6 최소 권한](https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final)
- [CIS Benchmark: 관리자 그룹 구성원](https://www.cisecurity.org/benchmark/windows_server)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.