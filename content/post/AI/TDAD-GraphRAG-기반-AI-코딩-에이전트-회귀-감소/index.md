---
title: "TDAD: GraphRAG 기반 AI 코딩 에이전트 회귀 감소"
date: 2026-03-23T01:30:08+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
---

## 서론

최근 자율 주행 자동차가 신호를 인지 못해 멈춰 선다면, 우리는 시스템의 전면적인 개선을 요구할 것입니다. 하지만 소프트웨어 개발의 영역에서 AI 코딩 에이전트가 발생시키는 유사한 사고는 종종 간과됩니다. 개발자가 AI에게 "결제 시스템의 타임아웃 버그를 수정해 줘"라고 요청했을 때, AI는 멋지게 문제를 해결하곤 합니다. 하지만 정작 다음 날, 아무런 관련이 없어 보이는 '로그인 기능'이 작동하지 않는 사태가 벌어집니다.

이것이 바로 **회귀(Regression)** 문제입니다. 현재 AI 코딩 에이전트를 평가하는 대부분의 벤치마크(SWE-bench 등)는 "문제를 해결했는가(Resolved?)"에만 집중합니다. 하지만 실제 프로덕션 환경에서는 "새로운 문제를 만들지 않았는가(No Regression?)"가 훨씬 더 중요할 수 있습니다. 이 글에서는 단순히 모델의 성능을 높이는 것을 넘어, AI가 코드를 수정할 때 어떤 테스트가 깨질지 미리 예측하여 회귀를 70%나 감소시킨 혁신적인 접근법 **TDAD(Test-Driven Agentic Development)**에 대해 심도 있게 다루고자 합니다.

## 본론

### 기술적 원리: AST 기반 코드-테스트 그래프와 GraphRAG

기존의 AI 에이전트가 TDD(Test-Driven Development)를 수행할 때 겪는 어려움은 명령의 '절차적' 이해에 그친다는 점입니다. "먼저 테스트를 쓰고, 코드를 수정하고, 검증해라"라는 지시는 모델에게 막연한 가이드라인만 제공할 뿐, 어떤 테스트가 현재 수정 사항과 연관되어 있는지에 대한 **맥락(Context)**을 주지 못합니다. 반면, TDAD는 추상 구문 트리(AST)를 분석하여 코드와 테스트 간의 의존 관계를 정량화합니다.

TDAD의 핵심은 **코드-테스트 그래프(Code-Test Graph)**를 구축하는 것입니다. 소스 코드의 함수와 테스트 케이스를 노드(Node)로, 호출 관계나 데이터 의존성을 엣지(Edge)로 연결합니다. 이때 단순한 연결이 아니라, 코드 변경 시 특정 테스트가 실패할 확률인 **영향도(Impact Score)**를 가중치로 부여합니다. 이 그래프를 바탕으로 GraphRAG 워크플로우를 수행하면, 에이전트는 전체 테스트 스위트를 실행하는 비용을 들이지 않고도 현재 수정 사항과 가장 관련 높은 테스트들만 타겟팅하여 검증할 수 있습니다.

다음은 TDAD 워크플로우가 어떻게 회귀를 방지하는지 보여주는 간단한 아키텍처입니다.

```javascript
graph TD
    A[Issue Report] --> B[Code Change Plan]
    B --> C[AST Parser]
    C --> D[Graph Construction]
    D --> E[Code-Test Graph]
    E --> F[GraphRAG Query]
    F --> G[Impact Analyzer]
    G --> H[High-Risk Tests]
    H --> I[LLM Coding Agent]
    I --> J[Apply Patch]
    J --> K[Selective Validation]
    K --> L[Success / Regression Check]
```

이 과정에서 에이전트는 무작위로 테스트를 작성하거나 모든 테스트를 실행하는 대신, `Impact Analyzer`가 선별한 '고위험 테스트(High-Risk Tests)'를 집중적으로 검증합니다. 이는 계산 비용을 절감함과 동시에, 회귀가 발생할 가능성이 가장 높은 지점을 사전에 차단하는 안전장치 역할을 합니다.

### 성능 비교 분석

연구진은 SWE-bench Verified 데이터셋을 통해 Qwen 시리즈 모델을 활용해 TDAD의 성능을 측정했습니다. 특히 흥미로운 점은 TDD를 단순히 프롬프트 레벨에서 지시했을 때(Procedural TDD)의 결과입니다. 절차적 지시만으로는 오히려 모델이 불필요한 테스트를 추가하거나 잘못된 경로를 선택하여 회귀율이 9.94%로 증가했습니다.

반면, TDAD는 관련 테스트에 대한 정보를 Context로 제공함으로써 회귀율을 획기적으로 낮추고 문제 해결율까지 높였습니다.

| 접근 방식 | 문제 해결율 (Resolved) | 회귀율 (Regression) | 특징 | | :--- | :---: | :---: | :--- | | 기존 방식 (Baseline) | 24.0% | 6.08% | 일반적인 코딩 에이전트 | | 절차적 TDD (Procedural) | 낮음 | 9.94% | "TDD 방식대로 해"라는 지시만 추가 (성능 저하) | | **TDAD (GraphRAG)** | **32.0%** | **1.82%** | **영향 분석 기반 테스트 제공** |

이 데이터는 작은 규모의 모델(약 30B~35B 파라미터)일수록 "어떻게(How)" 하는지보다 "무엇(What)"을 검증해야 하는지에 대한 정보가 성능에 결정적인 영향을 미침을 시사합니다.

### 실무 구현 가이드: TDAD 워크플로우 적용하기

