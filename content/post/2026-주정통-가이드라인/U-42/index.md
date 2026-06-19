---
title: "[2026 주요정보통신기반시설] U-42 불필요한 RPC 서비스 비활성화"
slug: "2026-주정통/U-42"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "불필요한RPC서비스의실행여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
draft: true
---

# U-42 불필요한 RPC 서비스 비활성화

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-42 |
| **점검내용** | 불필요한RPC서비스의실행여부점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX등 |
| **양호기준** | 불필요한RPC서비스가비활성화된경우 |
| **취약기준** | 불필요한RPC서비스가활성화된경우 |
| **조치방법** | 불필요한RPC서비스중지및비활성화설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 불필요한 RPC 서비스(rusersd, sprayd, walld 등)가 비활성화된 경우
- **취약**: 불필요한 RPC 서비스가 활성화된 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| rpcbind만 활성화 | 양호 | NFS/NIS 사용 시 필요 |
| rusersd 활성화 | 취약 | 사용자 정보 노출 |
| sadmind 활성화 | 취약 | root 권한 취약점 |
| walld 활성화 | 취약 | 메시지 전송 악용 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| Solaris | network/rpc/rusers | disabled (svcadm) | 사용자 정보 |
| Solaris | network/rpc/spray | disabled (svcadm) | DoS 도구 |
| Solaris | network/rpc/wall | disabled (svcadm) | wall 서비스 |
| Solaris | network/rpc/sadmind | disabled (svcadm) | 관리 데몬 |

### 2. 점검 방법

#### Solaris 점검

불필요한 RPC 서비스들은 심각한 보안 취약점을 가지고 있으므로 반드시 비활성화해야 합니다.

```bash
# 1. RPC 서비스 목록 확인
echo "=== 1. RPC Services ==="
rpcinfo -p localhost

# 2. SMF 서비스 상태 확인
echo "=== 2. SMF RPC Services ==="
svcs -a | grep -E "rpc|network"

# 3. 특정 서비스 확인
echo "=== 3. Specific RPC Services ==="
svcs network/rpc/rusers 2>/dev/null
svcs network/rpc/spray 2>/dev/null
svcs network/rpc/wall 2>/dev/null
svcs network/rpc/sadmind 2>/dev/null
```

**양호 출력 예시:**
```text
=== 2. SMF RPC Services ===
disabled  12:34:56 svc:/network/rpc/rusers:default
disabled  12:34:56 svc:/network/rpc/spray:default
=== 3. Specific RPC Services ===
svcs: Pattern 'network/rpc/rusers' doesn't match any instances
```

**취약 출력 예시:**
```text
=== 2. SMF RPC Services ===
online    12:34:56 svc:/network/rpc/rusers:default
online    12:34:56 svc:/network/rpc/spray:default
```

### 3. 조치 방법

#### Solaris (SMF) 설정

1. **RPC 서비스 비활성화**
   ```bash
   # 불필요한 RPC 서비스 중지
   svcadm disable network/rpc/rusers
   svcadm disable network/rpc/spray
   svcadm disable network/rpc/wall
   svcadm disable network/rpc/sadmind
   svcadm disable network/rpc/rstat
   svcadm disable network/rpc/ttdbserverd
   svcadm disable network/rpc/cmsd
   ```

2. **확인**
   ```bash
   svcs network/rpc/rusers
   svcs network/rpc/spray
   ```

#### Linux (xinetd) 설정

1. **xinetd 기반 RPC 서비스 비활성화**
   ```bash
   for svc in rusers rstat spray; do
       if [ -f "/etc/xinetd.d/$svc" ]; then
           sed -i.bak 's/disable = no/disable = yes/' "/etc/xinetd.d/$svc"
       fi
   done

   systemctl restart xinetd
   ```

### 4. 참고 자료

- CIS Benchmark for Solaris: RPC 서비스 비활성화 권고
- NIST SP 800-53: CM-7 (시스템 최소화)
- CVE-2019-1573: automountd 권한 상승 취약점
- man pages: rpcinfo(8), svcadm(1M)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.