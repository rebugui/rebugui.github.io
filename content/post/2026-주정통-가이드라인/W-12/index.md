---
title: "[2026 주요정보통신기반시설] W-12 익명 SID/이름 변환 허용 해제"
slug: "2026-주정통/W-12"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "익명SID/이름변환정책적용여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Windows
draft: true
---

# W-12 익명 SID/이름 변환 허용 해제

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | W-12 |
| **점검내용** | 익명SID/이름변환정책적용여부점검 |
| **점검대상** | Windows 2003, 2008, 2012, 2016, 2019, 2022 |
| **양호기준** | '익명SID/이름변환허용'정책이'사용안함'으로설정된경우 |
| **취약기준** | '익명SID/이름변환허용'정책이'사용'으로설정된경우 |
| **조치방법** | '네트워크액세스:익명SID/이름변환허용'정책'사용안함'설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: '네트워크 액세스: 익명 SID/이름 변환 허용' 정책이 '사용 안 함'으로 설정된 경우
- **취약**: '네트워크 액세스: 익명 SID/이름 변환 허용' 정책이 '사용'으로 설정된 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| W-01 미적용 환경 | 주의 | Administrator 계정 이름을 변경하지 않았다면 우선순위 낮음 |
| 도메인 컨트롤러 | 주의 | AD 환경에서는 추가 고려 필요 |
| 레거시 애플리케이션 | 주의 | 일부 구형 앱에서 SID 조회 필요 가능 |
| 레지스트리 값 없음 | 취약 | 기본값은 '사용'임 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| 모든 Windows 서버 | 익명 SID/이름 변환 허용 | 사용 안 함 | W-01(관리자 계정 이름 변경)과 함께 적용 |

### 2. 점검 방법

#### Windows 서버 점검

익명 SID/이름 변환을 비활성화하여, W-01(Administrator 계정 이름 변경)의 효과를 유지하고 공격자가 SID 조회로 계정 정보를 획득하는 것을 방지해야 합니다.

```bash
# PowerShell - 레지스트리 확인
Get-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Lsa" -Name "RestrictAnonymousSAM"
```

**양호 출력 예시:**
```text
RestrictAnonymousSAM : 1
또는
RestrictAnonymousSAM : 2
```
값이 1 또는 2이면 '사용 안 함'으로 양호

**취약 출력 예시:**
```text
RestrictAnonymousSAM : 0
또는
값이 존재하지 않음
```
값이 0이거나 없으면 '사용'으로 취약

### 3. 조치 방법

#### Windows 서버 설정

1. **레지스트리 설정**
   ```powershell
   # 관리자 권한 PowerShell 실행
   Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Lsa" -Name "RestrictAnonymousSAM" -Value 1 -Type DWord

   # 설정 확인
   Get-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Lsa" -Name "RestrictAnonymousSAM"
   ```

2. **명령 프롬프트 설정**
   ```cmd
   reg add "HKLM\SYSTEM\CurrentControlSet\Control\Lsa" /v RestrictAnonymousSAM /t REG_DWORD /d 1 /f
   ```

3. **로컬 보안 정책 설정 (GUI)**
   ```
   시작 > 제어판 > 관리 도구 > 로컬 보안 정책
   로컬 정책 > 보안 옵션
   '네트워크 액세스: 익명 SID/이름 변환 허용' 더블클릭
   '사용 안 함' 선택
   ```

4. **그룹 정책(GPO) 설정 (도메인 환경)**
   ```
   GPO 편집기(gpedit.msc 또는 gpmc.msc)
   컴퓨터 구성 > 정책 > Windows 설정 > 보안 설정 > 로컬 정책 > 보안 옵션
   '네트워크 액세스: 익명 SID/이름 변환 허용' 설정
   '사용 안 함' 선택
   ```

### 4. 참고 자료

- [Microsoft Docs: 익명 열거 제한](https://docs.microsoft.com/ko-kr/windows/security/threat-protection/security-policy-settings/network-access)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.