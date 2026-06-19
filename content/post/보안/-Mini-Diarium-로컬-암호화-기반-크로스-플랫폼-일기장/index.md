---
title: "🔒 Mini-Diarium: 로컬 암호화 기반 크로스 플랫폼 일기장"
date: 2026-04-19T08:06:14+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
draft: true
---

## 서론

최근 몇 년간 주요 클라우드 서비스에서 발생한 대규모 데이터 유출 사고들은 우리에게 "개인정보는 클라우드에 안전하지 않다"는 냉혹한 현실을 상기시켜 주었습니다. 보안이 철저하다고 믿었던 노트 앱이나 클라우드 스토리지에서 수백만 명의 일기와 메모가 고스란히 유출되었고, 해커들은 이를 이메일 피싱이나 인신공격에 악용했습니다. 심지어 법률적 기소 수단으로서 개인의 디지털 기록이 압수 수색되는 사례도 늘어나고 있습니다. 이처럼 타인의 서버에 내 가장 사적인 생각을 맡기는 행위는, 이제는 선택이 아닌 명백한 보안 리스크가 되었습니다.

우리는 "서버를 신뢰하지 않는(Zero Trust)" 모델을 개인용 소프트웨어에도 적용해야 합니다. 데이터 주권이 나에게 있고, 암호화 키조차도 나만의 소유여야 합니다. 이것이 바로 오픈소스 프로젝트인 **Mini-Diarium**이 등장한 배경입니다. 단순히 일기를 쓰는 앱을 넘어, 공격자의 침해 경로를 원천적으로 차단하는 '암호화된 요새'를 구축하는 것이 이 프로젝트의 핵심 목표입니다.

이 글에서는 Mini-Diarium이 어떻게 클라우드 의존성을 제거하고 로컬 환경에서 강력한 암호화를 구현하는지 기술적 관점에서 심층 분석하고, 실제 침투 테스트 관점에서 그 보안성을 검증해 보겠습니다.

## 본론: 로컬 퍼스트(Local-First) 아키텍처와 암호화 메커니즘

### 암호화 아키텍처의 이해

Mini-Diarium의 핵심은 'Client-Side Encryption'입니다. 데이터가 디스크에 기록되기 전, 메모리 상에서 이미 암호화가 완료된 상태여야 합니다. 즉, 해커가 물리적 장치를 탈취하거나 맬웨어가 파일 시스템을 스캔하더라도, 그들이 볼 수 있는 것은 무의미한 암호문(Ciphertext)뿐입니다.

일반적인 클라우드 앱과 Mini-Diarium의 데이터 처리 흐름을 비교하면 보안상의 차이가 명확해집니다.

```javascript
graph TD
    subgraph Cloud_App_Scenario
        A[User Input] --> B[Plain Text Upload]
        B --> C[Cloud Server]
        C --> D[Risk: Server Breach]
        C --> E[Risk: Subpoena]
    end

    subgraph Mini_Diarium_Scenario
        F[User Input] --> G[Key Derivation]
        G --> H[AES-256 Encryption]
        H --> I[Local Storage]
    end
```

위 다이어그램에서 볼 수 있듯이, 클라우드 앱은 평문(Plain Text)을 서버로 전송하는 순간 공격 벡터가 노출됩니다. 반면, Mini-Diarium은 사용자의 기기 내부에서 비밀번호를 키(Key)로 변환하고 데이터를 즉시 암호화하여 로컬에 저장합니다. 이 과정에서 외부 네트워크로 데이터가 나가지 않으므로 중간자 공격(Man-in-the-Middle Attack)이나 서버 해킹 위협으로부터 완벽하게 격리됩니다.

### 암호화 알고리즘 및 키 관리

보안 전문가로서 Mini-Diarium의 코드를 리뷰할 때 가장 주의 깊게 보는 부분은 **어떤 알고리즘을 사용하는가**와 **키를 어떻게 생성하고 관리하는가**입니다. 현대적인 암호화 표준을 따르는 앱은 대체로 AES-256(Advanced Encryption Standard) 알고리즘을 사용하며, 키 생성을 위해 PBKDF2나 Argon2와 같은 키 파생 함수(KDF)를 사용하여 사용자 비밀번호를 보강합니다.

