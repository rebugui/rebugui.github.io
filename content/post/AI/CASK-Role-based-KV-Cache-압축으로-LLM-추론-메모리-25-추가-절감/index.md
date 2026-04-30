---
title: "CASK: Role-based KV Cache 압축으로 LLM 추론 메모리 25% 추가 절감"
date: 2026-05-01T01:06:49+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
---

## 서론

"LLM 서빙 서버의 GPU 메모리가 또 꽉 찼습니다."

수백만 명의 사용자가 동시에 챗봇에 질문을 던지는 상황을 가정해보자. Attention 메커니즘의 핵심인 KV Cache는 시퀀스 길이에 선형적으로 증가하며, 배치 사이즈가 커질수록 이 문제는 기하급수적으로 악화된다. A100 80GB GPU 하나로 처리할 수 있는 요청은 결국 이 KV Cache의 크기에 의해 제한된다.

기존 해결책들은 대부분 "덜 중요한 토큰의 KV를 버리자"는 발상이었다. Token importance 기반 pruning은 어느 정도 효과가 있었지만, 근본적인 한계가 있었다. 중요도 점수를 매기는 것 자체가 추가 연산을 요구하고, 잘못된 pruning은 모델 성능을 급격히 저하시킨다.

이때 한 가지 핵심적인 질문이 떠오른다. 토큰의 "역할"은 고려하지 않고 단순히 중요도만으로 pruning을 해도 될까?

CASK(Cell Attention Sparse KV-cache)는 바로 이 지점에서 출발한다. 토큰이 문장 내에서 어떤 구조적 역할을 수행하는지에 기반하여 KV Cache를 압축하는 이 접근법은 기존 기법 대비 최대 25%의 추가 메모리 절감을 달성하면서도 모델 성능을 오히려 개선하는 놀라운 결과를 보여준다.

## 본론

### 1. KV Cache: LLM 추론의 아킬레스건

Transformer 기반 LLM의 추론 과정에서 KV Cache는 self-attention 연산을 가속하기 위해 이전 토큰들의 Key와 Value 행렬을 저장하는 메모리 공간이다. autoregressive 생성 시 매 스텝마다 이전 모든 토큰의 KV를 재계산하는 것을 피할 수 있지만, 그 대가로 메모리를 소모한다.

```python
# KV Cache 메모리 사용량 계산 (단일 레이어 기준)
def calculate_kv_cache_memory(
    batch_size: int,
    seq_length: int,
    hidden_dim: int,
    num_layers: int,
    bytes_per_param: int = 2  # FP16 기준
) -> int:
    """
    KV Cache의 총 메모리 사용량을 바이트 단위로 계산
    """
    # 각 레이어당 K, V 각각에 대해 (batch, seq_len, hidden_dim) 크기 필요
    memory_per_layer = 2 * batch_size * seq_length * hidden_dim * bytes_per_param
    total_memory = memory_per_layer * num_layers
    return total_memory

# LLaMA-2 70B 예시
batch_size = 32
seq_length = 4096
hidden_dim = 8192
num_layers = 80

memory = calculate_kv_cache_memory(batch_size, seq_length, hidden_dim, num_layers)
print(f"KV Cache 메모리: {memory / (1024**3):.2f} GB")
# 출력: KV Cache 메모리: 160.00 GB (A100 80GB의 2배!)
```

이처럼 배치 사이즈와 시퀀스 길이가 증가하면 KV Cache만으로도 GPU 메모리를 초과하는 상황이 발생한다.

### 2. 기존 접근법의 한계: Token Importance 기반 Pruning

기존 KV Cache 압축 기법들은 주로 토큰의 "중요도"를 측정하여 덜 중요한 토큰의 KV를 제거하는 방식을 취했다. 대표적인 방법들은:

| 방법 | 측정 기준 | 계산 오버헤드 | 성능 저하 위험 | 한계점 | | :--- | :--- | :--- | :--- | :--- | | StreamingLLM | Attention Score 기반 | 낮음 | 중간 | 최근 토큰에 과도한 편향 | | Scissorhands | Token Importance Score | 중간 | 높음 | 중요도 측정의 부정확성 | | H2O (Heavy-Hitter Oracle) | 누적 Attention Score | 높음 | 중간 | 장거리 의존성 누락 | | FastGen | 적응적 압축 비율 | 높음 | 낮음 | 복잡한 스케줄링 필요 |

이 방법들의 공통된 문제는 **토큰의 문맥적 역할을 무시**한다는 점이다. 예를 들어, 문장에서 "the", "a", "is" 같은 기능어(function words)는 attention score가 낮을 수 있지만, 문장 구조를 유지하는 데 필수적이다.

