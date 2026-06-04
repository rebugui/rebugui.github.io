---
title: "Binary-Level ECP: 레거시 펌웨어 동등 클래스 추론 및 테스트 기법"
date: 2026-04-29T01:06:49+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 서론

자동차 산업의 현장에서 보안 연구자로서 마주하는 가장 골치 아픈 상황 중 하나는 바로 "유령 펌웨어(Ghost Firmware)"입니다. 개발자는 퇴사했고, 소스 코드는 분실되었으며, 남은 것은 10년 전에 컴파일된 ECU(전자 제어 유닛)의 바이너리 이미지뿐인 상황을 상상해 보세요. 그런데 ISO 26262와 같은 기능 안전 표준 준수를 위해 이 레거시 펌웨어에 대한 체계적인 테스트를 증명해야 합니다.

전통적인 테스트 설계 기법인 동등 클래스 분할(Equivalence Class Partitioning, ECP)은 입력 조건에 따라 출력을 그룹화하여 테스트 케이스를 최적화합니다. 하지만 이는 명세서(Specification)가 전제되어야 가능합니다. 명세서가 없는 블랙박스 상태의 바이너리에서 어떻게 동등 클래스를 정의할 수 있을까요?

단순히 "업데이트하라"고 조언할 수 없는 상황입니다. 우리는 리버스 엔지니어링과 심볼릭 실행(Symbolic Execution)을 무기로 삼아, 소스 코드 없이도 펌웨어 내부의 논리를 파헤치고 동등 클래스를 자동으로 추론하는 방법론이 필요합니다. 이는 단순한 학술적 호기심을 넘어, 안전과 생명이 달린 자동차 소프트웨어를 검증하기 위한 필수적인 생존 기술입니다.
> **⚠️ 윤리적 경고**: 본문에서 다루는 바이너리 분석 및 심볼릭 실행 기술은 오직 보안 취약점 진단, 레거시 시스템의 안전성 검증 및 방어 목적으로만 사용되어야 합니다. 허가되지 않은 시스템에 대한 무단 분석은 불법이며, 반드시 책임감 있는 화이트 해킹 윤리 강령을 준수해야 합니다.

## 본론: 바이너리 레벨 동등 클래스 추론의 원리

레거시 펌웨어에서 동등 클래스를 추론하는 핵심 아이디어는 "관찰 가능한 행동(Observable Behavior)"에 기반합니다. 우리는 함수 내부의 복잡한 로직을 이해하려고 애쓰는 대신, 특정 입력이 주어졌을 때 **어떤 경로를 거쳐 어떤 결과값(Return Value)을 내뱉는지**에 집중합니다.

이 과정은 크게 1) 제어 흐름(Control Flow) 재구성, 2) 안내된 심볼릭 실행(Guided Symbolic Execution), 3) 동등 클래스 그룹화의 세 단계로 나뉩니다. 안내된 심볼릭 실행은 무작위 퍼징(Fuzzing)과 달리, 코드의 모든 분기(Branch)를 수학적으로 커버하면서 입력값이 가져야 할 제약 조건(Constraint)을 해결합니다.

이러한 접근 방식의 전체적인 워크플로우를 시각화하면 다음과 같습니다.

```javascript
graph LR
    A[Legacy Firmware Binary] --> B[Control Flow Graph CFG Reconstruction]
    B --> C[Target Function Selection]
    C --> D[Symbolic Execution Engine]
    D --> E[Path Exploration]
    E --> F[SMT Solver Constraints]
    F --> G[Observable Behavior Analysis]
    G --> H{Output/State Comparison}
    H -- Indistinguishable --> I[Group to Equivalence Class A]
    H -- Distinguishable --> J[Group to Equivalence Class B]
    I --> K[Test Case Generation]
    J --> K
```

위 다이어그램에서 볼 수 있듯이, 우리는 바이너리를 분석하여 CFG(Control Flow Graph)를 복원한 뒤, 심볼릭 실행 엔진을 통해 각 경로를 탐색합니다. 이때 SMT Solver(Z3 등)를 사용하여 특정 경로로 도달하기 위한 입력 조건을 계산하고, 최종적으로 함수의 반환 값이나 메모리 상태가 동일한 경로들을 하나의 "동등 클래스"로 묶게 됩니다.

## 실무 적용 가이드: 심볼릭 실행을 이용한 분석

