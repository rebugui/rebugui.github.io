---
title: "[2026 주요정보통신기반시설] WEB-09 웹서비스프로세스권한제한"
slug: "2026-주정통/WEB-09"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "웹서비스 프로세스의 관리자 권한 구동 여부 점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Web
---

# WEB-09 웹서비스프로세스권한제한

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | WEB-09 |
| **점검내용** | 웹서비스 프로세스의 관리자 권한 구동 여부 점검 |
| **점검대상** | Apache, Tomcat, Nginx, IIS, JEUS, WebtoB |
| **판단기준** | 양호: 웹프로세스(웹서비스)가 관리자 권한이 부여된 계정이 아닌 운영에 필요한 최소한의 권한을 가진 별도의 계정으로 구동되고 있는 경우 |
| **판단기준** | 취약: 웹프로세스가 관리자 권한(root, administrator 등)으로 구동되고 있는 경우 |
| **조치방법** | 웹서비스 프로세스 구동 시 관리자 권한이 아닌 운영에 필요한 최소한의 권한을 가진 계정으로 구동 설정 |

---
## 상세 설명

### 1. 항목 개요

웹 서비스 프로세스의 권한은 서버 보안의 가장 기초이면서 가장 중요한 설정입니다. 웹 서비스가 root나 administrator 같은 관리자 권한으로 실행되고 있다면, 웹 애플리케이션의 취약점 하나로 공격자가 시스템 전체를 장악할 수 있습니다. 마치 회사 보안카드를 청소부에게 주는 것과 같습니다. 웹 서비스는 반드시 최소 권한 원칙(Principle of Least Privilege)에 따라 운영되어야 합니다.

### 2. 왜 이 항목이 필요한가요?

**실제 시나리오:**
- 웹 서비스가 root 권한으로 실행되고 있습니다.
- 공격자가 웹 애플리케이션의 원격 코드 실행(RCE) 취약점을 발견합니다.
- 악성 코드를 실행하면 웹 서비스 권한(root)을 획득합니다.
- 시스템의 모든 파일에 접근 가능하고, 방화벽을 끄거나 백도어를 설치할 수 있습니다.

**관리자 권한 실행 위험성:**
- **취약점 연쇄 확산**: 웹 취약점 → 시스템 장악
- **파일 시스템 접근**: 모든 설정 파일, 로그, 데이터베이스 접근
- **시스템 설정 변경**: 방화벽, 사용자 계정, 시작 프로그램 수정
- **영구적 백도어 설치**: cron, 서비스, 시작 프로그램 등록
- **다른 시스템 공격**: 내부 네트워크 추가 공격 경로 확보

**최소 권한 원칙의 중요성:**
- 피해 범위 최소화
- 침해사고 발생 시 영향 제한
- 방어 심층화(Defense in Depth)

### 3. 점검 대상

- **Apache**: Apache HTTP Server
- **Tomcat**: Apache Tomcat 웹 서버
- **Nginx**: Nginx 웹 서버
- **IIS**: Microsoft Internet Information Services
- **JEUS**: Tmax JEUS 웹 애플리케이션 서버
- **WebtoB**: Tmax WebtoB 웹 서버

### 4. 판단 기준

- **양호**: 웹프로세스가 관리자 권한이 부여된 계정이 아닌 운영에 필요한 최소한의 권한을 가진 별도의 계정으로 구동되고 있는 경우
- **취약**: 웹프로세스가 관리자 권한(root, administrator 등)으로 구동되고 있는 경우

### 5. 점검 방법

#### Linux 계열 (Apache, Tomcat, Nginx, JEUS, WebtoB)

```bash
# 실행 중인 프로세스의 사용자 확인
ps -ef | grep nginx
ps -ef | grep tomcat
ps -ef | grep apache
ps -ef | grep httpd

# 출력 예시
# root     1234  ... nginx: master process  (취약: root로 실행)
# www-data 1235  ... nginx: worker process (양호: 일반 사용자로 실행)
```

