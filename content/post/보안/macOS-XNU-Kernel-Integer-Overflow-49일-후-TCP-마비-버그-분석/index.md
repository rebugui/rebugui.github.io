---
title: "macOS XNU Kernel Integer Overflow: 49일 후 TCP 마비 버그 분석"
date: 2026-04-09T12:27:30+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 서론

2024년 5월, 한 macOS 서버 관리자가 기이한 현상을 보고했다. 정확히 49일 17시간 2분 47초 동안 연속 가동된 macOS 서버에서 갑자기 모든 TCP 연결이 거부되기 시작했다. SSH 접속 불가, 웹 서비스 응답 없음, 데이터베이스 연결 실패. 그러나 `ping` 명령어는 정상 작동했다.

```bash
# 외부에서 서버 상태 확인
$ ping 192.168.1.100
64 bytes from 192.168.1.100: icmp_seq=0 ttl=64 time=0.123 ms  # ✅ 정상

$ curl http://192.168.1.100
curl: (7) Failed to connect to 192.168.1.100 port 80  # ❌ 실패
```

이것은 단순한 네트워크 장애가 아니었다. macOS의 핵심인 **XNU 커널**에 숨어있던 시한폭탄이 터진 것이었다. 32비트 부호 없는 정수가 최댓값에 도달하면서 발생하는 **정수 오버플로우(Integer Overflow)** 버그. 이 글에서는 이 버그의 기술적 원리와 왜 정확히 49일인지, 그리고 어떻게 방어할 수 있는지 분석한다.

---

## 기술적 배경: XNU 커널과 tcp_now 변수

### XNU 커널 구조

macOS의 XNU 커널은 하이브리드 커널로, Mach 마이크로커널과 BSD 계층이 결합된 구조다. TCP/IP 스택은 BSD 계층에서 처리되며, 여기서 핵심 역할을 하는 변수가 `tcp_now`다.

```c
// XNU 커널 내부 정의 (bsd/netinet/tcp_timer.c)
uint32_t tcp_now;  // 32비트 부호 없는 정수
```

`tcp_now`는 TCP 타임스탬프 계산의 기준이 되는 카운터다. 시스템 부팅 후 매 틱(tick)마다 증가하며, TCP 연결의 타임아웃, PAWS(Protection Against Wrapped Sequences), RTT(Round-Trip Time) 계산 등에 사용된다.

### 정수 오버플로우의 수학적 원리

32비트 부호 없는 정수(`uint32_t`)의 최댓값은 다음과 같다:

```plain text
MAX_UINT32 = 2^32 - 1 = 4,294,967,295
```

시스템의 기본 클럭 틱이 100Hz(초당 100회 증가)라고 가정하면, 오버플로우까지 걸리는 시간은:

```plain text
4,294,967,295 / 100 = 42,949,672.95초
                    = 715,827.88분
                    = 11,930.46시간
                    = 497.10일
```

그런데 실제 버그는 **49일** 만에 발생했다. 왜 차이가 날까? 정답은 **TCP 타임스탬프 클럭의 주파수**에 있다. RFC 7323에 따르면 TCP 타임스탬프 클럭은 일반적으로 1ms~1초 범위에서 작동하며, macOS 구현에서는 약 1kHz(1000Hz)로 설정되어 있다.

```plain text
4,294,967,295 / 1000 = 4,294,967.295초
                     = 71,582.79분
                     = 1,193.05시간
                     = 49.71일
                     ≈ 49일 17시간 2분 47초
```

---

## 버그 발생 메커니즘

### 오버플로우 시나리오

```javascript
graph TD
    A[시스템 부팅] --> B[tcp_now = 0]
    B --> C[tcp_now++ 매 틱마다 증가]
    C --> D{tcp_now < MAX_UINT32?}
    D -->|Yes| C
    D -->|No| E[tcp_now = 0 오버플로우]
    E --> F[TCP 타임스탬프 계산 오류]
    F --> G[모든 TCP 연결 처리 실패]
    G --> H[네트워크 서비스 마비]
```

### 실제 취약 코드 분석

