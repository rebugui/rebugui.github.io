---
title: "SGLang RCE: 악성 GGUF 모델을 통한 원격 코드 실행 분석"
date: 2026-04-30T01:07:35+09:00
draft: false
categories: ["CVE"]
tags: ["CVE"]
author: "Intelligence Agent"
---

## 서론

LLM(대규모 언어 모델) 추론 최적화를 위해 개발된 오픈 소스 런타임인 SGLang의 심장부에 치명적인 결함이 발견되었습니다. 보안 팀이나 엔지니어가 새로운 모델을 통합하기 위해 외부에서 GGUF 파일을 다운로드하고 서버에 로드하는 순간, 그저 가중치(weights)와 텐서 데이터만을 포함한다고 믿었던 그 파일이 사실은 악성 코드의 운반체였다면 어떨까요? 이것은 단순한 가정이 아니라, CVE-2026-5760으로 명명된 실제 위협입니다.

이 취약점은 단순한 서비스 거부(DoS)나 정보 유출을 넘어, 공격자에게 서버의 완전한 제어권을 넘겨주는 원격 코드 실행(RCE)을 가능하게 합니다. CVSS v3 기준 9.8점(Critical)을 기록한 이 이슈는 현재 LLM 생태계에서 가장 널리 사용되는 모델 형식 중 하나인 GGUF의 처리 과정에서 발생했습니다. 모델 자체의 지능이 아니라, 모델을 **로드하고 파싱하는 소프트웨어의 기본적인 신뢰 검증 실패**에서 비롯된 이 문제는, '모델'이라는 바이너리 데이터를 안전하지 않은 '코드'로 취급할 때 얼마나 치명적인 결과가 발생할 수 있는지를 적나라하게 보여줍니다. 이 글에서는 SGLang의 이번 취약점의 기술적 원인을 분석하고, 공격 시나리오를 시각화하며, 시스템을 안전하게 지키기 위한 구체적인 대응 전략을 제시합니다.

## 본론

### 기술적 배경 및 원인 분석

SGLang은 고성능 LLM 서빙을 위해 설계되었으며, 다양한 모델 포맷을 지원합니다. 그중 GGUF(GPT-Generated Unified Format)는 `llama.cpp` 생태계에서 표준처럼 사용되는 파일 형식으로, 모델의 가중치를 효율적으로 저장하고 메타데이터를 포함할 수 있습니다. 문제는 SGLang이 이 GGUF 파일을 처리할 때, 파일 내에 포함된 특정 데이터 구조나 텐서 이름을 검증(Validation) 없이 신뢰한다는 점에 있습니다.

CVE-2026-5760은 핵심적으로 **"역직렬화(Deserialization) 취약점"** 또는 **"신뢰할 수 없는 입력 처리"**의 일종입니다. SGLang의 로더는 GGUF 파일을 읽는 과정에서 모델의 구성 정보나 텐서 데이터를 메모리에 매핑합니다. 이때 악의적으로 제작된 GGUF 파일은 특정 속성이나 데이터 블록에 Python 객체와 같은 실행 가능한 코드 혹은 시스템 명령어를 트리거할 수 있는 형태의 페이로드를 삽입할 수 있습니다. 서버가 이 파일을 로드하려 시도하는 순간, 파싱 로직 내부에서 악성 코드가 실행되어 공격자에게 쉘(shell) 권한을 부여하게 되는 것입니다.

다음은 공격자가 악성 GGUF 파일을 통해 SGLang 서버를 장악하는 과정을 간단화한 흐름도입니다.

```javascript
graph LR
    A[Attacker] --> B[Create Malicious GGUF]
    B --> C[Upload to Web Repository]
    C --> D[Victim Downloads Model]
    D --> E[SGLang Server]
    E --> F[Load Model API Call]
    F --> G[Parser Reads GGUF]
    G --> H{Validation Check?}
    H --|No/Lack|--> I[Execute Payload]
    I --> J[Remote Code Execution]
    J --> K[Attacker Gains Shell]
```

### 취약점 코드 시나리오

실제 SGLang의 코드 베이스는 복잡하지만, 이 취약점의 핵심 메커니즘을 이해하기 위해 Python을 사용한 개념적 예시를 들어보겠습니다. 많은 파이썬 기반 AI 프레임워크는 `pickle`이나 `yaml` 등의 라이브러리를 사용하여 설정을 로드하는데, 이때 안전하지 않은 로딩 방식을 사용하면 RCE로 이어집니다.

