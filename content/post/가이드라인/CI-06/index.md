---
title: "[2026 주요정보통신기반시설] CI-06 크로스사이트스크립트(Cross-Site Scripting, XSS)"
slug: "2026-주정통/CI-06"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "웹애플리케이션내 악성 스크립트가 다른 사용자의 브라우저에서 실행되는 취약점 존재 여부 점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Web
---

# 크로스사이트스크립트(Cross-Site Scripting, XSS)

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | CI-06 |
| **점검내용** | 웹애플리케이션내 악성 스크립트가 다른 사용자의 브라우저에서 실행되는 취약점 존재 여부 점검 |
| **점검대상** | 웹 애플리케이션 소스코드, 웹방화벽 |
| **양호기준** | 사용자 입력값에 대해 검증 및 필터링이 이루어져, 악의적인 스크립트가 실행되지 않는 경우 |
| **취약기준** | 사용자 입력값에 대해 검증 및 필터링이 이루어지지 않으며, HTML 코드가 입력 및 실행되는 경우 |
| **조치방법** | 특수문자에 대해 필터링 처리와 출력값 인코딩(HTML 엔티티, 이스케이프 등)을 적용하여 악성 스크립트 실행을 방지하며, 부득이하게 HTML 코드를 사용해야 하는 경우 화이트리스트 방식을 적용해 허용된 HTML 코드만 처리하도록 설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 사용자 입력값에 대해 검증 및 필터링이 이루어져, 악의적인 스크립트가 실행되지 않는 경우
- **취약**: 사용자 입력값에 대해 검증 및 필터링이 이루어지지 않으며, HTML 코드가 입력 및 실행되는 경우

#### 경계 케이스 (Edge Case) 처리 방법
- 일반적인 경우 영향 없음
- HTML 에디터 등 정상적인 HTML 사용이 필요한 기능은 화이트리스트 방식 적용

#### 권장 설정값
- 일반적인 텍스트 영역: HTML Entity 인코딩 필수 적용
- HTML 에디터 영역: 화이트리스트 기반의 HTML Sanitizer 사용
- 쿠키: HttpOnly, Secure, SameSite 속성 적용

### 2. 점검 방법

#### Step 1: 저장형 XSS 테스트
```
사용자 입력값을 전달받아 HTML 상에 렌더링되는 애플리케이션(게시판, 검색 등)에 스크립트 구문 삽입 후 실행되는지 확인
```

**테스트 패턴:**
```html
<script>alert('XSS')</script>
<img src=x onerror=alert('XSS')>
<svg onload=alert('XSS')>
<body onload=alert('XSS')>
```

#### Step 2: 반사형 XSS 테스트
```
입력값이 HTML 상에 렌더링되어 스크립트가 삽입된 URL 접근 시 스크립트가 동작하는지 확인
```

**테스트 URL:**
```
https://example.com/search?q=<script>alert('XSS')</script>
https://example.com/error?msg=<img src=x onerror=alert('XSS')>
```

### 3. 조치 방법

#### 1. HTML Entity 인코딩 (가장 권장)

**Java 예시:**
```java
public static String sanitizeInput(String input) {
    if (input == null) return null;
    return input.replaceAll("&", "&amp;")
                 .replaceAll("<", "&lt;")
                 .replaceAll(">", "&gt;")
                 .replaceAll("\"", "&quot;")
                 .replaceAll("'", "&#39;");
}
```

**ASP.NET 예시:**
```csharp
public static string EscapeHtml(string input) {
    StringBuilder sb = new StringBuilder();
    foreach (char c in input) {
        switch (c) {
            case '<': sb.Append("&lt;"); break;
            case '>': sb.Append("&gt;"); break;
            case '"': sb.Append("&quot;"); break;
            case '\'': sb.Append("&#39;"); break;
            case '&': sb.Append("&amp;"); break;
            default: sb.Append(c); break;
        }
    }
    return sb.ToString();
}
```

**PHP 예시:**
```php
function escapeHtml($input) {
    return htmlspecialchars($input, ENT_QUOTES | ENT_HTML5, 'UTF-8', false);
}
```

#### 2. Content Security Policy (CSP) 적용

**HTTP 헤더 설정:**
```http
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; object-src 'none'; base-uri 'self';
```

**HTML 메타 태그:**
```html
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'">
```

#### 3. 쿠키 보안 설정

```java
// HttpOnly, Secure, SameSite 속성 적용
Cookie cookie = new Cookie("sessionId", sessionId);
cookie.setHttpOnly(true);  // JavaScript에서 쿠키 접근 차단
cookie.setSecure(true);     // HTTPS에서만 전송
cookie.setPath("/");
```

#### 4. 화이트리스트 방식 적용

부득이하게 HTML을 사용해야 하는 경우:
```java
// JSoup 라이브러리 사용
Whitelist whitelist = Whitelist.simpleText();
String clean = Jsoup.clean(userInput, whitelist);
```

#### 5. 웹 방화벽 룰셋 적용
- 웹 태그 및 스크립트 관련 특수문자 필터링 룰셋 적용
- XSS 공격 패턴 탐지 및 차단

### 4. 참고 자료

**HTML Entity 인코딩 예시:**

| 구분 | 필터링 전 | 필터링 후 |
|------|----------|----------|
| < | `<` | `&lt;` |
| > | `>` | `&gt;` |
| " | `"` | `&quot;` |
| ( | `(` | `&#40;` |
| ) | `)` | `&#41;` |

**XSS 공격 벡터:**
1. **저장형 XSS**: 악성 스크립트가 서버에 저장되어 다른 사용자에게 전달
2. **반사형 XSS**: 악성 스크립트가 URL 파라미터 등을 통해 즉시 반영
3. **DOM 기반 XSS**: 클라이언트 사이드 JavaScript에서 DOM 조작으로 스크립트 실행

**OWASP XSS Prevention Cheat Sheet:**
1. HTML Escape 신뢰할 수 없는 데이터
2. Attribute Escape 신뢰할 수 없는 데이터
3. JavaScript Escape 신뢰할 수 없는 데이터
4. CSS Escape 신뢰할 수 없는 데이터
5. URL Escape 신뢰할 수 없는 데이터

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.