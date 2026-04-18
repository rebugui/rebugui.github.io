---
title: "🤖 MARS: Margin-Aware Reward Modeling으로 RLHF 견고성 강화"
date: 2026-04-19T08:06:11+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
---

## 서론

최신 생성형 AI 개발의 흐름에서 단순히 사실적인 답변을 생성하는 것을 넘어, 인간의 가치판단과 선호도에 부합하는 '정렬(Alignment)'을 달성하는 것이 가장 중요한 과제로 떠오르고 있습니다. 이를 위해 RLHF(Reinforcement Learning from Human Feedback)가 표준처럼 자리 잡았으며, 이 파이프라인의 핵심 심장부에는 바로 **Reward Model(보상 모델)**이 있습니다. 보상 모델은 "이 답변이 저 답변보다 낫다"는 인간의 피드백을 학습하여, 정책 모델(Policy)을 조정하는 나침반 역할을 수행합니다.

그러나 현실적인 문제에 직면해 있습니다. 보상 모델이 믿을만해지기 위해서는 고품질의 인간 선호 데이터(Preference Pairs)가 필수적이지만, 이를 수집하는 비용은 천문학적이며 데이터의 양에는 한계가 있습니다. 이를 해결하기 위해 연구자들은 데이터 증강(Data Augmentation) 기법을 도입해왔으나, 대다수의 기존 접근 방식은 데이터의 '난이도'를 무시한 채 토큰이나 문장 단위로 무작위 섞기를 수행했습니다. 모델이 이미 잘 구별하는 쉬운 예제를 아무리 많이 늘려봤자 모델의 성능에는 큰 도움이 되지 않는다는 것은 직관적으로도 명확합니다.

여기서 우리의 동기(Motivation)가 시작됩니다. 보상 모델이 가장 불확실해하고 판단하기 어려워하는 '모호한 경계선(Decision Boundary)'에 있는 데이터에 집중적으로 증강을 수행한다면 어떨까요? 이번 아티클에서 다룰 **MARS(Margin-Aware Reward-Modeling with Self-Refinement)**는 바로 이 질문에서 출발했습니다. 모델이 헷갈려하는 Low-margin 데이터를 타겟팅하여 학습 분포를 정제하고, 손실 함수의 곡률을 높여 최적화 조건을 개선하는 과정을 기술적으로 심도 있게 다뤄보겠습니다.

## 본론

### MARS의 기술적 원리와 메커니즘

MARS의 핵심 철학은 **"모델이 확신하지 못하는 곳에서 학습하라"**입니다. 기존의 균등한 데이터 증강(Uniform Augmentation)은 모든 데이터에 동일한 기회를 부여하지만, MARS는 보상 모델의 추정 난이도를 고려하여 적응형(Adaptive)으로 증강을 수행합니다.

여기서 중요한 개념이 바로 **Margin**입니다. Margin은 보상 모델이 '선택된 답변(Chosen)'과 '거절된 답변(Rejected)'의 점수 차이($r_w - r_l$)를 의미합니다. 이 차이가 크다면(High-margin) 모델이 쉽게 구별하는 데이터이고, 차이가 작거나 서로 뒤바뀐다면(Low-margin) 모델이 혼란스러워하는 어려운 데이터입니다. MARS는 이 Low-margin 샘플을 식별하여 이를 변형 및 증강한 뒤 다시 학습 데이터셋에 투입하는 **Self-Refinement(자기 정제)** 루프를 형성합니다.

이론적으로 MARS는 이러한 Hard-sample mining 방식이 손실 함수의 평균 곡률(Average Curvature)을 증가시킴을 보입니다. 곡률이 증가한다는 것은 손실 함수의 표면이 더 뾰족해진다는 의미로, 이는 곧 더 나은 조건 번호(Conditioning)를 제공하여 최적화 과정에서 그래디언트가 더 명확한 방향성을 갖도록 돕습니다.

