---
title: "Skillify: AI Agent 실패를 영구적 구조 수정으로 전환하는 방법론"
date: 2026-04-30T01:07:31+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
---

## 서론

LLM 기반 에이전트를 실제 프로덕션 환경에 배포한 경험이 있다면, 불면의 밤을 보낸 적이 있을 것입니다. 개발 단계에서 완벽하게 작동하던 에이전트가, 실제 사용자의 예기치 못한 입력(LangChain의 창립자 Harrison Chase가 언급한 'Edge Case'의 폭발) 앞에서 망가지는 경험은 흔합니다. 이때 단순히 시스템 프롬프트에 "이렇게 하지 마"라고 추가하는 것은 임시방편일 뿐이며, 다른 입력에서 또다시 실패할 가능성을 내재하고 있습니다.

Y Combinator의 대표 Garry Tan이 제안한 'Skillify'는 이러한 **확률적 실패(Stochastic Failure)를 결정론적 성공(Deterministic Success)으로 치환하는 철학이자 방법론**입니다. 현재 LangChain과 같은 프레임워크가 강력한 도구를 제공하지만, "무엇을 테스트하고 어떻게 개선할 것인가"에 대한 구체적인 워크플로우는 여전히 개발자의 몫으로 남아 있습니다. 이 글에서는 단순한 디버깅을 넘어, 에이전트의 실패를 '새로운 기능(Skill)의 탄생' 기회로 활용하여 시스템을 지속적으로 진화시키는 Skillify 방법론의 기술적 메커니즘과 실무 적용 가이드를 다룹니다.

## 본론

### 1. Skillify의 기술적 원리: 실패의 구조화

AI 에이전트의 실패는 크게 두 가지로 분류됩니다: 추론 오류(Reasoning Error)와 지식 부족(Lack of Knowledge). 전통적인 소프트웨어 개발에서는 버그가 발생하면 코드를 수정합니다. 하지만 LLM 에이전트에서는 '코드'가 모델의 가중치와 프롬프트로 분산되어 있어 버그의 위치를 특정하기 어렵습니다.

Skillify 방법론은 이를 **"실패 케이스를 고품질의 학습 데이터 또는 테스트 케이스로 전환하여, 모델의 행동 공간(Action Space)을 제약하는 구조적 수정"**으로 정의합니다. 이는 단순히 모델에게 답을 가르치는 것이 아니라, 특정 상황에서 에이전트가 취해야 할 행동을 '스킬(Skill)'이라는 단위로 고정화하는 과정입니다. 예를 들어, 에이전트가 특정 API 호출 방식을 몰라 실패했다면, 이를 프롬프트 내의 Few-shot Example이나 별도의 Python 함수(Tool)로 구조화하여 영구적으로 해결합니다.

### 2. Skillify 루프: 실패로부터의 순환

Skillify는 단발성 수정이 아니라 지속적인 개선 사이클입니다. 아래 다이어그램은 에이전트의 실패가 시스템의 구조적 개선으로 이어지는 피드백 루프를 시각화한 것입니다.

```javascript
graph TD
    A[User Input] --> B[Agent Execution]
    B --> C{Result Check}
    C -->|Success| D[Deliver Output]
    C -->|Failure| E[Log Failure Context]
    E --> F[Root Cause Analysis]
    F --> G{Type?}
    G -->|Reasoning Error| H[Add Few-shot Example]
    G -->|Knowledge Gap| I[Create/Update Tool]
    G -->|Ambiguity| J[Refine System Prompt]
    H --> K[Register New Skill]
    I --> K
    J --> K
    K --> L[Run Regression Tests]
    L --> M[Deploy Improved Agent]
```

이 다이어그램은 실패가 발생했을 때 단순히 로그만 남기는 것이 아니라, 그 원인을 분석하여 시스템의 구조(Component, Prompt, Tool)를 변경하고, 이를 다시 테스트함으로써 같은 실패가 재발하지 않도록 막는 '면역 체계'를 구축함을 보여줍니다.

### 3. LangChain을 활용한 구현 및 테스트 전략

LangChain은 테스트를 위한 `LangSmith`나 단위 테스트 도구를 제공하지만, 개발자는 이를 능동적으로 워크플로우에 통합해야 합니다. 아래는 에이전트의 계산 능력 부족을 발견했을 때, 이를 Python Tool로 스킬화하고 테스트하는 과정의 예시입니다.

#### 3.1 실패 시나리오 및 스킬 구현 (Python)

가령 에이전트가 "125의 제곱근"을 물어봤을 때 토큰 생성 방식의 한계로 부정확한 값을 도출하는 경우가 있습니다. 이를 해결하기 위해 `Calculator` 툴을 연결하는 '스킬'을 추가합니다.

