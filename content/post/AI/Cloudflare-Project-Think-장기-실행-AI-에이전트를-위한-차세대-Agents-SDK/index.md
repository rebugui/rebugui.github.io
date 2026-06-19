---
title: "Cloudflare Project Think: 장기 실행 AI 에이전트를 위한 차세대 Agents SDK"
date: 2026-04-30T01:07:54+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
draft: true
---

## 서론

"에이전트가 3시간째 코드를 생성 중인데, 노트북을 덮으면 어떻게 되나요?"

최근 한 스타트업 CTO가 필자에게 던진 질문이다. Cursor, Devin, SWE-agent 같은 코딩 에이전트들이 쏟아지면서, 우리는 LLM의 코딩 능력에 열광하고 있다. 하지만 막상 프로덕션 환경에서 장시간 실행되는 에이전트를 배포하려고 하면 마주치는 문제가 있다. 바로 **실행 지속성(persistence)**과 **상태 관리(state management)**다.

기존 코딩 에이전트 대부분은 로컬 머신에서 실행된다. 사용자가 웹 브라우저를 닫거나, 노트북이 절전 모드에 들어가거나, 네트워크가 끊기면 에이전트의 작업이 중단된다. 더 심각한 문제는 비용이다. 에이전트가 사용자 입력을 기다리는 유휴 시간(idle time)에도 GPU 컴퓨팅 비용은 계속 청구된다.

Cloudflare가 발표한 **Project Think**는 바로 이 지점을 공략한다. 장기 실행 에이전트를 클라우드 네이티브 환경에서 안정적으로 구동하기 위한 프리미티브를 제공하는 차세대 Agents SDK다.

## 본론

### 기존 에이전트 아키텍처의 근본적 한계

현재 대부분의 AI 에이전트 프레임워크—LangChain, AutoGen, CrewAI—는 기본적으로 **단기 실행(short-lived)**을 전제로 설계되었다. 요청-응답 사이클 내에서 에이전트가 완료되거나, 상태를 외부 저장소에 직렬화하여 수동으로 관리해야 한다.

문제는 복잡한 작업일수록 이 사이클이 깨지기 쉽다는 점이다.

```javascript
graph TD
    A[사용자 요청] --> B[에이전트 시작]
    B --> C[코드 분석]
    C --> D[서브 에이전트 생성]
    D --> E[테스트 실행]
    E --> F{결과 확인}
    F -->|실패| G[디버깅]
    G --> E
    F -->|성공| H[결과 반환]
    E -->|타임아웃| I[상태 손실]
    D -->|OOM| I
    G -->|네트워크 끊김| I
```

위 다이어그램에서 볼 수 있듯, 장기 실행 에이전트는 수많은 실패 지점(failure point)을 가진다. 기존 프레임워크에서는 이러한 실패 시 처음부터 다시 시작하거나, 복잡한 체크포인트 로직을 직접 구현해야 한다.

### Project Think의 핵심 프리미티브

Project Think는 장기 실행 에이전트를 위한 네 가지 핵심 프리미티브를 제공한다.

| 프리미티브 | 설명 | 해결하는 문제 |
| :--- | :--- | :--- |
| **Durable Execution** | 에이전트 실행 상태를 자동으로 영속화 | 프로세스 크래시, 배포 시 상태 손실 |
| **Sub-agent Orchestration** | 에이전트 내부에서 하위 에이전트 생성/관리 | 복잡한 작업의 계층적 분해 |
| **Sandboxed Code Execution** | 격리된 환경에서 안전한 코드 실행 | 보안 위험, 리소스 충돌 |
| **Persistent Sessions** | 장기간 대화 세션 유지 | 컨텍스트 손실, 재연결 비용 |

#### Durable Execution의 기술적 원리

Durable Execution은 Temporal, Inngest 같은 워크플로우 엔진에서 영감을 받은 개념이다. 핵심 아이디어는 **이벤트 소싱(Event Sourcing)**이다.

에이전트의 모든 상태 변화를 이벤트 스트림으로 기록한다. 에이전트가 크래시되면, 이벤트 로그를 리플레이(replay)하여 마지막 정상 상태로 복구한다. 이는 데이터베이스의 WAL(Write-Ahead Log)과 같은 원리다.

