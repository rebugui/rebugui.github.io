---
title: "Anthropic Mythos LLM: 32단계 네트워크 공격 시뮬레이션에서 인간 능가"
date: 2026-04-30T01:07:52+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
draft: true
---

## 서론

어느 화요일 새벽 3시, 보안 운영 센터(SOC)의 알람이 울렸다. 한 글로벌 제약企業의 내부망에서 비정상적인 트래픽이 감지된 것이다. 공격자는 이미 경계망을 뚫고 내부 AD(Active Directory)를 타고 있었다. IR(Incident Response) 팀이 대응에 나섰지만, 공격자는 32단계에 걸친 연계 공격을 정확히 47분 만에 완성했다.

만약 이 공격자가 인간이 아니라면? 그리고 그것이 단 12분 만에 같은 작업을 수행한다면?

2024년, Anthropic이 개발한 LLM **'Mythos'**가 UK AI Security Institute의 테스트에서 바로 이 시나리오를 현실로 보여주었다. 32단계 기업 네트워크 침투 시뮬레이션에서 인간 레드팀 전문가를 능가하는 성능을 입증한 것이다. 이는 단순한 기술 데모가 아니다. 사이버보안의 패러다임이 근본적으로 바뀌고 있음을 의미한다.
> **⚠️ 윤리적 경고**: 본 글에서 다루는 모든 공격 기법은 오직 **방어 관점의 이해**를 위한 것입니다. 실제 시스템에 대한 무단 침투 시도는 범죄행위입니다.

## 본론

### Mythos의 32단계 공격 시뮬레이션: 무엇이 특별한가?

기존의 자동화된 공격 도구와 Mythos의 결정적 차이는 **'문맥 이해와 자율적 의사결정'** 능력이다. 전통적인 툴은 정해진 경로만 따르지만, Mythos는 실시간으로 환경을 분석하고 다음 단계를 스스로 결정한다.

```javascript
graph TD
    A[Recon: External Asset Discovery] --> B[Initial Access: Phishing Payload]
    B --> C[Execution: PowerShell Download Cradle]
    C --> D[Persistence: Registry Run Key]
    D --> E[Privilege Escalation: Token Impersonation]
    E --> F[Defense Evasion: AMSI Bypass]
    F --> G[Credential Access: LSASS Dump]
    G --> H[Lateral Movement: Pass-the-Hash]
    H --> I[Collection: Database Exfiltration Staging]
    I --> J[Exfiltration: DNS Tunneling]
```

*32단계 중 핵심 10단계 축약 (MITRE ATT&CK 프레임워크 기반)*

### 인간 vs Mythos: 성능 비교

| 평가 지표 | 인간 레드팀 (평균) | Mythos LLM | 차이 |
| :--- | :--- | :--- | :--- |
| 전체 시나리오 완료 시간 | 4.2시간 | 1.3시간 | **3.2x 빠름** |
| 단계 간 전환 지연 | 8-15분 (분석/판단) | 0.3-2분 | **자율적 의사결정** |
| 오탐/실패 후 복구율 | 72% (재시도 성공) | 94% | **+22% 높음** |
| 노이즈/탐지율 | 34% (보안 솔루션 탐지) | 11% | **은밀성 우수** |
| 크리덴셜 획득 성공률 | 5/8 시도 | 7/8 시도 | **정밀도 높음** |

### 왜 가능한가: LLM 기반 공격의 기술적 원리

Mythos의 성능은 세 가지 핵심 기술에 기반한다.

**1. 컨텍스트 윈도우 내의 전체 네트워크 모델링**

Mythos는 초기 정찰 단계에서 수집한 정보를 바탕으로 내부 네트워크 토폴로지를 자체적으로 모델링한다. 이 모델은 공격 진행 중 지속 업데이트된다.

**2. Chain-of-Thought 기반 공격 체인 계획**

단순한 프롬프트-응답이 아니다. Mythos는 각 단계의 결과를 분석하고, 실패 시 대안 경로를 실시간으로 생성한다.

**3. 메모리 기반의 크리덴셜/권한 추적**

획득한 권한과 자격 증명을 체계적으로 관리하여 최적의 권한 상승 경로를 탐색한다.

### PoC: LLM 기반 자율 공격 에이전트의 의사결정 로직 (학습용)
> **주의**: 이 코드는 개념 증명용으로, 실제 공격 기능은 포함하지 않습니다. Mythos의 의사결정 구조를 이해하기 위한 교육 목적입니다.

