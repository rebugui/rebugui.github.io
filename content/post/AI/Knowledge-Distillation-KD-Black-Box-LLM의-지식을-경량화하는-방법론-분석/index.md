---
title: "Knowledge Distillation (KD): Black-Box LLM의 지식을 경량화하는 방법론 분석"
date: 2026-07-06T14:27:50+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
---

## 서론

최근 몇 년간 대규모 언어 모델(LLM)은 인공지능 연구의 패러다임을 근본적으로 변화시켰습니다. GPT-4, Llama 3와 같은 거대 모델들은 방대한 파라미터 수와 학습 데이터를 통해 인간 수준을 뛰어넘는 추론 능력과 생성 능력을 입증했습니다. 그러나 이러한 '거대함'은 곧 실질적인 서비스 환경에서의 가장 큰 병목 지점(Bottleneck)이 됩니다. 즉, 엄청난 **Inference Latency**와 막대한 **운영 비용(Operational Cost)**입니다.

실무에서 우리는 종종 최첨단 LLM을 사용하고 싶지만, 다음과 같은 제약에 부딪힙니다.
1.  **비용 문제**: API 호출당 수십 달러의 비용이 발생할 때, 모든 요청을 거대 모델로 처리하기는 어렵습니다.
2.  **접근성 및 유연성 부족**: LLM 자체가 블랙박스 형태로 제공되어 있어 내부 구조에 접근하거나 특정 레이어만 수정하여 파인튜닝(Fine-tuning)하는 것이 불가능한 경우가 많습니다.

이러한 문제 상황에서, **Knowledge Distillation (KD)**은 가장 효과적이고 혁신적인 해결책으로 떠오르고 있습니다. KD는 단순히 모델을 압축하는 것을 넘어, 거대한 '선생님(Teacher)' 모델이 학습 과정에서 습득한 복잡하고 미묘한 지식을 작고 효율적인 '학생(Student)' 모델에게 전달하여, 학생 모델이 선생님의 성능을 거의 그대로 재현하도록 만드는 방법론입니다. 본 글에서는 블랙박스 LLM 환경에서의 KD 원리를 심층 분석하고 실무 적용 방법을 제시합니다.

## 지식 증류의 원리: 블랙박스에서 학생으로

KD의 핵심 아이디어는 '지식을 직접 복사하는 것'이 아니라, '지식의 표현 방식(Representation)'을 전달하는 것입니다. 기존의 모델 학습은 주로 최종 출력 레이어의 **하드 타겟(Hard Target)**에 집중합니다. 하드 타겟이란, 정답 토큰(예: 다음 단어가 'apple'일 확률 1.0)만을 나타내는 이산적인 값입니다. 하지만 KD는 여기에 더해진 부가적인 정보인 **소프트 타겟(Soft Target)**을 활용하여 지식을 전달합니다.

### Soft Targets와 Temperature Scaling

선생님 모델이 출력하는 확률 분포를 보면, 정답 토큰 외에도 다른 후보 토큰들(예: 'orange', 'banana')에 대한 상대적 확률값(0.01, 0.05)이 포함되어 있습니다. 이 값들이 바로 Soft Target이며, 이는 선생님 모델이 "정답은 apple이지만, orange도 상당히 유력한 선택지"라는 복잡한 추론 과정을 담고 있음을 의미합니다.

KD는 여기에 **Temperature Scaling ($\tau$)**이라는 기법을 적용하여 이 확률 분포를 더욱 부드럽게 만듭니다. $\tau$ 값을 높이면(예: 5.0), 모든 토큰의 확률 분포가 더 균일하게 퍼지면서, 정답이 아닌 후보 토큰들 간의 미묘한 관계성(Relative Knowledge)이 강조됩니다. 이 '부드러워진' 지식이야말로 학생 모델에게 전달해야 할 핵심 정보입니다.

**Mermaid 다이어그램: KD 프로세스 흐름도**

```javascript
graph LR
    A[Input Prompt] --> B{"Teacher LLM (Black Box)"}
    B --> C(Soft Target Distribution)
    C --> D{"Temperature Scaling ($\tau$)"}
    D --> E[Student Model Training]
    E --> F[Final Student Output]
```

## KD 방법론 심층 분석: 왜 지식 전달이 중요한가?

블랙박스 LLM 환경에서 KD를 적용하는 것은 단순한 모델 압축 이상의 의미를 가집니다. 선생님 모델의 파라미터가 고정되어 있어 역전파(Backpropagation)를 통해 직접적인 기울기(Gradient) 정보를 얻기 어렵거나, 혹은 특정 레이어에만 접근하여 지식을 추출하고 싶을 때 KD는 필수적입니다.

| 비교 항목 | 표준 Fine-Tuning (FT) | Knowledge Distillation (KD) |
| :--- | :--- | :--- |
| **선생님 모델 상태** | 가중치 고정 또는 업데이트 가능 | 가중치가 완전히 고정됨 (Black Box) |
| **학습 목표** | 하드 타겟(Hard Target) 일치에 집중 | Soft Target 및 Hard Target 동시 일치 |
| **주요 손실 함수** | Cross-Entropy Loss ($L_{CE}$) | KD Loss ($\alpha L_{KD} + (1-\alpha) L_{CE}$) |
| **효율성/비용** | 높음 (전체 모델 학습 필요) | 매우 높음 (최적화된 Student만 학습) |
| **지식 전달 방식** | 기울기(Gradient)를 통한 직접적인 가중치 조정 | 확률 분포(Soft Target) 매칭을 통한 간접적 지식 주입 |

