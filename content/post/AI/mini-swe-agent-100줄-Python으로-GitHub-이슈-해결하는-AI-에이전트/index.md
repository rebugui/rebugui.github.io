---
title: "mini-swe-agent: 100줄 Python으로 GitHub 이슈 해결하는 AI 에이전트"
date: 2026-04-29T01:06:58+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
---

## 서론

최근 소프트웨어 엔지니어링 분야에서 자동화된 AI 에이전트에 대한 관심이 폭발적으로 증가하고 있습니다. 그러나 MetaGPT, AutoGen, LangGraph와 같은 고급 프레임워크를 활용해 에이전트를 구축하다 보면, 필수적인 비즈니스 로직을 구현하기도 전에 프레임워크 자체의 설정과 추상화 계층으로 인해 복잡도가 기하급수적으로 늘어나는 경험을 하게 됩니다. 수천 줄의 보일러플레이트 코드와 복잡한 의존성 속에서 에이전트의 행동 원리를 파악하고 디버깅하는 것은 연구자나 실무자 모두에게 큰 부담입니다.

Princeton과 Stanford 연구진이 개발한 `mini-swe-agent`는 이러한 "복잡성의 역설"을 해결하기 위해 탄생했습니다. 이 도구는 SWE-bench 벤치마크와 SWE-agent 프로젝트의 핵심 통찰을 바탕으로, **불과 100줄 남짓한 Python 코드**로 GitHub 이슈를 해결하는 완전한 기능의 에이전트를 구현했습니다. 별도의 거대 모델 훈련이나 복잡한 모노레포 구조 없이도, LLM의 추론 능력과 터미널 환경만 연결하면 실제 소프트웨어 엔지니어링 작업이 가능하다는 것을 증명한 것입니다. 이 글에서는 `mini-swe-agent`가 어떻게 극단적인 단순함 속에서도 강력한 문제 해결 능력을 발휘하는지 그 기술적 원리와 구현 방법을 심층적으로 분석합니다.

## 본론

### 1. 에이전트의 핵심 아키텍처: ReAct 패턴의 단순화

`mini-swe-agent`의 핵심은 LLM 연구에서 잘 알려진 **ReAct (Reasoning + Acting)** 패턴을 가장 순수한 형태로 구현했다는 점입니다. 복잡한 메모리 관리나 멀티 에이전트 협상 없이, 에이전트는 단순히 "현재 상태를 관찰(Observation) -> 생각(Thought) -> 행동(Action)"의 루프를 반복할 뿐입니다. 일반적인 에이전트 프레임워크가 이 루프를 추상화 클래스, 이벤트 버스, 상태 머신 등으로 감싸는 반면, `mini-swe-agent`는 이 루프를 파이썬의 `while` 루프 하나로 표현합니다.

이 아키텍처의 핵심은 LLM에게 시스템 프롬프트를 통해 "너는 터미널과 코드를 통해 문제를 해결하는 엔지니어다"라는 역할을 부여하고, 이전 명령어의 실행 결과(관찰)를 컨텍스트로 다시 제공하여 다음 행동을 유도하는 것입니다. 이 과정에서 에이전트는 코드를 읽고, 검색하고, 수정하며, 테스트를 실행하여 GitHub 이슈를 해결합니다.

다음은 `mini-swe-agent`의 단순화된 실행 흐름을 보여주는 다이어그램입니다.

```javascript
graph LR
    A[GitHub Issue] --> B[LLM Context Setup]
    B --> C[LLM Reasoning]
    C --> D[Command Generation]
    D --> E[Terminal Execution]
    E --> F[Output Observation]
    F --> C
    C -->|Solution Found| G[Submit PR]
```

### 2. 기술적 구현 상세 및 코드 분석

`mini-swe-agent`는 OpenAI의 GPT-4o나 Anthropic의 Claude 3.5 Sonnet 같은 강력한 LLM을 "두뇌"로 사용하고, Python의 `subprocess` 모듈을 "손발"로 사용합니다. 전체 코드는 단일 파일로 작성되며, 핵심은 프롬프트 엔지니어링과 컨텍스트 윈도우 관리에 있습니다.

다음은 `mini-swe-agent`의 핵심 로직을 단순화하여 재구성한 Python 코드 예시입니다. 실제 구현체는 예외 처리와 로깅이 포함되어 있지만, 아래 코드는 에이전트가 작동하는 가장 기본적인 메커니즘을 보여줍니다.