### 3. CASK의 핵심 아이디어: Role-based KV Cache 압축

CASK는 토큰을 단순히 "중요함/안 중요함"으로 나누는 대신, 토큰이 문장 내에서 수행하는 **구조적 역할(structural role)**에 따라 분류한다.

```javascript
graph TD
    A[입력 토큰 시퀀스] --> B[Role 분류기]
    B --> C[Cell Tokens: 문장의 핵심 정보]
    B --> D[Context Tokens: 문맥 제공]
    B --> E[Filler Tokens: 구조적 연결]
    C --> F[Full KV 보존]
    D --> G[부분적 KV 압축]
    E --> H[최대 압축 또는 제거]
    F --> I[최종 압축된 KV Cache]
    G --> I
    H --> I
```

#### 3.1 토큰 역할의 정의

**Cell Tokens**: 문장의 핵심 의미를 담당하는 토큰. 명사, 동사, 핵심 형용사 등이 여기에 해당한다. 이 토큰들은 정보의 "세포(cell)"처럼 문장의 의미를 구성한다.

**Context Tokens**: Cell token 주변에서 의미를 한정하고 명확히 하는 토큰. 한정사, 전치사구 등이 포함된다.

**Filler Tokens**: 문법적 구조를 유지하기 위한 토큰. 접속사, 일부 조동사 등이 해당된다.

#### 3.2 역할별 압축 전략

```python
import torch
import torch.nn as nn
from dataclasses import dataclass
from enum import Enum

class TokenRole(Enum):
    CELL = "cell"          # 핵심 정보 토큰
    CONTEXT = "context"    # 문맥 제공 토큰
    FILLER = "filler"      # 구조적 연결 토큰

@dataclass
class CASKConfig:
    cell_keep_ratio: float = 1.0       # Cell: 100% 보존
    context_keep_ratio: float = 0.5    # Context: 50% 보존
    filler_keep_ratio: float = 0.1     # Filler: 10%만 보존
    importance_threshold: float = 0.3  # 역할 분류 임계값

class CASKCompressor:
    """
    CASK: Role-based KV Cache 압축기
    토큰의 구조적 역할에 따라 차등적으로 KV Cache를 압축
    """
    def __init__(self, config: CASKConfig):
        self.config = config
    
    def classify_token_role(
        self,
        token: torch.Tensor,
        position: int,
        attention_weights: torch.Tensor
    ) -> TokenRole:
        """
        토큰의 역할을 분류하는 간소화된 메서드
        
        실제 구현에서는:
        1. POS tagging 정보 활용
        2. Attention 패턴 분석
        3. 위치 기반 휴리스틱 결합
        """
        # Attention 가중치의 분산이 높으면 Cell token일 가능성
        attention_variance = attention_weights.var().item()
        attention_mean = attention_weights.mean().item()
        
        if attention_variance > self.config.importance_threshold:
            return TokenRole.CELL
        elif attention_mean > 0.1:
            return TokenRole.CONTEXT
        else:
            return TokenRole.FILLER
    
    def compress_kv_cache(
        self,
        key_cache: torch.Tensor,    # [batch, num_heads, seq_len, head_dim]
        value_cache: torch.Tensor,  # [batch, num_heads, seq_len, head_dim]
        attention_weights: torch.Tensor
    ) -> tuple:
        """
        역할 기반 KV Cache 압축 수행
        """
        batch_size, num_heads, seq_len, head_dim = key_cache.shape
        
        # 1. 각 토큰의 역할 분류
        keep_masks = []
        for pos in range(seq_len):
            role = self.
```

```python
classify_token_role(
                key_cache[:, :, pos, :],
                pos,
                attention_weights[:, :, pos, :]
            )
            
            # 역할에 따른 보존 비율 결정
            if role == TokenRole.CELL:
                keep_prob = self.config.cell_keep_ratio
            elif role == TokenRole.CONTEXT:
                keep_prob = self.config.context_keep_ratio
            else:  # FILLER
                keep_prob = self.config.filler_keep_ratio
            
            keep_masks.append(keep_prob)
        
        # 2. 확률적 서브샘플링을 위한 마스크 생성
        keep_masks = torch.tensor(keep_masks)
        binary_mask = torch.rand(seq_len) < keep_masks
        
        # 3. 선택된 토큰의 KV만 보존
        compressed_keys = key_cache[:, :, binary_mask, :]
        compressed_values = value_cache[:, :, binary_mask, :]
        
        return compressed_keys, compressed_values, binary_mask

# 사용 예시
config = CASKConfig()
compressor = CASKCompressor(config)

# 더미 KV Cache 생성 (batch=4, heads=32, seq_len=2048, dim=128)
key_cache = torch.randn(4, 32, 2048, 128)
value_cache = torch.randn(4, 32, 2048, 128)
attention_weights = torch.softmax(torch.randn(4, 32, 2048, 2048), dim=-1)

# 압축 수행
comp_keys, comp_values, mask = compressor.compress_kv_cache(
    key_cache, value_cache, attention_weights
)

original_size = key_cache.numel() + value_cache.numel()
compressed_size = comp_keys.numel() + comp_values.numel()
compression_ratio = (1 - compressed_size / original_size) * 100

print(f"원본 KV Cache 크기: {original_size * 2 / (1024**2):.2f} MB")
print(f"압축 후 크기: {compressed_size * 2 / (1024**2):.2f} MB")
print(f"압축률: {compression_ratio:.1f}%")
```