```python
from cloudflare.agents import Agent, durable, sandbox

@durable(timeout="2h", retry_policy={"max_attempts": 3})
class CodeReviewAgent(Agent):
    """장기 실행 코드 리뷰 에이전트"""
    
    async def run(self, repo_url: str):
        # 1. 리포지토리 클론
        repo = await self.clone_repository(repo_url)
        
        # 2. 파일 단위 분석 - 각 파일을 서브 에이전트에 위임
        files = await repo.get_changed_files()
        
        sub_agents = []
        for file in files:
            # 서브 에이전트 생성 및 오케스트레이션
            agent = self.spawn_sub_agent(
                FileAnalyzerAgent,
                file_path=file.path,
                timeout="10m"
            )
            sub_agents.append(agent)
        
        # 3. 서브 에이전트 결과 수집 (병렬 실행)
        results = await self.gather(sub_agents)
        
        # 4. 샌드박스에서 테스트 실행
        test_result = await self.sandbox.run(
            command="pytest tests/",
            image="python:3.11",
            memory="512Mi",
            timeout="5m"
        )
        
        # 5. 최종 리포트 생성
        return self.generate_report(results, test_result)

@sandbox(image="python:3.11", network="isolated")
class FileAnalyzerAgent(Agent):
    """개별 파일 분석 서브 에이전트"""
    
    async def run(self, file_path: str):
        content = await self.read_file(file_path)
        
        # LLM 호출 - 상태는 자동 영속화됨
        analysis = await self.llm.chat(
            model="claude-sonnet-4-20250514",
            messages=[
                {"role": "system", "content": "Analyze code quality..."},
                {"role": "user", "content": content}
            ]
        )
        
        return {"file": file_path, "analysis": analysis}
```

이 코드에서 주목할 점은 `@durable` 데코레이터다. 이 데코레이터 하나로:

1. **자동 체크포인트**: 각 `await` 지점마다 상태가 자동 저장된다
2. **자동 재시도**: 실패 시 설정된 retry_policy에 따라 재시도된다
3. **타임아웃 관리**: 2시간 초과 시 자동으로 정리된다

### 서브 에이전트 오케스트레이션 패턴

Project Think의 서브 에이전트 시스템은 **Actor Model**과 유사한 구조를 가진다. 부모 에이전트가 하위 에이전트를 생성하고, 메시지 패싱으로 통신하며, 각 에이전트는 독립적인 생명주기를 가진다.

```python
from cloudflare.agents import Agent, PersistentSession

class DevelopmentOrchestrator(Agent):
    """복잡한 개발 작업을 관리하는 오케스트레이터"""
    
    async def run(self, task: str):
        # 영속 세션 시작 - 사용자와의 대화 컨텍스트 유지
        session = PersistentSession(
            session_id=self.context.user_id,
            ttl="7d"  # 7일간 유지
        )
        
        # 이전 컨텍스트 복원
        history = await session.get_history()
        
        # 작업 분해
        subtasks = await self.plan(task, context=history)
        
        # 파이프라인 실행
        results = {}
        for subtask in subtasks:
            if subtask.type == "research":
                results[subtask.id] = await self.spawn(
                    ResearchAgent, 
                    query=subtask.description
                )
            elif subtask.type == "code":
                results[subtask.id] = await self.spawn(
                    CodingAgent,
                    spec=subtask.specification,
                    dependencies=results.get(subtask.depends_on)
                )
            elif subtask.type == "test":
                results[subtask.id] = await self.spawn(
                    TestingAgent,
                    code=results[subtask.code_ref]
                )
        
        # 세션에 결과 저장
        await session.save_context(results)
        return results
```

### 기존 솔루션과의 비교

| 기준 | 로컬 에이전트 (Cursor 등) | 기존 SDK (LangChain) | Project Think |
| :--- | :--- | :--- | :--- |
| **실행 환경** | 로컬 머신 | 서버 (수동 배포) | Cloudflare Workers |
| **상태 영속성** | 없음 (프로세스 종료 시 손실) | 수동 구현 필요 | 자동 (Durable Execution) |
| **유휴 비용** | 전체 리소스 비용 발생 | 인스턴스 유지 비용 | 요청당 과금 (유휴 시 0원) |
| **코드 실행 보안** | 호스트 OS 직접 접근 | 컨테이너 (수동 관리) | 샌드박스 (자동 격리) |
| **확장성** | 단일 머신 제한 | 수동 스케일링 | 자동 스케일링 |
| **세션 지속** | 브라우저 세션 | 구현 필요 | Persistent Sessions |

### 실무 적용: Step-by-Step 가이드

Project Think를 활용하여 장기 실행 에이전트를 구축하는 과정을 단계별로 살펴보자.

**Step 1: SDK 설치 및 설정**

```bash
# Cloudflare Workers 환경 설정
npm install -g wrangler
wrangler login

# Agents SDK 설치
pip install cloudflare-agents
```

**Step 2: 에이전트 정의**

