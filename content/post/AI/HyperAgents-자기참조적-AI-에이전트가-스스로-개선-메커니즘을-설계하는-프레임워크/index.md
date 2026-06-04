---
title: "HyperAgents: 자기참조적 AI 에이전트가 스스로 개선 메커니즘을 설계하는 프레임워크"
date: 2026-05-01T01:06:59+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
---

## 서론

개발자 A씨는 최근 LLM 기반 에이전트를 이용해 코드 리뷰 자동화 시스템을 구축했다. 초기에는 꽤 잘 동작했다. 하지만 몇 주가 지나자 에이전트의 성능이 정체되기 시작했다. 에이전트는 동일한 실수를 반복했고, 사용자 피드백을 수동으로 프롬프트에 반영해야 했다. 결국 A씨는 "에이전트가 스스로 실수에서 배우고 개선할 수는 없을까?"라는 근본적인 질문을 던지게 되었다.

이것은 단순히 한 개발자의 문제가 아니다. 2024년 현재 대부분의 LLM 에이전트 시스템은 **정적 프롬프트**와 **외부 피드백 루프**에 의존한다. 에이전트는 작업을 수행하지만, 자신이 *어떻게* 더 나아질 수 있는지에 대한 메커니즘은 설계하지 못한다. 이는 인공지능 연구의 오랜 숙제인 **자기 참조적 개선(self-referential improvement)** 문제와 직결된다.

Meta와 UBC(University of British Columbia)가 공동으로 발표한 **HyperAgents** 프레임워크는 이 문제에 대한 답을 제시한다. HyperAgents의 핵심 아이디어는 놀랍도록 직관적이다. 에이전트가 작업을 수행하는 코드뿐만 아니라, **자신의 개선 메커니즘 자체**를 수정할 수 있게 하는 것이다. 마치 학생이 문제를 푸는 동시에, 자신의 학습 방법론까지 스스로 재설계하는 것과 같다.

## 본론

### 1. 기존 에이전트 시스템의 한계

전통적인 LLM 에이전트 프레임워크(ReAct, AutoGPT, LangChain 기반 에이전트 등)는 다음과 같은 구조를 가진다:

```javascript
graph TD
    A[Task Input] --> B[LLM Reasoning]
    B --> C[Action Execution]
    C --> D[Observation]
    D --> B
    B --> E[Final Output]
```

이 구조의 문제점은 **적응성의 한계**에 있다. 에이전트는 주어진 프롬프트 내에서만 추론하고 행동한다. 성능을 개선하려면 외부에서 프롬프트를 수정하거나, 새로운 도구를 추가하거나, 파인튜닝을 수행해야 한다. 즉, **개선 주체가 에이전트 외부에 있다**.

### 2. HyperAgents의 핵심 원리: 메타 수준의 자기 개선

HyperAgents는 이 문제를 **메타 프로그래밍(meta-programming)** 관점에서 접근한다. 시스템은 두 가지 수준의 코드를 다룬다:
- **Task-Level Code**: 실제 작업(코딩, 리뷰, 수학 문제 해결 등)을 수행하는 코드
- **Meta-Level Code**: 에이전트가 어떻게 작업을 수행하고, 어떻게 개선할지를 정의하는 코드

```javascript
graph TD
    A[Task] --> B[Task Agent]
    B --> C[Task Result]
    C --> D[Evaluator]
    D --> E[Feedback]
    E --> F[Meta Agent]
    F --> G[Updated Meta Code]
    G --> B
    F --> H[Updated Improvement Mechanism]
    H --> F
```

중요한 점은 **Meta Agent**가 Task Agent의 코드뿐만 아니라, **자기 자신의 개선 메커니즘**까지 수정할 수 있다는 것이다. 이것이 "자기참조적(self-referential)"이라는 용어의 핵심이다.

### 3. 아키텍처 상세

HyperAgents의 아키텍처는 다음과 같은 핵심 컴포넌트로 구성된다:

#### 3.1 Task Agent 실제 작업을 수행하는 에이전트. LLM 기반으로 특정 도메인(코딩, 수학 등)의 문제를 해결한다.

#### 3.2 Meta Agent Task Agent의 성능을 관찰하고, 개선 방안을 코드 형태로 생성하는 에이전트. 여기서 "코드"는 프롬프트 템플릿, 검색 전략, 평가 기준 등을 포함한다.

#### 3.3 Code Editor Meta Agent가 생성한 개선안을 실제로 적용하는 모듈. 안전성 검사를 포함한다.

#### 3.4 Evaluator 작업 결과와 개선 효과를 평가하는 모듈. 도메인별 평가 메트릭을 사용한다.

