---
title: "[2026 주요정보통신기반시설] WEB-23 LDAP알고리즘적절하게구성"
slug: "2026-주정통/WEB-23"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "LDAP(Lightweight Directory Access Protocol)은 네트워크상에서 사용자 정보, 조직 정보 등을 조회하고 관리하는 표준 프로토콜입니다. 웹 서비스에서"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Web
---

# WEB-23 LDAP알고리즘적절하게구성

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | WEB-23 |
| **점검내용** | LDAP(Lightweight Directory Access Protocol)은 네트워크상에서 사용자 정보, 조직 정보 등을 조회하고 관리하는 표준 프로토콜입니다. 웹 서비스에서  |
| **점검대상** | Tomcat |
| **판단기준** | 양호: LDAP 연결 인증 시 안전한 비밀번호 다이제스트 알고리즘을 사용하는 경우 |
| **판단기준** | 취약: LDAP 연결 인증 시 안전한 비밀번호 다이제스트 알고리즘을 사용하지 않는 경우 |
| **조치방법** | 상세 조치 방법 참고 |

---
---
## 상세 설명

### 1. 항목 개요

LDAP(Lightweight Directory Access Protocol)은 네트워크상에서 사용자 정보, 조직 정보 등을 조회하고 관리하는 표준 프로토콜입니다. 웹 서비스에서 LDAP을 사용하여 인증을 수행할 때, 비밀번호 다이제스트(해시) 알고리즘이 중요합니다. 취약한 알고리즘(MD5, SHA-1 등)을 사용하면 공격자가 비밀번호를 크래킹할 수 있습니다. 마치 집 현관문 자물쇠가 쉽게 따질 수 있는 래치형 잠금장치인 것과 같습니다.

### 2. 왜 이 항목이 필요한가요?

**실제 시나리오:**
- 웹 서비스가 LDAP 인증을 사용합니다.
- 비밀번호 다이제스트 알고리즘으로 MD5 또는 SHA-1을 사용합니다.
- 공격자가 LDAP 트래픽을 스니핑합니다.
- 획득한 해시값을 무차별 대입 공격(Rainbow Table)으로 크래킹합니다.
- 취약한 알고리즘은 빠르게 크래킹 가능하여 비밀번호가 노출됩니다.

**다이제스트 알고리즘 안전성 비교:**
- **취약한 알고리즘**: MD5, SHA-1
  - 충돌 저항성 취약
  - 빠른 연산 속도로 크래킹 용이
  - Rainbow Table 공격 취약

- **권장 알고리즘**: SHA-256, SHA-384, SHA-512
  - 강력한 충돌 저항성
  - 느린 연산 속도로 크래킹 어려움
  - 솔트(Salt) 사용으로 Rainbow Table 방어

### 3. 점검 대상

- **Tomcat**: Apache Tomcat 웹 서버

### 4. 판단 기준

- **양호**: LDAP 연결 인증 시 안전한 비밀번호 다이제스트 알고리즘을 사용하는 경우
- **취약**: LDAP 연결 인증 시 안전한 비밀번호 다이제스트 알고리즘을 사용하지 않는 경우

### 5. 점검 방법

#### Tomcat

```bash
# 비밀번호 다이제스트 알고리즘 확인
grep 'digest=' /<Tomcat 설치 디렉터리>/conf/server.xml
```

**출력 예시:**
```xml
<!-- 취약 -->
<Realm className="org.apache.catalina.realm.JNDIRealm" digest="MD5" />
<Realm className="org.apache.catalina.realm.JNDIRealm" digest="SHA" />

<!-- 양호 -->
<Realm className="org.apache.catalina.realm.JNDIRealm" digest="SHA-256" />
```

### 6. 조치 방법

#### Tomcat

**Step 1) 비밀번호 다이제스트 알고리즘 확인 (LDAP 종류별 암호화 알고리즘 지원 여부 확인)**

```bash
grep -A 5 'JNDIRealm' /<Tomcat 설치 디렉터리>/conf/server.xml
```

**Step 2) 비밀번호 다이제스트 알고리즘 설정**

```bash
vi /<Tomcat 설치 디렉터리>/conf/server.xml
```

```xml
<!-- 변경 전 (취약) -->
<Realm className="org.apache.catalina.realm.JNDIRealm"
       connectionURL="ldap://localhost:389"
       digest="MD5"
       />
<!-- 또는 -->
<Realm className="org.apache.catalina.realm.JNDIRealm"
       connectionURL="ldap://localhost:389"
       digest="SHA"
       />

<!-- 변경 후 (양호) -->
<Realm className="org.apache.catalina.realm.JNDIRealm"
       connectionURL="ldap://localhost:389"
       digest="SHA-256"
       />
<!-- 또는 -->
<Realm className="org.apache.catalina.realm.JNDIRealm"
       connectionURL="ldaps://localhost:636"
       digest="SHA-512"
       />
```

**Step 3) Tomcat 재구동**

```bash
systemctl restart tomcat
```

**참고**: SHA-256 이상 암호화 알고리즘을 권고합니다. 가능하면 SHA-512 사용을 권장합니다.

**알고리즘별 비교:**

| 알고리즘    | 비트 수 | 보안성       | 권장 여부 |
|-----------|------|-----------|-------|
| MD5       | 128  | 취약 (충돌 발견) | 사용 금지  |
| SHA-1     | 160  | 취약 (충돌 발견) | 사용 금지  |
| SHA-256   | 256  | 양호        | 권장    |
| SHA-384   | 384  | 우수        | 권장    |
| SHA-512   | 512  | 우수        | 최우수 권장 |

### 7. 조치 시 주의사항

- 일반적인 경우 영향이 없습니다.
- LDAP 서버가 지원하는 알고리즘인지 확인 후 설정하세요.
- 다이제스트 알고리즘 변경 시 기존 비밀번호 해시와 호환되지 않을 수 있습니다.
- 변경 후 LDAP 인증이 정상 작동하는지 테스트해야 합니다.
- 가능하면 LDAPS(LDAP over SSL/TLS)를 함께 사용하는 것을 권장합니다.
- 솔트(Salt)를 적용한 해시 알고리즘을 사용하는 것을 권장합니다.

### 8. 참고 자료

- Apache Tomcat JNDIRealm: https://tomcat.apache.org/tomcat-9.0-doc/realm-howto.html#JNDIRealm
- NIST SP 800-131A: Transitions and Revision Guidance
- CWE-916: Use of Password Hash Instead of Password for Authentication
- OWASP Password Storage Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html

## 요약

LDAP 연결 인증 시 SHA-256 이상의 강력한 비밀번호 다이제스트 알고리즘을 사용하여 비밀번호 노출을 방지해야 합니다.
