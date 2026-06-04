---
title: "EUDI Wallet MDVM: 독일 전자신원 지갑의 기기 보안 검증 체계 분석"
date: 2026-04-07T01:04:56+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 서론

2024년 3월, 유럽의 한 보안 연구팀이 탈옥된 iPhone에서 정부 발급 디지털 ID를 사용해 신원 인증에 성공했다는 보고서를 발표했습니다. 공격자는 변조된 기기에서 생체 인증 데이터를 우회하고, 디지털 서명 키를 추출해 은행 계좌를 탈취했습니다. 이 사건은 모바일 기기에서 전자신원(Electronic Identity)을 다룰 때 "기기 자체가 믿을 수 있는가"라는 근본적인 질문을 던졌습니다.

독일은 이 문제에 대해 MDVM(Mobile Device Vulnerability Management)이라는 강력한 답을 제시했습니다. EU 디지털 신원 프레임워크(eIDAS 2.0)를 기반으로 하는 EUDI(European Digital Identity) Wallet은 단순히 앱 수준의 보안을 넘어, 기기의 운영체제와 하드웨어 키 저장소(HKS)의 무결성까지 실시간으로 검증합니다. Apple과 Google의 계정 인프라를 활용해 탈옥·루팅된 기기에서의 인증 요청을 원천 차단하는 이 시스템은 전자신원 보안의 새로운 표준이 되고 있습니다.

이 글에서는 MDVM의 작동 원리를 분석하고, 실제 구현 관점에서 기기 보안 검증 체계가 어떻게 설계되어야 하는지 살펴보겠습니다.

## 본론

### MDVM 아키텍처 개요

MDVM은 Mobile Device Vulnerability Management의 약자로, 모바일 기기의 보안 상태를 지속적으로 모니터링하고 평가하는 체계입니다. 핵심은 전자신원 인증 요청이 발생할 때마다 해당 기기가 "신뢰할 수 있는 상태"인지 실시간으로 확인하는 것입니다.

```javascript
graph TD
    A[사용자 인증 요청] --> B[EUDI Wallet App]
    B --> C[MDVM Client 모듈]
    C --> D[OS 무결성 체크]
    C --> E[하드웨어 키 저장소 검증]
    D --> F[Apple/Google Attestation 서버]
    E --> F
    F --> G[MDVM 서버]
    G --> H{위험도 평가}
    H -->|안전| I[인증 승인]
    H -->|위험| J[인증 거부]
```

MDVM의 검증 대상은 크게 두 가지입니다. 첫째, 운영체제의 무결성입니다. 탈옥(iOS)이나 루팅(Android) 여부, 미수정 보안 패치 상태, 실행 중인 프로세스의 신뢰성 등을 확인합니다. 둘째, 하드웨어 키 저장소(HKS)의 상태입니다. Secure Enclave(iOS)나 Titan M2(Android) 같은 보안 칩이 변조되지 않았는지, 키 추출 공격에 노출되지 않았는지 검증합니다.

### 기기 보안 검증 비교

| 검증 항목 | iOS (Secure Enclave) | Android (Titan M2) | 검증 실패 시 조치 |
| :--- | :--- | :--- | :--- |
| 부팅 로더 무결성 | Secure Boot 검증 | Verified Boot 검증 | 인증 차단 |
| OS 변조 탐지 | 탈옥 탐지 | 루팅/매직 마운트 탐지 | 인증 차단 |
| 보안 패치 레벨 | iOS 버전 확인 | Security Patch Level | 경고 또는 차단 |
| HKS 하드웨어 | App Attest | SafetyNet/Play Integrity | 인증 차단 |
| 키 추출 시도 | Secure Enclave 상태 | Keymaster 상태 | 인증 차단 |

### Apple App Attest 기반 검증 구현

iOS에서는 Apple의 App Attest API를 활용해 기기와 앱의 무결성을 검증합니다. 이는 앱이 공식 App Store에서 설치되었고, 기기가 변조되지 않았음을 암호학적으로 증명하는 메커니즘입니다.

```swift
import DeviceCheck

class MDVMAttestation {
    
    let service = DCAppAttestService.shared
    
    // 1. 기기 고유 키 생성
    func generateKey() async throws -> String {
        guard service.isSupported else {
            throw MDVMError.appAttestNotSupported
        }
        
        let keyId = try await service.generateKey()
        return keyId
    }
    
    // 2. 기기 무결성 증명 생성
    func attestKey(keyId: String, challenge: Data) async throws -> Data {
        let hash = SHA256.hash(data: challenge)
        let attestation = try await service.attestKey(keyId, clientDataHash: hash)
        return attestation
    }
    
    // 3. 인증 요청 서명
    func signRequest(keyId: String, request: Data) async throws -> Data {
        let hash = SHA256.hash(data: request)
        let signature = try await service.generateAssertion(keyId, clientDataHash: hash)
        return signature
    }
    
    // 4. MDVM 서버 검증 요청
    func verifyWithMDVM(attestation: Data, signature: Data) async throws -> MDVMResult {
        let payload: [String: Any] = [
            "attestation": attestation.base64EncodedString(),
            "signature": signature.base64EncodedString(),
            "timestamp": ISO8601DateFormatter().string(from: Date())
        ]
        
        let response = try await sendToMDVMServer(payload: payload)
        return response
    }
}

enum MDVMError: Error {
    case appAttestNotSupported
    case attestationFailed
    case deviceCompromised
}

struct MDVMResult: Codable {
    let isTrusted: Bool
    let riskScore: Int
    let reason: String?
}
```

