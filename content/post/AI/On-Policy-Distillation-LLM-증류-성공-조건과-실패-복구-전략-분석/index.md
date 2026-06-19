---
title: "On-Policy Distillation: LLM 증류 성공 조건과 실패 복구 전략 분석"
date: 2026-05-01T01:06:45+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
draft: true
---

## 서론

3주간의 fine-tuning을 마치고 드디어 7B 모델을 1.5B로 증류하려던 순간, 학생 모델의 성능이 교사 모델은커녕 증류 전보다도 하락하는 것을 발견했다면? 이는 최근 LLM 연구 커뮤니티가 직면한 공공연한 비밀이다. On-Policy Distillation(OPD)은 GPT-4나 Claude급 교사 모델의 능력을 경량 모델에 전이하는 핵심 기술로 주목받고 있지만, 실무에서는 실패 사례가 성공 못지않게 흔하다.

2025년 arXiv에 발표된 "Rethinking On-Policy Distillation of Large Language Models" 연구는 바로 이 지점을 정면으로 공략한다. OPD가 왜 어떤 경우에는 획기적인 성능 향상을 가져오고, 어떤 경우에는 오히려 모델을 망가뜨리는지에 대한 체계적인 분석을 제공한다. 단순히 "더 많은 데이터, 더 좋은 하이퍼파라미터" 같은 처방이 아니다. 이 연구는 토큰 수준에서의 메커니즘을 파헤치고, 실패한 증류를 복구하는 구체적인 전략까지 제시한다.

대규모 언어 모델을 실제 서비스에 배포하려는 엔지니어에게, 혹은 제한된 컴퓨팅 자원으로 최고의 성능을 짜내야 하는 연구자에게, 이 연구의 발견은 증류 파이프라인 전체를 재설계하는 계기가 될 수 있다.

## 본론

### On-Policy Distillation의 본질: 행동 공간에서의 만남

전통적인 knowledge distillation이 정적 데이터셋에서 교사의 출력 분포를 모방하는 것이라면, OPD는 동적이다. 학생 모델이 스스로 생성한 시퀀스 위에서 교사 모델의 피드백을 받는 방식이다. 이 차이가 왜 중요할까?

```javascript
graph TD
    A[학생 모델 샘플링] --> B[시퀀스 생성]
    B --> C[교사 모델 평가]
    C --> D[토큰별 보상 계산]
    D --> E[정책 그래디언트 업데이트]
    E --> A
```

OPD의 핵심은 학생이 방문한 상태(state)에서 교사가 어떤 토큰을 선호하는지 학습하는 것이다. 하지만 여기에 근본적인 딜레마가 존재한다. 학생이 결코 방문하지 않는 상태 공간에 있는 교사의 지식은 전이될 수 없다. 반대로, 학생과 교사의 사고 패턴이 전혀 다르다면, 교사의 피드백은 일관성 없는 노이즈가 된다.

### OPD 성공의 두 가지 조건

연구가 식별한 두 조건은 직관적이면서도 깊은 통찰을 담고 있다.

**조건 1: 호환되는 사고 패턴 공유**

학생과 교사가 유사한 추론 경로를 따라야 한다. 예를 들어, 수학 문제를 풀 때 교사가 "근의 공식을 사용하자"고 접근하는데 학생이 "대입법을 시도하자"는 방향으로 간다면, 토큰 수준에서의 정렬은 불가능해진다.

**조건 2: 진정한 새로운 능력 제공**

더 흥미로운 발견은 두 번째 조건이다. 교사와 학생의 사고 패턴이 완벽히 일치하더라도, 교사가 학생의 훈련 분포 내에 있는 능력만 보여준다면 증류는 실패한다. 연구진은 "weak-to-strong reverse distillation" 실험으로 이를 증명했다. 1.5B 모델이 7B 교사를 모방하려 할 때, 같은 모델 패밀리라면 분포적으로 구분이 불가능할 정도로 유사해진다. 즉, 교사가 진정으로 "더 나은" 능력을 보여주지 못하는 것이다.

### 토큰 수준 메커니즘: 97-99%의 확률 질량 집중

성공적인 OPD의 가장 인상적인 특징은 토큰 분포의 집중 현상이다.

