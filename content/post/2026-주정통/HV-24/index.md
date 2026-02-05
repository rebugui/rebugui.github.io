---
title: "[2026 주요정보통신기반시설] HV-24 가상 스위치 위조 전송(Forged Transmits) 모드 정책 비활성화"
slug: "2026-주정통/HV-24"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "가상스위치위조전송(Forged Transmits)모드비활성화여부점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Virtualization
---

# HV-24 가상 스위치 위조 전송(Forged Transmits) 모드 정책 비활성화

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | HV-24 |
| **점검내용** | 가상스위치위조전송(Forged Transmits)모드비활성화여부점검 |
| **점검대상** | VMware ESXi 등 |
| **판단기준** | 양호: 가상스위치에위조전송(Forged Transmits)모드설정이거부로설정된경우 |
| **판단기준** | 취약: 가상스위치에위조전송(Forged Transmits)모드설정이허용으로설정된경우 |
| **조치방법** | 위조전송(Forged Transmits)모드거부설정 |

---
## 상세 설명

### 1. 항목 개요

위조 전송(Forged Transmits) 모드는 가상 머신이 자신의 실제 MAC 주소가 아닌 **위조된(Source MAC이 다른) 패킷**을 전송하는 것을 허용하거나 거부하는 보안 설정입니다.

이 정책을 **거부(Reject)**로 설정하면, 가상 머신에서 MAC 주소 스푸핑을 통한 다양한 공격을 차단할 수 있습니다.

### 2. 왜 이 항목이 필요한가요?

**위조 전송의 위험성:**

1. **ARP 스푸핑 공격**
   - 게이트웨이 MAC 주소 위장
   - MITM(Man-in-the-Middle) 공격
   - 트래픽 가로채기

2. **네트워크 혼란**
   - 스위치 MAC 테이블 오염
   - 트래픽 루프 발생
   - 서비스 거부

3. **보안 우회**
   - MAC 필터링 우회
   - NAC(Network Access Control) 우회
   - 무단 접속

**위험 시나리오:**

```
악성 VM → 위조된 MAC 주소로 패킷 전송
→ 게이트웨이 MAC 주소로 위조된 ARP 패킷
→ 타겟 VM이 게이트웨이로 인식
→ 타겟 VM → 악성 VM으로 트래픽 전송
→ MITM 공격 성공
→ 모든 통신 내용 가로채기
→ 자격증명 탈취
→ 데이터 유출
```

### 3. 점검 대상

- VMware ESXi

### 4. 판단 기준

- **양호**: 가상 스위치에 위조 전송(Forged Transmits) 모드 설정이 거부로 설정된 경우
- **취약**: 가상 스위치에 위조 전송(Forged Transmits) 모드 설정이 허용으로 설정된 경우

### 5. 점검 방법

#### VMware ESXi

1. Web 콘솔 접속
   ```
   https://<VMware ESXi IP>
   ```

2. **네트워킹** > **가상 스위치** > [가상 스위치 선택] > **설정 편집** > **보안**로 이동

3. **위조 전송** 정책 확인

**양호 기준:**
- 위조 전송: **거부**

**취약 기준:**
- 위조 전송: **허용**

### 6. 조치 방법

#### VMware ESXi

**1) 가상 스위치 설정 변경**

1. **네트워킹** > **가상 스위치**로 이동

2. 변경할 가상 스위치 선택 > **설정 편집** 클릭

3. **보안** 탭으로 이동

4. **위조 전송** 정책을 **거부**로 변경

5. **저장** 클릭

**2) 분산 스위치(Distributed Switch) 설정**

1. **네트워킹** > **분산 스위치** > [분산 스위치 선택]

2. **설정 편집** > **보안** > **위조 전송**

3. **거부**로 설정

**3) PowerCLI를 이용한 일괄 설정**

```powershell
# 모든 표준 스위치에 Forged Transmits 거부 설정
Get-VirtualSwitch | ForEach-Object {
    $sw = $_
    # Forged Transmits 거부
    $sw | Get-SecurityPolicy | Set-SecurityPolicy `
        -ForgedTransmitsReject $true -Confirm:$false
    Write-Host "Forged Transmits 거부 설정 완료: $($sw.Name)"
}

