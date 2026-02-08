---
title: "🚨 VMware ESXi: 랜섬웨어 악용 취약점 실제 공격 확인"
date: 2026-02-08T12:57:13+09:00
draft: false
tags:
  - "VMware ESXi"
  - "Ransomware"
  - "Vulnerability"
  - "CISA"
  - "보안"
categories:
  - "보안"
---

## 서론

새벽 2시, 보안 대응 센터(SOC) 모니터링 화면을 가득 채운 것은 붉은색 경보 알림이었습니다. 평소와 다름없는 가상화 환경의 트래픽을 감시하던 직원은 VM(가상 머신)들이 하나둘씩 멈추고, 시스템 로그에 "encrypting"이라는 낯선 키워드가 수록되는 것을 목격합니다. 곧이어 ESXi 호스트의 관리 콘솔 접속이 차단되었고, 모든 가상 머신의 디스크 파일들이 잠금 처리되었다는 랜섬웨어 메시지가 띄워졌습니다.

이것은 단순한 가상 서버 장애가 아닙니다. 최근 CISA(사이버보안 및 인프라 보안국)가 경고한 바와 같이, VMware ESXi의 취약점이 이미 랜섬웨어 공격자들에 의해 실제 필드에서 무기화되고 있다는 명백한 증거입니다. 공격자는 더 이상 복잡한 웹 해킹만 시도하지 않습니다. 그들은 가상화 인프라의 심장부인 'Hypervisor'를 겨냥합니다. 왜 이 주제가 중요할까요? ESXi 하나가 장악되면, 그 위에서 구동되는 수십, 수백 개의 중요 서비스가 일순간에 마비되기 때문입니다. 단일 장애점(SPOF)이 보안의 최약점이 되는 순간, 우리는 가상화의 편리함을 내주고 파국을 맞이할 수 있습니다.

**⚠️ 윤리적 경고**: 본 문서에 포함된 기술적 세부 정보, 코드 예시, 및 공격 시나리오는 오로지 방어 목적과 시스템 취약점 점검을 위해서만 제공됩니다. 승인되지 않은 시스템에 대한 테스트는 불법이며 엄격히 금지됩니다.

## 본론: 기술적 원리와 공격 시나리오

### 1. 취약점의 핵심: 인증 우회(Authentication Bypass)

문제의 핵심은 VMware ESXi의 특정 버전에서 처리되는 사용자 인증 메커니즘에 결함이 있다는 점입니다. ESXi는 기본적으로 OpenSLP(SERVICE LOCATION PROTOCOL) 등을 통해 관리 기능을 노출하거나, Active Directory와 연동하여 권한을 관리합니다.

해당 취약점(최근 CISA가 지적한 CVE-2024-37085 등의 유형)은 공격자가 정상적인 인증 절차를 거치지 않고도 특정 조건 하에서 관리자 권한을 획득할 수 있는 경로를 제공합니다. 예를 들어, Active Directory 도메인 그룹 구성의 취약점을 악용하거나, 특정 API 요청을 조작하여 인증 서버의 검증을 우회하는 방식입니다.

### 2. 랜섬웨어 공격 시나리오 (Kill Chain)

공격자는 어떻게 이 취약점을 이용해 전체 시스템을 암호화할까요? 다음은 실제 현장에서 발생할 수 있는 공격 흐름도입니다.

```mermaid
graph LR
    A[Reconnaissance<br>스캔 및 탐색] -->|포트 443/SLP 스캔| B[Exploitation<br>인증 우회 취약점 공격]
    B --> C[Privilege Escalation<br>루트 권한 획득]
    C --> D[Persistence<br>백도어 설치 및 SSH 활성화]
    D --> E[Execution<br>ESXiArgs 랜섬웨어 실행]
    E --> F[Impact<br>VM 암호화 및 서비스 중단]

    style F fill:#ffcccc,stroke:#ff0000,stroke-width:2px
```

