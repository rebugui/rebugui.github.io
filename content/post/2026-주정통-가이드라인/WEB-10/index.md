---
title: "[2026 주요정보통신기반시설] WEB-10 불필요한프록시설정제한"
slug: "2026-주정통/WEB-10"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "프록시(Proxy) 서버는 클라이언트와 서버 사이에서 중개 역할을 하는 서버로, 로드 밸런싱, 캐싱, SSL 종료 등 다양한 목적으로 사용됩니다. 하지만 불필요하게 활성화된 프록시"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Web
---

# WEB-10 불필요한프록시설정제한

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | WEB-10 |
| **점검내용** | 프록시(Proxy) 서버는 클라이언트와 서버 사이에서 중개 역할을 하는 서버로, 로드 밸런싱, 캐싱, SSL 종료 등 다양한 목적으로 사용됩니다. 하지만 불필요하게 활성화된 프록시 |
| **점검대상** | Apache, Tomcat, Nginx, IIS, JEUS, WebtoB |
| **판단기준** | 양호: 불필요한 Proxy 설정을 제한한 경우 |
| **판단기준** | 취약: 불필요한 Proxy 설정을 제한하지 않은 경우 |
| **조치방법** | 상세 조치 방법 참고 |

---
---
## 상세 설명

### 1. 항목 개요

프록시(Proxy) 서버는 클라이언트와 서버 사이에서 중개 역할을 하는 서버로, 로드 밸런싱, 캐싱, SSL 종료 등 다양한 목적으로 사용됩니다. 하지만 불필요하게 활성화된 프록시 설정은 공격자에게 내부 네트워크 접근 경로를 제공할 수 있고, 중간자 공격(Man-in-the-Middle)이나 오픈 프록시 악용의 대상이 될 수 있습니다. 마치 집의 현관문 열쇠를 낯선 사람에게 맡기는 것과 같습니다.

### 2. 왜 이 항목이 필요한가요?

**실제 시나리오:**
- 웹 서버에 불필요한 리버스 프록시 설정이 되어 있습니다.
- 공격자가 이를 발견하고 내부 서버로의 접근 경로를 확인합니다.
- 프록시를 통해 내부 네트워크의 다른 서비스에 무단 접근합니다.
- 또는 오픈 프록시로 악용되어 스팸 메일 발송이나 DDoS 공격에 이용됩니다.

**불필요한 프록시 설정 위험성:**
- **내부 네트워크 노출**: 내부 서버 정보 및 구조 유출
- **오픈 프록시 악용**: 스팸, DDoS, 불법 콘텐츠 배포 경로 제공
- **중간자 공격**: 트래픽 가로채기 및 데이터 유출
- **관리 복잡성 증가**: 불필요한 설정으로 인한 운영 부담
- **자원 낭비**: 불필요한 연결로 인한 서버 부하

**보안 위협:**
- 내부 시스템 무단 접근
- 데이터 스니핑 및 변조
- 서버 리소스 도용
- 책임 전가 가능성 (범죄 악용 시)

### 3. 점검 대상

- **Apache**: Apache HTTP Server
- **Tomcat**: Apache Tomcat 웹 서버
- **Nginx**: Nginx 웹 서버
- **IIS**: Microsoft Internet Information Services
- **JEUS**: Tmax JEUS 웹 애플리케이션 서버
- **WebtoB**: Tmax WebtoB 웹 서버

### 4. 판단 기준

- **양호**: 불필요한 Proxy 설정을 제한한 경우
- **취약**: 불필요한 Proxy 설정을 제한하지 않은 경우

### 5. 점검 방법

#### Apache

```bash
# 프록시 모듈 확인
apache2ctl -M | grep proxy
grep -r "ProxyPass" /etc/apache2/
grep -r "ProxyRequests" /etc/apache2/
```

#### Tomcat

```bash
# 프록시 설정 확인
grep -i "proxy" /<Tomcat 설치 디렉터리>/conf/server.xml
```

#### Nginx

```bash
# 프록시 설정 확인
grep -r "proxy_pass" /<Nginx 설치 디렉터리>/conf/
```

### 6. 조치 방법

#### Apache

**Step 1) apache2.conf (또는 /conf/httpd.conf) 파일 내 불필요한 Proxy 제거**

```bash
vi /<Apache 설치 디렉터리>/httpd.conf (또는 apache2.conf)
```

