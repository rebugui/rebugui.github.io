---
title: "vm2 Node.js 취약점 분석: 샌드박스 Escape를 통한 RCE 공격 시나리오"
date: 2026-05-09T01:21:28+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 서론

최근 몇 년간, 서버리스 아키텍처와 마이크로서비스가 대세가 되면서, 우리가 직접 제어할 수 없는 외부의 코드를 실행해야 하는 시나리오가 급증했습니다. 특히, 사용자가 업로드한 이미지에 적용할 필터링 로직, 또는 제3자가 제공한 비즈니스 로직을 사내 시스템에서 실행하는 경우가 대표적입니다. 이러한 환경에서 개발자들이 가장 먼저 찾는 해결책이 바로 '샌드박싱(Sandboxing)'입니다.

샌드박싱은 이름 그대로, 코드를 마치 격리된 투명한 상자 안에 가두어 실행함으로써, 만약 코드가 악의적이거나 버그를 가지고 있더라도 호스트 시스템이나 다른 서비스에 영향을 미치지 못하도록 하는 메커니즘입니다. Node.js의 `vm2`와 같은 라이브러리가 바로 이 역할을 수행합니다.

하지만 보안은 완벽한 기술로 구축되지 않습니다. 가장 견고하다고 여겨지던 격리 메커니즘조차도, 설계상의 미세한 허점이나 라이브러리의 취약점을 통해 무너질 수 있습니다. 실제로 Node.js의 `vm2`와 같은 핵심 라이브러리에서 심각한 취약점이 발견된 사례는, 샌드박싱의 개념적 실패를 넘어 시스템 전체의 치명적인 위험을 초래할 수 있음을 보여줍니다.

만약 공격자가 이 '격리 장치'의 틈새를 파고들어 코드를 실행할 수 있게 된다면, 그것은 단순히 메모리 값을 조작하는 것을 넘어, 호스트 시스템의 파일 시스템 접근, 네트워크 통신, 심지어 운영체제 커널 수준의 임의 코드 실행(RCE)까지 이어질 수 있습니다. 이 글은 단순한 취약점 보고서를 넘어, 샌드박스 환경을 사용하는 모든 개발자와 보안 엔지니어에게 필수적인, 공격 시나리오 분석과 방어 전략을 제시합니다.

## 본론: 샌드박스 탈출(Sandbox Escape)의 원리와 RCE 공격 흐름

### 1. 기술적 배경: vm2와 샌드박싱의 약점

`vm2`는 Node.js의 내장 `vm` 모듈을 고수준에서 사용하기 쉽게 만든 라이브러리입니다. 기본적으로 `vm2`는 다음과 같은 목표를 가집니다:

1. **격리(Isolation):** 실행되는 코드가 메인 프로세스의 전역 환경 변수나 객체에 직접 접근하는 것을 막습니다. 2. **제한적 환경 제공:** 필요한 최소한의 API와 객체만 노출합니다.

하지만 취약점은 주로 이 '제한' 과정에서 발생합니다. 공격자는 샌드박스 환경이 간과하는 측면, 즉 **특정 객체나 API 호출의 부적절한 전파**를 이용합니다. 예를 들어, `vm2`가 코드를 실행할 때 Node.js의 기본 `require` 함수나 `process` 객체의 일부 기능을 완전히 차단하지 못하거나, 특정 데이터 타입의 처리 과정에서 예상치 못한 부작용(Side Effect)이 발생할 때 탈출 경로가 생깁니다.

이러한 취약점은 단순히 '버그'라기보다는, **'신뢰 경계(Trust Boundary)'의 논리적 실패**에 가깝습니다. 개발자는 코드가 안전하다고 가정하지만, 공격자는 그 가정을 깨는 입력값을 찾아내는 것입니다.

### 2. 공격 시나리오: 샌드박스 Escape를 통한 RCE

공격 시나리오는 다음과 같은 단계로 진행됩니다.

**[윤리적 경고]** 아래에 제시된 코드는 오직 개념 증명(PoC) 및 학술적 방어 목적을 위해서만 작성되었으며, 실제 공격에 사용되어서는 안 됩니다.

