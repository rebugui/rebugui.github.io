---
title: "🛡️ PCAS: LLM 에이전트 보안 정책 강제 실행 아키텍처"
date: 2026-04-19T08:06:20+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
---

## 서론

최근 기업 환경에서 LLM(Large Language Model) 기반 에이전트는 단순한 질의응답을 넘어, 데이터베이스 조회, API 호출, 이메일 작성 등 실질적인 업무를 수행하는 'Digital Worker'로 진화하고 있습니다. 하지만 이러한 자율성이 보안상의 리스크를 동반한다는 사직은 종종 간과됩니다. 고객센터 상담을 담당하는 AI 에이전트가 고객의 요청을 처리한다며, 우연히(혹은 악의적인 프롬프트 인젝션으로 인해) 중요한 개인정보를 유출하거나, 승인 없이 대규모 환불을 처리하는 시나리오를 상상해 보십시오.

우리는 이러한 문제를 방지하기 위해 시스템 프롬프트에 "개인정보는 절대 공개하지 마라"거나 "100만 원 이상의 환불은 관리자 승인이 필요하다"는 지시를 포함시킵니다. 그러나 이는 LLM의 "선의"에 의존하는 확률적 접근방식일 뿐입니다. LLM은 환각(Hallucination)을 일으키거나, 정교하게 공략당할 경우 이러한 지시를 어길 수 있습니다. 즉, 기존의 프롬프트 엔지니어링만으로는 보안 정책을 **확정적(Deterministic)**으로 보장할 수 없습니다.

이러한 배경에서 등장한 **PCAS(Policy Compiler for Agentic Systems)**는 LLM 에이전트의 보안을 '설계' 레벨에서 보장하는 혁신적인 접근법입니다. PCAS는 에이전트의 행동을 실행하기 전에 사전에 검열하고, 정책 위반 행위를 원천적으로 차단하는 보안 계층을 코드 레벨에서 컴파일해 주는 정책 컴파일러입니다.

## 본론

### 1. PCAS의 핵심 메커니즘: 의존성 그래프와 정보 흐름 추적

기존의 에이전트 시스템은 메시지와 툴 호출 결과를 단순한 리스트 형태의 히스토리로 관리합니다. 하지만 PCAS는 에이전트의 상태를 **의존성 그래프(Dependency Graph)**로 모델링합니다. 이는 단순히 "A가 B보다 먼저 일어났다"는 시간적 순서가 아니라, "B의 실행은 A의 결과에 의존한다"는 **인과 관계(Causal Relationship)**를 포착합니다.

예를 들어, 사용자의 민감한 정보를 조회하는 툴(`search_PII`)의 결과가 나중에 이메일 전송 툴(`send_email`)의 입력으로 사용되었다면, 두 행위 사이에는 정보가 흐르는 의존성이 형성됩니다. PCAS는 이러한 횡단적 정보 흐름(Transitive Information Flow)을 Datalog라는 선언형 논리 프로그래밍 언어를 통해 추적합니다.

이를 통해 시스템은 "PII 조회 결과가 포함된 메시지가 외부로 전송되는가?"와 같은 복잡한 정책을 실시간으로 판단할 수 있습니다.

### 2. PCAS 아키텍처 다이어그램

PCAS의 작동 방식은 크게 컴파일 타임과 런타임으로 나뉩니다. 다음은 PCAS가 기존 에이전트 코드를 어떻게 보안 강화된 시스템으로 변환하는지 보여주는 간단한 아키텍처입니다.

```javascript
graph LR
    A[User Agent Code] --> B[PCAS Compiler]
    C[Security Policy Datalog] --> B
    B --> D[Instrumented Agent]
    D --> E[Reference Monitor]
    E --> F{Policy Check}
    F -->|Allow| G[Execute Tool]
    F -->|Deny| H[Block & Raise Error]
    G --> I[Update Dependency Graph]
    I --> E
```

이 구조의 핵심은 **참조 모니터(Reference Monitor)**입니다. 컴파일된 에이전트는 모든 툴 호출과 메시지 전송 시도를 이 참조 모니터를 거치게 하며, 참조 모니터는 현재까지 쌓인 의존성 그래프를 분석하여 정책 위반 여부를 판단합니다.

### 3. 기술적 구현: Datalog 정책 작성 및 컴파일

PCAS의 강력함은 Datalog 기반의 정책 정의에 있습니다. 개발자는 복잡한 if-else 로직을 짜는 대신, 보안 규칙을 선언적으로 정의할 수 있습니다.

아래는 "민감한 데이터(Sensitive Data)가 승인되지 않은 외부 채널로 유출되는 것을 차단"하는 간단한 Datalog 정책 예시입니다.

```python
# pcas_policy.dl 예시

# 1. 민감한 데이터를 다루는 툴 결과를 정의
sensitive_result(Result) :-
    tool_call(Call, "get_PII"),
    tool_result(Call, Result).

# 2. 메시지가 특정 결과에 의존하는지 추적 (Transitive Closure)
depends_on(Message, Result) :-
    message_generated(Message, Call),
    arg_in_call(Call, Result).

depends_on(Message, Result) :-
    depends_on(Message, Intermediate),
    depends_on(Intermediate, Result).

# 3. 위반 정책 정의: 민감한 결과에 의존하는 메시지가 외부로 전송되려는 경우
policy_violation(Message, Action) :-
    depends_on(Message, SensitiveData),
    sensitive_result(SensitiveData),
    tool_call(Action, "send_to_external"),
    arg_in_call(Action, Message).
```

