---
title: "[2026 주요정보통신기반시설] HV-05 가상화장비 사용자 인증 강화"
slug: "2026-주정통/HV-05"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "사용자계정별적절한권한이부여여부점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Virtualization
---

# HV-05 가상화장비 사용자 인증 강화

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | HV-05 |
| **점검내용** | 사용자계정별적절한권한이부여여부점검 |
| **점검대상** | VMware ESXi, vCenter, XenServer, KVM, Nutanix 등 |
| **판단기준** | 양호: 계정별불필요한권한이부여되지않은경우 |
| **판단기준** | 취약: 계정별불필요한권한이부여된경우 |
| **조치방법** | 불필요한권한이부여된계정에대한권한제거 |

---
## 상세 설명

### 1. 항목 개요

가상화 장비의 사용자 계정 관리는 물리적 서버와 동일하게 중요하지만, 가상화 환경의 특성상 더욱 중요한 의미를 가집니다. 가상화 플랫폼은 여러 대의 가상 머신을 통합 관리하는 핵심 인프라로서, 단일 계정의 권한 남용으로 인한 영향이 물리적 서버보다 훨씬 광범위할 수 있습니다.

사용자 계정에 적절한 권한을 부여하는 것은 **최소 권한의 원칙(Principle of Least Privilege)**을 구현하는 핵심 요소입니다. 각 계정은 자신의 업무를 수행하는 데 필요한 최소한의 권한만을 가지도록 구성해야 합니다.

### 2. 왜 이 항목이 필요한가요?

가상화 시스템에서 계정 권한 관리가 중요한 이유는 다음과 같습니다.

**보안 위협 시나리오:**

1. **권한 과다 부여로 인한 위험**
   - 모든 계정에 관리자 권한이 부여된 경우
   - 일반 운영자 계정이 탈취되어도 가상화 시스템 전체 장악 가능

2. **의도치 않은 설정 변경**
   - 권한 없는 사용자의 실수로 중요한 가상 머신 삭제/중지
   - 네트워크 설정 변경으로 인한 서비스 중단

3. **공격 경로 제공**
   - 일반 계정 탈취 → 권한 상승 → 가상화 플랫폼 장악
   - 가상 머신 탈출(VM Escape) 공격과 연계될 가능성

4. **사후 추적 어려움**
   - 여러 계정이 동일한 관리자 권한을 사용할 경우
   - 로그에서 실제 공격자 식별이 어려움

### 3. 점검 대상

- VMware ESXi
- VMware vCenter
- Citrix XenServer
- KVM (Kernel-based Virtual Machine)
- Nutanix AHV

### 4. 판단 기준

- **양호**: 계정별로 불필요한 권한이 부여되지 않은 경우
- **취약**: 계정별로 불필요한 권한이 부여된 경우

### 5. 점검 방법

#### VMware ESXi

1. Web 콘솔 페이지 접속
   ```
   https://<VMware ESXi IP>
   ```

2. **호스트** > **작업** > **사용 권한**으로 이동

3. 등록된 계정별 사용 권한 확인

4. 각 계정의 역할(Role)이 적절한지 확인

#### VMware vCenter

1. vSphere Client 접속

2. **호스트 및 클러스터** > vCenter 서버 선택

3. **관리** > **사용 권한** 메뉴 확인

4. 사용자별 권한 레벨 확인

#### XenServer (Active Directory 미가입)

1. 호스트에 bash 쉘 접속

2. 계정 목록 확인
   ```bash
   grep /bin/bash /etc/passwd | cut -f1 -d:
   ```

3. 그룹 소속 확인
   ```bash
   groups <username>
   ```

#### XenServer (Active Directory 가입)

1. XenServer CLI 접속

2. 계정별 부여된 권한 확인
   ```bash
   xe subject-list
   ```

3. 역할(Role) 정보 확인
   ```bash
   xe role-list
   ```

#### KVM

1. 호스트에 접속

2. bash 계정 목록 확인
   ```bash
   grep /bin/bash /etc/passwd | cut -f1 -d:
   ```

3. libvirt 권한 확인
   ```bash
   vi /etc/libvirt/libvirtd.conf
   ```

#### Nutanix

1. 웹 콘솔 접속
   ```
   https://<Nutanix 웹 콘솔 IP>:9440
   ```

2. **Settings** > **Users and Roles** > **Local User Management** 선택

3. 등록된 사용자 계정 및 권한 확인

### 6. 조치 방법

#### VMware ESXi

1. **호스트** > **작업** > **사용 권한**으로 이동

