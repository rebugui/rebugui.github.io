---
title: "[2026 주요정보통신기반시설] U-64 주기적 보안 패치 및 벤더 권고 사항 적용"
slug: "2026-주정통/U-64"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "시스템에서 최신 패치 적용 여부 점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
draft: true
---

# U-64 주기적 보안 패치 및 벤더 권고 사항 적용

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-64 |
| **점검내용** | 시스템에서 최신 패치 적용 여부 점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX 등 |
| **양호기준** | 패치 적용 정책을 수립하여 주기적으로 패치 관리를 하고 있으며, 패치 관련 내용을 확인하고 적용하였을 경우 |
| **취약기준** | 패치 관리 정책이 수립되어 있지 않거나 최신 패치를 적용하지 않은 경우 |
| **조치방법** | OS 관리자, 서비스 개발자가 패치 적용에 따른 서비스 영향 정도를 파악하여 OS 관리자 및 벤더에서 적용하도록 설정 (OS 패치의 경우 지속해서 취약점이 발표되고 있으므로 O/S 관리자, 서비스 개발자가 패치 적용에 따른 서비스 영향 정도를 정확히 파악하여 주기적인 패치 적용 정책을 수립하여 적용해야 함) |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 최신 보안 패치가 주기적으로 확인되고 적용되어 있으며, 패치 관리 정책이 수립된 경우
- **취약**: 오랜 기간 패치가 적용되지 않아 다수의 보안 업데이트가 누락된 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| 최근 30일 이내 패치 적용 | 양호 | 정기 관리 중 |
| 6개월 이상 패치 미적용 | 취약 | 보안 위험 |
| Critical 패치만 누락 | 취약 | 높은 위험 |
| EOL OS 사용 | 취약 | 패치 제공 중단 |
| 패치 정책 수립됨 | 양호 | 프로세스 존재 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| Linux | 패치 주기 | 월 1회 이상 | Critical은 즉시 |
| Linux | 테스트 후 적용 | Staging → Production | 호환성 확인 |
| RHEL/CentOS | yum update --security | 보안 패치만 | 또는 전체 업데이트 |
| Ubuntu | unattended-upgrades | 자동 보안 패치 | 설정 필요 |

### 2. 점검 방법

#### Linux 점검

운영체제(OS) 및 설치된 소프트웨어의 보안 취약점을 해결하기 위해 벤더사가 배포하는 보안 패치 적용 여부를 확인해야 합니다.

```bash
# 1. RHEL/CentOS - 업데이트 가능한 패키지 확인
echo "=== 1. RHEL/CentOS Updates ==="
yum check-update --security
# 또는 전체 업데이트 확인
yum check-update

# 2. Ubuntu/Debian - 업데이트 확인
echo "=== 2. Ubuntu/Debian Updates ==="
apt list --upgradable
apt update && apt list --upgradable

# 3. 마지막 업데이트 확인 (RPM 기반)
echo "=== 3. Last Update ==="
rpm -qa --last | head -20

# 4. 커널 버전 확인
echo "=== 4. Kernel Version ==="
uname -r
```

**양호 출력 예시:**
```text
=== 1. RHEL/CentOS Updates ===
(업데이트 가능한 패키지 없음)
=== 3. Last Update ===
kernel-core-5.14.0-284.el9.x86_64                    Mon Jan 20 10:00 2026
```

**취약 출력 예시:**
```text
=== 1. RHEL/CentOS Updates ===
kernel.x86_64                    5.14.0-162.el9         updates
openssh.x86_64                   8.0p1-10.el9_2         updates
(다수의 보안 업데이트 누락)
=== 3. Last Update ===
kernel-core-5.14.0-162.el9.x86_64                    Tue Jul 15 10:00 2025
(6개월 이상 경과)
```

### 3. 조치 방법

#### 패치 적용 절차

1. **백업 수행** (중요!)
   ```bash
   # 커널 업데이트 등 중요한 패치 전에는 시스템 백업 권장
   # 전체 시스템 백업 또는 스냅샷 생성
   ```

2. **RHEL / CentOS 패치**
   ```bash
   # 보안 관련 업데이트만 적용
   yum update --security

   # 또는 전체 업데이트
   yum update

   # 특정 패키지만 업데이트
   yum update openssl bash openssh
   ```

3. **Ubuntu / Debian 패치**
   ```bash
   # 패키지 목록 업데이트
   apt update

   # 업그레이드 가능한 패키지 확인
   apt list --upgradable

   # 업그레이드 적용
   apt upgrade

   # 또는 보안 패치만 자동화 (unattended-upgrades)
   apt install unattended-upgrades
   dpkg-reconfigure -plow unattended-upgrades
   ```

4. **재부팅** (필요 시)
   ```bash
   # 커널이나 glibc 등 핵심 라이브러리 패치 후 재부팅
   reboot

   # 또는
   shutdown -r now
   ```

5. **패치 정책 수립 예시**
   - **Critical 보안 패치**: 7일 이내 적용
   - **Important 보안 패치**: 30일 이내 적용
   - **일반 업데이트**: 월 1회 정기 점검 후 적용
   - **테스트 환경 검증**: 운영 환경 적용 전 Staging 서버에서 테스트

### 4. 참고 자료

- CIS Benchmark for Linux: 패치 관리 권고
- NIST SP 800-53: SI-2 (취약점 보완), RM-6 (보안 업데이트 설치)
- 벤더 보안 권고: Red Hat SA, Ubuntu USN, CVE 데이터베이스

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.