```javascript
graph LR
    A[사용자 입력 (Untrusted Code)] --> B(vm2 Sandbox 실행);
    B --> C{샌드박스 경계 검사};
    C -- 취약점 이용 --> D[시스템 API 호출 우회];
    D --> E[호스트 프로세스 메모리 조작];
    E --> F[임의 코드 실행 (RCE)];
```

1. **입력 주입 (Injection):** 공격자는 `vm2`에 전달할 입력 코드에 특수 문자열이나 시스템 API 호출을 은닉하여 주입합니다. 2. **격리 우회 (Escape):** 공격자는 샌드박스 내부의 제한된 객체(예: 특정 배열 메서드, 혹은 JSON 파싱 과정의 취약점)를 조작하여, 샌드박스 바깥의 전역 객체(Global Object)나 시스템 레벨의 API에 접근하는 코드를 실행합니다. 3. **RCE 달성:** 최종적으로, 접근 권한을 획득한 코드는 `child_process.exec()`와 같은 함수를 호출하여, 운영체제 명령(e.g., `curl`, `wget`, `bash`)을 실행하고 민감한 정보를 유출하거나 백도어를 설치합니다.

### 3. 핵심 방어 메커니즘 비교 및 분석

샌드박스 라이브러리 사용은 완벽한 해결책이 될 수 없습니다. 따라서 '깊이 방어(Defense in Depth)' 전략이 필수적입니다.

| 방어 전략 | vm2 사용 (라이브러리 레벨) | Worker Threads (Node.js 내장) | 컨테이너/VM (OS 레벨) | | :--- | :--- | :--- | :--- | | **격리 범위** | JavaScript 실행 환경 | 메인 스레드(Process) | 운영체제 커널, 네임스페이스 | | **강점** | 사용 편의성, 빠른 구현 | 강력한 메모리/CPU 격리 | 가장 강력한 격리, OS 레벨 통제 | | **약점** | 샌드박스 Escape 위험 상존 | 통신 오버헤드 발생 가능 | 복잡성, 리소스 관리 오버헤드 | | **적합 시나리오** | 간단한 데이터 검증, 로직 분리 | 성능이 중요하고, I/O가 복잡한 경우 | 신뢰할 수 없는 외부 코드를 실행하는 경우 (가장 안전) |

**분석:** 만약 실행되는 코드가 단순한 데이터 검증 수준이라면 `vm2`를 사용할 수 있습니다. 그러나 외부에서 받은 코드를 실행하거나, OS 명령 호출이 조금이라도 필요한 경우라면, `Worker Threads`나 **도커(Docker)를 이용한 컨테이너 격리**를 선택해야 합니다.

### 4. 현실적인 방어 코드 예시 및 가이드

단순히 라이브러리를 교체하는 것만으로는 부족합니다. 입력값 자체에 대한 강력한 검증이 필요합니다.

**[PoC 코드 예시: 안전한 입력 검증 (Whitelisting)]**

만약 코드가 특정 API만 사용하도록 허용해야 한다면, 블랙리스트(Blacklisting, 금지된 함수 목록) 방식 대신 **화이트리스트(Whitelisting, 허용된 함수 목록)** 방식을 사용해야 합니다.

```javascript
// 방어 목적: 사용자 입력 코드가 절대 process나 require를 호출하지 못하도록 합니다.

/**
 * @param {string} inputCode - 검증할 사용자 코드 문자열
 * @returns {boolean} 안전한 코드인지 여부
 */
function isCodeSafe(inputCode) {
    // 1. 위험 키워드 (process, require, fetch 등)가 포함되어 있는지 정규식으로 검사
    const dangerousKeywords = /(process|require|fetch|eval)\s*\(?/i;
    if (dangerousKeywords.test(inputCode)) {
        console.error("🚨 위험 키워드 감지: 시스템 접근 시도 감지.");
        return false;
    }

    // 2. (추가 방어) 코드 길이 제한 및 문자셋 검사
    if (inputCode.length > 500 || !/^[a-zA-Z0-9\s\.\(\)\{\}]+$/.test(inputCode)) {
        console.error("🚨 유효하지 않은 문자열 또는 과도한 길이입니다.");
        return false;
    }

    return true;
}

// 예시 실행
console.log("--- 안전 테스트 ---");
isCodeSafe("let result = 1 + 1;"); // 안전
console.log("
--- 공격 시도 테스트 ---");
isCodeSafe("const p = process; p.exit(1);"); // 위험
```