위 코드에서 핵심은 `attestKey` 메서드입니다. Apple 서버는 이 요청을 받아 기기의 Secure Enclave가 생성한 키 쌍에 대한 증명서를 발급합니다. 이 증명서에는 기기 모델, OS 버전, 그리고 "이 기기가 변조되지 않았음"을 증명하는 Apple의 서명이 포함됩니다.

### Android Play Integrity API 구현

Android에서는 Google Play Integrity API를 사용합니다. 이 API는 기기의 무결성, 앱의 정품 여부, 계정의 신뢰도를 종합적으로 평가합니다.

```kotlin
class MDVMIntegrityChecker(private val context: Context) {
    
    private val integrityManager = IntegrityManagerFactory.create(context)
    
    // 1. 무결성 토큰 요청
    suspend fun requestIntegrityToken(nonce: String): Result<String> {
        val request = IntegrityTokenRequest.builder()
            .setNonce(nonce)
            .build()
        
        return try {
            val response = integrityManager.requestIntegrityToken(request).await()
            Result.success(response.token())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    // 2. 무결성 결과 파싱 (서버 측)
    fun parseIntegrityVerdict(verdict: JSONObject): IntegrityResult {
        val deviceRecognitionVerdict = verdict
            .getJSONObject("deviceRecognitionVerdict")
        
        val deviceIntegrity = deviceRecognitionVerdict
            .optString("deviceIntegrity", "UNKNOWN")
        
        val appRecognitionVerdict = deviceRecognitionVerdict
            .optString("appRecognitionVerdict", "UNKNOWN")
        
        val accountActivity = deviceRecognitionVerdict
            .optString("accountActivity", "UNKNOWN")
        
        return IntegrityResult(
            isDeviceTrusted = deviceIntegrity == "MEETS_DEVICE_INTEGRITY",
            isAppTrusted = appRecognitionVerdict == "PLAY_RECOGNIZED",
            isAccountTrusted = accountActivity == "KNOWN_GOOD",
            riskLevel = calculateRiskLevel(deviceIntegrity)
        )
    }
    
    private fun calculateRiskLevel(verdict: String): RiskLevel {
        return when (verdict) {
            "MEETS_DEVICE_INTEGRITY" -> RiskLevel.LOW
            "MEETS_BASIC_INTEGRITY" -> RiskLevel.MEDIUM
            else -> RiskLevel.HIGH
        }
    }
}

data class IntegrityResult(
    val isDeviceTrusted: Boolean,
    val isAppTrusted: Boolean,
    val isAccountTrusted: Boolean,
    val riskLevel: RiskLevel
)

enum class RiskLevel {
    LOW, MEDIUM, HIGH, CRITICAL
}
```

### MDVM 위험도 평가 로직

MDVM 서버는 Apple과 Google으로부터 받은 증명 데이터를 바탕으로 종합적인 위험도를 평가합니다. 단일 요소가 아닌 다층 검증을 통해 거짓 긍정(False Positive)을 최소화합니다.

```python
import hashlib
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional

@dataclass
class DeviceSecurityState:
    os_version: str
    security_patch_level: str
    is_jailbroken: bool
    is_rooted: bool
    hks_intact: bool
    boot_verified: bool
    last_seen: datetime
    
@dataclass
class MDVMRiskAssessment:
    risk_score: int  # 0-100
    is_trusted: bool
    block_reason: Optional[str]
    recommended_action: str

class MDVMRiskEngine:
    
    CRITICAL_PATCH_DELAY_DAYS = 30
    HIGH_RISK_THRESHOLD = 70
    MEDIUM_RISK_THRESHOLD = 40
    
    def assess_device(self, state: DeviceSecurityState) -> MDVMRiskAssessment:
        risk_score = 0
        
        # 1. OS 변조 검사 (결정적 차단)
        if state.is_jailbroken or state.is_rooted:
            return MDVMRiskAssessment(
                risk_score=100,
                is_trusted=False,
                block_reason="DEVICE_TAMPERED",
                recommended_action="BLOCK_IMMEDIATELY"
            )
        
        # 2. 부트 로더 검증
        if not state.boot_verified:
            risk_score += 40
        
        # 3. 하드웨어 키 저장소 무결성
        if not state.hks_intact:
            risk_score += 50
        
        # 4. 보안 패치 지연 검사
        patch_delay = self._calculate_patch_delay(state.security_patch_level)
        if patch_delay > self.CRITICAL_PATCH_DELAY_DAYS:
            risk_score += 30
        elif patch_delay > 14:
            risk_score += 15
        
        # 5. OS 버전 수명 종료 검사
        if self._is_os_eol(state.os_version):
            risk_score += 25
        
        # 최종 판정
        is_trusted = risk_score < self.HIGH_RISK_THRESHOLD
        block_reason = None if is_trusted else self._get_block_reason(risk_score)
        
        return MDVMRiskAssessment(
            risk_score=min(risk_score, 100),
            is_trusted=is_trusted,
            block_reason=block_reason,
            recommended_action=self._get_action(risk_score)
        )
    

```

