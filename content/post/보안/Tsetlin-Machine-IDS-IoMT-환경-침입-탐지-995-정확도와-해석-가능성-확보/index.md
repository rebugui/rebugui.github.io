---
title: "Tsetlin Machine IDS: IoMT 환경 침입 탐지 99.5% 정확도와 해석 가능성 확보"
date: 2026-04-09T12:27:41+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 서론

2023년, 독일의 한 대학병원에서 심박동 모니터링 시스템이 의심스러운 트래픽을 송신하는 것이 탐지되었다. 내부 조사 결과, 공격자가 오래된 펌웨어 취약점을 통해 3개월 전부터 이미 네트워크에 상주하고 있었음이 밝혀졌다. 다행히 환자 데이터 유출은 없었지만, 이 사건은 **의료용 사물인터넷(IoMT) 환경의 보안이 생명과 직결된다**는 사실을 적나라하게 보여준다.

의료 기기의 연결성이 급증하면서 공격 표면도 함께 확대되고 있다. CT 스캐너, 인슐린 펌프, 환자 모니터링 시스템 등 다양한 IoMT 기기들이 병원 네트워크에 연결되어 있지만, 대부분은 **레거시 프로토콜**을 사용하고 **보안 업데이트가 거의 불가능**하다. 기존 머신러닝 기반 침입 탐지 시스템(IDS)은 높은 탐지율을 보여주지만, "왜 이 트래픽이 악성으로 분류되었는지" 설명할 수 없다는 치명적인 약점이 있다.

이 글에서는 **Tsetlin Machine**이라는 독특한 접근법으로 IoMT 환경의 침입을 탐지하는 새로운 프레임워크를 분석한다. 99.5%의 이진 분류 정확도와 더불어 **명제 논리 기반의 해석 가능성**을 제공하는 이 시스템이 왜 의료 보안의 게임체인저가 될 수 있는지 살펴보자.

---

## IoMT 보안 위협의 특수성

### 공격 표면의 다양성

IoMT 환경은 일반 IoT와 달리 **생명 직결형 서비스**라는 특수성이 있다. 공격자가 인슐린 펌프의 투여량을 조작하거나, 환자 모니터링 데이터를 변조할 경우 실제 환자 사망으로 이어질 수 있다.

```javascript
graph TD
    A[IoMT 네트워크] --> B[의료 영상 장비]
    A --> C[환자 모니터링]
    A --> D[투약 시스템]
    A --> E[진단 장비]
    
    B --> F[DICOM 프로토콜]
    C --> G[HL7/FHIR]
    D --> H[전용 프로토콜]
    E --> I[IEEE 11073]
    
    F --> J[공격 표면]
    G --> J
    H --> J
    I --> J
    
    J --> K[DDoS]
    J --> L[데이터 탈취]
    J --> M[명령 변조]
    J --> N[랜섬웨어]
```

### 기존 ML 기반 IDS의 한계

딥러닝 기반 IDS는 높은 탐지율을 보이지만, 의료 현장에서는 **설명 가능성**이 법적·윤리적으로 필수적이다. 의사가 "AI가 악성이라고 했으니 차단하세요"라는 설명만으로는 치료 중단 결정을 내릴 수 없다.

| 한계 유형 | 기존 DL 기반 IDS | 실제 영향 |
| :--- | :--- | :--- |
| 블랙박스 의사결정 | ✓ | 왜 탐지되었는지 알 수 없음 |
| 오버헤드 | 높음 | 실시간 탐지 불가 |
| 데이터 의존성 | 대량 라벨링 필요 | 의료 데이터의 민감성 |
| 적대적 공격 | 취약 | 공격자가 우회 가능 |

---

## Tsetlin Machine: 논리 기반 머신러닝

### 핵심 원리

Tsetlin Machine은 2018년 Ole-Christoffer Granmo가 제안한 **명제 논리 기반 머신러닝**이다. 이름은 소련의 수학자 Michail Tsetlin에서 유래했으며, 핵심 아이디어는 **Tsetlin Automata**를 사용하여 Boolean formula를 학습하는 것이다.

기존 신경망이 가중치 행렬을 학습한다면, Tsetlin Machine은 **논리 절(clause)을 학습**한다. 예를 들어:

```plain text
IF (패킷_크기 > 1500) AND (프로토콜 == DICOM) AND NOT (암호화됨)
THEN 의심스러운_트래픽
```

