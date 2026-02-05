---
title: "[2026 주요정보통신기반시설] HV-13 ESXi Shell 세션 종료 시간 설정"
slug: "2026-주정통/HV-13"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "ESXi Shell(TSM, TSM-SSH)의 Session Timeout(로그인 후 일정 시간 사용하지 않을 경우 세션 종료)설정의적정성여부점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Virtualization
---

# HV-13 ESXi Shell 세션 종료 시간 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | HV-13 |
| **점검내용** | ESXi Shell(TSM, TSM-SSH)의 Session Timeout(로그인 후 일정 시간 사용하지 않을 경우 세션 종료)설정의적정성여부점검 |
| **점검대상** | VMware ESXi 등 |
| **판단기준** | 양호: Session Timeout 값(ESXiShellInteractiveTimeOut)이600이하로설정된경우 |
| **판단기준** | 취약: Session Timeout 값(ESXiShellInteractiveTimeOut)이0이거나,600초과로설정된경우 |
| **조치방법** | Session Timeout 값(ESXiShellInteractiveTimeOut)이900이하설정 |

---
## 상세 설명

### 1. 항목 개요

ESXi Shell 세션 종료 시간(Idle Timeout)은 사용자가 일정 시간 동안 입력이 없을 경우 자동으로 로그아웃하는 보안 기능입니다. 이는 **세션 하이재킹(Session Hijacking)** 공격과 **무단 사용**을 방지하는 중요한 보안 설정입니다.

ESXi Shell의 기본값은 **0(제한 없음)**으로 설정되어 있어, 사용자가 로그아웃하지 않으면 세션이 영구적으로 유지됩니다. 이는 심각한 보안 위협입니다.

### 2. 왜 이 항목이 필요한가요?

**세션 타임아웃의 중요성:**

1. **세션 하이재킹 방지**
   - 관리자가 자리를 비운 사이 공격자가 활성 세션 사용
   - 네트워크 스니핑 후 세션 토큰 탈취
   - 콘솔 물리적 접근 후 활성 세션 사용

2. **무단 사용 방지**
   - 로그인된 콘솔 방치로 인한 무단 접근
   - 의도치 않은 권한 노출
   - 감사 추적 불가능한 행위

3. **보안 규정 준수**
   - 보안 인증 기준(K-ISMS, ISO 27001 등) 준수
   - 일반적인 보안 정책: 10~15분 타임아웃

**위험 시나리오:**

```
관리자 → SSH로 ESXi Shell 접속
→ root 권한 획득
→ 긴급 호출로 자리 비움 (세션 활성화된 상태)
→ 내부자 또는 해커가 활성 세션 발견
→ root 권한으로 시스템 조작
→ 관리자 계정 생성, 백도어 설치
→ 모든 활동이 관리자의 것으로 기록됨
```

**실제 보안 사고:**
- 관리자가 점심 시간에 자리를 비운 사이 협력자가 악의적 스크립트 실행
- 공유 콘솔에서 이전 사용자의 세션을 그대로 사용하여 실수로 중요 VM 삭제

### 3. 점검 대상

- VMware ESXi

### 4. 판단 기준

- **양호**: Session Timeout 값(ESXiShellInteractiveTimeOut)이 600초(10분) 이하로 설정된 경우
- **취약**: Session Timeout 값(ESXiShellInteractiveTimeOut)이 0이거나, 600초(10분) 초과로 설정된 경우

### 5. 점검 방법

#### VMware ESXi

**1) Web 콘솔 확인**

1. Web 콘솔 접속
   ```
   https://<VMware ESXi IP>
   ```

2. **관리** > **설정** > **시스템** > **고급 설정**으로 이동

3. `UserVars.ESXiShellInteractiveTimeOut` 설정값 확인

**양호 기준:**
- `UserVars.ESXiShellInteractiveTimeOut`: 600 또는 600 초과의 0 아닌 값
- 예: 600(10분), 900(15분), 1200(20분)

**취약 기준:**
- `UserVars.ESXiShellInteractiveTimeOut`: 0 (제한 없음)
- 또는 600 초과 (단, 가이드라인에는 600초 초과를 취약으로 명시)

**2) CLI 확인**

1. SSH로 ESXi 접속 (ESXi Shell이 활성화된 경우)

2. 설정값 확인:
   ```bash
   vim-cmd hostsvc/advopt/query UserVars.ESXiShellInteractiveTimeOut
   ```

**3) 테스트**

```bash
# SSH 접속 후 10분 이상 대기
# 세션이 자동 종료되는지 확인
```

### 6. 조치 방법

#### VMware ESXi

**1) Web 콘솔 설정**

1. Web 콘솔 접속
   ```
   https://<VMware ESXi IP>
   ```

2. **관리** > **설정** > **시스템** > **고급 설정**으로 이동

3. `UserVars.ESXiShellInteractiveTimeOut` 선택 후 **옵션 편집** 클릭

4. 값 설정: `600` (10분)

5. **저장** 클릭

**2) CLI 설정**

```bash
# ESXi Shell 세션 타임아웃 설정 (초 단위)
vim-cmd hostsvc/advopt/update UserVars.ESXiShellInteractiveTimeOut long 600

# 설정 확인
vim-cmd hostsvc/advopt/query UserVars.ESXiShellInteractiveTimeOut

# 출력 예: UserVars.ESXiShellInteractiveTimeOut = 600
```

**3) SSH 설정 (추가 권장)**

SSH 클라이언트 측에서도 타임아웃 설정 권장:

```bash
# /etc/ssh/sshd_config 수정
vi /etc/ssh/sshd_config

# 다음 설정 추가/수정
ClientAliveInterval 600  # 10분
ClientAliveCountMax 0    # 0회 연장 불가

# SSH 서비스 재시작
/etc/init.d/SSH restart
```

### 7. 세션 타임아웃 설정 권장값

| 사용 환경 | 권장 타임아웃 | 설명 |
|-----------|--------------|------|
| 일반 운영 | 600초 (10분) | 대부분의 보안 기준 준수 |
| 높은 보안 요구 | 300초 (5분) | 금융, 국방 등 높은 보안 필요 |
| 개발/테스트 | 900초 (15분) | 개발 환경에서 다소 긴 허용 |
| 데이터 센터 | 600~900초 (10~15분) | 일반적인 데이터 센터 환경 |

**주의:** 0(제한 없음)은 절대 권장하지 않음

### 8. 타임아웃 설정 영향

**영향 받는 서비스:**

1. **TSM(ESXi Shell 로컬 콘솔)**
   - 직접 연결된 키보드/모니터 세션

2. **TSM-SSH(SSH 원격 접속)**
   - SSH 클라이언트 세션

3. **vSphere Client 콘솔**
   - 일부 경우 영향 받을 수 있음

**영향 받지 않는 서비스:**

- vSphere Client 웹 콘솔 (자체 타임아웃 있음)
- vCenter 서비스
- 가상 머전 콘솔

### 9. 추가 보안 설정

**1) TMOUT 환경변수 (쉘 레벨)**

```bash
# /etc/profile에 추가
vi /etc/profile

# 다음 라인 추가
readonly TMOUT=600
export TMOUT

# 변경 사항 적용
source /etc/profile
```

**2) ClientAliveInterval (SSH 서버)**

```bash
# /etc/ssh/sshd_config 수정
vi /etc/ssh/sshd_config

# 다음 설정 추가/수정
ClientAliveInterval 600  # 10분 간격으로 클라이언트 확인
ClientAliveCountMax 0    # 응답 없으면 즉시 종료

# SSH 서비스 재시작
/etc/init.d/SSH restart
```

**3) SSH 클라이언트 설정 (관리자 PC)**

```bash
# ~/.ssh/config 또는 /etc/ssh/ssh_config
Host esxi-hosts
    ServerAliveInterval 600
    ServerAliveCountMax 0
```

### 10. 세션 타임아웃 테스트

**1) 수동 테스트**

```bash
# 1. SSH 접속
ssh root@<ESXi_IP>

# 2. 10분 이상 대기

# 3. 명령어 입력 시도
# 예상 결과: "Connection closed" 또는 "timeout"
```

**2) 자동화 테스트**

```bash
#!/bin/bash
# ESXi Shell 타임아웃 테스트

ESXI_HOST="192.168.1.100"
TIMEOUT=600  # 10분

echo "Testing ESXi Shell timeout..."

# SSH 접속
ssh root@$ESXI_HOST "
    echo \"Connected at \$(date)\"
    echo \"Waiting for timeout...\"
    sleep $TIMEOUT
    echo \"This should not appear\"
"

if [ $? -eq 255 ]; then
    echo "PASS: Session timed out as expected"
else
    echo "FAIL: Session did not timeout"
fi
```

### 11. 대체 관리 방법

세션 타임아웃으로 인한 불편을 줄이기 위한 방법:

**1) vSphere Client 사용**

- 대부분의 작업은 vSphere Client로 수행 가능
- 자체 세션 타임아웃이 있음
- 더 나은 UI와 로깅

**2) PowerCLI 사용**

```powershell
# PowerShell 스크립트로 일괄 작업
Connect-VIServer -Server <vCenter_IP>
Get-VMHost | Where-Object {$_.ConnectionState -eq "Connected"}
# 작업 수행
Disconnect-VIServer
```

**3) 터미널 멀티플렉서(tmux/screen)**

```bash
# 세션 유지
tmux new -s session-name

# 분리 후 재접속
tmux attach -t session-name
```

### 12. 모니터링 및 로그

**1) 로그아웃 로그 확인**

```bash
# SSH 접속 종료 로그
grep "session closed" /var/log/auth.log
grep "logout" /var/log/auth.log

# 세션 타임아웃 로그
grep "timeout" /var/log/auth.log
```

**2) 활성 세션 모니터링**

```bash
# 현재 활성 세션 확인
who
w

# SSH 세션 확인
ps aux | grep sshd
```

**3) 비정상 활동 탐지**

```bash
# 장시간 활성 세션 경고
# /etc/profile.d/timeout-notify.sh
if [ $SECONDS -gt 1800 ]; then
    echo "Warning: Session active for more than 30 minutes"
fi
```

### 13. 주의사항

- ESXi Shell은 기본적으로 비활성화해야 함 (HV-12)
- 세션 타임아웃은 10~15분 권장 (보안 vs 편의성 균형)
- 0(제한 없음) 설정은 절대 권장하지 않음
- 변경 후 반드시 테스트 수행
- 긴 작업이 필요한 경우 vSphere Client 또는 PowerCLI 사용
- 관리자에게 세션 타임아웃 정책 교육 필요

## 요약

ESXi Shell 세션 타임아웃은 **10분(600초)**으로 설정하는 것을 권장합니다. 기본값인 **0(제한 없음)**은 세션 하이재킹 공격에 매우 취약하므로 반드시 변경해야 합니다. 가능하면 ESXi Shell 자체를 **비활성화(HV-12)**하고 **vSphere Client**를 통한 관리를 권장합니다. 불가피하게 Shell을 사용해야 하는 경우, **10~15분 타임아웃**과 **IP 제한**을 함께 적용하세요.
