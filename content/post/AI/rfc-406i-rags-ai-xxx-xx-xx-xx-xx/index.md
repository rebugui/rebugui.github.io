---
title: "🤖 RFC 406i RAGS: AI 저품질 기여 자동 거부 표준"
date: 2026-03-15T20:53:57+09:00
draft: false
tags:
  - "AI"
  - "RFC 406i"
  - "RAGS"
  - "오픈소스"
  - "LLM"
categories:
  - "AI"
draft: true
---


## 서론

오픈소스 생태계의 관문인 Pull Request(PR)와 이슈 트래커가 최근 극심한 혼란을 겪고 있습니다. 유지관리자(Maintainer)가 아침에 눈을 떴을 때, 밤새 수십 개의 PR이 도착해 있는 상황은 더 이상 드문 일이 아닙니다. 문제는 이 PR들이 대부분 "생성형 AI가 작성한 저품질 코드"라는 점입니다. 문법적으로는 완벽해 보이지만, 실제로는 프로젝트의 맥락을 전혀 반영하지 못한 채 GPT나 Claude와 같은 LLM이 '착각'하여 생성해 낸 결과물들입니다.
이러한 현상은 소프트웨어 엔지니어링 영역에서 **'비대칭적 노력(Asymmetric Effort)' 문제**를 야기합니다. 공격자 혹은 성의 없는 기여자는 AI를 통해 클릭 한 번으로 수백 개의 변질된 기여물을 생성할 수 있지만, 이를 검수하고 반려해야 하는 인간 유지관리자는 각각의 PR을 정밀하게 분석해야 합니다. 결국 인간의 시간과 정신력이라는 한정된 리소스가 고갈되어, 진짜 가치 있는 기여까지 묻히게 되는 '트래젝디 오브 더 코먼즈(Tragedy of the Commons)' 상황이 초래됩니다.
바로 이 지점에서 **RFC 406i RAGS (Rejection of Automatically Generated Spam)** 표준이 제안되었습니다. 이는 단순히 'AI를 싫어하자'는 감정적인 접근이 아닌, MLOps 관점에서 저품질 AI 기여물을 체계적으로 식별하고 자동 거부하여 오픈소스 생태계의 건전성을 확보하려는 기술적 시도입니다. 본문에서는 RFC 406i RAGS가 제시하는 기술적 메커니즘과 실제 구현 방안을 심도 있게 다루겠습니다.

## 본론


### RFC 406i RAGS의 기술적 원리와 메커니즘

RFC 406i RAGS의 핵심은 저품질 AI 기여물이 지니는 특유의 **'스타일러스틱(Stylistic)' 및 '시맨틱(Semantic)' 지문(Fingerprint)**을 포착하는 데 있습니다. 일반적으로 인간이 작성한 코드나 문서는 실수, 문맥에 깊이 결부된 변수명, 그리고 문장의 '버스트니스(Burstiness, 변동성)'가 존재합니다. 반면, LLM이 생성한 저품질 텍스트는 확률적 분포를 따르는 매끄러움과 문맥을 무시한 '착각(Hallucination)' 패턴을 보입니다.
RAGS 표준은 이러한 패턴을 다음과 같은 기술적 지표로 정형화합니다.
1.  **낮은 정보 엔트로피 (Low Information Entropy)**: 문장은 길지만 실제로 전달하는 구체적인 정보가 없는 막연한 표현.
2.  **맥락 부재 (Contextual Irrelevance)**: 레포지토리의 기존 코드 스타일, 코딩 컨벤션, 혹은 구조적 아키텍처를 전혀 고려하지 않은 제안.
3.  **반복적인 템플릿 구조 (Repetitive Templates)**: 특정 LLM이 자주 생성하는 도입부나 결론 문구의 패턴 매칭.
이러한 원리를 바탕으로 RAGS는 기여물이 들어오는 즉시 사전 필터링(Pre-filtering)을 수행하는 파이프라인을 구축할 것을 권고합니다.

### RAGS 필터링 파이프라인 아키텍처

RAGS 표준이 제안하는 자동 거부 시스템의 이상적인 아키텍처는 다음과 같습니다. 이는 CI/CD 파이프라인 초기 단계에 삽입되어 유지관리자의 부하를 줄이는 역할을 합니다.

