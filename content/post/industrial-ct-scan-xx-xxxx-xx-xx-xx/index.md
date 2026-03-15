---
title: "📸 Industrial CT Scan: 헬스 웨어러블 내부 구조 분석"
date: 2026-03-15T20:55:17+09:00
draft: false
tags:
  - "Hardware Security"
  - "Teardown"
  - "CT Scan"
  - "IoT"
  - "Reverse Engineering"
categories:
  - "보안"
---


## 서론

보안 컨설퍼런스나 CTF(해킹 방어 대회) 현장에서 흔히 볼 수 있는 장면은 하나같습니다. 화려한 웹 해킹이나 SQL 인젝션 시연이 끝나고 나면, 누군가는 반드시 "근데 이 물리적인 기기 자체는 어떻게 뜯어볼 생각인가요?"라고 묻습니다. 특히 의료용 IoT 기기나 웨어러블 기기의 경우, 이 물리적 접근이 곧 생명과 직결되는 보안 위협이 되기도 합니다.
최근 한 병원의 네트워크에서 의심스러운 트래픽이 포착되었습니다. 당시 사용된 당뇨 관리 기기가 외부 서버와 비정상적인 통신을 시도한 것이었죠. 보안 팀은 소프트웨어적 분석만으로는 원인을 찾을 수 없었고, 결국 기기 자체를 분석하기로 결정했습니다. 하지만 기기는 작고 밀봉이 견고했으며, 물리적으로 파괴하면 펌웨어를 추출할 UART나 JTAG 포인트를 영구적으로 잃을 위험이 있었습니다.
이 시나리오는 하드웨어 보안 엔지니어에게 "어떻게 기기를 부수지 않고 내부를 볼 것인가?"라는 근원적인 질문을 던집니다. 우리는 기존의 드라이버와 렌치를 든 티어다운(Teardown) 방식에서 벗어나, 의료용으로도 사용되는 고해상도 **Industrial CT Scan(산업용 전산화 단층 촬영)** 기술을 하드웨어 리버스 엔지니어링에 도입해야 합니다. 이 글에서는 Oura Ring, Dexcom G7 같은 첨단 웨어러블 기기를 CT 스캔으로 비파괴 분석하여, 하드웨어 설계 구조와 잠재적 보안 취약점을 어떻게 식별하는지 현장 감각 있게 다루겠습니다.
*(참고: 본 문서에서 다루는 모든 하드웨어 분석 기술과 공격 시나리오는 방어 목적의 연구이며, 무단 도해 및 악용을 엄격히 금지합니다.)*

## 본론


### 하드웨어 리버스 엔지니어링의 패러다임: 비파괴 검사

전통적인 하드웨어 분석은 드릴과 열전대 gun을 든 물리적 공격이었습니다. 기기의 케이스를 강제로 개봉하고, PCB를 들어 올려야 배선을 볼 수 있었죠. 하지만 Oura Ring이나 Dexcom G7과 같은 초소형 의료 기기는 실리콘으로 충전(Potting)되거나 워터프루프 처리가 되어 있어 물리적 분해가 거의 불가능합니다. 이때 등장하는 것이 Industrial CT Scan입니다.
CT 스캔은 X선을 이용해 기기 내부의 단면을 이미지화하는 기술입니다. 이를 3D로 재구성하면 기기를 열지 않고도 내부의 칩 배치, 배선 경로, 심지어 볼드(ball) 납땜 상태까지 육안으로 확인할 수 있습니다. 보안 관점에서 이는 게임 체인저입니다. 외부에서 접근 가능한 테스트 포인트(Test Point)나 디버그 핀의 위치를 정확히 파악한 뒤, 정밀 드릴링을 시도하여 드릴이 실제 회로를 건드리지 않고 목표 핀에 도달할 수 있게 해주기 때문입니다.
이러한 비파괴 분석 과정을 시각화하면 다음과 같습니다.

```javascript
graph LR
    A[Target Device] --> B[Industrial CT Scan]
    B --> C[3D Volumetric Data]
    C --> D[PCB Layer Separation]
    D --> E[Component Identification]
    E --> F[Test Point Mapping]
    F --> G[Precision Drilling Access]
    G --> H[Bus Sniffing / Glitching]
```


### 기술적 심층 분석: CT 데이터 처리와 취약점 탐지

