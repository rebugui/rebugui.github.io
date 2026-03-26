---
title: "AI Agent Protocol: MCP, A2A 등 6가지 프로토콜 개발 가이드"
date: 2026-03-23T01:30:08+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
---

## 서론

빈번한 주문이 쏟아지는 금요일 저녁의 레스토랑 주방을 상상해 보십시오. 오늘은 예상치 못한 '특제 스테이크' 주문이 폭주하여 한시간 만에 재고가 바닥났습니다. 이때 인간 점장은 육류 공급업체에 전화를 걸어 재고를 확인하고, 배송 시간을 협의한 뒤 포스(POS) 시스템에 메뉴 품절 처리를 할 것입니다. 하지만 AI 에이전트로 구축된 '스마트 레스토랑'에서는 어떤 일이 벌어져야 할까요?

주방 관리 에이전트(Kitchen Agent)가 육류 부족을 감지하면, 즉시 공급망 에이전트(Supply Agent)에게 "소고리 10kg 긴급 발주"를 요청해야 합니다. 이때 공급망 에이전트는 공급업체의 ERP 시스템을 조회하고, 협상을 통해 배송을 확정한 뒤, 그 결과를 다시 주방 관리 에이전트에게 통보해야 합니다. 문제는 주방 에이전트와 공급망 에이전트가 서로 다른 개발사에서 만들어졌고, 서로 다른 데이터 포맷과 통신 방식을 사용한다는 점입니다.

이것이 바로 현재 생성형 AI 생태계가 직면한 '바벨탑' 문제입니다. 수많은 에이전트가 개별적으로 존재하지만, 상호운용성(Interoperability)이 부족하여 협업이 불가능합니다. 이를 해결하기 위해 등장한 것이 **AI 에이전트 프로토콜**입니다. 본문에서는 MCP(Model Context Protocol), A2A(Agent-to-Agent) 등 핵심 프로토콜 6가지를 분석하고, Google ADK(Agent Development Kit)를 활용하여 실제 에이전트 간 협업 시스템을 구축하는 방법을 기술적으로 심도 있게 다루고자 합니다.

## 본론

### 1. 6가지 에이전트 프로토콜의 기술적 분류

레스토랑 공급망 시나리오를 원활하게 만들기 위해서는 에이전트 간의 소통뿐만 아니라 데이터 접근, 사용자 인터페이스 제어 등 다양한 계층의 표준이 필요합니다. 최근 논의되는 주요 프로토콜 6가지는 각기 다른 문맥(Context)과 목적을 해결합니다.

1.  **MCP (Model Context Protocol)**: Anthropic이 제안한 프로토콜로, LLM이 외부 데이터(파일, 데이터베이스, API)에 접근하고 컨텍스트를 이해하는 표준입니다. 2.  **A2A (Agent-to-Agent)**: 에이전트 간의 직접적인 메시지 교환과 협상을 위한 통신 프로토콜입니다. 3.  **UCP (Universal Control Protocol)**: 에이전트가 물리적 또는 디지털 도구를 제어하고 명령을 실행하기 위한 프로토콜입니다. 4.  **AP2 (Agent-to-Process)**: 비즈니스 프로세스 워크플로우를 에이전트가 이해하고 실행할 수 있게 정의한 프로토콜입니다. 5.  **A2UI (Agent-to-UI)**: 에이전트가 사용자의 화면(버튼 클릭, 스크롤 등)을 직접 제어하여 인간처럼 앱을 조작하는 프로토콜입니다. 6.  **AG-UI (Agent Graphic UI)**: 에이전트가 사용자에게 정보를 시각적으로 표현하기 위한 전용 그래픽 인터페이스 표준입니다.

이 중 가장 핵심적인 것은 **데이터와 도구에 대한 접근을 표준화하는 MCP**와 **에이전트 간 대화를 정의하는 A2A**입니다.

### 2. 에이전트 협업 아키텍처 다이어그램

앞서 언급한 레스토랑 시나리오를 구현하기 위해, 주방 에이전트가 MCP를 통해 공급업체 데이터베이스에 접근하고, A2A를 통해 협상 에이전트와 통신하는 과정을 시각화하면 다음과 같습니다. 이 아키텍처는 Google ADK가 제공하는 오케스트레이션 환경 위에서 구동됩니다.

```javascript
graph LR
    A[User Request] --> B[Kitchen Agent]
    B -->|Need Supply Info| C[MCP Server]
    B -->|Negotiate Price| D[Supplier Agent]
    C -->|Data Response| B
    D -->|Quote Response| B
    B -->|Execute Order| E[POS System UCP]
    B --> F[Frontend Display]
```

