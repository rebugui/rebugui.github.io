---
title: "[2026 주요정보통신기반시설] WEB-26 로그디렉터리및파일권한설정"
slug: "2026-주정통/WEB-26"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "로그 파일은 웹 서버의 모든 활동을 기록하는 중요한 정보입니다. 접속 기록, 에러 메시지, 사용자 정보 등이 포함되어 있어 공격자에게 매우 유용한 정보원이 됩니다. 로그 파일의 권"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Web
---

# WEB-26 로그디렉터리및파일권한설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | WEB-26 |
| **점검내용** | 로그 파일은 웹 서버의 모든 활동을 기록하는 중요한 정보입니다. 접속 기록, 에러 메시지, 사용자 정보 등이 포함되어 있어 공격자에게 매우 유용한 정보원이 됩니다. 로그 파일의 권 |
| **점검대상** | Apache, Tomcat, Nginx, IIS, JEUS, WebtoB |
| **판단기준** | 양호: 로그 디렉터리 및 파일에 일반 사용자의 접근 권한이 없는 경우 |
| **판단기준** | 취약: 로그 디렉터리 및 파일에 일반 사용자의 접근 권한이 있는 경우 |
| **조치방법** | 상세 조치 방법 참고 |

---
---
## 상세 설명

### 1. 항목 개요

로그 파일은 웹 서버의 모든 활동을 기록하는 중요한 정보입니다. 접속 기록, 에러 메시지, 사용자 정보 등이 포함되어 있어 공격자에게 매우 유용한 정보원이 됩니다. 로그 파일의 권한이 느슨하면 공격자는 이를 변조하거나 삭제하여 침해 사고를 은폐할 수 있습니다. 마치 CCTV 녹화테이프를 누구나 볼 수 있게 두는 것과 같습니다. 로그 파일은 반드시 철저하게 보호되어야 합니다.

### 2. 왜 이 항목이 필요한가요?

**실제 시나리오:**
- 웹 서버 로그 파일 권한이 644(rw-r--r--)로 설정되어 있습니다.
- 공격자가 웹 서버에 침입하여 일반 사용자 권한을 획득합니다.
- 로그 파일을 열람하여 관리자 활동, 내부 IP 주소, 시스템 구조 등을 파악합니다.
- 침해 사고를 은폐하기 위해 로그 파일을 삭제하거나 변조합니다.

**로그 파일에 포함될 수 있는 정보:**
- **접속 기록**: IP 주소, 타임스탬프, 요청 URL
- **사용자 정보**: 세션 ID, 쿠키, 사용자 에이전트
- **시스템 정보**: 서버 경로, 소프트웨어 버전, 에러 메시지
- **비즈니스 정보**: 거래 내역, 개인정보
- **보안 이벤트**: 인증 실패, 공격 시도, 오류 발생

**로그 파일 유출 위험성:**
- **추가 공격 경로**: 시스템 정보를 통한 추가 침투
- **개인정보 유출**: 사용자 활동 추적 가능
- **침해 사고 은폐**: 로그 변조로 포렌식 분석 방해
- **규정 위반**: 개인정보보호법 등 법적 책임

### 3. 점검 대상

- **Apache**: Apache HTTP Server
- **Tomcat**: Apache Tomcat 웹 서버
- **Nginx**: Nginx 웹 서버
- **IIS**: Microsoft Internet Information Services
- **JEUS**: Tmax JEUS 웹 애플리케이션 서버
- **WebtoB**: Tmax WebtoB 웹 서버

### 4. 판단 기준

- **양호**: 로그 디렉터리 및 파일에 일반 사용자의 접근 권한이 없는 경우
- **취약**: 로그 디렉터리 및 파일에 일반 사용자의 접근 권한이 있는 경우

### 5. 점검 방법

#### Linux 계열 (Apache, Tomcat, Nginx, JEUS, WebtoB)

```bash
# 로그 디렉터리 및 파일 권한 확인
ls -la /var/log/apache2/
ls -la /var/log/nginx/
ls -la /<Tomcat 설치 디렉터리>/logs/
ls -la /<JEUS 설치 디렉터리>/domains/*/logs/
ls -la /home/tmax/webtob/log/
```

**권한 설명:**
- **640 (rw-r-----)**: 소유자 읽기/쓰기, 그룹 읽기 (양호)
- **600 (rw-------)**: 소유자만 읽기/쓰기 (가장 안전)
- **644 (rw-r--r--)**: 모든 사용자가 읽기 가능 (취약)

#### Windows (IIS)

파일 탐색기 > 로그 디렉터리 > 속성 > 보안 탭 확인

### 6. 조치 방법

#### Apache

**Step 1) 로그 디렉터리 및 파일 권한 확인**

```bash
ls -la <Apache 로그 디렉터리>
# 예: /var/log/apache2/
```

**Step 2) 로그 디렉터리 및 파일의 불필요 권한 삭제**

```bash
# 일반 사용자(other) 권한 제거
chmod o-rwx <Apache 로그 파일>

# 예시
chmod o-rwx /var/log/apache2/access.log
chmod o-rwx /var/log/apache2/error.log

# 확인
ls -la /var/log/apache2/
```

**출력 예시 (양호):**
```bash
-rw-r----- 1 root adm 12345 Jan 20 10:00 access.log
-rw-r----- 1 root adm  6789 Jan 20 10:00 error.log
```

