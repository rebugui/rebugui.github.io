---
title: "🤖 SWE-CI: CI 환경에서 LLM 에이전트 코드 유지보수 능력 평가"
date: 2026-03-13T07:06:43+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
draft: true
---

## 서론

새벽 2시, 긴급한 핫픽스 배포 직전에 CI 파이프라인의 빨간색 실패(Fail) 아이콘을 마주한 경험이 있으신가요? 테스트 케이스 하나가 로컬에서는 통과하지만 리모트 환경에서는 깨지는 상황, 혹은 복잡한 의존성 문제로 인해 빌드가 무한히 대기하는 상황은 모든 소프트웨어 엔지니어의 악몽입니다. 최근 자동화된 코딩 도구가 급격히 발전했지만, 정작 이러한 **'유지보수(Maintenance)'** 영역에서의 성능은 아직 검증되지 않았습니다.

우리는 LLM(Large Language Model)이 단순히 코드를 생성하는 능력을 넘어, 실제 제품 환경에서 발생하는 버그를 수정하고, 레거시 코드를 리팩토링하며, CI(Continuous Integration) 파이프라인을 성공적으로 통과할 수 있는지를 평가해야 합니다. 기존의 SWE-bench와 같은 벤치마크는 주로 이슈 트래커를 기반으로 한 정적인 문제 해결에 초점을 맞추고 있어, 실제 개발 워크플로우의 핵심인 CI 환경과의 상호작용을 반영하지 못한다는 한계가 있었습니다.

바로 이 지점에서 **SWE-CI**가 등장합니다. SWE-CI는 실제 GitHub 저장소와 GitHub Actions 워크플로우를 활용하여, LLM 에이전트가 코드베이스를 유지보수하고 파이프라인의 제약 조건을 준수하며 수정 사항을 반영하는 능력을 객관적으로 측정하는 새로운 표준입니다. 이 벤치마크는 AI가 단순한 코딩 보조를 넘어 '자동화된 소프트웨어 엔지니어'로 거듭날 수 있는지를 판단하는 잣대가 됩니다.

## 본론

### SWE-CI의 기술적 원리와 메커니즘

SWE-CI는 기존 벤치마크와 달리 "실제 환경(Real-world Environment)"을 시뮬레이션하는 대신 실제 도커 컨테이너와 CI 워크플로우를 직접 사용한다는 점이 가장 큰 특징입니다. 연구진은 실제 오픈 소스 프로젝트의 저장소를 포크(fork)하고, 의도적으로 CI 테스트를 실패하게 만드는 커밋을 생성하여 에이전트에게 해결 과제를 부여합니다.

이 과정에서 에이전트는 단순히 코드만 수정하면 됩니다. 파이프라인의 로그를 읽고, 실패 원인을 진단하며, 의존성을 업데이트하고, 때로는 타임아웃 설정을 조정해야 할 수도 있습니다. 즉, 에이전트는 **'코드 수정'**과 **'환경 이해'**라는 두 가지 과제를 동시에 수행해야 합니다.

다음은 SWE-CI 평가 과정의 전체적인 워크플로우를 도식화한 것입니다.

```javascript
graph TD
    A[실제 GitHub 저장소 선택] --> B[문제 시나리오 생성]
    B --> C[CI 실패 유도]
    C --> D[에이전트 개입 시작]
    D --> E[코드/설정 수정 시도]
    E --> F[CI Pipeline 재실행]
    F --> G{테스트 통과 여부}
    G -- 통과 --> H[성공]
    G -- 실패 --> I[로그 분석]
    I --> D
```

이 다이어그램에서 볼 수 있듯이, SWE-CI의 핵심은 피드백 루프(Feedback Loop)입니다. 에이전트는 CI 결과(로그, 상태 코드)를 관찰하고(Observation), 이를 바탕으로 다시 행동(Action)하는 과정을 반복합니다. 이는 트랜스포머 모델의 다음 토큰 예측 방식과는 달리, 강화 학습적 관점에서의 환경과의 상호작용이 필수적인 작업입니다.

### 기존 벤치마크와의 비교 분석

SWE-CI의 필요성을 명확히 하기 위해, 대표적인 기존 평가 지표들과 비교해 보겠습니다.