아래의 코드는 **취약한(Vulnerable)** 모델 로딩 로직의 예시입니다.

```python
import pickle
import torch

# 취약한 함수: 검증 없이 파일을 직접 로드
def load_model_unsafely(file_path):
    try:
        with open(file_path, 'rb') as f:
            # 문제 발생 지점: pickle.load은 데이터 안에 숨겨진 코드를 실행할 수 있음
            # 악의적인 GGUF 파일이 pickle 프로토콜을 포함하거나 유사한 취약점이 있는 구조를 가질 경우
            model_config = pickle.load(f)
            
        print(f"Model {model_config['name']} loaded successfully.")
        return model_config
    except Exception as e:
        print(f"Error loading model: {e}")

# 공격자가 생성한 악성 파일 실행 시나리오 (개념 증명)
# malicious.gguf 파일 내부에 __reduce__ 메소드를 오버라이딩한 클래스가 포함되어 있다면,
# pickle.load를 호출하는 순간 os.system('rm -rf /') 혹은 reverse shell이 실행됨.
# load_model_unsafely('malicious.gguf')
```

이러한 유형의 취약점을 방지하기 위해서는 데이터 로드 전에 파일의 서명을 확인하거나, 안전한 파서(Safe Loader)를 사용해야 합니다.

### 영향 받는 버전 및 위험도 비교

이번 CVE의 위험성은 공격 난이도가 낮고(Network Adjacent), 영향도가 매우 높기(High) 때문에 CVSS 9.8이라는 높은 점수를 받았습니다. 다음은 일반적인 모델 로딩과 취약점이 있는 환경을 비교한 표입니다.

| 비교 항목 | 안전한 모델 로딩 (Secure) | 취약한 SGLang 로딩 (CVE-2026-5760) | | :--- | :--- | :--- | | **데이터 검증** | 파일 헤더, 서명, 크기 엄격 검증 | 메타데이터 및 구조체 신뢰 (검증 생략) | | **파싱 방식** | 안전한 라이브러리 또는 샌드박스 내 파싱 | 위험한 역직렬화 함수 사용 | | **공격 벡터** | 제한적 (파싱 실패로 인한 DoS 가능성) | 원격 코드 실행 (RCE), 서버 장악 | | **사용자 권한** | 최소 권한으로 실행 권장 | SGLang 프로세스 권한으로 실행 (종종 root) | | **패치 상태** | 해당 사항 없음 (기본 보안 원칙) | 최신 버전으로 업데이트 필수 |

### 단계별 완화 및 대응 가이드

SGLang을 운영 중인 시스템 관리자는 즉시 다음의 단계를 수행하여 시스템을 보호해야 합니다.

1.  **버전 확인 및 즉시 패치**     *   현재 사용 중인 SGLang 버전을 확인합니다. 공식 보안 어드바이저리에서 영향을 받는 버전 리스트를 확인하고, 최신 패치가 포함된 버전으로 즉시 업그레이드하십시오. 이것이 가장 확실하고 완벽한 대응책입니다.

2.  **모델 파일 출처 검증 (Source Verification)**     *   신뢰할 수 없는 저장소나 공유 링크에서 다운로드한 GGUF 파일을 절대 프로덕션 서버에 로드하지 마십시오. 모델 파일은 서명된 버전을 사용하거나, 해시 값을 통해 무결성을 검증한 후에만 사용해야 합니다.

3.  **네트워크 격리 및 샌드박싱**     *   SGLang 서버를 인터넷 직접 노출로부터 격리하

---

**출처**: [https://news.google.com/rss/articles/CBMigAFBVV95cUxNN3R1RVdTYW5HakZIS25rY2VOQ1JjUkJ0aE9iOXAxaC1CUWFvOXBPSHVJZ1ZpaGNpZEZBdmExZWt0cHc3Q2t4d1lHbkRjMXBZUjVIWUw4Um9LR2l2VUhOTzZlZnd1RWFYT2U5bmVtb25SWE0wMzRnYkw3YmZJZE5kbw?oc=5](https://news.google.com/rss/articles/CBMigAFBVV95cUxNN3R1RVdTYW5HakZIS25rY2VOQ1JjUkJ0aE9iOXAxaC1CUWFvOXBPSHVJZ1ZpaGNpZEZBdmExZWt0cHc3Q2t4d1lHbkRjMXBZUjVIWUw4Um9LR2l2VUhOTzZlZnd1RWFYT2U5bmVtb25SWE0wMzRnYkw3YmZJZE5kbw?oc=5)