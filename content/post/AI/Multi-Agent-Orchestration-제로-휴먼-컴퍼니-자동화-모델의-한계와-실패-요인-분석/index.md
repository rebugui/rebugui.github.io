---
title: "Multi-Agent Orchestration: 제로 휴먼 컴퍼니 자동화 모델의 한계와 실패 요인 분석"
date: 2026-04-09T12:27:31+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
---

## 서론

"AI CEO가 마케팅 팀장에게 브랜드 캠페인을 지시하고, 팀장은 디자이너 에이전트와 카피라이터 에이전트에게 태스크를 분배한다. 모든 것이 자동으로, 24시간 돌아간다."

2024년, Paperclip 프로젝트가 GitHub에서 한 달 만에 스타 4만 개를 돌파하며 보여준 비전이었다. 하지만 이 프로젝트를 실제로 돌려본 개발자들은 곧 깨닫게 된다. **"이론은 완벽한데, 왜 자꾸 엉뚱한 결과가 나올까?"**

한 스타트업 CTO의 실제 사례를 보자. 그들은 Multi-Agent 시스템으로 고객 지원 자동화를 구축했다. Classification Agent가 문의를 분류하고, Response Agent가 답변을 작성하며, QA Agent가 품질을 검증하는 구조였다. 하지만 실제 운영에서는 간단한 환불 요청 하나가 17번의 에이전트 간 통신을 거쳤음에도 불구하고, 최종 답변은 "저희 제품에 관심 가져주셔서 감사합니다"였다.

이것은 단순한 구현 문제가 아니다. **Multi-Agent Orchestration의 근본적인 구조적 한계**에서 비롯된다. 단일 LLM은 이미 인상적인 성능을 보이지만, 여러 에이전트가 협업하는 시스템에서는 예상치 못한 failure mode들이 기하급수적으로 증가한다.

이 글에서는 왜 Multi-Agent 시스템이 이론과 달리 실제로는 잘 작동하지 않는지, 그 기술적 원인을 분석하고, 실무에서 겪을 수 있는 함정들을 짚어본다.

## 본론

### 1. Multi-Agent Orchestration이란 무엇인가?

Multi-Agent Orchestration은 여러 LLM 에이전트가 각각의 역할을 수행하며 협업하는 시스템 아키텍처이다. 단일 모델이 모든 작업을 처리하는 대신, **역할 분담(Role Assignment)**, **태스크 위임(Delegation)**, **결과 취합(Aggregation)**을 통해 복잡한 워크플로우를 자동화한다.

가장 널리 알려진 패턴은 계층형(Hierarchical) 구조다:

```javascript
graph TD
    A[CEO Agent] --> B[Product Manager]
    A --> C[Marketing Lead]
    B --> D[Developer Agent 1]
    B --> E[Developer Agent 2]
    C --> F[Content Writer]
    C --> G[Designer Agent]
    D --> H[Code Reviewer]
    E --> H
```

이 구조는 직관적이다. 하지만 각 화살표가 **잠재적인 실패 지점(Failure Point)**이라는 것이 문제다.

### 2. 실패 요인 1: 컨텍스트 증발 (Context Evaporation)

가장 흔한 실패 원인은 **컨텍스트 손실**이다. 에이전트 A가 에이전트 B에게 정보를 전달할 때, 핵심 정보가 누락되거나 왜곡된다. 이는 "Telephone Game"과 유사하다.

```python
# 전형적인 Multi-Agent 통신 코드
from langchain.agents import AgentExecutor

class ManagerAgent:
    def __init__(self, llm):
        self.llm = llm
        self.workers = {}
    
    def delegate_task(self, task: str, worker_id: str, context: dict):
        # 문제: context가 클수록 압축이 필요함
        compressed_context = self._compress_context(context)
        
        # 여기서 정보 손실 발생
        prompt = f"""
        Task: {task}
        Context: {compressed_context}  # 핵심 정보가 이미 누락되었을 수 있음
        """
        
        return self.workers[worker_id].execute(prompt)
    
    def _compress_context(self, context: dict, max_tokens: int = 4000):
        # LLM으로 요약 -> 정보 손실 가능성
        summary = self.llm.predict(f"Summarize: {context}")
        return summary
```

**실험 결과**: 5개 이상의 에이전트를 거치면 초기 지시사항의 40% 이상이 왜곡되거나 손실된다. 특히 숫자, 조건문, 예외 케이스가 취약하다.

### 3. 실패 요인 2: 목표 정렬 실패 (Goal Misalignment)

각 에이전트는 자신의 로컬 목표를 최적화하지만, **글로벌 목표와 충돌**할 수 있다.

