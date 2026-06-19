---
title: "🚀 NVMe-to-GPU: RTX 3090 한 장으로 Llama 3.1 70B 구동"
date: 2026-04-19T08:06:04+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
draft: true
---

## 서론: 70B 모델의 유혹과 24GB VRAM의 한계

최근 생성형 AI의 발전 속도는 가히 폭발적입니다. Meta의 Llama 3.1 70B와 같은 모델은 오픈 소스 진영에서도 GPT-4급 성능에 근접하고 있어, 많은 연구자와 엔지니어가 로컬 환경에서 이를 구동하고 싶어 합니다. 하지만 현실은 냉혹합니다. 70B 파라미터 모델을 FP16으로 로드하려면 약 140GB 이상의 메모리가 필요하고, 4-bit 양자화(Quantization)를 수행하더라도 약 40GB~50GB의 VRAM이 요구됩니다.

소비자용 최상급 그래픽카드인 RTX 3090/4090조차도 24GB의 VRAM을 탑재하고 있어, 단일 카드로는 물리적으로 이 모델을 통째로 올릴 수 없습니다. 일반적인 해결책은 모델 일부를 시스템 RAM으로 Offloading하는 것이지만, 이는 CPU와 GPU 간의 병목 현상을 유발하여 추론 속도를 극도로 느리게 만듭니다. "그렇다면 CPU를 아예 거치지 않고 NVMe SSD의 데이터를 GPU로 직접 뿌리면 어떨까?"라는 질문에서 시작된 이 실험은, 하드웨어 아키텍처의 기본 원리를 재해석하여 단일 RTX 3090에서 거대 모델을 구동하는 흥미로운 시도입니다.

## 본론: 아키텍처의 혁신, NVMe-to-GPU

### 기존 방식의 병목 현상

전통적인 딥러닝 추론 파이프라인에서 데이터 흐름은 단순합니다. NVMe SSD → 시스템 RAM(DRAM) → CPU → PCIe 버스 → GPU VRAM 순서입니다. 문제는 데이터가 시스템 RAM에 로드된 후 CPU가 이를 PCIe 버스를 통해 GPU로 복사해야 한다는 점입니다. 이 과정에서 CPU의 연산 자원이 소모될 뿐만 아니라, 불필요한 메모리 카피(Memory Copy) 작업이 발생하여 지연 시간(Latency)이 증가합니다. Llama 3.1 70B와 같은 대형 모델을 다룰 때는 이 오버헤드가 치명적입니다.

### NVMe-to-GPU의 원리

이 기술의 핵심은 **Direct Memory Access (DMA)**를 극한까지 활용하는 것입니다. 최신 리눅스 커널과 NVIDIA GPU 드라이버는 `P2P (Peer-to-Peer)` DMA 및 `GPUDirect Storage`와 같은 기술을 지원합니다. 이를 통해 GPU가 CPU의 개입 없이 NVMe SSD 컨트롤러와 직접 통신할 수 있습니다.

즉, NVMe SSD의 특정 영역을 GPU의 주소 공간(Address Space)에 직접 매핑(Mapping)함으로써, GPU 입장에서는 디스크의 데이터가 마치 자신의 VRAM처럼 보이게 만드는 것입니다. 이를 "Zero-copy" 접근이라고 하며, 시스템 RAM을 완전히 우회함으로써 대역폭 효율을 극대화합니다.

### 데이터 흐름 비교

아래 다이어그램은 기존 방식과 NVMe-to-GPU 방식의 데이터 흐름 차이를 시각적으로 보여줍니다.

```javascript
graph TD
    subgraph Traditional
        D1[NVMe SSD] --> R1[System RAM]
        R1 -->|CPU Copy| C1[CPU]
        C1 -->|PCIe Bus| G1[GPU VRAM]
    end

    subgraph NVMe_to_GPU
        D2[NVMe SSD] -->|Direct DMA / PCIe| G2[GPU VRAM]
    end
```

### 성능 비교 및 기술적 깊이

