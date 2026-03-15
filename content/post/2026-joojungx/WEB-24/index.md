---
title: "[2026 주요정보통신기반시설] WEB-24 별도의업로드경로사용및권한설정"
slug: "2026-주정통/WEB-24"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "파일 업로드 기능은 웹 애플리케이션에서 필수적이지만 동시에 보안 위협의 주요 경로이기도 합니다. 업로드된 파일이 웹 루트 디렉터리에 저장되면 공격자는 악성 스크립트를 업로드하고 실"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Web
---

# WEB-24 별도의업로드경로사용및권한설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | WEB-24 |
| **점검내용** | 파일 업로드 기능은 웹 애플리케이션에서 필수적이지만 동시에 보안 위협의 주요 경로이기도 합니다. 업로드된 파일이 웹 루트 디렉터리에 저장되면 공격자는 악성 스크립트를 업로드하고 실 |
| **점검대상** | Apache, Tomcat, Nginx, IIS, JEUS, WebtoB |
| **판단기준** | 양호: 별도의 업로드 경로를 사용하고 일반 사용자의 접근 권한이 부여되지 않은 경우 |
| **판단기준** | 취약: 별도의 업로드 경로를 사용하지 않거나, 일반 사용자의 접근 권한이 부여된 경우 |
| **조치방법** | 상세 조치 방법 참고 |

---
---
## 상세 설명

### 1. 항목 개요

파일 업로드 기능은 웹 애플리케이션에서 필수적이지만 동시에 보안 위협의 주요 경로이기도 합니다. 업로드된 파일이 웹 루트 디렉터리에 저장되면 공격자는 악성 스크립트를 업로드하고 실행하여 서버를 장악할 수 있습니다. 별도의 업로드 디렉터리를 사용하고 실행 권한을 제한하는 것은 파일 업로드 취약점 악용을 방지하는 핵심 설정입니다. 마치 집 안에 위험물질 보관 창고를 따로 두고 출입을 통제하는 것과 같습니다.

### 2. 왜 이 항목이 필요한가요?

**실제 시나리오:**
- 웹사이트의 파일 업로드 기능이 웹 루트(`/var/www/html/uploads`)에 파일을 저장합니다.
- 공격자가 악성 PHP 스크립트(`shell.php`)를 업로드합니다.
- 웹 루트 내에 있으므로 `http://example.com/uploads/shell.php` URL로 접근하여 실행합니다.
- 웹쉘이 실행되어 서버 권한을 탈취합니다.

**업로드 파일 실행 위험성:**
- **웹쉘 업로드**: PHP, JSP, ASP 등 악성 스크립트 실행
- **시스템 장악**: 웹쉘을 통한 서버 장악
- **데이터 유출**: 파일 시스템 접근, 데이터베이스 탈취
- **서비스 거부**: 대용량 파일 업로드로 디스크 가득 참
- **영구적 백도어**: 후문, 악성코드 설치

### 3. 점검 대상

- **Apache**: Apache HTTP Server
- **Tomcat**: Apache Tomcat 웹 서버
- **Nginx**: Nginx 웹 서버
- **IIS**: Microsoft Internet Information Services
- **JEUS**: Tmax JEUS 웹 애플리케이션 서버
- **WebtoB**: Tmax WebtoB 웹 서버

### 4. 판단 기준

- **양호**: 별도의 업로드 경로를 사용하고 일반 사용자의 접근 권한이 부여되지 않은 경우
- **취약**: 별도의 업로드 경로를 사용하지 않거나, 일반 사용자의 접근 권한이 부여된 경우

### 5. 점검 방법

#### 간단한 점검 방법

1. 웹사이트의 파일 업로드 기능 사용
2. 업로드된 파일이 저장되는 경로 확인
3. 해당 경로가 웹 루트 외부인지 확인
4. 해당 경로에서 스크립트 실행이 가능한지 확인

#### Linux 계열

```bash
# 업로드 디렉터리 위치 확인
find /var/www/html -type d -name "uploads"
find /home/web -type d -name "uploads"

# 권한 확인
ls -la /var/www/html/uploads
```

#### Windows (IIS)

IIS 관리자 > 해당 웹사이트 > 기본 설정 > 실제 경로 확인

### 6. 조치 방법

#### Apache

**Step 1) apache2.conf 파일 내 업로드 경로 및 웹서비스 디렉터리 경로 확인**

```bash
vi /<Apache 설치 디렉터리>/apache2/apache2.conf (또는 apache2.conf)
```

```apache
<!-- 변경 전 (취약) -->
<!-- 업로드 경로가 웹 루트 내부 -->
DocumentRoot /var/www/html
```

**Step 2) 별도 업로드 경로 생성**

```bash
mkdir [웹서비스 디렉터리 외 경로]
mkdir /home/web/uploads
```

**Step 3) 파일 실행 권한 확인**

```bash
ls -la /[Apache 업로드 디렉터리]
```

**Step 4) 업로드 디렉터리 권한 설정**

```bash
chmod 750 /home/web/uploads/
chown www-data:www-data /home/web/uploads/
```

**Step 5) apache2.conf 파일 내 업로드 디렉터리 접근제한 설정**

```bash
vi /<Apache 설치 디렉터리>/apache2/apache2.conf
```

```apache
<!-- 업로드 디렉터리 접근 제한 -->
<Directory "/home/web/uploads">
    # PHP 실행 차단
    <FilesMatch "\.php$">
        Order Allow,Deny
        Deny from all
    </FilesMatch>

    # 스크립트 실행 차단
    Options -ExecCGI

    AllowOverride None
    Require all denied
</Directory>
```

