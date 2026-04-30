---
title: "Docker Pull 실패 트러블슈팅: 스페인 축구 중계권 Cloudflare IP 차단 사례"
date: 2026-05-01T01:06:58+09:00
draft: false
categories: ["DevOps"]
tags: ["DevOps"]
author: "Intelligence Agent"
---

## 서론

금요일 저녁, 프로덕션 배포 파이프라인이 갑자기 멈췄다. GitLab Runner가 Docker 이미지를 pull하지 못하고 TLS 인증서 오류를 뱉어내기 시작했다. 로컬에서 직접 `docker pull`을 실행해도 같은 에러. Tailscale 네트워크 문제인 줄 알고 VPN 설정을 만지고, DNS 설정을 바꿔보고, Docker 데몬을 재시작해봤지만 소용없었다.

에러 메시지는 명확했다:

```plain text
tls: failed to verify certificate: x509: certificate is not valid for any names
```

하지만 원인은 전혀 예상치 못한 곳에 있었다. 바로 스페인 프로축구 리그(La Liga) 경기 중계 시간이었다.

이 글에서는 스페인 법원 명령으로 인해 Docker Registry의 Cloudflare R2 스토리지 IP가 차단되면서 발생한 장애 사례를 분석하고, 유사한 네트워크 차단 이슈를 어떻게 진단하고 우회할 수 있는지 실무 관점에서 살펴본다.

## 본론

### 문제 발생 구조

GitLab CI/CD 파이프라인이 실패하는 과정을 다이어그램으로 확인해보자:

```javascript
graph TD
    A[Git Push] --> B[GitLab Runner 실행]
    B --> C[Docker Pull 시도]
    C --> D[DNS 해석: *.r2.cloudflarestorage.com]
    D --> E[ISP 라우팅]
    E --> F{법원 차단 IP 대역?}
    F -->|Yes| G[TLS 인증서 오류 반환]
    F -->|No| H[정상 이미지 다운로드]
    G --> I[파이프라인 실패]
```

스페인 인터넷 서비스 제공자(ISP)는 법원 명령에 따라 특정 IP 대역을 차단한다. 문제는 Docker Hub가 이미지 메타데이터를 저장하는 Cloudflare R2 스토리지의 IP가 이 차단 대상에 포함되었다는 점이다.

### 에러 메시지 분석

실제 발생한 에러 메시지를 단계별로 분해해보자:

```bash
# 1단계: GitLab Runner 로그 확인
$ gitlab-runner exec docker my-job
ERROR: Job failed: failed to pull image "alpine:latest"

# 2단계: 직접 docker pull 실행
$ docker pull alpine:latest
error pulling image configuration: download failed after attempts=6: 
tls: failed to verify certificate: x509: certificate is not valid for any names, 
but wanted to match docker-images-prod.6aa30f8b08e16409b46e0173d6de2f56.r2.cloudflarestorage.com
```

이 에러의 핵심 포인트:

| 항목 | 설명 | | :--- | :--- | | 에러 유형 | TLS 인증서 검증 실패 | | 대상 호스트 | `docker-images-prod.*.r2.cloudflarestorage.com` | | 재시도 횟수 | 6회 실패 후 포기 | | 근본 원인 | ISP 수준 IP 차단으로 인한 중간자 프록시 응답 |

일반적인 TLS 오류라면 인증서 만료나 DNS 하이재킹을 의심하겠지만, 이 경우 ISP가 법원 명령으로 IP를 차단하면서 반환하는 차단 페이지의 인증서와 충돌하는 것이다.

### 원인 상세: 스페인 법원 명령의 기술적 영향

2024년 12월 18일 바르셀로나 상업법원 판결에 따라, La Liga와 Telefónica Audiovisual Digital은 불법 스트리밍 차단을 위해 특정 IP 대역 차단을 요청했다.

차단 메시지 원문:

```plain text
El acceso a la presente dirección IP ha sido bloqueada en cumplimiento 
de lo dispuesto en la Sentencia de 18 de diciembre de 2024, dictada por 
el Juzgado de lo Mercantil nº 6 de Barcelona
```

번역하면: "바르셀로나 상업법원 제6부의 2024년 12월 18일 판결에 따라 해당 IP 접근이 차단되었습니다."

문제의 심각성:

| 조건 | 상황 | | :--- | :--- | | 발생 시간 | 축구 경기 시간에만 (간헐적) | | 차단 방식 | IP 대역 전체 차단 | | 영향 범위 | 해당 IP를 사용하는 모든 서비스 | | Docker 영향 | 이미지 메타데이터 다운로드 불가 |

### 트러블슈팅 스텝바이스텝

유사한 문제를 겪었을 때 진단하는 순서를 정리했다:

```bash
# Step 1: DNS 해석 확인
$ dig docker-images-prod.6aa30f8b08e16409b46e0173d6de2f56.r2.cloudflarestorage.com

# Step 2: 해당 IP로 직접 curl 테스트
$ curl -v https://docker-images-prod.6aa30f8b08e16409b46e0173d6de2f56.r2.cloudflarestorage.com

# Step 3: TLS 인증서 정보 확인
$ openssl s_client -connect docker-images-prod.6aa30f8b08e16409b46e0173d6de2f56.r2.cloudflarestorage.com:443

# Step 4: traceroute로 차단 지점 확인
$ traceroute docker-images-prod.6aa30f8b08e16409b46e0173d6de2f56.r2.cloudflarestorage.com
```