이 다이어그램은 복잡한 스타일 없이 각 구성 요소의 역할과 데이터 흐름을 명확하게 보여줍니다. 에이전트는 직접 데이터베이스나 외부 시스템과 결합하지 않고, MCP와 UCP라는 표준화된 계층을 통해 안전하게 상호작용합니다.

### 3. MCP (Model Context Protocol)의 원리와 Google ADK

MCP는 단순한 API 호출 이상의 구조를 가집니다. 클라이언트(Host Application, 예: Cursor, Google ADK)와 서버(예: GitHub, Database, Slack) 간의 표준화된 인터페이스를 제공합니다. 핵심 컴포넌트는 다음과 같습니다.
- **Resources**: 시스템의 상태나 데이터(예: `inventory://beef/stock`)를 읽기 전용으로 제공하는 URI 기반의 자원입니다.
- **Prompts**: 재사용 가능한 프롬프트 템플릿입니다. 에이전트가 복잡한 작업을 수행할 때 사전 정의된 양식을 사용할 수 있게 합니다.
- **Tools**: 데이터를 수정하거나 외부 시스템과 상호작용할 수 있는 실행 가능한 함수입니다.

Google ADK는 이러한 MCP 서버들을 쉽게 호스팅하고, 에이전트가 이들을 활용하여 복잡한 작업을 수행하도록 돕는 프레임워크입니다. ADK는 LangGraph와 유사한 상태 기반(Stateful) 관리를 통해 에이전트의 "생각(Thought)"과 "행동(Action)" 사이클을 제어합니다.

### 4. 프로토콜 비교 및 활용 전략

각 프로토콜은 에이전트 시스템의 어느 부분을 담당하는지 명확히 이해해야 합니다. 레스토랑 시나리오에 적용했을 때의 비교는 다음과 같습니다.

| 프로토콜 | 주요 역할 | 레스토랑 시나리오 예시 | 기술적 특징 | | :--- | :--- | :--- | :--- | | **MCP** | 데이터 접근 및 컨텍스트 제공 | 공급업체 DB에서 현재 소고리 가격 조회 | JSON-RPC 기반, 호스트-서버 구조 | | **A2A** | 에이전트 간 협상 및 메시징 | 할인 협상을 위해 다른 식당 에이전트와 커뮤니케이션 | 비동기 메시지 큐, 표준화된 의미론 | | **UCP** | 물리/디지털 액션 실행 | 재고 부족 시 POS 시스템에 자동 품절 등록 처리 | 명령(Command) 패턴, 보안 인증 중시 | | **A2UI** | 사용자 인터페이스 자동화 | 직원이 없을 때 키오스크 화면을 제어하여 주문 | 컴퓨터 비전, DOM 접근 |

### 5. 실전 구현: MCP 서버 구현 (Python)

이제 실제로 MCP 서버를 구축하여 에이전트가 재고 데이터를 조회할 수 있는 환경을 만들어 보겠습니다. 아래 코드는 Python의 `mcp` 라이브러리(가상의 SDK 구조)를 사용하여 간단한 재고 확인 서버를 구현한 예제입니다. 이 코드는 `stdio`를 통해 통신하며, Google ADK나 Claude Desktop과 같은 MCP 호스트와 연동될 수 있습니다.

```python
import asyncio
from mcp.server import Server
from mcp.types import Tool, TextContent
import json

# MCP 서버 인스턴스 생성
app = Server("restaurant-supply-chain")

# 가상의 재고 데이터베이스
INVENTORY_DB = {
    "beef": {"stock": 5, "unit": "kg", "price_per_kg": 50000},
    "tomato": {"stock": 20, "unit": "kg", "price_per_kg": 3000},
}

@app.list_tools()
async def list_tools() -> list[Tool]:
    """에이전트가 사용할 수 있는 도구 목록을 반환합니다."""
    return [
        Tool(
            name="check_inventory",
            description="현재 재고를 확인하고 재고가 부족하면 필요 수량을 계산합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "item": {"type": "string", "enum": ["beef", "tomato"]},
                    "required_quantity": {"type": "number"}
                },
                "required": ["item", "required_quantity"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """도구 실행 로직"""
    if name == "check_inventory":
        item = arguments.get("item")
        required = arguments.get("required_quantity")
        
        current_stock = INVENTORY_DB.get(item, {}).get("stock", 0)
        
        if current_stock >= required:
            message = f"[OK] {item}: 충분합니다. (현재: {current_stock})"
        else:
            shortage = required - current_stock
            message = f"[URGENT] {item}: 부족합니다. (현재: {current_stock}, 필요 추가: {shortage})"
            
        return [TextContent(
            type="text",
            text=json.dumps({"status": "success", "message": message, "data": INVENTORY_DB[item]})
        )]
    return [TextContent(type="text", text="Unknown tool")]

async def main():
    # stdio를 통해 MCP 호스트와 통신 시작
    async with app.run_stdio():
        pass # 무한 루프 대기

if __name__ == "__main__":
    asyncio.run(main())
```

