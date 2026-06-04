---
title: "[2026 주요정보통신기반시설] WEB-08 웹서비스파일업로드및다운로드용량제한"
slug: "2026-주정통/WEB-08"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "파일업로드및다운로드의용량제한설정여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Web
---

# WEB-08 웹서비스파일업로드및다운로드용량제한

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | WEB-08 |
| **점검내용** | 파일업로드및다운로드의용량제한설정여부점검 |
| **점검대상** | Apache, Tomcat, Nginx, IIS, JEUS, WebtoB |
| **판단기준** | 양호: 파일업로드및다운로드용량을제한한경우 |
| **판단기준** | 취약: 파일업로드및다운로드용량을제한하지않은경로 |
| **조치방법** | 파일업로드및다운로드용량을허용가능한최소범위로제한하여설정 |

---
## 상세 설명

### 1. 항목 개요

파일 업로드/다운로드 용량 제한은 웹 서비스의 가용성과 보안을 위한 중요한 설정입니다. 용량 제한이 없으면 공격자는 대용량 파일을 반복적으로 업로드하여 서버 디스크 공간을 가득 채우거나, 서버 자원(CPU, 메모리, 네트워크 대역폭)을 고갈시켜 서비스 거부(DoS) 공격을 할 수 있습니다. 마치 트럭이 다리를 통과할 때 무게 제한을 두어 다리 무너짐을 방지하는 것과 같습니다. 용량 제한은 서버 안정성의 필수 요소입니다.

### 2. 왜 이 항목이 필요한가요?

**실제 시나리오:**
- 공격자가 용량 제한이 없는 파일 업로드 기능을 발견합니다.
- 10GB 크기의 파일을 연속적으로 업로드하여 디스크 공간을 가득 채웁니다.
- 서버가 정상적으로 작동하지 못하게 되어 서비스 거부 상태가 됩니다.
- 또는 웹쉘(용량이 작은 악성 스크립트)을 업로드하여 서버를 장악합니다.

**용량 제한이 필요한 이유:**
- **디스크 공간 보호**: 대용량 파일 업로드로 인한 디스크 고갈 방지
- **서버 자원 보호**: 메모리, CPU, 네트워크 대역폭 과부하 방지
- **웹쉘 업로드 방지**: 악성 스크립트 업로드 시도 차단
- **서비스 안정성**: 정상 사용자의 서비스 이용 보장

**보안 위협:**
- DoS(Denial of Service) 공격: 대용량 파일 업로드로 서버 다운
- 디스크 공간 고갈: 로그, 데이터베이스 등 정상 기능 마비
- 웹쉘 업로드: 시스템 권한 탈취
- 서버 자원 독점: 다른 사용자 서비스 저하

### 3. 점검 대상

- **Apache**: Apache HTTP Server
- **Tomcat**: Apache Tomcat 웹 서버
- **Nginx**: Nginx 웹 서버
- **IIS**: Microsoft Internet Information Services
- **JEUS**: Tmax JEUS 웹 애플리케이션 서버
- **WebtoB**: Tmax WebtoB 웹 서버

### 4. 판단 기준

- **양호**: 파일 업로드 및 다운로드 용량을 제한한 경우
- **취약**: 파일 업로드 및 다운로드 용량을 제한하지 않은 경우

### 5. 점검 방법

#### Apache

```bash
# LimitRequestBody 설정 확인
grep -r "LimitRequestBody" /etc/apache2/

# 설정이 없으면 무제한 (취약)
```

#### Tomcat

```bash
# maxPostSize 설정 확인
grep "maxPostSize" /<Tomcat 설치 디렉터리>/conf/server.xml
```

#### Nginx

```bash
# client_max_body_size 설정 확인
grep "client_max_body_size" /<Nginx 설치 디렉터리>/conf/nginx.conf
```

### 6. 조치 방법

#### Apache

**Step 1) 설정 파일 내 LimitRequestBody 지시자에서 파일 용량 제한 설정**

```bash
vi /<Apache 설치 디렉터리>/conf/httpd.conf (또는 apache2.conf)
```

```apache
<Directory />
    # 바이트 단위 설정 (5MB = 5242880 bytes)
    LimitRequestBody 5242880
</Directory>

# 또는 특정 디렉터리에만 설정
<Directory "/var/www/html/uploads">
    LimitRequestBody 10485760  # 10MB
</Directory>
```

#### Tomcat

**Step 1) server.xml 파일 내 maxPostSize 요소 설정**

```bash
vi /<Tomcat 설치 디렉터리>/conf/server.xml
```