CT 스캔을 통해 얻은 원본 데이터(DICOM 또는 Voxel 데이터)는 단순히 '사진'이 아닙니다. 이는 3D 형상 정보를 담고 있어, 특정 칩셋의 정확한 좌표와 회로 기판 적층 구조를 분석할 수 있습니다. 보안 연구원은 이 데이터를 통해 공격자가 노릴 수 있는 표면(Attack Surface)을 식별합니다.
가장 흔한 취약점은 **활성화된 디버그 포트(Debug Port)**입니다. 제조사는 펌웨어 업데이트나 초기 불량 검사를 위해 UART, JTAG, SWD 등의 디버그 인터페이스를 PCB에 남겨두곤 합니다. CT 스캔 이미지를 분석하여 메인 MCU와 연결된 미사용 패드를 찾아내고, 그 좌표를 기반으로 정밀 시추 작업을 진행하면 펌웨어 덤프가 가능해집니다.
아래는 CT 스캔 분석을 통해 식별된 칩셋의 모델명과 위치 정보를 바탕으로, 해당 칩셋의 알려진 취약점(CVE)을 크로스 체크하는 간단한 자동화 스크립트 예시입니다.

```python
import requests

# CT 스캔 및 시각적 분석을 통해 식별된 부품 리스트 (예시)
# 실제 시나리오에서는 이미지 분석 AI를 통해 추출될 수 있음
identified_components = [
    {"name": "Nordic nRF52832", "role": "Main MCU", "coords": (12.5, 8.2)},
    {"name": "Cypress CY8C4014", "role": "Power Management", "coords": (15.1, 5.5)},
    {"name": "Unknown 8-pin SOIC", "role": "Secure Element?", "coords": (10.2, 9.0)}
]

def check_cve(component_name):
    # (주의) 실제 사용 시에는 공식 CVE 데이터베이스나 NVD API를 사용하세요.
    # 여기서는 예시를 위해 Mock API를 가정합니다.
    print(f"[*] Checking vulnerabilities for: {component_name}...")
    
    # 가상의 취약점 데이터베이스 응답 시뮬레이션
    vuln_db = {
        "Nordic nRF52832": "CVE-2020-XXXX: BLE stack heap overflow allows DoS.",
        "Cypress CY8C4014": "No critical CVEs found."
    }
    
    return vuln_db.get(component_name, "No known vulnerabilities or unrecognized chip.")

def analyze_hardware_security(components):
    report = []
    for comp in components:
        cve_info = check_cve(comp["name"])
        risk_level = "HIGH" if "CVE" in cve_info else "LOW"
        
        report.append({
            "Component": comp["name"],
            "Role": comp["role"],
            "Location": comp["coords"],
            "Risk": risk_level,
            "Details": cve_info
        })
    return report

# 분석 실행
security_report = analyze_hardware_security(identified_components)

# 결과 출력
for item in security_report:
    print(f"--------------------------------------------------")
    print(f"Component: {item['Component']} ({item['Role']})")
    print(f"Location  : {item['Location']}")
    print(f"Risk Level: {item['Risk']}")
    print(f"Analysis  : {item['Details']}")
```

이 코드는 단순히 문자열을 매칭하는 것이지만, 현장에서는 CT 스캔으로 얻은 칩 패키징 크기와 핀 배열을 기반으로 칩셋을 식별한 뒤, 해당 펌웨어 버전과 맵핑하여 실제 익스플로잇(Exploit) 가능성을 검증하는 단계로 확장됩니다.

### 분석 방식 비교: Physical Teardown vs. CT Scan

CT 스캔 기술이 기존 방식과 비교하여 보안 분석 측면에서 어떤 이점을 가지는지 명확히 이해해야 합니다.
| 비교 항목 | Physical Teardown (물리적 해체) | Industrial CT Scan (비파괴 스캔) | | :--- | :--- | :--- | | **파괴 여부** | 파괴적 (Irreversible) | 비파괴적 (Non-destructive) | | **분석 시간** | 느림 (정밀 작업 시간 소요) | 빠름 (스캔 후 3D 렌더링) | | **내부 시야** | 제한적 (IC 아래, 레이어 내부 불가) | 전방위 (IC 본딩 와이어, 내부 배선 가능) | | **정밀도** | 낮음 (미세 부품 손실 위험) | 매우 높음 (마이크론 단위 측정) | | **보안 분석 적합성** | 낮음 (증거 훼손 가능성) | 높음 (정확한 좌표 기반 액세스) |

