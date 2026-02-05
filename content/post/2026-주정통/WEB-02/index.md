---
title: "[2026 주요정보통신기반시설] WEB-02 취약한비밀번호사용제한"
slug: "2026-주정통/WEB-02"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "관리자계정의취약한비밀번호설정여부점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Web
---

# WEB-02 취약한비밀번호사용제한

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | WEB-02 |
| **점검내용** | 관리자계정의취약한비밀번호설정여부점검 |
| **점검대상** | Tomcat, IIS, JEUS |
| **판단기준** | 양호: 관리자비밀번호가암호화되어있거나,유추하기어려운비밀번호로설정된경우 |
| **판단기준** | 취약: 관리자비밀번호가암호화되어있지않거나,유추하기쉬운비밀번호로설정된경우 |
| **조치방법** | 복잡도기준에맞는추측하기어려운비밀번호설정 |

---
## 상세 설명

### 1. 항목 개요

비밀번호는 관리자 계정의 마지막 방어선입니다. 아무리 계정명을 변경하더라도 비밀번호가 `1234`, `admin123`, `password1` 같이 취약하다면 공격자는 쉽게 관리자 권한을 탈취할 수 있습니다. 현대의 공격 도구는 초당 수천에서 수만 개의 비밀번호를 시도할 수 있으므로, 강력한 비밀번호 정책은 필수적입니다.

### 2. 비유로 이해하기

취약한 비밀번호는 **"지갑문 열쇠를 문밑에 두는 것"**과 같습니다.

- **취약한 비밀번호** = "1234", "password" (쉽게 열림)
- **강력한 비밀번호** = 복잡한 조합 (열기 어려움)

예시:
```bash
# 공격자 시도
# 사전 공격 (가장 많이 사용되는 비밀번호)
1234, password, admin, qwerty, 12345678...

# 웹 관리자 로그인
POST /manager/html
username=admin&password=123456  # 1초 만에 성공!
```

### 3. 기술적 배경

**비밀번호 크래킹 속도**:
```bash
# 현대적인 GPU 기반 공격
Hashcat:
- MD5: 초당 100억 개 시도
- SHA-256: 초당 10만 개 시도
- SHA-512: 초당 5만 개 시도

# 6자리 소문자 비밀번호
26^6 = 308,915,776 조합
GPU로는 0.03초 만에 크랙 가능!
```

**웹 비밀번호 공격 도구**:
```bash
# 1. Hydra로 무차별 대입
hydra -L users.txt -P pass.txt http-post-form://target-server/manager

# 2. Burp Suite Intruder
# 웹 요청 캡처 후 무차별 대입 공격

# 3. SQLMap
# 관리자 페이지 발견 후 비밀번호 스프레이
```

### 4. 왜 이 항목이 필요한가요?

**실제 시나리오:**
- 공격자가 웹 서비스 관리자 페이지를 발견합니다.
- 자동화된 도구로 일반적인 비밀번호 목록(사전攻击)을 순차적으로 시도합니다.
- 취약한 비밀번호를 사용 중인 경우 몇 분 만에 관리자 권한을 탈취할 수 있습니다.

**비밀번호 유추 공격 유형:**
- **사전 공격(Dictionary Attack)**: 자주 사용되는 비밀번호 목록으로 공격
- **무차별 대입 공격(Brute Force)**: 가능한 모든 문자 조합 시도
- **패턴 분석**: 사용자 정보, 생일, 전화번호 등 개인정보 활용

**보안 위협:**
- 관리자 권한 탈취로 인한 서버 장악
- 중요 데이터 유출 및 변조
- 악성코드 설치 및 서버 악용
- 다른 시스템으로의 공격 경로 제공

**실제 공격 시나리오**:
```bash
# 1. 관리자 페이지 발견
curl http://target-server/manager/html
# 401 Unauthorized 인증 필요

# 2. 무차별 대입 공격
hydra -l admin -P /usr/share/wordlists/rockyou.txt http-post-form://target-server/manager
# [DATA] attacking: http://target-server:80/manager
# [STATUS] attack successful (admin:admin123)

# 3. 로그인 성공
curl -u admin:admin123 http://target-server/manager/html/upload
# WAR 파일 업로드 → 악성코드 설치
```

### 5. 보안 프레임워크 대응

| 프레임워크 | 항목 | 관련 요구사항 |
|----------|------|-------------|
| **CIS Benchmarks** | Tomcat, Apache | Ensure strong password policy |
| **NIST 800-53** | IA-5, AC-2 | Authenticator Management, Account Management |
| **ISO 27001:2013** | A.9.3.1 | Password management |
| **K-ISMS** | 2.3.1 | 비밀번호 관리 |
| **PCI DSS** | 8.2.3 | Secure authentication |

