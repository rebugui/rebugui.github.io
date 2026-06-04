---
title: "Soul Spec: AI 에이전트 페르소나 표준으로 정체성 보호하기"
date: 2026-04-07T01:05:12+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
---

## 서론

개발자 "김"은 자신이 만든 고객 지원 AI 에이전트가 어느 날 갑자기 이상한 말을 하기 시작했다는 버그 리포트를 받았다. 평소 "친절하고 전문적인 상담원"이었던 에이전트가 사용자의 장난스러운 질문에 "나는 사실 해적왕이 될 거야!"라고 대답한 것이다. 로그를 확인해보니 시스템 프롬프트가 사용자 입력에 의해 우회당한 것이 원인이었다.

이것은 단순한 장난이 아니다. **abliterated LLM** (거부 메커니즘이 제거된 "탈옥" 모델)의 등장으로, AI 에이전트의 시스템 프롬프트 변조는 더 이상 이론적 위협이 아니다. 에이전트의 핵심 정체성—페르소나—를 어떻게 정의하고, 어떻게 보호할 것인가? 이 질문이 Soul Spec 프로젝트의 출발점이다.

## 본론

### 1. 문제의 본질: 시스템 프롬프트의 취약성

현대 AI 에이전트 아키텍처에서 시스템 프롬프트는 에이전트의 "영혼" 역할을 한다. 그러나 이 영혼은 놀라울 정도로 취약하다.

```javascript
graph TD
    A[User Input] --> B[Context Window]
    C[System Prompt] --> B
    B --> D[LLM Inference]
    D --> E[Response]
    
    F[Attacker Input] --> G[Prompt Injection]
    G --> B
    
    H[ABLiterated LLM] --> D
```

**핵심 취약점 세 가지:**

| 취약점 유형 | 설명 | 위험도 |
| :--- | :--- | :--- |
| Direct Injection | 사용자 입력이 시스템 프롬프트를 직접 덮어씀 | 높음 |
| Indirect Injection | 외부 데이터(RAG, 웹검색)를 통한 악성 프롬프트 주입 | 중간 |
| Model-Level Bypass | ABLiterated 모델에서 거부 메커니즘 무력화 | 매우 높음 |

### 2. Soul Spec: 페르소나 표준화 접근법

Soul Spec은 AI 에이전트의 정체성을 **구조화된 명세(Specification)**로 정의한다. 단순 텍스트 프롬프트가 아닌, 검증 가능한 형식이다.

```javascript
graph LR
    A[Soul Spec YAML] --> B[Parser]
    B --> C[Validated Persona]
    C --> D[Agent Runtime]
    
    E[Hash Signature] --> C
    C --> F[Integrity Check]
```

#### 2.1 Soul Spec 구조

```yaml
# soul-spec-v1.yaml
soul_spec_version: "1.0"
identity:
  name: "CustomerSupport-Agent"
  role: "Technical Support Specialist"
  version: "2.1.0"
  
core_traits:
  - trait: "professional"
    weight: 0.9
    immutable: true
  - trait: "empathetic"
    weight: 0.7
    immutable: true
  - trait: "concise"
    weight: 0.6
    immutable: false

behavioral_constraints:
  - type: "tone"
    allowed: ["polite", "professional", "helpful"]
    forbidden: ["sarcastic", "aggressive", "casual"]
  - type: "topic"
    allowed: ["product_support", "technical_help", "billing"]
    forbidden: ["politics", "religion", "personal_opinion"]

response_templates:
  greeting: "안녕하세요! 고객지원팀 {{agent_name}}입니다. 무엇을 도와드릴까요?"
  fallback: "죄송합니다. 해당 질문은 제 전문 분야를 벗어납니다."

security:
  integrity_hash: "sha256:abc123..."
  allow_override: false
  tamper_detection: true
```

### 3. 구현: Soul Spec 검증 시스템

다음은 Soul Spec을 파싱하고 런타임에 페르소나 무결성을 검증하는 Python 구현이다.

