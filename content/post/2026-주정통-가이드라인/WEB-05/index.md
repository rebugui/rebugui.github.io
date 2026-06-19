---
title: "[2026 주요정보통신기반시설] WEB-05 지정하지않은CGI/ISAPI실행제한"
slug: "2026-주정통/WEB-05"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "웹서비스CGI실행제한설정여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Web
draft: true
---

# WEB-05 지정하지않은CGI/ISAPI실행제한

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | WEB-05 |
| **점검내용** | 웹서비스CGI실행제한설정여부점검 |
| **점검대상** | Apache, Tomcat, Nginx, IIS, WebtoB |
| **판단기준** | 양호: CGI스크립트를사용하지않거나CGI스크립트가실행가능한디렉터리를제한한경우 |
| **판단기준** | 취약: CGI스크립트를사용하고CGI스크립트가실행가능한디렉터리를제한하지않은경우 |
| **조치방법** | CGI스크립트를정해진디렉터리내에서만실행할수있도록설정 |

---
## 상세 설명

### 1. 항목 개요

CGI(Common Gateway Interface)와 ISAPI(Internet Server Application Programming Interface)는 웹 서버에서 동적인 콘텐츠를 생성하기 위해 사용되는 프로그램 인터페이스입니다. 하지만 이러한 기능이 모든 디렉터리에서 실행 가능하다면, 공격자는 파일 업로드 취약점을 이용해 악성 CGI/ISAPI 파일을 업로드하고 실행하여 서버를 장악할 수 있습니다. 마치 건물 모든 입구에 보안 검사 없이 출입이 가능한 것과 같습니다. CGI/ISAPI 실행은 반드시 지정된 디렉터리로 제한해야 합니다.

### 2. 왜 이 항목이 필요한가요?

**실제 시나리오:**
- 공격자가 게시판이나 자료실의 파일 업로드 취약점을 발견합니다.
- 악성 CGI 스크립트(예: `shell.cgi`, `backdoor.pl`)를 업로드합니다.
- 업로드된 디렉터리에서 CGI 실행이 가능하므로, 웹 브라우저로 해당 파일에 접속하여 악성 코드를 실행합니다.
- 시스템 권한을 획득하여 서버를 장악합니다.

**CGI/ISAPI 실행으로 인한 위험:**
- 웹 쉘(Web Shell) 업로드 및 실행
- 시스템 명령어 injection 공격
- 파일 시스템 접근 및 데이터 유출
- 서버를 botnet으로 악용
- 다른 시스템으로의 공격 경로 제공

### 3. 점검 대상

- **Apache**: Apache HTTP Server
- **Tomcat**: Apache Tomcat 웹 서버
- **Nginx**: Nginx 웹 서버
- **IIS**: Microsoft Internet Information Services
- **WebtoB**: Tmax WebtoB 웹 서버

### 4. 판단 기준

- **양호**: CGI 스크립트를 사용하지 않거나 CGI 스크립트가 실행 가능한 디렉터리를 제한한 경우
- **취약**: CGI 스크립트를 사용하고 CGI 스크립트가 실행 가능한 디렉터리를 제한하지 않은 경우

### 5. 점검 방법

#### Apache

```bash
# CGI 모듈 확인
cat /<Apache 설치 디렉터리>/httpd.conf | grep -E "LoadModule.*cgi"

# ExecCGI 옵션 확인
grep -r "ExecCGI" /etc/apache2/
```

#### Tomcat

```bash
# CGI 서블릿 매핑 확인
cat /<Tomcat 설치 디렉터리>/conf/web.xml | grep -A 5 "cgi"
```

#### Nginx

```bash
# FastCGI 설정 확인
cat /<Nginx 설치 디렉터리>/conf/nginx.conf | grep "fastcgi"
```

### 6. 조치 방법

#### Apache

**Step 1) Apache 설정 파일 내 CGI 모듈 비활성화 또는 주석 처리**

```bash
vi /<Apache 설치 디렉터리>/httpd.conf (또는 apache.conf)
```

```apache
# CGI 모듈 주석 처리
#LoadModule cgi_module modules/mod_cgi.so
#LoadModule cgid_module modules/mod_cgid.so
```

**Step 2) 설정된 모든 디렉터리의 Options 지시자에서 ExecCGI 옵션 제거**

```bash
vi /<Apache 설치 디렉터리>/apache.conf (또는 httpd.conf)
```

