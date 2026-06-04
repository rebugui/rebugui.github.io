---
title: "SystemBC C2 분석: 젠틀멘 랜섬웨어 공격 규모 실체"
date: 2026-04-30T01:07:32+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 서론

침투 테스트 현장에서 가장 악몽 같은 순간은 언제일까요? 방화벽이 뚫리고, 랜섬웨어가 실행되어 파일이 암호화되는 그 순간일까요? 경험상 보안 팀에게 더 큰 공포는 '침묵'입니다. 시스템이 평화로워 보이지만, 실제로는 공격자가 내부 네트워크를 유린하며 제멋대로 통신을 취하는 '숨겨진 터널'이 존재할 때가 가장 위험합니다.

최근 '젠틀멘(The Gentlemen)'이라는 이름의 랜섬웨어 조직이 큰 주목을 받았습니다. 단순히 암호화 기술이 뛰어나서가 아닙니다. 이들의 공격 규모가 드러난 배경에는 그들이 애용하는 C2(Command & Control) 도구인 'SystemBC'의 서버 데이터가 유출되었기 때문입니다. 분석 결과, 단일 C2 서버만으로도 무려 1,570명 이상의 피해자가 관리되고 있었다는 사실이 밝혀졌습니다.

이번 사태는 우리에게 중요한 질문을 던집니다. "우리의 보안 장비가 지금도 공격자의 프록시 서버처럼 사용되고 있지는 않은가?" SystemBC는 마치 조용한 하인처럼 작동하여 공격자의 트래픽을 정상 트래픽으로 위장합니다. 이 글에서는 유출된 데이터를 바탕으로 SystemBC의 작동 원리를 분석하고, 보안 팀이 실제로 사용할 수 있는 탐지 및 대응 전략을 다루고자 합니다.

⚠️ **윤리적 경고**: 본문에 포함된 기술적 분석 및 코드 예시는 오직 방어 목적과 시스템 취약점 이해를 위한 학습용으로만 제공됩니다. 악용은 엄격히 금지됩니다.

## SystemBC의 작동 원리와 공격 시나리오

### 공격 흐름의 이해

SystemBC는 단순한 원격 제어 도구가 아닌, 공격자가 피해자 네트워크 내부로 진입하기 위한 '프록시 봇'입니다. 주로 스파이웨어(Spyware) 배포나 초기 접근 후 설치되며, 피해자 PC를 공격자의 소켓(Socket)처럼 사용합니다.

젠틀멘 랜섬웨어 조직은 SystemBC를 이용해 다음과 같은 킬체인(Kill Chain)을 구성합니다.

```javascript
graph LR
    A[피싱 이메일 / 익스플로잇] --> B[SystemBC 다운로드 및 설치]
    B --> C[C2 서버 핸드셰이크]
    C --> D[SOCKS 프록시 터널 생성]
    D --> E[정찰 및 Lateral Movement]
    E --> F[랜섬웨어 실행]
```

위 다이어그램에서 볼 수 있듯이, SystemBC는 랜섬웨어 실행 직전까지의 '교통정리'를 담당합니다. 공격자는 SystemBC가 생성한 터널을 통해 피해자의 내부 네트워크를 자신의 로컬 네트워크처럼 탐색하며, 중요한 자산을 찾아내고 랜섬웨어를 배포합니다.

### 기술적 심층 분석: 통신 프로토콜

SystemBC의 가장 큰 위협 요소는 그 은밀성에 있습니다. 이 악성코드는 일반적으로 HTTP 또는 HTTPS 프로토콜을 사용하여 C2 서버와 통신합니다. 겉보기에는 일반적인 웹 브라우징처럼 보이지만, 내부적으로는 공격자의 명령을 기다리거나 탈취한 데이터를 전송합니다.

특히 이번 유출 사건에서 분석된 C2 서버의 트래픽 패턴을 보면, SystemBC는 특정한 User-Agent 문자열과 고정된 URI 패턴을 사용하는 경향이 있습니다. 이는 네트워크 기반 탐지(NIDS)를 위한 결정적인 단서가 됩니다.

다음은 SystemBC와 같은 C2 트래픽이 일반 트래픽과 어떻게 다른지 비교한 테이블입니다.

| 비교 항목 | 정상 웹 트래픽 | SystemBC 의심 트래픽 |
| :--- | :--- | :--- |
| **User-Agent** | 표준 브라우저 (Chrome, Firefox 등) | 비표준 또는 변형된 문자열 |
| **통신 간격** | 사용자 행동에 따른 불규칙한 패턴 | 주기적인 Heartbeat (주기 고정) |
| **URI 패턴** | 다양하고 페이지별 상이함 | 특정 디렉터리에 대한 반복적인 요청 |
| **전송 데이터** | HTML, 이미지, 스크립트 등 | 암호화된 페이로드 또는 Base64 데이터 |
| **지속성** | 세션 종료 시 연결 해제 | 장시간 연결 유지 및 재시도 시도 짧음 |

