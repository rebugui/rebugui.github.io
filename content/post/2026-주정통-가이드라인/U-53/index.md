---
title: "[2026 주요정보통신기반시설] U-53 FTP 서비스 정보 노출 제한"
slug: "2026-주정통/U-53"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "FTP서비스정보노출여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-53 FTP 서비스 정보 노출 제한

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-53 |
| **점검내용** | FTP서비스정보노출여부점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX등 |
| **양호기준** | FTP접속배너에노출되는정보가없는경우 |
| **취약기준** | FTP접속배너에노출되는정보가있는경우 |
| **조치방법** | FTP서비스를사용하지않는경우서비스중지및비활성화설정, FTP서비스사용시FTP설정파일을통해접속배너설정 (접속배너에서비스이름이나버전정보를노출하지않는것을권고) |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: FTP 배너에 버전 정보가 없는 경우
- **취약**: FTP 배너에 서버/버전 정보가 노출된 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| "vsFTPd 3.0.3" 표시 | 취약 | 버전 정보 노출 |
| "Welcome" 메시지 | 취약 | 환영 인밍됨 |
| "Secure FTP"만 | 양호 | 정보 최소화 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| vsftpd | ftpd_banner | "Secure FTP" 또는 간단한 메시지 | /etc/vsftpd/vsftpd.conf |
| ProFTPD | ServerIdent | on "Secure FTP" | /etc/proftpd/proftpd.conf |
| Pure-FTPD | DisplayLogin | .banner 파일 | 버전 정보 제외 |

### 2. 점검 방법

#### Linux 점검

FTP 접속 시 배너 정보가 과도하게 노출되지 않도록 해야 합니다.

```bash
# 1. FTP 배너 확인
echo "=== 1. FTP Banner ==="
(echo "QUIT"; sleep 1) | nc localhost 21 2>/dev/null | head -3

# 2. vsftpd 설정 확인
echo "=== 2. vsftpd Banner ==="
grep ftpd_banner /etc/vsftpd/vsftpd.conf 2>/dev/null
grep banner_file /etc/vsftpd/vsftpd.conf 2>/dev/null
```

**양호 출력 예시:**
```text
=== 1. FTP Banner ===
220 Secure FTP Service
```

**취약 출력 예시:**
```text
=== 1. FTP Banner ===
220 (vsFTPd 3.0.3) (Ubuntu)
```

### 3. 조치 방법

#### vsftpd 설정

1. **배너 변경**
   ```bash
   # /etc/vsftpd/vsftpd.conf
   vi /etc/vsftpd/vsftpd.conf

   # 추가/수정:
   ftpd_banner=Secure FTP Service
   # 또는
   banner_file=/etc/vsftpd/banner.txt

   # 배너 파일 생성
   echo "Secure FTP Service. Unauthorized access prohibited." > /etc/vsftpd/banner.txt

   systemctl restart vsftpd
   ```

#### ProFTPD 설정

1. **배너 변경**
   ```bash
   # /etc/proftpd/proftpd.conf
   ServerIdent on "Secure FTP"

   systemctl restart proftpd
   ```

### 4. 참고 자료

- CIS Benchmark for FTP: 배너 정보 최소화 권고
- NIST SP 800-53: AC-17 (공격 완화)
- RFC 959: FTP 사양
- man pages: vsftpd.conf(5), proftpd.conf(5)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.