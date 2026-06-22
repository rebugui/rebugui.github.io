---
title: "Lie-Algebra Attention: 토큰을 Group Element로 정의하여 LLM 성능 극대화하기"
date: 2026-06-22T12:17:42+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
---

## 서론: 벡터 토큰의 한계를 넘어서 - LLM에 기하학적 직관을 부여하다

대규모 언어 모델(LLM)은 방대한 텍스트 데이터를 처리하며 놀라운 성능을 보여주고 있지만, 그 내부에서 정보를 인코딩하는 방식, 즉 '토큰' 자체는 여전히 단순한 실수 벡터($\mathbb{R}^d$)로 정의되어 있습니다. 이 벡터 토큰들은 단어의 의미론적 유사성(Semantic Similarity)을 잘 포착하지만, 물리적인 공간이나 구조를 가진 데이터—예를 들어 이미지 내 객체의 회전, 3D 모델의 변환, 혹은 시퀀스 내 사건의 상대적 자세—와 같은 **기하학적 관계(Geometric Relationship)**를 표현하는 데는 근본적인 한계를 가집니다.

일반적으로 기존 트랜스포머 어텐션은 $Q \cdot K^T$ 형태의 스코어를 계산하며, 이 과정에서 토큰의 상대적 위치나 변환 정보가 *학습된 커널(Learned Kernel)*을 통해 간접적으로 주입됩니다. 하지만 이 방식은 다음과 같은 문제를 야기합니다: 1) 기하학적 불변성(Invariance)이 완벽하게 보장되지 않으며, 2) 복잡한 비콤팩트 군(Non-compact Groups)의 특성을 완전히 포착하는 데는 막대한 수의 파라미터를 요구합니다.

본 연구에서 제안하는 **Lie-Algebra Attention**은 이 문제를 정면으로 해결하며, 토큰을 단순 벡터가 아닌 **행렬 리 군($G$)의 원소 $g_i$**로 재정의함으로써 LLM에 내재적이고 수학적으로 엄밀한 기하학적 직관을 부여합니다.

## 본론: Lie-Algebra Attention의 메커니즘과 성능 분석

### 1. 토큰의 리 군(Lie Group) 정의와 상대 자세 (Relative Pose)

기존 방식에서 $i$번째 토큰이 벡터 $\mathbf{v}_i \in \mathbb{R}^d$였다면, Lie-Algebra Attention에서는 이 토큰이 행렬 $g_i \in G$의 원소입니다. 여기서 $G$는 SE(2), SO(3), Aff(2)와 같은 변환을 정의하는 Matrix Lie Group이며, $g_i$는 순수한 '변환 그 자체'를 나타냅니다.

두 토큰 $g_i$와 $g_j$ 사이의 관계는 **쌍별 상대 자세(Pairwise Relative Pose)** $g_{ij} = g_i^{-1} g_j$로 정의됩니다. 이 행렬은 $g_i$에서 $g_j$로 이동하기 위해 필요한 순수한 변환을 나타냅니다.

핵심적인 혁신은 이 상대 자세를 Lie 대수(Lie Algebra) $\mathfrak{g}$의 원소인 **로그($\log$) 맵**을 통해 추출하는 것입니다: $$w_{ij} = \log(g_i^{-1} g_j)$$

$w_{ij}$는 토큰 간의 기하학적 거리를 나타내는 내재적인 벡터이며, 이 자체가 바로 쌍별 불변량(Pairwise Invariant)이 됩니다. 즉, 두 토큰 $g_i$와 $g_j$가 다른 컨텍스트에서 사용되더라도 그들의 상대적인 변환 관계는 항상 동일하게 유지됩니다.

### 2. 어텐션 스코어 계산: 대수 노름 기반의 근접성 커널

Lie-Algebra Attention은 이 불변량 $w_{ij}$를 사용하여 직접적으로 어텐션 스코어를 계산합니다. 기존 방식처럼 별도의 복잡한 MLP 레이어를 통과시키거나, 특정한 표현론적 도구(Irreducible Representations)를 사용할 필요가 없습니다. 대신, **대수 노름($\text{Algebra Norm}$)을 기반으로 한 닫힌 형식(Closed-form) 스코어**를 사용합니다.