KD는 특히 $L_{KD}$ 항에 집중함으로써, 학생 모델이 단순히 정답만 맞추는 것을 넘어, 선생님처럼 '왜 이 토큰이 정답인지'에 대한 내부적인 추론 근거를 학습하게 만듭니다. 이는 일반적인 FT 대비 훨씬 더 풍부하고 견고한 지식을 습득하는 결과를 낳습니다.

## 실무 적용 가이드: Black-Box LLM 경량화 3단계

실제 MLOps 파이프라인에서 블랙박스 LLM을 활용하여 KD를 수행하는 과정은 다음과 같은 단계로 진행됩니다. 이 과정은 모델 자체의 구조에 접근할 수 없지만, API 호출을 통해 지식(Soft Target)을 추출할 수 있기 때문에 가능합니다.

### Step 1: 지식 데이터셋 구축 및 Soft Target 추출

먼저, 학생 모델이 학습해야 할 대표적인 프롬프트/입력 데이터셋 $D$를 준비합니다. 이 데이터를 선생님 LLM에 입력하고, 원하는 출력 토큰까지의 **확률 분포(Logits)**를 추출합니다. 이때 온도 $\tau$ 값을 설정하여 Soft Target을 생성합니다.

### Step 2: KD 손실 함수 계산 (Loss Calculation)

학생 모델 $S$가 예측한 확률 분포와 선생님 모델 $T$가 제공한 Soft Target 분포 간의 차이를 측정하는 것이 핵심입니다. 흔히 사용되는 것은 **KL Divergence**를 기반으로 한 KD Loss($L_{KD}$)입니다.

$$ L_{KD} = \tau^2 \cdot D_{KL}(P_T(\mathbf{z}) || P_S(\mathbf{z})) $$ *여기서 $P_T$와 $P_S$는 선생님과 학생의 Soft Target 분포이며, $\mathbf{z}$는 토큰입니다.*

### Step 3: Student 모델 최적화 및 배포

학생 모델은 일반적인 Cross-Entropy Loss($L_{CE}$) 외에 계산된 KD Loss를 함께 최소화하도록 학습됩니다. 최종 손실 함수 $L$는 가중치 $\alpha$를 사용하여 결합됩니다: $$ L = \alpha L_{KD} + (1-\alpha) L_{CE} $$

**개념 설명용 코드 예시 (PyTorch)** 아래 코드는 KD Loss 계산의 핵심 로직을 보여줍니다. `temperature`가 바로 $\tau$ 역할을 수행합니다.

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

# Teacher와 Student 모델에서 나온 Logits (확률 분포 전 단계)
teacher_logits = torch.randn(1, 50)  # Batch size=1, Vocab size=50
student_logits = torch.randn(1, 50)

temperature = 3.0 # Temperature Scaling factor (tau)

def calculate_kd_loss(teacher_logits, student_logits, temperature):
    """
    Knowledge Distillation Loss를 계산합니다.
    KL Divergence를 사용하며, 온도 제곱($\tau^2$)으로 스케일링합니다.
    """
    # 1. Soft Targets (확률 분포) 생성: Logit / Temperature
    soft_teacher_probs = F.softmax(teacher_logits / temperature, dim=-1)
    soft_student_probs = F.softmax(student_logits / temperature, dim=-1)

    # 2. KL Divergence 계산 (Soft Target 간의 차이 측정)
    kl_divergence = F.kl_div(
        F.log_softmax(student_logits / temperature, dim=-1), # Student의 Log Probability
        soft_teacher_probs,                                    # Teacher의 Soft Probability
        reduction='batchmean'
    )

    # 3. KD Loss 반환 (Temperature 제곱으로 스케일링)
    kd_loss = kl_divergence * (temperature ** 2)
    return kd_loss

# 손실 계산 및 출력
kd_loss_value = calculate_kd_loss(teacher_logits, student_logits, temperature)
print(f"Calculated KD Loss: {kd_loss_value.item():.4f}")
```

## 결론

Knowledge Distillation은 블랙박스 LLM의 잠재력을 현실 세계에 구현하는 데 있어 가장 강력한 도구 중 하나입니다. 이는 단순히 모델 크기를 줄이는 '압축'을 넘어, 거대 모델이 가진 복잡하고 정교한 추론 과정—즉, **Soft Target으로 표현된 지식**—을 학생에게 효과적으로 주입함으로써 성능 저하를 최소화합니다.

KD는 LLM을 실시간 서비스에 배포하는 MLOps 파이프라인의 핵심 단계이며, 비용 효율성과 응답 속도를 획기적으로 개선하여 상용화의 문턱을 낮춥니다. 앞으로의 연구 방향은 단순히 출력 레이어만 매칭하는 것을 넘어, **레이어별 특징(Feature-wise)** 또는 **Attention 메커니즘** 자체를 전달하는 하이브리드 KD 방법론에 집중될 것으로 예상됩니다.

KD는 LLM 시대의 '지식 전송 프로토콜'이며, 이 기술을 숙련되게 활용하는 것이 곧 차세대 AI 시스템 설계 능력이라 할 수 있습니다.

--- **📚 참고 자료**
- Knowledge Distillation of Black-Box Large Language Models (arXiv:2401.07013): [https://arxiv.org/abs/2401.07013](https://arxiv.org/abs/2401.07013)
- HackerNews Discussion: [https://news.ycombinator.com/item?id=48712420](https://news.ycombinator.com/item?id=48712420)

---

**출처**: [https://arxiv.org/abs/2401.07013](https://arxiv.org/abs/2401.07013)