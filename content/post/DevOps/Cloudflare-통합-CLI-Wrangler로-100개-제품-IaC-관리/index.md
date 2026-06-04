---
title: "Cloudflare 통합 CLI: Wrangler로 100개 제품 IaC 관리"
date: 2026-05-01T01:06:47+09:00
draft: false
categories: ["DevOps"]
tags: ["DevOps"]
author: "Intelligence Agent"
---

## 서론

새벽 3시, PagerDuty 알림이 울린다. 프로덕션 환경의 Cloudflare 설정이 누락되어 장애가 발생했다. 원인을 추적해보니, 누군가 대시보드에서 수동으로 WAF 규칙을 수정하면서 기존 설정을 덮어쓴 것이다. 이런 경험, 한 번쯤 있지 않나요?

Cloudflare는 단순한 CDN을 넘어 DDoS 방어, WAF, DNS, Workers, Pages, R2, D1, KV 등 100개가 넘는 제품을 제공하는 거대한 에코시스템이 되었습니다. 문제는 이 많은 서비스를 각각의 대시보드와 API로 관리해야 한다는 것입니다. 팀이 성장할수록 설정의 불일치, 드리프트(Drift), 재현 불가능한 인프라 상태가 골칫거리가 됩니다.

Cloudflare가 발표한 통합 CLI 프로젝트는 바로 이 문제를 해결합니다. 기존 Workers 배포 도구인 Wrangler를 확장하여, 모든 Cloudflare 제품과 약 3,000개의 API 작업을 단일 CLI와 코드 기반(IaC)으로 관리할 수 있게 됩니다. 이 글에서는 이것이 왜 게임체인저인지, 그리고 실무에 어떻게 적용할 수 있는지 살펴보겠습니다.

## Cloudflare IaC 관리의 현재와 한계

### 기존 도구들의 파편화 문제

현재 Cloudflare 리소스를 코드로 관리하려면 여러 도구를 조합해야 합니다.

| 관리 도구 | 관리 대상 | IaC 지원 | 한계점 |
| :--- | :--- | :--- | :--- |
| Wrangler | Workers, Pages, R2, KV | 부분적 | 제한된 리소스만 관리 |
| Terraform Provider | DNS, WAF, LB 등 전반 | 전체 | HCL 학습 필요, 느린 실행 |
| API 직접 호출 | 모든 리소스 | 커스텀 | 스크립트 유지보수 부담 |
| Dashboard | 모든 리소스 | 없음 | 수동 조작, 감사 추적 어려움 |

각 도구는 자신만의 설정 파일 포맷, 인증 방식, 워크플로우를 요구합니다. DNS는 Terraform으로, Workers는 Wrangler로, 보안 정책은 API 스크립트로 관리하는 식이면, 인프라 전체 상태를 파악하기 어렵습니다.

### Wrangler의 진화: Workers CLI에서 통합 IaC 도구로

```javascript
graph LR
    A[Wrangler v1] --> B[Workers 전용 배포]
    C[Wrangler v2] --> D[Workers + Pages + KV]
    E[Wrangler v3] --> F[R2, D1, Queues 추가]
    G[Unified CLI] --> H[100개 제품 통합 관리]
    
    B --> D
    D --> F
    F --> H
    
    H --> I[DNS]
    H --> J[WAF]
    H --> K[Load Balancer]
    H --> L[Access]
    H --> M[모든 Cloudflare 서비스]
```

## 통합 CLI의 아키텍처와 작동 원리

### API-first 설계 철학

Cloudflare의 모든 제품은 이미 REST API로 노출되어 있습니다. 통합 CLI는 이 기존 API 생태계를 활용하며, 각 제품의 OpenAPI 스펙을 자동으로 참조합니다.

```plain text
API 엔드포인트 구조:
https://api.cloudflare.com/client/v4/zones/{zone_id}/{product}/{resource}
https://api.cloudflare.com/client/v4/accounts/{account_id}/{product}/{resource}
```

약 3,000개의 API 작업이 존재한다는 것은, CLI가 이 모든 엔드포인트에 대한 CRUD(Create, Read, Update, Delete) 작업을 지원한다는 의미입니다. 이를 Declarative(선언적) 방식으로 관리할 수 있게 됩니다.

### 선언적 설정 파일 구조

