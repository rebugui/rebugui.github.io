---
title: "Email Deception Techniques: 42가지 사용자 기만 패턴 분석과 대응"
date: 2026-04-09T12:27:36+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 서론

지난 주, 한 중견 제조업체의 재무팀 직원이 CEO로 보이는 이메일을 받았다. 제목은 "긴급: M&A 계약금 송금 요청". 발신자 주소는 `ceo@company-secure.com`이었고, 이메일 본문에는 회사 로고가 완벽하게 렌더링되어 있었다. 30분 후, 2억 원이 낯선 계좌로 이체되었다.

나중에 밝혀진 사실: CEO의 실제 이메일은 `ceo@company.com`이었다. 공격자는 `company-secure.com`이라는 유사 도메인을 등록하고, 이메일 클라이언트가 자동으로 로고를 불러오는 특성을 악용해 진짜처럼 보이게 만들었다.

이것은 단순한 "주의 부족"의 문제가 아니다. 이메일 시스템 자체가 가진 구조적 취약점과 사용자 인터페이스의 한계를 악용하는 정교한 공격이다.

2025년 4월 arXiv에 발표된 연구 "Comprehensive List of User Deception Techniques in Emails"는 이러한 기법 42가지를 체계적으로 분류하고 64개의 구체적 구현 예시를 제시한다. 이 글에서는 그중 실제 현장에서 가장 자주 목격되는 기법들을 중심으로, 방어자 관점에서 분석하고 대응 전략을 제시한다.

---

## 이메일 기만 기법의 분류 체계

연구진은 42가지 기법을 크게 네 가지 카테고리로 분류했다:

```javascript
graph TD
    A[이메일 기만 기법 42종] --> B[발신자 정보 조작]
    A --> C[링크 기만]
    A --> D[첨부파일 위장]
    A --> E[렌더링 환경 악용]
    
    B --> B1[표시 이름 스푸핑]
    B --> B2[유사 도메인]
    B --> B3[서브도메인 악용]
    
    C --> C1[URL 단축 서비스]
    C --> C2[유니코드 동형 문자]
    C --> C3[리다이렉트 체인]
    
    D --> D1[더블 확장자]
    D --> D2[MIME 타입 위장]
    D --> D3[암호화 아카이브]
    
    E --> E1[HTML/CSS 렌더링]
    E --> E2[이미지 로딩 추적]
    E --> E3[반응형 위장]
```

### 주요 기법 상세 분석

#### 1. 발신자 정보 조작 (Sender Deception)

가장 기본적이지만 여전히 효과적인 기법이다. 사용자는 이메일 클라이언트에서 "보낸 사람" 필드를 주로 신뢰하는 경향이 있다.

| 기법 | 메커니즘 | 탐지 난이도 | 실제 사용 빈도 |
| :--- | :--- | :--- | :--- |
| Display Name Spoofing | 표시 이름만 진짜처럼 설정 | 낮음 | 매우 높음 |
| Look-alike Domain | `g00gle.com`, `arnazon.com` | 중간 | 높음 |
| Subdomain Abuse | `paypal.attacker.com` | 중간 | 중간 |
| RFC Non-compliant | 특수문자로 필터 우회 | 높음 | 낮음 |

**PoC: 발신자 스푸핑 탐지 스크립트 (방어 목적)**

```python
import re
from email.utils import parseaddr
import dns.resolver

class SenderSpoofDetector:
    """
    이메일 발신자 스푸핑 탐지 도구
    교육 및 방어 목적으로만 사용 가능
    """
    
    def __init__(self):
        self.suspicious_patterns = [
            r'[0o0]{1}[0o0]{1}gle',  # g00gle
            r'arnaz[0o0]n',           # arnazon
            r'payp[a@]l',             # payp@l
            r'micros[o0]ft',          # micros0ft
        ]
        
    def analyze_sender(self, from_header: str, reply_to: str = None) -> dict:
        """
        발신자 헤더 분석
        
        Args:
            from_header: From 헤더 값
            reply_to: Reply-To 헤더 값 (선택)
        
        Returns:
            분석 결과 딕셔너리
        """
        display_name, email_addr = parseaddr(from_header)
        domain = email_addr.split('@')[-1] if '@' in email_addr else ''
        
        results = {
            'display_name': display_name,
            'email_address': email_addr,
            'domain': domain,
            'risks': [],
            'risk_score': 0
        }
        
        # 1. 표시 이름과 도메인 불일치 검사
        known_brands = ['google', 'microsoft', 'amazon', 'paypal', 'apple']
        for brand in known_brands:
            if brand in display_name.lower() and brand not in domain.lower():
                results['risks'].append(f'Display name contains "{brand}" but domain differs')
                results['risk_score'] += 30
        
        # 2. 유사 도메인 패턴 검사
        for pattern in self.suspicious_patterns:
            if re.search(pattern, domain.lower()):
                results['risks'].append(f'Look-alike domain pattern detected')
                results['risk_score'] += 40
        
        # 3. From과 Reply-To 불일치
        if reply_to:
            _, reply_addr = parseaddr(reply_to)
            if reply_addr and reply_addr != email_addr:
                results['risks'].append('From and Reply-To addresses differ')
                results['risk_score'] += 25
        
        # 4.
```

