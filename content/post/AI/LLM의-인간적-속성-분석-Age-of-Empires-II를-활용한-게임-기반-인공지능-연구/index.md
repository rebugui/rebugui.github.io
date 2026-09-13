---
title: "LLM의 인간적 속성 분석: Age of Empires II를 활용한 게임 기반 인공지능 연구"
date: 2026-06-08T12:10:20+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
---

## 서론: 언어 이해를 넘어선 '행동'의 영역으로

최근 대규모 언어 모델(LLMs)은 인간이 작성한 텍스트를 놀라울 정도로 유창하게 생성하며, 복잡한 추론과 지식 검색 능력을 입증했습니다. 마치 인간처럼 사고하고 말하는 것처럼 보입니다. 하지만 이러한 능력은 주로 **언어적 패턴 인식**에 기반을 두고 있습니다. 만약 우리가 LLM의 진정한 '지능' 수준을 측정하고자 한다면, 단순히 얼마나 논리적인 글을 쓰는지 묻는 것만으로는 부족합니다.

진정한 지능이란, 주어진 제약 조건(Constraint) 하에서 목표를 달성하기 위해 일련의 복잡한 행동 계획(Action Plan)을 수립하고 실행하는 능력입니다. 마치 전략 시뮬레이션 게임과 같이, 자원 관리, 시간적 제약, 그리고 상대방과의 상호작용이 필수적인 환경이 필요합니다.

본 논문에서 다루는 Age of Empires II와 같은 게임 기반 연구는 바로 이 간극을 메우고자 합니다. LLM의 의사결정 과정을 단순히 텍스트 생성으로 국한하지 않고, 자원 수집, 유닛 배치, 공격 타이밍 결정과 같은 **복잡하고 실시간적인 행동 공간(Action Space)**에 투입함으로써, LLMs가 과연 '인간적 속성'이라 불리는 목표 지향적이고 제약 조건을 따르는 계획 능력을 갖추었는지 근본적으로 검증하는 것이 핵심 동기입니다.

## 본론: 게임 환경을 활용한 LLM의 행동 추론 메커니즘 분석

전통적인 NLP 모델은 입력(프롬프트)과 출력(응답 텍스트) 사이의 통계적 관계를 학습합니다. 그러나 전략 시뮬레이션 게임 AI는 **상태(State)** $\rightarrow$ **행동(Action)** $\rightarrow$ **새로운 상태(Next State)**라는 순환적인 피드백 루프를 따릅니다. LLM을 이러한 환경에 적용하려면, 모델이 언어적 추론 능력을 넘어 '게임 엔진의 API'와 상호작용할 수 있는 구조가 필요합니다.

### 1. 기술적 원리: 상태 인식 및 행동 공간 매핑

LLM을 게임 AI로 활용하는 과정은 크게 세 단계의 정보 변환 과정을 거칩니다.

**A. 상태 인코딩 (State Encoding):** 게임 엔진에서 발생하는 모든 정보(지도 좌표, 현재 자원량, 유닛 체력, 적군의 위치 등)는 이산적이고 구조화된 데이터입니다. LLM은 이 복잡한 비정형 데이터를 받아들여, 자신이 이해할 수 있는 **의미론적 상태 벡터**로 변환해야 합니다.

**B. 계획 및 추론 (Planning & Reasoning):** LLM은 '지금 자원이 부족하니 농장을 지어야 한다'와 같은 고수준 목표(High-Level Goal)를 설정하고, 이를 달성하기 위한 순차적인 행동 목록을 생성합니다. 이는 단순한 텍스트가 아니라 **구조화된 명령(Structured Command)**의 형태여야 합니다.

**C. 액션 디코딩 (Action Decoding):** 최종적으로 LLM은 "유닛 A를 좌표 (X, Y)로 이동시키고, 자원 B를 수집한다"와 같은 명확한 API 호출 형식으로 행동을 출력합니다. 이 과정이 성공해야만 게임 엔진이 다음 상태 변화를 계산할 수 있습니다.

**Mermaid 다이어그램: LLM 기반 에이전트의 의사결정 루프**

```javascript
graph TD
    A["환경 관찰 (Observation)"] --> B(상태 인코딩 및 파싱);
    B --> C{LLM 추론 엔진};
    C -- 목표 설정/계획 수립 --> D[구조화된 행동 명령 생성];
    D --> E["게임 엔진 실행 (Action)"];
    E --> F["새로운 환경 상태 (Next State)"];
    F --> A;
```

### 2. LLM 기반 게임 AI와 기존 접근 방식 비교 분석

| 비교 항목 | 전통적인 NLP 모델 (GPT-4 등) | 강화학습 (RL) 에이전트 (AlphaGo 등) | LLM-Game AI 하이브리드 |
| :--- | :--- | :--- | :--- |
| **주요 학습 방식** | Next Token Prediction (통계적 패턴) | Reward Maximization (최적화된 보상) | Prompting + RL/Planning (추론 기반 계획) |
| **강점** | 언어의 유창성, 광범위한 지식 활용 | 특정 환경에서의 최적 전략 수립 능력 | 고수준 목표 설정 및 복잡한 의사결정 설명 가능성 |
| **약점** | 행동 공간 부재, 제약 조건 무시 경향 | 데이터 효율성이 낮고, 계획의 '설명'이 어려움 (Black Box) | 모델 크기/복잡도에 따른 추론 지연 및 구조화 난이도 |

