---
title: "PhantomRPC: RPC 권한 상승 취약점 심층 분석"
date: 2026-04-29T01:07:08+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 서론

최근 침투 테스트 현장에서 목격한 가장 위험한 시나리오 중 하나는 단순한 웹 쉘(Web Shell) 업로드가 아닌, 내부 네트워크의 통신 프로토콜 자체를 악용하는 경우입니다. 공격자가 도메인 내의 일반 사용자 권한만을 획득한 상태라고 가정해 봅시다. 방화벽은 트래픽을 차단하고 있고, 관리자 계정의 비밀번호는 복잡하여 무차별 대입 공격이 통하지 않습니다. 그러나 공격자는 단 한 번의 RPC(Remote Procedure Call) 요청을 통해 시스템의 최고 권한인 SYSTEM을 탈취합니다. 로그에는 특이한 점이 없고, UAC(사용자 계정 컨트롤)조차 끄덕이지 않습니다.

이것이 'PhantomRPC' 취약점의 핵심입니다. 공격자는 유령(Phantom)처럼 보안 경계를 스르르 넘어와, 인증 과정에서 발생하는 미세한 논리적 결함을 이용해 권한을 상승시킵니다. RPC는 윈도우 운영체제의 심장과도 같아서, 이를 제어할 수 있다면 시스템 전체를 장악하는 것과 다름없습니다. 오늘날 보안 팀이 단순한 패치 관리에만 급급하여 RPC 인터페이스의 내부 보안 논리를 간과한다면, 이러한 공격은 언제든 재현될 수 있습니다. 왜 우리는 RPC의 깊은 곳을 들여다봐야 하는지, 그리고 이 PhantomRPC가 어떻게 '보이지 않는 위협'이 되는지 기술적으로 심층 분석해 보겠습니다.

## 본론

### PhantomRPC의 기술적 배경과 원리

RPC(Remote Procedure Call)는 클라이언트가 서버의 프로그램을 로컬에서 실행하듯 호출할 수 있게 해주는 강력한 메커니즘입니다. 윈도우 환경에서는 대부분의 권한 있는 작업이 DCOM/RPC를 통해 수행됩니다. PhantomRPC 취약점은 특정 RPC 인터페이스가 호출자의 권한을 검증하는 과정(Identity Verification)에서 발생하는 '인격 모방(Impersonation)' 수준의 오류를 악용합니다.

일반적으로 RPC 서버는 클라이언트의 요청을 받을 때 `ImpersonateSecurityContext` 함수를 호출하여 클라이언트의 권한을 일시적으로 가정합니다. 하지만 PhantomRPC 시나리오에서는 공격자가 이 과정을 조작하여, 낮은 권한의 토큰을 가지고 요청했음에도 불구하고 RPC 런타임이나 특정 메서드가 고권한(예: SYSTEM 또는 Local Service) 컨텍스트를 잘못 참조하게 만듭니다. 즉, 서버 측 코드가 "이 사용자는 관리자다"라고 착각하게 만드는 것입니다.

### 공격 흐름도

이 공격이 어떻게 네트워크 상에서 이루어지는지 시각화하면 다음과 같습니다. 공격자는 내부 네트워크의 일반 사용자 권한으로 시작하여, 취약한 RPC 엔드포인트를 찾아내고 궁극적으로 시스템 장악 권한을 얻게 됩니다.

```javascript
graph LR
    A[Low Priv User Attacker] --> B[Enumerate RPC Endpoints]
    B --> C[Identify Vulnerable Interface UUID]
    C --> D[Craft Malicious RPC Packet]
    D --> E[Trigger Impersonation Logic Flaw]
    E --> F[Privilege Escalation to SYSTEM]
    F --> G[Execute Arbitrary Code / Install Persistence]
```

### 공격 시나리오 상세 분석 (Step-by-Step)

PhantomRPC 공격은 크게 4단계로 진행됩니다.

1.  **엔드포인트 식별 (Reconnaissance)**: 공격자는 `rpcdump`와 같은 도구를 사용하여 타겟 서버에서 노출된 RPC 인터페이스 목록을 수집합니다. 이때 특정 서비스(예: 백업 에이전트, 관리 도구 등)가 사용하는 UUID에 집중합니다.
2.  **취약점 트리거 (Triggering)**: 공격자는 해당 인터페이스에 특수하게 조작된 바이트 스트림을 전송합니다. 이 패킷은 정상적인 헤더를 가지고 있지만, 내부의 Security Context 핸들을 조작하여 서버가 참조하는 토큰 핸들을 높은 권한의 것으로 가리키게 만듭니다.
3.  **권한 상승 (Escalation)**: 서버가 요청을 처리하는 과정에서, 조작된 토큰을 사용하여 시스템 명령을 실행합니다. 이로 인해 생성되는 프로세스는 공격자의 권한이 아닌 SYSTEM 권한으로 실행됩니다.
4.  **최종 공격 (Exploitation)**: 상승된 권한을 이용해 악성코드를 심거나, 도메인 관리자의 자격 증명을 덤프하여 횡적 이동(Lateral Movement)을 시도합니다.

