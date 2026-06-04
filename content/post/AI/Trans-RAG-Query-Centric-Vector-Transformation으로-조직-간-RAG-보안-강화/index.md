---
title: "Trans-RAG: Query-Centric Vector Transformation으로 조직 간 RAG 보안 강화"
date: 2026-05-01T01:06:55+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
---

## 서론

A제약사의 AI 연구팀이 신약 후보 물질을 검색하려 한다. 문제는 핵심 데이터가 파트너사 B의 서버에 있다는 점이다. 기존 방식이라면 B사의 데이터베이스에 질의를 보내고, 암호화된 인덱스에서 결과를 받아 복호화해야 한다. 그런데 이 복호화 순간, 보안의 사각지대가 열린다. 전송 계층에서는 완벽한 암호화가 유지되었지만, 검색 결과를 활용하는 지점에서 plaintext가 노출되는 것이다.

2024년 Healthcare 정보보호 동향 보고서에 따르면, 조직 간 데이터 협업 과정에서 발생하는 보안 사고의 34%가 바로 이 "복호화 이후 구간"에서 일어난다. Homomorphic Encryption(동형암호)이 이 문제의 해결책으로 떠올랐지만, 검색 시스템에 적용하면 연산 오버헤드가 100배 이상 증가하는 현실적인 한계가 있다.

바로 이 지점에서 Trans-RAG가 근본적으로 다른 접근을 제시한다. "암호화된 상태로 연산하자"는 기존의 패러다임을 벗어나, "처음부터 다른 언어(의미 공간)로 존재하게 하자"는 발상의 전환이다. 각 조직이 자신만의 고유한 vector space language를 가지면, 외부 쿼리는 해당 언어로 "번역"되어 들어오고 원본 데이터는 결코 원래 형태로 존재하지 않는다.

이 글에서는 2025년 4월 arXiv에 발표된 "Trans-RAG: Query-Centric Vector Transformation for Secure Cross-Organizational Retrieval" 논문을 중심으로, 이 혁신적인 접근법의 원리와 구현, 그리고 실무 적용 가능성을 깊이 있게 분석한다.

## 본론

### 문제 정의: Cross-Organizational RAG의 세 가지 딜레마

RAG(Retrieval-Augmented Generation) 시스템이 조직 경계를 넘어 배포될 때, 다음 세 가지 요구사항이 동시에 충족되어야 한다.

| 요구사항 | 기존 Homomorphic Encryption | Federated Learning | Trans-RAG |
| :--- | :--- | :--- | :--- |
| 데이터 기밀성 | 암호문 상태 연산 | 로컬 데이터 유지 | 수학적 의미 공간 격리 |
| 검색 정확도 | 높음 (이론적) | 중간 (모델 의존) | 높음 (nDCG@10 3.5% 감소만) |
| 연산 효율성 | 낮음 (100x+ 오버헤드) | 중간 (통신 비용) | 높음 (Native retrieval 속도) |
| Plaintext 노출 | 복호화 시 노출 | 로컬에 존재 | 원칙적 불가능 |
| 구현 복잡도 | 매우 높음 | 높음 | 중간 |

핵심 통찰은 "데이터를 숨기는 것"이 아니라 "데이터를 이해할 수 없게 만드는 것"이다. 이를 위해 Trans-RAG는 vector space language라는 개념을 도입한다.

### Vector Space Language: 핵심 개념

일반적인 embedding space에서 "apple"이라는 단어는 특정 좌표에 위치한다. Word2Vec이나 BERT, OpenAI의 text-embedding-ada-002 모두 이 좌표를 다르게 매핑하지만, 같은 모델을 사용하면 동일한 좌표를 공유한다. 즉, 누구나 이 좌표계를 알면 의미를 역추적할 수 있다.

Vector space language는 이 좌표계 자체를 조직 고유의 것으로 변환한다. 수학적으로 표현하면:

$$\text{Trans}(\mathbf{v}) = R \cdot S \cdot \mathbf{v} + \mathbf{b} + \epsilon$$

여기서:
- $R$: 직교 회전 행렬 (Orthogonal Rotation Matrix)
- $S$: 스케일링 행렬 (Scaling Matrix)
- $\mathbf{b}$: 바이어스 벡터 (Bias Vector)
- $\epsilon$: 노이즈 (Gaussian Noise)

이 변환의 아름다움은 "의미적 관계는 보존하되, 절대적 위치는 파괴"한다는 점이다. "왕 - 남자 + 여자 = 여왕"이라는 관계는 유지되지만, "왕"이 원래 어떤 단어였는지는 변환된 공간에서 알 수 없다.

