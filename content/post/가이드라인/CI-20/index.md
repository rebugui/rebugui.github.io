---
title: "[2026 주요정보통신기반시설] CI-20 자동화공격(Automated Attacks)"
slug: "2026-주정통/CI-20"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "웹 애플리케이션의 특정 프로세스(로그인 시도, 게시글 등록, SMS 발송 등)에 대한 반복적인 요청 시 통제여부를확인하여,자동화공격(봇공격등)을방지여부점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Web
---

# 자동화공격(Automated Attacks)

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | CI-20 |
| **점검내용** | 웹 애플리케이션의 특정 프로세스(로그인 시도, 게시글 등록, SMS 발송 등)에 대한 반복적인 요청 시 통제여부를확인하여,자동화공격(봇공격등)을방지여부점검 |
| **점검대상** | 웹 애플리케이션 소스코드, 웹방화벽 |
| **양호기준** | 웹애플리케이션의특정프로세스에대한반복적인요청시통제가적절한경우 |
| **취약기준** | 웹애플리케이션의특정프로세스에대한반복적인요청시통제가미흡한경우 |
| **조치방법** | 웹 애플리케이션의 특정 프로세스에 대한 대량 사용을 통제하는 로직을 구현하고, 웹 방화벽의 룰셋을 설정하여대량의불특정프로세스요청을차단 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 웹 애플리케이션의 특정 프로세스에 대한 반복적인 요청 시 통제가 적절한 경우
- **취약**: 웹 애플리케이션의 특정 프로세스에 대한 반복적인 요청 시 통제가 미흡한 경우

#### 경계 케이스 (Edge Case) 처리 방법
- 일반적인 경우 영향 없음
- 너무 엄격한 제한은 정상 사용자 경험 저하
- CAPTCHA는 사용성과 보안의 균형 필요

#### 권장 설정값
- 로그인: 5회/분 (실패 시)
- SMS 발송: 3회/일
- 게시글 등록: 10회/분
- API 호출: 100회/분

### 2. 점검 방법

#### Step 1: 로그인 실패 횟수 제한 확인
```
로그인 실패 일정 횟수 초과 시 반복적인 요청에 대한 통제가 미흡한지 확인
```

#### Step 2: 인증번호 발송 통제 확인
```
본인인증(계좌 인증, SMS 인증 등)을 반복적으로 시도하여 반복적인 요청에 대한 통제가 미흡한지 확인
```

### 3. 조치 방법

#### 1. 로그인 실패 횟수 제한

```java
@Service
public class LoginService {
    private static final int MAX_ATTEMPTS = 5;
    private static final long LOCK_TIME_MINUTES = 30;

    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestParam String username,
                                  @RequestParam String password,
                                  HttpServletRequest request) {
        String ip = getClientIP(request);

        // 잠긴 계정 확인
        if (isAccountLocked(username)) {
            return ResponseEntity.status(403)
                .body("계정이 잠겼습니다. 30분 후 다시 시도해주세요.");
        }

        // IP별 실패 횟수 확인
        int attempts = getFailedAttempts(ip);
        if (attempts >= MAX_ATTEMPTS) {
            return ResponseEntity.status(429)
                .body("너무 많은 로그인 시도로 일시적으로 차단되었습니다.");
        }

        // 인증 시도
        User user = authenticate(username, password);

        if (user == null) {
            // 실패 횟수 증가
            incrementFailedAttempts(ip, username);
            return ResponseEntity.status(401)
                .body("아이디 또는 비밀번호가 일치하지 않습니다.");
        }

        // 성공 시 실패 횟수 초기화
        resetFailedAttempts(ip, username);

        return ResponseEntity.ok("로그인 성공");
    }
}
```

#### 2. CAPTCHA 도입

