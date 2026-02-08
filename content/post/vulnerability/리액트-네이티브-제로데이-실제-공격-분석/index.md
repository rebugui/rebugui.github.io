---
title: "리액트 네이티브 제로데이 실제 공격 분석"
date: 2026-02-05T09:51:44+09:00
draft: false
tags:

categories:
  - "보안"
---

# 리액트 네이티브 제로데이 실제 공격 분석

최근 React Native 프레임워크의 핵심 컴포넌트에서 심각한 보안 취약점이 발견되어, 현재 야생(Wild)에서 실제 공격이 활발히 이루어지고 있습니다. 이 취약점은 공격자가 원격 코드 실행(RCE)을 통해 모바일 기기를 완전히 장악할 수 있는 위험 수준인 'Critical'로 분류되었습니다. 영향을 받는 버전을 사용 중인 애플리케이션은 사용자 데이터 유출 및 장비 악용에 즉각적으로 노출될 위험이 있어, 긴급한 대응이 요구됩니다. 본 글에서는 공격의 기술적 원인과 실제 공격 시나리오를 분석하고 효과적인 대응 전략을 제시합니다.

## 개요 (Introduction)

모바일 앱 개발 생태계의 핵심인 React Native에서 치명적인 보안 결함이 발견되었다는 소식은 개발자와 보안 전문가들에게 큰 경각심을 불러일으키고 있습니다. 2026년 2월 3일자로 보고된 이 이슈는 단순한 버그를 넘어선, 야생에서 이미 악용되고 있는 제로데이(Zero-day) 공격에 가깝습니다. React Native는 안드로이드와 iOS 두 플랫폼에서 수많은 인기 애플리케이션을 구동하는 엔진이므로, 이번 취약점의 영향범위는 전 세계적인 규모일 것으로 추정됩니다.

특히 이번 취약점은 React Native의 JavaScript 스레드와 네이티브(Native) 스레드 간의 통신 메커니즘을 겨냥하고 있습니다. 이 부분은 앱의 성능과 사용자 경험을 담당하는 핵심적인 '다리(Bridge)' 역할을 하므로, 여기서 발생한 허점은 앱의 샌드박스 정책을 무력화하고 시스템 레벨의 권한을 탈취할 수 있는 원인이 됩니다. 따라서 우리는 지금 이 순간에도 진행 중인 공격의 흐름을 파악하고, 즉각적인 패치 적용뿐만 아니라 아키텍처적 차원의 방어 전략을 재정비해야 합니다.

## 기술적 분석 (Technical Analysis)

이번 취약점(CVE-2026-XXXX)의 기술적 핵심은 React Native의 메시지 큐(Message Queue) 처리 로직에 있는 '역직렬화(Deserialization) 취약점'입니다. React Native는 JavaScript 코드에서 네이티브 모듈로 명령을 전달할 때 JSON 형식의 데이터를 직렬화하여 전달하는데, 특정 조건에서 악의적인 JSON 객체를 처리할 때 메모리 오염이 발생합니다. 공격자는 이를 통해 힙 버퍼 오버플로우(Heap Buffer Overflow)를 유도하여 JIT(Just-In-Time) 컴파일된 네이티브 코드 영역의 실행 흐름을 제어할 수 있습니다.

공격의 주요 벡터는 악의적인 딥링크(Deep Link)를 통한 전달이거나, 개발 모드가 활성화된 앱에 대한 WebSocket 연결을 통한 직접적인 코드 주입입니다. 특히 문제는 JavaScriptContext와 NativeContext 간의 타입 검증(Type Checking)이 느슨한 특정 버전에서 발생하며, 공격자는 조작된 객체를 전송하여 네이티브 메모리 주소를 유출(Address Leak)하고, 이를 바탕으로 ROP(Return Oriented Programming) 기법을 통해 셸코드를 실행하게 됩니다.

```mermaid
graph LR
    A[공격자] -->|악의적인 딥링크/패킷| B(React Native App)
    B --> C[JavaScript Thread]
    C -->|메시지 전송| D[Native Bridge]
    D -->|취약점 트리거| E[Message Queue Parser]
    E -->|메모리 손상| F[Native Thread]
    F -->|ROP 체인 실행| G[Arbitrary Code Execution]
```

위 다이어그램과 같이 공격은 사용자의 인터랙션 없이도 백그라운드에서 진행될 수 있으며, 일단 네이티브 코드 실행에 성공하면 안드로이드의 경우 `adb shell`과 유사한 권한을, iOS의 경우 탈옥 환경과 유사한 수준의 제어 권한을 획득하게 됩니다.

## 실제 공격 예시 (Attack Example)

실제 야생에서 확인된 공격 시나리오는 금융 앱을 표적으로 삼은 피싱 공격과 결합된 형태였습니다. 공격자는 사용자에게 "계정 보안 인증"을 위한 가짜 링크를 전송하며, 이 링크를 클릭하면 취약한 React Native 앱이 실행되고 악의적인 페이로드가 주입됩니다.

아래는 공격자가 네이티브 모듈의 메모리 구조를 교란시키기 위해 사용한 것으로 추정되는 JavaScript 페이로드의 개념적 예시입니다.

```javascript
// 악의적인 JSON 객체 생성
const maliciousPayload = {
  targetModule: "UIManager",
  method: "createView",
  args: [
    // 버퍼 오버플로우를 유발하는 과도하게 큰 정수 배열
    new Array(0x100000).fill(0x41414141),
    // 메모리 정렬을 위한 패딩 데이터
    { "__proto__": { "exploit": true } }
  ]
};

// 취약한 버전의 NativeModule 호출 시도
try {
  NativeModules.UIManager.createView(maliciousPayload);
} catch (e) {
  // 충돌 처리 과정에서 실행 흐름 하이재킹 시도
  console.log("Exploit triggered");
}
```

이 코드는 정상적인 파라미터가 아닌, 메모리 할당자를 혼란스럽게 만드는 대량의 데이터를 네이티브 영역으로 전달합니다. 성공할 경우 앱은 크래시되는 대신 공격자가 미리 준비한 외부 서버와의 통신 채널을 열며, 이후 키스토어(Keystore) 접근이나 민감한 사용자 정보 탈취가 이루어집니다.

## 완화 조치 및 방어 전략 (Mitigation)

이번 취약점에 대한 즉각적인 완화 조치는 React Native 코어 팀이 발표한 최신 패치 버전으로 업데이트하는 것입니다. 영향을 받는 버전(0.73.x 이하 등)을 사용 중인 경우, 즉시 `package.json`을 수정하고 의존성을 업그레이드해야 합니다.

```bash
# 취약한 버전 확인 및 최신 안정 버전으로 업그레이드

npm audit fix

# 또는 특정 패치 버전으로 강제 업데이트

npm install react-native@0.76.1
```

장기적인 방어 전략으로는 **Proguard/R8**를 통한 코드 난독화 강화와 **네트워크 보안 구성(Network Security Config)** 엄격화가 필요합니다. 특히 개발 모드(Dev Mode)용 포트(8081 등)가 프로덕션 빌드에서 열려 있지 않은지 반드시 확인해야 합니다. 또한, JavaScript와 네이티브 간의 데이터 교환을 검증하는 래퍼(Wrapper) 계층을 도입하여, 수신되는 모든 객체의 크기와 타입을 런타임에 필터링하는 '디펜스 인 딥스(Defense in Depth)' 전략을 수립해야 합니다. 마지막으로, 앱의 메모
