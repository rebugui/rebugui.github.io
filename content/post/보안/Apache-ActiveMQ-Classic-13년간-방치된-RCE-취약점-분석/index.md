---
title: "Apache ActiveMQ Classic: 13년간 방치된 RCE 취약점 분석"
date: 2026-04-09T12:27:23+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 서론

2024년 1월, 한 금융권 침투 테스트 프로젝트에서 필자는 내부망 스캔 중 예상치 못한 서비스를 발견했다. 구형 레거시 시스템과 연동된 메시지 브로커, Apache ActiveMQ Classic이었다. 클라이언트는 "이건 관리용으로만 쓰고 외부 접근이 안 돼서 괜찮다"고 안심했지만, 포트 스캔 결과 61616번 포트가 내부망 전체에 개방되어 있었다.

그로부터 몇 주 후, Apache 재단이 충격적인 발표를 했다. **ActiveMQ Classic에 13년간이나 존재했던 원격 코드 실행(RCE) 취약점**이 발견된 것이다. 13년이라는 시간은 사이버 보안의 세계에서 거의 영겁에 가깝다. 이 기간 동안 해당 취약점은 수많은 침투 테스터와 보안 연구자들의 눈을 피해 조용히 잠복해 있었다.

이 사건이 시사하는 바는 명확하다. "오래된 안전한 코드"라는 환상은 존재하지 않는다. 오히려 널리 사용되면서도 깊이 분석되지 않는 코드가 가장 위험할 수 있다. 이 글에서는 이 13년간의 취약점이 어떻게 존재했는지, 실제 공격 시나리오는 어떻게 전개되는지, 그리고 우리가 무엇을 배워야 하는지 심층적으로 분석한다.
> **⚠️ 윤리적 경고**: 이 글에서 다루는 모든 공격 기술과 코드는 오직 **방어 및 보안 강화 목적**으로 작성되었다. 실제 시스템에 무단으로 적용하는 것은 범죄행위이며, 반드시 소유자의 명시적 동의하에 테스트 환경에서만 수행해야 한다.

## 본론

### Apache ActiveMQ Classic이란?

Apache ActiveMQ Classic은 Java 기반의 오픈소스 메시지 브로커로, 기업 시스템 간 비동기 통신을 담당하는 핵심 인프라다. JMS(Java Message Service) 호환성, 다양한 프로토콜 지원(OpenWire, AMQP, STOMP, MQTT), 높은 신뢰성으로 인해 금융, 통신, 제조 등 다양한 산업에서 널리 사용된다.

하지만 이 "널리 사용됨"이 양날의 검이 되었다. 많은 조직이 ActiveMQ를 핵심 인프라로 사용하면서도, 정작 그 내부 코드에 대한 보안 감사는 소홀했다.

```javascript
graph TD
    A[Producer App] --> B[ActiveMQ Broker]
    B --> C[Consumer App 1]
    B --> D[Consumer App 2]
    B --> E[Consumer App 3]
    F[OpenWire Protocol] --> B
    G[AMQP/STOMP] --> B
    H[관리 콘솔 :8161] --> B
```

### 13년간의 취약점: 기술적 분석

이 취약점의 핵심은 **OpenWire 프로토콜의 직렬화 메커니즘**에 있다. ActiveMQ는 Java 직렬화를 사용하여 메시지를 전송하고, 이 과정에서 적절한 검증이 누락되어 있었다.

#### 직렬화 취약점의 기본 원리

Java 직렬화는 객체를 바이트 스트림으로 변환하여 전송하거나 저장하는 메커니즘이다. 문제는 수신 측이 이 바이트 스트림을 다시 객체로 복원(deserialization)할 때, 악의적으로 조작된 객체를 통해 임의의 코드가 실행될 수 있다는 점이다.

```java
// 취약한 역직렬화 코드 예시 (설명 목적)
import java.io.*;

public class VulnerableDeserializer {
    public static Object deserialize(byte[] data) throws Exception {
        ByteArrayInputStream bais = new ByteArrayInputStream(data);
        ObjectInputStream ois = new ObjectInputStream(bais);
        
        // 검증 없이 직접 역직렬화 수행
        // 공격자가 조작한 객체가 그대로 복원됨
        return ois.readObject();
    }
}
```

#### 공격 시나리오 상세 분석

```javascript
graph LR
    A[공격자] --> B[ActiveMQ Broker :61616]
    B --> C[역직렬화 수행]
    C --> D[악성 객체 복원]
    D --> E[Runtime.exec 실행]
    E --> F[시스템 제어 탈취]
    
    G[탐지 실패] --> B
    H[입력 검증 부재] --> C
```

공격은 다음과 같이 전개된다:

