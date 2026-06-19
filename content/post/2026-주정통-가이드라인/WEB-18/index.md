---
title: "[2026 주요정보통신기반시설] WEB-18 웹서비스WebDAV비활성화"
slug: "2026-주정통/WEB-18"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "WebDAV(Web Distributed Authoring and Versioning)는 웹을 통해 원격으로 파일을 읽고 쓸 수 있는 프로토콜입니다. 편리하지만 수많은 보안 취약점"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Web
draft: true
---

# WEB-18 웹서비스WebDAV비활성화

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | WEB-18 |
| **점검내용** | WebDAV(Web Distributed Authoring and Versioning)는 웹을 통해 원격으로 파일을 읽고 쓸 수 있는 프로토콜입니다. 편리하지만 수많은 보안 취약점 |
| **점검대상** | Apache, Nginx, IIS, WebtoB |
| **판단기준** | 양호: WebDAV 서비스를 비활성화하고 있는 경우 |
| **판단기준** | 취약: WebDAV 서비스를 활성화하고 있는 경우 |
| **조치방법** | 상세 조치 방법 참고 |

---
---
## 상세 설명

### 1. 항목 개요

WebDAV(Web Distributed Authoring and Versioning)는 웹을 통해 원격으로 파일을 읽고 쓸 수 있는 프로토콜입니다. 편리하지만 수많은 보안 취약점이 발견되어 왔으며, 특히 인증 우회, 버퍼 오버플로우 등의 심각한 문제가 있습니다. 대부분의 웹사이트는 WebDAV가 필요 없으므로 비활성화하는 것이 좋습니다. 마치 집에 특별한 방문객만 위한 출입문을 만들어두었는데 그 자물쇠가 고장된 것과 같습니다.

### 2. 왜 이 항목이 필요한가요?

**실제 시나리오:**
- 웹 서버에 WebDAV가 활성화되어 있습니다.
- 공격자가 WebDAV의 인증 우회 취약점을 발견합니다.
- 인증 없이 WebDAV 리소스에 접근하여 파일을 다운로드하거나 업로드합니다.
- 악성 파일을 업로드하거나 중요 설정 파일을 탈취합니다.

**WebDAV 주요 취약점:**
- **인증 우회**: IIS 5.0/6.0 WebDAV 인증 우회 취약점
- **버퍼 오버플로우**: 악의적인 PROPFIND 요청으로 서버 다운
- **무차별 대입 공격**: WebDAV를 통한 자격증명 공격
- **파일 업로드**: 악성코드, 웹쉘 업로드 경로

**공격 유형:**
```
1. WebDAV 활성화 확인
2. OPTIONS / HTTP/1.1 요청으로 메서드 확인
3. PROPFIND, PUT, DELETE, MKCOL 등 WebDAV 메서드 테스트
4. 인증 우회 취약점 공격
5. 파일 열람, 다운로드, 업로드, 삭제
```

### 3. 점검 대상

- **Apache**: Apache HTTP Server
- **Nginx**: Nginx 웹 서버
- **IIS**: Microsoft Internet Information Services
- **WebtoB**: Tmax WebtoB 웹 서버

### 4. 판단 기준

- **양호**: WebDAV 서비스를 비활성화하고 있는 경우
- **취약**: WebDAV 서비스를 활성화하고 있는 경우

### 5. 점검 방법

#### 간단한 점검 방법

```bash
# curl로 WebDAV 메서드 확인
curl -X OPTIONS http://your-domain.com/

# 또는
curl -I -X PROPFIND http://your-domain.com/
```

**WebDAV가 활성화된 경우 응답:**
```http
HTTP/1.1 200 OK
Allow: GET, HEAD, POST, PUT, DELETE, OPTIONS, PROPFIND, PROPPATCH, MKCOL, COPY, MOVE, LOCK, UNLOCK
```

#### Apache

```bash
# DAV 모듈 확인
apache2ctl -M | grep dav

# 설정 확인
grep -r "Dav" /etc/apache2/
```

#### IIS

IIS 관리자 > ISAPI 및 CGI 제한에서 WebDAV 확인

### 6. 조치 방법

#### Apache

**Step 1) httpd.conf 파일 내 모든 디렉터리에서 WebDAV 설정 확인**

```bash
cat /<Apache_Dir>/conf/httpd.conf (또는 apache2.conf)
```

