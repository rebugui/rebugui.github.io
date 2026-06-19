---
title: "🚨 CISA KEV 카탈로그: SolarWinds, Microsoft, Apple 취약점 긴급 대응"
date: 2026-02-16T08:53:00+09:00
draft: false
tags:
  - "CISA"
  - "KEV Catalog"
  - "SolarWinds"
  - "Microsoft"
  - "보안"
categories:
  - "보안"
draft: true
---

## 서론

금요일 오후, 보안 운영 센터(SOC)의 모니터가 붉게 점등하는 상황을 상상해 보십시오. 내부망의 한 서버가 의심스러운 아웃바운드 트래픽을 생성하고 있고, 잠시 후 시스템 관리자의 권한으로 랜섬웨어가 실행됩니다. 조사 결과, 공격자는 패치되지 않은 오래된 에디터 프로그램의 버그를 이용해 초기 진입을 시도했고, 이후 권한 상승 취약점을 통해 도메인 관리자 권한을 탈취했습니다.

이것은 단순한 가상 시나리오가 아닙니다. 미국 국토안보부 산하 사이버 보안 및 인프라 보안국(CISA)은 최근 SolarWinds, Microsoft, Apple, 널리 사용되는 텍스트 에디터인 Notepad++ 등의 주요 소프트웨어 취약점을 **KEV(Known Exploited Vulnerabilities, 악용 중인 취약점)** 카탈로그에 추가했습니다. KEV 카탈로그에 등재된다는 것은 해당 취약점이 "이론적으로 위험하다"는 수준을 넘어, "현실世界中에서 적들이 칼을 들고 휘두르고 있다"는 것을 의미합니다.

왜 우리는 여전히 CVSS 점수만 보고 패치 우선순위를 정할까요? 이번 CISA의 업데이트는 보안 팀에게 "위험의 실재"를 다시금 상기시키는 경종입니다. 특히 SolarWinds와 같은 공급망 소프트웨어나 Microsoft, Apple 같은 범용 플랫폼의 취약점은 사이버 공격의 핵심 진입 경로(Running the Gauntlet)로 악용되고 있습니다. 이 글에서는 최근 KEV에 추가된 취약점들의 기술적 메커니즘을 분석하고, 실제 공격 시나리오에 기반한 대응 전략을 다룹니다.

## 본론

### KEV 카탈로그와 공격的生命 주기

CISA KEV 카탈로그는 보안 팀이 패치를 어디부터 시작해야 할지 알려주는 나침반입니다. 일반적인 취약점 데이터베이스와 달리, KEV는 "악용됨(Active Exploitation)"이 확인된 취약점만을 포함합니다. 이는 공격자의 공격 라이프사이클과 밀접하게 연관되어 있습니다.

아래 다이어그램은 취약점이 발견된 후 KEV에 등록되고, 실제 공격에 이르기까지의 흐름을 간단화한 것입니다.

```mermaid
graph LR
    A[취약점 발견 및 제보] --> B[PoC 개발 및 유출]
    B --> C[실제 악용 시작]
    C --> D[보안 커뮤니티 탐지]
    D --> E[CISA 분석 및 검증]
    E --> F[KEV 카탈로그 등재]
    F --> G[랜섬웨어 그룹 악용 가속화]
    G --> H[패치 적용 안 된 시스템 침해]
```

이 흐름에서 가장 위험한 구간은 **F와 G 사이**입니다. CISA가 KEV에 등재한 순간, 공격자들은 해당 취약점이 "핫(Hot)"해졌음을 인지하고 자동화된 도구로 대규모 스캔을 시작합니다. 따라서 KEV 등재는 곧 "패치 데드라인"과 같습니다.

### SolarWinds: 공급망의 약점을 노리다

SolarWinds 관련 취약점(Serv-U 등)은 공급망 공급망(Supply Chain)의 위험성을 대변합니다. SolarWinds는 수많은 기업의 IT 인프라 관리에 사용되는 솔루션입니다. 만약 공격자가 이 서버에 접근할 수 있다면, 내부망 전체를 장악할 수 있는 발판을 마련할 수 있습니다.

**방어 목적의 분석**: 공격자는 SolarWinds Serv-U와 같은 FTP 서버 소프트웨어의 버퍼 오버플로우나 경로 순회(Path Traversal) 취약점을 악용합니다. 예를 들어, 특정한 잘못된 형식의 요청을 보내어 서버의 메모리를 덮어쓰고 악성 코드를 실행시키는 방식입니다.

다음은 SolarWinds Serv-U의 경로 순회 취약점(CVE-2021-35247 유형)을 개념적으로 테스트하기 위한 PoC(Proof of Concept) 코드 예시입니다. **이 코드는 교육 및 방어 목적이며, 허가되지 않은 시스템에서 실행하는 것은 불법입니다.**

```python
import socket
import sys

# 방어 목적의 취약점 스캐너 예시 (PoC)
def check_vulnerability(target_ip, target_port):
    """
    SolarWinds Serv-U Path Traversal 취약점 테스트 (교육용)
    """
    try:
        # 소켓 연결 시도
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect((target_ip, target_port))

        # 악성 패이턴: 경로 순회 시도
        # 공격자는 이러한 패턴을 통해 시스템 파일에 접근을 시도함
        payload = "GET /..%5C..%5C..%5C..%5C..%5C..%5C..%5C..%5C..%5C..%5Cwindows/win.ini HTTP/1.1\r
"
        payload += "Host: {}\r
".format(target_ip)
        payload += "User-Agent: Vulnerability-Scanner\r
\r
"

        s.send(payload.encode())
        response = s.recv(1024)

        # 응답 분석
        if b"extensions" in response or b"[fonts]" in response:
            print(f"[!] 경고: {target_ip}:{target_port}에서 취약점 징후가 발견되었습니다.")
            return True
        else:
            print(f"[+] 안전함: {target_ip}:{target_port}는 취약해 보이지 않습니다.")
            return False

    except Exception as e:
        print(f"[-] 연결 오류: {e}")
        return False
    finally:
        s.close()

if __name__ == "__main__":
    # 테스트 대상 (자신의 랩 환경 IP로 변경하세요)
    target = "192.168.1.10"
    print("취약점 점검을 시작합니다...")
    check_vulnerability(target, 80)
```

