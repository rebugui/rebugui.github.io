---
title: "[2026 주요정보통신기반시설] CI-11 불충분한권한검증(Insufficient Authorization)"
slug: "2026-주정통/CI-11"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "타사용자의 권한을 탈취하여 민감한 데이터 접근 및 수정 가능 여부 점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Web
---

# 불충분한권한검증(Insufficient Authorization)

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | CI-11 |
| **점검내용** | 타사용자의 권한을 탈취하여 민감한 데이터 접근 및 수정 가능 여부 점검 |
| **점검대상** | 웹 애플리케이션 소스코드 |
| **양호기준** | 중요페이지에 사용자검증 로직이 구현되어 있어, 타사용자의 권한탈취가 제한된 경우 |
| **취약기준** | 중요페이지에 사용자검증 로직이 미흡하여, 타사용자의 권한탈취가 가능한 경우 |
| **조치방법** | 접근제어가 필요한 모든 페이지에서 서버사이드 방식 사용자권한 검증 로직 구현 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 중요 페이지에 사용자 검증 로직이 구현되어 있어, 타 사용자의 권한 탈취가 제한된 경우
- **취약**: 중요 페이지에 사용자 검증 로직이 미흡하여, 타 사용자의 권한 탈취가 가능한 경우

#### 경계 케이스 (Edge Case) 처리 방법
- 일반적인 경우 영향 없음
- 모든 페이지에 일관된 권한 검증 필요
- 클라이언트에서 숨기는 방식(Javascript로 버튼 숨김 등)은 무의미

#### 권장 설정값
- 모든 요청에 대해 서버 사이드에서 권한 검증
- 세션/토큰에서 사용자 ID를 신뢰하고 DB에서 재확인
- 예측 불가능한 식별자 사용 (UUID vs 순차적 ID)

### 2. 점검 방법

#### Step 1: URL 구조 분석
```
타 사용자 접근이 제한된 페이지(비밀 게시글, 개인정보 변경 등)에서 사용되는 URL 구조와 파라미터를 분석하여 사용자 간 구분을 ID, 숫자, 일련번호 등 단순한 값의 사용 여부 확인
```

#### Step 2: 파라미터 변조 테스트
```
식별된 URL 구조와 파라미터를 변조하여 타 사용자의 비공개 정보나 권한 외 리소스에 대한 접근 가능 여부 확인
```

### 3. 조치 방법

#### 1. 서버 사이드 세션 검증

**Java Spring 예시:**
```java
@GetMapping("/inquiry/{id}")
public String viewInquiry(@PathVariable Long id,
                          Model model,
                          HttpSession session) {
    User currentUser = (User) session.getAttribute("currentUser");

    // 세션에서 현재 사용자 정보를 가져옴
    if (currentUser == null) {
        throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Not logged in");
    }

    Inquiry inquiry = inquiryService.findInquiryById(id);

    // 현재 사용자가 문의 작성자가 아니면 403 응답
    if (!inquiry.getUser().getUsername().equals(currentUser.getUsername())) {
        throw new ResponseStatusException(HttpStatus.FORBIDDEN, "Permission denied");
    }

    model.addAttribute("inquiry", inquiry);
    return "inquiry/view";
}
```

#### 2. 권한 매트릭스 구현

```java
// 권한 정의
public enum Permission {
    READ_OWN_PROFILE,
    EDIT_OWN_PROFILE,
    READ_ANY_PROFILE,
    EDIT_ANY_PROFILE,
    DELETE_POST,
    ADMIN_PANEL
}

// 사용자 권한 확인
@Service
public class PermissionService {
    public boolean hasPermission(User user, Permission permission, Resource resource) {
        // 관리자는 모든 권한 보유
        if (user.hasRole("ADMIN")) {
            return true;
        }

        // 리소스 소유자 확인
        if (resource.getOwner().equals(user)) {
            return user.hasPermission(Permission.READ_OWN_PROFILE);
        }

        // 기본 권한 확인
        return user.hasPermission(permission);
    }
}

// 컨트롤러에서 사용
@GetMapping("/profile/{id}")
public String viewProfile(@PathVariable Long id,
                          HttpSession session) {
    User currentUser = getCurrentUser(session);
    User targetUser = userService.findById(id);
    Resource resource = new Resource(targetUser);

    if (!permissionService.hasPermission(currentUser, Permission.READ_ANY_PROFILE, resource)) {
        throw new UnauthorizedException("권한이 없습니다.");
    }

    return "profile/view";
}
```

#### 3. Spring Security 활용

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/admin/**").hasRole("ADMIN")
                .requestMatchers("/profile/{id}").access((authentication, request) -> {
                    String ownerId = request.getVariable("id");
                    return new WebExpressionAuthorizationManager(
                        "#userId == authentication.principal.id or hasRole('ADMIN')"
                    ).check(authentication, request);
                })
                .anyRequest().authenticated()
            );
        return http.build();
    }
}
```

#### 4. ASP.NET 권한 검증

```csharp
[Authorize]
public class ProfileController : Controller {
    [HttpGet]
    public ActionResult View(int id) {
        var currentUser = Session["User"] as User;
        var targetUser = db.Users.Find(id);

        // 권한 검증: 본인이거나 관리자인 경우만 허용
        if (targetUser.Id != currentUser.Id && !currentUser.IsAdmin) {
            return new HttpStatusCodeResult(HttpStatusCode.Forbidden);
        }

        return View(targetUser);
    }
}
```

#### 5. 접근 제어 미들웨어

```javascript
// Node.js Express 미들웨어
function checkOwnership(req, res, next) {
    const currentUser = req.user;
    const resourceOwnerId = parseInt(req.params.id);

    // 관리자이거나 본인인 경우만 통과
    if (currentUser.role === 'admin' || currentUser.id === resourceOwnerId) {
        return next();
    }

    return res.status(403).json({ error: 'Forbidden' });
}

// 라우트에 적용
app.get('/profile/:id', authenticate, checkOwnership, (req, res) => {
    res.json(req.profile);
});
```

### 4. 참고 자료

**권한 상승 공격 유형:**

1. **수직 권한 상승 (Vertical)**
   - 일반 사용자 → 관리자
   - 게스트 → 인증 사용자
   - 낮은 권한 → 높은 권한

2. **수평 권한 상승 (Horizontal)**
   - 사용자 A → 사용자 B
   - 동일 권한 레벨 간 접근

**OWASP Top 10 A01: Broken Access Control:**
- URL 조작으로 인한 접근
- 세션 조작
- CSRF 토큰 없는 상태 변경
- CORS 설정 오류

**권장사항:**
- 모든 리소스 접근 시 권한 검증
- 예측 불가능한 식별자 사용
- 세션 무결성 보장
- 로그 및 모니터링

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.