---
title: "🚨 Ivanti EPMM: Critical 취약점 제로데이 악용 분석"
date: 2026-04-19T08:06:27+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 서론

새벽 3시, SOC(보안 운영 센터) 관제 화면에 불길한 붉은 불빛이 깜빡입니다. 평소와 다름없는 트래픽처럼 보였지만, 로그를 자세히 들여다보면 내부 MDM(모바일 기기 관리) 서버로 향하는 외부의 의심스러운 API 호출이 감지됩니다. 이 공격이 성공한다면, 해커는 기업의 수천 대의 모바일 기기를 원격에서 장악할 수 있게 됩니다. 이것이 바로 현재 Ivanti EPMM(Endpoint Manager Mobile)을 겨냥해 활발히 진행 중인 제로데이 공격의 현실입니다.

지난 Unit 42의 보고서에 따르면, 이미 보안 패치가 배포되기도 전에 이 취약점을 악용한 공격이 확인되었습니다. 단순한 정보 유출을 넘어, 인증 우회(Authentication Bypass)를 통해 서버 권한을 탈취하고 원격 코드 실행(RCE)으로 이어지는 이 취약점은 현대 기업 보안의 가장 큰 약점인 '관리자 계정의 권한'을 노립니다. 왜 우리는 지금 당장 MDM의 보안을 재점검해야 하는지, 그리고 이 공격이 어떻게 작동하는지 기술적인 수준에서 파헤쳐 보겠습니다.

## 본론: 공격 메커니즘과 기술적 분석
> **⚠️ 윤리적 경고**: 아래 설명되는 기술 내용과 코드는 보안 연구 및 방어 목적을 위해서만 제공됩니다. 승인되지 않은 시스템에 대한 테스트는 불법이며 처벌받을 수 있습니다.

### 취약점의 핵심: 인증 우회에서 RCE까지

Ivanti EPMM(구 MobileIron Core)은 기업의 모바일 기기를 관리하는 핵심 플랫폼입니다. 공격자들이 주목하는 것은 바로 이 EPMM이 외부와 통신하는 API 엔드포인트입니다. 이번 사건의 핵심은 특정 API 경로가 인증 절차를 우회하도록 설계되어 있거나, 잘못된 검증 로직을 가지고 있다는 점입니다.

일반적으로 사용자는 로그인을 위해 세션 쿠키나 토큰이 필요합니다. 하지만 이 취약점을 악용하면, 이러한 자격 증명 없이도 내부 기능에 접근할 수 있습니다. 공격자는 이를 이용해 시스템 설정을 변경하거나, 악의적인 파일을 서버에 업로드할 수 있는 권한을 얻습니다.

다음은 공격자가 인증 우회를 통해 서버를 장악하기까지의 일반적인 공격 흐름입니다.

```javascript
graph LR
    A[Attacker] --> B[Send crafted API Request]
    B --> C[Ivanti EPMM Server]
    C --> D{Auth Check Logic}
    D -->|Bypassed| E[Execute Admin Command]
    E --> F[Write Malicious File]
    F --> G[Remote Code Execution]
    D -->|Blocked| H[Request Denied]
```

### 심층 기술 원리 및 공격 시나리오

Unit 42가 분석한 바에 따르면, 공격자는 주로 `/mics/API/` 와 같은 특정 경로를 타겟팅합니다. 공격은 크게 두 단계로 나뉩니다.

1.  **인증 우회 (Authentication Bypass)**: 공격자는 HTTP 요청을 보낼 때, `Authorization` 헤더와 같은 일반적인 인증 정보를 제외하거나 변조된 쿠키를 사용합니다. 취약한 버전의 EPMM은 이러한 비정상적인 요청을 정상적인 관리자 요청으로 잘못 처리하여, 관리자 권한이 필요한 API 기능을 노출시킵니다.
2.  **원격 코드 실행 (RCE)**: 인증이 우회되면 공격자는 서버의 설정 파일을 조작하거나 웹 쉘(Web Shell)과 같은 악의적인 스크립트를 업로드할 수 있습니다. 서버 측에서 이 스크립트가 실행되면, 공격자는 시스템 셸(Shell) 획득에 성공하여 서버 전체를 장악합니다.

이 과정에서 방어자가 알아차리기 어려운 점은, 공격이 정상적인 HTTPS 트래픽처럼 보이거나, 로그인 과정이 생략되었기 때문에 실패 로그가 남지 않는다는 것입니다.

### PoC (개념 증명) 코드 분석

아래 예시는 취약한 서버에 대해 비인증 상태에서 특정 API 엔드포인트에 접근을 시도하여 권한 상승 가능성을 확인하는 Python 스크립트의 개념입니다. 이는 실제 공격 코드가 아닌 취약점 진단을 위한 시나리오입니다.