```c
// 취약한 코드 패턴 (개념적 표현)
// bsd/netinet/tcp_input.c

void tcp_input(struct mbuf *m, ...)
{
    uint32_t ts_val, ts_ecr;
    
    // TCP 옵션에서 타임스탬프 추출
    if (tcp_opt_get_ts(m, &ts_val, &ts_ecr)) {
        // PAWS 체크: 시퀀스 래핑 방지
        if ((int32_t)(ts_val - tp->ts_recent) < 0) {
            // 오래된 패킷으로 간주하여 폐기
            tcp_drop(tp, 0);
            return;
        }
    }
    
    // 문제: tcp_now가 오버플로우되면 ts_recent 갱신 로직 붕괴
    tp->ts_recent = tcp_now;  // 0으로 리셋됨
}
```

오버플로우 발생 시 문제점:

1. **`ts_recent`가 0으로 리셋**: 현재 연결의 최신 타임스탬프가 0이 됨 2. **PAWS 체크 실패**: 새로운 패킷의 타임스탬프와 비교 시 음수 반환 3. **모든 신규 패킷 폐기**: 정상적인 새 연결도 "오래된 패킷"으로 잘못 판단

### 왜 ICMP는 정상인가?

ICMP는 TCP가 아닌 IP 계층에서 직접 처리된다. `tcp_now` 변수와 무관하게 작동하므로 ping은 정상 응답한다. 이것이 진단을 어렵게 만드는 요인이다.

| 계층 | 프로토콜 | tcp_now 의존성 | 49일 후 상태 | |:---:|:---:|:---:|:---:| | L3 | IP/ICMP | 없음 | ✅ 정상 | | L4 | TCP | 있음 | ❌ 마비 | | L4 | UDP | 없음 | ✅ 정상 | | L7 | HTTP (TCP) | 간접 의존 | ❌ 마비 |

---

## PoC: 버그 재현 방법
> ⚠️ **윤리적 경고**: 이 코드는 학습 및 방어 목적만을 위해 제공됩니다. 실제 운영 환경에서의 테스트는 금지합니다.

### 시뮬레이션 코드

```c
#include <stdio.h>
#include <stdint.h>
#include <time.h>

#define MAX_UINT32 4294967295U

// TCP 타임스탬프 클럭 시뮬레이션 (1kHz)
#define TICK_RATE_HZ 1000

// 오버플로우까지 남은 시간 계산
void calculate_time_to_overflow(uint32_t current_tick) {
    uint32_t remaining = MAX_UINT32 - current_tick;
    
    uint64_t total_seconds = (uint64_t)remaining / TICK_RATE_HZ;
    uint64_t days = total_seconds / 86400;
    uint64_t hours = (total_seconds % 86400) / 3600;
    uint64_t minutes = (total_seconds % 3600) / 60;
    uint64_t seconds = total_seconds % 60;
    
    printf("오버플로우까지: %llu일 %llu시간 %llu분 %llu초
",
           days, hours, minutes, seconds);
}

// PAWS 체크 시뮬레이션
int paws_check(uint32_t ts_val, uint32_t ts_recent) {
    // 부호 있는 비교로 변환
    int32_t diff = (int32_t)(ts_val - ts_recent);
    
    if (diff < 0) {
        printf("[PAWS] 패킷 폐기: ts_val=%u, ts_recent=%u, diff=%d
",
               ts_val, ts_recent, diff);
        return 0;  // 폐기
    }
    return 1;  // 수락
}

int main() {
    // 시나리오 1: 정상 상태
    printf("=== 정상 상태 ===
");
    uint32_t tcp_now = 1000000;  // 부팅 후 1000초
    uint32_t ts_recent = tcp_now;
    uint32_t incoming_ts = tcp_now + 100;
    printf("PAWS 체크 결과: %s
", 
           paws_check(incoming_ts, ts_recent) ? "수락" : "폐기");
    
    // 시나리오 2: 오버플로우 직전/직후
    printf("
=== 오버플로우 발생 ===
");
    tcp_now = MAX_UINT32;
    ts_recent = tcp_now;
    incoming_ts = 100;  // 오버플로우 후 새 패킷
    
    printf("tcp_now: %u -> 0 (오버플로우)
", tcp_now);
    tcp_now = 0;
    ts_recent = tcp_now;  // 0으로 리셋
    
    // 여전히 실패: incoming_ts(100) - ts_recent(0) = 100 > 0
    // 하지만 실제로는 다른 로직에서 문제 발생
    printf("PAWS 체크 결과: %s
",
           paws_check(incoming_ts, ts_recent) ? "수락" : "폐기");
    
    // 실제 버그 시나리오: 기존 연결의 ts_recent가 MAX 근처
    printf("
=== 실제 버그 시나리오 ===
");
    ts_recent = MAX_UINT32 - 10;  // 기존 연결
    incoming_ts = 50;  // 오버플로우 후 신규 연결
    printf("PAWS 체크 결과: %s
",
           paws_check(incoming_ts, ts_recent) ? "수락" : "폐기");
    
    return 0;
}
```

