---
title: "[2026 주요정보통신기반시설] S-13 원격 로그서버 사용"
slug: "2026-주정통/S-13"
date: 2026-02-05T09:56:12+09:00
lastmod: 2026-02-05T09:56:12+09:00
description: "보안장비 원격 로그 설정((r)syslog)이 기관 정책에 맞게 설정되어 있으며 보안장비 로그를 원격 로그 서버에 별도로 보관하도록 설정되어 있는지 점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Security
---

# S-13 원격 로그서버 사용

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | S-13 |
| **점검내용** | 보안장비 원격 로그 설정((r)syslog)이 기관 정책에 맞게 설정되어 있으며 보안장비 로그를 원격 로그 서버에 별도로 보관하도록 설정되어 있는지 점검 |
| **점검대상** | 방화벽, VPN, IDS, IPS, Anti-DDoS, 웹방화벽 등 |
| **양호기준** | 별도의 원격 로그 서버가 구축되어 있고, 원격 로그 서버에 저장될 로그가 기관 정책에 맞게 설정된 경우 |
| **취약기준** | 별도의 원격 로그 서버가 구축되어 있지 않거나, 원격 로그 서버에 저장될 로그가 기관 정책에 맞게 설정되지 않은 경우 |
| **조치방법** | 기관 정책에 맞게 원격 로그 서버에 저장될 로그 설정 후 보안장비 로그 설정 메뉴에서 (r)syslog 설정 또는 주기적으로 별도 저장매체에 백업((r)syslog 미지원 경우) |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준

**양호**
- 별도의 원격 로그 서버가 구축되어 있고, 원격 로그 서버에 저장될 로그가 기관 정책에 맞게 설정된 경우

**취약**
- 별도의 원격 로그 서버가 구축되어 있지 않거나, 원격 로그 서버에 저장될 로그가 기관 정책에 맞게 설정되지 않은 경우

#### 경계 케이스 (Edge Case) 처리 방법

1. **Syslog 미지원 장비**
   - 주기적으로 별도 저장매체에 백업
   - 수동 로그 내보내기 기능 활용

2. **대역폭 제한 환경**
   - 로그 레벨 조정으로 전송량 최적화
   - TCP 프로토콜 사용으로 신뢰성 확보

#### 권장 설정값

- 프로토콜: TCP (신뢰성)
- 포트: 514 (표준 Syslog)
- 전송 형식: RFC 5424 표준

### 2. 점검 방법

**Step 1) 보안 장비 로그 설정 메뉴에서 syslog 설정 확인**

```bash
# Cisco ASA 예시
show logging
# Syslog logging: enabled (facility: 20, timestamp: enabled)
# Logging to 192.168.100.10, TCP/514, enabled

# Web 방화벽 예시
# Log > Configuration > Remote Logging
# Syslog Server: 192.168.100.10
# Protocol: TCP
# Port: 514
# Status: Enable
```

**Step 2) 원격 syslog 로그 수집 서버 설정 확인**

```bash
# Syslog 서버에서 수집 상태 확인
# Linux rsyslog 서버
tail -f /var/log/syslog
# Jan 20 10:15:30 firewall-01 %ASA-6-106100: access-list ...

# 로그 파일 확인
ls -l /var/log/
# -rw-r----- 1 syslog adm 10485760 Jan 20 10:15 syslog
```

### 3. 조치 방법

**Step 1) 원격 Syslog 서버 구축**

먼저 원격 로그 서버를 구축합니다.

**Linux Syslog 서버 구축 (rsyslog):**

```bash
# 1. rsyslog 설치
sudo apt-get install rsyslog  # Ubuntu/Debian
sudo yum install rsyslog       # CentOS/RHEL

# 2. rsyslog 설정
sudo vi /etc/rsyslog.conf

# 모듈 로드
$ModLoad imtcp
$InputTCPServerRun 514

# 템플릿 설정
$template RemoteLogs,"/var/log/remote/%HOSTNAME%/%PROGRAMNAME%.log"
*.* ?RemoteLogs

# 3. 로그 디렉터리 생성
sudo mkdir -p /var/log/remote
sudo chown syslog:syslog /var/log/remote

# 4. 서비스 재시작
sudo systemctl restart rsyslog
sudo systemctl enable rsyslog

# 5. 방화벽 설정
sudo ufw allow 514/tcp  # Ubuntu
sudo firewall-cmd --permanent --add-port=514/tcp  # CentOS
sudo firewall-cmd --reload
```

**Step 2) 보안 장비에서 Syslog 설정**

각 보안 장비에서 원격 Syslog 서버로 로그를 전송하도록 설정합니다.

**방화벽 Syslog 설정 (Cisco ASA):**

```bash
# 1. Syslog 서버 설정
logging host inside 192.168.100.10
logging trap informational
logging facility 20

# 2. 프로토콜 설정 (TCP 권장)
logging host inside 192.168.100.10 6/1514  # TCP/1514

# 3. 로그 레벨 설정
logging buffered informational
logging trap informational

# 4. 로그 전송 확인
show logging
```

**Web 방화벽 Syslog 설정:**

```bash
# Web GUI 설정
# Log > Configuration > Remote Logging > Syslog

# 1. Syslog 서버 추가
- Server IP: 192.168.100.10
- Protocol: TCP (신뢰성)
- Port: 514
- Facility: Local0
- Severity: Informational
- Format: BSD Syslog / RFC5424

# 2. 전송할 로그 유형 선택
- Security Logs: Enable
- System Logs: Enable
- Traffic Logs: Enable
- Admin Logs: Enable

# 3. TLS/SSL 설정 (선택사항)
- Enable TLS: Yes
- CA Certificate: /path/to/ca.crt
```

**Step 3) 로컬에서 별도의 저장매체를 통해 수동으로 로그 백업**

Syslog를 지원하지 않는 경우 수동으로 백업합니다.

```bash
# 1. 정기적으로 로그 다운로드
# System > Maintenance > Log Export
# Export Schedule: Daily
# Export Format: CSV / XML
# Export Location: FTP / SFTP

# 2. 백업 스크립트 예시
#!/bin/bash
DATE=$(date +%Y%m%d)
BACKUP_DIR="/backup/logs"

# SSH를 통한 로그 다운로드
ssh admin@firewall-01 "show logging" > $BACKUP_DIR/firewall-$DATE.log

# FTP를 통한 로그 다운로드
ftp -nv <<EOF
open 192.168.1.1
user admin password
get logs/syslog.log $BACKUP_DIR/firewall-$DATE.log
bye
EOF
```

### 4. 참고 자료

**원격 로그 서버의 장점**
- **로그 무결성 보호**: 원격 서버로 즉시 전송하여 로그 삭제/변조 방지
- **중앙 집중 관리**: 모든 장비의 로그를 한 곳에서 통합 관리
- **저장 공간 확보**: 대용량 스토리지로 장기 보관 가능
- **SIEM 연동**: 보안 정보 및 이벤트 관리 시스템과 연동
- **실시간 모니터링**: 실시간 로그 분석 및 알람

**주의사항**
- 일반적인 경우 영향이 없습니다.
- **TCP 사용**: UDP 대신 TCP를 사용하여 로그 손실 방지 (신뢰성 중요)
- **대역폭 고려**: 로그 전송량이 많을 경우 네트워크 대역폭에 영향
- **저장 공간**: 원격 서버의 충분한 저장 공간 확보
- **로그 포맷**: 기관 정책에 맞는 로그 포맷 설정
- **모니터링**: Syslog 서버 동작 상태 주기적인 확인
- **백업**: 원격 서버 로그도 정기적으로 백업

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.