LLM-Game AI는 RL의 강력한 최적화 능력과 LLM의 뛰어난 고수준 추론 능력을 결합하려는 시도로 해석할 수 있습니다. 즉, "어떤 전략을 취해야 하는가?"라는 질문에 대해 LLM이 인간적인 논리로 답하고, "그 전략을 어떻게 실행하는가?"라는 문제에 대해서는 RL 또는 명시적 규칙 기반 시스템(Rule-Based System)이 보완하는 방식입니다.

### 3. 구현 가이드: Python 개념 예시 (Action Space Handling)

LLM에게 게임 환경의 행동 공간을 이해시키기 위해서는, 단순히 "공격하라"가 아니라 **함수 호출 형태**로 명령을 구조화하도록 유도해야 합니다. 다음은 PyTorch 기반 에이전트가 상태를 파싱하고 액션을 생성하는 개념적인 예시입니다.

```python
# 개념 설명용 코드: LLM Agent의 Action Generation 로직
import json

def parse_llm_action(raw_output: str, current_state: dict) -> list:
    """LLM이 생성한 텍스트 출력을 구조화된 행동 리스트로 파싱합니다."""
    try:
        # LLM에게 JSON 형식으로 출력하도록 프롬프팅하는 것이 핵심입니다.
        action_json = json.loads(raw_output)
        actions = []

        for action in action_json['actions']:
            if action['type'] == 'MOVE' and 'unit_id' in action:
                # 유효성 검사 (예: 이동 가능한지, 목표 지점이 지도 경계 내인지)
                if current_state['units'][action['unit_id']]['hp'] > 0:
                    actions.append({
                        "command": "MOVE",
                        "unit_id": action['unit_id'],
                        "target_coord": (action['x'], action['y'])
                    })
            # 다른 행동 타입 추가 가능 (BUILD, ATTACK 등)

        return actions
    except json.JSONDecodeError:
        print("Warning: LLM output failed JSON parsing.")
        return []

# 예시 사용:
# state = {"resources": 500, "units": {...}}
# llm_output = '{"actions": [{"type": "MOVE", "unit_id": 1, "x": 10, "y": 20}]}'
# valid_actions = parse_llm_action(llm_output, state)
```

### 4. Step-by-step: LLM 기반 전략 수립 프로세스

실제 연구에서 이 시스템을 구현하는 단계는 다음과 같습니다.

**Step 1: 환경 정의 및 상태 벡터화 (State Definition):** 게임 엔진의 핵심 데이터를 추출하고, 이를 LLM이 처리할 수 있는 일관된 포맷(예: CSV 또는 JSON)으로 변환합니다. **Step 2: 목표 설정 프롬프팅 (Goal Prompting):** "현재 자원 상황과 적군의 움직임을 고려했을 때, 승리를 위한 최우선 목표는 무엇인가?"와 같은 고수준의 질문을 던져 LLM이 전략적 사고를 하도록 유도합니다. **Step 3: 행동 계획 생성 및 검증 (Planning & Validation):** LLM이 출력한 명령(예: `MOVE`, `BUILD`)을 받아, 게임 엔진의 규칙에 위배되는지(`Out of Bounds` 또는 `Insufficient Resources`) 검사하는 필터링 레이어를 거칩니다. **Step 4: 실행 및 피드백 (Execution & Feedback):** 유효성이 확인된 행동만 게임 엔진에 전달하여 실제 상태 변화를 일으키고, 이 새로운 상태가 다시 Step 1로 돌아와 루프를 완성합니다.

## 결론: LLM을 '계획자'로서 재정의하다

Age of Empires II와 같은 복잡한 시뮬레이션 환경을 활용하는 연구는 LLMs에게 단순한 언어 모델 이상의 역할을 요구합니다. 이는 LLMs가 단순히 **정보를 처리하는 주체**를 넘어, **환경과 상호작용하며 목표를 달성하는 '계획자(Planner)'이자 '행동 설계자(Action Designer)'**로 진화해야 함을 시사합니다.

이러한 게임 기반 AI 연구는 LLM의 잠재력을 검증할 수 있는 중요한 벤치마크가 됩니다. 앞으로의 연구 방향은 단순히 LLM의 추론 능력을 테스트하는 것을 넘어, 어떻게 하면 LLM의 논리적 사고를 강화학습의 최적화 메커니즘과 결합하여, 현실 세계의 제약 조건 하에서도 가장 효율적인 '행동'을 도출해낼 수 있을지에 초점을 맞추게 될 것입니다.

이러한 연구는 AI가 단순히 인간의 지식을 모방하는 것을 넘어, 인간처럼 목적을 가지고 환경에 적극적으로 개입할 수 있는 **범용 인공지능(AGI)**으로 나아가는 중요한 이정표를 제시합니다.

--- **참고 자료:**
- [LLMs Have Human-Like Attributes, Then So Does Age of Empires II](https://arxiv.org/abs/2605.31514)

---

**출처**: [https://arxiv.org/abs/2605.31514](https://arxiv.org/abs/2605.31514)