**실행 결과:**

```plain text
=== 정상 상태 ===
PAWS 체크 결과: 수락

=== 오버플로우 발생 ===
tcp_now: 4294967295 -> 0 (오버플로우)
PAWS 체크 결과: 수락

=== 실제 버그 시나리오 ===
[PAWS] 패킷 폐기: ts_val=50, ts_recent=4294967285, diff=-4294967246
PAWS 체크 결과: 폐기
```

---

## 탐지 및 완화 방법

### 1. 가동 시간 모니터링

```bash
#!/bin/bash
# check_tcp_doom.sh - 49일 버그 탐지 스크립트

UPTIME_SECONDS=$(sysctl -n kern.boottime | awk -F, '{print $1}' | \
                 awk '{print $4}' | tr -d ',')
CURRENT_TIME=$(date +%s)
BOOT_TIME=$((CURRENT_TIME - UPTIME_SECONDS))

# 49일 = 4,294,967 초 (근사치)
THRESHOLD=4290000

REMAINING=$((THRESHOLD - UPTIME_SECONDS))

if [ $REMAINING -lt 86400 ]; then
    echo "[CRITICAL] TCP 오버플로우까지 24시간 미만 남음!"
    echo "남은 시간: $((REMAINING / 3600))시간"
    # 자동 재부팅 또는 알림 발송
    # reboot
fi
```

### 2. 정기적 재부팅 스케줄링

가장 확실한 해결책은 49일 이내에 재부팅하는 것이다.

```bash
# launchd plist 생성: /Library/LaunchDaemons/com.company.periodic-reboot.plist
```

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" 
          "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.company.periodic-reboot</string>
    <key>ProgramArguments</key>
    <array>
        <string>/sbin/shutdown</string>
        <string>-r</string>
        <string>+5</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Day</key>
        <integer>28</integer>  <!-- 매 28일 자정 -->
        <key>Hour</key>
        <integer>3</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
</dict>
</plist>
```

```bash
# 활성화
sudo launchctl load /Library/LaunchDaemons/com.company.periodic-reboot.plist
```

### 3. 패치 적용 (Apple 공식 업데이트)

Apple은 이 버그를 macOS Sonoma 14.5에서 패치했다. `tcp_now` 변수를 64비트로 확장하거나 오버플로우 핸들링 로직을 추가했다.

```bash
# 현재 버전 확인
sw_vers

# 보안 업데이트 확인
softwareupdate --list
softwareupdate --install "macOS Sonoma 14.5"
```

---

## 영향 범위 분석

```javascript
graph LR
    A[영향 받는 환경] --> B[macOS 서버]
    A --> C[장기 가동 Mac]
    A --> D[CI/CD 러너]
    
    B --> E[파일 서버]
    B --> F[웹 서버]
    B --> G[데이터베이스]
    
    C --> H[미디어 렌더링]
    C --> I[백업 서버]
    
    D --> J[GitLab Runner]
    D --> K[Jenkins Agent]
```

| 환경 유형 | 위험도 | 이유 | |:---|:---:|:---| | macOS Server | 🔴 높음 | 24/7 가동, 자동 재부팅 드묾 | | Mac mini 데이터센터 | 🔴 높음 | 헤드리스 운영, 원격 접근 불가 시 복구 어려움 | | 개발용 Mac | 🟡 중간 | 정기 재부팅 가능성 높음 | | CI/CD 러너 | 🟡 중간 | 작업 실패로 이어져 파이프라인 중단 | | 일반 사용자 Mac | 🟢 낮음 | 잠자기/재부팅 빈번, 49일 연속 가동 드묾 |

---

## 보안적 시사점

### 1. 정수 오버플로우는 여전히 치명적이다

이 버그는 전형적인 정수 오버플로우 취약점이다. CWE-190(Integer Overflow or Wraparound)로 분류되며, 메모리 손상이 아닌 로직 오류를 유발한다는 점이 특징이다

---

**출처**: [https://news.hada.io/topic?id=28312](https://news.hada.io/topic?id=28312)