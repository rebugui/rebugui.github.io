---
title: "[2026 주요정보통신기반시설] WEB-11 웹서비스경로설정"
slug: "2026-주정통/WEB-11"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "웹 서비스의 경로 설정은 웹 콘텐츠와 시스템 파일을 분리하는 중요한 보안 설정입니다. 기본 설치 경로를 그대로 사용하면 공격자가 시스템 구조를 쉽게 파악할 수 있고, 웹 서비스 취"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Web
draft: true
---

# WEB-11 웹서비스경로설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | WEB-11 |
| **점검내용** | 웹 서비스의 경로 설정은 웹 콘텐츠와 시스템 파일을 분리하는 중요한 보안 설정입니다. 기본 설치 경로를 그대로 사용하면 공격자가 시스템 구조를 쉽게 파악할 수 있고, 웹 서비스 취 |
| **점검대상** | Apache, Tomcat, Nginx, IIS, JEUS, WebtoB |
| **판단기준** | 양호: 웹서버 경로를 기타 업무와 영역이 분리된 경로로 설정 및 불필요한 경로가 존재하지 않는 경우 |
| **판단기준** | 취약: 웹서버 경로를 기타 업무와 영역이 분리되지 않은 경로로 설정하거나 불필요한 경로가 있는 경우 |
| **조치방법** | 상세 조치 방법 참고 |

---
---
## 상세 설명

### 1. 항목 개요

웹 서비스의 경로 설정은 웹 콘텐츠와 시스템 파일을 분리하는 중요한 보안 설정입니다. 기본 설치 경로를 그대로 사용하면 공격자가 시스템 구조를 쉽게 파악할 수 있고, 웹 서비스 취약점을 이용해 시스템 영역으로 침투할 수 있습니다. 마치 사무실에서 중요 문서를 복도 바닥에 두는 것과 같습니다. 웹 서비스는 반드시 별도의 격리된 경로에 배치되어야 합니다.

### 2. 왜 이 항목이 필요한가요?

**실제 시나리오:**
- 웹 서비스가 기본 경로(`/var/www/html`, `C:\inetpub\wwwroot`)를 사용합니다.
- 공격자가 웹 애플리케이션 취약점을 발견합니다.
- 경로 순회 공격으로 시스템 파일에 접근을 시도합니다.
- 기본 경로의 구조를 잘 알고 있으므로 시스템 영역으로 쉽게 이동합니다.

**기본 경로 사용 위험성:**
- **예측 가능성**: 공격자가 시스템 구조를 쉽게 파악
- **경로 순회 공격 용이**: 상위 디렉터리로 쉽게 이동 가능
- **시스템 영역 침투**: 웹 취약점 → 시스템 장악 경로 단축
- **불필요한 경로 노출**: 백업, 임시 파일 등에 접근 가능

**보안 위협:**
- 시스템 파일 무단 접근 및 유출
- 웹 서비스 취약점 악용 시 시스템 장악 용이
- 백업 파일, 임시 파일 노출
- 다른 서비스로의 침투 경로 제공

### 3. 점검 대상

- **Apache**: Apache HTTP Server
- **Tomcat**: Apache Tomcat 웹 서버
- **Nginx**: Nginx 웹 서버
- **IIS**: Microsoft Internet Information Services
- **JEUS**: Tmax JEUS 웹 애플리케이션 서버
- **WebtoB**: Tmax WebtoB 웹 서버

### 4. 판단 기준

- **양호**: 웹서버 경로를 기타 업무와 영역이 분리된 경로로 설정 및 불필요한 경로가 존재하지 않는 경우
- **취약**: 웹서버 경로를 기타 업무와 영역이 분리되지 않은 경로로 설정하거나 불필요한 경로가 있는 경우

### 5. 점검 방법

#### Apache

```bash
# DocumentRoot 경로 확인
grep "DocumentRoot" /etc/apache2/apache2.conf
grep "DocumentRoot" /etc/apache2/sites-available/*.conf
```

#### Tomcat

```bash
# appBase 경로 확인
grep "appBase" /<Tomcat 설치 디렉터리>/conf/server.xml
```

#### Nginx

```bash
# root 경로 확인
grep "root" /<Nginx 설치 디렉터리>/conf/nginx.conf
```

### 6. 조치 방법

#### Apache

**Step 1) apache2.conf (또는 /conf/httpd.conf) 파일 내 DocumentRoot를 별도의 경로로 변경**