```python
    def _calculate_patch_delay(self, patch_level: str) -> int:
        patch_date = datetime.strptime(patch_level, "%Y-%m-%d")
        return (datetime.now() - patch_date).days
    
    def _is_os_eol(self, os_version: str) -> bool:
        # EOL 정책 확인 로직
        eol_versions = ["iOS 14", "Android 10"]
        return any(eol in os_version for eol in eol_versions)
    
    def _get_block_reason(self, score: int) -> str:
        if score >= 80:
            return "CRITICAL_SECURITY_RISK"
        elif score >= 60:
            return "HIGH_SECURITY_RISK"
        else:
            return "MODERATE_SECURITY_RISK"
    
    def _get_action(self, score: int) -> str:
        if score < 20:
            return "ALLOW_FULL_ACCESS"
        elif score < 40:
            return "ALLOW_WITH_WARNING"
        elif score < 60:
            return "ALLOW_LIMITED_ACCESS"
        elif score < 80:
            return "REQUIRE_STEP_UP_AUTH"
        else:
            return "BLOCK_ACCESS"
```

### 공격 시나리오와 MDVM 방어

**시나리오 1: 탈옥 기기에서 키 추출 시도**

공격자가 탈옥된 iPhone에서 EUDI Wallet의 키를 추출하려고 시도합니다. checkra1n 같은 탈옥 도구는 Secure Enclave 우회가 어렵지만, 메모리 덤프나 런타임 후킹을 통한 공격이 가능할 수 있습니다.

MDVM 방어:
1. App Attest 요청 시 Apple 서버가 탈옥 상태 감지
2. 증명서 발급 거부 또는 "compromised" 플래그 포함
3. MDVM 서버가 증명서 검증 실패 시 즉시 인증 차단
4. 사용자에게 "기기 보안 문제로 인증 불가" 알림

```javascript
graph LR
    A[공격자] --> B[탈옥된 기기]
    B --> C[EUDI Wallet 실행]
    C --> D[App Attest 요청]
    D --> E[Apple 서버]
    E --> F{탈옥 탐지}
    F -->|감지됨| G[증명서 거부]
    G --> H[MDVM 서버]
    H --> I[인증 차단]
    F -->|미감지| J[추가 검증]
```

**시나리오 2: 구형 OS에서 알려진 취약점 악용**

공격자가 보안 패치가 적용되지 않은 Android 10 기기를 사용해 EUDI Wallet에 접근하려 합니다. 이 OS 버전은 알려진 원격 코드 실행 취약점이 존재합니다.

MDVM 방어:
1. Play Integrity API가 OS 버전과 패치 레벨 보고
2. MDVM 데이터베이스에서 해당 버전의 알려진 취약점 조회
3. CVE 점수 기반 위험도 계산
4. "OS 업데이트 필요" 메시지와 함께 인증 제한

### Step-by-Step: MDVM 구현 가이드

**Step 1: 신뢰할 수 있는 기기 목록 정의**

```json
{
  "trusted_os_versions": {
    "ios": {
      "minimum_version": "16.0",
      "minimum_security_patch": "2024-01-01",
      "eol_versions": ["14.x", "15.x"]
    },
    "android": {
      "minimum_version": "13",
      "minimum_security_patch": "2024-01-05",
      "eol_versions": ["10", "11"]
    }
  },
  "hardware_requirements": {
    "ios": ["Secure Enclave", "Face ID/Touch ID"],
    "android": ["Titan M2", "Biometric Auth"]
  }
}
```

**Step 2: 클라이언트 측 검증 모듈 구현**

```swift
// iOS 클라이언트 검증
class MDVMClient {
    
    func performSecurityCheck() async throws -> SecurityReport {
        // 탈옥 탐지
        let isJailbroken = checkJailbreakStatus()
        
        // OS 버전 확인
        let osVersion = UIDevice.current.systemVersion
        
        // App Attest 수행
        let attestation = try await performAppAttest()
        
        return SecurityReport(
```

---

**출처**: [https://news.hada.io/topic?id=28229](https://news.hada.io/topic?id=28229)