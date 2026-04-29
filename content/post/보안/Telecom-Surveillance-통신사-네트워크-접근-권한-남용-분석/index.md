---
title: "Telecom Surveillance: 통신사 네트워크 접근 권한 남용 분석"
date: 2026-04-30T01:07:27+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 서론

휴대폰을 꺼두거나 비행기 모드로 설정하지 않은 이상, 당신의 스마트폰은 수분마다 통신사에게 "나는 여기 있소"라고 신호를 보냅니다. 이는 통신 연결을 유지하기 위한 네트워크의 기본적인 생존 본능입니다. 그런데 만약 이 정상적인 신호를 가로채는 사람이 단순한 해커가 아니라, 통신사의 핵심 망에 접근 권한을 가진, 혹은 그 권한을 위장한 민간 감시 업체(Surveillance Vendor)라면 어떨까요?

최대 익명성과 보안을 요구하는 활동가나 언론인이 자신의 위치가 노출되었다는 사실을 알게 되는 방법은 악성앱을 다운로드했을 때가 아닙니다. 그들은 자신의 단말기가 완벽하다고 믿고 있지만, 정작 통신사 내부의 데이터베이스에서 자신의 실시간 위치가 유출되고 있다는 사실을 전혀 알지 못합니다. 시티즌랩(Citizen Lab)이 최근 발표한 조사에 따르면, 전 세계적으로 적어도 두 건의 정교한 통신 감시 캠페인이 확인되었습니다. 이번 글에서는 단말기 해킹이 아닌, **통신 인프라 자체를 타겟으로 한 Telecom Surveillance** 공격이 어떻게 이루어지는지, 그 기술적 원리와 방어 전략을 심층적으로 분석하겠습니다.

## 본론

### 1. 통신 감시의 기술적 배경: SS7과 Diameter 프로토콜의 약점

이 공격의 핵심은 사용자의 스마트폰 OS나 앱의 취약점이 아닙니다. 바로 통신사들이 서로 통신하기 위해 사용하는 **신호망(Signaling Network)** 프로토콜인 SS7(Signaling System No.7)과 그 후속인 Diameter의 취약점을 악용합니다.

일반적으로 이동통신망에서 단말기의 위치를 파악하기 위해 사용자는 HLR(Home Location Register)이나 HSS(Home Subscriber Server)라는 중앙 데이터베이스를 조회합니다. 정상적인 절차에서는 로밍 중인 사용자를 찾기 위해 방문 통신사(VLR)와 홈 통신사(HLR) 간에 인증된 메시지가 오갑니다. 하지만 공격자는 이 프로토콜의 '신뢰'를 악용하여, 마치 자신이 정당한 통신사인 것처럼 가장하고 타겟의 위치 정보를 요청합니다.
- **주요 공격 벡터**: `Send Routing Info for SM` (SRI4SM) 요청 위조
- **타겟**: 홈 위치 레지스터(HLR/HSS)
- **결과**: 타겟 단말기가 현재 속해 있는 교환기(MSC) 및 셀 ID(Cell ID) 획득
> **⚠️ 윤리적 경고**: 아래 설명되는 기술 내용은 통신 인프라의 취약점을 이해하고 방어 목적으로만 사용해야 합니다. 승인되지 않은 시스템에 대한 접근 시도는 불법이며 엄중한 처벌을 받을 수 있습니다.

### 2. 공격 시나리오 시각화

다음은 공격자가 통신사 네트워크의 신뢰 관계를 악용하여 타겟의 위치를 추적하는 흐름도입니다.

```javascript
graph LR
    A[Target User] --> B[Visited Network VLR]
    B --> C[Home Network HLR]
    D[Surveillance Vendor] --> E[Signaling Gateway]
    E -->|Fake SRI4SM Request| C
    C -->|Location Data MSC Cell ID| E
    E --> D
```

이 다이어그램에서 볼 수 있듯이, 공격자(D)는 타겟의 단말기(A)를 직접 해킹하지 않습니다. 대신 글로벌 신호망에 연결된 게이트웨이(E)를 통해 홈 네트워크의 데이터베이스(C)에 직접 질의를 던집니다. 통신사 간의 로밍 협정(Roaming Agreement)에 기반한 막대한 양의 신뢰가 있기 때문에, 이 질의가 외부에서 온 악의적인 요청인지 식별하기 어렵습니다.

### 3. 정상 트래픽 vs 감시 공격 트래픽 비교

보안 담당자가 로그를 분석할 때 의심해야 할 패턴을 파악하기 위해, 정상적인 로밍 절차와 감시 공격의 차이를 비교해 보겠습니다.

| 구분 | 정상적인 로밍/호 처리 | 감시 공격 (Surveillance) | | :--- | :--- | :--- | | **요청 출발지** | 인증된 통신사의 GT (Global Title) | 위조된 GT, 승인되지 않은 서버 IP | | **요청 빈도** | 통화/문자 발생 시 또는 위치 등록 주기에 맞춰 발생 | **타겟의 실시간 추적을 위해 비정상적으로 잦음** | | **응답 데이터** | 해당 MSC 주소 및 라우팅 정보만 사용 | **MSC 주소, Cell ID, IMEI 등 상세 위치 정보 수집** | | **후속 행동** | 실제 음성 호 또는 SMS 연결 | **데이터 수집 후 연결 종료 (Silent Logging)** |

### 4. 탐지 및 분석을 위한 PoC 코드 (Python)

실제 통신망 환경에서는 Wireshark나 전용 프로토콜 분석기를 사용하지만, 여기서는 방어자의 관점에서 **SS7/Diameter 방화벽 로그**를 분석하여 의심스러운 위치 추적 시도를 탐지하는 Python 스크립트의 개념을 증명(PoC)하겠습니다.

이 스크립트는 SRI4SM 요청 로그를 파싱하여, 단시간 내에 특정 IMSI(가입자 식별번호)에 대해 너무 많은 위치 질의가 들어오는지 감지합니다.

```python
import re
from collections import defaultdict
from datetime import datetime, timedelta

# 로그 파일에서 IMSI와 타임스탬프를 추출하는 정규식 예시 (실제 환경에
```

---

**출처**: [https://techcrunch.com/2026/04/23/surveillance-vendors-caught-abusing-access-to-telcos-to-track-peoples-phone-locations-researchers-say/](https://techcrunch.com/2026/04/23/surveillance-vendors-caught-abusing-access-to-telcos-to-track-peoples-phone-locations-researchers-say/)