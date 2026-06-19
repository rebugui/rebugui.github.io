---
title: "🚨 Ivanti Zero-days: 100여 개 기업 타격 공격 분석"
date: 2026-02-10T11:09:36+09:00
draft: false
tags:
  - "Ivanti"
  - "Zero-Day"
  - "Vulnerability"
  - "Exploit"
  - "보안"
categories:
  - "보안"
draft: true
---

## 서론

보안 운영 센터(SOC)의 모니터를 밝히는 알림 등 중 "경계 네트워크 장비에서의 의심스러운 아웃바운드 연결"보다 더 보안 팀을 숨죽이게 하는 것은 드뭅니다. 바로 이번 Ivanti Zero-day 사태의 현장입니다. 최근 100여 개에 달하는 기업이 피해를 입었다는 소식은 단순한 뉴스가 아니며, 당장 내부 네트워크가 경계 장비를 통해 공격자에게 그대로 노출되었을 수도 있다는 경고입니다.

이번 사태의 핵심은 공격자가 이미 경계망을 넘어섰다는 사실입니다. 방화벽 뒤에 숨겨둔 것들이 안전하다는 믿음은 깨졌습니다. 우리는 단순히 "패치를 하라"는 말을 넘어, 공격자가 이 취약점을 통해 실제로 어떻게 내부로 침투했는지, 그 기술적 메커니즘을 정확히 이해해야 합니다. 이 글에서는 Ivanti 취약점을 악용한 실제 공격 흐름을 분석하고, 방어자가 취해야 할 구체적인 실무 가이드를 다룹니다.

> **⚠️ 윤리적 경고**: 본 문서에 포함된 기술적 분석 및 코드는 보안 강화 및 방어 목적(Defensive Security)입니다. 허가 없는 시스템 접근이나 공격은 엄격히 금지되며 법적 책임을 질 수 있습니다.

## 본론: 공격 시나리오 및 기술적 심층 분석

### 1. 취약점의 기술적 원리와 공격 체인

Ivanti Connect Secure(이전 Pulse Secure) 및 Policy Secure 제품에서 발견된 이번 취약점(CVE-2024-21887 등)은 주로 **웹 컴포넌트의 입력 검증 미흡(Input Validation Failure)**에서 기인합니다. 특히, 인증 우회(Authentication Bypass)와 원격 코드 실행(RCE)이 결합되어 치명적입니다.

공격자는 특수하게 조작된 HTTP 요청을 보내, 시스템의 관리자 권한을 획득하는 명령어를 삽입합니다. 이는 일반적인 SQL 인젝션이나 XSS와 달리, 서버의 운영체제 레벨에서 명령을 실행할 수 있는 **서버 사이드 템플릿 인젝션(SSTI)** 또는 **명령어 인젝션** 기법을 사용합니다.

다음은 공격자가 네트워크에 진입한 후 수행하는 일반적인 공격 흐름도입니다.

```mermaid
graph LR
    A[공격자] --> B[정찰 및 취약점 스캔]
    B --> C[익스플로잇 전송]
    C --> D[인증 우회]
    D --> E[웹 쉘 업로드]
    E --> F[백도어 설치]
    F --> G[자격 증명 훔치기]
    G --> H[내부 망 횡적 이동]
```

### 2. 악용 시나리오: 웹 쉘 삽입과 지속성 확보

공격자가 취약점을 통해 초기 진입에 성공하면, 가장 먼저 하는 일은 **지속성(Persistence)**을 확보하는 것입니다. 이를 위해 공격자는 시스템에 악성 스크립트(웹 쉘)를 심습니다. 이 웹 쉘을 통해 공격자는 복잡한 익스플로잇을 다시 시도할 필요 없이, 단순한 HTTP 요청만으로 시스템 내부 명령을 원격으로 제어할 수 있습니다.

아래 코드는 방어자가 자체 시스템의 로그를 분석하여 이러한 웹 쉘 삽입 시도가 있었는지 탐지하기 위해 사용할 수 있는 간단한 Python 스크립트입니다. (실제 익스플로잇 코드가 아닌 탐지용 로직입니다.)

```python
import re

def analyze_ivanti_logs(log_file_path):
    """
    Ivanti 접속 로그를 분석하여 의심스러운 명령어 인젝션 패턴을 탐색합니다.
    """
    # 일반적인 웹 쉘 패턴 또는 명령어 인젝션 시도 패턴 예시
    # 예: &(), ; cat, wget, curl 등의 조합
    suspicious_patterns = [
        r'\&\&\s*(cat|wget|curl|perl|python)', 
        r';\s*(rm|chmod|chown)',
        r'\|\|\s*(nc|netcat)',
        r'%26%26', # URL 인코딩된 &&
        r'%3B'     # URL 인코딩된 ;
    ]

    try:
        with open(log_file_path, 'r', encoding='utf-8') as file:
            for line in file:
                for pattern in suspicious_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        print(f"[ALERT] 탐지됨: {line.strip()}")
                        break
    except FileNotFoundError:
        print("파일을 찾을 수 없습니다.")

# 사용 예시 (실제 환경의 로그 경로로 변경 필요)
# analyze_ivanti_logs('/var/log/httpd/access_log')
```