이 코드는 서버가 부적절한 경로 검증을 수행하는지 확인하는 기초적인 로직을 보여줍니다. 실제 공격자는 이를 통해 시스템 구성 파일을 탈취하거나, RCE(원격 코드 실행)로 이어지는 페이로드를 주입합니다.

### Microsoft & Apple: 일상 속의 공격 벡터

Microsoft와 Apple 제품은 기업의 엔드포인트(Endpoint)를 지배합니다. 이번 KEV 추가 목록에는 Microsoft의 Windows SmartScreen 보안 기능 우회나 Apple의 WebKit 엔진 관련 취약점들이 포함될 가능성이 높습니다.

이러한 취약점의 공격 시나리오는 주로 **드라이브 바이 다운로드(Drive-by Download)** 형태입니다. 사용자가 악성 웹사이트를 방문하거나, 피싱 메일에 포함된 링크를 클릭하는 것만으로도 WebKit 렌더링 엔진의 버그를 통해 권한을 얻고 셸 코드를 실행시킵니다.

| 특징 | Microsoft SmartScreen 우회 (가상 시나리오) | Apple WebKit 취약점 (가상 시나리오) |
| :--- | :--- | :--- |
| **공격 벡터** | 악성 signed 파일이나 마크 오브 더 웹(MotW) 우회 | 방문한 웹사이트의 JS 엔진 버그 악용 |
| **주요 대상** | Windows 사용자 (다운로드 후 실행 단계) | Safari 사용자 (웹 브라우징 단계) |
| **영향도** | 사용자 인터페이스 경고 없이 맬웨어 설치 | 샌드박스 탈출 및 시스템 권한 획득 |
| **완화 난이도** | 중간 (파일 출처 검증 정책 강화 필요) | 높음 (브라우저 업데이트 즉시 필요) |

### 실무 적용 가이드: 단계별 대응 방안

이론적인 설명만으로는 랜섬웨어를 막을 수 없습니다. 현장에서 즉시 적용 가능한 단계별 가이드를 제시합니다.

1.  **자산 식별 (Identification)**     *   SolarWinds, Notepad++, Microsoft Office/Windows, Apple 기기의 인벤토리를 확보합니다.     *   특히, 인터넷에 노출된 SolarWinds Serv-U 서버가 있는지 확인합니다 (Shodan, Asset Discovery Tool 활용).

2.  **취약점 스캔 (Scanning)**     *   Nessus, OpenVAS, Qualys 등 스캐너를 사용하여 KEV 목록에 있는 CVE ID를 타겟팅하여 스캔을 실행합니다.     *   `nmap` 스크립트를 사용하여 특정 포트(예: SolarWinds FTP)의 배너 정보를 확인합니다.

3.  **패치 및 완화 (Patching & Mitigation)**     *   **SolarWinds**: 최신 버전으로 업데이트하거나, 인터넷 망에서 직접 접근을 차단하고 VPN 내부에서만 접근하도록 설정을 변경합니다.     *   **Microsoft/Apple**: 운영체제 및 브라우저의 최신 보안 업데이트를 강제로 배포합니다.     *   **Notepad++**: 최신 버전으로 업데이트합니다. 편집기 프로그램조차도 공격 경로가 될 수 있음을 기억하세요 (악성 파일 로딩 시 힙 오버플로우 등).

4.  **검증 (Verification)**     *   패치 적용 후 재스캔을 수행하여 취약점이 해결되었는지 확인합니다.     *   로그 분석(Windows Event Log, Syslog)을 통해 패치 시점 이전의 의심스러운 활동이 있었는지 소급하여 조사합니다.

## 결론

CISA가 SolarWinds, Microsoft, Apple의 주요 취약점을 KEV 카탈로그에 추가한 것은 단순한 정보 공유가 아닌 "긴급 행동 지령"입니다. 현대의 사이버 공격은 더 이상 무작위 대상을 노리는 난사(Spray and Pray) 방식이 아니라, 알려진 취약점을 구체적으로 타겟팅하는 저격수와 같습니다.

특히 SolarWinds와 같은 솔루션은 공급망 공격의 핵심 타겟이 되므로, 방화벽 뒤에 있다고 안심해서는 안 됩니다. Notepad++와 같은 사소해 보이는 툴조차도 공격자에게는 권한 상탱을 위한 발판이 될 수 있습니다.

**전문가 인사이트**: 보안의 핵심은 "완벽한 방어"가 아니라 "빠른 복구"와 "적시적인 패치"입니다. KEV 카탈로그는 여러분의 패치 우선순위를 결정하는 가장 신뢰할 수 있는 데이터 소스입니다. 오늘 KEV 목록을 확인하고, 내 시스템이 현재 진행 중인 공격의 표적이 되고 있지는 않은지 점검하십시오.

**참고자료**:

- [CISA Known Exploited Vulnerabilities Catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog)

- [CISA adds SolarWinds, Microsoft, Apple, Notepad++ vulnerabilities to KEV catalog - SC Media](https://www.scmagazine.com/news/cisa-adds-solarwinds-microsoft-apple-notepad-vulnerabilities-to-kev-catalog)
