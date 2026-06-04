---
title: "[2026 주요정보통신기반시설] S-10 보안장비 로그 설정"
slug: "2026-주정통/S-10"
date: 2026-02-05T09:56:12+09:00
lastmod: 2026-02-05T09:56:12+09:00
description: "보안 장비에 로그 설정이 적용되어 있는지 확인하고 로그 정책이 기관 정책에 맞게 적용되어 있는지 점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Security
---

# S-10 보안장비 로그 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | S-10 |
| **점검내용** | 보안 장비에 로그 설정이 적용되어 있는지 확인하고 로그 정책이 기관 정책에 맞게 적용되어 있는지 점검 |
| **점검대상** | 방화벽, VPN, IDS, IPS, Anti-DDoS, 웹방화벽 등 |
| **양호기준** | 기관 정책에 따른 로그 설정된 경우 |
| **취약기준** | 기관 정책에 따른 로그 설정이 되지 않은 경우 |
| **조치방법** | 기관 정책에 따른 로깅 설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준

**양호**
- 기관 정책에 따른 로그 설정된 경우

**취약**
- 기관 정책에 따른 로그 설정이 되지 않은 경우

#### 경계 케이스 (Edge Case) 처리 방법

1. **장비별 로그 지원 제한**
   - 일부 장비는 세부적인 로그 설정이 제한적
   - 최대한 가능한 범위에서 로그 설정

2. **성능 vs 로그 수준**
   - 로그 레벨이 높을수록 장비 성능에 영향
   - Informational 레벨 권장 (상황에 따라 조정)

#### 권장 설정값

- 로그 레벨: Informational (레벨 6)
- 필수 로그 항목: 접근 이력, 시스템 로그, 트래픽 로그
- 로그 형식: Syslog 표준 (RFC 5424)

### 2. 점검 방법

**Step 1) 보안 장비의 로그 설정 메뉴 확인**

```bash
# 방화벽 예시 (Cisco ASA)
show logging
# Syslog logging: enabled
# Facility: 20
# Timestamp logging: enabled

# Web 방화벽 예시
# Log > Configuration > Log Settings
```

**Step 2) 기관 정책에 따른 로깅 설정 확인**

```bash
# 1. 접근 이력 로그
- 로그인/로그아웃 기록
- 접속 IP, 시간, 사용자 ID
- 관리자 명령어 이력

# 2. 시스템 로그
- CPU, RAM 사용량
- 디스크 사용량
- 장비 상태 변화

# 3. 트래픽 로그
- 허용/차단된 트래픽
- Source/Destination IP
- Port 정보
- 프로토콜 정보
- 탐지된 공격 로그
```

### 3. 조치 방법

**Step 1) 기관 정책에 따른 로깅 설정**

각 벤더별 설정 방법이 상이하므로 장비 매뉴얼을 참조하여 설정합니다.

**방화벽 로그 설정 예시 (Cisco ASA):**

```bash
# 1. Syslog 활성화
logging enable
logging timestamp
logging buffer-size 1048576

# 2. 로그 레벨 설정 (informational: 레벨 6)
logging trap informational
logging buffered informational

# 3. 특정 이벤트 로깅
logging message <syslog_id> level <level>

# 4. 관리자 접속 로그
logging class auth
```

**Web 방화벽 로그 설정 예시:**

```bash
# 1. 접근 로그 설정
# Log > Configuration > Access Log
- Admin Login/Logout: Enable
- Console Access: Enable
- SSH/Web GUI Access: Enable

# 2. 보안 이벤트 로그
# Log > Configuration > Security Log
- Attack Detection: Enable
- Policy Violation: Enable
- Malware Detection: Enable

# 3. 시스템 로그
# Log > Configuration > System Log
- CPU/Memory Usage: Enable
- Configuration Changes: Enable
- System Events: Enable

# 4. 트래픽 로그
# Log > Configuration > Traffic Log
- Allowed Traffic: Enable (필요시)
- Blocked Traffic: Enable
- Session Logs: Enable
```

**IPS 로그 설정 예시:**

```bash
# 1. 탐지 로그 설정
# Security > IDS > Logging
- Alert Severity: All
- Log Source IP: Enable
- Log Destination IP: Enable
- Log Payload: Enable (최소 100 bytes)

# 2. 공격 패턴 로그
- Signature ID: All
- Attack Category: All
- Response Actions: Log All
```

**Step 2) 로그 레벨 설정**

```bash
# 권장 로그 레벨
- Emergency (0): 시스템 사용 불가
- Alert (1): 즉시 조치 필요
- Critical (2): 중요 상태
- Error (3): 오류 상태
- Warning (4): 경고 상태
- Notification (5): 정상적이지만 중요한 이벤트
- Informational (6): 정보성 메시지 (권장)
- Debug (7): 디버깅 정보 (필요시만)
```

**Step 3) 로그 포맷 설정**

```bash
# 표준 로그 포맷 (Syslog)
# <timestamp> <hostname> <process>[<pid>]: <message>

# 예시
# Jan 20 10:15:30 firewall-01 sshd[1234]: Accepted password for admin from 192.168.1.100 port 22 ssh2
```

### 4. 참고 자료

**필수 로그 항목**
1. **접근 이력**
   - 로그인/로그아웃 시간
   - 접속 IP 주소
   - 사용자 ID
   - 인증 성공/실패 여부

2. **관리자 활동**
   - 설정 변경 이력
   - 실행된 명령어
   - 정책 추가/삭제/수정 내역

3. **시스템 상태**
   - CPU 사용량
   - 메모리 사용량
   - 디스크 사용량
   - 네트워크 인터페이스 상태

4. **보안 이벤트**
   - 탐지된 공격
   - 차단된 트래픽
   - 정책 위반
   - 비정상적인 활동

**주의사항**
- 성능 영향: 세부적인 로깅 설정은 보안 장비 성능에 영향을 미칠 수 있으므로 적절한 로그 레벨을 설정하세요.
- 저장 공간: 로그 용량이 급증할 수 있으므로 디스크 공간을 모니터링하세요.
- 민감 정보: 로그에 포함된 민감 정보(비밀번호 등)가 노출되지 않도록 주의하세요.
- 로그 회전: 로그 파일의 크기가 너무 커지지 않도록 로그 회전(log rotation)을 설정하세요.
- 기관 정책 준수: 기관의 정보 보호 정책에 맞는 로그 설정을 유지하세요.

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.