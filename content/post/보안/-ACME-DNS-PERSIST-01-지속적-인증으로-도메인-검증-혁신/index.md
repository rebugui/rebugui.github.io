---
title: "🔒 ACME DNS-PERSIST-01: 지속적 인증으로 도메인 검증 혁신"
date: 2026-04-19T08:06:13+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 서론

새벽 2시, 모니터를 밝히며 경고 알림을 확인하는 시스템 엔지니어의 모습은 우리에게 익숙한 악몽과도 같습니다. 바로 "SSL/TLS 인증서 만료 경고"입니다. 완벽하게 자동화되었다고 믿었던 Let's Encrypt 인증서 갱신 스크립트가 DNS 제공자의 API 일시적 장애 혹은 Rate Limit 제한으로 인해 실패한 상황입니다. 이로 인해 웹 서비스는 중단되고, 사용자들은 "연결이 안전하지 않음" 경고를 마주하게 됩니다.

이는 단순한 불편함을 넘어 보안 위협입니다. 서비스 중단(Downtime)은 가용성을 목표로 하는 보안의 기본 원칙을 무너뜨립니다. 우리가 ACME 프로토콜(Automatic Certificate Management Environment)을 사용하며 겪는 가장 큰 고통은 바로 **'반복적인 검증(Recurring Validation)'**입니다. 90일마다 혹은 그 이하의 주기로 인증서를 갱신할 때마다, 매번 DNS 레코드를 생성하고 삭제하는这套繁瑣한 절차는 필연적으로 장애 지점을 늘립니다.

오늘 소개할 **ACME DNS-PERSIST-01**은 이러한 자동화의 역설을 해결하기 위한 새로운 접근법입니다. "도메인 제어권을 한번 증명하면, 왜 매번 다시 증명해야 하는가?"라는 직관적인 질문에서 시작된 이 모델은 특정 ACME 계정과 CA(인증 기관)에 바인딩된 지속적인 TXT 레코드를 통해 운영의 효율성과 안정성을 동시에 잡는 방안을 제시합니다.

## 본론

### 기존 dns-01 챌린지의 구조적 한계와 위협 모델

기존의 ACME 프로토콜에서 가장 널리 쓰이는 `dns-01` 챌린지는 도메인의 제어권을 증명하기 위해 클라이언트가 DNS 제공자의 API를 호출하여 `_acme-challenge.example.com`과 같은 서브도메인에 특정 토큰 값이 포함된 TXT 레코드를 생성하는 방식입니다.

이 과정에서 발생하는 보안 및 운영상의 문제점은 다음과 같습니다:

1.  **높은 장애 발생 가능성 (Availability Risk)**: 인증서 갱신 주기마다 외부 DNS API와의 통신이 필수적입니다. DNS 제공자의 장애, API 토큰 만료, 혹은 Rate Limiting 공격 등은 인증서 갱신 실패로 직결됩니다.
2.  **자격 증명 노출 위험**: 갱신 스크립트에 DNS 관리자 권한(Token)이 포함되어 있어, 해당 스크립트가 탈취당할 경우 공격자는 도메인의 DNS 레코드를 마음대로 조작할 수 있습니다.

이러한 문제를 해결하기 위해 제안된 것이 DNS-PERSIST-01 모델입니다. 이는 **지속성(Persistence)**을 핵심 메커니즘으로 사용합니다.

### DNS-PERSIST-01 작동 원리 및 메커니즘

DNS-PERSIST-01의 핵심은 ACME 계정의 공개키(Account Key)와 특정 CA가 서명한 영수증(혹은 지문)을 미리 DNS에 등록해두는 것입니다. 인증서 갱신 시마다 매번 새로운 값을 쓰는 것이 아니라, 사전에 등록된 **'신뢰할 수 있는 키'**의 존재 여부만을 확인합니다.

다음은 기존 방식과 지속적 검증 방식의 흐름을 비교한 다이어그램입니다.

```javascript
graph TD
    subgraph Legacy_dns-01
        A1[Client] -->|API Call| B1[DNS Provider]
        B1 -->|Create Temp Token| C1[_acme-challenge TXT]
        C1 -->|Validation| D1[CA Server]
        D1 -->|Success| E1[Issue Cert]
        A1 -->|Cleanup| B1
    end

    subgraph DNS_PERSIST_01
        A2[Client] -->|One-time Setup| B2[DNS Provider]
        B2 -->|Create Persistent Key| C2[_acme-persist TXT]
        A2 -->|Request Cert| D2[CA Server]
        D2 -->|Verify Persistent Key| C2
        C2 -->|Matched| E2[Issue Cert]
    end
```

이 모델에서 중요한 점은 **Account Binding**입니다. 공격자가 단순히 웹 서버를 장악했다고 해서, 이 지속적 레코드를 수정할 수는 없습니다. 이 레코드는 오직 도메인 관리자만이 수정할 수 있는 DNS 영역에 존재하기 때문입니다.

### 기술적 세부 사항 및 비교

기존 `dns-01`과 새로운 `dns-persist-01`의 기술적 차이는 명확합니다. 아래 표는 두 방식의 특성을 비교 분석한 것입니다.

