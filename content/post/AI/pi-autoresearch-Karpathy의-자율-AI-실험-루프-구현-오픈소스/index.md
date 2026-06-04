---
title: "pi-autoresearch: Karpathy의 자율 AI 실험 루프 구현 오픈소스"
date: 2026-04-30T01:07:52+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
---

## 서론

새벽 3시, 실험 로그를 뒤적이며 당신은 자문합니다. "이 아이디어, 정말 worth a try일까?" GPU 클러스터는 유휴 상태이고, Notion에는 검증되지 않은 가설만 수십 개 쌓여 있습니다. 연구자의 시간은 부족하고, 실험은 끝이 없습니다.

Andrej Karpathy가 최근 제시한 **"AI 자율 실험 루프"** 개념은 이 문제에 대한 도발적인 답입니다. 아이디어를 자동 생성하고, 실험을 실행하며, 결과를 측정하고, 개선되면 유지·그렇지 않으면 폐기하는 무한 루프. 인간 연구자를 대체하는 것이 아니라 **연구 파이프라인을 자동화**하는 패러다임 전환입니다.

이 개념을 실제로 구현한 오픈소스 프로젝트 **pi-autoresearch**가 등장했습니다. 터미널 기반으로 작동하며, LLM을 연구 어시스턴트로 활용해 아이디어 생성부터 검증까지 전체 사이클을 자동화합니다. 오늘은 이 시스템의 아키텍처, 작동 원리, 그리고 실제 활용 방법을 깊이 있게 분석해보겠습니다.

## 본론

### Karpathy의 자율 실험 철학

Karpathy가 제시한 핵심 루프는 놀라울 정도로 단순합니다:
> **"아이디어를 시도하고 → 측정하고 → 개선되면 유지, 아니면 버리고 → 영원히 반복한다."**

이는 과학적 방법론의 본질을 자동화한 것입니다. 중요한 점은 **"영원히"**라는 키워드입니다. 인간 연구자는 피로하고, 편향에 빠지며, 직관에 의존합니다. 하지만 자율 시스템은 편견 없이 무한히 반복할 수 있습니다.

```javascript
graph TD
    A[Idea Generation via LLM] --> B[Experiment Design]
    B --> C[Code Implementation]
    C --> D[Execution & Training]
    D --> E[Metric Evaluation]
    E --> F{Improved?}
    F -->|Yes| G[Merge & Document]
    F -->|No| H[Discard & Log]
    G --> I[Update Baseline]
    H --> I
    I --> A
```

### pi-autoresearch 아키텍처 분석

pi-autoresearch는 이 철학을 실제 코드로 구현한 프로젝트입니다. 핵심 컴포넌트를 분해해보겠습니다.

#### 1. 아이디어 생성 엔진

LLM 기반 아이디어 생성은 단순한 프롬프트가 아닙니다. **컨텍스트 인식 아이디어 생성(Context-Aware Idea Generation)**이 핵심입니다:
- 현재 베스트 모델의 아키텍처
- 이전에 시도했고 실패한 아이디어 이력
- 관련 논문의 최신 트렌드
- 현재 성능 메트릭과 병목 지점

이 모든 컨텍스트를 LLM에 주입하여 **실행 가능한(featible)** 아이디어를 생성합니다.

#### 2. 실험 실행 파이프라인

생성된 아이디어는 자동으로 코드로 변환됩니다. 핵심은 **안전한 샌드박스 실행**입니다:

```python
import subprocess
import json
from pathlib import Path
from dataclasses import dataclass

@dataclass
class ExperimentConfig:
    idea_description: str
    base_model_path: str
    dataset_name: str
    max_iterations: int = 1000
    metric_to_improve: str = "val_loss"
    patience: int = 5

class AutoResearchAgent:
    def __init__(self, config: ExperimentConfig, llm_client):
        self.config = config
        self.llm = llm_client
        self.history = []
        self.best_score = float('inf')
        
    def generate_idea(self) -> dict:
        """LLM을 활용한 컨텍스트 인식 아이디어 생성"""
        context = {
            "current_architecture": self._load_current_model_summary(),
            "failed_ideas": self._get_failed_ideas(),
            "metrics": self._get_current_metrics(),
            "recent_papers": self._fetch_recent_papers()
        }
        
        prompt = f"""
        Based on the following context, propose ONE specific, 
        testable improvement idea:
        
        Current Model: {context['current_architecture']}
        Current Metric ({self.config.metric_to_improve}): {context['metrics']}
        Failed Attempts: {context['failed_ideas'][-5:]}
        
        Output format:
        {{
            "idea_name": "short_name",
            "description": "detailed description",
            "code_changes": "specific code modifications",
            "expected_improvement": "quantified expectation"
        }}
        """
        
        response = self.llm.generate(prompt)
        return json.loads(response)
    
    def execute_experiment(self, idea: dict) -> dict:
        """아이디어를 코드로 변환하고 실행"""
        # 코드 수정 사항을 패치로 생성
        patch = self.llm.generate_code_patch(
            idea, 
            base_code=self._load_base_code()
        )
        
        # 백업 후 패치 적용
        self._backup_current_state()
        self._apply_patch(patch)
        
        # 실험 실행
        result = subprocess.run(
            ["python", "train.
```

