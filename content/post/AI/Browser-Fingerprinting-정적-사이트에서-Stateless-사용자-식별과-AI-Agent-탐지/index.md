---
title: "Browser Fingerprinting: 정적 사이트에서 Stateless 사용자 식별과 AI Agent 탐지"
date: 2026-04-07T01:04:53+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
---

## 서론

개인 블로그에 방문하는 사용자를 분석하고 싶다면 어떻게 해야 할까? 가장 쉬운 방법은 Google Analytics를 설치하는 것이다. 하지만 GDPR, CCPA 같은 개인정보보호 규제가 강화되면서, 쿠키 기반 추적은 점점 더 제한받고 있다. 실제로 2024년 Chrome의 Third-party Cookie 폐지 논의와 Safari의 ITP(Intelligent Tracking Prevention)는 웹 추적의 패러다임을 바꾸고 있다.

더 흥미로운 문제가 있다. 바로 **AI Agent의 등장**이다. ChatGPT, Claude, Perplexity 같은 AI 서비스들이 웹사이트를 크롤링하고 요약해서 보여주는 일이 빈번해졌다. 내 블로그 트래픽 중 얼마나 많은 비중이 실제 인간이고, 얼마나 AI Agent일까? 이 질문에 답하기 위해서는 로그인 없이, 쿠키 없이, 서버 상태 없이 사용자를 식별할 수 있는 방법이 필요하다.

바로 **Browser Fingerprinting**이라는 기술이다. 이 기술은 브라우저의 고유한 특성들을 조합해 마치 지문처럼 사용자를 식별한다. 서버리스 환경인 정적 사이트에서도 완벽하게 작동하며, 프라이버시 친화적인 접근법이다. 이 글에서는 이 기술의 원리와 구현 방법, 그리고 AI Agent 탐지에 대한 고민까지 깊이 있게 다뤄보겠다.

## 본론

### Browser Fingerprinting이란?

Browser Fingerprinting은 사용자의 브라우저와 디바이스가 가진 고유한 특성들을 수집해 이를 조합, 하나의 식별자를 생성하는 기술이다. 2010년 EFF(Electronic Frontier Foundation)의 연구에서 처음 체계적으로 제시되었으며, 당시 연구에서 **83.6%의 브라우저가 고유하게 식별 가능**하다는 결과를 보여줬다[^1].

```javascript
graph TD
    A[사용자 접속] --> B[Browser 특성 수집]
    B --> C[User Agent]
    B --> D[Screen Resolution]
    B --> E[Canvas Fingerprint]
    B --> F[WebGL Info]
    B --> G[Audio Context]
    B --> H[Timezone/Language]
    C --> I[Hash 함수]
    D --> I
    E --> I
    F --> I
    G --> I
    H --> I
    I --> J[Pseudo Identity 생성]
```

핵심 아이디어는 간단하다. 어떤 사용자가 Chrome 브라우저를 사용하고, 해상도가 1920x1080이며, 한국어 설정, 특정 GPU를 사용한다면, 이 조합은 매우 희귀할 확률이 높다. 이를 하나의 해시값으로 변환하면 **Stateless Pseudo Identity**가 탄생한다.

### 수집 가능한 Fingerprint 속성들

현대 브라우저에서 수집할 수 있는 주요 속성들은 다음과 같다:

| 속성 카테고리 | 수집 데이터 | 식별력 (Entropy) | | :--- | :--- | :--- | | Navigator | User Agent, Platform, Language | 중간 | | Screen | Resolution, Color Depth, Pixel Ratio | 높음 | | Canvas | 2D 렌더링 차이 | 매우 높음 | | WebGL | GPU Vendor, Renderer, Extensions | 매우 높음 | | Audio | AudioContext 샘플링 차이 | 높음 | | Fonts | 설치된 폰트 목록 | 높음 | | Timezone | Offset, TimeZone 이름 | 낮음 | | Hardware | CPU 코어 수, Memory | 중간 |

Canvas Fingerprinting이 특히 흥미로운데, 동일한 이미지를 그려도 GPU와 드라이버에 따라 픽셀 단위의 미세한 차이가 발생한다. 이는 하드웨어 수준의 식별을 가능하게 한다.

### 실제 구현: FingerprintJS 기반 식별자 생성

오픈소스 라이브러리인 FingerprintJS를 활용해 실제 구현해보자. 정적 사이트에서도 완벽하게 작동한다.

