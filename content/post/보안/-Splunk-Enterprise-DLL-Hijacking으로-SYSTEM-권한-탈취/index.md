---
title: "🔒 Splunk Enterprise: DLL Hijacking으로 SYSTEM 권한 탈취"
date: 2026-04-19T08:06:07+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
draft: true
---

## 서론

SIEM(Security Information and Event Management)의 대부주인 Splunk는 보안팀에게 있어 성지와도 같습니다. 수많은 로그가 집결되는 이곳을 관리하는 서버는 단순한 로그 수집기가 아니라, 전사 보안의 심장부와도 같습니다. 그런데 만약 이 심장부가 공격자의 명령을 따르는 '좀비'가 된다면 어떨까요?

최근 윈도우 환경에서 동작하는 Splunk Enterprise에서 심각한 권한 상승 취약점이 보고되었습니다. 바로 'DLL 하이재킹(DLL Hijacking)' 기법을 통해, 공격자가 일반 사용자 권한에서 시작해 최고 관리자 권한인 SYSTEM 권한을 탈취할 수 있는 시나리오입니다. 방화벽 뒤에 있어 안전하다고 믿었던 로그 서버가, 공격자에게는 전체 네트워크를 장악하는 가장 강력한 발판이 될 수 있는 상황입니다. 우리는 단순히 패치를 적으라는 뉴스를 넘어, 이 공격이 기술적으로 어떻게 가능한지, 그리고 왜 Splunk와 같은 신뢰할 수 있는 소프트웨어에서 이런 일이 발생하는지 그 원리를 냉철하게 분석해야 합니다.

## 본론

### DLL 하이재킹의 기술적 원리와 메커니즘

**[방어 목적의 분석]**: 이 섹션에서는 공격자가 악용하는 기술적 메커니즘을 이해하고, 이를 방어하기 위해 분석합니다.

DLL 하이재킹(Dynamic Link Library Hijacking)은 윈도우 운영체제의 라이브러리 로딩 메커니즘을 악용한 공격 기법입니다. 윈도우 응용 프로그램은 실행될 때 필요한 DLL 파일을 찾기 위해 특정한 순서로 디렉터리를 검색합니다.

문제는 Splunk와 같은 일부 소프트웨어가, 프로그램이 설치된 디렉터리가 아닌 쓰기 권한이 열려 있는 다른 경로(예: 현재 작업 디렉터리, 임시 폴더 등)에서 DLL을 로드하려고 시도하거나, 존재하지 않는 DLL을 참조할 때 발생합니다. 만약 공격자가 해당 경로에 악성 DLL을 미리 심어둔다면, 프로그램은 정상적인 DLL 대신 공격자의 악성 코드를 메모리에 로드하게 됩니다.

특히 Splunk 서비스는 기본적으로 `SYSTEM` 권한으로 실행됩니다. 따라서 하이재킹된 DLL이 로드되는 순간, 그 안에 포함된 악성 코드 역시 `SYSTEM` 권한으로 실행되어 버립니다. 이는 일반 사용자 권한으로 접속한 공격자가 즉시 관리자 권한을 얻는 가장 확실한 경로가 됩니다.

다음은 DLL 하이재킹을 통한 권한 상승 공격 흐름을 간략화한 다이어그램입니다.

```javascript
graph LR
    A[Low-priv User] -->|Places Malicious DLL| B[Weak Directory Path]
    B --> C[Splunk Service]
    C -->|Triggers Event| D[Search Order Check]
    D -->|Loads DLL| E[Malicious DLL Execution]
    E --> F[SYSTEM Shell]
```

### 공격 시나리오 분석

상황을 가정해 봅시다. 공격자는 웹 쉘 업로드 등의 방법을 통해 타겟 서버에 일반 사용자(예: `IUSR`) 권한으로 진입했습니다. 이제 공격자의 목표는 `SYSTEM` 권한을 얻는 것입니다.

