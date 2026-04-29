---
title: "iTerm2 SSH Integration 취약점: Escape Sequence 신뢰 실패로 인한 공격 가능"
date: 2026-04-30T01:07:44+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 서론

"서버에 접속해서 `cat readme.txt`만 했을 뿐인데 내 로컬 머신이 해킹당했습니다."

터미널 에뮬레이터는 개발자와 보안 엔지니어에게 가장 기본이 되는 도구다. 우리는 SSH로 원격 서버에 접속하고, 로그를 확인하고, 설정 파일을 읽는다. 이 과정에서 터미널은 단순히 텍스트를 화면에 출력하는 역할만 한다고 믿는다. 하지만 iTerm2의 SSH Integration 기능은 이 신뢰를 깨뜨린다.

iTerm2는 macOS에서 가장 널리 사용되는 터미널 에뮬레이터 중 하나다. 많은 사용자가 편의성을 위해 SSH Integration 기능을 활성화하여 사용한다. 이 기능은 원격 서버와의 세션 관리를 편하게 해주지만, 동시에 치명적인 공격 표면(Attack Surface)을 노출한다.

핵심 문제는 **신뢰 경계(Trust Boundary)의 실패**다. SSH Integration은 원격 셸과 통신하기 위해 터미널 escape sequence를 사용하는데, 이 구조적 특성 때문에 일반 터미널 출력도 conductor 프로토콜로 해석될 수 있다. 공격자가 제어하는 서버에 접속하거나, 신뢰할 수 없는 파일을 출력하기만 해도 로컬 시스템이 탈취될 수 있다.
> ⚠️ **윤리적 경고**: 이 글에서 다루는 모든 공격 기법은 학습 및 방어 목적으로 작성되었습니다. 실제 시스템에 무단으로 적용하는 것은 범죄행위입니다.

## 공격 원리: Escape Sequence와 Conductor 프로토콜

### 터미널 Escape Sequence란?

터미널은 단순한 텍스트 출력 도구가 아니다. 텍스트 색상 변경, 커서 이동, 창 제목 설정 등 다양한 제어 명령을 escape sequence를 통해 수행한다. 이는 `ESC[` (0x1B 0x5B)로 시작하는 특수 문자열이다.

```bash
# 터미널에서 실행해보면 이해가 쉽다
echo -e "\033[31m빨간 텍스트\033[0m"
echo -e "\033]0;새로운 창 제목\007"
```

문제는 이 escape sequence가 **어떤 터미널 출력에나 포함될 수 있다**는 점이다. `cat`, `head`, `tail` 같은 기본 명령어로 파일을 출력할 때, 파일 내용에 포함된 escape sequence도 그대로 해석된다.

### iTerm2 SSH Integration의 구조적 결함

iTerm2의 SSH Integration은 "conductor"라는 내부 프로토콜을 사용하여 원격 셸과 통신한다. 이 프로토콜은 터미널 escape sequence를 전송 채널로 사용한다.

```javascript
graph LR
    A[원격 서버] --> B[SSH 연결]
    B --> C[iTerm2 터미널]
    C --> D{Escape Sequence 해석}
    D --> E[일반 텍스트 출력]
    D --> F[Conductor 프로토콜 처리]
    F --> G[로컬 시스템 명령 실행]
```

정상적인 흐름에서는 iTerm2가 conductor 프로토콜의 escape sequence를 식별하고 처리한다. 하지만 **신뢰 경계가 명확하지 않다**. 원격 서버에서 전송된 일반 출력에 conductor 프로토콜 명령이 포함되어 있어도 iTerm2는 이를 구분하지 못한다.

### 신뢰 실패(Trust Failure)의 본질

이 취약점의 근본 원인은 **인증되지 않은 데이터를 신뢰**한다는 점이다:

| 측면 | 정상 설계 | 취약한 설계 | | :--- | :--- | :--- | | **신뢰 경계** | 원격 출력과 제어 명령 분리 | 동일 채널 사용 | | **명령 출처** | 로컬 사용자만 명령 발생 | 원격 서버도 명령 가능 | | **검증 메커니즘** | 출처 확인 및 인증 | 검증 없음 | | **영향 범위** | 원격 서버에 한정 | 로컬 시스템까지 확장 |

## 공격 시나리오 분석

### 시나리오 1: 악성 파일을 통한 공격

가장 현실적인 공격 시나리오는 악의적인 escape sequence가 포함된 파일을 출력하게 유도하는 것이다.

