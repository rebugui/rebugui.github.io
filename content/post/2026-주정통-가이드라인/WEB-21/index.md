---
title: "[2026 주요정보통신기반시설] WEB-21 HTTP리디렉션"
slug: "2026-주정통/WEB-21"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "HTTP 리디렉션은 사용자가 HTTP(80포트)로 접속했을 때 자동으로 HTTPS(443포트)로 전환해주는 기능입니다. SSL/TLS 인증서를 설치했더라도 사용자가 HTTP로 직접"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Web
draft: true
---

# WEB-21 HTTP리디렉션

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | WEB-21 |
| **점검내용** | HTTP 리디렉션은 사용자가 HTTP(80포트)로 접속했을 때 자동으로 HTTPS(443포트)로 전환해주는 기능입니다. SSL/TLS 인증서를 설치했더라도 사용자가 HTTP로 직접 |
| **점검대상** | Apache, Nginx, IIS, WebtoB |
| **판단기준** | 양호: HTTP 접근 시 HTTPS Redirection이 활성화된 경우 |
| **판단기준** | 취약: HTTP 접근 시 HTTPS Redirection이 비활성화된 경우 |
| **조치방법** | 상세 조치 방법 참고 |

---
---
## 상세 설명

### 1. 항목 개요

HTTP 리디렉션은 사용자가 HTTP(80포트)로 접속했을 때 자동으로 HTTPS(443포트)로 전환해주는 기능입니다. SSL/TLS 인증서를 설치했더라도 사용자가 HTTP로 직접 접속하면 평문 통신이 이루어집니다. 모든 HTTP 요청을 HTTPS로 자동 리디렉션하는 것은 사용자가 실수로 HTTP를 사용하는 것을 방지하고 보안을 강화하는 중요한 설정입니다. 마치 집의 모든 출입구가 보안 문으로 통하도록 만드는 것과 같습니다.

### 2. 왜 이 항목이 필요한가요?

**실제 시나리오:**
- 웹사이트에 SSL/TLS가 설치되어 있습니다.
- 하지만 HTTP(포트 80)도 여전히 열려 있습니다.
- 사용자가 `http://example.com`으로 접속합니다.
- 브라우저가 HTTP로 접속하므로 암호화되지 않은 평문 통신이 이루어집니다.
- 공격자가 이 평문 통신을 도청하여 정보를 탈취합니다.

**HTTP 리디렉션이 필요한 이유:**
- **강제 암호화**: 사용자가 HTTP로 접속해도 자동으로 HTTPS로 전환
- **보안 강화**: 평문 통신 경로 차단
- **사용자 경험**: 자동으로 안전한 연결로 전환
- **규정 준수**: 많은 보안 규정에서 HTTPS 리디렉션 요구

**리디렉션 방법:**
- **301 영구 리디렉션**: 영구적으로 URL이 변경됨 (권장)
- **302 임시 리디렉션**: 일시적으로 URL이 변경됨
- **HSTS**: 브라우저가 항상 HTTPS만 사용하도록 강제

### 3. 점검 대상

- **Apache**: Apache HTTP Server
- **Nginx**: Nginx 웹 서버
- **IIS**: Microsoft Internet Information Services
- **WebtoB**: Tmax WebtoB 웹 서버

### 4. 판단 기준

- **양호**: HTTP 접근 시 HTTPS Redirection이 활성화된 경우
- **취약**: HTTP 접근 시 HTTPS Redirection이 비활성화된 경우

### 5. 점검 방법

#### 간단한 점검 방법

```bash
# curl로 리디렉션 확인
curl -I http://your-domain.com

# 양호한 경우:
# HTTP/1.1 301 Moved Permanently
# Location: https://your-domain.com/
```

#### 웹 브라우저

1. 브라우저 주소창에 `http://your-domain.com` 입력
2. 자동으로 `https://your-domain.com`으로 변경되면 양호
3. 그대로 HTTP로 연결되면 취약

### 6. 조치 방법

#### Apache

**Step 1) SSL 모듈 활성화 확인**

```bash
apache2ctl -M | grep ssl
```

**출력이 없으면 SSL 모듈 활성화:**

```bash
# Debian/Ubuntu
a2enmod ssl
a2enmod rewrite

# 또는 mod_ssl 설치
apt install libapache2-mod-security2
```

**Step 2) HTTP Redirection 설정 확인**

```bash
vi /<Apache 설치 디렉터리>/sites-available/default-ssl.conf
```