```apache
<!-- 변경 전 (취약) -->
<VirtualHost *:80>
    ServerName www.example.com
    ProxyPreserveHost On
    ProxyRequests On
    ProxyPass / http://backend-server.example.com/
    ProxyPassReverse / http://backend-server.example.com/
</VirtualHost>

<!-- 변경 후 (양호) -->
<!-- 불필요한 Proxy 설정은 주석 처리 또는 제거 -->
#ProxyPreserveHost On
#ProxyRequests Off
#ProxyPass / http://backend-server.example.com/
#ProxyPassReverse / http://backend-server.example.com/
```

#### Tomcat

**Step 1) server.xml 파일 내 Connector 요소에서 불필요한 Proxy 설정 제거**

```bash
vi /<Tomcat 설치 디렉터리>/conf/server.xml
```

```xml
<!-- 변경 전 (취약) -->
<Connector port="8080" protocol="HTTP/1.1"
           proxyName="proxy.example.com"
           proxyPort="80" />

<!-- 변경 후 (양호) -->
<!-- 불필요한 proxyName, proxyPort 속성 제거 -->
<Connector port="8080" protocol="HTTP/1.1"
           connectionTimeout="20000"
           redirectPort="8443" />
```

#### Nginx

**Step 1) nginx.conf 파일 내 웹 사이트에서 불필요한 Proxy 설정 제거**

```bash
vi /<Nginx 설치 디렉터리>/conf/nginx.conf
```

```nginx
# 변경 전 (취약)
location / {
    proxy_pass http://backendserver:8080;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}

# 변경 후 (양호) - 불필요한 프록시 설정 제거
location / {
    root /var/www/html;
    index index.html;
}
```

#### IIS

**Step 1) 루트 디렉터리 web.config 파일에서 불필요한 Proxy 설정 제거**

1. 제어판 > 관리 도구 > 인터넷 정보 서비스(IIS) 관리자 실행
2. 해당 웹 사이트 선택 > 루트 디렉터리
3. web.config 파일 확인

```xml
<!-- 변경 전 (취약) -->
<configuration>
    <system.webServer>
        <directoryBrowse enabled="true" />
        <proxy enabled="true" />
    </system.webServer>
</configuration>

<!-- 변경 후 (양호) -->
<configuration>
    <system.webServer>
        <directoryBrowse enabled="false" />
        <!-- 불필요한 proxy 설정 제거 -->
    </system.webServer>
</configuration>
```

<!-- ![Proxy 설정 확인 및 제거](../images/04_웹서비스/image_0007.png) -->

#### JEUS

**Step 1) web.xml 파일 내 불필요한 Proxy 제거**

```bash
vi /[JEUS 설치 디렉터리]/WEB-INF/web.xml
# 또는
vi /[WebtoB 설치 디렉터리]/ReverseProxy/WEB-INF/web.xml
```

```xml
<!-- 변경 전 (취약) -->
<Connector port="8080" protocol="HTTP/1.1"
           redirectPort="8443"
           proxyName="proxy.example.com"
           proxyPort="80" />

<!-- 변경 후 (양호) -->
<!-- 불필요한 proxy 설정 제거 -->
<Connector port="8080" protocol="HTTP/1.1"
           redirectPort="8443" />
```

#### WebtoB

**Step 1) http.m 파일 내 불필요 Proxy 설정 제거**

```bash
vi /[WebtoB 디렉터리]/conf/http.m
```

```text
*VHOST vhost1
    ...

# 변경 전 (취약)
    REVERSE_PROXY(0): Name = rproxy1,
                      PathPrefix = "/proxypath/",
                      ServerAddress = "127.0.0.1:8088"

# 변경 후 (양호) - 불필요한 REVERSE_PROXY 설정 제거
#    REVERSE_PROXY(0): Name = rproxy1,
#                      PathPrefix = "/proxypath/",
#                      ServerAddress = "127.0.0.1:8088"
```

### 7. 조치 시 주의사항

- 일반적인 경우 영향이 없습니다.
- 프록시가 실제로 필요한 서비스인 경우(로드 밸런싱, SSL 오프로딩 등)에는 제거하지 마세요.
- 설정 제거 전에 해당 설정이 사용 중인지 확인해야 합니다.
- 변경 후 웹 서비스 정상 작동 여부를 테스트해야 합니다.
- 정기적으로 불필요한 프록시 설정이 추가되지 않았는지 감사해야 합니다.

### 8. 참고 자료

- Apache mod_proxy: https://httpd.apache.org/docs/current/mod/mod_proxy.html
- Nginx ngx_http_proxy_module: https://nginx.org/en/docs/http/ngx_http_proxy_module.html
- CWE-918: Server-Side Request Forgery (SSRF)

## 요약

불필요한 프록시 설정을 제거하여 내부 네트워크 정보 노출을 방지하고 오픈 프록시 악용 가능성을 차단해야 합니다.
