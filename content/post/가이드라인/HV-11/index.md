---
title: "[2026 주요정보통신기반시설] HV-11 MOB(Managed Object Browser) 서비스 비활성화"
slug: "2026-주정통/HV-11"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "MOB서비스비활성화여부점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Virtualization
---

# HV-11 MOB(Managed Object Browser) 서비스 비활성화

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | HV-11 |
| **점검내용** | MOB서비스비활성화여부점검 |
| **점검대상** | VMware ESXi, vCenter 등 |
| **판단기준** | 양호: MOB(Managed Object Browser)가비활성화된경우 |
| **판단기준** | 취약: MOB(Managed Object Browser)가활성화된경우 |
| **조치방법** | MOB(Managed Object Browser)서비스비활성화설정 |

---
## 상세 설명

### 1. 항목 개요

MOB(Managed Object Browser)는 VMware vSphere의 웹 기반 관리 인터페이스로, 모든 관리 객체를 탐색하고 조작할 수 있는 강력한 도구입니다. MOB는 주로 개발者和 Troubleshooting을 위해 설계되었으나, 동시에 심각한 보안 위험도 가지고 있습니다.

MOB는 기본적으로 인증 없이 또는 약한 인증으로 접근할 수 있어, 비인가자가 시스템을 완전히 장악할 수 있는 경로를 제공할 수 있습니다.

### 2. 왜 이 항목이 필요한가요?

**MOB의 위험성:**

1. **완전한 제어 권한**
   - 가상 머신 생성/삭제/중지/시작
   - 사용자 계정 생성/권한 변경
   - 네트워크 설정 변경
   - 스토리지 구성 변경

2. **정보 노출**
   - 모든 시스템 구조 노출
   - 관리 객체 계층 구조 확인
   - 시스템 설정 및 구성 정보 노출
   - 취약점 분석을 위한 정보 제공

3. **인증 우회 가능성**
   - 세션 하이재킹 가능
   - CSRF(Cross-Site Request Forgery) 공격 가능
   - 약한 인증 메커니즘

**위험 시나리오:**

```
공격자 → MOB URL 탐지 (https://<ESXi>/mob)
→ 접속 시도 → 인증 우회 또는 약한 비밀번호로 로그인
→ 시스템 객체 탐색 → 관리자 계정 생성
→ 권한 부여 → 시스템 완전 장악
→ 모든 가상 머신 삭제/암호화
```

**실제 공격 경로:**

1. **MOB를 통한 가상 머신 제어**
   ```
   /mob/?moid=vm-123&do=Destroy
   ```

2. **MOB를 통한 사용자 생성**
   ```
   /mob/?moid=UserDirectory&do=CreateUser
   ```

3. **MOB를 통한 권한 변경**
   ```
   /mob/?moid=AuthorizationManager&do=SetEntityPermissions
   ```

### 3. 점검 대상

- VMware ESXi
- VMware vCenter

### 4. 판단 기준

- **양호**: MOB(Managed Object Browser)가 비활성화된 경우
- **취약**: MOB(Managed Object Browser)가 활성화된 경우

### 5. 점검 방법

#### VMware ESXi

1. Web 콘솔 접속
   ```
   https://<VMware ESXi IP>
   ```

2. **호스트** > **관리** > **시스템** > **고급 설정**으로 이동

3. `Config.HostAgent.plugins.solo.enableMob` 설정값 확인

4. 웹 브라우저에서 직접 확인:
   ```
   https://<ESXi_IP>/mob
   ```
   - 비활성화: 접속 거부 또는 404 에러
   - 활성화: 로그인 페이지 표시

**양호 기준:**
- `Config.HostAgent.plugins.solo.enableMob` = `false`

**취약 기준:**
- `Config.HostAgent.plugins.solo.enableMob` = `true`

#### VMware vCenter

**vCenter 6.5:**

1. vSphere Client 접속

2. **호스트 및 클러스터** > [vCenter 서버] > **구성** > **설정** > **고급 설정**

3. `config.vpxd.enableDebugBrowse` 확인

**vCenter 8.0:**

1. vSphere Client 접속

2. **호스트 및 클러스터** > [vCenter 서버] > **구성** > **설정** > **고급 설정**

3. `config.vpxd.enableDebugBrowse` 확인

4. 웹 브라우저에서 직접 확인:
   ```
   https://<vCenter_IP>/mob
   ```

**양호 기준:**
- `config.vpxd.enableDebugBrowse` = `false`

**취약 기준:**
- `config.vpxd.enableDebugBrowse` = `true`

### 6. 조치 방법

#### VMware ESXi

**1) 웹 콘솔 설정**

1. Web 콘솔 접속
   ```
   https://<VMware ESXi IP>
   ```

2. **호스트** > **관리** > **시스템** > **고급 설정**으로 이동

3. `Config.HostAgent.plugins.solo.enableMob` 선택 후 **옵션 편집** 클릭

4. 값 설정: `false`

5. **저장** 클릭

6. 호스트 서비스 재시작 필요 없음

**2) CLI 설정**

1. SSH로 ESXi 접속

2. MOB 비활성화
   ```bash
   vim-cmd hostsvc/advopt/update Config.HostAgent.plugins.solo.enableMob boolean false
   ```

3. 설정 확인
   ```bash
   vim-cmd hostsvc/advopt/query Config.HostAgent.plugins.solo.enableMob
   ```

#### VMware vCenter

**vCenter 6.5:**

1. vSphere Client 접속

