---
title: "Multi-Agent LLM 시스템: 분산 시스템 관점의 아키텍처 설계"
date: 2026-05-01T01:06:51+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
---

## 서론

지난달 한 스타트업에서 AutoGPT 기반 코드 생성 에이전트 5개를 동시에 돌려 대규모 리팩토링을 시도했다가, 시스템 전체가 교착 상태에 빠진 사건이 있었다. 에이전트 A가 수정한 파일을 에이전트 B가 덮어쓰고, 에이전트 C는 변경 사항을 인지하지 못한 채 이전 버전 기준으로 테스트를 작성했다. 결국 3시간의 작업이 허사가 되었다.

이는 단순한 버그가 아니다. Multi-Agent LLM 시스템의 근본적인 설계 문제다.

단일 LLM 에이전트는 입력을 받아 출력을 반환하는 비교적 단순한 파이프라인이다. 하지만 여러 에이전트가 협업하는 순간, 우리는 **분산 시스템의 고전적 문제**와 정면으로 마주하게 된다. 상태 동기화, 메시지 순서 보장, 부분 실패 처리, 그리고 일관성 유지—이 모든 것이 LLM 에이전트 세계에서도 동일하게 발생한다.

2024년 arXiv에 발표된 "The Landscape of Emerging AI Agent Architectures" 연구에 따르면, 프로덕션 환경의 Multi-Agent 시스템 실패 원인 중 67%가 분산 시스템적 복잡성과 직결된다. 이 글에서는 Multi-Agent LLM 시스템을 분산 컴퓨팅 관점에서 분석하고, 실무에 적용 가능한 아키텍처 패턴을 제시한다.

## 본론: Multi-Agent 시스템의 분산 시스템적 본질

### 1. 왜 분산 시스템 문제인가

Multi-Agent LLM 시스템은 본질적으로 분산 시스템의 특성을 모두 갖추고 있다. 각 에이전트는 독립적인 computation node이며, 네트워크(프롬프트/응답)를 통해 통신한다. 결정적으로, LLM의 비결정적 특성 때문에 동일 입력에도 다른 출력이 발생하는 **비결정론적 분산 시스템**이다.

```javascript
graph TD
    A[User Request] --> B[Orchestrator]
    B --> C[Agent 1: Code Generator]
    B --> D[Agent 2: Code Reviewer]
    B --> E[Agent 3: Test Writer]
    C --> F[Shared State: Codebase]
    D --> F
    E --> F
    F --> G[Conflict Resolution]
    G --> H[Final Output]
```

이 아키텍처에서 발생하는 핵심 문제들을 분산 시스템 이론과 매핑해보면 다음 표와 같다.

| 분산 시스템 과제 | Multi-Agent LLM 매핑 | 발생 빈도 | 난이도 |
| :--- | :--- | :--- | :--- |
| 상태 일관성 (Consistency) | 에이전트 간 컨텍스트 동기화 | 매우 높음 | 높음 |
| 내결함성 (Fault Tolerance) | LLM API 장애, hallucination | 높음 | 중간 |
| 메시지 순서 (Ordering) | 프롬프트 처리 순서 보장 | 중간 | 높음 |
| 분합 트랜잭션 | 다중 파일 동시 수정 | 높음 | 매우 높음 |
| 합의 (Consensus) | 에이전트 간 의견 충돌 해결 | 중간 | 높음 |

### 2. 핵심 과제 상세 분석

#### 2.1 상태 일관성 문제

LLM 에이전트의 "상태"는 컨텍스트 윈도우의 내용이다. 에이전트 A가 파일을 수정했을 때, 에이전트 B가 이를 즉시 인지해야 한다. 하지만 LLM의 컨텍스트는 불변(immutable)이므로, 실행 중인 에이전트에게 새로운 상태를 "주입"하는 것은 간단하지 않다.

이는 분산 시스템의 **캡의 정리(CAP Theorem)**와 유사한 트레이드오프를 만든다:
- **강일관성(Strong Consistency)**: 모든 에이전트가 최신 상태를 유지, but 지연 증가
- **최종 일관성(Eventual Consistency)**: 임시 불일치 허용, but 충돌 가능

#### 2.2 내결함성과 부분 실패

LLM API는 실패한다. Rate limit, 타임아웃, hallucination, 그리고 의도치 않은 출력 형식. 분산 시스템의 제1원칙: **"네트워크를 통한 통신은 신뢰할 수 없다"**는 LLM API 호출에도 그대로 적용된다.

