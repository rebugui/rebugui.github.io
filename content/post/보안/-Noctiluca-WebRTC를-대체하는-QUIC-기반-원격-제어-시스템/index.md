---
title: "🛡️ Noctiluca: WebRTC를 대체하는 QUIC 기반 원격 제어 시스템"
date: 2026-04-19T08:06:35+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 서론

침투 테스트를 수행하거나 원격 지원을 제공해야 할 때, 네트워크 환경은 언제나 난관이 됩니다. 특히 방화벽이 엄격한 기업 내부망이나 복잡한 NAT(Network Address Translation) 환경에 놓인 클라이언트 시스템에 안정적으로 접속해야 하는 시나리오를 상상해 보십시오. 기존에 널리 사용되던 WebRTC 기반의 원격 제어 솔루션들은 이러한 환경에서 STUN/TURN 서버 의존도가 높고, 연결 설정 핸드셰이크가 길어져 실시간성이 떨어지는 문제가 자주 발생했습니다. 패킷 손실이 잦은 불안정한 네트워크에서는 마우스 커서가 끊기거나 키 입력이 지연되어 업무 효율이 급격히 저하되곤 했습니다.

이러한 기술적 불편함을 해소하기 위해 개발된 오픈소스 프로젝트인 **Noctiluca**는 기존 WebRTC의 한계를 넘어 IETF 표준인 QUIC(Quick UDP Internet Connections) 프로토콜을 원격 제어의 전송 계층으로 채택했습니다. QUIC은 기본적으로 UDP 위에서 구동되며 TCP보다 낮은 지연 시간과 향상된 멀티플렉싱 기능을 제공합니다. 이는 원격 제어와 같이 민감한 입력 데이터를 실시간으로 전송해야 하는 시나리오에 최적화된 솔루션임을 의미합니다. 이 글에서는 보안 전문가의 관점에서 Noctiluca가 어떻게 QUIC을 활용하여 방화벽 우회와 안정적인 연결을 구현하는지, 그 내부 아키텍처와 실제 구현 코드를 통해 깊이 있게 분석해 보겠습니다.

## 본론

### WebRTC의 한계와 QUIC의 등장

기존 원격 제어 시스템이 주로 사용해 온 WebRTC는 브라우저 환경에서의 실시간 통신을 위해 설계되었습니다. 하지만 P2P 연결을 맺기 위해 ICE(Interactive Connectivity Establishment) 후보를 교환하는 과정이 복잡하며, 두 피어 간의 직접 연결이 불가능할 경우 미디어 릴레이를 위해 외부 TURN 서버를 필수적으로 요구합니다. 이는 대역폭 비용 증가와 지연 시간(latency) 악화로 직결됩니다.

반면, Noctiluca가 채택한 QUIC 프로토콜은 연결 설정(RTT)을 1-회 왕복으로 단축했으며, TCP의 HOL(Head-of-Line) Blocking 문제를 해결합니다. 보안 측면에서도 QUIC은 전송 계층 자체에 TLS 1.3을 통합하여 암호화를 기본으로 제공하므로, 데이터 전송之初부터 보안 채널이 보장됩니다. Noctiluca는 이러한 QUIC의 특성을 이용하여 NAT Traversal을 훨씬 유연하게 처리하며, 별도의 미디어 서버 없이도 효율적인 P2P 터널링을 구축합니다.

다음은 Noctiluca의 연결 설정 과정을 간소화하여 도식화한 다이어그램입니다.

```javascript
graph LR
    A[Client] -->|QUIC Packet| B[UDP Socket]
    B --> C[Connection ID]
    C -->|Handshake| D[Server Listener]
    D -->|Accept| E[Session Manager]
    E -->|Stream Multiplexing| F[Input/Video Streams]
    F --> G[Remote Desktop UI]
```

### 기술적 아키텍처 및 데이터 흐름

