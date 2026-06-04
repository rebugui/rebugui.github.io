---
title: "🤖 LLM Hallucination: 생성형 AI가 거짓말을 하는 기술적 원인 분석"
date: 2026-03-13T07:06:43+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
---

## 서론

최근 실리콘밸리의 한 유명한 법률 사무소에서 파트너 변호사가 ChatGPT를 활용해 선행 판례를 조사하다가 큰 낭패를 본 일이 있었습니다. 모델이 인용한 판례들은 매우 그럴싸한 이름과 판결 내용을 갖추고 있었지만, 실제로는 존재하지 않는 완전한 허구였습니다. 이 변호사는 법정에서 모욕감을 줄 뿐만 아니라 직업적 윤리 문제까지 겪어야 했습니다. 이러한 현상, 즉 모델이 사실이 아닌 내용을 마치 진실인 것처럼 자신 있게 출력하는 행위를 우리는 **환각(Hallucination)**이라 부릅니다.

많은 사용자가 LLM을 방대한 지식을 저장한 데이터베이스, 혹은 진실을 추구하는 지능형 에이전트처럼 착각합니다. 하지만 "The L in LLM Stands for Lying"이라는 논란에서 볼 수 있듯이, 이는 근본적인 오해입니다. LLM이 거짓말을 하는 것은 도덕적 결함이 아니라, 모델의 설계 철학이 **'진실의 탐색'이 아니라 '가장 그럴듯한 다음 단어의 예측'**에 있기 때문입니다. 왜 모델은 존재하지 않는 논문을 인용하고, 잘못된 코딩 솔루션을 제시하는 것일까요? 이 글에서는 Transformer 아키텍처의 확률적 메커니즘을 깊이 들여다보며, 환각이 발생하는 기술적 원인을 분석하고자 합니다.

## 본론

### 확률적 패러뷋(Stochastic Parrots)과 다음 토큰 예측

LLM의 핵심은 방대한 텍스트 데이터를 학습하여, 주어진 문맥(Context) 다음에 올 가장 적절한 토큰(Token)을 예측하는 능력입니다. 모델은 "사실"이라는 개념을 이해하는 것이 아니라, 단순히 훈련 데이터의 통계적 패턴을 따를 뿐입니다. 예를 들어, "프랑스의 수도는 ..."이라는 프롬프트가 주어지면, 모델은 수많은 텍스트에서 "파리"가 이 문맥 뒤에 올 확률이 가장 높다는 것을 학습했습니다. 하지만 "고대 로마의 발명품인 스마트폰..."과 같은 존재하지 않는 문맥이 주어지면, 모델은 논리적 사실 여부를 떠나 문맥상 어울리는 단어들을 이어 붙이려 시도합니다. 이것이 환각의 시작점입니다.

다음은 Transformer 모델이 토큰을 생성하는 과정을 단순화하여 나타낸 것입니다. 모델은 과거의 토큰들을 바탕으로 다음 토큰의 확률 분포를 계산하고, 여기서 샘플링하여 결과를 냅니다.

```javascript
graph LR
    A[Input Context] --> B[Transformer Model]
    B --> C[Logit Vectors]
    C --> D[Softmax Probabilities]
    D --> E[Sampling Strategy]
    E --> F[Next Token]
    F --> A
```

### Temperature와 샘플링의 딜레마

환현상을 제어하는 핵심 하이퍼파라미터 중 하나는 **Temperature**입니다. Temperature는 Softmax 함수의 분포를 얼마나 날카롭게 혹은 평평하게 만들지 결정합니다.
- **Low Temperature (< 1.0)**: 확률 분포가 날카로워져 가장 높은 확률의 토큰이 선택될 확률이 매우 높아집니다. 결과는 결정적(Deterministic)이고 반복적이지만, 창의성이 떨어지며, 잘못된 고정 관념을 반복할 위험이 있습니다.
- **High Temperature (> 1.0)**: 확률 분포가 평평해져 낮은 확률의 토큰도 선택될 기회를 얻습니다. 이는 창의적인 글쓰기에 유용하지만, 문맥에 맞지 않는 단어가 섞여 들어가면서 환각 위험이 기하급수적으로 증가합니다.

즉, 우리는 모델이 "똑똑하게 창의적"이길 바라지만, 기술적으로는 '창의성'과 '허구' 사이에 얇은 선만 있을 뿐입니다. 아래 파이썬 코드는 Temperature가 다음 토큰 선택에 미치는 영향을 시뮬레이션합니다.

```python
import torch
import torch.nn.functional as F

def sample_next_token(logits, temperature=1.0, top_k=None):
    """
    Args:
        logits: 모델의 출력 로짓 (batch_size, vocab_size)
        temperature: 샘플링 온도 (낮을수록 보수적, 높을수록 창의적/무작위)
        top_k: 상위 K개 토큰 내에서만 샘플링 (필터링)
    """
    # Temperature scaling
    scaled_logits = logits / temperature
    
    # Top-K filtering (Optional but common)
    if top_k is not None:
        indices_to_remove = scaled_logits < torch.topk(scaled_logits, top_k)[0][..., -1, None]
        scaled_logits[indices_to_remove] = -float('Inf')
    
    # Softmax to probabilities
    probs = F.softmax(scaled_logits, dim=-1)
    
    # Multinomial sampling
    next_token = torch.multinomial(probs, num_samples=1)
    return next_token

# 예시 로짓 (단순화)
logits = torch.tensor([[1.0, 2.0, 10.0]]) # 3번째 토큰 확률이 가장 높음

print("Temp 0.1 (Conservative):", sample_next_token(logits, temperature=0.1))
# 거의 항상 토큰 2 (index 2) 선택

print("Temp 2.0 (Creative/Risky):", sample_next_token(logits, temperature=2.0))
# 토큰 0이나 1이 선택될 가능성 대폭 증가 (Hallucination risk)
```

