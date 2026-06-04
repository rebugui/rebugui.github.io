---
title: "인증/인가 로직 취약점 분석 심층 가이드: 권한 우회 및 BOLA 패턴 분석 방법론"
date: 2026-06-04T21:49:24+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 인증/인가 로직 취약점 분석 심층 가이드: 권한 우회 및 BOLA 패턴 분석 방법론

웹 애플리케이션의 보안을 논할 때, 단순히 SQL Injection이나 XSS 같은 코드 레벨의 취약점을 다루는 경우가 많습니다. 하지만 실제 운영 환경에서 가장 치명적이고 발견하기 어려운 공격은 바로 ‘논리(Logic)’를 건드리는 권한 우회 및 접근 제어 실패입니다. 이 글은 개발자가 간과하기 쉬운 인증(Authentication)과 인가(Authorization) 로직 취약점을 깊이 있게 분석하고, 실무에서 체계적으로 테스트하는 방법론을 제시합니다.

---

## 1. 왜 AuthZ/AuthN 논리적 결함이 치명적인가? (Impact Analysis)

인증(Authentication)은 "당신이 누구인지"를 확인하는 과정이며, 인가(Authorization)는 "당신이 무엇을 할 수 있는지"를 정의합니다. 이 두 가지 흐름 중 어느 한쪽에 작은 논리적 허점이 생기면, 공격자는 시스템의 경계 방어막 자체를 무너뜨릴 수 있습니다.

단순한 취약점은 특정 페이지 접근 불가로 끝나지만, 인가 로직 결함은 다음과 같은 치명적인 결과를 초래합니다:

1. **수평적 이동 (Lateral Movement):** 사용자 A의 자원에 대한 권한을 획득하여 사용자 B의 데이터를 열람하는 경우 (IDOR).
2. **수직적 상승 (Vertical Escalation):** 일반 사용자로 로그인했음에도 불구하고 관리자(Admin) 페이지에 접근하거나, 관리자 기능(예: `delete_user` API 호출)을 실행할 수 있는 경우 (Privilege Escalation).
3. **비즈니스 로직 우회:** 결제 과정에서 할인 코드를 여러 번 적용하거나, 재고 검사 없이 주문을 생성하는 등 애플리케이션의 핵심 비즈니스를 무력화시키는 경우.

따라서 우리는 단순히 '버그가 있는지'를 찾는 것이 아니라, '시스템이 정의한 권한 경계(Trust Boundary)'가 어디에 위치하며, 그 경계를 어떻게 우회할 수 있는지 사고해야 합니다.

## 2. 핵심 원리 이해: IDOR와 BOLA의 메커니즘 분석

최근 API 기반 웹 서비스에서 가장 빈번하게 발생하는 두 가지 논리적 취약점이 바로 **IDOR**과 **BOLA**입니다. 이들은 밀접하게 관련되어 있지만, 공격하는 지점과 깊이가 다릅니다.

### 2.1 IDOR (Insecure Direct Object Reference)

가장 기본적인 접근 제어 오류입니다. API나 웹 페이지에서 객체(Object)를 식별할 때, 고유한 참조 값(예: 사용자 ID, 주문 번호)을 직접 노출하고 이를 검증하지 않는 경우 발생합니다.

**공격 시나리오:** `GET /api/orders/{order_id}` 라는 API가 있다고 가정합시다. 정상적인 흐름은 현재 로그인한 사용자의 ID와 요청된 `order_id`의 소유자가 일치하는지 확인해야 합니다. 하지만 서버 측에서 이 검증이 누락되었다면, 공격자는 자신이 알게 된 임의의 `order_id=12345`를 대입하여 다른 사람의 주문 정보를 탈취할 수 있습니다.

### 2.2 BOLA (Broken Object Level Authorization)

BOLA는 IDOR보다 더 심층적이고 API 지향적인 취약점입니다. 이는 **"객체에 대한 접근 권한(Object-Level Access)"** 검증이 누락된 경우를 의미합니다.