```bash
# 공격자가 준비한 악성 파일 (readme.txt)
# 실제로는 escape sequence가 포함되어 있음
malicious_content=$(printf '\033]1337;ShellIntegration=backslash\007')
malicious_content+=$(printf '\033]1337;ExecCommand=rm -rf ~\007')
echo "$malicious_content" > readme.txt

# 피해자가 실행하는 명령
cat readme.txt
```

이 시나리오에서 피해자는 단순히 파일 내용을 확인하려는 것뿐이지만, iTerm2는 파일에 포함된 escape sequence를 conductor 프로토콜 명령으로 해석하여 실행한다.

### 시나리오 2: MITM을 통한 공격

```javascript
graph TD
    A[사용자] --> B[SSH 연결 시도]
    B --> C{중간자 공격}
    C --> D[정상 서버]
    C --> E[공격자 서버]
    E --> F[악성 Escape Sequence 주입]
    F --> G[iTerm2에서 명령 실행]
```

SSH 연결이 중간자 공격(MITM)에 노출된 경우, 공격자는 세션에 악의적인 escape sequence를 주입할 수 있다.

## PoC: 개념 증명 코드
> **면책 조항**: 다음 코드는 취약점 이해를 위한 학습 목적의 PoC입니다.

```python
#!/usr/bin/env python3
"""
PoC: iTerm2 SSH Integration Escape Sequence Injection
학습 및 방어 목적으로만 사용하세요.
"""

import sys

def generate_malicious_file(filename="readme.txt"):
    """
    iTerm2 Conductor 프로토콜을 악용하는
    가짜 escape sequence가 포함된 파일 생성
    """
    
    # 일반 텍스트로 위장한 내용
    normal_text = """
    프로젝트 README
    ===============
    
    이 프로젝트는 테스트 목적으로 작성되었습니다.
    설치 방법:
        1. 저장소를 클론합니다
        2. requirements.txt를 설치합니다
        3. main.py를 실행합니다
    
    주의: 이 파일은 보안 테스트용입니다.
    """
    
    # iTerm2가 해석할 수 있는 escape sequence
    # 실제 공격에서는 더 복잡한 명령이 사용됨
    # 이 예시에서는 무해한 명령만 포함
    escape_injection = (
        "\033]1337;SetUserVar=test_value\007"  # 변수 설정 (무해함)
    )
    
    # 두 번째 escape sequence: 경고 메시지 표시
    alert_sequence = (
        "\033]1337;Alert=Escape_Sequence_Detected\007"
    )
    
    # 파일에 결합하여 저장
    malicious_content = escape_injection + normal_text + alert_sequence
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(malicious_content)
    
    print(f"[*] 파일 생성 완료: {filename}")
    print(f"[*] 파일 크기: {len(malicious_content)} bytes")
    print("[!] 주의: 이 파일을 iTerm2에서 cat하지 마세요")

if __name__ == "__main__":
    generate_malicious_file()
```

이 PoC는 파일에 escape sequence를 숨기는 방법을 보여준다. 실제 공격에서는 파일을 출력하는 것만으로 로컬 시스템 제어가 가능하다.

## 방어를 위한 Step-by-Step 가이드

### Step 1: 현재 설정 확인

```bash
# iTerm2 설정에서 SSH Integration 활성화 여부 확인
defaults read com.googlecode.iterm2 | grep -i "shell\|integration"

# 현재 사용 중인 셸 프로파일 확인
echo $TERM_PROGRAM
echo $ITERM_SESSION_ID
```

### Step 2: 즉각적인 완화 조치

**방법 1: SSH Integration 비활성화**

iTerm2 메뉴에서 다음 경로로 이동: `Preferences` → `Profiles` → `General` → `Command`

SSH Integration 관련 설정을 비활성화한다.

**방법 2: Escape Sequence 필터링 스크립트 적용**

```bash
#!/bin/bash
# safe_cat.sh: 의심스러운 escape sequence를 필터링하는 래퍼 스크립트

safe_cat() {
    local file="$1"
    
    # 파일이 존재하는지 확인
    if [ ! -f "$file" ]; then
        echo "파일을 찾을 수 없습니다: $file"
        return 1
    fi
    
    # ESC 시퀀스 제거 (기본적인 필터링)
    # iTerm2 특정 시퀀스(1337)와 일반 CSI 시퀀스 제거
    sed 's/\x1b\[[0-9;]*[a-zA-Z]//g' "$file" | \
    sed 's/\x1b\]1337[^]*\x07//g' | \
    sed 's/\x1b\]1337[^\x1b]*\x1b\/g'
}

# 사용법
safe_cat "$1"
```

### Step 3: 신뢰할 수 없는 출처 처리 강화

