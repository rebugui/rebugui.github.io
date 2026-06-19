---
title: "[2026 주요정보통신기반시설] HV-25 주기적 보안 패치 및 벤더 권고사항 적용"
slug: "2026-주정통/HV-25"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "가상화장비및관리서버들에대해주기적인보안패치와벤더권고사항적용여부를확인"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Virtualization
draft: true
---

# HV-25 주기적 보안 패치 및 벤더 권고사항 적용

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | HV-25 |
| **점검내용** | 가상화장비및관리서버들에대해주기적인보안패치와벤더권고사항적용여부를확인 |
| **점검대상** | 공통 |
| **판단기준** | 양호: 패치절차를수립하여주기적으로패치및벤더권고사항을확인및적용하는경우 |
| **판단기준** | 취약: 패치절차가수립되어있지않거나주기적으로패치를설치하지않는경우 |
| **조치방법** | 장비별제공하는최신취약점정보를파악후최신패치및업그레이드를수행 |

---
## 상세 설명

### 1. 항목 개요

주기적 보안 패치 및 벤더 권고사항 적용은 가상화 장비와 관리 서버에 알려진 취약점을 해결하고 보안 기능을 강화하기 위해 정기적으로 패치를 설치하고 벤더의 보안 권고사항을 따르는 프로세스입니다.

가상화 환경은 물리적 서버보다 더 복잡하고, 단일 취약점으로 전체 가상화 인프라가 침해될 수 있어 패치 관리가 특히 중요합니다.

### 2. 왜 이 항목이 필요한가요?

**패치 관리의 중요성:**

1. **알려진 취약점 제거**
   - CVE(Common Vulnerabilities and Exposures) 해결
   - 제로데이(Zero-day) 공격 방지
   - 익스플로잇 키트(Exploit Kit) 차단

2. **보안 기능 강화**
   - 새로운 보안 기능 추가
   - 보안 정책 강화
   - 규정 준수

3. **안정성 향상**
   - 버그 수정
   - 성능 개선
   - 호환성 문제 해결

**위험 시나리오:**

```
CVE-2021-21972 (vSphere Client RCE) 발표
→ 관리자가 패치 미적용
→ 해커가 CVE-2021-21972 익스플로잇 사용
→ vCenter 서버 장악
→ 모든 ESXi 호스트 제어권 탈취
→ 전체 가상 머전 암호화/삭제
→ 비즈니스 연중 중단
```

**실제 사례:**
- **CVE-2021-21972**: vSphere Client 원격 코드 실행 취약점 (CVSS 9.8)
- **CVE-2020-3992**: ESXi OpenSLP as-heap-overflow-remote-code-execution (CVSS 9.8)
- **VENOM**: FLOPPY 드라이버 버퍼 오버플로우 (CVE-2015-3456)

### 3. 점검 대상

- **공통** (모든 가상화 장비)
  - VMware ESXi
  - VMware vCenter
  - Citrix XenServer
  - KVM (RHEL, CentOS, Ubuntu 등)
  - Nutanix AHV

### 4. 판단 기준

- **양호**: 패치 절차를 수립하여 주기적으로 패치 및 벤더 권고사항을 확인 및 적용하는 경우
- **취약**: 패치 절차가 수립되어 있지 않거나 주기적으로 패치를 설치하지 않는 경우

### 5. 점검 방법

#### 1) 패치 절차 확인

- 보안 패치 정책 문서 존재 여부
- 패치 절차 수립 여부
- 패치 주기 설정 여부

#### 2) 패치 적용 현황 확인

**VMware ESXi:**
```bash
# ESXi 버전 확인
esxcli system version get

# 설치된 VIB 확인
esxcli software vib list

# 패치 레벨 확인
esxcli software profile get
```

**VMware vCenter:**
```bash
# vCenter 버전 확인
vcenterserver --version

# 또는 vSphere Client에서 확인
```

