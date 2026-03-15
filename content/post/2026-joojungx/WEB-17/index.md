---
title: "[2026 주요정보통신기반시설] WEB-17 웹서비스가상디렉터리삭제"
slug: "2026-주정통/WEB-17"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "가상 디렉터리(Virtual Directory)는 웹 서버의 문서 루트 외부에 있는 파일이나 디렉터리를 웹을 통해 접근 가능하게 만드는 기능입니다. 편리하지만 불필요한 가상 디렉터"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Web
---

# WEB-17 웹서비스가상디렉터리삭제

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | WEB-17 |
| **점검내용** | 가상 디렉터리(Virtual Directory)는 웹 서버의 문서 루트 외부에 있는 파일이나 디렉터리를 웹을 통해 접근 가능하게 만드는 기능입니다. 편리하지만 불필요한 가상 디렉터 |
| **점검대상** | Apache, Tomcat, Nginx, WebtoB |
| **판단기준** | 양호: 불필요한 가상 디렉터리가 존재하지 않는 경우 |
| **판단기준** | 취약: 불필요한 가상 디렉터리가 존재하는 경우 |
| **조치방법** | 상세 조치 방법 참고 |

---
---
## 상세 설명

### 1. 항목 개요

가상 디렉터리(Virtual Directory)는 웹 서버의 문서 루트 외부에 있는 파일이나 디렉터리를 웹을 통해 접근 가능하게 만드는 기능입니다. 편리하지만 불필요한 가상 디렉터리는 공격자에게 추가적인 공격 경로를 제공할 수 있습니다. 특히 테스트용, 백업용, 샘플용 가상 디렉터리는 보안 허점이 될 수 있습니다. 마치 건물에 정문 외에도 아무나 출입 가능한 뒷문을 여러 개 만드는 것과 같습니다.

### 2. 왜 이 항목이 필요한가요?

**실제 시나리오:**
- 웹 서버에 `/backup`, `/test`, `/old-site` 등의 가상 디렉터리가 설정되어 있습니다.
- 이 디렉터리들은 개발 기간에 사용되다가 운영 환경에서도 그대로 남아 있습니다.
- 공격자가 이 가상 디렉터리들을 발견하고 탐색합니다.
- 백업 파일, 테스트 파일, 구버전 파일에서 취약점을 찾아 공격합니다.

**가상 디렉터리 위험성:**
- **추가 공격 경로**: 문서 루트 외부 접근 가능
- **보안 약화 영역**: 테스트, 백업용으로 보안이 느슨한 경우 많음
- **정보 노출**: 개발 문서, 테스트 데이터, 구버전 노출
- **권한 상승**: 취약한 스크립트를 통한 시스템 장악

**삭제가 필요한 가상 디렉터리 예시:**
- `/test`, `/testing`, `/dev`: 테스트용
- `/backup`, `/old`, `/archive`: 백업용
- `/sample`, `/examples`: 샘플용
- `/admin-old`, `/v1`: 구버전용
- `/temp`, `/tmp`: 임시 파일용

### 3. 점검 대상

- **Apache**: Apache HTTP Server
- **Tomcat**: Apache Tomcat 웹 서버
- **Nginx**: Nginx 웹 서버
- **WebtoB**: Tmax WebtoB 웹 서버

### 4. 판단 기준

- **양호**: 불필요한 가상 디렉터리가 존재하지 않는 경우
- **취약**: 불필요한 가상 디렉터리가 존재하는 경우

### 5. 점검 방법

#### Apache

```bash
# Alias 지시자 확인
grep -r "Alias" /etc/apache2/sites-available/

# 또는
grep -r "Alias" /<Apache 설치 디렉터리>/conf/
```

#### Tomcat

```bash
# Context 요소의 path 속성 확인
grep -A 3 "Context path=" /<Tomcat 설치 디렉터리>/conf/server.xml
```

#### Nginx

```bash
# alias 지시자 확인
grep -r "alias" /<Nginx 설치 디렉터리>/conf/
```

#### WebtoB

```bash
# ALIAS 절 확인
grep -A 2 "*ALIAS" /<WebtoB 설치 디렉터리>/config/http.m
```

### 6. 조치 방법

#### Apache

**Step 1) Alias 지시자 확인**