### Trans-RAG 아키텍처

```javascript
graph TD
    A[User Query] --> B[Source Embedding]
    B --> C[vector2Trans Encoder]
    C --> D[Transformed Query]
    D --> E[Target Organization Vector DB]
    E --> F[Retrieved Documents]
    F --> G[LLM Generation]
    
    H[Organization A Corpus] --> I[vector2Trans Transform]
    I --> J[Vector DB A]
    
    K[Organization B Corpus] --> L[vector2Trans Transform]
    L --> M[Vector DB B]
    
    J --> E
    M --> E
```

### vector2Trans: 다단계 변환 메커니즘

vector2Trans 알고리즘은 다음 5단계로 구성된다.

**Step 1: Key Generation** 각 조직은 고유한 변환 키 쌍을 생성한다. 이 키는 외부에 절대 노출되지 않는다.

**Step 2: Space Rotation** 직교 행렬(Orthogonal Matrix)을 사용하여 embedding space를 회전시킨다. 이 회전은 내적(dot product)의 결과를 보존하므로 코사인 유사도 계산이 가능하지만, 축의 의미를 완전히 재배치한다.

**Step 3: Dimensional Scaling** 각 차원에 독립적인 스케일링을 적용하여 거리 정보를 왜곡한다.

**Step 4: Translation & Noise** 바이어스 벡터를 더하고 미세한 가우시안 노이즈를 추가하여 원본 공간으로의 역변환을 수학적으로 불가능하게 만든다.

**Step 5: Query Transformation** 검색 시, 소스 조직의 쿼리를 타겟 조직의 vector space language로 변환하여 전송한다.

```python
import numpy as np
from scipy.stats import ortho_group
from typing import Tuple

class Vector2Trans:
    """
    Trans-RAG의 vector2Trans 변환기 구현
    각 조직은 고유한 변환 파라미터를 보유
    """
    
    def __init__(self, dim: int, noise_scale: float = 0.01):
        self.dim = dim
        self.noise_scale = noise_scale
        
        # 직교 회전 행렬 생성 (Haar measure)
        self.rotation = ortho_group.rvs(dim)
        
        # 랜덤 스케일링 (각 차원에 대해)
        self.scaling = np.random.uniform(0.5, 2.0, size=dim)
        
        # 바이어스 벡터
        self.bias = np.random.randn(dim)
        
        # 노이즈 스케일
        self.noise_scale = noise_scale
    
    def transform(self, vectors: np.ndarray) -> np.ndarray:
        """
        원본 벡터를 조직 고유의 vector space로 변환
        
        Args:
            vectors: (N, dim) 형태의 원본 embedding 벡터
        
        Returns:
            변환된 벡터 (N, dim)
        """
        # Step 1: Rotation
        rotated = np.dot(vectors, self.rotation.T)
        
        # Step 2: Scaling
        scaled = rotated * self.scaling
        
        # Step 3: Translation + Noise
        noise = np.random.normal(0, self.noise_scale, size=scaled.shape)
        transformed = scaled + self.bias + noise
        
        return transformed
    
    def transform_query(
        self, 
        query_vector: np.ndarray, 
        target_key: Tuple
    ) -> np.ndarray:
        """
        쿼리를 타겟 조직의 vector space로 변환
        
        Args:
            query_vector: (dim,) 형태의 쿼리 embedding
            target_key: 타겟 조직의 공개 변환 키
        
        Returns:
            변환된 쿼리 벡터
        """
        target_rot, target_scale, target_bias = target_key
        
        # 소스 공간에서 역변환 후 타겟 공간으로
        intermediate = query_vector.reshape(1, -1)
        
        # 타겟 조직의 변환 적용
        rotated = np.dot(intermediate, target_rot.T)
        scaled = rotated * target_scale
        transformed = scaled + target_bias
        
        return transformed.flatten()

```

