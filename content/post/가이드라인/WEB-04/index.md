---
title: "[2026 주요정보통신기반시설] WEB-04 웹서비스디렉터리리스팅방지설정"
slug: "2026-주정통/WEB-04"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "디렉터리리스팅기능차단여부점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Web
---

# WEB-04 웹서비스디렉터리리스팅방지설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | WEB-04 |
| **점검내용** | 디렉터리리스팅기능차단여부점검 |
| **점검대상** | Apache, Tomcat, Nginx, IIS, JEUS, WebtoB |
| **판단기준** | 양호: 디렉터리리스팅이설정되지않은경우 |
| **판단기준** | 취약: 디렉터리리스팅이설정된경로 |
| **조치방법** | 디렉터리리스팅기능차단설정 |

---
## 상세 설명

### 1. 항목 개요

웹 브라우저로 웹사이트에 접속할 때 인덱스 파일(index.html, index.php 등)이 없는 디렉터리를 방문하면, 웹 서버 설정에 따라 해당 디렉터리의 모든 파일 목록이 보이도록 설정될 수 있습니다. 마치 집의 현관문을 열어두어 누구나 방 안을 들여다볼 수 있는 것과 같습니다. 디렉터리 리스팅은 공격자에게 시스템 구조, 백업 파일, 소스 코드, 설정 파일 등 중요 정보를 제공하는 주요 정보 유출 경로입니다.

### 2. 왜 이 항목이 필요한가요?

**실제 시나리오:**
- 공격자가 웹사이트의 `/backup/` 경로에 접속합니다.
- 디렉터리 리스팅이 활성화되어 있어 `backup.zip`, `database.sql`, `config.bak` 등의 파일 목록을 확인합니다.
- 이 파일들을 다운로드하여 중요 정보를 획득합니다.

**디렉터리 리스팅을 통해 노출될 수 있는 정보:**
- 백업 파일: `backup.tar.gz`, `site_backup.zip`
- 소스 코드 파일: `.php~`, `.java.bak`, `.swp`
- 설정 파일: `config.php.bak`, `.env`
- 데이터베이스 덤프: `database.sql`, `dump.sql`
- 개발 문서: `README.md`, `CHANGELOG.txt`

**보안 위협:**
- 웹 서버 구조 노출로 인한 효과적인 공격 경로 파악
- 소스 코드 유출로 인한 취약점 분석 가능
- 백업 파일을 통한 데이터베이스 및 설정 정보 탈취
- 개발자가 실수로 남긴 백도어나 테스트 파일 발견

### 3. 점검 대상

- **Apache**: Apache HTTP Server
- **Tomcat**: Apache Tomcat 웹 서버
- **Nginx**: Nginx 웹 서버
- **IIS**: Microsoft Internet Information Services
- **JEUS**: Tmax JEUS 웹 애플리케이션 서버
- **WebtoB**: Tmax WebtoB 웹 서버

### 4. 판단 기준

- **양호**: 디렉터리 리스팅이 설정되지 않은 경우
- **취약**: 디렉터리 리스팅이 설정된 경우

### 5. 점검 방법

#### 간단한 점검 방법

웹 브라우저로 다음 URL들을 접속해 봅니다:
- `http://your-domain.com/images/`
- `http://your-domain.com/backup/`
- `http://your-domain.com/uploads/`

파일 목록이 보이면 취약, "403 Forbidden" 또는 "404 Not Found"가 나오면 양호입니다.

#### Apache

```bash
# httpd.conf 또는 apache.conf 파일 확인
cat /<Apache 설치 디렉터리>/httpd.conf | grep "Indexes"
```

#### Tomcat

```bash
# web.xml 파일 확인
cat /<Tomcat 설치 디렉터리>/conf/web.xml | grep "listings"
```

#### Nginx

```bash
# nginx.conf 파일 확인
cat /<Nginx 설치 디렉터리>/conf/nginx.conf | grep "autoindex"
```

### 6. 조치 방법

#### Apache

