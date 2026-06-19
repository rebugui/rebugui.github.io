---
title: "[2026 주요정보통신기반시설] WEB-06 웹서비스상위디렉터리접근제한설정"
slug: "2026-주정통/WEB-06"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "'..'와같은문자사용등을통한상위디렉터리접근제한여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Web
draft: true
---

# WEB-06 웹서비스상위디렉터리접근제한설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | WEB-06 |
| **점검내용** | '..'와같은문자사용등을통한상위디렉터리접근제한여부점검 |
| **점검대상** | Apache, Tomcat, Nginx, IIS, WebtoB |
| **판단기준** | 양호: 상위디렉터리접근기능을제거한경우 |
| **판단기준** | 취약: 상위디렉터리접근기능을제거하지않은경우 |
| **조치방법** | 상위디렉터리접근기능제거설정 |

---
## 상세 설명

### 1. 항목 개요

경로 순회(Path Traversal) 공격은 웹 애플리케이션에서 사용자 입력을 적절하게 검증하지 않아 발생하는 취약점입니다. 공격자는 `../` (또는 `..\`)와 같은 문자열을 사용하여 웹 서버의 문서 루트 디렉터리를 벗어나 시스템의 다른 부분에 접근할 수 있습니다. 마치 건물의 특정 방에서 출발해 계단을 통해 다른 층으로 이동하는 것과 같습니다. 상위 디렉터리 접근을 제한하는 것은 웹 서비스의 핵심 보안 설정입니다.

### 2. 왜 이 항목이 필요한가요?

**실제 시나리오:**
- 공격자가 다음과 같은 URL로 접근을 시도합니다:
  - `http://example.com/download?file=../../../../etc/passwd`
  - `http://example.com/images?file=..\..\..\windows\system32\config\sam`
- 웹 서버가 경로 검증을 하지 않아 시스템 파일에 접근합니다.
- 중요 설정 파일, 비밀번호 파일, 데이터베이스 파일 등을 탈취합니다.

**경로 순회 공격 패턴:**
- `../` - 상위 디렉터리 이동 (Unix/Linux)
- `..\` - 상위 디렉터리 이동 (Windows)
- `....//` - URL 인코딩 우회
- `%2e%2e%2f` - URL 인코딩된 `../`
- `..%255c` - Unicode 인코딩 우회

**보안 위협:**
- 시스템 설정 파일 유출 (/etc/passwd, web.config 등)
- 비밀번호 파일 접근 (.htpasswd, SAM 파일)
- 소스 코드 노출
- 데이터베이스 파일 접근
- 로그 파일을 통한 사용자 정보 탈취

### 3. 점검 대상

- **Apache**: Apache HTTP Server
- **Tomcat**: Apache Tomcat 웹 서버
- **Nginx**: Nginx 웹 서버
- **IIS**: Microsoft Internet Information Services
- **WebtoB**: Tmax WebtoB 웹 서버

### 4. 판단 기준

- **양호**: 상위 디렉터리 접근 기능을 제거한 경우
- **취약**: 상위 디렉터리 접근 기능을 제거하지 않은 경우

### 5. 점검 방법

#### 간단한 점검 방법

다음 URL들을 브라우저에 입력해 봅니다:
- `http://your-domain.com/download?file=../../../../etc/passwd`
- `http://your-domain.com/images?file=../../test.txt`

시스템 파일 내용이 보이면 취약, 에러 메시지가 나오면 양호입니다.

#### Apache

```bash
# AllowOverride 설정 확인
cat /<Apache 설치 디렉터리>/httpd.conf | grep "AllowOverride"
```

#### Tomcat

```bash
# allowLinking 설정 확인
cat /<Tomcat 설치 디렉터리>/conf/server.xml | grep "allowLinking"
```

### 6. 조치 방법

#### Apache

**Step 1) AllowOverride 지시자 AuthConfig 옵션 설정 확인**

```bash
vi /<Apache 설치 디렉터리>/httpd.conf (또는 apache.conf)
```

```apache
<!-- 변경 전 -->
<Directory '/usr/local/apache2/htdocs'>
    AllowOverride None
</Directory>

<!-- 변경 후 -->
<Directory '/usr/local/apache2/htdocs'>
    AllowOverride AuthConfig
</Directory>
```

**Step 2) 사용자 인증을 설정할 디렉터리에 .htaccess 파일 생성**