```python
import yaml
import hashlib
import json
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class TraitMutability(Enum):
    IMMUTABLE = True
    MUTABLE = False

@dataclass
class Trait:
    name: str
    weight: float
    immutable: bool

@dataclass
class BehavioralConstraint:
    type: str
    allowed: List[str]
    forbidden: List[str]

class SoulSpec:
    """
    AI Agent Persona Specification with Integrity Protection
    """
    
    def __init__(self, spec_path: str):
        with open(spec_path, 'r', encoding='utf-8') as f:
            self._raw_spec = yaml.safe_load(f)
        
        self.version = self._raw_spec['soul_spec_version']
        self.identity = self._raw_spec['identity']
        self.traits = self._parse_traits()
        self.constraints = self._parse_constraints()
        self._integrity_hash = self._raw_spec['security']['integrity_hash']
        
    def _parse_traits(self) -> List[Trait]:
        """Parse core traits into structured objects"""
        traits = []
        for t in self._raw_spec['core_traits']:
            traits.append(Trait(
                name=t['trait'],
                weight=t['weight'],
                immutable=t.get('immutable', False)
            ))
        return traits
    
    def _parse_constraints(self) -> List[BehavioralConstraint]:
        """Parse behavioral constraints"""
        constraints = []
        for c in self._raw_spec['behavioral_constraints']:
            constraints.append(BehavioralConstraint(
                type=c['type'],
                allowed=c['allowed'],
                forbidden=c['forbidden']
            ))
        return constraints
    
    def compute_hash(self) -> str:
        """Compute integrity hash of current spec state"""
        spec_copy = self._raw_spec.copy()
        spec_copy['security']['integrity_hash'] = ""
        
        canonical = json.dumps(spec_copy, sort_keys=True, ensure_ascii=False)
        return f"sha256:{hashlib.
```

```python
sha256(canonical.encode()).hexdigest()[:16]}"
    
    def verify_integrity(self) -> bool:
        """Verify spec hasn't been tampered with"""
        current_hash = self.compute_hash()
        return current_hash == self._integrity_hash
    
    def validate_response(self, response: str, response_traits: dict) -> tuple[bool, str]:
        """
        Validate response against persona constraints
        
        Returns: (is_valid, reason)
        """
        # Check trait violations
        for trait in self.traits:
            if trait.immutable:
                detected = response_traits.get(trait.name, 0)
                if detected < trait.weight * 0.5:  # 50% threshold
                    return False, f"Immutable trait '{trait.name}' violated"
        
        # Check forbidden content
        response_lower = response.lower()
        for constraint in self.constraints:
            for forbidden in constraint.forbidden:
                if forbidden in response_lower:
                    return False, f"Forbidden {constraint.type}: '{forbidden}'"
        
        return True, "Valid"

# Usage Example
if __name__ == "__main__":
    spec = SoulSpec("soul-spec-v1.yaml")
    
    # Verify spec integrity at runtime
    if not spec.verify_integrity():
        raise SecurityError("Soul Spec tampering detected!")
    
    # Validate agent response
    test_response = "음, 그건 좀 복잡한데... 내 개인적인 생각에는..."
    detected_traits = {"professional": 0.3, "empathetic": 0.5}
    
    is_valid, reason = spec.validate_response(test_response, detected_traits)
    print(f"Valid: {is_valid}, Reason: {reason}")
    # Output: Valid: False, Reason: Immutable trait 'professional' violated
```

### 4. ABLiterated LLM 대응 전략

abliterated LLM은 모델의 거부(refusal) 메커니즘을 제거한 변형 모델이다. 이는 연구 목적으로 유용하지만, 에이전트 보안 관점에서는 심각한 위협이다.

```javascript
graph TD
    A[Standard LLM] --> B[Refusal Mechanism]
    B --> C[Harmful Request Blocked]
    
    D[ABLiterated LLM] --> E[No Refusal]
    E --> F[All Requests Processed]
    
    G[Soul Spec Layer] --> H[Post-Generation Validation]
    F --> H
    H --> I[Persona Check]
    I --> J[Block if Violation]
```

**Soul Spec의 방어 계층:**

| 계층 | 방식 | ABLiterated 모델에서 효과 |
| :--- | :--- | :--- |
| Input Filtering | 프롬프트 인젝션 패턴 탐지 | 부분적 |
| Output Validation | 응답 트레이트 분석 | 높음 |
| Immutable Traits | 핵심 정체성 잠금 | 매우 높음 |
| Integrity Hash | 스펙 변조 탐지 | 매우 높음 |

### 5. Step-by-Step: Soul Spec 도입 가이드

#### Step 1: 페르소나 분석 기존 에이전트의 시스템 프롬프트를 분석하여 핵심 특성을 추출한다.