```apache
<!-- WebDAV 활성화 확인 -->
<Directory "/path/to/directory">
    Dav On
</Directory>
```

**Step 2) 모든 디렉터리에서 WebDAV 설정 비활성화 또는 주석 처리**

```bash
vi /<Apache_Dir>/conf/httpd.conf (또는 apache2.conf)
```

```apache
<!-- 변경 후 (양호) -->
<Directory "/path/to/directory">
    Dav Off
</Directory>
```

**Step 3) Apache 재구동**

```bash
systemctl restart apache2
```

#### Nginx

**Step 1) nginx.conf 파일 내 모든 디렉터리에서 WebDAV 설정 확인**

```bash
cat /<Nginx 설치 디렉터리>/conf/nginx.conf
```

```nginx
location /webdav {
    root /path/to/webdav;
    dav_methods PUT DELETE MKCOL COPY MOVE;
    dav_access user:rw group:rw all:r;
    create_full_put_path on;
}
```

**Step 2) nginx.conf 파일 내 모든 디렉터리에서 WebDAV 설정 주석 처리 또는 제거**

```bash
vi /<Nginx 설치 디렉터리>/conf/nginx.conf
```

```nginx
# 변경 후 (양호) - 주석 처리
#location /webdav {
#    root /path/to/webdav;
#    dav_methods PUT DELETE MKCOL COPY MOVE;
#    dav_access user:rw group:rw all:r;
#    create_full_put_path on;
#}
```

**Step 3) Nginx 재구동**

```bash
systemctl restart nginx
```

#### IIS

**Step 1) WebDAV 금지 설정 확인**

1. 제어판 > 관리 도구 > 인터넷 정보 서비스(IIS) 관리자 실행
2. 서버 선택 > IIS > 'ISAPI 및 CGI 제한' 더블클릭
3. WebDAV 항목 선택 > '확장 경로 실행 허용(A)' 체크 확인

<!-- ![WebDAV 제한 설정](../images/04_웹서비스/image_0019.png) -->

**Step 2) WebDAV 금지 설정 적용**

1. IIS 관리자 > 서버 선택 > IIS > 'ISAPI 및 CGI 제한' 선택
2. WebDAV 항목 선택
3. [작업]에서 제거하거나, 편집 클릭
4. '확장 경로 실행 허용(A)' 체크 해제
5. 확인 클릭

<!-- ![WebDAV 제한 설정](../images/04_웹서비스/image_0020.png) -->

**Step 3) IIS 재시작**

```powershell
iisreset
# 또는
Restart-Service W3SVC
```

#### WebtoB

**Step 1) Server 설정 파일 내 NODE 절 vhost 메소드 설정 확인**

```bash
vi /<WebtoB 설치 디렉터리>/config/http.m
```

```text
*VHOST vhost1
    Method = 'GET, POST, HEAD, OPTIONS, PROPFIND, PUT, DELETE, MKCOL, COPY, MOVE'
```

**Step 2) NODE 절 WebDAV 설정 삭제**

```text
# 변경 후 (양호)
*VHOST vhost1
    Method = 'GET, POST, HEAD, OPTIONS'
```

**Step 3) 설정 파일 컴파일 및 재구동**

```bash
wscfl -I http.m
wsdown
wsboot
```

### 7. 조치 시 주의사항

- 일반적인 경우 영향이 없습니다.
- WebDAV가 실제로 필요한 서비스인 경우(파일 공유, 오피스 통합 등)에는 비활성화하지 마세요.
- WebDAV가 필요한 경우 강력한 인증(SSL/TLS, 2단계 인증)과 IP 제한을 적용하세요.
- 변경 후 파일 공유 기능이 필요한 사용자에게 영향이 없는지 확인해야 합니다.
- 정기적으로 WebDAV가 재활성화되지 않았는지 감사해야 합니다.

### 8. 참고 자료

- Apache mod_dav: https://httpd.apache.org/docs/current/mod/mod_dav.html
- Nginx ngx_http_dav_module: https://nginx.org/en/docs/http/ngx_http_dav_module.html
- IIS WebDAV: https://docs.microsoft.com/en-us/iis/configuration/system.webServer/webdav
- CVE-2017-7269 (IIS WebDAV RCE)

## 요약

WebDAV 서비스를 비활성화하여 인증 우회, 버퍼 오버플로우 등의 알려진 취약점을 통한 공격을 방지해야 합니다.