```apache
# 방법 1: Redirect 지시자 사용
<VirtualHost *:80>
    ServerName example.com
    Redirect permanent / https://example.com/
</VirtualHost>

# 방법 2: mod_rewrite 사용
<VirtualHost *:80>
    ServerName example.com
    ServerAdmin webmaster@yourdomain.com
    DocumentRoot /var/www/html

    RewriteEngine On
    RewriteCond %{HTTPS} off
    RewriteRule ^ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```

**Step 3) SSL 가상 호스트 활성화 및 Apache 재구동**

```bash
a2ensite default-ssl
systemctl restart apache2
```

#### Nginx

**Step 1) Server 블록 내 HTTPS Redirection 설정 확인**

```bash
vi /<Nginx 설치 디렉터리>/sites-available/default
```

```nginx
# HTTP 서버 블록
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # 모든 요청을 HTTPS로 리디렉션
    return 301 https://$host$request_uri;
}

# HTTPS 서버 블록
server {
    listen 443 ssl;
    server_name mydomain.com www.mydomain.com;

    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    # 보안 설정
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;

    root /var/www/html;
    index index.html;
}
```

**Step 2) Nginx 재구동**

```bash
systemctl restart nginx
```

#### IIS

**Step 1) SSL 인증서 활성화**

1. IIS 관리자 실행
2. 해당 웹사이트 선택 > [사이트 바인딩] > [편집] 탭 클릭
3. 바인딩 '종류'를 HTTPS로 설정

<!-- ![사이트 바인딩 확인](../images/04_웹서비스/image_0027.png) -->

**Step 2) 등록된 SSL 인증서 바인딩 설정 확인**

1. 제어판 > 관리 도구 > IIS(인터넷 정보 서비스) 관리자
2. 해당 웹사이트 > [사이트 바인딩] > [편집] 탭
3. SSL 인증서 확인

**Step 3) URL Rewrite 모듈 설치 및 HTTP to HTTPS 리디렉션 설정**

URL Rewrite 모듈 다운로드: https://www.iis.net/downloads/microsoft/url-rewrite

web.config 파일 설정:
```xml
<configuration>
    <system.webServer>
        <rewrite>
            <rules>
                <rule name="HTTP to HTTPS redirect" stopProcessing="true">
                    <match url="(.*)" />
                    <conditions>
                        <add input="{HTTPS}" pattern="off" ignoreCase="true" />
                    </conditions>
                    <action type="Redirect" url="https://{HTTP_HOST}/{R:1}" redirectType="Permanent" />
                </rule>
            </rules>
        </rewrite>
    </system.webServer>
</configuration>
```

**Step 4) IIS 서버 재구동**

```powershell
iisreset
```

#### WebtoB

**Step 1) Server 설정 파일 NODE 절 vhost의 URLRewrite, URLRewriteConfig 설정 확인**

```bash
vi /<WebtoB 설치 디렉터리>/config/http.m
```

```text
*VHOST vhost1
    ...
    URLRewrite       = Y
    URLRewriteConfig = "config/rewrite_ssl.conf"
```

**Step 2) URLRewriteConfig 파일에서 Redirection 확인**

```bash
vi /<WebtoB 설치 디렉터리>/config/rewrite_ssl.conf
```

```text
# 변경 전 (취약 - 리디렉션 없음)
```

**Step 3) URLRewriteConfig 파일에서 Redirection 설정**

```text
# 변경 후 (양호)
RewriteCond %{HTTPS} off
RewriteRule .* https://%{SERVER_NAME}%{REQUEST_URI} [R=307,L]
```

**Step 4) 설정 파일 컴파일 및 재구동**

```bash
wscfl -I http.m
wsdown
wsboot
```

### 7. 조치 시 주의사항

- 일반적인 경우 영향이 없습니다.
- 리디렉션 설정 시 301(영구)과 302(임시) 중 적절한 것을 선택하세요.
- SEO를 위해서는 301 리디렉션을 권장합니다.
- HSTS(HTTP Strict Transport Security) 헤더도 함께 설정하는 것을 권장합니다.
- 리디렉션 후 정상적으로 서비스가 이루어지는지 확인해야 합니다.
- 모든 HTTP 요청이 HTTPS로 리디렉션되는지 테스트해야 합니다.

### 8. 참고 자료

- Apache mod_rewrite: https://httpd.apache.org/docs/current/mod/mod_rewrite.html
- Nginx return Directive: https://nginx.org/en/docs/http/ngx_http_rewrite_module.html#return
- IIS URL Rewrite Module: https://www.iis.net/downloads/microsoft/url-rewrite
- HSTS (HTTP Strict Transport Security): https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security

## 요약

HTTP 접속을 HTTPS로 자동 리디렉션하여 모든 통신이 암호화되도록 설정하고 스니핑 공격을 방지해야 합니다.
