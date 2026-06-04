---
title: "[2026 주요정보통신기반시설] WEB-16 웹서비스헤더정보노출제한"
slug: "2026-주정통/WEB-16"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "HTTP 응답 헤더에는 웹 서버의 종류, 버전, 운영체제 정보 등이 포함될 수 있습니다. 이 정보는 공격자에게 매우 유용한 정보원입니다. 예를 들어 `Server: Apache/2"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Web
---

# WEB-16 웹서비스헤더정보노출제한

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | WEB-16 |
| **점검내용** | HTTP 응답 헤더에는 웹 서버의 종류, 버전, 운영체제 정보 등이 포함될 수 있습니다. 이 정보는 공격자에게 매우 유용한 정보원입니다. 예를 들어 `Server: Apache/2 |
| **점검대상** | Apache, Tomcat, Nginx, IIS, JEUS, Webtob |
| **판단기준** | 양호: HTTP 응답 헤더에서 웹서버 정보가 노출되지 않는 경우 |
| **판단기준** | 취약: HTTP 응답 헤더에서 웹서버 정보가 노출되는 경우 |
| **조치방법** | 상세 조치 방법 참고 |

---
---
## 상세 설명

### 1. 항목 개요

HTTP 응답 헤더에는 웹 서버의 종류, 버전, 운영체제 정보 등이 포함될 수 있습니다. 이 정보는 공격자에게 매우 유용한 정보원입니다. 예를 들어 `Server: Apache/2.4.41 (Ubuntu)` 헤더는 공격자에게 Apache 2.4.41 버전이 Ubuntu에서 실행 중이라는 것을 알려줍니다. 마치 집 현관문에 "우리 집 보안 시스템은 OO사 20년형입니다"라고 적어두는 것과 같습니다.

### 2. 왜 이 항목이 필요한가요?

**실제 시나리오:**
- 공격자가 웹사이트에 접속합니다.
- HTTP 응답 헤더에서 `Server: Apache/2.4.41 (Ubuntu)`를 확인합니다.
- Apache 2.4.41의 알려진 취약점(CVE-2021-XXXX 등)을 검색합니다.
- 해당 버전에 맞는 익스플로잇 코드를 준비합니다.
- 취약점을 공격하여 시스템을 장악합니다.

**헤더 정보 노출 위험성:**
- **버전 특정 공격**: 특정 버전의 취약점 악용
- **OS 정보 노출**: 운영체제 특정 공격 가능
- **구조 파악**: 시스템 구조 및 설정 추정
- **공격 표면 축소**: 공격자의 정보 획득 경로 차단

**실제 헤더 예시:**
```
# 취약한 경우
Server: Apache/2.4.41 (Ubuntu)
X-Powered-By: PHP/7.4.3

# 양호한 경우
Server: Apache
X-Powered-By: (삭제)
```

### 3. 점검 대상

- **Apache**: Apache HTTP Server
- **Tomcat**: Apache Tomcat 웹 서버
- **Nginx**: Nginx 웹 서버
- **IIS**: Microsoft Internet Information Services
- **JEUS**: Tmax JEUS 웹 애플리케이션 서버
- **Webtob**: Tmax WebtoB 웹 서버

### 4. 판단 기준

- **양호**: HTTP 응답 헤더에서 웹서버 정보가 노출되지 않는 경우
- **취약**: HTTP 응답 헤더에서 웹서버 정보가 노출되는 경우

### 5. 점검 방법

#### 간단한 점검 방법

```bash
# curl 명령어로 헤더 확인
curl -I http://your-domain.com

# 또는
wget --server-response --spider http://your-domain.com
```

**출력 예시:**
```http
HTTP/1.1 200 OK
Date: Mon, 20 Jan 2026 00:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)  # 취약 - 버전 정보 노출
X-Powered-By: PHP/7.4.3         # 취약 - PHP 버전 노출
```

#### 웹 브라우저 개발자 도구

1. F12 키로 개발자 도구 열기
2. Network 탭 클릭
3. 페이지 새로고침
4. 첫 번째 요청 선택 > Headers 탭 > Response Headers 확인

### 6. 조치 방법

#### Apache

**Step 1) httpd.conf (또는 apache2.conf) 파일 내 모든 디렉터리에 ServerTokens, ServerSignature 옵션 설정**

```bash
vi /<Apache 설치 디렉터리>/conf/httpd.conf (또는 apache2.conf)
```

```apache
<Directory />
    ServerTokens Prod
    ServerSignature Off
</Directory>
```

**ServerTokens 지시자 옵션:**

| 옵션   | 제공하는 정보                  | 예문                                   |
|--------|---------------------------|--------------------------------------|
| Prod   | 웹서버 종류                    | Apache                               |
| Min    | 웹서버 버전                    | Apache/2.2.3                         |
| OS     | 웹서버 버전 + 운영체제              | Apache/2.2.3 (CentOS) 기본값             |
| Full   | 웹서버의 모든 정보                 | Apache/2.2.3 (CentOS) DAV/2 PHP/5.16 |

**Step 2) Apache 재시작**

```bash
systemctl restart apache2
```

#### Tomcat

**Step 1) server.xml 파일 내 server 값을 임의 정보로 변경**

```bash
vi /<Tomcat 설치 디렉터리>/conf/server.xml
```

```xml
<!-- 변경 전 -->
<Connector port="8080" protocol="HTTP/1.1"
           connectionTimeout="20000"
           redirectPort="8443" />