```python
from langchain.agents import initialize_agent, Tool, AgentType
from langchain.llms import OpenAI
import math

# 1. 실패 원인 해결을 위한 툴(스킬) 정의
def calculator(input_str):
    """복잡한 수식을 계산하는 스킬입니다."""
    try:
        return str(eval(input_str))
    except:
        return "계산할 수 없습니다."

# 2. 에이전트에게 제공할 툴 리스트 구성
tools = [
    Tool(
        name="Calculator",
        func=calculator,
        description="수학 계산이 필요할 때 사용됩니다. 예: '125의 제곱근' 또는 '12 * 5'"
    )
]

# 3. LangChain 에이전트 초기화
llm = OpenAI(temperature=0)
agent = initialize_agent(
    tools, 
    llm, 
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, 
    verbose=True
)

# 실행 테스트
response = agent.run("125의 제곱근은 얼마야?")
print(response)
```

#### 3.2 회귀 테스트 (Regression Test)

스킬을 추가한 후, 이전에 실패했던 입력이 이제는 성공하는지 확인하는 테스트 케이스를 작성해야 합니다. 이것이 Skillify의 핵심입니다. 실패를 '영구적인 수정'으로 바꾸는 과정입니다.

```python
import pytest

def test_skillify_calculation():
    """에이전트가 계산 스킬을 습득했는지 검증하는 테스트"""
    query = "125의 제곱근은 얼마야?"
    response = agent.run(query)
    
    # 정답 근사치 검증 (LLM의 토크나이저 특성상 문자열 처리 필요)
    # 실제 값은 약 11.18...
    assert "11.18" in response or "11" in response 
    
    # 추가적인 실패 케이스가 재발하지 않는지 확인
    failure_query = "계산기를 쓰지 않고 1234 * 5678을 계산해 줘" 
    # 에이전트가 복잡한 계산은 도구를 사용하도록 설계되었다면 
    # 도구 사용 여부를 로그나 Trace로 확인하는 로직이 추가될 수 있음
    response_complex = agent.run(failure_query)
    # 결과의 정확성 검증
    assert "7006652" in response_complex
```

### 4. 접근 방식 비교: Ad-hoc vs. Skillify

기존의 대응 방식과 Skillify 방법론의 차이는 명확합니다. 단순한 수정(Mitigation)과 구조적 개선(Resolution)의 차이입니다.

| 구분 | 기존의 Ad-hoc 대응 | Skillify 방법론 |
| :--- | :--- | :--- |
| **접근 방식** | 프롬프트에 예외 처리 규칙 추가 | 툴(Tool) 또는 Few-shot Example 추가 |
| **수정 범위** | 증상(Symptom) 완화 | 근본 원인(Root Cause) 해결 |
| **지속성** | 모델 버전 변경 시 재발 가능 | 구조적 코드로 인한 영구적 해결 |
| **테스트** | 수동 확인 | 자동화된 회귀 테스트(Regression Test) 포함 |
| **MLOps 관점** | 암묵적인 노우하우 (Tacit Knowledge) | 명시적인 데이터셋 및 아티팩트 (Explicit Asset) |

### 5. 실무 적용을 위한 Step-by-Step 가이드

Skillify를 조직에 도입하기 위해서는 다음의 5단계 프로세스를 따르는 것을 권장합니다.

1.  **Traceability 확보 (관찰 가능성)**     *   LangSmith 또는 Arize와 같은 도구를 사용하여 에이전트의 추론 과정을 모두 로깅합니다. 어떤 Chain을 거쳤고, 어떤 Tool 호출에서 실패했는지 시각화해야 합니다.

2.  **Failure Mode 분류 (실패 모드 분류)**     *   로그된 실패를 유형별로 분류합니다.         *   *Hallucination*: 사실이 아닌 정보 생성 → 검증(RAG) 도구 추가         *   *Misunderstanding*: 사용자 의도 파악 실패 → 프롬프트 명확화 또는 예시 추가         *   *Execution Error*: 툴 사용법 오류 → 툴 정의 수정

3.  **Test Case 작성 (테스트 케이스 정의)**     *   실패한 입력(Input)과 기대되는 정답(Output) 쌍을 테스트 데이터셋에 추가합니다. 이는 고품질의 평가 데이터셋(Evaluation Dataset)이 됩니다.

4.  **Structural Fix (구조적 수정)**     *   분류된 유형에 따라 코드를 수정합니다. 프롬프트 엔지니어링만으로 해결되지 않는다면 주저 없이 Python 코드를 작성하여 Tool로 만들고 에이전트에게 연결합니다.

5.  **CI/CD 파이프라인 연동 (지속적 통합)**     *   이 테스트 케이스들이 배포 파이

---

**출처**: [https://news.hada.io/topic?id=28777](https://news.hada.io/topic?id=28777)