API 요청은 일반적으로 `[Resource Type] / [ID]` 형태입니다. BOLA는 단순히 객체의 ID만 틀린 것이 아니라, 해당 객체를 수정하거나 삭제할 수 있는 **권한 수준 자체**가 잘못 처리되었을 때 발생합니다. 예를 들어, '자신의 프로필 정보'를 업데이트하는 API에 관리자가 접근하여 다른 사용자 정보를 덮어쓸 수 있게 설계된 경우입니다.

#### 공격 흐름도 (Mermaid)

```javascript
sequenceDiagram
    participant Attacker as 공격자
    participant Client as 클라이언트
    participant Server as 웹 서버/API 백엔드
    note over Attacker,Server: [1] 정상 요청 시나리오
    Attacker->>Client: GET /api/users/{user_id} (내 ID)
    Client->>Server: {Auth Token} + {User ID=A}
    Server->>Server: 1. AuthN 검증 (토큰 유효성)
    Server->>Server: 2. AuthZ 검증 (Owner == A?)
    Server-->>Client: [Success] 사용자 데이터 반환

    note over Attacker,Server: [2] BOLA 공격 시나리오
    Attacker->>Client: GET /api/users/{user_id} (타인 ID)
    Client->>Server: {Auth Token} + {User ID=A}
    Server->>Server: 1. AuthN 검증 (토큰 유효성)
    Server->>Server: 2. AuthZ 검증 (Owner == A?) <--- 이 단계가 누락됨
    Server-->>Client: [Success] 타인 사용자 데이터 반환 (취약점 발생)
```

## 3. 실전 분석 방법론 및 PoC (Proof of Concept)

논리적 취약점을 테스트할 때는 '문법적으로 올바른(Syntactically Correct)' 요청을 보내는 것이 아니라, **'권한이 없는 주체로 시스템의 신뢰 경계를 넘어서는(Logically Invalid)'** 요청을 보내야 합니다.

### 3.1 체계적인 분석 단계 (Test Checklist)

1. **경로 매개변수 변경 테스트:** 모든 URL 경로 변수(`{id}`, `{user_uuid}`)를 순차적으로 증가시키거나, 무작위 값(예: `0`, `-1`, `AAAA`)으로 대체하며 API 응답을 관찰합니다.
2. **Payload 조작 테스트 (HTTP Header/Body):** 요청 헤더에 `X-Forwarded-For` 같은 IP 관련 정보를 추가하거나, JSON Body 내부에 예상치 못한 필드(예: `"is_admin": true`)를 주입하여 서버가 이를 무시하는지 확인합니다.
3. **권한 범위 제한 테스트:** 현재 사용자가 접근 가능한 최소 권한의 API와 최대 권한의 API(관리자 기능) 목록을 모두 수집한 후, 낮은 권한 토큰으로 높은 권한 API를 호출해 봅니다.

### 3.2 PoC 예시: IDOR을 이용한 정보 탈취

다음은 특정 주문 번호를 조작하여 다른 사람의 정보를 가져오려는 시나리오입니다. (※ 이 코드는 **방어 목적**의 학습 자료이며, 실제 공격에 사용해서는 안 됩니다.)

```bash
# 1. 정상적인 요청 (내 주문 조회)
curl -H "Authorization: Bearer [My_Auth_Token]" \
     "https://api.example.com/v1/orders/my_order_id_12345"

# 2. IDOR 공격 시도 (다른 사람의 주문 조작)
# order_id를 임의로 변경하여 요청합니다.
curl -H "Authorization: Bearer [My_Auth_Token]" \
     "https://api.example.com/v1/orders/attacker_order_id_99999" 
```

만약 서버가 `my_order_id_12345`에 대한 요청은 처리하고, `attacker_order_id_99999`에 대해서도 데이터베이스 조회 후 JSON을 반환한다면, 심각한 IDOR 취약점이 존재합니다. 응답 본문에 "권한이 없습니다(Forbidden)"와 같은 명확한 오류 메시지를 반환해야 정상입니다.

## 4. 방어 아키텍처 설계: 논리적 결함을 막는 방법론

취약점은 코드로만 해결되지 않습니다. 시스템의 구조 자체가 권한 경계를 강제하도록 재설계되어야 합니다.