```javascript
graph LR
    A[User Contribution] --> B[Static Analysis]
    B --> C[RAGS Feature Extraction]
    C --> D{Quality Threshold Check}
    D -->|High Spam Prob| E[Auto Reject]
    D -->|Low Spam Prob| F[Human Review Queue]
    E --> G[Notify User]
    F --> H[Merge]
```

이 다이어그램은 기여가 들어오자마자 정적 분석(Static Analysis)을 통해 코드나 텍스트의 기본적인 특성을 추출하고, RAGS 알고리즘이 저품질 AI 생성 여부를 판단하는 과정을 보여줍니다. 임계값(Threshold)을 초과하는 스팸 점수를 받은 기여물은 자동으로 반려되며, 이 과정에서 인간의 개입은 전혀 필요하지 않습니다.

### 실무 적용을 위한 구현 가이드 (Python)

실제로 이 표준을 오픈소스 프로젝트에 적용하려면 어떻게 해야 할까요? 복잡한 LLM 모델을 다시 돌리는 것은 비효율적입니다. 대신 가벼운 Heuristic 기반의 필터링 로직을 Python으로 구현하여 GitHub Action이나 Pre-commit hook으로 배치할 수 있습니다.
다음은 RFC 406i의 가이드라인을 참고하여 작성한 간단한 `RAGSFilter` 클래스 예시입니다.

```python
import re
from typing import List, Tuple

class RAGSFilter:
    def __init__(self, max_generic_ratio: float = 0.3):
        self.max_generic_ratio = max_generic_ratio
        # LLM이 자주 사용하는 막연한 표현(Stopwords 또는 Hallucination markers)
        self.generic_phrases = [
            "as an AI language model",
            "it is important to note",
            "in conclusion",
            "furthermore",
            "comprehensive overview",
            "delve into",
            "ensure that",
        ]

    def _calculate_generic_ratio(self, text: str) -> float:
        """텍스트 내 포함된 일반적인(상투적인) LLM 구문의 비율을 계산합니다."""
        word_count = len(text.split())
        if word_count == 0:
            return 0.0
        
        generic_count = 0
        # 대소문자 구분 없이 패턴 매칭
        for phrase in self.generic_phrases:
            if re.search(re.escape(phrase), text, re.IGNORECASE):
                generic_count += 1
        
        # 단순히 구문의 등장 횟수가 아닌, 전체 문장 흐름에서의 차지 비중(가중치 적용 가능)
        return generic_count / max(1, word_count / 10) # Normalization heuristic

    def _check_contextual_relevance(self, diff_text: str, repo_keywords: List[str]) -> bool:
        """
        PR의 변경 사항(Diff)이 레포지토리의 핵심 키워드를 포함하는지 확인합니다.
        AI 스팸은 종종 프로젝트 내부 용어를 사용하지 않고 범용적인 용어만 사용합니다.
        """
        if not repo_keywords:
            return True # 키워드가 없으면 패스
        
        diff_lower = diff_text.lower()
        # 변경 사안이 적어도 하나의 프로젝트 관련 키워드를 언급해야 함
        relevance = any(keyword.lower() in diff_lower for keyword in repo_keywords)
        return relevance

    def evaluate_contribution(self, title: str, body: str, diff: str) -> Tuple[bool, str]:
        """
        기여물을 평가하고 (is_spam, reason) 튜플을 반환합니다.
        """
        full_text = f"{title} {body}"
        
        # 1. 상투적인 LLM 구문 비율 확인
        generic_ratio = self._calculate_generic_ratio(full_text)
        if generic_ratio > self.
```


```python
max_generic_ratio:
            return False, f"Rejected: High density of generic AI phrases detected (Ratio: {generic_ratio:.2f})"

        # 2. 맥락 관련성 확인 (예시 키워드: 'auth', 'db', 'model' 등 프로젝트에 맞게 설정)
        # 실제로는 프로젝트 설정 파일에서 키워드를 로드해야 합니다.
        project_keywords = ['PyTorch', 'tensor', 'model', 'training'] 
        if not self._check_contextual_relevance(diff, project_keywords) and len(diff) > 50:
            return False, "Rejected: Contribution lacks project-specific context or keywords."

        return True, "Passed RAGS filter."

# 사용 예시
if __name__ == "__main__":
    filter = RAGSFilter()
    
    # 스팸 시나리오
    spam_title = "Fix minor bug"
    spam_body = "It is important to note that this change improves the overall performance. Furthermore, it ensures that the system is stable."
    spam_diff = "+ public function run() { return true; }"
    
    is_valid, msg = filter.evaluate_contribution(spam_title, spam_body, spam_diff)
    print(f"Spam Check: {is_valid}, Reason: {msg}")
```