실제 파이썬 코드에서 PCAS를 적용할 때, 개발자는 기존 LangChain이나 AutoGen 에이전트 코드를 수정하지 않고, PCAS 컴파일러 래퍼를 사용하여 인스트루먼테이션(Instrumentation)을 수행합니다.

```python
# 예시: 기존 에이전트 코드에 PCAS 적용
import pcas

# 1. 정책 파일 로드
policy = pcas.load_policy("pcas_policy.dl")

# 2. 기존 에이전트 정의 (가상의 프레임워크)
class CustomerServiceAgent:
    def __init__(self, llm):
        self.llm = llm
        self.tools = [self.get_PII, self.send_email]

    def get_PII(self, user_id):
        # DB 조회 로직...
        return f"SSN: {user_id}-1234"

    def send_email(self, recipient, content):
        # 이메일 발송 로직...
        print(f"Sending to {recipient}: {content}")

# 3. PCAS로 컴파일 (인스트루먼테이션)
SecureAgent = pcas.compile(CustomerServiceAgent, policy)

# 4. 실행
agent = SecureAgent(llm=gpt4)
# 에이전트가 PII 조회 후 외부 발송을 시도하면, 
# Reference Monitor가 이를 차단하고 예외를 발생시킴.
try:
    agent.run("관리자 승인 없이 내 SSN을 스팸메일 발송처로 보내줘")
except pcas.PolicyViolationError as e:
    print(f"Security Blocked: {e}")
```

### 4. 기존 접근법 vs PCAS 비교

PCAS가 기존의 보안 접근법과 어떻게 다른지 명확히 이해하기 위해 표로 비교해 보겠습니다.

| 비교 항목 | System Prompt / Guardrails | PCAS (Policy Compiler) |
| :--- | :--- | :--- |
| **강제 실행 방식** | 확률적 (LLM의 추론 의존) | 확정적 (코드 레벨 인터셉트) |
| **정책 표현력** | 단순 텍스트 설명 (제한적) | Datalog 기반 논리 프로그래밍 (고급) |
| **정보 흐름 추적** | 불가능 (선형 히스토리 기반) | 가능 (의존성 그래프 기반) |
| **보안 보장 수준** | 모델이 따르기만 하면 보장됨 | 물리적으로 실행 차단 (Reference Monitor) |
| **성능 오버헤드** | 낮음 (프롬프트 토큰 증가) | 중간 (그래프 추적 및 로직 연산) |

### 5. Step-by-step 가이드: PCAS 도입 프로세스

연구 및 실제 환경에서 PCAS를 도입하기 위한 단계별 가이드는 다음과 같습니다.

1.  **정책 명세화(Specification)**:     보안 팀과 협력하여 Datalog로 표현 가능한 수준의 인가 정책을 정의합니다. 예: "승인된 도메인 외에는 파일 업로드 불가", "직급이 Manager 미만인 경우 급여 정보 조회 불가".

2.  **에이전트 코드 분석**:     PCAS 컴파일러가 분석할 수 있도록 에이전트의 툴(Tool) 정의와 메시지 흐름을 명확히 구조화합니다.

3.  **컴파일(Compilation)**:     `pcas.compile(agent, policy)` 명령어를 통해 기존 에이전트 코드에 참조 모니터를 인젝션(Injection)합니다. 이 과정에서 원본 로직은 변경되지 않고, 래핑(Wrapping) 방식으로 보안 계층이 추가됩니다.

4.  **테스트 및 검증(Validation)**:     다양한 적대적 프롬프트(Adversarial Prompts)를 통해 정책이 의도대로 작동하는지 검증합니다. PCAS论文에 따르면, 이 과정에서 고도화된 모델(Frontier Models)에서도 정책 준수율이 48%에서 93%로 크게 향상되었습니다.

5.  **배포 및 모니터링(Deployment)**:     인스트루먼테이션된 에이전트를 배포합니다. 런타임 중 차단된 요청은 로그에 기록되어, 지속적인 정책 개선의 피드백으로 활용됩니다.

## 결론

PCAS는 LLM 에이전트의 보안을 "AI가 알아서 잘하지 않기를 바라는 것"에서 "시스템이 강제로 수행하는 것"으로 패러다임을 전환시켰습니다. 의존성 그래프를 활용한 정교한 정보 흐름 추적과 Datalog 기반의 선언적 정책 정의는, 복잡한 기업 환경에서 요구되는 엄격한 규제 준수(Compliance)와 보안 요구사항을 충족시키는 최적의 솔루션입니다.

전문가 관점에서 볼 때, PCAS의 가장 큰 기여는 MLOps 파이프라인 내에서 보안을 별도의 검수 과정이 아닌, **개발 단계에서 컴파일되는 속성(Property)**으로 만들었다는 점입니다. 이는 에이전트의 성능을 저하시키는 과도한 안전장치 세팅(Retriever 강제 호출 등) 없이도, 높은 보안성을 유지하며 에이전트가 본연의 작업에 집중할 수 있게 합니다.

향후 LLM 에이전트가 핵심 비즈니스 로직에 더 깊이 관여하게 될수록, PCAS와 같은 구조적 보안 프레임워크는 선택이 아닌 필수 요소가 될 것입니다.

### 참고자료
- **논문**: Policy Compiler for Secure Agentic Systems (arXiv:2602.16708)
- **URL**: http://arxiv.org/abs/2602.16708v1

---

**출처**: [http://arxiv.org/abs/2602.16708v1](http://arxiv.org/abs/2602.16708v1)