| 지표 | 성공한 OPD | 실패한 OPD |
| :--- | :--- | :--- |
| 공유 토큰 비율 | 전체 어휘의 극소수 | 상대적으로 넓은 분포 |
| 확률 질량 집중도 | 97%-99% | 70%-85% |
| 정렬 패턴 | 점진적 수렴 | 불안정한 발산 |
| 교사-학생 KL 발산 | 0.1-0.3 (낮음) | 1.5-3.0 (높음) |

이는 무엇을 의미할까? 성공적인 증류에서 교사와 학생은 어휘 집합의 극히 일부분에 대해서만 의미 있는 합의를 이룬다. 나머지 토큰들은 무시해도 될 정도로 낮은 확률을 가진다. 이 "작은 공유 토큰 집합"이 바로 증류가 실제로 일어나는 공간이다.

### 실전 구현: PyTorch 기반 OPD 파이프라인

```python
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer

class OnPolicyDistillator:
    def __init__(
        self, 
        teacher_name: str, 
        student_name: str,
        temperature: float = 2.0,
        alpha: float = 0.5
    ):
        self.teacher = AutoModelForCausalLM.from_pretrained(
            teacher_name, 
            torch_dtype=torch.bfloat16
        )
        self.student = AutoModelForCausalLM.from_pretrained(
            student_name,
            torch_dtype=torch.bfloat16
        )
        self.tokenizer = AutoTokenizer.from_pretrained(teacher_name)
        self.temperature = temperature
        self.alpha = alpha  # KD loss weight
        
        self.teacher.eval()
    
    def compute_shared_token_mass(
        self, 
        teacher_logits: torch.Tensor,
        student_logits: torch.Tensor,
        top_k: int = 10
    ) -> dict:
        """공유 토큰 집합의 확률 질량을 계산"""
        teacher_probs = F.softmax(teacher_logits / self.temperature, dim=-1)
        student_probs = F.softmax(student_logits / self.temperature, dim=-1)
        
        # 각각의 top-k 토큰 추출
        _, teacher_top_indices = torch.topk(teacher_probs, top_k, dim=-1)
        _, student_top_indices = torch.topk(student_probs, top_k, dim=-1)
        
        # 공유 토큰 마스크 생성
        shared_mask = torch.zeros_like(teacher_probs, dtype=torch.bool)
        for i in range(top_k):
            shared_mask.scatter_(
                -1, 
                teacher_top_indices[:,:,i:i+1], 
                True
            )
            shared_mask.scatter_(
                -1, 
                student_top_indices[:,:,i:i+1], 
                True
            )
        
        shared_mass_teacher = (
            teacher_probs * shared_mask
        ).sum(dim=-1).mean().item()
        shared_mass_student = (
            student_probs * shared_mask
        ).sum(dim=-1).mean().
```

```python
item()
        
        return {
            "shared_mass_teacher": shared_mass_teacher,
            "shared_mass_student": shared_mass_student,
            "shared_token_ratio": shared_mask.float().mean().item()
        }
    
    def distillation_step(self, input_ids: torch.Tensor) -> dict:
        """단일 증류 스텝"""
        # 학생으로 시퀀스 생성 (on-policy)
        with torch.no_grad():
            student_outputs = self.student.generate(
                input_ids,
                max_new_tokens=128,
                do_sample=True,
                temperature=0.7,
                top_p=0.9
            )
        
        # 생성된 시퀀스에 대해 교사/학생 로짓 계산
        with torch.no_grad():
            teacher_logits = self.teacher(student_outputs).logits
        student_logits = self.student(student_outputs).logits
        
        # 공유 토큰 질량 모니터링
        metrics = self.compute_shared_token_mass(
            teacher_logits[:, -128:, :], 
            student_logits[:, -128:, :]
        )
        
        # KL divergence loss
        teacher_probs = F.softmax(
            teacher_logits / self.temperature, dim=-1
        )
        student_log_probs = F.log_softmax(
            student_logits / self.temperature, dim=-1
        )
        
        kd_loss = F.kl_div(
            student_log_probs,
            teacher_probs,
            reduction='batchmean'
        ) * (self.temperature ** 2)
        
        return {"loss": kd_loss, "metrics": metrics}
```

이 코드에서 주목할 점은 `compute_shared_token_mass` 함수다. 실시간으로 교사-학생 간 공유 토큰 집합의 확률 질량을 모니터링하여, 증류가 올바른 방향으로 진행되는지 진단할 수 있다.

### 실패 복구 전략 1: Off-Policy Cold Start

```javascript
graph LR
    A[Cold Start 실패 상태] --> B[Off-Policy 데이터로 초기화]
    B --> C[교사 시퀀스로 예열]
    C --> D[On-Policy로 전환]
    D --> E[정상 증류 진행]
```