2. **호스트 및 클러스터** > [vCenter 서버] > **구성** > **설정** > **고급 설정**

3. `config.vpxd.enableDebugBrowse` 선택 후 **편집** 클릭

4. 값 설정: `false`

5. **확인** 클릭

6. vCenter 서비스 재시작:
   ```bash
   service-control --stop --all
   service-control --start --all
   ```

**vCenter 8.0:**

1. vSphere Client 접속

2. **호스트 및 클러스터** > [vCenter 서버] > **구성** > **설정** > **고급 설정**

3. `config.vpxd.enableDebugBrowse` 선택 후 **편집** 클릭

4. 값 설정: `false`

5. **저장** 클릭

6. vCenter 서비스 재시작

**CLI 설정 (vCenter):**

1. vCenter 서버 SSH 접속

2. 설정 변경
   ```bash
   /usr/lib/vmware-vma/bin/vmactl-set-registrar -i \
       com.vmware.vpxd.config.vpxd.enableDebugBrowse -t boolean -v false
   ```

3. vCenter 서비스 재시작
   ```bash
   service-control --stop --all
   service-control --start --all
   ```

### 7. MOB 비활성화 검증

#### VMware ESXi

```bash
# 1. 설정 확인
vim-cmd hostsvc/advopt/query Config.HostAgent.plugins.solo.enableMob

# 2. 웹 브라우저에서 접속 시도
# https://<ESXi_IP>/mob
# 예상 결과: "404 Not Found" 또는 접속 거부
```

#### VMware vCenter

```bash
# 1. 설정 확인
/usr/lib/vmware-vma/bin/vmactl-get-registrar \
    com.vmware.vpxd.config.vpxd.enableDebugBrowse

# 2. 웹 브라우저에서 접속 시도
# https://<vCenter_IP>/mob
# 예상 결과: "404 Not Found" 또는 접속 거부
```

### 8. MOB가 필요한 경우 대안

MOB가 개발 또는 Troubleshooting에 필요한 경우, 다음과 같은 안전한 대안을 사용하세요.

**1) vSphere Client 사용**
- 대부분의 MOB 기능을 제공
- 보안이 강화된 인증

**2) PowerCLI 사용**
```powershell
# PowerCLI를 통한 안전한 관리
Connect-VIServer -Server <vCenter_IP>
Get-VM | Where-Object {$_.PowerState -eq "PoweredOn"}
```

**3) vSphere API SDK 사용**
- 공식 API를 통한 프로그래밍 방식 관리
- 적절한 인증과 권한 부여

**4) 일시적 활성화 + 강력한 네트워크 제한**
```bash
# MOB 일시적 활성화
vim-cmd hostsvc/advopt/update Config.HostAgent.plugins.solo.enableMob boolean true

# 방화벽에서 특정 IP만 접근 허용
esxcli network firewall ruleset set --ruleset-id=httpServer --allowed-all false
esxcli network firewall ruleset allowedip add --ruleset-id=httpServer --ip-address=<관리자_IP>

# 사용 후 즉시 비활성화
vim-cmd hostsvc/advopt/update Config.HostAgent.plugins.solo.enableMob boolean false
```

### 9. 추가 보안 조치

**1) 네트워크 접근 제한**
- MOB URL에 대한 IP 필터링
- 방화벽에서 웹 콘솔 접속 IP 제한 (HV-02 참조)

**2) 웹 애플리케이션 방화벽(WAF)**
- MOB URL 접근 차단 규칙
- 이상 행위 탐지

**3) 모니터링**
- MOB 접속 시도 로그 모니터링
- 비정상적 접속 시도 시 알림

**4) 정기적 검토**
- 웹 서비스 노출 점검
- 보안 설정 감사

### 10. MOB 공격 탐지

**로그 분석:**

```bash
# ESXi 호스트 로그
grep "mob" /var/log/vmware/hostd.log
grep "ManagedObjectBrowser" /var/log/vmware/hostd.log

# vCenter 로그
grep "mob" /var/log/vmware/vpxd/vpxd.log
grep "enableDebugBrowse" /var/log/vmware/vpxd/vpxd.log
```

**웹 접근 로그:**

```bash
# nginx/apache 접근 로그 (Reverse Proxy 사용 시)
grep "/mob" /var/log/nginx/access.log
```

### 11. 조치 시 주의사항

- MOB 비활성화는 즉시 적용됨 (서비스 재시작 불필요)
- vCenter의 경우 서비스 재시작 필요 (운영 중 단시간 중지)
- 비활성화 후 반드시 접속 차단 확인 필요
- PowerCLI 또는 vSphere Client를 통한 관리 방법 숙지 필요

### 12. 기타 관리 인터페이스

MOB 외에도 비활성화가 권장되는 관리 인터페이스:

| 인터페이스 | 경로 | 위험도 |
|-----------|------|--------|
| Managed Object Browser | /mob | 상 |
| vSphere Client SDK | /sdk | 중 |
| Web Access | /ui | 중 |
| vSphere Web Client | /vsphere-client | 하 |

## 요약

MOB(Managed Object Browser)는 가상화 시스템을 **완전히 장악할 수 있는 매우 위험한 관리 인터페이스**입니다. ESXi는 기본적으로 비활성화되어 있으나, vCenter는 기본적으로 활성화되어 있으므로 반드시 비활성화해야 합니다. PowerCLI 또는 vSphere Client와 같은 **안전한 대체 관리 도구**를 사용하세요.
