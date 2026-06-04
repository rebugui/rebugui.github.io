---
title: "OAuth 2.0 Token Exchange (RFC 8693): 보안 토큰 변환 메커니즘 이해"
date: 2026-06-04T21:49:29+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 서론

당신은 마이크로서비스 기반의 전자상거래 플랫폼을 개발 중입니다. 사용자가 로그인하면 인증 서버가 액세스 토큰을 발급합니다. 그런데 문제는 이 토큰이 "어디까지" 유효한가입니다. 프론트엔드에서 API 게이트웨이를 호출할 때는 잘 작동하지만, 게이트웨이가 내부 마이크로서비스(예: 주문 서비스, 결제 서비스)를 호출할 때는 "권한이 없습니다"라는 오류가 발생합니다. 혹은, 외부 파트너사 시스템과 연동할 때 "이 토큰은 우리 시스템용이 아닙니다"라는 메시지를 받습니다.

이런 상황에서 개발자들은 보통 두 가지 선택을 합니다. 첫째, 모든 서비스가 동일한 토큰을 이해하도록 만드는 것(비현실적). 둘째, 토큰을 직접 복사하거나 재발급하는 임시방편(보안 취약). 이 문제의 근본 원인은 하나의 토큰이 모든 컨텍스트와 대상을 만족시킬 수 없기 때문입니다.

OAuth 2.0 Token Exchange(RFC 8693)는 이 문제를 해결하기 위해 탄생했습니다. 이 표준은 "하나의 보안 토큰을 다른 토큰으로 변환하는 메커니즘"을 정의합니다. 즉, 인가 서버를 Security Token Service(STS)로 전환하여, 클라이언트가 보낸 토큰을 검증하고 새로운 컨텍스트나 대상(audience)에 맞는 토큰을 발급하는 것입니다. 이 글에서는 이 메커니즘의 원리, 실제 구현 방법, 그리고 실무에서의 적용 사례를 깊이 있게 다루겠습니다.

## 본론: OAuth 2.0 Token Exchange의 심층 분석

### 1. Token Exchange의 기본 원리

OAuth 2.0 Token Exchange는 기본적으로 "토큰을 토큰으로 교환"하는 프로토콜입니다. 클라이언트는 기존에 발급받은 토큰(예: 액세스 토큰, 리프레시 토큰, ID 토큰)을 인가 서버에 제출하고, 새로운 토큰을 받습니다. 이 새로운 토큰은 다른 대상(audience), 다른 범위(scope), 다른 권한(actor)을 가질 수 있습니다.

가장 중요한 개념은 **토큰 위임(Token Delegation)**입니다. 클라이언트는 자신의 권한을 다른 서비스에 위임할 수 있습니다. 예를 들어, 사용자가 로그인한 후 프론트엔드가 백엔드 API를 호출할 때, 프론트엔드는 자신의 액세스 토큰을 백엔드에 전달할 수 없습니다(보안상 위험). 대신, Token Exchange를 통해 백엔드 전용 토큰을 발급받아 사용합니다.

**핵심 용어 정리**:
- **Subject Token**: 현재 클라이언트가 보유한 토큰. 교환의 입력값.
- **Actor Token**: 위임을 수행하는 주체를 나타내는 토큰. 예를 들어, 사용자 토큰을 위임받은 서비스.
- **Requested Token**: 교환 결과로 발급받고자 하는 새로운 토큰.
- **Audience**: 새 토큰이 유효한 대상 서비스.
- **Scope**: 새 토큰이 허용하는 권한 범위.

### 2. Mermaid 다이어그램: Token Exchange 흐름도

다음은 Token Exchange의 기본 흐름을 나타낸 다이어그램입니다.

```javascript
sequenceDiagram
    participant Client
    participant STS as Security Token Service
    participant ServiceA as Service A (Audience)
    participant ServiceB as Service B (Target)

    Client->>STS: POST /token (grant_type=urn:ietf:params:oauth:grant-type:token-exchange)
    Note over Client,STS: subject_token=access_token, audience=ServiceB
    STS->>STS: Validate subject_token
    STS-->>Client: New access_token for ServiceB
    Client->>ServiceB: GET /api/resource (Authorization: Bearer new_token)
    ServiceB-->>Client: 200 OK
```

**흐름 설명**:

1. **클라이언트의 요청**: 클라이언트는 기존 액세스 토큰(`subject_token`)을 STS에 제출하고, `audience`를 `ServiceB`로 지정합니다.
2. **STS의 검증**: STS는 `subject_token`의 유효성을 검증합니다(서명, 만료 시간, 발급자 등).
3. **새 토큰 발급**: 검증이 완료되면 STS는 `ServiceB`를 대상으로 하는 새로운 액세스 토큰을 발급합니다. 이 새 토큰은 원래 토큰의 권한을 위임받습니다.
4. **리소스 접근**: 클라이언트는 새 토큰을 사용하여 `ServiceB`의 API를 호출합니다.

### 3. 코드 예시: 실제 Token Exchange 요청

다음은 Python을 사용하여 Token Exchange를 구현한 예시입니다. 이 코드는 실제 STS에 HTTP 요청을 보내는 개념 증명(PoC)입니다.

