---
title: "CT-GMARL: Sim2Real 갭을 극복하는 다중 에이전트 자율 사이버 방어"
date: 2026-05-01T01:06:55+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 서론

새벽 3시, SOC(Security Operations Center)의 스크린이 붉게 물들었다. 랜섬웨어가 내부 망으로 확산 중이다. 당신은 수십 개의 SIEM 알림을 보며 방화벽 규칙 수정, 네트워크 분리, 악성 프로세스 종료 중 어떤 조치를 먼저 취해야 할지 결정해야 한다. 이 복잡한 의사결정을 자동화하기 위해 다중 에이전트 강화학습(MARL)을 도입했다. 시뮬레이션에서는 완벽했다. 그러나 실전 투입 첫날, 에이전트는 멈췄다.

실제 네트워크 텔레메트리는 깔끔한 벡터가 아니다. 비동기적이고, 노이즈가 끼어 있으며, 불규칙한 시간 간격으로 쏟아진다. 시뮬레이터가 동기식 틱(tick)과 정제된 상태 벡터에 맞춰 훈련된 정책은 현실의 혼돈 앞에서 무용지물이 된다. 이것이 MARL 기반 사이버 방어가 학계를 벗어나지 못하는 근본 원인, **Sim2Real 갭**이다.

이 글에서는 이 격차를 해결하는 NetForge_RL 프레임워크와 그 핵심 알고리즘인 CT-GMARL을 분석한다. Neural ODE를 활용해 불규칙한 시간 간격의 데이터를 처리하는 원리, "Scorched earth" 현상을 어떻게 방지하는지, 그리고 실제 Docker 환경으로의 Zero-shot 전이 성공 사례를 다룬다.
> **⚠️ 윤리적 경고**: 본 글에서 다루는 모든 공격 시나리오와 코드는 사이버 방어 역량 강화를 목적으로 작성되었습니다. 오직 승인된 테스트 환경에서만 활용하십시오.

## 본론: Sim2Real 갭의 본질과 CT-GMARL의 해결책

### 시뮬레이션이 현실을 왜곡하는 방식

기존 사이버 방어 시뮬레이터의 치명적인 문제는 네트워크 프로토콜의 물리적 특성을 추상화한다는 점이다. 실제 네트워크에서는 패킷 손실, 지연, 순서 바뀜이 발생한다. SIEM 로그는 초단위로 들어오지 않고 불규칙하게 스트리밍된다. 하지만 기존 시뮬레이터는 이를 동기식 디스크리트 타임스텝으로 단순화한다.

```javascript
graph TD
    A[실전 네트워크 환경] --> B[비동기적 이벤트]
    A --> C[불규칙한 샘플링]
    A --> D[노이즈 포함 텔레메트리]
    B --> E[기존 시뮬레이터]
    C --> E
    D --> E
    E --> F[동기식 틱]
    E --> G[정제된 상태 벡터]
    E --> H[프로토콜 추상화]
    F --> I[훈련된 MARL 정책]
    G --> I
    H --> I
    I --> J[실전 투입]
    J --> K[성능 붕괴]
```

이 문제는 단순히 "시뮬레이터를 더 정교하게 만들면 해결된다"는 수준이 아니다. 근본적으로 MDP(Markov Decision Process)의 가정 자체가 깨진다. 실전에서는 상태가 연속적이고, 관측은 부분적이며, 행동과 결과 사이의 시간 간격이 일정하지 않다. 이를 **POSMDP**(Partially Observable Semi-Markov Decision Process)라고 부른다.

### POSMDP: 현실을 반영한 의사결정 모델

Semi-Markov Decision Process는 전통적 MDP에서 시간 간격이 고정되어 있다는 가정을 제거한 모델이다. 사이버 방어 관점에서 이것이 의미하는 바는 명확하다.

| 특성 | 기존 MDP 가정 | 실전 POSMDP |
| :--- | :--- | :--- |
| 시간 간격 | 고정 (Δt = 1) | 가변 (Δt ∈ [0.1, 60]초) |
| 상태 관측 | 완전 관측 가능 | 부분 관측 (PO-MDP) |
| 이벤트 발생 | 동기식 틱 | 비동기적 이벤트 드리븐 |
| 텔레메트리 | 정제된 벡터 | NLP 인코딩된 SIEM 로그 |
| 네트워크 모델 | 이진 연결 그래프 | ZTNA 제약 포함 토폴로지 |