```javascript
// fingerprint.js - 정적 사이트용 Stateless Identity 생성기

import FingerprintJS from '@fingerprintjs/fingerprintjs';

class StatelessIdentity {
  constructor() {
    this.fpPromise = FingerprintJS.load();
    this.visitorId = null;
    this.extendedData = {};
  }

  async generateIdentity() {
    const fp = await this.fpPromise;
    const result = await fp.get();
    
    // 기본 visitor ID
    this.visitorId = result.visitorId;
    
    // 확장 데이터 수집 (AI Agent 탐지용)
    this.extendedData = {
      // 기본 fingerprint
      visitorId: result.visitorId,
      confidence: result.confidence,
      
      // 추가 수집 데이터
      userAgent: navigator.userAgent,
      language: navigator.language,
      languages: navigator.languages,
      platform: navigator.platform,
      hardwareConcurrency: navigator.hardwareConcurrency,
      deviceMemory: navigator.deviceMemory,
      
      // 화면 정보
      screenWidth: screen.width,
      screenHeight: screen.height,
      colorDepth: screen.colorDepth,
      pixelRatio: window.devicePixelRatio,
      
      // 타임존
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      timezoneOffset: new Date().getTimezoneOffset(),
      
      // 터치 지원 여부
      touchSupport: 'ontouchstart' in window,
      
      // 세션 타이밍 (AI Agent 의심 탐지)
      timestamp: Date.now(),
      pageLoadTime: performance.timing.loadEventEnd - performance.timing.navigationStart,
    };
    
    // AI Agent 의심 점수 계산
    this.extendedData.agentScore = this.calculateAgentScore();
    
    return this.extendedData;
  }

  calculateAgentScore() {
    let score = 0;
    const data = this.extendedData;
    
    // 1. Headless Chrome 탐지
    if (/HeadlessChrome/i.test(data.userAgent)) score += 50;
    
    // 2. 불가능한 하드웨어 조합
    if (data.hardwareConcurrency === 0 || data.deviceMemory === 0) score += 30;
    
    // 3. 너무 빠른 페이지 로딩 (봇 의심)
    if (data.pageLoadTime < 100) score += 20;
```

```javascript

    
    // 4. 일관된 User Agent 패턴 (AI 서비스)
    const aiPatterns = [
      /ChatGPT/i, /Claude/i, /Perplexity/i, 
      /Anthropic/i, /OpenAI/i, /Googlebot/i
    ];
    aiPatterns.forEach(pattern => {
      if (pattern.test(data.userAgent)) score += 40;
    });
    
    // 5. Languages 배열 이상 (봇은 종종 비어있음)
    if (!data.languages || data.languages.length === 0) score += 15;
    
    return Math.min(score, 100);
  }

  // 식별자를 localStorage에 저장하지 않고 매번 재계산
  // (Stateless 원칙 준수)
  getIdentity() {
    return {
      id: this.visitorId,
      isLikelyAgent: this.extendedData.agentScore > 50,
      agentScore: this.extendedData.agentScore,
      raw: this.extendedData
    };
  }
}

// 사용 예시
const identity = new StatelessIdentity();
identity.generateIdentity().then(() => {
  const result = identity.getIdentity();
  console.log('Visitor ID:', result.id);
  console.log('Agent Score:', result.agentScore);
  console.log('Is AI Agent:', result.isLikelyAgent);
  
  // Analytics 서버로 전송 (서버리스 함수 또는 외부 서비스)
  sendToAnalytics(result);
});

async function sendToAnalytics(data) {
  // 서버리스 함수로 전송하거나, 직접 분석 플랫폼 API 호출
  await fetch('https://analytics.example.com/collect', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      eventId: crypto.randomUUID(),
      ...data,
      url: window.location.href,
      referrer: document.referrer
    })
  });
}
```

### Step-by-Step: 정적 사이트에 적용하기

```javascript
graph LR
    A[1. 라이브러리 설치] --> B[2. Fingerprint 모듈 작성]
    B --> C[3. AI Agent 탐지 로직 추가]
    C --> D[4. Analytics 엔드포인트 구성]
    D --> E[5. 데이터 시각화]
```

**Step 1: 프로젝트 설정**

```bash
# 프로젝트 초기화
npm init -y

# FingerprintJS 설치
npm install @fingerprintjs/fingerprintjs

# 번들러 설치 (Vite 추천)
npm install -D vite
```

**Step 2: 정적 사이트에 삽입**

```html
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>Static Site with Fingerprinting</title>
</head>
<body>
  <script type="module" src="/fingerprint.js"></script>
</body>
</html>
```

**Step 3: 서버리스 Analytics 수집 (Vercel/Netlify Functions)**

