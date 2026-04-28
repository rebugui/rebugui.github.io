---
title: "firma: Claude 기반 로컬 퍼스트 포트폴리오 관리 CLI"
date: 2026-04-29T01:06:59+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
---

## 서론

해외 주식 투자를 경험해 본 개발자라면 누구나 한 번쯤은 겪어봤을 법한 '스프레드시트 지옥'을 상상해 보십시오. 수시로 변동하는 환율, 각기 다른 거래소의 장 시간, 그리고 복잡한 배당일 계산까지. 이 모든 것을 엑셀이나 구글 스프레드시트로 관리하는 것은 단순히 번거로운 것을 넘어, 데이터 무결성을 해치는 위험한 작업입니다. `GOOGLEFINANCE` 함수가 가끔식 레이턴시를 일으키거나, 실수로 수식을 건드려 데이터가 꼬이는 상황은 개발자에게 재앙과도 같습니다.

여기서 핵심은 단순한 데이터 '시각화'가 아니라 데이터에 기반한 '통찰'의 추출입니다. 우리는 이미 수많은 금융 데이터에 접근할 수 있지만, 그 데이터를 나의 투자 철학에 맞게 해석해 주는 비서는 부족합니다. 최근 Generative AI, 특히 Anthropic의 Claude와 같은 고성능 LLM(Large Language Model)은 긴 문맥을 이해하고 복잡한 질의에 답변할 수 있는 능력을 갖추었습니다.

이러한 배경 하에 탄생한 **firma**는 '로컬 퍼스트(Local First)' 철학을 기반으로 합니다. 클라우드에 민감한 자산 데이터를 올리지 않으면서도, 로컬 환경의 데이터를 LLM에게 안전하게 전달하여 분석하는 하이브리드 아키텍처가 필요했습니다. 이 글에서는 단순한 CLI 도구를 넘어, Finnhub의 실시간 시세 데이터와 Claude의 추론 능력을 결합하여 개인 맞춤형 금융 비서를 구축하는 firma의 기술적 메커니즘과 실제 구현 방법을 심층적으로 분석합니다.

## 본론

### 1. firma의 기술적 아키텍처

firma는 기본적으로 Python 기반의 CLI 어플리케이션으로 설계되었으나, 내부적으로는 RAG(Retrieval-Augmented Generation)의 축소판 형태를 띠고 있습니다. 사용자의 로컬 포트폴리오 정보(Context)가 벡터화되지 않은 텍스트 형태로 프롬프트에 포함되며, Finnhub API로부터 가져온 실시간 시계열 데이터와 결합되어 Claude로 전송됩니다.

이때 가장 중요한 설계 원칙은 'Local First'입니다. 사용자의 보유 종목, 평단가, 매수 날짜 등 민감한 정보는 절대 Claude의 학습 데이터나 서버에 저장되지 않으며, 오직 추론(Inference)을 위한 토큰으로만 일회성 사용됩니다. 이러한 접근 방식은 MLOps 관점에서 데이터 프라이버시(Data Privacy)와 AI 기능의 트레이드오프를 해결하는 현대적인 사례입니다.

#### 시스템 데이터 플로우

아래 다이어그램은 사용자가 터미널에 명령어를 입력했을 때, 데이터가 로컬 저장소에서 외부 API를 거쳐 최종적으로 AI 응답으로 돌아오는 과정을 도식화한 것입니다.

```javascript
graph TD
    A[User CLI Input] --> B[Command Parser]
    B --> C{Command Type}
    C -->|Portfolio Check| D[Local DB/JSON]
    C -->|AI Analysis| D
    D --> E[Context Builder]
    F[Finnhub API] -->|Real-time Market Data| E
    E --> G[Claude API Request]
    G --> H[Claude LLM Inference]
    H --> I[Response Formatter]
    I --> J[Terminal Output]
```

이 아키텍처의 핵심은 **Context Builder** 단계입니다. 여기서 로컬의 정적 데이터(내가 산 종목)와 외부의 동적 데이터(현재 가격)를 하나의 잘 구조화된 프롬프트로 합치는 작업이 이루어집니다.

### 2. 핵심 기능 비교: 기존 스프레드시트 vs. firma

기존의 방식과 비교했을 때, 프로그래머블한 도구인 firma가 갖는 이점은 명확합니다. 단순한 숫자 나열을 넘어, 데이터에 기반한 '상호작용'이 가능하기 때문입니다.

| 비교 항목 | Google Sheets (기존) | firma (CLI + AI) | | :--- | :--- | :--- | | **데이터 소스 갱신** | 수동 입력 또는 느린 `GOOGLEFINANCE` 함수 | API 기반 실시간 요청 (On-demand) | | **인터페이스** | GUI (마우스 클릭, 스크롤 필요) | CLI (키보드 중심, 스크립트 가능) | | **데이터 분석** | 피벗 테이블, 수식 설정 (고난도) | 자연어 질의를 통한 AI 분석 | | **프라이버시** | 클라우드 서버 저장 | 로컬 JSON/YAML 저장 (Local First) | | **확장성** | 애드온 설치 필요 | Python 패키지로 쉬운 확장 가능 |

