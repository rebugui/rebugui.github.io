---
title: "🧪 Superficial Alignment: Task Complexity로 정렬 효과 정의하기"
date: 2026-04-19T08:06:25+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
---

## 서론

대규모 언어 모델(LLM)을 개발하거나 활용하는 연구자라면 한 번쯤은 이런 의문을 품어봤을 것입니다. "도대체 모델은 언제 지식을 배우는 걸까?" 수천억 개의 토큰으로 사전 학습(Pre-training)을 시키고, 그 후 지도 학습(SFT)이나 인간 피드백(RLHF)을 통해 정렬(Alignment) 작업을 거칩니다. 흥미로운 점은 사전 학습 단계에서 이미 모델이 방대한 세상의 지식을 내재하고 있다는 사실입니다. 하지만 우리는 그 지식을 끄집어내기 위해 다시 막대한 비용을 들여 정렬 과정을 수행합니다.

여기서 'Superficial Alignment Hypothesis(SAH, 표면적 정렬 가설)'라는 논쟁이 발생합니다. 이 가설은 "사후 학습(Post-training)은 새로운 지식을 가르치는 것이 아니라, 사전 학습된 지식을 사용하기 쉽게 표면화(Surface)하는 과정에 불과하다"고 주장합니다. 하지만 이는 직관적인 설명일 뿐, 정량적으로 증명된 바가 없어 많은 논쟁의 여지가 있었습니다. "도대체 얼마나 표면적이라는 거지?"라는 비판을 받아온 것입니다.

이번 arXiv 논문 "Operationalising the Superficial Alignment Hypothesis via Task Complexity"은 이 논란에 종지부를 찍기 위해 **'Task Complexity(과업 복잡도)'**라는 새로운 메트릭을 제안합니다. 연구진은 사전 학습된 모델이 갖고 있는 잠재력은 엄청나지만, 그 접근 경로가 기가바이트(GB) 단위의 복잡한 프로그램을 필요로 하는 반면, 사후 학습은 이를 킬로바이트(KB) 수준으로 획기적으로 단축한다는 것을 입증했습니다. 이는 LLM의 성능을 높이는 것이 지식의 주입이 아니라, 접근성(Accessibility)의 최적화임을 시사합니다.

## 본론

### Task Complexity: 과업 복잡도의 정의와 원리

이 논문의 핵심 기여는 추상적인 개념인 '정렬'을 **Kolmogorov Complexity(콜모고로프 복잡도)**의 관점에서 정량화한 것입니다. 논문에서 정의하는 'Task Complexity'란 **"특정 과업에서 목표 성능을 달성하기 위해 필요한 가장 짧은 프로그램의 길이"**를 의미합니다.

쉽게 비유하자면, 거대한 도서관(사전 학습된 모델)이 있다고 가정해 봅시다. 이 도서관에는 모든 책(지식)이 있지만, 색인이 전혀 되어 있지 않습니다. 특정 정보를 찾으려면 도서관 전체를 독파하는 엄청난 노력(복잡한 프로그램)이 필요합니다. 반면, 사후 학습은 이 도서관에 완벽한 목차와 검색 시스템을 설치하는 과정입니다. 이제 우리는 짧은 검색어(간단한 프로그램)만으로도 원하는 지식에 즉시 접근할 수 있습니다.

연구진은 이를 증명하기 위해 수학적 추론(Mathematical Reasoning), 기계 번역(Machine Translation), 지시 따르기(Instruction Following) 등 다양한 벤치마크에서 실험을 진행했습니다. 그 결과, 사전 학습된 모델(Base Model)만으로는 높은 성능을 내기 위한 입력 프로그램의 크기가 기가바이트(GB) 단위로 어마어마하게 컸던 반면, 정렬된 모델(Aligned Model)은 몇 킬로바이트(KB)의 짧은 프로그램(프롬프트)으로도 동일한 성능을 달성함을 확인했습니다.

### 아키텍처: 지식 압축과 접근 경로의 변화

이 과정을 시스템 아키텍처 관점에서 보면, 사전 학습은 '지식 압축(Knowledge Compression)' 과정이며, 사후 학습은 '검색 경로 최적화(Search Path Optimization)' 과정으로 이해할 수 있습니다.

다음 다이어그램은 사전 학습과 사후 학습이 'Task Complexity'에 미치는 영향을 개념적으로 보여줍니다.

