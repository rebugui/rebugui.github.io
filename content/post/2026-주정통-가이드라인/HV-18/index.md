---
title: "[2026 주요정보통신기반시설] HV-18 가상 머신의 장치 변경 제한 설정"
slug: "2026-주정통/HV-18"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "가상머신장치변경제한설정적용여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Virtualization
---

# HV-18 가상 머신의 장치 변경 제한 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | HV-18 |
| **점검내용** | 가상머신장치변경제한설정적용여부점검 |
| **점검대상** | VMware ESXi 등 |
| **판단기준** | 양호: 가상머신의장치설정변경방지설정이활성화(true)된경우 |
| **판단기준** | 취약: 가상머신의장치설정변경방지설정이없거나,비활성화(false)된경우 |
| **조치방법** | 가상머신의장치설정변경방지활성화적용 |

---
## 상세 설명

### 1. 항목 개요

가상 머신의 장치 변경 제한 설정은 게스트 OS 내에서 관리자 권한이 없는 사용자나 악성 프로세스가 가상 머신의 하드웨어 장치(네트워크 어댑터, CD-ROM, USB 등)를 연결 끊거나 설정을 변경하는 것을 방지하는 보안 기능입니다.

이 기능은 **VM Escape(가상 머신 탈출)** 공격의 일부를 차단하고, 게스트 OS에서의 악의적 행위로 호스트 보안을 위협하는 것을 방지합니다.

### 2. 왜 이 항목이 필요한가요?

**장치 변경 위험성:**

1. **VM Escape 공격 경로**
   - 악성코드가 가상 하드웨어 조작
   - 취약한 하이퍼바이저 드라이버 이용
   - 호스트 시스템 장악 시도

2. **네트워크 장치 변경**
   - 네트워크 어댑터 연결 해제
   - 서비스 거부
   - 프라미스큐어 모드 설정으로 스니핑

3. **CD-ROM/DVD 장치 악용**
   - 악성 ISO 이미지 마운트
   - 악성코드 실행
   - 데이터 반출

**위험 시나리오:**

```
게스트 OS 감염 → 악성코드 실행
→ 가상 CD-ROM 장치 제어
→ 악성 ISO 마운트
→ 하이퍼바이저 취약점 공격
→ VM Escape 성공
→ ESXi 호스트 장악
→ 다른 가상 머전 감염
```

**실제 공격 벡터:**
- CVE-2017-4901: CD-ROM 장치를 통한 VM Escape
- Venom 취약점: FLOPPY 장치 버퍼 오버플로우

### 3. 점검 대상

- VMware ESXi

### 4. 판단 기준

- **양호**: 가상 머신의 장치 설정 변경 방지 설정이 활성화(true)된 경우
- **취약**: 가상 머신의 장치 설정 변경 방지 설정이 없거나, 비활성화(false)된 경우

### 5. 점검 방법

#### VMware ESXi

1. Web 콘솔 접속
   ```
   https://<VMware ESXi IP>
   ```

2. **가상 시스템** > [가상 머신 선택] > **설정 편집** > **VM 옵션** > **고급** > **구성 매개 변수**로 이동

3. 다음 매개 변수 확인:
   - `isolation.device.edit.disable`
   - `isolation.device.connectable.disable`

**양호 기준:**
```
isolation.device.edit.disable = TRUE
isolation.device.connectable.disable = TRUE
```

**취약 기준:**
- 매개 변수가 존재하지 않음
- 값이 FALSE

### 6. 조치 방법

#### VMware ESXi

**1) 개별 가상 머신 설정**

1. 가상 머신 선택 > **설정 편집** 클릭

2. **VM 옵션** > **고급** > **구성 매개 변수**로 이동

3. **구성 매개 변수 편집** 클릭

4. 다음 매개 변수 추가:

   **매개 변수 1:**
   - 키: `isolation.device.connectable.disable`
   - 값: `TRUE`

   **매개 변수 2:**
   - 키: `isolation.device.edit.disable`
   - 값: `TRUE`

