---
title: "[2026 주요정보통신기반시설] CI-18 쿠키변조(Cookie Manipulation)"
slug: "2026-주정통/CI-18"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "쿠키변조를통한임의의타사용자권한탈취여부점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Web
---

# 쿠키변조(Cookie Manipulation)

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | CI-18 |
| **점검내용** | 쿠키변조를통한임의의타사용자권한탈취여부점검 |
| **점검대상** | 웹 애플리케이션 소스코드 |
| **양호기준** | 쿠키를 사용하지 않고 서버 사이드 세션을 사용하고 있거나, 쿠키를 사용하는 경우 안전한 알고리즘(SEED, 3DES,AES)이적용되어있는경우 |
| **취약기준** | 안전한 알고리즘이 적용되지 않은 쿠키를 사용하거나, 쿠키로만 인증 및 권한 부여를 적용하는 경우 |
| **조치방법** | 쿠키대신서버사이드세션방식을사용하거나,쿠키를통해인증등중요한기능을구현해야하는경우 안전한알고리즘(SEED, 3DES, AES등)을적용 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 쿠키를 사용하지 않고 서버 사이드 세션을 사용하고 있거나, 쿠키를 사용하는 경우 안전한 알고리즘(SEED, 3DES, AES 등)이 적용되어 있는 경우
- **취약**: 안전한 알고리즘이 적용되지 않은 쿠키를 사용하거나, 쿠키로만 인증 및 권한 부여를 적용하는 경우

#### 경계 케이스 (Edge Case) 처리 방법
- 일반적인 경우 영향 없음
- 쿠키보다 서버 사이드 세션 권장
- 암호화 키는 안전하게 관리 필요

#### 권장 설정값
- 서버 사이드 세션 사용 권장
- AES-256 암호화 알고리즘
- HttpOnly, Secure, SameSite 속성 적용

### 2. 점검 방법

#### Step 1: 쿠키 내 중요 정보 확인
```
일반 사용자 계정으로 로그인 한 뒤 쿠키 내용 및 발행되는 쿠키에 중요 정보(인증을 위한 ID, 권한을 위한 구분자 등)의 노출 여부 확인 후 변조 시도
```

#### Step 2: 쿠키 변조 시도
```
쿠키 내 노출되는 중요 정보를 변조하여 다른 사용자 및 권한으로 정상 이용이 가능한지 확인
```

### 3. 조치 방법

#### 1. 서버 사이드 세션 사용 (가장 권장)

```java
// 세션은 서버에 저장되고 클라이언트에는 세션 ID만 전달
@PostMapping("/login")
public String login(@RequestParam String username,
                    @RequestParam String password,
                    HttpSession session) {
    User user = userService.authenticate(username, password);

    // 사용자 정보는 서버 세션에 저장
    session.setAttribute("user", user);
    session.setAttribute("userId", user.getId());
    session.setAttribute("role", user.getRole());

    // 클라이언트에는 세션 ID만 전달 (자동 생성됨)
    return "redirect:/dashboard";
}
```

#### 2. 안전한 암호화 알고리즘 적용

**AES + HMAC 예시 (Java):**
```java
public class CookieUtil {
    private static final int IV_LEN = 16;
    private static final int HMAC_LEN = 32;
    private final byte[] encKey;  // AES-256 키
    private final byte[] hmacKey; // HMAC 키

    // 쿠키 생성
    public void addSecureCookie(HttpServletResponse resp,
                                String name,
                                String plaintext,
                                int maxAgeSec) throws Exception {
        byte[] iv = new byte[IV_LEN];
        new SecureRandom().nextBytes(iv);

        // AES-256-CBC 암호화
        Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5Padding");
        cipher.init(Cipher.ENCRYPT_MODE,
                   new SecretKeySpec(encKey, "AES"),
                   new IvParameterSpec(iv));
        byte[] ciphertext = cipher.doFinal(plaintext.getBytes());

        // HMAC 생성
        Mac mac = Mac.getInstance("HmacSHA256");
        mac.init(new SecretKeySpec(hmacKey, "HmacSHA256"));
        mac.update(iv);
        mac.update(ciphertext);
        byte[] hmac = mac.doFinal();

        // payload = IV + HMAC + 암호문
        byte[] payload = new byte[iv.length + hmac.length + ciphertext.length];
        System.arraycopy(iv, 0, payload, 0, iv.length);
        System.arraycopy(hmac, 0, payload, iv.length, hmac.length);
        System.arraycopy(ciphertext, 0, payload, iv.length + hmac.length, ciphertext.length);

        String encoded = Base64.getUrlEncoder().withoutPadding()
                            .encodeToString(payload);

        // HttpOnly, Secure, SameSite 속성 설정
        String header = String.format(
            "%s=%s; Max-Age=%d; Path=/; HttpOnly; Secure; SameSite=Strict",
            name, encoded, maxAgeSec
        );
        resp.addHeader("Set-Cookie", header);
    }

    // 쿠키 읽기 (HMAC 검증 + 복호화)
    public String readSecureCookie(String value) throws Exception {
        if (value == null) return null;

        byte[] data = Base64.getUrlDecoder().decode(value);

        byte[] iv = Arrays.copyOfRange(data, 0, IV_LEN);
        byte[] hmac = Arrays.copyOfRange(data, IV_LEN, IV_LEN + HMAC_LEN);
        byte[] ciphertext = Arrays.copyOfRange(data, IV_LEN + HMAC_LEN, data.length);

        // 복호화 전 HMAC 검증
        Mac mac = Mac.getInstance("HmacSHA256");
        mac.init(new SecretKeySpec(hmacKey, "HmacSHA256"));
        mac.update(iv);
        mac.update(ciphertext);
        byte[] calc = mac.doFinal();

        if (!MessageDigest.isEqual(hmac, calc)) {
            return null;  // 변조 탐지
        }

        // 복호화
        Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5Padding");
        cipher.init(Cipher.DECRYPT_MODE,
                   new SecretKeySpec(encKey, "AES"),
                   new IvParameterSpec(iv));

        return new String(cipher.doFinal(ciphertext), StandardCharsets.UTF_8);
    }
}
```

#### 3. 쿠키 보안 속성 적용

```java
Cookie cookie = new Cookie("sessionId", sessionId);
cookie.setHttpOnly(true);   // JavaScript 접근 차단 (XSS 방어)
cookie.setSecure(true);      // HTTPS에서만 전송
cookie.setPath("/");
cookie.setMaxAge(3600);      // 1시간
cookie.setSameSite(Cookie.SameSite.STRICT);  // CSRF 방지
response.addCookie(cookie);
```

### 4. 참고 자료

**안전한 암호화 알고리즘:**
- AES (Advanced Encryption Standard)
  - AES-128 (128비트 키)
  - AES-192 (192비트 키)
  - AES-256 (256비트 키) - 권장
- 3DES (Triple DES)
- SEED (한국 표준 암호)

**HMAC (Hash-based Message Authentication Code):**
- HMAC-SHA256 (권장)
- HMAC-SHA512
- 쿠키 무결성 검증에 사용

**쿠키 보안 속성:**
1. **HttpOnly**: JavaScript에서 쿠키 접근 차단 (XSS 방어)
2. **Secure**: HTTPS에서만 전송
3. **SameSite**: CSRF 공격 방어
   - Strict: 동일 사이트 요청에만 전송
   - Lax: 일부 교차 사이트 탐색 허용
   - None: 모든 요청에 전송 (취약함)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.