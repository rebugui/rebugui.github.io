---
title: "[2026 주요정보통신기반시설] HV-10 SNMP Community String 복잡성 적용"
slug: "2026-주정통/HV-10"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "SNMP CommunityString복잡성적용여부점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Virtualization
---

# HV-10 SNMP Community String 복잡성 적용

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | HV-10 |
| **점검내용** | SNMP CommunityString복잡성적용여부점검 |
| **점검대상** | VMware ESXi, vCenter, XenServer, KVM, Nutanix 등 |
| **판단기준** | 양호: SNMP Community String이복잡도를만족하는경우 |
| **판단기준** | 취약: SNMP CommunityString이복잡도를만족하지않는경우 |
| **조치방법** | SNMP CommunityString을복잡도를만족하는값으로설정 |

---
## 상세 설명

### 1. 항목 개요

SNMP(Simple Network Management Protocol)는 네트워크 장비를 모니터링하고 관리하기 위한 표준 프로토콜입니다. SNMP는 Community String이라는 일종의 비밀번호를 사용하여 장비에 접근을 제어합니다.

SNMPv1과 SNMPv2c는 Community String을 평문으로 전송하므로, 약한 Community String은 네트워크 스니핑을 통해 쉽게 탈취될 수 있습니다. 이는 공격자가 시스템 정보를 수집하거나 장비 설정을 변경할 수 있는 심각한 보안 위협으로 이어질 수 있습니다.

### 2. 왜 이 항목이 필요한가요?

**SNMP Community String의 위험성:**

1. **기본값 노출**
   - `public`: 읽기 전용 기본값
   - `private`: 쓰기 권한 기본값
   - 이러한 기본값은 공격자가 가장 먼저 시도하는 값

2. **평문 전송**
   - SNMPv1/v2c는 Community String을 암호화하지 않음
   - 네트워크 스니핑으로 쉽게 탈취 가능
   - Wireshark 등으로 캡처 시 바로 노출

3. **정보 노출**
   - 시스템 정보, 설치 소프트웨어, 네트워크 토폴로지
   - 사용자 계정, 프로세스 정보
   - 공격자가 시스템 공격 전 정보 수집(Reconnaissance)에 활용

4. **시스템 장악**
   - Community String 탈취 시 설정 변경 가능
   - 방화벽 규칙 변경, 서비스 중지
   - 시스템 장악 및 서비스 거부

**위험 시나리오:**

```
공격자 → 네트워크 스캔 → UDP 161 포트 발견
→ SNMP 서비스 탐지 → `public` 시도 → 성공
→ 시스템 정보 수집 (장비型号, OS 버전, 설치 SW, 네트워크 구성)
→ 취약점 공격 → 시스템 장악
```

### 3. 점검 대상

- VMware ESXi
- VMware vCenter
- Citrix XenServer
- KVM (RHEL, CentOS, Ubuntu 등)
- Nutanix AHV

### 4. 판단 기준

- **양호**: SNMP Community String이 복잡도를 만족하는 경우
  - 최소 8자리 이상
  - 영문, 숫자, 특수문자 조합
  - 유추하기 어려운 문자열

- **취약**: SNMP Community String이 복잡도를 만족하지 않는 경우
  - 기본값(`public`, `private`) 사용
  - 8자리 미만
  - 사전 단어 또는 유추 쉬운 값

### 5. 점검 방법

#### VMware ESXi

1. SSH로 ESXi 접속

2. SNMP 설정 확인
   ```bash
   esxcli system snmp get
   ```

3. Community String 확인:
   ```
   Enable: true
   Communities: <community_string>
   ```

#### VMware vCenter

1. SNMP 서비스 상태 확인
   ```bash
   if [[ $(vim-cmd proxysvc/service_list | grep 'TSM') ]]; then
       echo "SNMP service is running on vcenter"
   else
       echo "SNMP service is not running on vcenter"
   fi
   ```

2. Community String 확인
   ```bash
   cat /etc/vmware/snmp.xml | grep community | awk -F '"' '{print $4}'
   ```

#### KVM

1. SNMP 설정 파일 확인
   ```bash
   cat /etc/snmp/snmpd.conf | grep com2sec
   ```

2. Community String 확인

#### XenServer

1. XenCenter 접속

2. 해당 서버 설정 > SNMP

3. SNMP 활성화 여부 및 Community String 확인

#### Nutanix

1. 웹 콘솔 접속
   ```
   https://<Nutanix 웹 콘솔>:9440
   ```

2. **Settings** > **SNMP** 선택

3. Community String 확인

### 6. 조치 방법

#### VMware ESXi

1. SSH로 ESXi 접속

2. Community String 설정
   ```bash
   esxcli system snmp set --communities <새로운_Community_String>
   ```

   **예시:**
   ```bash
   esxcli system snmp set --communities Snmp@Str#ng$2025!
   ```

3. 설정 확인
   ```bash
   esxcli system snmp get
   ```

#### VMware vCenter

1. `/etc/vmware/snmp.xml` 파일 수정
   ```bash
   vi /etc/vmware/snmp.xml
   ```

2. Community String 변경
   ```xml
   <snmp>
       <communities>Snmp@Str#ng$2025!</communities>
       <enable>true</enable>
       <port>161</port>
   </snmp>
   ```

3. 서비스 재시작
   ```bash
   service-snmp restart
   ```

#### KVM

1. SNMP 설정 파일 수정
   ```bash
   vi /etc/snmp/snmpd.conf
   ```

2. Community String 변경
   ```
   com2sec readonly default Snmp@Str#ng$2025!
   com2sec readwrite default SnmpWrit@#2025!
   ```

