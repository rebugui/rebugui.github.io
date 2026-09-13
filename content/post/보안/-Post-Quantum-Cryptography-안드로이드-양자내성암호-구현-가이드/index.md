---
title: "🔒 Post-Quantum Cryptography: 안드로이드 양자내성암호 구현 가이드"
date: 2026-03-28T01:05:05+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 서론

"지금 수집하고, 나중에 해독한다(Store Now, Decrypt Later)."

국가급 위협 행위자들이 수년간 전 세계의 암호화 통신을 수집하고 있다는 건 보안 업계의 공공연한 비밀이다. 당장은 해독할 수 없지만, 양자컴퓨터가 실용화되는 순간 수집된 모든 데이터가 한순간에 평문으로 전락한다. 오늘 당신의 은행 거래, 의료 기록, 기업 영업비밀이 저장되고 있다는 것이다.

이것은 SF 소설이 아니다. 2024년 NIST가 Post-Quantum Cryptography(PQC) 표준을 최종 발표했고, Google은 이미 Android 14부터 ML-KEM(Kyber)과 ML-DSA(Dilithium)를 탑재하기 시작했다. 양자컴퓨터가 실제로 위협이 되기 전에, 우리는 미리 방어 태세를 갖춰야 한다.

이 글에서는 안드로이드 개발자가 **실제로 PQC를 구현하는 방법**을 단계별로 다룬다. 격자 기반 암호의 원리부터 하이브리드 암호 체계 구축까지, 실무에서 바로 적용 가능한 가이드를 제공한다.

---

## 본론

### 1. 양자컴퓨터가 기존 암호를 무력화하는 원리

기존 공개키 암호 시스템(RSA, ECC)의 보안성은 특정 수학적 문제의 난이도에 기반한다. RSA는 큰 정수의 소인수분해, ECC는 타원곡선 이산대수 문제다. 이들은 고전 컴퓨터로는 다항 시간 내에 풀 수 없지만, 양자컴퓨터에서는 **Shor 알고리즘**을 통해 지수적 가속이 가능하다.

```javascript
graph TD
    A[기존 공개키 암호] --> B[수학적 난제 의존]
    B --> C[소인수분해 RSA]
    B --> D[이산대수 문제 ECC]
    
    E[양자컴퓨터] --> F[Shor 알고리즘]
    F --> G[다항 시간 해결]
    G --> H[RSA 2048bit 해독]
    G --> I[ECC P-256 해독]
    
    H --> J[암호체계 붕괴]
    I --> J
```

2048비트 RSA 키는 고전 컴퓨터로 수십억 년이 걸리지만, 충분한 큐비트를 가진 양자컴퓨터로는 몇 시간 내에 해독 가능하다. IBM, Google, 중국 등이 경쟁적으로 양자컴퓨터를 개발 중이며, "암호학적으로 유의미한 양자컴퓨터(Cryptographically Relevant Quantum Computer, CRQC)"는 2030년대 초반 등장이 예상된다.

### 2. Post-Quantum Cryptography: 새로운 패러다임

PQC는 양자컴퓨터의 공격에도 안전한 암호 알고리즘이다. 2024년 NIST가 최종 표준화한 주요 알고리즘은 다음과 같다:

| 알고리즘 | 유형 | 용도 | 키 크기 (공개키) | NIST 표준명 |
| :--- | :--- | :--- | :--- | :--- |
| CRYSTALS-Kyber | 격자 기반 (Lattice) | 키 교환/KEM | 1,188 bytes | ML-KEM-768 |
| CRYSTALS-Dilithium | 격자 기반 (Lattice) | 디지털 서명 | 1,952 bytes | ML-DSA-65 |
| SPHINCS+ | 해시 기반 | 디지털 서명 | 32 bytes | SLH-DSA |
| FALCON | 격자 기반 (NTRU) | 디지털 서명 | 897 bytes | fn-DSA |

**격자 기반 암호(Lattice-based Cryptography)**의 핵심 원리는 다음과 같다:

격자(Lattice)는 n차원 공간에서 정수 좌표를 가진 점들의 규칙적인 배열이다. 격자 기반 암호는 "최단 벡터 문제(SVP)"나 "학습 오류(LWE)" 문제에 기반하는데, 이들은 양자컴퓨터로도 효율적으로 풀 수 없음이 증명되었다.

```python
# LWE(Learning With Errors) 문제의 개념적 이해
# 실제 구현은 아니지만, 원리를 보여주는 예시

import numpy as np

def lwe_key_generation(n=256, q=3329):
    """LWE 기반 키 생성의 개념적 구현"""
    # 비밀키 s: 작은 값들을 가진 벡터
    s = np.random.randint(-2, 3, size=n)
    
    # 공개 행렬 A: 무작위 값
    A = np.random.randint(0, q, size=(n, n))
    
    # 오류 벡터 e: 작은 값들
    e = np.random.randint(-2, 3, size=n)
    
    # 공개키 b = (A * s + e) mod q
    b = (np.dot(A, s) + e) % q
    
    return {
        'public_key': (A, b),
        'secret_key': s
    }

# 공격자가 s를 찾기 위해서는 A와 b만으로
# 오류가 포함된 연립방정식을 풀어야 함
# 이는 양자컴퓨터로도 NP-hard 문제
```

### 3. Android에서 PQC 구현: Step-by-Step Guide

Google은 Android 14부터 Bouncy Castle 라이브러리를 통해 PQC 알고리즘을 지원하기 시작했다. 하지만 안정적인 구현을 위해서는 몇 가지 단계를 거쳐야 한다.

#### Step 1: 의존성 추가

```plain text
// build.gradle (Module level)
dependencies {
    // Bouncy Castle 최신 버전 (PQC 지원)
    implementation 'org.bouncycastle:bcprov-jdk18on:1.78.1'
    implementation 'org.bouncycastle:bcpqc-jdk18on:1.78.1'
}
```

#### Step 2: ML-KEM(Kyber) 키 교환 구현

```kotlin
// PQCKeyExchange.kt
package com.example.pqcdemo

import org.bouncycastle.crypto.AsymmetricCipherKeyPair
import org.bouncycastle.pqc.crypto.crystals.kyber.*
import org.bouncycastle.pqc.jcajce.provider.BouncyCastlePQCProvider
import java.security.SecureRandom
import android.util.Base64

class PQCKeyExchange {
    
    private val provider = BouncyCastlePQCProvider()
    
    /**
     * ML-KEM-768 키 쌍 생성
     * Kyber3이 NIST 표준 ML-KEM-768에 해당
     */
    fun generateKeyPair(): KEMKeyPair {
        val keyGenParameters = KyberKeyGenerationParameters(
            SecureRandom(),
            KyberParameters.kyber768  // ML-KEM-768
        )
        
        val keyPairGenerator = KyberKeyPairGenerator()
        keyPairGenerator.init(keyGenParameters)
        
        val keyPair: AsymmetricCipherKeyPair = keyPairGenerator.generateKeyPair()
        
        val publicKey = keyPair.public as KyberPublicKeyParameters
        val privateKey = keyPair.private as KyberPrivateKeyParameters
        
        return KEMKeyPair(
            publicKey = publicKey.encoded,
            privateKey = privateKey.encoded
        )
    }
    
    /**
     * 키 캡슐화 (Encapsulation)
     * 수신자의 공개키로 공유 비밀키를 캡슐화
     */
    fun encapsulate(recipientPublicKey: ByteArray): EncapsulationResult {
        val kyberPublicKey = KyberPublicKeyParameters(
            KyberParameters.kyber768,
            recipientPublicKey
        )
        
        val kemGenerator = KyberKEMGenerator(SecureRandom())
        val encapsulated = kemGenerator.generateEncapsulated(kyberPublicKey)
        
        return EncapsulationResult(
            ciphertext = encapsulated.encapsulation,
            sharedSecret = encapsulated.secret
        )
    }
    
    /**
     * 키 탈캡슐화 (Decapsulation)
     * 자신의 개인키로 공유 비밀키 복원
     */
    fun decapsulate(
        ciphertext: ByteArray,
        privateKey: ByteArray
    ): ByteArray {
        val kyberPrivateKey = KyberPrivateKeyParameters(
            KyberParameters.
```

