---
title: "Utilyze: nvidia-smi보다 정확한 GPU 실성능(Throughput) 측정"
date: 2026-04-29T01:06:44+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
---

## 서론

대규모 언어 모델(LLM)을 학습하거나 추론하는 과정에서 흔히 겪는 딜레마가 하나 있습니다. 모니터링 대시보드에서 `nvidia-smi`가 GPU 사용량(GPU Utilization) 100%를 고정적으로 찍고 있는데, 정작 학습 속도나 처리량(Throughput)은 기대에 미치지 못하는 상황입니다. 이런 현상을 마주한 엔지니어나 연구자들은 종종 "이미 GPU가 꽉 차고 있는데 더 어떻게 최적화하란 말인가?"라며 막막함을 느낍니다.

결국 팀은 추가 GPU 장비를 도입해야 한다는 결론에 다다르기 쉽습니다. 하지만 이는 근본적인 원인을 해결하지 못한 단순한 자원 투입일 뿐입니다. 실제로 많은 경우 `nvidia-smi`가 보고하는 100%라는 수치는 GPU가 *열심히* 일하고 있다는 것을 의미하지 않습니다. 단지 커널(Kernel)이 실행되기 위해 스케줄러가 붙잡고 있는 시간이 길다는 뜻일 뿐, 실제 연산 유닛(ALU)이 얼마나 효율적으로 데이터를 처리했는지와는 무관합니다.

이러한 오해는 Capacity Planning 과정에서 치명적인 결과를 초래합니다. 실제로는 리소스가 남아돌지만, 잘못된 지표로 인해 시스템이 포화 상태라고 판단하여 비효율적인 비용을 지출하게 되는 것입니다. 정밀한 성능 분석을 위해서는 "얼마나 오래 작동했나"가 아니라 "얼마나 많은 일을 처리했나"를 측정해야 합니다. 이 글에서는 기존 모니터링 툴의 한계를 뛰어넘어 실제 GPU 성능을 정밀 측정하는 오픈소스 툴인 **Utilyze**를 소개하고, 그 기술적 원리와 실무 적용 방안을 살펴보겠습니다.

## 본론

### `nvidia-smi`의 착시 현상과 하드웨어 성능 카운터

기존 `nvidia-smi`, `nvtop`, 그리고 클라우드 제공사(AWS, GCP, Azure)의 대부분의 모니터링 도구는 GPU Utilization을 다음과 같이 정의합니다.
> **GPU Utilization = (하나 이상의 커널이 실행된 시간) / (전체 경과 시간)**

이 지표는 본질적으로 '시간(Time)' 기반의 측정입니다. 만약 GPU가 메모리 대역폭(Memory Bandwidth) 병목에 걸려 연산 유닛이 놀고 있더라도, 커널이 메모리에서 데이터를 기다리며 점유하고 있다면 사용량은 100%로 기록됩니다. 이를 **Memory-bound** 상태라고 합니다. 반대로 데이터 전송은 빠르지만 연산량이 많아 연산 유닛을 꽉 채우는 경우를 **Compute-bound**라고 합니다. `nvidia-smi`는 이 둘을 구별하지 못합니다.

**Utilyze**는 이 접근 방식을 완전히 바꿉니다. Utilyze는 하드웨어 성능 카운터(Performance Monitoring Counters, PMCs)를 직접 샘플링하여, 실제로 실행된 명령어 수와 처리된 데이터 양을 측정합니다. 이를 통해 해당 GPU 하드웨어의 이론적 성능 한도(Theoretical Peak Performance) 대비 실제 성능 비율을 계산합니다.

다음은 기존 방식과 Utilyze의 측정 프로세스를 비교한 간단한 다이어그램입니다.

```javascript
graph TD
    A[워크로드 실행] --> B[기존 방식 nvidia-smi]
    A --> C[Utilyze 방식]
    
    B --> D[커널 실행 시간 측정]
    D --> E[시간 기반 Utilization 계산]
    E --> F{결과: 100% Utilization}
    F --> G[실제 성능 저하 여부 판단 불가]

    C --> H[하드웨어 성능 카운터 샘플링]
    H --> I[실제 FLOPS 및 메모리 바이트 측정]
    I --> J[이론적 Peak 성능과 비교]
    J --> K{결과: 실제 Throughput %}
    K --> L[정확한 병목 지점 식별]
```

### 기술적 깊이: 이론적 한도(Theoretical Peak)와의 비교

