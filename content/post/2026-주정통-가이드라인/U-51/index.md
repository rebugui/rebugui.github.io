---
title: "[2026 주요정보통신기반시설] U-51 DNS 서비스의 취약한 동적 업데이트 설정 금지"
slug: "2026-주정통/U-51"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "DNS서비스의취약한동적업데이트설정여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-51 DNS 서비스의 취약한 동적 업데이트 설정 금지

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-51 |
| **점검내용** | DNS서비스의취약한동적업데이트설정여부점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX등 |
| **양호기준** | DNS서비스의동적업데이트기능이비활성화되었거나,활성화시적절한접근통제를수행하고 있는경우 |
| **취약기준** | DNS서비스의동적업데이트기능이활성화중이며적절한접근통제를수행하고있지않은경우 |
| **조치방법** | DNS서비스를사용하지않는경우서비스중지및비활성화설정, DNS서비스사용시일반적으로동적업데이트기능이필요없으나확인필요함 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: allow-update가 { none; } 또는 TSIG 키로 보호된 경우
- **취약**: allow-update가 { any; } 또는 IP 기반만 설정된 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| allow-update { any; } | 취약 | 누구나 레코드 수정 가능 |
| allow-update { none; } | 양호 | 동적 업데이트 차단 |
| TSIG 키 사용 | 양호 | 암호화된 인증 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| BIND | allow-update | none | /etc/named.conf |
| BIND (DDNS) | allow-update | key "ddns-key" | TSIG 인증 |
| DHCP-DDNS | GSS-TSIG | Kerberos 사용 | AD 통합 시 |

### 2. 점검 방법

#### Linux 점검

DNS 동적 업데이트 기능이 무단 레코드 수정에 악용되지 않도록 제한해야 합니다.

```bash
# 1. named.conf 설정 확인
echo "=== 1. Dynamic Update Settings ==="
grep allow-update /etc/named.conf
grep -A 5 "zone.*{" /etc/named.conf | grep update
```

**양호 출력 예시:**
```text
=== 1. Dynamic Update Settings ===
allow-update { none; };
```

**취약 출력 예시:**
```text
=== 1. Dynamic Update Settings ===
allow-update { any; };
```

### 3. 조치 방법

#### BIND 설정

1. **동적 업데이트 비활성화**
   ```bash
   # /etc/named.conf
   vi /etc/named.conf

   zone "example.com" {
       type master;
       file "example.com.zone";
       allow-update { none; };  # 비활성화
   };

   systemctl reload named
   ```

2. **TSIG 사용 시 (필요한 경우)**
   ```bash
   # 키 생성
   dnssec-keygen -a HMAC-SHA256 -b 256 -n HOST ddns-key

   # /etc/named.conf
   key "ddns-key" {
       algorithm hmac-sha256;
       secret "BASE64KEY";
   };

   allow-update { key "ddns-key"; };
   ```

### 4. 참고 자료

- CIS Benchmark for DNS: 동적 업데이트 제한 권고
- NIST SP 800-53: SC-8 (전송 기밀성)
- RFC 2845: TSIG 사양
- RFC 3007: DDNS 사양

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.