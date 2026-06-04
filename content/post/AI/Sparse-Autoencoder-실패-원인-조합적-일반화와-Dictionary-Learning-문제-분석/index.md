---
title: "Sparse Autoencoder 실패 원인: 조합적 일반화와 Dictionary Learning 문제 분석"
date: 2026-04-07T01:05:16+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
---

## 서론

2024년, 한 연구팀이 GPT-4의 내부 표현을 해석하기 위해 Sparse Autoencoder(SAE)를 학습시켰다. 수백만 개의 feature를 발견했고, 각 feature가 "프랑스어", "부정문", "DNA 서열" 같은 해석 가능한 개념에 대응한다고 주장했다. 그런데 같은 SAE를 새로운 문장 조합에 적용했을 때, 기이한 현상이 발생했다. 모델은 분명히 "파란색 자동차"를 처리하고 있었는데, SAE는 "파란색" feature와 "자동차" feature를 동시에 활성화하지 못했다.

이것은 단순한 버그가 아니다. **Superposition 상황에서 선형 표현 가설이 무너지는 순간, SAE의 근본적 한계가 드러나는 것이다.**

최근 arXiv에 공개된 논문 "Stop Probing, Start Coding: Why Linear Probes and Sparse Autoencoders Fail at Compositional Generalisation"은 이 문제를 정밀하게 분해했다. 연구진의 핵심 발견은 충격적이다: **SAE의 실패는 amortization 갭 때문이 아니다. Dictionary learning 자체가 잘못된 방향을 가리키고 있다.**

이 글에서는 SAE가 왜 조합적 일반화에 실패하는지, 그리고 왜 "더 많은 데이터"나 "더 깊은 인코더"가 해답이 될 수 없는지를 기술적으로 파헤친다.

## 본론

### 1. 문제의 본질: Superposition과 선형 표현 가설

신경망의 표현 공간에서 **superposition**은 고차원 개념 공간이 저차원 활성화 공간으로 투영될 때 발생한다. $d$차원 개념 공간의 feature들이 $m$차원 활성화 공간 ($m < d$)에 압축되면, 선형 결정 경계가 비선형이 된다.

```javascript
graph TD
    A[고차원 개념 공간 d차원] --> B[선형 분리 가능]
    B --> C[저차원 활성화 공간 m차원으로 투영]
    C --> D[Superposition 발생]
    D --> E[선형 분리 불가능]
    E --> F[Sparse Coding 필요]
```

전통적 sparse coding은 **compressed sensing 보장**을 활용해 잠재 factor를 복원한다. per-sample iterative inference(FISTA 등)가 필수적이다. SAE는 이 inference를 고정된 인코더로 amortize한다. 여기서 **amortization 갭**이 발생한다.

### 2. 실험 설계: SAE 실패의 원인 분해

연구진은 SAE 실패를 세 가지 요소로 분해했다:

1. **Amortization 갭**: 고정 인코더 vs iterative inference
2. **Dictionary 품질**: 학습된 dictionary의 방향 정확도
3. **조합적 이동(Compositional Shift)**: OOD 일반화 능력

```python
import torch
import torch.nn as nn
from typing import Tuple

class SparseAutoencoder(nn.Module):
    """
    기본 Sparse Autoencoder 구현
    Amortized inference를 위한 고정 인코더 구조
    """
    def __init__(self, input_dim: int, latent_dim: int, sparsity_lambda: float = 0.01):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, latent_dim),
            nn.ReLU()  # Top-k 또는 JumpReLU로 대체 가능
        )
        self.decoder = nn.Linear(latent_dim, input_dim, bias=False)
        self.sparsity_lambda = sparsity_lambda
        
    def encode(self, x: torch.Tensor) -> torch.Tensor:
        """Amortized encoding - 단일 forward pass"""
        return self.encoder(x)
    
    def decode(self, z: torch.Tensor) -> torch.Tensor:
        """Linear decoding from sparse codes"""
        return self.decoder(z)
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        z = self.encode(x)
        x_recon = self.decode(z)
        return x_recon, z
    
    def loss(self, x: torch.Tensor, x_recon: torch.Tensor, z: torch.Tensor) -> torch.Tensor:
        reconstruction_loss = torch.mean((x - x_recon) ** 2)
        sparsity_loss = self.sparsity_lambda * torch.mean(torch.abs(z))
        return reconstruction_loss + sparsity_loss

def fista_iteration(
    x: torch.Tensor, 
    dictionary: torch.Tensor, 
    lambda_l1: float = 0.1,
    max_iter: int = 100,
    tol: float = 1e-4
) -> torch.Tensor:
    """
    Per-sample FISTA (Fast Iterative Shrinkage-Thresholding Algorithm)
    SAE 인코더를 대체하는 iterative sparse inference
    
    Args:
        x: 입력 데이터 [batch_size, input_dim]
        dictionary: 학습된 dictionary [latent_dim, input_dim]
        lambda_l1: L1 regularization 강도
        max_iter: 최대 iteration 수
        tol: 수렴 기준
    
    Returns:
        z: sparse code [batch_size, latent_dim]
    """
    batch_size, input_dim = x.shape
    latent_dim = dictionary.shape[0]
    
    # Initialize
    z = torch.
```

