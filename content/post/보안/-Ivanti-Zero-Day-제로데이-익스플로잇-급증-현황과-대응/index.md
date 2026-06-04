---
title: "🚨 Ivanti Zero-Day: 제로데이 익스플로잇 급증 현황과 대응"
date: 2026-04-19T08:06:05+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 서론

SOC 상황실의 모니터에 붉은색 경보灯이 깜빡이고 있습니다. 평소와 다르지 않은 웹 트래픽처럼 보이지만, 정밀 분석 결과 이 트래픽은 내부 네트워크의 핵심 자산으로 향하고 있었습니다. 방화벽 로그에는 정상적인 관리자 세션으로 기록되었지만, 해당 시간대 실제 관리자는 퇴근한 상태였죠. 이것은 최근 Ivanti 제품군을 겨냥한 제로데이(Zero-Day) 공격이 보여주는 전형적인 모습입니다.

보안 전문가들 사이에서 가장 두려워하는 시나리오는 '알려지지 않은 취약점'이 '알려진 공격 도구'가 되는 순간입니다. 최근 보고서에 따르면, Ivanti의 엔터프라이즈 VPN 및 UEA 솔루션을 타깃으로 하는 제로데이 공격이 지난 7월부터 은밀하게, 그리고 지속적으로 이어져 왔음이 드러났습니다. 단순히 패치가 늦어진 문제가 아닙니다. 공격자들은 패치가 배포되기도 전에 이미 취약점을 weaponized(무기화)했으며, 수개월 동안 방어자의 레이더를 피해 침투 경로를 확보해 왔습니다. 왜 우리는 지금 이 Ivanti 제로데이 캠페인에 집중해야 할까요? 이 공격이 단순한 웹 해킹을 넘어, 기업의 경계를 무너뜨리고 횡적 이동(Lateral Movement)을 위한 발판을 제공하기 때문입니다.

## 본론

### 기술적 배경: 공격의 메커니즘
> ⚠️ **윤리적 경고**: 본 섹션에서 설명하는 기술적 세부사항 및 공격 벡터는 보안 연구 및 방어 목적(Defensive Purpose)으로만 제공됩니다. 승인되지 않은 시스템에서의 테스트는 불법이며 엄격히 금지됩니다.

Ivanti 제품군(주로 Connect Secure, Policy Secure 등)은 기업의 네트워크 경계에서 중요한 역할을 합니다. 이번 공격 캠페인의 핵심은 웹 인터페이스의 취약점을 악용한 **인증 우회(Authentication Bypass)**와 **원격 코드 실행(RCE)**입니다.

공격자는 먼저 인터넷에 노출된 Ivanti 장비의 특정 엔드포인트를 스캔합니다. 7월부터 시작된 이 공격은 초기에는 탐지를 피하기 위해 매우 느린 속도로 진행되었으나, 최근 들어 익스플로잇 시도가 급증하고 있습니다. 취약점의 원리는 대개 사용자 입력 값이 검증되지 않고 시스템 명령어로 전달되거나, 세션 관리 로직의 결함을 이용해 관리자 권한을 탈취하는 방식입니다.

다음은 이번 공격 캠페인의 일반적인 흐름을 도식화한 것입니다.

```javascript
graph LR
    A[공격자] --> B[정찰 및 스캔]
    B --> C[취약점 익스플로잇 요청 전송]
    C --> D[인증 우회 및 세션 하이재킹]
    D --> E[웹 쉘 업로드]
    E --> F[백도어 설치 및 지속성 확보]
    F --> G[내부 네트워크 횡적 이동]
```

### 침해 징후(IoC) 분석 및 탐지

이 공격의 악명 높은 점은 공격자가 공식 패치가 배포되기 전인 7월부터 활동했기 때문에, 과거 로그를 분석하지 않으면 이미 먹힌(Compromised) 시스템을 놓치기 쉽다는 것입니다. 특히 Ivanti 장비의 로그에서 정상적인 관리자 활동으로 위장된 특정 패턴을 찾아내야 합니다.

다음은 실제 현장에서 탐지해야 할 주요 IoC(Indicators of Compromise) 비교표입니다.

| 구분 | 정상 트래픽 | 의심스러운 활동 (익스플로잇 징후) |
| :--- | :--- | :--- |
| **User-Agent** | Mozilla/5.0 (일반 브라우저) | python-requests/2.x, 특수하게 조작된 문자열 |
| **요청 URI** | /dana-na/auth/, /dana-cached/ | /api/v1/..., /cgi-bin/, /por/login_config.lua 등 비정상적 경로 |
| **응답 크기** | 가변적 (보통 10KB 이상) | 매우 작음 (200 Byte 미만) 또는 고정된 패턴 |
| **요청 시간** | 업무 시간 대集中 | 불규칙적이거나 새벽 시간대 다수 발생 |

