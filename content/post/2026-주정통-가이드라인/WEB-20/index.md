---
title: "[2026 주요정보통신기반시설] WEB-20 SSL/TLS활성화"
slug: "2026-주정통/WEB-20"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "SSL/TLS는 인터넷상에서 데이터를 암호화하여 전송하는 보안 프로토콜입니다. HTTPS(Hypertext Transfer Protocol Secure)는 HTTP를 SSL/TLS"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Web
draft: true
---

# WEB-20 SSL/TLS활성화

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | WEB-20 |
| **점검내용** | SSL/TLS는 인터넷상에서 데이터를 암호화하여 전송하는 보안 프로토콜입니다. HTTPS(Hypertext Transfer Protocol Secure)는 HTTP를 SSL/TLS |
| **점검대상** | Apache, Nginx, IIS, WebtoB |
| **판단기준** | 양호: SSL/TLS 설정이 활성화되어 있는 경우 |
| **판단기준** | 취약: SSL/TLS 설정이 비활성화되어 있는 경우 |
| **조치방법** | 상세 조치 방법 참고 |

---
---
## 상세 설명

### 1. 항목 개요

SSL/TLS는 인터넷상에서 데이터를 암호화하여 전송하는 보안 프로토콜입니다. HTTPS(Hypertext Transfer Protocol Secure)는 HTTP를 SSL/TLS로 암호화한 것으로, 사용자가 웹사이트에 입력하는 모든 정보(로그인, 비밀번호, 신용카드번호 등)를 보호합니다. 현대의 모든 웹사이트는 HTTPS를 사용하는 것이 필수적입니다. 마치 편지를 내용을 암호화해서 보내는 것과 같습니다.

### 2. 왜 이 항목이 필요한가요?

**실제 시나리오:**
- 사용자가 HTTP(평문) 웹사이트에 로그인합니다.
- 같은 네트워크에 있는 공격자가 Wireshark 같은 도구로 트래픽을 캡처합니다.
- 캡처한 패킷에서 로그인 정보를 추출합니다: `username=admin&password=P@ssw0rd`
- 공격자가 획득한 정보로 로그인하여 계정을 탈취합니다.

**HTTPS가 필요한 이유:**
- **데이터 기밀성**: 암호화로 도청 방지
- **데이터 무결성**: 변조 방지
- **서버 인증**: 피싱 사이트 방지
- **SEO 향상**: 구글 검색 순위 상승
- **사용자 신뢰**: 브라우저의 보안 연결 표시

**스니핑 공격 예시:**
```bash
# 같은 네트워크에서 공격자가 실행
tcpdump -i wlan0 -A 'tcp port 80'

# 캡처된 평문 데이터
POST /login HTTP/1.1
Host: example.com
username=admin&password=secret123
```

### 3. 점검 대상

- **Apache**: Apache HTTP Server
- **Nginx**: Nginx 웹 서버
- **IIS**: Microsoft Internet Information Services
- **WebtoB**: Tmax WebtoB 웹 서버

### 4. 판단 기준

- **양호**: SSL/TLS 설정이 활성화되어 있는 경우
- **취약**: SSL/TLS 설정이 비활성화되어 있는 경우

### 5. 점검 방법

#### 간단한 점검 방법

1. 웹 브라우저로 `https://your-domain.com` 접속
2. 주소창의 자물쇠 아이콘 확인
3. 자물쇠가 열려 있거나 "보안되지 않음" 표시가 있으면 취약

#### 명령줄 점검

```bash
# OpenSSL로 SSL 확인
openssl s_client -connect your-domain.com:443

# curl로 HTTPS 확인
curl -I https://your-domain.com
```

### 6. 조치 방법

#### Apache

**Step 1) SSL 모듈 활성화 확인**

```bash
apache2ctl -M | grep ssl
```

**출력 예시:**
```bash
ssl_module (shared)
```

**Step 2) SSL 가상 호스트 설정에 SSL 인증서 설정 추가**

```bash
vi /<Apache 설치 디렉터리>/sites-available/default-ssl.conf
```

```apache
<VirtualHost *:443>
    ServerAdmin webmaster@yourdomain.com
    ServerName yourdomain.com
    DocumentRoot /var/www/html

    SSLEngine on
    SSLCertificateFile /path/to/your_domain_name.crt
    SSLCertificateKeyFile /path/to/your_domain_name.key
    # SSLCertificateChainFile /path/to/DigiCertCA.crt

    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```

**Step 3) SSL 가상 호스트 활성화**

```bash
a2ensite default-ssl
```

**Step 4) Apache 재구동**

```bash
systemctl restart apache2
```

#### Nginx

**Step 1) SSL 인증서 파일 및 개인키 파일 준비**

Let's Encrypt 무료 인증서 발급 권장:
```bash
certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

**Step 2) nginx.conf 파일 내 SSL/TLS 설정**

```bash
vi /<Nginx 설치 디렉터리>/conf/nginx.conf
```

```nginx
# HTTP를 HTTPS로 리디렉션
server {
    listen 80;
    server_name example.com;
    return 301 https://$host$request_uri;
}