### 3. 실무 적용 가이드: 구현 및 활용

firma를 실제로 구축한다고 가정하고, Python을 사용하여 Finnhub 데이터를 가져와서 Claude에게 포트폴리오 분석을 요청하는 핵심 로직을 구현해 보겠습니다.

#### 3.1. 환경 설정 및 데이터 수집 (Finnhub)

먼저 Finnhub의 API를 통해 실시간 주식 데이터를 가져와야 합니다. 이는 RAG에서 검색(Retrieval) 단계에 해당합니다.

```python
import os
import requests
import json

def get_current_price(symbol: str) -> float:
    """Finnub API를 사용하여 현재 주식 가격을 조회합니다."""
    api_key = os.getenv("FINNHUB_API_KEY")
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={api_key}"
    
    response = requests.get(url)
    data = response.json()
    
    if data['c'] == 0:
        raise ValueError(f"Invalid data for symbol {symbol}")
        
    return data['c'] # 'c'는 현재 가격(Current price)

# 예시 사용 (TSLA)
try:
    price = get_current_price("TSLA")
    print(f"Current TSLA Price: ${price}")
except Exception as e:
    print(f"Error fetching data: {e}")
```

#### 3.2. Claude API를 활용한 포트폴리오 분석

수집한 데이터와 사용자의 로컬 포트폴리오 데이터를 결합하여 Claude API에 전송합니다. 이때 시스템 프롬프트(System Prompt)를 통해 금융 어드바이저로서의 페르소나를 부여합니다.

```python
import anthropic

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def analyze_portfolio_with_ai(portfolio_data: dict):
    """로컬 포트폴리오 데이터와 시장 데이터를 바탕으로 Claude에게 분석을 요청합니다."""
    
    # 1. 프롬프트 구성
    user_message = f"""
    다음은 나의 현재 주식 포트폴리오 상태입니다:
    {json.dumps(portfolio_data, indent=2)}
    
    현재 시장 상황을 바탕으로, 나의 포트폴리오 리스크를 분석하고 
    향후 3개월간의 리밸런싱 전략에 대해 조언해 주세요.
    """

    # 2. API 호출
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        system="You are an expert financial advisor. Provide concise, data-driven insights.",
        messages=[
            {"role": "user", "content": user_message}
        ]
    )
    
    return message.content[0].text

# 예시 포트폴리오 데이터 (로컬 저장소에서 로드했다고 가정)
my_portfolio = {
    "holdings": [
        {"symbol": "TSLA", "qty": 10, "avg_price": 200.0},
        {"symbol": "AAPL", "qty": 20, "avg_price": 150.0}
    ],
    "total_invested": 5000
}

# 시장 데이터 업데이트 (실제 구현시 비동기 처리 권장)
for stock in my_portfolio['holdings']:
    stock['current_price'] = get_current_price(stock['symbol'])

# AI 분석 실행
insight = analyze_portfolio_with_ai(my_portfolio)
print("-" * 30)
print("AI Analysis Result:")
print(insight)
```

이 코드는 단순히 가격을 보여주는 것을 넘어, 현재 자산 상태(Context)를 LLM에게 완전히 전달하여 나만의 펀드 매니저처럼 행동하게 만드는 원리를 보여줍니다.

### 4. MLOps 관점에서의 고찰: 로컬 퍼스트와 토큰 최적화

firma와 같은 개인용 AI 도구를 개발할 때 가장 큰 난관은 **비용(Cost)**과 **지연(Latency)**입니다. 매번 `firma show` 명령어를 입력할 때마다 전체 포트폴리오 히스토리를 Claude Context Window에 넣는 것은 비효율적입니다.

따라서 실제 구현시에는 다음과 같은 MLOps 전략이 적용되어야 합니다.

1.  **Embedding & Caching**: 과거의 대화 내용이나 분석된 리포트는 벡터 DB에 저장하고, 유사한 질문이 들어오면 LLM 호출 없이 캐싱된 답변을 제공합니다. 2.  **Prompt Compression**: 종목 코드, 수량 등 구조화된 데이터는 JSON이 아닌 더 압축된 포맷으로 변환하여 토큰 사용량을 줄입니다. 3.  **Function Calling**: 단순한 "평가손익 계산"은 LLM이 하지 않고, Python 함수로 처리한 뒤 결과만 LLM에게 보내 텍스트 생성(Generative) 작업에 집중하게 합니다. 이는 토큰 비용을 획기적으로 절감합니다.

## 결론

firma는 단순히 주식 가격을 보여주는 CLI 도구가 아닙니다. **개인화된 데이터(Context)와 확장 가능한 지능(LLM)**을 결합한 초석입니다. 구글 스프레드시트라는 '블랙박스'에서 벗어나, 내 데이터의 소유권을 확보하면서도 최첨단 AI의 분석 능력을 누릴 수 있다는 점은 '로컬 퍼스트' 패러

---

**출처**: [https://news.hada.io/topic?id=28884](https://news.hada.io/topic?id=28884)