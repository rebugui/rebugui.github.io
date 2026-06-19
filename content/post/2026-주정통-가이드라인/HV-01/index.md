---
title: "[2026 주요정보통신기반시설] HV-01 가상화장비 > 1. 계정관리"
slug: "2026-주정통/HV-01"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "웹콘솔및사용자Shell Session Timeout설정여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Virtualization
draft: true
---

# 가상화장비 > 1. 계정관리

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | HV-01 |
| **점검내용** | 웹콘솔및사용자Shell Session Timeout설정여부점검 |
| **점검대상** | VMware ESXi, vCenter, XenServer, KVM, Nutanix 등 |
| **판단기준** | 양호: 웹콘솔및사용자Shell Session Timeout 설정이600초(10분)이하로설정된경우 |
| **판단기준** | 취약: 웹콘솔및사용자Shell Session Timeout 설정이600초(10분)를초과하여설정된경우 |
| **조치방법** | 600초(10분)동안입력이없을경우접속된클라이언트세션을끊도록설정 |

---
## 상세 설명

### 개요

**계정 로그오프/세션관리**는 가상화 장비에 접속한 사용자의 세션 타임아웃을 설정하여, 일정 시간 동안 활동이 없는 경우 자동으로 로그아웃되도록 하는 보안 조치입니다. 이는 공격자가 관리자의 세션을 하이재킹하거나, 장시간 유지되는 세션을 악용하는 것을 방지합니다.

### 필요성

가상화 환경에서 세션 관리는 특히 중요합니다. 관리자가 웹 콘솔이나 SSH에 접속한 후 자리를 비우는 경우가 빈번하기 때문입니다. 이때 세션 타임아웃이 설정되어 있지 않다면 다음과 같은 위험에 노출됩니다:

1. **세션 하이재킹**: 공격자가 관리자의 자리를 이용하여 시스템에 접근
2. **무단 접속**: 유휴 세션을 통해 비인가자가 시스템 제어 가능
3. **사고 발생 시 추적 어려움**: 세션을 통한 악의적 행위가 발생해도 누구의 세션인지 파악 불가

### 점검 방법

#### VMware ESXi, vCenter

**웹 콘솔 Session Timeout 설정 확인**

1. Web 콘솔 페이지 접속 (`https://<VMware ESXi IP>`)
2. 호스트 > 관리 > 시스템 > 고급 설정으로 이동
3. `UserVars.HostClientSessionTimeout` 설정이 600초(10분)로 설정되어 있는지 확인

```bash
# 확인할 설정 값
UserVars.HostClientSessionTimeout = 600
```

#### XenServer, KVM

**사용자 Shell Session Timeout 설정 확인**

1. 호스트에 접속
2. 다음 명령어로 현재 설정 확인

```bash
$ echo $TMOUT
9000  # 이 값이 600을 초과하면 취약
```

#### Nutanix

**사용자 Shell Session Timeout 확인**

1. Controller VM에 접속하여 설정 확인

```bash
sudo cat /etc/profile.d/os-security.sh
```

2. SSH Idle Timeout 확인

```bash
sudo cat /etc/ssh/sshd_config | grep "ClientAliveInterval"
```

### 조치 방법

#### VMware ESXi, vCenter

1. 웹 콘솔에서 고급 설정으로 이동
2. `UserVars.HostClientSessionTimeout` 값이 600초를 초과할 경우 [옵션 편집] 클릭
3. 값 수정: `600`

#### XenServer, KVM

1. `/etc/profile` 파일에 다음 내용 추가

```bash
$ vi /etc/profile
readonly TMOUT=600
export TMOUT
```

2. 설정 적용

```bash
$ source /etc/profile
```

#### Nutanix

**Shell Session Timeout 설정**

1. 설정 파일 수정

```bash
sudo vi /srv/salt/security/CVM/shellCVM.sls
```

2. 다음 내용으로 수정

```bash
os-security-create:
  file:
    - managed
    - name: /etc/profile.d/os-security.sh
    - mode: 644
    - user: root
    - group: root
    - contents: |
      readonly TMOUT=600 2> /dev/null || echo "TMOUT already set."
```

3. 설정 적용

```bash
sudo salt-call state.sls security/CVM/shellCVM
```

**SSH Idle Timeout 설정**

1. 설정 파일 수정

```bash
sudo vi /srv/salt/security/CVM/sshd/sshdconfCVM
```

2. 다음 내용 추가

```bash
ClientAliveInterval 600
```

3. 설정 적용

```bash
sudo salt-call state.sls security/CVM/sshdCVM
```

**관리 웹 콘솔 Session Timeout 설정**

1. 웹 콘솔 접속 (`https://<Nutanix 웹 콘솔 IP>:9440`)
2. Settings > UI Settings > Security Setting > SESSION TIMEOUT 설정을 10분으로 설정

### 주의사항

- **조치 시 영향**: 일반적인 경우 영향 없음
- **권장 설정값**: 600초(10분)
- **일관성**: 모든 관리 채널(웹, SSH, 콘솔)에 동일한 타임아웃 적용 권장

### 추가 팁

1. **업무 특성 고려**: 실제 업무 환경에서 10분이 너무 짧다고 판단되면, 최대 15분(900초)까지 허용하되 보안 정책에 명시
2. **정기적 점검**: 설정이 변경되지 않았는지 정기적으로 확인
3. **로그 모니터링**: 타임아웃으로 인한 세션 종료 로그를 모니터링하여 보안 사고 징후 파악
