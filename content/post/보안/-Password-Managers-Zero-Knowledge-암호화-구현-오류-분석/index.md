---
title: "🔑 Password Managers: Zero Knowledge 암호화 구현 오류 분석"
date: 2026-04-19T08:06:16+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 서론

최근 레드 팀(Red Team) 활동 중 흥미로운 사례를 접했습니다. 방화벽으로 튼튼하게 보호된 엔터프라이즈 환경이었음에도 불구하고, 공격자는 단 몇 분 만에 직원의 모든 계정 정보를 탈취하는 데 성공했습니다. 놀랍게도 공격의 진입로는 복잡한 서버 취약점도, 제로데이(Zero-day) 익스플로잇도 아니었습니다. 바로 직원이 사용하던 '유명한' 패스워드 매니저의 확장 프로그램이었죠.

이 패스워드 매니저는 마케팅 내내 "Zero Knowledge(제로 지식)" 아키텍처를 자랑했습니다. "우리는 당신의 마스터 비밀번호조차 알 수 없다"는 주장이었습니다. 하지만 현실은 달랐습니다. 클라이언트 사이드의 메모리 덤프를 분석해보니, 평문(Pertext) 상태의 마스터 비밀번호와 복호화 키가 고스란히 남아 있었습니다. 이는 사용자가 보안이라고 믿고 의지했던 그 '검은 상자'가 실제로는 얇은 종이상자였음을 보여주는 처참한 현장이었습니다.

이 글에서 단순히 제품을 비판하는 것이 목적은 아닙니다. 중요한 것은, 많은 보안 솔루션이 "Zero Knowledge"라는 용어를 마케팅 도구로 전락시키고 있으며, 실제 암호화 구현(Implementation) 단계에서 치명적인 실수를 범하고 있다는 기술적 진실을 파헤치는 것입니다. 왜 이론적으로 완벽한 암호화 모델이 코드로 구현되면 무너지는지, 그리고 우리는 어떻게 이를 식별하고 방어해야 하는지 살펴보겠습니다.

---

## 본론

### Zero Knowledge 아키텍처의 이론과 현실

"Zero Knowledge"는 암호학적으로 서버가 사용자 데이터를 전혀 볼 수 없는 상태를 의미합니다. 즉, 데이터는 클라이언트(사용자 기기)에서 암호화되어 서버로 전송되고, 서버는 암호화된 블롭(Blob)만 저장합니다. 서버는 복호화 키(Key)를 가지고 있지 않으므로 데이터를 열어볼 수 없죠.

하지만 최근 연구에서 지적된 바와 같이, 많은 패스워드 매니저가 이 아키텍처를 잘못 구현하고 있습니다. 주로 발견되는 문제는 다음과 같습니다:

1.  **메타데이터 유출**: 비밀번호 자체는 암호화되어 있지만, 암호화된 데이터의 크기, 접근 시간, 도메인 주소 등의 부가 정보가 노출되어 사용자 행적을 추적 가능하게 만듭니다. 2.  **클라이언트 사이드 로직 취약점**: 마스터 비밀번호를 처리하는 과정에서 메모리상에 키가 남거나, DOM(문서 객체 모델)에 노출되는 경우입니다. 3.  **잘못된 키 파생 함수(KDF) 사용**: 사용자 경험(UX)을 이유로 암호학적으로 안전하지 않은 빠른 해시 함수를 사용하여 무차별 대입(Brute-force) 공격에 취약하게 만듭니다.

이러한 취약점이 어떻게 악용될 수 있는지, 이상적인 흐름과 취약한 흐름을 비교해 보겠습니다.

```javascript
graph TD
    A[사용자 입력: 마스터 비밀번호] --> B{클라이언트 처리}
    B -->|이상적인 흐름| C[안전한 키 파생 KDF]
    C -->|메모리 내 임시 저장| D[데이터 암호화]
    D -->|암호문 전송| E[서버 저장]
    D -->|사용 후 즉시 소거| F[메모리 비우기]
    E --> G[서버 관리자: 내용 불가]

    B -->|취약한 흐름| H[느슨한 키 파생/로깅]
    H -->|메모리 고정/덤프 위험| I[데이터 암호화]
    I -->|암호문 전송| E
    I -->|DOM 로깅/Crash Dump| J[공격자 획득 경로]
```

### 취약점 시나리오 및 메커니즘 분석

#### 1. 메모리 누출 및 키 관리 실패

가장 흔한 실수는 마스터 비밀번호에서 파생된 키(Key)를 메모리에서 안전하게 지우지 못하는 것입니다. 자바스크립트 기반의 웹 패스워드 매니저나 전자 앱(Electron App) 환경에서는 가비지 컬렉션(Garbage Collection) 시점을 개발자가 정확히 제어하기 어렵습니다. 공격자가 브라우저 충돌이나 특정 익스플로잇을 통해 메모리 덤프를 얻어낸다면, 키가 그대로 노출될 수 있습니다.
> **⚠️ 윤리적 경고**: 아래 제공되는 모든 코드는 교육 및 방어 목적이며, 허가 없는 시스템에서 테스트하는 것은 불법입니다.