```python
"""
Autonomous Attack Agent Decision Engine (Educational PoC)
Mythos LLM의 핵심 의사결정 구조를 단순화한 모델
"""
from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass

class AttackPhase(Enum):
    RECON = 1
    INITIAL_ACCESS = 2
    EXECUTION = 3
    PERSISTENCE = 4
    PRIV_ESC = 5
    DEFENSE_EVASION = 6
    CRED_ACCESS = 7
    LATERAL_MOVEMENT = 8
    COLLECTION = 9
    EXFILTRATION = 10

@dataclass
class Credential:
    username: str
    password_hash: str
    domain: str
    privilege_level: int  # 1=low, 5=domain admin
    source: str

@dataclass
class NetworkNode:
    hostname: str
    ip: str
    os: str
    services: List[str]
    compromised: bool = False

class MythosDecisionEngine:
    """
    Mythos 스타일 공격 의사결정 엔진 (시뮬레이션)
    """
    
    def __init__(self):
        self.phase = AttackPhase.RECON
        self.credentials: List[Credential] = []
        self.compromised_hosts: List[NetworkNode] = []
        self.attack_graph: Dict[str, List[str]] = {}
        self.current_target: Optional[NetworkNode] = None
    
    def evaluate_environment(self, scan_results: Dict) -> Dict:
        """환경 분석 및 다음 최적 단계 결정"""
        
        # 1. 현재 권한 레벨 평가
        max_priv = max(
            (c.privilege_level for c in self.credentials), 
            default=0
        )
        
        # 2. 네트워크 노드 분석
        reachable = [
            n for n in scan_results.get('hosts', [])
            if not n.compromised
        ]
        
        # 3. 의사결정 트리
        if max_priv >= 4:  # 높은 권한 획득 시
            next_action = "lateral_movement_to_dc"
            target = self._find_domain_controller(reachable)
            
        elif max_priv >= 2:  # 일반 사용자 권한
            next_action = "privilege_escalation"
            target = self._find_privesc_vector(
                self.current_target, 
                scan_results
            )
            
        else:
```

```python
  # 권한 없음
            next_action = "credential_harvesting"
            target = self._find_cred_target(reachable)
        
        return {
            "current_phase": self.phase.name,
            "max_privilege": max_priv,
            "recommended_action": next_action,
            "target": target.hostname if target else None,
            "confidence": self._calculate_confidence(scan_results),
            "fallback_options": self._generate_fallbacks(
                next_action, 
                scan_results
            )
        }
    
    def _calculate_confidence(self, context: Dict) -> float:
        """공격 성공 확률 계산"""
        base_score = 0.6
        if len(self.credentials) > 2:
            base_score += 0.15
        if len(self.compromised_hosts) > 1:
            base_score += 0.1
        return min(base_score, 0.95)
    
    def _generate_fallbacks(self, primary: str, context: Dict) -> List[str]:
        """실패 시 대안 경로 생성 (Mythos의 핵심 능력)"""
        fallback_map = {
            "privilege_escalation": [
                "token_impersonation",
                "dll_injection",
                "unquoted_service_path",
                "always_install_elevated"
            ],
            "lateral_movement_to_dc": [
                "pass_the_hash",
                "kerberoasting",
                "dcsync_attack",
                "golden_ticket"
            ]
        }
        return fallback_map.get(primary, ["reposition_and_retry"])
    
    def _find_domain_controller(self, hosts: List) -> Optional[NetworkNode]:
        return next(
            (h for h in hosts if "ldap" in h.services), 
            None
        )
    
    def _find_privesc_vector(self, host, context):
        return host
    
    def _find_cred_target(self, hosts):
        return next(iter(hosts), None)

```

```python
# 시뮬레이션 실행
if __name__ == "__main__":
    engine = MythosDecisionEngine()
    
    # 가상의 스캔 결과 (교육용)
    mock_scan = {
        "hosts": [
            NetworkNode(
                "WS-DESKTOP01", 
                "10.0.1.45", 
                "Windows 10",
                ["smb", "rdp"]
            ),
            NetworkNode(
                "DC-PRIMARY", 
                "10.0.1.1", 
                "Windows Server 2022",
                ["ldap", "kerberos", "smb", "dns"]
            ),
        ]
    }
    
    # 의사결정 수행
    decision = engine.evaluate_environment(mock_scan)
    print(f"[공격 단계] {decision['current_phase']}")
    print(f"[권한 레벨] {decision['max_privilege']}/5")
    print(f"[다음 행동] {decision['recommended_action']}")
    print(f"[성공 확률] {decision['confidence']*100:.0f}%")
    print(f"[대안 경로] {decision['fallback_options']}")
```