| 비교 항목 | 기존 dns-01 (Ephemeral) | dns-persist-01 (Persistent) |
| :--- | :--- | :--- |
| **레코드 수명** | 임시 (검증 직후 삭제) | 반영구적 (키가 유효한 한 유지) |
| **갱신 시 API 호출** | 매번 필수 (Create + Delete) | 초기 설정 이후 불필요 (검증만 수행) |
| **주요 장애 요인** | DNS API 장애, Rate Limit | 없음 (DNS는 읽기만 수행) |
| **보안 핵심** | Token 검증 | Account Key Fingerprint 검증 |
| **운영 복잡도** | 높음 (API 토큰 관리, 스크립트 유지보수) | 낮음 (초기 설정 후 자동화 안정화) |

### 구현 가이드: Python을 이용한 PoC (개념 증명)

*이 코드는 학습 및 방어 목적의 개념 증명(PoC)입니다. 실제 운영 환경에서는 반드시 해당 CA가 제공하는 공식 클라이언트 라이브러리를 사용하십시오.*

DNS-PERSIST-01 방식에서는 클라이언트가 자신의 ACME 계정 공개키로부터 고유한 지문(Fingerprint)을 생성하고, 이를 DNS TXT 레코드로 등록해야 합니다. 아래는 이 과정을 시뮬레이션한 Python 코드입니다.

```python
import hashlib
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# 1. ACME 계정 키 생성 (실제로는 이미 존재하는 키를 로드합니다)
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

public_key = private_key.public_key()
public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# 2. 공개키 지문(Fingerprint) 생성
# CA와 협의된 해시 알고리즘(예: SHA-256)을 사용하여 공개키를 해싱합니다.
# 이 값이 DNS에 등록될 '지속적 인증 값'입니다.
digest = hashlib.sha256(public_pem).digest()
fingerprint_b64 = base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')

print(f"[+] Generated Account Key Fingerprint for DNS-PERSIST-01")
print(f"[+] DNS Record Name: _acme-persist.example.com")
print(f"[+] DNS Record Value: {fingerprint_b64}")

# 3. 시나리오: 공격자가 웹서버에 접근했지만 DNS를 변경할 수 없는 경우
print("
[!] Security Scenario Check:")
print("[!] Attacker compromised web server files.")
print("[!] Attacker attempts to issue a new certificate.")
print("[*] CA queries _acme-persist.example.com...")
print(f"[*] CA expects: {fingerprint_b64}")
print("[!] Attacker cannot change DNS record without DNS Admin credentials.")
print("[+] Validation FAILED. Certificate issuance denied.")
```

이 코드가 시사하는 바는 명확합니다. 공격자가 웹 서버의 파일 시스템을 모두 탈취하더라도, 도메인 관리 권한(DNS)이 분리되어 있는 한 인증서 발급을 막을 수 있습니다. 반대로, 운영자는 DNS 레코드 한 번만 안전하게 설정해두면, 이후 복잡한 갱신 스크립트의 유지보수 부담에서 벗어날 수 있습니다.

### 방어 전략 및 완화 조치

DNS-PERSIST-01을 도입할 때 고려해야 할 보안상의 완화 조치는 다음과 같습니다.

1.  **DNSSEC 강화**: 지속적인 레코드의 무결성이 중요하므로, 해당 도메인은 반드시 DNSSEC(DNS Security Extensions)이 활성화되어 있어야 합니다. 이를防止 DNS 캐싱 공격으로 인한 검증 우회를 방지할 수 있습니다.
2.  **레코드 롤오버(Rollover) 정책 수립**: "지속적"이라고 해서 영구적인 것은 아닙니다. ACME 계정 키가 노출되었다고 판단되면, 즉시 새로운 키 쌍을 생성하고 DNS 레코드를 업데이트하는 절차가 마련되어 있어야 합니다.
3.  **CNAME 체이닝 활용**: 대규모 인프라의 경우, `_acme-persist` 레코드를 단일 관리 포인트로 CNAME 연결하여 관리 오버헤드를 줄이는 것이 좋습니다.

## 결론

ACME DNS-PERSIST-01은 단순히 편의를 위한 프로토콜 변경이 아닙니다. 이는 **"자동화된 시스템의 안정성이 곧 보안이다"**라는 현대적 DevSecOps 철학을 반영한 설계입니다.

기존 `dns-01` 방식이 갖는 "잦은 쓰기 작업(Write Operation)"으로 인한 취약점을 제거하고, DNS를 "읽기 전용 신뢰 저장소(Read-only Trust Store)"로 활용함으로써, 우리는 공격 표면(Available Surface)을 획기적으로 줄일 수 있습니다. 물론, 지속적 레코드 관리를 위한 초기 설정과 키 교체 정책 수립이 필요하지만, 그 이득은 90일마다 발생하는 악몽 같은 새벽 작업을 없애는 것으로 충분히 보상받을 수 있습니다.

보안 전문가로서, 저는 이러한 프로토콜의 진화가 단순한 기술적 개선을 넘어 인프라 운영의 패러다임을 "반응형(Reactive)"에서 "선제적이고 안정적인(Proactive & Stable)" 모델로 변화시킨다고 봅니다. 여러분의 PKI 인프라에도 이러한 지속적 검증 모델을 도입하여 고도화된 안정성을 경험해 보시기를 권장합니다.

### 참고자료
- [Hada.io - DNS-PERSIST-01: DNS 기반 챌린지 검증을 위한 새로운 모델](https://news.hada.io/topic?id=26825)
- [IETF ACME Working Group Drafts](https://datatracker.ietf.org/wg/acme/about/)

---

**출처**: [https://news.hada.io/topic?id=26825](https://news.hada.io/topic?id=26825)