`curl` 명령으로 차단 메시지를 직접 확인할 수 있다:

```bash
$ curl -k https://<차단된-IP> 2>&1 | head -20
# 스페인어 법원 차단 안내 페이지가 반환됨
```

### 우회 및 해결 방안

프로덕션 환경에서 이런 문제에 대응하는几种 방법을 정리했다:

#### 방안 1: Mirror Registry 사용

```yaml
# /etc/docker/daemon.json
{
  "registry-mirrors": [
    "https://mirror.gcr.io",
    "https://registry.docker.jp.proxy.cekit.net"
  ]
}
```

```bash
# daemon.json 수정 후 Docker 재시작
$ sudo systemctl restart docker
```

#### 방안 2: GitLab Container Registry 프록시

```yaml
# gitlab-runner config.toml
[[runners]]
  [runners.docker]
    image = "alpine:latest"
    pull_policy = ["if-not-present"]
    allowed_images = ["registry.example.com/*"]
```

#### 방안 3: VPN 또는 프록시 경로 변경

```bash
# WireGuard VPN 설정 예시
$ wg-quick up vpn-tunnel

# 또는 HTTP 프록시 설정
$ export HTTP_PROXY=http://proxy.example.com:8080
$ export HTTPS_PROXY=http://proxy.example.com:8080
$ docker pull alpine:latest
```

### 해결 방안 비교

| 방안 | 장점 | 단점 | 적용 시나리오 | | :--- | :--- | :--- | :--- | | Mirror Registry | 투명한 우회, 설정 간편 | 미러 동기화 지연 가능 | 장기적 해결책 | | Container Registry 프록시 | 내부 캐싱, 빠른 pull | 스토리지 비용 발생 | 엔터프라이즈 환경 | | VPN/프록시 | 즉시 적용 가능 | 모든 트래픽 경로 변경 | 임시 대응 | | 이미지 캐싱 | 네트워크 의존성 감소 | 디스크 공간 필요 | CI/CD 안정성 향상 |

### 근본적 교훈: 인프라는 정치의 영향권 안에 있다

이 사건은 기술적 문제를 넘어선 중요한 시사점을 준다:

1. **법적 조치의 기술적 부작용**: 법원이 이해하지 못하는 인프라 의존성 2. **간헐적 장애의 위험성**: "경기 시간에만" 발생하면 원인 파악이 극도로 어려움 3. **글로벌 서비스의 로컬 법률 영향**: 클라우드 서비스가 특정 국가의 법적 제재를 받을 수 있음

## 결론

### 핵심 요약
- 스페인 법원의 축구 불법 중계 차단 명령이 Docker Registry에서 사용하는 Cloudflare R2 스토리지 IP를 차단
- 결과적으로 Docker pull 시 TLS 인증서 오류 발생, GitLab CI/CD 파이프라인 실패
- 간헐적 발생(경기 시간에만)으로 원인 파악이 특히 어려웠던 특이한 장애

### 전문가 인사이트

이 사례는 SRE에게 몇 가지 중요한 교훈을 준다:

**1. 장애 원인의 범위를 넓혀라**

TLS 오류가 발생하면 보통 인증서 만료, DNS 문제, 네트워크 설정 오류만 의심한다. 하지만 ISP 수준의 법적 차단, 정부 검열, 클라우드 제공자의 규정 준수 등 외부 요인도 고려해야 한다.

**2. 의존성 매핑이 필수다**

Docker 이미지 pull 하나에 얽힌 의존성 체인을 파악하고 있어야 빠르게 원인을 좁힐 수 있다:

```javascript
graph LR
    A[docker pull] --> B[Docker Hub API]
    B --> C[이미지 메타데이터]
    C --> D[Cloudflare R2 스토리지]
    D --> E[ISP 네트워크]
    E --> F[최종 사용자]
```

**3. 다중 경로 확보가 생존 전략이다**

단일 레지스트리, 단일 네트워크 경로에 의존하면 통제 불가능한 외부 요인에 무방비 상태가 된다. Mirror registry, 프라이빗 레지스트리 캐시, 대체 네트워크 경로를 미리 준비해야 한다.

### 참고 자료
- [HackerNews 원본 글](https://news.ycombinator.com/item?id=47738883)
- [La Liga 공식 성명](https://www.laliga.com/noticias/nota-informativa-en-relacion-con-el-bloqueo-de-ips-durante-las-ultimas-jornadas-de-laliga-ea-sports-vinculadas-a-las-practicas-ilegales-de-cloudflare)
- [Docker Registry Mirror 설정 가이드](https://docs.docker.com/registry/recipes/mirror/)
- [GitLab Runner 설정 문서](https://docs.gitlab.com/runner/configuration/)

---

*이 글은 실제 HackerNews에 게시된 사례를 바탕으로 작성되었습니다. "Thank you, Spain"이라는 원작자의 탄식이 기술 커뮤니티의 공감을 얻은 이유는, 통제할 수 없는 외부 요인이 프로덕션 시스템에 미치는 영향을 모든 DevOps 엔지니어가 두려워하기 때문일 것이다.*

---

**출처**: [https://news.ycombinator.com/item?id=47738883](https://news.ycombinator.com/item?id=47738883)