5. **저장** 클릭

**2) PowerCLI를 이용한 일괄 설정**

```powershell
# 모든 가상 머신에 설정 적용
Get-VM | ForEach-Object {
    $vm = $_
    # 장치 연결 변경 비활성화
    New-AdvancedSetting -Entity $vm `
        -Name "isolation.device.connectable.disable" `
        -Value $true -Confirm:$false

    # 장치 편집 비활성화
    New-AdvancedSetting -Entity $vm `
        -Name "isolation.device.edit.disable" `
        -Value $true -Confirm:$false
}
```

**3) 특정 장치만 제어**

네트워크 어댑터만 제어:
```
isolation.device.connectable.disable = FALSE
```

모든 장치 제어:
```
isolation.device.edit.disable = TRUE
```

### 7. 구성 매개 변수 상세

| 매개 변수 | 값 | 설명 |
|-----------|-----|------|
| isolation.device.connectable.disable | TRUE | 게스트 OS에서 장치 연결/해제 금지 |
| isolation.device.edit.disable | TRUE | 게스트 OS에서 장치 설정 변경 금지 |
| isolation.device.edit.disable | FALSE | 장치 설정 변경 허용 (기본) |

### 8. 영향 받는 장치

**제한되는 장치:**
- 네트워크 어댑터 (NIC)
- SCSI 컨트롤러
- SATA 컨트롤러
- 직렬 포트
- 병렬 포트
- USB 컨트롤러
- CD-ROM/DVD 드라이브
- FLOPPY 드라이브

**영향 받지 않는 것:**
- 가상 CPU
- 메모리
- 가상 디스크 (VMDK)

### 9. 특정 장치 예외 설정

**일부 장치만 허용:**

모든 장치를 제한하되 특정 장치만 허용하려면 VMX 파일을 직접 수정:

```
# 모든 장치 제한
isolation.device.edit.disable = TRUE

# 특정 장치만 허용 (예: USB)
isolation.device.edit.disable = FALSE
# VMX 파일에서 해당 장치 설정
```

### 10. 모범 사례

**1) 모든 운영 가상 머전에 적용**
- 서버용 VM: 반드시 적용
- 데스크톱용 VM: 권장 적용
- 테스트 VM: 선택 적용

**2) 템플릿에 설정**
- VM 템플릿에 미리 설정
- 새 VM 생성 시 자동 적용

**3) 정기적 점검**
- 신규 VM 생성 시 설정 확인
- 월 1회 이상 전체 VM 점검

### 11. 주의사항

- **관리자는 vSphere Client**에서 장치 변경 가능 (영향 없음)
- **게스트 OS 관리자**라고 하더라도 장치 변경 불가
- 일부 **레거시 애플리케이션**은 장치 연결이 필요할 수 있음
- 변경 전 **테스트 환경에서 검증** 필수
- **악성코드** 실행 방지를 위해서는 다른 보안 설정과 함께 적용 필요

### 12. 추가 보안 설정

**1) VMX 파일 보호**

```bash
# VMX 파일 권한 제한
chmod 600 /vmfs/volumes/datastore1/VM/VM.vmx
chown root:root /vmfs/volumes/datastore1/VM/VM.vmx
```

**2) 불필요한 장치 제거 (HV-19)**
- FLOPPY 제거
- 불필요한 직렬/병렬 포트 제거
- USB 제거

**3) 콘솔 기능 제한 (HV-20, HV-21)**
- 클립보드 복사/붙여넣기 비활성화
- 드래그 앤 드롭 비활성화

## 요약

모든 가상 머신에 **`isolation.device.edit.disable = TRUE`**와 **`isolation.device.connectable.disable = TRUE`**를 설정하여 게스트 OS에서의 장치 변경을 차단해야 합니다. 이는 **VM Escape 공격**과 **악성코드**에 의한 하이퍼바이저 공격을 방지하는 핵심 보안 설정입니다. **vSphere Client**를 통한 장치 관리는 여전히 가능하므로 운영에는 영향이 없습니다.
