---
title: "[2026 주요정보통신기반시설] WEB-15 웹서비스의불필요한스크립트매핑제거"
slug: "2026-주정통/WEB-15"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "스크립트 매핑은 웹 서버에서 특정 파일 확장자를 처리 프로그램에 연결하는 기능입니다. 예를 들어 `.asp` 파일은 `asp.dll`이 처리하고 `.php` 파일은 PHP 엔진이"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Web
draft: true
---

# WEB-15 웹서비스의불필요한스크립트매핑제거

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | WEB-15 |
| **점검내용** | 스크립트 매핑은 웹 서버에서 특정 파일 확장자를 처리 프로그램에 연결하는 기능입니다. 예를 들어 `.asp` 파일은 `asp.dll`이 처리하고 `.php` 파일은 PHP 엔진이  |
| **점검대상** | Tomcat, IIS, JEUS |
| **판단기준** | 양호: 불필요한 스크립트 매핑이 존재하지 않는 경우 |
| **판단기준** | 취약: 불필요한 스크립트 매핑이 존재하는 경우 |
| **조치방법** | 상세 조치 방법 참고 |

---
---
## 상세 설명

### 1. 항목 개요

스크립트 매핑은 웹 서버에서 특정 파일 확장자를 처리 프로그램에 연결하는 기능입니다. 예를 들어 `.asp` 파일은 `asp.dll`이 처리하고 `.php` 파일은 PHP 엔진이 처리합니다. 하지만 사용하지 않는 스크립트 매핑이 남아 있으면 공격자는 해당 확장자의 알려진 취약점을 악용할 수 있습니다. 마치 쓰지 않는 전기 기구의 코드를 콘센트에 꽂아두는 것과 같습니다.

### 2. 왜 이 항목이 필요한가요?

**실제 시나리오:**
- 웹 서버에 `.htr`, `.idq`, `.printer` 등의 오래된 스크립트 매핑이 설정되어 있습니다.
- 이 확장자들은 과거에 심각한 보안 취약점이 발견되었습니다.
- 공격자가 이러한 확장자를 요청하여 버퍼 오버플로우 취약점을 공격합니다.
- 서버 권한을 획득하거나 서비스 거부 상태를 만듭니다.

**불필요한 스크립트 매핑 위험성:**
- **버퍼 오버플로우**: 알려진 취약점으로 시스템 장악
- **서비스 거부**: 악의적인 요청으로 서버 다운
- **코드 실행**: 임의 코드 실행으로 서버 장악
- **정보 노출**: 소스 코드, 시스템 정보 유출

**취약한 확장자 예시:**
| 확장자명 | 기능 | 취약점 |
|---------|------|--------|
| .asp    | Active Server Pages 기능 지원 | Buffer Overflow (MS02-018) |
| .htr    | 웹 기반 비밀번호 재설정 | .htr 소스 공개 취약점 (MS01-004) |
| .idc    | Internet Database Connector | Web 디렉터리 경로 공개 |
| .stm/.shtml | Server-Side Includes | Buffer Overflow (MS01-044) |
| .printer | 인터넷 프린팅 | Buffer Overflow (MS01-023) |
| .ida/.idq | Index Server 쿼리 | Buffer Overflow (MS01-033) |
| .htw    | Index Server Webhit | Webhit 소스 공개 취약점 (MS00-006) |

### 3. 점검 대상

- **Tomcat**: Apache Tomcat 웹 서버
- **IIS**: Microsoft Internet Information Services
- **JEUS**: Tmax JEUS 웹 애플리케이션 서버

### 4. 판단 기준

- **양호**: 불필요한 스크립트 매핑이 존재하지 않는 경우
- **취약**: 불필요한 스크립트 매핑이 존재하는 경우

### 5. 점검 방법

#### Tomcat

```bash
# Servlet 매핑 확인
grep -A 5 "servlet-mapping" /<Tomcat 설치 디렉터리>/conf/web.xml
```

#### IIS

```powershell
# 처리기 매핑 확인
# IIS 관리자 > 처리기 매핑에서 확인
```

#### JEUS

```bash
# Servlet 매핑 확인
grep -A 5 "servlet-mapping" /<JEUS 설치 디렉터리>/web.xml
```

### 6. 조치 방법

#### Tomcat

**Step 1) 설정 파일의 불필요 스크립트 매핑 제거**

```bash
vi /<Tomcat 설치 디렉터리>/conf/web.xml
```

