---
title: "[2026 주요정보통신기반시설] HV-06 비밀번호 관리 정책 설정"
slug: "2026-주정통/HV-06"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-09-23
description: "로그인계정에대한비밀번호관리정책설정여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Virtualization
draft: false
---

# HV-06 비밀번호 관리 정책 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | HV-06 |
| **점검내용** | 로그인계정에대한비밀번호관리정책설정여부점검 |
| **점검대상** | VMware ESXi, vCenter, XenServer, KVM, Nutanix 등 |
| **판단기준** | 양호: 로그인계정비밀번호관리정책이적용된경우 |
| **판단기준** | 취약: 로그인계정비밀번호관리정책이적용되지않은경우 |
| **조치방법** | 로그인계정비밀번호를관리정책에맞게설정 |

---
## 상세 설명

### 1. 항목 개요

가상화 장비는 물리적 서버와 달리 여러 대의 가상 머신을 통합 관리하는 핵심 인프라입니다. 가상화 플랫폼의 관리자 계정이 탈취될 경우, 공격자는 단일 계정으로 수십 대에서 수백 대의 가상 머신을 제어할 수 있게 되어 치명적인 보안 사고로 이어질 수 있습니다.

비밀번호 관리 정책은 **무차별 대입 공격(Brute Force Attack)**과 **사전 대입 공격(Dictionary Attack)**으로부터 계정을 보호하는 첫 번째 방어선입니다. 강력한 비밀번호 정책은 계정 탈취 위험을 획기적으로 낮춥니다.

### 2. 왜 이 항목이 필요한가요?

**보안 위협 시나리오:**

1. **약한 비밀번호 사용 시**
   - 공격자가 무차별 대입 공격으로 쉽게 계정 탈취
   - 관리자 계정 탈취 → 모든 가상 머신 장악
   - 랜섬웨어 감염으로 전체 서비스 마비

2. **침해된 비밀번호 사용 시**
   - 탈취 정황이 확인되면 비밀번호 변경과 관련 세션 철회가 필요
   - 평소에는 유출 비밀번호 차단·접속 시도 제한·MFA를 우선

3. **추측하기 쉬운 비밀번호 사용 시**
   - `123456`, `password`, `admin123` 등 흔한 값은 차단
   - 긴 암호 구문을 사용할 수 있도록 설정

**심사 기준과 보안 권고 구분:**
이 글에 제시된 문자 종류 조합과 최대 90일·최소 7일 사용기간은 적용 판본·페이지가 확인된 KISA 기준으로 인용할 수 없습니다. 아래 90일 예시는 **기관에 실제 적용되는 별도 심사 기준이 확인된 경우에만** 검토하세요. 현행 [NIST SP 800-63B-4](https://pages.nist.gov/800-63-4/sp800-63b.html#passwordver)는 침해 증거 없는 주기적 변경과 문자 종류 강제를 요구하지 않으며, 침해 정황에는 변경을 요구합니다.

### 3. 점검 대상

- VMware ESXi
- VMware vCenter
- Citrix XenServer
- KVM (RHEL, CentOS, Ubuntu 등)
- Nutanix AHV

### 4. 판단 기준

- **양호**: 로그인 계정 비밀번호 관리 정책이 적용된 경우
- **취약**: 로그인 계정 비밀번호 관리 정책이 적용되지 않은 경우

### 5. 점검 방법

#### VMware ESXi

1. Web 콘솔 접속
   ```
   https://<VMware ESXi IP>
   ```

2. **호스트** > **관리** > **시스템** > **고급 설정**으로 이동

3. `Security.PasswordQualityControl` 설정값 확인

4. `Security.PasswordMaxDays` 설정값 확인

**확인 항목:**
- `Security.PasswordQualityControl`: 실제 환경에서 적용된 길이·허용 문자·비밀번호 정책 확인
- `Security.PasswordMaxDays`: 기관에 별도 만료 기준이 적용되는지 확인; 90일을 일반 양호 기준으로 단정하지 않음

#### VMware vCenter

1. vSphere Client 접속

2. **관리** > **Single Sign On** > **구성** > **로컬 계정** > **암호 정책**

3. 비밀번호 정책 확인

**확인 항목:**
- 최소 암호 길이
- 암호 복잡성 요구사항
- 암호 수명 기간

#### XenServer

1. XenServer 접속 > Local Command Shell 실행

2. 비밀번호 정책 확인
   ```bash
   cat /etc/login.defs | grep -i "PASS_MAX_DAYS"
   cat /etc/login.defs | grep -i "PASS_MIN_DAYS"
   cat /etc/login.defs | grep -i "PASS_MIN_LEN"
   ```

#### KVM (RHEL 8 이후)

1. PAM 및 pwquality 설정 파일 확인
   ```bash
   cat /etc/security/faillock.conf
   cat /etc/security/pwquality.conf
   ```

2. 비밀번호 정책 확인

#### Nutanix

1. Controller VM 접속

2. 비밀번호 최대 사용 기간 확인
   ```bash
   sudo cat /etc/login.defs | grep -v "^#" | grep "PASS_MAX_DAYS"
   ```

3. 비밀번호 최소 길이 확인
   ```bash
   cat /etc/login.defs | grep -v "^#" | grep "PASS_MIN_LEN"
   ```

### 6. 조치 방법(실제 적용되는 별도 정책 확인 후)

아래의 90일·문자 조합 예시는 모든 가상화 장비의 기본 권고가 아닙니다. 조직에 적용되는 규정의 판본·범위를 확인하지 못했다면 그대로 적용하지 마세요. 공급사 지원 여부와 운영 영향, 복구 절차를 먼저 검토하고 긴 비밀번호·유출 비밀번호 차단·MFA를 우선합니다.

#### VMware ESXi

**1) 비밀번호 복잡성 설정**

