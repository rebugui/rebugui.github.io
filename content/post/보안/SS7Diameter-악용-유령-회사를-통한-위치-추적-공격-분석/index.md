---
title: "SS7/Diameter 악용: 유령 회사를 통한 위치 추적 공격 분석"
date: 2026-04-29T01:07:07+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 서론

새벽 2시, 보호 대상자가 이동 통신망이 끊기는 외진 시골 도로로 진입했습니다. GPS 신호가 희미해지고 스마트폰의 데이터 연결이 불안정해지는 상황입니다. 보통이라면 추적이 끊겨야 할 시점입니다. 하지만 공격자의 모니터에는 타겟의 정확한 위치가 실시간으로 깜빡이고 있습니다. 스마트폰의 앱을 해킹한 것도 아니고, GPS 위성 신호를 교란한 것도 아닙니다. 공격자는 타겟의 위치 정보를 요청할 권한이 있는 '또 다른 통신사'처럼 행동했기 때문입니다.

최근 공개된 보고서에 따르면, 전 세계적인 통신 감시 캠페인이 발견되었습니다. 이 캠페인의 핵심은 실제 존재하지 않는 '유령 회사(Ghost Company)'를 설립하고, 합법적인 통신 사업자(MNO)인 것처럼 위장하여 글로벌 로밍 허브에 접속하는 데 있었습니다. 이들이 악용한 것은 바로 이동통신망의 혈관인 SS7(Signaling System No. 7)와 Diameter 프로토콜입니다. 이 공격은 단순한 기술적 우회가 아닌, 통신 산업의 '신뢰'를 악용한 고도로 정교한 사회공학적 기술 결합체입니다.

왜 우리는 지금 이 문제에 주목해야 할까요? 5G 시대로의 전환이 가속화되고 있지만, 음성 호 및 로밍 연결을 위해 여전히 레거시 프로토콜인 SS7에 의존하는 하위 호환성 구조가 존재하기 때문입니다. 오늘 포스팅에서는 유령 회사가 어떻게 글로벌 통신망에 침투하여 위치를 추적하는지, 그 기술적 메커니즘과 실제 공격 시뮬레이션을 통해 이 위협을 심층 분석하겠습니다.
> **⚠️ 윤리적 경고**: 본 문서에서 다루는 모든 기술 정보, 코드 예시 및 분석 내용은 보안 연구 및 방어 목적(Defensive Security)입니다. 승인되지 않은 시스템에 대한 접근이나 개인의 프라이버시 침해는 불법이며 엄격히 금지됩니다.

## 본론

### 1. 기술적 배경: 신뢰를 악용하는 프로토콜

SS7와 Diameter는 이동통신망에서 기지국, 교환기, 홈 위치 레지스트리(HLR/HSS) 등 네트워크 장비들이 서로 통신하기 위해 사용하는 신호 프로토콜(Signaling Protocol)입니다. 이 프로토콜의 설계 철학은 "네트워크 내의 모든 노드는 신뢰할 수 있다"는 가정하에 만들어졌습니다. 즉, 통신사 A가 통신사 B에게 "이 번호의 사용자 위치를 알려달라"고 요청하면, B는 A가 정당한 통신사인지 확인하는 절차 없이 즉시 응답합니다.

이러한 '신뢰 기반 모델'은 글로벌 로밍 환경에서 필수적이지만, 공격자에게는 치명적인 허점입니다. 유령 회사는 법적으로 등록된 통신 사업자(또는 MVNO) 형태를 갖추고 로밍 허브(Roaming Hub)나 클리어링하우스와 계약을 맺습니다. 이 과정에서 복잡한 국가 간 절차와 자본 검증 과정을 교묘히 피하거나 규제가 허술한 국가를 이용해 접속 권한을 획득합니다.

### 2. 공격 시나리오: 유령 회사의 위치 추적 흐름

유령 회사가 사용자를 추적하는 과정은 매우 간단하면서도 파괴적입니다. 공격자는 자신이 소유한 SS7/Diameter 노드에서 타겟 번호에 대한 정보를 요청하는 메시지를 생성합니다. 이때 주로 사용되는 메시지는 `Send Routing Info For SM`(SMS 라우팅 정보 요청)입니다. SMS를 보내기 위해 수신자의 위치(MSC/VLR)를 물어보는 것으로 위장하여, 응답으로 오는 '셀 ID(Cell ID)'나 '위치 영역(LAI)' 정보를 추출하는 방식입니다.

다음은 이 공격 흐름을 시각화한 다이어그램입니다.

```javascript
graph TD
    A[Attacker System] --> B[Ghost Telecom Node]
    B --> C[Global Roaming Hub]
    C --> D[Victims Home Network HLR/HSS]
    D --> E[Visited Network MSC/VLR]
    E --> F[Target Mobile Device]
    F --> E
    E --> D
    D --> C
    C --> B
    B --> A
```