```python
import requests
import json
import base64
from datetime import datetime, timedelta

# STS 엔드포인트 (예: Keycloak, Okta, Auth0)
sts_url = "https://auth.example.com/oauth/token"

# 클라이언트 자격 증명 (기밀 클라이언트)
client_id = "my-client"
client_secret = "my-secret"

# 기존 액세스 토큰 (subject_token)
subject_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."

def exchange_token(subject_token, target_audience, target_scope):
    """
    OAuth 2.0 Token Exchange 요청을 보내는 함수
    """
    # 요청 바디 구성
    payload = {
        "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
        "subject_token": subject_token,
        "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
        "audience": target_audience,
        "scope": target_scope,
        "requested_token_type": "urn:ietf:params:oauth:token-type:access_token"
    }
    
    # 클라이언트 인증 (Basic Auth)
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {auth_header}"
    }
    
    try:
        response = requests.post(sts_url, data=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Token Exchange 실패: {e}")
        return None

# 사용 예시
new_token = exchange_token(
    subject_token=subject_token,
    target_audience="https://api.payment-service.com",
    target_scope="payment:read payment:write"
)

if new_token:
    print(f"새로운 액세스 토큰: {new_token.get('access_token')[:50]}...")
    print(f"토큰 타입: {new_token.get('token_type')}")
    print(f"만료 시간: {new_token.get('expires_in')}초")
else:
    print("토큰 교환 실패")
```

**코드 설명**:
- `grant_type`: Token Exchange를 나타내는 URN 값입니다.
- `subject_token`: 교환할 기존 토큰입니다.
- `subject_token_type`: 기존 토큰의 타입을 지정합니다. 액세스 토큰, 리프레시 토큰, ID 토큰 등이 가능합니다.
- `audience`: 새 토큰이 유효한 대상 서비스의 식별자입니다.
- `scope`: 새 토큰에 부여할 권한 범위입니다.
- `requested_token_type`: 요청하는 새 토큰의 타입입니다.

### 4. 표: Token Exchange 파라미터 비교

다음 표는 Token Exchange 요청의 주요 파라미터와 일반 OAuth 2.0 Authorization Code Grant의 파라미터를 비교합니다.

| 파라미터 | Token Exchange (RFC 8693) | Authorization Code Grant (RFC 6749) |
| :--- | :--- | :--- |
| `grant_type` | `urn:ietf:params:oauth:grant-type:token-exchange` | `authorization_code` |
| 주요 입력 | `subject_token` (기존 토큰) | `code` (인가 코드) |
| 대상 지정 | `audience` (명시적) | `redirect_uri` (암시적) |
| 권한 위임 | `actor_token` (위임 주체) | 없음 |
| 토큰 타입 지정 | `subject_token_type`, `requested_token_type` | 없음 |
| 주요 사용 사례 | 서비스 간 위임, 토큰 변환 | 사용자 로그인, 최초 인증 |
| 보안 모델 | 토큰 위임 (Delegation) | 직접 인증 (Direct Auth) |
| 토큰 수명 | 새 토큰은 일반적으로 짧음 (5~15분) | 상대적으로 김 (1시간 이상) |

**표 분석**:
- Token Exchange는 **토큰 위임**에 특화되어 있습니다. 클라이언트가 직접 인증을 받는 대신, 기존 토큰을 기반으로 새로운 토큰을 발급받습니다.
- `audience` 파라미터는 Token Exchange의 핵심입니다. 이를 통해 새 토큰이 특정 서비스에만 유효하도록 제한할 수 있습니다.
- Authorization Code Grant는 사용자 인증에 초점을 맞춘 반면, Token Exchange는 **서비스 간 인증 흐름**을 유연하게 제어합니다.

### 5. Step-by-Step 가이드: 실무 적용

Token Exchange를 실제 환경에 적용하는 방법을 단계별로 설명합니다.

**Step 1: STS(인가 서버) 설정**

Token Exchange를 지원하는 STS를 선택합니다. 대표적인 옵션:
- **Keycloak**: 오픈소스, Token Exchange를 기본 지원
- **Okta**: 상용, Token Exchange 기능 제공
- **Auth0**: 상용, Actions를 통해 Token Exchange 구현 가능
- **Azure AD**: Microsoft Entra ID, Token Exchange 지원

설정 예시 (Keycloak):
1. Keycloak 관리 콘솔에 로그인합니다.
2. Realm을 선택하고 "Clients" > "my-client"를 선택합니다.
3. "Settings" 탭에서 "Client authentication"을 "On"으로 설정합니다.
4. "Service Accounts Roles" 탭에서 Token Exchange에 필요한 역할을 할당합니다.
5. "Token Exchange" 탭에서 "Permit client to exchange tokens"를 활성화합니다.

**Step 2: 클라이언트 설정**

클라이언트 애플리케이션에서 Token Exchange를 호출하도록 코드를 작성합니다. 위의 Python 코드 예시를 참고하세요.

**Step 3: 대상 서비스 설정**

새 토큰을 수신할 서비스(예: `ServiceB`)에서 토큰 검증 로직을 구현합니다. 다음은 FastAPI 기반의 검증 예시입니다.

```python
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt import PyJWKClient

app = FastAPI()
security = HTTPBearer()

# STS의 JWKS 엔드포인트
jwks_url = "https://auth.example.com/oauth/jwks"
jwks_client = PyJWKClient(jwks_url)

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    try:
        # JWKS를 사용하여 토큰 서명 검증
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience="https://api.payment-service.com",  # 대상 서비스 확인
            issuer="https://auth.example.com"  # 발급자 확인
        )
        return payload
    except jwt.PyJWTError as e:
        raise HTTPException(status_code=401, detail=f"토큰 검증 실패: {e}")

@app.get("/api/payment")
async def get_payment(payload: dict = Depends(verify_token)):
    return {"message": "Payment data", "user": payload.get("sub")}
```

---

**출처**: [https://news.hada.io/topic?id=30164](https://news.hada.io/topic?id=30164)