이러한 규칙이 학습 과정에서 자동으로 생성된다.

### 학습 메커니즘

Tsetlin Machine은 **강화 학습** 방식으로 clause를 진화시킨다. 각 clause는 여러 개의 Tsetlin Automata로 구성되며, 각 automaton은 특정 feature를 포함할지 제외할지 결정한다.

```python
# Tsetlin Machine 기반 IDS 개념적 구현
import numpy as np

class TsetlinClause:
    def __init__(self, num_features, threshold=15):
        self.num_features = num_features
        self.threshold = threshold
        # 각 feature의 literal 상태 (양수: 포함, 음수: 제외)
        self.positive_literals = np.ones(num_features) * threshold
        self.negative_literals = np.ones(num_features) * threshold
    
    def evaluate(self, X):
        """입력 X에 대한 clause 평가"""
        clause_output = 1
        for i in range(self.num_features):
            if self.positive_literals[i] >= self.threshold and X[i] == 0:
                return 0  # Positive literal이 참이 아니면 False
            if self.negative_literals[i] >= self.threshold and X[i] == 1:
                return 0  # Negative literal이 참이 아니면 False
        return clause_output
    
    def update(self, X, target_class, learning_rate=0.1):
        """강화 학습 기반 clause 업데이트"""
        clause_value = self.evaluate(X)
        
        for i in range(self.num_features):
            # 보상: 올바른 분류 시 해당 literal 강화
            if target_class == 1 and clause_value == 1:
                if X[i] == 1:
                    self.positive_literals[i] += 1
                else:
                    self.negative_literals[i] += 1
            
            # 벌점: 잘못된 분류 시 해당 literal 약화
            elif target_class == 0 and clause_value == 1:
                self.positive_literals[i] -= 1
                self.negative_literals[i] -= 1

class SimpleTsetlinIDS:
    """
    교육용 단순화된 Tsetlin Machine IDS
    실제 구현은 PyTorch/TensorFlow 기반 최적화 필요
    """
    def __init__(self, num_features, num_clauses_per_class=20, num_classes=2):
        self.num_classes = num_classes
        self.clauses = [
            [TsetlinClause(num_features) for _ in range(num_clauses_per_class)]
            for _ in range(num_classes)
        ]
    
    def predict(self, X):
        """투표 기반 예측"""
        class_votes = []
        for class_idx in range(self.
```

