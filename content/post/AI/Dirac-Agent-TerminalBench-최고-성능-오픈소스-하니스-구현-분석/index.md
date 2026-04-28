---
title: "Dirac Agent: TerminalBench 최고 성능, 오픈소스 하니스 구현 분석"
date: 2026-04-29T01:06:48+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
---

## 서론

최근 생성형 AI의 패러다임이 단순한 채팅 인터페이스에서 능동적인 **AI 에이전트(Agent)**로 급격히 이동하고 있습니다. 특히 리눅스 터미널이나 쉘 환경을 제어하여 복잡한 개발 작업을 자동화하는 기술은 MLOps와 자동화 분야에서 '성배'와도 같이 여겨집니다. 하지만 터미널 자동화는 채팅창과 달리 한 번의 명령어 실수가 치명적인 결과를 초래할 수 있는 낮은 관용도(Low Tolerance) 환경이며, 시스템의 현재 상태를 실시간으로 파악하는 'Observability'가 필수적입니다.

이러한 어려움 속에서 터미널 자동화 벤치마크인 **TerminalBench 2.0**은 모델의 실제 코딩 및 문제 해결 능력을 검증하는 리트머스 시험지로 자리 잡았습니다. 흥미로운 점은 최근 오픈소스 커뮤니티에서 개발된 'Dirac'이라는 에이전트가 구글(Gemini-3-flash-preview)의 공식 구현체(47.8%)는 물론, 기존 최상위 폐쇄형 모델인 Junie CLI(64.3%)까지 제치고 **65.2%**라는 압도적인 성적을 기록했다는 것입니다. 이 결과는 단순히 더 강력한 LLM을 사용했다는 뜻이 아닙니다. 이는 **에이전트를 감싸고 있는 하니스(Harness) 설계**, 즉 모델의 행동을 제어하고 관찰하는 실행 환경의 품질이 성능의 핵심 변수임을 시사합니다.

## 본론

### 하니스(Harness)의 중요성과 기술적 배경

Dirac의 성과는 "모델이 전부가 아니다"라는 명제를 증명합니다. 많은 연구자들이 모델의 파라미터 수나 사전 학습 데이터에 집중하는 사이, Dirac은 모델과 환경 사이의 인터페이스를 최적화하는 데 주력했습니다. 터미널 벤치마크에서 모델은 단순히 명령어를 생성하는 것을 넘어, 긴 출력 결과를 파싱하고, 에러 메시지를 이해하며, 이를 바탕으로 다음 행동을 계획하는 복잡한 루프(Loop)를 실행해야 합니다.

특히 최근 TerminalBench 2.0에서 일부 에이전트가 문제 해결 힌트가 포함된 `{agents/skills}.md`와 같은 파일을 몰래 주입하는 등 편법을 쓰는 사례가 드러나며 논란이 된 바 있습니다. 하지만 Dirac은 완벽하게 공정한 조건, 즉 외부 리소스 수정이나 하드코딩된 스킬 없이, 오픈소스 코드와 동일한 환경에서 이 결과를 달성했습니다. 이는 견고한 하니스 설계가 모델의 추론 능력을 최대한 끌어올릴 수 있음을 보여줍니다.

### Dirac의 아키텍처: Think-Act-Observe 루프

Dirac의 핵심은 효율적인 상태 관리와 피드백 루프입니다. 아래 다이어그램은 Dirac이 터미널 명령을 수행하고 학습하는 단순화된 프로세스를 보여줍니다.

```javascript
graph TD
    A[User Task] --> B[Dirac Harness]
    B --> C[LLM Reasoning]
    C --> D[Command Generation]
    D --> E[Terminal Execution]
    E --> F[Output Observation]
    F --> G{Status Check}
    G -- Success --> H[Task Complete]
    G -- Failure/Incomplete --> B
```

이 루프는 단순해 보이지만, 각 단계에서의 '프롬프트 엔지니어링'과 '컨텍스트 윈도우 관리'가 미묘하게 작용합니다. Dirac의 하니스는 터미널의 출력 중 불필요한 잡음(Noise)을 필터링하고, LLM이 중요한 에러 로그에 집중하도록 돕습니다.

### 주요 성능 비교 및 분석

아래 표는 Dirac과 경쟁 모델들의 TerminalBench 2.0 성능과 주요 특징을 비교한 것입니다.