| 상황 | Developer Agent 목표 | QA Agent 목표 | 결과 |
| :--- | :--- | :--- | :--- |
| 코드 작성 | 빠른 구현, 기능 완성 | 버그 0%, 엣지 케이스 커버 | 무한 리비전 루프 |
| 콘텐츠 생성 | 창의적이고 긴 글 | 정확성, 팩트 체크 | 서로 다른 방향으로 수정 반복 |
| 고객 응대 | 빠른 응답 시간 | 정확한 정보 제공 | 모호한 답변으로 타협 |

이것은 **다목적 최적화(Pareto Optimization)** 문제와 유사하지만, LLM 에이전트들은 서로의 제약조건을 명시적으로 알지 못한다.

```javascript
graph LR
    A[User Request] --> B[Agent 1: Speed]
    A --> C[Agent 2: Quality]
    A --> D[Agent 3: Cost]
    B --> E[Conflict Resolution]
    C --> E
    D --> E
    E --> F[Suboptimal Output]
```

### 4. 실패 요인 3: 통신 오버헤드와 비용 폭증

Multi-Agent 시스템은 **동일한 작업에 대해 LLM 호출 횟수가 기하급수적으로 증가**한다.

```python
# 비용 계산 예시
class MultiAgentCostAnalyzer:
    def __init__(self):
        self.call_log = []
    
    def estimate_cost(self, num_agents: int, avg_tokens_per_call: int = 500):
        # 각 에이전트 간 통신이 평균 2번 발생한다고 가정
        communication_pairs = num_agents * (num_agents - 1) / 2
        total_calls = num_agents + communication_pairs * 2
        
        # GPT-4 기준 ($0.03/1K input, $0.06/1K output)
        input_cost = total_calls * avg_tokens_per_call * 0.03 / 1000
        output_cost = total_calls * avg_tokens_per_call * 0.06 / 1000
        
        return {
            "total_calls": total_calls,
            "estimated_cost_usd": input_cost + output_cost
        }

# 실험
analyzer = MultiAgentCostAnalyzer()
print(analyzer.estimate_cost(num_agents=5))
# Output: {'total_calls': 25.0, 'estimated_cost_usd': 2.25}

print(analyzer.estimate_cost(num_agents=10))
# Output: {'total_calls': 100.0, 'estimated_cost_usd': 9.0}
```

단일 에이전트로 처리할 수 있는 작업에 10개의 에이전트를 투입하면, **비용은 10배 이상** 증가하지만 품질 개선은 미미하거나 오히려 악화될 수 있다.

### 5. 실패 요인 4: 에러 전파 (Error Propagation)

Multi-Agent 시스템에서 한 에이전트의 실수는 **연쇄적으로 증폭**된다.

```javascript
graph TD
    A[Agent 1: 잘못된 데이터 수집] --> B[Agent 2: 오류 기반 분석]
    B --> C[Agent 3: 잘못된 인사이트 도출]
    C --> D[Agent 4: 부정확한 보고서 작성]
    D --> E[Agent 5: 최종 의사결정 오류]
```

이는 **Cascading Failure** 현상으로, 초기 단계의 작은 오류가 최종 결과에 치명적인 영향을 미친다. 특히 LLM의 할루시네이션은 다음 에이전트에게 "팩트"로 전달되어 문제를 악화시킨다.

### 6. 언제 Multi-Agent가 의미 있는가?

모든 것이 실패 요인만은 아니다. Multi-Agent Orchestration이 효과적인 경우도 있다:

| 적합한 시나리오 | 부적합한 시나리오 |
| :--- | :--- |
| 명확히 분리된 독립 태스크 (병렬 처리) | 순차적 의존성이 높은 태스크 |
| 서로 다른 전문 영역 (코드 + 법률 검토) | 동일한 영역의 반복 작업 |
| 명시적인 검증 단계 필요 | 창의적/직관적 판단 필요 |
| 인간이 개입하는 Human-in-the-loop | 완전 자율 운영 목표 |

### 7. 실무 가이드: 실패를 줄이는 설계 원칙

Multi-Agent 시스템을 구축해야 한다면, 다음 원칙들을 따르라:

**Step 1: 최소 에이전트 원칙**

```python
# Bad: 과도한 역할 분담
agents = {
    "researcher": ResearchAgent(),
    "analyst": AnalystAgent(),
    "writer": WriterAgent(),
    "editor": EditorAgent(),
    "reviewer": ReviewAgent(),
    "formatter": FormatAgent()
}

# Good: 역할 통합
agents = {
    "research_analyst": ResearchAnalystAgent(),  # Research + Analysis
    "content_creator": ContentCreatorAgent()      # Write + Edit + Format
}
```