이 코드는 에이전트가 "소고리 10kg 확인해줘"라고 요청했을 때, 데이터베이스를 조회하여 "5kg밖에 없으니 5kg이 더 필요하다"는 구조화된 응답을 반환합니다. 이러한 표준화된 인터페이스 덕분에 에이전트는 데이터베이스 스키마를 몰라도도 도구(Tool) 이름과 인자만으로 원하는 작업을 수행할 수 있습니다.

### 6. 단계별 개발 가이드: 에이전트 통합 시스템 구축

이제 프로토콜과 코드를 바탕으로 실무에서 에이전트 시스템을 구축하는 단계를 정리합니다.

1.  **도구 정의 및 MCP 서버화 (Define & Expose)**     기존 레거시 시스템(재고 DB, 회계 ERP)을 래핑하여 MCP 서버로 변환합니다. 이때 민감한 데이터는 `Resources`가 아닌 인증이 필요한 `Tools`로 노출해야 합니다.

2.  **의사소통 규칙 설정 (A2A Protocol Design)**     에이전트 간 메시지 포맷을 정의합니다. 예를 들어, 주문 에이전트가 발송하는 메시지는 `{ "intent": "ORDER_REQUEST", "items": [...], "urgency": "HIGH" }`와 같은 JSON 스키마를 따르도록 강제합니다.

3.  **오케스트레이션 로직 구현 (Google ADK)**     ADK를 사용하여 메인 에이전트(Manager)를 구축합니다. 이 에이전트는 사용자의 요청을 받으면, 어떤 MCP 서버를 호출해야 하고, 어떤 하위 에이전트(A2A)에게 작업을 위임해야 할지 결정하는 LLM 기반의 라우터 역할을 합니다.

4.  **UI 연동 및 피드백 루프 (A2UI / AG-UI)**     최종 결정 사항(예: 긴급 주문 승인)을 사용자에게 승인받기 위해 AG-UI를 통해 간단한 버튼 인터페이스를 띄우거나, A2UI를 통해 기존 ERP 웹페이지에 자동 입력합니다.

5.  **배포 및 모니터링 (MLOps)**     각 MCP 서버는 독립적인 도커 컨테이너로 배포되며, Google ADK는 상태를 안정적으로 관리합니다. 에이전트 간 대화 로그는 추적 가능하도록 저장하여 헬루시네이션이 발생했을 때 원인을 분석할 수 있어야 합니다.

## 결론

AI 에이전트 프로토콜(MCP, A2A 등)의 등장은 생성형 AI가 '장난감'에서 '인프라'로 진입하는 결정적인 순간입니다. 단일 LLM이 모든 것을 해결하려는 시도는 한계에 도달했으며, 이제는 특정 목적을 가진 전문 에이전트들이 표준화된 프로토콜을 통해 군집(Swarm)을 이루어 협업하는 시대로 넘어가고 있습니다.

본문에서 살펴본 레스토랑 공급망 사례는 비즈니스의 한 단면에 불과합니다. 금융의 거래 검증, 제조의 공장 관제, 헬스케어의 환자 모니터링 등 모든 도메인에서 이 프로토콜들은 상호운용성의 기반이 될 것입니다. 특히 Google ADK와 같은 프레임워크는 이러한 복잡한 프로토콜 엔지니어링을 추상화하여 개발자가 비즈니스 로직에 집중할 수 있게 돕습니다.

연구자 및 엔지니어로서 우리는 이제 단순히 프롬프트를 작성하는 것을 넘어, 에이전트 간의 계약(Contract)을 설계하고 프로토콜을 준수하는 신뢰할 수 있는 시스템을 구축해야 합니다. 이것이 바로 진정한 Agentic AI의 미래입니다.

**참고자료:**
- [Model Context Protocol (MCP) Spec](https://modelcontextprotocol.io/)
- [Google Agent Development Kit (ADK) Documentation](https://cloud.google.com/agent-development)
- Anthropic, "Building Agentic Systems with MCP" (2024)

---

**출처**: [https://news.hada.io/topic?id=27636](https://news.hada.io/topic?id=27636)