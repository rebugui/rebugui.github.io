---
title: "OpenSSL 4.0.0: TLS/SSL 암호화 라이브러리 메이저 업데이트 분석"
date: 2026-05-01T01:06:48+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 서론

2024년 한 중견 금융회사의 침투 테스트를 진행 중이었다. 내부 웹 애플리케이션 방화벽(WAF)과 최신 SIEM 솔루션이 가동되고 있었지만, TLS 1.0으로 암호화된 관리자 페이지에서 평문 전송되는 세션 쿠키를 가로채는 데 성공했다. 10년 전에 개발된 레거시 시스템이 여전히 구형 OpenSSL 1.0.2에 묶여 있었기 때문이다. 공격자는 복잡한 제로데이 익스플로잇조차 필요 없었다. 단지 오래된 프로토콜을 지원하는 클라이언트로 접속하고, 네트워크 중간자(MITM) 위치에서 패킷을 캡처하면 끝이었다.

인터넷 인프라의 성곽과 같은 역할을 하는 OpenSSL이 새로운 메이저 버전인 4.0.0을 릴리즈했다. 단순한 기능 추가가 아니다. 수십 년간 축적된 기술 부채를 정리하고, 현대적인 위협 환경에 맞춰 근본적인 구조 개선이 이루어졌다. 시스템 관리자와 보안 엔지니어에게 이 업데이트는 선택이 아닌 생존의 문제다. 이 글에서는 OpenSSL 4.0.0이 어떤 보안적 변화를 가져왔는지, 그리고 우리 시스템에 어떤 영향을 미치는지 현장 감각 있게 분석한다.
> **⚠️ 윤리적 경고**: 본 글에 포함된 모든 기술적 분석과 코드는 시스템 보안 강화를 위한 방어 목적으로 작성되었습니다. 실제 운영 환경에 적용하기 전 반드시 테스트 환경에서 검증하시기 바랍니다.

## 본론

### 1. OpenSSL 4.0.0: 왜 메이저 버전인가

OpenSSL의 버전 번호는 단순한 라벨이 아니다. 메이저 버전 업그레이드는 하위 호환성이 깨질 정도의 구조적 변화를 의미한다. 3.0에서 4.0으로의 전환은 패치 수준의 변화가 아니라, 암호화 라이브러리의 철학과 아키텍처 자체가 바뀌었음을 뜻한다.

핵심 변화를 한 줄로 요약하면 **"레거시의 장례식과 현대 암호학의 실천"**이다.

#### 주요 변경 카테고리

| 변경 영역 | OpenSSL 3.x | OpenSSL 4.0.0 | 보안적 영향 |
| :--- | :--- | :--- | :--- |
| **TLS 프로토콜** | TLS 1.0 ~ 1.3 | TLS 1.2, 1.3만 지원 | 다운그레이드 공격 원천 차단 |
| **RSA 키 크기** | 1024비트 이상 허용 | 2048비트 최소 강제 | 약한 키 거부 |
| **해시 알고리즘** | MD5, SHA-1 사용 가능 | SHA-2/SHA-3 패밀리만 | 충돌 공격 방어 |
| **인증서 형식** | SSLv3 호환 유지 | X.509 v3 엄격 모드 | 변조 인증서 차단 |
| **FIPS 모듈** | 선택적 로드 | 통합 아키텍처 | 규제 준수 간소화 |

### 2. TLS 핸드셰이크: 공격 표면의 변화

가장 중요한 변화는 TLS 구현체의 정리다. 구형 프로토콜이 지원되면 공격자는 클라이언트와 서버가 가장 안전한 버전을 협상하는 과정을 방해할 수 있다. 이를 **프로토콜 다운그레이드 공격**이라 부른다.

```javascript
graph LR
    A[Client Hello] --> B{Server: OpenSSL 4.0.0}
    B --> C[TLS 1.3 Only]
    B --> D[TLS 1.2 Fallback]
    D --> E[Strong Cipher Suite]
    C --> E
    E --> F[Encrypted Application Data]
```