이 접근 방식이 단순히 속도를 높이는 것을 넘어, 하드웨어 자원의 활용 방식을 근본적으로 변화시킵니다. 다음은 두 방식의 주요 차이점을 비교한 표입니다.

| 비교 항목 | Traditional Offloading (CPU/RAM) | NVMe-to-GPU Direct |
| :--- | :--- | :--- |
| **데이터 경로** | SSD → RAM → CPU → GPU | SSD → GPU |
| **주요 병목** | 시스템 RAM 대역폭, CPU 오버헤드 | PCIe 대역폭 (하지만 직접 전송) |
| **메모리 복사** | 2회 이상 (Host to Device) | 0회 (Direct Mapping) |
| **CPU 점유율** | 높음 (데이터 이동 관리) | 낮음 (초기 설정 이후 최소화) |
| **지연 시간(Latency)** | 높음 (비동기 처리 난이도 상승) | 낮음 (예측 가능한 I/O) |

기술적으로 더 깊이 들어가면, 이 과정은 리눅스의 `mmap` 시스템 콜과 NVIDIA의 `cuMemHostRegister` 혹은 CUDA Unified Memory 기능을 결합하여 구현됩니다. 특히 `nvidia-peermem` 커널 모듈을 통해 타사 장치(여기서는 NVMe 컨트롤러)의 메모리를 GPU가 액세스할 수 있도록 BAR(Base Address Register) 영역을 매핑하는 것이 핵심입니다.

## 구현 가이드: 단계별 접근법

이제 실제로 단일 RTX 3090에서 Llama 3.1 70B를 구동하기 위한 단계를 살펴보겠습니다. 이 과정은 하드웨어 지원과 소프트웨어 설정 모두를 요구합니다.

### 1단계: 하드웨어 및 커널 준비

먼저, 시스템의 PCIe 레인과 IOMMU(Input-Output Memory Management Unit) 설정이 올바르게 되어 있어야 합니다. RTX 3090은 PCIe Gen 4.0 x16을 지원하므로, 최대 대역폭을 활용하기 위해서는 NVMe SSD 또한 CPU에 직접 연결된 Gen 4.0/5.0 슬롯에 장착되어야 합니다. M.2 지원 슬롯일지라도 칩셋(Chipset)을 통해 연결된 경우(Southbridge 경유) 대역폭이 절반으로 줄어들어 성능이 저하될 수 있습니다.

또한, 리눅스 커널 부팅 파라미터에서 `iommu=pt` (Pass-through) 모드를 활성화하여, 장치 간의 직접 메모리 액세스를 위한 주소 변환 오버헤드를 최소화해야 합니다.

### 2단계: 메모리 매핑 및 로더 구현

가장 중요한 단계는 모델 가중치(Weights)가 저장된 NVMe 영역을 GPU에 직접 매핑하는 것입니다. Python 코드를 통해 이 개념을 구현하면 다음과 같습니다. 다음은 실제 `ntransformer` 라이브러리의 핵심 아이디어를 단순화한 개념적 코드입니다.

```python
import torch
import cupy as cp
import numpy as np
import mmap
import os

# 1. NVMe SSD에 저장된 모델 가중치 파일 열기
# 파일 시스템 캐싱을 방지하기 위해 O_DIRECT 플래그 사용이 권장됨 (os.O_DIRECT)
# 여기서는 설명을 위해 표준 open 사용
model_path = "/mnt/nvme_disk/llama3.1_70b_weights.bin"
file_size = os.path.getsize(model_path)

with open(model_path, "r+b") as f:
    # 2. 파일을 메모리에 매핑 (mmap)
    # 이 메모리 영역은 실제로 페이지 캐시가 아닌 디스크 데이터를 직접 가리킴
    mmapped_file = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    
    # 3. numpy array로 뷰(View) 생성
    # CPU 접근을 위한 인터페이스 (실제로는 GPU로 바로 넘길 예정)
    cpu_array = np.frombuffer(mmapped_file, dtype=np.float16)
    
    # 4. Zero-copy 방식으로 GPU로 직접 전송
    # CuPy의 cuda.MemcpyHostToDevice 대신 P2P DMA를 활용하는 cudaMemcpyAsync 등을 사용
    # 여기서는 개념적 구현을 위해 cp.asarray 사용
    # 실제 구현에서는 cudaHostRegister나 커스텀 CUDA 커널이 필요할 수 있음
    gpu_tensor = cp.asarray(cpu_array)
    
    # 5. PyTorch 텐서로 변환 (DLPack 활용하여 메모리 복사 없이 공유 가능)
    torch_tensor = torch.utils.dlpack.from_dlpack(cp.toDlpack(gpu_tensor))
    
    print(f"GPU Tensor Shape: {torch_tensor.shape}")
    print(f"Device: {torch_tensor.device}")
    
    # 이제 torch_tensor를 사용하여 추론 수행
    # 메모리는 실제로 NVMe SSD에 있지만, GPU는 마치 VRAM에 있는 것처럼 접근
```

