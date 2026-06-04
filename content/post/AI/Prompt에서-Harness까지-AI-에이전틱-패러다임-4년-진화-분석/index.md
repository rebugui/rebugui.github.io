---
title: "Prompt에서 Harness까지: AI 에이전틱 패러다임 4년 진화 분석"
date: 2026-04-09T12:27:29+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
---

## 서론

2023년 초, 한 스타트업의 CTO가 필자에게 절박한 전화를 걸어왔다. "우리는 GPT-4로 고객 응대 챗봇을 만들었어요. 프롬프트도 정성스럽게 작성했고, few-shot 예시도 20개나 넣었죠. 그런데 배포 후 일주일 만에 환각으로 인해 잘못된 정보를 제공하는 사례가 30%나 되었어요."

이것은 드문 일이 아니다. 수많은 기업이 LLM을 프로덕션에 도입하려다 비슷한 벽에 부딪혔다. 프롬프트만 잘 쓰면 된다는 초기의 낙관론은 곧 한계에 봉착했고, 더 정교한 접근이 필요해졌다.

**AI 에이전틱 패러다임의 진화**는 단순한 유행이 아니다. 이것은 "언어 모델에게 무엇을 원하는지 말하기"에서 "어떻게 원하는 것을 얻을지 시스템화하기"로의 근본적 전환이다. 각 패러다임 전환은 이전 방식이 현장에서 약속을 지키지 못한 실패로부터 비롯되었다.

이 글에서는 2022년부터 2026년까지의 세 번의 패러다임 전환을 기술적으로 분석하고, 왜 각 단계가 필요했는지, 그리고 실무에서 어떻게 적용해야 하는지를 다룬다.

---

## 본론

### 1. 패러다임 진화 개요

```javascript
graph LR
    A[Prompt Engineering<br/>2022-2023] --> B[Context Engineering<br/>2023-2024]
    B --> C[Harness Engineering<br/>2024-2026]
    
    A --> D[실패: 일관성 부족]
    D --> B
    
    B --> E[실패: 상태 관리 한계]
    E --> C
```

위 다이어그램은 AI 개발 패러다임이 어떻게 진화했는지를 보여준다. 각 전환은 명확한 실패 지점에서 출발했다.

### 2. 제1막: Prompt Engineering (2022-2023)

#### 2.1 등장 배경과 약속

GPT-3가 등장했을 때, 개발자들은 "자연어로 프로그래밍한다"는 꿈을 꿨다. 복잡한 코드 대신 영어로 원하는 것을 설명하면 AI가 알아서 처리해 줄 것이라 믿었다.

**핵심 철학**: "모든 것은 프롬프트 안에 있다"

```python
# 전형적인 Prompt Engineering 접근 (2022년 스타일)
SYSTEM_PROMPT = """
당신은 전문 고객 서비스 에이전트입니다.
다음 원칙을 따르세요:
1. 항상 정중하게 응답하세요
2. 확실하지 않은 정보는 제공하지 마세요
3. 고객의 문제를 먼저 이해하세요

예시:
고객: "환불하고 싶어요"
응답: "불편을 드려 죄송합니다. 어떤 상품에 대한 환불을 원하시나요?"
"""

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query}
    ]
)
```

#### 2.2 기술적 원리: In-Context Learning

Prompt Engineering의 핵심은 **In-Context Learning (ICL)**이다. 모델 가중치를 업데이트하지 않고, 컨텍스트 윈도우 내에서 예시와 지시사항을 통해 원하는 동작을 유도한다.

2020년 GPT-3 논문(Brown et al.)에서 제시된 ICL은 다음 세 가지 형태로 발전했다:

| 기법 | 설명 | 예시 개수 | 효과 |
| :--- | :--- | :--- | :--- |
| Zero-shot | 예시 없이 지시만 | 0개 | 단순 작업에 적합 |
| Few-shot | 몇 개의 예시 제공 | 1-10개 | 복잡한 패턴 인식 |
| Chain-of-Thought | 추론 과정 명시 | 3-5개 | 논리적 추론 향상 |

