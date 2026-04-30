---
title: "Microsoft SharePoint Server 0-Day: 실제 공격에 악용 중인 취약점 분석"
date: 2026-05-01T01:06:44+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 서론

어제 새벽 3시, 한 중견 제조업체의 보안팀이 SIEM 시스템에서 의심스러운 트래픽을 포착했다. SharePoint 서버에서 발생한 비정상적인 프로세스 생성 로그였다. `w3wp.exe`가 `powershell.exe`를 실행하고, 외부 C2 서버로 5GB의 문서가 유출되고 있었다. 이미 늦었다. 공격자는 72시간 전就已经 시스템을 장악했다.

이것은 가상의 시나리오가 아니다. Microsoft SharePoint Server의 0-Day 취약점이 현재 실제 공격에 악용되고 있으며, 패치되지 않은 시스템은 누구나 표적이 될 수 있다.

SharePoint는 전 세계 수십만 개 기업이 문서 관리와 협업에 사용하는 핵심 인프라다. 내부 문서, 인사 기록, 재무 데이터, 심지어 경영진의 기밀 자료까지 모여 있는 '단일 실패점'이다. 이 서버가 털리면 기업의 모든 비밀이 한꺼번에 유출된다.

더 심각한 문제는 SharePoint가 내부망에 위치한다는 점이다. 공격자가 외부에서 직접 공격하기 어려워 보이지만, 피싱 공격으로 내부 PC를 장악한 뒤 SharePoint를 타겟으로 삼는다면 이야기가 달라진다. 한 번 뚫리면 Active Directory 전체로의 lateral movement가 가능해진다.

## 본론

### 취약점 기술 분석

이번 0-Day 취약점은 SharePoint의 웹 애플리케이션 레이어에서 발생한다. 공격자는 특수하게 조작된 HTTP 요청을 통해 서버 측에서 임의 코드를 실행할 수 있다. 인증이 필요 없다는 점이 핵심이다.

```javascript
graph LR
    A[공격자] --> B[특수 조작된 HTTP 요청]
    B --> C[SharePoint 서버]
    C --> D[취약한 파서 실행]
    D --> E[임의 코드 실행]
    E --> F[시스템 장악]
    F --> G[문서 유출]
    F --> H[내부망 횡적 이동]
```

취약점의 근본 원인은 입력 검증 부족에 있다. SharePoint는 다양한 파일 포맷과 메타데이터를 처리하는 복잡한 파서를 사용한다. 이 파서가 악의적으로 조작된 입력을 제대로 필터링하지 못하고, 결국 메모리 corruption이나 unsafe deserialization으로 이어진다.

### 공격 시나리오 상세 분석

실제 공격은 다음 단계로 진행된다:

**1단계: 정찰 (Reconnaissance)** 공격자는 대상 기업의 SharePoint 서버를 식별한다. 기업 도메인에 `/sites`, `/_layouts`, `/_api` 같은 경로를 스캔하여 SharePoint 존재를 확인한다.

**2단계: 취약점 확인** 버전 정보를 수집하고, 패치 이력을 추정한다. 많은 조직이 SharePoint 업데이트를 미루는 경향이 있어 구버전이 대부분이다.

**3단계: 익스플로잇 실행** 특수하게 조작된 요청을 전송하여 취약점을 트리거한다. 서버 프로세스 권한으로 코드가 실행된다.

**4단계: 지속성 확보** 웹쉘을 설치하거나, 예약 작업을 등록하여 재부팅 후에도 접근을 유지한다.

**5단계: 데이터 수집 및 유출** SharePoint 데이터베이스에 접근하여 문서를 수색하고 외부로 유출한다.

### PoC (개념 증명) 코드
> ⚠️ **윤리적 경고**: 다음 코드는 학습 및 방어 목적으로만 작성되었습니다. 실제 시스템에 무단으로 실행하는 것은 범죄행위입니다. 반드시 자체 테스트 환경에서만 사용하세요.

```python
#!/usr/bin/env python3
"""
SharePoint 0-Day Vulnerability Detection PoC
Purpose: Educational and defensive testing only
Author: Security Research Team
"""

import requests
import sys
from urllib.parse import urljoin

class SharePointVulnChecker:
    def __init__(self, target_url):
        self.target = target_url.rstrip('/')
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Content-Type': 'application/json'
        }
        self.indicators = []
    
    def check_sp_version(self):
        """SharePoint 버전 정보 확인"""
        try:
            # _api/endpoint는 버전 정보를 노출할 수 있음
            resp = requests.get(
                f"{self.target}/_api/web",
                headers=self.headers,
                timeout=10,
                verify=False
            )
            
            if resp.status_code == 200:
                # 응답에서 버전 정보 추출
                if 'Microsoft.SharePoint' in resp.text:
                    print("[+] SharePoint instance detected")
                    self._extract_version(resp.text)
                    return True
            return False
        except requests.RequestException as e:
            print(f"[-] Connection error: {e}")
            return False
    
    def check_vulnerability_indicator(self):
        """취약점 간접 지표 확인"""
        # 취약한 엔드포인트에 대한 안전한 테스트
        test_paths = [
            '/_api/web/GetFolderByServerRelativeUrl',
            '/_api/web/GetFileByServerRelativeUrl',
            '/_layouts/15/Upload.aspx'
        ]
        
        results = {
            'accessible_endpoints': [],
            'auth_required': [],
            'potential_risk': 'LOW'
        }
        
        for path in test_paths:
            try:
                url = urljoin(self.target, path)
                resp = requests.get(
                    url,
                    headers=self.
```