```bash
# ~/.bashrc 또는 ~/.zshrc에 추가할 설정

# 신뢰할 수 없는 파일을 위한 안전한 출력 함수
safe_view() {
    # 16진수 덤프로 내용 확인 (escape sequence 무력화)
    hexdump -C "$1" | less
    
    # 또는 cat -v 사용 (제어 문자를 표시형태로 변환)
    # cat -v "$1"
}

# alias 설정
alias scat='cat -v'  # 제어 문자 표시
alias xxd='hexdump -C'  # 16진수 덤프
```

### Step 4: 모니터링 및 탐지

```python
#!/usr/bin/env python3
"""
escape_sequence_detector.py
파일 내 의심스러운 escape sequence를 탐지하는 스크립트
"""

import re
import sys

SUSPICIOUS_PATTERNS = [
    rb'\x1b\]1337;',  # iTerm2 특정 시퀀스
    rb'\x1b\[',        # CSI 시퀀스
    rb'\x1b\]',        # OSC 시퀀스
    rb'\x07',          # BEL 문자 (시퀀스 종료)
]

def detect_escape_sequences(filename):
    """파일 내 의심스러운 escape sequence를 탐지"""
    
    alerts = []
    
    with open(filename, 'rb') as f:
        content = f.read()
    
    for pattern in SUSPICIOUS_PATTERNS:
        matches = list(re.finditer(pattern, content))
        if matches:
            alerts.append({
                'pattern': pattern,
                'count': len(matches),
                'positions': [m.start() for m in matches[:5]]
            })
    
    return alerts

def main():
    if len(sys.argv) != 2:
        print("사용법: python3 escape_detector.py <파일경로>")
        sys.exit(1)
    
    filename = sys.argv[1]
    alerts = detect_escape_sequences(filename)
    
    if alerts:
        print(f"[!] 경고: {filename}에 의심스러운 시퀀스가 탐지됨")
        for alert in alerts:
            print(f"    패턴: {alert['pattern']}")
            print(f"    횟수: {alert['count']}")
            print(f"    위치: {alert['positions']}")
    else:
        print(f"[+] {filename}은 비교적 안전해 보임")

if __name__ == "__main__":
    main()
```

## 영향 범위와 심각도 평가

### 취약점 영향 매트릭스

| 평가 항목 | 등급 | 설명 | | :--- | :--- | :--- | | **공격 복잡도** | 낮음 | 파일 출력만으로 공격 가능 | | **인증 필요** | 없음 | 인증 우회 가능 | | **사용자 상호작용** | 최소 | 파일 열람만으로 충분 | | **기밀성 영향** | 높음 | 로컬 파일 접근 가능 | | **무결성 영향** | 높음 | 시스템 수정 가능 | | **가용성 영향** | 높음 | 시스템 파괴 가능 |

### 실제 위협 시나리오

1. **오픈소스 프로젝트**: 공격자가 PR을 통해 README나 설정 파일에 악성 시퀀스 삽입 2. **공유 서버**: 다중 사용자 환경에서 다른 사용자의 파일에 악성 시퀀스 심기 3. **공격 서버**: 침투 테스트 중 발견한 서버에 접속 시 역공격 당함

## 결론

### 핵심 요약

iTerm2 SSH Integration 취약점은 터미널 에뮬레이터의 근본적인 설계 문제를 보여준다. **신뢰할 수 없는 원격 출력을 제어 명령으로 해석**하는 구조적 결함은 다양한 공격 시나리오를 가능하게 한다.

핵심 교훈:
- 터미널은 단순한 텍스트 출력 도구가 아니다
- Escape sequence는 강력한 제어 메커니즘이다
- 신뢰 경계(Trust Boundary)는 명확해야 한다
- 편의성과 보안은 항상 트레이드오프 관계다

### 전문가 인사이트

이 취약점은 **소프트웨어 공학에서 반복적으로 나타나는 패턴**의 하나다. "데이터와 제어 명령을 같은 채널로 전송하면 발생하는 문제"는 SQL Injection, XSS, Buffer Overflow 등 수많은 취약점의 근본 원인이다.

터미널 에뮬레이터 보안에 대한 관심이 필요한 시점이다. 웹 브라우저가 샌드박스와 CSP를 통해 공격 표면을 줄여왔듯, 터미널 에뮬레이터도 비슷한 진화를 겪어야 한다.

실무 권장 사항: 1. 신뢰할 수 없는 서버에 접속 시 iTerm2 대신 기본 터

---

**출처**: [https://news.hada.io/topic?id=28664](https://news.hada.io/topic?id=28664)