```python
import subprocess
from openai import OpenAI

client = OpenAI()

def run_command(command):
    """터미널 명령어를 실행하고 결과를 반환하는 함수"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=20
        )
        return result.stdout + result.stderr
    except Exception as e:
        return str(e)

def solve_issue(issue_description, model="gpt-4o"):
    """GitHub 이슈를 해결하는 메인 루프"""
    messages = [
        {
            "role": "system", 
            "content": "You are an expert software engineer. Use commands to solve the issue."
        },
        {
            "role": "user", 
            "content": f"Issue: {issue_description}
Start by listing files."
        }
    ]

    history = [] # 실행된 명령과 결과 저장

    while True:
        # 1. LLM에게 현재 상태(이슈 + 이력) 전달하고 행동 요청
        response = client.chat.completions.create(
            model=model,
            messages=messages
        )
        
        thought_and_action = response.choices[0].message.content
        
        # 2. LLM의 응답에서 실행할 명령어 파싱 (예: ```bash ... ```)
        # 실제 구현에서는 더 정교한 파싱 로직이 필요함
        if "```bash" in thought_and_action:
            command_block = thought_and_action.split("```bash")[1].split("```")[0]
            command = command_block.strip()
        else:
            # 명령어 없는 사고이거나 종료 의사 표현
            print(thought_and_action)
            break

        print(f"Executing: {command}")
        
        # 3. 명령어 실행 및 관찰(Observeration)
        observation = run_command(command)
        
        # 4. 실행 결과를 기록하여 LLM에게 다시 피드백
        step_log = f"
User: run {command}
Assistant: {observation}"
        messages.append({"role": "assistant", "content": thought_and_action})
        messages.append({"role": "user", "content": f"Observation: {observation}"})
        
        # 비용 절감 및 컨텍스트 관리를 위해 히스토리 관리 로직 추가 가능
        history.append({"cmd": command, "output": observation})

```

```python
# 실행 예시
solve_issue("Fix the typo in the README.md file")
```

이 코드의 핵심은 `messages` 리스트가 LLM의 단기 기억(Short-term Memory) 역할을 한다는 점입니다. 에이전트가 명령어를 실행할 때마다 그 결과가 메시지 히스토리에 추가되므로, LLM은 자신이 이전에 무엇을 했고 무엇이 실패했는지를 인지하여 피드백 루프를 형성합니다.

### 3. 기존 프레임워크와의 비교 분석

`mini-swe-agent`의 가장 큰 장점은 기존의 무거운 솔루션 대비 비교할 수 없을 정도로 가볍고 투명하다는 것입니다. 다음 표는 일반적인 복잡한 에이전트 프레임워크와 `mini-swe-agent`를 비교한 것입니다.

| 비교 항목 | 일반적인 Agent Framework (LangChain, AutoGen 등) | mini-swe-agent |
| :--- | :--- | :--- |
| **코드 복잡도** | 높음 (수천 줄의 추상화 계층) | 낮음 (약 100줄, 핵심 로직 노출) |
| **의존성** | 다수 (내부 라이브러리, DB, 서버 등) | 최소화 (OpenAI API, standard lib만) |
| **디버깅 난이도** | 어려움 (프레임워크 내부 블랙박스) | 쉬움 (모든 상태 변화 추적 가능) |
| **학습 곡선** | 가파름 (특정 DSL이나 패러다임 학습 필요) | 완만 (기본 Python 스크립트 이해) |
| **확장성** | 높음 (플러그인, 도구 통합 용이) | 제한적 (직접 코드 수정 필요) |
| **주요 용도** | 상용 서비스, 대규모 시스템 | 프로토타이핑, 연구, 교육 |

### 4. 실무 적용 및 실행 가이드

연구자나 엔지니어가 `mini-swe-agent`를 활용하여 자신만의 코딩 에이전트를 실험해보고 싶다면 다음과 같은 단계를 따를 수 있습니다.

1.  **환경 준비**: Docker 컨테이너나 격리된 가상 환경을 준비합니다. 에이전트가 시스템을 변경할 수 있으므로 호스트 머신의 안전을 위해 필수적입니다.
2.  **레포지토리 클론**: 문제를 해결하고자 하는 GitHub 레포지토리를 로컬에 다운로드합니다.
3.  **프롬프트 설정**: 에이전트가 사용할 시스템 프롬프트를 정의합니다. 여기에는 "코드를 변경하기 전에 반드시 테스트를 실행하라"거나 "전체 파일이 아닌 관련 부분만 먼저 읽어라"와 같은 제약 조건이 포함됩니다.
4.  **실행 및 모니터링**: 스크립트를 실행하고 에이전트가 터미널에 입력하는 명령어를 실시간으로 모니터링합니다. 안전장치로 인해 위험한 명령어(`rm -rf /` 등)가 실행되지 않도록 필터링 로직

---

**출처**: [https://news.hada.io/topic?id=28891](https://news.hada.io/topic?id=28891)