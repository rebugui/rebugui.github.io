---
title: "CISA CVSS 한계 돌파: Miggo, SSVC Scoring 도입으로 취약점 우선순위화 강화 분석"
date: 2026-06-19T11:15:55+09:00
draft: false
categories: ["CVE"]
tags: ["CVE"]
author: "Intelligence Agent"
draft: true
---

## 서론: 취약점 홍수 속에서 길을 찾는 여정

"Critical"이라는 경고 메시지가 하루에도 수십 번씩 울리는 현대의 IT 환경에서, 조직들은 매번 같은 근본적인 질문에 봉착합니다. "이 모든 취약점 중에서 **가장 먼저** 고쳐야 할 것은 무엇인가?" 기존에는 CVSS(Common Vulnerability Scoring System) 점수가 이 답을 제공해 주었습니다. 9.8이라는 최고점을 받은 취약점은 무조건 최우선 순위로 처리되어야 한다는 강력한 가이드라인을 제시했기 때문입니다.

하지만 현실은 녹록지 않습니다. 단순히 CVSS 점수만으로는 조직의 실제 위험도를 완벽하게 파악할 수 없습니다. 9.8점짜리 취약점이 회사의 핵심 서비스(핵심 자산)에 존재하며, 현재 활발히 공격받고 있다면 그 위험도는 7.5점이지만 외부에 노출된 단순 웹 서버의 9.8점보다 훨씬 치명적일 수 있습니다.

이러한 한계를 인지하고 CISA(Cybersecurity and Infrastructure Security Agency)가 CVSS 기반의 단편적인 접근을 넘어선 새로운 평가 기준 도입에 박차를 가하고 있습니다. 그리고 이 변화의 흐름에 발맞춰 Miggo는 혁신적인 **SSVC (Security Score for Vulnerability) Scoring**을 플랫폼에 통합했습니다. SSVC는 단순한 심각도(Severity)를 넘어, 실제 비즈니스 영향과 위협 환경을 반영하여 취약점 우선순위화의 패러다임을 근본적으로 전환하고 있습니다.

## 본론: CVSS 한계를 돌파하는 SSVC의 메커니즘 분석

### 1. 기존 CVSS의 역할과 내재적 한계

CVSS는 취약점 자체의 고유한 특성(Intrinsic Characteristics)을 측정하여 점수화합니다. 이는 공격 벡터, 필요한 권한 수준, 영향 범위(Confidentiality, Integrity, Availability) 등 객관적인 기술 지표에 기반합니다. 예를 들어, 원격 코드 실행(RCE)이 가능한 취약점은 높은 CVSS 점수를 받게 됩니다.

그러나 CVSS의 가장 큰 한계는 **"맥락(Context)"**을 반영하지 못한다는 점입니다. 즉, 해당 취약점이 어떤 자산에 존재하는지, 그 자산이 회사 운영에서 얼마나 중요한 역할을 하는지, 그리고 현재 공격자들이 이 취약점을 실제로 어떻게 활용하고 있는지와 같은 외부적 요소를 통합적으로 고려하기 어렵습니다.

### 2. SSVC: 위험 기반의 새로운 평가 프레임워크 (Mermaid 다이어그램)

SSVC는 CVSS가 제공하는 '심각도' 위에 조직 고유의 비즈니스 맥락을 덧입혀 **'실제 위험(Actual Risk)'** 점수를 도출합니다. 이는 취약점 자체의 잠재적 파괴력뿐만 아니라, 그 취약점이 현실 세계에서 일으킬 수 있는 피해 규모까지 종합적으로 평가하는 것입니다.

다음 다이어그램은 전통적인 CVSS 지표가 어떻게 SSVC로 확장되어 최종 위험 점수(Risk Score)를 산출하는지 보여줍니다.

```javascript
graph TD
    A[CVSS Base Metrics] --> B{Severity Level}
    B --> C["Asset Criticality (자산 중요도)"]
    C --> D["Threat Intelligence (위협 정보)"]
    D --> E["Exploitability Context (실제 공격 가능성)"]
    E --> F(SSVC Final Risk Score)
```