#### 2.3 왜 실패했는가

Prompt Engineering의 근본적 한계는 **결정론적 통제의 부재**였다.

```python
# 같은 입력, 다른 출력 - 비결정적 동작
for _ in range(5):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "파리의 수도는?"}],
        temperature=0.0  # 낮춰도 완전한 결정성 보장 안 됨
    )
    print(response.choices[0].message.content)
# 출력이 5번 모두 같다는 보장이 없음
```

**주요 실패 요인**:

1. **Temperature ≠ 0도 완전한 결정성을 보장하지 않음**
2. **프롬프트 버전 관리의 어려움** - "v1.2_final_real_final.txt"
3. **프롬프트 인젝션 취약점** - 사용자 입력이 시스템 지시를 덮어씀
4. **환각(Hallucination) 통제 불가** - 모델이 그럴듯한 거짓말을 생성

Wei et al. (2022)의 연구에 따르면, Chain-of-Thought 프롬프팅도 수학적 추론에서 40% 이상의 오류율을 보였다.

### 3. 제2막: Context Engineering (2023-2024)

#### 3.1 패러다임 전환의 계기

"프롬프트를 더 잘 쓰는 것"이 아니라 "프롬프트에 더 많은 정확한 정보를 담는 것"으로 초점이 이동했다.

```javascript
graph TD
    A[User Query] --> B[Embedding]
    B --> C[Vector DB 검색]
    C --> D[관련 문서 추출]
    D --> E[Context 구성]
    E --> F[LLM 추론]
    F --> G[응답]
```

#### 3.2 RAG: Retrieval-Augmented Generation

**RAG**는 Context Engineering의 핵심 기술이다. Lewis et al. (2020)가 제안했고, 2023년에 폭발적으로 채택되었다.

```python
# RAG 파이프라인 구현 (LangChain 스타일)
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA

# 1. 지식 베이스 구축
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(
    documents=knowledge_base_docs,
    embedding=embeddings
)

# 2. RAG 체인 구성
llm = ChatOpenAI(model="gpt-4", temperature=0)
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",  # 모든 문서를 컨텍스트에 포함
    retriever=vectorstore.as_retriever(
        search_kwargs={"k": 5}  # 상위 5개 문서 검색
    )
)

# 3. 질의
response = qa_chain.run("우리 회사의 환불 정책이 어떻게 되나요?")
```

#### 3.3 기술적 발전: RAG의 고도화

RAG는 빠르게 진화했다:

| RAG 세대 | 특징 | 기술적 한계 |
| :--- | :--- | :--- |
| Naive RAG | 단순 유사도 검색 | 관련성 낮은 문서 검색 |
| Advanced RAG | 재순위화, 쿼리 재작성 | 검색 품질 의존 |
| Modular RAG | 검색-생성 모듈 분리 | 파이프라인 복잡도 증가 |
| Graph RAG | 지식 그래프 활용 | 그래프 구축 비용 |

#### 3.4 왜 또 실패했는가

Context Engineering은 프롬프트의 "정보 품질"을 개선했지만, **상태 관리와 행동 제어** 문제는 해결하지 못했다.

```python
# Context Engineering의 한계 예시
# 대화가 길어질수록 컨텍스트가 폭발

conversation_history = []  # 계속 쌓임

def chat_with_memory(user_input):
    conversation_history.append({"role": "user", "content": user_input})
    
    # 컨텍스트 윈도우 한계 도달
    total_tokens = count_tokens(conversation_history)
    if total_tokens > 128000:  # GPT-4 Turbo 한계
        # 어떤 대화를 버릴 것인가? -> 정보 손실
        conversation_history = truncate_middle(conversation_history)
    
    response = llm.chat(conversation_history)
    conversation_history.append({"role": "assistant", "content": response})
    return response
```

**핵심 실패 요인**:

