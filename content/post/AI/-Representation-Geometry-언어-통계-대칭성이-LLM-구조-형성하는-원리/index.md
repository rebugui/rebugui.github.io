---
title: "🧠 Representation Geometry: 언어 통계 대칭성이 LLM 구조 형성하는 원리"
date: 2026-04-19T08:08:51+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
---

## 서론

대규모 언어 모델(LLM)의 내부를 들여다보면 놀라운 현상을 목격합니다. 수만 개의 차원을 가진 잠재 공간(Latent Space)에서 "달력의 월(month)"들이 나타내는 단어 벡터들이 원형(Circle)을 그리며排列되는 것입니다. 1월과 12월이 서로 인접해 있고, 계절 순서대로 표현되는 이 기하학적 구조는 모델이 단순히 텍스트 패턴을 암기한 것이 아니라, 시간이라는 추상적인 개념을 공간적으로 구현했음을 시사합니다.

왜 모델은 이처럼 명료한 기하학적 구조를 학습하게 될까요? 이는 단순한 우연이나 아키텍처의 부작용이 아닙니다. 최근 arXiv에 게재된 논문 "Symmetry in language statistics shapes the geometry of model representations"는 이 현상의 원인이 **언어 통계(Language Statistics)가 가진 '대칭성(Symmetry)'**에 있음을 수학적으로 증명했습니다. 즉, 단어들이 텍스트에서 함께 등장하는 확률 분포가 가진 변환 불변성(Translation Symmetry)이 모델 내부의 표현 기하학을 결정짓는다는 것입니다. 이를 이해하는 것은 블랙박스로 여겨지던 LLM의 해석 가능성(Interpretability)을 높이고, 더 효율적인 학습 방법을 설계하는 데 중요한 열쇠가 됩니다.

## 본론

### 언어 통계의 대칭성과 기하학적 구조의 형성 원리

연구진은 언어 데이터 내의 단어 동시 출현(Co-occurrence) 통계가 특정한 대칭성을 가질 때, 모델의 표현 공간이 어떤 형태를 띠는지 이론적으로 규명했습니다. 여기서 핵심은 **변환 대칭성(Translation Symmetry)**입니다.

예를 들어, "1월"과 "3월"이 동시에 등장할 확률은 "2월"과 "4월"이 동시에 등장할 확률과 매우 유사합니다. 이는 두 단어 사이의 상대적인 시간 간격(간격이 2개월)이 동일하기 때문입니다. 수식으로 표현하면 $P(w_i, w_j) \approx P(w_{i+k}, w_{j+k})$가 성립합니다. 논문은 이러한 대칭성을 가진 공분산 행렬(Covariance Matrix)의 주성분(Principal Components)이 푸리에 기저(Fourier Basis), 즉 사인(Sine)과 코사인(Cosine) 형태를 띠게 됨을 증명했습니다. 이것이 바로 잠재 공간에서 단어들이 원형이나 선형 매니폴드(Manifold)를 형성하는 수학적 근거입니다.

이 과정을 개념적으로 도식화하면 다음과 같습니다.

```javascript
graph LR
    A[Underlying Latent Variable] --> B[Word Generation]
    B --> C[Language Statistics]
    C --> D[Co-occurrence Matrix]
    D --> E[Translation Symmetry]
    E --> F[Model Training]
    F --> G[Geometric Representation]
```

이 다이어그램은 보이지 않는 잠재 변수(예: 시간, 좌표)가 데이터 생성 과정을 거쳐 통계적 대칭성을 만들어내고, 이것이 모델 학습을 통해 결과적으로 기하학적 구조로 응축됨을 보여줍니다.

### Python으로 살펴보는 구조 형성 시뮬레이션

이론을 검증하기 위해, 변환 대칭성을 가진 합성 데이터를 생성하고 이를 PCA(Principal Component Analysis)로 차원 축소했을 때 어떤 형태가 나타나는지 코드로 구현해 보겠습니다. 이는 LLM이 실제로 수행하는 과정의 극히 단순화된 버전입니다.

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

def generate_circular_data(n_points=12, noise_level=0.1):
    """
    변환 대칭성(Translation Symmetry)을 가진 데이터를 생성합니다.
    12개의 월을 원형 위에 배치하고, 인접한 월끼리 유사한 벡터를 갖도록 설정합니다.
    """
    angles = np.linspace(0, 2 * np.pi, n_points, endpoint=False)
    
    # 잠재 공간에서의 원형 구조 (Ground Truth)
    x = np.cos(angles)
    y = np.sin(angles)
    
    # 고차원 벡터로 확장 (예: 100차원)
    dim = 100
    vectors = np.zeros((n_points, dim))
    
    # 각 단어에 해당하는 벡터 생성
    # 인접한 단어(Translationally symmetric)는 유사한 패턴을 가짐
    for i in range(n_points):
        base_signal = np.cos(np.linspace(0, 10, dim) + angles[i])
        vectors[i] = base_signal + np.random.normal(0, noise_level, dim)
        
    return vectors, x, y

# 데이터 생성
vectors, true_x, true_y = generate_circular_data(n_points=12)

# PCA를 이용한 2차원 시각화 (모델이 학습하는 Representation과 유사)
pca = PCA(n_components=2)
reduced_vectors = pca.fit_transform(vectors)

# 시각화
plt.figure(figsize=(10, 5))

plt.subplot(1, 2, 1)
plt.title("Ground Truth Latent Structure")
plt.scatter(true_x, true_y, s=100, c='blue')
for i, (x, y) in enumerate(zip(true_x, true_y)):
    plt.text(x, y, str(i+1), ha='center', va='center', color='white', fontweight='bold')
plt.gca().set_aspect('equal')

