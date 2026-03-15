---
title: "[2026 주요정보통신기반시설] HV-23 가상 스위치 무차별(Promiscuous) 모드 정책 비활성화"
slug: "2026-주정통/HV-23"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "무차별(Promiscuous)모드비활성화여부점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Virtualization
---

# HV-23 가상 스위치 무차별(Promiscuous) 모드 정책 비활성화

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | HV-23 |
| **점검내용** | 무차별(Promiscuous)모드비활성화여부점검 |
| **점검대상** | VMware ESXi, XenServer 등 |
| **판단기준** | 양호: 가상스위치무차별(Promiscuous)모드정책설정이거부로설정된경우 |
| **판단기준** | 취약: 가상스위치무차별(Promiscuous)모드정책설정이허용으로설정된경우 |
| **조치방법** | 가상스위치무차별(Promiscuous)모드정책거부설정 |

---
## 상세 설명

### 1. 항목 개요

무차별(Promiscuous) 모드는 네트워크 인터페이스가 자신에게 전달된 패킷뿐만 아니라, **동일한 네트워크 세그먼트의 모든 트래픽**을 수신하는 모드입니다. 이는 네트워크 관리자가 트래픽을 분석하거나 문제를 해결할 때 유용하지만, 동시에 **스니핑(Sniffing)** 공격에 악용될 수 있는 심각한 보안 위협입니다.

가상 스위치의 Promiscuous 모드가 허용되어 있으면, 악의적인 VM이 동일한 가상 스위치에 연결된 다른 VM의 트래픽을 모니터링할 수 있게 됩니다.

### 2. 왜 이 항목이 필요한가요?

**Promiscuous 모드의 위험성:**

1. **네트워크 스니핑**
   - 다른 VM 간 통신 내용 가로채기
   - 평문 트래픽(HTTP, FTP, Telnet 등) 노출
   - 중요 정보(암호, 세션 ID, 데이터) 탈취

2. **프라이버시 침해**
   - 사용자 활동 모니터링
   - 기밀 정보 유출
   - 감사 우회 가능

3. **MITM 공격 지원**
   - 트래픽 분석으로 취약점 파악
   - 세션 하이재킹 준비
   - 공격 경로 탐색

**위험 시나리오:**

```
악성 VM → Promiscuous 모드 활성화
→ 동일 가상 스위치의 모든 트래픽 수신
→ 웹 서버 VM과 DB 서버 간 통신 가로채기
→ HTTP 평문 트래픽에서 암호 추출
→ 세션 쿠키 탈취
→ 관리자 계정 탈취
→ 가상화 인프라 장악
```

**실제 공격 사례:**
- 동일 네트워크의 다른 VM에서 전송되는 데이터베이스 쿼리 가로채기
- HTTP 기반 내부 웹 애플리케이션의 로그인 자격증명 탈취

### 3. 점검 대상

- VMware ESXi
- Citrix XenServer

### 4. 판단 기준

- **양호**: 가상 스위치 무차별(Promiscuous) 모드 정책 설정이 거부로 설정된 경우
- **취약**: 가상 스위치 무차별(Promiscuous) 모드 정책 설정이 허용으로 설정된 경우

### 5. 점검 방법

#### VMware ESXi

1. Web 콘솔 접속
   ```
   https://<VMware ESXi IP>
   ```

2. **네트워킹** > **가상 스위치** > [가상 스위치 선택] > **설정 편집** > **보안**으로 이동

3. **무차별 모드** 정책 확인

**양호 기준:**
- 무차별 모드: **거부**

**취약 기준:**
- 무차별 모드: **허용**

#### XenServer

1. XenServer CLI 접속

2. PIF/VIF UUID 확인:
   ```bash
   xe pif-list network-name-label="<네트워크_이름>"
   xe vif-list vm-name-label="<VM_이름>"
   ```

3. promiscuous 값 확인:
   ```bash
   xe pif-param-list uuid=<PIF_UUID>
   xe vif-param-list uuid=<VIF_UUID>
   ```

### 6. 조치 방법

#### VMware ESXi

**1) 가상 스위치 설정 변경**

1. **네트워킹** > **가상 스위치**로 이동

2. 변경할 가상 스위치 선택 > **설정 편집** 클릭

3. **보안** 탭으로 이동

4. **무차별 모드** 정책을 **거부**로 변경

5. **저장** 클릭

**2) 분산 스위치(Distributed Switch) 설정**

1. **네트워킹** > **분산 스위치** > [분산 스위치 선택]

2. **설정 편집** > **보안** > **무차별 모드**

3. **거부**로 설정

**3) PowerCLI를 이용한 일괄 설정**

```powershell
# 모든 표준 스위치에 Promiscuous 모드 거부 설정
Get-VirtualSwitch | ForEach-Object {
    $sw = $_
    # Promiscuous 모드 거부
    $sw | Get-SecurityPolicy | Set-SecurityPolicy `
        -AllowPromiscuous $false -Confirm:$false
    Write-Host "Promiscuous 모드 거부 설정 완료: $($sw.Name)"
}