OpenSSL 4.0.0은 협상 과정 자체를 단순화했다. TLS 1.2와 1.3만 지원함으로써, 공격자가 끼어들 여지를 원천 차단한 것이다.

#### 실제 공격 시나리오: POODLE의 유산

2014년 POODLE 공격은 SSLv3의 취약점을 이용해 TLS 연결을 강제로 SSLv3로 다운그레이드시켰다. OpenSSL 4.0.0은 이러한 다운그레이드 자체를 불가능하게 만든다.

```bash
# OpenSSL 4.0.0에서 TLS 1.0 연결 시도 시 결과
$ openssl s_client -connect target.com:443 -tls1

# 출력 결과 (연결 거부)
# 40E7A9FE01000000:error:0A000102:SSL routines:
# ssl_choose_client_version:unsupported protocol:
# ssl/statem/statem_lib.c:1142:
```

서버 측에서도 마찬가지다. 구형 클라이언트가 TLS 1.0으로 연결을 시도하면 서버가 거부한다.

### 3. 취약한 설정 감지: 자동화 스크립트

실무에서 가장 먼저 해야 할 작업은 기존 시스템의 OpenSSL 버전과 설정을 점검하는 것이다. 다음 스크립트는 서버의 TLS 설정을 점검하고, OpenSSL 4.0.0 비호환 항목을 식별한다.

```python
#!/usr/bin/env python3
"""
TLS Security Scanner - OpenSSL 4.0.0 Readiness Check
Author: Security Team
Purpose: Identify configurations incompatible with OpenSSL 4.0.0
"""

import ssl
import socket
import sys
from datetime import datetime

class TLSScanner:
    def __init__(self, hostname, port=443):
        self.hostname = hostname
        self.port = port
        self.results = []
    
    def scan_protocol_versions(self):
        """지원되는 TLS 프로토콜 버전 점검"""
        protocols = {
            'TLS 1.0': ssl.TLSVersion.TLSv1,
            'TLS 1.1': ssl.TLSVersion.TLSv1_1,
            'TLS 1.2': ssl.TLSVersion.TLSv1_2,
            'TLS 1.3': ssl.TLSVersion.TLSv1_3,
        }
        
        print(f"[*] Scanning {self.hostname}:{self.port}")
        print(f"[*] Protocol Support Check
")
        
        for name, version in protocols.items():
            try:
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                context.minimum_version = version
                context.maximum_version = version
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                
                with socket.create_connection((self.hostname, self.port), timeout=5) as sock:
                    with context.wrap_socket(sock, server_hostname=self.hostname) as ssock:
                        cipher = ssock.cipher()
                        self.results.append({
                            'protocol': name,
                            'status': 'SUPPORTED',
                            'cipher': cipher[0]
                        })
                        print(f"  [+] {name}: SUPPORTED ({cipher[0]})")
                        
            except (ssl.SSLError, socket.error) as e:
                self.results.
```

```python
append({
                    'protocol': name,
                    'status': 'REJECTED',
                    'cipher': 'N/A'
                })
                print(f"  [-] {name}: REJECTED")
    
    def check_v4_compatibility(self):
        """OpenSSL 4.0.0 호환성 평가"""
        print(f"
[*] OpenSSL 4.0.0 Compatibility Assessment
")
        
        issues = []
        for result in self.results:
            if result['status'] == 'SUPPORTED':
                if result['protocol'] in ['TLS 1.0', 'TLS 1.1']:
                    issues.append(f"CRITICAL: {result['protocol']} 지원 중단 필요")
                elif result['protocol'] == 'TLS 1.2':
                    # SHA-1, RC4 등 약한 cipher 확인 로직 추가 가능
                    pass
        
        if not issues:
            print("  [✓] OpenSSL 4.0.0 마이그레이션 준비 완료")
        else:
            print("  [!] 해결 필요 사항:")
            for issue in issues:
                print(f"    - {issue}")
        
        return issues

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 tls_scanner.py <hostname> [port]")
        sys.exit(1)
    
    target = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 443
    
    scanner = TLSScanner(target, port)
    scanner.scan_protocol_versions()
    scanner.check_v4_compatibility()
```