사용자가 '1234' 같은 취약한 비밀번호를 입력하더라도, KDF를 거치며 수만 번의 해싱 과정을 거쳐 컴퓨팅 파워로 뚫기 어려운 강력한 암호화 키로 변환됩니다. 이는 공격자가 무차별 대입 공격(Brute-force Attack)을 시도할 때 드는 비용을 기하급수적으로 높이는 방어 기제입니다.

이를 파이썬을 통해 개념적으로 증명하는 PoC(Proof of Concept) 코드를 작성해 보겠습니다.

```python
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

# 윤리적 경고: 이 코드는 암호화 원리를 학습하고 방어 목적으로 구현된 것입니다.
# 실제 운영 환경에서는 잘 테스트된 라이브러리의 고수준 API를 사용하십시오.

def encrypt_journal_entry(password, plaintext):
    # 1. 솔트(Salt) 생성: 매번 다른 키를 생성하기 위한 무작위 값
    salt = os.urandom(16)
    
    # 2. 키 파생 함수(KDF)를 사용한 키 생성 (PBKDF2-HMAC-SHA256)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32, # 256 bits
        salt=salt,
        iterations=480000, # 반복 횟수가 높을수록 무차별 대입 공격에 강함
    )
    key = kdf.derive(password.encode())
    
    # 3. AES-GCM 초기화 벡터(IV) 생성
    iv = os.urandom(12)
    
    # 4. AES-GCM 암호화 객체 생성
    encryptor = Cipher(algorithms.AES(key), modes.GCM(iv)).encryptor()
    
    # 5. 데이터 암호화
    ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()
    
    # 6. 결과 패킹 (Salt + IV + Tag + Ciphertext)
    # Tag은 데이터 무결성 검증에 사용됨
    return base64.b64encode(salt + iv + encryptor.tag + ciphertext).decode('utf-8')

# 시나리오: 사용자가 비밀 일기를 작성함
user_password = "MyStrongP@ssw0rd!"
secret_diary = "오늘 회의에서 보안 결함을 발견했다. 이 내용은 누구에게도 알리지 말아야 한다."

# 암호화 수행
encrypted_data = encrypt_journal_entry(user_password, secret_diary)

print(f"Original: {secret_diary}")
print(f"Encrypted: {encrypted_data}")
```

이 코드는 Mini-Diarium과 같은 앱이 내부적으로 수행하는 과정을 단순화한 것입니다. `Salt`와 `IV`가 매번 랜덤하게 생성되므로, 같은 비밀번호와 같은 일기 내용을 입력하더라도 결과값은 매번 달라집니다. 이는 공격자가 패턴을 분석하려는 시도를 무력화시킵니다.

### 보안 위협 모델 및 비교 분석

침투 테스트 관점에서 Mini-Diarium을 분석할 때, 우리는 주로 '물리적 장치 탈취' 시나리오를 가정합니다. 노트북이 도난당하거나 외장 하드에 백업된 파일이 유출되었을 때, 데이터가 안전한가?

아래 표는 일반적인 클라우드 기반 저널링 앱과 Mini-Diarium의 보안 특성을 비교한 것입니다.

| 보안 특성 | 일반적인 클라우드 앱 (SaaS) | Mini-Diarium (Local-First) |
| :--- | :--- | :--- |
| **저장소 위치** | 원격 서버 (Third-party Server) | 로컬 디스크 (User Device) |
| **데이터 상태** | 서버 측 암호화 (키 소유권 불확실) | 클라이언트 측 암호화 (사용자 키 소유) |
| **주요 공격 벡터** | 서버 해킹, 내부자 위협, 계정 탈취 | 물리적 도난, 로컬 맬웨어, 키로그거 |
| **압수 수색 대응** | 서버 제공자가 데이터 제공 가능 | 데이터만 압수되어도 복호화 불가능 |
| **오프라인 접근** | 불가능 (인터넷 필수) | 언제든 가능 |
| **소스 코드 검증** | 불가능 (Black Box) | 가능 (Open Source) |