1. **Reconnaissance (정찰)**: 공격자는 인터넷에 노출된 ESXi 관리 포트(기본 443)나 OpenSLP 포트(427)를 스캔하여 취약한 버전의 ESXi를 찾아냅니다.
2. **Exploitation (공격)**: 발견된 취약점을 통해 악성 HTTP 요청이나 특정 패킷을 전송하여, 인증 과정을 우회하고 `root` 권한을 탈취합니다.
3. **Execution (실행)**: 공격자는 ESXi의 SSH 셸에 접근하거나 원격 명령 실행 기능을 사용하여, `.vmx` 파일과 `.vmdk` 파일(가상 머신 설정 및 디스크)을 암호화하는 악성 스크립트를 실행합니다.

### 3. 취약점 진단 PoC (개념 증명) 코드

방어자의 관점에서 시스템이 취약한지 확인하기 위해, 아래와 같은 Python 스크립트로 사전 점검(PoC)을 수행할 수 있습니다. 이 코드는 익명의 공격 도구가 아닌, 관리자가 자사 시스템의 상태를 진단하기 위한 **Scanner**의 형태입니다.

```python
#!/usr/bin/env python3
import requests
import sys
from urllib3.exceptions import InsecureRequestWarning

# 억제성 경고 비활성화 (테스트 환경에서만 사용)
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def check_esxi_vulnerability(target_ip):
    """
    ESXi 타겟의 인증 우회 취약점 여부를 체크하는 진단 함수입니다.
    실제 공격을 수행하지 않으며, 응답 코드를 분석합니다.
    """
    print(f"[*] Checking target: {target_ip}")

    # 취약점 확인을 위한 엔드포인트 (예시)
    # 실제 환경에서는 해당 CVE에 맞는 특정 URI와 패이로드가 필요합니다.
    # 여기서는 설명을 위해 일반적인 구조를 보여줍니다.
    test_url = f"https://{target_ip}/sdk/vimService"

    headers = {
        "User-Agent": "ESXi-Scanner/1.0 (Security Audit)",
        "Content-Type": "text/xml"
    }

    # 인증 우회 시나리오를 시뮬레이션하는 테스트 데이터
    # 실제 악성 코드가 아닌 구조적 검증용 더미 데이터입니다.
    payload = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
                   <soapenv:Header/>
                   <soapenv:Body>
                      <RetrieveServiceContent xmlns="urn:vim25"/>
                   </soapenv:Body>
                 </soapenv:Envelope>"""

    try:
        response = requests.post(test_url, data=payload, headers=headers, verify=False, timeout=5)

        # 200 OK 응답이지만 인증 없이 접근 가능한 경우 등을 분석
        if response.status_code == 200 and "vim25" in response.text:
            print(f"[!] WARNING: Target {target_ip} responded to unauthenticated request.")
            print("[!] Further investigation required to confirm specific CVE version.")
        else:
            print(f"[+] Target {target_ip} seems to enforce authentication or is not vulnerable to this specific check.")

    except requests.exceptions.RequestException as e:
        print(f"[-] Connection error to {target_ip}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 esxi_check.py <TARGET_IP>")
        sys.exit(1)

    target = sys.argv[1]
    check_esxi_vulnerability(target)
```

이 코드는 단순히 ESXi의 서비스 응답을 확인하는 수준의 안전한 예시이나, 실제 공격에서는 이러한 인증 우회 로직을 통해 랜섬웨어 바이너리를 업로드하는 명령어를 삽입하게 됩니다.

### 4. 공격 징후 분석 및 대응 방안 비교

공격이 발생했을 때 시스템 로그에서 어떤 변화가 관찰되는지, 그리고 어떻게 대응해야 하는지 비교해 보겠습니다.

