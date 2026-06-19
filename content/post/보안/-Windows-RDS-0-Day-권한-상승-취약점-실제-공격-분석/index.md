---
title: "🔒 Windows RDS 0-Day: 권한 상승 취약점 실제 공격 분석"
date: 2026-04-19T20:33:40+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
draft: true
---

## 서론

새벽 2시, 보안 관제실(SOC)의 모니터를 밝히는 붉은색 경고창. 그것은 단순한 포트 스캔이나 뻔한 SQL 인젝션 시도가 아니었습니다. 내부망의 개발용 서버에서 권한이 제한된 일반 사용자 계정이 순식간에 `SYSTEM` 권한을 획득하여 의심스러운 프로세스를 생성하려 했다는 치명적인 신호였습니다.

이 글은 Windows Remote Desktop Services(RDS)에 존재하는 0-Day 취약점이 실제 공격(In-the-Wild)에서 어떻게 악용되고 있는지에 대한 분석입니다. 최근 공개된 이 취약점은 원격 데스크톱 프로토콜(RDP)의 핵심 서비스인 RDS의 취점을 노려, 인증된 사용자의 권한을 시스템 최고 관리자 수준으로 끌어올리는(Local Privilege Escalation) 기능을 합니다.

"단순히 패치를 기다리면 된다"고 생각할 수 있습니다. 하지만 공격이 이미 시작되었다면, 패치가 배포되기 전까지 당신의 서버는 공격자의 놀이터가 될 수 있습니다. 왜 이 공격이 위험한지, 그리고 기술적으로 어떤 원리로 작동하는지 파헤쳐 보겠습니다. (모든 기술적 설명은 방어 목적이며, 윤리적 해킹을 전제로 합니다.)

## 본론

### 기술적 배경 및 원리

Windows Remote Desktop Services(RDS)는 사용자가 원격으로 Windows 시스템에 접속할 수 있게 해주는 핵심 구성 요소입니다. 이번 0-Day 취약점(CVE 미할당)은 RDS가 특정 사용자의 세션을 설정하거나 드라이버를 로드하는 과정에서 발생하는 메모리 관리 오류, 혹은 접근 토큰(Access Token) 핸들링의 논리적 결함을 야기합니다.

공격자는 이미 서버에 낮은 권한(예: Domain User 또는 IIS User)으로 침투한 상태에서, 악의적인 시스템 호출을 통해 RDS의 특정 기능을 트리거합니다. 이때 RDS 서비스는 `SYSTEM` 권한으로 실행되고 있으므로, 공격자는 이 권한을 탈취(Impersonation)하거나 잘못된 메모리 주소를 기록하여 커널 모드 코드 실행을 유도할 수 있습니다.

### 공격 시나리오 분석

공격자는 외부에서 바로 관리자 권한을 얻는 것이 아니라, '내부 침투 -> 권한 상승 -> 횡적 이동'의 단계를 밟습니다. 아래는 이번 RDS 0-Day를 악용한 일반적인 공격 체인입니다.

```javascript
graph LR
    A[초기 침투<br>Phishing/Exposed Service] --> B[낮은 권한 획득<br>Low Priv User]
    B --> C[RDS 0-Day Exploit Trigger<br>Privilege Escalation]
    C --> D[SYSTEM 권한 탈취<br>Code Execution as SYSTEM]
    D --> E[백도어 설치 및<br>자격 증명 덤프]
    E --> F[내부 네트워크<br>횡적 이동]
```

이 시나리오의 핵심은 **단계 C**입니다. 공격자는 RDS 취약점을 이용해 일반 사용자 권한의 벽을 넘어 `SYSTEM`이라는 거대한 문을 따냅니다.

### PoC 개념 증명 및 코드 분석

**⚠️ 경고**: 아래 코드는 해당 취약점의 기술적 메커니즘을 이해하기 위한 학습용 PoC 개념입니다. 악용은 엄격히 금지됩니다.

공격자는 주로 Windows API의 `ImpersonateLoggedOnUser` 혹은 특정 RDS 관련 IOCTL(Input/Output Control)을 호출하여 권한 상승을 시도합니다. 아래는 공격자가 토큰 조작을 통해 권한을 상승시키려는 시도의 **개념적 예시**입니다.

