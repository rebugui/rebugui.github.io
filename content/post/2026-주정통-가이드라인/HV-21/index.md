---
title: "[2026 주요정보통신기반시설] HV-21 가상 머신 콘솔 드래그 앤 드롭 기능 비활성화"
slug: "2026-주정통/HV-21"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "가상머신드래그앤드롭기능비활성화여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Virtualization
---

# HV-21 가상 머신 콘솔 드래그 앤 드롭 기능 비활성화

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | HV-21 |
| **점검내용** | 가상머신드래그앤드롭기능비활성화여부점검 |
| **점검대상** | VMware ESXi 등 |
| **판단기준** | 양호: 가상머신콘솔드래그앤드롭기능이비활성화되어있거나,제한설정된경우 |
| **판단기준** | 취약: 가상머신콘솔드래그앤드롭기능이활성화되어있거나,제한설정되지않은경우 |
| **조치방법** | 가상머신콘솔드래그앤드롭제한설정 |

---
## 상세 설명

### 1. 항목 개요

가상 머신 콘솔의 드래그 앤 드롭(Drag and Drop) 기능은 사용자가 호스트 시스템에서 파일을 마우스로 끌어 게스트 OS로 놓으면 파일이 전송되는 편리한 기능입니다. 하지만 이 기능은 **클립보드 복사/붙여넣기(HV-20)**와 마찬가지로 **데이터 유출 경로**와 **악성코드 전파 경로**가 될 수 있으며, 파일 전송이 로그에 기록되지 않는 심각한 보안 문제가 있습니다.

### 2. 왜 이 항목이 필요한가요?

**드래그 앤 드롭 기능의 위험성:**

1. **무제한 파일 전송**
   - 용량 제한 없이 파일 전송 가능
   - 대용량 데이터 유출 위험
   - 바이너리 파일 전송 가능

2. **로그 기록 부재**
   - 파일 전송 로그 남지 않음
   - 어떤 파일이 전송되었는지 추적 불가
   - 침해 사고 조사 방해

3. **악성코드 전파**
   - 악성 실행 파일을 드래그 앤 드롭으로 전송
   - 매크로 포함 문서 파일 전송
   - 자동 실행으로 악성코드 감염

**위험 시나리오:**

```
해커 또는 내부자 → 중요 파일들 선택 (수백 MB)
→ vSphere Client 콘솔로 드래그 앤 드롭
→ 게스트 OS로 파일 전송
→ 외부 USB 또는 클라우드로 업로드
→ 데이터 유출 완료
→ 로그에는 파일 전송 기록 없음
→ 보안팀에서 유출 경로 추적 불가
```

**실제 유출 사례:**
- 설계도면 CAD 파일을 드래그 앤 드롭으로 유출
- 고객 데이터베이스 덤프 파일 전송
- 소스 코드 전체를 압축하여 전송

### 3. 점검 대상

- VMware ESXi

### 4. 판단 기준

- **양호**: 가상 머신 콘솔 드래그 앤 드롭 기능이 비활성화되어 있거나, 제한 설정된 경우
- **취약**: 가상 머신 콘솔 드래그 앤 드롭 기능이 활성화되어 있거나, 제한 설정되지 않은 경우

### 5. 점검 방법

#### VMware ESXi

1. Web 콘솔 접속
   ```
   https://<VMware ESXi IP>
   ```

2. **가상 시스템** > [가상 머신 선택] > **설정 편집** > **VM 옵션** > **고급** > **구성 매개 변수**로 이동

3. 다음 매개 변수 확인:
   - `isolation.tools.dnd.disable`

**양호 기준:**
```
isolation.tools.dnd.disable = TRUE
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

   **매개 변수:**
   - 키: `isolation.tools.dnd.disable`
   - 값: `TRUE`

5. **저장** 클릭

**2) PowerCLI를 이용한 일괄 설정**

```powershell
# 모든 VM에 드래그 앤 드롭 비활성화
Get-VM | ForEach-Object {
    $vm = $_

    # 기존 설정 확인
    $existing = Get-AdvancedSetting -Entity $vm -Name "isolation.tools.dnd.disable" -ErrorAction SilentlyContinue

    if (-not $existing) {
        # 새로운 설정 추가
        New-AdvancedSetting -Entity $vm `
            -Name "isolation.tools.dnd.disable" `
            -Value $true -Confirm:$false
        Write-Host "드래그 앤 드롭 비활성화 완료: $($vm.Name)"
    } elseif ($existing.Value -ne $true) {
        # 기존 설정 변경
        Set-AdvancedSetting -AdvancedSetting $existing -Value $true -Confirm:$false
        Write-Host "드래그 앤 드롭 비활성화 수정 완료: $($vm.Name)"
    } else {
        Write-Host "이미 비활성화됨: $($vm.Name)"
    }
}
```

**3) VMX 파일 직접 수정**

```bash
# VM 전원 OFF 상태에서 VMX 파일 수정
vi /vmfs/volumes/datastore1/VM/VM.vmx

