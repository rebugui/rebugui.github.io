---
title: "[2026 주요정보통신기반시설] HV-08 시스템 사용 주의사항 출력 설정"
slug: "2026-주정통/HV-08"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "원격로그인시시스템사용주의사항출력여부점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Virtualization
---

# HV-08 시스템 사용 주의사항 출력 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | HV-08 |
| **점검내용** | 원격로그인시시스템사용주의사항출력여부점검 |
| **점검대상** | VMware ESXi, vCenter, XenServer, KVM, Nutanix 등 |
| **판단기준** | 양호: 시스템사용주의사항이출력된경우 |
| **판단기준** | 취약: 시스템사용주의사항미출력또는표시문구내에시스템버전정보가노출된경우 |
| **조치방법** | 시스템사용주의사항출력설정 |

---
## 상세 설명

### 1. 항목 개요

시스템 사용 주의사항 출력(Login Banner)은 사용자가 시스템에 로그인하기 전에 보안 경고 메시지를 표시하는 기능입니다. 이는 법적으로 시스템 무단 접속을 경고하고, 사용자가 시스템 사용 시 보안 정책을 인식하도록 하는 중요한 보안 요소입니다.

미국에서는 이를 **베너(Banner)**라고 하며, 연방 법원 판례에 따라 시스템 접속 전 법적 경고를 표시해야만 무단 접속을 처벌할 수 있습니다. 한국에서도 중요 시스템의 경우 법적 효력을 갖는 경고 문구를 표시하는 것이 권장됩니다.

### 2. 왜 이 항목이 필요한가요?

**법적 효력:**
1. **무단 접속 처벌 근거**: 베너가 없는 경우 무단 접속 처벌이 어려울 수 있음
2. **명시적 동의 간주**: 로그인 시 동의한 것으로 간주
3. **감시 권한 고지**: 시스템 모니터링 사전 고지

**보안 효과:**
1. **억제 효과**: 명시적 경고로 비인가 접속 시도 억제
2. **보안 인식**: 사용자에게 보안 정책 상기
3. **실수 방지**: 정상 사용자도 보안 규정 준수 유도

**위험 시나리오:**

1. **베너 미표시 시**
   - 내부자가 악의적인 행위를 해도 처벌 근거 약화
   - 사용자가 보안 정책 인식 부족으로 실수
   - 감시 행위가 프라이버시 침해로 소지 가능

2. **시스템 버전 노출 시**
   - 공격자가 특정 버전 취약점 공격 가능
   - 정보 수집(Reconnaissance) 단계에서 도움

### 3. 점검 대상

- VMware ESXi
- VMware vCenter
- Citrix XenServer
- KVM (RHEL, CentOS, Ubuntu 등)
- Nutanix AHV

### 4. 판단 기준

- **양호**: 시스템 사용 주의사항이 출력된 경우
- **취약**: 시스템 사용 주의사항 미출력 또는 표시 문구 내에 시스템 버전 정보가 노출된 경우

### 5. 점검 방법

#### VMware ESXi

1. Web 콘솔 접속
   ```
   https://<VMware ESXi IP>
   ```

2. **호스트** > **관리** > **시스템** > **고급 설정**으로 이동

3. `Annotations.WelcomeMessage` 설정값 확인

4. 로그인 시 배너 표시 확인

#### VMware vCenter

1. vSphere Client 접속

2. **관리** > **Single Sign On** > **구성** > **로그인 배너** (vCenter 6.5)
   또는
   **관리** > **Single Sign On** > **구성** > **로그인 메시지** (vCenter 8.0)

3. 로그인 배너 설정 여부 확인

#### KVM

1. SSH 설정 파일 확인
   ```bash
   cat /etc/ssh/sshd_config | grep "Banner"
   ```

2. 배너 파일 존재 여부 확인
   ```bash
   cat /etc/issue
   cat /etc/issue.net
   cat /etc/motd
   ```

#### XenServer

1. SSH 설정 파일 확인
   ```bash
   cat /etc/ssh/sshd_config | grep "Banner"
   ```

2. 배너 파일 확인

#### Nutanix

**웹 콘솔 배너:**
1. 웹 콘솔 접속
   ```
   https://<Nutanix 웹 콘솔 IP>:9440
   ```

