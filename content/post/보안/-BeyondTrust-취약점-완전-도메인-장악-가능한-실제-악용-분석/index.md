---
title: "🚨 BeyondTrust 취약점: 완전 도메인 장악 가능한 실제 악용 분석"
date: 2026-04-19T08:06:39+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 서론

새벽 2시, SOC(Security Operations Center) 모니터링 화면을 붉게 물들이는 경고 메시지. BeyondTrust Privileged Remote Access(PRA) 관리 콘솔에서 이상적인 트래픽이 감지되었다는 알림입니다. 처음에는 단순한 잘못된 로그인 시도로 보였지만, 곧 해당 세션이 `SYSTEM` 권한으로 도메인 컨트롤러와 통신을 시작했습니다. 이것은 결코 단순한 오작동이 아닙니다.

우리가 흔히 '요새'라고 믿던 Privileged Access Management(PAM) 솔루션이 공격자의 '발판'이 되는 순간입니다. 최근 실제 공격(ITW)에서 확인된 BeyondTrust의 치명적인 취약점은 단순한 서비스 거부를 넘어, **공격자에게 도메인 전체를 장악할 수 있는 '골든 티켓'**을 내어주고 있습니다. 이 글에서는 이 취약점이 어떻게 방어선을 뚫고 Active Directory(AD)의 핵심을 탈취하는지, 그 기술적 메커니즘과 대응 전략을 다룹니다.

*(⚠️ **윤리적 경고**: 본 문서에 포함된 기술적 내용과 코드는 보안 연구 및 방어 목적을 위해서만 작성되었습니다. 무단으로 타인의 시스템에 시뮬레이션을 수행하는 것은 불법입니다.)*

## 본론

### 취약점의 기술적 원인과 메커니즘

이번 사태의 핵심은 BeyondTrust 제품군(주로 Password Safe 또는 Remote Support)의 특정 API 엔드포인트 및 웹 인터페이스에서 발생하는 **인증 우회 및 권한 상승 취약점**입니다. 공격자는 복잡한 공격 툴이 필요 없습니다. 취약한 버전을 실행 중인 서버에 특수하게 조작된 HTTP 요청을 보내기만 하면, 인증 절차를 거치지 않고도 백엔드 서비스의 기능을 실행할 수 있습니다.

더욱 위험한 점은 이 서비스가 대개 Windows 서버 내에서 `NT AUTHORITY\SYSTEM` 또는 `Local System`과 같은 고권한 계정으로 실행된다는 점입니다. 공격자가 이 취약점을 통해 임의의 명령을 실행하거나 구성 설정을 조작할 수 있게 되면, PAM이 관리하던 모든 자격 증명이 공격자의 손아귀에 들어오게 됩니다.

### 공격 시나리오: 인증 우부부터 도메인 장악까지

공격자는 이 취약점을 악용하여 다음과 같은 단계로 공격을 수행합니다.

1.  **정찰(Reconnaissance)**: 인터넷에 노출된 BeyondTrust 인터페이스를 스캔하여 취약한 버전 식별. 2.  **초기 침투(Initial Access)**: 별도의 자격 증명 없이 취약한 API 엔드포인트에 악성 페이로드 전송. 3.  **권한 상승(Privilege Escalation)**: 서버의 SYSTEM 권한 획득. 4.  **자격 증명 추출(Credential Dumping)**: 메모리 내 로그온 세션 또는 PAM 자격 증명 저장소에서 Domain Admin 계정 정보 탈취. 5.  **횡적 이동(Lateral Movement)**: 탈취한 Domain Admin 계정으로 도메인 내 다른 중요 서버 접속.

이 흐름을 시각화하면 다음과 같습니다.

```javascript
graph LR
    A[Attacker] --> B[Vulnerable BeyondTrust Endpoint]
    B --> C[Authentication Bypass]
    C --> D[SYSTEM Level Access]
    D --> E[Credential Dumping]
    E --> F[Domain Admin Credentials]
    F --> G[Full Domain Compromise]
```

### 심층 분석: 공격 코드 및 검증 방법

*이 섹션은 시스템 관리자가 자사 시스템의 취약 여부를 확인하기 위한 PoC(개념 증명) 코드를 포함합니다.*

취약점은 주로 특정 REST API 호출 시 적절한 권한 검사가 누락되어 발생합니다. 아래의 Python 스크립트는 대상 서버가 의심스러운 응답을 반환하는지 확인하는 가상의 체크 로직입니다.

```python
import requests
import sys

def check_vulnerability(target_url):
    """
    대상 BeyondTrust 시스템의 취약 여부를 확인하는 진단 스크립트 (학습용)
    주의: 실제 공격용 페이로드가 아닌, 버전 정보 노출 여부를 확인하는 로직입니다.
    """
    endpoint = f"{target_url}/api/v1/health" 
    # 실제 취약점은 비슷한 방식으로 /api/config 또는 /api/users 등에
    # 인증 없이 접근하여 시스템 정보를 뽑아내는 것입니다.
    
    headers = {
        "User-Agent": "VulnerabilityScanner/1.0",
        "Content-Type": "application/json"
    }

    try:
        # 인증 헤더 없이 요청 전송
        response = requests.get(endpoint, headers=headers, timeout=5, verify=False)
        
        if response.status_code == 200:
            print(f"[!] 경고: 대상 {target_url}이(가) 인증 없이 응답을 반환했습니다.")
            print(f"[*] 상태 코드: {response.status_code}")
            print(f"[*] 응답 데이터 미리보기: {response.text[:100]}...")
            print("[!] 시스템 관리자에게 즉시 보고하세요.")
            return True
        else:
            print(f"[+] 안전: 대상 {target_url}은(는) 적절히 차단되었습니다 (Status: {response.status_code}).")
            return False

    except requests.exceptions.RequestException as e:
        print(f"[-] 네트워크 오류 발생: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python check_pam.py <target_url>")
        sys.exit(1)
    
    target = sys.argv[1]
    check_vulnerability(target)
```