```c
#include <windows.h>
#include <stdio.h>

// 개념적 PoC: 토큰 핸들링을 통한 권한 상승 시도 모사
// 실제 취약점은 RDS 서비스 내부의 취약한 로직을 트리거합니다.

void ExploitAttempt() {
    HANDLE hToken;
    HANDLE hNewToken;

    // 1. 현재 프로세스의 토큰 얻기 (Low Privilege)
    if (!OpenProcessToken(GetCurrentProcess(), TOKEN_ALL_ACCESS, &hToken)) {
        printf("[-] OpenProcessToken Failed. Error: %d
", GetLastError());
        return;
    }

    // 2. (가상의) RDS 취약점을 통해 SYSTEM 토큰 핸들 획득 시도
    // 실제 공격에서는 이 단계에서 Exploit 코드가 RDS의 취약한 드라이버를 호출하여
    // SYSTEM 권한의 토큰을 반환받거나 Duplicate합니다.
    printf("[*] Attempting to trigger RDS Vulnerability for Token Duplication...
");
    
    // hSystemToken = Trigger_RDS_Exploit(); (가상의 함수)

    // 3. 권한 상승된 토큰으로 프로세스 생성
    // 공격 성공 시, 이 루틴은 SYSTEM 권한으로 cmd.exe를 실행합니다.
    STARTUPINFO si = { sizeof(si) };
    PROCESS_INFORMATION pi;

    // 실제 공격 코드에서는 여기서 획득한 SYSTEM 토큰을 사용합니다.
    if (CreateProcessWithTokenW(hToken, LOGON_WITH_PROFILE, 
            L"C:\Windows\System32\cmd.exe", NULL, 0, NULL, NULL, &si, &pi)) {
        printf("[+] Exploit Success! Spawned SYSTEM Shell.
");
    } else {
        printf("[-] Exploit Failed. Error: %d
", GetLastError());
    }
    
    CloseHandle(hToken);
}

int main() {
    printf("=== RDS 0-Day Privilege Escalation PoC (Concept) ===
");
    ExploitAttempt();
    return 0;
}
```

이 코드는 실제 공격의 메커니즘 중 '토큰 복제(Duplication)' 단계를 추상화한 것입니다. 실제 필드에서는 RDS와 연동된 커널 모드 드라이버의 취약점을 이용하여 `CreateProcess`가 아닌 `NtCreateProcessEx`와 같은 하위 레벨 API를 직접 조작하여 탐지를 우회합니다.

### 취약점 영향 비교

이번 RDS 0-Day가 기존의 다른 공격 방식과 어떻게 다른지 비교해 보겠습니다.

| 비교 항목 | 일반적인 RDP 브루트 포스 | RDP 원격 코드 실행 (BlueKeep 등) | **RDS 0-Day 권한 상승** |
| :--- | :--- | :--- | :--- |
| **공격 조건** | 네트워크 노출 및 약한 비밀번호 | 패치되지 않은 RDP 서비스 (인증 불필요) | **이미 인증된 낮은 권한 계정** |
| **주요 위험** | 계정 탈취 | 서버 장악 및 웜 전파 | **내부망 장악 및 도미노 효과** |
| **탐지 난이도** | 중 (로그인 실패 다수 발생) | 하 (네트워크 기반 탐지 용이) | **상 (정상적인 RDP 트래픽 위장)** |
| **주요 피해** | 데이터 유출 | 서버 다운, 암호화 마이닝 | **자격 증명 덤프, 도메인 장악** |

이번 공격의 가장 큰 문제는 **'정상적인 로그인 이후'**에 발생한다는 점입니다. 방화벽이나 IDS/IPS가 RDP 접속 자체를 막지 않는 이상, 공격 트래픽은 일반적인 업무용 RDP 트래픽과 구별하기 어렵습니다.

### 방어 가이드: 즉시 수행해야 할 조치

0-Day 취약점은 패치가 나오기 전까지는 완벽한 방어가 불가능합니다. 따라서 '레이어드 방어(Layered Defense)'가 필수적입니다.

#### 1. 즉시 조치 (Immediate Action)
- **RDS 서비스 비활성화**: 업무상 절대적으로 필요하지 않은 경우 RDS 서비스를 중지하십시오.

    ```powershell     # PowerShell을 이용한 RDS 서비스 중지     Stop-Service -Name "TermService" -Force     Set-Service -Name "TermService" -StartupType Disabled     ```
- **네트워크 분할 (Segmentation)**: RDS 서버(포트 3389)를 인터넷으로부터 직접 격리하거나, VPN/SSL VPN을 통해서만 접근하도록 점프 서버(Jump Server)를 구성하십시오.
- **NLA(네트워크 수준 인증) 강제**: 기본적으로 비활성화된 경우 NLA를 켜서 인증되지 않은 연결 시도를 차단하십시오.

#### 2. 감지 및 모니터링 (Detection)