```kotlin
kyber768,
            privateKey
        )
        
        val kemExtractor = KyberKEMExtractor(kyberPrivateKey)
        return kemExtractor.extractSecret(ciphertext)
    }
}

// 데이터 클래스
data class KEMKeyPair(
    val publicKey: ByteArray,
    val privateKey: ByteArray
) {
    fun publicKeyBase64(): String = Base64.encodeToString(publicKey, Base64.NO_WRAP)
    fun privateKeyBase64(): String = Base64.encodeToString(privateKey, Base64.NO_WRAP)
}

data class EncapsulationResult(
    val ciphertext: ByteArray,    // ~1,088 bytes for ML-KEM-768
    val sharedSecret: ByteArray   // 32 bytes
)
```

#### Step 3: ML-DSA(Dilithium) 디지털 서명 구현

```kotlin
// PQCSignature.kt
package com.example.pqcdemo

import org.bouncycastle.crypto.AsymmetricCipherKeyPair
import org.bouncycastle.pqc.crypto.crystals.dilithium.*
import java.security.SecureRandom

class PQCSignature {
    
    /**
     * ML-DSA-65 키 쌍 생성
     * Dilithium3이 NIST 표준 ML-DSA-65에 해당
     */
    fun generateSigningKeyPair(): SigningKeyPair {
        val keyGenParams = DilithiumKeyGenerationParameters(
            SecureRandom(),
            DilithiumParameters.dilithium3  // ML-DSA-65
        )
        
        val keyGen = DilithiumKeyPairGenerator()
        keyGen.init(keyGenParams)
        
        val keyPair: AsymmetricCipherKeyPair = keyGen.generateKeyPair()
        
        val publicKey = keyPair.public as DilithiumPublicKeyParameters
        val privateKey = keyPair.private as DilithiumPrivateKeyParameters
        
        return SigningKeyPair(
            publicKey = publicKey.encoded,
            privateKey = privateKey.encoded
        )
    }
    
    /**
     * 메시지 서명
     */
    fun sign(message: ByteArray, privateKey: ByteArray): ByteArray {
        val dilithiumPrivateKey = DilithiumPrivateKeyParameters(
            DilithiumParameters.dilithium3,
            privateKey
        )
        
        val signer = DilithiumSigner()
        signer.init(true, dilithiumPrivateKey)
        
        return signer.generateSignature(message)
    }
    
    /**
     * 서명 검증
     */
    fun verify(
        message: ByteArray,
        signature: ByteArray,
        publicKey: ByteArray
    ): Boolean {
        val dilithiumPublicKey = DilithiumPublicKeyParameters(
            DilithiumParameters.dilithium3,
            publicKey
        )
        
        val verifier = DilithiumSigner()
        verifier.init(false, dilithiumPublicKey)
        
        return verifier.verifySignature(message, signature)
    }
}

data class SigningKeyPair(
    val publicKey: ByteArray,    // ~1,952 bytes
    val privateKey: ByteArray    // ~4,016 bytes
)
```

### 4. 하이브리드 암호 접근법: 실무적 해결책

PQC 알고리즘은 비교적 새롭고, 구현 버그나 사이드채널 공격에 대한 검증이 부족하다. 따라서 실무에서는 **기존 알고리즘과 PQC를 결합한 하이브리드 방식**을 권장한다.

```javascript
graph TD
    A[하이브리드 키 교환] --> B[ECDH 키 교환]
    A --> C[ML-KEM 키 교환]
    
    B --> D[ECDH 공유 비밀]
    C --> E[ML-KEM 공유 비밀]
    
    D --> F[KDF 입력]
    E --> F
    
    F --> G[최종 세션 키]
    
    G --> H[AES-256-GCM 암호화]
```

하이브리드 방식에서는 공격자가 두 알고리즘 중 **하나라도** 깨지 않으면 세션 키를 복원할 수 없다.