### 4.1 Policy Enforcement Point (PEP) 도입

가장 중요한 원칙입니다. 모든 API 엔드포인트 진입점마다 **'권한 검증 게이트(Gate)'**를 두어야 합니다. 이 Gate는 요청이 들어올 때마다 다음 세 가지 질문에 답해야 합니다.

1. **Authentication:** 토큰이 유효하고 만료되지 않았는가?
2. **Scope Check (인가):** 현재 사용자의 권한 범위(`scope`)가 해당 API 호출을 허용하는가? (예: `read:profile`만 가능, `write:settings` 불가)
3. **Ownership Check (소유권):** 요청된 객체 ID가 현재 사용자에게 할당되어 있는가?

### 4.2 구현 가이드라인 및 코드 스니펫 (개념 설명용)

직접 개발하는 백엔드 로직에서 `GET /api/orders/{order_id}`를 처리하는 경우, 다음과 같은 구조적 방어 코드를 적용해야 합니다.

```python
# [Bad Practice - 취약한 방식]
def get_order(request, order_id):
    # DB에서 단순히 ID로 조회만 함 -> 권한 검증 부재!
    order = db.fetch_order_by_id(order_id) 
    return jsonify(order)

# [Good Practice - 방어적 방식]
def get_order(request, order_id):
    current_user_id = request.get_user_id() # 토큰에서 추출된 사용자 ID
    
    # Step 1: 객체 조회 시 소유자 ID를 필수로 포함하여 조회한다. (핵심)
    order = db.fetch_order_by_owner_and_id(current_user_id, order_id)
    
    if not order:
        # 오류 메시지를 일반적인 "찾을 수 없음"으로 처리하여 정보 노출 방지
        raise AccessDenied("요청하신 리소스를 찾을 수 없습니다.") 
    
    return jsonify(order)
```

### 4.3 권장되는 기술적 완화 조치 체크리스트

| 취약점 유형 | 문제 발생 원인 | 구체적인 대응 방법 (Mitigation) |
| :--- | :--- | :--- |
| **IDOR/BOLA** | 객체 식별자가 노출되고 소유권 검증이 없음. | 1. 사용자 ID를 URL에 직접 사용하지 말고, UUID나 암호화된 토큰으로 대체한다. <br>2. 모든 데이터 접근 API는 반드시 요청 주체의 ID와 리소스의 소유자 ID를 비교하는 로직을 포함해야 한다. |
| **세션 관리** | 세션 토큰이 탈취되거나 재사용됨. | 1. 짧은 만료 시간을 설정하고, 비활성 상태 시 자동 로그아웃(Idle Timeout) 기능을 구현한다. <br>2. 민감한 작업 수행 직후에는 강제 로그아웃 또는 비밀번호 재확인 절차를 거친다. |
| **권한 상승** | 특정 기능이 '관리자만 사용 가능'으로 제한되지 않음. | 1. 모든 API 호출에 대해 역할 기반 접근 제어(RBAC) 정책을 적용한다 (예: `ROLE_ADMIN`만이 이 엔드포인트에 접근 가능). <br>2. 클라이언트 측에서 권한을 숨기는 것이 아니라, 서버에서 아예 해당 기능을 수행할 수 없게 막아야 한다. |

## 5. 결론: 보안은 코드가 아닌 '사고방식'의 영역이다

인증/인가 로직 취약점 분석은 단순히 특정 CVE를 찾아내는 해킹 기술이 아닙니다. 이는 애플리케이션을 설계하고 개발하는 과정에서 **"만일 이 경계가 무너진다면 어떤 일이 벌어질까?"**라는 질문을 끊임없이 던지는, 보안 엔지니어의 근본적인 사고방식(Mindset)의 문제입니다.

개발자는 모든 API 호출이 마치 외부 공격자로부터 오는 것처럼 취급되어야 합니다. 객체 ID를 받으면 "누가 요청했는가?"와 "요청한 사람이 이 객체의 주인인가?" 두 가지 질문에 대한 답을 반드시 얻도록 아키텍처 레벨에서 강제하는 것이, 가장 견고하고 실용적인 방어책입니다.