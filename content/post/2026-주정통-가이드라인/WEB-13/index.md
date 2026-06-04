---
title: "[2026 주요정보통신기반시설] WEB-13 웹서비스설정파일노출제한"
slug: "2026-주정통/WEB-13"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "데이터베이스 연결 파일은 웹 애플리케이션의 가장 민감한 정보를 담고 있습니다. 데이터베이스 주소, 계정명, 비밀번호, 암호화 키 등이 포함되어 있어 외부에 노출되면 즉시 치명적인"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Web
---

# WEB-13 웹서비스설정파일노출제한

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | WEB-13 |
| **점검내용** | 데이터베이스 연결 파일은 웹 애플리케이션의 가장 민감한 정보를 담고 있습니다. 데이터베이스 주소, 계정명, 비밀번호, 암호화 키 등이 포함되어 있어 외부에 노출되면 즉시 치명적인  |
| **점검대상** | Tomcat, IIS, JEUS |
| **판단기준** | 양호: 일반 사용자의 DB 연결 파일에 대한 접근을 제한하고, 불필요한 스크립트 매핑이 제거된 경우 |
| **판단기준** | 취약: 일반 사용자의 DB 연결 파일에 대한 접근을 제한하지 않거나, 불필요한 스크립트 매핑이 제거되지 않은 경우 |
| **조치방법** | 상세 조치 방법 참고 |

---
---
## 상세 설명

### 1. 항목 개요

데이터베이스 연결 파일은 웹 애플리케이션의 가장 민감한 정보를 담고 있습니다. 데이터베이스 주소, 계정명, 비밀번호, 암호화 키 등이 포함되어 있어 외부에 노출되면 즉시 치명적인 보안 사고로 이어질 수 있습니다. 마치 집 현관문 열쇠와 금고 열쇠를 현관문 앞에 두는 것과 같습니다. DB 연결 파일은 반드시 철저하게 보호되어야 합니다.

### 2. 왜 이 항목이 필요한가요?

**실제 시나리오:**
- 개발자가 DB 연결 설정을 `config.php`, `database.properties` 등의 파일에 저장했습니다.
- 웹 서버 설정 오류로 이 파일이 웹을 통해 접근 가능한 상태입니다.
- 공격자가 `http://example.com/config/database.php` URL로 접근합니다.
- 데이터베이스 연결 정보(호스트, 사용자, 비밀번호)를 확인합니다.
- 획득한 정보로 데이터베이스에 직접 접속하여 데이터를 탈취합니다.

**DB 연결 정보 노출 위험성:**
- **데이터베이스 장악**: 관리자 권한으로 데이터 무단 접근
- **데이터 유출**: 고객 정보, 비밀번호, 신용카드 정보 등 탈취
- **데이터 변조**: 데이터 무결성 훼손
- **시스템 추가 침투**: DB 권한 상승 공격으로 서버 장악
- **내부 구조 노출**: 서버 IP, 네트워크 구조 정보 유출

**보안 위협:**
- 데이터베이스 비밀번호 크래킹
- SQL Injection 공격과 연계
- 백도어 설치 및 악성코드 삽입
- 개인정보 유출 법적 책임

### 3. 점검 대상

- **Tomcat**: Apache Tomcat 웹 서버
- **IIS**: Microsoft Internet Information Services
- **JEUS**: Tmax JEUS 웹 애플리케이션 서버

### 4. 판단 기준

- **양호**: 일반 사용자의 DB 연결 파일에 대한 접근을 제한하고, 불필요한 스크립트 매핑이 제거된 경우
- **취약**: 일반 사용자의 DB 연결 파일에 대한 접근을 제한하지 않거나, 불필요한 스크립트 매핑이 제거되지 않은 경우

### 5. 점검 방법

#### Tomcat

```bash
# server.xml 파일 내 DB 연결 리소스 확인
grep -A 10 "Resource name=" /<Tomcat 설치 디렉터리>/conf/server.xml

# 파일 권한 확인
ls -la /<Tomcat 설치 디렉터리>/conf/server.xml
```

#### IIS

```powershell
# 처리기 매핑 확인
# IIS 관리자 > 처리기 매핑 > *.asa, *.asax 확인
```

#### JEUS

```bash
# DB 연결 설정 확인
grep -A 10 "datasource" /<JEUS 설치 디렉터리>/conf/domain.xml
```

### 6. 조치 방법

#### Tomcat

**Step 1) server.xml 파일 내 불필요한 DB 연결 리소스 설정 제거**

```bash
vi /<Tomcat 설치 디렉터리>/conf/server.xml
```

