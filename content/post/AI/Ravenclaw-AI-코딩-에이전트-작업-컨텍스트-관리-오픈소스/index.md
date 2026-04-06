---
title: "Ravenclaw: AI 코딩 에이전트 작업 컨텍스트 관리 오픈소스"
date: 2026-04-07T01:04:57+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
---

## 서론

"방금 Claude Code로 작성하던 인증 모듈, Gemini CLI에서 이어서 작업하고 싶은데..."

이런 경험, 있으신가요? Claude Code로 열심히 작업하다가 토큰 제한에 막히거나, 특정 작업에 더 적합한 다른 AI 에이전트를 쓰고 싶어서 Gemini CLI나 Codex로 전환하는 순간, 가장 먼저 마주하는 것은 **"에이전트가 이전 작업 내용을 전혀 모른다"**는 사실입니다.

```plain text
You: "아까 작업하던 그 인증 모듈 계속해줘"
Gemini CLI: "죄송합니다, 어떤 인증 모듈을 말씀하시는지..."
You: 😤 (처음부터 다시 설명 시작)
```

이것은 단순한 불편함이 아닙니다. **컨텍스트 스위칭 비용(Context Switching Cost)**이라는 실제 생산성 저하 요인이죠. LLM 기반 코딩 에이전트가 폭발적으로 늘어난 지금, 우리는 **멀티 에이전트 개발 환경**에 살고 있습니다. 각 에이전트는 강점이 다르고, 프로젝트마다 최적의 도구가 다릅니다. 하지만 이들을 오가며 작업할 때마다 매번 컨텍스트를 새로 주입해야 한다면, AI가 주는 생산성 향상은 순식간에 증발합니다.

Ravenclaw는 바로 이 문제를 해결하는 오픈소스 시스템입니다. **프로젝트 단위로 작업 맥락을 중앙 관리**하고, 서로 다른 AI 코딩 에이전트 간에 이 맥락을 자동으로 공유함으로써, 진정한 의미의 연속적인 개발 워크플로우를 가능하게 합니다.

## 문제의 본질: AI 코딩 에이전트의 컨텍스트 파편화

### 왜 이 문제가 중요한가?

2024년 이후 AI 코딩 에이전트 시장은 폭발적으로 성장했습니다. Anthropic의 Claude Code, Google의 Gemini CLI, OpenAI의 Codex, 그리고 Cursor, Copilot 등 수많은 도구가 경쟁하고 있습니다.

| 에이전트 | 강점 | 컨텍스트 관리 | | :--- | :--- | :--- | | Claude Code | 긴 컨텍스트, 복잡한 추론 | 자체 세션 내에서만 유지 | | Gemini CLI | 멀티모달, Google 생태계 통합 | 독립적인 세션 관리 | | Codex | OpenAI 모델 호환성 | 격리된 컨텍스트 | | Cursor | IDE 통합, 로컬 파일 접근 | 프로젝트 내 제한적 공유 |

각 에이전트는 **자신만의 세션과 컨텍스트**를 가집니다. 이는 보안과 격리 측면에서는 장점이지만, **개발자가 여러 에이전트를 병행 사용할 때는 치명적인 단점**이 됩니다.

```javascript
graph TD
    subgraph 기존 방식
        A[개발자] --> B[Claude Code]
        A --> C[Gemini CLI]
        A --> D[Codex]
        B --> B1[격리된 컨텍스트 A]
        C --> C1[격리된 컨텍스트 B]
        D --> D1[격리된 컨텍스트 C]
    end
```

이러한 파편화는 다음과 같은 문제를 야기합니다:

1. **반복적인 컨텍스트 주입**: 에이전트 전환 시마다 프로젝트 배경, 코딩 컨벤션, 이전 작업 내용을 재설명 2. **일관성 저하**: 서로 다른 에이전트가 생성한 코드 간 스타일 불일치 3. **작업 흐름 단절**: 큰 기능을 여러 에이전트에 분산 작업하기 어려움 4. **토큰 낭비**: 동일한 컨텍스트를 여러 세션에 반복해서 전송

## Ravenclaw 아키텍처

Ravenclaw는 **중앙 집중식 컨텍스트 저장소**를 통해 이 문제를 해결합니다.