$$\text{Score}_{ij} = s_{ij} = -\frac{\|\log(g_i^{-1} g_j)\|_{\lambda}^2}{\tau}$$

여기서 $\|\cdot\|_{\lambda}$는 블록 가중치 Frobenius 내적을 사용하는 노름이며, $\tau$는 스케일링 팩터입니다. 음의 제곱 대수 노름은 두 토큰이 얼마나 '가까운지'를 측정하는 **정준 근접성 커널(Canonical Proximity Kernel)** 역할을 수행합니다.

#### Lie-Algebra Attention 작동 흐름 (Mermaid Diagram) 다음 다이어그램은 일반적인 트랜스포머와 Lie-Algebra Attention의 스코어 계산 과정을 비교하여 보여줍니다.

```javascript
graph TD
    A[Token $g_i$] --> B{Relative Pose: $g_{ij} = g_i^{-1} g_j$}
    B --> C["Log Map: $w_{ij} = \log(g_{ij})$"]
    C --> D[Algebra Norm Calculation: $\|w_{ij}\|_{\lambda}^2$]
    D --> E{Score: $s_{ij} = -\|w_{ij}\|_{\lambda}^2 / \tau$}
```

### 3. 성능 분석 및 비교 (Table)

Lie-Algebra Attention의 가장 강력한 장점은 그 효율성과 수학적 엄밀성입니다. 특히 SE(2), SO(3), Aff(2)와 같은 비콤팩트 군에서 기존 방법론들이 도달하지 못했던 어파인 풀-프레임 그룹을 완벽하게 커버합니다.

| 비교 항목 | Vector Token Attention (Baseline) | MLP Kernel Attention (Learned) | Lie-Algebra Attention (Proposed) |
| :--- | :--- | :--- | :--- |
| **토큰 정의** | $\mathbf{v}_i \in \mathbb{R}^d$ | $\mathbf{v}_i \in \mathbb{R}^d$ | $g_i \in G$ (Matrix) |
| **스코어 계산 방식** | $Q K^T$ (선형 변환 후 내적) | MLP 레이어를 통한 비선형 매핑 | 닫힌 형식 대수 노름 ($\ |
| \log(\cdot)\ | _{\lambda}^2$) | **파라미터 효율성** | 기준 (1x) |
| 높음 (기준 대비 50~80x) | 극도로 낮음 (MLP 대비 50~80x 적은 스코어 파라미터) | **기하학적 불변성** | $10^{-5}$ ~ $10^{-12}$ 수준의 오차 발생 가능 |
| 학습에 의존, 비교적 높음 | 수학적으로 **완벽히 보장 (Tautological)** | **커버 가능한 군** | 주로 Compact Group 중심 |
| 다양하나 복잡한 비콤팩트 그룹은 어려움 | Affine Full-Frame Groups 완벽 커버 |  |  |

### 4. 실무 구현 가이드: SE(2)에서의 스코어 계산 예시 (Step-by-step)

SE(2)는 평면상의 회전(Rotation, $\text{SO}(2)$)과 병진(Translation)을 결합한 군입니다. $g_i$는 다음과 같은 형태를 가집니다: $$g = \begin{pmatrix} R & t \ 0 & 1 \end{pmatrix}$$

우리는 두 토큰 $g_i, g_j$의 스코어를 계산하는 과정을 PyTorch 스타일로 구현해 보겠습니다.

**Step 1: 상대 자세 행렬 계산 ($g_{ij}$)** $$g_{ij} = g_i^{-1} g_j$$

**Step 2: 로그 매핑 적용 ($w_{ij}$) 및 대수 노름 추출** SE(2)의 경우, $\log$ 맵은 간단한 변환을 통해 이루어지며, $w_{ij}$는 회전 각도($\theta$)와 병진 벡터($\mathbf{t}$)를 포함하는 $\mathbb{R}^3$ 벡터가 됩니다.

**Step 3: 스코어 계산 ($s_{ij}$)** 대수 노름은 $w_{ij} = (\theta, t_x, t_y)^T$에 대해 $\|\cdot\|_{\lambda}^2 = \theta^2 + t_x^2 + t_y^2$ (단순 Frobenius norm)로 계산됩니다.

