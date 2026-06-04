---
title: "[2026 주요정보통신기반시설] WEB-12 웹서비스링크사용금지"
slug: "2026-주정통/WEB-12"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "심볼릭 링크(Symbolic Link)나 별칭(Aliases)은 파일 시스템의 다른 위치에 있는 파일이나 디렉터리를 참조하는 편리한 기능입니다. 하지만 웹 서비스에서 무분별하게 사"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Web
---

# WEB-12 웹서비스링크사용금지

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | WEB-12 |
| **점검내용** | 심볼릭 링크(Symbolic Link)나 별칭(Aliases)은 파일 시스템의 다른 위치에 있는 파일이나 디렉터리를 참조하는 편리한 기능입니다. 하지만 웹 서비스에서 무분별하게 사 |
| **점검대상** | Apache, Tomcat, Nginx, IIS, JEUS, WebtoB |
| **판단기준** | 양호: 심볼릭 링크, aliases, 바로가기 등의 링크 사용을 허용하지 않는 경우 |
| **판단기준** | 취약: 심볼릭 링크, aliases, 바로가기 등의 링크 사용을 허용하는 경우 |
| **조치방법** | 상세 조치 방법 참고 |

---
---
## 상세 설명

### 1. 항목 개요

심볼릭 링크(Symbolic Link)나 별칭(Aliases)은 파일 시스템의 다른 위치에 있는 파일이나 디렉터리를 참조하는 편리한 기능입니다. 하지만 웹 서비스에서 무분별하게 사용되면 경로 검증을 우회하여 허용되지 않은 시스템 영역에 접근할 수 있는 심각한 보안 허점이 됩니다. 마치 집 안에 보안 방을 열어두고 그 방으로 향하는 또 다른 문을 열어두는 것과 같습니다.

### 2. 왜 이 항목이 필요한가요?

**실제 시나리오:**
- 웹 서비스의 공개 디렉터리에 `/etc/passwd` 파일을 가리키는 심볼릭 링크가 있습니다.
- 또는 중요 설정 파일을 가리키는 별칭이 설정되어 있습니다.
- 공격자가 이 링크를 발견하고 클릭하면 시스템의 중요 파일에 접근할 수 있습니다.
- 경로 검증 우회로 인해 웹 루트를 벗어난 파일도 접근 가능합니다.

**링크 사용 위험성:**
- **경로 우회**: 웹 루트 외부 파일 접근 가능
- **정보 노출**: 시스템 설정, 로그, 비밀번호 파일 유출
- **경로 검증 우회**: 링크를 통해 보안 검사 우회
- **악용 가능성**: 공격자가 링크를 조작하여 중요 파일 접근

**보안 위협:**
- 시스템 파일 무단 접근 (/etc/passwd, 웹 설정 등)
- 백업 파일, 소스 코드 유출
- 로그 파일을 통한 사용자 정보 탈취
- 다른 사용자의 파일 접근

### 3. 점검 대상

- **Apache**: Apache HTTP Server
- **Tomcat**: Apache Tomcat 웹 서버
- **Nginx**: Nginx 웹 서버
- **IIS**: Microsoft Internet Information Services
- **JEUS**: Tmax JEUS 웹 애플리케이션 서버
- **WebtoB**: Tmax WebtoB 웹 서버

### 4. 판단 기준

- **양호**: 심볼릭 링크, aliases, 바로가기 등의 링크 사용을 허용하지 않는 경우
- **취약**: 심볼릭 링크, aliases, 바로가기 등의 링크 사용을 허용하는 경우

### 5. 점검 방법

#### Linux 계열

```bash
# 심볼릭 링크 확인
find /var/www/html -type l
ls -la /var/www/html | grep "^l"

# 링크된 대상 확인
ls -la /var/www/html/link_name
```

#### Apache

```bash
# FollowSymLinks 옵션 확인
grep -r "FollowSymLinks" /etc/apache2/
```

#### IIS

파일 탐색기에서 바로가기 파일 확인:
- `.lnk` 파일
- 파일 종류: 바로가기

### 6. 조치 방법

#### Apache

**Step 1) apache.conf (또는 /conf/httpd.conf) 파일 내 Options 지시자 FollowSymLinks 옵션 제거**

```bash
vi /<Apache 설치 디렉터리>/conf/httpd.conf (또는 apache.conf)
```

```apache
<!-- 변경 전 (취약) -->
<Directory />
    Options Indexes FollowSymLinks
</Directory>

<!-- 변경 후 (양호) -->
<Directory />
    Options -FollowSymLinks
    #Options Indexes FollowSymLinks  # 주석 처리
</Directory>
```

**Step 2) Apache 재시작**