```python
# api/collect.py - Vercel Serverless Function
import json
import hashlib
from datetime import datetime
from http import HTTPStatus

# 간단한 in-memory 저장소 (실제로는 DynamoDB, KV 등 사용)
# Cloudflare KV, Vercel KV, Supabase 등 추천

def handler(request):
    if request.method != 'POST':
        return {'statusCode': HTTPStatus.METHOD_NOT_ALLOWED}
    
    body = json.loads(request.body)
    
    # Pseudo Identity 해시화 (프라이버시 보호)
    raw_id = body.get('id', '')
    hashed_id = hashlib.sha256(raw_id.encode()).hexdigest()[:16]
    
    # 이벤트 로그 생성
    event = {
        'visitor_hash': hashed_id,
        'agent_score': body.get('agentScore', 0),
        'is_agent': body.get('isLikelyAgent', False),
        'url': body.get('url', ''),
        'referrer': body.get('referrer', ''),
        'timestamp': datetime.utcnow().isoformat(),
        'user_agent': body.get('raw', {}).get('userAgent', '')
    }
    
    # 여기서 실제 DB에 저장
    print(f"[Analytics] {json.dumps(event)}")
    
    return {
        'statusCode': HTTPStatus.OK,
        'body': json.dumps({'status': 'recorded'})
    }
```

### AI Agent 탐지: 현재 기술의 한계와 가능성

최근 arXiv에 발표된 "Detecting AI-Generated Text in Academic Writing" 논문[^2]에서는 AI 생성 텍스트 탐지가 얼마나 어려운지 보여준다. 웹 트래픽에서 AI Agent를 탐지하는 것도 마찬가지로 도전적이다.

**현재 탐지 방법의 한계:**

| 방법 | 원리 | 한계점 | | :--- | :--- | :--- | | User Agent 검사 | 특정 문자열 탐지 | 쉽게 스푸핑 가능 | | Behavioral Analysis | 마우스/키보드 패턴 | Headless 모드에서 무력화 | | CAPTCHA | 인간 상호작용 검증 | 사용자 경험 저하 | | Request Rate Limiting | 요청 빈도 제한 | 정상 사용자도 차단 가능 | | TLS Fingerprinting | TLS 핸드셰이크 패턴 | 프록시/VPN 우회 가능 |

필자의 실험적 접근법은 **다층적 신호 결합(Multi-signal Fusion)**이다. Fingerprint, 행동 패턴, 요청 특성을 종합해 확률적 점수를 계산한다. ML 모델을 학습시켜 분류할 수도 있지만, 정적 사이트에서는 경량화된 휴리스틱이 더 실용적이다.

```javascript
// 고급 AI Agent 탐지 - 행동 패턴 분석
class AgentBehaviorAnalyzer {
  constructor() {
    this.mouseMovements = [];
    this.scrollEvents = [];
    this.clickEvents = [];
    this.startTime = Date.now();
  }

  track() {
    // 마우스 움직임 추적
    document.addEventListener('mousemove', (e) => {
      this.mouseMovements.push({
        x: e.clientX,
        y: e.clientY,
        t: Date.now() - this.startTime
      });
      // 최근 100개만 유지
      if (this.mouseMovements.length > 100) {
        this.mouseMovements.shift();
      }
    });

    // 스크롤 패턴
    document.addEventListener('scroll', () => {
      this.scrollEvents.push({
        y: window.scrollY,
        t: Date.now() - this.startTime
      });
    });

    // 클릭 패턴
    document.addEventListener('click', (e) => {
      this.clickEvents.push({
        x: e.clientX,
        y: e.clientY,
        target: e.target.tagName,
        t: Date.now() - this.startTime
      });
    });
  }

  analyze() {
    const score = {
      mouseNaturalness: this.analyzeMouseNaturalness(),
      scrollPattern: this.analyzeScrollPattern(),
      interactionRate: this.analyzeInteractionRate(),
      overall: 0
    };

    score.overall = (score.mouseNaturalness + score.scrollPattern + score.interactionRate) / 3;
    return score;
  }

  analyzeMouseNaturalness() {
    // 인간의 마우스 움직임은 베지에 곡선을 따름
    // 봇은 직선 이동이 많음
    if (this.mouseMovements.length < 10) return 50; // 데이터 부족

    let linearCount = 0;
    for (let i = 2; i < this.mouseMovements.length; i++) {
      const p0 = this.mouseMovements[i - 2];
      const p1 = this.mouseMovements[i - 1];
      const p2 = this.mouseMovements[i];

      // 직선성 체크
      const d1 = Math.sqrt((p1.x - p0.x) ** 2 + (p1.y - p0.y) ** 2);
      const d2 = Math.sqrt((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2);
      const d3 = Math.sqrt((p2.x - p0.x) ** 2 + (p2.y - p0.y) ** 2);

      if (Math.abs(d1 + d2 - d3) < 5) linearCount++;
    }

```

```javascript
    const linearityRatio = linearCount / (this.mouseMovements.length - 2);
    // 직선 비율이 높으면 봇일 확률 높음
    return Math.max(0, 100 - linearityRatio * 100);
  }

  analyzeScrollPattern() {
```

---

**출처**: [https://news.hada.io/topic?id=28226](https://news.hada.io/topic?id=28226)