이 코드는 단순히 응답 여부를 확인하는 것이지만, 실제 공격자는 이 메커니즘을利用해 내부 명령어를 실행하거나 데이터베이스를 덤프하는 요청을 보냅니다.

### 완화 조치: 단계별 대응 가이드

문제가 발생했을 때 패닉에 빠지지 않고 체계적으로 대응하기 위해서는 다음의 단계를 따라야 합니다.

| 단계 | 조치 항목 | 상세 설명 | | :--- | :--- | :--- | | **1. 격리 (Isolation)** | 네트워크 차단 | 즉시 BeyondTrust 서버의 외부 인터넷 연결(80/443 등)을 차단하고, 내부 네트워크에서도 관리자 외 접근을 차단합니다. | | **2. 패치 (Patch)** | 소프트웨어 업데이트 | 벤더(BeyondTrust)가 배포한 최신 보안 패치를 즉시 적용합니다. 패치 적용 전에는 서비스를 중지하는 것을 권장합니다. | | **3. 조사 (Forensics)** | 로그 분석 | IIS 로그 및 Windows 이벤트 로그(Security, System)를 분석하여 공격 시점(시작 시간, 사용자 에이전트)을 파악합니다. | | **4. 순환 (Rotation)** | 자격 증명 변경 | PAM에 저장된 **모든** 계정(AD Admin, DB Admin, Root 등)의 비밀번호를 즉시 변경합니다. 공격자가 이미 탈취했을 가능성을 배제할 수 없습니다. |

### 전문가 인사이트: PAM 보안의 재정립

이번 사건은 우리에게 "PAM 솔루션을 도입했다고 안전한 것이 아니다"라는 뼈아픈 교훈을 줍니다. PAM이 **보안의 중심**이 되기 위해서는 다음의 원칙을 준수해야 합니다.

1.  **Zero Trust 아키텍처 적용**: PAM 서버 자체도 신뢰할 수 있는 구역으로 두지 말고, 내부에서도 세밀한 네트워크 세그먼테이션(Micro-segmentation)을 적용해야 합니다. 2.  **관리자 계정 보호**: PAM 시스템에 접근하는 관리자 계정은 반드시 MFA(Multi-Factor Authentication)와 특별히 강화된 IDP(Identity Provider) 정책을 적용해야 합니다. 3.  **익명의 접근 차단**: API 엔드포인트는 IP 화이트리스트와 같은 네트워크 레벨의 보안 계층으로 보호해야 합니다.

## 결론

BeyondTrust 취약점은 단순한 버그가 아닌, 조직의 심장부인 Active Directory를 정지시킬 수 있는 '광선 총'과 같습니다. 실제 공격이 확인된(ITW) 시점에서 지체는 곧 피해로 직결됩니다.

관리자는 즉시 패치를 적용하고, 노출되었을 가능성이 있는 모든 고권한 자격 증명을 순환(Rotate)해야 합니다. 보안 도구가 오히려 공격의 경로가 되지 않도록, PAM 시스템 자체에 대한 보안 감시와 하드닝을 지금 다시 점검해야 할 때입니다.

### 참고자료
- [BeyondTrust Security Advisories](https://www.beyondtrust.com/trust/security-advisories)
- [CWE-287: Improper Authentication](https://cwe.mitre.org/data/definitions/287.html)
- [MITRE ATT&CK: Credential Dumping](https://attack.mitre.org/techniques/T1003/)

---

**출처**: [https://news.google.com/rss/articles/CBMidEFVX3lxTE05REpFaXFCS2FuNzVlY2hSMXpWdWNYQ1lTYS16TEhKT3lBdUtpczlNMU5uNGxSenR2anFIOTFGWjFWR2J2enI5SGt4ZUlfMEFNNzQ0b2lDeDFMR3pQUnlaa0pPOVNLcGdnQU9YM0tXS2doYkM20gF6QVVfeXFMTW42a0NhSThIRnR6MGk3OFZLSENZeWQtaHY1S2Y4VFZVVnZhTEdrQ2IyZzZ2Z0J2Q2lnM09CaUdXUFRiWERsenBzOU91M1dNMHhacG1RdzlXazVtU0FlbXQ4bG9KUFhlRVdGYzMtQWswY09jWlJmSlE0RVE?oc=5](https://news.google.com/rss/articles/CBMidEFVX3lxTE05REpFaXFCS2FuNzVlY2hSMXpWdWNYQ1lTYS16TEhKT3lBdUtpczlNMU5uNGxSenR2anFIOTFGWjFWR2J2enI5SGt4ZUlfMEFNNzQ0b2lDeDFMR3pQUnlaa0pPOVNLcGdnQU9YM0tXS2doYkM20gF6QVVfeXFMTW42a0NhSThIRnR6MGk3OFZLSENZeWQtaHY1S2Y4VFZVVnZhTEdrQ2IyZzZ2Z0J2Q2lnM09CaUdXUFRiWERsenBzOU91M1dNMHhacG1RdzlXazVtU0FlbXQ4bG9KUFhlRVdGYzMtQWswY09jWlJmSlE0RVE?oc=5)