### MARS 학습 파이프라인

MARS의 전체 작동 과정은 아래와 같이 요약할 수 있습니다. 초기 데이터로부터 보상 모델을 학습시킨 후, 예측이 불확실한 샘플을 필터링하고 이를 증강하여 다시 학습셋에 합치는 순환 구조를 가집니다.

```javascript
graph TD
    A[Raw Preference Data] --> B[Initial Reward Model Training]
    B --> C[Margin Calculation on Training Set]
    C --> D{Margin < Threshold?}
    D -->|Yes Low Margin| E[Targeted Data Augmentation]
    D -->|No High Margin| F[Exclude or Keep Original]
    E --> G[Refined Training Set]
    F --> G
    G --> H[Updated Reward Model]
    H --> C
```

### 기존 방식과의 비교

MARS의 접근 방식이 기존 방식과 어떻게 다른지 명확히 이해하기 위해 표로 비교해 보겠습니다.

| 비교 항목 | 기존 균등 증강 (Uniform Augmentation) | MARS (Margin-Aware Augmentation) | | :--- | :--- | :--- | | **샘플링 전략** | 전체 데이터셋에서 무작위 샘플링 | 낮은 Margin(모호한) 샘플 우선 선별 | | **모델의 추정 난이도 고려** | 고려하지 않음 (Agnostic) | 명시적으로 고려 (Difficulty-aware) | | **손실 함수 곡률** | 변화 없거나 미미 | 평균 곡률 증가 (Better Conditioning) | | **주요 효과** | 단순 데이터 양 증가 | 학습 효율화 및 경계선 명확화 | | **견고성(Robustness)** | 노이즈 데이터에 취약할 수 있음 | 아웃오브 디스트리뷰션(OOD) 성능 향상 |

### 구현 예시: Margin-Aware 필터링 및 증강

파이토치(PyTorch)를 사용하여 MARS의 핵심 아이디어인 Low-margin 샘플 필터링 및 로스 계산을 어떻게 구현할 수 있는지 살펴보겠습니다. 아래 코드는 보상 모델이 예측한 보상 점수를 바탕으로 마진을 계산하고, 임계값 이하의 난이도 높은 샘플만을 선택하는 과정을 보여줍니다.

```python
import torch
import torch.nn.functional as F

def get_reward_scores(model, chosen_ids, rejected_ids, mask=None):
    """
    Reward Model로부터 Chosen과 Rejected 시퀀스의 점수를 추출
    """
    # 각 시퀀스의 마지막 토큰 혹은 특정 위치의 hidden state를 기반으로 점수 계산
    # 실제 구현에서는 모델 아키텍처에 맞게 수정 필요 (예: RM이 head를 반환하는지)
    chosen_logits = model(chosen_ids, attention_mask=mask)
    rejected_logits = model(rejected_ids, attention_mask=mask)
    
    # 간단히 스칼라 점수로 변환 (실제 RM은 보통 linear head를 통과)
    r_chosen = chosen_logits.mean(dim=-1) 
    r_rejected = rejected_logits.mean(dim=-1)
    return r_chosen, r_rejected

def mars_margin_loss(r_chosen, r_rejected, margin_threshold=0.5):
    """
    MARS를 위한 마진 기반 로스 및 필터링 로직
    """
    # 기본적인 Preference Loss (LogSigmoid 혹은 Ranking Loss)
    diff = r_chosen - r_rejected
    # Loss: Rejected 점수보다 Chosen 점수가 높도록 유도
    loss = -torch.mean(F.logsigmoid(diff))
    
    # Margin 계산 (모델의 확신도)
    margins = diff.detach()
    
    # Low-margin 샘플 식별 (마진이 임계값보다 작은 경우)
    # 이 인덱스들을 추후 데이터 증강 타겟으로 사용
    low_margin_indices = torch.where(margins < margin_threshold)[0]
    
    return loss, low_margin_indices, margins

# 사용 예시
# model: 학습된 Reward Model
# batch: chosen_input_ids, rejected_input_ids 포함된 배치
# loss, indices, margins = mars_margin_loss(model(batch.chosen), model(batch.rejected))
# indices를 활용해 해당 데이터만 Augmentation 파이프라인으로 전송
```