#### Tomcat

**Step 1) 로그 디렉터리 및 파일 권한 확인**

```bash
ls -la /<Tomcat 로그 디렉터리>
```

**Step 2) 로그 디렉터리 및 파일의 불필요 권한 삭제**

```bash
# 일반 사용자(other) 권한 제거
chmod o-rwx /<Tomcat 로그 파일>

# 예시
chmod o-rwx /<Tomcat 설치 디렉터리>/logs/catalina.out
chmod o-rwx /<Tomcat 설치 디렉터리>/logs/localhost.*.log

# 확인
ls -la /<Tomcat 설치 디렉터리>/logs/
```

#### Nginx

**Step 1) 로그 디렉터리 및 파일의 권한 확인**

```bash
ls -la /<Nginx 로그 디렉터리>
# 예: /var/log/nginx/
```

**Step 2) 로그 디렉터리 및 파일의 불필요 권한 삭제**

```bash
# 일반 사용자(other) 권한 제거
chmod o-rwx /<Nginx 로그 디렉터리>

# 예시
chmod o-rwx /var/log/nginx/access.log
chmod o-rwx /var/log/nginx/error.log

# 확인
ls -la /var/log/nginx/
```

#### IIS

**Step 1) 로그 디렉터리 및 파일의 권한 확인**

1. 파일 탐색기(C:\Windows\System32\config) > 로그 디렉터리 > 속성 > 보안 > 고급 클릭

<!-- ![config 속성 확인](../images/04_웹서비스/image_0034.png) -->

**Step 2) Everyone 권한 제거**

1. 보안 탭 > 편집 클릭
2. '그룹 또는 사용자 이름' 목록에서 Everyone 선택 후 제거 클릭
3. 확인 클릭

<!-- ![config 타 사용자 권한 확인](../images/04_웹서비스/image_0035.png) -->

**참고**: 일반적으로 시스템 로그는 `C:\Windows\system32\config` 파일에 저장되지만, 서비스 로그 파일은 각각의 서비스마다 로그 저장 위치가 다릅니다. IIS의 경우 `C:\Windows\system32\LogFiles`에 저장됩니다.

#### JEUS

**Step 1) 도메인별 logs 파일 권한 확인**

```bash
ls -la /<JEUS 설치 디렉터리>/domains/jeus_domain/servers/sample/logs
```

**Step 2) 로그 디렉터리 권한을 750으로 변경**

```bash
chmod 750 /<JEUS 설치 디렉터리>/domains/jeus_domain/servers/sample/logs
```

**Step 3) 로그 파일의 권한을 640으로 변경 (기본값: 644)**

```bash
chmod 640 /<JEUS 설치 디렉터리>/domains/jeus_domain/servers/sample/logs/[로그 파일]

# 예시
chmod 640 /<JEUS 설치 디렉터리>/domains/jeus_domain/servers/sample/logs/server.log
chmod 640 /<JEUS 설치 디렉터리>/domains/jeus_domain/servers/sample/logs/trace.log
```

**참고**: 그 외 로그 파일의 권한도 동일하게 설정

#### WebtoB

**Step 1) logs 파일 권한 확인**

```bash
ls -la /home/tmax/webtob/log/
```

**출력 예시:**
```bash
-rw------- 1 tmax tmax 674 8월 19 16:06 access.log_08192024
```

**Step 2) 로그 디렉터리 권한을 750으로 변경**

```bash
chmod 750 /<WebtoB 설치 디렉터리>/log/
```

**Step 3) 로그 파일의 권한을 640으로 변경 (기본값: 644)**

```bash
chmod 640 /<WebtoB 설치 디렉터리>/log/[로그 파일]

# 예시
chmod 640 /home/tmax/webtob/log/access.log
chmod 640 /home/tmax/webtob/log/error.log
```

**참고**: 그 외 로그 파일의 권한도 동일하게 설정

<!-- ![로그 파일 권한 설정 예시](../images/04_웹서비스/image_0036.png) -->

### 7. 조치 시 주의사항

- 일반적인 경우 영향이 없습니다.
- 로그 모니터링 도구나 로그 분석 도구가 로그에 접근해야 하는 경우 영향이 있을 수 있습니다.
- 로그 파일 소유자는 root 또는 해당 웹 서비스 실행 계정이어야 합니다.
- 로그 롤오버 기능이 정상 작동하는지 확인해야 합니다.
- 중앙 로그 서버(SIEM)를 사용하는 경우 전송 권한도 확인해야 합니다.
- 정기적으로 로그 파일 권한이 올바르게 설정되어 있는지 감사해야 합니다.
- 로그 백업 시에도 권한을 유지해야 합니다.

### 8. 참고 자료

- Linux File Permissions: https://wiki.archlinux.org/title/File_permissions_and_attributes
- Apache Logging: https://httpd.apache.org/docs/current/logs.html
- Nginx Logging: https://nginx.org/en/docs/http/ngx_http_log_module.html
- IIS Log Files: https://docs.microsoft.com/en-us/iis/manage/provisioning-and-managing-iis/configure-logging-in-iis
- CWE-532: Insertion of Sensitive Information into Log File

## 요약

로그 디렉터리 및 파일의 권한을 640/750 등으로 설정하여 일반 사용자의 접근을 차단하고 로그 파일 유출 및 변조를 방지해야 합니다.
