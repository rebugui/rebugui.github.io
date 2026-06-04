---
title: "Vercel Breach: Roblox 치트 위장 악성코드 침투 경로 분석"
date: 2026-04-30T01:07:35+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 서론

새벽 2시, 당신의 팀에서 가장 실력 있는 시니어 개발자의 노트북이 켜집니다. 하지만 이는 야근을 위한 것이 아닙니다. 그는 인기 게임인 Roblox에서 승리하기 위해 '무료 치트 툴'을 검색하고 있었습니다. 다운로드 버튼을 클릭하고 실행 파일을 키자마자, 게임은 켜지지 않았지만 그의 PC 백그라운드에서는 끔찍한 일이 벌어집니다. 이것이 최근 클라우드 개발 플랫폼인 Vercel을 강타한 보안 사고의 서막이었습니다.

많은 기업이 방화벽을 구축하고, SSO(Single Sign-On)를 도입하며, 내부 네트워크를 격리하며 안심하고 있습니다. 하지만 이번 사건은 기업의 보안이 얼마나 쉽게 '개인의 취미 활동' 한 번으로 무너질 수 있는지를 적나라하게 보여줍니다. 공격자는 정교한 APT(지속적 위협) 공격이나 제로데이 취약점을 사용하지 않았습니다. 그저 게이머의 욕망을 자극하는 간단한 사회공학(Social Engineering)과 악성코드(Malware) 하나면 충분했습니다.

왜 우리는 이 주제에 주목해야 할까요? 원격 근무가 일상화되고 업무용 장비와 개인용 장비의 경계가 모호해진 지금, "개인적인 기기에서 발생한 일"이라는 변명은 더 이상 유효하지 않습니다. 이 글에서는 Roblox 치트로 위장한 악성코드가 어떻게 개발자의 세션을 탈취하고, 이를 통해 Vercel의 내부 시스템까지 침투했는지 그 기술적 메커니즘을 분석하고 방어 전략을 모색합니다.

## 본론: 침해 사고의 기술적 분석

### 1. 공격 벡터: 게임 치트를 가장한 정보 탈취(Infostealer)

이번 공격의 핵심은 **정보 탈취형 맬웨어(Infostealer)**입니다. 공격자는 Roblox와 같은 인기 게임의 '무료 핵', '무한 자원 치트'를 내세워 사용자를 유혹했습니다. 사용자가 악성 실행 파일을 실행하면, 맬웨어는 즉시 백그라운드에서 활동을 시작합니다.

주요 타겟은 브라우저에 저장된 **쿠키(Cookie)와 세션 토큰**입니다. 현대적인 웹 애플리케이션은 인증 상태를 유지하기 위해 쿠키를 사용하며, 이 쿠키가 탈취되면 비밀번호를 몰라도 해당 사용자의 계정에 접근할 수 있는 세션 하이재킹(Session Hijacking)이 가능해집니다. Vercel의 경우, 직원의 개인 PC에 감염된 맬웨어가 Vercel 내부 시스템 및 고객 지원 대시보드에 접근할 수 있는 인증 토큰을 훔쳐간 것으로 알려졌습니다.

### 2. 침투 경로 분석 (Attack Chain)

이 공격이 단순한 개인용 PC 감염을 넘어 기업 내부로 침투하기까지의 과정을 시각화하면 다음과 같습니다.

```javascript
graph TD
    A[공격자] --> B[유혹적인 게임 치트 배포]
    B --> C[직원 다운로드 및 실행]
    C --> D[맬웨어 감염]
    D --> E[브라우저 쿠키 및 토큰 탈취]
    E --> F[C2 서버로 유출]
    F --> G[탈취한 토큰으로 Vercel 내부 시스템 접근 시도]
    G --> H{접근 권한 확인}
    H -- 성공 --> I[고객 데이터 유출 및 내부 정보 탈취]
    H -- 실패 --> J[탐지 및 로그 남김]
```

이 다이어그램에서 볼 수 있듯이, 가장 취약한 고리는 '기술적 결함'이 아니라 '사람의 행동'이었습니다. 맬웨어는 훔친 세션 토큰을 이용하여 마치 정상적인 직원처럼 행세하며 내부 시스템에 로그인했습니다. 이는 보안 장비가 정상적인 인증 절차를 거친 트래픽을 차단하기 어렵다는 것을 의미합니다.

### 3. 기술적 심층 분석: 세션 하이재킹 메커니즘

공격자가 사용한 악성코드는 주로 크롬(Chrome)이나 엣지(Edge) 같은 주요 브라우저의 SQLite 데이터베이스 파일을 직접 읽는 방식을 사용합니다. 브라우저는 로그인 정보를 `Cookies` 파일이나 `Local Storage`에 저장하는데, 이 파일들이 암호화되어 있지 않거나(혹은 OS 사용자 키와 연동되어 있어 맬웨어가 해독 가능한 경우) 복호화 키에 접근할 수 있으면 쿠키 값을 쉽게 추출할 수 있습니다.

