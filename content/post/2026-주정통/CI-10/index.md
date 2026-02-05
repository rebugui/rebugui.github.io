---
title: "[2026 주요정보통신기반시설] CI-10 불충분한인증절차(Insufficient Authentication)"
slug: "2026-주정통/CI-10"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "중요페이지 접근시 추가 인증절차 존재 여부 및 인증로직 우회 여부 점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Web
---

# 불충분한인증절차(Insufficient Authentication)

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | CI-10 |
| **점검내용** | 중요페이지 접근시 추가 인증절차 존재 여부 및 인증로직 우회 여부 점검 |
| **점검대상** | 웹 애플리케이션 소스코드 |
| **양호기준** | 중요 정보 페이지 접근 시 추가 인증 절차가 존재하며, 인증 로직이 서버 사이드에서 구현되어 우회가 불가능한 경우 |
| **취약기준** | 중요 정보 페이지 접근 시 추가 인증 절차가 없거나, 인증 로직이 클라이언트 사이드에서 구현되어 우회 가능한 경우 |
| **조치방법** | 중요페이지에 대한 추가 인증절차를 도입하고, 서버사이드에서 인증여부를 검증하는 로직 구현 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 중요 정보 페이지 접근 시 추가 인증 절차가 존재하며, 인증 로직이 서버 사이드에서 구현되어 우회가 불가능한 경우
- **취약**: 중요 정보 페이지 접근 시 추가 인증 절차가 없거나, 인증 로직이 클라이언트 사이드에서 구현되어 우회 가능한 경우

#### 경계 케이스 (Edge Case) 처리 방법
- 일반적인 경우 영향 없음
- 모든 중요 페이지에 일관된 인증 절차 적용 필요
- 클라이언트 사이드 인증만으로는 충분하지 않음

#### 권장 설정값
- 개인정보 수정: 현재 비밀번호 재입력 또는 SMS 인증
- 비밀번호 변경: 현재 비밀번호 입력 필수
- 계좌 이체: OTP 인증
- 관리자 권한 변경: 재인증 요구

### 2. 점검 방법

#### Step 1: 재인증 절차 확인
```
중요 정보(개인정보 변경 등) 페이지 접근 시 재인증 절차 존재 여부 확인
```

#### Step 2: 인증 로직 우회 시도
```
로직 변조, 파라미터 변조 등의 행위를 통하여 인증 로직(OTP 인증, 휴대폰 본인인증 등)의 우회 여부 확인
```

### 3. 조치 방법

#### 1. 재인증 로직 구현

**Java Spring 예시:**
```java
// 재인증이 필요한 페이지 접근 전 검증
@GetMapping("/edit/profile")
public String editProfile(HttpSession session, Model model) {
    User user = (User) session.getAttribute("user");
    Boolean isVerified = (Boolean) session.getAttribute("isVerified");

    // 세션을 통해 인증 유무 검증
    if (user == null || isVerified == null || !isVerified) {
        return "redirect:/user/authenticate";
    }

    model.addAttribute("user", user);
    return "edit_profile";
}

// 재인증 처리
@PostMapping("/verify/code")
public String verifyCode(@RequestParam String code, HttpSession session) {
    if (isValidCode(code)) {
        session.setAttribute("isVerified", true);
        return "redirect:/user/edit/profile";
    } else {
        return "redirect:/user/authenticate?error=true";
    }
}
```

#### 2. 접근 통제 공통 모듈 구현

```java
// 인터셉터로 적용
public class AuthInterceptor implements HandlerInterceptor {
    @Override
    public boolean preHandle(HttpServletRequest request,
                            HttpServletResponse response,
                            Object handler) throws Exception {
        HttpSession session = request.getSession();
        String uri = request.getRequestURI();

        // 중요 페이지 접근 시 재인증 확인
        if (uri.startsWith("/user/edit/")) {
            if (!AccessControl.isVerified(session)) {
                response.sendRedirect("/user/authenticate");
                return false;
            }
        }

        return true;
    }
}
```

#### 3. 서버 사이드 인증 구현

```java
// 서버 사이드에서 인증 처리
@PostMapping("/login")
public String login(@RequestParam String username,
                    @RequestParam String password,
                    HttpSession session) {
    User user = userService.findByUsername(username);

    if (user != null && user.getPassword().equals(password)) {
        session.setAttribute("user", user);
        session.setAttribute("isVerified", false);  // 인증 세션 초기값 설정
        return "redirect:/user/dashboard";
    } else {
        return "login?error=true";
    }
}
```

#### 4. 권한 기반 접근 제어

```java
// 권한 어노테이션
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface RequirePermission {
    String value();
}

// AOP로 권한 검증
@Aspect
@Component
public class PermissionAspect {
    @Around("@annotation(requirePermission)")
    public Object checkPermission(ProceedingJoinPoint joinPoint,
                                  RequirePermission requirePermission) throws Throwable {
        HttpSession session = getCurrentSession();
        User user = (User) session.getAttribute("user");

        if (user == null || !user.hasPermission(requirePermission.value())) {
            throw new UnauthorizedException("권한이 없습니다.");
        }

        return joinPoint.proceed();
    }
}
```

### 4. 참고 자료

**재인증이 필요한 페이지 예시:**
- 개인정보 수정
- 비밀번호 변경
- 이메일/연락처 변경
- 계좌 이체
- 주소 변경
- 보안 설정 변경

**인증 방법:**
- 현재 비밀번호 재입력
- SMS 인증번호
- OTP (One-Time Password)
- 인증서 기반 인증
- 생체 인증

**OWASP Authentication Cheat Sheet:**
- 모든 인증은 서버 사이드에서 수행
- 중요 작업 전 재인증 요구
- 세션 만료 후 재인증
- 다중 인증(MFA) 도입 권장

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.