NetForge_RL은 이 POSMDP를 기본 모델로 채택한다. 방어 에이전트는 더 이상 정해진 틱마다 의사결정하지 않는다. 이벤트가 발생했을 때, 그리고 그 이후의 불규칙한 시간 간격 동안 상태를 추론하며 의사결정한다.

### Neural ODE: 불규칙한 시간 간격의 수학적 처리

CT-GMARL의 핵심 혁신은 **Neural Ordinary Differential Equations(ODE)**를 활용해 비동기적 이벤트를 처리하는 것이다. 전통적 RNN이나 Transformer는 고정된 시간 간격의 입력을 가정한다. Neural ODE는 연속시간 모델이므로 불규칙한 샘플링 간격을 자연스럽게 처리한다.

```python
import torch
import torch.nn as nn
from torchdiffeq import odeint

class NeuralODECell(nn.Module):
    """
    CT-GMARL의 핵심 구성요소
    불규칙한 시간 간격으로 들어오는 네트워크 텔레메트리를 
    연속시간으로 모델링하는 Neural ODE
    """
    def __init__(self, hidden_dim: int, telemetry_dim: int):
        super().__init__()
        self.hidden_dim = hidden_dim
        
        # ODE 함수 네트워크: dh/dt = f(h, t)
        self.ode_func = nn.Sequential(
            nn.Linear(hidden_dim + telemetry_dim, 128),
            nn.Tanh(),
            nn.Linear(128, 128),
            nn.Tanh(),
            nn.Linear(128, hidden_dim)
        )
        
        # 관측 인코더 (SIEM 텔레메트리 -> 잠재 공간)
        self.obs_encoder = nn.Linear(telemetry_dim, hidden_dim)
    
    def forward(self, h_prev: torch.Tensor, obs: torch.Tensor, 
                dt: torch.Tensor) -> torch.Tensor:
        """
        Args:
            h_prev: 이전 은닉 상태 [batch, hidden_dim]
            obs: 새로운 SIEM 관측 [batch, telemetry_dim]
            dt: 이전 이벤트로부터의 경과 시간 [batch, 1]
        Returns:
            h_new: 업데이트된 은닉 상태 [batch, hidden_dim]
        """
        # 관측값 인코딩
        obs_encoded = self.obs_encoder(obs)
        
        # ODE 정의: h의 시간에 따른 변화율
        def ode_derivative(t, h):
            combined = torch.cat([h, obs_encoded], dim=-1)
            return self.ode_func(combined)
        
        # dt만큼 시간 전파 (고정 스텝 ODE 솔버)
        # 실제 구현에서는 RK4 등 사용
        h_new = h_prev + dt * ode_derivative(0, h_prev)
        
        return h_new

# 실제 사용 예시
batch_size = 4
hidden_dim = 64
telemetry_dim = 32

cell = NeuralODECell(hidden_dim, telemetry_dim)

# 불규칙한 시간 간격의 이벤트 시뮬레이션
h = torch.randn(batch_size, hidden_dim)  # 초기 은닉 상태

# 에이전트 1: 0.3초 후 침입 탐지 알림
dt_1 = torch.tensor([[0.3], [0.3], [0.3], [0.3]])
obs_1 = torch.randn(batch_size, telemetry_dim)
h = cell(h, obs_1, dt_1)

# 에이전트 2: 12.7초 후 악성 행위 탐지
dt_2 = torch.tensor([[12.7], [12.7], [12.7], [12.7]])
obs_2 = torch.randn(batch_size, telemetry_dim)
h = cell(h, obs_2, dt_2)

```

```python
print(f"업데이트된 은닉 상태 shape: {h.shape}")
```

이 코드에서 핵심은 `dt` 매개변수다. 실전에서는 이벤트 간격이 0.1초일 수도, 60초일 수도 있다. Neural ODE는 이 시간 간격을 미분방정식의 적분 구간으로 사용해 자연스럽게 처리한다.

### NetForge_RL의 듀얼 모드 엔진

NetForge_RL은 훈련과 평가를 위한 두 가지 모드를 제공한다. 이것이 Sim2Real 브릿지의 핵심이다.

```javascript
graph LR
    A[MARL 에이전트] --> B[Mock Hypervisor]
    A --> C[Docker Hypervisor]
    B --> D[고속 훈련 모드]
    C --> E[실전 평가 모드]
    D --> F[대규모 에피소드]
    E --> G[실제 익스플로잇]
    F --> H[Zero-shot 전이]
    H --> E
```

