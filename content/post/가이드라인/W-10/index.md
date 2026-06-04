---
title: "[2026 주요정보통신기반시설] W-10 마지막 사용자 이름 표시 안 함"
slug: "2026-주정통/W-10"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "로그인화면에마지막로그온사용자이름을표시하지않도록설정되었는지를점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Windows
---

# W-10 마지막 사용자 이름 표시 안 함

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | W-10 |
| **점검내용** | 로그인화면에마지막로그온사용자이름을표시하지않도록설정되었는지를점검 |
| **점검대상** | Windows NT, 2000, 2003, 2008, 2012, 2016, 2019, 2022 |
| **양호기준** | '마지막사용자이름표시안함'이'사용'으로설정된경우 |
| **취약기준** | '마지막사용자이름표시안함'이'사용안함'으로설정된경우 |
| **조치방법** | 대화형로그온:마지막사용자이름표시안함'사용'설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: '대화형 로그온: 마지막 사용자 이름 표시 안 함' 정책이 '사용'으로 설정된 경우
- **취약**: '대화형 로그온: 마지막 사용자 이름 표시 안 함' 정책이 '사용 안 함'으로 설정된 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| 도메인 컨트롤러 | 주의 | GPO로 일괄 적용 권장 |
| 자동 로그온 사용 | 주의 | 자동 로그온에는 영향 없으나 보안상 비권장 |
| 레지스트리 값 없음 | 취약 | 기본값은 '사용 안 함'임 |
| RDP 환경 | 양호 | RDP 서비스에도 동일하게 적용됨 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| 모든 Windows 서버 | 마지막 사용자 이름 표시 안 함 | 사용 | 계정 정보 노출 방지 |

### 2. 점검 방법

#### Windows 서버 점검

로그인 화면에 마지막으로 로그온한 사용자 이름을 표시하지 않도록 설정하여, 공격자가 시스템의 사용자 정보를 쉽게 획득하는 것을 방지해야 합니다.

```bash
# PowerShell - 레지스트리 확인
Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -Name "dontdisplaylastusername"
```

**양호 출력 예시:**
```text
dontdisplaylastusername : 1
```
값이 1이면 '사용'으로 양호

**취약 출력 예시:**
```text
dontdisplaylastusername : 0
또는
값이 존재하지 않음
```
값이 0이거나 없으면 '사용 안 함'으로 취약

### 3. 조치 방법

#### Windows 서버 설정

1. **레지스트리 설정**
   ```powershell
   # 관리자 권한 PowerShell 실행
   Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -Name "dontdisplaylastusername" -Value 1 -Type DWord

   # 설정 확인
   Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -Name "dontdisplaylastusername"
   ```

2. **명령 프롬프트 설정**
   ```cmd
   reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v dontdisplaylastusername /t REG_DWORD /d 1 /f
   ```

3. **로컬 보안 정책 설정 (GUI)**
   ```
   시작 > 제어판 > 관리 도구 > 로컬 보안 정책
   로컬 정책 > 보안 옵션
   '대화형 로그온: 마지막 사용자 이름 표시 안 함' 더블클릭
   '사용' 선택
   ```

4. **그룹 정책(GPO) 설정 (도메인 환경)**
   ```
   GPO 편집기(gpedit.msc 또는 gpmc.msc)
   컴퓨터 구성 > 정책 > Windows 설정 > 보안 설정 > 로컬 정책 > 보안 옵션
   '대화형 로그온: 마지막 사용자 이름 표시 안 함' 설정
   '사용' 선택
   ```

### 4. 참고 자료

- [Microsoft Docs: 대화형 로그온 보안 옵션](https://docs.microsoft.com/ko-kr/windows/security/threat-protection/security-policy-settings/interactive-logon)
- [CIS Benchmark: 마지막 사용자 이름 표시 안 함](https://www.cisecurity.org/benchmark/windows_server)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.