2. **Settings** > **Appearance** > **Welcome Banner** 확인

**SSH 배너:**
1. Controller VM 또는 AHV에 SSH 접속

2. 배너 파일 확인
   ```bash
   cat /etc/issue
   ```

### 6. 조치 방법

#### VMware ESXi

**웹 콘솔 배너 설정:**

1. **호스트** > **관리** > **시스템** > **고급 설정**으로 이동

2. `Annotations.WelcomeMessage` 선택 후 **옵션 편집** 클릭

3. 다음 배너 메시지 입력:
   ```
   본 시스템은 승인된 사용자만 사용할 수 있습니다.
   무단 접속은 법적 처벌을 받을 수 있습니다.
   모든 접속 및 활동은 모니터링되고 기록됩니다.
   ```

4. 저장

#### VMware vCenter

**vCenter 6.5:**

1. vSphere Client 접속

2. **관리** > **Single Sign On** > **구성** > **로그인 배너**

3. **로그인 배너 텍스트** 입력:
   ```
   본 vCenter 시스템은 승인된 관리자만 사용할 수 있습니다.
   무단 접속은 법적 처벌을 받을 수 있습니다.
   모든 관리 활동은 기록되고 감사됩니다.
   ```

4. 저장

**vCenter 8.0:**

1. vSphere Client 접속

2. **관리** > **Single Sign On** > **구성** > **로그인 메시지**

3. 로그인 배너 텍스트 입력 후 저장

#### KVM

**1) /etc/motd 설정**

1. 메시지 파일 작성
   ```bash
   vi /etc/motd
   ```

2. 다음 내용 입력:
   ```
   *******************************************************************************
   본 시스템은 승인된 사용자만 사용할 수 있습니다.
   무단 접속은 법적 처벌을 받을 수 있습니다.
   모든 접속 및 활동은 모니터링되고 기록됩니다.
   *******************************************************************************
   ```

**2) /etc/issue 설정 (로그인 전 표시)**

1. 메시지 파일 작성
   ```bash
   vi /etc/issue
   ```

2. 로그인 전 메시지 입력:
   ```
   본 시스템은 승인된 사용자만 사용할 수 있습니다.
   무단 접속은 법적 처벌을 받을 수 있습니다.
   ```

**3) SSH 배너 설정**

1. SSH 설정 파일 수정
   ```bash
   vi /etc/ssh/sshd_config
   ```

2. 다음 설정 추가/수정:
   ```
   Banner /etc/issue.net
   ```

3. `/etc/issue.net` 파일 작성
   ```bash
   vi /etc/issue.net
   ```

4. 다음 내용 입력:
   ```
   *******************************************************************************
   경고: 본 시스템은 승인된 사용자만 사용할 수 있습니다.
   무단 접속 시도는 모니터링되며 법적 조치를 취할 수 있습니다.
   접속을 계속하면 이에 동의하는 것으로 간주됩니다.
   *******************************************************************************
   ```

5. SSH 서비스 재시작
   ```bash
   systemctl restart sshd
   ```

#### XenServer

1. SSH 설정 파일 수정
   ```bash
   vi /etc/ssh/sshd_config
   ```

2. 다음 설정 추가/수정:
   ```
   Banner /etc/issue.net
   ```

3. `/etc/issue.net` 파일 작성
   ```bash
   vi /etc/issue.net
   ```

4. 배너 메시지 입력 후 SSH 재시작
   ```bash
   systemctl restart sshd
   ```

#### Nutanix

**웹 콘솔 배너:**

1. 웹 콘솔 접속
   ```
   https://<Nutanix 관리 Web IP>:9440
   ```

2. **Settings** > **Appearance** > **Welcome Banner** 선택

3. 배너 입력:
   ```
   본 시스템은 승인된 사용자만 사용할 수 있습니다.
   무단 접속은 법적 처벌을 받을 수 있습니다.
   ```

4. **Enable Banner** 체크 > **Save** 클릭

**SSH 배너 (DoD 표준):**

1. Controller VM 접속

2. DoD 배너 비활성화
   ```bash
   ncli cluster edit-cvm-security-params enable-banner=false
   ```

3. 배너 파일 백업
   ```bash
   sudo cp -a /srv/salt/security/CVM/sshd/DODbanner \
           /srv/salt/security/CVM/sshd/DODbanner.bak
   ```

