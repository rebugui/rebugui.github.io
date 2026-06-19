---
title: "[2026 주요정보통신기반시설] CI-17 데이터평문전송(Cleartext Transmission)"
slug: "2026-주정통/CI-17"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "서버와클라이언트간통신시데이터의암호화여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Web
draft: true
---

# 데이터평문전송(Cleartext Transmission)

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | CI-17 |
| **점검내용** | 서버와클라이언트간통신시데이터의암호화여부점검 |
| **점검대상** | 웹 애플리케이션 소스코드, 웹 애플리케이션 서버 |
| **양호기준** | 중요정보전송구간에암호화통신이적용된경우 |
| **취약기준** | 중요정보전송구간에암호화통신이이루어지지않는경우 |
| **조치방법** | 사이트의중요정보전송구간(로그인, 회원가입, 회원정보관리, 게시판등)에대하여암호화통신(https, 애플리케이션방식)적용 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 중요 정보 전송 구간에 암호화 통신이 적용된 경우
- **취약**: 중요 정보 전송 구간에 암호화 통신이 이루어지지 않는 경우

#### 경계 케이스 (Edge Case) 처리 방법
- 일반적인 경우 영향 없음
- SSL 인증서 설치 필요
- 모든 HTTP 리소스를 HTTPS로 변경 필요
- 혼합 콘텐츠(Mixed Content) 방지

#### 권장 설정값
- TLS 1.2 이상 사용
- HSTS max-age: 31536000 (1년)
- 강력한 암호화 스위트 사용

### 2. 점검 방법

#### Step 1: 중요 정보 페이지 확인
```
중요 정보(인증정보, 개인정보, 로그인페이지 등)를 송수신하는 페이지 존재 여부 확인
```

#### Step 2: HTTPS 사용 확인
```
중요 정보 송수신 페이지가 암호화 통신(https, 데이터 암호화 등)을 하는지 확인
```

#### Step 3: 프로토콜 버전 확인
```
취약한 버전의 암호 프로토콜 사용 시 암호화된 통신 내용이 유출될 가능성이 존재하므로 취약한 버전의 SSL(SSL 2.0, 3.0) 사용 여부를 점검
```

### 3. 조치 방법

#### 1. HTTPS 적용

**모든 중요 페이지 HTTPS 강제:**
```java
// HTTP를 HTTPS로 리다이렉트
@Configuration
public class HttpsRedirectConfig {
    @Bean
    public ServletWebServerFactory servletContainer() {
        TomcatServletWebServerFactory tomcat = new TomcatServletWebServerFactory() {
            @Override
            protected void postProcessContext(Context context) {
                SecurityConstraint securityConstraint = new SecurityConstraint();
                securityConstraint.setUserConstraint("CONFIDENTIAL");
                SecurityCollection collection = new SecurityCollection();
                collection.addPattern("/*");
                securityConstraint.addCollection(collection);
                context.addConstraint(securityConstraint);
            }
        };
        tomcat.addAdditionalTomcatConnectors(redirectConnector());
        return tomcat;
    }

    private Connector redirectConnector() {
        Connector connector = new Connector("org.apache.coyote.http11.Http11NioProtocol");
        connector.setScheme("http");
        connector.setPort(8080);
        connector.setSecure(false);
        connector.setRedirectPort(8443);
        return connector;
    }
}
```

#### 2. 취약한 프로토콜 비활성화

**Apache 서버:**
```apache
# SSL 2.0, 3.0, TLS 1.0, 1.1 비활성화
SSLProtocol all -SSLv2 -SSLv3 -TLSv1 -TLSv1.1

# TLS 1.2, 1.3만 허용
SSLProtocol -all +TLSv1.2 +TLSv1.3
```

**Nginx 서버:**
```nginx
server {
    listen 443 ssl;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256';
    ssl_prefer_server_ciphers on;
}
```

**IIS 레지스트리:**
```
[HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\SSL 3.0\Server]
"Enabled"=dword:00000000

[HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.0\Server]
"Enabled"=dword:00000000
```

#### 3. HSTS (HTTP Strict Transport Security) 적용

```apache
# Apache
Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
```

```nginx
# Nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

```java
// Spring Boot
server.ssl.enabled=true
server.headers.hsts.enabled=true
server.headers.hsts.max-age=31536000
server.headers.hsts.includeSubDomains=true
```

#### 4. Secure 쿠키 속성 적용

```java
// HTTPS에서만 전송되는 쿠키
Cookie cookie = new Cookie("sessionId", sessionId);
cookie.setSecure(true);    // HTTPS에서만 전송
cookie.setHttpOnly(true);  // JavaScript 접근 차단
```

#### 5. HTTP에서 HTTPS로 리다이렉트

**.htaccess:**
```apache
# 모든 HTTP 요청을 HTTPS로 리다이렉트
RewriteEngine On
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
```

**Spring Boot:**
```java
@Configuration
public class SecurityConfig extends WebSecurityConfigurerAdapter {
    @Override
    protected void configure(HttpSecurity http) throws Exception {
        http.requiresChannel()
            .anyRequest().requiresSecure();
    }
}
```

### 4. 참고 자료

**TLS/SSL 버전별 보안성:**

| 버전 | 상태 | 비고 |
|------|------|------|
| SSL 2.0 | 사용 금지 | 1995년 폐기, 취약함 |
| SSL 3.0 | 사용 금지 | POODLE 취약점 |
| TLS 1.0 | 사용 권장 안 함 | BEAST 취약점 |
| TLS 1.1 | 사용 권장 안 함 | RC4 취약점 |
| TLS 1.2 | 권장 | 안전함 |
| TLS 1.3 | 권장 | 가장 안전함 |

**권장 암호화 스위트:**
- TLS 1.2: ECDHE-RSA-AES128-GCM-SHA256
- TLS 1.3: TLS_AES_256_GCM_SHA384

**체크리스트:**
1. [ ] SSL/TLS 인증서 설치
2. [ ] 모든 HTTP 트래픽을 HTTPS로 리다이렉트
3. [ ] 취약한 프로토콜(SSLv2/v3, TLSv1.0/1.1) 비활성화
4. [ ] HSTS 헤더 적용
5. [ ] Secure 쿠키 속성 적용
6. [ ] 혼합 콘텐츠 방지
7. [ ] 강력한 암호화 스위트 사용

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.