```python
 SPF/DKIM/DMARC 확인 (실제 환경에서)
        spf_status = self._check_spf(domain)
        if spf_status == 'fail':
            results['risks'].append('SPF validation failed')
            results['risk_score'] += 20
            
        return results
    
    def _check_spf(self, domain: str) -> str:
        """SPF 레코드 확인 (간소화 버전)"""
        try:
            answers = dns.resolver.resolve(domain, 'TXT')
            for rdata in answers:
                if 'v=spf1' in str(rdata):
                    return 'pass'
            return 'neutral'
        except:
            return 'none'

# 사용 예시
detector = SenderSpoofDetector()
result = detector.analyze_sender(
    from_header='"Google Security" <security@g00gle-alerts.com>',
    reply_to='admin@attacker-site.com'
)
print(f"Risk Score: {result['risk_score']}")
print(f"Risks: {result['risks']}")
```

#### 2. 링크 기만 기법 (Link Deception)

링크는 피싱 공격의 핵심 진입점이다. 사용자가 클릭하기 전까지 악의적인지 판단하기 어렵게 만드는 다양한 기법이 존재한다.

```javascript
graph LR
    A[사용자 클릭] --> B{URL 분석}
    B -->|정상| C[목적지 도달]
    B -->|기만| D[중간 단계]
    D --> E[리다이렉트]
    E --> F[최종 악성 사이트]
    
    D --> D1[단축 URL]
    D --> D2[유니코드 변환]
    D --> D3[JavaScript 처리]
```

**주요 링크 기만 기법:**

1. **URL Obfuscation via Encoding**    - `https://example.com/%70%61%79%70%61%6C` (16진수 인코딩)    - 일반 사용자는 이를 `paypal`로 디코딩된 것으로 인식하지 못함

2. **Homograph Attack (IDN)**    - 키릴 문자 'а' (U+0430)와 라틴 문자 'a' (U+0061)는 동일하게 보임    - `pаypal.com` (키릴 문자 포함)을 도메인으로 등록

3. **Redirect Chain Abuse**    - `https://trusted-site.com/redirect?url=malicious.com`    - 신뢰된 도메인을 통과하므로 필터 우회 가능

**PoC: URL 기만 탐지 (방어 목적)**

```python
import urllib.parse
import idna
import unicodedata

class LinkDeceptionDetector:
    """
    URL 기만 기법 탐지 도구
    """
    
    def __init__(self):
        self.redirect_params = ['url', 'redirect', 'next', 'target', 'dest', 'goto']
    
    def analyze_url(self, url: str) -> dict:
        results = {
            'url': url,
            'decoded_forms': [],
            'risks': [],
            'risk_score': 0
        }
        
        # 1. 퍼센트 인코딩 디코딩
        try:
            decoded = urllib.parse.unquote(url)
            if decoded != url:
                results['decoded_forms'].append(decoded)
                results['risks'].append('URL contains percent encoding')
                results['risk_score'] += 15
        except:
            pass
        
        # 2. 유니코드 정규화 및 동형 문자 검사
        try:
            parsed = urllib.parse.urlparse(url)
            hostname = parsed.hostname or ''
            
            # IDN을 ASCII로 변환
            try:
                ascii_form = idna.encode(hostname).decode('ascii')
                if ascii_form != hostname:
                    results['risks'].append(f'IDN detected: {hostname} -> {ascii_form}')
                    results['risk_score'] += 35
            except:
                pass
            
            # 혼합 문자 스크립트 검사
            scripts = set()
            for char in hostname:
                script = unicodedata.name(char).split()[0] if unicodedata.name(char, '') else 'Unknown'
                scripts.add(script)
            
            if len(scripts) > 1:
                results['risks'].append(f'Mixed character scripts: {scripts}')
                results['risk_score'] += 30
                
        except Exception as e:
            results['risks'].append(f'URL parsing error: {str(e)}')
        
        # 3. 리다이렉트 파라미터 검사
        query_params = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
        for param in self.
```

