---
title: "📁 Llm9p: Plan 9로 LLM을 파일 시스템처럼 제어하기"
date: 2026-03-13T07:06:43+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
---

## 서론

현대의 AI 개발 환경, 특히 대규모 언어 모델(LLM)을 운영하는 인프라를 들여다보면 우리는 수많은 복잡성의 늪에 빠져 있습니다. OpenAI API, Anthropic API, Hugging Face Inference Endpoint, 그리고 이들을 호출하기 위한 무수한 Python 클라이언트 라이브러리들. 개발자가 단순히 모델에 질문을 던지고 답변을 받기 위해, HTTP 헤더를 설정하고, JSON 파싱을 처리하며, 재시도 로직을 구현하는 과정은 피로감을 안겨줍니다. 더구나 MLOps 관점에서 볼 때, 이러한 비표준화된 인터페이스는 모델 서빙의 통합 관리를 어렵게 만드는 주요 요인입니다.

여기서 우리는 컴퓨터 과학 역사의 가장 성공적인 추상화 중 하나인 "유닉스 철학(Unix Philosophy)"을 기억해야 합니다. "모든 것은 파일이다(Everything is a file)"라는 이 단순한 원칙은 수십 년간 수많은 소프트웨어의 상호 운용성을 보장해 왔습니다. 만약 LLM이 복잡한 REST API 엔드포인트가 아니라, 단순한 파일 시스템 내의 하나의 파일이나 디렉터리로 존재한다면 어떨까요? `cat` 명령어로 답변을 읽고, `echo` 명령어로 프롬프트를 전달하며, `chmod`로 접근 권한을 제어한다면 얼마나 개발 경험이 직관적이고 강력해질까요?

'Llm9p'는 바로 이러한 철학을 현대 생성형 AI 시대에 끌어온 프로젝트입니다. Plan 9 운영 체제에서 유래한 9P 프로토콜을 사용하여 LLM을 파일 시스템 인터페이스로 노출시킴으로써, 개발자는 별도의 SDK 없이 표준 시스템 호출만으로 거대 언어 모델을 제어할 수 있습니다. 이는 단순한 기술적 호기심을 넘어, AI 인프라의 구조를 단순화하고 보편적인 도구와의 통합성을 극대화하려는 시도입니다.

## 본론

### 기술적 배경: Plan 9와 9P 프로토콜

Llm9p를 이해하기 위해서는 먼저 Plan 9 from Bell Labs의 핵심 개념을 짚어볼 필요가 있습니다. Plan 9는 유닉스의 설계자들이 만든 후속 운영 체제로, "모든 것은 파일"이라는 개념을 극단까지 밀어붙였습니다. 네트워크 소켓, 윈도우 시스템, 심지어 프로세스 자체도 파일 시스템 네임스페이스 내의 파일로 다뤄집니다. 이때 사용되는 통신 프로토콜이 9P입니다.

Llm9p는 이 9P 프로토콜을 구현한 사용자 공간 파일 시스템(FUSE)입니다. 이는 로컬이나 원격의 LLM 추론 엔진(e.g., llama.cpp, vLLM 등)을 백엔드로 두고, 클라이언트에게는 마치 로컬 디스크의 파일처럼 보이게 만듭니다. 사용자가 특정 파일에 텍스트를 쓰면(write), 그 데이터가 프롬프트로 처리되어 모델에게 전송되고, 파일을 읽으면(read) 모델이 생성한 토큰들이 스트리밍되어 반환됩니다.

### 아키텍처 다이어그램

이 구조는 기존의 클라이언트-서버 모델과 유사하지만, 인터페이스 계층이 파일 시스템으로 추상화된다는 점이 결정적으로 다릅니다.

```javascript
graph LR
    A[User / App] --> B[Standard File Ops]
    B --> C[Plan 9 Filesystem]
    C --> D[Llm9p Server]
    D --> E[LLM Engine]
    E --> F[Model Weights]
    D --> G[Control Files]
```

