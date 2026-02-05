---
title: "[2026 주요정보통신기반시설] HV-17 코어 덤프 수집 기능 활성화"
slug: "2026-주정통/HV-17"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "코어덤프수집기능활성화여부점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Virtualization
---

# HV-17 코어 덤프 수집 기능 활성화

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | HV-17 |
| **점검내용** | 코어덤프수집기능활성화여부점검 |
| **점검대상** | VMware ESXi 등 |
| **판단기준** | 양호: 코어덤프수집기능이활성화(true)된경우 |
| **판단기준** | 취약: 코어덤프수집기능이비활성화(false)된경우 |
| **조치방법** | 코어덤프수집기능활성화적용 |

---
## 상세 설명

### 1. 항목 개요

코어 덤프(Core Dump)는 시스템에 심각한 오류(Panic/Blue Screen)가 발생했을 때, 메모리 내용을 디스크 또는 네트워크로 전송하여 저장하는 기능입니다. 이 덤프 파일을 통해 장애 발생 원인을 분석하고 재발 방지 대책을 수립할 수 있습니다.

VMware ESXi의 **vSphere Network Dump Collector**는 ESXi 호스트가 패닉(PSOD - Purple Screen of Death) 발생 시, VMKernel 메모리 내용을 네트워크로 전송하여 저장하는 서비스입니다.

### 2. 왜 이 항목이 필요한가요?

**코어 덤프의 중요성:**

1. **장애 원인 파악**
   - 커널 패닉 원인 분석
   - 메모리 덤프를 통한 문제점 식별
   - 버그 리포트 작성

2. **재발 방지**
   - 근본 원인 해결
   - 패치 적용 전략 수립
   - 설정 변경 결정

3. **지원 티켓 처리**
   - VMware 지원팀에 덤프 파일 제공
   - 빠른 문제 해결
   - 다운타임 최소화

**위험 시나리오:**

```
ESXi 호스트 → PSOD (Purple Screen of Death) 발생
→ 관리자가 강제 재부팅
→ 장애 원인 미확인
→ 동일 장애 재발
→ 서비스 장애 시간 증가
→ 비즈니스 손실 확대
```

**실제 사례:**
- HBA 드라이버 버그로 반복적 PSOD 발생
- 코어 덤프 분석으로 특정 드라이버 버전 확인
- 패치 적용 후 문제 해결

### 3. 점검 대상

- VMware ESXi

### 4. 판단 기준

- **양호**: 코어 덤프 수집 기능이 활성화(true)된 경우
- **취약**: 코어 덤프 수집 기능이 비활성화(false)된 경우

### 5. 점검 방법

#### VMware ESXi

1. SSH로 ESXi 접속

2. 코어 덤프 상태 확인:
   ```bash
   esxcli system coredump network get
   ```

**양호 출력 예:**
```
   Enable: true
   ServerPort: 6500
   ServerIP: 192.168.1.10
   NetworkInterface: vmk0
```

**취약 출력 예:**
```
   Enable: false
```

3. 코어 덤프 정책 확인:
   ```bash
   esxcli system coredump network check
   ```

### 6. 조치 방법

#### VMware ESXi

**1) 코어 덤프 네트워크 서버 설정**

1. SSH로 ESXi 접속

2. VMKernel 네트워크 인터페이스 확인:
   ```bash
   esxcli network ip connection list | grep vmk
   ```

3. 네트워크 코어 덤프 설정:
   ```bash
   esxcli system coredump network set \
       --interface-name vmk0 \
       --server-ipv4 192.168.1.10 \
       --server-port 6500
   ```

   **설정 예시:**
   - `--interface-name`: VMKernel 인터페이스명 (예: vmk0)
   - `--server-ipv4`: 코어 덤프 서버 IP
   - `--server-port`: 코어 덤프 서버 포트 (기본 6500)

**2) 네트워크 코어 덤프 활성화**

```bash
# 네트워크 코어 덤프 활성화
esxcli system coredump network set --enable true

# 설정 확인
esxcli system coredump network get
```

**3) 코어 덤프 정책 확인**

```bash
# 코어 덤프가 정상적으로 구성되었는지 확인
esxcli system coredump network check
```

### 7. vSphere Network Dump Collector 설정

**vSphere Network Dump Collector**는 VMware가 제공하는 별도의 서비스로, ESXi 호스트의 코어 덤프를 받아서 저장합니다.

**1) vSphere Network Dump Collector 설치**

vCenter Server와 함께 제공되는 별도 설치 파일:
- Windows: `VMware-vSphere-Dump-Collector-x.x.x-xxxxxxx.exe`
- Linux (vCenter Appliance): 번들로 포함

**2) Dump Collector 서버 설정**

