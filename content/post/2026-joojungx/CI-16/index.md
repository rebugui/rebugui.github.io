---
title: "[2026 주요정보통신기반시설] CI-16 불충분한세션관리(Insufficient Session Management)"
slug: "2026-주정통/CI-16"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "세션 만료 기간 설정, 예측 가능한 세션 ID 생성, 고정된 세션 ID 발행 등 세션 관리 정책을 점검하고, 인증토큰(JWT등)사용시에도안전한서명알고리즘사용여부,안전한비밀키사용여부,토큰만료 등의정책점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Web
---

# 불충분한세션관리(Insufficient Session Management)

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | CI-16 |
| **점검내용** | 세션 만료 기간 설정, 예측 가능한 세션 ID 생성, 고정된 세션 ID 발행 등 세션 관리 정책을 점검하고, 인증토큰(JWT등)사용시에도안전한서명알고리즘사용여부,안전한비밀키사용여부,토큰만료 등의정책점검 |
| **점검대상** | 웹 애플리케이션 소스코드, 웹 애플리케이션 서버 |
| **양호기준** | 추측불가능한세션ID가발급되고,세션종료시간이설정되어있는경우 |
| **취약기준** | 세션 ID가 일정한 패턴으로 발급되거나 세션 종료 시간이 설정되지 않아 세션 재사용이 가능한 경우 |
| **조치방법** | 추측불가능한세션ID가발급되도록로직을구현하고,세션종료시간설정또는자동로그아웃기능을 구현하여사이트특성에맞게적정시간을설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 추측 불가능한 세션 ID가 발급되고, 세션 종료 시간이 설정되어 있는 경우
- **취약**: 세션 ID가 일정한 패턴으로 발급되거나 세션 종료 시간이 설정되지 않아 세션 재사용이 가능한 경우

#### 경계 케이스 (Edge Case) 처리 방법
- 세션 만료 시간은 서비스 특성에 맞게 설정 (10~60분 권장)
- 너무 짧은 만료 시간은 사용자 경험 저하
- 로그아웃 시 반드시 세션 무효화

#### 권장 설정값
- 세션 ID 최소 128비트 이상
- 세션 만료: 10~60분 (서비스 특성에 따라)
- JWT 알고리즘: HS256 이상
- JWT 비밀 키: 최소 256비트

### 2. 점검 방법

#### 세션(Session) 점검

**Step 1: 세션 ID 패턴 확인**
```
로그인 과정에서 발급받은 세션 ID를 확인하고 로그아웃 후 재 로그인 시 각각 발급받은 세션 ID에 대해 일정한 패턴이 존재하는지 검증
```

**Step 2: 세션 만료 확인**
```
로그인 후 웹 페이지 사용을 중지한 상태로 일정 시간이 경과하였을 때 세션이 유지되는지 확인
```

#### JWT(JSON Web Token) 점검

**Step 1: JWT 사용 확인**
```
사용자 인증 및 상태 유지를 위해 JWT가 사용되는지 확인
```

**Step 2: JWT 디코딩**
```
JWT의 헤더와 페이로드 부분을 Base64 디코딩하여 내용을 확인
```

**Step 3: 페이로드 변조 시도**
```
페이로드 변조 후 서명을 삭제하거나 None 알고리즘으로 변조하였을 때 토큰이 유효한지 확인
```

### 3. 조치 방법

#### 1. 세션 고정 및 예측 방지

**Java Spring Security:**
```java
// 세션 고정 방지
@Override
protected void configure(HttpSecurity http) throws Exception {
    http.sessionManagement()
        .sessionFixation().migrateSession()  // 로그인 시 새 세션 ID 발급
        .sessionCreationPolicy(SessionCreationPolicy.IF_REQUIRED)
        .maximumSessions(1)  // 동시 세션 1개로 제한
        .maxSessionsPreventsLogin(false)
        .expiredUrl("/login?expired");
}

// 로그인 시 세션 ID 변경
@RequestMapping("/login")
public String login(HttpServletRequest request) {
    request.changeSessionId();  // 신규 세션 ID 발급
    return "redirect:/home";
}
```

