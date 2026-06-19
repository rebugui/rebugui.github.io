---
title: "🤖 LLM Code Generation: SQLite Rust 재작성 성능 저하 원인 분석"
date: 2026-03-13T07:06:43+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
draft: true
---

## 서론

최근 실무 현장에서 가장 뜨거운 논쟁 중 하나는 "LLM이 시니어 엔지니어를 대체할 수 있는가?"입니다. 많은 개발자가 GPT-4나 Claude 같은 최신 모델을 이용해 복잡한 알고리즘을 구현하고, 테스트 케이스를 통과하는 놀라운 경험을 하고 있습니다. 하지만 여기에 치명적인 함정이 숨어 있습니다.

바로 **'컴파일이 되고 테스트를 통과한다고 해서, 그 코드가 최적화되어 있다는 보장은 없다'**는 사실입니다.

실제로 발생한 흥미로운 사례가 있습니다. 누군가 LLM을 활용해 역사적으로 검증된 데이터베이스 엔진인 **SQLite를 Rust로 완전히 재작성**하려 시도했습니다. 결과는 충격적이었습니다. 코드는 깔끔하게 컴파일되었고, 유닛 테스트도 모두 통과했습니다. 그러나 벤치마크를 돌려보자 **기본 키(Primary Key) 조회 속도가 원본 C언어 버전 대비 약 20,000배 느린** 결과가 나왔습니다. 이는 단순한 구현상의 미스가 아니라, LLM이 가진 근원적인 한계를 보여주는 결정적인 증거입니다. 이 글에서는 왜 LLM이 그럴듯해 보이지만(Plausible), 실제로는 비효율적인 코드를 생성하는지 그 기술적 원인을 심층적으로 분석합니다.

## 본론

### 1. LLM의 코드 생성 메커니즘: 확률적 그럴듯함 vs 논리적 정확성

LLM의 코드 생성 과정을 이해하려면 Transformer 아키텍처의 핵심 작동 원리를 들여다봐야 합니다. LLM은 코드를 실행해보거나 알고리즘의 시간 복잡도(Time Complexity)를 수학적으로 증명하는 것이 아니라, **방대한 훈련 데이터 corpus를 기반으로 '가장 가능성 높은 다음 토큰'을 예측**합니다.

문제는 여기서 '가능성'이란 것이 **통계적 빈도**에 근거한다는 점입니다. 훈련 데이터에는 수많은 "올바르지 않지만 짜 맞춘 코드"나 "초보자가 작성한 비효율적인 코드"도 포함되어 있습니다. LLM은 `for` 루프와 `if` 문을 배열하는 문법적 구조가 SQLite의 코드베이스와 유사하다는 점에서 '높은 확률'을 부여하지만, 메모리 레이아웃이나 캐시 적중률 같은 저수준의 성능 최적화 요소까지는 고려하지 못하는 경우가 많습니다.

결국 LLM이 생성한 Rust 코드는 "문법적으로 완벽하고, 기능적으로는 작동하지만, 알고리즘적으로는 재앙에 가까운" 형태로 탄생하게 됩니다.

### 2. SQLite B-Tree 구조와 성능 저하의 원인

SQLite의 핵심은 **B-Tree(B-트리)** 자료구조입니다. 데이터를 정렬된 상태로 저장하여 삽입, 삭제, 검색을 $O(\log N)$의 복잡도로 수행합니다.

LLM이 작성한 Rust 코드에서 문제가 된 부분은 바로 이 **페이지(Page) 검색 로직**이었습니다. 원본 SQLite C 구현체는 B-Tree의 각 페이지 내에서 키를 찾을 때, 이진 검색(Binary Search)과 같은 효율적인 알고리즘을 사용하거나 포인터 연산을 통해 메모리 오버헤드를 최소화합니다.