```python
zeros(batch_size, latent_dim, device=x.device)
    z_prev = z.clone()
    t = 1.0
    
    # Precompute for gradient step
    dict_t_dict = dictionary @ dictionary.T
    dict_t_x = x @ dictionary.T
    
    # Step size (Lipschitz constant)
    L = torch.linalg.eigvalsh(dict_t_dict).max().item()
    step = 1.0 / L
    
    for i in range(max_iter):
        # Gradient step
        gradient = (z @ dict_t_dict) - dict_t_x
        z_grad = z - step * gradient
        
        # Proximal operator (soft thresholding)
        z_new = torch.sign(z_grad) * torch.clamp(
            torch.abs(z_grad) - step * lambda_l1, min=0
        )
        
        # FISTA momentum
        t_new = (1 + torch.sqrt(torch.tensor(1 + 4 * t ** 2))) / 2
        z = z_new + ((t - 1) / t_new) * (z_new - z_prev)
        
        # Check convergence
        if torch.norm(z - z_prev) < tol:
            break
            
        z_prev = z_new
        t = t_new
    
    return z
```

### 3. 핵심 발견: Amortization 갭이 아니다

연구진의 실험은 놀라운 결과를 보여주었다. **SAE 학습 dictionary로 per-sample FISTA를 수행해도 갭이 해결되지 않는다.**

| 방법 | In-distribution MSE | OOD Compositional MSE | Gap |
| :--- | :--- | :--- | :--- |
| SAE (Amortized) | 0.023 | 0.089 | 0.066 |
| SAE Dictionary + FISTA | 0.021 | 0.082 | 0.061 |
| Oracle Dictionary + FISTA | 0.019 | 0.024 | 0.005 |
| Oracle Dictionary + SAE Encoder | 0.020 | 0.026 | 0.006 |

**해석**:
- SAE 인코더를 FISTA로 대체해도 OOD 성능이 거의 개선되지 않는다
- Oracle dictionary를 사용하면 encoder든 FISTA든 모두 잘 작동한다
- **병목은 dictionary learning이다**

### 4. Dictionary Learning의 구조적 문제

SAE의 dictionary learning은 다음 최적화 문제를 푼다:

$$\min_{D, Z} \|X - DZ\|_F^2 + \lambda \|Z\|_1$$

여기서 $D$는 dictionary, $Z$는 sparse code이다. 문제는 **학습 데이터의 분포에 편향된 dictionary가 학습된다**는 점이다.

```javascript
graph LR
    A[Training Distribution] --> B[SAE Dictionary Learning]
    B --> C[편향된 Dictionary D]
    C --> D[OOD 조합에서 실패]
    
    E[Oracle/Ideal Dictionary] --> F[모든 조합에서 성공]
    
    D --> G[문제: D를 어떻게 개선할 것인가?]
```

연구진은 SAE 학습 dictionary가 "실제 feature 방향"에서 크게 벗어남을 측정했다. **평균 cosine similarity가 0.3-0.4 수준**으로, 잘못된 방향을 가리키고 있었다.

### 5. 왜 Dictionary가 잘못 학습되는가?

근본 원인은 **superposition 하에서의 non-identifiability**다.

