---
title: "[2026 주요정보통신기반시설] WEB-07 웹서비스경로내불필요한파일제거"
slug: "2026-주정통/WEB-07"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "웹서비스설치시기본으로생성되는불필요한파일및디렉터리제거여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Web
draft: true
---

# WEB-07 웹서비스경로내불필요한파일제거

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | WEB-07 |
| **점검내용** | 웹서비스설치시기본으로생성되는불필요한파일및디렉터리제거여부점검 |
| **점검대상** | Apache, Tomcat, Nginx, IIS, JEUS, WebtoB |
| **판단기준** | 양호: 기본으로생성되는불필요한파일및디렉터리가존재하지않을경우 |
| **판단기준** | 취약: 기본으로생성되는불필요한파일및디렉터리가존재하는경우 |
| **조치방법** | 불필요한파일및디렉터리를제거하도록설정 |

---
## 상세 설명

### 1. 항목 개요

웹 서비스를 설치하면 기본적으로 샘플 파일, 매뉴얼, 테스트 페이지 등이 함께 설치됩니다. 이 파일들은 개발자에게는 유용하지만, 운영 환경에서는 공격자에게 중요한 정보를 제공하는 훌륭한 정보원이 됩니다. 마치 집을 지을 때 건축 설계도와 현관문 열쇠를 현관문 앞에 두는 것과 같습니다. 운영 환경에서는 반드시 이러한 불필요한 파일들을 제거해야 합니다.

### 2. 왜 이 항목이 필요한가요?

**실제 시나리오:**
- 공격자가 웹사이트에 접속하여 `/manual/`, `/docs/`, `/examples/` 경로를 탐색합니다.
- 매뉴얼 페이지에서 서버 버전, 설정 예시, 알려진 취약점 정보를 확인합니다.
- 샘플 페이지에서 취약한 코드 패턴을 발견하고 이를 공격에 활용합니다.
- 테스트 페이지를 통해 서버 설정 정보를 노출합니다.

**불필요한 파일을 통해 노출될 수 있는 정보:**
- **서버 버전 정보**: 알려진 취약점 공격 가능
- **설정 예시**: 시스템 구조 파악
- **테스트 페이지**: 서버 기능 및 설정 정보 노출
- **백업 파일**: `.bak`, `.old`, `.backup` 등 소스 코드 및 설정 파일 유출
- **개발자 도구**: 테스트용 관리자 계정, 디버그 정보

**보안 위협:**
- 웹 서버 구조 및 버전 노출
- 알려진 취약점 공격 경로 제공
- 소스 코드 유출로 인한 추가 취약점 발견
- 개발자가 실수로 남긴 테스트 계정, 백도어 발견

### 3. 점검 대상

- **Apache**: Apache HTTP Server
- **Tomcat**: Apache Tomcat 웹 서버
- **Nginx**: Nginx 웹 서버
- **IIS**: Microsoft Internet Information Services
- **JEUS**: Tmax JEUS 웹 애플리케이션 서버
- **WebtoB**: Tmax WebtoB 웹 서버

### 4. 판단 기준

- **양호**: 기본으로 생성되는 불필요한 파일 및 디렉터리가 존재하지 않을 경우
- **취약**: 기본으로 생성되는 불필요한 파일 및 디렉터리가 존재하는 경우

### 5. 점검 방법

#### 간단한 점검 방법

웹 브라우저에서 다음 경로들을 접속해 봅니다:
- `http://your-domain.com/manual/`
- `http://your-domain.com/docs/`
- `http://your-domain.com/examples/`
- `http://your-domain.com/test/`

파일 목록이나 페이지가 보이면 취약, "404 Not Found"가 나오면 양호입니다.

#### Apache

```bash
# 매뉴얼 디렉터리 확인
ls -la /<Apache 설치 디렉터리>/htdocs/manual
ls -la /<Apache 설치 디렉터리>/manual
```

#### Tomcat

```bash
# 매뉴얼 및 샘플 디렉터리 확인
ls -la /<Tomcat 설치 디렉터리>/webapps/docs/
ls -la /<Tomcat 설치 디렉터리>/webapps/examples/
```