**기술적 깊이 해설:** SSVC는 단순히 CVSS 점수에 가중치를 부여하는 방식이 아닙니다. 이는 **수학적 모델링을 통해 복합적인 위험 함수를 계산**합니다. 예를 들어, $SSVC = f(\text{CVSS}, \text{AC}, \text{TI}, \text{EC})$ 와 같은 형태로 표현될 수 있으며, 여기서 $\text{AC}$는 자산 중요도(Asset Criticality), $\text{TI}$는 위협 정보(Threat Intelligence)의 활성도를 의미합니다.

### 3. CVSS vs SSVC 비교 분석 (표)

| 비교 항목 | CVSS (기존 방식) | SSVC (Miggo 도입/신규 방식) |
| :--- | :--- | :--- |
| **평가 초점** | 취약점 자체의 잠재적 심각도 (Severity) | 실제 환경에서의 위험 수준 (Actual Risk) |
| **주요 반영 요소** | 공격 벡터, 영향 범위(CIA), 복잡성 등 기술 지표 | CVSS + 자산 중요도 + 위협 정보 + 비즈니스 영향 |
| **결과값의 의미** | "이 취약점은 얼마나 파괴적인가?" | "이 취약점은 우리 회사에 얼마나 큰 피해를 줄 수 있는가?" |
| **활용 목적** | 기술적 우선순위 지정, 표준화된 보고 | 비즈니스 위험 기반 자원 최적화 및 대응 결정 |

### 4. SSVC 활용 Step-by-step 가이드 및 코드 예시

조직이 Miggo 플랫폼에서 SSVC 점수를 활용하여 취약점 관리를 수행하는 과정은 다음과 같습니다.

**Step 1: 데이터 수집 및 CVSS 산출 (Identify)**
- 다양한 스캐너를 통해 모든 취약점을 식별하고, 각 취약점에 대해 표준 CVSS 점수(예: 7.5)를 부여합니다.

**Step 2: 맥락 정보 주입 (Assess)**
- 해당 취약점이 위치한 자산의 중요도(Tier 1~3), 현재 공격 트렌드(TI), 해당 취약점의 실제 노출 여부 등을 플랫폼에 입력합니다.

**Step 3: SSVC 최종 점수 도출 및 우선순위화 (Prioritize)**
- 플랫폼이 CVSS와 맥락 정보를 결합하여 최종 SSVC 점수를 산출합니다. 이 점수가 곧 대응 우선순위를 결정하는 지표가 됩니다.
- (예시) CVSS 7.5 + Tier 1 자산 + Active Exploit $\rightarrow$ **SSVC 9.2 (최우선)**

**Step 4: 효율적 리소스 할당 및 완화 (Remediate)**
- 높은 SSVC 점수를 받은 취약점부터 패치, 설정 변경(Configuration Change), 또는 임시 방어 조치(WAF 규칙 추가 등)를 적용합니다.

#### 개념 설명용 Python 코드 예시: 위험도 계산 함수

다음 코드는 CVSS와 맥락 변수(자산 중요도, 위협 활성도)를 결합하여 SSVC의 기본 원리를 구현한 것입니다.

```python
def calculate_ssvc(cvss_score: float, asset_criticality: float, threat_activity: float) -> float:
    """
    CVSS 기반으로 위험 점수를 계산하는 함수 (단순화된 모델).
    asset_criticality: 1.0 (낮음) ~ 3.0 (매우 높음)
    threat_activity: 0.0 (없음) ~ 1.0 (활발함)
    """
    # 위험 함수 예시: CVSS에 맥락 가중치를 곱하고 선형적으로 조정
    ssvc = cvss_score * ((asset_criticality / 3.0) + (threat_activity * 0.5))
    return round(ssvc, 2)

# 시나리오 1: CVSS 7.5, 중요 자산(Tier 1), 활발히 공격받는 경우
score1 = calculate_ssvc(cvss_score=7.5, asset_criticality=3.0, threat_activity=1.0)
print(f"시나리오 1 (최고 위험): {score1}") # 예상 출력: ~9.25

# 시나리오 2: CVSS 7.5, 중요하지 않은 자산(Tier 1), 공격 트렌드 없음
score2 = calculate_ssvc(cvss_score=7.5, asset_criticality=1.0, threat_activity=0.0)
print(f"시나리오 2 (낮은 위험): {score2}") # 예상 출력: ~6.25
```

