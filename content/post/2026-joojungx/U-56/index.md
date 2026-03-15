---
title: "[2026 주요정보통신기반시설] U-56 FTP 서비스 접근 제어 설정"
slug: "2026-주정통/U-56"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "FTP서비스에비인가자의접근가능여부점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-56 FTP 서비스 접근 제어 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-56 |
| **점검내용** | FTP서비스에비인가자의접근가능여부점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX등 |
| **양호기준** | 특정IP주소또는호스트에서만FTP서버에접속할수있도록접근제어설정을적용한경우 |
| **취약기준** | FTP서버에접근제어설정을적용하지않은경우 |
| **조치방법** | FTP서비스를사용하지않는경우서비스중지및비활성화설정, FTP서비스사용시접근제어설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: TCP Wrapper나 방화벽으로 IP 기반 접근 제어가 설정된 경우
- **취약**: 모든 IP에서 FTP 접속이 가능한 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| 전체 접속 허용 | 취약 | 누구나 접속 가능 |
| 내부 대역만 허용 | 양호 | IP 제한 |
| TCP wrappers 설정 | 양호 | hosts.allow/deny |
| 방화벽 규칙 | 양호 | iptables/firewalld |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| TCP Wrappers | /etc/hosts.allow | vsftpd: 내부IP | 접근 제어 |
| vsftpd | tcp_wrappers | YES | 설정 활성화 |

### 2. 점검 방법

#### Linux 점검

```bash
# 1. hosts.allow/deny 확인
echo "=== 1. TCP Wrappers ==="
cat /etc/hosts.allow | grep -E "(ftp|vsftpd)"
cat /etc/hosts.deny | grep -E "(ftp|vsftpd)"

# 2. vsftpd 설정 확인
echo "=== 2. vsftpd TCP Wrappers ==="
grep tcp_wrappers /etc/vsftpd/vsftpd.conf

# 3. 방화벽 확인
echo "=== 3. Firewall ==="
iptables -L -n | grep 21 2>/dev/null
firewall-cmd --list-all 2>/dev/null | grep ftp
```

**양호 출력 예시:**
```text
=== 1. TCP Wrappers ===
vsftpd: 192.168.1.0/24
=== 2: vsftpd TCP Wrappers ===
tcp_wrappers=YES
```

**취약 출력 예시:**
```text
=== 1. TCP Wrappers ===
(FTP 관련 설정 없음)
```

### 3. 조치 방법

#### TCP Wrappers 설정

```bash
# /etc/hosts.allow
echo "vsftpd: 192.168.1.0/24" >> /etc/hosts.allow
echo "vsftpd: 127.0.0.1" >> /etc/hosts.allow

# /etc/hosts.deny
echo "vsftpd: ALL" >> /etc/hosts.deny

# vsftpd 설정
vi /etc/vsftpd/vsftpd.conf
# tcp_wrappers=YES 추가

systemctl restart vsftpd
```

### 4. 참고 자료

- CIS Benchmark for Linux: FTP 접근 제어 권고
- NIST SP 800-53: AC-3 (접근 제어 정책)
- TCP Wrappers: hosts_access(5)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.