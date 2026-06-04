---
title: "[2026 주요정보통신기반시설] HV-06 비밀번호 관리 정책 설정"
slug: "2026-주정통/HV-06"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "로그인계정에대한비밀번호관리정책설정여부점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Virtualization
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

2. **비밀번호 변경 기간 미설정 시**
   - 한번 탈취된 계정을 무기한 사용 가능
   - 탈취 사실 발견 지연
   - 피해 확대

3. **비밀번호 복잡성 미적용 시**
   - `123456`, `password`, `admin123` 등 쉬운 비밀번호 사용
   - 사전 공격으로 쉽게 탈취

**비밀번호 정책 기준 (KISA 가이드라인):**
- 영문, 숫자, 특수문자 **2개 조합**: **10자리 이상**
- 영문, 숫자, 특수문자 **3개 조합**: **8자리 이상**
- 비밀번호 **최대 사용 기간**: 90일 이하
- 비밀번호 **최소 사용 기간**: 7일 이상

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

**양호 기준:**
- `Security.PasswordQualityControl`: `retry=3 min=N0,N1,N2,N3,N4` (N3, N4가 8 이상)
- `Security.PasswordMaxDays`: 90 이하

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

### 6. 조치 방법

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

**2) 비밀번호 최대 사용 기간 설정**

1. `Security.PasswordMaxDays` 선택 후 **옵션 편집** 클릭

2. 값 설정: `90`

**설정 예시:**
```
Security.PasswordQualityControl = retry=3 min=10,8,8,8,8
Security.PasswordMaxDays = 90
```

#### VMware vCenter

1. vSphere Client 접속

2. **관리** > **Single Sign On** > **구성** > **로컬 계정** > **암호 정책**

3. 다음 정책 설정:
   - **최소 암호 길이**: 8자 이상
   - **암호 복잡성**: 영문, 숫자, 특수문자 조합
   - **암호 수명**: 90일

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

### 7. 비밀번호 정책 파라미터 설명

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

| 파라미터 | 설명 | 권장값 |
|---------|------|--------|
| minlen | 비밀번호 최소 길이 | 8 |
| minclass | 필수 문자 종류 수 | 3 |
| dcredit | 숫자 필수 여부 (-1: 필수) | -1 |
| ucredit | 대문자 필수 여부 | -1 |
| lcredit | 소문자 필수 여부 | -1 |
| ocredit | 특수문자 필수 여부 | -1 |

### 8. 비밀번호 정책 모범 사례

**1) 강력한 비밀번호 정책**
- 최소 8자리 이상
- 영문 대문자, 소문자, 숫자, 특수문자 중 3개 이상 조합
- 개인정보 포함 금지 (생일, 전화번호 등)
- 사전 단어 사용 금지

**2) 비밀번호 수명 관리**
- 최대 사용 기간: 90일
- 최소 사용 기간: 7일 (빈번한 변경 방지)
- 만료 전 7일 알림

**3) 비밀번호 이력 관리**
- 최근 5개 비밀번호 재사용 금지
- 이전 비밀번호와 50% 이상 달라야 함

**4) 계정 잠금 정책 연계**
- 실패 5회 계정 잠금 (HV-07)
- 잠금 시간: 10분 이상
- 관리자만 계정 잠금 해제

### 9. 조치 시 주의사항

- 비밀번호 정책 변경 시 기존 비밀번호는 즉시 만료되지 않음
- 다음 로그인/비밀번호 변경 시부터 적용
- 너무 복잡한 정책은 사용자가 비밀번호를 적어두게 만들 수 있음
- 비밀번호 관리자 솔루션 도입 권장
- 정책 변경 전 사용자 교육 필수

### 10. 참고 자료

- **비밀번호 복잡성 계산기**: https://www.passwordmeter.com/
- **약한 비밀번호 목록**: https://github.com/danielmiessler/SecLists
- **NIST SP 800-63B**: 디지털 아이덴티티 가이드라인

## 요약

가상화 장비의 비밀번호 관리 정책은 **최소 8자리 이상, 영문/숫자/특수문자 3개 조합, 90일 주기 변경** 기준을 충족해야 합니다. 관리자 계정이 탈취될 경우 전체 가상화 인프라가 위험에 처하므로, 강력한 비밀번호 정책 적용이 필수적입니다.