# 다음 라인 추가
isolation.tools.dnd.disable = "TRUE"
```

**4) 모든 VM 일괄 적용 스크립트**

```bash
#!/bin/bash
# 모든 VM의 VMX 파일에 드래그 앤 드롭 비활성화 추가

for VMX_FILE in $(find /vmfs/volumes -name "*.vmx"); do
    if ! grep -q "isolation.tools.dnd.disable" "$VMX_FILE"; then
        echo "isolation.tools.dnd.disable = \"TRUE\"" >> "$VMX_FILE"
        echo "드래그 앤 드롭 비활성화: $VMX_FILE"
    else
        echo "이미 설정됨: $VMX_FILE"
    fi
done
```

### 7. 구성 매개 변수 상세

| 매개 변수 | 값 | 설명 |
|-----------|-----|------|
| isolation.tools.dnd.disable | TRUE | 드래그 앤 드롭 비활성화 |
| isolation.tools.dnd.disable | FALSE | 드래그 앤 드롭 활성화 (기본값) |

### 8. HV-20과 함께 적용

**클립보드 + 드래그 앤 드롭 완전 차단:**

```
isolation.tools.copy.disable = TRUE
isolation.tools.paste.disable = TRUE
isolation.tools.dnd.disable = TRUE
isolation.tools.setGUIOptions.enable = FALSE
```

이 4가지 설정을 모두 적용하면 **모든 형태의 호스트-게스트 간 파일 전송**이 차단됩니다.

### 9. 대체 파일 전송 방법

드래그 앤 드롭 대신 안전한 파일 전송 방법:

**1) vSphere Client 데이터스토어 브라우저**
- 파일을 데이터스토어에 업로드 (로그 남음)
- VM 내부에서 네트워크 공유로 접근

**2) SCP/SFTP**
```bash
# SCP를 통한 안전한 파일 전송
scp -P 22 file.txt root@vm-ip:/tmp/

# SFTP
sftp root@vm-ip
put file.txt
```

**3) VMware Tools 복사 기능**
```powershell
# PowerCLI
Copy-VMGuestFile -VM "VM-Name" -SourceToDestination `
    -LocalPath "C:\file.txt" -GuestPath "/tmp/file.txt" `
    -GuestUser "root" -GuestPassword "password"
```

**4) 네트워크 공유**
- SMB/CIFS 공유
- NFS 공유
- 웹 서버

**5) 관리 도구**
- Ansible
- PowerShell Remoting
- Chef, Puppet

### 10. 모범 사례

**1) 모든 운영 VM에 적용**
- 서버용 VM: 반드시 적용
- 데스크톱용 VM: 권장 적용
- VDI 환경: 필수 적용

**2) 템플릿에 설정**
- VM 템플릿에 미리 설정
- 신규 VM 생성 시 자동 적용

**3) 파일 전송 정책 수립**
- 허용된 파일 전송 방법 문서화
- 승인 프로세스 마련
- 전송 로그 검토

**4) 정기적 점검**
- 월 1회 이상 전체 VM 점검
- 신규 VM 생성 시 즉시 확인

### 11. 주의사항

- **관리자 편의성 저하**: 드래그 앤 드롭 차단 시 파일 전송 불편
- **VMware Tools 필요**: VMware Tools가 설치되어 있어야 작동
- **대체 수단 마련**: 안전한 파일 전송 방법 교육 필요
- 콘솔 기능만 차단, 네트워크 전송은 정상 작동
- 변경 후 **기능 테스트** 필요

### 12. 파일 전송 모니터링

드래그 앤 드롭을 비활성화한 후에도 다른 경로의 파일 전송을 모니터링하세요.

**1) vCenter 로그 확인**
```bash
# 파일 전송 로그
grep "file" /var/log/vmware/hostd.log
```

**2) 네트워크 전송 모니터링**
- firewall-cmd 로그
- IDS/IPS rule

**3) 데이터스토어 접근 로그**
- 데이터스토어 브라우저 접근 기록
- 파일 업로드/다운로드 로그

### 13. 추가 보안 설정

**1) HV-20 클립보드 비활성화**

**2) HV-18 장치 변경 제한**

**3) USB 장치 제거 (HV-19)**

**4) VM 콘솔 접속 제한**
- IP 기반 접속 제한
- 시간대별 접속 제한

## 요약

모든 가상 머신에 **`isolation.tools.dnd.disable = TRUE`**를 설정하여 드래그 앤 드롭 기능을 비활성화해야 합니다. 이는 **대용량 데이터 유출 방지**와 **감사 추적**을 위한 필수 보안 설정입니다. **HV-20 클립보드 비활성화**와 함께 적용하면 모든 호스트-게스트 간 파일 전송이 차단됩니다. 대신 **SCP/SFTP**, **vSphere 데이터스토어 브라우저**, **네트워크 공유**와 같은 **안전하고 로그가 남는 파일 전송 방법**을 사용하세요.