이 코드는 실제 운영 환경에서 사용하기 전에 프로젝트의 특성에 맞게 `generic_phrases`와 `project_keywords`를 튜닝해야 합니다. 하지만 이것만으로도 "AI가 작성한 듯하지만 아무런 내용도 담고 있지 않은" 수많은 스팸 PR을 효과적으로 차단할 수 있습니다.

### 기존 검수 방식 vs RFC 406i RAGS 적용 방식

RFC 406i RAGS를 도입했을 때 얻을 수 있는 이점을 기존의 수동 검수 방식과 비교해 보겠습니다.
| 비교 항목 | 기존 인간 중심 검수 (Manual Review) | RFC 406i RAGS 자동 필터링 |
| :--- | :--- | :--- |
| **노동 비용 (Labor Cost)** | 매우 높음 (모든 PR을 일일이 확인) | 낮음 (자동화된 스크립트가 처리) |
| **대응 속도 (Latency)** | 느림 (Maintainer의 가용 시간에 의존) | 즉각적 (Event-triggered Action) |
| **스팸 누락률 (False Negative)** | 높음 (피로도로 인해 스팸을 Merge할 가능성) | 낮음 (일관된 기준 적용) |
| **건전한 기여 차단 (False Positive)** | 낮음 (인간이 판단하므로) | 발생 가능 (초기 설정에 따라 다름) |
| **확장성 (Scalability)** | 낮음 (기여량이 급증하면 감당 불가) | 높음 (비용 증가 없이 확장 가능) |

### 비대칭적 노력의 균형 맞추기

기술적으로 RAGS는 단순한 텍스트 분석을 넘어 **'비대칭적 노력(Asymmetric Effort)'의 균형을 맞추는 도구**입니다. 스패머는 0달러의 비용으로 AI를 돌려 스팸을 생성하지만, RAGS를 도입한 커뮤니티는 이를 방어하기 위해 CPU 연산 power와 알고리즘을 투입합니다.
여기서 중요한 점은 RAGS가 모든 AI 기여를 배척하는 것이 아니라는 점입니다. AI를 활용하여 고품질의 코드를 작성하고, 충분한 테스트 케이스를 포함하며, 프로젝트의 맥락을 정확히 이해하는 기여는 RAGS 필터를 통과할 수 있습니다. 이 표준은 "AI가 썼느냐"가 아니라 "기여의 가치가 있는가(인간 리뷰어의 시간을 낭비하게 하지 않는가)"를 판단합니다.

## 결론

RFC 406i RAGS는 단순한 반(Anti)-AI 운동이 아닙니다. 이는 생성형 AI 시대에 오픈소스 생태계를 지속 가능하게 만들기 위한 필연적인 MLOps 진화의 과정입니다. 저품질 AI 기여물이 인간 유지관리자의 시간을 고갈시키는 '스팸'으로 전락하는 현실을 직시하고, 기술적 기준을 통해 이를 체계적으로 관리하려는 시도입니다.
전문가 관점에서 볼 때, RAGS와 같은 표준은 더욱 정교해질 것입니다. 현재는 휴리스틱(Heuristic) 기반의 텍스트 분석에 의존하고 있지만, 향후에는 가벼운 온프레미스 모델(예: DistilBERT 기반의 Classifier)을 통합하여 AI 생성물의 확률적 패턴을 더 정밀하게 탐지하는 방향으로 발전할 것입니다.
오픈소스 기여자들에게는 경각심을, 유지관리자들에게는 강력한 방패를 제공하는 RFC 406i RAGS 표준의 도입은 프로젝트의 기술적 부채를 줄이고 건전한 협업 문화를 유지하는 데 필수적인 요소가 될 것입니다.

### 참고자료

- [RFC 406i - RAGS Specification](https://news.hada.io/topic?id=27288)
- GitHub Actions Documentation (Custom Workflows)
- "Detecting GPT-4 Generated Text", arXiv preprints