```python
def extract_persona_traits(system_prompt: str) -> List[dict]:
    """Extract traits from existing system prompt using LLM"""
    extraction_prompt = f"""
    Analyze the following system prompt and extract core persona traits.
    For each trait, assign:
    - name: trait identifier
    - weight: importance (0.0-1.0)
    - immutable: should this never change? (true/false)
    
    System Prompt:
    {system_prompt}
    
    Output as JSON array.
    """
    # LLM 호출 및 파싱 로직
    pass
```

#### Step 2: Soul Spec 작성 추출된 특성을 YAML 포맷으로 구조화한다.

#### Step 3: 검증 레이어 통합 에이전트 파이프라인에 Soul Spec 검증을 추가한다.

```python
class AgentWithSoulSpec:
    def __init__(self, llm, spec_path: str):
        self.llm = llm
        self.soul_spec = SoulSpec(spec_path)
        self.trait_analyzer = TraitAnalyzer()  # 별도 모듈
    
    def generate(self, user_input: str) -> str:
        # 1. Integrity check
        if not self.soul_spec.verify_integrity():
            raise SecurityError("Persona compromised")
        
        # 2. Generate response
        response = self.llm.generate(
            system_prompt=self._build_system_prompt(),
            user_input=user_input
        )
        
        # 3. Validate response
        traits = self.trait_analyzer.analyze(response)
        is_valid, reason = self.soul_spec.validate_response(response, traits)
        
        if not is_valid:
            return self.soul_spec._raw_spec['response_templates']['fallback']
        
        return response
```

#### Step 4: 모니터링 및 로깅 페르소나 이탈을 실시간으로 모니터링한다.

### 6. 페르소나 공유 커뮤니티 플랫폼

Soul Spec은 단순한 명세를 넘어, **페르소나 마켓플레이스** 생태계를 목표로 한다.

| 플랫폼 기능 | 설명 | 상태 |
| :--- | :--- | :--- |
| Persona Registry | 검증된 페르소나 저장소 | 개발중 |
| Version Control | 페르소나 버전 관리 | 계획중 |
| Rating System | 커뮤니티 기반 품질 평가 | 계획중 |
| Fork & Modify | 페르소나 포크 및 커스터마이징 | 개발중 |

```javascript
graph LR
    A[Creator] --> B[Publish Persona]
    B --> C[Soul Spec Registry]
    C --> D[Validation]
    D --> E[Published]
    
    F[User] --> G[Browse Registry]
    G --> H[Download Spec]
    H --> I[Deploy Agent]
```

## 결론

### 핵심 요약

Soul Spec은 AI 에이전트의 정체성을 **코드처럼 다루는** 접근법이다. 시스템 프롬프트를 단순 텍스트가 아닌, 버전 관리되고 무결성이 검증되는 명세로 격상시킨다.

1. **구조화된 페르소나**: YAML 기반의 명확한 정체성 정의
2. **불변 특성(Immutable Traits)**: 핵심 정체성의 변경 방지
3. **무결성 검증**: 해시 기반 변조 탐지
4. **응답 검증**: 생성 후 페르소나 준수 여부 확인

### 전문가 인사이트

ABLiterated LLM의 등장은 양날의 검이다. 연구 커뮤니티에는 모델 거부 메커니즘 연구의 기회를 제공하지만, 프로덕션 환경에서는 새로운 보안 위협이 된다.

Soul Spec과 같은 **페르소나 표준화**는 단순한 기술적 해결책을 넘어, AI 에이전트의 **정체성 거버넌스** 문제를 다룬다. 미래에는 기업의 AI 에이전트가 "누구냐"는 질문에 Soul Spec ID로 증명해야 할 수도 있다.

더 깊은 고민이 필요한 영역:
- 페르소나 간 상호작용 시 정체성 충돌 해결
- 멀티모달 에이전트에서의 일관된 페르소나 유지
- 연합학습 환경에서의 분산 페르소나 관리

### 참고 자료
- [Soul Spec - 원본 프로젝트](https://news.hada.io/topic?id=28092)
- [ABLiterated LLM 연구](https://arxiv.org/abs/2407.xxxxx) - 거부 메커니즘 제거 관련
- [Prompt Injection Survey](https://arxiv.org/abs/2311.16119) - 프롬프트 인젝션 종합 분석
- [Constitutional AI](https://arxiv.org/abs/2212.08073) - Anthropic의 AI 원칙 접근법

---

**출처**: [https://news.hada.io/topic?id=28092](https://news.hada.io/topic?id=28092)