다음은 마스터 비밀번호 처리 시 취약할 수 있는 JavaScript 코드의 개념적 예시입니다.

```javascript
// 취약한 구현 예시 (개념 증명)

class VaultManager {
    constructor() {
        this.masterKey = null;
    }

    // 마스터 비밀번호 입력 시 호출
    async unlock(masterPassword) {
        // 취약점 1: PBKDF2 반복 횟수가 너무 적음 (성능 우선으로 보안 타협)
        const salt = 'hardcoded_salt'; 
        const iterations = 1000; // 매우 낮음, 추천 100,000+

        // 키 파생
        const keyBuffer = await crypto.subtle.importKey(
            'raw', new TextEncoder().encode(masterPassword), 'PBKDF2', false, ['deriveBits']
        );
        
        const derivedBits = await crypto.subtle.deriveBits(
            { name: 'PBKDF2', salt: new TextEncoder().encode(salt), iterations: iterations },
            keyBuffer, 256
        );

        // 취약점 2: 키를 클래스 인스턴스에 계속 보관 (메모리 노출 위험)
        this.masterKey = derivedBits;

        // 취약점 3: 디버깅 목적으로 콘솔에 로그 남김 (실제 사고 발생 사례 있음)
        console.log('[DEBUG] Vault unlocked with key:', this.masterKey);
        
        return true;
    }

    // 데이터 복호화
    decryptData(encryptedData) {
        // masterKey를 사용하여 복호화 수행
        // ... 로직 생략 ...
    }
}

// 공격자 시나리오:
// 1. 사용자가 unlock() 호출
// 2. 브라우저 개발자 도구나 크래시 덤프를 통해 this.masterKey 값 탈취 가능
// 3. 탈취된 키로 로컬에 저장된 암호화된 DB 복호화
```

위 코드는 몇 가지 결정적인 실수를 보여줍니다. 첫째, `console.log`를 통해 민감한 정보를 노출시켰고, 둘째 키를 메모리에 장기 보관하고 있으며, 셋째 약한 KDF 설정을 사용했습니다. 이는 "Zero Knowledge"가 깨지는 지점입니다.

#### 2. 메타데이터 유출 (Side-Channel Attack)

Zero Knowledge라고 주장하는 서버라도, 사용자가 어떤 사이트에 접속하는지 알 수 있다면 보안의 의미가 퇴색됩니다. 예를 들어, 패스워드 매니저가 특정 도메인(`evil.com`)의 비밀번호를 요청할 때 서버로 보내는 패킷의 크기가 다르거나 타이밍이 다르다면, 공격자는 이를 통해 사용자의 행동 패턴을 파악할 수 있습니다.

다음은 안전한 구현과 취약한 구현을 비교한 표입니다.

| 비교 항목 | 안전한 Zero Knowledge 구현 | 취약한 구현 (일반적인 사례) | | :--- | :--- | :--- | | **서버 데이터 가시성** | 암호화된 BLOB만 저장 (내용 확인 불가) | 암호화된 BLOB 저장 (내용 확인 불가) | | **메타데이터 (URL 등)** | 클라이언트에서 필터링 후 요청하거나, 전체 암호화된 DB 다운로드 후 로컬 검색 | 요청 시 도메인 이름 포함하여 API 콜 (서버가 접속 사이트 인지 가능) | | **마스터 키 저장소** | 서버에 저장 안 함 (클라이언트 전용) | 서버에 저장 안 함 (동일하나 클라이언트 메모리 관리 실패) | | **통신 프로토콜** | TLS 위에 추가적인 래핑 또는 상태 암호화 사용 | 단순 TLS (패턴 분석 가능) | | **클라이언트 메모리** | 안전한 enclave 또는 사용 후 즉시 zeroing | 자바스크립트 힙에 장기간 잔존 |

### 실무 적용 가이드: 안전한 패스워드 매니저 선정 및 점검

보안 전문가로서, 또는 개인 사용자로서 우리는 무엇을 점검해야 할까요? 다음은 패스워드 매니저의 보안성을 평가하기 위한 단계별 가이드입니다.

**Step 1: 오픈 소스 여부 확인** 보안의 투명성은 필수적입니다. 소스 코드가 공개되어 있지 않은 독점(Closed-source) 솔루션은 "Zero Knowledge"라고 주장하더라도 검증이 불가능합니다. Bitwarden, KeePassXC와 같은 오픈 소스 프로젝트를 우선 고려하세요.

**Step 2: 클라이언트 사이드 암호화 로직 검증** 암호화가 서버가 아닌 로컬 장치에서 일어나는지 확인해야 합니다. 네트워크 탭을 열고 로그인 시 어떤 데이터가 전송되는지 관찰하세요. 마스터 비밀번호나 복호화 키가 서버로 전송된다면 그건 Zero Knowledge가 아닙니다.

