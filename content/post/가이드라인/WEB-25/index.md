---
title: "[2026 주요정보통신기반시설] WEB-25 주기적보안패치및벤더권고사항적용"
slug: "2026-주정통/WEB-25"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "소프트웨어 보안 패치는 알려진 취약점을 수정하고 보안을 강화하는 가장 기본적이고 중요한 활동입니다. 웹 서버는 인터넷에 직접 노출되어 있어 지속적인 공격에 노출되어 있으므로 최신"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Web
---

# WEB-25 주기적보안패치및벤더권고사항적용

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | WEB-25 |
| **점검내용** | 소프트웨어 보안 패치는 알려진 취약점을 수정하고 보안을 강화하는 가장 기본적이고 중요한 활동입니다. 웹 서버는 인터넷에 직접 노출되어 있어 지속적인 공격에 노출되어 있으므로 최신  |
| **점검대상** | Apache, Tomcat, Nginx, IIS, JEUS, WebtoB |
| **판단기준** | 양호: 최신 보안 패치가 적용되어 있으며, 패치 적용 정책을 수립하여 주기적인 패치 관리를 하는 경우 |
| **판단기준** | 취약: 최신 보안 패치가 적용되어 있지 않거나 패치 적용 정책을 수립 및 주기적인 패치 관리를 하지 않는 경우 |
| **조치방법** | 상세 조치 방법 참고 |

---
---
## 상세 설명

### 1. 항목 개요

소프트웨어 보안 패치는 알려진 취약점을 수정하고 보안을 강화하는 가장 기본적이고 중요한 활동입니다. 웹 서버는 인터넷에 직접 노출되어 있어 지속적인 공격에 노출되어 있으므로 최신 보안 패치를 유지하는 것은 필수적입니다. 마치 집 현관문 자물쇠가 고장될 때마다 수리하는 것과 같습니다. 보안 패치는 지속적인 프로세스여야 합니다.

### 2. 왜 이 항목이 필요한가요?

**실제 시나리오:**
- 웹 서버가 Apache 2.4.41 버전을 사용 중입니다.
- 2021년에 Apache 2.4.49의 경로 순회 취약점(CVE-2021-41773)이 발견되었습니다.
- 공격자가 이 취약점을 악용하여 시스템 파일에 접근합니다.
- 최신 버전으로 패치하지 않았기 때문에 공격에 성공합니다.

**보안 패치가 필요한 이유:**
- **알려진 취약점 수정**: CVE에 등록된 취약점 해결
- **0-Day 공격 방어**: 새로운 공격 기법 차단
- **시스템 안정성**: 버그 수정으로 안정성 향상
- **규정 준수**: 보안 규정(개인정보보호법 등) 준수

**패치 관리 주요 사항:**
- **정기적 점검**: 월간, 분기별 보안 패치 확인
- **긴급 패치**: 심각한 취약점(CVSS 9.0 이상) 즉시 적용
- **테스트**: 패치 전 테스트 환경에서 검증
- **백업**: 패치 전 시스템 백업
- **문서화**: 패치 이력 기록

### 3. 점검 대상

- **Apache**: Apache HTTP Server
- **Tomcat**: Apache Tomcat 웹 서버
- **Nginx**: Nginx 웹 서버
- **IIS**: Microsoft Internet Information Services
- **JEUS**: Tmax JEUS 웹 애플리케이션 서버
- **WebtoB**: Tmax WebtoB 웹 서버

### 4. 판단 기준

- **양호**: 최신 보안 패치가 적용되어 있으며, 패치 적용 정책을 수립하여 주기적인 패치 관리를 하는 경우
- **취약**: 최신 보안 패치가 적용되어 있지 않거나 패치 적용 정책을 수립 및 주기적인 패치 관리를 하지 않는 경우

### 5. 점검 방법

#### Apache

```bash
# 웹 서버 버전과 최신 패치 버전을 비교하여 확인
/<Apache 설치 디렉터리>/httpd -v
```

**출력 예시:**
```bash
Server version: Apache/2.4.41 (Ubuntu)
Server built:   2022-01-20T10:00:00
```

<!-- ![Apache 웹 서버 버전 확인](../images/04_웹서비스/image_0030.png) -->

**참고 사이트**: http://httpd.apache.org/download.cgi