1. **컨텍스트 윈도우 한계** - 긴 대화에서 정보 손실
2. **상태 일관성** - 에이전트가 이전 결정을 "기억"하지 못함
3. **도구 사용의 불안정성** - API 호출 실패 시 복구 불가
4. **평가 기준 부재** - "좋은 컨텍스트"가 무엇인지 정의 안 됨

### 4. 제3막: Harness Engineering (2024-2026)

#### 4.1 새로운 패러다임의 정의

**Harness Engineering**은 AI 에이전트를 "감싸는(harness)" 구조적 프레임워크를 설계하는 것이다. 이것은 단순한 프롬프트가 아닌, **아키텍처 레벨의 엔지니어링**이다.

```javascript
graph TD
    A[User Input] --> B[Input Guardrail]
    B --> C[Intent Classifier]
    C --> D[Action Planner]
    D --> E[Tool Executor]
    E --> F[State Manager]
    F --> G[Output Validator]
    G --> H[Response]
    
    E --> I[Memory Store]
    I --> F
    
    G -->|실패| J[Fallback Handler]
    J --> H
```

#### 4.2 핵심 구성 요소

**Harness Engineering의 5가지 기둥**:

```python
# Harness Engineering 아키텍처 예시 (Pydantic 기반)
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from enum import Enum

class AgentState(str, Enum):
    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    WAITING_FOR_INPUT = "waiting_for_input"
    COMPLETED = "completed"
    FAILED = "failed"

class ToolCall(BaseModel):
    tool_name: str
    arguments: dict
    expected_output: str

class AgentMemory(BaseModel):
    short_term: List[dict] = Field(default_factory=list)
    long_term: List[dict] = Field(default_factory=list)
    working_memory: dict = Field(default_factory=dict)

class HarnessAgent:
    def __init__(self):
        self.state = AgentState.IDLE
        self.memory = AgentMemory()
        self.tools = self._register_tools()
        self.guardrails = self._setup_guardrails()
        
    def execute_with_harness(self, user_input: str) -> dict:
        """Harness로 감싸진 실행 파이프라인"""
        
        # 1. Input Guardrail
        if not self.guardrails.validate_input(user_input):
            return self._fallback("invalid_input")
        
        # 2. Intent Classification (구조화)
        intent = self._classify_intent(user_input)
        
        # 3. Action Planning (상태 기반)
        plan = self._plan_actions(intent)
        
        # 4. Constrained Execution
        for step in plan:
            if not self._can_execute(step):
                return self._fallback("constraint_violation")
            
            result = self._execute_step(step)
            self._update_state(result)
            
            if self.state == AgentState.FAILED:
                return self._recover_or_fail()
        
        # 5. Output Validation
        response = self._generate_response()
        if not self.guardrails.validate_output(response):
            return self._fallback("output_validation_failed")
        
        return response
```

#### 4.3 상태 기반 설계 (State Machine)

```python
# 유한 상태 머신 기반 에이전트 제어
class StateMachine:
    transitions = {
        AgentState.IDLE: [AgentState.PLANNING],
        AgentState.PLANNING: [AgentState.EXECUTING, AgentState.FAILED],
        AgentState.EXECUTING: [
            AgentState.COMPLETED, 
            AgentState.WAITING_FOR_INPUT,
            AgentState.FAILED
        ],
        AgentState.WAITING_FOR_INPUT: [AgentState.EXECUTING],
        AgentState.COMPLETED: [AgentState.IDLE],
        AgentState.FAILED: [AgentState.IDLE]
    }
    
    def transition(self, from_state: AgentState, to_state: AgentState) -> bool:
        if to_state in self.transitions[from_state]:
            self.current_state = to_state
            return True
        raise InvalidStateTransition(
            f"Cannot transition from {from_state} to {to_state}"
        )
```

#### 4.4 패러다임 비교

| 차원 | Prompt Engineering | Context Engineering | Harness Engineering |
| :--- | :--- | :--- | :--- |
| **핵심 가 |  |  |  |

---

**출처**: [https://news.hada.io/topic?id=28301](https://news.hada.io/topic?id=28301)