```python
import requests

def check_epmm_vulnerability(target_ip):
    """
    Ivanti EPMM 인증 우회 취약점 진단 (PoC)
    목적: 비인증 상태에서 관리자 API 접근 가능성 확인
    """
    target_url = f"https://{target_ip}/mics/API/MICS"
    headers = {
        "User-Agent": "Mozilla/5.0 (Security Scanner)",
        "Accept": "application/json",
        # 주의: Authorization 헤더가 의도적으로 생략됨
    }

    try:
        # SSL 인증서 검증 우회 (테스트 환경 가정)
        response = requests.get(target_url, headers=headers, verify=False, timeout=5)

        # 응답 코드 분석
        if response.status_code == 200:
            print("[+] 경고: 인증 우회 가능성 발생!")
            print(f"[+] 서버 응답: {response.text[:100]}")
            print("[!] 민감한 정보가 노출되었는지 확인 필요.")
        elif response.status_code == 401 or response.status_code == 403:
            print("[-] 안전함: 인증이 올바르게 차단됨 (401/403).")
        else:
            print(f"[?] 알 수 없는 응답 코드: {response.status_code}")

    except requests.exceptions.SSLError:
        print("[!] SSL 연결 오류 발생")
    except Exception as e:
        print(f"[!] 연결 실패: {e}")

# 사용 예시 (테스트 대상은 반드시 승인된 범위 내여야 함)
# check_epmm_vulnerability("192.168.1.10")
```

이 코드를 통해 방어자는 자사 시스템이 비인증 API 호출에 대하여 401(Unauthorized) 또는 403(Forbidden)을 반환하는지, 아니면 우회되어 데이터를 노출하는지 확인할 수 있습니다.

### 영향 분석 및 완화 조치 가이드

이 취약점의 파급력은 단순한 서버 해킹 그 이상입니다. MDM 서버는 기업의 모든 모바일 기기, 이메일, VPN 설정, 인증서를 관리합니다. 이 서버가 장악되면 공격자는 다음과 같은 작업이 가능해집니다.

| 공격 단계 | 영향 범위 | 기술적 결과 |
| :--- | :--- | :--- |
| 1단계: 초기 침투 | 네트워크 경계 | 방화벽 우회, 내부망 접근 경로 확보 |
| 2단계: MDM 장악 | 모바일 인프라 | 기기 등록 정보 탈취, 완드(Wipe) 명령 권한 획득 |
| 3단계: 데이터 유출 | 기업 데이터 | 이메일, 연락처, 사내 문서 유출 |
| 4단계: 지속적 지배 | 전사적 보안 | 악성 앱 강제 설치, 중간자 공격(Man-in-the-Middle) |

**완화 조치 (Mitigation Strategies)**

업데이트는 필수적이지만, 즉시 업데이트가 어려운 환경을 위해 다음과 같은 네트워크 레벨의 완화 조치를 즉시 적용해야 합니다.

1.  **인터넷 노출 차단 (Block Internet Exposure)**: Ivanti EPMM 관리 콘솔(포트 8443, 8080 등)이 인터넷에서 직접 접근 가능하지 않도록 해야 합니다. VPN 내부에서만 접근하도록 제한하거나, IP 화이트리스팅을 적용합니다.
2.  **IoC 기반 탐지规则 적용**: 방화벽이나 IPS/IDS에 다음과 같은 IoC(침해 지표) 패턴을 추가하여 공격 시도를 차단합니다.     *   URI 경로: `/mics/API/...` 로의 비정상적인 외부 접근     *   User-Agent: 특정 공격 툴에서 사용하는 패턴
3.  **패치 적용**: Ivanti에서 제공하는 최신 보안 패치(각 버전별 Fixed Build)로 즉시 업그레이드해야 합니다. 특히 11.x 버전 사용자는 매우 취약하므로 즉각적인 조치가 필요합니다.

## 결론

Ivanti EPMM에서 발견된 이번 제로데이 취약점은 "인증"이라는 보안의 가장 기본적인 전제를 무너뜨리는 공격입니다. 공격자는 복잡한 암호 해독 없이도 API 엔드포인트의 허점을 파고들어, 전사적인 모바일 보안 체계를 무너뜨릴 수 있습니다.

현장 보안 전문가로서의 제 인사이트는 이렇습니다. **우리는 지금 '서버 보안'이 아닌 '기기 관리 권한'을 지키는 전쟁을 치르고 있습니다.** 단순히 서버를 패치하는 것을 넘어, MDM이 외부에 노출되어 있는지, 그리고 관리자 권한을 가진 API가 적절히 격리되어 있는지 다시 한번 점검해야 합니다.

보안의 기본은 "신뢰할 수 없는 요청은 차단하는 것"입니다. 오늘 발생한 이 사태는 그 기본이 얼마나 중요한지를 다시금 상기시켜 줍니다. 지금 당장 Ivanti EPMM 로그를 확인하고, 의심스러운 API 호출이 없는지 살펴보십시오. 방어의 골든타임은 지금입니다.

**참고자료**
- [Unit 42 Advisory: Critical Vulnerabilities in Ivanti EPMM Exploited](https://unit42.paloaltonetworks.com/)
- [Ivanti Security Bulletin](https://forums.ivanti.com/)

---

**출처**: [https://news.google.com/rss/articles/CBMie0FVX3lxTE1RbVlMZTBUT1B5QTBVOHc3WFFoUmZjUlNIM3RUSjROUVJpM2pMaXBzSDRqeVZCemI4QXN6VU1zcjJTbkROUFBvVlRhWFJsWFQ2eEFBdU5wb2J5blBYTFU3RFc4cFBxQTBLVVZEbk5tQW54ZHdSbmFlRlg1WQ?oc=5](https://news.google.com/rss/articles/CBMie0FVX3lxTE1RbVlMZTBUT1B5QTBVOHc3WFFoUmZjUlNIM3RUSjROUVJpM2pMaXBzSDRqeVZCemI4QXN6VU1zcjJTbkROUFBvVlRhWFJsWFQ2eEFBdU5wb2J5blBYTFU3RFc4cFBxQTBLVVZEbk5tQW54ZHdSbmFlRlg1WQ?oc=5)