1. 설치 후 Dump Collector 서비스 시작

2. 포트 설정 (기본: 6500)

3. 로그 저장 디렉터리 확인

**3) 방화벽 설정**

```bash
# ESXi 방화벽에서 코어 덤프 포트 허용
esxcli network firewall ruleset set --ruleset-id vmkdump --enabled true
```

### 8. 코어 덤프 파일 구조

**Dump Collector 서버 저장 경로:**

```
C:\ProgramData\VMware\vCenterServer\data\vmkdumps\
├── esxi-host-1-20250120-143502.dmp
├── esxi-host-2-20250120-150821.dmp
└── esxi-host-3-20250120-161234.dmp
```

**파일 크기:**
- 일반적으로 1~4 GB
- 메모리 크기에 비례

### 9. 대체 코어 덤프 방법

네트워크 코어 덤프 외에도 다음 방법을 사용할 수 있습니다.

**1) 디스크 코어 덤프**

```bash
# 기존 코어 덤프 파티션 확인
esxcli system coredump partition list

# 새로운 코어 덤프 파티션 설정
esxcli system coredump partition set --enable true \
    --smart-array yes \
    --partition-number 1
```

**2) ESXi 설치 시 자동 생성**

ESXi를 설치할 때 자동으로 코어 덤프 파티션이 생성됩니다 (기본 2.5 GB).

### 10. 코어 덤프 분석

**1) VMware Go to Damkern**

VMware가 제공하는 코어 덤프 분석 도구:
- VMKernel 스택 트레이스 분석
- 장애 원인 식별
- 제품 지원팀에 파일 전송

**2) KB 문서 조회**

코어 덤프 에러 코드로 VMware KB 검색:
- 예: `PSOD error 0x1`, `Purple Screen`
- VMware Knowledge Base: https://kb.vmware.com/

**3) VMware 지센터 티켓**

덤프 파일을 첨부하여 지원 티켓 생성:
- 최대 2 GB 파일 업로드 가능
- 보안 FTP를 통해 전송

### 11. 스토리지 계획

**권장 사항:**

| 호스트 수 | 권장 스토리지 | 설명 |
|-----------|--------------|------|
| 1~10 | 50 GB | 소규모 환경 |
| 11~50 | 200 GB | 중규모 환경 |
| 51+ | 500 GB+ | 대규모 환경 |

**고려사항:**
- 각 덤프 파일: 1~4 GB
- 동시 장애 대비
- 30일 보관 (정책에 따라)

### 12. 모니터링

**1) 코어 덤프 로그 확인**

```bash
# 코어 덤프 이벤트 로그
grep "coredump" /var/log/vmkernel.log

# Dump Collector 서버 로그
# C:\ProgramData\VMware\vCenterServer\logs\vmkdump\
```

**2) 디스크 공간 모니터링**

```bash
# Windows Dump Collector
dir "C:\ProgramData\VMware\vCenterServer\data\vmkdumps\"

# PowerShell
Get-ChildItem "C:\ProgramData\VMware\vCenterServer\data\vmkdumps\" | Measure-Object -Property Length -Sum
```

**3) 자동화된 정리**

```powershell
# PowerShell 스크립트: 30일 이상된 덤프 삭제
$path = "C:\ProgramData\VMware\vCenterServer\data\vmkdumps\"
Get-ChildItem $path -Filter "*.dmp" | Where-Object {
    $_.LastWriteTime -lt (Get-Date).AddDays(-30)
} | Remove-Item
```

### 13. 주의사항

- 네트워크 코어 덤프는 **별도의 Dump Collector 서버** 필요
- Dump Collector 서버는 **높은 대역폭** 필요 (1~4 GB 전송)
- 코어 덤프 파일에는 **민감한 정보** 포함 가능 (메모리 내용)
- **접근 제어** 및 **암호화** 필요
- 정기적 **백업 후 삭제**로 스토리지 관리
- 테스트를 위해 **의도적 PSOD**는 운영 환경에서 비권장

### 14. 테스트 및 검증

**비운영 환경에서 테스트:**

```bash
# ESXi 테스트 모드에서 PSOD 발생
vsish -e set /reliability/crashMe 1

# 주의: 운영 환경에서 절대 실행 금지
```

## 요약

VMware ESXi의 **코어 덤프 수집 기능**은 시스템 장애(PSOD) 발생 시 원인을 파악하는 필수 기능입니다. 반드시 **vSphere Network Dump Collector** 또는 **디스크 코어 덤프**를 활성화해야 합니다. Dump Collector 서버는 충분한 **스토리지(최소 50 GB)**와 **높은 네트워크 대역폭**을 확보해야 합니다. 코어 덤프 파일은 **보안에 주의**하여 관리해야 합니다.
