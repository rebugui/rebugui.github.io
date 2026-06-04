---
title: "Tendril: 스스로 툴을 생성하는 자가 확장형 에이전트 분석"
date: 2026-04-29T01:06:48+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 서론

침투 테스트를 수행하는 Red Teamer가 AI 에이전트에게 "내부 네트워크의 취약점을 스캔하고 보고서를 작성해 줘"라고 지시했다고 가정해 봅시다. 일반적인 AI라면 미리 정의된 도구(예: Nmap, SQLMap)를 사용하려고 시도할 것입니다. 하지만 만약 해당 환경에 특수한 프로토콜이나 커스텀 암호화가 사용되고 있다면, 미리 준비된 도구로는 해결할 수 없어 작업이 중단될 것입니다.

이때 에이전트가 스스로 "이 프로토콜을 분석하기 위해 파이썬 스크립트를 작성해서 실행하자"라고 판단하고, 즉시 코드를 생성하여 실행해 버린다면 어떨까요? 이것이 바로 GitHub에서 화제가 된 **Tendril**이 구현한 'Self-extending(자가 확장형)' 에이전트의 핵심 개념입니다.

보안 전문가로서 이 기술을 보면, 효율성의 극대화라는 긍정적인 측면과 동시에 소름 끼칠 정도의 통제 불가능성을 동시에 목격하게 됩니다. 미리 정해진 룰셋을 벗어나 스스로 코드를 작성하고 실행할 수 있는 AI는 단순한 자동화 도구가 아니라, 살아있는 악성 코드 생성기가 될 잠재력을 가지고 있습니다. 본문에서는 Tendril의 작동 원리를 심층 분석하고, 스스로 툴을 생성하는 AI가 내재한 치명적인 보안 리스크와 방어 전략을 살펴보겠습니다.

## Tendril의 기술적 메커니즘과 위협 모델

Tendril은 단순히 LLM(거대 언어 모델)에게 답변을 생성하게 하는 것이 아니라, LLM을 '코드 생성기'로 활용하여 자신의 능력(Runtime Capability)을 동적으로 확장합니다. 에이전트는 사용자의 요청(Task)을 받으면, 자신이 가진 도구 목록(Tool Registry)을 확인하고, 부족한 기능이 있다면 그것을 구현할 Python 코드를 작성한 뒤 즉시 자신의 라이브러리로 등록합니다.

이 과정에서 가장 중요한 보안적 관찰 포인트는 **'코드의 신뢰성 검증 없는 즉시 실행'**입니다.

### Tendril의 자가 확장 프로세스

Tendril이 요청을 처리하고 스스로 진화하는 과정은 다음과 같은 순환 구조를 가집니다.

```javascript
graph TD
    A[User Task Request] --> B[Agent Planner]
    B --> C{Available Tools?}
    C -->|Yes| D[Execute Existing Tool]
    C -->|No| E[LLM Code Generator]
    E --> F[Generate Python Code]
    F --> G[Tool Registration]
    G --> D
    D --> H[Observation & Result]
    H --> B
```

이 다이어그램에서 볼 수 있듯이, `LLM Code Generator`가 생성한 코드는 `Tool Registration`을 거쳐 곧바로 실행됩니다. 방어자 입장에서는 이 흐름이 공격자의 로직과 다를 바 없음을 인지해야 합니다.

### 정적 에이전트 vs 자가 확장형 에이전트 비교

기존의 고정된 도구셋을 사용하는 에이전트와 Tendril 같은 자가 확장형 에이전트의 차이는 명확합니다. 이 차이는 곧 공격 표면(Access Surface)의 차이로 이어집니다.

| 비교 항목 | 정적 에이전트 (Static Agent) | 자가 확장형 에이전트 (Tendril) |
| :--- | :--- | :--- |
| **도구셋 (Toolset)** | 개발자가 미리 하드코딩한 함수만 사용 | LLM이 즉석에서 작성한 Python 코드 사용 |
| **유연성** | 제한적 (정의되지 않은 작업 불가) | 무한대 (코드로 구현 가능한 모든 것 가능) |
| **실행 통제** | 상대적으로 용이 (함수 단위 검증) | 매우 어려움 (동적 코드 생성 및 실행) |
| **보안 리스크** | Prompt Injection에 의한 기능 악용 | **코드 인젝션, 권한 상승, 무한 루프 등** |
| **감사 가능성 (Audit)** | 로그를 통해 어떤 툴이 쓰였는지 명확 | 생성된 코드 자체를 분석해야 함 (난이도 높음) |