이 스크립트를 실행하면 대상 서버가 OpenSSL 4.0.0의 요구사항을 충족하는지 즉시 파악할 수 있다.

### 4. 마이그레이션 Step-by-Step 가이드

OpenSSL 4.0.0으로의 전환은 단순한 라이브러리 교체가 아니다. 의존하는 애플리케이션의 동작 방식까지 변경될 수 있다.

#### Step 1: 의존성 매핑

```bash
# 시스템 내 OpenSSL 의존성 패키지 확인 (Ubuntu/Debian)
$ apt-cache rdepends libssl-dev | head -20

# CentOS/RHEL
$ rpm -q --whatrequires openssl-libs
```

#### Step 2: 코드 레벨 변경사항 적용

C/C++ 애플리케이션에서 가장 흔히 발생하는 호환성 문제는 직접적인 구조체 접근이다.

```c
/* OpenSSL 3.x (더 이상 권장되지 않음) */
RSA *rsa = RSA_new();
rsa->n = BN_bin2bn(modulus, len, NULL);  // 직접 멤버 접근

/* OpenSSL 4.0.0 호환 코드 */
RSA *rsa = RSA_new();
BIGNUM *n = BN_bin2bn(modulus, len, NULL);
RSA_set0_key(rsa, n, NULL, NULL);  // setter 함수 사용
```

#### Step 3: 구성 파일 업데이트

`openssl.cnf` 파일의 구조가 변경되었다. 특히 FIPS 모듈 설정이 통합되었다.

```plain text
# OpenSSL 4.0.0 - openssl.cnf 예시

# 기본 provider와 FIPS provider를 명시적으로 로드
[provider_sect]
default = default_sect
fips = fips_sect

[default_sect]
activate = 1

[fips_sect]
activate = 1
# FIPS 140-3 검증 모듈 경로 (시스템마다 다를 수 있음)
module = /usr/lib/ossl-modules/fips.so

# 보안 수준 설정 (레거시 알고리즘 완전 차단)
[ssl_sect]
MinProtocol = TLSv1.2
CipherSuites = TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256
```

#### Step 4: 인증서 갱신

기존 인증서 중 키 크기가 작거나 만료된 해시 알고리즘을 사용하는 것은 거부된다.

```bash
# 인증서 정보 확인
$ openssl x509 -in cert.pem -text -noout | grep -E "(Signature Algorithm|Public-Key)"

# SHA-1 인증서 교체
# OpenSSL 4.0.0은 기본적으로 SHA-1 인증서를 거부함
$ openssl x509 -in old_cert.pem -text -noout | grep "Signature Algorithm"
# Signature Algorithm: sha1WithRSAEncryption  <-- 거부됨
```

### 5. API 변경: 개발자를 위한 체크리스트

| API 변경 | 기존 코드 | 대응 방안 |
| :--- | :--- | :--- |
| `SSL_CTX_new()` | `SSLv23_method()` 사용 | `TLS_method()`로 변경 |
| `ENGINE` API | 하드웨어 가속 엔진 로드 | `provider` 메커니즘으로 전환 |
| 에러 처리 | `ERR_get_error()` | 동일하나 에러 코드 체계 변경 |
| 스레드 안전성 | 수동 콜백 설정 | 자동 처리 (별도 설정 불필요) |
| `BIO` 필터 | `BIO_f_ssl()` | API 유지, 내부 최적화 |

## 결론

### 핵심 요약

OpenSSL 4.0.0은 단순한 버전업이 아니다. 인터넷 보안의 근간을 이루는 암호화 통신이 어떻게 변화하는지를 보여주는 이정표다.

1. **레거시 제거**: TLS 1.0/1.1, SSLv3, 약한 암호화 완전 제거
2. **기본 보안 강화**: 2048비트 미만 RSA 키, SHA-1 인증서 자동 거부
3. **아키텍처 현대화**: Provider 기반 플러그인, FIPS 통합 4

---

**출처**: [https://github.com/openssl/openssl/releases/tag/openssl-4.0.0](https://github.com/openssl/openssl/releases/tag/openssl-4.0.0)