---
title: "🎬 Qwen2.5-7B Fine-tuning: 확률적 스토리 그래프 구현"
date: 2026-02-09T06:59:35+09:00
draft: false
tags:
  - "LLM"
  - "Fine-tuning"
  - "Qwen2.5"
  - "LoRA"
  - "생성형 AI"
categories:
  - "AI"
---

## 서론: 영화 제작의 '제2막' 문제와 AI의 한계

영화 제작자, 특히 각본가들 사이에서 흔히 회자되는 악명 높은 장벽이 있습니다. 바로 '제2막의 문제(The Second Act Problem)'입니다. 도입부(제1막)에서 흥미로운 설정을 만들었고, 결말(제3막)의 장면은 머릿속에 그려지는데, 그 둘을 연결하는 중간 과정이 자꾸만 삐걱거리는 경험, 다들 한 번쯤은 겪어보셨을 것입니다. 이때 우리는 흔히 AI 라이팅 툴이나 챗봇에게 도움을 요청합니다. "주인공이 여기서 왼쪽으로 간다면 어떤 사건이 일어날까?"라고 묻지만, 돌아오는 대답은 십중팔구 진부한 클리셰와 이미 수천 번 본 듯한 공식적인 플롯 전개입니다.

이런 '진부함(Generic Slop)'의 근본적인 원인은 무엇일까요? 바로 대규모 언어 모델(LLM)이 학습한 데이터의 편향성에 있습니다. 기존의 AI는 인터넷의 일반적인 텍스트, 혹은 위키백과식의 줄거리 요약을 학습했기 때문에, '가장 확률이 높은' 단어를 선택할 때 필연적으로 평균적인 이야기를 만들어냅니다. 하지만 진정한 창의성은 평균이 아닌 '변칙'에서 나옵니다. 장고드의 점프 컷, 쿠로사와 아키라의 평행 서사, 타르코프스키의 느린 연출과 같은 영화적 구조는 일반적인 텍스트 코퍼스에서는 포착하기 어렵습니다.

CineGraphs 프로젝트는 이러한 딜레마를 해결하기 위해 탄생했습니다. 이 프로젝트는 단순히 텍스트를 생성하는 것이 아니라, 영화의 '구조적 DNA(Structural DNA)'를 추출하여 확률적 분기 그래프(Probabilistic Story Graph)로 시각화합니다. 사용자는 선형적인 대본을 작성하기에 앞서, 나무의 가지가 뻗어나가듯 다양한 서사적 가능성을 탐색하고 '조각(Sculpting)'할 수 있습니다. 본 글에서는 100편의 고급 영화로 파인튜닝된 Qwen2.5-7B 모델이 어떻게 비선형적인 스토리텔링을 구현하는지 그 기술적 원리와 구현 과정을 심도 있게 다루고자 합니다.

## 본론: 시네마틱 구조를 학습하는 Qwen2.5-7B

### 1. 데이터 파이프라인: 위키백과가 아닌 영화 그 자체에서 배우기

모델의 성능은 데이터가 결정합니다. CineGraphs의 핵심 차별점은 '영화 줄거리 요약'이 아닌 '영화 그 자체'를 학습 데이터로 활용했다는 점입니다. 연구자는 고다르, 쿠로사와, 브래키지, 타르코프스키 등 독특한 내러티브 구조를 지닌 100편의 영화를 선정했습니다. 이 데이터는 단순한 텍스트가 아닙니다.

1000줄 이상의 파이썬 파이프라인을 구축하여 Qwen3-VL(비전-언어 모델)을 활용, 영화의 자막과 영상을 동시에 분석했습니다. 이 과정에서 모델은 단순히 "무슨 일이 일어났는지"를 요약하는 것이 아니라, *이 장면이 도입부와 거울 구조를 이루는지*, *캐릭터의 궤적이 어떻게 반전되는지*와 같은 시네마틱 문법을 학습합니다. 이렇게 추출된 데이터는 총 1만 개의 '프롬프트-분기 서사 쌍(Prompt-to-Branching-Narrative pairs)'으로 구성된 데이터셋으로 변환되었습니다.

아래는 영화 분석 및 학습 데이터 생성 과정을 도식화한 아키텍처입니다.