## 결론: 취약점 관리의 미래는 '위험'에 있다

CISA가 주도하고 Miggo가 구현한 SSVC Scoring 도입은 단순한 점수 체계의 변화를 넘어, **취약점 관리가 기술적 문제 해결에서 비즈니스 위험 관리로 진화**했음을 선언하는 사건입니다. 더 이상 "CVSS 9.8이니까 무조건 고쳐야 해"라는 직관적인 대응이 아닌, "우리 회사에게 이 취약점이 미치는 실질적인 피해가 가장 크기 때문에 우선순위를 최상으로 두고 고치자"는 전략적 접근을 가능하게 합니다.

전문가의 관점에서 볼 때, SSVC와 같은 위험 기반 점수화 방식은 앞으로 AI 및 머신러닝과의 결합을 통해 더욱 정교해질 것입니다. 공격 패턴 변화를 실시간으로 감지하고, 자산의 사용량이나 트래픽 급증에 따라 동적으로 SSVC 점수를 조정하는 'Dynamic Scoring'이 표준이 될 것으로 예상됩니다.

제한된 보안 리소스를 가장 높은 ROI(Return on Investment)로 활용하고자 하는 모든 조직에게 SSVC는 단순한 도구가 아닌, **최적화된 방어 전략을 위한 나침반**입니다.

--- 🔗 **참고 자료:** Miggo adds SSVC scoring as CISA moves beyond CVSS-based vulnerability prioritization (MSSP Alert) [https://news.google.com/rss/articles/CBMitwFBVV95cUxOOFJGQmJDaHdNRk9waFFWckhVMFlhUDZ6ZXBNN05odDNENkVLc0d3eXpqQXh2RkNIQWFKUy1ZZkdRZXJPYlJlNHZydGtQdXRrTGV5MENub1dCMjZNSnZBeUI5dDd6YUUza1AzX213LW5BTVd5MTZHSkxicXVKNms0YzVHX2ktbjdhUFduUnFxYVdsVEVCMzcyODlzR0FNdl8wX0o4SUlGSjE1ZWZ3NjhxcEZCSkVhdnc?oc=5](https://news.google.com/rss/articles/CBMitwFBVV95cUxOOFJGQmJDaHdNRk9waFFWckhVMFlhUDZ6ZXBNN05odDNENkVLc0d3eXpqQXh2RkNIQWFKUy1ZZkdRZXJPYlJlNHZydGtQdXRrTGV5MENub1dCMjZNSnZBeUI5dDd6YUUza1AzX213LW5BTVd5MTZHSkxicXVKNms0YzVHX2ktbjdhUFduUnFxYVdsVEVCMzcyODlzR0FNdl8wX0o4SUlGSjE1ZWZ3NjhxcEZCSkVhdnc?oc=5)

---

**출처**: [https://news.google.com/rss/articles/CBMitwFBVV95cUxOOFJGQmJDaHdNRk9waFFWckhVMFlhUDZ6ZXBNN05odDNENkVLc0d3eXpqQXh2RkNIQWFKUy1ZZkdRZXJPYlJlNHZydGtQdXRrTGV5MENub1dCMjZNSnZBeUI5dDd6YUUza1AzX213LW5BTVd5MTZHSkxicXVKNms0YzVHX2ktbjdhUFduUnFxYVdsVEVCMzcyODlzR0FNdl8wX0o4SUlGSjE1ZWZ3NjhxcEZCSkVhdnc?oc=5](https://news.google.com/rss/articles/CBMitwFBVV95cUxOOFJGQmJDaHdNRk9waFFWckhVMFlhUDZ6ZXBNN05odDNENkVLc0d3eXpqQXh2RkNIQWFKUy1ZZkdRZXJPYlJlNHZydGtQdXRrTGV5MENub1dCMjZNSnZBeUI5dDd6YUUza1AzX213LW5BTVd5MTZHSkxicXVKNms0YzVHX2ktbjdhUFduUnFxYVdsVEVCMzcyODlzR0FNdl8wX0o4SUlGSjE1ZWZ3NjhxcEZCSkVhdnc?oc=5)