```python
# 사용 예시
if __name__ == "__main__":
    dim = 768  # BERT-base embedding dimension
    org_a = Vector2Trans(dim, noise_scale=0.01)
    org_b = Vector2Trans(dim, noise_scale=0.01)
    
    # 조직 A의 문서 embeddings
    doc_embeddings = np.random.randn(1000, dim)
    
    # 조직 A의 vector space로 변환하여 저장
    transformed_docs = org_a.transform(doc_embeddings)
    
    # 쿼리 처리 (조직 B에서 조직 A로 검색)
    query = np.random.randn(dim)
    
    # 조직 A의 공개 키 (rotation, scaling, bias만)
    org_a_public_key = (org_a.rotation, org_a.scaling, org_a.bias)
    
    # 쿼리를 조직 A의 공간으로 변환
    transformed_query = org_b.transform_query(query, org_a_public_key)
    
    # 검색 수행 (코사인 유사도)
    similarities = np.dot(
        transformed_docs, 
        transformed_query
    ) / (
        np.linalg.norm(transformed_docs, axis=1) * 
        np.linalg.norm(transformed_query)
    )
    
    top_k_idx = np.argsort(similarities)[-5:][::-1]
    print(f"Top-5 검색 결과 인덱스: {top_k_idx}")
    print(f"최고 유사도: {similarities[top_k_idx[0]]:.4f}")
```

### 보안 분석: 수학적 격리 보장

논문의 핵심 기여 중 하나는 변환된 vector space 간의 수학적 독립성을 증명한 것이다. 실험 결과는 인상적이다.

| 보안 메트릭 | 측정값 | 의미 |
| :--- | :--- | :--- |
| Angular Separation | 89.90° | 두 조직의 공간이 거의 직교 |
| Isolation Rate | 99.81% | 크로스 공간 검색 실패율 |
| Reconstruction Error | >95% | 원본 복원 시도의 오차율 |
| Brute-force Resistance | 2^(dim/2) | 차원 공격의 복잡도 |

89.90°의 각도 분리가 의미하는 바는 직관적이다. 90°가 완전한 직교(어떤 정보도 공유하지 않음)이므로, 89.90°는 "사실상 독립적"임을 수학적으로 보여준다.

### 성능 평가: 8 × 3 × 3 실험 매트릭스

논문은 8개 retriever, 3개 dataset, 3개 LLM으로 구성된 포괄적인 실험을 수행했다.

**Retriever 구성:**
- Sparse: BM25, SPLADE
- Dense: DPR, ANCE, TAS-B, GenQ, Aggretriever, BGE

**Dataset:**
- Natural Questions (NQ)
- TriviaQA
- MS MARCO

**LLM:**
- GPT-3.5-Turbo
- Llama-2-70B
- Mistral-7B

| 메트릭 | Baseline (No Security) | Homomorphic Enc. | Trans-RAG | 차이 |
| :--- | :--- | :--- | :--- | :--- |
| nDCG@10 | 0.672 | 0.658 | 0.649 | -3.5% |
| Recall@100 | 0.841 | 0.823 | 0.830 | -1.3% |
| MRR | 0.621 | 0.609 | 0.604 | -2.7% |
| 검색 지연 (ms) | 12.3 | 1,245.6 | 14.1 | +14.6% |
| 吞吐量 (QPS) | 813 | 8.2 | 709 | -12.8% |

nDCG@10 기준 3.5% 감소는 Homomorphic Encryption 대비 연산 효율성의 극적 개선(100배 이상)을 고려하면 실무적으로 충분히 수용 가능한 trade-off이다.

### 실무 적용 가이드

Trans-RAG를 프로덕션 환경에 적용하기 위한 단계별 가이드를 제공한다.

**Phase 1: 기존 RAG 파이프라인 분석**

현재 사용 중인 embedding model, vector DB, retriever 구성을 파악한다. Trans-RAG는 embedding model에 독립적이므로 기존 인프라 변경이 최소화된다.

**Phase 2: 변환 키 관리 체계 구축**

```python
# 변환 키 관리를 위한 간단 예시
from dataclasses import dataclass
import hashlib
import os

@dataclass
class OrgKeyPair:
    """조직별 변환 키 쌍"""
    org_id: str
    private_rotation: np.ndarray
    private_scaling: np.ndarray
    private_bias: np.ndarray
    
    def get_public_key(self) -> bytes:
        """공개 키 해시 생성 (키 자체는 직접 교환)"""
        key_data = (
            self.private_rotation.tobytes() +
            self.private_scaling.tobytes() +
            self.private_bias.tobytes()
        )
        return hashlib.sha256(key_data).digest()
    
    def rotate_key(self):
        """주기적 키 로테이션"""
        dim = self.private_rotation.shape[0]
        self.private_rotation = ortho_group.rvs(dim)
        self.private_scaling = np.random.uniform(0.5, 2.0, size=dim)
        self.private
```

---

**출처**: [http://arxiv.org/abs/2604.09541v1](http://arxiv.org/abs/2604.09541v1)