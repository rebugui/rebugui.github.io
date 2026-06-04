---
title: "[2026 주요정보통신기반시설] CI-13 프로세스검증누락(Missing Process Validation)"
slug: "2026-주정통/CI-13"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "서비스제공에 필요한 사용자입력 및 실행단계의 흐름에 대한 검증의 적절성 여부 점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Web
---

# 프로세스검증누락(Missing Process Validation)

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | CI-13 |
| **점검내용** | 서비스제공에 필요한 사용자입력 및 실행단계의 흐름에 대한 검증의 적절성 여부 점검 |
| **점검대상** | 웹 애플리케이션 소스코드 |
| **양호기준** | 프로세스에 대한 검증이 존재하며, 악의적인 행위(URL 직접 접근, Javascript 로직 변조 등)를 통하여 논리오류가 발생하지 않는 경우 |
| **취약기준** | 프로세스에 대한 검증이 미흡하여, 논리 오류를 통한 의도된 기능이 왜곡되거나 보안 취약점이 발생하는 경우 |
| **조치방법** | 프로세스검증이 필요한 경우 각 프로세스에 대한 체크 로직 구현 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 프로세스에 대한 검증이 존재하며, 악의적인 행위(URL 직접 접근, Javascript 로직 변조 등)를 통하여 논리오류가 발생하지 않는 경우
- **취약**: 프로세스에 대한 검증이 미흡하여, 논리 오류를 통한 의도된 기능이 왜곡되거나 보안 취약점이 발생하는 경우

#### 경계 케이스 (Edge Case) 처리 방법
- 일반적인 경우 영향 없음
- 모든 프로세스에 일관된 검증 로직 적용 필요
- 클라이언트 데이터는 절대 신뢰하지 말 것

#### 권장 설정값
- 모든 단계를 거쳤는지 세션으로 확인
- 클라이언트에서 보낸 데이터는 서버에서 재검증
- URL 직접 접근 시 차단

### 2. 점검 방법

#### Step 1: 프로세스 흐름 파악
```
웹 사이트 내 기능들의 권한 종류 및 프로세스의 흐름을 파악하고 각 프로세스의 통제를 우회 및 악용 가능성 여부 점검 (권한 상승, 민감 정보 획득, 가격 변조 등)
```

#### Step 2: 우회 공격 시도
```
비 로그인 상태로 URL 직접 접근을 통해 내부 사용자 관리 페이지로 접근할 수 있는지 확인
```

### 3. 조치 방법

#### 1. 세션 기반 접근 통제

**Java Spring 인터셉터 예시:**
```java
@Component
public class AuthInterceptor implements HandlerInterceptor {
    @Override
    public boolean preHandle(HttpServletRequest request,
                            HttpServletResponse response,
                            Object handler) throws Exception {
        HttpSession session = request.getSession();

        // 로그인 확인
        if (session.getAttribute("user") == null) {
            response.sendRedirect("/login");
            return false;
        }

        // 프로세스 단계 확인
        String uri = request.getRequestURI();
        if (uri.startsWith("/order/complete")) {
            Boolean checkoutCompleted = (Boolean) session.getAttribute("checkoutCompleted");
            if (checkoutCompleted == null || !checkoutCompleted) {
                response.sendRedirect("/cart");
                return false;
            }
        }

        return true;
    }
}
```

#### 2. 플로우 제어 로직

**Java Spring 예시:**
```java
@Controller
@SessionAttributes("checkoutFlow")
public class CheckoutController {

    // 1단계: 장바구니 확인
    @GetMapping("/checkout")
    public String checkout(HttpSession session) {
        if (session.getAttribute("cart") == null) {
            return "redirect:/cart";
        }
        session.setAttribute("checkoutStep", 1);
        return "checkout/step1";
    }

    // 2단계: 배송 정보 입력
    @PostMapping("/checkout/shipping")
    public String setShipping(@ModelAttribute ShippingInfo shipping,
                              HttpSession session) {
        Integer currentStep = (Integer) session.getAttribute("checkoutStep");
        if (currentStep == null || currentStep != 1) {
            return "redirect:/checkout";
        }

        session.setAttribute("shipping", shipping);
        session.setAttribute("checkoutStep", 2);
        return "checkout/step2";
    }

    // 3단계: 결제
    @PostMapping("/checkout/payment")
    public String processPayment(@ModelAttribute Payment payment,
                                 HttpSession session) {
        Integer currentStep = (Integer) session.getAttribute("checkoutStep");
        if (currentStep == null || currentStep != 2) {
            return "redirect:/checkout";
        }

        // 결제 처리
        boolean paymentResult = paymentService.process(payment);

        if (paymentResult) {
            session.setAttribute("checkoutStep", 3);
            session.setAttribute("checkoutCompleted", true);
            return "redirect:/order/complete";
        } else {
            return "checkout/payment-failed";
        }
    }
}
```

#### 3. ASP.NET Page_Load 검증

```csharp
protected void Page_Load(object sender, EventArgs e) {
    // 로그인 확인
    if (Session["UserName"] == null) {
        Response.Redirect("~/Login.aspx");
        return;
    }

    // 프로세스 단계 확인
    if (Session["CheckoutStep"] == null ||
        (int)Session["CheckoutStep"] < 2) {
        Response.Redirect("~/Checkout.aspx");
        return;
    }
}
```

#### 4. 가격 검증 로직

```java
@PostMapping("/order/place")
public String placeOrder(@RequestBody OrderRequest request,
                         HttpSession session) {
    // 세션에서 장바구니 정보 조회
    Cart cart = (Cart) session.getAttribute("cart");

    // 서버에서 상품 가격 재확인
    Order order = new Order();
    for (CartItem item : cart.getItems()) {
        Product product = productService.findById(item.getProductId());

        // 클라이언트가 보낸 가격이 아닌, DB의 가격 사용
        order.addItem(product, product.getPrice(), item.getQuantity());
    }

    // 총액 검증
    if (request.getTotalAmount() != order.getTotalAmount()) {
        throw new InvalidAmountException("가격이 조작되었습니다.");
    }

    orderService.place(order);
    return "order/complete";
}
```

#### 5. PHP 세션 변수 플로우 제어

```php
session_start();

// 1단계 완료 시
if ($step1_completed) {
    $_SESSION['step1_completed'] = true;
    header('Location: step2.php');
    exit;
}

// 2단계 직접 접근 시
if (!isset($_SESSION['step1_completed']) ||
    $_SESSION['step1_completed'] !== true) {
    header('Location: step1.php');
    exit;
}
```

### 4. 참고 자료

**비즈니스 로직 취약점 유형:**

1. **프로세스 우회**
   - 단계 건너뛰기
   - 순서 변경

2. **파라미터 변조**
   - 가격 조작
   - 수량 변경
   - 한도 초과

3. **클라이언트 신뢰**
   - JavaScript 검증만 의존
   - 히든 필드 신뢰

4. **경로 예측**
   - 순차적 URL
   - 관리자 페이지 유추

**검증이 필요한 프로세스:**
1. 인증 절차 (로그인, 본인인증)
2. 결제 프로세스 (장바구니 → 결제 → 완료)
3. 파일 업로드 (검증 → 업로드 → 처리)
4. 게시글 작성 (작성 → 미리보기 → 등록)
5. 멀티폼 (폼 작성 → 확인 → 제출)

**검증 원칙:**
1. 모든 단계를 거쳤는지 세션으로 확인
2. 클라이언트에서 보낸 데이터는 서버에서 재검증
3. URL 직접 접근 시 차단
4. 이전 단계 완료 여부 확인

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.