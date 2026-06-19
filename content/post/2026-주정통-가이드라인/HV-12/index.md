---
title: "[2026 주요정보통신기반시설] HV-12 ESXi Shell 비활성화"
slug: "2026-주정통/HV-12"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "ESXi Shell(TSM, TSM-SSH)비활성화여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Virtualization
draft: true
---

# HV-12 ESXi Shell 비활성화

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | HV-12 |
| **점검내용** | ESXi Shell(TSM, TSM-SSH)비활성화여부점검 |
| **점검대상** | VMware ESXi 등 |
| **판단기준** | 양호: ESXi Shell(TSM, TSM-SSH)서비스가비활성화된경우 |
| **판단기준** | 취약: ESXi Shell(TSM, TSM-SSH)서비스가활성화된경우 |
| **조치방법** | ESXi Shell(TSM, TSM-SSH)서비스가비활성화설정 |

---
## 상세 설명

### 1. 항목 개요

ESXi Shell(이전 ESX의 Console OS)은 VMware ESXi 호스트에 직접 접속하여 명령어로 시스템을 관리할 수 있는 텍스트 기반 인터페이스입니다. TSM(Tech Support Mode)이라고도 불리며, 크게 두 가지 형태가 있습니다.

1. **TSM(로컬 콘솔)**: ESXi 호스트에 직접 키보드/모니터를 연결하여 사용
2. **TSM-SSH**: SSH 프로토콜을 통해 원격에서 접속

ESXi Shell은 매우 강력한 관리 기능을 제공하지만, 동시에 **보안상 심각한 위험**을 가지고 있습니다.

### 2. 왜 이 항목이 필요한가요?

**ESXi Shell의 보안 위험:**

1. **감사 기록 누락**
   - ESXi Shell에서 실행한 명령은 vCenter와 동기화되지 않음
   - 중앙 감사 시스템에서 기록 부재
   - 누가 언제 무엇을 했는지 추적 불가

2. **권한 남용 가능성**
   - root 계정으로 직접 접속 가능
   - 모든 시스템 명령 실행 가능
   - 가상 머전 제어, 네트워크 설정 변경, 스토리지 조작

3. **비인가 접속 경로**
   - SSH 포트(22) 스캔으로 탐지 가능
   - vCenter 우회하여 직접 호스트 접속
   - 방화벽 우회 가능성

4. **악성코드 실행**
   - 쉘 스크립트를 통한 악성코드 실행
   - 백도어 설치
   - 크립토마이너 설치

**위험 시나리오:**

```
내부자 또는 해커 → SSH 포트 스캔
→ ESXi Shell(TSM-SSH) 서비스 발견
→ 무차별 대입 공격 또는 취약점 공격
→ Shell 접속 성공
→ root 권한 획득
→ vCenter 거치지 않고 직접 시스템 조작
→ 감사 로그 없는 악의적 행위
→ 모든 가상 머전 삭제/암호화
```

**실제 공격 사례:**
- 내부자가 SSH로 직접 접속하여 비밀 코인 마이닝
- 관리자 계정 탈취 후 가상 머전 전체 삭제
- 네트워크 설정 변경으로 서비스 거부

### 3. 점검 대상

- VMware ESXi

### 4. 판단 기준

- **양호**: ESXi Shell(TSM, TSM-SSH) 서비스가 비활성화된 경우
- **취약**: ESXi Shell(TSM, TSM-SSH) 서비스가 활성화된 경우

### 5. 점검 방법

#### VMware ESXi

**1) Web 콘솔 확인**

1. Web 콘솔 접속
   ```
   https://<VMware ESXi IP>
   ```

2. **호스트** > **관리** > **서비스**로 이동

3. 다음 서비스 활성화 여부 확인:
   - **TSM** (Tech Support Mode)
   - **TSM-SSH** (Tech Support Mode-SSH)

**양호 기준:**
- TSM: **중지** 또는 **실행 중이 아님**
- TSM-SSH: **중지** 또는 **실행 중이 아님**

**취약 기준:**
- TSM: **실행 중**
- TSM-SSH: **실행 중**

**2) CLI 확인**

1. SSH로 ESXi 접속 (활성화된 경우)

2. 서비스 상태 확인:
   ```bash
   esxcli system shell get
   ```

3. TSM-SSH 상태 확인:
   ```bash
   esxcli network firewall ruleset list | grep TSM
   ```

**3) SSH 접속 시도**

```bash
# 터미널에서 SSH 접속 시도
ssh root@<ESXi_IP>

# 접속 가능: TSM-SSH 활성화 (취약)
# 접속 거부: TSM-SSH 비활성화 (양호)
```

### 6. 조치 방법

#### VMware ESXi

**1) Web 콘솔에서 비활성화**

**TSM 비활성화:**

1. Web 콘솔 접속
   ```
   https://<VMware ESXi IP>
   ```

2. **호스트** > **관리** > **서비스**로 이동

3. **TSM** 서비스 선택 > **중지** 클릭

4. 정책 변경: **정책** > **시작 및 중지** > **호스트 부팅 시 서비스 시작** 해제

**TSM-SSH 비활성화:**

1. **TSM-SSH** 서비스 선택 > **중지** 클릭

2. 정책 변경: **정책** > **시작 및 중지** > **호스트 부팅 시 서비스 시작** 해제

3. 방화벽 규칙 비활성화:
   - **네트워킹** > **방화벽 규칙** > **TSM-SSH** > **사�용 안 함**

**2) CLI에서 비활성화**

**TSM 비활성화:**

