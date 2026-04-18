---
title: "📡 Bluehood: 블루투스 신호를 통한 사용자 추적 분석"
date: 2026-04-19T08:06:39+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 서론

지하철역 플랫폼이나 붐비는 카페에 앉아 있다고 상상해 보십시오. 주변 수십 명의 낯선 사람들이 지나가고 있습니다. 휴대폰은 주머니 속에 깊숙이 들어있고, 화면은 꺼져 있습니다. 당신은 지금 완벽하게 익명이라고 느끼실 것입니다. 하지만 보안 전문가의 관점에서, 이 공간은 데이터의 홍수입니다. 당신을 포함한 대부분의 사람들의 기기는 초당 수차례씩 자신의 존재를 외침으로써 "나는 여기에 있고, 내 이름은 이것이며, 이전에 이곳에도 있었다"라고 방송하고 있기 때문입니다.

우리는 흔히 블루투스를 무선 이어폰이나 스마트워치를 연결하는 편리한 도구로만 생각합니다. 하지만 편리함의 이면에는 공격자가 악용할 수 있는 매우 날카로운 칼날이 숨어 있습니다. 최근 공개된 `Bluehood` 같은 도구는 단순히 주변 기기를 찾는 것을 넘어, 이러한 방송 신호(Broadcasting)를 수집하고 시각화하여 개인의 생활 패턴을 복원해 낼 수 있음을 보여줍니다.

이 글에서는 "단순히 블루투스를 켜둔 것만으로 내 위치가 추적될 수 있는가?"라는 질문에 대한 기술적 답변을 제시하고, Bluehood를 통해 어떻게 사용자의 프라이버시가 무너지는지, 그리고 우리는 이를 어떻게 방어해야 하는지 심층적으로 분석하겠습니다. 이는 단순한 이론적인 논의가 아니라, 실제 현장에서 발생할 수 있는 Physical Security 침해 시나리오입니다.

## 본론

### 기술적 배경: BLE Beaconing과 MAC Address 노출

현대의 스마트폰과 웨어러블 기기는 대부분 Bluetooth Low Energy (BLE)를 사용합니다. BLE 기기는 연결되지 않은 상태에서도 주변 기기를 탐색하거나 자신을 알리기 위해 'Advertising Packet'이라는 신호를 주기적으로 송신합니다. 문제는 이 패킷에 포함된 정보의 양과 지속성입니다.

가장 치명적인 요소는 MAC(Media Access Control) 주소입니다. 이는 네트워크 인터페이스의 고유 식별자로, 이론적으로는 변경 불가능해 보이지만, 소프트웨어적으로 랜덤화(Randomization)가 가능합니다. 하지만 많은 기기, 특히 특정 IoT 기기나 구형 OS를 사용하는 스마트폰은 고정된 MAC 주소를 사용하거나, 랜덤화 로직에 취약점이 있습니다. 공격자는 이 고유한 MAC 주소를 '마커(Marker)'로 사용하여, 특정 위치에서 이 MAC 주소를 포착한 시간과 장소를 기록함으로써 해당 기기 소유자의 동선을 추적할 수 있습니다.

#### 공격 시나리오: 타겟팅된 물리적 추적

보안 감사(Pentest) 상황을 가정해 보겠습니다. 기업의 임원이나 보안 담당자의 이동 경로를 파악하려는 악의적인 공격자(또는 경쟁사의 스파이)가 있습니다. 공격자는 타겟이 출퇴근하는 경로에 있는 지점(예: 카페, 엘리베이터 홀)에 Bluehood와 유사한 기능을 탑재한 작은 하드웨어(라즈베리 파이 등)를 설치하거나 배낭에 넣고 다닙니다.

공격자는 능동적으로 해킹을 시도할 필요가 없습니다. 그저 수동적으로 신호를 듣기만(Passive Sniffing) 하면 됩니다. 수집된 데이터는 시간대별로 MAC 주소가 어디서 포착되었는지 매핑됩니다. "MAC 주소 A:AM 8시에 지하철역, AM 9시에 회사 로비, PM 12시에 근처 식당." 이 데이터가 쌓이면, 누구인지 몰라도 이 MAC 주소의 주인이 '이 회사 직원'이고 '점심은 이 식당에서 먹는다'는 고도화된 정보가 도출됩니다.

다음은 Bluehood가 수행하는 스캐닝 및 추적 과정의 간략化的 데이터 흐름입니다.

```javascript
graph LR
    A[Target Device BLE On] -->|Broadcasting Packet| B[Scanner Bluehood]
    B -->|Extract MAC RSSI Name| C[Data Processing]
    C -->|Store Data| D[Database]
    D -->|Correlate Time Location| E[Visualization Dashboard]
```

### 실습: Python을 이용한 BLE 신호 분석 (PoC)

**윤리적 경고**: 아래 코드는 오직 방어 목적의 교육 및 연구용으로만 제공됩니다. 타인의 동의 없이 위치를 추적하는 것은 불법이며 윤리적으로 용납될 수 없습니다.

Bluehood의 핵심은 Python의 `bleak` 라이브러리나 `scapy`를 사용하여 주변 BLE 패킷을 캡처하고 분석하는 것입니다. 아래 예시는 주변 기기를 스캔하여 MAC 주소와 기기 이름(광고 패킷에 공개된 경우)을 수집하는 기본적인 PoC(Proof of Concept) 코드입니다.

