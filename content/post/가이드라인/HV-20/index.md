---
title: "[2026 주요정보통신기반시설] HV-20 가상 머신 콘솔 클립보드 복사&붙여넣기 기능 비활성화"
slug: "2026-주정통/HV-20"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "가상머신콘솔복사기능비활성화여부점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Virtualization
---

# HV-20 가상 머신 콘솔 클립보드 복사&붙여넣기 기능 비활성화

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | HV-20 |
| **점검내용** | 가상머신콘솔복사기능비활성화여부점검 |
| **점검대상** | VMware ESXi 등 |
| **판단기준** | 양호: 가상머신콘솔복사기능이비활성화되어있거나,복사제한이설정된경우 |
| **판단기준** | 취약: 가상머신콘솔복사기능이활성화되어있거나,복사제한이설정되지않은경우 |
| **조치방법** | 가상머신콘솔복사제한설정 |

---
## 상세 설명

### 1. 항목 개요

가상 머신 콘솔의 클립보드 복사&붙여넣기 기능은 사용자가 호스트와 게스트 OS 사이에 텍스트를 복사하고 붙여넣을 수 있는 편리한 기능입니다. 하지만 이 기능은 동시에 **데이터 유출 경로**와 **악성코드 전파 경로**가 될 수 있습니다.

이 기능이 활성화되어 있으면 파일 전송이 로그에 기록되지 않아, 침해 사고 조사 시 데이터 유출 경로를 추적할 수 없습니다.

### 2. 왜 이 항목이 필요한가요?

**클립보드 기능의 위험성:**

1. **데이터 유출**
   - 중요 정보를 클립보드에 복사하여 외부로 유출
   - 로그에 기록되지 않아 추적 불가
   - 대용량 텍스트 데이터 유출 가능

2. **악성코드 전파**
   - 호스트에서 악성 스크립트 복사
   - 게스트 OS에 붙여넣어 실행
   - 감사 로그 없이 악성코드 실행

3. **감사 우회**
   - 파일 전송 로그 없음
   - 정상 파일 전송과 구분 어려움
   - 침해 사고 조사 방해

**위험 시나리오:**

```
내부자 → 중요 문서 열람
→ 클립보드에 내용 복사
→ 외부 메신저에 붙여넣기
→ 데이터 유출
→ 로그에는 "복사/붙여넣기" 기록 안 남음
→ 보안팀에서 유출 경로 추적 불가
```

**실제 유출 사례:**
- 소스 코드를 클립보드로 복사하여 경쟁사에 유출
- 고객 정보를 클립보드로 복사하여 개인 이메일로 전송

### 3. 점검 대상

- VMware ESXi

### 4. 판단 기준

- **양호**: 가상 머신 콘솔 복사 기능이 비활성화되어 있거나, 복사 제한이 설정된 경우
- **취약**: 가상 머신 콘솔 복사 기능이 활성화되어 있거나, 복사 제한이 설정되지 않은 경우

### 5. 점검 방법

#### VMware ESXi

1. Web 콘솔 접속
   ```
   https://<VMware ESXi IP>
   ```

2. **가상 시스템** > [가상 머신 선택] > **설정 편집** > **VM 옵션** > **고급** > **구성 매개 변수**로 이동

3. 다음 매개 변수 확인:
   - `isolation.tools.copy.disable`
   - `isolation.tools.paste.disable`
   - `isolation.tools.setGUIOptions.enable`

**양호 기준:**
```
isolation.tools.copy.disable = TRUE
isolation.tools.paste.disable = TRUE
isolation.tools.setGUIOptions.enable = FALSE
```

**취약 기준:**
- 매개 변수가 존재하지 않음
- 값이 FALSE (기본값: ESXi는 비활성화가 기본이나 명시적으로 설정 권장)

### 6. 조치 방법

#### VMware ESXi

**1) 개별 가상 머신 설정**

1. 가상 머신 선택 > **설정 편집** 클릭

2. **VM 옵션** > **고급** > **구성 매개 변수**로 이동

3. **구성 매개 변수 편집** 클릭

4. 다음 매개 변수 추가:

   **매개 변수 1:**
   - 키: `isolation.tools.copy.disable`
   - 값: `TRUE`

   **매개 변수 2:**
   - 키: `isolation.tools.paste.disable`
   - 값: `TRUE`

   **매개 변수 3:**
   - 키: `isolation.tools.setGUIOptions.enable`
   - 값: `FALSE`

5. **저장** 클릭

**2) PowerCLI를 이용한 일괄 설정**