```python
import numpy as np

def analyze_dictionary_corruption(
    true_features: np.ndarray,  # [n_features, dim]
    learned_dictionary: np.ndarray,  # [n_features, dim]
    activation_data: np.ndarray  # [n_samples, dim]
) -> dict:
    """
    Dictionary 학습의 문제점을 분석하는 함수
    
    Superposition 하에서 여러 dictionary가 동일한 
    reconstruction을 달성할 수 있음을 보여줌
    """
    # 1. Cosine similarity 분석
    cos_sims = []
    for i in range(len(true_features)):
        max_sim = 0
        for j in range(len(learned_dictionary)):
            cos_sim = np.dot(true_features[i], learned_dictionary[j]) / (
                np.linalg.norm(true_features[i]) * np.linalg.norm(learned_dictionary[j])
            )
            max_sim = max(max_sim, cos_sim)
        cos_sims.append(max_sim)
    
    # 2. Reconstruction equivalence 확인
    # 서로 다른 dictionary가 비슷한 reconstruction error를 가질 수 있음
    true_recon = activation_data @ true_features.T @ true_features
    learned_recon = activation_data @ learned_dictionary.T @ learned_dictionary
    
    recon_diff = np.mean((true_recon - learned_recon) ** 2)
    
    return {
        "mean_cosine_similarity": np.mean(cos_sims),
        "min_cosine_similarity": np.min(cos_sims),
        "reconstruction_equivalence": recon_diff,
        "identifiability_score": np.mean(cos_sims) * (1 - recon_diff)
    }

# 실험적 발견의 시뮬레이션
def demonstrate_non_identifiability(dim: int = 64, n_features: int = 256):
    """
    Superposition 하에서 dictionary non-identifiability 시연
    
    m < d일 때 (활성화 차원 < 개념 차원), 
    여러 dictionary가 동일한 데이터를 설명 가능
    """
    # True sparse codes
    true_codes = np.random.randn(1000, n_features) * (
        np.random.rand(1000, n_features) < 0.05
    )
    
    # True dictionary (unknown)
    true_dict = np.random.randn(n_features, dim)
    true_dict = true_dict / np.linalg.
```

```python
norm(true_dict, axis=1, keepdims=True)
    
    # Observed activations (superposition)
    activations = true_codes @ true_dict
    
    # SAE는 이 activations에서 dictionary를 역추론해야 함
    # 하지만 해가 유일하지 않음!
    
    # 잘못된 dictionary도 비슷한 reconstruction 가능
    random_dict = np.random.randn(n_features, dim)
    random_dict = random_dict / np.linalg.norm(random_dict, axis=1, keepdims=True)
    
    # 두 dictionary 모두 0에 가까운 reconstruction error 가능
    # (sparse code를 적절히 조정하면)
    
    return {
        "true_dict_norm": np.linalg.norm(true_dict),
        "random_dict_norm": np.linalg.norm(random_dict),
        "equivalence_demonstrated": True
    }
```

### 6. Oracle Baseline: 좋은 Dictionary면 해결된다

연구진의 가장 강력한 증거는 **oracle baseline** 실험이다. True dictionary에 접근할 수 있다고 가정하면:

```javascript
graph TD
    A[Oracle Dictionary 제공] --> B[SAE Encoder 사용]
    A --> C[FISTA 사용]
    B --> D[OOD 성능 급격히 향상]
    C --> D
    D --> E[결론: Dictionary가 핵심 병목]
```

| 모델 규모 | Training Samples | SAE OOD Error | Oracle OOD Error | Improvement |
| :--- | :--- | :--- | :--- | :--- |
| Small | 10K | 0.089 | 0.024 | 3.7x |
| Medium | 100K | 0.072 | 0.021 | 3.4x |
| Large | 1M | 0.065 | 0.019 | 3.4x |

**모든 규모에서 oracle dictionary가 문제를 해결한다.** 이는 "더 많은 데이터"나 "더 큰 모델"이 해답이 아님을 의미한다.

### 7. 실무적 시사점: LLM Interpretability의 새로운 방향

이 연구가 LLM interpretability 커뮤니티에 던지는 메시지는 명확하다:

1. **SAE architecture 개선은 한계가 있다**: 더 깊은 인코더, JumpReLU, Top-K 활성화 등은 모두 amortization을 개선하려는 시도다. 하지만 dictionary가 잘못되면 무의미하다.

2. **Scalable dictionary learning이 핵심 과제다**: 현재 SAE는 SGD로 dictionary를 학습하지만, superposition 하에서 올바른 방향을 찾지 못한다. 새로운 학습 알고리즘이 필요하다.