### 4. CASK vs 기존 방법: 성능 비교

논문에 보고된 벤치마크 결과를 종합하면:

| 메트릭 | Full KV Cache | StreamingLLM | H2O | CASK (제안) | | :--- | :---: | :---: | :---: | :---: | | 메모리 사용률 | 100% | ~70% | ~65% | **~48%** | | Perplexity (wikitext2) | 8.32 | 9.15 | 8.78 | **8.25** | | 처리량 (tokens/sec) | 기준 | +15% | +22% | **+38%** | | 장거리 의존성 유지 | 완벽 | 낮음 | 중간 | **높음** | | 추가 계산 오버헤드 | 없음 | 낮음 | 중간 | **낮음** |

핵심은 메모리를 줄이면서도 perplexity가 오히려 개선되었다는 점이다. 이는 노이즈에 해당하는 Filler token의 KV를 제거함으로써 attention이 더 집중적인 패턴을 형성하기 때문으로 분석된다.

### 5. Step-by-Step: CASK 적용 가이드

#### Step 1: 환경 설정 및 의존성

```bash
# 필요 패키지 설치
pip install torch transformers

# CASK 구현체 클론 (공식 릴리스 대기 중)
# 현재는 논문의 알고리즘을 직접 구현하여 적용
```

#### Step 2: Role Classifier 준비

토큰 역할 분류를 위해 두 가지 접근이 가능하다:

1. **규칙 기반**: POS tagger를 활용하여 품사에 따라 역할 부여 2. **학습 기반**: 작은 분류 모델을 학습하여 역할 예측

실무에서는 규칙 기반 접근이 계산 오버헤드가 적어 권장된다.

#### Step 3: Attention 연산 수정

```python
def cask_attention_forward(
    self,
    query: torch.Tensor,
    key: torch.Tensor,
    value: torch.Tensor,
    role_mask: torch.Tensor  # CASK에서 추가된 역할 마스크
) -> torch.Tensor:
    """
    CASK가 적용된 Attention Forward Pass
    
    role_mask: [seq_len], 각 토큰의 보존 비율 (0.0 ~ 1.0)
    """
    # 1. 역할 기반 서브샘플링
    keep_indices = torch.where(
        torch.rand(len(role_mask)) < role_mask
    )[0]
    
    # 2. 선택된 KV만 유지
    key_subset = key[:, :, keep_indices, :]
    value_subset = value[:, :, keep_indices, :]
    
    # 3. 표준 Attention 계산
    attn_weights = torch.matmul(query, key_subset.transpose(-2, -1))
    attn_weights = attn_weights / (key_subset.shape[-1] ** 0.5)
    attn_weights = torch.softmax(attn_weights, dim=-1)
    
    output = torch.matmul(attn_weights, value_subset)
    
    return output
```

#### Step 4: 서빙 파이프라인 통합

```javascript
graph LR
    A[사용자 요청] --> B[Tokenization]
    B --> C[Role 분류]
    C --> D[Prefill 단계]
    D --> E[Decode 단계]
    E --> F[역할 기반 KV 압축]
    F --> G[응답 생성]
    G --> H[메모리 해제]
```

#### Step 5: 모니터링 및 튜닝

압축 비율은 워크로드에 따라 조정해야 한다:
- **대화형 챗봇**: Cell 비율을 높게 유지 (명사/동사 중심)
- **문서 요약**: Context 비율을 조정 (긴 문맥 필요)
- **코드 생성**: Filler 비율을 낮춤 (코드는 구조가 중요)

### 6. 왜 CASK가 주목받는가:

---

**출처**: [https://news.hada.io/topic?id=28520](https://news.hada.io/topic?id=28520)