---
title: "Roach PI: AI 코딩 에이전트 투명성 확보와 엔지니어링 규율 적용"
date: 2026-04-09T12:27:40+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
---

## 서론

지난주, AI 개발자 커뮤니티에 충격적인 문서 하나가 돌았다. Claude Code의 내부 시스템 프롬프트로 추정되는 수천 줄의 코드가 유출된 것이다. 이 문서에는 사용자가 절대 볼 수 없었던 수많은 지시사항들이 담겨 있었다: "어떤 파일을 우선적으로 읽을 것인가", "어떤 경우에 사용자에게 물어보고 어떤 경우에 임의로 진행할 것인가", "도구 사용을 어떻게 최적화할 것인가".

이 사건은 단순히 한 회사의 보안 사고가 아니었다. 그것은 **우리가 매일 의존하는 AI 코딩 에이전트가 사실상 완전한 블랙박스**라는 불편한 진실을 확인시켜 주었다.

개발자로서 우리는 프로덕션 코드에 들어가는 모든 라인을 검토한다. 코드 리뷰를 하고, 테스트 커버리지를 측정하며, 의존성을 신중하게 선택한다. 그런데 정작 가장 강력한 권한을 가진 "AI 페어 프로그래머"가 내부에서 무슨 짓을 하는지는 전혀 모른 채 사용해왔다.

Roach PI는 이 문제에 대한 근본적인 해결책을 제시한다. AI 코딩 에이전트 위에 **엔지니어링 규율(engineering discipline)을 적용**하여, 에이전트가 수행하는 모든 동작을 투명하게 만들고 사용자가 직접 제어할 수 있게 하는 오픈소스 확장이다.

## 본론

### AI 코딩 에이전트의 불투명성: 근본 원인

현대 AI 코딩 에이전트는 복잡한 multi-agent 시스템이다. 단순히 사용자의 요청을 LLM에 전달하는 것이 아니라, 다음과 같은 복잡한 파이프라인을 거친다:

1. **시스템 프롬프트 주입**: 개발사가 정의한 수천 줄의 지시사항
2. **컨텍스트 수집**: 프로젝트 파일, 히스토리, 메타데이터 스캔
3. **도구 선택 및 실행**: 파일 읽기, 쓰기, 셸 명령어 등
4. **자기 수정 루프**: 오류 발생 시 자동 재시도

문제는 이 과정에서 **사용자가 알 수 있는 것이 거의 없다**는 점이다. 어떤 파일이 읽혔는지, 어떤 추가 지시사항이 주입되었는지, 왜 특정 결정이 내려졌는지—모든 것이 불투명하다.

```javascript
graph TD
    A[사용자 요청] --> B[에이전트 블랙박스]
    B --> C[시스템 프롬프트 주입]
    C --> D[컨텍스트 수집]
    D --> E[도구 실행]
    E --> F[결과 반환]
    
    G[사용자에게 불투명한 영역] -.-> B
    G -.-> C
    G -.-> D
    G -.-> E
```

이러한 불투명성은 다음과 같은 실제 문제를 야기한다:

| 문제 유형 | 구체적 사례 | 영향도 |
| :--- | :--- | :--- |
| 보안 | 민감한 파일 무단 스캔 | 데이터 유출 위험 |
| 비용 | 과도한 토큰 사용으로 API 비용 폭증 | 예산 초과 |
| 품질 | 잘못된 컨텍스트로 인한 환각 | 버그 발생 |
| 디버깅 | 에이전트 동작 원인 파악 불가 | 생산성 저하 |

### Roach PI의 아키텍처: 투명성 계층 도입

Roach PI는 기존 AI 코딩 에이전트(현재는 Claude Code 지원)와 사용자 사이에 **투명성 계층(transparency layer)**을 삽입한다. 이 계층은 다음 세 가지 핵심 기능을 수행한다:

**1. 프롬프트 가로채기 및 검사 (Prompt Interception)**

모든 시스템 프롬프트와 사용자 프롬프트를 가로채서 사용자에게 표시한다. 에이전트가 실제로 어떤 지시사항을 받았는지 정확히 알 수 있다.

**2. 동작 로깅 및 모니터링**

에이전트가 수행하는 모든 도구 호출, 파일 접근, API 요청을 실시간으로 로깅한다.

**3. 제어 규칙 적용 (Governance Rules)**

사용자가 정의한 규칙에 따라 에이전트의 동작을 제한하거나 수정할 수 있다.

```javascript
graph LR
    A[사용자] --> B[Roach PI]
    B --> C[투명성 계층]
    C --> D[프롬프트 검사]
    C --> E[동작 로깅]
    C --> F[규칙 적용]
    D --> G[AI 코딩 에이전트]
    E --> G
    F --> G
    G --> H[실행 결과]
    H --> B
```

### 실제 구현: 코드로 보는 Roach PI

Roach PI의 핵심은 에이전트의 동작을 "후킹"하는 것이다. 다음은 개념적인 구현 예시다:

```python
from roach_pi import AgentProxy, TransparencyLayer, GovernanceRule

# 투명성 계층 초기화
transparency = TransparencyLayer(
    log_all_prompts=True,
    log_tool_calls=True,
    expose_system_prompt=True
)

# 거버넌스 규칙 정의
rules = [
    # 특정 디렉토리 접근 제한
    GovernanceRule(
        name="protect_secrets",
        pattern=r"\.env|credentials|secrets",
        action="block",
        message="민감한 파일 접근이 차단되었습니다"
    ),
    # 토큰 사용량 제한
    GovernanceRule(
        name="token_budget",
        max_tokens_per_request=50000,
        action="warn"
    ),
    # 파일 쓰기 전 사용자 승인 요구
    GovernanceRule(
        name="write_approval",
        tool_pattern="write_file|edit_file",
        action="require_approval"
    )
]

# 프록시 에이전트 생성
proxy = AgentProxy(
    base_agent="claude-code",
    transparency_layer=transparency,
    governance_rules=rules
)

# 사용자 요청 처리
response = proxy.execute("인증 모듈을 리팩토링해줘")

# 투명성 리포트 확인
print(response.transparency_report)
# 출력 예시:
# {
#   "system_prompt_tokens": 3247,
#   "files_accessed": ["auth.py", "config.py"],
#   "tools_used": ["read_file", "edit_file"],
#   "total_tokens": 12453,
#   "blocked_actions": []
# }
```

