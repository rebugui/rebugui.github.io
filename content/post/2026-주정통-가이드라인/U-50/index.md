---
title: "[2026 주요정보통신기반시설] U-50 DNS Zone Transfer 설정"
slug: "2026-주정통/U-50"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "Secondary NameServer로만Zone정보전송제한여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
draft: true
---

# U-50 DNS Zone Transfer 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-50 |
| **점검내용** | Secondary NameServer로만Zone정보전송제한여부점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX등 |
| **양호기준** | ZoneTransfer를허가된사용자에게만허용한경우 |
| **취약기준** | Zone Transfer를모든사용자에게허용한경우 |
| **조치방법** | DNS서비스를사용하지않는경우서비스중지및비활성화설정, DNS서비스사용시DNSZoneTransfer를허가된사용자에게만전송허용하도록설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: allow-transfer에 신뢰된 보조 DNS만 지정된 경우
- **취약**: allow-transfer가 ANY 또는 설정되지 않은 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| allow-transfer { any; } | 취약 | 모두에게 전송 허용 |
| allow-transfer { none; } | 양호 | 완전 차단 |
| allow-transfer { slave-ips; } | 양호 | 보조 서버만 |
| 보조 서버 없음 | 양호 | none 권장 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| BIND | allow-transfer | none 또는 slave-ips | /etc/named.conf |
| BIND | allow-query-cache | 내부 대역만 | 캐시 포이징 방지 |

### 2. 점검 방법

#### Linux 점검

DNS Zone Transfer가 무단으로 전송되지 않도록 제한해야 합니다.

```bash
# 1. named.conf 설정 확인
echo "=== 1. Zone Transfer Settings ==="
grep -A 2 "zone.*{" /etc/named.conf | grep allow-transfer
grep allow-transfer /etc/named.conf

# 2. AXFR 테스트
echo "=== 2. AXFR Test ==="
dig @localhost example.com axfr
```

**양호 출력 예시:**
```text
=== 1. Zone Transfer Settings ===
allow-transfer { "slave-servers"; };
allow-transfer { none; };
=== 2. AXFR Test ===
; Transfer failed
```

**취약 출력 예시:**
```text
=== 2. AXFR Test ===
; AXFR started
example.com.  3600 IN A 192.168.1.10
```

### 3. 조치 방법

#### BIND 설정

1. **allow-transfer 설정**
   ```bash
   # /etc/named.conf 수정
   vi /etc/named.conf

   # ACL 정의:
   acl "slave-servers" {
       192.168.1.2;
       192.168.1.3;
   };

   # options 또는 zone 섹션:
   options {
       allow-transfer { "slave-servers"; };
   };

   # 또는 보조 서버가 없는 경우:
   options {
       allow-transfer { none; };
   };

   systemctl reload named
   ```

### 4. 참고 자료

- CIS Benchmark for DNS: Zone Transfer 제한 권고
- NIST SP 800-53: AC-4 (정보 흐름 제한)
- RFC 5936: AXFR 사양
- man pages: named.conf(5)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.