Mock Hypervisor는 실제 컨테이너를 띄우지 않고 네트워크 토폴로지와 프로토콜 동작을 시뮬레이션한다. 초당 수천 에피소드를 실행할 수 있다. Docker Hypervisor는 실제 컨테이너 기반 네트워크를 구축하고 실제 익스플로잇을 실행한다. 핵심은 두 환경 간에 동일한 관측 공간과 행동 공간을 유지한다는 점이다.

### Scorched Earth: 과잉 방어의 치명적 함정

기존 MARL 알고리즘(R-MAPPO, QMIX)이 빠지는 가장 위험한 함정이 있다. 바로 **"Scorched Earth(전술한)" 현상**이다.

방어 에이전트의 보상 함수가 "위험 최소화"에만 초점을 맞추면, 에이전트는 가장 확실한 방어 전략을 선택한다. **네트워크를 완전히 분리하는 것.** 모든 포트를 닫고, 모든 서비스를 중지하면 침입자도 들어올 수 없다. 방어 목표는 달성했지만, 조직은 마비된다.

```python
# Scorched Earth 문제를 보여주는 보상 함수 비교

def naive_reward_function(network_state, agent_action):
    """위험만 최소화하는 단순 보상 함수"""
    risk_score = calculate_risk(network_state)
    
    # 위험이 낮으면 보상
    if risk_score < 0.1:
        return +100
    
    # 네트워크 가용성은 고려하지 않음!
    return -risk_score * 100

def balanced_reward_function(network_state, agent_action):
    """CT-GMARL 방식의 균형 잡힌 보상 함수"""
    risk_score = calculate_risk(network_state)
    availability = calculate_availability(network_state)
    
    # 가용성이 낮으면 큰 페널티
    availability_penalty = 0.0
    if availability < 0.7:
        availability_penalty = (0.7 - availability) * 200
    
    # 장애 복구 보너스
    recovery_bonus = count_restored_services(agent_action) * 50
    
    # 위험 감소 보너스
    risk_reduction = previous_risk - risk_score
    risk_bonus = risk_reduction * 80 if risk_reduction > 0 else 0
    
    total_reward = (risk_bonus + recovery_bonus 
                    - availability_penalty - risk_score * 30)
    
    return total_reward
```

CT-GMARL은 이 문제를 근본적으로 해결한다. 연속시간 모델링 덕분에 에이전트는 "기다렸다가 정밀하게 대응"하는 전략을 학습한다. 불필요하게 네트워크를 분리하지 않고, 침해된 서비스만 선별적으로 복구한다.

### CT-GMARL 성능 검증: 실험 결과

연구진의 실험 결과는 인상적이다. 세 가지 주요 지표에서 기존 알고리즘을 압도한다.

| 평가 지표 | QMIX | R-MAPPO | CT-GMARL | 개선율 |
| :--- | :--- | :--- | :--- | :--- |
| 수렴 중간 보상 | 27,208 | 28,567 | 57,135 | 2.0x / 2.1x |
| 복구된 서비스 수 | 1.2 | 1.4 | 16.8 | 12.0x |
| Zero-shot 보상 | - | - | 98,026 | 실측값 |
| Scorched Earth 발생률 | 73% | 68% | 0% | 근절 |

특히 주목할 점은 Zero-shot 전이 결과다. Mock Hypervisor에서 훈련한 정책을 Docker Hypervisor에 그대로 적용했을 때, 오히려 더 높은 보상(98,026 vs 57,135)을 기록했다. 이는 시뮬레이션 환경이 실전의 복잡성을 충분히 반영하면서도, 실전 환경의 명확한 피드백 신호가 에이전트 성능을 더 끌어올렸음을 의미한다.

### Step-by-Step: NetForge_RL 환경 구축 가이드

실제 환경에서 NetForge_RL 기반 방어 시스템을 구축하는 과정을 단계별로 살펴보자.

**Step 1: 네트워크 토폴로지 정의**

```python
network_config = {
    "subnets": [
        {"name": "DMZ", "hosts": ["web_server", "mail_gateway"],
         "ztna_policy": "restricted"},
        {"name": "INTERNAL", "hosts": ["db_server", "app_server", "file_server"],
         "ztna
```

---

**출처**: [http://arxiv.org/abs/2604.09523v1](http://arxiv.org/abs/2604.09523v1)