TDAD의 개념을 실제 MLOps 파이프라인에 통합하기 위해, 파이썬과 NetworkX를 사용한 간단한 영향 분석 시뮬레이션 코드를 작성해 보겠습니다. 이는 실제 TDAD 리포지토리의 로직을 단순화한 것으로, 함수와 테스트 간의 의존성 그래프를 구축하고 변경된 함수에 영향을 받는 테스트를 추출하는 과정을 보여줍니다.

```python
import networkx as nx

def build_dependency_graph(code_changes, test_dependencies):
    """
    코드 변경 사항과 테스트 의존성을 기반으로 영향 분석 그래프 구축
    :param code_changes: 변경된 함수 리스트 (예: ['user_service.py:login', 'auth.py:verify_token'])
    :param test_dependencies: 테스트 파일과 연결된 함수들의 매핑 딕셔너리
    """
    G = nx.DiGraph()
    
    # 노드 추가 (함수 및 테스트)
    for func in code_changes:
        G.add_node(func, type='function')
    
    for test, funcs in test_dependencies.items():
        G.add_node(test, type='test')
        for func in funcs:
            G.add_edge(func, test, weight=1.0) # 기본 가중치 1.0
            
    return G

def get_impacted_tests(G, changed_functions):
    """
    변경된 함수로부터 영향을 받는 테스트를 추출 (Graph Traversal)
    """
    impacted_tests = []
    
    for func in changed_functions:
        if func in G:
            # 해당 함수에서 직접 연결된 테스트 노드 탐색
            neighbors = G.neighbors(func)
            for neighbor in neighbors:
                if G.nodes[neighbor]['type'] == 'test':
                    impacted_tests.append(neighbor)
                    
    return list(set(impacted_tests)) # 중복 제거

# 시나리오: 결제 모듈 수정 시 로그인 테스트 영향 분석
changed_functions = ['payment_gateway.py:process_refund']
test_map = {
    'tests/test_payment.py': ['payment_gateway.py:process_refund', 'payment_gateway.py:charge'],
    'tests/test_user_balance.py': ['payment_gateway.py:process_refund', 'user_service.py:get_balance']
}

G = build_dependency_graph(changed_functions, test_map)
risky_tests = get_impacted_tests(G, changed_functions)

print(f"코드 변경 대상: {changed_functions}")
print(f"검증이 필요한 고위험 테스트: {risky_tests}")
# 출력: 검증이 필요한 고위험 테스트: ['tests/test_payment.py', 'tests/test_user_balance.py']
```

이 코드는 기본적인 아이디어를 보여줍니다. 실제 TDAD 시스템에서는 AST 파싱을 통해 함수 간의 호출(Call graph)뿐만 아니라 변수 참조(Reference graph)까지 분석하여 가중치를 더 정교하게 계산합니다. 실무 적용 시에는 다음 단계를 따르는 것을 권장합니다.

1.  **정적 분석 (Static Analysis)**: 커밋 푸시 시점에 AST 기반 파서를 돌려 코드-테스트 그래프를 업데이트합니다. 2.  **컨텍스트 패킹 (Context Packing)**: AI 에이전트가 코드를 수정하기 전, `get_impacted_tests` 로직을 거쳐 검증해야 할 테스트 리스트를 시스템 프롬프트에 포함합니다. 3.  **셀프-힌팅 (Self-Hinting)**: "당신은 지금 `process_refund` 함수를 수정하려 합니다. 이로 인해 `test_user_balance`와 `test_payment`에 영향을 줄 수 있으니 이를 주의하라"는 맥락을 제공합니다.

### 전문가 인사이트: 절차가 아닌 맥락으로

이 논문의 가장 큰 시사점은 "작은 모델(LMs)의 능력을 끌어올리는 가장 효과적인 방법은 복잡한 사고 과정(Chain of Thought)을 강요하는 것이 아니라, 관련성 높은 정보(Relevant Context)를 제공하는 것"이라는 점입니다. 연구진은 이를 통해 자율 개선 루프(Auto-improvement loop)를 구성했을 때, 문제 해결율을 12%에서 60%까지 끌어올리는 데 성공했습니다.

MLOps 관점에서 볼 때, 이는 에이전트에게 "TDD라는 프로세스를 따르라고 훈련시키는 것"보다, "현재 코드 베이스의 구조적 의존성을 그래프로 추출해 제공하는 도구(Tool)"를 갖추는 것이 훨씬 더 강력하다는 것을 의미합니다. AI에게 방법론을 가르치지 말고, 지도를 쥐여주어야 합니다.

## 결론

TDAD는 AI 코딩 에이전트가 단순히 버그를 수정하는 수준을 넘어, 안정적인 소프트웨어를 유지 관리할 수 있도록 돕는 중요한 이정표입니다. GraphRAG를 활용한 정밀한 영향 분석을 통해, 우리는 에이전트가 야기할 수 있는 회귀 문제를 70%나 감소시킬 수 있었습니다. 특히 절차적인 지시보다는 맥락적 정보 제공이 모델의 성능에 결정적인 도움이 된다는 발견은 향후 AI 에이전트 설계 방향에 시사하는 바가 큽니다.

앞으로의 AI 개발 도구는 모델의 파라미터 크기 경쟁보다는, 코드베이스의 복잡성을 얼마나 잘 그래프로 파악하고 모델에게 제공할 수 있는지에 대한 '컨텍스트 인텔리전스' 경쟁으로 나아갈 것입니다. 연구진이 공개한 [TDAD GitHub](https://github.com/pepealonso95/TDAD) 리포지토리를 통해 여러분의 프로젝트에 이 그래프 기반의 회귀 방지 메커니즘을 도입해 보시기를 강력히 권장합니다.

---

**출처**: [http://arxiv.org/abs/2603.17973v1](http://arxiv.org/abs/2603.17973v1)