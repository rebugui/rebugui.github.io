---
title: "[2026 주요정보통신기반시설] W-26 RDS(Remote Data Services) 제거"
slug: "2026-주정통/W-26"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "RDS(Remote Data Services) 비활성화 여부 점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Windows
---

# W-26 RDS(Remote Data Services) 제거

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | W-26 |
| **점검내용** | RDS(Remote Data Services) 비활성화 여부 점검 |
| **점검대상** | Windows NT, 2000, 2003 |
| **양호기준** | RDS 관련 레지스트리 및 가상 디렉터리가 제거된 경우 |
| **취약기준** | RDS 기능을 사용 중이거나 관련 파일이 존재하는 경우 |
| **조치방법** | 사용하지 않는 경우 IIS 서비스 중지/사용 안 함, 사용할 경우 레지스트리 키 값 제거 또는 관련 패치 적용 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: RDS(Remote Data Services) 관련 파일과 레지스트리 키가 제거된 경우
- **취약**: IIS에 msadc 가상 디렉터리가 존재하거나 RDS 관련 레지스트리 키가 활성화된 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| Windows Server 2008 이상 | 양호 | 기본적으로 RDS가 설치되지 않음 |
| msadc 디렉토리만 제거됨 | 양호 | 가상 디렉터리 제거로 충분 |
| 레지스트리 키만 존재하나 IIS 매핑 없음 | 주의 | 안전하나 제거 권장 |
| ADCLaunch 레지스트리 존재 | 취약 | RDS 활성화 상태 |
| msadcs.dll 파일만 존재 | 주의 | IIS 핸들러 매핑 확인 필요 |
| 레거시 애플리케이션 사용 중 | 주의 | 최신 기술로 마이그레이션 권장 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| IIS 가상 디렉터리 | msadc | 제거 | RDS 제거 |
| IIS 핸들러 매핑 | .idc, .ida, .idq | 제거 | ISAPI 확장 제거 |
| 레지스트리 | ADCLaunch 키 | 제거 | HKLM\SYSTEM\CurrentControlSet\Services\W3SVC\Parameters\ |

### 2. 점검 방법

#### Windows IIS 서버 점검

RDS는 과거 IIS에서 사용되던 데이터베이스 연동 기능으로, 심각한 보안 취약점(MDAC 취약점 등)이 알려져 있습니다.

```powershell
# IIS msadc 가상 디렉터리 확인
Import-Module WebAdministration
Get-WebVirtualDirectory -Site "Default Web Site" | Where-Object {$_.Path -like "*msadc*"}
```

**양호 출력 예시:**
```text
(결과 없음)
```

**취약 출력 예시:**
```text
Name      : msadc
Path      : C:\Program Files\Common Files\System\msadc
```

```powershell
# 레지스트리 키 확인
Get-Item "HKLM:\SYSTEM\CurrentControlSet\Services\W3SVC\Parameters\ADCLaunch" -ErrorAction SilentlyContinue
```

**양호 출력 예시:**
```text
Get-Item: Cannot find path
```

**취약 출력 예시:**
```text
    Hive: HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\W3SVC\Parameters
Name                           Property
----                           --------
ADCLaunch                       {AdvancedDataFactory}
```

```cmd
# 파일 존재 여부 확인
dir "C:\Program Files\Common Files\System\msadc\msadcs.dll"
```

```powershell
# IIS 핸들러 매핑 확인 (구형 ISAPI)
Get-WebConfiguration -Filter "/system.webServer/handlers" -PSPath "IIS:\" | Where-Object {$_.path -like "*.idc" -or $_.path -like "*.ida"}
```

### 3. 조치 방법

#### Windows IIS 서버 설정

1. **msadc 가상 디렉터리 제거**
   ```powershell
   # 가상 디렉터리 제거
   Remove-WebVirtualDirectory -Site "Default Web Site" -Name "msadc"

   # 또는
   Remove-WebVirtualDirectory -Site "IIS여러사이트이름" -Application "/" -Name "msadc"
   ```

2. **레지스트리 키 제거**
   ```powershell
   # ADCLaunch 레지스트리 키 삭제
   Remove-Item -Path "HKLM:\SYSTEM\CurrentControlSet\Services\W3SVC\Parameters\ADCLaunch" -Recurse -ErrorAction SilentlyContinue
   ```

3. **IIS 핸들러 매핑 제거**
   ```powershell
   # 구형 ISAPI 확장 제거
   Remove-WebConfigurationProperty -Filter "/system.webServer/handlers" -PSPath "IIS:\" -Name "." -AtElement @{path="*.idc"}
   Remove-WebConfigurationProperty -Filter "/system.webServer/handlers" -PSPath "IIS:\" -Name "." -AtElement @{path="*.ida"}
   Remove-WebConfigurationProperty -Filter "/system.webServer/handlers" -PSPath "IIS:\" -Name "." -AtElement @{path="*.idq"}
   ```

4. **IIS 관리자에서 제거 (GUI)**
   ```
   1. IIS 관리자 실행
   2. 기본 웹 사이트(또는 운영 중인 사이트) 확장
   3. "msadc" 가상 디렉터리 우클릭
   4. [제거] 클릭
   ```

5. **IIS 관리자에서 핸들러 매핑 제거 (GUI)**
   ```
   1. IIS 관리자 > 서버 노드 선택
   2. "핸들러 매핑" 더블클릭
   3. *.idc, *.ida, *.idq 등 구형 ISAPI 확장 검색
   4. 해당 항목 선택 > [제거]
   ```

### 4. 참고 자료

- [Microsoft Security Bulletin MS02-065](https://docs.microsoft.com/en-us/security-updates/securitybulletins/2002/ms02-065)
- [Microsoft Docs: RDS 취약점](https://docs.microsoft.com/ko-kr/previous-versions/windows/it-pro/windows-server-2003/cc771485(v=ws.10))
- [CVE-1999-0747: RDS DataFactory vulnerability](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-1999-0747)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.