| 컴포넌트 | 역할 | 입력 | 출력 |
| :--- | :--- | :--- | :--- |
| Task Agent | 작업 수행 | Task + Meta Code | Task Result |
| Meta Agent | 메타 개선 | History + Feedback | Meta Code Update |
| Code Editor | 코드 적용 | Meta Code Update | Updated System |
| Evaluator | 성능 평가 | Task Result | Score + Feedback |

### 4. 코드 예시: HyperAgents 스타일 자기 개선 구현

다음은 HyperAgents의 핵심 아이디어를 간소화한 Python 구현 예시다. 실제 연구 코드는 더 복잡하지만, 원리를 이해하기에 충분하다:

```python
import json
from typing import Dict, Any
from dataclasses import dataclass, field

@dataclass
class TaskResult:
    """작업 결과를 저장하는 데이터 클래스"""
    task_id: str
    output: str
    score: float
    feedback: str

@dataclass
class MetaCode:
    """메타 수준의 코드 (프롬프트, 전략 등)"""
    version: int = 1
    prompt_template: str = "Solve the following problem: {task}"
    strategy: str = "step_by_step"
    evaluation_criteria: Dict[str, float] = field(
        default_factory=lambda: {"accuracy": 1.0}
    )

class HyperAgent:
    """자기참조적 개선이 가능한 에이전트"""
    
    def __init__(self, llm_client):
        self.llm = llm_client
        self.meta_code = MetaCode()
        self.history = []
    
    def execute_task(self, task: str) -> TaskResult:
        """Task Agent: 메타 코드를 사용하여 작업 수행"""
        prompt = self.meta_code.prompt_template.format(task=task)
        
        # LLM으로 작업 수행
        response = self.llm.generate(prompt)
        
        # 결과 평가
        result = TaskResult(
            task_id=f"task_{len(self.history)}",
            output=response,
            score=0.0,  # 실제로는 Evaluator가 계산
            feedback=""
        )
        
        self.history.append(result)
        return result
    
    def meta_improve(self) -> MetaCode:
        """Meta Agent: 자기 개선 메커니즘 수행"""
        
        # 이전 성능 분석
        performance_summary = self._analyze_performance()
        
        # 메타 프롬프트: 개선 방안 생성
        meta_prompt = f"""
        Current meta code version: {self.meta_code.version}
        Current prompt template: {self.meta_code.prompt_template}
        Current strategy: {self.meta_code.strategy}
        
        Recent performance: {performance_summary}
        
        Generate improved meta code as JSON:
        {{
            "prompt_template": "...",
            "strategy": "...",
            "rationale": "..."
        }}
        """
        
        response = self.llm.generate(meta_prompt)
        improvements = json.
```

```python
loads(response)
        
        # 메타 코드 업데이트
        new_meta_code = MetaCode(
            version=self.meta_code.version + 1,
            prompt_template=improvements["prompt_template"],
            strategy=improvements["strategy"],
            evaluation_criteria=self.meta_code.evaluation_criteria
        )
        
        # 안전성 검사 후 적용
        if self._validate_meta_code(new_meta_code):
            self.meta_code = new_meta_code
            print(f"Meta code updated to v{self.meta_code.version}")
            print(f"Rationale: {improvements.get('rationale', 'N/A')}")
        
        return self.meta_code
    
    def _analyze_performance(self) -> Dict[str, Any]:
        """성능 이력 분석"""
        if not self.history:
            return {"status": "no_data"}
        
        recent = self.history[-5:]  # 최근 5개 작업
        avg_score = sum(r.score for r in recent) / len(recent)
        
        return {
            "avg_score": avg_score,
            "num_tasks": len(self.history),
            "trend": "improving" if len(self.history) > 1 else "initial"
        }
    
    def _validate_meta_code(self, meta_code: MetaCode) -> bool:
        """메타 코드 안전성 검증"""
        # 프롬프트 길이 제한
        if len(meta_code.prompt_template) > 2000:
            return False
        # 필수 플레이스홀더 확인
        if "{task}" not in meta_code.prompt_template:
            return False
        return True

# 사용 예시
if __name__ == "__main__":
    # 가상의 LLM 클라이언트 (실제로는 OpenAI, Anthropic 등)
    class MockLLM:
        def generate(self, prompt: str) -> str:
            if "improved meta code" in prompt.lower():
                return json.dumps({
                    "prompt_template": (
                        "Analyze and solve step-by-step: {task}
"
                        "Show your reasoning process."
                    ),
                    "strategy": "chain_of_thought",
                    "rationale":
```

