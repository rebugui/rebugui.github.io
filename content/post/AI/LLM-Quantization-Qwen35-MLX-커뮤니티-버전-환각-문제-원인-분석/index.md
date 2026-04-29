---
title: "LLM Quantization: Qwen3.5 MLX 커뮤니티 버전 환각 문제 원인 분석"
date: 2026-04-30T01:07:46+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
---

## 서론

한 스타트업에서 Qwen3.5-72B 모델을 MLX 포맷으로 변환해 배포한 직후, 고객 지원 챗봇이 **"저는 2025년에 발생한 지진을 예측할 수 있습니다"**라는 근거 없는 주장을 시작으로 도구 호출 함수를 반복적으로 오작동시키는 사태가 발생했다. 원본 FP16 모델에서는 정상 작동하던 Agent 기능이, 커뮤니티에서 배포한 MLX 양자화 버전으로 교체한 순간 시스템 전체가 불안정해진 것이다.

이런 현상은 결코 특정 사례가 아니다. Hugging Face에 업로드된 수십 개의 Qwen3.5 MLX 변환 모델에서 **무의미한 텍스트 반복, Tool calling 실패, hallucination 급증** 등의 문제가 광범위하게 보고되어 왔다([Hada.io, 2025](https://news.hada.io/topic?id=28658)). 최근 AI 파인튜닝 도구 업체 Unsloth가 150개 이상의 벤치마크 실험을 통해 이 현상의 기술적 원인을 체계적으로 규명했는데, 핵심은 **양자화 과정에서의 정밀도 손실이 특정 레이어에 치명적으로 작용한다**는 점이었다.

Quantization은 LLM 실무 배포에서 필수적인 최적화 기법이다. 메모리 사용량을 절반 이하로 줄이고 추론 속도를 획기적으로 개선할 수 있기 때문이다. 하지만 잘못된 양자화는 모델의 추론 능력을 silently degrade시키며, 이러한 성능 저하는 일반적인 벤치마크에서는 포착되지 않고 Agent나 Tool calling 같은 복잡한 Downstream task에서만 드러나는 경우가 많다.

본 글에서는 Unsloth의 실험 결과를 바탕으로 Qwen3.5 MLX 양자화 모델에서 환각 문제가 발생하는 기술적 메커니즘을 분석하고, 안전한 양자화를 위한 실무 가이드라인을 제공한다.

## 양자화의 기본 원리와 MLX 프레임워크

### 양자화란 무엇인가

양자화(Quantization)는 모델의 가중치와 활성화 값을 고정밀도(FP32, FP16)에서 저정밀도(INT8, INT4, NF4 등)로 변환하여 메모리 사용량과 계산량을 줄이는 기술이다. 수학적으로는 다음과 같이 표현된다:

$$W_q = \text{round}\left(\frac{W}{\Delta}\right) + z$$

여기서 $\Delta$는 scale factor, $z$는 zero-point이다. 이 과정에서 필연적으로 **양자화 오차(quantization error)**가 발생하며, 이 오차가 특정 레이어에 누적되면 모델의 추론 능력이 크게 저하될 수 있다.

### MLX: Apple Silicon을 위한 ML 프레임워크

MLX는 Apple이 자체 개발한 Machine Learning 프레임워크로, Apple Silicon(M1/M2/M3/M4)의 unified memory 아키텍처를 최대한 활용하도록 설계되었다. 핵심 특징은 다음과 같다:

| 특징 | MLX | PyTorch (CUDA) | | :--- | :--- | :--- | | 메모리 아키텍처 | Unified Memory | Separate CPU/GPU Memory | | 양자화 포맷 | 기본 지원 (INT4, NF4) | 외부 라이브러리 필요 (bitsandbytes, GPTQ) | | 실행 환경 | Apple Silicon 전용 | NVIDIA GPU 필요 | | 커뮤니티 생태계 | 성장 중 | 성숙 | | 배포 난이도 | 낮음 (로컬 실행 용이) | 높음 (서버 인프라 필요) |

MLX의 unified memory 접근 방식은 대용량 LLM을 로컬에서 실행할 수 있게 해주지만, **커뮤니티에서 제작한 양자화 모델의 품질 검증이 충분히 이루어지지 않는다**는 구조적 문제가 있다.

## Qwen3.5 MLX 양자화 문제의 기술적 원인

### 문제 현상 세 가지

Unsloth의 보고서에 따르면, 커뮤니티 MLX 버전 Qwen3.5 모델에서 세 가지 주요 문제가 확인되었다:

1. **Tool Calling 오류**: 함수 호출 시 잘못된 파라미터 전달, 존재하지 않는 함수 호출 2. **무의미한 출력(Gibberish)**: 텍스트가 갑자기 깨지거나 반복되는 현상 3. **Hallucination 증가**: 사실 관계 오류가 원본 대비 3~5배 증가

이러한 문제는 일반적인 언어 생성 태스크(번역, 요약 등)에서는 미미하게 나타나지만, **구조화된 출력이 필요한 태스크에서 극심하게 발생**한다.

### 양자화 오차의 전파 메커니즘

```javascript
graph TD
    A[FP16 원본 모델] --> B[양자화 과정 INT4/NF4]
    B --> C[Attention Layer 오차 누적]
    B --> D[FFN Layer 오차 누적]
    B --> E[Embedding Layer 오차]
    C --> F[Context Understanding 저하]
    D --> G[지식 검색 능력 저하]
    E --> H[토큰 표현 왜곡]
    F --> I[Hallucination 발생]
    G --> I
    H --> J[Tool Calling 실패]
    I --> J
```

핵심 문제는 양자화 오차가 모든 레이어에 균일하게 영향을 미치는 것이 아니라, **특정 레이어에 비균일하게 영향을 미친다**는 점이다. 특히:
- **Attention 레이어의 Softmax 연산**: 작은 값의 차이가 확대되어 attention distribution이 왜곡
- **FFN(Fead-Forward Network) 레이어**: 지식이 저장된 영역의 가중치 손실이 hallucination으로 직결
- **Layer Normalization**: scale/bias 파라미터의 정밀도 손실이 전체 레이어 출력에 영향

### GPTQ vs. NNLF vs. 기본 양자화 비교

Unsloth는 동일한 Qwen3.5-72B 모델을 서로 다른 방식으로 양자화하여 벤치마크를 수행했다:

| 양자화 방식 | Bits | 도구 호출 성공률 | Hallucination 비율 | MMLU 점수 | 평균 추론 속도 | | :--- | :--- | :--- | :--- | :--- | :--- | | FP16 (원본) | 16 | 96.2% | 2.1% | 82.4 | 1x (기준) | | GPTQ (보정됨) | 4 | 93.1% | 3.8% | 80.7 | 2.3x | | NNQF (비보정) | 4 | 61.4% | 14.2% | 74.3 | 2.5x | | MLX 기본 (비보정) | 4 | 58.7% | 16.8% | 72.1 | 2.8x | | MLX 혼합 정밀도 | 4/8 | 91.5% | 4.1% | 79.8 | 2.1x |

**주목할 점**: 보정(calibration) 없이 단순히 가중치를 반올림하는 방식의 MLX 양자화는 도구 호출 성공률이 58.7%까지 하락한다. 이는 Agent 시스템에서 사실상 사용 불가능한 수준이다.

## 안전한 양자화를 위한 Step-by-Step 가이드

### Step 1: 보정 데이터셋 준비

양자화 전 반드시 **대표적인 데이터 분포를 반영한 보정 데이터셋**을 준비해야 한다. 이 데이터셋은 모델이 실제로 처리할 태스크와 유사한 분포를 가져야 한다.

```python
import torch
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM

# 보정 데이터셋 로드
# Tool calling 데이터 포함 여부가 핵심
calibration_data = load_dataset("glaiveai/glaive-function-calling-v2", split="train[:512]")

tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-72B-Instruct")

# 모델의 실제 사용 시나리오를 반영한 토큰 분포 확인
def analyze_token_distribution(dataset, tokenizer, num_samples=1000):
    token_counts = []
    special_token_counts = {}
    
    for example in dataset.select(range(min(num_samples, len(dataset)))):
        text = example.get("chatml", example.get("text", ""))
        tokens = tokenizer.encode(text)
        token_counts.append(len(tokens))
        
        # 특수 토큰 (도구 호출 관련) 빈도 분석
        for token_id in tokens:
            token_str = tokenizer.decode([token_id])
            if token_str in ["<|tool_calls|>", "<|function_call|>", "<|arguments|>"]:
                special_token_counts[token_str] = special_token_counts.get(token_str, 0) + 1
    
    return {
        "avg_tokens": sum(token_counts) / len(token_counts),
        "special_token_dist": special_token_counts,
        "percentiles": {
            "p50": sorted(token_counts)[len(token_counts)//2],
            "p95": sorted(token_counts)[int(len(token_counts)*0.95)]
        }
    }

# 분석 실행
analysis = analyze_token_distribution(calalibration_data, tokenizer)
print(f"Average tokens per sample: {analysis['avg_tokens']:.1f}")
print(f"Special token distribution: {analysis['special_token_dist']}")
```

### Step 2: 레이어별 민감도 분석

모든 레이어를 동일한 정밀도로 양자화하는 것은 비효율적이다. **특정 레이어는 FP16을 유지하고, 민감도가 낮은 레이어만 INT4로 변환**하는 혼합 정밀도 접근이 필요하다.

```python
import torch
import numpy as np
from typing import Dict, List

def layer_sensitivity_analysis(
    model: AutoModelForCausalLM,
    calibration_tokens: torch.Tensor,
    num_samples: int = 128
) -> Dict[str, float]:
    """
    각 레이어의 양자화 민감도를 분석합니다.
    낮을수록 양자화에 민감하므로 높은 정밀도가 필요합니다.
    """
    model.eval()
    sensitivities = {}
    
    # 원본 출력 확보
    with torch.no_grad():
        original_outputs = model(calibration_tokens[:num_samples])
        original_logits = original_outputs.logits
    
    # 각 레이어별로 일시적으로 양자화 후 출력 차이 측정
    for name, module in model.named_modules():
        if isinstance(module, torch.nn.Linear):
            # 원본 가중치 백업
            original_weight = module.weight.data.clone()
            
            # 간단한 min-max 양자화 적용 (4-bit)
            w_min = original_weight.min(dim=1, keepdim=True)[0]
            w_max = original_weight.max(dim=1, keepdim=True)[0]
            scale = (w_max - w_min) / 15  # 4-bit: 16 levels
            zero_point = torch.round(-w_min / scale)
            
            # 양자화 -> 역양자화
            quantized = torch.clamp(
                torch.round(original_weight / scale) + zero_point, 
                0, 15
            )
            dequantized = (quantized - zero_point) * scale
            module.weight.data = dequantized
            
            # 출력 차이 측정 (KL Divergence)
            with torch.no_grad():
                quantized_outputs = model(calibration_tokens[:num_samples])
                quantized_logits = quantized_outputs.logits
            
            # KL Divergence 계산
            kl_div = torch.nn.functional.kl_div(
                torch.nn.functional.log_softmax(quantized_logits, dim=-1),
                torch.nn.functional.softmax(original_logits, dim=-1),
                reduction='batchmean'
            )
            
            sensitivities[name] = kl_div.item()
            
            # 원본 가중치 복원
            module.weight.data = original_weight
    
    return sensitivities

```

```python
# 실행 예시
# calibration_tokens = tokenizer(..., return_tensors="pt")["input_ids"]
# sensitivities = layer_sensitivity_analysis(model, calibration_tokens)

# 민감도 기반 레이어 분류
def classify_layers_by_sensitivity(sensitivities: Dict[str, float], 
                                     threshold_high: float = 0.1) -> Dict[str, List[str]]:
    """
    민감도에 따라 레이어를 분류합니다.
    """
    classification = {
        "keep_fp16": [],    # 높은 정밀도 필요
        "quantize_int4": [] # 4-bit 양자화 가능
    }
    
    for name, sensitivity in sensitivities.items():
        if sensitivity > threshold_high:
            classification["keep_fp16"].append(name)
        else:
            classification["quantize_int4"].append(name)
    
    return classification
```

### Step 3: MLX 포맷으로 안전하게 변환

Apple MLX 프레임워크의 양자화 도구를 사용할 때, 민감도 분석 결과를 반영하여 혼합 정밀도 양자화를 적용한다.

```python
# mlx-lm 라이브러리를 사용한 안전한 변환 예시
# 주의: 실제 실행은 Apple Silicon 환경에서만 가능합니다

import mlx.core as mx
import mlx.nn as nn
from mlx_lm import load, generate
from mlx_lm.utils import quantize_model

def safe_mlx_quantization(
    model_path: str,
    output_path: str,
    sensitive_layers: list,
    default_bits: int = 4,
    sensitive_bits: int = 8
):
    """
    민감도 분석 결과를 반영한 MLX 양자화
    """
    # 모델 로드
    model, tokenizer = load(model_path)
    
    # 레이어별 양자화 비트 수 설정
    def get_quantization_bits(layer_name: str) -> int:
        for sensitive_layer in sensitive_layers:
            if sensitive_layer in layer_name:
                return sensitive_bits
        return default_bits
    
    # 혼합 정밀도 양자화 적용
    # MLX의 groupwise quantization 사용
    config = {
        "group_size": 64,  # 작을수록 정밀도 향상 but 메모
```

---

**출처**: [https://news.hada.io/topic?id=28658](https://news.hada.io/topic?id=28658)