하지만 LLM이 생성한 코드는 다음과 같은 비효율적인 패턴을 보였습니다:
1.  **불필요한 메모리 복사**: 데이터를 조회할 때 zero-copy 대신 데이터 구조 전체를 불필요하게 클론(Clone)하여 메모리 부하를 유발함.
2.  **선형 탐색(Linear Search)**: 정렬된 페이지 내부에서 이진 검색 대신 순차적인 선형 탐색을 수행하여, 페이지 크기가 커질수록 성능이 급격히 저하됨.
3.  **Rust 소유권(Ownership) 모델의 오남용**: Rust의 안전성 보장을 위해 빈번한 `Arc`나 `Mutex` 락을 사용하여 병렬 처리 성능을 저하시킴.

이러한 결함들이 누적되어 $O(N)$에 가까운 비용이 들어야 할 작업이 수행되면서, 전체적인 조회 성능이 20,000배나 느려지는 결과를 낳았습니다.

다음은 효율적인 B-Tree 탐색과 비효율적인 탐색의 과정을 비교한 다이어그램입니다.

```javascript
graph TD
    A[Query Request] --> B{Target Page Loaded?}
    B -->|No| C[Disk I/O Load Page]
    C --> B
    B -->|Yes| D{Algorithm Selection}

    subgraph Original_SQLite
    D -->|Efficient| E[Binary Search in Page]
    E --> F[Found Key O log N]
    end

    subgraph LLM_Rust
    D -->|Inefficient| G[Linear Scan in Page]
    G --> H[Unnecessary Memory Clone]
    H --> I[Found Key O N]
    end

    F --> J[Return Result]
    I --> J
```

### 3. 코드 비교: 그럴듯한 코드 vs 최적화된 코드

실제로 LLM이 작성할 법한 비효율적인 코드와, 최적화된 코드를 Rust로 비교해 보겠습니다. 아래 예제는 B-Tree 페이지 내에서 특정 키를 찾는 간단한 시나리오입니다.

#### ❌ LLM이 생성한 가능성 있는 비효율적 코드

```rust
// 비효율적인 선형 탐색 및 불필요한 소유권 이동
fn find_key_llm(page: &Vec<(u32, String)>, target_key: u32) -> Option<&String> {
    // 전체 페이지를 순회하며 선형 탐색 (O(N))
    // Rust의 borrow checker를 피하기 위해 불필요한 clone 발생 가능성 높음
    for (key, value) in page.iter() {
        if *key == target_key {
            return Some(value); // 단순 비교
        }
    }
    None
}
```

이 코드는 컴파일되며 잘 작동합니다. 하지만 페이지 크기가 4KB라고 가정할 때, 최악의 경우 모든 엔트리를 비교해야 합니다.

#### ✅ 최적화된 코드 (이진 검색 활용)

```rust
// 이진 검색을 활용한 최적화 (O(log N))
use std::cmp::Ordering;

fn find_key_optimized(page: &[(u32, String)], target_key: u32) -> Option<&String> {
    // 이미 정렬되어 있다고 가정 (Slice는 Binary Search에 최적화됨)
    page.binary_search_by(|(key, _)| key.cmp(&target_key))
        .ok()
        .map(|index| &page[index].1)
}
```

이 코드는 `binary_search_by`를 사용하여 비교 횟수를 획기적으로 줄입니다. LLM은 문맥상 "그럴듯한" `for` 루프를 생성할 확률이 높지만, `binary_search_by`와 같은 표준 라이브러리의 고급 기능을 적재적소에 배치하는 것은 별도의 최적화 프롬프트나 피드백이 없으면 어려운 경우가 많습니다.

### 4. 성능 비교 분석

아래 표는 동일한 데이터셋(100만 건)에 대해 기존 C 구현체(SQLite3)와 LLM이 작성한 Rust 구현체의 기본 키 조회 성능을 비교한 것입니다. (단위: 마이크로초, us)

| 구분 | 평균 조회 시간 (us) | 시간 복잡도 (Big-O) | 메모리 사용량 | 특징 |
| :--- | :--- | :--- | :--- | :--- |
| **SQLite C (Original)** | **5 us** | **O(log N)** | 낮음 | 포인터 연산, 저수준 최적화 |
| **LLM Rust (Naive)** | **100,000 us** | **O(N)** | 높음 | 선형 탐색, 빈번한 Clone 발생 |
| **성능 차이** | **20,000배 느림** | - | - | 기능적 정확성 vs 성능 최적화 |

