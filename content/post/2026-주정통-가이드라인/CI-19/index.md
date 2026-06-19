---
title: "[2026 주요정보통신기반시설] CI-19 관리자페이지노출(Exposed Admin Page)"
slug: "2026-주정통/CI-19"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "유추가능한URL또는설계상의오류로인해관리자페이지및메뉴에접근가능여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Web
draft: true
---

# 관리자페이지노출(Exposed Admin Page)

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | CI-19 |
| **점검내용** | 유추가능한URL또는설계상의오류로인해관리자페이지및메뉴에접근가능여부점검 |
| **점검대상** | 웹 애플리케이션 소스코드, 웹 애플리케이션 서버, 웹방화벽 |
| **양호기준** | 유추하기쉬운URL로관리자페이지접근이불가능한경우 |
| **취약기준** | 유추하기쉬운URL로관리자페이지접근또는계정로그인이가능한경우 |
| **조치방법** | 유추하기어려운이름(포트번호변경포함)으로관리자페이지를변경하여비인가자가접근할수없도록 하고, 근본적인 해결을 위해 지정된 IP만 관리자 페이지에 접근할 수 있도록 제한함. 단, 부득이하게 관리자 페이지를 외부에 노출해야 하는 경우, 관리자 페이지 로그인 시 2차 인증(OTP, VPN, 인증서 등)을적용 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 유추하기 쉬운 URL로 관리자 페이지 접근이 불가능한 경우
- **취약**: 유추하기 쉬운 URL로 관리자 페이지 접근 또는 계정 로그인이 가능한 경우

#### 경계 케이스 (Edge Case) 처리 방법
- 일반적인 경우 영향 없음
- IP 제한 시 VPN이 필요할 수 있음
- 2차 인증 시 관리자 편의성 고려 필요

#### 권장 설정값
- 관리자 페이지 URL: 유추 어렵게 (랜덤 문자열)
- IP 화이트리스트 적용
- 2차 인증 (OTP, VPN, 인증서) 도입

### 2. 점검 방법

#### Step 1: 유추 가능한 URL 접속 시도
```
유추하기 쉬운 URL, 포트 등 접속을 시도하여 관리자 페이지가 노출되는지 확인
```

**테스트할 URL:**
```
/admin, /administrator, /manager, /root
/admin.php, /admin.jsp, /admin.asp
/wp-admin, /typo3, /administrator
/backend, /controlpanel
```

#### Step 2: 추측 가능한 계정 로그인 시도
```
추측하기 쉬운 관리자 계정(admin, adm, administrator, manager 등) 및 비밀번호를 입력하여 로그인 가능한지 확인
```

### 3. 조치 방법

#### 1. 관리자 페이지 URL 변경

```java
// 쉽게 유추할 수 없는 URL 사용
// 변경 전: /admin
// 변경 후: /Xy9kL2mN8pQ4

@Controller
@RequestMapping("/Xy9kL2mN8pQ4")  // 랜덤한 경로
public class AdminController {
    // ...
}
```

#### 2. IP 기반 접근 제한

**Apache .htaccess:**
```apache
<Directory "/var/www/html/admin">
    Order Deny,Allow
    Deny from all
    Allow from 192.168.1.100  # 허용된 IP
    Allow from 203.0.113.0/24  # 허용된 대역
</Directory>
```

**Nginx:**
```nginx
location /admin/ {
    allow 192.168.1.100;
    allow 203.0.113.0/24;
    deny all;
}
```

**Java Spring Security:**
```java
@Configuration
public class SecurityConfig {
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/Xy9kL2mN8pQ4/**")
                    .hasIpAddress("192.168.1.100")
            );
        return http.build();
    }
}
```

#### 3. 2차 인증 도입

```java
// 관리자 로그인 시 OTP 인증
@PostMapping("/admin/login")
public String adminLogin(@RequestParam String username,
                         @RequestParam String password,
                         @RequestParam String otpCode,
                         HttpSession session) {
    // 1단계: 일반 로그인
    User user = userService.authenticate(username, password);

    if (!user.hasRole("ADMIN")) {
        return "redirect:/login?error=unauthorized";
    }

    // 2단계: OTP 인증
    if (!otpService.verify(user.getOtpSecret(), otpCode)) {
        return "redirect:/admin/login?error=invalid_otp";
    }

    session.setAttribute("admin", user);
    return "redirect:/admin/dashboard";
}
```

#### 4. 세션 검증 적용

```java
// 모든 관리자 페이지에서 세션 검증
@Controller
@RequestMapping("/Xy9kL2mN8pQ4")
public class AdminController {

    @BeforeAdvice
    public void checkAdminSession(HttpSession session) {
        User admin = (User) session.getAttribute("admin");

        if (admin == null || !admin.hasRole("ADMIN")) {
            throw new UnauthorizedException("관리자 권한이 필요합니다.");
        }
    }

    @GetMapping("/user/list")
    public String listUsers() {
        // 세션 검증 완료 후 실행
        return "admin/user/list";
    }
}
```

#### 5. 취약한 기본 계정 변경

```sql
-- 관리자 계정 비밀번호 강력한 것으로 변경
UPDATE users
SET password = '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj9SjKEq1.9i'  -- bcrypt 해시
WHERE username = 'admin';

-- 또는 관리자 계정명 변경
UPDATE users
SET username = 'superuser_' || SUBSTRING(MD5(RANDOM()::text), 1, 8)
WHERE role = 'admin';
```

### 4. 참고 자료

**자주 사용되는 취약한 관리자 계정:**
- admin/admin
- admin/password
- admin/123456
- administrator/admin
- root/root
- manager/manager

**관리자 페이지 URL 패턴:**
- /admin, /administrator, /manager
- /admin.php, /admin.jsp, /admin.asp
- /wp-admin (WordPress)
- /typo3 (TYPO3 CMS)
- /backend, /controlpanel

**체크리스트:**
1. [ ] 관리자 페이지 URL 변경 (유추 어렵게)
2. [ ] IP 기반 접근 제어
3. [ ] 2차 인증 (OTP, VPN, 인증서) 도입
4. [ ] 취약한 기본 계정 변경/삭제
5. [ ] 모든 하위 페이지 세션 검증
6. [ ] 로그인 실패 횟수 제한
7. [ ] 관리자 활동 로그 기록

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.