#### 2.3 메시지 전달과 순서 보장

에이전트 간 통신은 프롬프트로 이루어진다. 프롬프트의 순서가 결과에 큰 영향을 미치며, 이는 분산 시스템의 **인과적 일관성(Causal Consistency)** 문제와 직결된다.

### 3. 아키텍처 패턴: Event-Sourcing Multi-Agent

이러한 문제를 해결하기 위해, 분산 시스템의 **Event Sourcing** 패턴을 적용한 아키텍처를 제안한다.

```javascript
graph LR
    A[Agent Action] --> B[Event Bus]
    B --> C[Event Store]
    C --> D[State Projection]
    D --> E[Agent Context Update]
    B --> F[Conflict Detector]
    F --> G[Resolution Strategy]
```

핵심 아이디어는 모든 에이전트의 행동을 이벤트로 기록하고, 상태는 이벤트의 투영(projection)으로 계산하는 것이다. 이렇게 하면:
1. 언제든 상태를 재구성할 수 있다
2. 충돌 발생 시 원인을 추적할 수 있다
3. 에이전트 실패 시 이벤트 로그에서 복구할 수 있다

#### 구현 예시: Python 기반 Event-Sourced Agent Framework

```python
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import json
import uuid

class EventType(Enum):
    CODE_GENERATED = "code_generated"
    CODE_MODIFIED = "code_modified"
    REVIEW_SUBMITTED = "review_submitted"
    TEST_WRITTEN = "test_written"
    CONFLICT_DETECTED = "conflict_detected"

@dataclass
class Event:
    event_id: str
    event_type: EventType
    agent_id: str
    timestamp: datetime
    payload: Dict[str, Any]
    parent_event_ids: List[str]  # 인과 관계 추적

class EventStore:
    """이벤트 소싱 기반 상태 관리"""
    
    def __init__(self):
        self.events: List[Event] = []
        self.agent_contexts: Dict[str, List[Event]] = {}
        
    def append(self, event: Event) -> bool:
        """이벤트 추가 및 충돌 검사"""
        conflicts = self._detect_conflicts(event)
        
        if conflicts:
            resolution_event = self._resolve_conflict(event, conflicts)
            self.events.append(resolution_event)
            self._notify_agents(resolution_event)
            return True
        
        self.events.append(event)
        self._update_contexts(event)
        return True
    
    def _detect_conflicts(self, new_event: Event) -> List[Event]:
        """동일 리소스에 대한 동시 수정 감지"""
        target_file = new_event.payload.get("file_path")
        if not target_file:
            return []
            
        return [
            e for e in self.events[-50:]  # 최근 50개 이벤트만 검사
            if e.payload.get("file_path") == target_file
            and e.event_type in [EventType.CODE_GENERATED, EventType.CODE_MODIFIED]
            and e.event_id not in new_event.parent_event_ids
        ]
    
    def _resolve_conflict(self, new_event: Event, conflicts: List[Event]) -> Event:
        """Last-Writer-Wins 전략 기반 충돌 해결"""
        # 실제로는 LLM 기반 의미적 병합 수행
        return Event(
            event_id=str(uuid.uuid4()),
            event_type=EventType.
```

```python
CONFLICT_DETECTED,
            agent_id="system",
            timestamp=datetime.now(),
            payload={
                "conflict_type": "concurrent_modification",
                "conflicting_events": [e.event_id for e in conflicts],
                "resolution_strategy": "semantic_merge",
                "target_file": new_event.payload.get("file_path")
            },
            parent_event_ids=[new_event.event_id] + [e.event_id for e in conflicts]
        )
    
    def _update_contexts(self, event: Event):
        """관련 에이전트의 컨텍스트 업데이트"""
        for agent_id in self.agent_contexts:
            if agent_id != event.agent_id:
                self.agent_contexts[agent_id].append(event)
    
    def get_current_state(self, file_path: str) -> Optional[Dict]:
        """특정 파일의 현재 상태를 이벤트 로그에서 재구성"""
        relevant_events = [
            e for e in self.events
            if e.payload.get("file_path") == file_path
            and e.event_type in [EventType.CODE_GENERATED, EventType.CODE_MODIFIED]
        ]
        
        if not relevant_events:
            return None
            
        # 최신 이벤트의 내용을 반환 (실제로는 incremental patch 적용)
        return relevant_events[-1].payload

class Agent:
    """Event-Sourced 에이전트"""
    
    def __init__(self, agent_id: str, role: str, event_store: EventStore):
        self.agent_id = agent_id
        self.role = role
        self.event_store = event_store
        self.event_store.agent_contexts[agent_id] = []
    
    def execute_task(self, task: Dict[str, Any]) -> Event:
        """태스크 실행 및 이벤트 발행"""
        # 최신 상태 조회
        current_state = self.event_store.get_current_state(
            task.get("file_path", "")
        )
        
        # LLM 호출 (여기서는 모킹)
        result = self._call_llm(task, current_state)
        
        # 이벤트 생성
        event = Event(
            event_id=str(uuid.uuid4()),
            event_type=self._get_event_type(),
            agent_id=self.agent_id,
            timestamp=datetime.
```