4. 배너 파일 수정
   ```bash
   sudo vi /srv/salt/security/CVM/sshd/DODbanner
   ```

5. 다음 내용 입력:
   ```
   본 시스템은 승인된 사용자만을 위한 시스템입니다.
   무단 접속 또는 오용은 모니터링되며 법적 조치를 취할 수 있습니다.
   ```

6. DoD 배너 활성화
   ```bash
   ncli cluster edit-cvm-security-params enable-banner=true
   ```

### 7. 권장 배너 메시지

#### 기본 형식 (국문)

```
*******************************************************************************
주의: 본 시스템은 승인된 사용자만 사용할 수 있는 시스템입니다.

무단 접속, 무단 사용, 시스템 오용은 민형사상 책임을 질 수 있으며,
법적 처벌을 받을 수 있습니다.

시스템의 모든 활동은 모니터링되고 기록됩니다.
본 시스템에 접속함으로써 이러한 모니터링에 동의하는 것으로 간주됩니다.

문의: 관리자 (이메일 또는 전화번호)
*******************************************************************************
```

#### DoD 표준 (영문)

```
You are accessing a U.S. Government (USG) Information System (IS) that is
provided for USG-authorized use only.

By using this IS (which includes any device attached to this IS), you consent
to the following conditions:

- The USG routinely intercepts and monitors communications on this IS for
  purposes including, but not limited to, penetration testing, COMSEC monitoring,
  network operations and defense, personnel misconduct (PM), law enforcement
  (LE), and counterintelligence (CI) investigations.

- At any time, the USG may inspect and seize data stored on this IS.

- Communications using, or data stored on, this IS are not private, are subject
  to routine monitoring, interception, and search, and may be disclosed or used
  for any USG-authorized purpose.

- This IS includes security measures (e.g., authentication and access controls)
  to protect USG interests--not for your personal benefit or privacy.

- Notwithstanding the above, using this IS does not constitute consent to PM,
  LE or CI investigative searching or monitoring of the content of privileged
  communications, or work product, related to personal representation or services
  by attorneys, psychotherapists, or clergy, and their assistants. Such
  communications and work product are private and confidential. See User
  Agreement for details.
```

#### 간결형 (국문)

```
본 시스템은 승인된 사용자만 사용할 수 있습니다.
무단 접속은 법적 처벌을 받을 수 있습니다.
모든 활동은 기록됩니다.
```

### 8. 배너 표시 파일 차이

| 파일 | 설명 | 표시 시점 |
|------|------|----------|
| /etc/issue | 로컬 터미널 로그인 전 | 터미널 로그인 전 |
| /etc/issue.net | 네트워크 로그인 전 | SSH/Telnet 로그인 전 |
| /etc/motd | 로그인 성공 후 | 로그인 후 쉘 시작 전 |
| SSH Banner | SSH 프로토콜 | SSH 연결 시 |

### 9. 주의사항

1. **시스템 버전 정보 노출 금지**
   - 배너에 OS 버전, 소프트웨어 버전 표시 금지
   - 공격자가 정보 수집에 활용 가능

2. **법적 효력 고려**
   - 명확하고 강경한 어조 사용
   - 법적 근거 명시
   - 동의 간주 명시

3. **다국어 지원**
   - 내외국인 사용자 고려
   - 영문/국문 병행 권장

4. **연락처 포함**
   - 관리자 연락처 포함
   - 보안팀 연락처 포함

5. **정기적 검토**
   - 배너 메시지 정기적 검토
   - 법적 자문 권장

### 10. 조치 시 주의사항

- 배너 메시지는 너무 길지 않게 작성 (사용자 경험 고려)
- 특수 문자가 제대로 표시되는지 확인
- SSH, 웹 콘솔 등 모든 접속 경로에 배너 표시 확인
- 배너 적용 후 로그인 테스트 수행

## 요약

시스템 사용 주의사항 배너는 법적 효력과 보안 인식 제고를 위해 **모든 가상화 장비에 필수**로 설정해야 합니다. 배너 메시지는 **"승인된 사용자 전용", "무단 접속 처벌", "모니터링 사실 고지"** 내용을 포함해야 하며, 시스템 버전 정보는 노출하지 않아야 합니다.
