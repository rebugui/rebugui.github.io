---
title: "Gemma 4와 WebAssembly: 브라우저 내 다이어그램 자동 생성 데모"
date: 2026-04-30T01:07:42+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
---

## 서론

엔터프라이즈 환경에서 설계도나 시스템 아키텍처를 공유할 때, 우리는 종종 딜레마에 빠집니다. 클라우드 기반의 AI 툴을 사용하면 편리하지만, 민감한 설계 데이터가 외부 서버로 전송되는 것에 대한 보안 우려가 따릅니다. 반면, 로컬 설치형 소프트웨어는 하드웨어 의존도가 높고 설치 과정이 복잡하여 접근성이 떨어지곤 합니다. 특히 'Prompt-to-Diagram'과 같이 대규모 언어 모델(LLM)의 추론 능력이 필수적인 생성형 AI 작업은 고성능 GPU가 장착된 서버 없이는 구현하기 어렵다고 여겨져 왔습니다.

이러한 문제를 해결하는 핵심 동력은 바로 'WebAssembly(WASM)'와 경량화된 오픈소스 LLM의 결합입니다. 구글이 최근 발표한 Gemma 4와 같은 효율적인 모델을 4비트 양자화 기술을 통해 압축하면, 이제 막대한 서버 리소스 없이도 브라우저의 메모리 공간만으로 복잡한 추론이 가능해집니다. 이 접근 방식은 데이터 프라이버시를 완벽하게 보장하면서도, 서버 레이턴시(latency) 없이 실시간으로 텍스트를 시각적 다이어그램으로 변환하는 혁신적인 사용자 경험을 제공합니다. 이제 우리는 클라우드 API 호출 없이, 사용자의 브라우저 내에서 완전히 독립적인 AI 크리에이티브 워크스테이션을 구축할 수 있게 되었습니다.

## 본론

### 브라우저 내 추론의 기술적 배경과 원리

기존의 LLM 서빙은 Python 생태계(PyTorch, TensorFlow)에 의존하여 GPU 서버에서 이루어졌습니다. 그러나 브라우저 환경에서 이를 실행하기 위해서는 C++나 Rust로 작성된 코어를 WASM으로 컴파일하여 자바스크립트 엔진(V8, SpiderMonkey 등) 위에서 구동하는 기술이 필요합니다. 이 과정에서 가장 중요한 기술은 **양자화(Quantization)**입니다.

Gemma 4 모델은 FP16(16비트 부동소수점)으로 학습되었지만, 이를 그대로 브라우저에 로드하면 용량이 수십 GB에 달해 현실적으로 불가능합니다. 이를 해결하기 위해 INT4(4비트 정수)나 NF4(Normal Float 4)로 가중치(Weight)를 변환하는 양자화 과정을 거칩니다. 이 데모에서 약 3.1GB의 모델 사이즈는 바로 이 과정을 통해 압축된 결과입니다. 이렇게 압축된 모델은 브라우저의 WebAssembly Heap에 로드되어, WebGPU를 통해 사용자의 로컬 GPU 자원을 직접 활용해 연산을 수행합니다.

또한, 텍스트 프롬프트를 Excalidraw라는 특정 JSON 포맷으로 변환하는 과정은 단순한 텍스트 생성이 아닙니다. 모델은 Excalidraw의 스키마(schema)를 이해하고, `type`, `x`, `y`, `width`, `height`, `strokeColor` 등의 속성을 포함한 구조화된 JSON을 정확하게 생성해야 합니다. 이는 LLM이 자연어만이 아닌 구조화된 데이터(Structured Data) 생성에도 탁월한 능력을 갖추고 있음을 보여주는 사례입니다.

### 아키텍처: 프롬프트부터 시각화까지

다음은 브라우저 내에서 사용자 입력이 Excalidraw 다이어그램으로 렌더링되기까지의 전체 데이터 흐름을 보여주는 다이어그램입니다. 이 과정은 서버를 전혀 거치지 않는 클라이언트 사이드(Client-side) 아키텍처의 전형입니다.