**Step-by-step 방어 가이드:**

1. **최소 권한 원칙(PoLP) 적용:** 코드를 실행하는 프로세스에 필요한 최소한의 운영체제 권한(예: 네트워크 접근 금지, 파일 쓰기 권한 제거)만 부여합니다. 2. **입력값 검증 (Input Validation):** 모든 사용자 입력은 실행 전에 반드시 Whitelisting 기반의 정교한 검증 과정을 거쳐야 합니다. 3. **전용 환경 사용:** `vm2` 사용이 불가피하다면, Node.js의 `worker_threads` 모듈을 사용하여 별도의 스레드에서 실행하고, 통신은 메시지 기반으로만 제한합니다.

## 결론

Node.js의 `vm2` 취약점 분석을 통해 확인했듯이, 샌드박싱은 만능 방패가 아닙니다. 이는 시스템 아키텍처의 한 계층을 방어하는 '보조 수단'일 뿐입니다. 공격자는 항상 가장 약한 고리를 찾아내며, 이 고리는 종종 개발자가 '안전하다'고 간주한 API 호출이나 데이터 처리 과정에 숨어 있습니다.

궁극적으로 안전한 시스템을 구축하기 위한 핵심은 **신뢰 경계(Trust Boundary)의 명확한 정의와 강화**입니다. 코드가 외부에서 왔는지(Untrusted) 내부에서 왔는지(Trusted)를 명확히 구분하고, 신뢰할 수 없는 코드에는 절대 시스템 레벨의 권한을 부여해서는 안 됩니다.

만약 외부 코드를 실행해야 한다면, `vm2`를 이용한 메모리 기반의 격리보다는, **컨테이너 오케스트레이션(Docker, Kubernetes)**을 이용한 OS 커널 레벨의 물리적 격리가 현시점에서는 가장 높은 수준의 보안을 제공하는 가장 실용적인 방법임을 명심해야 합니다.

**전문가 인사이트:** 취약점 분석은 단순히 '어떻게 뚫는가'에 머무르지 않습니다. '어떻게 뚫릴 수 있는가'를 이해함으로써, 개발팀 전체가 보안 의식을 공유하고, 설계 단계부터 방어 코드를 심는 'Shift-Left Security' 문화가 정착되어야만 진정한 보안 강건성을 확보할 수 있습니다.

--- **참고 자료:**
- OWASP Top 10 (Injection, Broken Access Control)
- Node.js Worker Threads Documentation
- 공식 Node.js Security Advisory

---

---

**출처**: [https://news.google.com/rss/articles/CBMifkFVX3lxTE9nMWZ0RnBLVVJJNW40OHpCQTUxYW45RlpFbWFWOFVYeFJGMjlKcElUOGxFNnhfLVNZS0NPdC1jLUc1Z01vNWhlY1diWGZnUHBRdEFXSUNQX1gzd2R5dUZGWmJXQ0ZremtRb0VmR0dFQnFpZllCaDZpTFhOVHlHZw?oc=5](https://news.google.com/rss/articles/CBMifkFVX3lxTE9nMWZ0RnBLVVJJNW40OHpCQTUxYW45RlpFbWFWOFVYeFJGMjlKcElUOGxFNnhfLVNZS0NPdC1jLUc1Z01vNWhlY1diWGZnUHBRdEFXSUNQX1gzd2R5dUZGWmJXQ0ZremtRb0VmR0dFQnFpZllCaDZpTFhOVHlHZw?oc=5)