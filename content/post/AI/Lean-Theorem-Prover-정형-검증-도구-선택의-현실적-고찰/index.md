---
title: "Lean Theorem Prover: 정형 검증 도구 선택의 현실적 고찰"
date: 2026-04-29T01:06:46+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
---

## 서론

최근 생성형 AI가 작성한 코드가 상용 소프트웨어에 통합되면서, "AI가 만든 코드를 어떻게 신뢰할 것인가?"라는 문제가 산업계의 뜨거운 감자가 되었습니다. ChatGPT나 GitHub Copilot이 놀라운 생산성을 제공하지만, 때로는 미묘하면서도 치명적인 논리적 결함을 만들어내기도 합니다. 이러한 불확실성 속에서 소프트웨어 검증의 최후의 보루로 떠오르고 있는 기술이 바로 '정형 검증(Formal Verification)'입니다.

그러나 정형 검증 커뮤니티 내에서도 도구 선택을 둘러싼 치열한 논쟁이 벌어지고 있습니다. 특히 마이크로소프트의 지원을 받는 Lean 4와 그 방대한 수학 라이브러리(Mathlib)가 급부상하면서, 많은 연구자와 엔지니어들이 "Why not just use Lean?"이라는 질문을 던지고 있습니다. 수십 년간 정형 검증의 표준으로 군림해 온 Isabelle/HOL의 창시자인 Lawrence Paulson조차 이러한 흐름을 주시하며, 단순한 유행을 넘어 기술적 트레이드오프에 대해 심도 있게 고찰할 필요성을 역설하고 있습니다.

본 글에서는 Lean의 약진이 가져온 생태계의 변화를 분석하고, Isabelle/HOL과 같은 기존 도구와의 기술적 차이를 비교합니다. 나아가 AI 기반 자동 증명(Automated Theorem Proving) 연구 환경 구축 시, 어느 도구를 선택하는 것이 현명한지에 대한 기준을 제시하고자 합니다.

## 본론

### 정형 검증 도구의 기술적 토대: 타입 이론의 갈림길

정형 검증 도구를 이해하려면 그 바탕에 깔린 논리 체계, 즉 타입 이론(Type Theory)을 이해해야 합니다. Lean과 Isabelle은 근본적인 철학에서부터 차이를 보입니다.

**Lean**은 '의존 타입 이론(Dependent Type Theory)'에 기반하고 있습니다. 여기서 타입은 값에 의존할 수 있어, 수학적 명제와 프로그래밍의 타입을 일대일로 대응시키는 'Curry-Howard Correspondence'를 매우 강력하게 구현합니다. 이는 복잡한 수학적 구조를 코드 안에 직접 매핑하기에 매우 적합합니다.

반면 **Isabelle/HOL**은 '고계 논리(Higher-Order Logic)'를 사용합니다. 이는 의존 타입만큼 표현력이 높지는 않지만, 그 대신 논리적 일관성을 유지하기가 더 쉽고 검증기(Kernel)의 신뢰성 확보가 유리합니다. Paulson 교수가 지적하는 것처럼, Lean의 강력한 표현력은 배우는 사람의 진입 장벽을 높이고, 증명을 관리하는 복잡도를 증가시킬 수 있습니다.

### Lean 증명 프로세스의 아키텍처

Lean이 어떻게 증명을 구성하고 검증하는지 이해하기 위해, 내부 처리 과정을 간소화하여 도식화했습니다. 사용자는 '전략(Tactic)'이라는 명령어를 사용하여 증명을 단계별로 구성하고, 이를 시스템이 처리합니다.

```javascript
graph LR
    A[사용자 입력 Tactic] --> B[Tactic Interpreter]
    B --> C[Proof State 업데이트]
    C --> B
    C --> D[구성된 Term Proof]
    D --> E[Kernel Type Checker]
    E --> F{Type Checking 결과}
    F -->|성공| G[Trusted Theorem 저장]
    F -->|실패| H[에러 리포트]
```

