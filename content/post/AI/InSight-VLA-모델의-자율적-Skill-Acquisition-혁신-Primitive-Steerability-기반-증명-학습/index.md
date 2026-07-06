---
title: "InSight: VLA 모델의 자율적 Skill Acquisition 혁신, Primitive Steerability 기반 증명 학습"
date: 2026-07-06T16:29:16+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
---

## 서론

현대 인공지능 연구의 최전선에 있는 Vision-Language-Action (VLA) 모델은 로봇 공학 분야에서 혁명적인 발전을 이끌고 있습니다. VLA는 시각 정보(Vision), 언어적 명령(Language), 그리고 실제 행동(Action)을 통합하여, "컵을 집어서 테이블 위에 놓아라"와 같은 복합적인 작업을 수행할 수 있게 합니다. 그러나 현재의 VLA 모델들이 직면한 가장 근본적인 한계점은 바로 **데이터 의존성(Data Boundedness)**입니다. 즉, 모델이 학습 데이터셋에서 본 스킬 범위 내에서만 작동하며, 훈련 과정에서 명시적으로 시연되지 않은 새로운 환경이나 복잡한 미션을 수행할 때 성능이 급격히 저하되는 경향을 보입니다.

실제 산업 현장에서는 로봇이 예측 불가능한 변수(예: 물체의 위치 변화, 예상치 못한 장애물)를 만나거나, 기존에 알려지지 않은 새로운 작업을 지시받는 경우가 빈번합니다. 이러한 상황에서 VLA가 '자율적으로' 필요한 스킬을 스스로 찾아내고 학습할 수 있다면, 이는 로봇 시스템의 활용 범위를 비약적으로 확장시키는 핵심 동력이 될 것입니다. 본 글에서는 arXiv에 발표된 InSight 프레임워크를 깊이 있게 분석하며, 어떻게 VLA 모델을 원시 행동(Primitive Action) 수준에서 'Steerable'하게 만들어 이러한 자율적 스킬 획득을 가능하게 했는지 그 메커니즘과 실무적 함의를 탐구하고자 합니다.

## 본론: Primitive Steerability와 InSight 프레임워크 분석

### 1. 원시 행동(Primitive Action)으로의 전환: 왜 'Steerable'해야 하는가?

기존 VLA 모델은 보통 고수준(High-level) 명령, 예를 들어 "Block Flip"이나 "Pouring"과 같은 전체 태스크를 하나의 단위로 학습합니다. 하지만 이러한 고수준 스킬들은 내부적으로 수많은 저수준의 원시 행동들("gripper to bowl", "lift upward", "rotate 45 degrees")이 조합되어 이루어집니다. InSight는 VLA가 이 **원시 행동 수준**에서 'Steerable'하게 작동할 수 있도록 설계했습니다.

이는 마치 운전자가 최종 목적지(High-level)만 지정하는 것이 아니라, "왼쪽으로 살짝 꺾고 (Primitive A), 가속하고 (Primitive B), 오른쪽으로 미세 조정하라 (Primitive C)"와 같이 중간 단계의 행동을 직접 조절하며 목표에 도달하도록 유도하는 것과 같습니다. 이 원시 행동 수준에서의 제어 가능성 덕분에, 모델은 기존 데이터셋에 없던 새로운 조합이나 변형된 작업을 훨씬 유연하게 처리할 수 있게 됩니다.

다음 다이어그램은 InSight가 추구하는 Primitive Steerability의 개념적 흐름을 보여줍니다.

```javascript
graph TD
    A[High-Level Task: Pouring] --> B{VLA Policy};
    B --> C1[Primitive A: Move Gripper to Bottle];
    B --> C2[Primitive B: Lift Upward];
    B --> C3[Primitive C: Tilt/Pour Action];
    C1 & C2 & C3 --> D[End-Effector Pose / State Change];
```

### 2. InSight의 핵심 메커니즘: VLM-Guided Data Flywheel

InSight 프레임워크는 두 가지 주요 단계로 구성되어 있으며, 이들이 순환하며 새로운 지식을 끊임없이 생성하고 학습 세트에 통합하는 '데이터 플라이휠(Data Flywheel)'을 형성합니다.

#### Step 1: 자동화된 Primitive 분할 (Segmentation Pipeline) VLA가 시연(Demonstration) 데이터를 받으면, InSight는 이를 무작위의 행동 시퀀스로 취급하지 않습니다. 대신, **Vision-Language Model (VLM)**이 이 시연을 분석하여 태스크를 논리적인 계획(Plan Decomposition)으로 분해합니다. VLM은 해당 액션 시점의 엔드-이펙터 포즈와 결합된 언어적 설명을 통해 각 행동 세그먼트를 명확한 원시 행동 단위로 레이블링 합니다.
- **기술적 깊이**: 이 단계는 단순히 클러스터링하는 것이 아니라, VLM이 "다음 목표(Goal)"를 예측하고 그 목표에 도달하기 위한 가장 최소화된 '행동 조각'을 식별해낸다는 점에서 강력합니다.

#### Step 2: 누락 Primitive 식별 및 자율 시연 (Data Flywheel) 새로운 태스크($T_{novel}$)가 주어졌을 때, InSight는 VLM에게 해당 태스크를 완수하는 데 **필요한 필수 원시 행동(Missing Primitives)**이 무엇인지 질의합니다. 만약 학습 데이터셋에 이 Primitive가 없다면, 시스템은 다음 과정을 자율적으로 수행합니다:

