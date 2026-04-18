---
title: "🤖 SQL 기반 RAG: Azure Vector Search와 LangChain 구현"
date: 2026-04-19T08:06:14+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
---

## 서론

수많은 기업이 생산형 AI(Generative AI) 도입을 꿈꾸지만, 현실의 데이터는 복잡하게 얽혀 있습니다. 기업의 핵심 데이터인 고갈 로그, 재고 현황, 금융 거래 내역 등 대부분은 이미 관계형 데이터베이스(RDBMS) 안에 깊이 저장되어 있습니다. 전통적인 RAG(Retrieval-Augmented Generation) 아키텍처를 구축하려면 이 정형 데이터를 별도의 벡터 데이터베이스(Vector DB)로 이동시키는 ETL 파이프라인을 구축해야 했습니다. 이는 데이터 중복(Data Redundancy), 동기화 지연(Synchronization Lag), 그리고 두 개의 서로 다른 데이터베이스 시스템을 관리해야 하는 운영상의 복잡성을 야기했습니다.

만약 데이터가 있는 곳에서 곧바로 벡터 검색을 수행할 수 있다면 어떨까요? Azure SQL Database와 Microsoft Fabric은 최근 네이티브 벡터 검색 기능을 도입하여 이 가능성을 현실로 만들었습니다. 별도의 전용 벡터 엔진 없이도, 우리가 매일 접하는 SQL 환경 내에서 고차원 벡터를 저장하고 인덱싱하며, 초고속으로 유사도 검색을 수행할 수 있게 된 것입니다. 이 글에서는 기존의 데이터 웨어하우스 인프라를 유지하면서도 LangChain을 통해 어떻게 강력한 RAG 시스템을 구축할 수 있는지, 그 기술적 원리와 구현 방법을 심도 있게 다루고자 합니다.

## 본론

### 기술적 배경: SQL 내의 벡터화

RAG의 핵심은 "검색(Retrieval)"입니다. LLM이 사실에 기반한 답변을 생성하려면 관련 문서를 정확히 찾아내야 합니다. 전통적으로는 문서를 임베딩 모델(예: `text-embedding-3-small`)을 통해 벡터로 변환하고, 이를 Pinecone, Milvus 같은 전용 DB에 저장했습니다.

Azure SQL의 네이티브 벡터 검색은 이 과정을 데이터베이스 계층으로 내렸습니다. 기술적으로 살펴보면 다음과 같은 메커니즘이 작동합니다.

1.  **데이터 타입 지원**: `VECTOR(N)` 데이터 타입이 추가되어, N차원의 부동 소수점 배열(FP32 또는 FP16)을 테이블의 컬럼으로 직접 저장할 수 있습니다. 2.  **인덱싱 알고리즘**: 내부적으로 HNSW(Hierarchical Navigable Small World)와 같은 근사 최근접 이웃(Approximate Nearest Neighbor, ANN) 알고리즘을 구현하여, 수백만 개의 벡터라도 밀리초 단위로 검색합니다. 3.  **거리 함수**: `DOT_DISTANCE`, `EUCLIDEAN_DISTANCE`와 같은 내장 함수를 통해 SQL 쿼리문 안에서 바로 벡터 간의 유사도를 계산할 수 있습니다.

이 아키텍처의 가장 큰 장점은 **데이터 중복의 제거**입니다. 메타데이터(구조적 데이터)와 벡터 임베딩(비구조적 데이터)이 동일한 행(Row)에 존재하므로, 데이터 무결성이 자동으로 보장되며 관리 포인트가 줄어듭니다.

### 아키텍처 흐름

LangChain과 Azure SQL을 통합한 RAG 파이프라인은 다음과 같은 단계로 데이터가 처리됩니다. 아래 다이어그램은 문서 수집부터 질의응답까지의 전체 흐름을 보여줍니다.

```javascript
graph LR
    A[Raw Documents] --> B[LangChain Text Splitter]
    B --> C[Azure OpenAI Embedding Model]
    C --> D[Azure SQL Database]
    D --> E[Vector Index]
    
    F[User Query] --> G[Query Embedding]
    G --> H[Azure SQL Vector Search]
    H --> D
    D --> I[Retrieved Context]
    I --> J[LLM Generation]
    J --> K[Final Answer]
```

### 구현 가이드: LangChain과 Azure SQL 통합

이제 실제 코드를 통해 어떻게 구현하는지 살펴보겠습니다. Python의 LangChain 라이브러리와 `azure-identity`를 활용하여 Azure SQL에 벡터를 저장하고 검색하는 과정을 단계별로 설명합니다.

#### 1. 환경 설정 및 연결

먼저 필요한 라이브러리를 설치하고 데이터베이스 연결을 구성합니다.

```bash
pip install langchain langchain-community langchain-openai azure-identity
```

```python
from langchain_community.vectorstores import AzureSQLVectorStore
from langchain_openai import AzureOpenAIEmbeddings
from azure.identity import DefaultAzureCredential

# Azure OpenAI 임베딩 모델 설정 (환경 변수 또는 직접 입력)
embeddings = AzureOpenAIEmbeddings(
    azure_deployment="text-embedding-3-small",
    openai_api_version="2024-02-15-preview"
)

# Azure SQL 데이터베이스 연결 문자열 설정
# 서버 이름, 데이터베이스 이름 등은 실제 환경에 맞게 수정
connection_string = "mssql+pyodbc://<username>:<password>@<server>.database.windows.net/<dbname>?driver=ODBC+Driver+18+for+SQL+Server"

# AzureSQLVectorStore 인스턴스화
vector_store = AzureSQLVectorStore(
    connection_string=connection_string,
    embedding_function=embeddings,
    table_name=" rag_documents "
)
```

