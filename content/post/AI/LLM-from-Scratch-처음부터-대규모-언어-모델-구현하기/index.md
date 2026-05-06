---
title: "LLM from Scratch: 처음부터 대규모 언어 모델 구현하기"
date: 2026-05-07T01:23:45+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
---

## 서론

대규모 언어 모델(LLM)이 우리의 일상과 업무 방식을 송두리째 바꾸어 놓고 있습니다. 하지만 대부분의 사용자와 개발자는 이 강력한 모델을 단순히 API 호출을 통해 '블랙 박스'처럼 사용할 뿐, 내부에서 정확히 어떤 연산이 일어나 다음 토큰을 생성해내는지는 잘 알지 못합니다. 최근 GPT-4나 Claude와 같은 모델의 성능이 압도적이다 보니, "어차피 만들 수도 없고, 만든다 한들 성능을 따라갈 수 없을 것"이라는 생각에 직접 구현을 시도조차 하지 않는 경우가 많습니다.

하지만 고도로 추상화된 라이브러리나 API에만 의존하다 보면, 모델이 왜 특정 방향으로 편향되는지, 혹은 왜 특정 하이퍼파라미터에서 학습이 발산하는지와 같은 근본적인 문제에 직면했을 때 대처할 수 없습니다. Andrej Karpathy의 'Let's build GPT from scratch' 철학처럼, 복잡한 시스템이라도 기초 원리부터 하나씩 쌓아 올려 보면 그 동작 원리는 명확해집니다. 이 글에서는 `angelos-p/llm-from-scratch` 프로젝트와 같은 접근 방식을 통해, 복잡해 보이는 LLM의 핵심인 Transformer 아키텍처를 PyTorch로 직접 구현하며 그 내부 메커니즘을 해부해 보고자 합니다. 이론과 코드의 괴리를 줄이고, 진정한 모델 소유자가 되기 위한 여정을 시작하겠습니다.

## 본론

### Transformer 아키텍처의 해부와 데이터 흐름

LLM의 심장은 바로 Transformer 구조, 그중에서도 디코더(Decoder) 부분입니다. 이 구조가 핵심인 이유는 'Self-Attention' 메커니즘을 통해 입력 시퀀스 내의 모든 토큰 간의 의존성을 효율적으로 계산할 수 있기 때문입니다. RNN(순환 신경망) 계열이 시간 순서대로 정보를 처리하여 병렬화가 어려웠던 반면, Transformer는 시퀀스 전체를 행렬 연산으로 한 번에 처리하여 대규모 데이터셋에서의 학습을 가능하게 했습니다(Vaswani et al., 2017).

모델이 입력을 받아 다음 토큰을 예측하기까지의 과정은 크게 **토큰화(Tokenization)**, **임베딩(Embedding)**, **트랜스포머 블록(Transformer Block)**, **출력 헤드(Output Head)**로 나눌 수 있습니다. 이 과정을 시각적으로 정리하면 다음과 같습니다.

```javascript
graph LR
    A[Input Text] --> B[Tokenizer]
    B --> C[Input IDs]
    C --> D[Embedding & Positional Encoding]
    D --> E[Transformer Block N x Layer]
    E --> F[Layer Norm]
    F --> G[Linear Projection]
    G --> H[Softmax]
    H --> I[Output Probabilities]
```

이 다이어그램은 매우 단순해 보이지만, `Transformer Block` 내부에는 가장 복잡하고 중요한 연산들이 집중되어 있습니다. 여기에는 **Multi-Head Self-Attention(MHSA)**과 **Feed-Forward Network(FFN)**이 포함되며, 각 레이어마다 잔차 연결(Residual Connection)과 층 정규화(Layer Normalization)가 적용됩니다.

### 핵심 구현: Multi-Head Self-Attention

LLM의 성능을 좌우하는 가장 중요한 부분은 Self-Attention입니다. 이는 문장 내의 단어들이 서로 어떻게 관련되어 있는지를 계산하는 메커니즘입니다. 쿼리(Query), 키(Key), 값(Value)이라는 세 가지 행렬을 통해, "현재 단어(Q)가 문맥상 어떤 단어(K)에 주목해야 하는가"를 결정하고 그 정보(V)를 가져옵니다.

다음은 PyTorch를 사용하여 이 핵심 메커니즘을 직접 구현한 코드입니다. 실무에서는 `nn.MultiheadAttention`을 주로 사용하지만, 내부 원리를 이해하기 위해 직접 클래스를 작성해 보겠습니다.

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
import math