1. **호스트** > **관리** > **시스템** > **고급 설정**으로 이동

2. `Security.PasswordQualityControl` 선택 후 **옵션 편집** 클릭

3. 다음과 같이 설정:
   ```
   retry=3 min=10,8,8,8,8
   ```

   - **retry**: 비밀번호 변경 시 조건 불만족 시 재입력 횟수
   - **N0**: 문자 종류 1개만 사용 시 최소 길이
   - **N1**: 문자 종류 2개 사용 시 최소 길이
   - **N2**: 암호 구문 사용 시 최소 길이
   - **N3**: 문자 종류 3개 사용 시 최소 길이 (최소 8)
   - **N4**: 문자 종류 4개 사용 시 최소 길이 (최소 8)

**2) 비밀번호 최대 사용 기간 설정(별도 기준에서 요구할 때만)**

1. `Security.PasswordMaxDays` 선택 후 **옵션 편집** 클릭

2. 해당 기관의 적용 기준이 90일임을 확인한 경우에만 값 `90` 설정

**설정 예시:**
```
Security.PasswordQualityControl = retry=3 min=10,8,8,8,8
Security.PasswordMaxDays = 90
```

#### VMware vCenter

1. vSphere Client 접속

2. **관리** > **Single Sign On** > **구성** > **로컬 계정** > **암호 정책**

3. 적용 정책에 맞는 길이·만료 조건을 선택합니다. 예컨대 별도 심사 기준이 확인된 경우에만 다음 값을 검토합니다.
   - **최소 암호 길이**: 해당 제품과 인증 방식의 허용 범위 확인
   - **암호 복잡성**: 해당 심사 기준에 별도 요구가 있을 때만 사용
   - **암호 수명**: 90일 기준의 적용이 확인된 경우에만 90일

#### XenServer

1. `/etc/login.defs` 파일 수정
   ```bash
   vi /etc/login.defs
   ```

2. 다음 설정 추가/수정:
   ```
   PASS_MIN_LEN 8
   PASS_MAX_DAYS 90
   PASS_MIN_DAYS 7
   ```

#### KVM (RHEL 8 이후)

**1) pwquality.conf 설정**

1. `/etc/security/pwquality.conf` 파일 수정
   ```bash
   vi /etc/security/pwquality.conf
   ```

2. 다음 설정 추가/수정:
   ```
   minlen = 8
   minclass = 3
   dcredit = -1
   ucredit = -1
   lcredit = -1
   ocredit = -1
   ```

**2) login.defs 설정**

1. `/etc/login.defs` 파일 수정
   ```bash
   vi /etc/login.defs
   ```

2. 다음 설정 추가/수정:
   ```
   PASS_MIN_LEN 8
   PASS_MAX_DAYS 90
   PASS_MIN_DAYS 7
   ```

#### Nutanix

**1) 비밀번호 최대 사용 기간 설정**

1. Salt 설정 파일 수정
   ```bash
   sudo vi /srv/salt/security/CVM/pamCVM.sls
   ```

2. 다음 내용 추가/수정:
   ```yaml
   passmaxdays:
     file:
       - replace
       - name: /etc/login.defs
       - pattern: '^PASS_MAX_DAYS.*'
       - repl: 'PASS_MAX_DAYS 90'
   ```