```bash
vi /<Apache 설치 디렉터리>/apache2.conf (또는 httpd.conf)
```

```apache
<!-- 변경 전 (취약) -->
DocumentRoot /var/www/html

<!-- 변경 후 (양호) -->
DocumentRoot /home/web/example/public
```

**참고**: 기본 경로인 `/var/www/html`이 아닌 별도의 경로를 사용하세요.

#### Tomcat

**Step 1) server.xml 파일 내 Context 요소의 docBase를 별도의 경로로 변경**

```bash
vi /<Tomcat 설치 디렉터리>/conf/server.xml
```

```xml
<!-- 변경 전 (취약) -->
<Host name="localhost"
      appBase="webapps"
      unpackWARs="true"
      autoDeploy="true">
    <Context path="" docBase="/var/lib/tomcat9/webapps/ROOT" />
</Host>

<!-- 변경 후 (양호) -->
<Host name="localhost"
      appBase="webapps"
      unpackWARs="true"
      autoDeploy="true">
    <Context path="" docBase="/home/web/example" />
</Host>
```

**Step 2) Tomcat 재시작**

```bash
systemctl restart tomcat
```

#### Nginx

**Step 1) sites-available 파일 내 root 경로를 별도의 경로로 변경**

```bash
vi /<Nginx 설치 디렉터리>/sites-available/default
# 또는
vi /<Nginx 설치 디렉터리>/conf/nginx.conf
```

```nginx
# 변경 전 (취약)
server {
    listen 80;
    server_name example.com;
    root /var/www/html;
    index index.html;
}

# 변경 후 (양호)
server {
    listen 80;
    server_name example.com;
    root /home/web/example/public;
    index index.html;
}
```

**Step 2) Nginx 재시작**

```bash
systemctl restart nginx
```

#### IIS

**Step 1) 기본 디렉터리 경로 확인 및 변경**

1. 시작 > Windows 관리 도구 > 인터넷 정보 서비스(IIS) 관리자 실행
2. 해당 웹 사이트 선택 > 사이트 편집 클릭
3. 기본 설정 > '실제 경로'를 별도의 경로로 변경

<!-- ![루트 디렉터리 경로 확인](../images/04_웹서비스/image_0012.png) -->

```text
변경 전: C:\inetpub\wwwroot
변경 후: D:\Websites\Example\Public
```

#### JEUS

**Step 1) ws_engine.m 파일 내 Docroot를 별도의 경로로 변경**

```bash
vi /<JEUS 설치 디렉터리>/config/ws_engine.m
# 또는 domain.xml 파일 내 context-root 확인
```

```text
# 변경 전 (취약)
Docroot = "/home/jeus/domains/sample/docs"

# 변경 후 (양호)
Docroot = "/home/web/example/public"
```

#### WebtoB

**Step 1) http.m 파일 내 DOCROOT를 별도의 경로로 변경**

```bash
vi /<WebtoB 설치 디렉터리>/config/http.m
```

```text
*NODE imuser
    WEBTOBDIR="/home/tmax/webtob/"
    SHMKEY = 54000

# 변경 전 (취약)
    DOCROOT="/home/tmax/webtob/docs"

# 변경 후 (양호)
    DOCROOT="/home/web/example/public"
```

**Step 2) 설정 파일 컴파일 및 재구동**

```bash
wscfl -I http.m
wsdown
wsboot
```

### 7. 조치 시 주의사항

- 일반적인 경우 영향이 없습니다.
- 경로 변경 시 파일 권한을 확인하고 웹 서비스 계정이 접근 가능하도록 설정해야 합니다.
- 변경 후 모든 웹 애플리케이션이 정상 작동하는지 테스트해야 합니다.
- 로그, 임시 파일 등도 별도 경로에 배치하는 것을 권장합니다.
- 다른 서비스와 경로를 분리하여 관리하는 것을 권장합니다.

### 8. 참고 자료

- Apache DocumentRoot: https://httpd.apache.org/docs/current/mod/core.html#documentroot
- Nginx root Directive: https://nginx.org/en/docs/http/ngx_http_core_module.html#root
- CIS Apache Benchmark: https://www.cisecurity.org/benchmark/apache_web_server

## 요약

웹 서비스 경로를 기본 경로와 분리된 별도의 경로로 설정하여 웹 취약점 악용 시 시스템 영역으로의 침투를 방지해야 합니다.