### 6. 조치 방법

#### Apache

**Step 1) rm 명령어로 확인된 불필요한 매뉴얼 디렉터리 및 파일 제거**

```bash
# 메뉴얼 디렉터리 제거
rm -rf /<Apache 설치 디렉터리>/htdocs/manual
rm -rf /<Apache 설치 디렉터리>/manual

# 기본 샘플 파일 제거
rm -f /var/www/html/index.html
rm -f /var/www/html/apache2-default/*
```

**참고**: Apache 2.4 버전 이상은 htdocs 디렉터리가 기본 제공되지 않으므로 `/var/www/html`을 확인합니다.

#### Tomcat

**Step 1) rm 명령어로 확인된 불필요한 매뉴얼 디렉터리 및 파일 제거**

```bash
# 메뉴얼 디렉터리 제거
rm -rf /<Tomcat 설치 디렉터리>/webapps/docs/<불필요 파일>

# 샘플 애플리케이션 제거
rm -rf /<Tomcat 설치 디렉터리>/webapps/examples/
rm -rf /<Tomcat 설치 디렉터리>/webapps/ROOT/

# 불필요한 설정 파일 제거
rm -f /<Tomcat 설치 디렉터리>/BUILDING.txt
rm -f /<Tomcat 설치 디렉터리>/RELEASE-NOTES.txt
rm -f /<Tomcat 설치 디렉터리>/jndi-resources-howto.html
```

**참고**: `BUILDING.txt`, `RELEASE-NOTES.txt`, `jndi-resources-howto.html` 등 매뉴얼 파일도 포함됩니다.

#### Nginx

**Step 1) rm 명령어로 확인된 불필요한 매뉴얼 디렉터리 및 파일 제거**

```bash
# 기본 HTML 페이지 제거
rm -rf /<Nginx 설치 디렉터리>/html/index.html
rm -rf /usr/share/nginx/html/*.html
```

#### IIS

**Step 1) 샘플 디렉터리 존재 여부 확인 및 제거**

다음 샘플 디렉터리 경로들을 확인하고 제거합니다:
- `c:\inetpub\iissamples`
- `c:\winnt\help\iishelp`
- `c:\program files\common files\system\msadc\sample`
- `%SystemRoot%\System32\Inetsrv\IISADMPWD`

파일 탐색기에서 해당 디렉터리를 찾아 삭제하거나, IIS 관리자에서 가상 디렉터리를 제거합니다.

#### JEUS

**Step 1) rm 명령어로 확인된 불필요한 매뉴얼 디렉터리 및 파일 제거**

```bash
# 메뉴얼 제거
rm -rf /<JEUS 설치 디렉터리>/docs/manuals/default/web-manager/<불필요 파일>

# 샘플 제거
rm -rf /<JEUS 홈 디렉터리>/samples/<불필요 파일>
```

#### WebtoB

**Step 1) rm 명령어로 확인된 불필요한 매뉴얼 디렉터리 및 파일 제거**

```bash
# 메뉴얼 제거
rm -rf /<WebtoB 설치 디렉터리>/docs/manuals/<불필요 파일>

# 샘플 제거
rm -rf /<WebtoB 홈 디렉터리>/samples/<불필요 파일>
```

### 7. 조치 시 주의사항

- 일반적인 경우 영향이 없습니다.
- 파일 제거 전에 반드시 백업을 권장합니다.
- 운영 중인 서비스에서 사용 중인 파일인지 확인 후 제거해야 합니다.
- 제거 후 웹 서비스 정상 작동 여부를 확인해야 합니다.
- 개발/테스트 환경과 운영 환경을 분리하여 관리하는 것을 권장합니다.

### 8. 참고 자료

- CIS Apache Benchmark: https://www.cisecurity.org/benchmark/apache_web_server
- OWASP Development Guide: https://owasp.org/www-project-secure-development-life-cycle/

## 요약

웹서비스 경로 내 샘플 파일, 매뉴얼, 테스트 파일 등 불필요한 파일을 제거하여 시스템 정보 노출을 방지해야 합니다.
