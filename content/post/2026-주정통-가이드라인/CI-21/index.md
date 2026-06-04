---
title: "[2026 주요정보통신기반시설] CI-21 불필요한Method악용(Unnecessary HTTP Methods)"
slug: "2026-주정통/CI-21"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "PUT,DELETE,TRACE등불필요한HTTP메소드의악용여부확인"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Web
---

# 불필요한Method악용(Unnecessary HTTP Methods)

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | CI-21 |
| **점검내용** | PUT,DELETE,TRACE등불필요한HTTP메소드의악용여부확인 |
| **점검대상** | 웹 애플리케이션 서버 |
| **양호기준** | 웹 애플리케이션에 불필요한 메소드(PUT, DELETE, TRACE, CONNECT 등)로 변조한 요청 패킷전송시해당메소드를통하여임의의행위로부터악용이제한되는경우 |
| **취약기준** | 웹 애플리케이션에 불필요한 메소드(PUT, DELETE, TRACE, CONNECT 등)로 변조한 요청 패킷전송시해당메소드를통하여임의의행위에대한악용이가능한경우 |
| **조치방법** | WEB/WAS의설정파일을변경하여불필요한메소드의사용을제한 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 웹 애플리케이션에 불필요한 메소드(PUT, DELETE, TRACE, CONNECT 등)로 변조한 요청 패킷 전송 시 해당 메소드를 통하여 임의의 행위로부터 악용이 제한되는 경우
- **취약**: 웹 애플리케이션에 불필요한 메소드(PUT, DELETE, TRACE, CONNECT 등)로 변조한 요청 패킷 전송 시 해당 메소드를 통하여 임의의 행위에 대한 악용이 가능한 경우

#### 경계 케이스 (Edge Case) 처리 방법
- 일반적인 경우 영향 없음
- RESTful API에서 PUT, DELETE를 사용하는 경우 괜찮음
- 단, WebDAV는 비활성화 권장

#### 권장 설정값
- TRACE 메소드: 반드시 비활성화
- WebDAV (PUT, DELETE): 필요한 경우에만 사용
- CONNECT: 비활성화 권장

### 2. 점검 방법

#### Step 1: PUT 메소드 테스트
```
PUT 메소드를 사용하여 악성 파일(Server Side Script, 악성 스크립트 등) 생성 시도
```

#### Step 2: DELETE 메소드 테스트
```
DELETE 메소드를 사용하여 서버에 저장된 임의의 데이터 삭제 가능
```

#### Step 3: TRACE 메소드 테스트
```
TRACE 메소드를 사용하여 쿠키 탈취 가능 여부 확인
```

### 3. 조치 방법

#### 1. Apache 서버

**WebDAV 비활성화:**
```bash
# WebDAV 모듈 비활성화
sudo a2dismod dav
sudo a2dismod dav_fs
```

**PUT, DELETE 메소드 제한:**
```apache
<Directory "/var/www/html">
    Dav Off  # WebDAV 비활성화
    Options FollowSymLinks

    # PUT, DELETE 메소드 사용 금지
    <LimitExcept GET POST OPTIONS>
        Order Allow,Deny
        Deny from all
    </LimitExcept>
</Directory>
```

**TRACE 메소드 비활성화:**
```apache
# /etc/apache2/apache2.conf 또는 httpd.conf
TraceEnable Off
```

**CONNECT 메소드 비활성화:**
```apache
<IfModule mod_rewrite.c>
    RewriteEngine On
    RewriteCond %{REQUEST_METHOD} ^CONNECT
    RewriteRule .* - [F]
</IfModule>
```

#### 2. Nginx 서버

**WebDAV 비활성화:**
```nginx
location /dav/ {
    # dav_methods 지시어 제거
    # dav_methods PUT DELETE MKCOL COPY MOVE;
}
```

**TRACE 메소드 비활성화:**
```nginx
# Nginx 0.5.17 이후 버전은 기본적으로 TRACE 비활성화
# 명시적으로 설정하려면:
server {
    if ($request_method = TRACE) {
        return 405;
    }
}
```

#### 3. Tomcat 서버

**WebDAV 비활성화:**
```xml
<!-- server.xml 또는 context.xml -->
<!-- webdav 서블릿 제거 또는 readonly 설정 -->
<servlet>
    <servlet-name>webdav</servlet-name>
    <servlet-class>org.apache.catalina.servlets.WebdavServlet</servlet-class>
    <init-param>
        <param-name>readonly</param-name>
        <param-value>true</param-value>  <!-- 쓰기 권한 제거 -->
    </init-param>
</servlet>
```

**TRACE 메소드 비활성화:**
```xml
<!-- server.xml -->
<Connector port="8080" protocol="HTTP/1.1"
           connectionTimeout="20000"
           redirectPort="8443"
           allowTrace="false" />  <!-- 설정 제거 또는 false로 설정 -->
```

#### 4. IIS 서버

**IIS 6.0 이하:**
```
1. 레지스트리 편집기 열기
2. HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\W3SVC\Parameters
3. 새 DWORD 값: DisableWebDAV = 1
4. IIS 재시작
```

**IIS 7.0 이상:**
```
1. IIS 관리자 실행
2. 요청 필터링 → HTTP 동사 → 동사 거부
3. TRACE 추가

또는 WebDAV 역할 서비스 비활성화
```

#### 5. 애플리케이션 레벨 제한

**Spring Boot 예시:**
```java
@Configuration
public class WebSecurityConfig {
    @Bean
    public FilterRegistrationBean<MethodFilter> methodFilter() {
        FilterRegistrationBean<MethodFilter> registration = new FilterRegistrationBean<>();
        registration.setFilter(new MethodFilter());
        registration.addUrlPatterns("/*");
        return registration;
    }
}

public class MethodFilter implements Filter {
    private static final Set<String> ALLOWED_METHODS =
        Set.of("GET", "POST", "HEAD", "OPTIONS");

    @Override
    public void doFilter(ServletRequest request, ServletResponse response,
                        FilterChain chain) throws IOException, ServletException {
        HttpServletRequest req = (HttpServletRequest) request;
        String method = req.getMethod();

        if (!ALLOWED_METHODS.contains(method)) {
            ((HttpServletResponse) response).sendError(
                HttpServletResponse.SC_METHOD_NOT_ALLOWED,
                "Method Not Allowed"
            );
            return;
        }

        chain.doFilter(request, response);
    }
}
```

### 4. 참고 자료

**HTTP 메소드:**

| 메소드 | 용도 | 위험성 |
|--------|------|--------|
| GET | 리소스 조회 | 안전함 |
| POST | 리소스 생성 | 안전함 |
| HEAD | 헤더만 조회 | 안전함 |
| OPTIONS | 통신 옵션 확인 | 안전함 |
| PUT | 리소스 업데이트/생성 | 파일 업로드 가능 |
| DELETE | 리소스 삭제 | 데이터 삭제 가능 |
| TRACE | 요청 반향 | 쿠키 탈취 가능 |
| CONNECT | 프록시 터널 | 프록시 악용 가능 |
| PATCH | 부분 업데이트 | 일부 공격 가능 |

**XST (Cross-Site Tracing) 공격:**
- TRACE 메소드를 악용
- HttpOnly 쿠키 탈취 가능
- 모든 최신 브라우저에서 TRACE 비활성화됨

**RESTful API 사용 시:**
- PUT, DELETE를 사용해도 됨
- 하지만 인증과 권한 검증 필수
- 입력값 검증 필수

**WebDAV 사용 시:**
- 망 분리된 내부망에서만 사용
- 적절한 인증 절차 필요
- 쓰기 권한 최소화

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.