---
title: "LLM 작동 원리 가이드: Transformer 구조 시각화 분석"
date: 2026-04-29T01:07:10+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
---

## 서론

최근 생성형 AI의 발전으로 인해 ChatGPT나 Claude 같은 대규모 언어 모델(LLM)을 일상에서 자연스럽게 사용하게 되었습니다. 하지만 "다음 토큰을 예측한다"는 단순한 원리가 어떻게 코딩, 창작, 논리적 추론과 같은 복잡한 작업을 수행할 수 있는지에 대해 의문을 가진 개발자들은 여전히 많습니다. 수백만 개의 파라미터와 행렬 곱셈으로 이루어진 이 '블랙박스'를 열어보고 싶어 하지만, 방대한 논문과 수식 앞에서 진입 장벽을 느끼기 일쑤입니다.

특히 실무에서 모델을 배포하거나 파인튜닝할 때, 모델 내부에서 데이터가 어떻게 흐르는지에 대한 직관적인 이해는 필수적입니다. 단순히 API 호출만으로는 디버깅이나 최적화의 한계에 부딪힙니다. Andrej Karpathy의 "Intro to Large Language Models" 강의는 이러한 개념적 격차를 해소하는 데 탁월한 자료이지만, 긴 영상을 다시 보거나 트랜스크립트를 뒤지는 것은 비효율적일 수 있습니다.

이러한 배경에서 탄생한 인터랙티브 시각화 도구는 복잡한 Transformer 구조를 웹상에서 직접 조작하며 이해할 수 있는 기회를 제공합니다. 정적인 그림이나 수식으로는 알기 어려운 'Attention 메커니즘'의 가중치 분포나 '임베딩'의 변화 과정을 눈으로 확인하며 학습할 수 있다는 점에서 이 주제는 매우 중요하며, 딥러닝을 배우는 모두에게 필수적인 학습 자료가 될 것입니다.

## 본문

### Transformer 아키텍처의 핵심 메커니즘

LLM의 심장은 바로 Transformer 구조입니다. 기존의 RNN이나 LSTM이 순차적으로 데이터를 처리하여 병렬 처리가 어렵고 장기 의존성(Long-term dependency)을 잃어버리는 문제가 있었던 반면, Transformer는 'Self-Attention' 메커니즘을 통해 입력 시퀀스 전체를 한 번에 참조할 수 있습니다.

이 과정은 단순히 데이터를 통과시키는 것이 아니라, 문맥(Context)을 이해하는 과정입니다. 모델은 입력된 문장의 각 단어(토큰)가 다른 단어들과 얼마나 관련이 있는지를 '가중치(Attention Score)'로 계산합니다. 예를 들어 "나는 고양이를 좋아해"라는 문장에서 "좋아해"라는 단어를 처리할 때, "고양이"라는 단어에 더 높은 주의를 기울여야 의미를 파악할 수 있습니다.

#### 데이터 처리 흐름 시각화

아래 다이어그램은 사용자가 입력한 텍스트가 Transformer 모델을 통과하여 다음 단어를 예측하기까지의 단순화된 흐름을 보여줍니다. 복잡한 수학적 연산을 제외하고 데이터의 흐름에 집중하면 구조를 훨씬 쉽게 파악할 수 있습니다.

```javascript
graph TD
    A[Input Text] --> B[Tokenizer]
    B --> C[Token IDs]
    C --> D[Embedding Layer]
    D --> E[Positional Encoding]
    E --> F[Transformer Block]
    F --> G[Multi-Head Attention]
    G --> H[Add & Layer Norm]
    H --> I[Feed Forward Network]
    I --> J[Add & Layer Norm]
    J --> K[Linear Layer]
    K --> L[Softmax]
    L --> M[Output Probabilities]
```

### PyTorch로 구현하는 Self-Attention

이론적인 이해를 넘어 실제 코드로 동작 원리를 확인하는 것은 연구자와 엔지니어에게 필수적입니다. 아래는 PyTorch를 사용하여 Transformer의 핵심인 Scaled Dot-Product Attention을 구현한 간단한 예시입니다.

이 코드는 Query($Q$), Key($K$), Value($V$) 행렬 간의 곱셈을 통해 어텐션 맵을 생성하고, 이를 입력에 적용하는 과정을 보여줍니다.