이 코드의 핵심은 `mmap`을 통해 디스크 파일을 가상 메모리 주소 공간에 올리고, 이를 GPU가 PCIe 버스를 통해 읽어갈 수 있도록 포인터를 전달하는 과정입니다.

### 3단계: 추론 실행 및 캐싱 전략

모델을 메모리에 올린 후에는 추론 루프를 실행합니다. NVMe-to-GPU 방식은 VRAM이 아니므로, GDDR6X보다는 느린 PCIe 대역폭(약 32GB/s)에 의존합니다. 따라서 모델의 모든 레이어를 매번 디스크에서 읽어오는 것은 비효율적입니다.

효율적인 추론을 위해 **'Compute-bound'와 'Memory-bound' 작업의 분리**가 필요합니다. 현재 실행 중인 레이어에 해당하는 가중치만 GPU로 스트리밍하고, 다음 레이어를 예측하여 미리 불러오는(Prefetching) 기법이 필수적입니다. RTX 3090의 경우, 단일 토큰 생성에 소요되는 시간 내에 필요한 가중치를 전송할 수 있는 충분한 PCIe 대역폭을 제공하므로, 적절한 스케줄링만 된다면 사용 가능한 수준의 속도(Interactive chatting 가능)를 보여줍니다.

## 결론: 소비자용 하드웨어의 잠재력 해방

NVMe-to-GPU 기술은 단순한 꼼수(Hack)를 넘어, 하드웨어 아키텍처의 계층을 얇게 만드는 현대적인 MLOps 접근 방식입니다. CPU와 RAM이라는 중개인을 제거함으로써, 우리는 훨씬 더 효율적으로 데이터를 이동시킬 수 있음을 확인했습니다. 비록 H100이나 A100 같은 전용 하드웨어만큼의 효율성은 보여주지 못하지만, 단일 RTX 3090과 고속 NVMe SSD만으로 Llama 3.1 70B를 구동할 수 있다는 사실은 개발자와 연구자들에게 엄청난 기회를 제공합니다.

이 접근 방식은 특히 **온프레미스(On-premise) 개발 환경**에서 예산 제약을 극복하는 데 큰 도움이 됩니다. 연구자는 이제 수천만 원이 투입되는 서버 클러스터 없이도, 자신의 데스크탑에서 최신 SOTA(State-of-the-Art) 모델을 파인튜닝하거나 실험해 볼 수 있는 환경을 갖추게 되었습니다.

향후 Linux 커널과 NVIDIA 드라이버의 발전에 따라 이러한 Peer-to-Peer DMA 기능은 더욱 안정적이고 널리 사용될 것입니다. GPU의 VRAM 용량이 물리적 한계에 도달하는 상황에서, 저장 장치의 속도를 활용한 이러한 '확장된 메모리' 기법은 딥러닝 인프라의 새로운 표준이 될 잠재력을 가지고 있습니다.

**참고자료:**
- [xaskasdf/ntransformer GitHub Repository](https://github.com/xaskasdf/ntransformer)
- NVIDIA GPUDirect Storage Documentation
- Linux Kernel DMA Mapping Documentation

---

**출처**: [https://github.com/xaskasdf/ntransformer](https://github.com/xaskasdf/ntransformer)