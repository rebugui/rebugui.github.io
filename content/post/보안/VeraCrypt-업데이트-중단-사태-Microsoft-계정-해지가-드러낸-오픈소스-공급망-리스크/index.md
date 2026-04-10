---
title: "VeraCrypt 업데이트 중단 사태: Microsoft 계정 해지가 드러낸 오픈소스 공급망 리스크"
date: 2026-04-11T01:00:40+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 서론

어느 날 아침, 전 세계 수백만 명의 사용자가信赖하던 디스크 암호화 도구가 더 이상 업데이트를 받을 수 없게 되었습니다. 2024년, 오픈소스 암호화 프로젝트 VeraCrypt의 개발자 Mounir Idrassi는 Microsoft로부터 통보 없이 개발자 계정을 해지당했습니다. 결과적으로 Windows 환경에서 VeraCrypt의 정상적인 업데이트 배포가 전면 중단되었습니다.

이 사건은 단순한 계정 정지를 넘어 심각한 구조적 문제를 드러냅니다. 보안 소프트웨어의 무결성과 배포 생존성이 단일 벤더의 정책 결정에 좌우될 수 있다는 사실입니다. 만약 악의적인 공격자가 Microsoft 인프라를 해킹하여 특정 오픈소스 프로젝트의 계정을 탈취하거나, 정책적 이유로 계정을 해지한다면 어떻게 될까요? 이는 전형적인 **공급망 공격(Supply Chain Attack)** 벡터가 됩니다.

이 글에서는 VeraCrypt 사태를 통해 오픈소스 생태계가 안고 있는 공급망 의존성 문제를 분석하고, 실질적인 방어 전략을 제시합니다.

## 본론

### 1. 사건 분석: 무슨 일이 있었나?

VeraCrypt는 TrueCrypt의 후속 프로젝트로, 전 세계 수백만 명이 사용하는 오픈소스 디스크 암호화 도구입니다. Windows, macOS, Linux를 모두 지원하며, 특히 Windows 환경에서는 코드 서명 인증서와 Microsoft의 배포 인프라에 크게 의존하고 있었습니다.

```javascript
graph TD
    A[VeraCrypt 개발자] --> B[Microsoft Developer Account]
    B --> C[Code Signing Certificate]
    C --> D[Windows Binary Signing]
    D --> E[Windows Update Distribution]
    E --> F[End User Installation]
    
    G[Microsoft Account Revocation] -.-> B
    G -.-> H[No Code Signing]
    H -.-> I[Update Distribution Blocked]
    
    style G fill:#ff6b6b,stroke:#333,stroke-width:2px
```

개발자 계정이 해지되면서 다음과 같은 연쇄적 문제가 발생했습니다:

1. **코드 서명 불가**: Windows용 바이너리 서명이 불가능해짐 2. **배포 채널 단절**: Microsoft Store 및 자동 업데이트 메커니즘 중단 3. **사용자 신뢰 하락**: 서명되지 않은 바이너리에 대한 보안 경고 표시 4. **보안 업데이트 지연**: 패치가 있어도 배포할 수 없는 상황

### 2. 기술적 원인: 코드 서명과 공급망 의존성

Windows 생태계에서 소프트웨어를 배포하려면 반드시 **Authenticode 코드 서명**이 필요합니다. 이 과정을 간단한 PowerShell 스크립트로 확인해볼 수 있습니다:

```plain text
# 코드 서명 인증서 확인 스크립트
# ⚠️ 교육 및 방어 목적으로만 사용하세요

function Check-CodeSignature {
    param(
        [string]$FilePath
    )
    
    $signature = Get-AuthenticodeSignature -FilePath $FilePath
    
    $result = [PSCustomObject]@{
        File = Split-Path $FilePath -Leaf
        Status = $signature.Status
        SignerCertificate = $signature.SignerCertificate.Subject
        Issuer = $signature.SignerCertificate.Issuer
        ValidFrom = $signature.SignerCertificate.NotBefore
        ValidTo = $signature.SignerCertificate.NotAfter
        TimeStamp = $signature.TimeStamperCertificate.NotBefore
    }
    
    return $result
}

# VeraCrypt 실행 파일 서명 상태 확인
$veracryptPath = "C:\Program Files\VeraCrypt\VeraCrypt.exe"
if (Test-Path $veracryptPath) {
    $sig = Check-CodeSignature -FilePath $veracryptPath
    Write-Host "=== VeraCrypt 서명 정보 ===" -ForegroundColor Cyan
    Write-Host "서명 상태: $($sig.Status)"
    Write-Host "서명자: $($sig.SignerCertificate)"
    Write-Host "유효 기간: $($sig.ValidFrom) ~ $($sig.ValidTo)"
} else {
    Write-Host "VeraCrypt가 설치되어 있지 않습니다." -ForegroundColor Yellow
}
```