Wrangler가 확장되면, 단일 설정 파일로 여러 Cloudflare 서비스를 정의할 수 있습니다. 예상되는 설정 구조를 살펴보겠습니다.

```yaml
# wrangler.toml - 통합 설정 파일 (예상 구조)
name = "my-project"
main = "src/worker.js"
compatibility_date = "2024-01-01"

# Workers 설정
[workers]
route = "api.example.com/*"
env.production = { name = "my-project-prod" }

# DNS 레코드 관리
[[dns.records]]
type = "A"
name = "api.example.com"
content = "203.0.113.1"
ttl = 3600
proxied = true

[[dns.records]]
type = "CNAME"
name = "www.example.com"
content = "example.com"
proxied = true

# WAF 규칙
[[waf.rules]]
action = "block"
expression = "(ip.geoip.country eq "XX" and http.request.uri.path contains "/admin")"
description = "Block admin access from specific countries"

[[waf.rules]]
action = "challenge"
expression = "(http.request.method eq "POST" and cf.bot_management.score < 30)"
description = "Challenge suspected bot POST requests"

# R2 스토리지
[[r2.buckets]]
name = "my-assets"
location_hint = "APAC"

# KV 네임스페이스
[[kv.namespaces]]
binding = "CACHE"
id = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# D1 데이터베이스
[[d1.databases]]
binding = "DB"
database_name = "production-db"
database_id = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
```

### Imperative vs Declarative 워크플로우

통합 CLI는 두 가지 모드를 모두 지원할 것으로 예상됩니다.

```bash
# Imperative (명령형) - 즉시 실행
wrangler dns create --zone example.com --type A --name api --content 203.0.113.1
wrangler waf rule create --action block --expression "(ip.geoip.country eq "XX")"
wrangler r2 bucket create my-assets

# Declarative (선언형) - 상태 동기화
wrangler apply  # wrangler.toml 기반으로 모든 리소스 동기화
wrangler plan   # 변경 사항 미리 보기 (Terraform plan과 유사)
wrangler diff   # 현재 상태와 원하는 상태 비교
```

## 실무 적용: Step-by-step 가이드

### Step 1: Wrangler 최신 버전 설치 및 인증

```bash
# Wrangler 최신 버전 설치
npm install -g wrangler@latest

# 버전 확인 (v3 이상 필요)
wrangler --version

# Cloudflare 계정 인증
wrangler login

# OAuth 브라우저 인증 후 계정 정보 확인
wrangler whoami
```

인증이 완료되면 `~/.wrangler/config/default.toml`에 OAuth 토큰이 저장됩니다. CI/CD 환경에서는 API 토큰을 사용합니다.

### Step 2: API 토큰 기반 CI/CD 인증 설정

```yaml
# GitHub Actions 워크플로우
name: Deploy Cloudflare Infrastructure

on:
  push:
    branches: [main]
    paths:
      - 'cloudflare/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          
      - name: Install Wrangler
        run: npm install -g wrangler@latest
        
      - name: Validate Configuration
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
        run: |
          wrangler deploy --dry-run
          
      - name: Deploy Infrastructure
        if: github.ref == 'refs/heads/main'
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
        run: |
          wrangler deploy
```

### Step 3: 환경별 설정 분리

```plain text
# wrangler.toml - 환경별 구성
name = "my-project"
main = "src/worker.js"

# 공통 DNS 설정
[[dns.records]]
type = "A"
name = "example.com"
content = "203.0.113.1"
proxied = true

# 개발 환경
[env.dev]
name = "my-project-dev"
[env.dev.d1_databases]
binding = "DB"
database_name = "dev-db"
preview_database_id = "dev-preview-db-id"

[[env.dev.dns.records]]
type = "CNAME"
name = "dev.example.com"
content = "dev-worker.example.workers.dev"
proxied = false

# 스테이징 환경
[env.staging]
name = "my-project-staging"
[env.staging.d1_databases]
binding = "DB"
database_name = "staging-db"

[[env.staging.waf.rules]]
action = "log"
expression = "(http.request.uri.path contains "/api/")"
description = "Log all API requests in staging"

# 프로덕션 환경
[env.production]
name = "my-project-production"
routes = ["api.example.com/*"]

[env.production.d1_databases]
binding = "DB"
database_name = "production-db"

[[env.production.waf.rules]]
action = "block"
expression = "(cf.threat_score > 10)"
description = "Block high threat score requests"

[[env.production.waf.rules]]
action = "managed_challenge"
expression = "(http.request.method eq "POST" and not cf.bot_management.verified_bot)"
description = "Challenge non-verified bot POST requests"
```

