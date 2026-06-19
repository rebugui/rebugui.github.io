---
title: "SpecKV: LLM 추론 가속을 위한 압축 인식 Gamma 선정"
date: 2026-05-07T01:23:46+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
draft: true
---

## 서론

최근 생성형 AI 서비스를 운영하는 엔지니어라면 한 번쯤은 딜레마에 빠져봤을 것입니다. 사용자에게 더 빠른 응답 속도(latency)를 제공하기 위해 모델 양자화(Quantization)를 적용해 FP16이나 INT8, 심지어 NF4 수준으로 압축하는 것은 필수적이 되었습니다. 하지만 메모리 효율을 얻기 위해 추론 정확도를 일부 포기하는 과정에서, 기존의 고속화 기술인 '추측 디코딩(Speculative Decoding)'의 효율이 급격히 떨어진다는 사실을 간과하기 쉽습니다.

추측 디코딩은 작은 Draft 모델이 먼저 토큰을 제안(Draft)하고, 큰 Target 모델이 이를 검증(Verify)하는 방식입니다. 이때 한 번에 제안할 토큰의 개수인 $\gamma$(Gamma)가 성능을 좌우하는 핵심 하이퍼파라미터입니다.业界에서는 보통 편의상 $\gamma=4$로 고정해서 사용합니다. 하지만 압축된 모델은 검증 단계에서 토큰 기각률(Rejection Rate)이 높아지기 때문에, 무조건 많이 제안하는 것이 오히려 독이 됩니다. 즉, 모델의 압축 수준과 현재 문맥의 난이도에 따라 '적당한' $\gamma$는 실시간으로 달라져야 합니다.

이번 글에서는 이러한 문제를 해결하기 위해 제안된 **SpecKV(Speculative Decoding with Compression-Aware Gamma Selection)** 기술을 깊이 있게 분석해보겠습니다. SpecKV는 단순한 휴리스틱을 넘어, Draft 모델의 엔트로피와 신뢰도를 실시간으로 모니터링하여 단계별로 최적의 $\gamma$를 동적으로 결정하는 적응형 컨트롤러입니다.

## 본론

### 기술적 배경 및 원리: 왜 고정된 Gamma는 비효율적인가?

기존의 추측 디코딩 시스템은 Target 모델의 압축 레벨(FP16, INT8, NF4)과 무관하게 고정된 $\gamma$ 값을 사용합니다. 연구진은 4가지 작업 유형과 3가지 압축 레벨, 4가지 $\gamma$ 값 조합으로 총 5,112개의 스텝 레벨 데이터를 프로파일링했습니다. 그 결과, 놀라운 사실이 발견되었습니다. 최적의 $\gamma$ 값은 압축 레벨에 따라 크게 변한다는 점입니다.
- **FP16 (고정밀도)**: 모델이 정확하므로 Draft 모델의 토큰을 높은 확률로 수락합니다. 따라서 $\gamma$를 크게(예: 8~16) 잡아도 이득이 큽니다.
- **NF4 (고압축)**: 모델의 정보 손실로 인해 검증 실패 확률이 높습니다. 이 경우 $\gamma$를 크게 잡으면 연속으로 토큰이 기각되어 디코딩 속도가 오히려 느려집니다. 작은 $\gamma$(예: 2~4)가 유리합니다.

SpecKV의 핵심 아이디어는 **Draft 모델의 출력 통계(Draft Statistics)**가 Target 모델의 수락률(Acceptance Rate)을 예측하는 강력한 신호라는 점입니다. 구체적으로, Draft 모델이 다음 토큰에 대해 얼마나 확신하는지(Confidence)와 출력 분포가 얼마나 불확실한지(Entropy)를 측정합니다.

### SpecKV 아키텍처 및 메커니즘

SpecKV는 매 추론 스텝마다 다음과 같은 과정을 거쳐 최적의 $\gamma$를 결정합니다. 이 과정은 매우 가볍기 때문에 전체 추론 시간에 미치는 오버헤드는 0.34ms 미만입니다.

```javascript
graph TD
    A[Input Prompt] --> B[Draft Model]
    B --> C[Collect Draft Statistics]
    C --> D[Calculate Confidence & Entropy]
    D --> E[SpecKV Controller MLP]
    E --> F[Select Optimal Gamma]
    F --> G[Generate K Tokens]
    G --> H[Target Model Verification]
    H --> I[Accept Tokens]
    H --> J[Resample if Rejected]
    I --> K[Output]
    J --> L[Next Token]
```

