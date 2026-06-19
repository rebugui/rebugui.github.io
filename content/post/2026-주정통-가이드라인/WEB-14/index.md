---
title: "[2026 주요정보통신기반시설] WEB-14 웹서비스경로내파일의접근통제"
slug: "2026-주정통/WEB-14"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "웹 서비스 경로 내의 파일들은 웹사이트의 핵심 구성 요소입니다. 설정 파일, 소스 코드, 데이터 파일 등이 포함되어 있어 이들에 대한 접근 권한이 느슨하면 공격자는 웹사이트를 변조"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Web
draft: true
---

# WEB-14 웹서비스경로내파일의접근통제

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | WEB-14 |
| **점검내용** | 웹 서비스 경로 내의 파일들은 웹사이트의 핵심 구성 요소입니다. 설정 파일, 소스 코드, 데이터 파일 등이 포함되어 있어 이들에 대한 접근 권한이 느슨하면 공격자는 웹사이트를 변조 |
| **점검대상** | Apache, Tomcat, Nginx, IIS, JEUS, WebtoB |
| **판단기준** | 양호: 주요 설정 파일 및 디렉터리에 불필요한 접근 권한이 부여되지 않은 경우 |
| **판단기준** | 취약: 주요 설정 파일 및 디렉터리에 불필요한 접근 권한이 부여된 경우 |
| **조치방법** | 상세 조치 방법 참고 |

---
---
## 상세 설명

### 1. 항목 개요

웹 서비스 경로 내의 파일들은 웹사이트의 핵심 구성 요소입니다. 설정 파일, 소스 코드, 데이터 파일 등이 포함되어 있어 이들에 대한 접근 권한이 느슨하면 공격자는 웹사이트를 변조하거나 중요 정보를 탈취할 수 있습니다. 마치 회사의 중요 문서가 보관된 서류실에 모든 직원이 출입할 수 있는 것과 같습니다. 웹 서비스 파일은 반드시 최소 권한 원칙에 따라 관리되어야 합니다.

### 2. 왜 이 항목이 필요한가요?

**실제 시나리오:**
- 웹 서비스 디렉터리의 파일 권한이 777(모두 읽기/쓰기/실행 가능)로 설정되어 있습니다.
- 공격자가 웹을 통해 설정 파일, 소스 코드에 접근합니다.
- 비밀번호 정보를 확인하거나, 소스 코드를 수정하여 백도어를 심습니다.
- 또는 중요 파일을 삭제하여 서비스 거부 상태를 만듭니다.

**파일 접근 권한 위험성:**
- **설정 파일 노출**: DB 비밀번호, API 키 등 중요 정보 유출
- **소스 코드 유출**: 비즈니스 로직, 취약점 분석 가능
- **파일 변조**: 웹사이트 변조, 악성코드 삽입
- **파일 삭제**: 서비스 거부 공격
- **백도어 설치**: 영구적 시스템 장악

**보안 위협:**
- 웹사이트 변조 (웹 데플레이스먼트)
- 데이터 유출 및 파괴
- 시스템 장악 및 botnet 가입
- 개인정보 유출 법적 책임

### 3. 점검 대상

- **Apache**: Apache HTTP Server
- **Tomcat**: Apache Tomcat 웹 서버
- **Nginx**: Nginx 웹 서버
- **IIS**: Microsoft Internet Information Services
- **JEUS**: Tmax JEUS 웹 애플리케이션 서버
- **WebtoB**: Tmax WebtoB 웹 서버

### 4. 판단 기준

- **양호**: 주요 설정 파일 및 디렉터리에 불필요한 접근 권한이 부여되지 않은 경우
- **취약**: 주요 설정 파일 및 디렉터리에 불필요한 접근 권한이 부여된 경우

### 5. 점검 방법

#### Linux 계열 (Apache, Tomcat, Nginx, JEUS, WebtoB)

```bash
# 파일 권한 확인
ls -la /<웹서비스 경르>/

# 설정 파일 권한 확인
ls -la /<Apache 설치 디렉터리>/apache2.conf
ls -la /<Tomcat 설치 디렉터리>/conf/web.xml
ls -la /<Nginx 설치 디렉터리>/conf/nginx.conf
ls -la /<JEUS 설치 디렉터리>/conf/accounts.xml
ls -la /<WebtoB 설치 디렉터리>/config/http.m
```