1.  **정찰(Reconnaissance)**: 공격자는 Splunk이 설치된 경로와 관련 프로세스(`splunkd.exe`, `splunk-optimize.exe` 등)를 분석합니다. 이때 프로세스 모니터(Process Monitor)와 같은 도구를 사용하면, 어떤 DLL을 찾지 못해 `NAME NOT FOUND` 에러를 뱉는지 확인할 수 있습니다.
2.  **취약점 식별**: Splunk의 특정 기능(예: Python 스크립트 실행 또는 특정 모듈 로드)이 사용자가 쓰기 가능한 경로(예: `$SPLUNK_HOME\var\run\splunk\` 또는 임시 디렉터리)에서 DLL을 찾으려 시도함을 확인합니다.
3.  **익스플로잇(Exploitation)**: 공격자는 해당 경로에 자신의 코드가 담긴 DLL을 `suspicious.dll`이라는 이름으로 업로드합니다.
4.  **권한 상승**: Splunk 서비스가 재시작되거나 특정 스케줄링된 작업이 수행되어 DLL 로딩이 트리거되면, 악성 코드가 `SYSTEM` 권한으로 실행됩니다.

다음은 이러한 공격에 사용될 수 있는 개념 증명(PoC) DLL 코드의 예시입니다.

```c++
// dll_hijack_poc.c
// 윤리적 경고: 이 코드는 보안 연구 및 방어 목적의 학습용으로만 사용해야 합니다.
#include <windows.h>
#include <stdlib.h>

// DLL 진입점
BOOL APIENTRY DllMain(HMODULE hModule, DWORD  ul_reason_for_call, LPVOID lpReserved) {
    switch (ul_reason_for_call) {
    case DLL_PROCESS_ATTACH:
        // 프로세스에 로드될 때 실행될 코드
        // 실제 공격에서는 여기서 Reverse Shell을 연결하거나 백도어를 설치합니다.
        // 여기서는 SYSTEM 권한 증명을 위해 메모장 실행을 시뮬레이션합니다.
        WinExec("C:\Windows\System32\cmd.exe", SW_SHOW);
        break;
    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
    case DLL_PROCESS_DETACH:
        break;
    }
    return TRUE;
}
```

이 코드를 컴파일하여 취약한 경로에 배치하면, Splunk 프로세스가 해당 DLL을 호출할 때 `cmd.exe`가 `SYSTEM` 권한으로 실행됩니다.

### DLL 검색 순서 비교

윈도우는 DLL 로드 시 안전 검색(Safe DLL Search Mode) 여부에 따라 다른 순서로 검색합니다. 아래 표는 각 모드의 검색 순서를 비교한 것입니다.

| 검색 순서 | Safe DLL Search Mode (기본) | Directory Search Mode (취약) |
| :--- | :--- | :--- |
| 1순위 | 애플리케이션이 설치된 디렉터리 | 애플리케이션이 로드된 디렉터리 |
| 2순위 | System32 디렉터리 | **현재 작업 디렉터리 (CWD)** |
| 3순위 | 16비트 System 디렉터리 | System32 디렉터리 |
| 4순위 | Windows 디렉터리 | Windows 디렉터리 |
| 5순위 | 현재 작업 디렉터리 (CWD) | PATH 환경 변수 |
| 6순위 | PATH 환경 변수 | - |

공격자는 보통 "현재 작업 디렉터리(CWD)"나 PATH에 포함된 쓰기 권한이 있는 디렉터리를 노립니다. Splunk와 같은 서버 소프트웨어는 서비스로 실행되더라도, 특정 스크립트나 설정 파일을 처리하면서 CWD를 변경하는 경우가 많아 이 취약점에 노출될 수 있습니다.

### 실무 적용 가이드 및 완화 조치

**[윤리적 경고]**: 아래 내용은 시스템의 보안성을 강화하기 위한 방어적 관점에서 작성되었습니다.

이러한 권한 상승 취약점을 막기 위해서는 운영 레벨에서 다음과 같은 구체적인 조치가 필요합니다.

1.  **소프트웨어 업데이트**: Splunk는 해당 취약점(CVE-2024-36991 등 관련 버전)을 수정한 패치를 릴리스했습니다. 즉시 최신 버전으로 업그레이드해야 합니다.
2.  **파일 시스템 권한 강화**: Splunk 설치 디렉터리 및 하위 폴더(특히 `bin`, `lib` 등)에 대해 일반 사용자의 쓰기 권한을 제거해야 합니다. `SYSTEM` 및 `Administrators` 그룹만 쓰기가 가능하도록 ACL(Access Control List)을 설정합니다.     ```powershell     # 예시: Splunk 설치 폴더의 권한 확인 및 수정 (관리자 권한 PowerShell)     $path = "C:\Program Files\Splunk"     icacls $path     # 불필요한 쓰기 권한 제거     # icacls $path /remove "Users" /T     ```
3.  **DLL Search Order 모드 확인**: 레지스트리를 통해 시스템 전체의 Safe DLL Search Mode가 활성화되어 있는지 확인합니다.     *   경로: `HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Session Manager`     *   키 값: `SafeDllSearchMode` (1로 설정되어 있어야 함)
4.  **모니터링**: 특이한 프로세스 생성(`splunkd.exe`에 의한 `cmd.exe` 또는 `powershell.exe` 실행)을 감지하는 SIEM 룰을 추가합니다. Splunk 자신이 공격의 도구로 악용되는 것을 막기 위해서는 "Who's watching the watchers" 관점의 감시가 필요합니다.

## 결론

Splunk Enterprise의 DLL 하이재킹 취약점은 "신뢰할 수 있는 프로그램"이라는 인식이 주는 안전띠를 해체하는 매우 교활한 공격 벡터입니다. 로그를 수집하고 분석하는 도구가 오히려 공격자에게 `SYSTEM` 권한을 선물하는 역설적인 상황을 막기 위해서는, 단순한 패치를 넘어 시스템의 권한 구조와 로딩 메커니즘에 대한 근본적인 이해가 필수적입니다.

보안 전문가로서 우리는 보안 제품이 설치된 것만으로 안전하다고 착각해서는 안 됩니다. 보안 도구 또한 소프트웨어일 뿐이며, 취약점으로부터 자유롭지 않습니다. 이번 사건은 SIEM 서버와 같은 핵심 인프라에 대한 보안 하드닝이 얼마나 중요한지를 다시금 일깨워주는 사례입니다. 항상 의심하며, 최신 권고 사항을 반영하고, 파일 시스템 권한과 같은 기초적인 보안 기제를 놓치지 않는 것이 최고의 방어전략입니다.

### 참고자료
- [Splunk Security Advisory](https://www.splunk.com/en_us/product-security.html)
- [Microsoft Documentation: Dynamic-Link Library Search Order](https://learn.microsoft.com/en-us/windows/win32/dlls/dynamic-link-library-search-order)
- [MITRE ATT&CK: Hijack Execution Flow](https://attack.mitre.org/techniques/T1574/001/)

---

**출처**: [https://news.google.com/rss/articles/CBMif0FVX3lxTE9LSDRsSEU2NE9ZXzBJR3BObTZqWk1yWXFZTFMyWXA5dHVCNzk3d1ZvTE4yVTc5NTBWLUpOTlFLRl80VmEyN054dzlBSW9lREt5QVpsYTFWakxrTzRacHhKeHk4UktWWGtqUzRucmZTdm9oa2dpbFJZemdGNVJRNjjSAYQBQVVfeXFMTXJYUXcxSTB1UjZ2dnd4TUxTenJqTnEtcDJ6dl95NDVqb1lHbEtxWkRqMmREWXpvdV9oUFVvZncyRXVkYUhkdTcwT29CaGU1VTA1RFBhSUZ5bW5TQ2pFOEhtQTBqVGQtVDhBSkM1MEduN21HYWtqVGpqMFJKVG9leHEtNl82?oc=5](https://news.google.com/rss/articles/CBMif0FVX3lxTE9LSDRsSEU2NE9ZXzBJR3BObTZqWk1yWXFZTFMyWXA5dHVCNzk3d1ZvTE4yVTc5NTBWLUpOTlFLRl80VmEyN054dzlBSW9lREt5QVpsYTFWakxrTzRacHhKeHk4UktWWGtqUzRucmZTdm9oa2dpbFJZemdGNVJRNjjSAYQBQVVfeXFMTXJYUXcxSTB1UjZ2dnd4TUxTenJqTnEtcDJ6dl95NDVqb1lHbEtxWkRqMmREWXpvdV9oUFVvZncyRXVkYUhkdTcwT29CaGU1VTA1RFBhSUZ5bW5TQ2pFOEhtQTBqVGQtVDhBSkM1MEduN21HYWtqVGpqMFJKVG9leHEtNl82?oc=5)