---
title: "[2026 주요정보통신기반시설] U-43 NIS, NIS+ 점검"
slug: "2026-주정통/U-43"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "안전하지않은NIS서비스의비활성화,안전한NIS+서비스의활성화여부점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-43 NIS, NIS+ 점검

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-43 |
| **점검내용** | 안전하지않은NIS서비스의비활성화,안전한NIS+서비스의활성화여부점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX등 |
| **양호기준** | NIS서비스가비활성화되어있거나,불가피하게사용시NIS+서비스를사용하는경우 |
| **취약기준** | NIS서비스가활성화된경우 |
| **조치방법** | NIS관련서비스비활성화설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: NIS(ypserv) 서비스가 비활성화된 경우
- **취약**: NIS(ypserv) 서비스가 활성화된 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| NIS 서비스 활성화 | 취약 | 평문 패스워드 전송 |
| NIS+ 사용 | 양호 | 보안 강화됨 |
| LDAP/Kerberos 사용 | 양호 | 대안으로 권장 |
| /etc/passwd만 사용 | 양호 | 로컬 인증 |
| securenets 설정됨 | 주의 | IP 제한만으로는 부족 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| Linux | ypserv | disabled (systemctl) | NIS 서버 |
| Linux | ypbind | disabled (systemctl) | NIS 클라이언트 |
| Solaris | network/nis/server | disabled (svcadm) | NIS 서버 |
| Solaris | network/nis/client | disabled (svcadm) | NIS 클라이언트 |
| 대안 | LDAP + TLS | 사용 권장 | 중앙 인증 |

### 2. 점검 방법

#### Linux, Solaris 점검

NIS는 평문으로 패스워드 해시를 전송하므로 보안에 매우 취약합니다. 반드시 비활성화해야 합니다.

```bash
# 1. NIS 서비스 상태 확인
echo "=== 1. NIS Services ==="
systemctl is-active ypserv ypbind yppasswdd 2>/dev/null
systemctl is-enabled ypserv ypbind yppasswdd 2>/dev/null

# 2. 프로세스 확인
echo "=== 2. NIS Processes ==="
ps -ef | grep -E "ypserv|ypbind|rpc.yppasswdd" | grep -v grep

# 3. NIS 도메인 확인
echo "=== 3. NIS Domain ==="
domainname
cat /etc/defaultdomain 2>/dev/null

# 4. 포트 listening 확인
echo "=== 4. NIS Ports ==="
netstat -tuln | grep -E ":(111|635|745)"
```

**양호 출력 예시:**
```text
=== 1. NIS Services ===
ypserv: inactive (dead)
ypbind: inactive (dead)
ypserv: disabled
=== 2. NIS Processes ===
(프로세스 없음)
=== 3. NIS Domain ===
(none)
```

**취약 출력 예시:**
```text
=== 1. NIS Services ===
ypserv: active (running)
ypbind: active (running)
=== 2. NIS Processes ===
root   1234  1  0  Jan20 ?  00:00:00 /usr/sbin/ypserv
=== 3. NIS Domain ===
nis.example.com
```

### 3. 조치 방법

#### Linux 설정

1. **NIS 서비스 중지**
   ```bash
   # 서비스 중지
   systemctl stop ypserv
   systemctl stop ypbind
   systemctl stop yppasswdd
   systemctl stop ypxfrd

   # 부팅 시 비활성화
   systemctl disable ypserv
   systemctl disable ypbind
   systemctl disable yppasswdd
   systemctl disable ypxfrd
   ```

2. **확인**
   ```bash
   systemctl status ypserv
   ```

#### Solaris 설정

1. **NIS 서비스 비활성화**
   ```bash
   svcadm disable network/nis/server
   svcadm disable network/nis/client

   # 상태 확인
   svcs network/nis/server
   svcs network/nis/client
   ```

2. **보안 강화 (불가피 시)**
   ```bash
   # /var/yp/securenets
   echo "255.255.255.0  192.168.1.0" >> /var/yp/securenets
   ```

### 4. 참고 자료

- CIS Benchmark for Solaris: NIS 비활성화 권고
- NIST SP 800-53: SC-12 (암호화 인증)
- LDAP + Kerberos: 중앙 인증 대안
- man pages: ypserv(8), ypbind(8)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.