#### 2. 문서 임베딩 및 저장

LangChain의 문서 로더와 분할기를 사용하여 텍스트를 적절한 크기(Chunk)로 나누고 데이터베이스에 저장합니다.

```python
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 1. 문서 로드
loader = TextLoader("./harry_potter_summary.txt")
documents = loader.load()

# 2. 텍스트 분할 (Chunking)
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
)
splits = text_splitter.split_documents(documents)

# 3. Azure SQL에 벡터 저장
# 이 과정에서 자동으로 임베딩이 생성되어 DB의 VECTOR 컬럼에 저장됩니다.
vector_store.add_documents(documents=splits)
```

#### 3. 유사도 검색 (Similarity Search)

이제 사용자의 질문(Query)을 벡터로 변환하여 가장 관련성이 높은 문서 조각을 검색합니다.

```python
query = "해리 포터는 호그와트에서 어떤 마법을 배우나요?"

# 유사도 검색 수행 (k=4: 상위 4개 문서 반환)
results = vector_store.similarity_search(query, k=4)

for res in results:
    print(f"Content: {res.page_content}
Metadata: {res.metadata}
")
```

### 비교 분석: 전용 Vector DB vs. Azure SQL Native Vector

기존의 방식과 Azure SQL을 활용한 방식의 차이를 명확히 이해하는 것이 중요합니다. 아래 표는 두 접근 방식의 주요 차이점을 비교 분석한 것입니다.

| 비교 항목 | 전용 Vector DB (Pinecone, Milvus 등) | Azure SQL Native Vector | | :--- | :--- | :--- | | **데이터 아키텍처** | Polyglot Persistence (데이터 분산 저장) | Unified Storage (단일 저장소) | | **데이터 동기화** | ETL 파이프라인 필수 (지연 발생 가능) | 실시간 트랜잭션 내 저장 (즉시 반영) | | **운영 복잡도** | DB 인프라 이중 관리 필요 | 기존 SQL DB 인프라 재활용 | | **확장성 (Scalability)** | 수십억 개 벡터 처리에 최적화 | 중소 규모 ~ 중대 규모에 적합 (Fabric으로 확장 가능) | | **주요 사용 사례** | 대규모 글로벌 서비스, 전용 AI 서비스 | 기업 내부 데이터, 하이브리드 검색 (RDB + Vector) |

**실무 관점의 인사이트**: 기업의 B2E(Business-to-Employee) 서비스나 이미 방대한 메타데이터가 SQL에 존재하는 경우, 전용 Vector DB를 도입하는 것보다 Azure SQL의 기능을 활용하는 것이 훨씬 효율적일 수 있습니다. 특히 **하이브리드 검색(Hybrid Search)**이 필요한 시나리오에서 강력합니다. 예를 들어, "2023년에 판매된 `제품 A`의 `매뉴얼` 내용 중 `배터리 교체 방법`을 알려줘"와 같은 쿼리는 `WHERE year=2023 AND product='A'`(필터링)와 벡터 검색(매뉴얼 내용)이 결합되어야 합니다. Azure SQL은 이런 복합 조건 쿼리를 단일 쿼리문으로 최적화하여 처리할 수 있습니다.

## 결론

Azure SQL과 Microsoft Fabric의 네이티브 벡터 검색 기능은 "벡터 데이터베이스는 반드시 별도로 존재해야 한다"는 통념을 깨고 있습니다. 딥러닝 모델의 임베딩 출력을 관계형 데이터의 일부로 취급함으로써, 우리는 데이터 사일로(Silo)를 허물고 훨씬 더 단순하고 강력한 RAG 파이프라인을 구축할 수 있게 되었습니다.

이 접근 방식의 핵심 가치는 **데이터 중심의 AI**입니다. AI 모델을 위해 데이터를 옮기는 것이 아니라, 데이터가 있는 곳으로 AI 기능을 가져오는 것입니다. 특히 보안이 엄격한 금융, 의료, 공공 기관 등에서 데이터 이동을 최소화하고 기존의 거버넌스 체계를 유지하면서 생성형 AI 기능을 확장할 수 있는 최적의 솔루션이 될 것입니다.

앞으로의 연구 방향으로는 SQL 엔진 내부에서의 quantization(양자화) 기술 고도화를 통한 메모리 사용량 최적화와, Microsoft Fabric 내의 Real-Time Intelligence와의 결합을 통해 더욱 저지연성을 요구하는 추천 시스템 등으로의 확장이 기대됩니다.

### 참고자료
- [Microsoft Learn - Introducing vector search in Azure SQL Database](https://learn.microsoft.com/en-us/azure/azure-sql/database/vector-search)
- [LangChain Documentation - Azure SQL VectorStore](https://python.langchain.com/docs/integrations/vectorstores/azure_sql)
- [arXiv: Vector Database Systems: A Survey](https://arxiv.org/abs/2307.05344)

---

**출처**: [https://news.hada.io/topic?id=26824](https://news.hada.io/topic?id=26824)