```python
py", 
             "--config", self.config.base_model_path,
             "--output", f"runs/{idea['idea_name']}"],
            capture_output=True,
            text=True,
            timeout=3600  # 1시간 타임아웃
        )
        
        # 메트릭 수집
        metrics = self._parse_metrics(result.stdout)
        
        return {
            "idea": idea,
            "metrics": metrics,
            "success": result.returncode == 0,
            "logs": result.stdout[-5000:]  # 마지막 5000자
        }
    
    def evaluate_and_decide(self, result: dict) -> bool:
        """결과 평가 및 유지/폐기 결정"""
        current_score = result["metrics"][self.config.metric_to_improve]
        
        improved = current_score < self.best_score
        
        if improved:
            self.best_score = current_score
            self._commit_changes(result["idea"])
            print(f"[IMPROVED] {result['idea']['idea_name']}: "
                  f"{self.best_score:.4f}")
        else:
            self._revert_changes()
            print(f"[DISCARDED] {result['idea']['idea_name']}: "
                  f"{current_score:.4f}")
        
        self.history.append({
            "idea": result["idea"]["idea_name"],
            "score": current_score,
            "improved": improved
        })
        
        return improved
    
    def run_loop(self, max_iterations: int = 100):
        """메인 자율 연구 루프"""
        for i in range(max_iterations):
            print(f"
=== Iteration {i+1}/{max_iterations} ===")
            
            # 1. 아이디어 생성
            idea = self.generate_idea()
            print(f"Testing idea: {idea['idea_name']}")
            
            # 2. 실험 실행
            result = self.execute_experiment(idea)
            
            if not result["success"]:
                print(f"Execution failed: {result['logs'][-500:]}")
                continue
            
            # 3. 평가 및 결정
            self.evaluate_and_decide(result)
            
            # 4.
```

```python
 중간 결과 리포트
            if (i + 1) % 10 == 0:
                self._generate_progress_report()

# 실행 예시
if __name__ == "__main__":
    config = ExperimentConfig(
        idea_description="autoresearch_loop",
        base_model_path="configs/base_transformer.yaml",
        dataset_name="wikitext-103",
        metric_to_improve="val_loss"
    )
    
    agent = AutoResearchAgent(config, llm_client=None)
    agent.run_loop(max_iterations=50)
```

#### 3. 메트릭 평가 시스템

객관적인 평가가 자율 연구의 생명입니다. pi-autoresearch는 다중 메트릭 평가를 지원합니다:

| 평가 지표 | 용도 | 임계값 설정 | 주기 |
| :--- | :--- | :--- | :--- |
| Validation Loss | 모델 품질 | 이전 최솟값 대비 | 매 에포크 |
| Training Time | 효율성 | 베이스라인 대비 2배 | 실험당 |
| GPU Memory | 리소스 제약 | 사용 가능 VRAM의 90% | 실험당 |
| Metric Variance | 안정성 | 표준편차 < 0.01 | 3회 실행 |
| Downstream Task | 실제 성능 | 태스크별 기준치 | 10회 반복마다 |

### Step-by-Step: pi-autoresearch 설정 가이드

실제 프로젝트를 시작하는 방법을 단계별로 설명합니다.

#### Step 1: 환경 설정

```bash
# 저장소 클론
git clone https://github.com/davebcn87/pi-autoresearch.git
cd pi-autoresearch

# 의존성 설치
pip install -r requirements.txt

# LLM API 키 설정 (OpenAI/Anthropic)
export OPENAI_API_KEY="your-key-here"
# 또는
export ANTHROPIC_API_KEY="your-key-here"
```

#### Step 2: 베이스라인 모델 준비

