---
title: "Post-Quantum Cryptography: 퀀텀 위협 방어 가이드"
date: 2026-04-29T01:07:06+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 서론

2019년, 구글은 자신들의 Sycamore 양자 컴퓨터가 최첨단 슈퍼컴퓨터보다 1조 5,000억 배 빠르게 특정 문제를 해결했다고 발표했습니다. 많은 사람이 이를 단순한 기술적인 기적로 여겼지만, 보안 전문가의 시선에서는 **"잠재적 재앙의 서막"**으로 읽혔습니다.

현재 금융, 의료, 국방 등 우리 사회의 핵심 인프라를 지키고 있는 암호화 기술(RSA, ECC)은 거대한 소수인수분해의 난해함에 기반하고 있습니다. 그러나 쇼어(Shor) 알고리즘과 같은 양자 알고리즘은 이 난제를 다항식 시간 내에 해결할 수 있습니다. 이는 즉, 양자 컴퓨터가 실용화되는 순간 현재의 모든 공개키 암호화(PKI)가 무력화된다는 뜻입니다.

더 무서운 시나리오는 현재 진행형입니다. 공격자들은 아직 암호를 깰 능력이 없더라도, 지금 당장 암호화된 통신을 훔쳐서(Harvest) 저장해 두었다가, 나중에 양자 컴퓨터가 왔을 때 복호화(Decrypt Later)하는 **"Harvest Now, Decrypt Later"** 전략을 사용하고 있습니다. 내일 태어날 아이의 의료 기록이나, 유효기간이 10년 이상 남은 국가 기밀이 지금 도청당하고 있을 수 있습니다.

이 글에서는 이러한 퀀텀 위협에 대응하기 위해 **후량자 암호학(Post-Quantum Cryptography, PQC)**의 기술적 원리를 분석하고, AWS가 제안하는 하이브리드 암호화 전략을 통해 실제 시스템에 어떻게 적용할지 심층적으로 다룹니다.
> **⚠️ 윤리적 경고**: 본 문서에 포함된 모든 기술적 내용, 코드 예시 및 공격 시나리오는 잠재적인 보안 위협을 이해하고 방어 태세를 확립하기 위한 교육 및 연구 목적입니다. 이 정보를 악의적인 목적으로 사용하는 것은 엄격히 금지됩니다.

## 본론

### 1. 양자 위협의 본질: Shor vs Grover

양자 컴퓨팅이 암호학에 미치는 영향은 알고리즘에 따라 다릅니다.

**Shor's Algorithm (쇼어 알고리즘)**: 이 알고리즘은 큰 정수를 소수의 곱으로 인수분해하는 문제를 극도로 빠르게 해결합니다. 이는 **RSA, Diffie-Hellman, 타원 곡선 암호(ECC)**와 같은 비대칭 키 암호화에 치명적입니다. 키 크기를 아무리 키워도 양자 컴퓨터 앞에서는 무의미합니다.

**Grover's Algorithm (그로버 알고리즘)**: 이 알고리즘은 비정형 데이터베이스 검색 속도를 향상시킵니다. 이는 대칭키 암호화(AES, ChaCha20)와 해시 함수(SHA-256)에 영향을 미칩니다. 하지만 이 경우는 대응이 상대적 간단합니다. 예를 들어 AES-128의 안전성이 64비트 수준으로 떨어지므로, 단순히 **AES-256**으로 키를 두 배로 늘리면 양자 내성을 확보할 수 있습니다.

즉, 우리의 최우선 과제는 공개키 기반(PKI) 시스템을 PQC로 전환하는 것입니다.

### 2. 공격 시나리오: Harvest Now, Decrypt Later

공격자가 현재 시점에서 어떻게 데이터를 수집하는지 시각화해 보겠습니다. 이는 단순한 이론이 아니라, 국가 차원의 해킹 그룹들이 이미 수행 중인 것으로 평가됩니다.

```javascript
graph LR
    A[Origin Server] -->|Encrypted Traffic (TLS 1.2)| B[Attacker / Surveillance Node]
    A --> C[Legitimate User]
    B -->|Store Ciphertext| D[(Cold Storage)]
    D --> E[Wait Years]
    E -->|Deploy Quantum Computer| F[Decrypt Data]
    F --> G[Data Breach]
```

위 다이어그램에서 볼 수 있듯이, 공격자는 현재의 방화벽이나 IDS/IPS를 뚫을 필요가 없습니다. 단순히 트래픽을 복사해서 저장만 하면 됩니다. 이 공격이 성립하기 위한 조건은 **"데이터의 수명 > 양자 컴퓨터 개발 시간"**입니다. 따라서 장기간 보안이 필요한 데이터는 지금 즉시 보호 조치를 취해야 합니다.