```bash
# TSM 비활성화
esxcli system shell set --enabled false

# 설정 확인
esxcli system shell get

# 출력: ESXi Shell is disabled: true
```

**TSM-SSH 비활성화:**

```bash
# TSM-SSH 비활성화
esxcli network firewall ruleset set --ruleset-id sshClient --enabled false

# 또는
vim-cmd hostsvc/enable_ssh -E false

# 설정 확인
esxcli network firewall ruleset list | grep sshClient

# 또는
vim-cmd hostsvc/enable_ssh -E | grep enabled
```

**3) vi /etc/ssh/sshd_config (직접 설정)**

```bash
# SSH 설정 파일 수정
vi /etc/ssh/sshd_config

# 다음 라인 주석 처리
# PermitRootLogin yes

# SSH 서비스 중지
/etc/init.d/SSH stop

# 방화벽에서 SSH 비활성화
esxcli network firewall ruleset set --ruleset-id sshClient --enabled false
```

### 7. ESXi Shell이 필요한 경우

일부 Troubleshooting 또는 특정 스크립트 실행을 위해 ESXi Shell이 필요할 수 있습니다. 이 경우 다음과 같이 안전하게 사용하세요.

**1) 일시적 활성화**

```bash
# 필요할 때만 일시적 활성화
esxcli system shell set --enabled true

# 사용 후 즉시 비활성화
esxcli system shell set --enabled false
```

**2) 네트워크 접근 제한**

```bash
# SSH 접속 IP 제한
esxcli network firewall ruleset set --ruleset-id sshClient --allowed-all false
esxcli network firewall ruleset allowedip add --ruleset-id sshClient --ip-address=<관리자_IP>

# 여러 IP 허용
esxcli network firewall ruleset allowedip add --ruleset-id sshClient --ip-address=<관리자_IP2>
```

**3) vSphere API 사용**

ESXi Shell 대신 vSphere API 또는 PowerCLI 사용 권장:

```powershell
# PowerCLI 예시
Connect-VIServer -Server <vCenter_IP>
$VMHost = Get-VMHost -Name <ESXi_Host>
# 다양한 관리 작업 가능
```

**4) ESXi Shell 접속 로그 남기기**

```bash
# .ssh/authorized_keys에 키 등록
# 각 접속 시도 로그 기록
vi /etc/ssh/sshd_config

# 로그 설정
LogLevel VERBOSE
SyslogFacility AUTHPRIV
```

### 8. 대체 관리 방법

| 작업 | ESXi Shell | 대체 방법 |
|------|-----------|----------|
| 시스템 모니터링 | `esxtop` | vSphere Client, ESXTOP via vCenter |
| 네트워크 설정 | `esxcfg-route` | vSphere Client 네트워크 설정 |
| 스토리지 관리 | `esxcli storage` | vSphere Client 스토리지 관리 |
| 가상 머전 관리 | `vim-cmd vmsvc` | vSphere Client, PowerCLI |
| 로그 확인 | `cat /var/log/` | vSphere Client 로그 뷰어, Syslog |
| 패치 적용 | `esxcli software` | vCenter Update Manager |

### 9. ESXi Shell 사용 시 모니터링

Shell을 활성화해야 하는 경우, 반드시 모니터링을 수행하세요.

**1) 접속 로그 확인**

```bash
# SSH 접속 로그
grep "Accepted" /var/log/auth.log
grep "Failed" /var/log/auth.log

# root 접속 시도
grep "root" /var/log/auth.log
```

**2) 명령어 기록 확인**

```bash
# Shell 히스토리
cat /root/.ash_history

# 또는
history
```

**3) 비정상 활동 탐지**

```bash
# 네트워크 연결 확인
esxcli network connection list

# 실행 중인 프로세스 확인
esxcli process list

# CPU/메모리 사용률 확인
esxcli system stats get
```

### 10. 추가 보안 조치

**1) SSH 키 기반 인증**

비밀번호 대신 SSH 키 사용:

```bash
# SSH 공개키 등록
mkdir -p /etc/ssh/keys-root
vi /etc/ssh/keys-root/authorized_keys

# 비밀번호 인증 비활성화
vi /etc/ssh/sshd_config
PasswordAuthentication no
```

**2) 계정 잠금 정책 (HV-07 참조)**

```bash
# 실패 5회 계정 잠금
esxcli system account set -i root -l 5
```

**3) 세션 시간 제한 (HV-01 참조)**

```bash
# SSH 세션 10분 제한
echo "ClientAliveInterval 600" >> /etc/ssh/sshd_config
echo "ClientAliveCountMax 0" >> /etc/ssh/sshd_config
```

**4) 방화벽 규칙**

```bash
# SSH 접속 IP 제한
esxcli network firewall ruleset set --ruleset-id sshClient --allowed-all false
```

### 11. 주의사항

- ESXi Shell 비활성화는 시스템 운영에 영향 없음
- vSphere Client를 통한 모든 관리 가능
- 일부 스크립트가 Shell을 사용하는 경우 PowerCLI로 마이그레이션 필요
- Troubleshooting을 위해 일시적으로만 활성화 권장
- 활성화 시 반드시 IP 제한과 강력한 인증 적용

## 요약

ESXi Shell(TSM, TSM-SSH)은 **vCenter와 동기화되지 않는 감사 누락 경로**이므로 반드시 비활성화해야 합니다. 대부분의 관리 작업은 **vSphere Client**와 **PowerCLI**를 통해 수행할 수 있습니다. 특별한 경우가 아니면 ESXi Shell은 **항상 비활성화** 상태로 유지하고, 필요할 때만 **일시적으로 활성화**하여 사용하세요.
