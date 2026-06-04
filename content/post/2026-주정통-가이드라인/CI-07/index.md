---
title: "[2026 주요정보통신기반시설] CI-07 크로스사이트요청위조(Cross-Site Request Forgery, CSRF)"
slug: "2026-주정통/CI-07"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "웹애플리케이션내 사용자의 인증 세션을 악용하여 의도하지 않은 위조 요청 가능 여부 점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Web
---

# 크로스사이트요청위조(Cross-Site Request Forgery, CSRF)

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | CI-07 |
| **점검내용** | 웹애플리케이션내 사용자의 인증 세션을 악용하여 의도하지 않은 위조 요청 가능 여부 점검 |
| **점검대상** | 웹 애플리케이션 소스코드, 웹방화벽 |
| **양호기준** | 중요한 요청(비밀번호 변경, 송금 등)에 대해 CSRF 방어 토큰이 적용되어 있으며, 토큰 검증이 정상적으로 수행되는 경우 |
| **취약기준** | 중요한 요청에 대해 CSRF 토큰이 없거나, 토큰 검증을 수행하지 않아 인증된 사용자의 요청 위조가 가능한 경우 |
| **조치방법** | 중요한 요청에는 CSRF 방어 토큰을 포함하고, 서버측에서 해당 토큰의 유효성을 검증하도록 설정하며, Referer/Origin 헤더 검증 및 SameSite 쿠키 옵션을 활용하여 불필요한 외부 도메인 요청이 차단되도록 구성 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 중요한 요청(비밀번호 변경, 송금 등)에 대해 CSRF 방어 토큰이 적용되어 있으며, 토큰 검증이 정상적으로 수행되는 경우
- **취약**: 중요한 요청에 대해 CSRF 토큰이 없거나, 토큰 검증을 수행하지 않아 인증된 사용자의 요청 위조가 가능한 경우

#### 경계 케이스 (Edge Case) 처리 방법
- 일반적인 경우 영향 없음
- AJAX 요청 시에는 요청 헤더에 토큰 포함 필요
- 여러 탭/브라우저에서의 사용성 고려

#### 권장 설정값
- CSRF Token: 예측 불가능한 난수 생성 (SecureRandom 사용)
- SameSite: Lax 또는 Strict 설정
- 토큰 유효기간: 세션 만료와 동일하게 설정

### 2. 점검 방법

#### Step 1: CSRF 토큰 유무 확인
```
중요한 요청(게시글 등록, 비밀번호 변경 등)에 CSRF 토큰이 포함되어 있는지 확인
```

**확인 방법:**
```html
<!-- 양호한 예시 -->
<form action="/transfer" method="POST">
  <input type="hidden" name="csrf_token" value="abc123xyz456">
  <!-- ... -->
</form>
```

#### Step 2: 토큰 검증 로직 확인
```
CSRF 토큰이 없거나 위조된 요청이 차단되는지 확인
```

### 3. 조치 방법

#### 1. CSRF 토큰 구현

**토큰 생성 예시 (Java):**
```java
// CSRF 토큰 생성
private String generateCsrfToken() {
    SecureRandom secureRandom = new SecureRandom();
    byte[] token = new byte[16];
    secureRandom.nextBytes(token);
    return Base64.getUrlEncoder().encodeToString(token);
}

// 세션에 토큰 저장
HttpSession session = request.getSession();
String csrfToken = generateCsrfToken();
session.setAttribute("csrfToken", csrfToken);
```

**토큰 검증 예시 (Java):**
```java
@PostMapping("/submit")
public String submit(@RequestParam String input,
                     @RequestParam String csrfToken,
                     HttpSession session) {
    String sessionToken = (String) session.getAttribute("csrfToken");

    if (sessionToken == null || !sessionToken.equals(csrfToken)) {
        throw new IllegalStateException("Invalid CSRF token");
    }

    // 정상 처리
    return "success";
}
```

**HTML 폼에 토큰 포함:**
```html
<form action="/submit" method="post">
    <input type="hidden" name="csrfToken" th:value="${csrfToken}" />
    <label for="input">Enter text:</label>
    <input type="text" id="input" name="input">
    <button type="submit">Submit</button>
</form>
```

#### 2. SameSite 쿠키 속성 적용

```java
// 쿠키 생성 시 SameSite 속성 설정
String header = String.format(
    "%s=%s; Max-Age=%d; Path=/; HttpOnly; Secure; SameSite=Strict",
    name, value, maxAge
);
response.addHeader("Set-Cookie", header);
```

**SameSite 옵션:**
- **Strict**: 동일 사이트 요청에만 쿠키 전송 (가장 보안성 높음)
- **Lax**: 일부 교차 사이트 탐색 요청에 쿠키 전송 (권장)
- **None**: 모든 요청에 쿠키 전송 (취약함)

#### 3. Referer/Origin 헤더 검증

```java
@PostMapping("/transfer")
public String transfer(HttpServletRequest request) {
    String referer = request.getHeader("Referer");
    String origin = request.getHeader("Origin");

    // 허용된 도메인인지 검증
    if (!isValidOrigin(referer) || !isValidOrigin(origin)) {
        throw new SecurityException("Invalid origin");
    }

    // 처리 로직
    return "success";
}

private boolean isValidOrigin(String origin) {
    if (origin == null) return false;
    return origin.startsWith("https://example.com");
}
```

#### 4. 사용자 재인증

중요 작업 전 추가 인증 요구:
```java
// 비밀번호 변경 시 현재 비밀번호 입력 요구
// 대규모 이체 시 OTP 인증 요구
// 관리자 권한 변경시 재인증 요구
```

#### 5. Spring Security 설정

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf
                .csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse())
            )
            .sessionManagement(session -> session
                .sessionFixation().migrateSession()
            );
        return http.build();
    }
}
```

### 4. 참고 자료

**CSRF 방어 계층:**

1. **CSRF Token** (가장 효과적)
   - 서버에서 생성한 예측 불가능한 토큰
   - 모든 상태 변경 요청에 포함

2. **SameSite Cookie**
   - 쿠키의 전송 범위 제한
   - 최신 브라우저에서 지원

3. **Referer/Origin 검증**
   - 요청 출처 확인
   - 우회 가능성 있으므로 보조 수단

4. **사용자 재인증**
   - 중요 작업 전 비밀번호 재입력
   - OTP 추가 인증

**OWASP CSRF Cheat Sheet 권장사항:**
- CSRF Token 사용 (필수)
- SameSite 속성 사용 (권장)
- Verifiable Same-Site Origin 사용 (권장)
- 사용자 재인증 (권장)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.