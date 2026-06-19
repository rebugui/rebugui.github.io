---
title: "Spring AI Playground: MCP 툴 작성부터 테스트, 외부 연동까지"
date: 2026-04-11T01:00:39+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
draft: true
---

## 서론

"Claude Code로 MCP 툴을 하나 만들었는데... 이걸 어떻게 테스트하지?"

최근 AI 에이전트 개발 커뮤니티에서 가장 흔히 들리는 질문이다. Claude Code나 Cursor 같은 코딩 에이전트의 도움으로 Model Context Protocol(MCP) 툴 코드는 순식간에 작성할 수 있게 되었지만, 막상 그 코드가 **제대로 동작하는지 검증**하는 일은 여전히 고통스러운 과정이다. 로컬 환경을 설정하고, 의존성을 맞추고, 실제 MCP 클라이언트와 연동해서 테스트하고... 이 모든 과정을 거쳐야 "아, 이 툴이 작동하는구나"를 확인할 수 있다.

이 문제는 단순히 "불편하다"를 넘어선다. **MCP 생태계의 확장을 가로막는 병목**이다. 툴 개발자가 빠르게 프로토타입을 만들고 검증할 수 없으면, MCP 기반 AI 에이전트가 사용할 수 있는 도구의 다양성과 품질 모두 제한된다. 이는 곧 에이전트의 능력 한계로 이어진다.

Spring AI Playground는 이 지점을 정확히 공략한다. MCP 툴 코드를 브라우저에서 즉시 작성하고, 원클릭으로 테스트하며, 외부 시스템과의 연동까지 하나의 데스크톱 앱에서 해결한다. 복잡한 환경 설정 없이 **아이디어에서 실행 가능한 툴까지의 거리를 최소화**하는 것이다.

## MCP(Model Context Protocol): 빠른 기술 복습

본격적인 논의에 앞서 MCP의 핵심 아키텍처를 간단히 짚고 넘어가자. MCP는 Anthropic이 2024년 11월에 발표한 오픈 프로토콜로, LLM이 외부 도구 및 데이터 소스와 상호작용할 수 있도록 표준화된 인터페이스를 제공한다.

```javascript
graph LR
    A[MCP Host] --> B[MCP Client]
    B --> C[MCP Server]
    C --> D[Local Resource]
    C --> E[External API]
    C --> F[Database]
```

핵심 구성 요소는 세 가지다:
- **MCP Host**: Claude Desktop, IDE, AI 에이전트 등 MCP 클라이언트를 호스팅하는 애플리케이션
- **MCP Client**: 서버와 1:1 연결을 유지하며 프로토콜을 처리
- **MCP Server**: 실제 툴(tools), 리소스(resources), 프롬프트(prompts)를 노출하는 서비스

툴 개발자가 집중해야 할 영역은 바로 **MCP Server**다. 이 서버가 제공하는 툴의 스펙(input schema, output format)을 정의하고, 실제 비즈니스 로직을 구현하면 된다.

## Spring AI Playground 아키텍처

Spring AI Playground가 이 생태계에서 차지하는 위치를 이해하는 것이 중요하다. 이 도구는 단순한 코드 에디터가 아니라 **MCP 툴 개발의 전체 라이프사이클을 지원하는 통합 환경**이다.

```javascript
graph TD
    A[Spring AI Playground] --> B[Code Editor]
    A --> C[Test Runner]
    A --> D[MCP Client Emulator]
    B --> E[Tool Definition]
    B --> F[Business Logic]
    C --> G[Unit Tests]
    C --> H[Integration Tests]
    D --> I[Schema Validation]
    D --> J[Execution Result]
```

핵심 기능을 표로 정리하면 다음과 같다:

| 기능 영역 | 세부 기능 | 기존 방식과의 차이 |
| :--- | :--- | :--- |
| 코드 작성 | 내장 에디터 + 자동완성 | 별도 IDE 설정 불필요 |
| 스키마 정의 | JSON Schema 기반 툴 스펙 | 수동 JSON 편집 최소화 |
| 즉시 테스트 | 원클릭 실행 및 결과 확인 | MCP 클라이언트 수동 연동 필요 |
| 외부 연동 | API, DB 연결 설정 UI | 코드로 환경변수 관리 |
| 디버깅 | 실행 로그 및 에러 추적 | 별도 로깅 설정 필요 |

## MCP 툴 개발 실전 가이드

### Step 1: 툴 정의하기

MCP 툴의 핵심은 **명확한 스펙 정의**다. LLM이 이 툴을 언제, 어떻게 사용할지 결정하려면 툴의 이름, 설명, 입력 파라미터가 정확하게 정의되어야 한다.