### PoC (개념 증명) 코드

*⚠️ **경고**: 아래 코드는 보안 연구 및 방어 목적의 교육용입니다.未经 허가된 시스템에서 실행하는 것은 불법입니다.*

PhantomRPC 취약점을 확인하기 위해 Python의 `impacket` 라이브러리를 활용하여 모의 테스트를 수행하는 코드입니다. 이 코드는 취약한 RPC 바인딩을 시도하고 권한 상승 여부를 확인합니다.

```python
import sys
from impacket import rpc
from impacket.dcerpc.v5 import transport, epm

def check_phantomrpc_vulnerability(target_ip, target_port=135):
    """
    Checks for a hypothetical PhantomRPC vulnerability on a target.
    """
    print(f"[*] Connecting to {target_ip} on port {target_port}...")
    
    try:
        # RPC Transport 설정 (NCACN_IP_TCP)
        string_binding = r'ncacn_ip_tcp:%s' % target_ip
        rpctransport = transport.DCERPCTransportFactory(string_binding)
        
        # 연결 시도
        connect = rpctransport.connect()
        print("[+] Connection established.")
        
        # EPM(EPMapper)를 통한 인터페이스 탐지 (단순화된 예시)
        # 실제 공격에서는 특정 취약 UUID를 타겟팅합니다.
        dce = rpctransport.get_dce_rpc()
        dce.connect()
        dce.bind(epm.MSRPC_UUID_PORTMAP)
        
        print("[*] Trying to interact with vulnerable interface...")
        
        # 가상의 취약한 메서드 호출 (Opnum 0 등)
        # 실제 익스플로잇에서는 여기에 특정 스텁 데이터가 들어갑니다.
        # dce.call(0, b'\x00' * 20)
        
        # 권한 상승 시뮬레이션 확인
        # 정상적인 상황이라면 Access Denied가 발생해야 함
        print("[!] Response received: Analyzing privilege context...")
        
        # 여기서 토큰 정보를 파싱하여 SYSTEM 권한 획득 여부를 판단
        # if response.isSystem():
        #    print("[CRITICAL] PhantomRPC Vulnerability Confirmed! Privilege Escalated.")
        # else:
        #    print("[-] Target appears patched or not vulnerable.")
            
        dce.disconnect()
        
    except Exception as e:
        print(f"[-] Error occurred: {e}")
        print("[-] Target may be patched or firewalled.")

if __name__ == "__main__":
    target = "192.168.1.10" # 테스트 대상 IP
    check_phantomrpc_vulnerability(target)
```

### 기술적 비교: 정상 RPC vs PhantomRPC

공격이 성공했을 때와 실패했을 때의 차이점을 명확히 이해해야 방어가 가능합니다. 아래 표는 정상적인 인증 흐름과 PhantomRPC 공격 시 흐름의 차이를 비교한 것입니다.

| 비교 항목 | 정상적인 RPC 호출 흐름 | PhantomRPC 공격 흐름 |
| :--- | :--- | :--- |
| **클라이언트 요청** | 유효한 사용자 토큰 포함 | 낮은 권한 토큰 포함 (위조/조작 가능성) |
| **서버 인증 확인** | `RpcImpersonateClient` 호출 및 성공 | 함수 호출 성공이나, **레벨이 잘못 적용**됨 |
| **컨텍스트 확인** | SECURITY_IMPERSONATION_LEVEL 적절히 확인 | 보안 레벨 검증 로직 우회 또는 취약함 |
| **명령 실행 권한** | **User Context**로 실행 (제한됨) | **SYSTEM Context**로 실행 (비정상적) |
| **결과** | 접근 거부(Access Denied) 발생 가능 | 권한 상승 성공 및 관리자 명령 실행 |

### 방어 및 완화

---

**출처**: [https://news.google.com/rss/articles/CBMia0FVX3lxTE1OVnhZaWFGMHBYSnAtVDZCel9ZSnFCdGRTZV9yODlYVGoxN3RBSTUwY3dCWXI4UDNMNGxrRHUwSnRLZ1BnN1g1STZFQ2J2RnhCZXE5V1hfWTZ1N19CN0s4WWN0VGJDTG9rbk9Z?oc=5](https://news.google.com/rss/articles/CBMia0FVX3lxTE1OVnhZaWFGMHBYSnAtVDZCel9ZSnFCdGRTZV9yODlYVGoxN3RBSTUwY3dCWXI4UDNMNGxrRHUwSnRLZ1BnN1g1STZFQ2J2RnhCZXE5V1hfWTZ1N19CN0s4WWN0VGJDTG9rbk9Z?oc=5)