### 파일 시스템 vs REST API 비교

기존의 방식과 Llm9p 방식을 비교하면, 왜 이 접근 방식이 획기적인지 명확해집니다. 특히 MLOps나 파이프라인 구축 시 표준 도구와의 호환성은 엄청난 생산성 향상을 가져옵니다.

| 비교 항목 | 기존 REST API (OpenAI 등) | Llm9p (File System) | | :--- | :--- | :--- | | **인터페이스** | HTTP Endpoint / JSON | 파일 경로 / I/O syscall | | **클라이언트 라이브러리** | Python SDK, Node.js 등 필요 | 별도 라이브러리 불필요 (os 모듈 등) | | **도구 통합** | curl, Postman (전문 도구 필요) | cat, echo, grep, tail (기본 Unix 도구) | | **스트리밍 처리** | SSE (Server-Sent Events) 구현 필요 | 파일 읽기 버퍼링으로 자동 해결 | | **권한 관리** | 별도의 API Key 시스템 | OS 파일 시스템 권한 (chmod, chown) | | **운영 모니터링** | 별도 메트릭 서비스 필요 | `ls -l`, `stat` 등으로 파일 상태 확인 |

### 구현 및 사용 가이드

Llm9p를 사용하는 과정은 놀라울 정도로 간단합니다. 복잡한 의존성을 설치하는 대신, 파일 시스템을 마운트하고 파일을 다루듯 모델을 제어합니다.

#### 1. 환경 설정 및 실행 Llm9p 서버는 보통 Go나 C로 작성된 가벼운 바이너리로 제공되며, 백엔드로 로컬 LLM 서버를 지정하여 실행합니다. 예를 들어, 로컬에서 실행 중인 llama.cpp 서버를 Llm9p에 연결한다고 가정해 봅시다.

```bash
# llm9p를 실행하여 특정 디렉토리에 마운트
# (백엔드 URL은 상황에 맞게 설정)
./llm9p -dir /mnt/llm -backend http://localhost:8080
```

#### 2. 상호작용 (Shell) 이제 `/mnt/llm` 디렉터리 아래에서 LLM과 상호작용할 수 있습니다. 가장 기본적인 "채팅"은 파일 쓰기와 읽기로 이루어집니다.

```bash
# 1. 프롬프트 전송 (모델에게 질문하기)
# 'prompt' 파일에 질문 내용을 씁니다.
echo "Explain Quantum Computing in one sentence." > /mnt/llm/prompt

# 2. 답변 수신 (모델의 답변 읽기)
# 'output' 파일을 읽으면 모델이 생성한 결과가 나옵니다.
cat /mnt/llm/output
```

이 과정은 비동기적으로 작동할 수 있습니다. `tail -f /mnt/llm/output`을 사용하면 마치 서버 로그를 보듯 토큰이 생성되는 과정을 실시간으로 모니터링할 수 있습니다.

#### 3. 파이썬을 이용한 프로그래매틱 제어 Python 개발자 입장에서 가장 큰 장점은 별도의 `openai` 라이브러리를 설치할 필요가 없다는 점입니다. 표준 파일 I/O만으로 AI 애플리케이션을 구축할 수 있습니다.

```python
import time

def query_llm(question: str):
    # 프롬프트 파일에 질문 쓰기
    with open("/mnt/llm/prompt", "w") as f:
        f.write(question)
    
    # 모델이 처리할 시간을 조금 주거나, 이벤트를 기다림
    # 실제 구현에서는 파일 기반 이벤트 핸들링을 사용할 수 있음
    time.sleep(0.5)
    
    # 결과 파일 읽기
    with open("/mnt/llm/output", "r") as f:
        response = f.read()
        
    return response

if __name__ == "__main__":
    result = query_llm("What is the capital of France?")
    print(f"LLM Answer: {result}")
```