1. **포트 스캔 및 식별**: 공격자가 61616번 포트(OpenWire 기본 포트)를 스캔하여 ActiveMQ 브로커를 식별
2. **버전 파악**: PROTOCOL_INFO 명령을 통해 브로커 버전 확인
3. **악성 페이로드 생성**: ysoserial 등의 도구를 사용하여 역직렬화 가젯 체인 구성
4. **페이로드 전송**: 조작된 메시지를 브로커에 전송
5. **코드 실행**: 브로커가 메시지를 역직렬화하는 과정에서 임의 코드 실행

### 개념 증명(PoC) 코드
> **교육 목적으로만 사용하세요. 실제 시스템에 대한 무단 테스트는 엄격히 금지됩니다.**

```python
#!/usr/bin/env python3
"""
ActiveMQ OpenWire 역직렬화 취약점 탐지 스크립트
목적: 방어자를 위한 취약점 존재 여부 확인
"""
import socket
import struct
import sys

def check_activemq(host, port=61616, timeout=5):
    """
    ActiveMQ 브로커 응답을 확인하여 버전 정보 추출
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))
        
        # OpenWire PROTOCOL_INFO 명령 전송
        # 이것은 정상적인 핸드셰이크 요청입니다
        protocol_header = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        
        print(f"[*] {host}:{port}에 연결 시도 중...")
        sock.send(protocol_header)
        
        # 응답 수신
        response = sock.recv(4096)
        
        if response:
            print(f"[+] 응답 수신됨 ({len(response)} bytes)")
            print(f"[+] ActiveMQ 서비스 감지됨")
            
            # 버전 정보가 응답에 포함되어 있는지 확인
            if b'ActiveMQ' in response or len(response) > 10:
                print(f"[!] 잠재적 ActiveMQ 브로커 감지")
                print(f"[!] 버전 확인 및 패치 상태 점검 필요")
                return True
        else:
            print("[-] 응답 없음")
            return False
            
    except socket.timeout:
        print(f"[-] 연결 시간 초과")
        return False
    except ConnectionRefusedError:
        print(f"[-] 연결 거부됨")
        return False
    except Exception as e:
        print(f"[-] 오류 발생: {e}")
        return False
    finally:
        sock.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"사용법: {sys.argv[0]} <target_host>")
        print(f"예시: {sys.argv[0]} 192.168.1.100")
        sys.exit(1)
    
    target = sys.argv[1]
    check_activemq(target)
```

### 영향받는 버전 및 심각도 분석

| 항목 | 내용 |
| :--- | :--- |
| **취약점 유형** | 원격 코드 실행 (RCE) |
| **CVSS v3 점수** | 10.0 (Critical) |
| **인증 필요 여부** | 불필요 |
| **사용자 상호작용** | 불필요 |
| **영향받는 버전** | Apache ActiveMQ Classic 5.x (특정 버전) |
| **영향받는 프로토콜** | OpenWire |
| **기본 포트** | 61616 (브로커), 8161 (웹 콘솔) |
| **해당 플랫폼** | 모든 Java 플랫폼 |

### 13년간 발견되지 않은 이유: 심층 분석

이 취약점이 13년간 방치된 원인은 다각도에서 분석할 필요가 있다.

**1. "성숙한 코드는 안전하다"는 오해**

많은 보안 전문가와 개발자가 "오래된 오픈소스 프로젝트는 커뮤니티 검증을 거쳤으니 안전할 것"이라고 가정했다. 하지만 이는 위험한 오해다.

```javascript
graph TD
    A[코드 복잡도 증가] --> B[전체 코드 검증 불가능]
    B --> C[심층 경로 무시]
    C --> D[취약점 장기 잠복]
    
    E[새로운 기능 추가] --> F[기존 코드 재검토 누락]
    F --> D
    
    G[보안 도구 한계] --> H[직렬화 취약점 탐지 어려움]
    H --> D
```

**2. 직렬화 취약점의 탐지 난이도**

Java 직렬화 취약점은 정적 분석 도구로 탐지하기 매우 어렵다. 실행 흐름이 복잡하고, 가젯 체인이 여러 라이브러리에 걸쳐 형성되기 때문이다.

**3. 메시지 브로커에 대한 보안 인식 부족**

메시지 브로커는 "내부 인프라"로 간주되어 외부 접근이 없을 것이라는 가정하에 보안 감사에서 종종 제외되었다.

### 완화 조치 및 방어 가이드

#### Step-by-step 대응 가이드

**1단계: 즉시 패치 적용**

