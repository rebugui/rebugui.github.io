---
title: "[2026 주요정보통신기반시설] CI-04 에러페이지적용미흡(Inadequate Error Handling)"
slug: "2026-주정통/CI-04"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "웹애플리케이션 에러페이지내 불필요한 정보 노출 여부 점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Web
---

# 에러페이지적용미흡(Inadequate Error Handling)

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | CI-04 |
| **점검내용** | 웹애플리케이션 에러페이지내 불필요한 정보 노출 여부 점검 |
| **점검대상** | 웹 애플리케이션서버, 웹방화벽 |
| **양호기준** | 에러 발생 시 자체 정의 에러페이지를 출력하여 과도한 정보가 노출되지 않는 경우 |
| **취약기준** | 에러 발생 시 기본 에러페이지가 출력되며, 해당페이지에 불필요한 정보(서버 버전 정보, 시스템 경로, 스택트레이스 등)가 노출되는 경우 |
| **조치방법** | 웹애플리케이션서버내 사용자 정의 에러페이지를 적용함으로써 불필요한 정보 노출을 방지 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 에러 발생 시 자체 정의 에러 페이지를 출력하여 과도한 정보가 노출되지 않는 경우
- **취약**: 에러 발생 시 기본 에러 페이지가 출력되며, 해당 페이지에 불필요한 정보(서버버전정보, 시스템 경로, 스택트레이스 등)가 노출되는 경우

#### 경계 케이스 (Edge Case) 처리 방법
- 에러 로그는 서버 측에 상세하게 기록해야 디버깅 가능
- 사용자에게는 최소한의 정보만 제공
- 개발/운영 환경 분리 권장

#### 권장 설정값
- Apache: `ServerTokens Prod`, `ServerSignature Off`
- Nginx: `server_tokens off;`
- Tomcat: `showReport="false"`, `showServerInfo="false"`

### 2. 점검 방법

#### Step 1: 에러 유도 테스트
```
에러 유도 시 에러 페이지 내 불필요한 정보(서버 버전 정보, 시스템 절대 경로, 스택 트레이스 등)가 노출되는지 확인
```

**테스트 방법:**
1. 존재하지 않는 페이지 접근: `https://example.com/nonexistent-page`
2. 잘못된 파라미터 전송: `https://example.com/search?q=<script>`
3. 긴 URL 입력: `https://example.com/` + 4000자 이상의 문자열
4. 특수문자 포함 요청

### 3. 조치 방법

#### 1. Apache 서버

**httpd.conf 또는 apache2.conf 파일 수정:**

```apache
# 응답 헤더 내 서버 버전 정보 제거
ServerTokens Prod
ServerSignature Off

# 사용자 정의 에러 페이지
ErrorDocument 404 /errorpages/404.html
ErrorDocument 500 /errorpages/500.html
ErrorDocument 403 /errorpages/403.html
ErrorDocument 503 /errorpages/503.html
```

#### 2. Nginx 서버

**nginx.conf 파일 수정:**

```nginx
http {
    # 응답 헤더 내 서버 버전 정보 제거
    server_tokens off;

    # 에러 페이지 매핑
    error_page 404 /custom_404.html;
    error_page 500 502 503 504 /custom_50x.html;

    location = /custom_404.html {
        root /var/www/html;
        internal;
    }
}
```

#### 3. Tomcat 서버

**server.xml 파일 수정:**

```xml
<!-- 응답 헤더 내 서버 버전 정보 제거 -->
<Connector port="8080" protocol="HTTP/1.1"
           connectionTimeout="20000"
           redirectPort="8443"
           server=" " />

<!-- 개발용 리포트 비활성화 -->
<Valve className="org.apache.catalina.valves.ErrorReportValve"
       showReport="false"
       showServerInfo="false" />
```

**web.xml 파일 수정:**

```xml
<error-page>
    <error-code>404</error-code>
    <location>/errors/404</location>
</error-page>
<error-page>
    <error-code>500</error-code>
    <location>/errors/500</location>
</error-page>
<error-page>
    <exception-type>java.lang.Exception</exception-type>
    <location>/errors/500</location>
</error-page>
```

#### 4. IIS 7.0 이상

**응답 헤더 설정:**
1. URL Rewrite 모듈 설치
2. IIS 관리자 → URL 재작성 → 서버 변수 보기 → 추가
3. `RESPONSE_SERVER` 변수 추가
4. 아웃바운드 규칙 추가 → 응답 헤더의 Server 값 제거

**에러 페이지 설정:**
1. IIS 관리자 → 오류 페이지
2. 기능 설정 편집 → 사용자 지정 오류 페이지
3. 각 에러 코드별 사용자 정의 페이지 지정

#### 5. 애플리케이션 레벨 조치

**Java (Spring Boot):**
```java
@ControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(Exception.class)
    public String handleError(Exception ex, Model model) {
        // 로그에는 상세 에러 기록
        logger.error("Error occurred", ex);

        // 사용자에게는 일반적인 메시지만 표시
        model.addAttribute("errorMessage", "서버 오류가 발생했습니다.");
        return "error/500";
    }
}
```

**PHP:**
```php
// 개발 환경에서만 상세 에러 표시
if (defined('DEVELOPMENT_MODE') && DEVELOPMENT_MODE) {
    ini_set('display_errors', 1);
    error_reporting(E_ALL);
} else {
    ini_set('display_errors', 0);
    error_reporting(0);
}

// 사용자 정의 에러 핸들러
function customError($errno, $errstr) {
    error_log("Error: [$errno] $errstr");
    echo "서버 오류가 발생했습니다. 관리자에게 문의해주세요.";
    return true;
}
set_error_handler("customError");
```

### 4. 참고 자료

**HTTP 응답 헤더 보안:**

| 헤더 | 위험성 | 조치 방법 |
|------|--------|----------|
| Server | 서버 버전 노출 | ServerTokens Off (Apache) |
| X-Powered-By | 기술 스택 노출 | header_unset('X-Powered-By') |
| X-AspNet-Version | ASP.NET 버전 노출 | <httpRuntime enableVersionHeader="false" /> |

**에러 페이지에 포함해야 할 정보:**
- 사용자 친화적인 에러 메시지
- 문제 해결을 위한 안내
- 홈페이지로 돌아가기 링크
- 관리자 연락처

**에러 페이지에 포함하지 말아야 할 정보:**
- 서버 버전
- 시스템 경로
- 스택 트레이스
- 데이터베이스 쿼리
- 내부 IP 주소

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.