```powershell
# 모든 VM에 클립보드 비활성화 설정 적용
Get-VM | ForEach-Object {
    $vm = $_

    # 복사 비활성화
    New-AdvancedSetting -Entity $vm `
        -Name "isolation.tools.copy.disable" `
        -Value $true -Confirm:$false -ErrorAction SilentlyContinue

    # 붙여넣기 비활성화
    New-AdvancedSetting -Entity $vm `
        -Name "isolation.tools.paste.disable" `
        -Value $true -Confirm:$false -ErrorAction SilentlyContinue

    # GUI 옵션 비활성화
    New-AdvancedSetting -Entity $vm `
        -Name "isolation.tools.setGUIOptions.enable" `
        -Value $false -Confirm:$false -ErrorAction SilentlyContinue
}
```

**3) VMX 파일 직접 수정**

```bash
# VM 전원 OFF 상태에서 VMX 파일 수정
vi /vmfs/volumes/datastore1/VM/VM.vmx

# 다음 라인 추가
isolation.tools.copy.disable = "TRUE"
isolation.tools.paste.disable = "TRUE"
isolation.tools.setGUIOptions.enable = "FALSE"
```

### 7. 구성 매개 변수 상세

| 매개 변수 | 값 | 설명 |
|-----------|-----|------|
| isolation.tools.copy.disable | TRUE | 호스트→게스트 복사 금지 |
| isolation.tools.paste.disable | TRUE | 게스트→호스트 복사 금지 |
| isolation.tools.setGUIOptions.enable | FALSE | 모든 GUI 옵션 비활성화 |

**설정 조합:**

| 복사 | 붙여넣기 | 설명 |
|------|---------|------|
| TRUE | TRUE | 양방향 모두 차단 (권장) |
| TRUE | FALSE | 호스트→게스트만 차단 |
| FALSE | TRUE | 게스트→호스트만 차단 (데이터 유출 방지) |
| FALSE | FALSE | 모두 허용 (취약) |

### 8. 특정 VM에만 예외 적용

**관리자 VM에만 클립보드 허용:**

```powershell
# 관리자 VM 목록
$AdminVMs = Get-VM | Where-Object {$_.Name -like "*Admin*"}

# 관리자 VM은 클립보드 허용
Get-VM | Where-Object {$_.Name -notin $AdminVMs.Name} | ForEach-Object {
    New-AdvancedSetting -Entity $_ `
        -Name "isolation.tools.copy.disable" `
        -Value $true -Confirm:$false
}
```

### 9. 대체 파일 전송 방법

클립보드 대신 안전한 파일 전송 방법:

**1) vSphere Client 데이터스토어 브라우저**
- ISO 파일 업로드
- VM에 CD-ROM으로 마운트

**2) 공유 폴더**
- vSphere Shared Folders
- 네트워크 파일 시스템 (NFS, SMB)

**3) SCP/SFTP**
```bash
# SCP를 통한 안전한 파일 전송
scp file.txt root@vm-ip:/tmp/
```

**4) 관리 도구**
- VMware Tools의 파일 복사 기능 (로그 남음)
- Ansible, PowerShell과 같은 구성 관리 도구

### 10. 모범 사례

**1) 모든 운영 VM에 적용**
- 서버용 VM: 반드시 적용
- 데스크톱용 VM: 권장 적용
- 관리자 VM: 선택적 허용

**2) 템플릿에 설정**
- VM 템플릿에 미리 설정
- 신규 VM 생성 시 자동 적용

**3) 정기적 점검**
- 월 1회 이상 전체 VM 점검
- 신규 VM 생성 시 즉시 확인

### 11. 주의사항

- **관리자 편의성 vs 보안**: 클립보드 차단 시 편의성 저하
- **관리자 VM은 예외** 가능하나 최소화 권장
- **VMware Tools** 설치 상태와 상관없이 작동
- 콘솔 복사 기능 외에도 **HV-21 드래그 앤 드롭**도 비활성화 권장
- 변경 후 **기능 테스트** 필요

### 12. 추가 보안 설정

**1) HV-21 드래그 앤 드롭 비활성화**
```
isolation.tools.dnd.disable = TRUE
```

**2) HV-18 장치 변경 제한**

**3) VM 콘솔 접속 로그 기록**
- vCenter 로그에서 콘솔 접속 기록 확인
- 비정상적 접속 시도 탐지

## 요약

모든 가상 머신에 **`isolation.tools.copy.disable = TRUE`**와 **`isolation.tools.paste.disable = TRUE`**를 설정하여 클립보드 복사&붙여넣기 기능을 비활성화해야 합니다. 이는 **데이터 유출 방지**와 **감사 추적**을 위한 필수 보안 설정입니다. 불가피하게 사용해야 하는 관리자 VM은 **최소화**하고 **별도의 승인 프로세스**를 두는 것이 좋습니다. 대신 **SCP/SFTP**나 **vSphere 데이터스토어 브라우저**와 같은 **안전한 파일 전송 방법**을 사용하세요.