이 아키텍처에서 가장 핵심은 **Kernel Type Checker**입니다. 사용자가 작성한 고수준의 증명 스크립트(Tactic)가 최종적으로 커널을 통과할 때, 수학적으로 엄밀한 타입 검사를 거쳐야만 정리(Theorem)로 인정받습니다. Lean 4는 이 과정을 매우 효율적으로 최적화하여, 사용자가 대화형으로 증명을 작성할 때 즉각적인 피드백을 제공합니다.

### 코드로 보는 Lean의 강력함: Mathlib 생태계

Lean의 인기 비결 중 하나는 **Mathlib**이라 불리는 방대한 표준 라이브러리입니다. 이는 단순한 함수 모음이 아니라, 수천 년간의 인류 수학 지식이 형식화된 데이터베이스입니다. AI 연구자들에게 이는 "ImageNet이 컴퓨터 비전에 끼친 영향"과 유사한 효과를 냅니다.

아래는 Lean 4를 사용하여 자연수의 덧셈에 대한 교환 법칙(`a + b = b + a`)을 증명하는 간단한 예시입니다. `simp`와 같은 전략(tactic)이 얼마나 강력한 자동화를 제공하는지 확인할 수 있습니다.

```plain text
import Mathlib.Data.Nat.Basic

theorem add_comm (a b : Nat) : a + b = b + a := by
  -- 자동 증명 전략(simp)을 사용하여 Nat.add_comm 정리를 적용
  simp [Nat.add_comm]

-- 혹은 단계별 증명 (Step-by-step)
theorem add_comm_manual (a b : Nat) : a + b = b + a := by
  induction a with
  | zero =>
    -- base case: 0 + b = b + 0
    rw [Nat.zero_add]
    rw [Nat.add_zero]
  | succ n ih =>
    -- inductive step: n.succ + b = b + n.succ
    rw [Nat.add_succ, ih, Nat.succ_add]
```

이 코드에서 `rw` (rewrite)는 정리를 이용해 등식을 치환하는 전략이며, `induction`은 수학적 귀납법을 수행합니다. `Mathlib`에는 `Nat.add_comm`과 같은 기초 정리들이 이미 증명되어 있어, 사용자는 복잡한 문제를 해결할 때 이들을 레고 블록처럼 조립하여 사용할 수 있습니다.

### Lean vs. Isabelle: 선택의 기준

AI 연구자나 엔지니어가 도구를 선택할 때 고려해야 할 현실적인 비교 지표를 정리했습니다. Lawrence Paulson의 관점을 반영하여, 단순히 "최신"이라는 이유만으로 Lean을 선택하는 것의 위험성과 기회비용을 분석했습니다.

| 비교 항목 | Lean 4 (+ Mathlib) | Isabelle/HOL |
| :--- | :--- | :--- |
| **타입 시스템** | **의존 타입 (CIC)** - 매우 높은 표현력 | **Simple Types (HOL)** - 상대적으로 단순하고 안정적 |
| **자동화 (Automation)** | Tactic 기반, 최근 AI 툴(Copilot 등)과의 연계성 강점 | **Sledgehammer** - 외부 강력한 ATP solvers (Vampire, E)와의 연계 최고 |
| **학습 곡선** | 가파름 (의존 타입, 독특한 문법) | 상대적으로 완만 (Isar 언어가 인간에게 더 친숙함) |
| **AI 데이터 활용** | **최상** (Mathlib의 규모와 통합성 덕분에 LLM 학습에 적합) | 제한적 (AFP는 있으나 분산되어 있음) |
| **컴파일 속도** | 빠름 (Lean 4는 자체적으로 최적화된 컴파일러 사용) | 상대적으로 느림 (ML/TLI 인터프리터 방식) |

### AI 기반 자동 증명을 위한 도구 선택 가이드

LLM(대규모 언어 모델)을 활용한 정형 검증 연구를 계획하고 있다면, 다음 단계에 따라 도구를 결정하는 것을 추천합니다.

1.  **데이터 중심 접근 (Data-Centric AI)**     연구의 핵심이 '모델이 증명을 얼마나 잘

---

**출처**: [https://lawrencecpaulson.github.io//2026/04/23/Why_not_Lean.html](https://lawrencecpaulson.github.io//2026/04/23/Why_not_Lean.html)