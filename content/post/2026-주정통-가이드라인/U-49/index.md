---
title: "[2026 주요정보통신기반시설] U-49 DNS 보안 버전 패치"
slug: "2026-주정통/U-49"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "BIND최신버전사용유무및주기적보안패치여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
draft: true
---

# U-49 DNS 보안 버전 패치

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-49 |
| **점검내용** | BIND최신버전사용유무및주기적보안패치여부점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX등 |
| **양호기준** | 주기적으로패치를관리하는경우 |
| **취약기준** | 주기적으로패치를관리하고있지않은경우 |
| **조치방법** | DNS서비스를사용하지않는경우서비스중지및비활성화설정, DNS서비스사용시패치관리정책수립및주기적으로패치적용설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: BIND 버전이 최신 보안 패치가 적용된 경우
- **취약**: BIND 버전이 구버전이거나 알려진 취약점이 있는 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| BIND 9.18+ | 양호 | 최신 안정 버전 |
| BIND 9.11 이하 | 취약 | 보안 업데이트 중단 |
| DNSSEC 사용 | 양호 | 추가 보안 계층 |
| 버전 정보 노출 | 주의 | 정보 유출 위험 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| BIND | version 옵션 | "Unknown" 또는 숨김 | /etc/named.conf |
| BIND | 버전 | 최신 안정 버전 | 보안 패치 |
| All DNS | Recursion | 제한 설정 | 증폭 공격 방지 |

### 2. 점검 방법

#### Linux 점검

DNS 서버의 BIND 버전을 확인하고 최신 보안 패치가 적용되었는지 점검해야 합니다.

```bash
# 1. BIND 버전 확인
echo "=== 1. BIND Version ==="
named -v 2>/dev/null
dig @localhost version.bind chaos txt

# 2. 포트 listening 확인
echo "=== 2. DNS Port ==="
netstat -tuln | grep :53
```

**양호 출력 예시:**
```text
=== 1. BIND Version ===
BIND 9.18.19
=== 2. DNS Port ===
tcp        0      0 192.168.1.10:53        0.0.0.0:*                   LISTEN
```

**취약 출력 예시:**
```text
=== 1. BIND Version ===
BIND 9.11.4-P2
```

### 3. 조치 방법

#### 패치 적용

1. **RHEL/CentOS**
   ```bash
   yum update bind
   ```

2. **Ubuntu/Debian**
   ```bash
   apt update && apt upgrade bind9
   ```

#### 버전 숨김

1. **named.conf 설정**
   ```bash
   # /etc/named.conf
   vi /etc/named.conf

   # options 섹션에 추가:
   options {
       version "Unknown";
   };

   systemctl restart named
   ```

### 4. 참고 자료

- CIS Benchmark for DNS: BIND 보안 권고
- NIST SP 800-53: SI-2 (취약점 보완)
- ISC BIND Security: CVE 정보
- RFC 4035: DNSSEC 사양

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.