```bash
# 환경별 배포
wrangler deploy --env dev
wrangler deploy --env staging
wrangler deploy --env production

# 특정 리소스 상태 확인
wrangler d1 list --env production
wrangler r2 bucket list
wrangler kv namespace list
```

### Step 4: 상태 관리 및 Drift 감지

```bash
# 현재 인프라 상태를 코드와 비교
wrangler diff --env production

# 출력 예시:
# ~ dns.record "api.example.com" 
#   content: "203.0.113.1" => "203.0.113.2" (changed externally)
#   
# ~ waf.rule "block-suspicious-bots"
#   action: "block" => "challenge" (manual dashboard change detected)

# 상태를 코드에 맞게 강제 동기화
wrangler apply --env production --auto-approve

# 현재 상태를 코드로 내보내기 (기존 인프라 마이그레이션)
wrangler import --env production --output ./imported-config.toml
```

### Step 5: GitOps 워크플로우 구성

```yaml
# .github/workflows/cloudflare-gitops.yml
name: Cloudflare GitOps Sync

on:
  schedule:
    - cron: '0 */6 * * *'  # 6시간마다 드리프트 체크
  workflow_dispatch:

jobs:
  drift-detection:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Check for Configuration Drift
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
        run: |
          wrangler diff --env production > drift-report.txt 2>&1
          
          if grep -q "changed externally\|manual dashboard change" drift-report.txt; then
            echo "::warning::Configuration drift detected!"
            cat drift-report.txt
            
            # Slack 알림
            curl -X POST ${{ secrets.SLACK_WEBHOOK }} \
              -H 'Content-type: application/json' \
              -d "{"text":"⚠️ Cloudflare config drift detected in production. Check drift-report.txt"}"
            exit 1
          fi
          
          echo "No drift detected. Infrastructure is in sync."
```

## Terraform과 Wrangler: 언제 무엇을 쓸까?

통합 Wrangler CLI가 등장하면서 Terraform Cloudflare Provider와의 선택이 고민될 수 있습니다. 두 도구의 포지션을 비교해봅시다.

| 비교 항목 | Terraform + Cloudflare Provider | Wrangler 통합 CLI |
| :--- | :--- | :--- |
| **학습 곡선** | 중간 (HCL 문법) | 낮음 (JavaScript/TypeScript 친화적) |
| **실행 속도** | 느림 (Provider 다운로드, 상태 잠금) | 빠름 (경량 CLI) |
| **상태 관리** | 외부 State 파일 (S3, Terraform Cloud) | 로컬 또는 Cloudflare 관리 |
| **에코시스템 연동** | AWS, GCP 등 멀티클라우드 | Cloudflare 전용 |
| **CI/CD 통합** | GitHub Actions, GitLab CI 지원 | 네이티브 Wrangler Actions |
| **적합 시나리오** | 멀티클라우드, 기존 Terraform 코드베이스 | Cloudflare 중심, Edge-first 아키텍처 |

**추천 전략**: Cloudflare를 주 인프라로 사용하는 스타트업이나 Edge-first 프로젝트는 Wrangler를, 멀티클라우드 환경에서 Cloudflare를 일부 사용하는 기업은 Terraform을 유지하는 것이 합리적입니다. 두 도구는 경쟁보다 보완 관계입니다.

## 모니터링 및 관측성

Wrangler로 관리되는 인프라의 상태를 Prometheus와 Grafana로 모니터링할 수 있습니다.

```yaml
# prometheus.yml - Cloudflare API 메트릭 수집
scrape_configs:
  - job_name: 'cloudflare_exporter'
    static_configs:
      - targets: ['cloudflare-exporter:9199']
    metrics_path: '/metrics'
    params:
      zones: ['your-zone-id']
```

```bash
# Wrangler 상태 점검 스크립트 (cron
```

---

**출처**: [https://news.hada.io/topic?id=28522](https://news.hada.io/topic?id=28522)