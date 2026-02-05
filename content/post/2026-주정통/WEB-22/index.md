---
title: "[2026 주요정보통신기반시설] WEB-22 에러페이지관리"
slug: "2026-주정통/WEB-22"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "웹 서버에서 오류가 발생했을 때 기본 에러 페이지는 웹 서버의 버전, OS 정보, 스택 트레이스 등을 포함할 수 있습니다. 이 정보는 공격자에게 매우 유용한 정보원입니다. 맞춤형"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Web
---

# WEB-22 에러페이지관리

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | WEB-22 |
| **점검내용** | 웹 서버에서 오류가 발생했을 때 기본 에러 페이지는 웹 서버의 버전, OS 정보, 스택 트레이스 등을 포함할 수 있습니다. 이 정보는 공격자에게 매우 유용한 정보원입니다. 맞춤형  |
| **점검대상** | Apache, Tomcat, Nginx, IIS, JEUS, WebtoB |
| **판단기준** | 양호: 웹서비스 에러 페이지가 별도로 지정된 경우 |
| **판단기준** | 취약: 웹서비스 에러 페이지가 별도로 지정되지 않거나 에러 발생 시 중요 정보가 노출되는 경우 |
| **조치방법** | 상세 조치 방법 참고 |

---
---
## 상세 설명

### 1. 항목 개요

웹 서버에서 오류가 발생했을 때 기본 에러 페이지는 웹 서버의 버전, OS 정보, 스택 트레이스 등을 포함할 수 있습니다. 이 정보는 공격자에게 매우 유용한 정보원입니다. 맞춤형 에러 페이지를 사용하여 정보 노출을 최소화하고 사용자 경험을 개선해야 합니다. 마치 회사 비상 연락망에 모든 내부 정보를 적어두는 것과 같습니다.

### 2. 왜 이 항목이 필요한가요?

**실제 시나리오:**
- 사용자가 존재하지 않는 페이지 `http://example.com/admin`에 접근합니다.
- 기본 404 에러 페이지가 표시됩니다:
  ```
  HTTP/1.1 404 Not Found
  Date: Mon, 20 Jan 2026 00:00:00 GMT
  Server: Apache/2.4.41 (Ubuntu)
  Content-Type: text/html

  <!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
  <html><head>
  <title>404 Not Found</title>
  </head><body>
  <h1>Not Found</h1>
  <p>The requested URL /admin was not found on this server.</p>
  <hr>
  <address>Apache/2.4.41 (Ubuntu) Server at example.com Port 80</address>
  </body></html>
  ```
- 공격자는 Apache 2.4.41 버전과 Ubuntu OS 정보를 획득합니다.

**기본 에러 페이지 위험성:**
- **버전 정보 노출**: 웹 서버, PHP, 데이터베이스 버전
- **OS 정보 노출**: 운영체제 종류 및 버전
- **경로 노출**: 내부 파일 시스템 구조
- **스택 트레이스**: 애플리케이션 구조 정보
- **디버깅 정보**: 개발 관련 정보 노출

### 3. 점검 대상

- **Apache**: Apache HTTP Server
- **Tomcat**: Apache Tomcat 웹 서버
- **Nginx**: Nginx 웹 서버
- **IIS**: Microsoft Internet Information Services
- **JEUS**: Tmax JEUS 웹 애플리케이션 서버
- **WebtoB**: Tmax WebtoB 웹 서버

### 4. 판단 기준

- **양호**: 웹서비스 에러 페이지가 별도로 지정된 경우
- **취약**: 웹서비스 에러 페이지가 별도로 지정되지 않거나 에러 발생 시 중요 정보가 노출되는 경우

### 5. 점검 방법

#### 간단한 점검 방법

1. 브라우저로 다음 URL 접속:
   - `http://your-domain.com/nonexistent-page` (404 테스트)
   - `http://your-domain.com/test-500-error` (500 테스트)
2. 에러 페이지 내용 확인:
   - 서버 버전, OS 정보가 보이면 취약
   - "Apache/2.4.41 (Ubuntu)" 같은 정보가 있으면 취약
   - 일반적인 "페이지를 찾을 수 없습니다" 메시지만 있으면 양호

### 6. 조치 방법

#### Apache

**Step 1) httpd.conf 파일 내 에러 코드별 에러 페이지 설정 정보 확인 후 별도의 일원화된 에러 페이지 설정**

```bash
vi /<Apache 설치 디렉터리>/sites-available/000-default.conf
```

```apache
# 에러 페이지 설정
ErrorDocument 400 /error.html
ErrorDocument 401 /error.html
ErrorDocument 403 /error.html
ErrorDocument 404 /error.html
ErrorDocument 500 /error.html
ErrorDocument 503 /error.html
```

**Step 2) Apache 재구동**

```bash
systemctl restart apache2
```

#### Tomcat

**Step 1) web.xml 파일 내 에러 페이지 설정**

```bash
vi /<Tomcat 설치 디렉터리>/conf/web.xml
```

```xml
<error-page>
    <error-code>400</error-code>
    <location>/error/400.html</location>
</error-page>
<error-page>
    <error-code>404</error-code>
    <location>/error/404.html</location>
</error-page>
<error-page>
    <error-code>500</error-code>
    <location>/error/500.html</location>
</error-page>
<error-page>
    <error-code>503</error-code>
    <location>/error/503.html</location>
</error-page>
<!-- 기타 에러 코드 -->
```

**Step 2) Tomcat 재구동**

```bash
systemctl restart tomcat
```

#### Nginx