1.  **Attacker System**: 공격자가 타겟의 전화번호를 입력하여 추적을 명령합니다.
2.  **Ghost Telecom Node**: 유령 통신 노드가 요청을 가로채거나 직접 생성하여 Global Roaming Hub로 전송합니다.
3.  **Global Roaming Hub**: 메시지의 발신자(Ghost Telecom)가 등록된 사업자이므로 이를 정상 라우팅하여 타겟의 소속국(HLR)으로 전달합니다.
4.  **Victims Home Network (HLR/HSS)**: 타겟의 현재 위치를 담당하는 교환국(MSC/VLR)에 위치 질의를 합니다.
5.  **Visited Network (MSC/VLR)**: 타겟 단말기가 접속된 기지국의 셀 ID(Global Cell ID)를 포함한 정보를 응답합니다.
6.  **Data Return**: 이 정보는 역순으로 전달되어 공격자에게 도달합니다. 공격자는 셀 ID를 지도 데이터와 매핑하여 실제 좌표를 복원합니다.

### 3. 분석: SS7 대 Diameter 프로토콜

과거의 감시 도구들이 주로 SS7에 집중했다면, 최근의 공격들은 4G/LTE 및 5G 네트워크에서 사용되는 Diameter 프로토콜로 확장되었습니다. 두 프로토콜의 차이와 악용 포인트를 비교하여 살펴보겠습니다.

| 특성 | SS7 (2G/3G) | Diameter (4G/5G) |
| :--- | :--- | :--- |
| **기반 전송 계층** | SCCP/MTP (TDM 기반) | TCP/SCTP (IP 기반) |
| **주요 악용 메시지** | `SRI_FOR_SM`, `ATI` | `Diameter-Location-Info`, `UDR` |
| **신뢰 모델** | Global Title 기반의 오픈 트러스트 | Peer-to-Peer 인증 (TLS 등이 적용되나 설정 미흡) |
| **추적 정확도** | 셀 ID (LAC + CI) 기반, 오차 범위 넓음 | 더 정밀한 TA (Tracking Area) 및 eNodeB 정보 가능 |
| **탐지 난이도** | 상대적으로 낮음 (레거시 트래픽) | 높음 (대량의 정상 4G/5G 트래픽에 섞임) |

Diameter는 보안성을 강화하기 위해 IPsec이나 TLS를 사용할 수 있도록 설계되었으나, 실제 현장에서는 호환성 문제와 성능 이슈로 인해 암호화가 제대로 적용되지 않는 경우가 빈번합니다. 공격자는 이러한 설정 미흡(Configuration Gap)을 악용합니다.

### 4. PoC 개념 증명: Python을 이용한 요청 시뮬레이션

실제 환경에서는 전용 하드웨어나 `Sigtran` 스택이 필요하지만, 공격의 논리를 이해하기 위해 Python으로 **가상의 Diameter 메시지 구조**를 시뮬레이션해 보겠습니다. 이 코드는 방어자 입장에서 어떤 패턴이 들어오는지 이해하는 데 목적이 있습니다.

아래 코드는 악의적인 노드가 사용자의 위치 정보를 요청하는 `User-Data-Request(UDR)` 메시지의 헤더와 AVP(Attribute-Value Pairs) 구성을 단순화한 것입니다.

```python
#!/usr/bin/env python3
# 이 코드는 위치 추적 공격의 원리를 이해하기 위한 교육용 시뮬레이션입니다.
# 실제 통신망 접근 시에는 Wireshark 등으로 패킷 캡처 후 분석이 필요합니다.

import struct
import binascii

class DiameterAVP:
    def __init__(self, code, vendor_id, flags, data):
        self.code = code
        self.vendor_id = vendor_id
        self.flags = flags
        self.data = data

    def encode(self):
        # AVP Header: Code(4) + Flags(1) + Length(3)
        # Vendor-Specific bit 플래그 확인
        header = struct.pack("!I B", self.code, self.flags)
        length = 12 + len(self.data) # Header(8) + VendorID(4, if present) + Data
        
        if self.vendor_id > 0:
            length += 4
            length_field = struct.pack("!I", length)
            payload = header + length_field[:3] + struct.pack("!I", self.vendor_id) + self.data
        else:
            length_field = struct.pack("!I", length)
            payload = header + length_field[:3] + self.data
        
        return payload

def create_malicious_location_request():
    """
    공격자 노드에서 생성할 수 있는 위치 추적 요청 메시지 시뮬레이션
    예: User-Data-Request (UDR) 또는 Location-Info-Request
    """
    
    # Session-ID (공격자 세션 식별자
```

---

**출처**: [https://news.hada.io/topic?id=28850](https://news.hada.io/topic?id=28850)