**권한 설명:**
- **750 (rwxr-x---)**: 소유자는 모든 권한, 그룹은 읽기/실행만 가능
- **644 (rw-r--r--)**: 소유자는 읽기/쓰기, 그룹과 기타 사용자는 읽기만 가능
- **600 (rw-------)**: 소유자만 읽기/쓰기 가능 (가장 안전)

#### Windows (IIS)

파일 탐색기 > 파일 우클릭 > 속성 > 보안 탭에서 권한 확인

### 6. 조치 방법

#### Apache

**Step 1) 루트 디렉터리 내 불필요한 권한 삭제 또는 적절한 권한 부여**

```bash
# 설정 파일 소유자 변경
chown -R www-data:www-data /etc/apache2/apache2.conf

# 권한 변경
chmod -R 750 /etc/apache2/apache2.conf

# 또는 httpd.conf
chmod -R 750 /<Apache 설치 디렉터리>/conf/httpd.conf
```

**참고**: `www-data`는 Apache 실행 계정입니다. 실제 환경의 계정으로 변경하세요.

#### Tomcat

**Step 1) 루트 디렉터리 불필요한 권한 삭제 또는 적절한 권한 부여**

```bash
# 설정 파일 소유자 변경
chown -R tomcat:tomcat /<Tomcat 설치 디렉터리>/conf/web.xml

# 권한 변경
chmod -R 750 /<Tomcat 설치 디렉터리>/conf/web.xml

# 또는
chmod -R 600 /<Tomcat 설치 디렉터리>/conf/web.xml
```

#### Nginx

**Step 1) 루트 디렉터리 불필요한 권한 삭제 또는 적절한 권한 부여**

```bash
# 설정 파일 소유자 변경
chown -R nginx:nginx /<Nginx 설치 디렉터리>/conf/nginx.conf

# 권한 변경
chmod -R 750 /<Nginx 설치 디렉터리>/conf/nginx.conf

# 또는
chmod -R 600 /<Nginx 설치 디렉터리>/conf/nginx.conf
```

#### IIS

**Step 1) 실제 경로 디렉터리 내 불필요한 권한 삭제 또는 적절한 권한 부여**

1. 파일 탐색기에서 설정 파일(web.config 등) 우클릭
2. 속성 > 보안 탭 클릭
3. 편집 버튼 클릭
4. '그룹 또는 사용자 이름'의 불필요 권한 제거
5. IIS_IUSRS, SYSTEM, Administrators만 남기고 나머지 제거

<!-- ![설정 파일 권한 확인](../images/04_웹서비스/image_0016.png) -->

#### JEUS

**Step 1) 루트 디렉터리 불필요한 권한 삭제 또는 적절한 권한 부여**

```bash
# 설정 파일 소유자 변경
chown -R jeus:jeus /<JEUS 설치 디렉터리>/conf/accounts.xml

# 권한 변경
chmod -R 750 /<JEUS 설치 디렉터리>/conf/accounts.xml

# 또는
chmod -R 600 /<JEUS 설치 디렉터리>/conf/accounts.xml
```

#### WebtoB

**Step 1) 루트 디렉터리 불필요한 권한 삭제 또는 적절한 권한 부여**

```bash
# 설정 파일 소유자 변경
chown -R webtob:webtob /<WebtoB 설치 디렉터리>/config/http.m

# 권한 변경
chmod -R 750 /<WebtoB 설치 디렉터리>/config/http.m

# 또는
chmod -R 600 /<WebtoB 설치 디렉터리>/config/http.m
```

### 7. 조치 시 주의사항

- 일반적인 경우 영향이 없습니다.
- 권한 변경 시 웹 서비스 실행 계정이 파일에 접근 가능한지 확인해야 합니다.
- 너무 제한적인 권한 설정은 웹 서비스 작동을 중단시킬 수 있습니다.
- 설정 파일: 600 또는 640 권한 권장
- 디렉터리: 750 권한 권장
- 정기적으로 파일 권한을 감사해야 합니다.
- 소스 코드 리포지토리(git 등)의 `.git` 디렉터리 접근도 차단해야 합니다.

### 8. 참고 자료

- Linux File Permissions: https://wiki.archlinux.org/title/File_permissions_and_attributes
- Apache Security Tips: https://httpd.apache.org/docs/current/misc/security_tips.html
- CWE-732: Incorrect Permission Assignment for Critical Resource

## 요약

웹 서비스 경로 내 주요 파일과 디렉터리의 접근 권한을 최소한으로 제한하여 비인가자의 파일 접근을 차단해야 합니다.