3. 설정 적용
   ```bash
   sudo salt-call state.sls security/CVM/pamCVM
   ```

**2) 계정별 비밀번호 만료 설정**

1. 사용자 그룹 설정 파일 수정
   ```bash
   sudo vi /srv/salt/security/CVM/checkusergroupsCVM.sls
   ```

2. nutanix 및 admin 계정 설정:
   ```yaml
   nutanix:
     user:
       - present
       - shell: /bin/bash
       - home: /home/nutanix
       - uid: 1000
       - gid_from_name: True
       - mindays: 1
       - maxdays: 90

   admin:
     user:
       - present
       - shell: /bin/bash
       - home: /home/admin
       - uid: 2000
       - gid_from_name: True
       - mindays: -1
       - maxdays: 90
   ```

3. 설정 적용
   ```bash
   sudo salt-call state.sls security/CVM/checkusergroupsCVM
   ```

**3) 비밀번호 최소 길이 설정**

1. pamCVM.sls 파일에 추가:
   ```yaml
   passminlendef:
     file:
       - replace
       - name: /etc/login.defs
       - pattern: '^PASS_MIN_LEN.*'
       - repl: 'PASS_MIN_LEN    9'
       - onlyif:
   ```

2. 설정 적용
   ```bash
   sudo salt-call state.sls security/CVM/pamCVM
   ```

### 7. 비밀번호 정책 파라미터 설명(아래 값은 조건부 심사 예시)

#### VMware PasswordQualityControl

| 파라미터 | 설명 | 권장값 |
|---------|------|--------|
| retry | 조건 불만족 시 재입력 횟수 | 3 |
| N0 | 문자 종류 1개 사용 시 최소 길이 | disabled |
| N1 | 문자 종류 2개 사용 시 최소 길이 | 10 |
| N2 | 암호 구문 사용 시 최소 길이 | 8 |
| N3 | 문자 종류 3개 사용 시 최소 길이 | 8 |
| N4 | 문자 종류 4개 사용 시 최소 길이 | 8 |

#### Linux PAM pwquality

| 파라미터 | 설명 | 조건부 심사 예시 |
|---------|------|--------|
| minlen | 비밀번호 최소 길이 | 8 |
| minclass | 필수 문자 종류 수 | 3 |
| dcredit | 숫자 필수 여부 (-1: 필수) | -1 |
| ucredit | 대문자 필수 여부 | -1 |
| lcredit | 소문자 필수 여부 | -1 |
| ocredit | 특수문자 필수 여부 | -1 |

### 8. 비밀번호 정책 운용 시 우선할 사항

1. 관리 계정에는 가능한 한 긴 암호 구문과 MFA를 사용하고 흔하거나 유출된 비밀번호를 차단합니다.
2. 탈취 정황이 확인되면 즉시 비밀번호를 변경하고 세션·접근 기록을 조사합니다. 침해 근거가 없는 일률적인 90일 만료는 일반 권고가 아닙니다.
3. 공급사의 인증 정책 지원 범위와 기관에 실제 적용되는 심사 기준을 확인하고, 계정 잠금이 운영에 미치는 영향과 복구 절차를 검토합니다.

계정 잠금은 원격 운전·복구 계정이 차단될 위험을 고려해 제품별 정책과 승인 절차에 맞춰 설정합니다. 횟수나 잠금 시간도 별도 적용 기준 없이 일률적으로 강제하지 않습니다.

### 9. 조치 시 주의사항

- 비밀번호 정책 변경 시 기존 비밀번호는 즉시 만료되지 않음
- 다음 로그인/비밀번호 변경 시부터 적용
- 너무 복잡한 정책은 사용자가 비밀번호를 적어두게 만들 수 있음
- 비밀번호 관리자 솔루션 도입 권장
- 정책 변경 전 사용자 교육 필수

### 10. 참고 자료

- 비밀번호 길이와 유출 비밀번호 차단은 인증 제공자·제품별 지원 여부 확인
- [NIST SP 800-63B-4: Password Verifiers](https://pages.nist.gov/800-63-4/sp800-63b.html#passwordver)

## 요약

가상화 장비 관리자 계정에는 제품이 허용하는 충분한 길이의 비밀번호, 유출 비밀번호 차단, 인증 시도 제한 및 MFA를 적용해야 합니다. **문자 종류 3개 조합과 90일 주기 변경은 근거가 확인되지 않은 보편적 기준이 아닙니다.** 기관에 별도로 적용되는 심사 기준이 확인되면 그 판본·범위와 현행 보안 권고의 차이를 문서화하고 운영 영향에 맞춰 적용하세요.