이 표에서 가장 중요한 차이점은 '키 소유권'입니다. 클라우드 서비스는 "우리는 암호화합니다"라고 말하지만, 복호화 키는 종종 서버 측에 있거나 비밀번호 재설정 기능을 위해 저장됩니다. 즉, 공급자가 데이터를 볼 수 있습니다. 반면 Mini-Diarium에서는 사용자가 비밀번호를 잊으면 영원히 데이터를 열 수 없습니다. 이는 기능의 결핍이 아니라, 완벽한 보안을 위한 필수적인 트레이드오프입니다.

### 완화 조치 및 안전한 사용 가이드

아무리 강력한 암호화 앱이라도 사용자의 잘못된 설정이나 행동으로 인해 뚫릴 수 있습니다. Mini-Diarium을 최대한 안전하게 사용하기 위한 실무적 가이드를 제시합니다.

1.  **강력한 비밀번호 정책(Password Policy) 수립**     *   암호화 강도는 암호화 알고리즘보다 비밀번호의 엔트로피(Entropy)에 의존적입니다.     *   **가이드**: 최소 12자리 이상, 대소문자/숫자/특수문자 포함, 개인정보(생일, 이름 등) 미포함.     *   **전문가 팁**: 문장형 비밀번호(Passphrase) 추천 (예: `Coffee!Mountain#Blue$Sky2024`). 기억하기 쉽고 충돌 가능성이 극히 낮습니다.

2.  **정기적인 로컬 백업 및 암호화된 저장**     *   로컬 앱의 단점은 하드디스크 장애 시 데이터 소멸 위험입니다.     *   **가이드**: Mini-Diarium의 데이터베이스 파일(.db, .diary 등)을 주기적으로 백업하되, 이 백업 파일 역시 암호화된 상태로 저장하거나, VeraCrypt와 같은 디스크 암호화 도구를 사용해 보관합니다. 절대 백업 파일을 그대로 클라우드에 업로드하지 마십시오.

3.  **시스템 전체 보안 강화**     *   앱 자체가 뚫리지 않더라도 키로거(Keylogger)가 박히면 비밀번호가 탈취됩니다.     *   **가이드**: OS 최신 업데이트 유지, 백신/EDR 솔루션 실시간 탐지 실행, 의심스러운 설치 파일 실행 금지.

## 결론

Mini-Diarium은 단순한 일기장 앱이 아닌, 프라이버시가 침해받기 쉬운 디지털 시대에 개인의 영역을 지키는 방패와 같습니다. 클라우드 서버에 데이터를 맡기는 대신, 수학적으로 검증된 암호화 기술을 통해 내 기기에만 책임을 지우는 **'Local-First'** 패러다임은 보안 전문가로서 매우 반가운 접근법입니다.

우리는 지금 데이터 유출 사고 뉴스에 무감각해져 가고 있지만, 내 가장 사적인 기록들이 공개되는 상황을 상상해 보면 그 위험도는 명확합니다. Mini-Diarium은 소스 코드가 공개되어 있어 누구나 그 보안 메커니즘을 감사할 수 있다는 점에서 투명성을 확보했습니다. "눈에 보이지 않는 곳에서 무슨 일이 일어나는지 모르는" 상태가 가장 위험한 것입니다.

결론적으로, 보안은 도구의 설정값 몇 가지가 아니라 사용자의 **'데이터 주권 의식'**에서 시작됩니다. 여러분이 기록하는 모든 데이터에는 당신의 정체성이 담겨 있습니다. 그 데이터를 보호할 책임은 서비스 제공자가 아닌 바로 여러분에게 있습니다. Mini-Diarium과 같은 도구를 활용해 암호화의 힘을 직접 쥐고, 디지털 프라이버시의 주도권을 되찾으시길 권장합니다.

### 참고자료
- [Mini-Diarium GitHub Repository](https://github.com/fjrevoredo/mini-diarium)
- [Cryptography Library Documentation](https://cryptography.io/)
- [OWASP Key Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Key_Management_Cheat_Sheet.html)

---

**출처**: [https://github.com/fjrevoredo/mini-diarium](https://github.com/fjrevoredo/mini-diarium)