### 환각의 유형과 원인 분석

모든 환현상이 동일하게 발생하는 것은 아닙니다. 최신 연구 논문들은 환현상을 크게 사실 기반(Factuality Hallucination)과 충실도 기반(Faithfulness Hallucination)으로 구분합니다. 아래 표는 각 유형의 특징을 비교합니다.

| 구분 | 사실 기반 환각 (Fact Hallucination) | 충실도 기반 환각 (Faithfulness Hallucination) |
| :--- | :--- | :--- |
| **정의** | 모델의 내부 지식 혹은 외부 참조와 다르게, 사실이 아닌 내용을 생성함. | 사용자의 제약 조건(Instruction)이나 컨텍스트를 무시하고 내용을 생성함. |
| **예시** | "지구는 평평하다"라고 주장하거나, 존재하지 않는 논문 인용. | "3줄로 요약해달라"는 요청을 무시하고 긴 글을 쓰거나, 특정 스타일 위반. |
| **주요 원인** | 학습 데이터의 노이즈, 잘못된 연관성 학습, Parametric Memory 부재. | Attention 메커니즘의 실패, Long-Context 의존도 부족, Alignment 부재. |
| **해결 방향** | RAG(검색 증강 생성), Knowledge Graph 활용. | Chain-of-Thought prompting, Fine-tuning with instruction data. |

### 기술적 완화 전략: RAG와 Chain-of-Thought

환현상을 완전히 제거하는 것은 불가능에 가깝지만, MLOps 관점에서 이를 최소화하기 위한 아키텍처 전략들이 존재합니다.

**1. 검색 증강 생성 (RAG, Retrieval-Augmented Generation)** 모델이 내부 파라미터에만 의존해 답변하게 만드는 대신, 외부 신뢰할 수 있는 지베이스(Vector DB)에서 관련 문서를 검색하여 컨텍스트로 제공하는 방식입니다. 이는 모델이 "생각해서" 답하는 것을 막고, "읽고" 답하게 유도하여 사실성을 높입니다.

**2. 사고 연쇄 (Chain-of-Thought, CoT)** 모델에게 답변을 바로 내놓으라고 하는 대신, 단계별로 추론 과정을 기술하게 함으로써 논리적 비일관성을 줄이는 방법입니다. "Let's think step by step" 같은 프롬프트가 이에 해당합니다.

아래는 환각을 줄이기 위한 실무 적용 가이드입니다.

### Step-by-Step: 환hallucination 저감 가이드

1.  **프롬프트 엔지니어링 (System Prompt 강화)**     *   모델에게 "모르는 것은 모른다고 대답해라"고 명시적으로 지시합니다.     *   예: `"If you are unsure of the answer, please state that you do not know rather than fabricating information."`

2.  **RAG 파이프라인 구축**     *   사용자 질문 -> Dense Retrieval(Embedding 유사도 검색) -> Top-K 문서 추출 -> Context 구성 -> LLM 생성.     *   중요: 검색된 문서의 출처를 함께 요구하게 하면 모델이 허위 정보 만들 가능성이 더 낮아집니다.

3.  **Self-Consistency (자기 일관성) 검증**     *   동일한 질문에 대해 여러 번 샘플링을 수행합니다. (예: Temperature를 변경하거나 여러 코어를 사용)     *   생성된 답변들 중 다수결로 가장 자주 등장하는 답변을 최종 결과로 채택합니다. 이는 노이즈가 많은 추론을 걸러내는 효과가 있습니다.

## 결론

LLM이 보여주는 환현상은 모델이 고장 난 것이 아니라, **'확률적 언어 모델'이라는 정체성의 그림자**입니다. Transformer는 거짓말을 할 의도가 없지만, 진실을 보장하는 메커니즘 또한 가지고 있지 않습니다. 모델은 주어진 문맥에서 통계적으로 가장 매끄러운 경로를 찾을 뿐이며, 그 경로가 때로는 허구의 영역으로 빠져들 수 있습니다.

우리 연구자들과 엔지니어에게 중요한 것은 이 환현상을 '버그'로 보지 않고, 확률적 시스템의 고유한 특성으로 받아들이는 것입니다. 이를 위해서는 LLM을 전지전능한 오라클(Oracle)이 아닌, **엔지니어링이 필요한 강력하지만 불완전한 구성 요소(Component)**로 다루어야 합니다. RAG, Fine-tuning, 그리고 철저한 Human-in-the-loop 검증 시스템을 통해 이 불완전성을 보완하는 것이 현대 AI 개발의 핵심 과제입니다.

AI가 "거짓말쟁이"가 되지 않게 하려면, 우리는 먼저 그가 "확률계산기"일 뿐이라는 사실을 명심하고 시스템을 설계해야 합니다.

### 참고자료
- [The L in "LLM" Stands for Lying - Acko.net](https://acko.net/blog/the-l-in-llm-stands-for-lying/)
- [Bender, E. M., et al. (2021). "On the Dangers of Stochastic Parrots: Can Language Models Be Too Big?"](https://dl.acm.org/doi/10.1145/3442188.3445922)
- [Wei, J., et al. (2022). "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models."](https://arxiv.org/abs/2201.11903)

---

**출처**: [https://acko.net/blog/the-l-in-llm-stands-for-lying/](https://acko.net/blog/the-l-in-llm-stands-for-lying/)