1.  **Draft Model**: 소형 모델이 후보 토큰 시퀀스를 생성합니다.
2.  **Feature Extraction**: 생성된 토큰의 소프트맥스 확률 분포에서 **Confidence (최대 확률값)**와 **Entropy (불확실성)**를 계산합니다.
3.  **SpecKV Controller (MLP)**: 이 값들과 현재 압축 레벨(Quantization Type)을 입력으로 받아, 기대 수락 토큰 수를 최대화하는 $\gamma$를 예측합니다.
4.  **Verification**: Target 모델이 결정된 $\gamma$ 만큼의 토큰을 검증합니다.

### 성능 비교: 고정 Gamma vs SpecKV

SpecKV가 제공하는 유연성은 실제 성능 수치에서 명확하게 드러납니다. 아래 표는 다양한 압축 환경에서 SpecKV가 고정된 $\gamma=4$ 방식 대비 얼마나 더 효율적인지를 보여줍니다.

| 비교 항목 | Fixed Gamma ($\gamma=4$) | SpecKV (Adaptive) | 성능 향상율 |
| :--- | :--- | :--- | :--- |
| **FP16 (High Precision)** | Baseline | +32% | 높은 신뢰도로 인해 $\gamma$를 6~8로 자동 증가 |
| **INT8 (Medium Precision)** | Baseline | +48% | 균형적인 $\gamma$ 조절 (4~6) |
| **NF4 (High Compression)** | Baseline | +56% | 낮은 신뢰도 반영하여 $\gamma$를 2~3으로 축소 |
| **평균 오버헤드** | 0 ms | 0.34 ms | 전체 추론 시간의 0.5% 미만 |

이 결과는 통계적으로도 매우 유의미하며($p < 0.001$), 특히 압축률이 높아질수록 SpecKV의 효과가 극대화됨을 알 수 있습니다.

### 구현 가이드: SpecKV와 호환되는 추론 루프

실제 MLOps 파이프라인에 SpecKV를 통합하기 위해서는 추론 루프 내에 가벼운 로직을 추가해야 합니다. 아래는 PyTorch 기반으로 SpecKV의 의사결정 로직을 단순화하여 구현한 예제 코드입니다.

```python
import torch
import torch.nn as nn

class SpecKVController(nn.Module):
    def __init__(self, input_dim=3, hidden_dim=64, max_gamma=8):
        super().__init__()
        self.mlp = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, max_gamma + 1) # Output logits for each possible gamma
        )
        self.max_gamma = max_gamma

    def forward(self, draft_logits, quant_level_onehot):
        """
        draft_logits: (batch, vocab_size) - Draft model's output logits
        quant_level_onehot: (batch, 3) - One-hot encoded [FP16, INT8, NF4]
        """
        # 1. Calculate Draft Confidence (Max Prob)
        probs = torch.softmax(draft_logits, dim=-1)
        confidence, _ = torch.max(probs, dim=-1) # (batch,)
        
        # 2. Calculate Draft Entropy
        entropy = -torch.sum(probs * torch.log(probs + 1e-9), dim=-1) # (batch,)
        
        # 3. Construct Input Vector [Confidence, Entropy, Quant_Level_Scaled]
        # Note: In actual paper, quant level is passed as separate feature or one-hot concatenated
        # Simplified here for logic demonstration
        x = torch.stack([confidence, entropy, quant_level_onehot[:, 0].float()], dim=-1)
        
        # 4. Predict Best Gamma
        gamma_logits = self.mlp(x) # (batch, max_gamma + 1)
        predicted_gamma = torch.argmax(gamma_logits, dim=-1) # (batch,)
        
        return predicted_gamma

# Usage Example in Inference Loop
def inference_step_with_speckv(target_model, draft_model, controller, input_ids, quant_type):
    # 1. Draft Generation
    with torch.no_grad():
        draft_logits = draft_model(input_ids)
    
    # 2. Prepare Quantization Feature (Mockup)
    quant_map = {'FP16': [1.0, 0.0, 0.0], 'INT8': [0.0, 1.0, 0.0], 'NF4': [0.0, 0.0, 1.0]}
    quant_feat = torch.tensor([quant_map[quant_type]]).unsqueeze(0) # (1, 3)
    
    # 3.
```

```python
 Decide Gamma dynamically
    gamma = controller(draft_logits[:, -1, :], quant_feat).item() # Use last token's logits
    
    # 4. Speculative Decoding Step with decided Gamma
    # ... (Target verification logic using 'gamma') ...
    print(f"Current Quant: {quant_type}, Selected Gamma: {gamma}")
    
    return gamma, input_ids # Return updated ids
```

이 코드는 SpecKV의 �

---

**출처**: [http://arxiv.org/abs/2605.02888v1](http://arxiv.org/abs/2605.02888v1)