| 비교 항목 | Google Official (Gemini-3) | Junie CLI (Closed Source) | **Dirac (Ours)** | | :--- | :--- | :--- | :--- | | **벤치마크 점수** | 47.8% | 64.3% | **65.2%** | | **모델 접근성** | 공식 API 사용 | 폐쇄형 (Closed) | **오픈소스 (Fully Open)** | | **하니스(Harness)** | 기본 제공 구현체 독점 | 독자적 구현 (비공개) | **공개 (GitHub)** | | **부정 행위(Cheating)** | 없음 (Official) | 제기된 바 없음 | **없음 (검증됨)** | | **핵심 강점** | 멀티모달 입력 처리 | 독자적 파인튜닝 모델 | **실행 환경 최적화** |

### 실무 적용을 위한 구현 가이드

Dirac의 핵심 아이디어는 오픈소스 LLM(예: Llama 3, Mistral 등)을 활용하여도 훌륭한 터미널 에이전트를 구축할 수 있다는 점입니다. 아래는 Python을 사용하여 간단한 터미널 에이전트 하니스를 구현하는 예시 코드입니다.

이 코드는 `subprocess`를 통해 터미널 명령을 실행하고, 그 결과를 다시 LLM에게 피드백하여 다음 명령을 생성하는 기본 메커니즘을 보여줍니다.

```python
import subprocess
import openai # 또는 Hugging Face Transformers 등

class TerminalAgent:
    def __init__(self, model_name):
        self.client = openai.OpenAI() # LLM 클라이언트 초기화
        self.model_name = model_name
        self.history = []

    def run_command(self, cmd):
        """터미널 명령 실행 및 결과 반환"""
        try:
            result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            return result.stdout, result.stderr, result.returncode
        except Exception as e:
            return "", str(e), -1

    def think(self, user_task, observation):
        """LLM을 통한 사고 및 명령 생성"""
        system_prompt = f"""
        You are a terminal assistant. 
        Current Task: {user_task}
        Previous Observation: {observation}
        
        Respond with a single shell command to execute next.
        If the task is complete and successful, respond with 'DONE'.
        """
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "system", "content": system_prompt}],
            temperature=0.1
        )
        return response.choices[0].message.content.strip()

    def execute_loop(self, task, max_steps=10):
        """Dirac 스타일의 Think-Act-Observe 루프"""
        observation = "Terminal ready."
        
        for _ in range(max_steps):
            print(f"Observation: {observation[:100]}...") # 로그 출력
            
            action = self.think(task, observation)
            print(f"Action: {action}")

```

```python
            if action == "DONE":
                print("Task Completed Successfully.")
                break
            
            stdout, stderr, returncode = self.run_command(action)
            
            # 성공/실패 여부에 따른 관찰 결과 구성
            if returncode == 0:
                observation = stdout
            else:
                observation = f"Error: {stderr}"

# 사용 예시 (API 키 필요)
# agent = TerminalAgent("gpt-4o-mini")
# agent.execute_loop("List all python files in the current directory and create a zip file named 'code.zip'")
```

이 코드는 Dirac의 복잡한 로직을 극도로 단순화한 것이지만, `run_command`와 `think` 함수가 분리되어 있어 독립적인 모듈로 테스트 및 최적화가 가능하다는 '하니스'의 철학을 반영합니다.

### 기술적 심층 분석: Dirac이 성공한 이유

1.  **상태 추적 및 컨텍스트 압축**: 터미널 작업은 긴 시간 동안 진행되어 컨텍스트 창(Context Window)을 가득 채울 수 있습니다. Dirac은 최근의 중요한 로그만 유지하거나 요약(Summarization) 기법을 활용해 모델의 추론 능력을 보존합니다. 2.  **격리된 샌드박스 실행**: 벤치마크 환경과 호환되면서도 안전한 명령 실행을 보장하기 위해 컨테이너 환경 격리를 엄격히 수행합니다. 이는 실행 횟수나 타임아웃 리소스를 제어하는 데 필수적입니다. 3.  **명확한 피드백 신호**: 모호한 텍스트 피드백보다는 구조화된 에러 코드나 상태 플래그를 활용하여 LLM이 현재 상황을 더 명확히 인식하도록 돕습니다.

## 결론

Dirac의 TerminalBench 2.0 최고 성능 달성은 AI 에이전트 연구에 중요한 시사점을 던집니다. 이는 초거대 모델의 파라미터 경쟁이 아니라, **모델을 어떻게 환경과 연결하느냐(Harness Design)**에 대한 승리입니다. 구글의 공식 구현체나 폐�

---

**출처**: [https://github.com/dirac-run/dirac](https://github.com/dirac-run/dirac)