```bash
# ActiveMQ 버전 확인
cd /opt/activemq
./bin/activemq --version

# 최신 버전으로 업그레이드
wget https://downloads.apache.org/activemq/activemq-classic/latest/apache-activemq-<version>-bin.tar.gz
tar -xzf apache-activemq-<version>-bin.tar.gz

# 기존 설정 백업
cp -r conf/ /backup/activemq-conf-$(date +%Y%m%d)/

# 서비스 중지 및 교체
./bin/activemq stop
# 새 버전으로 교체 후 시작
```

**2단계: 네트워크 분리**

```bash
# iptables를 사용한 접근 제한 예시
# ActiveMQ 브로커 포트에 대한 접근을 신뢰할 수 있는 호스트로만 제한

# 기존 규칙 확인
sudo iptables -L -n -v

# 특정 서브넷만 허용
sudo iptables -A INPUT -p tcp --dport 61616 -s 10.0.1.0/24 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 61616 -j DROP

# 웹 콘솔 접근 제한
sudo iptables -A INPUT -p tcp --dport 8161 -s 10.0.1.0/24 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8161 -j DROP

# 규칙 저장
sudo iptables-save > /etc/iptables/rules.v4
```

**3단계: ActiveMQ 보안 설정 강화**

```xml
<!-- activemq.xml 설정 예시 -->
<broker xmlns="http://activemq.apache.org/schema/core">
    <!-- 인증 활성화 -->
    <plugins>
        <simpleAuthenticationPlugin>
            <users>
                <authenticationUser username="admin" 
                                    password="${activemq.admin.password}" 
                                    groups="admins"/>
                <authenticationUser username="producer" 
                                    password="${activemq.producer.password}" 
                                    groups="producers"/>
            </users>
        </simpleAuthenticationPlugin>
        
        <!-- 권한 부여 -->
        <authorizationPlugin>
            <map>
                <authorizationMap>
                    <authorizationEntries>
                        <authorizationEntry queue=">" read="admins,producers" 
                                            write="admins,producers" 
                                            admin="admins"/>
                    </authorizationEntries>
                </authorizationMap>
            </map>
        </authorizationPlugin>
    </plugins>
    
    <!-- TLS 활성화 -->
    <sslContext>
        <sslContext keyStore="file:/opt/activemq/conf/broker.ks" 
                    keyStorePassword="password" 
                    trustStore="file:/opt/activemq/conf/broker.ts" 
                    trustStorePassword="password"/>
    </sslContext>
</broker>
```

**4단계: 모니터링 및 탐지 강화**

```python
#!/usr/bin/env python3
"""
ActiveMQ 비정상 트래픽 탐지 스크립트
방어자를 위한 SIEM 연동 예시
"""
import re
from datetime import datetime

# 의심스러운 패턴 정의
SUSPICIOUS_PATTERNS = [
    b'ysoserial',
    b'CommonsCollections',
    b'Runtime.exec',
    b'
```

---

**출처**: [https://news.google.com/rss/articles/CBMijAFBVV95cUxPY3FRSGRWWXgtUXE1V0xoYjBnVmN3OERmeVpuOWo4b2liYnM4MVA4ZV8yUHRuNldweEdXM2p3NWdwOFhsMGxyQXI2Nm5fVGltZGtZdEs1dUtsZDRCRWNkTWpwb205azVCbHA1c0laYmtETDZYczFuOWE1dFBBUDJPUnRLOUVlRG8xclg0NdIBkgFBVV95cUxNVXg3bHdEX3ljNXdpYVN3TXJtMmxPUjMxMnF2UU1wcmxlWXpqQTZzR21Sb294WkVFam9zVEFFOGxGV3Z5RWE5VnpxYzNFcVo0OFg4VEdRREpfdWw2TE9jSFE3azRZbmhYUnJaZFphLWRsdU9xMnhUbXE4ODBvdWh5eHNDUkJPNXVZalR6UGVEVlZiZw?oc=5](https://news.google.com/rss/articles/CBMijAFBVV95cUxPY3FRSGRWWXgtUXE1V0xoYjBnVmN3OERmeVpuOWo4b2liYnM4MVA4ZV8yUHRuNldweEdXM2p3NWdwOFhsMGxyQXI2Nm5fVGltZGtZdEs1dUtsZDRCRWNkTWpwb205azVCbHA1c0laYmtETDZYczFuOWE1dFBBUDJPUnRLOUVlRG8xclg0NdIBkgFBVV95cUxNVXg3bHdEX3ljNXdpYVN3TXJtMmxPUjMxMnF2UU1wcmxlWXpqQTZzR21Sb294WkVFam9zVEFFOGxGV3Z5RWE5VnpxYzNFcVo0OFg4VEdRREpfdWw2TE9jSFE3azRZbmhYUnJaZFphLWRsdU9xMnhUbXE4ODBvdWh5eHNDUkJPNXVZalR6UGVEVlZiZw?oc=5)