이 코드의 아름다움은 `requests` 라이브러리조차 필요 없다는 사실에 있습니다. 순수 표준 라이브러리만으로 외부 지능형 시스템과 통합이 가능합니다.

### 고급 제어 및 메커니즘

단순한 질의응답을 넘어, Llm9p는 파일 시스템의 구조적 장점을 활용하여 파라미터 제어를 세분화합니다. 보통 다음과 같은 파일 구조를 가질 수 있습니다.

```javascript
graph TD
    A[/mnt/llm] --> B[prompt]
    A --> C[output]
    A --> D[ctl]
    D --> D1[temperature]
    D --> D2[top_k]
    D --> D3[top_p]
    D --> D4[model_name]
```
- **`ctl` 디렉터리**: 모델의 하이퍼파라미터를 제어하는 파일들이 위치합니다. 예를 들어, 생성의 창의성을 높이기 위해 다음과 같이 명령어를 입력할 수 있습니다.

```bash
echo 0.9 > /mnt/llm/ctl/temperature
echo 0.8 > /mnt/llm/ctl/top_p
```

이 방식은 MLOps 관점에서 설정 관리(Configuration Management)를 획기적으로 단순화합니다. 복잡한 YAML 설정 파일이나 환경 변수 대신, 단순히 파일 내용을 변경하는 것만으로 모델의 행동을 튜닝할 수 있습니다. 또한 `chown`과 `chmod`를 통해 특정 사용자나 그룹에게만 모델 사용 권한을 부여할 수 있으므로, 보안 관리 또한 OS 수준에서 위임할 수 있습니다.

## 결론

Llm9p는 소프트웨어 공학의 오랜 교훈인 "간단한 인터페이스의 강력함"을 AI 시대에 증명하는 프로젝트입니다. HTTP와 JSON이 웹의 표준으로 자리 잡았듯이, LLM과 같은 고차원적인 리소스를 파일 시스템으로 추상화하는 시도는 컴퓨팅 자원을 다루는 가장 원초적이고 보편적인 방법으로 돌아가는 지혜입니다.

전문가의 관점에서 볼 때, Llm9p의 가장 큰 잠재력은 **"Composability(조합성)"**에 있습니다. 셸 스크립트 파이프라인(`|`)을 통해 LLM의 출력을 바로 다른 프로그램의 입력으로 연결할 수 있는 능력은, AI 애플리케이션 개발 속도를 획기적으로 높여줍니다. 복잡한 RAG(Retrieval-Augmented Generation) 파이프라인조차도 파일 시스템의 도구들(e.g., grep, awk, find)만으로 조립할 수 있게 됩니다.

물론 현재의 생태계가 REST/gRPC 중심으로 구축되어 있어 당장 전면적인 도입에는 어려움이 있겠지만, 로컬 LLM 서빙, 엣지 컴퓨팅, 그리고 개발용 샌드박스 환경에서는 Llm9p가 매우 강력한 대안이 될 것입니다. 이는 "AI를 특별한 존재가 아니라 시스템의 일부(Hardware/OS의 일부)로 만들겠다"는 철학의 구현체이며, 앞으로 AI 인프라가 나아가야 할 방향성을 제시한다고 볼 수 있습니다.

AI를 개발하는 것이 아니라, AI를 '사용'하는 방식에 대한 패러다임 시프트. 그것이 바로 Llm9p가 우리에게 던지는 메시지입니다.

### 참고자료
- **Llm9p GitHub Repository**: [https://github.com/NERVsystems/llm9p](https://github.com/NERVsystems/llm9p)
- **Plan 9 from Bell Labs**: [https://9p.io/plan9/](https://9p.io/plan9/)
- **The 9P Protocol**: [https://9p.io/magic/man2html/5/](https://9p.io/magic/man2html/5/)

---

**출처**: [https://github.com/NERVsystems/llm9p](https://github.com/NERVsystems/llm9p)