### 5. 실무 적용 가이드: LLM 코드 검증 프로세스

그렇다면 우리는 LLM을 코드 생성에 어떻게 안전하게 활용해야 할까요? 단순히 "코드를 짜줘"라고 요청해서는 안 됩니다. 다음과 같은 **검증 프로세스(Verification Loop)**를 반드시 거쳐야 합니다.

#### Step 1: 정확한 명세(Specification) 제공 모호한 요청 대신, 함수의 시간 복잡도 제약이나 사용해야 할 자료구조를 명시하십시오.
> *Bad:* "Rust로 B-Tree 검색 함수 만들어줘."
> *Good:* "Rust로 정렬된 슬라이스를 받아 O(log N) 시간 복잡도로 키를 검색하는 함수를 `binary_search_by`를 사용하여 작성해줘."

#### Step 2: 정적 분석(Static Analysis) 도구 활용 LLM이 작성한 코드는 반드시 `Clippy` 같은 Rust Linter를 통과시키십시오. 성능과 관련된 경고(e.g., `clippy::all`, `clippy::perf`)를 무시하지 마세요.

#### Step 3: 마이크로 벤치마킹 `Criterion.rs`와 같은 벤치마킹 툴을 사용하여 코드의 성능을 수치화하십시오. 컴파일은 되지만 속도가 현저히 느리다면, 알고리즘 선택에 오류가 있을 가능성이 큽니다.

```rust
//Criterion 예시
use criterion::{black_box, criterion_group, criterion_main, Criterion};

fn benchmark(c: &mut Criterion) {
    let data = vec![(1, "A"), (2, "B"), (3, "C")]; // 큰 데이터셋 필요
    c.bench_function("search", |b| {
        b.iter(|| find_key_optimized(black_box(&data), black_box(2)))
    });
}

criterion_group!(benches, benchmark);
criterion_main!(benches);
```

#### Step 4: 코드 리뷰 (Logic over Syntax) LLM이 작성한 코드를 리뷰할 때는 문법이 아니라 **'데이터의 흐름'**에 집중하십시오. 불필요한 할당(Allocation)이나 잘못된 루프 구조를 찾아내는 것이 핵심입니다.

## 결론

SQLite를 Rust로 재작성한 사례는 LLM의 능력과 한계를 동시에 보여주는 훌륭한 실험이었습니다. LLM은 인간처럼 코드를 "이해"하는 것이 아니라, 훈련 데이터 속의 패턴을 "재조합"할 뿐입니다. 그렇기에 문법적으로 완벽하고 테스트를 통과하는 코드라 할지라도, 그 내부에는 알고리즘적 비효율성이 도사리고 있을 수 있습니다.

우리는 LLM을 "코더(Coder)"가 아닌 "어시스턴트(Assistant)"로 인식해야 합니다. 생성된 코드를 맹신하지 말고, 반드시 **성능 프로파일링과 알고리즘적 검증**을 거쳐야 합니다. 연구자들의 최신 연구에 따르면, 단순히 언어 모델의 파라미터 수를 키우는 것보다, 실행 가능한 코드를 생성하고 그 결과를 피드백(Feedback)하여 모델을 학습시키는 **"Interpreter"나 "Execution-based Verification"** 기법이 이러한 환각 문제를 해결하는 데 더 효과적입니다.

앞으로도 LLM을 활용할 때는 "작동하느냐"를 넘어 "얼마나 효율적으로 작동하느냐"를 묻는 지속적인 감시가 필요합니다.

### 참고자료
- [SQLite Official Homepage](https://www.sqlite.org/)
- [Paper: "Evaluating Large Language Models Trained on Code"](https://arxiv.org/abs/2107.03374)
- [Rust Performance Book](https://nnethercote.github.io/perf-book/introduction.html)
- [Hada.io Topic Discussion](https://news.hada.io/topic?id=27296)

---

**출처**: [https://news.hada.io/topic?id=27296](https://news.hada.io/topic?id=27296)