```bash
systemctl restart apache2
```

#### Tomcat

**Step 1) server.xml 파일 내 Context 요소 allowLinking 옵션 설정**

```bash
vi /<Tomcat 설치 디렉터리>/conf/server.xml
```

```xml
<!-- 변경 전 (취약) -->
<Context allowLinking='true'>
    <WatchedResource>WEB-INF/web.xml</WatchedResource>
    <WatchedResource>WEB-INF/tomcat-web.xml</WatchedResource>
    <WatchedResource>${catalina.base}/conf/web.xml</WatchedResource>
</Context>

<!-- 변경 후 (양호) -->
<Context allowLinking='false'>
    <WatchedResource>WEB-INF/web.xml</WatchedResource>
    <WatchedResource>WEB-INF/tomcat-web.xml</WatchedResource>
    <WatchedResource>${catalina.base}/conf/web.xml</WatchedResource>
</Context>
```

**Step 2) Tomcat 재시작**

```bash
systemctl restart tomcat
```

#### Nginx

**Step 1) nginx.conf 파일 내 모든 디렉터리의 disable_symlinks on 설정 (기본값: 설정값 없음)**

```bash
vi /<Nginx 설치 디렉터리>/conf/nginx.conf
```

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        root   html;
        index  index.html index.htm;
        disable_symlinks on;  # 심볼릭 링크 비활성화
    }
}
```

**Step 2) Nginx 재시작**

```bash
systemctl restart nginx
```

**참고**: `disable_symlinks` 지시자는 Nginx 1.1.15 이상에서 사용 가능합니다.

#### IIS

**Step 1) 홈 디렉터리 바로가기 파일 확인 및 제거**

1. 제어판 > 관리 도구 > 인터넷 정보 서비스(IIS) 관리자 실행
2. 해당 웹사이트 선택 > 기본 설정 클릭
3. '실제 경로'로 설정된 경로로 이동
4. 바로가기 파일(`.lnk`) 확인 후 제거

<!-- ![홈 디렉터리 위치 확인](../images/04_웹서비스/image_0013.png) -->

**Step 2) 파일 탐색기에서 바로가기 파일 제거**

- 파일 탐색기에서 홈 디렉터리로 이동
- 모든 `.lnk` 파일 찾기 및 제거

#### JEUS

**Step 1) jeus-web-dd.xml 파일 내 alias 요소 설정 제거**

```bash
vi /<JEUS 설치 디렉터리>/WEB-INF/jeus-web-dd.xml
```

```xml
<!-- 변경 전 (취약) -->
<aliasing>
    <alias>
        <alias-name>/images/</alias-name>
        <real-path>/home/web/images/</real-path>
    </alias>
</aliasing>

<!-- 변경 후 (양호) - alias 요소 제거 또는 주석 처리 -->
<!--
<aliasing>
    <alias>
        <alias-name>/images/</alias-name>
        <real-path>/home/web/images/</real-path>
    </alias>
</aliasing>
-->
```

#### WebtoB

**Step 1) http.m 파일 내 ALIAS 절 요소 설정 제거**

```bash
vi /<WebtoB 설치 디렉터리>/config/http.m
```

```text
# 변경 전 (취약)
*ALIAS alias1
    URI = "/cgi-bin/"
    RealPath = "/home/tmax/webtob/cgi-bin/"

# 변경 후 (양호) - 주석 처리 또는 제거
#*ALIAS alias1
#    URI = "/cgi-bin/"
#    RealPath = "/home/tmax/webtob/cgi-bin/"
```

**Step 2) 설정 파일 컴파일 및 재구동**

```bash
wscfl -I http.m
wsdown
wsboot
```

### 7. 조치 시 주의사항

- 심볼릭 링크를 이용하여 웹페이지가 구성된 경우 해당 서비스가 실행되지 않을 수 있습니다.
- 변경 전에 심볼릭 링크 사용 여부를 확인하고 영향도를 평가해야 합니다.
- 실제 파일은 존재하고 링크만 제거하므로, 필요한 경우 실제 파일을 웹 루트 내로 복사해야 합니다.
- 설정 변경 후 웹사이트 정상 작동 여부를 테스트해야 합니다.

### 8. 참고 자료

- Apache Options Directive: https://httpd.apache.org/docs/current/mod/core.html#options
- Nginx disable_symlinks: https://nginx.org/en/docs/http/ngx_http_core_module.html#disable_symlinks
- CWE-59: Improper Link Resolution Before File Access ('Link Following')

## 요약

웹 서비스에서 심볼릭 링크, aliases, 바로가기 등의 링크 사용을 제한하여 경로 검증 우회를 방지하고 시스템 파일 접근을 차단해야 합니다.