### Step-by-Step: 32단계 공격의 핵심 흐름

Mythos가 수행한 32단계 시나리오의 핵심 구간을 분석한다.

**Phase 1: 정찰 및 초기 진입 (Step 1-8)**

1. 외부 자산 열거 (OSINT, 서브도메인, IP 대역)
2. 취약점 스캐닝 (Nmap + 커스텀 시그니처)
3. 피싱 페이로드 생성 (문맥에 맞는 사회공학)
4. 매크로/HTA/DLL 사이드로딩 중 최적 벡터 선택
5. C2 채널 수립 (HTTPS + DNS 이중 채널)
6. 환경 변수 수집 (AV, EDR, 네트워크 위치)
7. 초기 권한 확인
8. 시스템 정보 수집

**Phase 2: 수비 회피 및 지속성 (Step 9-16)**

```javascript
graph LR
    A[AMSI Bypass] --> B[ETW Patching]
    B --> C[DLL Unhooking]
    C --> D[Process Injection]
    D --> E[Registry Persistence]
    E --> F[Scheduled Task Creation]
    F --> G[WMI Event Subscription]
    G --> H[Startup Folder LNK]
```

**Phase 3: 권한 상승 및 크리덴셜 획득 (Step 17-24)**

이 단계에서 Mythos의 차이가 가장 두드러진다. 인간은 경험에 의존하지만, Mythos는 **모든 가능한 권한 상승 벡터를 병렬로 평가**하고 최적 경로를 선택한다.

**Phase 4: 측면 이동 및 데이터 유출 (Step 25-32)**

획득한 크리덴셜을 기반으로 도메인 컨트롤러까지의 경로를 탐색하고, 최종적으로 데이터를 암호화하여 외부로 반출한다.

### 사이버보안은 이제 작업증명(PoW)이다

원문의 핵심 메타포를 기술적으로 해석하면 이렇다.

```python
# 블록체인의 작업증명(PoW)
def pow_mining(block, difficulty):
    nonce = 0
    while not hash_valid(block, nonce, difficulty):
        nonce += 1  # 막대한 연산 자원 투입
    return nonce

# 사이버보안의 "작업증명"
def security_defense(attack_surface):
    """방어는 공격자보다 더 많은 '작업'을 수행해야 함"""
    layers = 0
    for asset in attack_surface:
        layers += patch(asset)         # 지속적 패치
        layers += monitor(asset)       # 24/7 모니터링
        layers += hunt(asset)          # 위협 사냥
        layers += test(asset)          # 침투 테스트
    # 공격자는 한 번 성공하면 됨
    # 방어자는 모든 레이어를 항상 성공해야 함
    return layers  # 방어의 "작업량"
```

Mythos 같은 LLM이 등장하면서 이 비대칭성이 더 극심해진다. 공격자(또는 공격 AI)는 자원을 집중하여 한 곳을 뚫으면 되지만, 방어자는 AI 수준의 자동화로 모든 표면을 보호해야 한다.

### 방어자를 위한 완화 조치 (구체적)

LLM 기반 공격에 대응하기 위한 실무 설정값:

**1. EDR/EDR 규칙 강화 (Process Injection 탐지)**

```yaml
# Sigma 룰 예시: 프로세스 인젝션 의심 행위 탐지
title: Potential Process Injection via CreateRemoteThread
status: experimental
detection:
    selection:
        EventID: 8  # Sysmon CreateRemoteThread
        SourceImage|endswith:
            - '\powershell.exe'
            - '\cmd.exe'
            - '\rundll32.exe'
        TargetImage|endswith:
            - '\svchost.exe'
            - '\explorer.exe'
            - '\lsass.exe'
    condition: selection
level: high
```

**2. 크리덴셜 보호 강화**

```plain text
# Windows Registry 설정
# LSA Protection 활성화
[HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Lsa]
"RunAsPPL"=dword:00000001

# Credential Guard 강제 (GPO)
Computer Configuration > Administrative Templates > System > Device Guard
"Turn On Virtualization Based Security" = Enabled
"Credential Guard Configuration" = Enabled with UEFI lock
```

**3. 네트워크 세분화 (Lateral Movement 방지)**

```plain text
# PowerShell: 방
```

---

**출처**: [https://news.hada.io/topic?id=28594](https://news.hada.io/topic?id=28594)