# HTTPS 서버 설정
server {
    listen 443 ssl;
    server_name example.com;

    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    # 보안 설정 권장
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';

    root /var/www/html;
    index index.html;
}
```

**Step 3) Nginx 재구동**

```bash
systemctl restart nginx
```

#### IIS

**Step 1) SSL 인증서 바인딩 설정**

1. 제어판 > 관리 도구 > IIS(인터넷 정보 서비스) 관리자 실행
2. 해당 웹사이트 선택 > [사이트 바인딩] > [편집] 탭 클릭
3. SSL 인증서 확인

<!-- ![SSL 인증서 확인](../images/04_웹서비스/image_0023.png) -->

**Step 2) SSL 인증서 가져오기**

1. 발급받은 인증서 > 인증서 설치
2. '로컬 컴퓨터' 선택 > 다음
3. '인증서 종류를 기준으로 인증서 저장소를 자동으로 선택' 선택 > 다음 > 마침

**Step 3) SSL 인증서 설치**

1. `C:\Windows\System32\mmc.exe` 실행
2. 파일 > 스냅인 추가/제거 > 인증서 추가
3. '이 스냅인이 항상 관리할 인증서 대상' '컴퓨터 계정' 선택
4. 로컬 컴퓨터 > 확인

<!-- ![SSL 인증서 추가 과정 1](../images/04_웹서비스/image_0024.png) -->
<!-- ![SSL 인증서 추가 과정 2](../images/04_웹서비스/image_0025.png) -->

**Step 4) 추가된 인증서 확인**

1. 콘솔 루트 > 인증서(로컬 컴퓨터) > 개인용 > 인증서
2. 발급된 인증서 확인

<!-- ![추가된 인증서 확인](../images/04_웹서비스/image_0026.png) -->

**Step 5) 인증서 등록**

1. IIS 관리자 > 서버 선택 우클릭 > '바인딩 편집' 선택
2. 추가 > 종류 'https', IP 주소, 포트(443), 호스트 이름, SSL 인증서 선택 > 확인

**Step 6) IIS 서버 재구동**

```powershell
iisreset
```

#### WebtoB

**Step 1) http.m 파일 내 SSLFlag, SSLName 설정 확인**

```bash
vi /<WebtoB 설치 디렉터리>/config/http.m
```

```text
*VHOST vhost1
    ERRORDOCUMENT = "400,401,403,404,405,406,503"
    SSLFLAG      = Y
    SSLNAME      = "ssl_nxcore"
    LOGGING      = "acc_https"
```

**Step 2) http.m 파일 내 인증서 설정 파일 확인**

```text
*SSL ssl_nxcore
    CertificateFile      = "/sw/webtob5/ssl/2023/cert.crt"
    CertificateKeyFile   = "/sw/webtob5/ssl/2023/privkey.key"
    CertificateChainFile = "/sw/webtob5/ssl/2023/chain.crt"
    CACertificateFile    = "/sw/webtob5/ssl/2023/rootca.crt"
    PassPhraseDialog     = "file:/sw/webtob5/ssl/passwd"
    Protocols            = "-SSLv2, -SSLv3, -TLSv1, -TLSv1.1, TLSv1.2, TLSv1.3"
    RequiredCiphers      = "HIGH:!RSA:!SHA1"
```

**Step 3) CA 인증서 및 개인키를 생성해 WebtoB 설정 파일에 설정**

### 7. 조치 시 주의사항

- 일반적인 경우 영향이 없습니다.
- SSL 인증서는 신뢰할 수 있는 인증 기관(CA)에서 발급받는 것을 권장합니다.
- Let's Encrypt와 같은 무료 인증서도 사용 가능합니다.
- HTTPS로 변경 시 HTTP 접속을 HTTPS로 자동 리디렉션하는 설정을 권장합니다.
- SSL 인증서 만료일을 모니터링해야 합니다.
- 취약한 SSL/TLS 프로토콜(SSLv2, SSLv3, TLSv1.0, TLSv1.1)은 비활성화하세요.
- HSTS(HTTP Strict Transport Security) 설정을 권장합니다.

### 8. 참고 자료

- Let's Encrypt: https://letsencrypt.org/
- Mozilla SSL Configuration Generator: https://ssl-config.mozilla.org/
- Apache SSL/TLS: https://httpd.apache.org/docs/current/ssl/
- Nginx HTTP SSL Module: https://nginx.org/en/docs/http/ngx_http_ssl_module.html
- IIS SSL Certificates: https://docs.microsoft.com/en-us/iis/manage/configuring-security/configuring-ssl-in-iis-manager

## 요약

웹서비스에 SSL/TLS를 활성화하여 데이터를 암호화 전송하고 스니핑 공격을 방지해야 합니다.