# 분산 스위치
Get-VDSwitch | ForEach-Object {
    $vds = $_
    $vds | Get-VDSecurityPolicy | Set-VDSecurityPolicy `
        -AllowPromiscuous $false -Confirm:$false
    Write-Host "분산 스위치 Promiscuous 모드 거부 설정 완료: $($vds.Name)"
}
```

#### XenServer

**Promiscuous 모드 비활성화:**

```bash
# PIF promiscuous 비활성화
xe pif-param-set uuid=<PIF_UUID> other-config:promiscuous="false"

# VIF promiscuous 비활성화
xe vif-param-set uuid=<VIF_UUID> other-config:promiscuous="false"

# 전체 네트워크에 적용
xe network-list params=other-config
```

### 7. 보안 정책 옵션

| 정책 | 설명 | 권장 대상 |
|------|------|-----------|
| 허용 | Promiscuous 모드 허용 | 취약 |
| 거부 | Promiscuous 모드 거부 | 모든 스위치 (권장) |

### 8. Promiscuous 모드 이해

**정상 동작 (비-Promiscuous):**
- 자신의 MAC 주소로 향하는 패킷만 수신
- 브로드캐스트, 멀티캐스트 패킷도 수신

**Promiscuous 모드:**
- 모든 패킷 수신 (자신 MAC 관계없음)
- 네트워크 스니핑 가능

### 9. Promiscuous 모드 필요 시나리오

**정당한 사용 사례:**

1. **IDS/IPS 시스템**
   - 네트워크 침입 탐지 시스템
   - 트래픽 분석 필요

2. **네트워크 모니터링**
   - 네트워크 성능 분석
   - 문제 해결

3. **패킷 캡처**
   - 네트워크 포렌식
   - 보안 조사

**이러한 경우 처리 방법:**
- **별도의 전용 VLAN**에 IDS/IPS 배치
- **포트그룹 레벨**에서만 허용
- **네트워크 세그먼트 분리**

### 10. 함께 적용해야 할 설정

**HV-22 MAC 주소 변경 비활성화**
```
MAC 주소 변경: 거부
```

**HV-24 위조 전송 비활성화**
```
위조 전송: 거부
```

**3가지 설정 모두 적용 시:**
```
MAC 주소 변경: 거부
무차별 모드: 거부
위조 전송: 거부
```

### 11. 예외 사항

**Promiscuous 모드가 필요한 경우:**

1. **IDS/IPS 가상 머신**
   - Snort, Suricata 등
   - 네트워크 트래픽 분석

2. **네트워크 모니터링 도구**
   - Wireshark 실행 VM
   - 네트워크 분석기

**예외 처리 방법:**
- 해당 VM이 있는 **포트그룹만 허용**
- **전용 VLAN**으로 격리
- **VXLAN/NVGRE**로 트래픽 암호화

### 12. 모범 사례

**1) 기본 정책: 거부**
- 모든 스위치와 포트그룹의 기본값을 거부로 설정

**2) IDS/IPS용 별도 포트그룹**
- Promiscuous 허용 포트그룹 생성
- IDS/IPS VM만 연결
- VLAN으로 격리

**3) 정기적 점검**
- 월 1회 이상 전체 스위치 점검
- 승인되지 않은 Promiscuous 모드 탐지

### 13. 모니터링

**Promiscuous 모드 탐지:**

```bash
# ESXi 호스트에서 Promiscuous 모드 감지
esxcli network vswitch standard list | grep "Promiscuous"

# vCenter에서 PowerCLI로 확인
Get-VirtualPortGroup | Get-SecurityPolicy | Where-Object {$_.AllowPromiscuous -eq $true}
```

**비정상 트래픽 탐지:**
- IDS/IPS 경보 모니터링
- 네트워크 이상 행위 탐지

### 14. 주의사항

- Promiscuous 모드 **거부**가 네트워크 기능에 영향 없음
- IDS/IPS 등 특수한 경우 **포트그룹 레벨 예외** 허용
- 변경 후 **네트워크 연결 테스트** 필수
- **HV-22, HV-24**와 함께 적용 권장
- **암호화된 트래픽**(HTTPS, SSH)이라도 스니핑 가능성 있음

## 요약

모든 가상 스위치의 **Promiscuous 모드를 거부**로 설정해야 합니다. 이는 **네트워크 스니핑 공격**을 차단하여 가상 머신 간 트래픽 보안을 강화하는 핵심 설정입니다. IDS/IPS와 같이 **정당한 사유**가 있는 경우, **별도의 포트그룹과 VLAN**으로 격리하여 허용할 수 있습니다. **HV-22 MAC 주소 변경 비활성화**와 **HV-24 위조 전송 비활성화**와 함께 적용하여 가상 네트워크의 3대 주요 보안 정책을 완성하세요.
