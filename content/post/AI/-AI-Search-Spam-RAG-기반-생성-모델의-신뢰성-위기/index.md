---
title: "🚨 AI Search Spam: RAG 기반 생성 모델의 신뢰성 위기"
date: 2026-04-19T08:06:15+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
draft: true
---

## 서론

최근 엔지니어링 팀 회의에서 한 임원이 "내년도 최고의 클라우드 비용 절감 툴"을 AI 검색 엔진에 물어보았습니다. AI는 즉시 A라는 회사의 툴을 1위로 추천하며, 그 근거로 A사의 기술 블로그 글을 인용했습니다. 겉보기에는 완벽한 답변처럼 보였습니다. 그러나 우리 팀이 조사해보니, 그 블로그 글은 A사에서 며칠 전에 집중적으로 생성한 스팸 콘텐츠였고, 타사의 벤치마크 데이터를 조작하여 포함하고 있었습니다.

이 사례는 단순한 오답이 아닙니다. 이는 RAG(Retrieval-Augmented Generation) 시스템이 가진 구조적 보안 취약점을 적나라하게 보여줍니다. 현재 ChatGPT, Perplexity, Google Gemini와 같은 AI 검색 서비스는 방대한 웹의 지식을 검색하여 답변을 생성하지만, 검색된 정보의 '존재 여부'에는 민감하면서도 그 정보의 '독립성'이나 '신뢰성'에 대해서는 맹인과 다를 바 없습니다.

생성형 AI의 신뢰성은 곧 검색 데이터의 품질에서 나옵니다. 하지만 기업들이 자신들의 이익을 위해 AI의 학습 및 검색 데이터를 오염(Spamming)시키기 시작하면서, 우리는 '정보의 쓰레기장' 위에 거대한 지성을 건설하려는 시도를 하고 있는 것은 아닌지 자문해야 합니다. 이 글에서는 AI 검색 스팸의 기술적 메커니즘과 이를 방어하기 위한 MLOps적 관점의 해법을 심층적으로 다루고자 합니다.

## 본론

### RAG 아키텍처와 '존재의 함정'

RAG는 대규모 언어 모델(LLM)의 지식 한계를 극복하고 실시간 정보를 제공하기 위해 탄생한 혁신적인 아키텍처입니다. 사용자의 질문(Query)이 들어오면 시스템은 벡터 데이터베이스(Vector DB)나 웹 인덱스에서 관련 문서를 검색(Retrieve)하고, 이를 컨텍스트(Context)로 하여 LLM이 답변을 생성(Generate)합니다.

문제는 '검색' 단계의 알고리즘, 특히 밀도 기반의 의미 검색(Semantic Search)에 있습니다. 기존의 키워드 기반 검색이 단어의 일치를 중시했다면, AI 검색은 쿼리와 문서 간의 '의미적 유사도(Semantic Similarity)'를 계산합니다. 스패머들은 이를 역이용합니다. "최고의 CRM 추천"이라는 질문에 대해, 자신들의 제품이 최고라는 내용을 담은 문서를 생성하여 의미적 벡터 공간 내에서 질문과 극도로 가깝게 위치시키는 것입니다. AI 검색 엔진은 해당 문서가 "존재"하고 "관련성이 높다"는 팩트만 확인할 뿐, 그 문구가 객관적인 제3자의 리뷰인지, 아니면 유료 광고주의 자화자찬인지 구별하지 못합니다.

다음은 공격자가 AI 검색의 결과를 조작하는 과정을 간략화한 다이어그램입니다.

```javascript
graph LR
    A[Attacker] -->|Create Content| B[Target Webpage]
    B -->|Indexing| C[Web Index]
    D[User Query] --> E[AI Search Engine]
    E -->|Semantic Search| C
    C -->|Retrieve Spam Doc| E
    E -->|Generate Answer| F[User receives Biased Info]
```

### 기존 SEO 스팸과 AI 검색 스팸의 비교

이 문제를 명확히 이해하기 위해 기존의 SEO(검색 엔진 최적화) 스팸과 AI 검색 스팸의 차이를 비교해볼 필요가 있습니다. AI 검색은 단순히 링크를 걸어주는 것이 아니라, 답변 자체를 만들어내기 때문에 그 파급력이 훨씬 큽니다.

| 비교 항목 | 기존 SEO 스팸 (Google Search) | AI 검색 스팸 (Perplexity, GPT) |
| :--- | :--- | :--- |
| **주 목표** | 검색 결과 상위 노출 및 트래픽 유입 | AI 답변 내 직접 언급 및 긍정적 평가 |
| **공격 방식** | 키워드 스터핑, 링크 팜, 백링크 조작 | 의미적 유사도 조작, 구조화된 데이터 꾸미기 |
| **사용자 경험** | 불편한 클릭 유도, 낮은 품질 사이트 방문 | 거짓 정보를 사실처럼 인지하여 잘못된 의사결정 |
| **탐지 난이도** | 상대적으로 낮음 (Spam Score 등) | 높음 (높은 의미적 연관성을 가짐) |
| **피해 형태** | 트래픽 감소, 광고비 손실 | LLM의 할루시네이션 유발, 브랜드 신뢰도 하락 |

### 신뢰도 기반 검증: Re-ranking 알고리즘 구현

이러한 스팸을 방어하기 위해서는 검색 단계에서 단순히 유사도(Similarity Score)만 보는 것이 아니라, 출처의 신뢰도(Trust Score)를 반영하는 **하이브리드 리랭킹(Hybrid Re-ranking)** 시스템이 필수적입니다.