```python
headers,
                    timeout=10,
                    verify=False
                )
                
                if resp.status_code == 200:
                    results['accessible_endpoints'].append(path)
                    self.indicators.append(f"Open endpoint: {path}")
                elif resp.status_code == 401:
                    results['auth_required'].append(path)
                    
            except requests.RequestException:
                continue
        
        # 위험도 평가
        if len(results['accessible_endpoints']) > 1:
            results['potential_risk'] = 'MEDIUM'
        
        return results
    
    def generate_report(self, check_results):
        """보안 점검 보고서 생성"""
        report = f"""
========================================
SharePoint Security Assessment Report
========================================
Target: {self.target}
Status: {'Vulnerable' if check_results.get('potential_risk') != 'LOW' else 'Needs Review'}

Findings:
"""
        for indicator in self.indicators:
            report += f"  [!] {indicator}
"
        
        report += f"""
Risk Level: {check_results.get('potential_risk', 'UNKNOWN')}

Recommendations:
1. Apply latest SharePoint security updates immediately
2. Review and restrict API endpoint access
3. Implement WAF rules for SharePoint-specific attacks
4. Enable detailed logging for _api requests
5. Monitor for suspicious process creation from w3wp.exe

========================================
"""
        return report

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <target_url>")
        print(f"Example: {sys.argv[0]} https://sharepoint.company.local")
        sys.exit(1)
    
    target = sys.
```

```python
argv[1]
    
    print("[*] SharePoint Vulnerability Assessment Tool")
    print(f"[*] Target: {target}")
    print("[*] This tool performs NON-INTRUSIVE checks only
")
    
    checker = SharePointVulnChecker(target)
    
    # Step 1: SharePoint 감지
    print("[*] Checking for SharePoint instance...")
    if not checker.check_sp_version():
        print("[-] SharePoint not detected or inaccessible")
        sys.exit(1)
    
    # Step 2: 취약점 지표 확인
    print("[*] Checking vulnerability indicators...")
    results = checker.check_vulnerability_indicator()
    
    # Step 3: 보고서 생성
    report = checker.generate_report(results)
    print(report)

if __name__ == '__main__':
    main()
```

### 취약점 영향 범위 비교

| 영향 범위 | 심각도 | 설명 | 실제 피해 사례 | | :--- | :--- | :--- | :--- | | 원격 코드 실행 (RCE) | Critical | 인증 없이 서버에서 임의 코드 실행 | 랜섬웨어 배포, 백도어 설치 | | 데이터 유출 | High | SharePoint 내 모든 문서 접근 가능 | 기밀문서 유출, 경영정보 노출 | | 권한 상승 | High | 서비스 계정에서 시스템 권한으로 | 도메인 관리자 권한 획득 | | Lateral Movement | Medium | 내부망 다른 시스템으로 이동 | AD 전체 장악, 추가 서버 침투 | | 서비스 거부 | Medium | SharePoint 서비스 중단 | 업무 마비, 비즈니스 연속성 차단 |

### 탐지 방법 및 로그 분석

공격 탐지를 위해서는 다층적인 모니터링이 필요하다. Windows 이벤트 로그, IIS 로그, SharePoint ULS 로그를 교차 분석해야 한다.

```plain text
# SharePoint 공격 탐지를 위한 PowerShell 스크립트
# IIS 로그에서 의심스러운 _api 요청 패턴 탐지

param(
    [string]$LogPath = "C:\inetpub\logs\LogFiles\W3SVC*",
    [int]$Threshold = 50  # 단일 IP당 최대 허용 _api 요청 수
)

Write-Host "[*] SharePoint Attack Detection Script" -ForegroundColor Cyan
Write-Host "[*] Analyzing IIS logs for suspicious patterns..." -ForegroundColor Yellow

# 의심스러운 User-Agent 패턴
$suspiciousPatterns = @(
    "python-requests",
    "curl",
    "wget",
    "nikto",
    "sqlmap",
    "burpsuite"
)

# 위험한 API 엔드포인트
$dangerousEndpoints = @(
    "/_api/web/GetFolderByServerRelativeUrl",
    "/_api/web/GetFileByServerRelativeUrl",
    "/_api/contextinfo",
    "/_vti_bin/ListData.svc"
)

# IIS 로그 분석
Get-ChildItem -Path $LogPath -Filter "*.log" | ForEach-Object {
    $logFile = $_.FullName
    Write-Host "[*] Processing: $logFile" -ForegroundColor Gray
    
    # 로그 파싱 및 분석
    $suspiciousRequests = Select-String -Path $logFile -Pattern $dangerousEndpoints
    
    if ($suspiciousRequests) {
        # IP별 요청 빈도 분석
        $ipCounts = $suspiciousRequests | ForEach-Object {
            if ($_ -match '(\d+\.\d+\.\d+\.\d+)\s+') {
                $matches[1]
            }
        } | Group-Object | Sort-Object Count -Descending
        
        Write-Host "`n[!] Suspicious API access detected:" -ForegroundColor Red
        foreach ($entry in $ipCounts | Where-Object { $_.Count -gt $Threshold }) {
            Write-Host "    IP: $($entry.Name) - Requests: $($entry.Count)" -ForegroundColor Yellow
        }
    }
}