### 3. 기술적 해결책: 하이브리드 암호화 (Hybrid Encryption)

PQC 알고리즘(NIST가 표준화한 Kyber, Dilithium 등)은 아직 새롭기 때문에, 미래에 발견되지 않은 취약점이 있을 수 있습니다. 만약 PQC 알고리즘만 사용해서 전환했다가, 그 알고리즘이 뚫리면 데이터가 완전히 노출됩니다.

따라서 AWS를 포함한 업계 표준은 **"하이브리드 접근법"**을 권장합니다. 이는 기존의 클래식 암호(예: RSA-2048)와 새로운 PQC 알고리즘(예: Kyber-768)을 **동시에 사용**하는 전략입니다.

| 비교 항목 | 클래식 암호화 (RSA/ECC) | 후량자 암호화 (PQC: Kyber, Dilithium) | 하이브리드 방식 (AWS 권장) |
| :--- | :--- | :--- | :--- |
| **기반 수학 문제** | 정수 인수분해, 이산로그 문제 | 격자 기반(Lattice), 부호 기반 등 | 위 두 가지 혼합 |
| **양자 내성** | ❌ 취약함 (Shor's Algorithm) | ✅ 강함 (검증됨) | ✅ 강함 (둘 중 하나만 안전해도 됨) |
| **알고리즘 신뢰도** | 높음 (수십 년간 검증됨) | 중간 (최신 표준, 검증 중) | 매우 높음 (Defense in Depth) |
| **키/암호문 크기** | 작음 | 큼 (성능 오버헤드 존재) | 큼 (PQC로 인한 오버헤드 흡수) |
| **주요 용도** | 현재 TLS, VPN, KMS | 미래 지향적 보안 통신 | 마이그레이션过渡기 |
| **실패 시 영향** | 모든 데이터 노출 | 모든 데이터 노출 | **최소화** (하나가 뚫려도 다른 하나 방어) |

### 4. 구현 가이드: 하이브리드 키 캡슐화 (Python)

방어 목적을 위해, Python을 사용하여 하이브리드 암호화의 개념을 구현해 보겠습니다. 실제 환경에서는 AWS KMS의 `Multi-Region keys`나 OpenSSL 3.0+의 PQC 모듈을 사용하겠지만, 여기서는 메커니즘 이해를 돕기 위해 로직을 단순화했습니다.

이 시나리오는 **"대칭키(세션 키)를 안전하게 전달하기 위해"** 클래식 키와 PQC 키를 각각 사용해 암호화하는 과정입니다.

```python
import os
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# --- 1. 시뮬레이션용 PQC 알고리즘 (Mock) ---
# 실제로는 'liboqs'나 'cryptography'의 최신 PQC 백엔드를 사용합니다.
class MockPQC:
    def encrypt(self, data):
        # 실제 Kyber 등은 복잡한 격자 연산을 수행합니다.
        # 여기서는 단순히 데이터 앞에 PQC 헤더를 붙이는 것으로 시뮬레이션합니다.
        return b"[PQC_ENCRYPTED]" + data

    def decrypt(self, data):
        if data.startswith(b"[PQC_ENCRYPTED]"):
            return data[15:]
        raise ValueError("PQC Decryption Failed")

# --- 2. 키 생성 (클래식 RSA) ---
def generate_classic_keys():
    private_key = serialization.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key

# --- 3. 하이브리드 암호화 로직 ---
def hybrid_encrypt_session_key(session_key, classic_pub_key, pqc_pub_key):
    # Step A: 클래식 암호로 세션 키 암호화
    classic_cipher = classic_pub_key.encrypt(
        session_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    # Step B: PQC 암호로 세션 키 암
```

---

**출처**: [https://news.google.com/rss/articles/CBMilgFBVV95cUxOQk1HUElFeDl2eXp1aU9lZHFmd0I3bUYydGd2NnJ2ak1GbnRlRUxxYVl6TEUyUmF5NEJyeFVnLWpOUkU2dWpGZldVaG04ZmMycmhJM2NrN19qNGxfX2I1bTRUU1RpNXFCY3VTYmR6LWhxNkYxU2t3VUpaT3U4b04yNENYa01iMDE1dmNHWWFyeTlxay1wMVE?oc=5](https://news.google.com/rss/articles/CBMilgFBVV95cUxOQk1HUElFeDl2eXp1aU9lZHFmd0I3bUYydGd2NnJ2ak1GbnRlRUxxYVl6TEUyUmF5NEJyeFVnLWpOUkU2dWpGZldVaG04ZmMycmhJM2NrN19qNGxfX2I1bTRUU1RpNXFCY3VTYmR6LWhxNkYxU2t3VUpaT3U4b04yNENYa01iMDE1dmNHWWFyeTlxay1wMVE?oc=5)