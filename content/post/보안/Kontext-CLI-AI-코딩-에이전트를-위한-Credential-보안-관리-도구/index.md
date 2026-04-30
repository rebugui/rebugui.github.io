---
title: "Kontext CLI: AI 코딩 에이전트를 위한 Credential 보안 관리 도구"
date: 2026-05-01T01:06:49+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 서론

평범한 화요일 오후, 한 스타트업의 시니어 개발자가 Claude Code에게 데이터베이스 스키마를 마이그레이션해달라고 요청했습니다. 30분 뒤, 그 에이전트는 실수로 프로덕션 데이터베이스를 날렸습니다. 더 끔찍한 건 이 사실을 그 누구도 몰랐다는 것입니다.

문제의 핵심은 권한 남용이 아닙니다. 바로 **가시성 부족**입니다. 대부분의 팀이 AI 코딩 에이전트에게 GitHub Personal Access Token, Stripe API Key, 데이터베이스 연결 문자열을 `.env` 파일이나 채팅창에 하드코딩해서 전달합니다. 이 순간, 감사(audit) 기능은 사라집니다. 어떤 개발자가 어떤 에이전트를 실행했는지, 그 에이전트가 정확히 무엇에 접근했는지, 그 접근이 적법했는지 추적할 방법이 없습니다.

Kontext CLI는 이 근본적인 문제를 해결합니다. 단순한 시크릿 매니저가 아니라, AI 에이전트를 위한 **Credential Broker**입니다. OIDC 인증, RFC 8693 토큰 교환, 세션 기반 단기 토큰 발급을 통해 자율 에이전트 환경에서의 권한 통제와 컴플라이언스를 실현합니다.

## 본론

### 문제 본질: Secret Sprawl과 감사 공백

전통적인 credential 관리는 human-in-the-loop를 전제로 설계되었습니다. 개발자가 터미널에서 직접 API를 호출하면, 그 행위는 개발자의 의도와 연결됩니다. 하지만 AI 에이전트는 다릅니다.

**전통적 접근 vs AI 에이전트 접근의 차이:**

| 비교 항목 | 전통적 개발자 워크플로우 | AI 코딩 에이전트 워크플로우 | | :--- | :--- | :--- | | 인증 주체 | 개발자 본인 | 에이전트 (개발자 대리) | | 호출 빈도 | 분당 1~5회 | 분당 수백 회 | | 권한 범위 | 필요 최소 권한 | 과도한 권한 (편의상) | | 감사 추적 | 쉘 히스토리, 로그 | 추적 불가 (채팅 로그에 묻힘) | | Credential 수명 | 장기 (90일~1년) | 동일 (장기 토큰 재사용) | | 회전(Rotation) 영향 | 제한적 | 전체 에이전트 세션 중단 |

핵심 문제는 **장기 수명 API 키가 자율 프로세스에 직접 전달된다는 점**입니다. 이 키가 유출되면, 공격자는 원래 개발자와 동일한 권한을 얻습니다. 더 심각한 건, 내부 위협 시나리오에서 악의적 에이전트가 권한을 남용해도 이를 감지할 수단이 없다는 것입니다.

### Kontext CLI 아키텍처: Credential Broker 모델

Kontext는 AWS STS(Security Token Service)의 개념을 AI 에이전트 환경에 맞게 재해석했습니다.

```javascript
graph TD
    A[Developer] -->|kontext start --agent claude| B[Kontext CLI]
    B -->|OIDC Authentication| C[Identity Provider]
    C -->|ID Token| B
    B -->|Token Exchange Request| D[Kontext Backend]
    D -->|RFC 8693 Token Exchange| E[Service Provider]
    E -->|Short-lived Access Token| D
    D -->|Session Token| B
    B -->|Scoped Credentials in Memory| F[AI Agent Runtime]
    F -->|Tool Calls with Session Token| G[External Services]
    F -->|Audit Stream| H[Audit Log]
```

이 흐름의 핵심은 **토큰 교환 패턴**입니다. 에이전트는 원본 API 키를 절대 보지 않습니다. 대신 세션에 한정된 단기 토큰을 받습니다.

### 작동 원리 심층 분석

#### 1. 선언적 Credential 매핑

프로젝트 루트에 `.env.kontext` 파일을 생성합니다:

```bash
# .env.kontext - 프로젝트별 credential 요구사항 선언
GITHUB_TOKEN={{kontext:github}}
STRIPE_KEY={{kontext:stripe}}
LINEAR_TOKEN={{kontext:linear}}
DATABASE_URL={{kontext:postgres-prod}}
```

이 파일은 credential 자체가 아닙니다. **요구사항 선언**입니다. "이 프로젝트는 GitHub, Stripe, Linear, PostgreSQL에 접근해야 한다"는 메타데이터일 뿐, 실제 시크릿은 포함하지 않습니다.

