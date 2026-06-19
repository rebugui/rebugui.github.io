---
title: "[2026 주요정보통신기반시설] U-38 DoS 공격에 취약한 서비스 비활성화"
slug: "2026-주정통/U-38"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "사용하지않는DoS공격에취약한서비스의실행여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
draft: true
---

# U-38 DoS 공격에 취약한 서비스 비활성화

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-38 |
| **점검내용** | 사용하지않는DoS공격에취약한서비스의실행여부점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX등 |
| **양호기준** | DoS공격에취약한서비스가비활성화된경우 |
| **취약기준** | DoS공격에취약한서비스가활성화된경우 |
| **조치방법** | echo, discard, daytime, chargen, ntp, dns,snmp등의서비스비활성화설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: echo, discard, daytime, chargen 서비스가 비활성화된 경우
- **취약**: echo, discard, daytime, chargen 서비스 중 하나라도 활성화된 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| 내부 네트워크에서만 서비스 | 주의 | 방화벽에서 외부 차단 필요 |
| NTP monlist 활성화 | 취약 | 최대 556배 증폭 공격 가능 |
| DNS Recursion 허용 | 취약 | 증폭 공격에 악용 가능 |
| chargen 서비스 활성화 | 취약 | 4096배 증폭 가능 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| Linux (xinetd) | echo | disable = yes | /etc/xinetd.d/echo |
| Linux (xinetd) | discard | disable = yes | /etc/xinetd.d/discard |
| Linux (xinetd) | daytime | disable = yes | /etc/xinetd.d/daytime |
| Linux (xinetd) | chargen | disable = yes | /etc/xinetd.d/chargen |
| NTP | monlist | disable monitor | /etc/ntp.conf |
| DNS | Recursion | allow-recursion 제한 | /etc/named.conf |

### 2. 점검 방법

#### Linux 점검

DoS 증폭 공격에 악용될 수 있는 레거시 서비스들과 NTP, DNS 설정을 점검해야 합니다.

```bash
# 1. xinetd 기반 서비스 확인
echo "=== 1. Legacy Services (xinetd) ==="
for svc in echo discard daytime chargen time; do
    if [ -f "/etc/xinetd.d/$svc" ]; then
        echo "--- $svc ---"
        grep -E "disable\s*=" /etc/xinetd.d/$svc
    fi
done

# 2. inetd 기반 서비스 확인
if [ -f /etc/inetd.conf ]; then
    echo "=== 2. /etc/inetd.conf ==="
    grep -E "^(echo|discard|daytime|chargen|time)" /etc/inetd.conf
fi

# 3. 포트 listening 확인
echo "=== 3. Listening Ports ==="
netstat -tuln | grep -E ":(7|9|13|19|37|123|53|161)"

# 4. NTP monlist 확인
echo "=== 4. NTP Monitor ==="
ntpq -c monlist localhost 2>&1 | head -5

# 5. DNS Recursion 확인
echo "=== 5. DNS Recursion ==="
dig @localhost +short version.bind chaos txt
```

**양호 출력 예시:**
```text
=== 1. Legacy Services (xinetd) ===
--- echo ---
disable = yes
--- chargen ---
disable = yes
=== 3. Listening Ports ===
(해당 포트에서 listening하지 않음)
=== 4. NTP Monitor ===
timed out
```

**취약 출력 예시:**
```text
=== 1. Legacy Services (xinetd) ===
--- echo ---
disable = no
=== 3. Listening Ports ===
udp        0      0 0.0.0.0:123            0.0.0.0:*                   536/ntpd
=== 4. NTP Monitor ===
=== 5. DNS Recursion ===
status: NOERROR
```

#### Solaris, AIX, HP-UX 점검

```bash
# inetd.conf 확인
cat /etc/inetd.conf | grep -E "^(echo|discard|daytime|chargen)"

# 서비스 상태 확인
netstat -an | grep -E ":(7|9|13|19)"
```

### 3. 조치 방법

#### Linux (xinetd) 설정

1. **레거시 서비스 비활성화**
   ```bash
   # 서비스 비활성화
   for service in echo discard daytime chargen time; do
       if [ -f "/etc/xinetd.d/$service" ]; then
           sed -i.bak 's/disable = no/disable = yes/' "/etc/xinetd.d/$service"
           echo "Disabled $service"
       fi
   done

   # xinetd 재시작
   systemctl restart xinetd
   ```

2. **inetd 주석 처리**
   ```bash
   # 백업 생성
   cp /etc/inetd.conf /etc/inetd.conf.bak

   # 주석 처리
   sed -i 's/^\(echo\|discard\|daytime\|chargen\|time\)/#\1/' /etc/inetd.conf

   # inetd 재시작
   kill -HUP $(cat /var/run/inetd.pid 2>/dev/null)
   ```

#### NTP monlist 비활성화 (중요!)

1. **NTP 설정 수정**
   ```bash
   # /etc/ntp.conf 또는 /etc/chrony.conf에 추가
   cat >> /etc/ntp.conf << 'EOF'
   # NTP amplification attack prevention
   disable monitor
   restrict default nopeer noquery limited kod
   restrict 127.0.0.1
   EOF

   # 서비스 재시작
   systemctl restart ntpd
   # 또는
   systemctl restart chronyd
   ```

2. **확인**
   ```bash
   ntpq -c monlist localhost
   # "timed out" 또는 "no association ID" 메시지 = 양호
   ```

#### DNS Recursion 제한

1. **DNS 설정 수정**
   ```bash
   # /etc/named.conf 수정 (options 섹션)
   vi /etc/named.conf

   # 추가할 설정:
   allow-recursion { 192.168.1.0/24; localhost; };
   allow-query-cache { 192.168.1.0/24; localhost; };

   # 재시작
   systemctl restart named
   ```

### 4. 참고 자료

- CIS Benchmark for Network Infrastructure: 불필요한 서비스 비활성화
- NIST SP 800-53: SC-5 (DoS 보호)
- US-CERT Alert TA14-017A: NTP Amplification Attacks
- man pages: ntpd(8), named(8), xinetd.conf(5)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.