1.  **Primitive 제안**: VLM이 "Block을 들어 올리는 (Lift Block)" Primitive가 필요하다고 판단합니다.
2.  **자율 시연 생성**: InSight는 VLM이 제안한 저수준 컨트롤(Low-level Control) 파라미터를 사용하여 로봇에 명령을 내리고, 해당 Primitive를 실행해 봅니다.
3.  **통합 및 학습**: 성공적으로 수행된 이 새로운 시연은 자동으로 레이블링되고, 기존의 VLA 학습 세트에 통합되어 모델이 즉시 활용할 수 있게 됩니다.

### 3. 실무 적용: 성능 비교 및 코드 예시

InSight를 통해 습득된 Primitive는 복잡하고 장기적인 태스크(Long-horizon Tasks)를 수행하는 데 사용됩니다. 다음 표는 InSight가 제공하는 자율 학습 능력과 기존 VLA의 한계를 비교한 것입니다.

| 비교 항목 | 기존 VLA (고수준 기반) | InSight (Primitive Steerable) |
| :--- | :--- | :--- |
| **학습 범위** | 훈련 데이터에 명시된 스킬로 제한됨 | 새로운 환경에서 자율적으로 확장 가능 |
| **새로운 태스크 대응** | 시연이 필요하거나, 성능 저하 발생 | 누락 Primitive를 스스로 찾아 학습 후 수행 |
| **제어 수준** | Task-level (전체 행동) | Primitive-level (원시 단위 조절) |
| **장기 작업 능력** | 중간 복잡도까지는 우수하나 조합에 취약 | 원시 행동의 유연한 조합을 통해 높은 성공률 보장 |

#### 개념 설명용 코드 예시: Primitive Action 정의 및 VLM 추론

다음은 PyTorch 기반 환경에서 InSight가 사용하는 'Primitive'를 어떻게 정의하고, VLM이 이를 활용하여 다음 액션을 결정하는지 보여주는 개념적 예시입니다.

```python
import torch
from transformers import AutoModelForCausalLM # VLM 사용 가정

# 1. Primitive Action Space Definition (예: 7가지 원시 행동)
PRIMITIVE_ACTIONS = {
    0: "MoveToTarget",      # 목표 지점으로 이동
    1: "LiftUpward",        # 위로 들어 올림
    2: "TiltPour",          # 기울여 따르기/밀어내기
    3: "GraspObject",      # 물체 잡기
    4: "RotateAxis",       # 특정 축 회전
    5: "ReleaseGripper",   # 그리퍼 해제
    6: "SweepPath"         # 지정된 경로를 쓸기
}

class VLA_InSightPolicy(torch.nn.Module):
    def __init__(self, vlm_model):
        super().__init__()
        self.vlm = vlm_model # 사전 학습된 Vision-Language Model (예: CLIP + LLM)

    # 2. VLM이 현재 상태와 목표를 기반으로 다음 Primitive를 추론하는 함수
    def predict_next_primitive(self, observation: torch.Tensor, goal_description: str):
        # Observation: [시각 피처, 로봇 관절 각도 등]
        # Goal Description: "컵을 들고 테이블 중앙에 놓아라."

        # VLM에게 현재 상태와 목표를 입력하여 다음 행동의 '언어적 설명'을 요청
        prompt = f"Current State Observation. Goal: {goal_description}. Next essential primitive is:"
        
        # (실제로는 VLM 추론 과정이 복잡하게 들어감)
        vlm_output = self.vlm(observation, prompt).logits

        # 출력된 토큰 중 Primitive Action에 해당하는 ID를 찾아 반환
        predicted_action_id = torch.argmax(vlm_output[-1]).item()
        
        return PRIMITIVE_ACTIONS[predicted_action_id]

# 사용 예시: 
# policy = VLA_InSightPolicy(vlm_model)
# next_primitive = policy.predict_next_primitive(current_state, "Block을 들어서 오른쪽으로 옮겨라.")
# print(f"VLM이 예측한 다음 원시 행동: {next_primitive}") 
```

## 결론

InSight 프레임워크는 VLA 모델의 자율적 스킬 획득이라는 난제를 **원시 행동 수준에서의 제어 가능성 (Primitive Steerability)**을 통해 성공적으로 해결했습니다. 이는 단순히 더 많은 데이터를 넣어 학습시키는 것을 넘어, 모델이 스스로 '무엇이 부족한지' 인지하고, 그 부족분을 '스스로 시연하여 채워 넣는' 능동적인 메커니즘(Data Flywheel)을 구축했다는 점에서 학술적/실용적으로 매우 큰 의미를 가집니다.

InSight의 핵심 성과는 VLA가 더 이상 수동 시연에 종속되지 않고, 복잡하고 장기적인 태스크 환경에서 **지속적인 스킬 획득(Continual Skill Acquisition)**을 수행할 수 있는 실질적인 기반을 마련했다는 점입니다. 이는 로봇이 인간의 개입 없이도 새로운 미션에 적응하는 '진정한 자율성'으로 나아가는 결정적인 이정표라 할 수 있습니다.

**💡 전문가 인사이트:** InSight와 같은 프레임워크는 VLA가 단순한 패턴 인식 기계를 넘어, 마치 인간처럼 목표를 설정하고 → 현재 상태를 분석하며 → 필요한 도구(Primitive)를 찾아내고 → 실행하는 **계획-실행 루프(Plan-Execute Loop)**를 자체적으로 돌릴 수 있게 했음을 의미합니다. 앞으로의 연구는 이 Primitive Action Space를 어떻게 더 효율적이고 일반화되게 설계할 것인지에 초점을 맞출 것입니다.

--- **참고 자료:**
- InSight: Self-Guided Skill Acquisition via Steerable VLAs (arXiv) - [http://arxiv.org/abs/2606.24884v1](http://arxiv.org/abs/2606.24884v1)

---

**출처**: [http://arxiv.org/abs/2606.24884v1](http://arxiv.org/abs/2606.24884v1)