#### Tomcat

```bash
# 웹 서버 버전과 최신 패치 버전을 비교하여 확인
cd /<Tomcat 설치 디렉터리>/lib
java -cp catalina.jar org.apache.catalina.util.ServerInfo
```

<!-- ![Tomcat 웹 서버 버전 확인](../images/04_웹서비스/image_0031.png) -->

**참고 사이트**: https://tomcat.apache.org/

#### Nginx

```bash
# 웹 서버 버전과 최신 패치 버전을 비교하여 확인
/<Nginx Dir>/nginx -v
```

<!-- ![Nginx 웹 서버 버전 확인](../images/04_웹서비스/image_0032.png) -->

**참고 사이트**: https://nginx.org/en/download.html

#### IIS

```powershell
# 웹 서버 버전과 최신 패치 버전을 비교하여 확인
reg query 'HKLM\SOFTWARE\Microsoft\InetStp' /v VersionString
```

<!-- ![Windows Server 버전 확인](../images/04_웹서비스/image_0033.png) -->

**참고 사이트**: https://www.iis.net/downloads/microsoft

#### JEUS

```bash
# 웹 서버 버전과 최신 패치 버전을 비교하여 확인
jeusadmin -version
# 또는
jeusadmin -fullversion
```

**참고 사이트**: https://technet.tmaxsoft.com/ko/front/download/findDownloadList.do

#### WebtoB

```bash
# 웹 서버 버전과 최신 패치 버전을 비교하여 확인
wscfl -version
```

**참고 사이트**: https://technet.tmaxsoft.com/ko/front/download/findDownloadList.do?cmProductCode=0102

### 6. 조치 방법

**Step 1) 현재 버전 확인**

각 웹 서버의 버전 확인 명령어 실행

**Step 2) 최신 버전 및 보안 패치 확인**

각 벤더의 공식 웹사이트에서 최신 버전 및 보안 권고사항 확인

**Step 3) 보안 패치 적용 정책 수립**

```
[보안 패치 정책 예시]

1. 주기적 점검
   - 월간: 일반 보안 패치 확인
   - 분기별: 전체 시스템 보안 점검

2. 긴급 패치
   - CVSS 9.0 이상: 7일 이내 적용
   - CVSS 7.0-8.9: 30일 이내 적용
   - CVSS 6.0 이하: 다음 정기 점검 시 적용

3. 패치 프로세스
   - 백업 → 테스트 → 적용 → 검증 → 문서화

4. 예외 절차
   - 운영상 적용 불가 시: 완화 조치 수립
   - 임시 조치: WAF, 네트워크 보안 장비 활용
```

**Step 4) 보안 패치 적용**

1. 시스템 백업
2. 테스트 환경에서 패치 적용 및 테스트
3. 운영 환경에 패치 적용
4. 정상 작동 여부 확인
5. 패치 이력 기록

**Step 5) 주기적인 모니터링**

- 보안 권고사항 메일링 가입
- CVE 데이터베이스 주기적 검색
- 벤더 보안 알림 확인

### 7. 조치 시 주의사항

- 시스템 영향도를 파악하여 충분한 테스트 후 적용을 권고합니다.
- 패치 적용 전 반드시 백업을 수행하세요.
- 테스트 환경에서 먼저 검증 후 운영 환경에 적용하세요.
- 롤백 계획을 수립해야 합니다.
- 패치 중 서비스 중단 시간을 고려해야 합니다.
- 주요 보안 패치는 즉시 적용하는 것을 권장합니다.
- 정기적인 보안 패치 관리 정책을 수립하고 문서화하세요.

### 8. 참고 자료

- CVE Detail: https://www.cvedetails.com/
- NVD - National Vulnerability Database: https://nvd.nist.gov/
- Apache Security Reports: https://httpd.apache.org/security_report.html
- Tomcat Security: https://tomcat.apache.org/security-issues.html
- Nginx Security Advisories: https://nginx.org/en/security_advisories.html
- Microsoft Security Bulletin: https://msrc.microsoft.com/
- CVE Scoring: https://www.first.org/cvss/calculator/3.1

## 요약

주기적인 보안 패치 적용 정책을 수립하고 최신 보안 패치를 적용하여 알려진 취약점을 통한 공격을 방지해야 합니다.