```xml
<Connector port="<사용 포트>" protocol="HTTP/1.1"
           connectionTimeout="20000"
           redirectPort="<사용 포트>"
           maxParameterCount="1000"
           maxPostSize="5242880" />  <!-- maxPostSize=5242880=5MB -->
```

**Step 2) web.xml 파일 내 multipart-config 요소 설정**

```bash
vi /<Tomcat 설치 디렉터리>/conf/web.xml
```

```xml
<multipart-config>
    <max-file-size>2097152</max-file-size>      <!-- 2MB -->
    <max-request-size>4194304</max-request-size> <!-- 4MB -->
    <file-size-threshold>0</file-size-threshold>
</multipart-config>
```

#### Nginx

**Step 1) nginx.conf 파일 내 client_max_body_size 설정**

```bash
vi /<Nginx 설치 디렉터리>/conf/nginx.conf
```

```nginx
http {
    client_max_body_size 5M;  # 전체 설정
}

# 또는 특정 location에만 설정
server {
    location /uploads {
        client_max_body_size 10M;  # 10MB로 제한
    }
}
```

**Step 2) Nginx 데몬 재구동**

```bash
systemctl restart nginx
```

#### IIS

**Step 1) 루트 디렉터리 web.config 파일 내 maxAllowedContentLength 설정 확인**

파일 탐색기에서 사이트 루트 디렉터리의 web.config 파일 확인

<!-- ![최대 컨텐츠 파일 용량 제한 설정 확인](../images/04_웹서비스/image_0008.png) -->

**Step 2) 루트 디렉터리 web.config 파일 내 maxAllowedContentLength 제한 설정**

```xml
<configuration>
    <system.webServer>
        <security>
            <requestFiltering>
                <!-- 기본값: 30MB (30000000 bytes) -->
                <requestLimits maxAllowedContentLength="5242880" />  <!-- 5MB -->
            </requestFiltering>
        </security>
    </system.webServer>
</configuration>
```

**Step 3) applicationHost.config 파일 내 bufferingLimit 및 maxRequestEntityAllowed 설정**

```xml
<system.webServer>
    <limits />
    <asp>
        <!-- bufferingLimit: 4MB, maxRequestEntityAllowed: 0.2MB -->
        <bufferingLimit>4194304</bufferingLimit>
        <maxRequestEntityAllowed>204800</maxRequestEntityAllowed>
    </asp>
</system.webServer>
```

**참고**: web.config 파일이 없으면 사이트 홈 디렉터리에 새로 생성합니다.

#### JEUS

**Step 1) web.xml 파일 내 max-file-size 지시자에서 파일 용량 제한 설정**

```bash
vi /[JEUS 설치 디렉터리]/WEB-INF/web.xml
```

```xml
<multipart-config>
    <max-file-size>5242880</max-file-size>  <!-- 5MB -->
</multipart-config>
```

**참고**: 출력값이 존재하지 않는 경우 용량을 제한하고 있지 않은 상태로 취약합니다.

#### WebtoB

**Step 1) LimitRequestBody 지시자를 사용하여 파일 업로드 및 다운로드 용량 제한 설정**

```bash
vi /[WebtoB 설치 디렉터리]/conf/http.m
```

```text
*NODE imuser
    WEBTOBDIR="/home/tmax/webtob/"
    SHMKEY = 54000
    DOCROOT="/home/tmax/webtob/docs"

*ALIAS alias1
    URI = "/cgi-bin/"
    RealPath = "/home/webtob/webtob/cgi-bin/"
    LimitRequestBody = 2048000  # 약 2MB
```

**참고**: 업로드 및 다운로드 파일이 5MB를 넘지 않도록 설정을 권고합니다.

### 7. 조치 시 주의사항

- 일반적인 경우 영향이 없습니다.
- 업무상 대용량 파일 업로드가 필요한 경우, 해당 기능에 한해 적절한 용량으로 설정하세요.
- 너무 낮게 설정할 경우 정상적인 파일 업로드가 차단될 수 있습니다.
- 설정 변경 후 정상 파일 업로드가 가능한지 테스트해야 합니다.
- 사용자에게 용량 제한에 대한 안내를 하는 것을 권장합니다.

### 8. 참고 자료

- Apache Core Features: https://httpd.apache.org/docs/current/mod/core.html#limitrequestbody
- Nginx Module ngx_http_core_module: https://nginx.org/en/docs/http/ngx_http_core_module.html#client_max_body_size
- IIS Request Limits: https://docs.microsoft.com/en-us/iis/configuration/system.webServer/security/requestFiltering/requestLimits

## 요약

파일 업로드 및 다운로드 용량을 제한하여 서버 자원 고갈을 방지하고 웹쉘 업로드 등의 보안 위협을 차단해야 합니다.
