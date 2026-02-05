---
title: "[2026 주요정보통신기반시설] WEB-01 Default관리자계정명변경"
slug: "2026-주정통/WEB-01"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "웹서비스설치시기본적으로설정된관리자계정의변경후사용여부점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Web
---

# WEB-01 Default관리자계정명변경

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | WEB-01 |
| **점검내용** | 웹서비스설치시기본적으로설정된관리자계정의변경후사용여부점검 |
| **점검대상** | Tomcat, JEUS |
| **판단기준** | 양호: 관리자페이지를사용하지않거나,계정명이기본계정명으로설정되어있지않은경우 |
| **판단기준** | 취약: 계정명이 기본 계정명으로 설정되어 있거나, 추측하기 쉬운 문자 조합으로 이루어진 계정명을 사용하는경우 |
| **조치방법** | 기본관리자계정명을추측하기어려운계정명으로설정 |

---
## 상세 설명

### 1. 항목 개요

웹 서비스를 설치할 때 기본으로 생성되는 관리자 계정은 공격자들에게 널리 알려져 있습니다. 마치 집을 새로 지었는데 현관문 열쇠를 문발매 아래에 두는 것과 같습니다. 공격자는 먼저 `admin`, `administrator`, `tomcat` 같은 기본 계정명으로 로그인을 시도합니다. 이를 예방하기 위해 기본 계정명을 변경하는 것은 웹 서비스 보안의 첫 단계입니다.

### 2. 비유로 이해하기

기본 관리자 계정명은 **"공개된 보물 열쇠"**와 같습니다.

- **admin/administrator/tomcat** = "열쇠는 현관문 발매 아래"
- **변경된 계정명** = "알 수 없는 위치에 숨겨둔 열쇠"

예시:
```
# 공격자 시도
GET /manager/html  # Tomcat 관리자 페이지
Authorization: Basic YWRtaW46YWRtaW4=  # admin:admin (Base64)
# 또는
Authorization: Basic dG9tY2F0OnRvbWNhdA==  # tomcat:tomcat
```

### 3. 기술적 배경

**웹 서비스별 기본 계정**:
```xml
<!-- Tomcat: tomcat-users.xml -->
<user username="tomcat" password="tomcat" roles="admin-gui,manager-gui"/>

<!-- JEUS -->
<user name="administrator" password="weblogic"/>
```

**HTTP Basic 인증 공격**:
```bash
# 1. 기본 계정으로 시도
curl -u admin:admin http://target-server/manager

# 2. 비밀번호 스프레이
hydra -L users.txt -P pass.txt http-get://target-server/manager

# 3. 성공 시 WAR 파일 업로드
curl -u admin:admin -F deploy=@backdoor.war http://target-server/manager/text/deploy
```

### 4. 왜 이 항목이 필요한가요?

**실제 시나리오:**
- 공격자가 웹 서비스의 관리자 페이지 URL을 발견합니다.
- 기본 계정명인 `admin`이나 `tomcat`으로 로그인을 시도합니다.
- 비밀번호 추측 공격(무차별 대입, 사전 공격)을 병행하면 관리자 권한을 탈취할 수 있습니다.
- 관리자 권한을 탈취하면 웹 서버를 완전히 장악할 수 있습니다.

**보안 위협:**
- 계정명 노출로 인한 무차별 대입 공격(brute force) 가능성 증가
- 관리자 권한 탈취로 인한 시스템 장악
- 데이터 유출 및 변조
- 악성코드 설치 및 서버를 botnet으로 악용

### 5. 보안 프레임워크 대응

| 프레임워크 | 항목 | 관련 요구사항 |
|----------|------|-------------|
| **CIS Benchmarks** | Apache Tomcat 8.5 | Ensure default accounts are removed |
| **NIST 800-53** | AC-2, IA-2 | Account Management, Identification and Authentication |
| **ISO 27001:2013** | A.9.2.3 | Management of system access privileges |
| **K-ISMS** | 2.5.1 | 계정 관리 |
| **PCI DSS** | 8.1.5 | ID management - Remove/disable non-essential accounts |