```xml
<!-- 변경 전 (취약) -->
<GlobalNamingResources>
    <Resource name="jdbc/MyDB"
              auth="Container"
              type="javax.sql.DataSource"
              maxTotal="100"
              maxIdle="30"
              maxWaitMillis="10000"
              username="dbuser"
              password="dbpassword"
              driverClassName="com.mysql.jdbc.Driver"
              url="jdbc:mysql://localhost:3306/mydb"/>
</GlobalNamingResources>

<!-- 변경 후 (양호) - 제거 또는 주석 처리 -->
<!--
<GlobalNamingResources>
    <Resource name="jdbc/MyDB"
              auth="Container"
              type="javax.sql.DataSource"
              ... />
</GlobalNamingResources>
-->
```

**Step 2) DB 연결 리소스가 존재하는 설정 파일 접근권한을 600으로 설정**

```bash
chmod 600 /<Tomcat 설치 디렉터리>/conf/server.xml

# 권한 확인
ls -la /<Tomcat 설치 디렉터리>/conf/server.xml
```

**참고**: context.xml 파일 내 명시된 설정 파일에서도 DB 연결 확인이 필요합니다.

#### IIS

**Step 1) 처리기 매핑에서 불필요한 DB 매핑 설정 제거**

1. 제어판 > 관리 도구 > 인터넷 정보 서비스(IIS) 관리자 실행
2. 해당 웹사이트 선택 > IIS > 처리기 매핑 더블클릭
3. 사용 항목에서 `*.asa`, `*.asax` 항목 선택 후 제거 클릭

<!-- ![asa/asax 스크립트 매핑 확인](../images/04_웹서비스/image_0014.png) -->

**Step 2) 요청 필터링에서 DB 매핑 설정 제한**

1. IIS 관리자 > 요청 필터링 더블클릭
2. '파일 이름 확장명' 탭 클릭
3. '허용됨' 값이 true인 매핑 제거
4. '파일 이름 확장명 거부' 탭에서 `.asa`, `.asax` 등록

<!-- ![asa/asax 파일 필터링 확인](../images/04_웹서비스/image_0015.png) -->

**참고**: asa/asax 스크립트 매핑 또는 파일 필터링 중 하나라도 설정 시 취약합니다. 둘 다 제거해야 합니다.

#### JEUS

**Step 1) 설정 파일 내 불필요 DB 연결 리소스 설정 제거**

```bash
vi /<JEUS 설치 디렉터리>/conf/domain.xml
```

```xml
<!-- 변경 전 (취약) -->
<datasource>
    <jndi-name>jdbc/UnnecessaryDB</jndi-name>
    <driver-class>com.example.Driver</driver-class>
    <url>jdbc:example://localhost:1234/unnecessarydb</url>
    <username>user</username>
    <password>password</password>
    <max-connections>10</max-connections>
</datasource>

<!-- 변경 후 (양호) - 제거 또는 주석 처리 -->
<!--
<datasource>
    <jndi-name>jdbc/UnnecessaryDB</jndi-name>
    ...
</datasource>
-->
```

**Step 2) 설정 파일의 접근권한을 600으로 설정**

```bash
chmod 600 /<JEUS 설치 디렉터리>/conf/domain.xml

# 권한 확인
ls -la /<JEUS 설치 디렉터리>/conf/domain.xml
```

**참고**: domain.xml 뿐만 아니라 개별 웹 서비스의 설정 파일인 jeus-web-dd.xml에서도 삭제가 필요합니다.

### 7. 조치 시 주의사항

- 일반적인 경우 영향이 없습니다.
- DB 연결이 필요한 웹 애플리케이션의 경우, 해당 설정을 제거하면 서비스가 중단될 수 있습니다.
- 설정 제거 전에 실제 사용 중인 DB 연결인지 확인해야 합니다.
- 파일 권한 변경 후 웹 서비스가 정상 작동하는지 확인해야 합니다.
- DB 연결 정보는 별도의 환경 변수나 암호화된 설정 파일로 관리하는 것을 권장합니다.
- 정기적으로 DB 연결 파일의 접근 권한을 감사해야 합니다.

### 8. 참고 자료

- Tomcat JNDI DataSource: https://tomcat.apache.org/tomcat-9.0-doc/jndi-datasource-examples-howto.html
- IIS Handler Mappings: https://docs.microsoft.com/en-us/iis/configuration/system.webServer/handlers
- CWE-538: Insertion of Sensitive Information into Externally-Accessible File or Directory

## 요약

DB 연결 파일의 접근 권한을 제한하고 불필요한 스크립트 매핑을 제거하여 데이터베이스 연결 정보 노출을 방지해야 합니다.