가장 실용적인 복구 전략은 off-policy cold start다. 학생 모델이 처음부터 on-policy로 시작하면, 초기의 낮은 품질 시퀀스 때문에 교사의 피드백이 무의미해진다. 대신, 교사 모델이 생성한 고품질 시퀀스로 먼저 학생을 예열(warm-up)하는 것이다.

```python
def off_policy_cold_start(
    distillator: OnPolicyDistillator,
    prompts: list[str],
    warmup_steps: int = 500
):
    """Off-policy cold start 구현"""
    optimizer = torch.optim.AdamW(
        distillator.student.parameters(),
        lr=1e-5
    )
    
    for step in range(warmup_steps):
        prompt = prompts[step % len(prompts)]
        input_ids = distillator.tokenizer(
            prompt, return_tensors="pt"
        ).input_ids.cuda()
        
        # 교사가 시퀀스 생성 (off-policy)
        with torch.no_grad():
            teacher_seq = distillator.teacher.generate(
                input_ids.cuda(),
                max_new_tokens=256,
                do_sample=True,
                temperature=0.8
            )
        
        # 교사 시퀀스에 대해 학생 학습
        with torch.no_grad():
            teacher_logits = distillator.teacher(
                teacher_seq
            ).logits
        
        student_logits = distillator.student(teacher_seq).logits
        
        # 표준 KD loss 계산
        loss = F.kl_div(
            F.log_softmax(student_logits / 2.0, dim=-1),
            F.softmax(teacher_logits / 2.0, dim=-1),
            reduction='batchmean'
        ) * 4.0
        
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
        
        if step % 100 == 0:
            print(f"Warmup step {step}, Loss: {loss.item():.4f}")
    
    return distillator
```

### 실패 복구 전략 2: Teacher-Aligned Prompt Selection

두 번째 전략은 프롬프트 선택의 문제로 접근한다. 모든 프롬프트가 증류에 동등하게 유용한 것이 아니다. 교사 모델의 사고 패턴과 정렬된 프롬프트만 선별하여 학습하는 것이다.

```python
def select_teacher_aligned_prompts(
    teacher_model,
    student_model,
    tokenizer,
    candidate_prompts: list[str],
    alignment_threshold: float = 0.7
) -> list[str]:
    """교사와 정렬된 프롬프트 선별"""
    aligned_prompts = []
    
    for prompt in candidate_prompts:
        input_ids = tokenizer(
            prompt, return_tensors="pt"
        ).input_ids
        
        # 각 모델의 응답 생성
        with torch.no_grad():
            teacher_response = teacher_model.generate(
                input_ids.cuda(),
                max_new_tokens=64,
                do_sample=False  # 결정론적 비교
            )
            student_response = student_model.generate(
                input_ids.cuda(),
                max_new_tokens=64,
                do_sample=False
            )
        
        # 응답 유사도 계산 (간소화된 버전)
        teacher_text = tokenizer.decode(
            teacher_response[0], skip_special_tokens=True
        )
        student_text = tokenizer.decode(
            student_response[0], skip_special_tokens=True
        )
        
        # 토큰 오버랩 기반 유사도
        teacher_tokens = set(teacher_text.split())
        student_tokens = set(student_text.split())
        
        if len(teacher_tokens) == 0:
            continue
            
        overlap = len(teacher_tokens & student_tokens)
        similarity = overlap / len(teacher_tokens)
        
        if similarity >= alignment_threshold:
            aligned_prompts.append(prompt)
    
    return aligned_prompts
```

### OPD의 숨겨진 비용: Long-Horizon의 함정

연구의 마지막 부분은 다소 우울한, 하지만 반드시 직면해야 할 통찰을 제공한다. OPD의 "공짜 점심" 같은 dense token-level reward에는 숨겨진 비용이 있다.

```javascript
graph TD
    A[OPD 시작] --> B{시퀀스 길이}
    B -->|짧은 시퀀스| C[안정적 학습]
    B -->|긴 시퀀스| D[에러 누적]
    D --> E[분포 편향 증가]
    E --> F[교사-학생 간극 확대]
    C --> G[성공적 증류]
    F --> H[증류 실패]
```

짧은 시퀀스에서는 각 토�

---

**출처**: [http://arxiv.org/abs/2604.13016v1](http://arxiv.org/abs/2604.13016v1)