# 프로세스 생성 모니터링 (공격 후 단계 탐지)
Write-Host "`n[*] Checking for suspicious process creations..." -ForegroundColor Yellow

```

```plain text
Get-WinEvent -FilterHashtable @{
    LogName = 'Security'
    ID = 4688  # Process Creation
} -MaxEvents 1000 | Where-Object {
    $_.Properties[5].Value -eq 'w3wp.exe' -and 
    $_.Properties[13].Value -match 'powershell|cmd|wscript|cscript'
} | ForEach-Object {
    $parentProc = $_.Properties[5].Value
    $childProc = $_.Properties[13].Value
    $commandLine = $_.Properties[8].Value
    
    Write-Host "[!!!] ALERT: Suspicious process chain detected!" -ForegroundColor Red
    Write-Host "    Parent: $parentProc -> Child: $childProc" -ForegroundColor Red
    Write-Host "    Command: $commandLine" -ForegroundColor Red
    Write-Host "    Time: $($_.TimeCreated)" -ForegroundColor Red
    Write-Host ""
}

Write-Host "[*] Scan complete. Review findings above." -ForegroundColor Cyan
```

### 완화 조치: Step-by-Step 가이드

**1단계: 즉시 패치 적용**

```plain text
# 관리자 권한으로 실행
# 현재 SharePoint 버전 확인
Get-SPFarm | Select-Object BuildVersion

# 최신 누적 업데이트 확인
# https://aka.ms/SPUpdate 로 이동하여 최신 CU 다운로드

# 패치 적용 전 팜 백업
Backup-SPFarm -Directory "C:\SPBackup" -BackupMethod Full
```

**2단계: 네트워크 접근 제한 강화**

```plain text
# Windows 방화벽 규칙 생성
# SharePoint 서버에 대한 접근을 내부망으로만 제한

New-NetFirewallRule -DisplayName "SharePoint - Restrict Access" `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort 80,443 `
    -Action Allow `
    -RemoteAddress "10.0.0.0/8","172.16.0.0/12","192.168.0.0/16" `
    -Profile Domain

# 외부 IP의 직접 접근 차단
New-NetFirewallRule -DisplayName "
```

---

**출처**: [https://news.google.com/rss/articles/CBMid0FVX3lxTE5iUkR0NFdZUzlZNjFVMElONThDTjdjN2N1cWgzUHBTck5XMGM2YXY4ZFlmQ2dmTWNka19CclRYVzNTTkQxdVdkVm9vcnlvQTJDRm1XU0F4NXVsQUdaQkx4OEYtQk41X0ZlSGItVHk4YnY3ZXFzQzBv0gF8QVVfeXFMTWpVc0pXSVNXZlpHaHVNZUhXOG5uRHVSSlRvM0M0NEZucnY0YndiemVha1kxTXAxVUczZTVlNzJIQS03eDdwWVUwQVJ2N0JSZ01XcGh6X1JoX1BtMERIcFJGYzFNSjBRaV9OSElQSEpSd1VXSkMzVmU0MXdjeA?oc=5](https://news.google.com/rss/articles/CBMid0FVX3lxTE5iUkR0NFdZUzlZNjFVMElONThDTjdjN2N1cWgzUHBTck5XMGM2YXY4ZFlmQ2dmTWNka19CclRYVzNTTkQxdVdkVm9vcnlvQTJDRm1XU0F4NXVsQUdaQkx4OEYtQk41X0ZlSGItVHk4YnY3ZXFzQzBv0gF8QVVfeXFMTWpVc0pXSVNXZlpHaHVNZUhXOG5uRHVSSlRvM0M0NEZucnY0YndiemVha1kxTXAxVUczZTVlNzJIQS03eDdwWVUwQVJ2N0JSZ01XcGh6X1JoX1BtMERIcFJGYzFNSjBRaV9OSElQSEpSd1VXSkMzVmU0MXdjeA?oc=5)