2. 권한 조정이 필요한 계정 선택

3. **역할에 맞는 권한으로 변경**

   - **Read-only**: 읽기 전용 권한
   - **Administrator**: 모든 권한 (최소한으로 부여)
   - **No-access**: 접속 불가

4. 권한 변경 후 저장

#### VMware vCenter

1. vSphere Client에서 사용자 선택

2. **권한** 탭에서 권한 확인

3. **편집** 클릭 후 역할 변경

4. 적절한 역할 선택:
   - **Read-only**: 모니터링만 가능
   - **Virtual Machine User**: VM 운영만 가능
   - **Administrator**: 전체 관리 권한

#### XenServer (Active Directory 미가입)

1. 불필요한 그룹에서 계정 제거
   ```bash
   gpasswd -d username users
   ```

2. 필요한 경우 그룹 추가
   ```bash
   gpasswd -a username admin
   ```

#### XenServer (Active Directory 가입)

1. 기존 역할 제거
   ```bash
   xe subject-role-remove uuid=<subject uuid> role-name=<role_name_to_remove>
   ```

2. 새로운 역할 추가
   ```bash
   xe subject-role-add uuid=<subject uuid> role-name=<role_name_to_add>
   ```

#### KVM

1. 불필요한 그룹에서 계정 제거
   ```bash
   gpasswd -d username users
   ```

2. libvirt 권한 설정
   ```bash
   vi /etc/libvirt/libvirtd.conf
   ```

3. 설정 후 libvirt 재시작
   ```bash
   systemctl restart libvirtd
   ```

#### Nutanix

1. 웹 콘솔에서 해당 계정 선택

2. 불필요한 권한 제거

3. 역할(Role) 변경:
   - **Admin**: 모든 권한
   - **Viewer**: 읽기 전용
   - **Cluster Admin**: 클러스터 관리만 가능

4. 변경 사항 저장

### 7. 권한별 역할 정의

#### VMware vSphere 역할

| 역할 | 권한 범위 | 사용 예시 |
|------|-----------|----------|
| Administrator | 모든 권한 | 시스템 관리자 |
| Read-only | 읽기만 가능 | 모니터링 담당자 |
| Virtual Machine User | VM 생성/관리 | VM 운영자 |
| Virtual Machine Power User | VM 권한 + 스냅샷 | VM 운영자 |
| Datastore Consumer | 데이터스토어 읽기 | 백업 담당자 |
| Network Administrator | 네트워크 설정 | 네트워크 관리자 |

#### XenServer 역할

| 역할 | 권한 범위 |
|------|-----------|
| Pool Admin | 풀 전체 관리 |
| Pool Operator | VM 운영만 가능 |
| VM Power Admin | VM 전원 관리 |
| Read-only | 읽기만 가능 |

#### Nutanix 역할

| 역할 | 권한 범위 |
|------|-----------|
| Admin | 모든 권한 |
| Viewer | 읽기 전용 |
| Cluster Admin | 클러스터 관리 |
| User | 기본 사용자 권한 |

### 8. 조치 시 주의사항

- 관리자 권한은 **반드시 최소 인원**에게만 부여
- 업무 역할에 따라 **적절한 권한 수준** 부여
- 정기적으로 **권한 재검토** (최소 6개월 1회)
- 퇴사자 및 이동자 계정의 **즉시 권한 회수**
- 권한 변경 내역 **로그 기록** 및 **정기 검토**
- Emergency 계정(비상용 계정)은 별도로 관리하고 비밀번호 보관

### 9. 모범 사례

1. **역할 기반 접근 제어(RBAC) 구현**
   - 업무 역할에 따라 권한 그룹화
   - 개별 계정이 아닌 그룹으로 권한 관리

2. **권한 분리**
   - 운영 권한과 감사 권한 분리
   - 변경 권한과 승인 권한 분리

3. **정기적 권한 검토**
   - 분기별 권한 재검토
   - 연 1회 이상 외부 감사

4. **가상화 플랫폼별 권한 관리 정책 수립**
   - 각 플랫폼별 권한 관리 가이드라인 마련
   - 권한 요청 및 변경 절차 문서화

## 요약

가상화 장비의 사용자 계정에는 **최소 권한의 원칙**을 적용하여, 각 계정이 업무 수행에 필요한 최소한의 권한만 가지도록 구성해야 합니다. 관리자 권한은 최소한의 계정에만 부여하고, 일반 사용자 계정이 탈취되더라도 가상화 시스템 전체가 장악당하는 위험을 최소화해야 합니다.