```javascript
graph LR
    A[User Input Prompt] --> B[Tokenizer JS]
    B --> C[WebAssembly Runtime]
    C --> D[Gemma 4 Quantized Model]
    D --> C
    C --> E[Detokenizer]
    E --> F[Raw Text String]
    F --> G[JSON Parser]
    G --> H[Excalidraw Elements]
    H --> I[Canvas Rendering]
```

1.  **Tokenizer**: 사용자의 자연어 입력을 모델이 이해할 수 있는 토큰 ID 시퀀스로 변환합니다. 2.  **WebAssembly Runtime**: 브라우저 내에서 모델 연산을 수행하는 가상 머신 환경입니다. WebGPU를 통해 하드웨어 가속을 받습니다. 3.  **Gemma 4 Model**: 양자화된 가중치를 메모리에 탑재하고, 각 토큰 다음에 올 확률이 가장 높은 토큰을 예측(Autoregressive)합니다. 4.  **Parser**: 모델이 생성한 텍스트(JSON 형식)를 유효성 검사 후 자바스크립트 객체로 파싱합니다. 5.  **Canvas**: 파싱된 데이터를 기반으로 화면에 도형을 그립니다.

### 모델 양자화 및 구현 예시

연구자나 엔지니어 관점에서 Gemma 4를 브라우저에 배포하기 위해서는 먼저 모델을 양자화해야 합니다. 아래는 Python 환경에서 Hugging Face Transformers 라이브러리와 `bitsandbytes`를 사용하여 모델을 4비트로 양자화하고, 이를 ONNX 또는 GGUF 포맷으로 변환하는 과정을 개념적으로 보여주는 코드입니다.

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

model_id = "google/gemma-4-2b-it"

# 4비트 양자화 설정: 브라우저 메모리 효율을 극대화하기 위해 NF4 혹은 INT4 사용
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

# 모델 로드 및 양자화 적용
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    quantization_config=bnb_config,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(model_id)

# Excalidraw JSON 생성을 위한 프롬프트 엔지니어링
prompt = """
Generate a valid Excalidraw JSON for a simple 'Server-Client' architecture diagram.
Return only the JSON object without markdown formatting.
"""

input_ids = tokenizer(prompt, return_tensors="pt").to("cuda")
outputs = model.generate(**input_ids, max_new_tokens=512)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))

# 실제 배포 시: 이 양자화된 모델을 .onnx 또는 .gguf로 변환하여 웹 서버에 호스팅
```

위 코드는 백엔드 사이드에서의 준비 과정입니다. 실제 브라우저에서는 이렇게 변환된 모델 파일을 `transformers.js`와 같은 라이브러리를 통해 로드하여 실행합니다. 이 프레임워크는 PyTorch 모델을 ONNX로 변환하고, 이를 다시 WASM용 최적화 포맷으로 변경하여 브라우저의 `WebAssembly.Instantiate` 기능을 통해 실행합니다.

### 클라이언트 사이드 추론 vs 서버 사이드 추론 비교

이 기술의 진정한 가치는 기존의 API 기반 서빙 방식과 비교했을 때 명확하게 드러납니다. 특히 다이어그램 생성과 같이 대화형이고 반응성이 중요한 웹 애플리케이션에서 그 장점이 극대화됩니다.

| 비교 항목 | Server-side Inference (OpenAI/Anthropic API) | Client-side Inference (Gemma 4 + WASM) | | :--- | :--- | :--- | | **데이터 프라이버시** | 서버로 프롬프트 전송 필요 (보안 위험 가능성) | 모든 데이터 로컬 처리 (완전 보안) | | **네트워크 레

---

**출처**: [https://teamchong.github.io/turboquant-wasm/draw.html](https://teamchong.github.io/turboquant-wasm/draw.html)