```javascript
graph LR
    A[Raw Data] --> B[Pre-training]
    B --> C[Base Model]
    C --> D[High Performance Potential]
    C --> E[High Task Complexity]
    E --> F[Needs GBs of Instructions]
    
    C --> G[Post-training]
    G --> H[Aligned Model]
    H --> I[Realized Performance]
    H --> J[Low Task Complexity]
    J --> K[Needs KBs of Instructions]
```

위 다이어그램에서 볼 수 있듯이, 사전 학습(C)은 높은 성능 잠재력(D)을 제공하지만 복잡도(E)가 매우 높습니다. 반면, 사후 학습(G)을 거친 모델(H)은 동일한 지식을 기반으로 복잡도(J)를 획기적으로 낮추어 실용적인 성능(I)을 가능하게 합니다.

### 성능 비교: Base Model vs. Aligned Model

아래 표는 논문의 실험 결과를 바탕으로 사전 학습 모델과 사후 학습 모델의 특성을 비교한 것입니다. 이는 SAH가 실제로 어떻게 작동하는지를 직관적으로 보여줍니다.

| 비교 항목 | Base Model (Pre-trained only) | Aligned Model (Post-trained) | | :--- | :--- | :--- | | **지식 소스 (Knowledge Source)** | 사전 학습 데이터 (Internet corpus 등) | 동일 (사전 학습 데이터) | | **지식 습득 여부** | 내재하고 있음 (Implicit) | 내재하고 있음 (Implicit) | | **Task Complexity (접근 난이도)** | 극도로 높음 (High) | 현저히 낮음 (Low) | | **필요 프로그램 크기** | 기가바이트 (GB) 수준 (거대한 few-shot 등) | 킬로바이트 (KB) 수준 (간단한 명령) | | **결론** | 지식은 있으나 꺼내 쓰기 어려움 | 지식에 즉시 접근 가능 (Superficial) |

이 표에서 가장 중요한 인사이트는 **"지식은 이미 거기에 있다"**는 점입니다. 우리는 모델에게 새로운 것을 가르치는 것이 아니라, 복잡한 내부 회로를 적절히 자극하는 단축키(Alignment)를 만들어주고 있는 것입니다.

### 구현 예시: Task Complexity 측정 시뮬레이션

논문에서는 Task Complexity를 측정하기 위해 다양한 최적화 기법을 사용하지만, 여기서는 개념을 이해하기 쉽게 PyTorch를 사용하여 **Base Model과 Aligned Model의 요구 입력 크기(Input Context Length)**를 시뮬레이션하는 코드를 작성해 보겠습니다.

실제로 복잡도는 '가장 짧은 프로그램'의 길이로 측정되지만, LLM의 맥락에서 이는 often '성능을 내기 위해 필요한 최소한의 프롬프트 길이'나 '필요한 Few-shot 예제의 양'과 비례합니다.

```python
import torch
import torch.nn as nn

# 시뮬레이션을 위한 가상의 모델 클래스 정의
class HypotheticalLLM(nn.Module):
    def __init__(self, is_aligned=False):
        super().__init__()
        self.is_aligned = is_aligned
        # 모델 파라미터 크기는 동일하다고 가정 (지식량은 같음)
        self.embed_dim = 4096
        
    def calculate_complexity_cost(self, target_accuracy):
        """
        목표 성능을 달성하기 위해 필요한 입력 프로그램의 복잡도(비용)를 계산합니다.
        이는 논문의 'Task Complexity' 개념을 단순화한 것입니다.
        """
        base_complexity = 10000  # 사전 학습 모델의 기본 복잡도 (KB)
        
        if not self.is_aligned:
            # Base Model: 성능을 높이려면 입력이 기하급수적으로 필요함 (GB 단위 시뮬레이션)
            # 복잡한 Reasoning을 위해 거대한 프롬프트 엔지니어링이 필요하다고 가정
            return base_complexity * (target_accuracy ** 2)
        else:
            # Aligned Model: 적은 입력으로도 높은 성능 달성 (KB 단위 유지)
            # Alignment가 검색 경로를 단축시킴
            return base_complexity * (target_accuracy * 0.1)

# 시나리오 설정: 목표 정확도 90% 달성
target_acc = 0.9

# 1. Base Model (Pre-trained only)
base_model = HypotheticalLLM(is_aligned=False)
complexity_base = base_model.calculate_complexity_cost(target_acc)

# 2. Aligned Model (SFT/RLHF applied)
aligned_model = HypotheticalLLM(is_aligned=True)
complexity_aligned = aligned_model.calculate_complexity_cost(target_acc)

print(f"[Task Complexity Analysis]")
print(f"Target Accuracy: {target_acc*100}%")
print(f"-----------------------------------")
print(f"Base Model Complexity:    {complexity_base:,.0f} units (Simulated GBs)")
print(f"Aligned Model Complexity: {complexity_aligned:,.0f} units (Simulated KBs)")
print(f"-----------------------------------")
print(f"Complexity Reduction: {complexity_base / complexity_aligned:.1f}x")
```