plt.subplot(1, 2, 2)
plt.title("Learned Representation (PCA)")
plt.scatter(reduced_vectors[:, 0], reduced_vectors[:, 1], s=100, c='red')
for i, (x, y) in enumerate(zip(reduced_vectors[:, 0], reduced_vectors[:, 1])):
    plt.text(x, y, str(i+1), ha='center', va='center', color='white', fontweight='bold')
plt.gca().set_aspect('equal')

plt.show()
```

이 코드를 실행하면, 모델이 전체적인 분포의 구조(원형)를 학습했음을 확인할 수 있습니다. 이는 LLM이 방대한 텍스트 데이터 속에서 단어 간의 통계적 관계를 파악하여 기하학적 구조를 재구성함을 시사합니다.

### 잠재 변수와 견고성(Robustness)

연구의 또 다른 중요한 발견은 이러한 구조의 **견고성(Robustness)**입니다. 실험 결과, "1월"과 "2월"이 동시에 등장하는 문장을 모두 삭제하여 공기 확률을 인위적으로 파괴하더라도, 모델이 학습한 표현은 여전히 원형 구조를 유지했습니다.

이는 데이터가 단순한 무작위가 아니라, 하나의 **연속적인 잠재 변수(Continuous Latent Variable)**에 의해 통제되기 때문입니다. 비록 특정 직접적인 연결 고리(문장)가 끊어졌다 하더라도, 다른 문맥을 통해 잠재 변수(시간의 흐름)가 추론 가능하기 때문에 모델은 구조를 복원합니다.

다음은 잠재 변수의 존재 유무에 따른 모델 학습 안정성을 비교한 표입니다.

| 비교 항목 | 잠재 변수 존재 (실제 언어) | 잠재 변수 부재 (무작위 섞임) |
| :--- | :--- | :--- |
| **데이터 구조** | Translation Symmetry 존재 | Symmetry 붕괴 |
| **결과 기하학** | 명확한 Circle / Manifold 형성 | 무작위 분포 (Structureless) |
| **노이즈 내성** | 높음 (데이터 손실에도 구조 유지) | 낮음 (약간의 데이터 변경에도 분산) |
| **학습 효율** | 적은 데이터로도 구조 파악 가능 | 많은 데이터 필요해도 구조 파악 불가 |

이 표는 실제 언어 데이터가 가진 구조적 압축성이 왜 LLM의 효율적인 학습을 가능하게 하는지 설명합니다.

### 실무 적용을 위한 가이드: 모델 내부 기하학 분석하기

LLM 연구자나 엔지니어로서 모델이 학습한 개념을 이해하고 싶다면, 다음과 같은 단계를 통해 표현 기하학을 분석해 볼 수 있습니다. 이는 모델의 편향성(Bias)을 진단하거나, 모델이 특정 개념을 올바르게 습득했는지 확인하는 데 유용합니다.

1.  **프롬프트 설계**: 분석하고자 하는 개념(예: 계절, 감정, 정치 성향)에 속하는 단어 리스트를 정의합니다.
2.  **임베딩 추출**: 해당 단어들을 모델에 입력하고, 마지막 히든 레이어의 토큰 임베딩을 추출합니다. (예: LLaMA의 `model.layers[-1]`)
3.  **차원 축소**: PCA, t-SNE, 또는 UMAP을 사용하여 고차원 벡터를 2D 또는 3D 공간으로 축소합니다.
4.  **시각화 및 해석**:     *   축소된 데이터 포인트를 시각화합니다.     *   단어들이 의미론적 순서대로排列되는지(예: 차가움 -> 뜨거움), 또는 군집을 이루는지 확인합니다.     *   회귀 분석(Linear Probe)을 사용하여 특정 축이 어떤 의미(예: x축은 시간, y축은 강도)와 매핑되는지 확인합니다.

이 과정을 통해 "월"이 원형을 그리는지, 아니면 "감정"이 선형 스펙트럼을 형성하는지 식별할 수 있으며, 이는 모델의 개선 방향을 설정하는 데 중요한 피드백이 됩니다.

## 결론

이번 연구는 LLM이 학습하는 표현(Representation)이 데이터의 기하학적 구조를 단순히 반영하는 것을 넘어, 언어 통계가 내재한 대칭성(Translation Symmetry)에 의해 수학적으로 결정됨을 밝혀냈다는 점에서 의의가 큽니다. 단순한 텍스트 예측을 넘어, 모델 내부에는 데이터를 생성한 원인(Latent Variable)의 구조가 그대로 투영된다는 것입니다.

전문가 관점에서 볼 때, 이 발견은 **MLOps와 모델 안전성(Safety)** 측면에서 중요한 시사점을 줍니다. 모델이 학습한 기하학적 구조를 분석함으로써, 우리는 모델이 가진 편향이나 결함을 "직접 볼" 수 있게 됩니다. 또한, 합성 데이터(Synthetic Data)를 생성하여 모델을 학습시킬 때, 원하는 기하학적 구조가 형성되도록 통계적 대칭성을 인위적으로 부여하는 방식으로 학습 효율을 극대화할 수 있을 것입니다.

딥러닝 모델을 블랙박스가 아닌, 우리 세상의 구조를 압축해 놓은 거울이라고 이해한다면, 이 거울을 어떻게 더 깨끗하고 정확하게 만들지 고민하는 것은 연구자들의 몫입니다.

### 참고자료
- **Paper**: [Symmetry in language statistics shapes the geometry of model representations](http://arxiv.org/abs/2602.15029v1)
- **Concepts**: Representation Learning, Word Embeddings, Linear Probe, Manifold Learning

---

**출처**: [http://arxiv.org/abs/2602.15029v1](http://arxiv.org/abs/2602.15029v1)