```python
import torch
import torch.nn.functional as F

def scaled_dot_product_attention(query, key, value, mask=None):
    d_k = query.size(-1)
    
    # 1. Q와 K의 내적을 통해 유사도 점수 계산
    scores = torch.matmul(query, key.transpose(-2, -1)) / torch.sqrt(torch.tensor(d_k, dtype=torch.float32))
    
    # 2. 마스킹 (예: 패딩 처리 또는 디코더의 미래 토큰 가리기)
    if mask is not None:
        scores = scores.masked_fill(mask == 0, -1e9)
    
    # 3. Softmax를 통해 확률 분포(가중치) 변환
    attention_weights = F.softmax(scores, dim=-1)
    
    # 4. 가중치를 Value에 곱하여 최종 출력 계산
    output = torch.matmul(attention_weights, value)
    
    return output, attention_weights

# 예시 시퀀스 (배치 크기 1, 시퀀스 길이 3, 임베딩 차원 4)
x = torch.randn(1, 3, 4)

# 선형 변환을 통해 Q, K, V 생성 (실제로는 학습 가능한 가중치 행렬 사용)
W_q = torch.randn(4, 4)
W_k = torch.randn(4, 4)
W_v = torch.randn(4, 4)

Q = torch.matmul(x, W_q)
K = torch.matmul(x, W_k)
V = torch.matmul(x, W_v)

# 어텐션 수행
result, weights = scaled_dot_product_attention(Q, K, V)

print("Output Shape:", result.shape)
print("Attention Weights:
", weights[0])
```

이 코드를 실행하면 `attention_weights` 텐서를 통해 모델이 현재 단어를 예측할 때 입력 시퀀스의 어떤 부분에 집중하고 있는지 수치적으로 확인할 수 있습니다. 인터랙티브 시각화 도구는 이러한 텐서 값을 시각적 히트맵(Heatmap)으로 제공하여 직관적인 해석을 돕습니다.

### 아키텍처 비교: RNN vs Transformer

Transformer가 등장하기 전까지 자연어 처리(NLP)를 주도했던 RNN 계열과 Transformer를 비교하면 왜 현재의 LLM들이 Transformer를 선택하는지 명확히 알 수 있습니다. 특히 MLOps 관점에서 학습 속도와 효율성은 결정적인 차이를 만듭니다.

| 비교 항목 | RNN (LSTM/GRU) | Transformer (LLM) |
| :--- | :--- | :--- |
| **연산 방식** | 순차적 (Sequential) | 병렬적 (Parallel) |
| **장기 의존성** | 멀리 있는 정보 전달 어려움 (Vanishing Gradient) | Attention 메커니즘으로 직접 참조 가능 |
| **학습 속도** | 느림 (이전 타임스텝 기다려야 함) | 빠름 (전체 시퀀스 동시 처리 가능) |
| **주요 용도** | 시계열 데이터, 간단한 Sequence-to-Sequence | 대규모 언어 모델, 생성형 AI |

### 단계별 학습 및 디버깅 가이드

Karpathy의 강의 기반 시각화 툴이나 직접 구현한 코드를 활용하여 LLM을 깊이 있게 이해하려면 다음 단계를 따르는 것을 권장합니다.

1.  **토크나이저 이해 (Tokenizer)**: 모델은 단어가 아닌 정수(Integer) 형태의 토큰을 입력받습니다. BPE(Byte Pair Encoding) 같은 알고리즘이 문장을 어떻게 쪼개는지 확인하는 것이 첫 번째 단계입니다.
2.  **임베딩 공간 탐색**: 단어가 고차원 벡터 공간에 어떻게 매핑되는지 살펴봅니다. 유사한 의미를 가진 단어들이 벡터 공간상에서 가까이 위치하는지 확인해 보세요.
3.  **어텐션 맵 분석**: 특정 문장을 입력했을 때, 모델이 예측에 있어 어떤 단어에 높은 가중치를 두었는지 시각화된 맵을 통해 분석합니다. 이를 통해 모델이 문맥을 제대로 파악하는지 확인할 수 있습니다.
4.  **다음 토큰 예측 (Next Token Prediction)**: 최종 Softmax 레이어에서 나온 확률 분포를 확인합니다. Top-k sampling이나 Temperature 설정이 결과 생성에 어떤 영향을 미치는지 실험해보세요.

### 실무 적용 팁: 추론 최적화

대규모 모델을 서빙할 때는 생성 과정의 효율성이 중요합니다. Transformer 구조에서는 **KV-Cache** 기술이 널리 사용됩니다. 토큰을 하나 생성할 때마다 이전 모든 토큰에 대한 Key와 Value 행렬을 다시 계산하는 것은 비효율적입니다. KV-Cache는 이전 단계에서 계산된 K와 V를 캐싱하여, 새로운 토큰 생성 시 마지막 토큰의 Query와 캐싱된 K, V만 연산하여 속도

---

**출처**: [https://ynarwal.github.io/how-llms-work/](https://ynarwal.github.io/how-llms-work/)