```python
import torch
import numpy as np

# 가상의 SE(2) 토큰 행렬 정의 (R: 2x2 Rotation, t: 1x2 Translation)
# g = [[cos(theta), -sin(theta), tx], [sin(theta), cos(theta), ty], [0, 0, 1]]

def calculate_lie_algebra_score(g_i: torch.Tensor, g_j: torch.Tensor, tau: float = 1.0) -> torch.Tensor:
    """
    Lie-Algebra Attention 스코어를 계산하는 함수 (SE(2) 가정).
    Args:
        g_i, g_j: 각각의 토큰 행렬 (3x3).
        tau: 스케일링 팩터.
    Returns:
        스코어 값 (스칼라 또는 배치 크기).
    """
    # Step 1: 상대 자세 계산 (g_ij = g_i^-1 * g_j)
    g_i_inv = torch.inverse(g_i)
    g_ij = g_i_inv @ g_j

    # SE(2)의 로그 매핑은 행렬에서 벡터로 추출하는 과정입니다.
    # w = [theta, tx, ty]
    cos_r, sin_r = g_ij[0, 0], g_ij[1, 0]
    tx, ty = g_ij[0, 2], g_ij[1, 2]

    # 회전 각도 (theta) 계산: atan2(sin(theta), cos(theta))
    theta = torch.atan2(sin_r, cos_r)

    # Step 2: Lie Algebra Vector w 추출 완료
    w_ij = torch.tensor([theta, tx, ty], dtype=torch.float32)

    # Step 3: 대수 노름 계산 (Frobenius Norm의 제곱)
    algebra_norm_sq = torch.sum(w_ij**2)

    # 최종 스코어 계산
    score_ij = -algebra_norm_sq / tau
    return score_ij

# 예시 토큰 생성: g_i는 (0, 0)에서 회전 30도; g_j는 (1, 0)으로 이동 후 회전 60도
g_i_example = torch.tensor([
    [np.cos(np.pi/6), -np.sin(np.pi/6), 0],
    [np.sin(np.pi/6), np.cos(np.pi/6), 0],
    [0, 0, 1]
])

g_j_example = torch.tensor([
    [np.cos(2*np.pi/6), -np.sin(2*np.pi/6), 1], # R=60deg, tx=1
    [np.sin(2*np.pi/6), np.cos(2*np.pi/6), 0], # ty=0
    [0, 0, 1]
])

# 스코어 계산 실행
score = calculate_lie_algebra_score(g_i_example, g_j_example)
print(f"계산된 Lie-Algebra Score: {score.item():.4f}")
```

## 결론: LLM의 지능을 기하학적 구조로 증강하다

Lie-Algebra Attention은 토큰을 단순한 특징 벡터에서 수학적으로 풍부하고 의미 있는 **군 원소**로 승격시킴으로써, 트랜스포머 아키텍처가 가진 근본적인 표현력 한계를 돌파했습니다. 이 방법론의 핵심 가치는 단순히 성능 향상에 그치지 않고, *수학적 엄밀성*과 *효율성*을 동시에 달성했다는 점입니다.

우리는 닫힌 형식의 대수 노름 스코어를 통해 어텐션 메커니즘을 재정의했으며, 이는 학습된 MLP 커널이 제공하는 성능에 필적하거나 능가하면서도 **50~80배 적은 파라미터**만을 사용합니다. 특히 SE(2), SO(3)와 같은 군에서 벡터 토큰 기반 모델들이 겪는 기하학적 불변성 붕괴 문제를 완벽하게 해결하여, LLM이 시각 정보나 물리적 상호작용을 이해하는 **Embodied AI** 분야에 혁명적인 돌파구를 제공할 것으로 기대됩니다.

결론적으로, Lie-Algebra Attention은 "토큰은 벡터가 아니라 변환이다"라는 단순하지만 강력한 전제를 통해, 생성형 AI 모델의 지능이 단순히 통계적 패턴 매칭을 넘어 **진정한 기하학적 직관**에 도달하는 길을 열어주었습니다.

--- 🔗 **참고 자료:** The Token Is a Group Element: On Lie-Algebra Attention over Matrix Lie Groups (arXiv:2606.20547v1) [http://arxiv.org/abs/2606.20547v1](http://arxiv.org/abs/2606.20547v1)

---

**출처**: [http://arxiv.org/abs/2606.20547v1](http://arxiv.org/abs/2606.20547v1)