```java
// 재시도 횟수 초과 시 CAPTCHA 표시
@GetMapping("/login")
public String loginForm(@RequestParam(required = false) Integer attempts,
                         Model model) {
    if (attempts != null && attempts >= 3) {
        model.addAttribute("showCaptcha", true);
    }
    return "login";
}

// CAPTCHA 검증
@PostMapping("/login")
public String login(@RequestParam String username,
                    @RequestParam String password,
                    @RequestParam String captcha,
                    HttpServletRequest request) {

    // CAPTCHA 검증
    if (!captchaService.verify(captcha)) {
        return "redirect:/login?error=captcha";
    }

    // 로그인 처리
    // ...
}
```

#### 3. Rate Limiting 적용

**Spring Boot + Bucket4j 예시:**
```java
@Configuration
public class RateLimitConfig {
    @Bean
    public RateLimiter rateLimiter() {
        // 1분에 10회 요청 허용
        return RateLimiter.create(10.0, 1, TimeUnit.MINUTES);
    }
}

@GetMapping("/api/sms")
public ResponseEntity<?> sendSms(@RequestParam String phone) {
    // Rate Limiting 확인
    if (!rateLimiter.tryAcquire()) {
        return ResponseEntity.status(429)
            .body("너무 자주 요청하셨습니다. 잠시 후 다시 시도해주세요.");
    }

    // SMS 발송 처리
    smsService.send(phone);
    return ResponseEntity.ok("인증번호가 발송되었습니다.");
}
```

#### 4. IP 기반 차단

```java
@Component
public class IpFilter implements Filter {
    private static final int MAX_REQUESTS_PER_MINUTE = 60;
    private final Map<String, Queue<Long>> ipRequests = new ConcurrentHashMap<>();

    @Override
    public void doFilter(ServletRequest request, ServletResponse response,
                        FilterChain chain) throws IOException, ServletException {
        HttpServletRequest req = (HttpServletRequest) request;
        String ip = getClientIP(req);

        long currentTime = System.currentTimeMillis();
        Queue<Long> timestamps = ipRequests.computeIfAbsent(
            ip, k -> new LinkedList<>()
        );

        // 1분 이전 요청 제거
        timestamps.removeIf(time -> currentTime - time > 60000);

        // 1분 요청 횟수 확인
        if (timestamps.size() >= MAX_REQUESTS_PER_MINUTE) {
            ((HttpServletResponse) response).sendError(429, "Too Many Requests");
            return;
        }

        timestamps.add(currentTime);

        chain.doFilter(request, response);
    }
}
```

#### 5. 웹 방화벽 룰셋 적용

```
# ModSecurity WAF 예시
SecRule IP:@ipMatch "192.168.1.100" \
    "id:1000,phase:1,t:none,deny,status:403,msg:'Blocked IP'"

# Rate Limiting
SecAction "id:1001,phase:1,t:none,nolog,pass,initcol:ip=GLOBAL"
SecRule IP:@eq "%{GLOBAL.ip}" \
    "id:1002,phase:1,t:none,deny,status:429,msg:'Rate limit exceeded'"
```

### 4. 참고 자료

**CAPTCHA 종류:**
1. **텍스트 CAPTCHA**
   - 사용자가 왜곡된 텍스트 입력
   - OCR 가능한 봇에 취약

2. **이미지 CAPTCHA**
   - reCAPTCHA v2, hCaptcha
   - 사용자 친화적

3. **무형 CAPTCHA**
   - reCAPTCHA v3
   - 사용자 개입 불필요
   - 점수 기반

**Rate Limiting 권장:**
- 로그인: 5회/분 (실패 시)
- SMS 발송: 3회/일
- 게시글 등록: 10회/분
- API 호출: 100회/분

**자동화 공격 도구:**
- Burp Suite Intruder
- OWASP ZAP
- Hydra
- Medusa
- Selenium, Puppeteer

**OWASP Automated Threats to Web Applications:**
1. Credential Stuffing
2. Credential Cracking
3. Aggressive Scraping
4. Account Creation
5. Denial of Service
6. Fingerprinting
7. Automated Click Fraud

**방어 계층:**
1. 애플리케이션 레벨: 횟수 제한, CAPTCHA
2. 서버 레벨: Rate Limiting, IP 차단
3. 네트워크 레벨: WAF, IPS/IDS
4. CDN 레벨: DDoS 방지, Rate Limiting

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.