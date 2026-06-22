---
title: "GentleKiller Ransomware: 취약 드라이버를 이용한 EDR 프로세스 무력화 공격 분석"
date: 2026-06-22T11:17:05+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 서론: EDR의 그림자 속에서 벌어지는 '조용한' 침투

최근 사이버 보안 현장에서 가장 흔하게 접하는 시나리오는 "EDR이 있는데 왜 랜섬웨어에 감염되지?"라는 의문입니다. 기업들은 수십억 원을 들여 최첨단 엔드포인트 탐지 및 대응(EDR) 솔루션을 구축합니다. 이 EDR은 파일 시스템의 변화, 네트워크 트래픽, 프로세스 실행 등 수많은 지표를 실시간으로 모니터링하며 공격을 사전에 차단하거나 즉시 격리하는 '보안 감시자' 역할을 수행하죠.

하지만 GentleKiller 랜섬웨어는 바로 이 완벽해 보이는 방어막의 치명적인 허점을 공략합니다. 단순한 파일 암호화나 메모리 인젝션 수준을 넘어, 시스템의 가장 깊은 곳에 뿌리내린 **취약한 장치 드라이버(Vulnerable Device Driver)**를 악용하여 EDR이 감시하는 핵심 보안 프로세스 400여 개 이상을 마치 '시스템 관리자'가 명령하듯 무력화시키는 것입니다. 이는 전통적인 방어 전략으로는 탐지 자체가 불가능해지는, 고도화된 공격 시나리오의 전형입니다.

## 본론: 드라이버 권한이 곧 왕권이다 (The Power of Driver Privilege)

GentleKiller의 핵심 공격 메커니즘은 '최고 권한 획득(Privilege Escalation)'과 '탐지 우회'라는 두 축으로 이루어집니다. 일반적인 사용자 모드(User Mode) 프로세스는 제한된 권한 내에서만 작동하지만, 드라이버는 커널 모드(Kernel Mode)에서 실행되며 시스템 전체에 대한 절대적인 접근 권한을 가집니다.

### 1. 공격 원리 및 메커니즘 분석

GentleKiller는 다음과 같은 단계를 거쳐 EDR 프로세스를 무력화합니다:

**① 취약 드라이버 식별:** 대상 시스템의 장치 드라이버 목록 중, 알려진 취약점(예: 버퍼 오버플로우, 잘못된 입력 처리)을 가진 드라이버를 찾아냅니다. **② 공격 페이로드 전달:** 랜섬웨어는 이 취약한 드라이버에게 악성 명령 또는 데이터를 전달합니다 (일반적으로 I/O Control Codes, IOCTL 사용). **③ 커널 모드 침투 및 실행:** 드라이버가 이 페이로드를 처리하는 과정에서 취약점이 트리거되고, 공격자는 원하는 코드를 커널 메모리 공간에 주입하여 실행시킵니다. **④ EDR 프로세스 무력화:** 이제 랜섬웨어는 일반적인 사용자 권한을 넘어선 '드라이버 권한'으로 작동합니다. 이 권한을 이용해 EDR이 모니터링하는 핵심 보안 서비스(예: 메모리 스캔 에이전트, 파일 시스템 필터 드라이버 등)의 프로세스 핸들을 획득하고, 해당 프로세스를 강제로 중지시키거나(Terminate), API 호출을 가로채는(Hooking) 방식으로 탐지를 우회합니다.

### 2. 공격 흐름 시각화 (Attack Flow Diagram)

다음 Mermaid 다이어그램은 GentleKiller가 시스템에 침투하여 EDR을 무력화하는 과정을 간결하게 보여줍니다.

```javascript
graph TD
    A[랜섬웨어 실행] --> B(취약 드라이버 식별 및 타겟팅);
    B --> C{IOCTL/페이로드 전달};
    C --> D[드라이버 취약점 트리거];
    D --> E[커널 모드 침투 및 코드 주입];
    E --> F(EDR 핵심 프로세스 핸들 획득);
    F --> G[프로세스 강제 종료/API Hooking];
    G --> H[탐지 우회 성공 & 랜섬웨어 실행];
```

### 3. 공격 방식 비교: 전통적 vs. GentleKiller (드라이버 활용)