**ASP.NET web.config:**
```xml
<system.web>
    <!-- 세션 고정 방지 -->
    <sessionState regenerateExpiredSessionId="true" />

    <!-- 세션 예측 방지 -->
    <machineKey
        validationKey="AutoGenerate,IsolateApps"
        decryptionKey="AutoGenerate,IsolateApps"
        validation="HMACSHA512"
        decryption="AES" />
</system.web>
```

**PHP:**
```php
// 기존 세션 삭제 후 새 세션 ID 생성
session_start();
session_regenerate_id(true);

// 예측 불가능한 세션 ID 생성
ini_set('session.entropy_length', '256');
ini_set('session.entropy_file', '/dev/urandom');
```

#### 2. 세션 만료 설정

**Java web.xml:**
```xml
<session-config>
    <session-timeout>60</session-timeout>  <!-- 60분 -->
</session-config>
```

**Spring Boot application.properties:**
```properties
server.servlet.session.timeout=60m
```

**ASP.NET web.config:**
```xml
<configuration>
    <system.web>
        <sessionState timeout="60" />  <!-- 60분 -->
    </system.web>
</configuration>
```

**PHP php.ini:**
```ini
session.gc_maxlifetime = 3600  ; 60분 (3600초)
session.cookie_lifetime = 3600
```

#### 3. JWT 보안 설정

**안전한 서명 알고리즘:**
```javascript
// 안전한 알고리즘 사용
const jwt = require('jsonwebtoken');

const token = jwt.sign(
    { userId: user.id, role: user.role },
    process.env.JWT_SECRET,  // 강력하고 랜덤한 비밀 키
    {
        algorithm: 'HS256',  // 안전한 알고리즘 명시
        expiresIn: '1h'       // 짧은 만료 시간
    }
);

// 검증 시 알고리즘 명시
jwt.verify(token, process.env.JWT_SECRET, {
    algorithms: ['HS256']  // none 알고리즘 차단
});
```

**안전한 JWT 서명 알고리즘:**
- HS256, HS384, HS512 (HMAC-SHA)
- RS256, RS384, RS512 (RSA)
- ES256, ES384, ES512 (Elliptic Curve)

**취약한 알고리즘:**
- HS1, RS1 (SHA-1 기반)
- none (서명 없음)
- plaintext (평문 서명)

#### 4. 동시 세션 제어

```java
// 동시 접속 세션 제한
@Override
protected void configure(HttpSecurity http) throws Exception {
    http.sessionManagement()
        .maximumSessions(1)  // 최대 1개 세션
        .maxSessionsPreventsLogin(false)  // 이전 세션 만료
        .expiredUrl("/login?expired");
}
```

### 4. 참고 자료

**세션 타임아웃 권장:**
- 금융 서비스: 10~30분
- 쇼핑몰: 30~60분
- 뉴스/블로그: 60~120분

**JWT 토큰 관리:**
- 비밀 키는 최소 256비트 이상
- 비밀 키는 환경 변수로 관리
- 리프레시 토큰과 액세스 토큰 분리

**세션 관리 모범 사례:**
1. 로그인 시 항상 새 세션 ID 발급
2. 예측 불가능한 세션 ID 생성 (최소 128비트)
3. 적절한 세션 만료 시간 설정
4. 로그아웃 시 세션 즉시 무효화
5. 동시 세션 수 제한

**JWT 보안 체크리스트:**
- [ ] 안전한 서명 알고리즘 사용 (HS256 이상)
- [ ] 강력하고 랜덤한 비밀 키 사용
- [ ] 짧은 만료 시간 설정 (1시간 이내 권장)
- [ ] 알고리즘 명시적 검증 (none 차단)
- [ ] 리프레시 토큰 사용
- [ ] 토큰 폐기 리스트 관리

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.