문제는 코드 서명 인증서를 발급받으려면 **Microsoft가 신뢰하는 CA(인증 기관)**를 거쳐야 한다는 점입니다. 그리고 이 과정에서 Microsoft의 정책이나 계정 상태가 절대적인 영향을 미칩니다.

### 3. 공급망 리스크 비교 분석

이번 사태는 여러 공급망 리스크 유형 중 하나를 보여줍니다:

| 리스크 유형 | 사례 | 영향 범위 | 탐지 난이도 | VeraCrypt 사태와의 관련성 | | :--- | :--- | :--- | :--- | :--- | | **벤더 종속성** | Microsoft 계정 해지 | 배포 중단 | 낮음 (공개적) | 직접적 원인 | | **인프라 의존** | GitHub/AWS 장애 | 배포/개발 중단 | 낮음 | 간접적 영향 | | **인증서 만료** | Let's Encrypt 인증서 갱신 실패 | 서비스 중단 | 중간 | 유사 사례 | | **라이선스 변경** | HashiCorp BSL 변경 | 생태계 분열 | 낮음 | 구조적 유사성 | | **공급자 퇴출** | 구글 서비스 종료 | 데이터 손실 | 낮음 | 장기적 리스크 |

### 4. 공격 시나리오: 이 취약점이 악용될 수 있는 방법
> **⚠️ 윤리적 경고**: 다음 시나리오는 순수하게 방어 관점에서의 위협 모델링입니다. 실제 공격 시도는 불법입니다.

```javascript
graph LR
    A[공격자] --> B[Microsoft 인프라 취약점]
    A --> C[내부자 위협]
    A --> D[소셜 엔지니어링]
    
    B --> E[개발자 계정 탈취]
    C --> E
    D --> E
    
    E --> F[코드 서명 인증서 획득]
    F --> G[악성 업데이트 배포]
    G --> H[대규모 공급망 공격]
    
    E --> I[계정 해지]
    I --> J[정상 업데이트 차단]
    J --> K[알려진 취약점 악용]
```

**시나리오 1: 계정 탈취를 통한 악성 업데이트 배포** 공격자가 VeraCrypt 개발자의 Microsoft 계정을 탈취하면, 합법적인 코드 서명으로 악성 바이너리를 배포할 수 있습니다. 이는 SolarWinds 공격과 유사한 벡터입니다.

**시나리오 2: 업데이트 차단을 통한 취약점 악용** 계정 해지로 인해 보안 패치가 배포되지 않으면, 공격자는 이미 패치된 취약점을 악용할 수 있습니다. 사용자는 "최신 버전"이라고 믿지만 실제로는 취약한 버전을 사용하게 됩니다.

**PoC: 업데이트 상태 확인 도구**

```python
#!/usr/bin/env python3
"""
오픈소스 소프트웨어 업데이트 상태 모니터링 도구
방어 목적: 설치된 소프트웨어의 업데이트 가능성 확인
"""

import requests
import json
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class SoftwareStatus:
    name: str
    installed_version: str
    latest_version: str
    last_update_date: datetime
    signing_authority: str
    update_channel_active: bool

def check_veracrypt_status():
    """VeraCrypt 업데이트 상태 확인"""
    
    # GitHub API를 통한 최신 릴리즈 확인
    api_url = "https://api.github.com/repos/veracrypt/VeraCrypt/releases/latest"
    
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        
        release_data = response.json()
        
        status = SoftwareStatus(
            name="VeraCrypt",
            installed_version="1.25.9",  # 예시
            latest_version=release_data['tag_name'].lstrip('VeraCrypt_'),
            last_update_date=datetime.strptime(
                release_data['published_at'][:10], 
                '%Y-%m-%d'
            ),
            signing_authority="IDRIX SARL",
            update_channel_active=True  # GitHub는 정상
        )
        
        # 업데이트 지연 경고
        days_since_update = (datetime.now() - status.last_update_date).days
        
        if days_since_update > 90:
            print(f"[WARNING] {status.name} - 마지막 업데이트가 {days_since_update}일 전입니다.")
            print("  업데이트 채널 장애 가능성을 확인하세요.")
        
        return status
        
    except requests.RequestException as e:
        print(f"[ERROR] 업데이트 확인 실패: {e}")
        return None

def verify_binary_signature(binary_path: str) -> dict:
    """
    바이너리 서명 검증 (Windows)
    sigcheck와 유사한 기능의 Python 구현
    """
    import subprocess
    
    try:
        # PowerShell을 사용한 서명 확인
        cmd = f'''
        $sig = Get-AuthenticodeSignature "{binary_path}"
        ConvertTo-Json @{{
            Status = $sig.Status.ToString()
            Subject = $sig.SignerCertificate.
```