**⚠️ 주의: 아래 코드는 악성코드의 동작 원리를 이해하기 위한 학습 목적인 PoC(Proof of Concept)이며, 악용될 수 없도록 수정된 예시입니다.**

```python
import os
import sqlite3
import json

# 학습 목적의 개념 증명(PoC) 코드입니다.
# 실제 악성코드는 암호화 키를 해독하거나 프로세스 메모리를 덤프하는 복잡한 기법을 사용합니다.

def simulate_cookie_stealing(browser_profile_path):
    """
    브라우저 쿠키 파일에서 세션 토큰을 추출하는 시뮬레이션 함수
    """
    cookies_file = os.path.join(browser_profile_path, "Network", "Cookies")
    
    if not os.path.exists(cookies_file):
        print("[+] 쿠키 파일을 찾을 수 없습니다.")
        return

    try:
        # 데이터베이스 연결 (실제 환경에서는 잠시 파일 복사 후 수행해야 함)
        conn = sqlite3.connect(cookies_file)
        cursor = conn.cursor()
        
        # vercel.com 도메인과 관련된 쿠키 쿼리
        query = "SELECT host_key, name, value, encrypted_value FROM cookies WHERE host_key LIKE '%vercel%'"
        cursor.execute(query)
        
        print("[+] Vercel 관련 쿠키 검색 중...")
        
        for host, name, value, encrypted_value in cursor.fetchall():
            # 실제 악성코드는 여기서 복호화 루틴을 실행합니다.
            # 이 예시에서는 암호화 여부와 관계없이 존재 유무만 확인합니다.
            print(f"    Found: {name} @ {host}")
            
            if name in ["_vercel_auth", "authjs.session-token"]: 
                # 가상의 중요 토큰 출력
                print(f"    [CRITICAL] Sensitive Token Detected: {name}")
                
        conn.close()
        
    except Exception as e:
        print(f"[-] 오류 발생: {e}")

# 시뮬레이션 실행 (가상 경로)
print("=== Malware Simulation: Cookie Stealer ===")
simulate_cookie_stealing("/fake/path/to/chrome/profile")
```

이 코드는 맬웨어가 내부적으로 어떻게 동작하는지 보여줍니다. 실제 공격자는 이렇게 확보한 `_vercel_auth` 토큰이나 세션 쿠키를 자신의 브라우저에 주입(Injection)함으로써, 비밀번호 없이도 해당 직원의 계정에 즉시 접속할 수 있습니다.

### 4. 전통적 피싱과 게임 기반 맬웨어의 비교

기업 보안 팀은 주로 이메일 피싱에 집중하는 경향이 있지만, 게임이나 크랙 툴을 통한 공격은 다른 특징을 가집니다.

| 비교 항목 | 전통적 피싱 (Business Email Compromise) | 게임/크랙 툴 기반 공격 (Malware) |
| :--- | :--- | :--- |
| **공격 경로** | 이메일, 메신저 | 웹사이트, 포럼, 토렌트 |
| **탐지 난이도** | 상대적 낮음 (스팸 필터, 이메일 sandbox) | **상대적 높음** (사용자가 의도적으로 다운로드) |
| **감염 속도** | 링크 클릭 시 즉시 혹은 문서 열람 시 | 설치 파일 실행 시 즉시 |
| **주 타겟** | 재무팀, 인사팀, 경영진 | **개발자, 엔지니어, 일반 직원** |
| **주요 피해** | 송금 사기, 정보 유출 | **자격증명 탈취, 내부 시스템 장악** |

Vercel 사건은 이 '게임 기반 공격'이 개발자와 같은 기술 직군에게도 얼마나 효과적인지 증명했습니다. 개발자라 해서 보안 의식이 완벽할 수는 없기 때문입니다.

### 5. 방어 및 대응 가이드 (Mitigation Strategies)

이러한 공격을 막기 위해서는 단순한 백신 설치를 넘어선 심층

---

**출처**: [https://news.google.com/rss/articles/CBMilAFBVV95cUxPRFhKT2t2RFY5Z0MzSUxjeGxaaGdRSUxQS19PTnhOZVdSU1FsOHZOZGx1NnRBbWhQLVBYQy1vcVJyZzJQak80TWJmLXVEbndPc19FaF93QkJkeGVXNThqNEtFSWVYdEdNS0hHcU1hWEExVkVDdk9lekJRTEVkbkkyWThJYm5SSnlETTBVZW1RYjlxVzVW?oc=5](https://news.google.com/rss/articles/CBMilAFBVV95cUxPRFhKT2t2RFY5Z0MzSUxjeGxaaGdRSUxQS19PTnhOZVdSU1FsOHZOZGx1NnRBbWhQLVBYQy1vcVJyZzJQak80TWJmLXVEbndPc19FaF93QkJkeGVXNThqNEtFSWVYdEdNS0hHcU1hWEExVkVDdk9lekJRTEVkbkkyWThJYm5SSnlETTBVZW1RYjlxVzVW?oc=5)