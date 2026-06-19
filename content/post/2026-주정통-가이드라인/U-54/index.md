---
title: "[2026 주요정보통신기반시설] U-54 암호화되지 않는 FTP 서비스 비활성화"
slug: "2026-주정통/U-54"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "암호화되지않은FTP서비스비활성화여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
draft: true
---

# U-54 암호화되지 않는 FTP 서비스 비활성화

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-54 |
| **점검내용** | 암호화되지않은FTP서비스비활성화여부점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX등 |
| **양호기준** | 암호화되지않은FTP서비스가비활성화된경우 |
| **취약기준** | 암호화되지않은FTP서비스가활성화된경우 |
| **조치방법** | 암호화되지않은FTP서비스중지및비활성화설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: FTP 대신 SFTP/FTPS를 사용하거나 FTP가 비활성화된 경우
- **취약**: 평문 FTP 서비스가 활성화된 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| FTP 활성화 (평문) | 취약 | 암호/데이터 노출 |
| SFTP만 사용 | 양호 | SSH 기반 암호화 |
| FTPS 활성화 | 양호 | TLS/SSL 암호화 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| All | SSH/SFTP | enabled | 내장 암호화 |
| vsftpd | ssl_enable | YES | FTPS |
| ProFTPD | TLSRequired | on | FTPS |

### 2. 점검 방법

#### Linux 점검

```bash
# 1. FTP 서비스 확인
echo "=== 1. FTP Service ==="
systemctl is-active vsftpd proftpd pure-ftpd 2>/dev/null
netstat -tuln | grep :21

# 2. SFTP 확인
echo "=== 2. SFTP ==="
grep "Subsystem sftp" /etc/ssh/sshd_config
```

**양호 출력 예시:**
```text
=== 1. FTP Service ===
vsftpd: inactive (dead)
=== 2: SFTP ===
Subsystem sftp /usr/lib/openssh/sftp-server
```

**취약 출력 예시:**
```text
=== 1. FTP Service ===
vsftpd: active (running)
```

### 3. 조치 방법

#### SFTP 사용 (권장)

```bash
# SSH 내장 SFTP 사용 (별도 설치 불필요)
# /etc/ssh/sshd_config 확인:
Subsystem sftp /usr/lib/openssh/sftp-server

systemctl restart sshd
```

#### FTP 비활성화

```bash
systemctl stop vsftpd
systemctl disable vsftpd
```

### 4. 참고 자료

- CIS Benchmark for Linux: SFTP 권장
- NIST SP 800-53: SC-8 (전송 기밀성)
- RFC 959: FTP, RFC 4254: SFTP

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.