# 분산 스위치
Get-VDSwitch | ForEach-Object {
    $vds = $_
    $vds | Get-VDSecurityPolicy | Set-VDSecurityPolicy `
        -ForgedTransmitsReject $true -Confirm:$false
    Write-Host "분산 스위치 Forged Transmits 거부 설정 완료: $($vds.Name)"
}
```

### 7. 보안 정책 옵션

| 정책 | 설명 | 권장 대상 |
|------|------|-----------|
| 허용 | 위조 전송 허용 | 취약 |
| 거부 | 위조 전송 거부 | 모든 스위치 (권장) |

### 8. 위조 전송 공격 이해

**공격 유형:**

1. **ARP 스푸핑**
   - 게이트웨이 MAC 위장 패킷 전송
   - 타겟 VM의 트래픽 유도

2. **MAC 스푸핑**
   - 다른 VM의 MAC 주소 위장
   - 권한 획득 시도

3. **IP 스푸핑**
   - 위조된 Source IP 패킷 전송
   - DDoS 공격 도구로 악용

### 9. HV-22, HV-23과의 차이점

| 설정 | 차단 대상 | 공격 유형 |
|------|-----------|----------|
| HV-22 MAC 주소 변경 | VM이 자신의 MAC 변경 | MAC 스푸핑 |
| HV-23 Promiscuous 모드 | 다른 패킷 수신 | 스니핑 |
| HV-24 위조 전송 | 위조된 패킷 전송 | ARP 스푸핑, MITM |

**3가지 설정 모두 적용 시 효과:**
- 자신 MAC 변경 불가 (HV-22)
- 다른 패킷 수신 불가 (HV-23)
- 위조 패킷 전송 불가 (HV-24)

### 10. 예외 사항

**위조 전송이 필요한 경우:**

1. **NLB(Network Load Balancing)**
   - Microsoft NLB 유니캐스트 모드
   - 동일 MAC를 여러 VM이 사용

2. **고가용성 클러스터링**
   - 일부 클러스터 솔루션
   - VIP(Virtual IP) 구성

3. **라우터/방화벽 VM**
   - 여러 네트워크 간 패킷 포워딩
   - L2/L3 가상 어플라이언스

**예외 처리 방법:**
- 해당 포트그룹만 **허용**으로 설정
- **VLAN**으로 분리하여 격리
- 별도의 보안 정책 수립

### 11. 모범 사례

**1) 모든 가상 스위치에 적용**
- 표준 스위치(Standard Switch)
- 분산 스위치(Distributed Switch)
- 모든 포트그룹

**2) 포트그룹 레벨 설정**
- 스위치 레벨: 기본 정책 (거부)
- 포트그룹 레벨: 예외 허용

**3) 정기적 점검**
- 월 1회 이상 전체 스위치 점검
- 신규 스위치 생성 시 즉시 설정

**4) 네트워크 세그먼트 분리**
- NLB/클러스터용 별도 VLAN
- 라우터/방화벽용 격리 네트워크

### 12. 모니터링

**위조 패킷 탐지:**

```bash
# ESXi 호스트 로그
grep "forged" /var/log/vmkernel.log
grep "spoof" /var/log/vmkernel.log

# vCenter 로그
grep "MAC address" /var/log/vmware/vpxd.log
grep "forged" /var/log/vmware/vpxd.log
```

**IDS/IPS 규칙:**
- ARP 스푸핑 탐지 규칙
- MAC 스푸핑 탐지 규칙
- 비정상 MAC 주소 경고

### 13. 주의사항

- 위조 전송 **거부**가 대부분의 네트워크 기능에 영향 없음
- NLB, 클러스터, 라우터 VM은 **예외 허용** 필요
- 변경 후 **네트워크 연결 테스트** 필수
- **HV-22, HV-23**과 함께 적용 권장
- 예외가 필요한 경우 **VLAN 분리** 필수

### 14. 추가 보안 설정

**가상 네트워크 3대 보안 정책 완성:**

```powershell
# 모든 스위치에 3대 보안 정책 적용
Get-VirtualSwitch | ForEach-Object {
    $sw = $_
    $policy = $sw | Get-SecurityPolicy

    # MAC 주소 변경 거부
    $policy | Set-SecurityPolicy -MacChangesReject $true -Confirm:$false

    # Promiscuous 모드 거부
    $policy | Set-SecurityPolicy -AllowPromiscuous $false -Confirm:$false

    # 위조 전송 거부
    $policy | Set-SecurityPolicy -ForgedTransmitsReject $true -Confirm:$false

    Write-Host "가상 스위치 보안 정책 완료: $($sw.Name)"
}
```

## 요약

모든 가상 스위치의 **위조 전송(Forged Transmits) 모드를 거부**로 설정해야 합니다. 이는 **ARP 스푸핑**, **MITM 공격**을 차단하여 네트워크 보안을 강화하는 핵심 설정입니다. **HV-22 MAC 주소 변경 비활성화**, **HV-23 Promiscuous 모드 비활성화**와 함께 적용하면 가상 네트워크의 **3대 주요 보안 정책**을 완성할 수 있습니다. NLB나 클러스터와 같이 **정당한 사유**가 있는 경우, **별도의 포트그룹과 VLAN**으로 격리하여 예외를 허용하세요.