<!-- 변경 후 -->
<Connector port="8080" protocol="HTTP/1.1"
           connectionTimeout="20000"
           redirectPort="8443"
           server="MyServer" />  <!-- 임의 정보로 변경 -->
```

**Step 2) server.xml 파일 내 ErrorReportValve 설정**

```bash
vi /<Tomcat 설치 디렉터리>/conf/server.xml
```

```xml
<Host>
    ...
    <Valve className="org.apache.catalina.valves.ErrorReportValve"
           showReport="true"
           showServerInfo="false" />
    ...
</Host>
```

#### Nginx

**Step 1) nginx.conf 파일 내 server_tokens 값을 'off'로 설정**

```bash
vi /<Nginx 설치 디렉터리>/conf/nginx.conf
```

```nginx
http {
    server_tokens off;  # 서버 토큰 비활성화
}

# 또는
server {
    listen 80;
    server_tokens off;
}
```

**Step 2) Nginx 재시작**

```bash
systemctl restart nginx
```

#### IIS

**Step 1) 오류 페이지 설정 편집**

1. 제어판 > 관리 도구 > IIS(인터넷 정보 서비스) 관리자 실행
2. 해당 웹 사이트 선택
3. [오류 페이지] 더블클릭
4. [작업] 탭에서 [기능 설정 편집] 클릭
5. '서버 오류 발생 시 다음 반환' 항목을 '사용자 지정 오류 페이지'로 설정

<!-- ![오류 페이지 설정 편집](../images/04_웹서비스/image_0018.png) -->

**Step 2) URL Rewrite 모듈 설치 후 응답 헤더 제거**

```xml
<system.webServer>
    <rewrite>
        <outboundRules>
            <rule name="Remove Server header">
                <match serverVariable="RESPONSE_Server" pattern=".*" />
                <action type="Rewrite" value="" />
            </rule>
        </outboundRules>
    </rewrite>
</system.webServer>
```

#### JEUS

**JEUS 7 이전 버전:**

**Step 1) JEUSMain.xml 파일 내 설정 추가**

```bash
vi /<JEUS 설치 디렉터리>/config/JEUSMain.xml
```

```xml
<jeus-system>
    <node>
        ...
        <engine-container>
            ...
            <command-option>-Djeus.servlet.response.header.serverInfo=false</command-option>
        </engine-container>
        ...
    </node>
</jeus-system>
```

**JEUS 7:**

**Step 2) domain.xml 파일 내 설정 추가**

```bash
vi /<JEUS 설치 디렉터리>/config/domain.xml
```

```xml
<response-header>
    <custom-header>
        <header-field>
            <field-name>P3P</field-name>
            <field-value>CP='CAO PSA CONi OTR OUR DEM ONL'</field-value>
        </header-field>
    </custom-header>
</response-header>
```

#### WebtoB

**Step 1) http.m 파일 내 ServerTokens 지시자 확인 (기본값: off)**

```bash
cat /<WebtoB 설치 디렉터리>/config/http.m | grep -i 'ServerTokens'
```

**Step 2) 설정 파일 내부 지시자 옵션 설정**

```bash
vi /<WebtoB 설치 디렉터리>/config/http.m
```

```text
ServerTokens ProductOnly(Prod)
ServerSignature off  # Off: Response Header에 server 필드를 사용하지 않음
```

**ServerTokens 옵션별 반환 정보:**

| 구분          | 반환되는 헤더 정보                                    |
|-------------|-----------------------------------------------|
| Prod[uctOnly] | WebtoB                                        |
| Min[imal]   | WebtoB/4.1.3                                  |
| OS          | WebtoB/4.1.3 LINUX-K2.6_x86 libc2.3         |
| Full        | WebtoB/4.1.3 LINUX-K2.6_x86 libc2.3         |
| Custom      | user-specified-name                          |

### 7. 조치 시 주의사항

- 일반적인 경우 영향이 없습니다.
- 모니터링 도구나 로그 분석 도구가 서버 정보를 사용하는 경우 영향이 있을 수 있습니다.
- 설정 변경 후 헤더 정보를 확인하여 제대로 적용되었는지 검증해야 합니다.
- X-Powered-By 헤더도 함께 제거하는 것을 권장합니다.
- 에러 페이지에서도 서버 정보가 노출되지 않도록 별도의 에러 페이지를 구성해야 합니다.

### 8. 참고 자료

- Apache ServerTokens: https://httpd.apache.org/docs/current/mod/core.html#servertokens
- Nginx server_tokens: https://nginx.org/en/docs/http/ngx_http_core_module.html#server_tokens
- OWASP Information Exposure: https://cwe.mitre.org/data/definitions/200.html

## 요약

HTTP 응답 헤더에서 웹서버 버전 및 OS 정보를 최소화하여 공격자의 정보 수집을 차단하고 버전 특정 공격을 방지해야 합니다.