```java
// Spring AI 기반 MCP 툴 정의 예시
@Configuration
public class WeatherToolConfig {
    
    @Bean
    @Description("지정된 도시의 현재 날씨 정보를 조회합니다. 온도는 섭씨로 반환됩니다.")
    public Function<WeatherRequest, WeatherResponse> currentWeather() {
        return request -> {
            // 실제 API 호출 로직
            WeatherApiResponse apiResponse = weatherClient
                .getWeather(request.city(), request.unit());
            
            return new WeatherResponse(
                request.city(),
                apiResponse.temperature(),
                apiResponse.humidity(),
                apiResponse.description(),
                LocalDateTime.now()
            );
        };
    }
    
    public record WeatherRequest(
        @Description("조회할 도시 이름 (영문)") String city,
        @Description("온도 단위 (Celsius 또는 Fahrenheit)") String unit
    ) {}
    
    public record WeatherResponse(
        String city,
        double temperature,
        int humidity,
        String description,
        LocalDateTime timestamp
    ) {}
}
```

이 코드에서 주목할 점은 `@Description` 어노테이션의 활용이다. 이 설명은 LLM이 툴을 선택할 때 참고하는 핵심 정보다. "날씨 조회"보다 "지정된 도시의 현재 날씨 정보를 조회합니다"가 훨씬 명확하다.

### Step 2: 입력 스키마 설계

LLM이 툴을 올바르게 호출하려면 입력 파라미터의 스키마가 명확해야 한다. JSON Schema 표준을 따르며, Spring AI Playground에서는 이를 시각적으로 편집할 수 있다.

```json
{
  "type": "object",
  "properties": {
    "city": {
      "type": "string",
      "description": "조회할 도시 이름 (영문, 예: Seoul, Tokyo, New York)"
    },
    "unit": {
      "type": "string",
      "enum": ["Celsius", "Fahrenheit"],
      "default": "Celsius",
      "description": "온도 표시 단위"
    }
  },
  "required": ["city"]
}
```

### Step 3: 비즈니스 로직 구현 및 외부 API 연동

실제 툴의 핵심 로직이다. 외부 API 호출이 필요한 경우, Spring AI Playground의 연동 설정을 활용할 수 있다.

```java
@Service
public class WeatherService {
    
    private final WebClient webClient;
    private final String apiKey;
    
    public WeatherService(
        @Value("${weather.api.key}") String apiKey,
        @Value("${weather.api.base-url}") String baseUrl
    ) {
        this.apiKey = apiKey;
        this.webClient = WebClient.builder()
            .baseUrl(baseUrl)
            .defaultHeader("Accept", "application/json")
            .build();
    }
    
    public WeatherData fetchWeather(String city, String unit) {
        try {
            return webClient.get()
                .uri(uriBuilder -> uriBuilder
                    .path("/weather")
                    .queryParam("q", city)
                    .queryParam("units", unit.equals("Celsius") ? "metric" : "imperial")
                    .queryParam("appid", apiKey)
                    .build())
                .retrieve()
                .bodyToMono(WeatherData.class)
                .block(Duration.ofSeconds(10));
        } catch (WebClientRequestException e) {
            throw new ToolExecutionException(
                "날씨 API 호출 실패: " + e.getMessage(), e
            );
        }
    }
}
```

### Step 4: Spring AI Playground에서 테스트

코드 작성이 끝나면 Playground에서 즉시 테스트할 수 있다. 핵심 테스트 시나리오는 다음과 같다:

```java
// 테스트 케이스 예시
@Test
void testWeatherTool_ValidCity() {
    WeatherRequest request = new WeatherRequest("Seoul", "Celsius");
    WeatherResponse response = currentWeather.apply(request);
    
    assertNotNull(response);
    assertEquals("Seoul", response.city());
    assertTrue(response.temperature() > -50 && response.temperature() < 60);
    assertNotNull(response.description());
}

@Test
void testWeatherTool_InvalidCity() {
    WeatherRequest request = new WeatherRequest("NonExistentCity123", "Celsius");
    
    assertThrows(ToolExecutionException.class, () -> {
        currentWeather.apply(request);
    });
}

@Test
void testWeatherTool_FahrenheitUnit() {
    WeatherRequest request = new WeatherRequest("New York", "Fahrenheit");
    WeatherResponse response = currentWeather.apply(request);
    
    assertNotNull(response);
    // 화씨 온도 범위 검증
    assertTrue(response.temperature() > -60 && response.temperature() < 140);
}
```