시스템 로그를 면밀히 감시하여 이상 징후를 포착해야 합니다.
- **이벤트 ID 4672 & 4674 감시**: 특별한 관리자 그룹에 할당되지 않은 사용자가 `SYSTEM` 권한을 가진 프로세스를 생성하려 할 때 경고를 발생시켜야 합니다.
- **RDS 관련 프로세스의 비정상적 자식 프로세스 생성**: `svchost.exe`나 `rdpclip.exe` 프로세스가 `cmd.exe`, `powershell.exe` 등을 자식 프로세스로 생성하는 시도를 차단합니다.

아래는 파워셸을 활용하여 의심스러운 프로세스 생성 로그를 필터링하는 간단한 스크립트 예시입니다.

```plain text
# 보안 로그에서 권한 상승 시도 필터링
Get-WinEvent -LogName Security | Where-Object {
    $_.Id -eq 4672 -and $_.Message -match "Privilege List" -and $_.Message -match "SeDebugPrivilege"
} | Select-Object TimeCreated, Id, Message | Format-List
```

## 결론

Windows RDS 0-Day 취약점은 원격 접속 환경이 필수적인 현대 기업 환경에 맞춤형으로 제작된 치명적인 위협입니다. 공격자는 방화벽과 인증 시스템을 통과한 낮은 권한의 계정을 '트로이 목마'처럼 사용하여, 서버의 심장부인 `SYSTEM` 권한을 탈취합니다.

이번 사건을 통해 우리가 얻어야 할 핵심 인사이트는 **"인증된 사용자는 곧 신뢰할 수 있는 사용자가 아니다"**라는 것입니다. Zero Trust(제로 트러스트) 보안 모델의 관점에서, 모든 사용자와 세션은 지속적으로 검증되어야 합니다.

현재로서는 Microsoft의 보안 업데이트 공지를 주시하고, 나오는 즉시 패치를 적용하는 것이 가장 확실한 해결책입니다. 그전까지는 불필요한 RDP 접속을 최소화하고, 최소 권한 원칙을 철저히 준수하여 공격의 표면을 줄여야 합니다. 보안은 하루아침에 완성되는 것이 아니라, 끊임없는 경계와 대응의 연속입니다.

### 참고자료
- [Microsoft Security Response Center (MSRC)](https://msrc.microsoft.com/)
- [CISA - Understanding and Responding to 0-Day Vulnerabilities](https://www.cisa.gov/)
- [OWASP - Privilege Escalation](https://owasp.org/www-community/attacks/Privilege_escalation)

---

**출처**: [https://news.google.com/rss/articles/CBMiigFBVV95cUxNVFN4SmRZdzNXRjVRMzJHTnJwLW1CeFdvaE1ocmVId3Voakx4QlhmSEhmUmE3WEltNWd0SkRKckIzWmctN2QwNy1kd2JOM1FRYlRVaHdDcExoejEweFk4TnpYM2tEZ3p1TUhPNkVmZkM1czNtdmE4b2V3TFhHTzZ1UVg4Q0RiNV9jdkHSAY8BQVVfeXFMTVNBR2hEdWZzQkFPaU9rNmVVdkE0WnlZRzRjNzd1MnVDV2xSUG92Q1V1Wk5NX2ZTdkEwMVBVMl9TMlVHNHJBNkRiRlVGXzVZOWdLUEswNmxoN2liVXFVY1ZsVk0teU42Wjh6VGJPM0JmU2NQTzh0bm5FdVhteGh1VVdXcDVJdmJaTVBveE9aNnc?oc=5](https://news.google.com/rss/articles/CBMiigFBVV95cUxNVFN4SmRZdzNXRjVRMzJHTnJwLW1CeFdvaE1ocmVId3Voakx4QlhmSEhmUmE3WEltNWd0SkRKckIzWmctN2QwNy1kd2JOM1FRYlRVaHdDcExoejEweFk4TnpYM2tEZ3p1TUhPNkVmZkM1czNtdmE4b2V3TFhHTzZ1UVg4Q0RiNV9jdkHSAY8BQVVfeXFMTVNBR2hEdWZzQkFPaU9rNmVVdkE0WnlZRzRjNzd1MnVDV2xSUG92Q1V1Wk5NX2ZTdkEwMVBVMl9TMlVHNHJBNkRiRlVGXzVZOWdLUEswNmxoN2liVXFVY1ZsVk0teU42Wjh6VGJPM0JmU2NQTzh0bm5FdVhteGh1VVdXcDVJdmJaTVBveE9aNnc?oc=5)