```apache
<!-- 변경 전 (취약) -->
<Directory "/var/www/cgi-bin">
    Options ExecCGI
</Directory>

<!-- 변경 후 (양호) -->
<Directory "/var/www/cgi-bin">
    Options -ExecCGI
</Directory>

<!-- 업로드 디렉터리의 경우 반드시 제거 -->
<Directory "/var/www/html/uploads">
    Options -ExecCGI -Includes
    AllowOverride None
    Require all granted
</Directory>
```

**Step 3) Apache 재시작**

```bash
systemctl restart apache2
```

#### Tomcat

**Step 1) web.xml 파일 내 CGI 매핑 비활성화**

```bash
vi /<Tomcat 설치 디렉터리>/conf/web.xml
```

```xml
<!-- 변경 전 (취약) -->
<servlet-mapping>
    <servlet-name>cgi</servlet-name>
    <url-pattern>/cgi-bin/*</url-pattern>
</servlet-mapping>

<!-- 변경 후 (양호) - 주석 처리 -->
<!--
<servlet-mapping>
    <servlet-name>cgi</servlet-name>
    <url-pattern>/cgi-bin/*</url-pattern>
</servlet-mapping>
-->
```

**Step 2) Tomcat 재시작**

```bash
systemctl restart tomcat
```

#### Nginx

**Step 1) nginx.conf 파일 내 FastCGI 사용 여부 확인**

```bash
cat /<Nginx 설치 디렉터리>/conf/nginx.conf
```

```nginx
# CGI 실행 설정이 있다면 주석 처리 또는 제거
# location ~ \.cgi$ {
#     fastcgi_pass <FastCGI 서버 주소>:<FastCGI 서버 통신 포트>;
#     include fastcgi_params;
# }
```

**Step 2) Nginx 재시작**

```bash
systemctl restart nginx
```

#### IIS

**Step 1) CGI/ISAPI 모듈 설정 해제**

1. IIS 관리자 실행
2. 서버 선택 > ISAPI 및 CGI 제한 더블클릭
3. 사용하지 않는 CGI/ISAPI 항목 선택 후 '허용 안 함'으로 설정

<!-- ![CGI/ISAPI 모듈 설정 확인](../images/04_웹서비스/image_0006.png) -->

**Step 2) 처리기 매핑에서 불필요한 매핑 제거**

1. 해당 웹사이트 선택 > 처리기 매핑 더블클릭
2. 불필요한 CGI/ISAPI 확장자 매핑 제거

#### WebtoB

**Step 1) http.m 파일 내 CGI 설정 제거 또는 비활성화**

```bash
vi /<WebtoB 설치 디렉터리>/config/http.m
```

```text
*SVRGROUP
htmlg   SVRTYPE = HTML
#cgig    SVRTYPE = CGI  # 주석 처리
ssig    SVRTYPE = SSI
jsvg    SVRTYPE = JSV

*SERVER
#cgi    SVGNAME = cgig, MinProc = 2, MaxProc = 10  # 주석 처리

*URI
#uri1   Uri = "/cgi-bin/", Svrtype = CGI  # 주석 처리
```

**Step 2) 설정 파일 컴파일 및 재구동**

```bash
wscfl -I http.m
wsdown
wsboot
```

**참고**: 필요한 경우 해당 디렉터리만 제한적으로 CGI 스크립트 실행 설정을 적용할 수 있습니다.

### 7. 조치 시 주의사항

- 해당 디렉터리 확인 후 추가적인 파일이 없다면 영향이 없습니다.
- CGI를 사용하는 서비스가 있는 경우, 반드시 `/cgi-bin/`과 같이 지정된 디렉터리에서만 실행되도록 제한해야 합니다.
- 업로드 디렉터리, 임시 디렉터리에서는 CGI 실행을 반드시 차단해야 합니다.
- 설정 변경 후 정상 서비스에 영향이 없는지 충분히 테스트해야 합니다.

### 8. 참고 자료

- Apache CGI Tutorial: https://httpd.apache.org/docs/current/howto/cgi.html
- IIS CGI Configuration: https://docs.microsoft.com/en-us/iis/configuration/system.webServer/cgi
- CWE-94: Improper Control of Generation of Code ('Code Injection')

## 요약

CGI/ISAPI 스크립트 실행을 지정된 디렉터리로 제한하여 파일 업로드 취약점을 통한 악성 코드 실행을 방지해야 합니다.