**KVM:**
```bash
# 커널 버전 확인
uname -r

# 설치된 패키지 확인
rpm -qa | grep kernel
yum list installed kernel
```

**Nutanix:**
```bash
# AHV 버전 확인
ncli cluster info | grep Version

# 또는 웹 콘솔에서 확인
```

#### 3) 보안 권고사항 구독 확인

- 벤더 보안 공지 메일링 리스트 가입 여부
- RSS 피드 구독 여부
- 보안 포털 접속 권한 확인

### 6. 조치 방법

#### 1) 패치 절차 수립

**패치 관리 프로세스:**

```
1. 취약점 식별 → 2. 패치 테스트 → 3. 유지보수 계획 → 4. 패치 적용 → 5. 검증
```

**상세 절차:**

**1단계: 취약점 식별**
- 벤더 보안 공지 확인
- CVE 데이터베이스 검색
- 내부 시스템 스캔

**2단계: 패치 테스트**
- 개발/테스트 환경에서 패치 적용
- 기능 테스트 수행
- 성능 영향 평가

**3단계: 유지보수 계획**
- 유지보수 시간대 설정
- 백업 생성
- 롤백 계획 수립

**4단계: 패치 적용**
- 순차적 패치 적용
- 모니터링 강화
- 문제 발생 시 즉시 대응

**5단계: 검증**
- 시스템 정상 동작 확인
- 보안 취약점 해결 확인
- 문서화

#### 2) 주기적 패치 일정

**권장 패치 주기:**

| 유형 | 주기 | 설명 |
|------|------|------|
| 보안 패치 | 즉시 ~ 30일 | 심각한 취약점(CVSS 9.0+)은 즉시, 그 외 30일 이내 |
| 범용 패치 | 분기별 | 버그 수정, 기능 개선 |
| 기능 업데이트 | 반기별 | 새로운 기능, 성능 개선 |
| 버전 업그레이드 | 연간 | 메이저 버전 업그레이드 |

#### 3) 보안 권고사항 정보源

**VMware ESXi, vCenter:**
- 웹사이트: https://support.broadcom.com/web/ecx/security-advisory
- RSS: https://www.vmware.com/security/advisories.html
- 이메일 알림: 구독 신청

**XenServer:**
- 웹사이트: https://support.citrix.com/support-home/home
- 보안 공지: https://xenbits.xen.org/xsa

**KVM (Red Hat):**
- 웹사이트: https://access.redhat.com/security/
- CVE 데이터베이스: https://access.redhat.com/security/cve/

**Nutanix:**
- 웹사이트: https://www.nutanix.com/trust/security-advisories
- 보안 포털: https://portal.nutanix.com/

#### 4) 패치 적용 가이드

**VMware ESXi:**

1. VUM(vCenter Update Manager) 사용
2. ESXi 호스트를 Maintenance Mode로 전환
3. 패치 적용
4. 호스트 재부팅
5. VM 마이그레이션 복귀

**VMware vCenter:**

1. vCenter Appliance Update 사용
2. 스냅샷 생성 (백업)
3. 패치 적용
4. 서비스 재시작
5. 기능 검증

**KVM:**

```bash
# 1. 시스템 업데이트
yum update kernel
# 또는
yum update

# 2. 시스템 재부팅
reboot

# 3. 버전 확인
uname -r
```

**Nutanix:**

1. 웹 콘솔 접속
2. **Settings** > **Upgrade Software**
3. AOS 및 Hypervisor 업그레이드
4. One-Click Upgrade 또는 롤링 업그레이드

### 7. 패치 관리 모범 사례

**1) 패치 정책 수립**
- 문서화된 패치 절차
- 승인 프로세스
- 긴급 패치 절차

**2) 테스트 환경 활용**
- 운영과 동일한 테스트 환경
- 모든 패치 사전 테스트
- 롤백 절차 검증

**3) 롤링 업데이트**
- 클러스터 환경에서 순차적 패치
- 서비스 중단 최소화
- 무중단 업데이트