**Step 1) httpd.conf 파일 내 모든 디렉터리의 Options 지시자에서 Indexes 옵션 제거**

```bash
vi /<Apache 설치 디렉터리>/httpd.conf (또는 apache.conf)
```

```apache
<!-- 변경 전 (취약) -->
<Directory />
    Options Indexes FollowSymLinks
</Directory>

<!-- 변경 후 (양호) -->
<Directory />
    Options -Indexes
    # 또는
    # Options FollowSymLinks
</Directory>
```

**Step 2) Apache 재시작**

```bash
systemctl restart apache2
# 또는
systemctl restart httpd
```

**참고**: httpd.conf 뿐만 아니라 sites-available 디렉터리 내 모든 사이트 설정에도 적용해야 합니다.

#### Tomcat

**Step 1) web.xml 파일 내 listings 옵션 비활성화**

```bash
vi /<Tomcat 설치 디렉터리>/conf/web.xml
```

```xml
<!-- 변경 전 (취약) -->
<init-param>
    <param-name>listings</param-name>
    <param-value>true</param-value>
</init-param>

<!-- 변경 후 (양호) -->
<init-param>
    <param-name>listings</param-name>
    <param-value>false</param-value>
</init-param>
```

**Step 2) Tomcat 재시작**

```bash
systemctl restart tomcat
```

#### Nginx

**Step 1) nginx.conf 파일 내 autoindex 지시자 off 설정**

```bash
vi /<Nginx 설치 디렉터리>/conf/nginx.conf
```

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        autoindex off;  # 디렉터리 리스팅 비활성화
        root /var/www/html;
    }
}
```

**Step 2) Nginx 재시작**

```bash
systemctl restart nginx
```

#### IIS

**Step 1) 디렉터리 검색 비활성화**

1. 시작 > Windows 관리 도구 > 인터넷 정보 서비스(IIS) 관리자 실행
2. 해당 웹 사이트 선택
3. IIS 섹션에서 '디렉터리 검색' 더블클릭
4. '사용'을 '사용 안 함'으로 설정
5. 우측 '적용' 클릭

<!-- ![디렉터리 검색 기능 비활성화](../images/04_웹서비스/image_0005.png) -->

#### JEUS

**Step 1) jeus-web-dd.xml 파일 내 디렉터리 리스팅 설정 변경**

```bash
vi /<JEUS 설치 디렉터리>/WEB-INF/jeus-web-dd.xml
```

```xml
<!-- 변경 전 (취약) -->
<allow-indexing>true</allow-indexing>

<!-- 변경 후 (양호) -->
<allow-indexing>false</allow-indexing>
```

#### WebtoB

**Step 1) http.m 파일 내 Options 지시자 설정**

```bash
nano /<WebtoB 설치 디렉터리>/config/http.m
```

```text
*NODE imuser
    WEBTOBDIR="/root/webtob"
    Options = "-Indexes"  # -Indexes로 설정

# 또는 Options 항목에서 Indexes 제거
```

**Step 2) 설정 파일 컴파일 및 재시작**

```bash
wscfl -I http.m
wsdown
wsboot
```

### 7. 조치 시 주의사항

- 일반적인 경우 영향이 없습니다.
- 디렉터리 리스팅이 필요한 특정 디렉터리(예: 공개 파일 다운로드 사이트)는 별도로 설정할 수 있습니다.
- 설정 변경 후 웹사이트의 모든 디렉터리에서 정상적으로 동작하는지 확인하세요.
- 개발 환경과 운영 환경 모두에서 적용해야 합니다.

### 8. 참고 자료

- Apache Directory 지시자: https://httpd.apache.org/docs/current/mod/core.html#directory
- Nginx ngx_http_autoindex_module: https://nginx.org/en/docs/http/ngx_http_autoindex_module.html
- OWASP Directory Listing: https://cwe.mitre.org/data/definitions/538.html

## 요약

디렉터리 리스팅 기능을 차단하여 웹 서버의 파일 구조와 중요 파일 정보 노출을 방지해야 합니다.