### Step 5: MCP 클라이언트와 연동 검증

툴이 개별 테스트를 통과했다면, 실제 MCP 프로토콜을 통해 클라이언트와 연동되는지 확인해야 한다. Spring AI Playground는 **내장 MCP 클라이언트 에뮬레이터**를 제공하여, 별도의 Claude Desktop이나 다른 호스트 애플리케이션 없이도 end-to-end 테스트가 가능하다.

```javascript
graph LR
    A[Playground MCP Emulator] --> B[JSON-RPC Request]
    B --> C[MCP Server]
    C --> D[Tool Execution]
    D --> E[JSON-RPC Response]
    E --> A
```

에뮬레이터가 보내는 실제 MCP 요청은 다음과 같은 형태다:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "currentWeather",
    "arguments": {
      "city": "Seoul",
      "unit": "Celsius"
    }
  }
}
```

## 기존 개발 방식과의 비교

Spring AI Playground가 가져오는 개발 효율성 개선을 정량적으로 비교해보자.

| 개발 단계 | 기존 수동 방식 | Spring AI Playground | 개선 효과 |
| :--- | :--- | :--- | :--- |
| 프로젝트 설정 | 30-60분 (의존성, 설정) | 즉시 시작 | 설정 시간 제로 |
| 툴 코드 작성 | IDE + 문서 참조 | 내장 에디터 + 가이드 | 컨텍스트 스위칭 감소 |
| 단위 테스트 | 테스트 코드 작성 후 실행 | 원클릭 즉시 실행 | 피드백 루프 단축 |
| MCP 연동 테스트 | Claude Desktop 설정 + 재시작 | 내장 에뮬레이터 | 외부 의존성 제거 |
| 외부 API 연동 | 환경변수/설정 파일 관리 | UI 기반 설정 | 설정 오류 감소 |
| 디버깅 | 로그 파일 확인 | 실시간 로그 뷰어 | 디버깅 시간 단축 |

## 실무 적용 시 고려사항

### 프로덕션 배포 준비

Playground에서 검증된 툴을 실제 프로덕션 환경에 배포할 때는 몇 가지 추가 고려사항이 있다:

1. **에러 핸들링 강화**: 개발 중에는 단순한 예외 처리로 충분하지만, 프로덕션에서는 재시도 로직, 서킷 브레이커, 타임아웃 설정이 필요하다.

2. **인증 및 권한 관리**: 외부 API 호출 시 API 키 관리, OAuth 토큰 갱신 등 보안 요구사항을 처리해야 한다.

3. **성능 최적화**: 응답 시간, 메모리 사용량, 동시 요청 처리 능력을 모니터링하고 최적화한다.

4. **로깅 및 모니터링**: 툴 사용 패턴, 성공/실패율, 응답 시간 분포를 추적하는 체계가 필요하다.

### 다중 툴 오케스트레이션

실제 AI 에이전트는 단일 툴이 아닌 여러 툴을 조합해서 사용한다. Spring AI Playground에서도 이러한 시나리오를 테스트할 수 있다:

```java
@Configuration
public class TravelPlanningTools {
    
    @Bean
    @Description("특정 도시의 날씨를 조회합니다.")
    public Function<WeatherRequest, WeatherResponse> getWeather() { ... }
    
    @Bean
    @Description("두 도시 간의 항공편 정보를 조회합니다.")
    public Function<FlightRequest, FlightResponse> searchFlights() { ... }
    
    @Bean
    @Description("특정 도시의 호텔을 검색합니다.")
    public Function<HotelRequest, HotelResponse> searchHotels() { ... }
}
```

이렇게 구성된 툴셋을 Claude나 다른 LLM이 조합해서 사용할 때, 툴 간의 데이터 흐름과 의존성이 올바르게 처리되는지 Playground에서 종합적으로 테스트할 수 있다.

## MCP 생태계의 현재와 미래

2025년 현재 MCP 생태계는 급격히 확장하고 있다. Anthropic의 공식 MCP 서버 저장소에는 파일 시스템, GitHub, PostgreSQL, Slack 등 다양한 서버 구현체가 등록되어 있으며, 커뮤니티 기여도 활발하다.

Spring AI Playground와 같은 개발 도구의 등장은 MCP 생태계가 **초기 실험 단계를 넘어 실용적 성숙기**로 진입하고 있음을 시사한다. 개발자가 툴을 쉽게 만들고 테스트할수록, 에이전트가 활용할 수 있는 능력의 범위도 넓어진다. 이는 L

---

**출처**: [https://news.hada.io/topic?id=28355](https://news.hada.io/topic?id=28355)