```python
 "Adding explicit reasoning improves accuracy"
                })
            return "Sample solution"
    
    agent = HyperAgent(llm_client=MockLLM())
    
    # 작업 수행 → 메타 개선 반복
    for iteration in range(3):
        print(f"
=== Iteration {iteration + 1} ===")
        result = agent.execute_task("Solve: 2x + 5 = 13")
        agent.meta_improve()
        print(f"Current version: v{agent.meta_code.version}")
```

이 코드는 HyperAgents의 핵심 원리를 보여준다:
1. **Task Agent**가 메타 코드(프롬프트 템플릿, 전략)를 사용하여 작업을 수행한다
2. **Meta Agent**가 성능 이력을 분석하고, 개선된 메타 코드를 생성한다
3. **안전성 검증**을 거쳐 메타 코드를 업데이트한다
4. 이 과정이 반복되며 에이전트가 자기 개선한다

### 5. 실험 결과: 다양한 도메인에서의 성능

논문에 따르면 HyperAgents는 네 가지 도메인에서 실험되었다:

| 도메인 | 작업 유형 | 초기 성능 | 반복 개선 후 성능 | 향상률 |
| :--- | :--- | :--- | :--- | :--- |
| 코딩 | 알고리즘 문제 해결 | 62.4% | 78.1% | +15.7%p |
| 논문 리뷰 | 학술 논문 평가 | 3.2/5.0 | 4.1/5.0 | +28.1% |
| 로보틱스 | 작업 계획 수립 | 54.3% | 71.6% | +17.3%p |
| 수학 채점 | 정답 판별 및 채점 | 71.8% | 84.5% | +12.7%p |

주목할 만한 점은 **개선 곡선이 로그 스케일로도 지속적**이라는 것이다. 즉, 초기 급격한 향상 이후에도 개선이 멈추지 않고 계속된다.

### 6. Step-by-Step: HyperAgents 적용 가이드

HyperAgents를 실제 프로젝트에 적용하는 과정을 단계별로 살펴보자:

#### Step 1: 작업 정의 및 초기 메타 코드 설계

```python
# 초기 메타 코드 정의
initial_meta = {
    "task_type": "code_review",
    "prompt_template": """
    Review the following code for:
    1. Bugs and errors
    2. Performance issues
    3. Best practices
    
    Code: {task}
    """,
    "evaluation_criteria": {
        "bug_detection": 0.4,
        "style_compliance": 0.3,
        "performance_insight": 0.3
    }
}
```

#### Step 2: 평가 파이프라인 구축 작업 결과를 정량적으로 평가할 수 있는 파이프라인이 필수적이다. HyperAgents의 자기 개선은 **평가 신호**에 의존하기 때문이다.

#### Step 3: 안전 가드레일 설정 메타 에이전트가 시스템을 망가뜨리지 않도록 안전장치를 마련한다:
- 메타 코드 변경 시 백업 유지
- 성능 임계치 하향 시 자동 롤백
- 메타 코드 변경 빈도 제한

#### Step 4: 반복 루프 실행 작업 수행 → 평가 → 메타 개선 → 적용 사이클을 자동화한다.

#### Step 5: 모니터링 및 분석 메타 코드의 변화 이력을 추적하고, 어떤 개선이 효과적이었는지 분석한다.

### 7. 기술적 도전과 해결책

HyperAgents 구현 시 직면하는 주요 도전과 해결책은 다음과 같다:

**도전 1: 메타 코드의 무한 확장** 에이전트가 메타 프롬프트를 계속 추가하면, 컨텍스트 윈도우가 초과될 수 있다.
- 해결: 메타 코드 압축 메커니즘 도입. 핵심 규칙만 유지하고 세부 사항은 요약.

**도전 2: 개선의 수렴 여부** 에이전트가 로컬 옵티마에 빠질 위험.
- 해결: 탐험(exploration) 메커니즘 도입. 일정 확률로 새로운 전략 시도.

**도전 3: 안전성 보장** 메타 에이전트가 위험하거나 무의미한 변경을 가할 수 있음.
- 해결: 검증 계층(validator layer) 도입. 변경 사항을 테스트 환경에서 먼저 평가.

### 8. 기존 자기 개선 방법과의 비교

| 방법론 | 개선 주체 | 개선 대상 | 외부 의존성 | 적응 속도 |
| :--- | :--- | :--- | :--- | :--- |
| 수동 프롬프트 엔지니어링 | 인간 | 프롬프트 | 높음 | 느림 |

---

**출처**: [https://news.hada.io/topic?id=28430](https://news.hada.io/topic?id=28430)