| 구분 | 정상(Normal) 상태 | 침해(Compromised) 징후 | 즉시 조치(Action) |
| :--- | :--- | :--- | :--- |
| **ESXi Shell** | 비활성화되거나, 특정 관리자만 접근 | 알 수 없는 IP에서 SSH 활성화 및 로그인 기록 | SSH 서비스 즉시 중지 및 계정 로그아웃 |
| **파일 시스템** | `.vmx`, `.vmdk` 파일 원본 유지 | 모든 `.vmdk` 파일과 함께 `.args`, `.enc` 파일 생성 | ESXi 호스트 네트워크 분리(Network Isolation) |
| **로그 (Hostd)** | 일반적인 API 요청 및 관리자 로그인 | 인증 우관련 의심 로그 다수 발생, `vim-cmd` 비정상 실행 | 로그 백업 및 포렌식 분석 시작 |
| **성능** | 안정적인 CPU 및 메모리 사용량 | 암호화 연산으로 인한 CPU 급격한 스파이크 | 영향 받은 호스트 전원 차단 |

## 실무 적용 가이드: 방어와 완화 조치

이론적인 이해를 넘어 실제 현장에서 즉시 적용할 수 있는 단계별 가이드를 제공합니다.

### Step 1: 즉시 확인 (Immediate Check)

1. **버전 확인**: ESXi 호스트의 버전이 취약점(CVE-2024-37085 포함 해당되는 버전)에 해당하는지 확인합니다.

```bash
# ESXi Shell에서 실행
vmware -vl
```

2. **패치 적용**: VMware에 제공된 최신 패치(ESXi70U3-xxxxx 등)로 즉시 업데이트를 진행합니다. ESXi 호스트를 VUM(vCenter Update Manager)을 통해 패치하거나, ISO 이미지로 부팅하여 업데이트합니다.

### Step 2: 네트워크 경계 강화 (Network Segmentation)

가장 효과적인 방어는 공격자가 타겟에 도달조차 못하게 하는 것입니다.

- **관리 네트워크 분리**: ESXi 관리 포트(443, 22)를 인터넷에 직접 노출하지 않습니다. 내부 관리용 VPN이나 베어메탐 네트워크(VLAN)로 격리해야 합니다.

- **SLP 서비스 비활성화 (구버전)**: 만약 OpenSLP를 사용 중인 레거시 환경이라면, 이 서비스는 ESXi 7.0 U2c 및 8.0 GA 이상에서 기본 비활성화되었습니다. 하지만 구버전 사용 시 방화벽에서 UDP 427 포트를 차단해야 합니다.

### Step 3: 인증 강화 (Access Control)

- **Active Directory 통합 검증**: ESXi가 AD와 연동되어 있다면, 최소 권한 원칙을 적용하여 ESXi 호스트에 접근할 수 있는 AD 그룹을 엄격히 제한합니다.

- **계정 잠금 정책**: 무작위 대입 공격(Brute Force) 방지를 위해 계정 잠금 임계값을 설정합니다.

## 결론

VMware ESXi를 노리는 랜섬웨어의 유행은 단순히 소프트웨어의 버그를 넘어섭니다. 이는 **"가상화가 곧 인프라의 전부인 현대의 클라우드 환경에서, 하이퍼바이저는 공격자들의 성(Castle)"**이 되고 있음을 의미합니다. CISA의 경고는 단순한 권고가 아니라, 이미 전쟁터가 되었음을 알리는 신호탄입니다.

우리가 지금 당장 해야 할 일은 명확합니다. 첫째, 미루지 말고 패치를 적용하세요. 둘째, 관리 콘솔을 공용 인터넷으로부터 철저히 격리하세요. 마지막으로, 백업 시스템을 오프라인(Immutable Backup)으로 유지하여 최악의 상황에서도 복구할 수 있도록 준비해야 합니다. 보안의 완성은 최신 기술이 아니라, 기본적인 하이진(Hygiene)을 얼마나 빈틈없이 지키느냐에 달려 있습니다.

---

### 참고자료 및 심층 학습 링크

- [CISA Known Exploited Vulnerabilities Catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog)

- [VMware Security Advisories (VMSA)](https://www.vmware.com/security/advisories.html)

- [MITRE ATT&CK: Cloud Infrastructure](https://attack.mitre.org/matrices/enterprise/cloud/)