```python
from cloudflare.agents import Agent, durable, PersistentSession
from cloudflare.agents.tools import WebSearch, CodeInterpreter

@durable(
    timeout="1h",
    retry_policy={"max_attempts": 5, "backoff": "exponential"},
    checkpoint_interval="30s"
)
class ResearchAgent(Agent):
    """장기 실행 리서치 에이전트"""
    
    tools = [WebSearch, CodeInterpreter]
    
    system_prompt = """
    You are a research agent. Conduct thorough analysis.
    Save intermediate results frequently.
    """
    
    async def run(self, research_question: str):
        # 연구 계획 수립
        plan = await self.think(research_question)
        
        # 단계별 실행 - 각 단계마다 자동 체크포인트
        findings = []
        for step in plan.steps:
            result = await self.execute_step(step)
            findings.append(result)
            
            # 중간 결과 영속화
            await self.checkpoint({
                "completed_steps": step.id,
                "findings": findings
            })
        
        return await self.synthesize(findings)
```

**Step 3: 배포 및 모니터링**

```bash
# 에이전트 배포
wrangler deploy

# 실행 상태 모니터링
wrangler agents list
wrangler agents logs <agent-id>
```

### 샌드박스 코드 실행의 보안 모델

Project Think의 샌드박스는 **V8 Isolates** 기반이다. Cloudflare Workers와 동일한 기술을 사용하여, 마이크로초 단위의 시작 시간과 완전한 격리를 동시에 달성한다.

```python
from cloudflare.agents import Sandbox

# 격리된 환경에서 신뢰할 수 없는 코드 실행
async def execute_user_code(code: str):
    sandbox = Sandbox(
        runtime="python",
        memory_limit="256Mi",
        cpu_limit="1",
        network="none",  # 네트워크 접근 차단
        filesystem="read_only",  # 읽기 전용 파일시스템
        timeout="30s"
    )
    
    try:
        result = await sandbox.run(code)
        return result.stdout
    except Sandbox.TimeoutError:
        return "Execution timed out"
    except Sandbox.MemoryError:
        return "Memory limit exceeded"
    finally:
        await sandbox.destroy()  # 리소스 즉시 해제
```

이 샌드박스 모델은 AI가 생성한 코드를 안전하게 실행하는 핵심 요소다. 특히 사용자 입력을 기반으로 코드를 생성하는 에이전트에서는 필수적이다.

## 결론

### 핵심 요약

Project Think는 장기 실행 AI 에이전트 개발의 근본적 문제를 해결한다:

1. **Durable Execution**으로 프로세스 실패 시에도 상태를 보존한다
2. **서브 에이전트 오케스트레이션**으로 복잡한 작업을 계층적으로 관리한다
3. **샌드박스 실행**으로 AI 생성 코드를 안전하게 실행한다
4. **영속 세션**으로 장기간 컨텍스트를 유지한다

이 모든 것이 Cloudflare의 엣지 인프라 위에서 동작하며, 유휴 시간 비용이 발생하지 않는 요청당 과금 모델을 제공한다.

### 전문가 인사이트

Project Think의 진정한 의의는 단순히 새로운 SDK가 아니라, **AI 에이전트의 패러다임 전환**에 있다. 지금까지 AI 에이저는 기본적으로 "대화형 챗봇"의 확장으로 이해되었다. 사용자가 프롬프트를 입력하고, AI가 응답하는 동기식 모델이다.

하지만 실제 프로덕션 환경에서 필요한 에이전트는 **비동기적이고 장기 실행되며, 분산된** 시스템이다. 한 에이전트가 코드를 작성하는 동안 다른 에이전트는 테스트를 실행하고, 또 다른 에이전트는 문서를 업데이트하는 식이다. 이러한 복잡한 오케스트레이션을 견고하게 관리하려면, Temporal 같은 워크플로우 엔진에서 검증된 패턴이 필요하다.

Project Think는 바로 그 지점—에이전트 오케스트레이션과 워크플로우 엔진의 결합—을 겨냥하고 있다. 향후 에이전트 생태계는 기능(capability) 경쟁을 넘어, **신뢰성(reliability)**과 **지속성(durability)** 경쟁으로 이동할 것이다.

### 참고 자료
- [Project Think 공식 발표 - Cloudflare Blog](https://news.hada.io/topic?id=28579)
- [Durable Execution 패턴 - Temporal Documentation](https://temporal.io/durable-execution)
- [Actor Model for AI Agents - Microsoft Research](https://www.microsoft.com/en-us/research/publication/actors-for-ai/)
- [Cloudflare Workers V8 Isolates Architecture](https://developers.cloudflare.com/workers/platform/how-workers-works/)
- [SWE-agent: Autonomous Coding Agent - Princeton NLP](https://swe-agent.com/)

---

**출처**: [https://news.hada.io/topic?id=28579](https://news.hada.io/topic?id=28579)