```javascript
graph LR
    subgraph Ravenclaw 시스템
        A[Claude Code] --> E[중앙 컨텍스트 저장소]
        B[Gemini CLI] --> E
        C[Codex] --> E
        D[기타 에이전트] --> E
        E --> F[프로젝트 메타데이터]
        E --> G[작업 히스토리]
        E --> H[코딩 컨벤션]
    end
```

### 핵심 구성 요소

1. **Context Store**: 프로젝트별 구조화된 컨텍스트 저장 2. **Agent Adapter**: 각 AI 에이전트에 맞는 포맷 변환 3. **Sync Engine**: 실시간 컨텍스트 동기화 4. **CLI Interface**: 명령줄 기반 관리 도구

## 작동 원리: 어떻게 컨텍스트가 유지되는가?

Ravenclaw의 핵심은 **프로젝트 상태를 에이전트 독립적인 형식으로 추상화**하는 것입니다.

### 1단계: 프로젝트 초기화

```bash
# Ravenclaw 설치
pip install ravenclaw-context

# 프로젝트 초기화
ravenclaw init my-project

# 현재 프로젝트 컨텍스트 분석
ravenclaw analyze --source ./src --docs ./docs
```

### 2단계: 컨텍스트 구조 생성

Ravenclaw는 프로젝트를 분석하여 다음과 같은 구조화된 컨텍스트를 생성합니다:

```python
# ravenclaw/context_schema.py

from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class ProjectContext(BaseModel):
    """Ravenclaw 프로젝트 컨텍스트 스키마"""
    
    project_name: str
    description: str
    
    # 기술 스택 정보
    tech_stack: Dict[str, List[str]]  # {"languages": ["Python"], "frameworks": ["FastAPI"]}
    
    # 코드 구조
    architecture: str  # "microservice", "monolith", "serverless"
    key_directories: Dict[str, str]  # {"src/": "메인 소스 코드", "tests/": "테스트"}
    
    # 코딩 컨벤션
    conventions: Dict[str, str]  # {"naming": "snake_case", "docstring": "Google Style"}
    
    # 작업 히스토리
    recent_tasks: List[Dict[str, str]]
    
    # 현재 포커스
    current_focus: Optional[str] = None
    
    # 메타데이터
    last_updated: datetime
    active_agent: Optional[str] = None

# 사용 예시
context = ProjectContext(
    project_name="auth-service",
    description="JWT 기반 인증 마이크로서비스",
    tech_stack={
        "languages": ["Python", "TypeScript"],
        "frameworks": ["FastAPI", "SQLAlchemy"],
        "databases": ["PostgreSQL", "Redis"]
    },
    architecture="microservice",
    key_directories={
        "src/api/": "REST API 엔드포인트",
        "src/auth/": "인증 로직",
        "src/models/": "데이터베이스 모델"
    },
    conventions={
        "naming": "snake_case for Python, camelCase for TypeScript",
        "testing": "pytest with 80% coverage minimum",
        "commits": "Conventional Commits"
    },
    recent_tasks=[
        {
            "task": "JWT 리프레시 토큰 로직 구현",
            "agent": "claude-code",
            "status": "in_progress",
            "files_modified": ["src/auth/jwt_handler.py", "src/api/routes/auth.py"]
        }
    ],
    current_focus="JWT 리프레시 토큰 만료 처리 로직 완성",
    last_updated=datetime.now(),
    active_agent="claude-code"
)
```

### 3단계: 에이전트 전환 시나리오