3. 서비스 재시작
   ```bash
   systemctl enable snmpd
   systemctl restart snmpd
   ```

#### XenServer

1. XenCenter 접속

2. 해당 서버 설정 > SNMP

3. **Enable SNMP** 체크

4. Community String 변경:
   ```
   Snmp@Str#ng$2025!
   ```

5. **OK** 클릭

#### Nutanix

**1) 불필요한 경우 SNMP 서비스 비활성화 (권장)**

1. 웹 콘솔 접속
   ```
   https://<Nutanix 웹 콘솔>:9440
   ```

2. **Settings** > **SNMP** 선택

3. **Enable for Nutanix objects** 체크 해제

4. **Save** 클릭

**2) SNMPv3 사용 (권장)**

1. **Settings** > **SNMP** > **Users** > **New User** 클릭

2. SNMP User 생성:
   - **User Name**: 모니터링 사용자
   - **Authentication Protocol**: SHA
   - **Privacy Protocol**: AES
   - **Password**: 강력한 비밀번호

3. **Traps** > **New Trap receiver** 클릭

4. Receiver 설정:
   - **Receiver Name**: logcenter
   - **IP Address**: 트랩 수신 서버 IP
   - **Port**: 162
   - **Version**: v3
   - **User**: 생성한 사용자

5. **Save** 클릭

**3) v2c 사용 시 Community String 복잡성 적용**

1. **Settings** > **SNMP** > **Traps** > **편집** 클릭

2. SNMP Community String 설정:
   ```
   COMMUNITY Tltjf135&()
   ```

3. **Save** 클릭

### 7. SNMP Community String 복잡성 요구사항

**최소 요구사항:**
- 최소 8자리 이상
- 영문 대소문자, 숫자, 특수문자 조합
- 사전 단어 사용 금지
- 기본값(`public`, `private`) 사용 금지

**권장 사항:**
- 12자리 이상
- 영문, 숫자, 특수문자 최소 3종류 조합
- 시스템별 고유한 값 사용
- 주기적 변경 (최소 1년 1회)

**복잡한 Community String 예시:**

```
Snmp@Str#ng$2025!
K1a@Snmp#C0mm!2025
N3tw0rk$M0nit#2025!
```

**취약한 Community String 예시:**

```
public (기본값)
private (기본값)
12345678
password
snmp123
```

### 8. SNMPv3 사용 권장

SNMPv3는 다음과 같은 보안 기능을 제공합니다.

| 기능 | 설명 |
|------|------|
| 메시지 무결성 | HMAC-MD5 또는 HMAC-SHA |
| 메시지 암호화 | CBC-DES 또는 CFB-AES |
| 인증 | USM (User-based Security Model) |
| 접근 제어 | VACM (View-based Access Control Model) |

**SNMPv3 설정 예시 (KVM):**

1. `/etc/snmp/snmpd.conf` 파일 수정
   ```bash
   vi /etc/snmp/snmpd.conf
   ```

2. SNMPv3 사용자 생성
   ```
   createUser snmpv3user SHA "authpassword" AES "privpassword"
   rouser snmpv3user priv
   ```

3. 서비스 재시작
   ```bash
   systemctl restart snmpd
   ```

### 9. SNMP 보안 모범 사례

**1) SNMPv3 사용**
- 암호화와 인증 지원
- Community String 대신 USM 사용
- 새로운 설치 시 SNMPv3만 사용

**2) 불필요 시 서비스 비활성화**
- 모니터링 도구가 없는 경우 비활성화
- SNMP 서비스를 사용하지 않는다면 완전히 제거

**3) 네트워크 접근 제한**
- 방화벽에서 UDP 161/162 포트 제한
- 관리 네트워크에서만 접근 허용
- SNMP 접속 IP 화이트리스트

**4) SNMP View 제한**
- 전체 OID가 아닌 필요한 OID만 노출
- 읽기 전용 Community String만 사용
- 쓰기 권한은 특별한 경우에만 부여

**5) 정기적 변경**
- Community String 주기적 변경
- SNMPv3 비밀번호 주기적 변경
- 변경 내역 로그 기록

### 10. SNMP 보안 설정 확인 방법

**SNMP Community String 테스트:**

```bash
# SNMP walk 테스트
snmpwalk -v2c -c <community_string> <target_ip> system

# SNMPv3 테스트
snmpwalk -v3 -u <username> -l authPriv -a SHA -A <auth_password> \
         -x AES -X <priv_password> <target_ip> system
```

**SNMP 정보 노출 확인:**

```bash
# 시스템 정보 확인
snmpwalk -v2c -c <community_string> <target_ip> 1.3.6.1.2.1.1

# 네트워크 인터페이스 확인
snmpwalk -v2c -c <community_string> <target_ip> 1.3.6.1.2.1.2

# 설치 소프트웨어 확인
snmpwalk -v2c -c <community_string> <target_ip> 1.3.6.1.2.1.25
```

### 11. 주의사항

- SNMP Community String 변경 시 모니터링 도구 설정도 함께 변경 필요
- 여러 시스템에서 동일한 Community String 사용 자제
- 변경 전 반드시 백업 수행
- 네트워크 장비에서도 동일하게 적용 필요

## 요약

SNMP Community String은 **최소 8자리 이상, 영문/숫자/특수문자 조합**으로 구성해야 하며, 기본값(`public`, `private`)은 반드시 변경해야 합니다. 가능하면 **SNMPv3**를 사용하여 암호화와 인증을 적용하는 것이 권장됩니다. 모니터링 도구가 없다면 **SNMP 서비스를 비활성화**하는 것이 가장 안전합니다.