```kotlin
// HybridKeyExchange.kt
package com.example.pqcdemo

import javax.crypto.KeyAgreement
import java.security.KeyPairGenerator
import java.security.spec.ECGenParameterSpec
import javax.crypto.spec.SecretKeySpec
import java.security.MessageDigest

class HybridKeyExchange {
    
    private val pqcKeyExchange = PQCKeyExchange()
    
    /**
     * 하이브리드 키 교환: X25519 + ML-KEM-768
     * 두 알고리즘의 출력을 결합하여 최종 키 도출
     */
    fun performHybridKeyExchange(
        peerEcdhPublicKey: ByteArray,
        peerMlKemCiphertext: ByteArray
    ): HybridKeyResult {
        
        // 1. ECDH (X25519) 수행
        val ecdhKeyGen = KeyPairGenerator.getInstance("XDH")
        ecdhKeyGen.init(ECGenParameterSpec("X25519"))
        val ecdhKeyPair = ecdhKeyGen.generateKeyPair()
        
        val ecdhKeyAgreement = KeyAgreement.getInstance("XDH")
        ecdhKeyAgreement.init(ecdhKeyPair.private)
        // 실제로는 peer의 공개키로 doPhase 수행
        // ecdhKeyAgreement.doPhase(peerEcdhPublicKey, true)
        val ecdhSecret = ByteArray(32) // ECDH 결과
        
        // 2. ML-KEM 탈캡슐화
        val mlKemSecret = pqcKeyExchange.decapsulate(
            peerMlKemCiphertext,
            ByteArray(1632) // 자신의 ML-KEM 개인키
        )
        
        // 3. 두 비밀을 결합하여 최종 키 도출 (KDF)
        val combinedSecret = ecdhSecret + mlKemSecret
        val sha256 = MessageDigest.getInstance("SHA-256")
        val finalKey = sha256.digest(combinedSecret)
        
        return HybridKeyResult(
            sessionKey = finalKey,
            ecdhPublicKey = ecdhKeyPair.public.encoded,
            mlKemPublicKey = ByteArray(1184) // ML-KEM-768 공개키
        )
    }
    
    /**
     * 하이브리드 서명: ECDSA + ML-DSA
     */
    fun verifyHybridSignature(
        message: ByteArray,
        ecdsaSignature: ByteArray,
        mldsaSignature: ByteArray,
        ecdsaPublicKey: ByteArray,
        mldsaPublicKey: ByteArray
    ):
```

```kotlin
 Boolean {
        // 두 서명 모두 검증되어야 함
        val ecdsaValid = verifyECDSA(message, ecdsaSignature, ecdsaPublicKey)
        val mldsaValid = verifyMLDSA(message, mldsaSignature, mldsaPublicKey)
        
        return ecdsaValid && mldsaValid
    }
    
    private fun verifyECDSA(
        message: ByteArray,
        signature: ByteArray,
        publicKey: ByteArray
    ): Boolean {
        // ECDSA 검증 로직
        return true // 실제 구현 필요
    }
    
    private fun verifyMLDSA(
        message: ByteArray,
        signature: ByteArray,
        publicKey: ByteArray
    ): Boolean {
        // ML-DSA 검증 로직
        return true // 실제 구현 필요
    }
}

data class HybridKeyResult(
    val sessionKey: ByteArray,        // 32 bytes
    val ecdhPublicKey: ByteArray,     // 32 bytes (X25519)
    val mlKemPublicKey: ByteArray     // 1,188 bytes (ML-KEM-768)
)
```

### 5. Android 권장 아키텍처

```javascript
graph TD
    A[Android App] --> B[PQC Module]
    
    B --> C[Key Exchange Layer]
    B --> D[Signature Layer]
    B --> E[Hybrid Orchestration]
    
    C --> F[ML-KEM-768]
    C --> G[X25519]
    
    D --> H[ML-DSA-65]
    D --> I[ECDSA P-256]
    
    E --> J[Combined KDF]
    J --> K[Session Key]
    
    K --> L[AES-256-GCM]
    K --> M[ChaCha20-Poly1305]
    
    F --> N[BouncyCastle PQC]
    H --> N
```

### 6. 성능 고려사항