class CausalSelfAttention(nn.Module):
    def __init__(self, config):
        super().__init__()
        # 토큰 임베딩 차원의 크기
        self.n_embd = config.n_embd
        # 어텐션 헤드의 개수
        self.n_head = config.n_head
        # 헤드당 차원 크기 (n_embd가 n_head로 나누어떨어져야 함)
        self.head_dim = self.n_embd // self.n_head
        
        # Q, K, V를 위한 선형 투영 (Bias는 주로 제거하여 사용하기도 함)
        self.c_attn = nn.Linear(self.n_embd, 3 * self.n_embd)
        # 출력 투영
        self.c_proj = nn.Linear(self.n_embd, self.n_embd)
        
        # 어텐션 스코어에 적용할 마스킹 (Causal Mask)
        # 미래의 정보를 현재 시점에서 볼 수 없도록 막는 역할
        self.register_buffer("bias", torch.tril(torch.ones(config.block_size, config.block_size))
                                     .view(1, 1, config.block_size, config.block_size))
        
        self.dropout = nn.Dropout(config.dropout)

    def forward(self, x):
        # x의 형태: (Batch, Sequence_Length, Embedding_Dim) -> (B, T, C)
        B, T, C = x.size()
        
        # Q, K, V 계산 (단일 행렬 곱셈으로 효율화)
        qkv = self.c_attn(x)
        q, k, v = qkv.split(self.n_embd, dim=2)
        
        # 멀티 헤드를 위해 (B, T, C) -> (B, n_head, T, head_dim)으로 재구성
        k = k.view(B, T, self.n_head, self.head_dim).transpose(1, 2)
        q = q.view(B, T, self.n_head, self.head_dim).transpose(1, 2)
        v = v.view(B, T, self.n_head, self.head_dim).transpose(1, 2)
        
        # 어텐션 스코어 계산: (Q * K^T) / sqrt(d_k)
        att = (q @ k.transpose(-2, -1)) * (1.0 / math.sqrt(k.size(-1)))
        
        # Causal Mask 적용: 미래 토큰과의 어텐션을 -inf로 만들어 Softmax 후 0이 되도록 함
        att = att.masked_fill(self.bias[:, :, :T, :T] == 0, float('-inf'))
        att = F.softmax(att, dim=-1)
        att = self.dropout(att)
        
        # 가중합: (Attention_Scores) * V
        y = att @ v
        # 헤드 연결: (B, n_head, T, head_dim) -> (B, T, C)
        y = y.transpose(1, 2).contiguous().
```

```python
view(B, T, C)
        
        # 최종 출력 투영
        y = self.c_proj(y)
        y = self.dropout(y)
        return y
```

이 코드는 GPT 스타일의 모델에서 가장 핵심적인 **Causal Attention(인과적 어텐션)**을 구현합니다. `masked_fill` 부분은 "미래의 단어를 미리 보지 못한다"는 언어 모델의 근본적인 규칙을 강제합니다. 이 부분이 빠진다면 모델은 문장 생성이 아니라 전체 문장을 보고 빈칸을 채우는 BERT 스타일의 마스크드 언어 모델(MLM)처럼 동작하게 됩니다.

### 직접 구현 vs 라이브러리 사용: 실무적 관점

모델을 직접 처음부터(Scratch) 구현하는 것은 교육적 가치가 매우 높지만, 실제 프로덕션 환경에서는 효율성과 최적화가 필수적입니다. 두 가지 접근 방식의 장단점을 비교해 보겠습니다.

| 비교 항목 | 직접 구현 (From Scratch) | 라이브러리 활용 (Hugging Face 등) | | :--- | :--- | :--- | | **학습 곡선** | 높음 (수학적 원리, 행렬 연산 이해 필수) | 낮음 (문서 읽고 API 호출만으로 가능) | | **커스터마이징** | 매우 유연함 (아키텍처 변경이 자유로움) | 제한적 (정의된 config 내에서 변경만 가능) | | **디버깅** | 어려움 (low-level 에러 해결 필요) | 상대적으로 쉬움 (community support 활용) | | **성능 최적화** | 직접 구현해야 함 (Flash Attention 등 적용 어려움) | 최적화된 kernel 이미 포함 (XLA, FP8 지원 등) | | **초기 구축 시간** | 김 | 짧음 |

### 단계별 구현 가이드 (Step-by-Step)

실제로 나만의 LLM을 구축하려면 위의 코드를 포함하여 다음과 같은 단계를 거쳐야 합니다.

1.  **데이터 파이프라인 구축**: 텍스트 데이터를 수집하고, Byte Pair Encoding(BPE)와 같은 토크나이저를 학습시켜 텍스트

---

**출처**: [https://github.com/angelos-p/llm-from-scratch](https://github.com/angelos-p/llm-from-scratch)