#### 2. 세션 시작 및 OIDC 인증

에이전트를 실행할 때 Kontext를 통해 시작합니다:

```bash
# Claude Code를 Kontext로 시작
kontext start --agent claude

# 출력 예시:
# ✓ Authenticated via OIDC (user: seungbin@company.com)
# ✓ Session ID: sess_abc123def456
# ✓ Exchanging tokens for 4 services...
# ✓ GITHUB_TOKEN: short-lived token (TTL: 1h)
# ✓ STRIPE_KEY: short-lived token (TTL: 1h)
# ✓ LINEAR_TOKEN: short-lived token (TTL: 1h)
# ✓ DATABASE_URL: injected credential (memory-only)
# ✓ Audit logging enabled
# → Claude Code launched with scoped credentials
```

#### 3. RFC 8693 Token Exchange 메커니즘

OAuth를 지원하는 서비스(GitHub, Stripe 등)의 경우, Kontext는 **RFC 8693 OAuth 2.0 Token Exchange**를 사용합니다:

```go
// Simplified token exchange flow (conceptual)
package main

import (
    "context"
    "fmt"
    "time"
)

// TokenExchangeRequest represents RFC 8693 request
type TokenExchangeRequest struct {
    GrantType          string // "urn:ietf:params:oauth:grant-type:token-exchange"
    SubjectToken       string // OIDC ID token from identity provider
    SubjectTokenType   string // "urn:ietf:params:oauth:token-type:id_token"
    ActorToken         string // Optional: delegating user's token
    ActorTokenType     string
    Resource           string // Target service identifier
    Audience           string // "https://github.com" or "https://api.stripe.com"
    Scope              string // Requested permissions
}

// SessionCredential holds the short-lived token
type SessionCredential struct {
    AccessToken string
    ExpiresAt   time.Time
    SessionID   string
    Scope       []string
    Service     string
}

func ExchangeToken(ctx context.Context, req TokenExchangeRequest) (*SessionCredential, error) {
    // 1. Validate subject token (OIDC ID token)
    claims, err := validateOIDCToken(req.SubjectToken)
    if err != nil {
        return nil, fmt.Errorf("invalid subject token: %w", err)
    }

    // 2. Check user's permission for requested resource
    if !hasPermission(claims.UserID, req.Resource, req.Scope) {
        return nil, fmt.Errorf("access denied: user %s lacks permission for %s",
            claims.UserID, req.Resource)
    }

    // 3. Mint short-lived access token scoped to session
    sessionToken := &SessionCredential{
        AccessToken: generateShortLivedToken(1 * time.Hour),
        ExpiresAt:   time.Now().Add(1 * time.Hour),
        SessionID:   generateSessionID(),
        Scope:       req.Scope,
        Service:     req.Resource,
    }

    // 4. Never persist to disk - memory only
    // Token is injected directly into agent's runtime environment

    return sessionToken, nil
}
```

**핵심 보안 속성:**

| 속성 | 설명 | 보안 이점 | | :--- | :--- | :--- | | 단기 수명 | 토큰 TTL: 1시간 | 유출 시 노출 창 최소화 | | 범위 제한 | 세션별 최소 권한 | lateral movement 방지 | | 메모리 전용 | 디스크 기록 금지 | at-rest 유출 차단 | | 세션 바인딩 | 특정 세션에 종속 | 토큰 재사용 공격 방지 |

#### 4. 감사 로깅 및 접근 추적

모든 도구 호출은 실시간으로 스트리밍됩니다:

```json
{
  "timestamp": "2025-01-15T14:32:07.891Z",
  "session_id": "sess_abc123def456",
  "user": "seungbin@company.com",
  "agent": "claude-code",
  "tool_call": {
    "service": "github",
    "operation": "create_pull_request",
    "repository": "company/backend-api",
    "parameters": {
      "title": "Fix: Update database schema migration",
      "branch": "feature/db-migration"
    }
  },
  "decision": "allowed",
  "policy": "default-allow",
  "token_scope": ["repo:write", "pr:write"]
}
```

### Step-by-Step: Kontext CLI 설정 가이드

**1단계: 설치**

```bash
# macOS (Homebrew)
brew install kontext-dev/tap/kontext

# 또는 Go install
go install github.com/kontext-dev/kontext-cli@latest

# 버전 확인
kontext version
# kontext version 0.1.0 (build: abc123)
```

**2단계: 초기 인증**

```bash
# OIDC 제공자로 인증
kontext auth login

# 브라우저가 열리며 SSO 로그인 진행
# 성공 시:
# ✓ Authenticated as seungbin@company.com
# ✓ Credentials stored in system keyring
```

**3단계: 프로젝트 credential 선언**