#### Windows (IIS)

```powershell
# IIS 응용프로그램 풀 ID 확인
# IIS 관리자 > 응용프로그램 풀 > 고급 설정 > ID 확인
```

### 6. 조치 방법

#### Apache

**Step 1) envvars 파일 내 실행 계정을 관리자 계정이 아닌 별도의 계정으로 변경**

```bash
vi /<Apache 설치 디렉터리>/envvars
# 또는
vi /etc/apache2/envvars
```

```bash
# 변경 전 (취약)
export APACHE_RUN_USER=root
export APACHE_RUN_GROUP=root

# 변경 후 (양호)
export APACHE_RUN_USER=www-data
export APACHE_RUN_GROUP=www-data
```

**Step 2) Apache 서비스 파일 소유권 변경**

```bash
chown -R www-data:www-data /etc/apache2/
chown -R www-data:www-data /var/www/
chown -R www-data:www-data /var/log/apache2/
```

**Step 3) 웹 서비스 실행 계정 로그인 제한 설정**

```bash
usermod -s /sbin/nologin www-data
```

**Step 4) Apache 재구동**

```bash
systemctl restart apache2
# 또는
systemctl restart httpd
```

#### Tomcat

**Step 1) tomcat.service 파일 내 Tomcat 데몬 구동 권한을 관리자 계정이 아닌 별도 계정으로 변경**

```bash
vi /etc/systemd/system/tomcat.service
```

```ini
[Service]
User=tomcat
Group=tomcat
```

**Step 2) Tomcat 서비스 파일 소유권 변경**

```bash
chown -R tomcat:tomcat /<Tomcat 설치 디렉터리>/
chown -R tomcat:tomcat /usr/share/tomcat9/temp
chown -R tomcat:tomcat /<Tomcat 설치 디렉터리>/logs
chown -R tomcat:tomcat /usr/share/tomcat9/webapps
chown -R tomcat:tomcat /usr/share/tomcat9/work
```

**Step 3) 웹서비스 실행 계정 로그인 제한 설정**

```bash
usermod -s /sbin/nologin tomcat
```

**Step 4) Tomcat 서비스 재구동**

```bash
systemctl restart tomcat
```

#### Nginx

**Step 1) nginx.conf 파일 내 Nginx 데몬 구동 권한을 관리자 계정이 아닌 별도 계정으로 변경**

```bash
vi /<Nginx 설치 디렉터리>/conf/nginx.conf
```

```nginx
# 변경 전 (취약)
user root;

# 변경 후 (양호)
user nginx nginx;
# 또는
user www-data www-data;
```

**Step 2) Nginx 전용 계정 생성 및 Nginx 전용 그룹 추가**

```bash
adduser --system --no-create-home --shell /bin/false nginx
groupadd nginx
usermod -aG nginx nginx
```

**Step 3) 웹서비스 실행 계정 로그인 제한 설정**

```bash
usermod -s /sbin/nologin nginx
```

**Step 4) Nginx 서비스 재구동**

```bash
systemctl restart nginx
```

#### IIS

**Step 1) 웹 사이트 응용프로그램 풀 이름 확인**

1. 제어판 > 관리 도구 > 인터넷 정보 서비스(IIS) 관리자 실행
2. 해당 웹 사이트 선택 > 고급 설정 클릭
3. '응용프로그램 풀 이름(DefaultAppPool)' 확인

<!-- ![응용프로그램 풀 이름 확인](../images/04_웹서비스/image_0009.png) -->

**Step 2) 웹 사이트 응용프로그램 풀 ID 확인**

1. IIS 관리자 > 응용프로그램 풀 클릭
2. '응용프로그램 풀 이름(DefaultAppPool)' 선택 > 고급 설정 클릭
3. ID 항목 확인