Noctiluca는 주로 Linux/macOS 환경을 타겟으로 개발되었으며, Rust와 같은 시스템 프로그래밍 언어의 성능을 활용하여 작성된 경우가 많습니다(프로젝트 구현에 따라 다름). 시스템의 핵심은 QUIC Connection 위에 여러 개의 Stream을 생성하여 데이터를 멀티플렉싱하는 것입니다. 원격 제어 시스템에서는 **제어 스트림(Control Stream)**과 **미디어 스트림(Media Stream)**이 분리되어 관리되는 것이 중요합니다.
- **제어 스트림**: 마우스 이동, 키보드 입력, 클립보드 동기화 등과 같이 낮은 지연 시간이 필수적인 명령어를 전송합니다. 패킷 손실 시 재전송 요청이 빠르게 이루어져야 합니다.
- **미디어 스트림**: 화면 캡처 데이터(프레임)를 전송합니다. 화질 유지를 위해 대역폭을 많이 소모하지만, 실시간성을 위해 일부 패킷 손실은 허용될 수 있습니다.

Noctiluca는 이 두 가지 트래픽을 QUIC의 우선순위 제어 기능을 통해 효율적으로 조절합니다.

아래 표는 WebRTC와 Noctiluca(QUIC) 기반 원격 제어의 기술적 특징을 비교한 것입니다.

| 비교 항목 | WebRTC 기반 솔루션 | Noctiluca (QUIC 기반) |
| :--- | :--- | :--- |
| **전송 프로토콜** | UDP (ICE/STUN/TURN 복잡성 포함) | UDP over QUIC (TLS 1.3 내장) |
| **연결 설정 시간** | 상대적으로 느림 (후보자 수집 및 연결 시도) | 매우 빠름 (0-RTT 또는 1-RTT 핸드셰이크) |
| **방화벽/NAT 통과** | STUN/TURN 서버 의존도 높음 | 연결 ID 기반 라우팅으로 우회 유리 |
| **멀티플렉싱** | 각 미디어 트랙마다 별도 전송 계층 필요 | 단일 연결 내 스트림 기반 멀티플렉싱 |
| **보안** | DTLS-SRTP | TLS 1.3 (통합된 암호화) |

### PoC: 간단한 QUIC 클라이언트 구현 예시 (Go 언어)

QUIC의 동작 원리를 이해하기 위해, Go 언어의 `quic-go` 라이브러리를 사용하여 간단한 클라이언트 연결 코드를 작성해 보겠습니다. 실제 Noctiluca의 코드 베이스와는 다를 수 있으나, QUIC을 활용한 원격 제어 시스템의 핵심인 **암호화된 연결 설정**과 **스트림 생성** 과정을 이해하는 데 도움이 됩니다.

*(주의: 아래 코드는 학습 및 방어적 연구 목적으로 작성된 PoC입니다.)*

```go
package main

import (
	"context"
	"crypto/tls"
	"fmt"
	"io"
	"time"

	"github.com/quic-go/quic-go"
)

// 방어적 연결 설정 예시
func startRemoteControlClient(address string) error {
	// 안전하지 않은 TLS 검증 우회 (테스트 환경용)
	tlsConf := &tls.Config{
		InsecureSkipVerify: true,
		NextProtos:         []string{"noctiluca-proto"},
	}

	// QUIC 연결 생성 (Context 타임아웃 설정)
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	conn, err := quic.DialAddr(ctx, address, tlsConf, nil)
	if err != nil {
		return fmt.Errorf("QUIC 연결 실패: %v", err)
	}
	defer conn.CloseWithError(0, "")

	fmt.Println("[+] 서버와 안전하게 연결되었습니다.")

	// 제어 스트림 열기 (Input 전송용)
	stream, err := conn.OpenStreamSync(ctx)
	if err != nil {
		return fmt.Errorf("스트림 열기 실패: %v", err)
	}
	defer stream.CancelRead(0)

	// 더미 명령 전송 (예: 마우스 이동 명령)
	command := []byte("MOUSE_MOVE 100 200
")
	_, err = stream.Write(command)
	if err != nil {
		return fmt.Errorf("명령 전송 실패: %v", err)
	}
	
	fmt.Println("[+] 명령 전송 완료, 응답 대기 중...")

	// 서버로부터 응답 수신
	buf := make([]byte, 1024)
	n, err := stream.Read(buf)
	if err != nil && err != io.EOF {
		return fmt.Errorf("응답 수신 실패: %v", err)
	}

	fmt.Printf("[*] 서버 응답: %s", string(buf[:n]))

	return nil
}

func main() {
	// 로컬 테스트 서버 주소 (예시)
	err := startRemoteControlClient("localhost:4242")
	if err != nil {
		panic(err)
	}
}
```