```xml
<!-- 변경 전 (취약) -->
<servlet-mapping>
    <servlet-name>UnuseServlet</servlet-name>
    <url-pattern>/example/*</url-pattern>
</servlet-mapping>

<!-- 변경 후 (양호) - 주석 처리 또는 제거 -->
<!--
<servlet-mapping>
    <servlet-name>UnuseServlet</servlet-name>
    <url-pattern>/example/*</url-pattern>
</servlet-mapping>
-->
```

**Step 2) Tomcat 재시작**

```bash
systemctl restart tomcat
```

**참고**: context.xml 파일 내 명시된 설정 파일에서도 DB 연결 확인이 필요합니다.

#### IIS

**Step 1) 취약한 매핑 설정 확인 및 제거**

다음 확장자 매핑 확인 및 제거:
- `.htr`, `.idc`, `.stm`, `.shtm`, `.shtml`, `.printer`, `.htw`, `.ida`, `.idq`

1. 시작 > 실행 > INETMGR 입력
2. 웹사이트 > 해당 웹사이트 선택
3. '처리기 매핑' 더블클릭
4. 미사용 확장자 매핑 선택 후 제거 클릭

<!-- ![웹사이트의 처리기 매핑](../images/04_웹서비스/image_0017.png) -->

**취약한 확장자별 조치:**

| 확장자명 | 양호 버전 | 조치 방법 |
|---------|----------|----------|
| .asp    | Win 2000 SP3 이상 | 최신 패치 적용 또는 매핑 제거 |
| .htr    | Win 2000 SP3, NT SP7.0 이상 | 최신 패치 적용 또는 매핑 제거 |
| .idc    | NT 4.0, NT SP6a 이상 | 최신 패치 적용 또는 매핑 제거 |
| .stm/.shtml | Win 2000 SP3 이상 | 최신 패치 적용 또는 매핑 제거 |
| .printer | Win 2000 SP2 이상 | 최신 패치 적용 또는 매핑 제거 |
| .ida/.idq | Win 2000 SP3 이상 | 최신 패치 적용 또는 매핑 제거 |
| .htw    | Win 2000 SP1 이상 | 최신 패치 적용 또는 매핑 제거 |

**Step 2) IIS 재시작**

```powershell
iisreset
# 또는
Restart-Service W3SVC
```

#### JEUS

**Step 1) web.xml 파일 내 servlet-mapping 요소에서 불필요 매핑 확인 및 제거**

```bash
vi /<JEUS 설치 디렉터리>/conf/web.xml
```

```xml
<!-- 변경 전 (취약) -->
<servlet-mapping>
    <url-pattern>/welcome</url-pattern>
    <servlet-name>jsp</servlet-name>
</servlet-mapping>

<!-- 변경 후 (양호) - 주석 처리 또는 제거 -->
<!--
<servlet-mapping>
    <url-pattern>/welcome</url-pattern>
    <servlet-name>jsp</servlet-name>
</servlet-mapping>
-->
```

**Step 2) JEUS 재시작**

```bash
# 서버 중지
./stopServer -host <도메인명>:<포트 번호>

# 서버 시작
./startDomainAdminServer -host <도메인명>:<포트 번호>
```

### 7. 조치 시 주의사항

- 일반적인 경우 영향이 없습니다.
- 실제 사용 중인 스크립트 매핑인지 확인 후 제거해야 합니다.
- 확장자를 사용하는 웹 애플리케이션이 있는 경우 제거하면 서비스가 중단됩니다.
- 매핑 제거 전에 웹사이트에서 해당 확장자를 사용하는지 검색해야 합니다.
- 제거 후 웹사이트 정상 작동 여부를 테스트해야 합니다.
- 정기적으로 불필요한 매핑이 추가되지 않았는지 감사해야 합니다.

### 8. 참고 자료

- IIS Handler Mappings: https://docs.microsoft.com/en-us/iis/configuration/system.webServer/handlers
- Microsoft Security Bulletins: https://docs.microsoft.com/en-us/security-updates/
- Apache Tomcat Servlet Mapping: https://tomcat.apache.org/tomcat-9.0-doc/servletapi/
- CWE-940: Improper Verification of Source of a Communication Channel

## 요약

웹 서비스에서 사용하지 않는 불필요한 스크립트 매핑을 제거하여 알려진 취약점을 악용한 공격을 방지해야 합니다.