```python
Subject
            Issuer = $sig.SignerCertificate.Issuer
            NotAfter = $sig.SignerCertificate.NotAfter.ToString()
        }}
        '''
        
        result = subprocess.run(
            ["powershell", "-Command", cmd],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return json.loads(result.stdout)
        
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print("=== VeraCrypt 공급망 상태 점검 ===
")
    status = check_veracrypt_status()
    
    if status:
        print(f"소프트웨어: {status.name}")
        print(f"최신 버전: {status.latest_version}")
        print(f"마지막 업데이트: {status.last_update_date.strftime('%Y-%m-%d')}")
        print(f"서명 기관: {status.signing_authority}")
        print(f"업데이트 채널 활성: {'✅' if status.update_channel_active else '❌'}")
```

### 5. Step-by-step 방어 가이드: 공급망 리스크 완화 전략

#### Step 1: 다변화된 배포 채널 구축

```bash
#!/bin/bash
# 다중 소스에서 다운로드 검증 스크립트
# ⚠️ 방어 목적: 무결성 검증 자동화

SOFTWARE="VeraCrypt"
VERSION="1.26.7"
HASH_ALGO="sha256"

# 다운로드 소스 정의
declare -A SOURCES=(
    ["GitHub"]="https://github.com/veracrypt/VeraCrypt/releases/download/VeraCrypt_${VERSION}/veracrypt-${VERSION}.exe"
    ["Official"]="https://www.veracrypt.fr/en/Downloads.html"
    ["Mirror"]="https://www.fosshub.com/VeraCrypt.html"
)

# 예상 해시값 (공식 웹사이트에서 확인)
EXPECTED_HASH="1234567890abcdef..."  # 실제 해시로 교체 필요

for source in "${!SOURCES[@]}"; do
    echo "[*] ${source}에서 다운로드 시도..."
    url="${SOURCES[$source]}"
    filename="${SOFTWARE}_${VERSION}_${source}.exe"
    
    # 다운로드
    curl -L -o "$filename" "$url" 2>/dev/null
    
    if [ -f "$filename" ]; then
        actual_hash=$(${HASH_ALGO}sum "$filename" | awk '{print $1}')
        
        echo "  소스: ${source}"
        echo "  해시: ${actual_hash}"
        
        if [ "$actual_hash" = "$EXPECTED_HASH" ]; then
            echo "  ✅ 해시 일치 - 무결성 확인됨"
            break
        else
            echo "  ❌ 해시 불일치 - 변조 가능성"
            rm "$filename"
        fi
    fi
done
```

#### Step 2: 서명 검증 자동화

```python
#!/usr/bin/env python3
"""
소프트웨어 서명 자동 검증 시스템
CI/CD 파이프라인에 통합하여 사용
"""

import subprocess
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SupplyChainMonitor")

class SignatureVerifier:
    def __init__(self):
        self.trusted_publishers = {
            "VeraCrypt": "IDRIX SARL",
            "7-Zip": "Igor Pavlov",
            # 추가 신뢰할 수 있는 게시자 등록
        }
    
    def verify_windows_binary(self, filepath: str) -> Dict:
        """Windows 바이너리 서명 검증"""
        try:
            result = subprocess.run(
                ["sigcheck", "-a", "-h", filepath],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            verified = "Verified:\tSigned" in result.stdout
            
            return {
                "file": filepath,
                "signed": verified,
                "output": result.stdout
            }
        except FileNotFoundError:
            logger.warning("sigcheck 도구가 설치되지 않았습니다.")
            return {"file": filepath, "signed": False, "error": "sigcheck not found"}
    
    def check_certificate_chain(self, filepath: str) -> List[str]:
        """인증서 체인 검증"""
        try:
            result = subprocess.run(
                ["certutil", "-verify", filepath],
                capture_output=True,
                text=True
            )
            
            chain = []
            for line in result.stdout.split('
'):
                if "CN=" in line:
                    chain.append(line.strip())
            
            return chain
        except Exception as e:
            logger.error(f"인증서 체인 확인 실패: {e}")
            return []

# 사용 예시
if __name__ == "__main__":
    verifier
```

---

**출처**: [https://news.hada.io/topic?id=28330](https://news.hada.io/topic?id=28330)