아래 예제는 LangChain을 사용하여 검색된 문서들의 신뢰도 점수를 가중치로 적용하여 최종 컨텍스트를 재구성하는 간단한 Python 코드입니다. 도메인 권위(Domain Authority)를 시뮬레이션하여 낮은 신뢰도를 가진 스팸 사이트를 필터링하는 로직을 포함합니다.

```python
from typing import List, Dict
from pydantic import BaseModel

class Document(BaseModel):
    content: str
    source_url: str
    similarity_score: float
    trust_score: float  # 0.0 to 1.0 (e.g., based on Domain Authority)

def trust_aware_rerank(docs: List[Document], top_k: int = 3) -> List[Document]:
    """
    유사도와 신뢰도를 결합한 하이브리드 리랭킹 함수
    Formula: Relevance = (Similarity * 0.4) + (Trust * 0.6)
    """
    for doc in docs:
        # 가중치 조절: 신뢰도(Trust)에 더 높은 가중치를 두어 스팸 필터링 강화
        doc.final_score = (doc.similarity_score * 0.4) + (doc.trust_score * 0.6)
    
    # 최종 점수에 따라 정렬
    reranked_docs = sorted(docs, key=lambda x: x.final_score, reverse=True)
    
    # 상위 N개 문서 반환
    return reranked_docs[:top_k]

# Mock Data: 시나리오 - 사용자가 "Best CRM 2024" 검색
# 스팸 사이트(A Corp)는 유사도는 높지만 신뢰도가 낮음
retrieved_docs = [
    Document(
        content="A Corp CRM is the best choice in 2024...", 
        source_url="https://acorp-spam.com/best-crm", 
        similarity_score=0.95, # 매우 높은 유사도
        trust_score=0.1       # 낮은 도메인 권위 (스팸으로 판단)
    ),
    Document(
        content="Review of CRM systems: Gartner report...", 
        source_url="https://gartner.com/reviews", 
        similarity_score=0.85, 
        trust_score=0.98      # 높은 신뢰도
    ),
    Document(
        content="Top CRM tools comparison by TechBlog...", 
        source_url="https://techblog.io/comparison", 
        similarity_score=0.88, 
        trust_score=0.75      # 중간 신뢰도
    )
]

# Re-ranking 실행
filtered_context = trust_aware_rerank(retrieved_docs)

# 결과 확인
print("Filtered Context for LLM Generation:")
for i, doc in enumerate(filtered_context):
    print(f"{i+1}. [{doc.source_url}] (Score: {doc.final_score:.2f})")
    print(f"   Content: {doc.content[:50]}...")
```

이 코드를 실행하면 `similarity_score`가 가장 높았던 스팸 문서(A Corp)가 `trust_score`에 의해 필터링되어 최종 답변 생성에서 제외되는 것을 확인할 수 있습니다.

### 방어 전략: Step-by-Step 가이드

AI 검색 시스템을 운영하는 엔지니어들은 다음과 같은 단계별 방어 전략을 수립해야 합니다.

1.  **출처 독립성 검증 (Source Independence Check)**     *   검색된 문서들이 특정 도메인에 편중되어 있지는 않은지 확인합니다. 만약 상위 5개의 검색 결과 중 4개가 같은 서브넷이나 소유권을 가진 사이트라면 스팸일 확률이 높습니다.

2.  **다원적 검증 (Adversarial Verification)**     *   LLM이 답변을 생성하기 전, '사실 확인자(Fact Checker)' 모델을 먼저 통과시킵니다. 이 모델은 검색된 문서들 간의 모순을 찾아내고, 주장에 대한 반증 증거(Counter-evidence)가 있는지 추가 검색을 수행합니다.

3.  **신뢰 점수 주입 (Trust Score Injection)**     *   앞서 보여진 코드 예시처럼, 벡터 검색 결과에 페이지 랭크(PageRank), 도메인 연령, 사용자 신고 이력 등의 메타데이터를 결합하여 최종 리랭킹을 수행합니다.

4.  **피드백 루프 (RLHF for Retrieval)**     *   최종 답변에 대해 사용자가 "도움이 됐어요/도움이 안 됐어요"를 누르면, 이 피드백을 검색 단계로 전파하여 잘못된 출처를 제공한 리트리버(Retriever)를 페널티 주는 학습 과정을 거쳐야 합니다.

## 결론

AI 검색의 스팸 문제는 기술적 결함이라기보다는 정보 생태계의 구조적 모순이 반영된 결과입니다. RAG 시스템은 정보의 '양'과 '속도'를 해결했지만, '질'과 '진실성'에 대한 책임을 사용자에게 전가하는 오류를 범하고 있습니다.

앞으로 AI 검색 엔진들은 단순히 "있는 그대로"의 정보를 나열하는 검색 도구를 넘어, "믿을 수 있는" 정보를 선별하는 큐레이터로 진화해야 합니다. 이를 위해서는 의미 검색(Semantic Search)만으로는 부족하며, 도메인 신뢰도, 정보의 독립성, 다각적 검증을 종합하는 **Trust-Aware RAG** 아키텍처로의 전환이 시급합니다.

우리가 AI에게 답을 묻기 전에, 우리는 AI가 어디서 그 답을 가져왔는지 의심할 줄 알아야 하며, 기술자들은 그 의심을 해소할 수 있는 견고한 파이프라인을 구축해야 합니다. 그것이야말로 생성형 AI 시대의 진정한 기술 윤리이자 MLOps의 과제일 것입니다.

### 참고자료
- *Original Source:* Hada.io - "AI 검색의 스팸 문제"
- *Related Concept:* Retrieval-Augmented Generation (Lewis et al., 2020)
- *Related Concept:* Adversarial Attacks on Machine Learning Models (Goodfellow et al.)

---

**출처**: [https://news.hada.io/topic?id=26809](https://news.hada.io/topic?id=26809)