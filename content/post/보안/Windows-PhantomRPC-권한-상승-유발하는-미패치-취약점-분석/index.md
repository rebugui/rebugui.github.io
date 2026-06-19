---
title: "Windows PhantomRPC: 권한 상승 유발하는 미패치 취약점 분석"
date: 2026-04-29T01:06:46+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
draft: true
---

## 서론

침투 테스트(Penetration Test) 현장에서 레드 팀(Red Team)이 가장 선호하는 시나리오 중 하나는 방화벽이나 엔드포인트 보안 솔루션의 탐지를 피해 조용히 권한을 상승시키는 것입니다. 보통 우리는 잘 알려진 커널 취약점이나 서비스 설정 오류를 노리곤 합니다. 하지만 최근 보고된 'PhantomRPC'는 우리의 상식을 뒤엎는 방식으로 접근합니다.

상상해 보십시오. 일반 사용자 권한으로만 접속해 있는 해커가 복잡한 익스플로잇 코드를 실행하거나 커널 메모리를 직접 조작하지 않고, 단순히 시스템 내부의 통신 프로토콜인 RPC(Remote Procedure Call)를 호출하는 것만으로 `NT AUTHORITY\SYSTEM` 권한을 탈취하는 시나리오입니다. 이 취약점의 가장 큰 문제는 현재까지 마이크로소프트로부터 공식적인 패치가 배포되지 않았다는 점입니다. 즉, Zero-day에 준하는 위협이 현재진행형으로 존재하고 있습니다.

이 글에서는 단순한 뉴스 전달을 넘어, PhantomRPC가 내부적으로 어떤 메커니즘을 통해 권한 상승을 유발하는지 기술적으로 깊이 파헤쳐보고, 보안 담당자가 즉시 적용할 수 있는 대응 전략을 제시하고자 합니다.

## 본론

### PhantomRPC의 기술적 원리와 공격 메커니즘

Windows RPC(원격 프로시저 호출)는 프로세스 간 통신(IPC)의 핵심 메커니즘입니다. PhantomRPC는 특정 RPC 인터페이스의 마샬링(Marshalling) 데이터 처리 과정이나, 호출자(Caller)의 권한을 검증하는 ACL(Access Control List) 검사 로직에 결함이 있음을 악용합니다.

일반적으로 RPC 서버는 클라이언트의 요청을 받기 전에 `ImpersonateSecurityContext`를 호출하여 클라이언트의 권한을 가장(Impersonation)하거나 검증합니다. 그러나 PhantomRPC 취약점은 특정 Opnum(Operation Number) 호출 시, 이 권한 검사 단계가 우회되거나, 잘못된 컨텍스트 핸들을 통해 시스템 권한 컨텍스트를 그대로 사용하도록 만듭니다. 결과적으로 공격자는 낮은 권한의 프로세스에서 높은 권한의 RPC 메서드를 실행하여 임의의 코드를 시스템 권한으로 실행할 수 있습니다.

**[방어 목적의 공격 시나리오 분석]** 공격자는 이미 로컬 사용자 권한(Low-privilege User)을 획득한 상태라고 가정할 때, 취약한 RPC 엔드포인트를 식별하고 악의적인 패킷을 전송하여 시스템 권한을 얻습니다.

```javascript
graph TD
    A[Low-priv User] --> B[Malicious RPC Client]
    B --> C[Bind to Vulnerable Interface]
    C --> D[Send Crafted RPC Request]
    D --> E[RPC Runtime Service]
    E --> F{Access Check Logic}
    F -- Bypassed/Flawed --> G[Elevated Context Execution]
    G --> H[Spawn Shell/Process as SYSTEM]
    F -- Blocked --> I[Access Denied]
```

### PoC 개념 증명 (Proof of Concept)

아래 코드는 취약점의 원리를 이해하기 위한 학습용입니다. 실제 공격용 도구가 아님을 밝히며, 윤리적 해킹(Ethical Hacking) 목적으로만 참조하시기 바랍니다. 이 예제는 Python의 `impacket` 라이브러리 구조를 차용하여, 취약한 RPC 인터페이스에 연결하고 특정 명령을 호출하는 논리를 보여줍니다.