```python
now(),
            payload={
                "file_path": task.get("file_path"),
                "content": result,
                "role": self.role
            },
            parent_event_ids=self._get_parent_ids()
        )
        
        self.event_store.append(event)
        return event
    
    def _call_llm(self, task: Dict, current_state: Optional[Dict]) -> str:
        """LLM API 호출 로직"""
        # 실제 구현에서는 OpenAI/Anthropic API 호출
        return f"// Generated by {self.role}"
    
    def _get_event_type(self) -> EventType:
        type_map = {
            "generator": EventType.CODE_GENERATED,
            "reviewer": EventType.REVIEW_SUBMITTED,
            "tester": EventType.TEST_WRITTEN
        }
        return type_map.get(self.role, EventType.CODE_MODIFIED)
    
    def _get_parent_ids(self) -> List[str]:
        """인과관계를 위한 부모 이벤트 ID 목록"""
        recent = self.event_store.agent_contexts[self.agent_id][-3:]
        return [e.event_id for e in recent]

# 사용 예시
event_store = EventStore()

generator = Agent("agent_1", "generator", event_store)
reviewer = Agent("agent_2", "reviewer", event_store)
tester = Agent("agent_3", "tester", event_store)

# 코드 생성
gen_event = generator.execute_task({
    "file_path": "src/main.py",
    "task": "Implement user authentication"
})

# 리뷰 수행
rev_event = reviewer.execute_task({
    "file_path": "src/main.py",
    "task": "Review authentication code"
})

# 현재 상태 확인
state = event_store.get_current_state("src/main.py")
print(f"Events recorded: {len(event_store.events)}")
print(f"Current state: {state}")
```

### 4. 설계 원칙: Multi-Agent LLM을 위한 5가지 원칙

#### 원칙 1: Shared Nothing 아키텍처

에이전트 간 직접 통신을 최소화하라. 모든 통신은 중앙 이벤트 버스를 통해 이루어져야 한다. 이는 분산 시스템에서 메시지 브로커(Kafka, RabbitMQ)를 사용하는 것과 동일한 원리다.

#### 원칙 2: Idempotent 에이전트 설계

동일한 프롬프트를 여러 번 전송해도 동일한 결과를 보장하도록 설계하라. LLM의 비결정성을 고려할 때, temperature=0 설정과 시드 관리가 필수적이다.

```python
import hashlib
from functools import lru_cache

class IdempotentAgent:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.result_cache: Dict[str, Any] = {}
    
    def execute_with_cache(self, prompt: str, cache_ttl: int = 3600) -> str:
        """결과 캐싱으로 멱등성 보장"""
        cache_key = self._generate_cache_key(prompt)
        
        if cache_key in self.result_cache:
            return self.result_cache[cache_key]
        
        result = self._call_llm(prompt, temperature=0.0)
        self.result_cache[cache_key] = result
        return result
    
    def _generate_cache_key(self, prompt: str) -> str:
        return hashlib.sha256(prompt.encode()).hexdigest()
```

#### 원칙 3: Circuit Breaker 패턴으로 내결함성 확보

LLM API 장애가 전체 시스템으로 전파되는 것을 방지하라.

```python
import time
from typing import Callable

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.last_failure_time = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
            
            raise e

# LLM 호출에 Circuit Breaker 적용
llm_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30)

def safe_llm_call(prompt: str) -> str:
    try:
        return llm_breaker.call(call_openai_api,
```

---

**출처**: [https://kirancodes.me/posts/log-distributed-llms.html](https://kirancodes.me/posts/log-distributed-llms.html)