공격의 깊이와 탐지 난이도를 기준으로 두 가지 방식을 비교하면, 드라이버 악용의 파괴력이 명확히 드러납니다.

| 비교 항목 | 기존 파일 암호화 공격 (User Mode) | GentleKiller 공격 (Driver/Kernel Mode) |
| :--- | :--- | :--- |
| **작동 공간** | 사용자 모드 (User Space) | 커널 모드 (Kernel Space) |
| **핵심 목표** | 데이터 파일 암호화 및 Lock | EDR 프로세스, 시스템 서비스 무력화 |
| **권한 수준** | 일반/관리자 권한 (제한적) | 시스템 최고 권한 (절대적) |
| **탐지 난이도** | 중간 (파일 I/O 변화 감지 용이) | 높음 (시스템 내부 동작을 직접 조작하므로 탐지가 어려움) |

### 4. 실무 적용: 드라이버 악용 공격 방어 가이드

현장에서 이 공격을 효과적으로 막기 위해서는 단순한 소프트웨어 업데이트를 넘어, 시스템의 깊숙한 곳에서부터 방어 체계를 구축해야 합니다.

**Step 1. 취약 드라이버 스캐닝 및 패치:**
- 정기적으로 사용 중인 모든 장치 드라이버 목록(특히 네트워크 어댑터, 가상화 소프트웨어, 주변 기기)을 추출하고 알려진 CVE와 대조하여 취약점을 식별합니다.
- 제조사에서 제공하는 최신 버전으로 즉시 업데이트를 수행합니다.

**Step 2. 커널 무결성 모니터링 강화:**
- EDR 솔루션이 단순히 프로세스 목록만 보는 것이 아니라, **커널 메모리 공간의 변조(Kernel Memory Tampering)** 여부를 실시간으로 감시하도록 설정해야 합니다. 드라이버가 코드를 주입하는 순간을 포착할 수 있습니다.

**Step 3. 방어 목적 PoC 코드 예시 (Python):**
- 다음은 Python에서 특정 프로세스 핸들을 얻어 강제로 종료(Kill)시키는 개념 증명 코드입니다. GentleKiller는 이와 유사한 방식으로 EDR의 핵심 프로세스를 타겟팅합니다.

```python
import psutil
import os

def kill_process_by_name(process_name):
    """지정된 이름의 프로세스를 찾아 강제 종료하는 함수 (개념 설명용)"""
    print(f"--- [방어 목적] '{process_name}' 프로세스 탐색 시작 ---")
    
    found = False
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            try:
                # 드라이버 권한을 얻어 핸들을 획득했다고 가정하고 프로세스 종료 시도
                proc.kill() 
                print(f"[SUCCESS] PID {proc.info['pid']} ({process_name})를 성공적으로 종료했습니다.")
                found = True
            except psutil.NoSuchProcess:
                print(f"[WARN] PID {proc.info['pid']}가 이미 사라졌습니다.")
            except Exception as e:
                # 권한 부족 등으로 인해 종료에 실패했을 때 (일반 사용자 모드에서 발생 가능)
                print(f"[ERROR] 프로세스 종료 중 오류 발생: {e}")
    
    if not found:
        print(f"[INFO] '{process_name}' 프로세스를 찾지 못했습니다.")

# 예시: EDR 솔루션의 핵심 프로세스 이름 (실제 환경에 따라 다름)
TARGET_EDR_PROCESS = "CrowdStrike.exe" 
kill_process_by_name(TARGET_EDR_PROCESS)
```

## 결론: 방어는 표면이 아닌 '깊이'에서 시작되어야 한다

GentleKiller 랜섬웨어 공격은 우리에게 사이버 보안의 패러다임 전환을 요구합니다. 더 이상 "최신 EDR을 설치했다"는 사실만으로는 충분하지 않습니다. 공격자가 시스템의 가장 낮은 계층인 **드라이버**를 장악하는 순간, 모든 상위 레벨의 방어 체계(EDR)는 무력화될 수 있습니다.

핵심은 '탐지'에서 '예방 및 제어'로 초점을 옮기는 것입니다. 드라이버가 시스템에 로드되는 시점부터 그 행위를 면밀히 감시하고, 해당 드라이버의 코드가 커널 메모리 영역을 변조하려는 순간 즉각적으로 경고하거나 강제 격리하는 능동적인 방어 메커니즘이 필수적입니다.