| 연산 | RSA-2048 | ECDSA P-256 | ML-KEM-768 | ML-DSA-65 |
| :--- | :--- | :--- | :--- | :--- |
| 키 생성 | ~50ms | ~5ms | ~1ms | ~0.5ms |
| 암호화/서명 | ~10ms | ~5ms | ~0.5ms | ~3ms |
| 복호화/검증 | ~1ms | ~10ms | ~0.5ms | ~1ms |
| 공개키 크기 | 256 bytes | 64 bytes | 1,188 bytes | 1,952 bytes |
| 서명 크기 | 256 bytes | 64 bytes | N/A | 3,293 bytes |

PQC는 키와 서명 크기가 크지만, 연산 속도는 오히려 기존 알고리즘보다 빠른 경우가 많다. 네트워크 대역폭이 제한적인 모바일 환경에서는 이를 고려해야 한다.

---

## 결론

### 핵심 요약

1. **"Store Now, Decrypt Later" 공격이 현실적 위협**이다. 오늘 수집된 암호화 데이터는 양자컴퓨터 등장 시 모두 해독된다.

2. **NIST 표준 PQC 알고리즘**(ML-KEM, ML-DSA)이 확정되었고, Android 14부터 지원이 시작되었다.

3. **하이브리드 접근법**(ECDH + ML-KEM, ECDSA + ML-DSA)이 현재 가장 안전한 선택이다. PQC만 단독 사용은 아직 검증이 부족하다.

4. **격자 기반 암호**의 수학적 안전성은 양자컴퓨터로도 깨지지 않음이 증명되었다.

### 전문가 인사이트
> "Post-Quantum 마이그레이션은 Y2K 문제와 다르다. Y2K는 특정 날짜에 발생했지만, PQC는 언제 양자컴퓨터가 실용화될지 모른다. 그러나 'Store Now, Decrypt Later' 공격 때문에 **지금** 시작해야 한다. 5년 전의 통신이 이미 수집되어 있을 수 있다."

실무 권장사항:
- **신규 프로젝트**: 처음부터 하이브리드 PQC 적용
- **기존 프로젝트**: 2025년 내로 PQC 마이그레이션 계획 수립
- **장기 비밀 데이터**: 즉시 PQC 또는 하이브리드 암호로 재암호화

### 참고 자료
- [NIST Post-Quantum Cryptography Standards](https://csrc.nist.gov/projects/post-quantum-cryptography) - FIPS 203, 204, 205
- [Google Android Security Blog - PQC Implementation](https://security.googleblog.com/)
- [BouncyCastle PQC Documentation](https://www.bouncycastle.org/java.html)
- [IETF Hybrid Key Exchange RFC 9180](https://datatracker.ietf.org/doc/html/rfc9180)
- [CRYSTALS-Kyber Specification](https://pq-crystals.org/kyber/)
- [Open Quantum Safe - liboqs](https://openquantumsafe.org/)

---

*⚠️ 이 글의 모든 코드는 교육 및 방어 목적으로 작성되었습니다. 실제 프로덕션 환경에서는 보안 감사와 충분한 테스트를 거친 후 적용하세요.*

---

**출처**: [https://news.google.com/rss/articles/CBMiiAFBVV95cUxPLTBkTVdSZzc3WWk2by1lZTZhQTR0Y3hpNVNRLWxSNF9JV3RTTFB1ZDVHREVlaW4wdUJsWTlBLV9OZXluREc1VGU4U2tlaTU4T2NPRGpDRnFzTlB5eTZqbEdfQjFwSDBHM3Zuc3JzcTBKalpCNExpTnpSLWx5bGUxd21FU1p3TXRV?oc=5](https://news.google.com/rss/articles/CBMiiAFBVV95cUxPLTBkTVdSZzc3WWk2by1lZTZhQTR0Y3hpNVNRLWxSNF9JV3RTTFB1ZDVHREVlaW4wdUJsWTlBLV9OZXluREc1VGU4U2tlaTU4T2NPRGpDRnFzTlB5eTZqbEdfQjFwSDBHM3Zuc3JzcTBKalpCNExpTnpSLWx5bGUxd21FU1p3TXRV?oc=5)