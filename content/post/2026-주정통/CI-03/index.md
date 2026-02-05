---
title: "[2026 주요정보통신기반시설] CI-03 디렉터리인덱싱(Directory Indexing)"
slug: "2026-주정통/CI-03"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "웹애플리케이션서버내 디렉터리 인덱싱 취약점 존재 여부 점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Web
---

# 디렉터리인덱싱(Directory Indexing)

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | CI-03 |
| **점검내용** | 웹애플리케이션서버내 디렉터리 인덱싱 취약점 존재 여부 점검 |
| **점검대상** | 웹 애플리케이션서버 |
| **양호기준** | 디렉터리 파일 리스트가 노출되지 않는 경우 |
| **취약기준** | 디렉터리 파일 리스트가 노출되는 경우 |
| **조치방법** | 웹애플리케이션서버 설정을 변경하여 디렉터리 파일 리스트가 노출되지 않도록 설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 디렉터리 파일 리스트가 노출되지 않는 경우
- **취약**: 디렉터리 파일 리스트가 노출되는 경우

#### 경계 케이스 (Edge Case) 처리 방법
- 디렉터리 목록을 의도적으로 사용하는 기능이 있을 경우 해당 기능 사용 불가
- 이 경우 별도의 인증 절차를 도입하여 접근 제어 필요

#### 권장 설정값
- Apache: `Options -Indexes` 또는 `Indexes` 옵션 제거
- Nginx: `autoindex off;`
- IIS: 디렉터리 검사(또는 디렉터리 검색) 비활성화

### 2. 점검 방법

#### Step 1: URL 직접 접근 테스트
```
URL 경로 중 확인하고자 하는 디렉터리 경로에 대하여 주소창에 입력하여 인덱싱 여부 확인
```

**테스트할 URL 예시:**
```
https://example.com/images/
https://example.com/css/
https://example.com/js/
https://example.com/upload/
https://example.com/backup/
https://example.com/admin/
```

**노출되는 정보 예시:**
- 파일 이름
- 파일 크기
- 수정 날짜
- 파일 설명

### 3. 조치 방법

#### 1. Apache 서버

**httpd.conf 또는 apache2.conf 파일 수정:**
```apache
<Directory /var/www/html>
    # Indexes 옵션 제거
    # Options Indexes FollowSymLinks
    Options FollowSymLinks
</Directory>
```

#### 2. Tomcat 서버

**web.xml 파일 수정:**
```xml
<init-param>
    <param-name>listings</param-name>
    <param-value>false</param-value>
</init-param>
```

#### 3. Nginx 서버

**/etc/nginx/sites-available/default 파일 수정:**
```nginx
server {
    location / {
        autoindex off;
    }
}
```

#### 4. IIS 6.0 이하

1. 인터넷 정보 서비스(IIS) 관리자 실행
2. 해당 웹 사이트 선택 → 등록 정보
3. 홈 디렉터리 탭 → 디렉터리 검색 체크 해제
4. 서비스 재시작

#### 5. IIS 7.0 이상

1. IIS 관리자 실행
2. 해당 사이트 선택
3. 디렉터리 검색 → 사용 안 함 선택
4. 적용 버튼 클릭

### 4. 참고 자료

**자주 노출되는 민감한 파일:**
- 설정 파일: `web.config`, `database.php`, `.env`
- 백업 파일: `backup.sql`, `dump.sql`, `config.bak`
- 소스 코드: `.java`, `.class`, `.cs`, `.vb`
- 로그 파일: `error.log`, `access.log`, `debug.log`
- 키 파일: `api_key.txt`, `secret.key`, `private.pem`

**OWASP 권장사항:**
- 모든 디렉터리에 기본 문서(index.html 등) 배치
- 디렉터리 목록 기능 비활성화
- 불필요한 파일 및 백업 파일 삭제
- 파일 접근 권한 적절히 설정

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.