```python
import sys
from impacket.dcerpc.v5 import transport, epm
from impacket.dcerpc.v5.rpcrt import RPC_C_AUTHN_LEVEL_PKT_PRIVACY, RPC_C_AUTHN_WINNT

def check_phantomrpc_vulnerability(target_ip):
    """
    대상 시스템의 RPC 엔드포인트에 연결하여 취약점을 검증하는 개념적 함수입니다.
    실제 환경에서는 무차별 대입(Brute-force)이나 불법 접근 시도를 금지합니다.
    """
    # RPC 바인딩 문자열 예시 (ncacn_np: named pipes)
    stringBinding = r'ncacn_np:%s[\pipe\{vulnerable-uuid}]' % target_ip
    
    try:
        print(f"[*] Attempting to connect to {target_ip}...")
        rpctransport = transport.DCERPCTransportFactory(stringBinding)
        
        # 인증 설정 (NTLM 인증)
        rpctransport.set_connect_timeout(5)
        # dce 연결 설정
        dce = rpctransport.get_dce_rpc()
        dce.connect()
        
        # 인증 레벨 설정 (일반적으로 필요)
        dce.bind(epm.MSRPC_UUID_PORTMAP, transfer_syntax=('8a885d04-1ceb-11c9-9fe8-08002b104860', '2.0'))
        
        print("[+] Connection established. Authenticating...")
        dce.set_auth_level(RPC_C_AUTHN_LEVEL_PKT_PRIVACY)
        dce.set_auth_type(RPC_C_AUTHN_WINNT)
        
        # 가상의 취약한 함수 호출 (Opnum 0 등)
        # 실제 익스플로잇에서는 여기에 특수하게 제작된 페이로드가 들어갑니다.
        # request_packet = create_malicious_rpc_structure()
        # dce.call(request_packet)
        
        print("[!] Vulnerability check logic executed.")
        print("[*] Response handling would occur here if exploit succeeds.")
        
        dce.disconnect()
        
    except Exception as e:
        print(f"[-] Error occurred: {e}")

if __name__ == "__main__":
    # 테스트 환경에서만 사용하세요 (localhost 대상 등)
    # check_phantomrpc_vulnerability("192.168.1.10")
    print("This is a PoC template for educational purposes only.")
```

이 코드는 단순히 연결 시도를 보여주는 수준이지만, 실제 공격에서는 `dce.call()` 부분에 힙 스프레이(Heap Spray) 기법이나 특정 포인터 조작이 포함된 데이터가 전송되어 RPC 서버의 권한 검사를 무시하고 쉘을 실행하게 됩니다.

### 취약점 분석 비교

PhantomRPC는 기존의 권한 상승 취약점과 비교할 때 몇 가지 독특한 특징을 가집니다. 이를 이해하는 것이 방어 전략 수립에 중요합니다.

| 비교 항목 | 일반적인 권한 상승 (Kernel Exploit) | PhantomRPC (Logic Flaw) |
| :--- | :--- | :--- |
| **공격 벡터** | 커널 모드 드라이버 취약점, 메모리 손상 | 사용자 모드 RPC 라이브러리 로직 오류 |
| **탐지 난이도** | 높음 (드라이버 로드 필요, BSOD 위험) | 중간 (정상적인 트래픽으로 위장됨) |
| **안정성** | 낮음 (시스템 크래시 유발 가능) | 높음 (논리적 오류를 이용하므로 안정적) |
| **패치 주기** | 주기적인 패치 화요일에 포함되는 경우 많음 | 미패치(Unpatched) 상태, 즉각적인 대응 필요 |
| **완화 조치** | 드라이버 서명 강제, VBS/HVCI 활성화 | 방화벽 규칙, RPC 인터페이스 제한 |

### 현장 대응 가이드: Step-by-Step

패치가 배포되지 않은 상황에서는 보안 통제(Compensating Control)를 통해 위험을 줄여야 합니다. 다음

---

**출처**: [https://news.google.com/rss/articles/CBMiqgFBVV95cUxQcVN2VkJSZWxIMTAzN2ZZN0l3OVI3d1kzSFN4RFFxblJrN3ZjZ3dYNHdfdk1OQUdNV0MtY2hhOFQ1SjEyZzJVRkU0NGhPVFFBR1RkSEtxdUdySTRSMWszbG5CLTdGcmFUaTRvd2Z5NHdyd0tUZThUT2x5S3NfOTJHNmhDMkNlUUgxSGpVdFluVDZlSFVOdUh1NTJDT0lRM1lPeDkxTm4yMVh4UQ?oc=5](https://news.google.com/rss/articles/CBMiqgFBVV95cUxQcVN2VkJSZWxIMTAzN2ZZN0l3OVI3d1kzSFN4RFFxblJrN3ZjZ3dYNHdfdk1OQUdNV0MtY2hhOFQ1SjEyZzJVRkU0NGhPVFFBR1RkSEtxdUdySTRSMWszbG5CLTdGcmFUaTRvd2Z5NHdyd0tUZThUT2x5S3NfOTJHNmhDMkNlUUgxSGpVdFluVDZlSFVOdUh1NTJDT0lRM1lPeDkxTm4yMVh4UQ?oc=5)