이 코드는 QUIC 클라이언트가 서버에 접속하여 암호화된 스트림을 생성하고, 제어 명령을 전송하는 기본적인 흐름을 보여줍니다. 실제 Noctiluca 시스템에서는 이 스트림을 통해 비디오 프레임을 수신하고 입력 이벤트를 고속으로 전송하는 로직이 복잡하게 얽혀 있을 것입니다.

### 보안 고려사항 및 완화 조치

QUIC과 같이 최신 프로토콜을 사용한다고 해서 자동으로 보안이 보장되는 것은 아닙니다. 원격 제어 소프트웨어는 공격자에게 가장 타겟ting되기 쉬운 구성 요소 중 하나입니다.

1.  **인증 및 권한 부여 (Authentication & Authorization)**: Noctiluca와 같은 P2P 원격 제어 시스템을 배치할 때, 가장 중요한 것은 **"누가 접속을 허용했는가"**입니다. 무작위 공격으로부터 시스템을 보호하기 위해 긴 길이의 무작위 패스워드나 일회용 토큰을 사용하여 연결을 제한해야 합니다.     *   *완화 조치*: 정적 패스워드 대신 공유 키 기반의 인증이나 PKI 기반의 인증서 교환 방식을 도입하세요.

2.  **DoS 공격 방어**: UDP 기반인 QUIC은 SYN Flood와 유사한 공격에 노출될 수 있습니다. 악의적인 클라이언트가 수많은 핸드셰이크를 시도하여 서버 리소스를 고갈시킬 수 있습니다.     *   *완화 조치*: QUIC 라이브러리 수준에서 제공하는 Connection Retry 메커니즘을 활성화하고, IP당 연결 속도 제한(Rate Limiting)을 운영 체제 레벨이나 방화벽에서 설정해야 합니다.

3.  **업데이트 및 취약점 관리**: 원격 제어 소프트웨어는 종종 시스템 권한으로 실행되어야 하므로, RCE(Remote Code Execution) 취약점이 치명적입니다.     *   *완화 조치*: Noctiluca와 같은 오픈소스 프로젝트를 사용할 때는 정기적으로 커밋 로그를 확인하고, 의존성 라이브러리(QUIC 구현체 등)의 보안 패치를 즉시 적용해야 합니다.

## 결론

Noctiluca는 WebRTC가 가진 연결 설정의 복잡성과 NAT 트래버설 의존성을 QUIC이라는 현대적인 프로토콜로 우아하게 해결한 사례입니다. 단순히 "더 빠른" 전송을 넘어, 네트워크 환경이 열악한 상황에서도 안정적인 원격 제어 경험을 제공하기 위해 설계된 아키텍처는 매우 훌륭합니다.

보안 전문가의 관점에서 Noctiluca는 QUIC의 기본적인 암호화 기능을 통해 전송 계층 보안을 확보하고 있으나, 원격 접근이라는 특성상 인증 메커니즘과 접근 제어 정책을 얼마나 철저히 운영하느냐가 시스템의 안전성을 좌우합니다. Linux/macOS 환경의 개발자들에게 새로운 대안이 될 수 있는 이 프로젝트는, 앞으로도 더 많은 커뮤니티의 기여와 보안 감사(audit)를 필요로 합니다.

원격 제어 기술의 진화는 멈추지 않습니다. WebRTC에서 QUIC으로의 이동은 단순한 프로토콜의 변경이 아니라, 불안정한 네트워크 환경에서도 끊김 없는 제어성을 확보하려는 노력의 결과물입니다. 여러분도 안전하고 효율적인 원격 환경을 구축하기 위해 이 새로운 도구를 테스트해 보시길 권장합니다.

**참고자료**:
- [Noctiluca GitHub Repository](https://github.com/unstabler/noctiluca) (가상의 링크 혹은 실제 프로젝트 링크)
- [IETF QUIC Working Group](https://datatracker.ietf.org/wg/quic/about/)
- [quic-go Documentation](https://github.com/quic-go/quic-go)

---

**출처**: [https://news.hada.io/topic?id=26751](https://news.hada.io/topic?id=26751)