| 비교 항목 | HumanEval / MBPP | SWE-bench | SWE-CI (제안) |
| :--- | :--- | :--- | :--- |
| **평가 환경** | 고립된 Python 함수 실행 | 로컬 테스트 스위트 실행 | **실제 GitHub Actions CI** |
| **문제 유형** | 알고리즘/함수 구현 | Issue 기반 버그 수정 | **CI 실패 해결 및 유지보수** |
| **코드베이스** | 단일 파일 수준 | 다중 파일, 프로젝트 수준 | **다중 파일 + CI 설정(.yml) 포함** |
| **현실성** | 낮음 (토이 문제) | 중간 (정적 분석) | **높음 (동적 파이프라인/의존성)** |
| **주요 평가 지표** | Pass@k | Resolved Rate | **CI Pass Rate / Turnaround Time** |

기존 벤치마크들이 코드의 '정답성'에 집중했다면, SWE-CI는 코드의 '생존력'을 평가합니다. 예를 들어, SWE-CI에서는 `requirements.txt`를 수정하여 버전 충돌을 해결하거나, `.github/workflows/test.yml`의 타임아웃을 조정하는 작업도 정답으로 간주됩니다. 이는 실제 MLOps 파이프라인에서 발생하는 문제들과 매우 흡사합니다.

### 실습: SWE-CI 스타일의 에이전트 시뮬레이션

SWE-CI의 환경을 직접 구축하기 전에, 에이전트가 어떻게 CI 피드백을 처리하고 코드를 수정하는지 간단히 시뮬레이션해 보겠습니다. 아래 코드는 가상의 CI 에이전트가 실패한 테스트 로그를 분석하여 소스 코드를 패치하는 과정을 파이썬으로 구현한 예시입니다.

```python
import subprocess
import re

class SWECIAgent:
    def __init__(self, repo_path):
        self.repo_path = repo_path

    def run_ci(self):
        """가상의 CI 파이프라인을 실행합니다."""
        print("--- CI Pipeline 실행 중 ---")
        # 실제 환경에서는 'pytest' 혹은 'github actions' 실행 로직이 들어갑니다.
        result = subprocess.run(
            ["python", "-m", "pytest", "test_module.py", "-v"],
            capture_output=True,
            text=True,
            cwd=self.repo_path
        )
        return result

    def analyze_logs(self, ci_result):
        """CI 로그를 분석하여 실패 원인을 파악합니다."""
        if ci_result.returncode == 0:
            return "PASSED"
        
        # 로그에서 AssertionError 패턴 찾기
        error_match = re.search(r"AssertionError: (.+)", ci_result.stdout)
        if error_match:
            return error_match.group(1)
        
        # 로그에서 ImportError 패턴 찾기
        import_match = re.search(r"ModuleNotFoundError: (.+)", ci_result.stdout)
        if import_match:
            return f"Missing Module: {import_match.group(1)}"
            
        return "Unknown Error"

    def fix_code(self, error_message):
        """에러 메시지에 따라 코드를 수정합니다."""
        print(f"--- 에러 분석: {error_message} ---")
        
        if "AssertionError" in error_message and "expected 5" in error_message:
            file_path = f"{self.repo_path}/source.py"
            with open(file_path, 'r') as f:
                content = f.read()
            
            # 간단한 패치: return 4를 return 5로 변경
            updated_content = content.replace("return 4", "return 5")
            
            with open(file_path, 'w') as f:
                f.write(updated_content)
            print("패치 적용: source.py (return 4 -> return 5)")
            
        elif "Missing Module" in error_message:
            # 의존성 설치 시뮬레이션
            print("의존성 설치 시뮬레이션 수행 중...")
            # subprocess.run(["pip", "install", "missing_package"])

```

```python
    def run_loop(self, max_attempts=3):
        for i in range(max_attempts):
            result = self.run_ci()
            status = self.analyze_logs(result)
            
            if status == "PASSED":
                print("✅ CI 테스트 통과!")
                return True
            else:
                print(f"❌ 시도 {i+1} 실패. 수정 시도합니다...")
                self.fix_code(status)
        
        print("⛔ 최대 시도 횟수 초과: 문제 해결 실패")
        return False

# 실행 예시 (가상 환경 가정)
# agent = SWECIAgent("./my_project")
# agent.run_loop()
```

이 코드는 단순화된 예시이지만, SWE-CI 벤치마크에서 요구하는 핵심 역량을 보여줍니다. 에이전트는 단순히 텍스트를 생성하는 것이 아니라, 외부 프로세스(`subprocess`)를 통해 테스트를 수행하고 그 결과(Stdout/Stderr)를 파싱하여 자신의 행동(코드 수정)을 결정합니다.