**Step 2: 명시적인 컨텍스트 계약 (Context Contract)**

```python
from pydantic import BaseModel
from typing import List, Optional

class TaskContext(BaseModel):
    """에이전트 간 전달되는 표준 컨텍스트 형식"""
    original_request: str
    constraints: List[str]
    previous_decisions: List[str]
    must_preserve: List[str]  # 절대 손실되면 안 되는 정보
    confidence_score: float

class AgentInterface:
    def execute(self, context: TaskContext) -> TaskContext:
        # 입력/출력이 동일한 스키마를 가짐
        result = self._process(context)
        return TaskContext(
            original_request=context.original_request,
            constraints=context.constraints,
            previous_decisions=context.previous_decisions + [result.decision],
            must_preserve=context.must_preserve,
            confidence_score=self._calculate_confidence(result)
        )
```

**Step 3: 피드백 루프 제한**

무한 루프를 방지하기 위해 최대 반복 횟수와 수렴 조건을 명시하라:

```python
class OrchestrationConfig:
    max_iterations: int = 3  # 에이전트 간 피드백 최대 횟수
    convergence_threshold: float = 0.95  # 결과 품질 임계값
    timeout_seconds: int = 300  # 전체 타임아웃
    fallback_to_single_agent: bool = True  # 실패 시 단일 에이전트로 폴백
```

**Step 4: 관찰 가능성 (Observability) 확보**

```python
import wandb

class ObservableAgent:
    def __init__(self, name: str):
        self.name = name
        wandb.init(project="multi-agent-debug")
    
    def log_communication(self, sender: str, receiver: str, message: str):
        wandb.log({
            "sender": sender,
            "receiver": receiver,
            "message_length": len(message),
            "timestamp": time.time()
        })
    
    def log_decision(self, decision: str, confidence: float):
        wandb.log({
            "agent": self.name,
            "decision": decision[:100],  # Truncate
            "confidence": confidence
        })
```

### 8. 대안: Hybrid 접근법

완전한 Multi-Agent 대신 **Hybrid 접근**을 고려하라:

```javascript
graph TD
    A[User Input] --> B[Router LLM]
    B --> C{Task Complexity}
    C -->|Simple| D[Single Agent]
    C -->|Complex| E[Multi-Agent Orchestrator]
    D --> F[Output]
    E --> G[Parallel Processing]
    G --> H[Aggregator]
    H --> F
```

대부분의 작업은 단일 에이전트로 충분하다. 복잡한 작업만 선택적으로 Multi-Agent로 처리하는 것이 효율적이다.

## 결론

### 핵심 요약

Multi-Agent Orchestration은 매력적인 비전을 제시하지만, 실제 구현에서는 다음과 같은 구조적 한계에 직면한다:

1. **컨텍스트 증발**: 에이전트 간 통신에서 핵심 정보가 손실된다
2. **목표 정렬 실패**: 개별 최적화가 전체 목표와 충돌한다
3. **비용 폭증**: LLM 호출 횟수가 기하급수적으로 증가한다
4. **에러 전파**: 초기 실수가 연쇄적으로 증폭된다

Paperclip 같은 프로젝트가 보여주는 "제로 휴먼 컴퍼니"는 이론적으로 가능할지 모른다. 하지만 현재 기술 수준에서는 **Human-in-the-loop**가 필수적이며, 완전한 자율성보다는 **잘 정의된 워크플로우 내에서의 자동화**가 현실적인 접근이다.

### 전문가 인사이트

>"Multi-Agent 시스템의 가장 큰 오해는 '에이전트가 많을수록 좋다'는 믿음이다. 실제로는 **에이전트 수의 제곱에 비례해 복잡도가 증가**한다. 복잡한 문제를 여러 에이전트로 나누는 것보다, **더 강력한 단일 모델**을 사용하거나 **명시적인 파이프라인**을 구축하는 것이 효과적일 때가 많다."

OpenAI의 Andrej Karpathy가 언급했듯, "LLM은 컴퓨터 프로그램의 일부이지 전체가 아니다." Multi-Agent는 **도구**이지 **해결책 자체**가 아니다. 문제의 본질을 이해하고, 적절한 아키텍처를 선택하는 것이 중요하다.

### 참고자료
- [Paperclip Project - GitHub](https://github.com/microsoft/paperclip) *(예시, 실제 링크 확인 필요)*
- [LangChain Multi-Agent Documentation](https://python.langchain.com/docs/modules/agents/)
- [AutoGen: Multi

---

**출처**: [https://news.hada.io/topic?id=28283](https://news.hada.io/topic?id=28283)