이 코드의 실행 결과는 개념적으로 다음과 같습니다. Base Model은 90% 성능을 내기 위해 엄청난 양의 입력(복잡도)을 요구하지만, Aligned Model은 매우 적은 양의 입력으로도 동일한 성능을 냅니다. 이는 실제로 SAH가 주장하는 바와 일치합니다.

### Step-by-Step 가이드: 연구 및 실무 적용 방법

이러한 SAH와 Task Complexity 이론은 실제 연구와 MLOps 파이프라인에 어떻게 적용할 수 있을까요? 다음은 연구자가 이 메트릭을 활용하여 모델의 효율성을 평가하는 단계별 가이드입니다.

1.  **과업 정의 (Task Definition)**:     평가하고자 특정 작업(예: GSM8K 수학 문제 해결, MT 기계 번역)을 명확히 정의하고 성능 지표(예: 정확도, BLEU 점수)를 설정합니다.

2.  **기준선 설정 (Baseline Measurement)**:     사전 학습된 Base Model에 대해 목표 성능을 달성할 때까지 입력 크기(Context Window)나 Few-shot 예제의 개수를 늘려갑니다. 이때 소요되는 총 토큰 수를 초기 복잡도(Initial Complexity)로 기록합니다.

3.  **정렬 수행 및 최적화 (Post-training)**:     SFT(Supervised Fine-Tuning)나 RLHF를 통해 모델을 정렬합니다. 논문에 따르면 이 과정은 모델 내부의 '가장 짧은 경로'를 학습하게 합니다.

4.  **복잡도 재측정 (Re-measurement)**:     정렬된 모델이 동일한 목표 성능을 달성하기 위해 필요한 입력의 크기(예: 0-shot 또는 짧은 instruction)를 측정합니다.

5.  **압축률 계산 (Compression Ratio)**:     `[초기 복잡도 / 정렬 후 복잡도]` 비율을 계산합니다. 이 비율이 클수록 'Superficial Alignment'가 성공적으로 수행되었다고 해석할 수 있습니다. 즉, 모델이 지식을 효율적으로 접근하도록 최적화되었다는 뜻입니다.

## 결론

이 논문은 **"정렬(Alignment)은 모델을 더 똑똑하게 만드는 것이 아니라, 더 사용하기 쉽게 만드는 과정"**임을 수학적으로 명확히 보여주었습니다. Task Complexity라는 새로운 렌즈를 통해 볼 때, 우리가 LLM을 개발하는 과정은 거대한 지식의 데이터베이스를 구축하는 것(Pre-training)과 그 데이터베이스를 쿼리하는 효율적인 API를 만드는 것(Post-training)으로 나눌 수 있습니다.

전문가 입장에서 이 결과는 자원 분배의 중요한 시사점을 줍니다. 무작정 모델의 크기를 키우거나 사전 학습 데이터를 늘리는 것보다, 데이터 품질을 높여 '정렬' 과정에서 복잡도를 얼마나 더 줄일 수 있느냐가 실제 제품의 성능을 좌우하는 핵심 경쟁력이 될 것입니다. 수 킬로바이트의 명령어로 수천억 파라미터의 지식을 제어하는 것이야말로 LLM 연구의 진정한 미래일 것입니다.

**참고자료 (References)**:
- Paper: *Operationalising the Superficial Alignment Hypothesis via Task Complexity* (arXiv:2602.15829)
- Link: [http://arxiv.org/abs/2602.15829v1](http://arxiv.org/abs/2602.15829v1)

---

**출처**: [http://arxiv.org/abs/2602.15829v1](http://arxiv.org/abs/2602.15829v1)