### 실무 대응: 로그 분석 자동화 스크립트

방어자는 수동으로 로그를 확인하는 것 외에, 자동화된 도구를 통해 의심스러운 요청을 필터링해야 합니다. 아래는 Python으로 작성된 간단한 로그 분석 스크립트 예시입니다. 이 스크립트는 Ivanti 접근 로그(Apache/Nginx 스타일 가정)에서 의심스러운 User-Agent나 비정상적인 경로를 탐지합니다.

```python
import re
import sys

# 의심스러운 User-Agent 패턴 (예시)
SUSPICIOUS_UA_PATTERN = re.compile(r'(python-requests|curl|wget|scanner|bot)', re.IGNORECASE)
# Ivanti 제로데이 관련 의심 경로 (예시)
SUSPICIOUS_PATH_PATTERN = re.compile(r'(/api/v1/|/cgi-bin/|/por/login_config\.lua)')

def analyze_log_file(log_file_path):
    print(f"[*] Analyzing log file: {log_file_path}")
    
    try:
        with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_no, line in enumerate(f, 1):
                # 로그 파싱 (단순화를 위해 공백 기준 분할)
                parts = line.split()
                if len(parts) < 7:
                    continue
                
                # IP 추출
                ip_address = parts[0]
                # 경로 추출 (예: "GET /path HTTP/1.1")
                path = parts[6]
                # User-Agent 추출 (단순화: 마지막 부분)
                user_agent = ' '.join(parts[11:])

                # 탐지 로직
                if SUSPICIOUS_PATH_PATTERN.search(path):
                    print(f"[!!!] Suspicious Path Found at Line {line_no}: IP={ip_address}, Path={path}")
                
                if SUSPICIOUS_UA_PATTERN.search(user_agent):
                    print(f"[!] Suspicious User-Agent Found at Line {line_no}: IP={ip_address}, UA={user_agent}")

    except FileNotFoundError:
        print("[-] File not found. Please check the path.")

if __name__ == "__main__":
    # 사용법: python ivanti_checker.py access.log
    if len(sys.argv) < 2:
        print("Usage: python ivanti_checker.py <log_file_path>")
    else:
        analyze_log_file(sys.argv[1])
```

이 스크립트는 기초적인 PoC(Proof of Concept)로, 실제 환경에서는 정규표현식을 최신 IoC에 맞춰 지속적으로 업데이트하고 SIEM(Security Information and Event Management) 시스템과 연동해야 합니다.

### 단계별 완화 및 대응 가이드

이미 공격이 시작되었다고 가정할 때, 즉각적이고 체계적인 대응이 필요합니다. 단순한 패치 적용만으로는 잠복해 있는 백도어를 제거할 수 없습니다.

1.  **즉시 격리 (Isolation)**     *   인터넷을 통해 노출된 Ivanti 장비의 관리 포트(HTTPS 등)를 방화벽에서 즉시 차단하십시오. 공격자가 언제든 다시 접속할 수 있는 통로를 끊어야 합니다.

2.  **IoC 헌팅 및 포렌식 (Investigation)**     *   위 스크립트나 SIEM 룰을 사용하여 7월 이후의 모든 접속 로그를 재검토하십시오.     *   시스템 내 `/tmp`, `/var/tmp`, 웹 루트 디렉터리 내 숨겨진 파일(예: `.`, `..`으로 시작하는 파일) 등을 검사하여 웹 쉘이 업로드되었는지 확인합니다.

3.  **공식 패치 적용 및 펌웨어 업그레이드**     *   Ivanti가发布한 최신 보안 권고 사항(Security Advisory)을 확인하고, 해당 취약점(CVE)을 해결하는 최신 펌웨어로 업그레이드합니다. 단, 펌웨어 업그레이드 전 반드시 설정 백업을 수행해야 합니다.

4.  **시스템 초기화 (Factory Reset - 권장)**     *   제로데이 공격의 특성상 공격자가 시스템 깊숙이 영구 백도어를 심어놓았을 가능성이 높습니다. 패치만으로는 제거되지 않을 수 있으므로, 보안 장비의 신뢰할 수 없는 설정을 초기화하고 패치가 적용된 '깨끗한' 상태에서 구성을 다시 가져오는 것을 강력히 권장합니다.

5.  **자격증명 및 키 교체**     *   VPN 계정, 관리자 비밀번호, 그리고 해당 장비에 저장된 SSL/TLS 인증서 등을 모두 폐기하고 새로 발급해야 합니다. 공격자가 이미 탈취한 크레덴셜을 사용하여 재침투하는 것을 방지하기 위함입니다.

## 결론