### 3. 점검 대상

- **Tomcat**: Apache Tomcat 웹 서버
- **IIS**: Microsoft Internet Information Services
- **JEUS**: Tmax JEUS 웹 애플리케이션 서버

### 4. 판단 기준

- **양호**: 관리자 비밀번호가 암호화되어 있거나, 유추하기 어려운 비밀번호로 설정된 경우
- **취약**: 관리자 비밀번호가 암호화되어 있지 않거나, 유추하기 쉬운 비밀번호로 설정된 경우

### 5. 점검 방법

#### Tomcat

```bash
# tomcat-users.xml 파일 확인
cat /<Tomcat 설치 디렉터리>/conf/tomcat-users.xml

# 비밀번호 확인
# <user username="admin" password="XNDJxndn264!@" roles="manager-gui"/>
```

#### IIS

```powershell
# SAM 파일 권한 확인
# %systemroot%\system32\config\SAM 파일 속성 > 보안 확인
```

#### JEUS

JEUS 관리 콘솔에서 관리자 계정의 비밀번호 복잡도 확인

### 6. 조치 방법

#### 비밀번호 설정 기준

**1. 길이 및 복잡도 요구사항**
- 영문, 숫자, 특수문자를 조합하여 계정명과 상이한 자 이상의 비밀번호 설정
- 다음 문자 종류 중 2종류 이상을 조합하여 최소 10자리 이상 또는 3종류 이상을 조합하여 최소 8자리 이상 구성
  - 영문 대문자 (26개)
  - 영문 소문자 (26개)
  - 숫자 (10개)
  - 특수문자 (32개)

**2. 비밀번호 안전성 원칙**
- Null(공백) 비밀번호 사용 금지
- 문자 또는 숫자만으로 구성 금지
- 사용자 ID와 같거나 유사한 비밀번호 금지
- 연속적인 문자나 숫자 사용 금지 (예: 1111, 1234, abcd)
- 주기성 비밀번호 재사용 금지
- 전화번호, 생일과 같이 추측하기 쉬운 개인정보 사용 금지

**3. 사용하면 안 되는 비밀번호 예시**
- Null, 계정과 같거나 유사한 스트링
- 지역명, 부서명, 담당자명, 대표 업무명
- `root`, `rootroot`, `root123`, `123root`
- `admin`, `admin123`, `123admin`, `osadmin`, `adminos`

#### Tomcat

**Step 1) 복잡도를 만족하는 비밀번호 설정**

```bash
vi <Tomcat 설치 디렉터리>/conf/tomcat-users.xml
```

```xml
<!-- 변경 전 (취약) -->
<user username="admin" password="admin123" roles="manager-gui"/>

<!-- 변경 후 (양호) -->
<user username="admin" password="XNDJxndn264!@" roles="manager-gui"/>
```

**Step 2) Tomcat 재시작**

```bash
systemctl restart tomcat
```

**참고**: SHA-256 이상 암호화 방식으로 비밀번호를 설정해야 합니다.

#### IIS

**Step 1) SAM 파일 보안 설정**

1. `%systemroot%\system32\config\SAM` 파일 우클릭
2. 속성 > 보안 > 편집 클릭
3. Administrators, SYSTEM을 제외한 계정 및 그룹 권한 제거

#### JEUS

**Step 1) JEUS 관리 콘솔에서 비밀번호 변경**

1. Lock & EDIT 클릭
2. Security > Security Domains > 해당 도메인 > Account & Policies Management > Users 이동
3. 기본 관리자 계정 선택 > 비밀번호 변경 클릭
4. 복잡도 기준을 만족하는 비밀번호 입력
5. 확인 클릭
6. 'Activate Changes' 클릭하여 설정 저장

### 7. 조치 시 주의사항

- 일반적인 경우 영향이 없습니다.
- 비밀번호 변경 후 반드시 새 비밀번호로 로그인하여 정상 작동하는지 확인하세요.
- 비밀번호 변경 시 기존 세션이 만료될 수 있으므로 운영 중인 서비스에 영향이 없도록 주의해야 합니다.
- 비밀번호 파일의 접근 권한을 600으로 설정하여 비밀번호 정보 노출을 방지해야 합니다.

### 8. 참고 자료

- Apache Tomcat 보안 가이드: https://tomcat.apache.org/tomcat-9.0-doc/security-howto.html
- Microsoft IIS 보안 베스트 프랙티스: https://docs.microsoft.com/en-us/iis/
- NIST SP 800-63B: Digital Identity Guidelines

## 요약

관리자 비밀번호의 복잡도 기준을 준수하여 비인가자의 비밀번호 유추 공격을 차단하고 관리자 권한 탈취를 방지해야 합니다.