**전문가 인사이트:** 장치 드라이버에 대한 보안 검증(Driver Signing, Fuzzing 테스트)은 이제 선택이 아닌 의무입니다. 특히 외부 공급업체로부터 받은 드라이버의 경우, 해당 드라이버가 시스템 깊숙한 곳에서 어떤 API를 호출하고 있는지 분석하는 것이 공격 방어의 첫걸음입니다.

--- **🔗 참고 자료:** GentleKiller Ransomware Abuses Vulnerable Drivers to Disable 400+ EDR Security Processes (CyberSecurityNews) [https://news.google.com/rss/articles/CBMid0FVX3lxTFBMdVZGUnctTHUzSldJOHUxLXZ1Y3FHVDVCU0luVnNZQ1h5R0dKQzEtTWI5RnNkZUFVczF6RXVFSEh0bVdMN09pOF9FOFNSRlBCeEtHal9nOUFveHpzbG4wSXlPdzNxUDhZN1pjelU4eHVvYzR1Vkxj0gF8QVVfeXFMTzNiOFhtRFU3anlGQWtOSEFLRzBVME04MkY4dUV1OWFEaGdpRHBEWkJHZ3FJRzl4RkhXSzNvaS0ybUlJUVlGUHJJc2h6R1dvUm9oSkVhaVhMZkFFaE1SWFVPNkxXTlJFX25hUFlxenpoUFdpa3pBTU5MN3k5Nw?oc=5](https://news.google.com/rss/articles/CBMid0FVX3lxTFBMdVZGUnctTHUzSldJOHUxLXZ1Y3FHVDVCU0luVnNZQ1h5R0dKQzEtTWI5RnNkZUFVczF6RXVFSEh0bVdMN09pOF9FOFNSRlBCeEtHal9nOUFveHpzbG4wSXlPdzNxUDhZN1pjelU4eHVvYzR1Vkxj0gF8QVVfeXFMTzNiOFhtRFU3anlGQWtOSEFLRzBVME04MkY4dUV1OWFEaGdpRHBEWkJHZ3FJRzl4RkhXSzNvaS0ybUlJUVlGUHJJc2h6R1dvUm9oSkVhaVhMZkFFaE1SWFVPNkxXTlJFX25hUFlxenpoUFdpa3pBTU5MN3k5Nw?oc=5)

---

**출처**: [https://news.google.com/rss/articles/CBMid0FVX3lxTFBMdVZGUnctTHUzSldJOHUxLXZ1Y3FHVDVCU0luVnNZQ1h5R0dKQzEtTWI5RnNkZUFVczF6RXVFSEh0bVdMN09pOF9FOFNSRlBCeEtHal9nOUFveHpzbG4wSXlPdzNxUDhZN1pjelU4eHVvYzR1Vkxj0gF8QVVfeXFMTzNiOFhtRFU3anlGQWtOSEFLRzBVME04MkY4dUV1OWFEaGdpRHBEWkJHZ3FJRzl4RkhXSzNvaS0ybUlJUVlGUHJJc2h6R1dvUm9oSkVhaVhMZkFFaE1SWFVPNkxXTlJFX25hUFlxenpoUFdpa3pBTU5MN3k5Nw?oc=5](https://news.google.com/rss/articles/CBMid0FVX3lxTFBMdVZGUnctTHUzSldJOHUxLXZ1Y3FHVDVCU0luVnNZQ1h5R0dKQzEtTWI5RnNkZUFVczF6RXVFSEh0bVdMN09pOF9FOFNSRlBCeEtHal9nOUFveHpzbG4wSXlPdzNxUDhZN1pjelU4eHVvYzR1Vkxj0gF8QVVfeXFMTzNiOFhtRFU3anlGQWtOSEFLRzBVME04MkY4dUV1OWFEaGdpRHBEWkJHZ3FJRzl4RkhXSzNvaS0ybUlJUVlGUHJJc2h6R1dvUm9oSkVhaVhMZkFFaE1SWFVPNkxXTlJFX25hUFlxenpoUFdpa3pBTU5MN3k5Nw?oc=5)