이제 실제 현장에서 이 방법론을 어떻게 적용하는지 구체적인 시나리오와 코드를 통해 살펴보겠습니다. 가령, 악의적인 입력이 들어왔을 때 차량의 통신 제어 함수가 어떻게 반응하는지 분석해야 하는 상황을 가정해 봅시다.

### 공격 시나리오 및 분석 대상

레거시 펌웨어의 `CAN_Parse_Msg` 함수는 입력된 메시지 ID에 따라 다른 처리를 수행합니다. 우리는 소스 코드가 없지만, 동적 분석과 정적 분석을 통해 이 함수가 입력값(`msg_id`)의 범위에 따라 3가지 다른 에러 코드를 반환한다는 것을 추측했습니다.

### PoC: Python과 Angr를 활용한 경로 분석

아래는 Python의 `angr` 프레임워크를 사용하여, 특정 바이너리 함수에서 입력값에 따른 동등 클래스를 추론하는 개념 증명(PoC) 코드입니다. 이 코드는 실제 펌웨어 분석 과정을 단순화한 예시입니다.

```python
import angr
import claripy

def analyze_equivalence_classes(binary_path, function_addr):
    # 프로젝트 로드
    project = angr.Project(binary_path, auto_load_libs=False)
    
    # 함수의 시작 상태 생성
    state = project.factory.blank_state(addr=function_addr)
    
    # 심볼릭 입력 변수 생성 (예: 4바이트 정수 입력)
    input_symbol = claripy.BVS('input_symbol', 32)
    
    # 레지스터에 심볼릭 변수 설정 (ARM 아키텍처 가정: R0)
    state.regs.r0 = input_symbol
    
    # 시뮬레이션 매니저 생성
    simgr = project.factory.simulation_manager(state)
    
    # 경로 탐색 (함수 종료까지)
    # explore 함수는 특정 조건(여기서는 함수의 리턴 지점)을 찾을 때까지 실행
    simgr.explore(find=0x40000400) # 종료 주소는 예시
    
    equivalence_classes = {}

    if simgr.found:
        for found_state in simgr.found:
            # 관찰 가능한 행동: 반환 값 (R0 레지스터)
            output_val = found_state.solver.eval(found_state.regs.r0)
            
            # 해당 출력에 도달하기 위한 입력 조건 해결
            input_constraints = found_state.solver.eval(input_symbol)
            
            # 동등 클래스 그룹화
            if output_val not in equivalence_classes:
                equivalence_classes[output_val] = []
            
            equivalence_classes[output_val].append(input_constraints)
            
    return equivalence_classes

# 사용 예시
# classes = analyze_equivalence_classes('legacy_firmware.elf', 0x40000100)
# print(f"Detected Classes: {classes.keys()}")
```

이 코드는 심볼릭 변수 `input_symbol`을 함수의 입력으로 전달하고, 프로그램이 실행되면서 가능한 모든 경로를 탐색합니다. `output_val`(반환값)이 같다면, 서로 다른 입력이라도 시스템 내부적으로 동일한 취급을 받는다고 볼 수 있으므로 하나의 동등 클래스로 분류됩니다.

### 기존 방식 대비 Binary-Level ECP의 효율성

이 방법론이 기존의 수동 분석이나 무작위 테스트에 비해 얼마나 효과적인지 비교해 보겠습니다.

| 비교 항목 | 기존 문서 기반 ECP (명세서 있음) | 레거시 수동 리버싱 | Binary-Level ECP (제안 방식) |
| :--- | :--- | :--- | :--- |
| **선행 조건** | 완벽한 명세서 (Requirements) | 고수준 어셈블리 전문가 | 컴파일된 바이너리만 있으면 됨 |
| **분석 시간** | 매우 빠름 (설계 단계) | 매우 느림 (주당 수십 함수) | 빠름 (자동화 가능) |
| **커버리지** | 의도한 로직에 한정 | 분석자의 피로도에 의존 | 수학적 모든 경로 탐색 가능 |
| **객관성** | 명세서의 품질에 의존 | 분석자 주관적 편향 가능 | 실행 가능한 경로에 기반한 객관적 분류 |
| **테스트 설계** | 명세서 준수 테스트 | Ad-hoc 테스트 | 경로 기반 테스트 케이스 자동 생성 |

## 방어적 관점에서의 완화 조치 및 인사이트

이 기법을 활용하여 레거시 시스템의 테스트 케이스를 생성했다면, 이를 바탕으로 구체적인 보안 및 안전 조치를 취해야 합니다.

1.  **

---

**출처**: [http://arxiv.org/abs/2604.22673v1](http://arxiv.org/abs/2604.22673v1)