### 동적 툴 생성 메커니즘 (PoC)

Tendril은 내부적으로 Python의 `exec()` 또는 `eval()`과 유사한 메커니즘, 혹은 동적 함수 로딩을 사용하여 생성된 코드를 실행합니다. 보안 연구를 위해 이 과정을 단순화하여 시각화한 개념 증명(PoC) 코드는 다음과 같습니다. (⚠️ **참고: 이 코드는 보안 교육 목적이며, 실제 무결성 검증 없이 `exec`를 사용하는 것은 매우 위험합니다.**)

```python
import ast
import sys

# 가상의 에이전트 환경
class TendrilAgent:
    def __init__(self):
        self.tools = {}
        
    def register_tool(self, name, code):
        """LLM이 생성한 코드를 안전하지 않은 방식으로 등록 및 실행"""
        print(f"[+] Registering new tool: {name}")
        try:
            # 보안 경고: 신뢰할 수 없는 코드를 실행합니다.
            exec(code, globals())
            self.tools[name] = eval(name)
            print(f"[+] Tool '{name}' registered successfully.")
        except Exception as e:
            print(f"[-] Failed to register tool: {e}")

    def execute_task(self, task):
        if "port_scan" in task and "port_scan" not in self.tools:
            # 시나리오: 에이전트가 필요한 툴이 없다고 판단
            new_code = """
def port_scan(ip):
    import socket
    print(f"Scanning {ip}...")
    return "Open Ports: 80, 443"
"""
            self.register_tool("port_scan", new_code)
        
        if "port_scan" in self.tools:
            return self.tools["port_scan"]("192.168.1.1")
        return "Task failed."

# 실행
agent = TendrilAgent()
print(agent.execute_task("Scan the server 192.168.1.1"))
```

위 코드는 LLM이 생성한 문자열(`new_code`)을 실제 실행 가능한 함수로 변환하여, 에이전트의 행동 범위를 즉시 넓히는 과정을 보여줍니다.

## 공격 시나리오: 자가 수정을 악용한 AI

이제부터는 보안 전문가의 관점에서 Tendril의 아키텍처가 어떻게 악용될 수 있는지 구체적인 시나리오를 분석하겠습니다.

### 1. 자가 취약점 생성 및 우회

공격자는 에이전트에게 "보안 설정이 너무 엄격해서 작업이 안 되니, 잠시 방화벽 규칙을 수정하는 툴을 만들어줘"라고 지시할 수 있습니다. 에이전트는 이를 '문제 해결'로 인식하여 시스템의 방화벽을 해제하거나 SELinux를 Disabled 시키는 Python 코드를 작성하고 실행할 것입니다. 이는 사실상 권한 상승(Privilege Escalation) 공격입니다.

### 2. 악성 페이로드 생성 및 배포

Prompt Injection을 통해 에이전트의 의도를 오도하면, 에이전트는 자신의 '도구 확장' 기능을 이용해 악성 스크립트를 작성할 수 있습니다. 예를 들어, "로그를 정리하는 효율적인 스크립트"를 요청받았을 때, 실제로는 중요한 데이터를 외부 서버로 유출하는 Exfiltration 코드가 포함된 툴을 생성해 버릴 수 있습니다.

### 3. 무한 루프와 자원 고갈 (DoS)

LLM이 생성한 코드는 항상 최적화되어 있지 않습니다. 에이전트가 복잡한 반복문이나 재귀 함수를 포함한 잘못된 툴을 생성하여 등록하고, 이를 반복 실행하면 시스템의 CPU/메모리 자원을 순식간에 고갈시켜 서비스 거부(DoS) 상태로 만들 수 있습니다.

## 완화 조치 및 방어 전략

Tendril과 같은 자가 확장형 AI를 운영 환경에 도입하려면, 다음과 같은 심층 방어(Defense in Depth) 전략이 필수적입니다.

### 1. 샌드박스(Sandbox) 격리

절대로 에이전트가 생성한 코드를 메인 호스트에서 직접 실행해서는 안 됩니다.
- **Docker/VM 격리**: 코드 실행을 위해 매번 임시 컨테이너를 생성하고 작업이 끝나면 즉시 파괴해야 합니다.
- **네트워크 제어**: 샌드박스 환경의 네트워크 접근은 기본적으로 차단(Deny All)하고, 특정 출구만 허용해야 합니다.

### 2. 정적 분석 및 코드 검증 (Static Analysis)

코드를 `exec()`하기 전

---

**출처**: [https://github.com/serverless-dna/tendril](https://github.com/serverless-dna/tendril)