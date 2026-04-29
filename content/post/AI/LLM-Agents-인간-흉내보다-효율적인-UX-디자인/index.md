---
title: "LLM Agents: 인간 흉내보다 효율적인 UX 디자인"
date: 2026-04-30T01:07:32+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
---

## 서론

최근 대규모 언어 모델(LLM)을 기반으로 한 AI 에이전트(AI Agent)를 사용하다 보면 묘한 답답함을 느끼곤 합니다. 복잡한 데이터 분석을 요청했을 때, 에이전트가 "네, 한번 확인해 보겠습니다"라는 안부 인사와 함께 인간처럼 일부러 속도를 늦춰 출력하거나, 굳이 사용자에게 알릴 필요가 없는 잡담을 늘어놓는 상황을 경험해 보셨을 것입니다. 초기에는 신기했던 이러한 '인간 흉내(Human mimicry)'는 업무 효율성이 중요한 실무 환경에서는 독이 되고 있습니다.

우리는 왜 AI를 인간처럼 행동하게 하려는 걸까요? 이는 AI가 인간의 언어를 이해한다는 착각을 심어주어 '친근함'을 줄 수 있지만, 동시에 인지적 부하(Cognitive Overhead)를 증가시키고 핵심 기능의 신뢰성을 떨어뜨리는 결과를 초래합니다. Nial의 블로그 "Less human AI agents, please"에서 지적했듯, 사용자는 AI로부터 위로나 사교적인 제스처가 아니라, 기계가 수행할 수 있는 가장 빠르고 정확한 연산 결과를 원합니다. 이 글에서는 불필요한 인격화(Anthropomorphism)를 배제하고 기계의 효율성을 극대화하는 UX 설계의 중요성과 그 구체적인 구현 방안을 기술적 관점에서 분석합니다.

## 본론

### 기술적 배경: 인지적 부하와 추론 지연의 문제점

LLM 에이전트의 UX를 설계할 때 가장 중요하게 고려해야 할 요소는 '토큰 효율성'과 '추론 속도(Latency)'입니다. 대부분의 최신 에이전트는 Yao et al. (2022)이 제안한 ReAct(Reasoning + Acting) 패러다임을 따르며, [사고(Thought) -> 행동(Action) -> 관찰(Observation)]의 루프를 반복합니다. 문제는 이 '사고(Thought)' 과정을 자연어 문장으로 사용자에게 그대로 노출시키거나, 인공적인 지연 시간(Delay)을 삽입하여 "생각하고 있는 중"이라는 느낌을 주려는 시도입니다.

이러한 접근 방식은 사용자 인터페이스(UI)에서 두 가지 심각한 기술적 결함을 야기합니다. 첫째, 불필요한 토큰 생성으로 인해 Time-to-First-Token(TTFT) 및 Total Generation Time이 증가합니다. 둘째, 사용자의 시선을 중요한 정보가 아닌 채팅창의 '타이핑 애니메이션'이나 '긴 설명'으로 분산시켜 작업 흐름(Workflow)을 끊깁니다. 즉, 인간 흉내는 기계의 고유한 강점인 '병렬 처리'와 '즉각적인 응답'을 저해하는 요소가 됩니다.

### 효율적인 에이전트 아키텍처: Human vs. Machine Mode

기존의 대화형 에이전트와 기능 중심의 에이전트가 요청을 처리하는 방식의 차이를 시각화하면 다음과 같습니다.

```javascript
graph TD
    U[User Request] --> A{Agent Processing}

    subgraph Human_Mode_Conventional
        A --> H1[Greeting & Small Talk]
        H1 --> H2[Verbose Thinking Display]
        H2 --> H3[Action Execution]
        H3 --> H4[Polite Closing]
    end

    subgraph Machine_Mode_Optimized
        A --> M1[Direct Plan Generation]
        M1 --> M2[Tool Call]
        M2 --> M3[Structured Output JSON]
    end

    H4 --> R[Result Delivery]
    M3 --> R
```

위 다이어그램과 같이 'Human Mode'는 불필요한 사교적(Social) 단계를 거치기 때문에 처리 파이프라인이 길어집니다. 반면 'Machine Mode'는 사용자의 의도를 파악하자마자 즉시 도구(Tool)를 호출하고 구조화된 결과(JSON 등)를 반환합니다.

### 실무 구현 가이드: 기능적 시스템 프롬프트 설계

실제로 LangChain이나 OpenAI API를 사용하여 에이전트를 구현할 때, 시스템 프롬프트(System Prompt)를 어떻게 설계하느냐에 따라 성능이 크게 달라집니다. 다음은 Python을 사용하여 '기계적이고 효율적인' 에이전트를 구성하는 예시 코드입니다.

이 코드는 OpenAI의 Chat Completions API를 사용하며, 시스템 프롬프트를 통해 불필요한 대화를 차단하고 직관적인 명령 실행을 유도합니다.

```python
import openai

client = openai.OpenAI(api_key="YOUR_API_KEY")

def execute_efficient_agent(user_query):
    # 기능적 에이전트를 위한 시스템 프롬프트 설계
    system_instruction = """
    You are a functional CLI interface, not a human assistant.
    
    Rules:
    1. DO NOT use conversational fillers (e.g., "Sure", "Here is the result", "Let me check").
    2. Think silently if needed, but only output the final execution result or direct tool calls.
    3. If information is missing, ask only the essential questions in a concise format.
    4. Prioritize accuracy and speed over politeness.
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_query}
        ],
        temperature=0, # 창의성보다는 정확성을 위해 0 설정
        max_tokens=500 # 불필요한 긴 답변 방지
    )

    return response.choices[0].message.content

# 실행 예시
# 사용자: "Calculate 123 * 456"
# 기존 AI: "Of course! Let me calculate that for you. The result of 123 times 456 is 56088. Hope that helps!"
# 효율적 AI: "56088"
print(execute_efficient_agent("Calculate 123 * 456"))
```

이 코드에서 핵심은 `temperature=0`으로 설정하여 확률적 변동성을 줄이고, 시스템 프롬프트를 통해 "함수형 인터페이스"로서의 역할을 부여하는 것입니다. 이는 단순히 답변을 짧게 만드는 것이 아니라, 에이전트의 추

---

**출처**: [https://nial.se/blog/less-human-ai-agents-please/](https://nial.se/blog/less-human-ai-agents-please/)