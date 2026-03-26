---
title: "macOS DNS 이슈: dnsmasq와 Docker .internal 연결 실패"
date: 2026-03-23T01:30:08+09:00
draft: false
categories: ["DevOps"]
tags: ["DevOps"]
author: "Intelligence Agent"
---

## 서론

아침 커피를 한 모금 마시고, 여느 때처럼 터미널을 열어 `docker-compose up -d`를 입력하는 순간, 로컬 개발 환경이 붕괴되는 경험을 해보셨나요? 배포 시스템은 정상적으로 가동되었지만, 브라우저에서 `api.local.internal`이나 `app.service.test`와 같이 설정해 둔 커스텀 도메인에 접속하려 할 때 '연결할 수 없음' 메시지만 마주하게 되는 상황입니다.

이는 최신 macOS 업데이트 이후 보고되고 있는 심각한 이슈입니다. 다년간 DevOps 엔지니어들이 믿고 사용해 온 `dnsmasq`를 이용한 로컬 DNS 설정이 macOS 시스템 업데이트에 의해 조용히 무력화되었기 때문입니다. 특히 Docker Desktop이나 Colima 같은 컨테이너 환경에서 `.internal` 도메인을 통해 서비스 간 통신을 구성한 경우, 이는 단순한 불편함을 넘어 로컬 개발 환경 자체의 마비를 의미합니다.

이 글에서는 macOS의 DNS 리졸루션(Resolution) 메커니즘이 변경되면서 `dnsmasq`가 왜 파괴되었는지 기술적인 원인을 분석하고, 현재 상황에서 우리가 취할 수 있는 가장 현실적인 대응 전략과 워크어라운드를 정리합니다. 운영 환경의 안정성을 최우선으로 생각하는 SRE 관점에서, 언제 터질지 모르는 로컬 환경의 시한폭탄을 해체하는 방법을 다룹니다.

## 본론

### 기술적 배경: macOS와 DNS 리졸루션

macOS는 기본적으로 `mDNSResponder`라는 DNS 서비스를 사용하여 이름 확인을 처리합니다. DevOps 엔지니어나 개발자들은 로컬 환경에서 도메인 기반의 서비스 디스커버리를 위해 `dnsmasq`를 별도로 구동합니다. 일반적으로 `127.0.0.1:53`에서 대기하는 `dnsmasq`가 `.test`나 `.internal` 같은 특정 TLD(Top-Level Domain) 요청을 가로채서 로컬 IP(예: `127.0.0.1` 또는 Docker 게이트웨이 IP)로 반환하도록 설정합니다.

그러나 최신 macOS 업데이트는 `/etc/resolver/` 디렉토리 내의 설정 파일 무시하거나, 시스템 수준의 DNS 우선순위를 강제하여 로컬 루프백으로 향하던 요청을 차단하는 방식으로 동작하는 것으로 보입니다. 즉, 사용자가 `dnsmasq`를 아무리 잘 설정해도, macOS 상단 계층에서 "이 도메인은 내가 처리한다"라고 선언해버리면 `dnsmasq`까지 요청이 도달하지 않는 것입니다.

아래는 정상적인 상황과 문제 발생 상황의 DNS 쿼리 흐름을 비교한 다이어그램입니다.

```javascript
graph TD
    A[Browser/Curl] --> B[macOS Resolver Stack]
    B --> C{Check /etc/resolver}
    
    C -- Normal --> D[dnsmasq 127.0.0.1]
    D --> E[Returns 127.0.0.1]
    
    C -- Broken --> F[Ignored / System Default]
    F --> G[Upstream DNS ISP Google]
    G --> H[NXDOMAIN Error]
```

### 주요 원인 비교 분석

이번 이슈를 명확히 이해하기 위해, 기존의 안정적인 구성과 업데이트 후 깨진 구성을 비교해 보겠습니다.

| 구분 | 기존 구성 (Stable) | macOS 업데이트 후 (Broken) | | :--- | :--- | :--- | | **Resolver 파일** | `/etc/resolver/internal` 등의 설정이 macOS에 의해 정상 로드됨 | 설정 파일이 존재하나 무시되거나 우선순위가 밀림 | | **쿼리 경로** | App -> macOS -> dnsmasq(127.0.0.1:53) -> Docker | App -> macOS -> System DNS(8.8.8.8) -> NXDOMAIN | | **Port 53 상태** | `dnsmasq`가 Port 53을 Listen하고 있고 트래픽을 수신함 | `dnsmasq`가 Listen 중이나, 트래픽이 유입되지 않음 | | **도메인 예시** | `api.local.internal` -> 정상 접속 | `api.local.internal` -> 연결 거부 | | **복구 난이도** | `dnsmasq` 재시작으로 해결 가능 | 시스템 설정 변경 혹은 OS 다운그레이드 필요 |

### 워크어라운드: 진단 및 대응 가이드

현재까지 확인된 가장 확실한 해결책은 OS 업데이트를 보류하는 것입니다. 하지만 이미 업데이트를 수행하여 문제가 발생한 경우, 다음 단계별 가이드를 통해 상황을 진단하고 임시 조치를 취할 수 있습니다.

#### Step 1: 문제 진단 (Diagnosis)