### Step-by-step 가이드: SWE-CI 벤치마크 도입 방법

연구자나 엔지니어가 자신의 모델을 SWE-CI로 평가하거나, 팀 내 개발 프로세스에 이러한 평가 방식을 도입하고자 할 때 다음 단계들을 고려할 수 있습니다.

1.  **데이터셋 준비 (Dataset Curation)**     *   자신이 속한 도메인의 오픈 소스 레포지토리를 선택합니다. (예: 웹 프레임워크, 데이터 분석 라이브러리)     *   CI가 구성되어 있고 테스트 커버리지가 어느 정도 확보된 프로젝트를 선정하는 것이 중요합니다.

2.  **파괴적 수정 (Breaking Changes Injection)**     *   평가를 위해 정상적인 상태의 레포지토리에 의도적으로 버그를 심습니다.     *   논리적 오류, 잘못된 타입 선언, 혹은 의존성 버전 업그레이드로 인한 호환성 문제 등을 다양하게 생성합니다.

3.  **에이전트 도구 세팅 (Agent Tooling)**     *   에이전트에게 파일 읽기/쓰기, 터미널 명령 실행, git diff 확인 등의 도구를 제공해야 합니다.     *   LangChain이나 AutoGen과 같은 에이전트 프레임워크를 사용하여 도구 호출 기능을 구현합니다.

4.  **평가 및 메트릭 측정 (Evaluation)**     *   **CI Pass Rate**: 에이전트가 제한된 횟수 내에 CI를 성공시킨 비율.     *   **Edit Distance**: 정답과 얼마나 유사한 패치를 적용했는지 측정.     *   **Turnaround Time**: 문제 해결까지 걸린 총 시간과 API 호출 비용.

### MLOps 관점에서의 함의

SWE-CI는 단순한 연구를 넘어 실무 MLOps에 중요한 시사점을 던집니다. LLM 오피서(LLMOps)를 구축할 때, 우리는 이제 모델의 창의적인 글쓰기 능력보다는 **'안정적인 시스템 유지 능력'**에 집중해야 합니다. RAG(Retrieval-Augmented Generation) 시스템을 설계할 때도 단순히 코드 스니펫만 검색해서 보여주는 것이 아니라, 해당 프로젝트의 CI 로그와 연계하여 "이 에러를 해결하려면 어떤 코드를 수정해야 하는지"를 추천하는 방향으로 발전해야 합니다.

## 결론

SWE-CI 벤치마크는 LLM 에이전트 연구 분야에 중요한 이정표를 세웠습니다. 우리는 이제 '단순한 코딩 테스트'를 뛰어넘어, **'실제 CI 환경에서 버그를 고치고 시스템을 안정적으로 유지하는 능력'**을 평가할 수 있는 표준을 갖게 되었습니다.

전문가 관점에서 볼 때, SWE-CI의 결과는 LLM의 범용 지능(Generic Intelligence)을 측정하는 것이 아니라, **'전문가적 숙련도(Expertise)'**를 측정하는 지표로 해석해야 합니다. 모델이 아무리 방대한 지식을 가지고 있더라도, 실제 GitHub Actions 파이프라인에서 발생하는 복잡한 의존성 문제나 타임아웃 이슈를 해결하지 못한다면 현장의 엔지니어로서 신뢰할 수 없기 때문입니다.

향후 연구에서는 단일 모델의 성능을 넘어, **코드 에이전트와 셀 에이전트(Terminal Agent)가 협력하는 멀티 에이전트 시스템(Multi-Agent System)**이 SWE-CI 벤치마크에서 어떤 성과를 낼지 주목해야 합니다. 이는 곧 자율적인 소프트웨어 유지보수 시대의 도래를 의미합니다.

### 참고자료
- [SWE-CI: Evaluating Agent Capabilities in Maintaining Codebases via CI (arXiv)](https://arxiv.org/abs/2603.03823)
- [SWE-bench: Can LMs Resolve Real-World Github Issues?](https://arxiv.org/abs/2310.06770)
- [Hacker News Discussion](https://news.ycombinator.com/item?id=47295537)

---

**출처**: [https://arxiv.org/abs/2603.03823](https://arxiv.org/abs/2603.03823)