### Step-by-Step 가이드: 웨어러블 기기 하드웨어 보안 점검

실제 현장에서 Dexcom G7이나 Oura Ring과 같은 의료 웨어러블을 입수했을 때, 보안 연구원이 수행하는 표준 절차를 정리합니다.
1.  **초기 스캔 및 표면 조사**     기기 외형을 육안으로 확인하고 모델 번호, FCC ID 등을 기록합니다. 이를 통해 사용 가능한 무선 주파수 대역과 공개 문서(테스트 리포트 등)를 수집합니다.
2.  **Industrial CT 스캔 실행**     기기를 CT 스캔너 내부에 고정합니다. 배터리가 내장된 경우, 폭발이나 발화 위험이 없도록 X선 조사 조건을 세심하게 설정해야 합니다. 고해상도 스캔을 통해 내부 구조를 Voxel 데이터로 확보합니다.
3.  **3D 모델링 및 PCB 분리**     수집된 데이터를 분석 소프트웨어(예: VGStudio, DragonFly)로 불러와 3D 모델을 재구성합니다. 'Thresholding' 기능을 통해 밀도 차이를 이용해 PCB 구리선, 플라스틱 케이스, 배터리, 실리콘 몰딩을 레이어별로 분리합니다.
4.  **보안 핵심 포인트 식별**     PCB 레이어를 확대하여 메인 MCU 근처의 패드를 분석합니다.     *   TX/RX 라인 추적: 직렬 통신 포트 식별     *   TCK/TMS/TDI/TDO 라인 추적: JTAG 포트 식별     *   VCC/GND 라인 확인: 전력 분석 채널 확보
5.  **정밀 시추 및 측정 (Precision Drilling & Probing)**     CT 스캔으로 확보한 좌표값을 CNC 머신이나 수동 마이크로 포지셔너에 입력합니다. 정확한 위치에 0.1mm 수준의 미세 드릴 구멍을 뚫어 내부 패드로 프로브(Probe)를 연결합니다.
6.  **인터페이스 연결 및 데이터 획득**     식별된 UART나 JTAG 인터페이스를 통해 논리 분석기(Logic Analyzer)나 디버거를 연결합니다. 부팅 로그를 캡처하거나 펌웨어 이미지를 덤프하여 소프트웨어적 취약점 분석을 진행합니다.

## 결론

웨어러블 기기와 의료용 IoT는 단순한 전자 기기를 넘어 사용자의 생체 정보를 다루는 민감한 플랫폼입니다. 우리는 소프트웨어 보안에만 집중하다가, 가장 기본적인 하드웨어 계층에서의 방어가 허술하다는 사실을 간과해서는 안 됩니다.
이번 포스팅에서 살펴본 Industrial CT Scan을 활용한 분석은 기기를 부수지 않고 내부의 설계 의도와 숨겨진 디버그 포인트를 찾아내는 가장 강력한 방법론입니다. Oura Ring이나 Dexcom G7 같은 기기들이 밀봉 설계를 통해 물리적 접근을 어렵게 만들려고 할수록, 우리는 투명한 X선 시야로 그들의 설계 흐름을 읽어내고 보안 허점을 찾아내야 합니다.
결국 하드웨어 보안의 핵심은 **"보이지 않는 것을 보이게 만드는 능력"**입니다. CT 스캔 기술은 연구원에게 그런 초능력을 부여합니다. 의료 기기 제조사들 역시 이러한 비파괴 분석 기술이 공격자들에게도 사용될 수 있음을 인지하고, 디버그 포트를 생산 단계에서 물리적으로 차단하거나, 칩 내부의 보안 부트(Secure Boot)와 암호화 강도를 높이는 등의 방어적 설계(Defense-in-Depth)를 적용해야 합니다.
**참고자료 및 링크**
- [Hada.io - 헬스 웨어러블 기기의 CT 스캔](https://news.hada.io/topic?id=27293)
- [Industrial CT Scanning in Electronics Failure Analysis](https://www.jenoptik.com)
- [Hardware Hacking Resources for IoT Security](https://github.com/hardware-hacking)