```python
import asyncio
from bleak import BleakScanner

async def scan_devices():
    print("[*] Starting BLE Scan... (Press Ctrl+C to stop)")
    
    # 디바이스 발견 시 콜백 함수 정의
    def detection_callback(device, advertisement_data):
        # MAC 주소와 수신 신호 강도(RSSI) 출력
        # RSSI는 거리 추정의 척도가 됨 (값이 클수록 가까움)
        print(f"[+] Found: {device.name} | MAC: {device.address} | RSSI: {device.rssi} dB")

    # 스캐너 설정 및 실행
    scanner = BleakScanner(detection_callback=detection_callback)
    await scanner.start()
    
    # 무한 루프 유지 (실제 운영 시에는 특정 시간 동안만 수행)
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await scanner.stop()
        print("[*] Scan stopped.")

if __name__ == "__main__":
    asyncio.run(scan_devices())
```

이 코드를 실행하면 주변의 수많은 기기가 자신의 MAC 주소를 노출하고 있음을 확인할 수 있습니다. 특히 RSSI(Received Signal Strength Indicator) 값을 활용하면, 기기와의 거리를 대략적으로 계산하여 타겟이 접근하고 있는지 멀어지고 있는지까지 판별할 수 있습니다.

### 심층 분석: 고정 MAC vs 랜덤 MAC

모든 기기가 취약한 것은 아닙니다. 최신 스마트폰 OS(Apple iOS, Android)는 프라이버시 보호를 위해 MAC 주소 랜덤화 기능을 지원합니다. 하지만 이 기능이 완벽하지 않거나 의도적으로 비활성화된 경우도 존재합니다.

다음은 공격자 관점에서 MAC 주소 유형에 따른 추적 난이도를 비교한 표입니다.

| 비교 항목 | 고정 MAC (Static MAC) | 랜덤 MAC (Random MAC) | | :--- | :--- | :--- | | **추적 난이도** | 낮음 (쉬움) | 높음 (어려움) | | **식별 지속성** | 영구적 (기기마다 고유) | 일시적 (세션마다 변경) | | **주요 취약점** | 장기간 생활 패턴 파악 가능 | 연결 시도 시 MAC 고정화 현상 | | **대상 기기** | 저가형 IoT, 구형 폰, 설정 변경 없는 기기 | 최신 iOS/Android (설정에 따라 다름) | | **대응 전략** | MAC 주소 랜덤화 필수 활성화 | 주기적인 갱신 확인 필요 |

중요한 점은, 많은 기기가 랜덤 MAC을 사용하더라도 **연결(Connectability)**을 시도할 순간 원래의 고정 MAC 주소로 전환하거나, 랜덤 MAC 생성에 사용하는 시드(Seed) 값이 예측 가능한 경우가 있다는 것입니다. 공격자는 이러한 패턴을 분석하여 랜덤화가 되었더라도 동일한 기기임을 식별해 내는 '디지털 지문(Digital Fingerprinting)' 기법을 사용하기도 합니다.

### 완화 조치 및 대응 가이드

이러한 위협으로부터 개인정보를 보호하기 위해 사용자와 관리자는 다음과 같은 단계를 수행해야 합니다.

1.  **MAC 주소 랜덤화 강제 활성화**:     *   **Android**: 설정 > 연결 > Bluetooth > 블루투스 기기 이름/MAC 주소 > '비공개 기기 사용' 또는 '랜덤화' 활성화.     *   **iOS**: 기본적으로 활성화되어 있으나, 기업용 MDM(모바일 기기 관리) 프로필에 의해 비활성화될 수 있으므로 설정 확인 필요.

2.  **Bluetooth 끄기 (Off)**:     *   가장 확실한 방법입니다. 사용하지 않을 때는 Bluetooth를 꺼두십시오. 특히 공공장치나 민감한 구역에서는 필수적입니다.

3.  **앱 권한 제어**:     *   특정 앱이 굳이 Bluetooth 스캔 권한이 필요 없는데도 요구하는지 확인합니다. 위치 정보와 연동된 Bluetooth 스캔은 정교한 추적으로 이어질 수 있습니다.

4.  **기기 펌웨어 업데이트**:     *   제조사가 랜덤화 알고리즘의 결함을 수정했을 수 있으므로 최신 상태를 유지해야 합니다.

## 결론

Bluehood는 우리가 무심코 넘겨던블고 있던 블루투스 신호 하나가 가진 파괴력을 시각적으로 증명합니다. 이는 단순히 "기기가 보인다"는 수준을 넘어, "사람의 이동 경로가 보인다"는 심각한 프라이버시 침해로 이어질 수 있습니다. 사이버 보안의 핵심은 가상 공간에만 있는 것이 아니라, 우리가 매일 걷는 물리적 공간과 휴대하는 기기 사이의 경계선에 놓여 있습니다.

전문가로서의 인사이트를 덧붙이자면, 향후 보안 방향은 단순히 기술적인 '차단(Block)'에서 '인지(Awareness)'로 나아가야 합니다. 사용자는 자신의 기기가 어떤 데이터를 방송하고 있는지 알 권리가 있으며, 기술 개발자는 편의성을 위해 프라이버시를 타협하지 않는 'Privacy by Design' 원칙을 준수해야 합니다.

오늘 당장 휴대폰의 Bluetooth 설정을 한번쯤 확인해 보시는 것은 어떨까요? 끄는 것보다 더 강력한 보안은 없습니다.

### 참고자료
- [Bluehood GitHub Repository](https://github.com/example/bluehood) (도구 예시 링크)
- [Bluetooth Specification - Advertising Packets](https://www.bluetooth.com/specifications/)
- [Hada.io: 블루투스 기기가 당신에 대해 드러내는 것](https://news.hada.io/topic?id=26752)

---

**출처**: [https://news.hada.io/topic?id=26752](https://news.hada.io/topic?id=26752)