**Step 1) nginx.conf 파일 내 에러 페이지 설정**

```bash
vi /<Nginx 설치 디렉터리>/conf/nginx.conf
```

```nginx
server {
    ...
    error_page 400 /error.html;
    error_page 401 /error.html;
    error_page 403 /error.html;
    error_page 404 /404.html;
    error_page 500 502 503 504 /50x.html;

    location = /error.html {
        root html;
        internal;
    }

    location = /404.html {
        root html;
        internal;
    }

    location = /50x.html {
        root html;
        internal;
    }
}
```

**Step 2) Nginx 재구동**

```bash
systemctl restart nginx
```

#### IIS

**Step 1) 오류 페이지 확인 후 설정**

1. 제어판 > 관리 도구 > IIS(인터넷 정보 서비스) 관리자 실행
2. 해당 웹사이트 > [오류 페이지] 더블클릭
3. [작업] 탭 내 [기능 설정 편집] 클릭
4. '서버 오류 발생 시 다음 반환' 항목을 '사용자 지정 오류 페이지'로 설정

<!-- ![오류 페이지 설정 편집](../images/04_웹서비스/image_0028.png) -->

**Step 2) 각 에러 코드별 사용자 지정 페이지 설정**

1. 오류 페이지 목록에서 상태 코드 선택
2. '편집' > '사용자 지정 페이지 URL 설정' 선택
3. 일원화된 에러 페이지 경로 입력

#### JEUS

**Step 1) web.xml(또는 webcommon.xml) 파일 내 에러 메시지 설정 확인**

```bash
vi /<JEUS 설치 디렉터리>/conf/web.xml (또는 webcommon.xml)
```

```xml
<!-- 변경 전 (취약) -->
<error-page>
    <error-code>404</error-code>
    <location>404.html</location>
</error-page>
```

**Step 2) 설정한 에러 메시지 내용 확인**

```bash
vi /<WebtoB 설치 디렉터리>/docs/404.html
```

```html
<!-- 변경 전 (취약) -->
HTTP Error 404 - Service unavailable
```

**Step 3) 일원화된 오류 메시지 설정**

```html
<!-- 변경 후 (양호) -->
<!DOCTYPE html>
<html>
<head>
    <title>404 Not Found</title>
</head>
<body>
    <h1>죄송합니다. 요청하신 페이지를 찾을 수 없습니다.</h1>
    <p>메인 페이지로 이동하시기 바랍니다.</p>
</body>
</html>
```

**Step 4) Server 설정 파일 VHOST, NODE, ERRORDOCUMENT에 오류 메시지 설정**

```bash
vi /<JEUS 설치 디렉터리>/conf/web.xml (또는 webcommon.xml)
```

```xml
*ERRORDOCUMENT
    status = 403, url = "/403.html"
    status = 404, url = "/404.html"
    status = 500, url = "/500.html"
    status = 503, url = "/503.html"
```

#### WebtoB

**Step 1) Server 설정 파일 VHOST, NODE, ERRORDOCUMENT에 설정한 오류 메시지 설정 확인 후 별도의 일원화된 에러 페이지 설정**

```bash
vi /<WebtoB 설치 디렉터리>/config/http.m
```

```text
*ERRORDOCUMENT
    503     status = 503, url = "/503.html"
```

**Step 2) 설정한 에러 메시지 내용 확인**

```bash
vi /<WebtoB 설치 디렉터리>/docs/503.html
```

```html
<!-- 변경 전 (취약) -->
HTTP Error 503 - Service unavailable
```

**Step 3) 일원화된 오류 메시지 설정**

```html
<!-- 변경 후 (양호) -->
<!DOCTYPE html>
<html>
<head>
    <title>서비스 이용 불가</title>
</head>
<body>
    <h1>죄송합니다. 요청하신 페이지를 찾을 수 없습니다.</h1>
    <p>잠시 후 다시 시도해 주시기 바랍니다.</p>
</body>
</html>
```

**Step 4) 설정 파일 컴파일 및 재구동**

```bash
wscfl -I http.m
wsdown
wsboot
```

**참고**: 일원화된 페이지에서의 불필요한 정보 노출 제한 및 웹 서비스가 제공하는 서비스에 대한 오류 코드별 에러 페이지 설정 필요. 예시와 같이 에러 코드 및 웹 버전이 출력되지 않도록 설정해야 합니다.

### 7. 조치 시 주의사항

- 일반적인 경우 영향이 없습니다.
- 에러 페이지는 사용자 친화적이어야 합니다.
- 에러 페이지 내에 서버 정보, 버전, 경로 등이 포함되지 않도록 주의하세요.
- 각 에러 코드(400, 401, 403, 404, 500, 503 등)에 맞는 페이지를 제공하세요.
- 로그에는 상세 에러 정보를 기록하되, 사용자에게는 일반적인 메시지만 보여주세요.
- 에러 페이지도 HTTPS를 통해 제공되어야 합니다.

### 8. 참고 자료

- Apache ErrorDocument: https://httpd.apache.org/docs/current/mod/core.html#errordocument
- Nginx error_page: https://nginx.org/en/docs/http/ngx_http_core_module.html#error_page
- IIS Custom Error Pages: https://docs.microsoft.com/en-us/iis/configuration/system.webServer/httpErrors
- OWASP Error Handling: https://cheatsheetseries.owasp.org/cheatsheets/Error_Handling_Cheat_Sheet.html

## 요약

필수 에러 코드에 대해 일원화된 사용자 지정 에러 페이지를 사용하고 불필요한 서버 정보 노출을 제한해야 합니다.