이번 Ivanti 제로데이 익스플로잿 급증 사태는 단순한 소프트웨어 결함을 넘어선 '고도로 조직화된 공격 캠페인'임을 시사합니다. 7월부터 시작된 공격이 최근 급증한 것은 공격자들이 확보한 봇넷이나 익스플로잇 툴이 성숙기에 접어들었음을 의미합니다.

핵심은 **"패치는 최소한의 조치일 뿐"**이라는 점입니다. 이미 장악된 시스템을 구원하려면 패치보다는 '철저한 포렌식'과 '시스템 초기화' 같은 외과적 수술이 필요할 수 있습니다. 방어자는 단순히 CVE 번호를 확인하는 것에 그치지 말고, 자사의 네트워크 트래픽 로그 속에 7월 이후 묻혀 있을지도 모르는 공격의 흔적을 찾아 적극적으로 헌팅(Hunting)해야 합니다. 제로데이는 패치가 나오는 순간 'N-Day'가 되지만, 방어자가 대응하는 그 순간까지는 언제나 '제로데이'처럼 치명적입니다. 즉각적인 행동을 취하십시오.

**참고자료**:
- [SecurityWeek - Ivanti Exploitation Surges](https://news.google.com/rss/articles/CBMiowFBVV95cUxPejZpZkpKZ0ZoQThXOXpjbGdHU1hGZUx0T0NkRk9lcGVoUU5pbmNoQmVqX1hTT2VYOWo2Q3Y1ZTVHN21weWdLMmJNQ0xmQmRzT0tkUS1ISzVaRDk3WUE0SkUwWTA3VmIwVU1NWlBZekttdWhBSFhPaDBXYXVyYVltVVR4bENRRU52V190dm5RaVFGdlFqMkRWUDFmRVVxQjZJQjFv0gGoAUFVX3lxTE5vVEcwdldJdGI2Z1VianBFeXE3UHZ5TFM4WEZqZ0ZuWHRETHZGaXhlZE1Rc0hfMGp1bVk1YjU1MmxnMWZuOXkwWVBORHVyMjlwakpCallRVEs0dVc2TV9GRHhGYmdWVWI1VERjSnZlX1BrTnlSbW5ralY3OFYyTGltaDdCWEVTeGlPSWE2bGhINXA3ckxHSDhtd2hHaGxHQS1LUHdPSUh4WA?oc=5)
- Ivanti Official Security Advisories

---

**출처**: [https://news.google.com/rss/articles/CBMiowFBVV95cUxPejZpZkpKZ0ZoQThXOXpjbGdHU1hGZUx0T0NkRk9lcGVoUU5pbmNoQmVqX1hTT2VYOWo2Q3Y1ZTVHN21weWdLMmJNQ0xmQmRzT0tkUS1ISzVaRDk3WUE0SkUwWTA3VmIwVU1NWlBZekttdWhBSFhPaDBXYXVyYVltVVR4bENRRU52V190dm5RaVFGdlFqMkRWUDFmRVVxQjZJQjFv0gGoAUFVX3lxTE5vVEcwdldJdGI2Z1VianBFeXE3UHZ5TFM4WEZqZ0ZuWHRETHZGaXhlZE1Rc0hfMGp1bVk1YjU1MmxnMWZuOXkwWVBORHVyMjlwakpCallRVEs0dVc2TV9GRHhGYmdWVWI1VERjSnZlX1BrTnlSbW5ralY3OFYyTGltaDdCWEVTeGlPSWE2bGhINXA3ckxHSDhtd2hHaGxHQS1LUHdPSUh4WA?oc=5](https://news.google.com/rss/articles/CBMiowFBVV95cUxPejZpZkpKZ0ZoQThXOXpjbGdHU1hGZUx0T0NkRk9lcGVoUU5pbmNoQmVqX1hTT2VYOWo2Q3Y1ZTVHN21weWdLMmJNQ0xmQmRzT0tkUS1ISzVaRDk3WUE0SkUwWTA3VmIwVU1NWlBZekttdWhBSFhPaDBXYXVyYVltVVR4bENRRU52V190dm5RaVFGdlFqMkRWUDFmRVVxQjZJQjFv0gGoAUFVX3lxTE5vVEcwdldJdGI2Z1VianBFeXE3UHZ5TFM4WEZqZ0ZuWHRETHZGaXhlZE1Rc0hfMGp1bVk1YjU1MmxnMWZuOXkwWVBORHVyMjlwakpCallRVEs0dVc2TV9GRHhGYmdWVWI1VERjSnZlX1BrTnlSbW5ralY3OFYyTGltaDdCWEVTeGlPSWE2bGhINXA3ckxHSDhtd2hHaGxHQS1LUHdPSUh4WA?oc=5)