### 3. 점검 대상

- **Tomcat**: Apache Tomcat 웹 서버
- **JEUS**: Tmax JEUS 웹 애플리케이션 서버

### 4. 판단 기준

- **양호**: 관리자 페이지를 사용하지 않거나, 계정명이 기본 계정명으로 설정되어 있지 않은 경우
- **취약**: 계정명이 기본 계정명으로 설정되어 있거나, 추측하기 쉬운 문자 조합으로 이루어진 계정명을 사용하는 경우

### 5. 점검 방법

#### Tomcat

```bash
# server.xml 파일 확인
cat /<Tomcat 설치 디렉터리>/conf/tomcat-users.xml

# 기본 계정 확인 예시
# <user username="admin" password="..." roles="manager-gui"/>
# <user username="tomcat" password="..." roles="manager-gui"/>
```

#### JEUS

JEUS 관리 콘솔에서 Security > Security Domains > Account & Policies Management > Users 메뉴에서 기본 관리자 계정명(`administrator`) 확인

### 6. 조치 방법

#### Tomcat

**Step 1) 기본 계정명 변경 또는 관리자 페이지 비활성화**

```bash
# vi <Tomcat 설치 디렉터리>/conf/tomcat-users.xml
```

```xml
<!-- 변경 전 (취약) -->
<user username="admin" password="XNDJxndn264!@" roles="manager-gui"/>

<!-- 변경 후 (양호) -->
<user username="secadmin2024" password="XNDJxndn264!@" roles="manager-gui"/>
```

**Step 2) Tomcat 재구동**

```bash
systemctl restart tomcat
```

**참고**: `roles="manager-gui, manager-script, manager-jmx, manager-status"` 설정 시 관리자 계정 및 페이지가 활성화됩니다. 관리자 페이지가 필요 없는 경우 이 설정을 제거하는 것을 권장합니다.

#### JEUS

**Step 1) JEUS 관리 콘솔에서 계정 변경**

1. Security → Security Domains 페이지 해당 도메인 선택
2. Account & Policies Management → Users 메뉴 이동
3. 기본 관리자 계정의 Name 확인
4. Lock & EDIT 클릭
5. Security → Security Domains → 해당 도메인 → Account & Policies Management → Users → ADD 클릭
6. 기본 관리자 계정의 Name을 유추하기 어려운 계정 이름 입력 (예: `jeusadmin2024`)
7. Administrators 그룹 체크 후 확인
8. Accounts & Policies Management → policies → Role Permissions → AdministratorsRole 이동
9. 'Activate Changes' 클릭하여 설정 저장

**Step 2) JEUS 재구동**

```bash
# 서버 중지
./stopServer -host [도메인명]:[포트 번호]

# 서버 시작
./startDomainAdminServer -host [도메인명]:[포트 번호]
```

**참고**: 웹 서비스명과 연관된 단어(예: `administrator`)를 계정명으로 사용하는 것을 금지합니다. 기본 계정명 변경이 불가능한 경우 초기 비밀번호를 강력한 비밀번호로 변경하여 보완해야 합니다.

### 7. 조치 시 주의사항

- 일반적인 경우 영향이 없습니다.
- 관리자 페이지를 통해 운영 중인 서비스가 있는 경우, 관리자 계정명 변경 후 반드시 새 계정명으로 로그인 가능한지 확인해야 합니다.
- 기본 계정명 변경이 불가능한 환경에서는 반드시 강력한 비밀번호와 2단계 인증(가능한 경우)을 설정하여 보완하세요.

### 8. 참고 자료

- Apache Tomcat 공식 문서: https://tomcat.apache.org/
- Tmax JEUS 가이드: https://technet.tmaxsoft.com/

## 요약

웹 서비스의 기본 관리자 계정명을 변경하여 공격자의 추측 공격을 차단하고 관리자 권한 탈취를 방지하는 것이 핵심입니다.