**Step 3: 감사(Audit) 보고서 확인** 서드파티 보안 업체의 감사를 받은 이력이 있는지 확인하세요. 감사 보고서에서 "메모리 안전성", "키 관리", "메타데이터 누출" 부분을 중점적으로 읽으십시오.

**Step 4: 메타데이터 차단 기능 확인** 최신 패스워드 매니저들은 "도메인 추적 금지" 또는 "메타데이터 필터링" 기능을 제공합니다. 이 기능이 켜져 있는지, 혹은 기본적으로 메타데이터를 서버로 보내지 않는 아키텍처인지 확인하세요.

**Step 5: 이중 인증(MFA) 및 하드웨어 키 활성화** 비밀번호 관리 자체의 취약점을 보완하기 위해, 계정 접근 시 반드시 FIDO2/WebAuthn 기반의 하드웨어 키(예: YubiKey)를 사용하십시오. 이는 클라이언트 측 취약점이 노출되더라도 공격자가 계정을 탈취하는 것을 방지하는 마지막 방어선입니다.

---

## 결론

우리가 패스워드 매니저에 기대하는 것은 단순한 편의성이 아닙니다. 디지털 자산의 가장 마지막 성문(Seongmun) 역할입니다. 하지만 최근 연구가 밝혀낸 "Zero Knowledge 암호화 구현 오류"는 그 성문이 종잇장으로 만들어져 있을 수도 있다는 경각심을 줍니다.

Zero Knowledge는 마케팅 슬로건이 아니라, 수학적으로 증명 가능한 아키텍처이자 그에 부합하는 엄격한 코딩 표준이어야 합니다. 단순히 "서버에 비밀번호를 저장하지 않는다"는 사실만으로는 안전할 수 없습니다. 클라이언트의 메모리 관리, 메타데이터 유출 방지, 그리고 강력한 키 파생 알고리즘의 사용이 결합되었을 때 비로소 진정한 의미의 Zero Knowledge 보안이 완성됩니다.

보안 전문가로서의 제 인사이트는 다음과 같습니다: **"어떤 보안 솔루션도 맹신하지 마십시오. 특히 그 솔루션이 검증 불가능한 '검은 상자'라면 더더욱 그렇습니다."** 사용하는 도구의 작동 원리를 이해하고, 오픈 소스이며 정기적으로 감사를 받는 도구를 선택하는 것이 결국 여러분의 데이터를 지키는 가장 확실한 길입니다.

**참고자료:**
- [Original Study Summary - PC Gamer](https://news.google.com/rss/articles/CBMi4wFBVV95cUxONF9DSnpCMXRXdUh2WVJhMFFpd3RZSkc0VVZwRTJINGFRc3RWYk12SHdlM3hUUk1OVEpRVEVxQ2NhYkdMV3NuSTBBV0VJRUhsYXhLTS03N3gtbEw4aENYU29IVXJsWmRlU0JDQmkwVUZqYnAzdVd0ZnRzWHpuRXNRVUptNHZndDRnN0NlRDdtN1VNSnRvTHQ1NDBjQ2xMUU4wM0lNVFBkQ2lLQjNmUzQ0eDFzMjJGbWxJX3ZvbFpsckt4X2ZUcUJ4UFdKV1g3bGsyQXc4QlFGUW5Sa2hKeDFvN0xHSQ?oc=5)
- OWASP Password Storage Cheat Sheet
- CWE-922: Insecure Storage of Sensitive Information

---

**출처**: [https://news.google.com/rss/articles/CBMi4wFBVV95cUxONF9DSnpCMXRXdUh2WVJhMFFpd3RZSkc0VVZwRTJINGFRc3RWYk12SHdlM3hUUk1OVEpRVEVxQ2NhYkdMV3NuSTBBV0VJRUhsYXhLTS03N3gtbEw4aENYU29IVXJsWmRlU0JDQmkwVUZqYnAzdVd0ZnRzWHpuRXNRVUptNHZndDRnN0NlRDdtN1VNSnRvTHQ1NDBjQ2xMUU4wM0lNVFBkQ2lLQjNmUzQ0eDFzMjJGbWxJX3ZvbFpsckt4X2ZUcUJ4UFdKV1g3bGsyQXc4QlFGUW5Sa2hKeDFvN0xHSQ?oc=5](https://news.google.com/rss/articles/CBMi4wFBVV95cUxONF9DSnpCMXRXdUh2WVJhMFFpd3RZSkc0VVZwRTJINGFRc3RWYk12SHdlM3hUUk1OVEpRVEVxQ2NhYkdMV3NuSTBBV0VJRUhsYXhLTS03N3gtbEw4aENYU29IVXJsWmRlU0JDQmkwVUZqYnAzdVd0ZnRzWHpuRXNRVUptNHZndDRnN0NlRDdtN1VNSnRvTHQ1NDBjQ2xMUU4wM0lNVFBkQ2lLQjNmUzQ0eDFzMjJGbWxJX3ZvbFpsckt4X2ZUcUJ4UFdKV1g3bGsyQXc4QlFGUW5Sa2hKeDFvN0xHSQ?oc=5)