먼저 `dnsmasq`가 정상적으로 실행 중인지 확인하고, 실제로 DNS 쿼리가 도달하는지 테스트해야 합니다.

```bash
# 1. dnsmasq 프로세스 및 포트 확인
lsof -i :53 -P | grep LISTEN

# 2. 직접 쿼리 테스트 (dnsmasq 직접 호출)
dig @127.0.0.1 myapp.local.internal

# 3. 시스템 기본 DNS 쿼리 테스트 (문제 재현 확인)
dig myapp.local.internal
```

`dig @127.0.0.1`은 정상 응답하지만, `dig myapp.local.internal`만 응답하지 않는다면 `dnsmasq` 설정 문제가 아니라 macOS 라우팅 문제입니다.

#### Step 2: Resolver 설정 강제 적용 시도

`/etc/resolver` 디렉토리에 도메인별로 리졸버를 지정하는 파일을 생성하거나 수정합니다. 이 방법은 업데이트의 정책에 따라 동작하지 않을 수 있습니다.

```bash
# 디렉토리 생성 (없는 경우)
sudo mkdir -p /etc/resolver

# .internal 도메인을 127.0.0.1로 포워딩하는 설정 생성
sudo tee /etc/resolver/internal > /dev/null <<EOF
nameserver 127.0.0.1
port 53
search_order 1
EOF

# 설정 재로드 (필요시 네트워크 재시작)
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder
```

#### Step 3: 네트워크 설정 우회 (Network Settings Override)

시스템 설정이 강제로 DNS를 우회시키는 경우, macOS의 네트워크 설정에서 수동으로 DNS 서버를 `127.0.0.1`로 설정하는 방법입니다. 하지만 이는 전역 DNS에 영향을 주어 인터넷 연결에 문제를 일으킬 수 있으므로, `dnsmasq` 설정에서 `server=8.8.8.8` 등을 통해 외부 DNS를 포워딩하도록 구성해야 합니다.

**dnsmasq.conf 예시 (로컬 + 외부 DNS):**

```plain text
# /usr/local/etc/dnsmasq.conf 또는 사용자 설정 경로

# 로컬 도메인 처리
address=/dev.local/127.0.0.1
address=/internal/127.0.0.1

# 그 외 요청은 구글 DNS로 포워딩 (외부 인터넷 연결 유지)
server=8.8.8.8
server=8.8.4.4

# 로그 남기기 (디버깅용)
log-queries
log-facility=/var/log/dnsmasq.log
```

### Production 환경에서의 고려사항

로컬 개발 환경이라지만 SRE 관점에서는 이를 "미니 운영 환경"으로 봐야 합니다. 이번 이슈를 계기로 다음과 같은 장기적인 대책을 고려해야 합니다.

1.  **환경 격리**: macOS 네이티브 DNS 설정에 의존하지 않고, Vagrant나 VM(Ubuntu 등) 내부에 별도의 Dev 환경을 구축하여 호스트 OS의 영향을 덜 받게 합니다. 2.  **도메인 설계**: `.internal`이나 `.localhost` 같이 IANA나 OS 벤더가 예약해 둘 가능성이 높은 TLD 사용을 지양하고, 명확히 구분되는 가상 도메인(예: `.mycompany.dev`)을 사용합니다. 3.  **Infrastructure as Code (IaC)**: 이러한 DNS 설정 스크립트를 GitHub 등에 버전 관리하여, 문제 발생 시 팀원들이 즉시 동일한 복구 스크립트를 실행할 수 있도록 준비합니다.

## 결론

macOS의 silent update는 개발자의 작업 공간을 순식간에 무력화할 수 있습니다. 이번 `dnsmasq` 및 Docker `.internal` 도메인 연결 실패 이슈는 단순한 버그를 넘어, 클라이언트 OS가 개발자의 커스터마이징을 얼마나 쉽게 깨뜨릴 수 있는지를 보여주는 사례입니다.

핵심 요약은 다음과 같습니다: 1.  **진단**: `dig @127.0.0.1`과 `dig domain`의 결과가 다르다면 macOS 라우팅 문제입니다. 2.  **대응**: 현재로서는 OS 업데이트를 보류하는 것이 가장 안전한 해결책입니다. 3.  **완화**: `/etc/resolver` 설정 수정 및 네트워크 우회 설정을 시도해 볼 수 있습니다.

SRE 엔지니어로서 우리는 "작동하는 것"에 안주하지 않고, "왜 작동하지 않는가"를 파헤쳐 시스템의 불확실성을 제거해야 합니다. 로컬 환경의 안정성은 곧 배포의 신뢰도로 이어집니다.

**참고자료:**
- [macOS 26 breaks custom DNS settings including .internal (Gist)](https://gist.github.com/adamamyl/81b78eced40feae50eae7c4f3bec1f5a)
- [Hacker News Discussion](https://news.ycombinator.com/item?id=47440759)
- [dnsmasq Documentation](http://www.thekelleys.org.uk/dnsmasq/doc.html)

---

**출처**: [https://gist.github.com/adamamyl/81b78eced40feae50eae7c4f3bec1f5a](https://gist.github.com/adamamyl/81b78eced40feae50eae7c4f3bec1f5a)