```python
# ravenclaw/agent_manager.py

class AgentManager:
    """다양한 AI 에이전트 간 컨텍스트 전환 관리"""
    
    AGENT_PROMPTS = {
        "claude-code": """
        당신은 이 프로젝트의 이전 작업을 이어받습니다.
        마지막 작업 상태: {current_focus}
        최근 수정 파일: {recent_files}
        이어서 작업을 진행하세요.
        """,
        
        "gemini-cli": """
        Continuing work on this project.
        Last task: {current_focus}
        Recent changes: {recent_files}
        Please continue the implementation.
        """,
        
        "codex": """
        // Project Context
        // Current focus: {current_focus}
        // Recent modifications: {recent_files}
        // Continue implementation
        """
    }
    
    def __init__(self, context_store_path: str):
        self.store_path = context_store_path
        self.current_context = self._load_context()
    
    def switch_agent(
        self, 
        from_agent: str, 
        to_agent: str,
        task_update: str = None
    ) -> str:
        """
        에이전트 전환 시 컨텍스트 포맷팅
        
        Args:
            from_agent: 현재 사용 중인 에이전트
            to_agent: 전환하려는 에이전트
            task_update: 전환 전 마지막 작업 상태 업데이트
        
        Returns:
            새 에이전트용 포맷팅된 컨텍스트 프롬프트
        """
        # 현재 상태 저장
        if task_update:
            self.current_context.current_focus = task_update
        
        self.current_context.active_agent = to_agent
        self._save_context()
        
        # 새 에이전트용 프롬프트 생성
        prompt_template = self.AGENT_PROMPTS.get(to_agent)
        
        formatted_prompt = prompt_template.format(
            current_focus=self.current_context.current_focus,
            recent_files=self._get_recent_files_summary(),
            project_structure=self._get_structure_summary(),
            conventions=self._get_conventions_summary()
        )
        
        return formatted_prompt
    
    def _get_recent_files_summary(self) -> str:
        """최근 수정된 파일 요약 생성"""
        recent = self.current_context.
```

```python
recent_tasks[-3:]  # 최근 3개
        summary = []
        for task in recent:
            summary.append(f"- {task['task']} ({task['files_modified']})")
        return "
".join(summary)
    
    def _save_context(self):
        """컨텍스트를 영속화"""
        import json
        with open(f"{self.store_path}/context.json", "w") as f:
            json.dump(self.current_context.model_dump(), f, default=str, indent=2)
```

### 4단계: 실제 사용 워크플로우

```bash
# Claude Code로 작업 시작
ravenclaw use claude-code

# ... Claude Code에서 작업 ...

# 작업 상태 저장
ravenclaw checkpoint "JWT 리프레시 로직 80% 완료"

# Gemini CLI로 전환
ravenclaw switch gemini-cli

# 자동으로 컨텍스트가 포맷팅되어 클립보드에 복사됨
# Gemini CLI 세션에 붙여넣기 하면 이전 작업 맥락이 즉시 복원됨
```

## 컨텍스트 동기화 메커니즘

Ravenclaw의 가장 흥미로운 점은 **단방향이 아닌 양방향 동기화**를 지원한다는 것입니다.

```javascript
graph TD
    A[Git Repository] --> B[Ravenclaw Context]
    B --> C[Agent Session]
    C --> D[Code Changes]
    D --> E[Context Update]
    E --> B
    B --> F[Other Agents]
```

### 자동 컨텍스트 업데이트

```python
# ravenclaw/sync.py

import os
import hashlib
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ContextSyncHandler(FileSystemEventHandler):
    """파일 시스템 변경 감지 및 컨텍스트 자동 업데이트"""
    
    def __init__(self, context_manager):
        self.context = context_manager
        self.file_hashes = {}
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        file_path = event.src_path
        
        # 파일 해시 계산하여 실제 변경 확인
        current_hash = self._calculate_hash(file_path)
        if self.file_hashes.get(file_path) == current_hash:
            return
        
        self.file_hashes[file_path] = current_hash
        
        # 컨텍스트 업데이트
        self._update_context_for_file(file_path)
    
    def _calculate_hash(self, file_path: str) -> str:
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def _update_context_for_file(self, file_path: str):
        """파일 변경사항을 컨텍스트에 반영"""
        # 파일에서 중요 정보 추출 (imports, class 정의 등)
        extracted_info = self._extract_semantic_info(file_path)
        
        # 컨텍스트의 recent_tasks 업데이트
        self.context.add_recent_modification(
            file=file_path,
            changes=extracted_info,
            timestamp=datetime.now()
        )

# 파일 시스템 감시 시작
def start_sync_watch(project_path: str, context_manager):
    event_handler = ContextSyncHandler(context_manager)
    observer = Observer()
    observer.schedule(event_handler, project_path, recursive=True)
    observer.start()
    return observer
```

## 실무 적용 가이드

### 프로젝트 설정 파일 예시

---

**출처**: [https://news.hada.io/topic?id=28225](https://news.hada.io/topic?id=28225)