### 3. 방어 전략 비교: 단순 패치 vs 심층 방어

많은 기업이 패치만 배포하면 끝났다고 생각하지만, 공급망 공격의 특성상 완화 조치(Mitigation)가 선행되어야 합니다. 다음은 단순 패치와 심층 방어 전략의 차이를 비교한 표입니다.

| 구분 | 단순 패치 접근 (Reactive) | 심층 방어 접근 (Proactive)
|:--- | :--- | :---
|**대응 시점** | 벤더 업데이트 릴리즈 후 적용 | 취약점 공개 즉시 완화 규칙(Mitigation) 적용
|**인증 우회 대책** | 패치 적용 시까지 노출됨 | 외부 접근 차단(VPN 그룹 제한) 및 MFA 강제
|**탐지 능력** | 로그 확인에 의존 | IOCs(침해 지표) 기반 SIEM 규칙 추가
|**백도어 대응** | 패치 시 자동 제거 안 됨 | 포렌식을 통한 웹 쉘 및 계정 숨김 파일 수동 검증
|**복구 신뢰도** | 낮음 (재감염 가능성 높음) | 높음 (시스템 재설치 또는 깊은 검증 후 복구) |

### 4. 실무 적용 가이드: 단계별 대응 절차

만약 귀하의 조직이 Ivanti 제품을 사용 중이라면, 다음 절차를 즉시 따르십시오. 패치가 적용되기 전까지는 시스템을 "Compromised(피해)"라고 가정하고 운영해야 합니다.

#### 1단계: 격리 (Isolation)

- 인터넷을 통한 Ivanti 장비로의 모든 접속을 차단하십시오. 내부 네트워크에서만 관리 포트에 접근할 수 있도록 방화벽 규칙을 수정합니다.

#### 2단계: 사용자 및 관리자 감사 (Audit)

- 공격자는 종종 숨겨진 계정을 생성합니다. 다음 명령어(Unix 기반)를 통해 의심스러운 계정이 없는지 확인하십시오.

```bash
# /etc/passwd 파일에서 UID 0(root) 권한을 가진 계정 및 최근 생성 계정 확인
cat /etc/passwd | grep -E "(:0:)|(/home/.*:)"
```

#### 3단계: IOC(침해 지표) 검증

- Ivanti에서 배포한 IOC 리스트를 바탕으로 시스템 내 의심스러운 파일을 검색합니다.

- 특히, 웹 루트 디렉토리 내 최근 수정된 파일들(`*.php`, `*.cgi`, `*.jsp`)을 면밀히 검토해야 합니다.

#### 4단계: 완화 패치 및 업데이트 (Mitigation & Patch)

- Ivanti에서 제공하는 XML 기반의 완화 스크립트를 먼저 적용합니다.

- 이후 최신 패치를 적용하고, 장비를 재부팅하여 메모리 상의 악성 프로세스를 제거합니다.

## 결론

이번 Ivanti Zero-day 사태는 100여 개 기업이 피해를 입을 때까지 이미 늦은 상태에서 발견되었습니다. 공급망 공급업체의 취약점은 우리의 통제 밖에서 발생하지만, 그 결과는 우리의 네트워크를 무너뜨립니다.

전문가의 관점에서 볼 때, 가장 큰 교훈은 **"신뢰의 재설정"**입니다. 더 이상 경계 장비(VPN, 방화벽)는 신뢰할 수 있는 구역이 아닙니다. 이 장비들 또한 인터넷에 직접 노출된 '일반 서버'와 동일한 수준으로 엄격한 보안 강화(Security Hardening)와 지속적인 모니터링이 필요합니다.

오늘 당장 Ivanti 장비의 로그를 확인하고, 비인가 접속 흔적이 없는지 검증하는 것은 선택이 아닌 필수입니다. 방화벽 너머의 적은 이미 안으로 들어와 있을 수 있습니다.

### 참고자료 (References)

- [Ivanti Security Advisory](https://www.ivanti.com/blog/articles/security-advisory)

- [CISA - Known Exploited Vulnerabilities Catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog)

- [Volexity - Analysis of Ivanti Connect Zero-Days](https://www.volexity.com/blog/)