**4) 자동화**
- 패치 관리 도구 활용
- 안드의(orcha) 스케줄링
- 자동화된 스캔 및 보고

### 8. 주요 CVE 사례

**최근 심각한 취약점:**

| CVE | 연도 | 영향 제품 | CVSS | 설명 |
|-----|------|-----------|-------|------|
| CVE-2021-21972 | 2021 | vCenter Server | 9.8 | 원격 코드 실행 |
| CVE-2020-3992 | 2020 | ESXi | 9.8 | OpenSLP RCE |
| CVE-2020-3952 | 2020 | ESXi | 7.5 | USB arbitrator 취약점 |
| CVE-2015-3456 | 2015 | FLOPPY 드라이버 | 7.5 | VENOM 취약점 |

**조치 시간:**

| 심각도 | 권장 조치 시간 |
|--------|--------------|
| Critical (CVSS 9.0~10.0) | 48시간 ~ 7일 |
| High (CVSS 7.0~8.9) | 30일 이내 |
| Medium (CVSS 4.0~6.9) | 다음 정기 유지보수 시 |
| Low (CVSS 0.1~3.9) | 다음 버전 업그레이드 시 |

### 9. 패치 전 준비 체크리스트

**사전 준비:**
- [ ] 패치 공지 내용 검토
- [ ] 영향 받는 시스템 파악
- [ ] 테스트 환경에서 패치 테스트 완료
- [ ] 백업 생성
- [ ] 롤백 계획 수립
- [ ] 유지보수 시간대 사용자 통보
- [ ] 롤백 절차 문서화

**패치 적용:**
- [ ] 사전 점검(사전 점검표 실행)
- [ ] 패치 적용
- [ ] 시스템 재부팅
- [ ] 기능 테스트
- [ ] 성능 모니터링

**사후 검증:**
- [ ] 정상 동작 확인
- [ ] 취약점 해결 확인 (스캔)
- [ ] 문서화 및 보고
- [ ] 이해관계자 통보

### 10. 패치 관리 도구

**VMware:**
- vCenter Update Manager (VUM)
- vSphere Lifecycle Manager (LCM)
- VMware Skyline (예측적 분석)

**Red Hat/KVM:**
- Red Hat Satellite
- Red Hat Insights
- yum update

**Nutanix:**
- Prism Element Upgrade
- Lifecycle Manager
- One-Click Upgrade

**자동화 도구:**
- Ansible
- Puppet
- Chef
- Terraform

### 11. 모니터링 및 보고

**패치 준수성 모니터링:**

```powershell
# PowerCLI로 ESXi 버전 확인
Get-VMHost | Select-Object Name, Version, Build

# vCenter 버전 확인
Get-View ServiceInstance | Select-Object Content.AboutVersion
```

**보고서 항목:**
- 전체 시스템 대비 패치 적용률
- 심각한 취약점 미해결 현황
- 다음 패치 일정
- 최근 패치 적용 현황

### 12. 주의사항

- **반드시 백업 후 패치** 적용
- **테스트 환경에서 사전 검증** 필수
- **중요 시스템은 비수기에** 패치 권장
- **롤백 계획** 필수 수립
- **서비스 중단 시간** 고려
- **VM 마이그레이션**으로 중단 최소화
- **벤더사와 협의** 후 대규모 패치

## 요약

모든 가상화 장비는 **주기적 보안 패치 절차**를 수립하고, **벤더 권고사항을 정기적으로 확인**하여 적용해야 합니다. **심각한 취약점(CVSS 9.0+)**은 **즉시 또는 7일 이내**에 패치를 적용하고, 그 외 취약점은 **30일 이내**에 해결하는 것을 권장합니다. **테스트 환경에서 사전 검증**하고 **백업과 롤백 계획**을 수립한 후 패치를 적용하세요. VMware vCenter Lifecycle Manager, Red Hat Satellite, Nutanix Lifecycle Manager와 같은 **자동화된 도구**를 활용하여 효율적으로 패치를 관리하세요.