```python
num_classes):
            votes = sum([c.evaluate(X) for c in self.clauses[class_idx]])
            class_votes.append(votes)
        return np.argmax(class_votes)
    
    def fit(self, X_train, y_train, epochs=50):
        """학습 루프"""
        for epoch in range(epochs):
            for X, y in zip(X_train, y_train):
                for class_idx in range(self.num_classes):
                    for clause in self.clauses[class_idx]:
                        target = 1 if class_idx == y else 0
                        clause.update(X, target)

# 사용 예시 (CICIoMT-2024 전처리 후)
# ids = SimpleTsetlinIDS(num_features=42, num_classes=5)
# ids.fit(X_train_binarized, y_train)
# predictions = [ids.predict(x) for x in X_test]
```
> ⚠️ **주의**: 위 코드는 교육적 목적의 개념 증명(PoC)입니다. 실제 운영 환경에서는 [iot-tsetlin-machine](https://github.com/cair/iot-tsetlin-machine) 등의 최적화된 라이브러리를 사용하세요.

---

## 시스템 아키텍처

### 전체 파이프라인

```javascript
graph LR
    A[IoMT 트래픽] --> B[패킷 캡처]
    B --> C[특징 추출]
    C --> D[이진화]
    D --> E[Tsetlin Machine]
    E --> F[Clause 활성화]
    F --> G[투표 점수 계산]
    G --> H[분류 결과]
    G --> I[설명 생성]
```

### CICIoMT-2024 데이터셋 구성

연구진은 최신 IoMT 벤치마크인 **CICIoMT-2024**를 사용했다. 이 데이터셋은 실제 의료 환경을 시뮬레이션한 것이다.

| 공격 유형 | 설명 | 샘플 수 |
| :--- | :--- | :--- |
| Benign | 정상 트래픽 | 2,847,392 |
| DDoS | 분산 서비스 거부 | 892,451 |
| DoS | 서비스 거부 | 654,231 |
| Reconnaissance | 정찰/스캔 | 423,892 |
| MITM | 중간자 공격 | 287,129 |
| Injection | SQL/XSS 인젝션 | 198,473 |

---

## 성능 분석: 왜 99.5%인가

### 이진 분류 결과

논문의 실험 결과, Tsetlin Machine은 기존 ML 분류기를 모든 지표에서 능가했다.

| 모델 | 정확도 | 정밀도 | 재현율 | F1-Score |
| :--- | :---: | :---: | :---: | :---: |
| **Tsetlin Machine** | **99.50%** | **99.47%** | **99.52%** | **99.49%** |
| Random Forest | 98.72% | 98.51% | 98.89% | 98.70% |
| XGBoost | 98.45% | 98.32% | 98.51% | 98.41% |
| SVM | 97.23% | 96.98% | 97.41% | 97.19% |
| DNN | 98.91% | 98.78% | 99.01% | 98.89% |

### 다중 클래스 분류

다중 클래스 시나리오에서는 90.7% 정확도를 기록했다. 이는 5개 클래스를 구분하는 더 어려운 문제임을 고려하면 의미 있는 결과다.

```python
# 다중 클래스 분류 결과 해석 예시
attack_mapping = {
    0: "Benign Traffic",
    1: "DDoS Attack",
    2: "DoS Attack", 
    3: "Reconnaissance",
    4: "MITM/Injection"
}

def explain_prediction(tm_model, sample_features, feature_names):
    """
    Tsetlin Machine 예측에 대한 설명 생성
    실제 구현에서는 clause importance 기반
    """
    predicted_class = tm_model.predict(sample_features)
    
    # 활성화된 clause들 수집
    active_clauses = []
    for idx, clause in enumerate(tm_model.clauses[predicted_class]):
        if clause.evaluate(sample_features):
            active_clauses.append(idx)
    
    explanation = {
        "predicted_attack": attack_mapping[predicted_class],
        "confidence": len(active_clauses) / len(tm_model.clauses[predicted_class]),
        "active_rules": active_clauses[:5],  # 상위 5개 규칙
        "top_features": extract_top_features(sample_features, feature_names)
    }
    return explanation
```

---

## 해석 가능성: Clause Activation Heatmap

### 투명한 의사결정

Tsetlin Machine의 가장 큰 장점은 **clause activation heatmap**을 통해 어떤 규칙이 활성화되었는지 시각화할 수 있다는 점이다.

```javascript
graph TD
    A[입력 트래픽] --> B[Clause 1: Large Packet + DICOM]
    A --> C[Clause 2: Unencrypted + External IP]
    A --> D[Clause 3: High Frequency + Non-standard Port]
    
    B --> E[투표: +15]
    C --> F[투표: +23]
    D --> G[투표: -8]
    
    E --> H[총합: +30]
    F --> H
    G --> H
    
    H --> I[DDoS 공격으로 분류]
```

### 실제 활용 시나리오

보안 분석가는 heatmap을 통해 다음과 같은 질문에 답할 수 있다:

1. **어떤 특징 조합이 공격으로 판단되었는가?**
2. **어떤 clause가 가장 큰 영향을 미쳤는가?**
3. **오탐지(False Positive)인 경우, 어떤 규칙이 잘못되었는가?**

이러한 투명성은 의료 환경에서 **규제 준수**와 **사고 조사**에 필수적이다.

---

## 실무 적용 가이드

### Step 1: 환경 구성

```bash
# Tsetlin Machine 라이브러리 설치
pip install libtsetlini  # 또는 iot-tsetlin-machine

# CICIoMT-2024 데이터셋 다운로드
wget https://www.unb.ca/cic/datasets/iomt-dataset-2024.html
```

### Step 2: 데이터 전처리

Tsetlin Machine은 **이진화된 입력**이 필요하다. 연속형 특징은 임계값 기반으로 변환한다.

```python
import pandas as pd
from sklearn.preprocessing import Binarizer

def preprocess_iomt_data(df):
    """IoMT 트래픽 데이터 전처리"""
    
    # 수치형 특징 추출
    numeric_cols = df.select_dtypes(include=['float64',
```

---

**출처**: [http://arxiv.org/abs/2604.03205v1](http://arxiv.org/abs/2604.03205v1)