#### Tomcat

**Step 1) server.xml 파일 내 Context 요소 allowLinking 옵션 설정 (기본값: 업로드 디렉터리 경로 존재하지 않음)**

```bash
vi /<Tomcat 설치 디렉터리>/conf/context.xml
```

```xml
<!-- Servlet 설정 예시 -->
<servlet>
    <servlet-name>fileUploadServlet</servlet-name>
    <servlet-class>com.example.FileUploadServlet</servlet-class>
    <init-param>
        <param-name>uploadDir</param-name>
        <param-value>/home/web/uploads</param-value>
    </init-param>
</servlet>
```

**Step 2) 별도의 업로드 경로 생성**

```bash
mkdir [웹서비스 디렉터리 외 경로]
mkdir /home/web/uploads
```

**Step 3) 업로드 디렉터리 권한 설정**

```bash
chmod 750 /home/web/uploads
chown tomcat:tomcat /home/web/uploads
```

**Step 4) 지정한 디렉터리 권한을 웹 서비스에서 사용**

애플리케이션 코드에서 업로드 경로를 `/home/web/uploads`로 설정

#### Nginx

**Step 1) nginx.conf 파일 내 업로드 경로 확인 및 웹서비스 디렉터리 경로 사용 여부 확인**

```bash
vi /<Nginx 설치 디렉터리>/conf/nginx.conf
```

**Step 2) 별도의 업로드 경로 생성**

```bash
mkdir [웹서비스 디렉터리 외 경로]
mkdir /home/web/uploads
```

**Step 3) 업로드 디렉터리의 권한 설정**

```bash
chmod 750 /home/web/uploads
chown www-data:www-data /home/web/uploads
```

**Step 4) nginx.conf 파일 내 업로드 디렉터리 접근제한 설정**

```bash
vi /<Nginx 설치 디렉터리>/conf/nginx.conf
```

```nginx
location /uploads/ {
    alias /home/web/uploads/;
    autoindex off;

    # PHP 실행 차단
    location ~ \.php$ {
        deny all;
    }
}
```

**Step 5) 변경된 설정 내용을 적용하기 위하여 Nginx 데몬 재구동**

```bash
systemctl restart nginx
```

#### IIS

**Step 1) 실제 경로에 입력된 홈 디렉터리로 업로드 디렉터리 확인**

1. 제어판 > 관리 도구 > 인터넷 정보 서비스(IIS) 관리자 실행
2. 해당 웹사이트 > 기본 설정 > '실제 경로'에서 홈 디렉터리 확인

<!-- ![홈 디렉터리 위치 확인](../images/04_웹서비스/image_0029.png) -->

**Step 2) 웹 서비스 외부에 업로드 디렉터리를 생성**

1. 파일 탐색기에서 `D:\Uploads` 등 별도 경로 생성
2. '새 폴더' 클릭 > 이름 지정

**Step 3) 새로 생성한 폴더에 대한 권한 설정**

1. 외부 업로드 파일 우클릭 > 속성 > 보안 탭
2. 편집 클릭
3. IIS 구동 계정 그룹 추가 및 쓰기 권한 부여 설정

#### JEUS

**Step 1) web.xml 파일 내 파일 업로드 경로 확인**

```bash
vi /<JEUS 설치 디렉터리>/conf/web.xml (또는 webcommon.xml)
```

```xml
<context-param>
    <param-name>uploadDir</param-name>
    <param-value>/path/to/your/upload/directory</param-value>
</context-param>
```

**Step 2) 파일 업로드 경로 권한 확인**

```bash
ls -la /<JEUS 업로드 디렉터리>
```

**Step 3) 업로드 디렉터리 권한 설정**

```bash
chmod 750 /<JEUS 업로드 디렉터리>
chown jeus:jeus /<JEUS 업로드 디렉터리>
```

#### WebtoB

**Step 1) http.m 파일 내 파일 업로드 경로 확인**

```bash
cat /root/webtob/config/http.m
```

```text
*ALIAS alias_upload
    URI = "/upload/"
    RealPath = "/home/tmax/webtob/uploads/"
```

**Step 2) 파일 업로드 경로 권한 확인**

```bash
ls -la /<WebtoB 업로드 디렉터리>
```

**Step 3) 업로드 디렉터리의 권한 설정**

```bash
chmod 750 /<WebtoB 엔업로드 디렉터리>
chown tmax:tmax /<WebtoB 업로드 디렉터리>
```

### 7. 조치 시 주의사항

- 일반적인 경우 영향이 없습니다.
- 업로드 디렉터리는 웹 루트 외부에 위치하는 것이 가장 안전합니다.
- 업로드된 파일의 실행을 반드시 차단해야 합니다.
- 업로드 파일 크기 제한, 파일 형식 검증 등 애플리케이션 레벨의 보안도 필요합니다.
- 정기적으로 업로드 디렉터리를 스캔하여 악성 파일이 없는지 확인해야 합니다.
- 변경 후 파일 업로드가 정상 작동하는지 테스트해야 합니다.

### 8. 참고 자료

- Apache File Upload: https://httpd.apache.org/docs/current/howto/htaccess.html
- OWASP Unrestricted File Upload: https://owasp.org/www-community/vulnerabilities/Unrestricted_File_Upload
- CWE-434: Unrestricted Upload of File with Dangerous Type

## 요약

별도의 업로드 경로를 지정하고 일반 사용자의 접근 권한을 제한하여 악성 파일 업로드 및 실행을 방지해야 합니다.