Utilyze의 핵심 메커니즘은 '달성 가능한 성능 상한(Attainable Utilization Ceiling)'을 추정하는 것입니다. GPU는 보통 연산 성능(TFLOPS)과 메모리 전송 성능(GB/s) 두 가지 축에서 이론적 최대치가 정해져 있습니다.

예를 들어, NVIDIA A100 GPU의 경우:
- **Compute Peak:** FP32 기준 약 19.5 TFLOPS
- **Memory Bandwidth Peak:** 약 1,555 GB/s (HBM2e)

Utilyze는 실제 워크로드가 이 이론적 수치 중 얼마나 달성했는지 백분율로 보여줍니다. 만약 연산 사용량은 10%인데 메모리 대역폭 사용량이 95%라면, 이 워크로드는 극도로 Memory-bound 상태이므로 더 강력한 GPU로 바꿔도 성능 향상이 기대하기 어렵다는 결론을 내릴 수 있습니다. 반대로 두 지표 모두 매우 낮다면 소프트웨어적인 최적화(CUDA kernel 튜닝 등)가 필요한 상태입니다.

### 실무 적용 가이드 및 코드 예시

Utilyze를 실제 MLOps 파이프라인에 적용하여 GPU 리소스를 최적화하는 방법을 단계별로 살펴보겠습니다.

#### 1. 설치 및 실행

Utilyze는 Python 기반 패키지로 제공되며, 별도의 복잡한 설정 없이 특정 프로세스(PID)를 모니터링할 수 있습니다.

```bash
# pip를 통한 설치
pip install utilyze

# 분석하고자 하는 PyTorch 학습 스크립트 실행 (백그라운드)
python train_llm.py --batch_size 32 &

# 프로세스 ID(PID) 확인 후 Utilyze 실행
# 예: PID가 12345인 경우
utilyze monitor --pid 12345
```

#### 2. Python 코드 내에서의 활용 (워크로드 시뮬레이션)

실제 상황에서 발생할 수 있는 두 가지 시나리오(Compute-bound vs. Memory-bound)를 PyTorch 코드로 간단히 구현하고, Utilyze가 이를 어떻게 식별하는지 확인해 보겠습니다.

```python
import torch
import time

# GPU가 사용 가능한지 확인
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

def scenario_compute_bound():
    """
    연산 병목 시나리오:
    복잡한 행렬 연산 수행 (데이터 크기는 상대적으로 작음)
    연산 유닛을 많이 사용하지만 메모리 이동은 적음
    """
    print("
[Scenario 1] Compute-bound Workload Start")
    x = torch.randn(4096, 4096, device=device)
    
    for _ in range(100):
        # 복잡한 행렬곱 수행
        y = torch.matmul(x, x)
        # 비선형 활성화 함수 추가
        y = torch.nn.functional.relu(y)
    
    torch.cuda.synchronize()
    print("[Scenario 1] Done. Utilyze 확인: Compute Throughput 높음 예상")

def scenario_memory_bound():
    """
    메모리 병목 시나리오:
    단순한 연산이지만 매우 큰 데이터를 메모리에서 로드 및 저장
    메모리 대역폭이 병목이 됨
    """
    print("
[Scenario 2] Memory-bound Workload Start")
    # 매우 큰 텐서 생성 (메모리 사용량 증가)
    size = 20000
    x = torch.randn(size, size, device=device)
    
    for _ in range(10):
        # 단순 합계 연산 (Element-wise addition) - 메모리 접근 위주
        y = x + 1.0
        x = y - 1.0
        
    torch.cuda.synchronize()
    print("[Scenario 2] Done. Utilyze 확인: Memory Throughput 높음, Compute 낮음 예상")

if __name__ == "__main__":
    # 테스트 실행 (실행 시 utilyze monitor --pid <PID>를 터미널에서 띄워둘 것)
    scenario_compute_bound()
    time.sleep(2)
    scenario_memory_bound()
```

이 코드를 실행하는 동안 `utilyze monitor`를 실행하면, 시나리오 1에서는 Compute Throughput이 높게, 시나리오 2에서는 Memory Throughput이 높게 측정되는 것을 확인할 수 있습니다. 이를 통해 `nvidia-smi`로는 구별할 수 없었던 워크로드의 특성을 정확히 파악할 수 있습니다.

#### 3. 측정 결과 해석 및 비교

다음은 각 도구가 제공하는 지표의 차이점을 정리한 표입니다.

| 비교 항목 | nvidia-smi (Legacy) | Utilyze (Modern) |
| :--- | :--- | :--- |
| **측정 대상** | 커널 실행 시간 (Time) |  |

---

**출처**: [https://www.systalyze.com/utilyze](https://www.systalyze.com/utilyze)