```python
redirect_params:
            if param in query_params:
                results['risks'].append(f'Redirect parameter found: {param}')
                results['risk_score'] += 25
        
        return results

# 사용 예시
detector = LinkDeceptionDetector()
test_urls = [
    'https://example.com/redirect?url=http://malicious.com',
    'https://xn--pypl-9sd.com/login',  # IDN 형태
    'https://test.com/%70%61%79%70%61%6C'
]

for url in test_urls:
    result = detector.analyze_url(url)
    print(f"
URL: {url}")
    print(f"Risk Score: {result['risk_score']}")
    for risk in result['risks']:
        print(f"  - {risk}")
```

#### 3. 첨부파일 위장 (Attachment Deception)

첨부파일은 멀웨어 배포의 주요 벡터다. 연구에서는 다음과 같은 기법들이 식별되었다:

| 기법 | 설명 | 예시 |
| :--- | :--- | :--- |
| Double Extension | 실제 확장자 숨기기 | `invoice.pdf.exe` |
| Right-to-Left Override | 문자열 뒤집기 | `gpj.exe` → `exe.jpg`로 표시 |
| MIME Mismatch | 확장자와 실제 타입 불일치 | `.jpg`지만 실행 코드 포함 |
| Encrypted Archive | 검사 우회 | 암호 걸린 ZIP 파일 |
| Macro Embedded | 문서 내 매크로 | `.docm`, `.xlsm` |

```javascript
graph TD
    A[첨부파일 수신] --> B{확장자 검사}
    B -->|위험 확장자| C[차단]
    B -->|안전 확장자| D{MIME 타입 검사}
    D -->|불일치| C
    D -->|일치| E{콘텐츠 분석}
    E -->|악성| C
    E -->|정상| F[사용자 전달]
    
    C --> G[격리 및 알림]
```

#### 4. 렌더링 환경 악용 (Rendering Environment)

이 카테고리는 특히 흥미롭다. 이메일 클라이언트가 HTML을 렌더링하는 방식 자체를 악용한다.

**주요 기법:**

1. **CSS-based Content Hiding**    - 화면에 보이는 내용과 실제 링크가 다르게 표시    - `display:none`으로 악성 링크 숨기기

2. **Image-based Tracking**    - 원격 이미지 로딩으로 수신자 정보 수집    - 1x1 픽셀 투명 이미지 (웹 비콘)

3. **Responsive Spoofing**    - 화면 크기에 따라 다른 콘텐츠 표시    - 모바일에서는 악성, 데스크톱에서는 정상으로 보이게

**HTML 렌더링 기만 예시 (교육용):**

```html
<!--
  WARNING: 이 코드는 교육 및 방어 목적으로만 사용하세요
  실제 사용은 불법일 수 있습니다
-->
<div style="position: relative;">
  <!-- 사용자에게 보이는 버튼 -->
  <a href="https://legitimate-site.com" 
     style="display: block; 
            padding: 10px 20px; 
            background: #007bff; 
            color: white;">
    안전한 로그인
  </a>
  
  <!-- 겹쳐진 투명 링크 (악용 시나리오) -->
  <a href="https://malicious-site.com" 
     style="position: absolute; 
            top: 0; 
            left: 0; 
            width: 100%; 
            height: 100%; 
            opacity: 0;">
  </a>
</div>
```

---

## 방어 대책: 다층 접근법

### 1. 기술적 대책

```javascript
graph LR
    A[이메일 수신] --> B[Gateway 필터링]
    B --> C[SPF/DKIM/DMARC]
    C --> D[콘텐츠 분석]
    D --> E[링크 평판]
    E --> F[샌드박스 실행]
    F --> G[최종 전달]
    
    B --> H[격리]
    C --> H
    D --> H
    E --> H
    F --> H
```

**DMARC 정책 설정 예시:**

```bash
# DNS TXT 레코드 설정
# 도메인: example.com

# 기본 모니터링 모드
```

---

**출처**: [http://arxiv.org/abs/2604.04926v1](http://arxiv.org/abs/2604.04926v1)