```bash
vi /usr/local/apache/test/.htaccess
```

```apache
AuthName "Directory User Authentication"
AuthType Basic
AuthUserFile /usr/local/apache/test/.auth
Require valid-user
```

**지시자 설명:**
| 지시자           | 설명                                              |
|----------------|-------------------------------------------------|
| AuthName       | 인증 영역(웹브라우저의 인증창에 표시되는 문구)                |
| AuthType       | 인증 형태(Basic 또는 Digest)                      |
| AuthUserFile   | 사용자 정보(아이디 및 비밀번호) 저장 파일 위치              |
| AuthGroupFile  | 그룹 파일의 위치(옵션)                               |
| Require        | 접근을 허용할 사용자 또는, 그룹 정의                         |

**Step 3) 사용자 인증에 사용할 아이디 및 비밀번호 생성**

```bash
htpasswd /<Apache 설치 디렉터리>/.htpasswd [사용자명]
New password: <비밀번호 입력>
Re-type new password: <비밀번호 재입력>
Adding password for user <사용자명>
```

**Step 4) Apache 재구동**

```bash
systemctl restart apache2
```

#### Tomcat

**Step 1) server.xml 파일 내 Context 요소에서 allowLinking 옵션 확인**

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
<Context>
    <WatchedResource>WEB-INF/web.xml</WatchedResource>
    <WatchedResource>WEB-INF/tomcat-web.xml</WatchedResource>
    <WatchedResource>${catalina.base}/conf/web.xml</WatchedResource>
</Context>
```

#### Nginx

**Step 1) nginx.conf 파일 내 디렉터리 접근을 기본 인증으로 제한 설정**

```bash
vi /<Nginx 설치 디렉터리>/conf/nginx.conf
```

```nginx
location /<접근제한 디렉터리>/ {
    auth_basic "Restricted Content";
    auth_basic_user_file /etc/nginx/.htpasswd;
}
```

#### IIS 6.0 이하

**Step 1) 부모 경로 사용 설정 비활성화**

1. 시작 > Windows 관리 도구 > 인터넷 정보 서비스(IIS) 관리자 실행
2. 웹 사이트 선택 > IIS > ASP 더블클릭
3. '부모 경로 사용' 항목을 'False'로 설정

<!-- ![부모 경로 설정 확인](../images/04_웹서비스/image_0007.png) -->

#### IIS 7.0 이상

**Step 1) web.config 파일에서 enableParentPaths 설정**

1. 제어판 > 관리 도구 > 인터넷 정보 서비스(IIS) 관리자
2. 해당 웹사이트 선택 > 사이트 편집에서 루트 디렉터리
3. 루트 디렉터리의 web.config 파일에서 'enableParentPaths' 요소를 'False'로 설정

```xml
<configuration>
    <system.web>
        <httpRuntime enableParentPaths="false" />
    </system.web>
</configuration>
```

**참고**: web.config 파일이 없으면 사이트 홈 디렉터리에 새로 생성합니다.

#### WebtoB

**Step 1) http.m 파일 내 UpperDirRestrict 옵션 제거 또는 비활성화**

```bash
vi /<WebtoB 설치 디렉터리>/config/http.m
```

```text
*NODE imuser
    UpperDirRestrict = N  # N으로 설정 또는 주석 처리
```

**Step 2) 설정 파일 컴파일 및 재구동**

```bash
wscfl -I http.m
wsdown
wsboot
```

### 7. 조치 시 주의사항

- 웹서버 및 웹서비스의 특성에 따라 영향을 줄 수 있습니다.
- 상위 디렉터리 접근이 필요한 레거시 애플리케이션이 있는 경우 영향도를 사전에 테스트해야 합니다.
- 사용자 입력에 대한 경로 검증을 애플리케이션 레벨에서도 수행해야 합니다.
- 설정 변경 후 서비스 정상 작동 여부를 충분히 확인해야 합니다.

### 8. 참고 자료

- Apache Path Traversal: https://httpd.apache.org/docs/current/securing.html
- CWE-22: Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal')
- OWASP Path Traversal: https://owasp.org/www-community/attacks/Path_Traversal

## 요약

상위 디렉터리 접근 기능을 제한하여 경로 순회 공격을 차단하고 시스템의 중요 파일과 데이터를 보호해야 합니다.