이 코드는 학습 루프 내에서 `low_margin_indices`를 추출하고, 해당 인덱스에 해당하는 원본 텍스트 데이터를 증강(Augmentation) 함수에 넣어 새로운 파라피레이징(Paraphrasing)이나 역번역(Back-translation) 등을 수행한 뒤, 이를 다시 데이터셋에 추가하는 방식으로 확장될 수 있습니다.

### 실무 적용을 위한 Step-by-Step 가이드

연구 환경뿐만 아니라 실제 RLHF 파이프라인에 MARS 개념을 접목하기 위한 단계별 가이드입니다.

1.  **베이스라인 모델 학습**: 기존의 SFT(Supervised Fine-Tuning) 모델 위에 간단한 Reward Head를 붙여 인간 선호 데이터로 초기 학습을 진행합니다. 2.  **마진 분석**: 검증 데이터셋이나 학습 데이터셋에 대해 현재 모델의 마진 분포를 시각화합니다. 마진이 0 근처에 쏠려 있는지 확인합니다. 3.  **증강 정책 수립**: Low-mairgin 샘플을 단순히 복제하는 것이 아니라, 의미를 유지하되 표현을 변형하는 증강 기법(LLM을 이용한 리라이팅 등)을 선택합니다. 노이즈가 섞이면 안 되므로 고품질 증강이 필수적입니다. 4.  **Self-Refinement 루프 실행**:     *   에폭이나 단계마다 Low-margin 샘플을 추출합니다.     *   해당 샘플을 증강하여 데이터셋을 업데이트합니다.     *   업데이트된 데이터셋으로 모델을 미세 조정(Fine-tuning)합니다. 5.  **평가**: 단순히 Accuracy가 아니라, Calibration(보정) 오차나 AUC 등 보상 모델의 신뢰성을 측정하는 지표로 확인합니다.

## 결론

MARS(Margin-Aware Reward Modeling)는 제한된 인간 피드백 데이터를 효율적으로 활용하여 보상 모델의 견고성을 극대화하는 우아한 솔루션입니다. 단순히 데이터의 양을 늘리는 것이 아니라, 모델이 '가장 필요로 하는 데이터'를 스스로 찾아내어 학습하는 Self-Refinement 메커니즘을 통해, 우리는 더 적은 리소스로 더 강건한 정렬 시스템을 구축할 수 있습니다.

특히 이 논문이 주는 시사점은 손실 함수의 기하학적 성질(곡률, 조건)을 데이터 구성 전략과 연결했다는 점입니다. 실무자 입장에서, 더 이상 모든 데이터를 똑같이 대우하지 않고, 모델의 현재 능력 수준에 맞춰 난이도를 조절하는 **커리큘럼 학습(Curriculum Learning)**의 관점에서 RLHF 파이프라인을 재고해야 한다는 중요한 인사이트를 얻을 수 있습니다.

향후 LLM 성능을 높이는 것은 거대한 파라미터를 쌓는 것보다, 어떻게 모델이 혼란스러워하는 '앙상블 오류(Confusion)'를 줄여주느냐에 달려 있을 것입니다. MARS는 그 방향성으로 가는 중요한 발걸음입니다.

### 참고자료
- **Paper**: MARS: Margin-Aware Reward-Modeling with Self-Refinement (arXiv:2602.17658)
- **Related Concepts**: RLHF, PPO, Data Augmentation, Hard Example Mining, Loss Landscape

---

**출처**: [http://arxiv.org/abs/2602.17658v1](http://arxiv.org/abs/2602.17658v1)