```javascript
graph TD
    Input[Raw Footage & Subtitles] --> Preprocess[Preprocessing Sync]
    Preprocess --> VLM[Qwen3-VL Analyzer]
    
    subgraph Extraction ["Structural DNA Extraction"]
        VLM --> Beats[Scene-level Narrative Beats]
        VLM --> Relations[Character Relationship Evolution]
        VLM --> Themes[Thematic Threads]
    end

    Beats --> Dataset[10K Dataset Prompt-Branch Pairs]
    Relations --> Dataset
    Themes --> Dataset

    Dataset --> Base[Qwen2.5-7B Instruct]
    Base --> LoRA[LoRA Adapter]
    LoRA --> Infer[vLLM Inference Engine]
    Infer --> Output[Probabilistic Story Graph]

    style Input fill:#f9f,stroke:#333,stroke-width:2px
    style Preprocess fill:#f9f,stroke:#333,stroke-width:2px
    style VLM fill:#bbf,stroke:#333,stroke-width:2px
    style Beats fill:#f9f,stroke:#333,stroke-width:2px
    style Relations fill:#f9f,stroke:#333,stroke-width:2px
    style Themes fill:#f9f,stroke:#333,stroke-width:2px
    style Dataset fill:#f9f,stroke:#333,stroke-width:2px
    style Base fill:#f9f,stroke:#333,stroke-width:2px
    style LoRA fill:#bbf,stroke:#333,stroke-width:2px
    style Infer fill:#f9f,stroke:#333,stroke-width:2px
    style Output fill:#bbf,stroke:#333,stroke-width:2px
```

### 2. 모델 아키텍처: Qwen2.5-7B와 LoRA의 조화

기본 베이스 모델로 Qwen2.5-7B-Instruct를 선택한 이유는 명확합니다. 70B 모델에 비해 서빙 비용이 효율적이면서도, 영화와 같은 복잡한 문맥을 이해하고 프로그래밍적인 논리(구조적 데이터)를 생성하는 데 필요한 성능을 갖추고 있기 때문입니다. 특히 Qwen 시리즈는 최근 멀티모달 및 긴 문맥 처리(Long Context)에서 강력한 성능을 입증하며 연구자들 사이에서 널리 사용되고 있습니다.

하지만 여기서 중요한 것은 **LoRA(Low-Rank Adaptation)**의 활용입니다. 7B 파라미터 전체를 업데이트(Full Fine-tuning)하는 것은 계산 비용이 많이 들고 '카타스트로픽 포게팅(Catastrophic Forgetting)'을 유발할 수 있습니다. 대신, 우리는 LoRA 어댑터를 사용하여 모델의 '확률적 분기 생성 능력'에만 집중적으로 학습을 진행했습니다.

LoRA는 사전 학습된 가중치 행렬 $W$를 변경하지 않고, 낮은 랭크(Rank)의 행렬 $A$와 $B$를 더하여 $h = W_0 x + BAx$ 형태로 출력을 조정합니다. 이 방식을 통해 단일 4090 GPU에서도 효율적으로 학습을 마칠 수 있었습니다.

다음은 PyTorch와 PEFT 라이브러리를 사용하여 LoRA 설정을 구현하는 예시 코드입니다.

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model, TaskType

# 1. Qwen2.5-7B 모델 및 토크나이저 로드
model_id = "Qwen/Qwen2.5-7B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)

# 2. LoRA 설정: 스토리 분기 생성에 최적화
# 타겟 모듈은 Attention의 q_proj, v_proj 등으로 설정하여 의사결정 로직 강화
peft_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM, 
    inference_mode=False,
    r=16,             # Rank (낮을수록 파라미터가 적지만 표현력이 제한됨)
    lora_alpha=32,    # Scaling factor
    lora_dropout=0.05,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj"]
)

# 3. 모델에 LoRA 어댑터 적용
model = get_peft_model(model, peft_config)
model.print_trainable_parameters()