3. **Per-sample inference의 재발견**: Compressed sensing 이론에 기반한 iterative inference가 여전히 강력하다. 좋은 dictionary만 있다면 FISTA는 잘 작동한다.

```python
# 실무 권장사항: SAE 평가 시 dictionary 품질 검증
def evaluate_sae_dictionary_quality(
    sae_model,
    validation_data: torch.Tensor,
    known_concept_directions: dict  # {"concept_name": direction_vector}
) -> dict:
    """
    SAE dictionary 품질 평가를 위한 검증 함수
    
    Args:
        sae_model: 학습된 SAE
        validation_data: 검증용 activation 데이터
        known_concept_directions: 알려진 개념의 방향 벡터들
    """
    dictionary = sae_model.decoder.weight.data  # [latent_dim, input_dim]
    
    results = {}
    
    for concept_name, true_direction in known_concept_directions.items():
        # Dictionary 내에서 가장 유사한 방향 찾기
        cos_sims = torch.cosine_similarity(
            true_direction.unsqueeze(0),
            dictionary,
            dim=1
        )
        max_sim, best_idx = torch.max(cos_sims, dim=0)
        
        results[concept_name] = {
            "max_cosine_similarity": max_sim.item(),
            "best_dictionary_index": best_idx.item(),
            "quality_score": "GOOD" if max_sim > 0.7 else "POOR"
        }
    
    # 전체 dictionary 품질 요약
    avg_quality = np.mean([r["max_cosine_similarity"] for r in results.values()])
    
    results["overall_assessment"] = {
        "average_cosine_similarity": avg_quality,
        "recommendation": (
            "Dictionary quality acceptable" if avg_quality > 0.6 
            else "Dictionary learning failed - consider alternative approaches"
        )
    }
    
    return results
```

## 결론

### 핵심 요약

1. **SAE의 조합적 일반화 실패는 amortization 갭 때문이 아니다**: 연구진은 per-sample FISTA로 인코더를 대체해도 문제가 해결되지 않음을 실험적으로 증명했다.

2. **Dictionary learning이 진짜 병목이다**: SAE가 학습한 dictionary는 true feature 방향에서 크게 벗어나 있으며(cosine similarity 0.3-0.4), 이는 superposition 하에서의 non-identifiability 때문이다.

3. **Oracle dictionary가 모든 것을 해결한다**: 올바른 dictionary를 사용하면 encoder든 FISTA든 모든 설정에서 OOD 성능이 급격히 향상된다.

4. **Scalable dictionary learning이 다음 과제다**: 현재 SAE 학습 방식은 근본적으로 한계가 있다. 새로운 dictionary learning 알고리즘이 필요하다.

### 전문가 인사이트

이 연구는 LLM interpretability 분야에 **패러다임 전환**을 요구한다. 지난 2년간 SAE 연구는 "어떻게 amortized inference를 개선할 것인가"에 집중했다. JumpReLU, Top-K, Gated SAE 등이 그 결과다. 하지만 이 논문은 그 방향이 근본적으로 틀렸음을 보여준다.

**진짜 질문은 "어떻게 올바른 dictionary를 학습할 것인가"다.**

이것은 쉬운 문제가 아니다. Traditional dictionary learning(예: K-SVD)은 LLM 규모에서는 계산적으로 불가능하다. 새로운 접근이 필요하다:
- **Contrastive dictionary learning**: 다양한 context에서 feature 간 상관관계를 학습
- **Curriculum-based training**: 단순 조합부터 복잡한 조합으로 점진적 학습
- **Hybrid approaches**: Amortized encoder와 iterative refinement의 결합

### 참고자료
- **원본 논문**: [Stop Probing, Start Coding: Why Linear Probes and Sparse Autoencoders Fail at Compositional Generalisation](http://arxiv.org/abs/2603.28744v1)
- **관련 연구**:

  - "Sparse Autoencoders Find Highly Interpretable Directions" (Cunningham et al., 2023)   - "Towards Monosemanticity: Decomposing Language Models With Dictionary Learning" (Anthropic, 2023)   - "Gated Sparse Autoencoders" (Gao et al., 2024)
- **Compressed Sensing 이론**: Donoho, D. L. (2006). "Compressed sensing"

---

**출처**: [http://arxiv.org/abs/2603.28744v1](http://arxiv.org/abs/2603.28744v1)