```bash
# 프로젝트 루트에서
cat > .env.kontext << 'EOF'
GITHUB_TOKEN={{kontext:github}}
STRIPE_KEY={{kontext:stripe}}
EOF

# .env.kontext를 .gitignore에 추가
echo ".env.kontext" >> .gitignore
```

**4단계: 에이전트 실행**

```bash
# Claude Code를 Kontext로 실행
kontext start --agent claude

# 에이전트는 환경 변수로 단기 토큰을 받음
# echo $GITHUB_TOKEN → gho_shortlivedtoken...
```

**5단계: 세션 감사 로그 확인**

```bash
# 현재 세션의 접근 기록 조회
kontext audit list --session current

# 출력:
# TIME                 SERVICE   OPERATION          DECISION
# 2025-01-15 14:32:07  github    create_pull_request  allowed
# 2025-01-15 14:32:15  github    push_commits         allowed
# 2025-01-15 14:33:01  stripe    list_customers       allowed
# 2025-01-15 14:33:45  github    delete_branch        denied (policy)
```

### 공격 시나리오와 Kontext의 방어
> **⚠️ 윤리적 경고**: 다음 공격 시나리오는 교육 및 방어 목적으로만 제공됩니다. 실제 시스템에 대한 무단 접근은 불법입니다.

**시나리오 1: 에이전트 프로세스 메모리 덤프**

공격자가 에이전트 프로세스의 메모리를 덤프하려고 시도합니다:

```bash
# 공격자 시도 (실패)
gcore <agent_pid>
strings core.<pid> | grep -E 'ghp_|sk_live_'

# 결과: 단기 토큰만 발견됨 (1시간 내 만료)
# 원본 API 키는 메모리에 존재하지 않음
```

Kontext 없었다면, 장기 수명 API 키(`ghp_...`, `sk_live_...`)가 메모리에 노출되었을 것입니다.

**시나리오 2: .env 파일 유출**

```bash
# 공격자 시도
cat /project/.env
# 결과: 파일 없음 (Kontext는 메모리 주입만 사용)

cat /project/.env.kontext
# 결과: placeholder만 존재
# GITHUB_TOKEN={{kontext:github}}
# → 실제 토큰 값 없음
```

**시나리오 3: 권한 상승 시도**

에이전트가 허용되지 않은 리소스에 접근하려는 경우:

```json
{
  "tool_call": {
    "service": "github",
    "operation": "delete_repository",
    "repository": "company/production-config"
  },
  "decision": "denied",
  "policy": "repo-deletion-restricted",
  "reason": "Repository deletion requires explicit approval"
}
```

서버 측 정책 강제(roadmap)가 구현되면, 이러한 시도는 자동으로 차단됩니다.

### 성능 고려사항

Kontext CLI는 Go로 작성되어 도구 호출당 약 5ms의 오버헤드를 가집니다. ConnectRPC를 사용하여 백엔드와 통신하며, 인증 정보는 시스템 키링(keyring)에 안전하게 저장합니다.

**성능 벤치마크 (참고):**

| 메트릭 | 측정값 | 비고 | | :--- | :--- | :--- | | 훅 오버헤드 | ~5ms/call | 도구 호출당 추가 시간 | | 세션 시작 시간 | ~2초 | 토큰 교환 포함 | | 메모리 사용량 | ~15MB | CLI 프로세스 기준 | | 토큰 크기 | ~1KB | 세션 토큰 당 |

### 한계점 및 개선 방향

현재 Kontext CLI에는 몇 가지 한계가 있습니다:

1. **지원 에이전트 제한**: 현재 Claude Code만 지원. Codex 지원은 예정 2. **서버 측 정책 미완성**: 도구 호출 거부 인프라는 구축되었으나, 루프가 완전히 닫히지 않음 3. **백엔드 의존성**: 자체 호스팅 옵션 명확성 부족 4. **OAuth 미지원 서비스**: 정적 API 키의 경우, 단기 토큰 발급 불가

개선 제안:

```bash
# 정적 API 키에 대한 추가 보호 (제안)
# HashiCorp Vault와 통합하여 동적 시크릿 생성
kontext config set vault-address https://vault.company.com
kontext config set vault-path secret/ai-agents

# 세션 격리 강화 (제안)
# 네트워크 정책과 연동하여 토큰별 허용 IP 제한
kontext start --agent claude --network-policy restricted
```

## 결론

### 핵심 요약

Kontext CLI는 AI 코딩 에이전트 시대의 credential 관리 문제에 대한 실용적 해결책입니다:

1. **장기 API 키 제거**: 에이전트는 단기 세션 토큰만 수신 2. **메모리 전용 저장**: 디스크에 시크릿 기록 금지 3. **포괄적 감사**: 모든 도구 호출의 사용자, 세션, 조직 귀속 추적

---

**출처**: [https://github.com/kontext-dev/kontext-cli](https://github.com/kontext-dev/kontext-cli)