# 출력 예시: trainable params: 20M || all params: 7.6B || trainable%: 0.26%
# 이처럼 전체 파라미터의 아주 적은 부분만을 학습하여 효율성을 극대화합니다.
```

### 3. 확률적 분기 그래프와 추론(Inference) 전략

학습된 모델은 단순히 텍스트를 나열하는 것이 아니라, JSON 혹은 Graph 형식의 데이터를 생성하도록 튜닝되었습니다. 사용자가 "주인공이 열쇠를 발견한다"는 개념을 입력하면, 모델은 다음과 같은 확률적 가지를 제안합니다.

1.  **가지 A:** 열쇠가 옛 연인의 집 열쇠다 (과거 회상). 2.  **가지 B:** 열쇠가 보물 창고의 열쇠다 (액션 전개). 3.  **가지 C:** 열쇠가 아무 쓸모가 없는 오래된 물건이다 (반전/이터니티).

이때 vLLM 라이브러리가 핵심적인 역할을 수행합니다. vLLM은 PagedAttention 기술을 사용하여 메모리 관리를 효율화함으로써, 단일 NVIDIA 4090 GPU에서도 높은 처리량(Throughput)을 유지하며 실시간으로 그래프를 생성할 수 있게 합니다. 사용자가 React Flow 기반의 프론트엔드에서 노드를 확장할 때마다 백엔드의 vLLM은 즉각적으로 새로운 서사를 생성하여 응답합니다.

### 4. 성능 비교 및 분석

일반적인 AI 라이팅 툴과 CineGraphs(Qwen2.5-7B FT)의 차이는 데이터 선정에서 기인합니다. 실험 결과, 일반적인 헐리우드 블록버스터 위주로 학습된 초기 버전은 매우 공식적인 플롯만을 생성했습니다. 반면, 실험 영화와 국제 영화를 포함한 데이터셋으로 학습한 모델은 서사의 다양성이 획기적으로 개선되었습니다.

| 비교 항목 | 기존 AI 라이팅 툴 (Generic LLM) | CineGraphs (Qwen2.5-7B FT) | | :--- | :--- | :--- | | **학습 데이터** | 일반 인터넷 텍스트, 요약문 | 100편의 고급 영화 구조적 데이터 | | **출력 형식** | 선형 텍스트 (Paragraph) | **확률적 분기 그래프 (Graph)** | | **창의성 지표** | 낮음 (Cliché 위험) | 높음 (비선형적, 실험적 구조) | | **사용자 경험** | 텍스트 프롬프트 입력 후 결과 대기 | **노드 탐색 및 시각적 조각(Sculpting)** | | **서빙 효율성** | Cloud API 의존 (고비용) | **Single 4090 + vLLM (저비용)** |

이 표에서 볼 수 있듯이, CineGraphs는 텍스트 생성 자체를 목표로 하지 않고 '스토리텔링의 설계 공간'을 모델링한다는 점에서 기존 도구와 결정적으로 다릅니다.

## 결론: 비선형적 창의성의 모방

CineGraphs 프로젝트가 시사하는 바는 큽니다. 첫째, 데이터의 질(Quality)이 양(Quantity)을 압도할 수 있다는 점입니다. 방대한 인터넷 텍스트보다 100편의 잘 선정된 영화의 구조적 분석이 훨씬 더 높은 창의성을 이끌어냈습니다. 둘째, LLM의 활용처는 단순한 '채팅 봇'이 아닌 '확률적 엔진'으로 확장되고 있다는 점입니다. 사용자는 AI에게 답을 듣는 것이 아니라, AI가 제시하는 가능성의 분포를 탐색하며 의사결정을 내립니다.

앞으로도 이러한 도메인 특화 파인튜닝과 구조적 생성(Graph Generation)의 결합은 게임 시나리오 작성, 교육용 시뮬레이션, 심지어 법적 논증 구성 등 정형화되지 않은 창의적 작업에서 강력한 위력을 발휘할 것입니다.

기술적으로 Qwen2.5-7B라는 강력한 오픈소스 모델 위에 LoRA와 vLLM이라는 효율적인 MLOps 기술을 결합한 이 프로젝트는, 개발자가 자신만의 창의적 도구를 제작하는 데 있어 얼마나 큰 자유도를 가지게 되었는지를 보여주는 훌륭한 사례입니다.

### 참고자료

- [CineGraphs Demo](https://cinegraphs.ai/)

- [Qwen2.5 Technical Report](https://arxiv.org/abs/2309.16609)

- [vLLM: Easy, Fast, and Cheap LLM Serving](https://arxiv.org/abs/2309.06180)

- [LoRA: Low-Rank Adaptation of Large Language Models](https://arxiv.org/abs/2106.09685)