이 코드는 Roach PI의 핵심 개념을 보여준다. 실제 사용 시에는 CLI 도구나 IDE 확장으로 더 간편하게 사용할 수 있다.

### Step-by-Step: Roach PI 설치 및 설정

**Step 1: 저장소 클론 및 설치**

```bash
# 저장소 클론
git clone https://github.com/tmdgusya/roach-pi.git
cd roach-pi

# 의존성 설치
pip install -r requirements.txt

# 또는 npm을 사용하는 경우
npm install
```

**Step 2: 설정 파일 구성**

```yaml
# roach-pi-config.yaml
agent:
  type: claude-code
  path: /usr/local/bin/claude

transparency:
  log_prompts: true
  log_tool_calls: true
  log_file_access: true
  output_format: json

governance:
  rules:
    - name: block_secrets
      pattern: "\.env$|\.pem$|credentials"
      action: block
      
    - name: budget_limit
      max_tokens: 100000
      action: warn
      
    - name: require_approval_for_delete
      tools: ["delete_file", "execute_shell"]
      action: require_approval

output:
  log_file: ./roach-pi-logs/transparency.jsonl
  console_output: true
```

**Step 3: Roach PI 실행**

```bash
# Claude Code를 Roach PI로 래핑하여 실행
python roach-pi.py --config roach-pi-config.yaml

# 또는 직접 명령 전달
python roach-pi.py "프로젝트 구조를 분석하고 README를 업데이트해줘"
```

**Step 4: 투명성 리포트 확인**

```bash
# 실시간 로그 확인
tail -f ./roach-pi-logs/transparency.jsonl

# 요약 리포트 생성
python roach-pi.py --report --last-session
```

### 기술적 깊이: 프롬프트 인터셉션 메커니즘

Roach PI가 어떻게 에이전트의 내부 동작을 가로챌 수 있을까? 핵심은 **API 프록시 패턴**과 **프로세스 후킹**의 조합이다.

```javascript
graph TD
    A[AI 에이전트 프로세스] --> B[API 호출]
    B --> C[Roach PI 프록시]
    C --> D[요청 검사]
    D --> E{규칙 위반?}
    E -->|예| F[차단/수정]
    E -->|아니오| G[원본 API 전달]
    G --> H[LLM 응답]
    H --> I[응답 로깅]
    I --> J[사용자에게 반환]
    F --> J
```

**API 프록시 방식**: Roach PI는 LLM API 엔드포인트를 가로채는 로컬 프록시 서버를 실행한다. 에이전트는 자신이 직접 Anthropic API에 연결한다고 생각하지만, 실제로는 Roach PI를 거친다.

```python
# 간소화된 API 프록시 구현
from fastapi import FastAPI, Request
import httpx

app = FastAPI()
ANTHROPIC_API = "https://api.anthropic.com"

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(request: Request, path: str):
    # 원본 요청 캡처
    body = await request.body()
    headers = dict(request.headers)
    
    # 투명성 로깅
    log_request(body, headers)
    
    # 거버넌스 규칙 적용
    modified_body = apply_governance_rules(body)
    
    # 원본 API로 전달
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=request.method,
            url=f"{ANTHROPIC_API}/{path}",
            content=modified_body,
            headers=headers
        )
    
    # 응답 로깅
    log_response(response.content)
    
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers)
    )
```

이 방식의 장점은 **에이전트 코드를 수정할 필요가 없다**는 점이다. 환경 변수만 변경하면 된다:

```bash
export ANTHROPIC_BASE_URL="http://localhost:8080"
```

### 비교 분석: 기존 방식 vs Roach PI

| 측면 | 기존 AI 코딩 에이전트 | Roach PI 적용 |
| :--- | :--- | :--- |
| 시스템 프롬프트 | 불투명 (숨겨짐) | 완전 공개 |
| 파일 접근 로그 | 없음 또는 제한적 | 전체 기록 |
| 토큰 사용량 | 事后 확인만 가능 | 실시간 모니터링 |
| 동작 제어 | 불가능 | 규칙 기반 제어 |
| 디버깅 | 어려움 | 상세 추적 가능 |
| 보안 감사 | 불가능 | 완전한 감사 로그 |
| 커스터마이징 | 제한적 | 프롬프트 수정 가능 |

### 실무 적용 시나리오

**시나리오 1: 엔터프라이즈 보안 감사**

규제 대상 산업에서는 AI 시스템의 모든 동작을 감사할 수 있어야 한다. Roach PI는 SOC 2, ISO 27001 등의 컴플라이언스 요구사항을 충족시키는 감사 로그를 제공한다.

**시나리오 2: 비용 최적화**

어떤 유형의 작업이 토큰을 많이 소비하는지 파악하여, 프롬프트 엔지니어링이나 워크플로우 수정으로 비용을 절감할 수 있다.

**시나리오 3: 팀 협업 표준화**

팀 전체에 동일한 거버넌스 규칙을 적용하여, 모든 개발자가 일관된 방식으로 AI 코딩 에이전

---

**출처**: [https://news.hada.io/topic?id=28257](https://news.hada.io/topic?id=28257)