<!-- ![응용프로그램 풀 ID 확인](../images/04_웹서비스/image_0010.png) -->

**Step 3) 웹사이트 응용프로그램 풀 ID 설정**

1. IIS 관리자 > 응용프로그램 풀 > '응용프로그램 풀 이름' 선택
2. 고급 설정 > ID > ApplicationPoolIdentity 선택

<!-- ![응용프로그램 풀 ID 설정](../images/04_웹서비스/image_0011.png) -->

#### JEUS

**Step 1) JEUS 데몬 구동 권한 확인**

```bash
ps -ef | grep jeus
```

```bash
# 출력 예시
# jeus   25305   4223 99 09:54 pts/5   00:03:31 /usr/lib/jvm/java-11-openjdk-amd64/bin/java -DadminServer...
```

**Step 2) JEUS 데몬 구동 권한을 관리자 계정이 아닌 별도 계정으로 변경**

```bash
useradd -m jeus
mv /<JEUS 설치 디렉터리>/home/jeus
```

**Step 3) JEUS 설치 디렉터리 소유자 및 그룹 소유자를 JEUS 계정으로 변경**

```bash
chown -R jeus:jeus /home/jeus/
```

#### WebtoB

**Step 1) 소유자 및 그룹 소유자 변경**

```bash
chown -R [WebtoB 전용 계정]:[WebtoB 전용 계정] /[WebtoB 디렉터리]/
```

**Step 2) http.m 파일 내 기존 경로 변경**

```bash
vi /[WebtoB 설치 디렉터리]/config/http.m
```

```text
*NODE 절의 WEBTOBDIR, DOCROOT을 변경한 디렉터리로 설정
*NODE imuser
    WEBTOBDIR="/home/tmax/webtob/"
    SHMKEY = 54000
    DOCROOT="/home/tmax/webtob/docs"

*ALIAS 절의 alias1을 변경한 디렉터리로 설정
*ALIAS alias1
    URI = "/cgi-bin/"
    RealPath = "/home/webtob/webtob/cgi-bin/"

*LOGGING 절의 로그 파일 경로를 변경한 디렉터리로 설정
*LOGGING log1
    Format = "DEFAULT"
    FileName = "/home/tmax/webtob/log/access.log"
    Option = "sync"
```

**Step 3) 변경한 디렉터리명 환경변수에 추가**

```bash
export WEBTOB=/[WebtoB 디렉터리]
source ~/.bashrc
```

**Step 4) 라이브러리 캐시 업데이트**

```bash
cp /webtob/lib/libwbiconv.so /usr/lib/
ldconfig
```

**Step 5) 설정 파일 컴파일**

```bash
wscfl -i http.m
```

### 7. 조치 시 주의사항

- 일반적인 경우 영향이 없습니다.
- 권한 변경 후 파일 접근, 로그 기록 등 정상 동작하는지 확인해야 합니다.
- 웹 서비스 계정은 로그인이 불가능하도록 설정(`/sbin/nologin`)하는 것을 권장합니다.
- 특정 기능(예: 80/443 포트 바인딩)을 위해 관리자 권한이 필요한 경우, 시작 시에만 관리자 권한으로 실행 후 권한을 하향하는 방식을 사용하세요.
- 정기적으로 실행 권한을 모니터링해야 합니다.

### 8. 참고 자료

- Apache Running as Root: https://httpd.apache.org/docs/current/misc/security_tips.html#serverroot
- Nginx User Directive: https://nginx.org/en/docs/ngx_core_module.html#user
- CIS Microsoft IIS Server Benchmark: https://www.cisecurity.org/benchmark/microsoft_iis_server
- Principle of Least Privilege: https://cwe.mitre.org/data/definitions/250.html

## 요약

웹 서비스 프로세스를 최소 권한을 가진 별도 계정으로 실행하여 웹 취약점 악용 시 피해 범위를 최소화해야 합니다.