```bash
vi /<Apache 설치 디렉터리>/conf/httpd.conf (또는 apache2.conf)
```

```apache
<!-- 변경 전 (취약) -->
Alias /virtual /var/www/virtual

<Directory /var/www/virtual>
    Options Indexes FollowSymLinks
    AllowOverride None
    Require all granted
</Directory>
```

**Step 2) 불필요한 가상 디렉터리 삭제**

```apache
<!-- 변경 후 (양호) - 주석 처리 또는 제거 -->
#Alias /virtual /var/www/virtual
#
#<Directory /var/www/virtual>
#    Options Indexes FollowSymLinks
#    AllowOverride None
#    Require all granted
#</Directory>
```

**Step 3) Apache 재시작**

```bash
systemctl restart apache2
```

#### Tomcat

**Step 1) Context 블록 요소의 path 속성값 확인**

```bash
vi /<Tomcat 설치 디렉터리>/server.xml
```

```xml
<!-- 변경 전 (취약) -->
<Host name="localhost"
      appBase="webapps"
      unpackWARs="true"
      autoDeploy="true">
    <Context path="/virtual"
             docBase="/path/to/your/virtual/directory"
             reloadable="true"/>
</Host>
```

**Step 2) Context 블록 요소 가상 디렉터리 제거**

```xml
<!-- 변경 후 (양호) - 주석 처리 또는 제거 -->
<Host name="localhost"
      appBase="webapps"
      unpackWARs="true"
      autoDeploy="true">
    <!--
    <Context path="/virtual"
             docBase="/path/to/your/virtual/directory"
             reloadable="true"/>
    -->
</Host>
```

**Step 3) Tomcat 재시작**

```bash
systemctl restart tomcat
```

#### Nginx

**Step 1) Alias 지시자 확인**

```bash
vi /<Nginx Dir>/nginx.conf
```

```nginx
# 변경 전 (취약)
location /virtual {
    alias /var/www/virtual;
    index index.html index.htm;
}
```

**Step 2) 설정된 모든 디렉터리의 불필요한 Alias 지시자 제거**

```nginx
# 변경 후 (양호) - 주석 처리 또는 제거
#location /virtual {
#    alias /var/www/virtual;
#    index index.html index.htm;
#}
```

**Step 3) Nginx 재구동**

```bash
systemctl restart nginx
```

#### WebtoB

**Step 1) NODE 절의 Alias 설정 확인**

```bash
vi /<WebtoB 설치 디렉터리>/config/http.m
```

```text
# 변경 전 (취약)
*ALIAS alias1
    URI = '/cgi-bin/'
    RealPath = '/home/tmax/webtob/cgi-bin/'
```

**Step 2) NODE 절의 불필요한 Alias 설정 삭제**

```text
# 변경 후 (양호) - 주석 처리
#*ALIAS alias1
#    URI = '/cgi-bin/'
#    RealPath = '/home/tmax/webtob/cgi-bin/'
```

**Step 3) 설정 파일 컴파일 및 재구동**

```bash
wscfl -I http.m
wsdown
wsboot
```

### 7. 조치 시 주의사항

- 일반적인 경우 영향이 없습니다.
- 실제 운영 중인 가상 디렉터리인지 확인 후 삭제해야 합니다.
- 삭제 전에 해당 디렉터리에서 제공되는 서비스가 있는지 확인하세요.
- 가상 디렉터리가 필요한 경우라도 별도 인증을 설정하는 것을 권장합니다.
- 삭제 후 웹사이트 정상 작동 여부를 테스트해야 합니다.
- 정기적으로 불필요한 가상 디렉터리가 추가되지 않았는지 감사해야 합니다.

### 8. 참고 자료

- Apache Alias Directive: https://httpd.apache.org/docs/current/mod/mod_alias.html#alias
- Nginx alias Directive: https://nginx.org/en/docs/http/ngx_http_core_module.html#alias
- Tomcat Context Container: https://tomcat.apache.org/tomcat-9.0-doc/config/context.html
- CWE-425: Direct Request ('Forced Browsing')

## 요약

불필요한 가상 디렉터리를 삭제하여 공격 표면을 최소화하고 추가적인 공격 경로를 차단해야 합니다.