## 탐지 및 대응을 위한 실무 가이드

### Step-by-step: 네트워크 로그 분석 및 탐지

이제 실제 보안 엔지니어가 유출된 IoC(Indicators of Compromise) 정보를 활용하여 자사 네트워크 내 SystemBC 감염 여부를 확인하는 절차를 살펴보겠습니다.

**1단계: 관련 IoC 수집** 보안 업체가 공개한 SystemBC C2 서버의 IP 목록과 도메인 목록, 그리고 악성코드에서 사용하는 특정 해시 값을 확보합니다.

**2단계: 방화벽 및 프록시 로그 조회** SIEM(Security Information and Event Management) 시스템이나 방화벽 로그에서 확보된 IP나 도메인으로의 접속 시도를 쿼리합니다. `dst_ip IN ( malicious_ips )` 조건으로 필터링합니다.

**3단계: 패턴 기반 탐지** 특정 IP를 못 잡더라도 통신 패턴이 의심스러운 연결을 찾아야 합니다. 예를 들어, 비정상적인 User-Agent를 사용하거나, 짧은 간격으로 반복되는 작은 크기의 POST 요청을 탐지합니다.

**4단계: 호스트 분석 (Endpoint Forensics)** 네트워크 탐지가 확인되면 해당 내부 IP를 사용하는 호스트에서 이상 프로세스가 실행 중인지 확인합니다. SystemBC는 종종 `svchost.exe`나 `rundll32.exe`와 같은 윈도우 시스템 프로세스 이름을 위장하거나, 유효한 디지털 서명이 없는 실행 파일을 생성합니다.

### PoC: 탐지를 위한 Python 스크립트

학습 및 방어 목적으로, 로그 파일을 분석하여 SystemBC와 유사한 특징을 가지는 트래픽을 식별하는 간단한 Python 스크립트를 작성해 보겠습니다. 이 스크립트는 사용자 정의 User-Agent와 비정상적인 빈도로 발생하는 연결을 탐지합니다.

```python
import re
from collections import defaultdict

# 가상의 악성 User-Agent 패턴 (실제 분석된 IoC 기반 설정)
MALICIOUS_UA_PATTERNS = [
    r"Mozilla/5\.0 \(compatible; Bot/1\.0\)",
    r"Python-urllib/3\.9",
    r"CustomAgent/1\.0"
]

# 로그 파싱 및 분석 함수
def analyze_logs(log_file_path):
    connection_counts = defaultdict(int)
    suspicious_entries = []

    try:
        with open(log_file_path, 'r') as f:
            for line in f:
                # 로그 형식: [TIMESTAMP] SRC_IP DST_IP USER_AGENT
                # 실제 환경에 맞게 파싱 로직 수정 필요
                parts = line.strip().split()
                if len(parts) < 4:
                    continue
                
                src_ip = parts[1]
                user_agent = parts[3]
                
                # 의심스러운 User-Agent 패턴 매칭
                for pattern in MALICIOUS_UA_PATTERNS:
                    if re.search(pattern, user_agent):
                        suspicious_entries.append(line)
                        connection_counts[src_ip] += 1
                        break
                        
    except FileNotFoundError:
        print("파일을 찾을 수 없습니다.")
        return

    # 결과 출력
    print("--- 탐지 결과 ---")
    if not suspicious_entries:
        print("감염 의심 트래픽이 없습니다.")
    else:
        print(f"총 {len(suspicious_entries)}건의 의심스러운 로그가 탐지되었습니다.")
        print("상위 발생 IP:")
        for ip, count in sorted(connection_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"- {ip}: {count}회")
        
        print("
상세 로그 (
```

---

**출처**: [https://news.google.com/rss/articles/CBMihAFBVV95cUxNRy1Benh3RDFCTzJqY0pXOEJxX01OSWh2Nmtqc2V4aHRUYVIxdGZqbmtPVWxGOElfZFA3OTVVaGxpeU5DS0t3MDZjSGJIUVI1Y3h5SURCbWI4ck1nWjZ3SGtOeWNzLW43S3p2N1VleEotRjN5RjNDM2NLLTIzeHRXbXZESGU?oc=5](https://news.google.com/rss/articles/CBMihAFBVV95cUxNRy1Benh3RDFCTzJqY0pXOEJxX01OSWh2Nmtqc2V4aHRUYVIxdGZqbmtPVWxGOElfZFA3OTVVaGxpeU5DS0t3MDZjSGJIUVI1Y3h5SURCbWI4ck1nWjZ3SGtOeWNzLW43S3p2N1VleEotRjN5RjNDM2NLLTIzeHRXbXZESGU?oc=5)