```python
# baseline_model.py
import torch
import torch.nn as nn

class BaselineTransformer(nn.Module):
    """비교 기준이 되는 베이스라인 모델"""
    def __init__(self, vocab_size=32000, d_model=512, nhead=8, 
                 num_layers=6, max_seq_len=2048):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoding = nn.Parameter(
            torch.randn(1, max_seq_len, d_model) * 0.02
        )
        
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=d_model * 4,
            dropout=0.1,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(
            encoder_layer, num_layers=num_layers
        )
        self.lm_head = nn.Linear(d_model, vocab_size, bias=False)
        
    def forward(self, input_ids):
        x = self.embedding(input_ids) + self.pos_encoding[:, :input_ids.size(1), :]
        x = self.transformer(x)
        logits = self.lm_head(x)
        return logits

# 베이스라인 성능 측정
def evaluate_baseline(model, val_loader, device="cuda"):
    model.eval()
    total_loss = 0
    criterion = nn.CrossEntropyLoss()
    
    with torch.no_grad():
        for batch in val_loader:
            input_ids = batch["input_ids"].to(device)
            labels = batch["labels"].to(device)
            
            logits = model(input_ids)
            loss = criterion(
                logits.view(-1, logits.size(-1)), 
                labels.view(-1)
            )
            total_loss += loss.item()
    
    avg_loss = total_loss / len(val_loader)
    print(f"Baseline Val Loss: {avg_loss:.4f}")
    return avg_loss
```

#### Step 3: 자율 연구 루프 실행

```bash
# 터미널에서 자율 연구 루프 시작
python -m pi_autoresearch \
    --base-model configs/baseline.yaml \
    --dataset wikitext-103-raw-v1 \
    --metric val_loss \
    --max-iterations 100 \
    --llm-model gpt-4-turbo-preview \
    --verbose

# 출력 예시:
# [2024-01-15 10:00:01] Starting autonomous research loop
# [2024-01-15 10:00:02] Baseline val_loss: 3.4521
# [2024-01-15 10:05:12] Idea #1: Add rotary positional embeddings
# [2024-01-15 10:25:34] Result: val_loss = 3.3801 [IMPROVED ✓]
# [2024-01-15 10:30:01] Idea #2: Implement flash attention
# [2024-01-15 10:50:22] Result: val_loss = 3.3950 [DISCARDED ✗]
# ...
```

### 핵심 설계 결정 및 트레이드오프

pi-autoresearch의 설계에서 몇 가지 흥미로운 결정이 있습니다.

#### LLM을 메타러너(Meta-Learner)로 사용

전통적인 AutoML은 탐색 공간을 하드코딩합니다. pi-autoresearch는 **LLM을 메타러너로 사용**하여 탐색 공간 자체를 동적으로 생성합니다. 이는 NAS(Neural Architecture Search)와 근본적으로 다른 접근입니다:

| 접근 방식 | 탐색 공간 | 비용 | 발견 가능성 |
| :--- | :--- | :--- | :--- |
| Grid Search | 사전 정의 | 낮음 | 제한적 |
| Bayesian Optimization | 사전 정의 | 중간 | 보통 |
| NAS | 제약 조건 내 | 매우 높음 | 높음 |
| **LLM 기반 생성** | **무한** | **중간** | **매우 높음** |

#### 안전 메커니즘

자율 시스템의 위험을 완화하기 위한 장치가 있습니다:

1. **타임아웃**: 각 실험은 1시간 제한
2. **리소스 모니터링**: GPU 메모리 초과 시 자동 중단
3. **체크포인트**: 성공 상태를 Git 커밋으로 관리
4. **휴리스틱 필터**: LLM이 생성한 아이디어를 실행 전 사전 검증

```python
# safety_checks.py
class SafetyChecker:
    def validate_idea(self, idea: dict) -> bool:
        """실행 전 아이디어 안전성 검증"""
        # 1. 코드 인젝션 방지
        if any(cmd in str(idea) for cmd in ["os.system", "subprocess", "eval"]):
            return False
        
        # 2. 리소스 추정
        estimated_vram = self._estimate_vram(idea)
        if estimated_vram > self.max_vram * 0.9:
            return False
        
        # 3. 중복 실험 방지
        if self._is_duplicate(idea):
            return False
            
        return True
```

### 실제 성능 및 한계

pi-autoresearch는 아직 초기 단계지만, 개념 증명(proof-of-concept)으로서 가치가 있습니다. 실제 테스트에서 관찰된 패턴:

**긍정적 측면:**
- 100회 반복 중 약 15-20%의 아이디어가 실제 개선을 보임
- 인간 연구자가 간과할 수 있는 조합적 아이디어 탐색
- 24/7 실험 실행으로 연구자 시간 절약

**현재 한계:**
- 장거리 의존성(long-range dependency) 파악 부족
- 아이디어의 다양성이 초기 컨텍스트에 종속
- 단일 메트릭 최적화에 치우침 위험
- 실패 분석의 질

---

**출처**: [https://news.hada.io/topic?id=28600](https://news.hada.io/topic?id=28600)