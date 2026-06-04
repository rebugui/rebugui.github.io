---
title: "[2026 주요정보통신기반시설] WEB-03 비밀번호파일권한관리"
slug: "2026-주정통/WEB-03"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "비밀번호파일에대해적절한접근권한설정여부점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Web
---

# WEB-03 비밀번호파일권한관리

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | WEB-03 |
| **점검내용** | 비밀번호파일에대해적절한접근권한설정여부점검 |
| **점검대상** | Tomcat, IIS, JEUS |
| **판단기준** | 양호: 비밀번호파일에권한이600이하로설정된경우 |
| **판단기준** | 취약: 비밀번호파일에권한이600초과로설정된경우 |
| **조치방법** | 비밀번호파일권한600이하로설정 |

---
## 상세 설명

### 1. 항목 개요

비밀번호 파일은 웹 서비스의 핵심 보안 정보를 담고 있습니다. 아무리 강력한 비밀번호를 사용하더라도, 비밀번호 파일 자체가 일반 사용자들이 읽을 수 있는 상태라면 보안의 의미가 없습니다. 집의 보안을 아무리 강화해도 현관문 열쇠를 아무나 열 수 있는 곳에 두는 것과 같습니다. 비밀번호 파일의 권한 관리는 웹 서비스 보안의 기초 중의 기초입니다.

### 2. 왜 이 항목이 필요한가요?

**실제 시나리오:**
- 공격자가 웹 서버에 일반 사용자 권한으로 접속합니다.
- 비밀번호 파일의 권한이 느슨하게 설정되어 있어 파일 내용을 확인할 수 있습니다.
- 비밀번호 파일에서 관리자 비밀번호를 획득합니다.
- 획득한 비밀번호로 관리자 권한을 탈취합니다.

**파일 권한 이해하기:**
- **600 (rw-------)**: 소유자만 읽기/쓰기 가능 (가장 안전)
- **640 (rw-r-----)**: 소유자와 그룹만 읽기/쓰기 가능
- **644 (rw-r--r--)**: 모든 사용자가 읽기 가능 (취약)

**보안 위협:**
- 비밀번호 평문 또는 해시값 노출
- 무차별 대입 공격(brute force)으로 비밀번호 크래킹 가능
- 관리자 권한 탈취로 이어질 수 있는 경로 제공
- 다른 시스템의 비밀번호 재사용 시 연쇄적 침해 위험

### 3. 점검 대상

- **Tomcat**: Apache Tomcat 웹 서버 (tomcat-users.xml)
- **IIS**: Microsoft Internet Information Services (SAM 파일)
- **JEUS**: Tmax JEUS 웹 애플리케이션 서버 (accounts.xml, policies.xml)

### 4. 판단 기준

- **양호**: 비밀번호 파일에 권한이 600 이하로 설정된 경우
- **취약**: 비밀번호 파일에 권한이 600 초과로 설정된 경우

### 5. 점검 방법

#### Tomcat

```bash
# 비밀번호 파일 권한 확인
ls -al /<Tomcat 설치 디렉터리>/conf/tomcat-users.xml

# 출력 예시
# -rw-r--r-- 1 root root 1234 Jan 20 10:00 tomcat-users.xml (취약: 644)
# -rw------- 1 root root 1234 Jan 20 10:00 tomcat-users.xml (양호: 600)
```

#### IIS

```powershell
# SAM 파일 권한 확인
# 파일 탐색기에서 %systemroot%\system32\config\SAM 파일 우클릭
# 속성 > 보안 탭 확인
```

#### JEUS

```bash
# 비밀번호 파일 권한 확인
ls -al /<JEUS 설치 디렉터리>/jeus_domain/config/security/SYSTEM_DOMAIN/accounts.xml
ls -al /<JEUS 설치 디렉터리>/jeus_domain/config/security/SYSTEM_DOMAIN/policies.xml
```

### 6. 조치 방법

#### Tomcat

**Step 1) tomcat-users.xml 파일 권한 변경**

```bash
chmod 600 /<Tomcat 설치 디렉터리>/conf/tomcat-users.xml

# 권한 변경 확인
ls -al /<Tomcat 설치 디렉터리>/conf/tomcat-users.xml
# -rw------- 1 root root 1234 Jan 20 10:00 tomcat-users.xml
```

#### IIS

**Step 1) SAM 파일 보안 설정**

1. 파일 탐색기에서 `%systemroot%\system32\config\SAM` 파일 우클릭
2. 속성 > 보안 탭 클릭
3. 편집 버튼 클릭
4. Administrators, SYSTEM을 제외한 모든 계정 및 그룹 선택 후 제거 클릭

<!-- 이미지 파일 없음 -->

#### JEUS

**Step 1) 비밀번호 파일 권한 변경**

```bash
# accounts.xml 파일 권한 변경
chmod 600 /<JEUS 설치 디렉터리>/jeus_domain/config/security/SYSTEM_DOMAIN/accounts.xml

# policies.xml 파일 권한 변경
chmod 600 /<JEUS 설치 디렉터리>/jeus_domain/config/security/SYSTEM_DOMAIN/policies.xml

# 권한 변경 확인
ls -al /<JEUS 설치 디렉터리>/jeus_domain/config/security/SYSTEM_DOMAIN/
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
- 권한 변경 후 웹 서비스가 정상적으로 동작하는지 확인해야 합니다.
- 일부 웹 서버는 설정 파일을 읽기 위해 특정 그룹 권한이 필요할 수 있습니다. 이 경우 640 권한으로 설정하거나 해당 그룹에만 읽기 권한을 부여하세요.
- 정기적으로 비밀번호 파일의 권한이 올바르게 설정되어 있는지 모니터링해야 합니다.
- 백업 파일이나 임시 파일의 권한도 동일하게 제한해야 합니다.

### 8. 참고 자료

- Linux 파일 권한 가이드: https://wiki.archlinux.org/title/File_permissions_and_attributes
- Apache Tomcat 보안 가이드: https://tomcat.apache.org/tomcat-9.0-doc/security-howto.html
- CWE-732: Incorrect Permission Assignment for Critical Resource

## 요약

비밀번호 파일의 접근 권한을 600 이하로 설정하여 비인가자의 비밀번호 정보 접근을 차단하고 비밀번호 유출을 방지해야 합니다.
