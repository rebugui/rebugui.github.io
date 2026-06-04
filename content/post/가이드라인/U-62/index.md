---
title: "[2026 주요정보통신기반시설] U-62 로그인 시 경고 메시지 설정"
slug: "2026-주정통/U-62"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "서버 및 서비스에 로그온 시 불필요한 정보 차단 설정 및 불법적인 사용에 대한 경고 메시지 출력 여부 점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-62 로그인 시 경고 메시지 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-62 |
| **점검내용** | 서버 및 서비스에 로그온 시 불필요한 정보 차단 설정 및 불법적인 사용에 대한 경고 메시지 출력 여부 점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX 등 |
| **양호기준** | 로그온 시 경고 메시지가 출력되도록 설정된 경우 |
| **취약기준** | 로그온 시 경고 메시지가 출력되도록 설정되어 있지 않은 경우 |
| **조치방법** | 로그온 시 경고 메시지가 출력되도록 설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: /etc/issue.net, /etc/motd에 보안 경고 메시지가 설정되어 있고, OS 버전 정보가 노출되지 않는 경우
- **취약**: 배너 파일이 없거나, 서버 버전 정보 등 불필요한 내용만 있거나, 경고 메시지가 없는 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| "Welcome" 메시지 포함 | 취약 | 법적 초대 의미로 해석됨 |
| OS 버전 정보 노출 (\r, \m) | 취약 | 정보 유출 |
| 법적 경고 문구 포함 | 양호 | 무단 접속 경고 |
| SSH Banner 설정됨 | 양호 | /etc/ssh/sshd_config |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| Linux | /etc/issue.net | 경고 메시지 | Telnet/SSH 배너 |
| Linux | /etc/motd | 경고 메시지 | 로그인 후 메시지 |
| SSH | Banner | /etc/issue.net | /etc/ssh/sshd_config |
| FTP | ftpd_banner | 버전 정보 제외 | 배너 설정 |

### 2. 점검 방법

#### Linux, Solaris, AIX, HP-UX 점검

로그인 배너를 통해 "관계자 외 출입 금지", "모든 활동은 모니터링 됨" 등의 경고 메시지가 표시되는지 확인해야 합니다. 이는 법적 대응의 근거가 됩니다.

```bash
# 1. Telnet용 배너 확인
echo "=== 1. /etc/issue.net ==="
cat /etc/issue.net

# 2. 로그인 성공 후 메시지 확인
echo "=== 2. /etc/motd ==="
cat /etc/motd

# 3. SSH 배너 설정 확인
echo "=== 3. SSH Banner ==="
grep Banner /etc/ssh/sshd_config

# 4. issue 파일 확인 (Console)
echo "=== 4. /etc/issue ==="
cat /etc/issue
```

**양호 출력 예시:**
```text
=== 1. /etc/issue.net ===
#####################################################################
#  WARNING: Authorized access only!                                 #
#  This system is for the use of authorized users only.             #
#  Individuals using this computer system without authority, or in  #
#  excess of their authority, are subject to having all of their    #
#  activities on this system monitored and recorded by system       #
#  personnel.                                                       #
#####################################################################
=== 3. SSH Banner ===
Banner /etc/issue.net
```

**취약 출력 예시:**
```text
=== 1. /etc/issue.net ===
\r\n\s
(\m: OS 버전 정보 노출)
=== 3. SSH Banner ===
#Banner none
```

### 3. 조치 방법

#### 경고 메시지 파일 작성

1. **/etc/issue.net 생성** (원격 접속 시 표시)
   ```bash
   cat > /etc/issue.net << 'EOF'
   #####################################################################
   #  WARNING: Authorized access only!                                 #
   #  This system is for the use of authorized users only.             #
   #  Individuals using this computer system without authority, or in  #
   #  excess of their authority, are subject to having all of their    #
   #  activities on this system monitored and recorded by system       #
   #  personnel.                                                       #
   #                                                                   #
   #  Anyone using this system expressly consents to such monitoring   #
   #  and is advised that if such monitoring reveals possible          #
   #  criminal activity, system personnel may provide the evidence     #
   #  of such monitoring to law enforcement officials.                 #
   #####################################################################
   EOF

   chmod 644 /etc/issue.net
   chown root:root /etc/issue.net
   ```

2. **/etc/motd 생성** (로그인 후 표시)
   ```bash
   cat > /etc/motd << 'EOF'
   #####################################################################
   #  WARNING: Authorized access only!                                 #
   #  All activities are monitored and recorded.                       #
   #####################################################################
   EOF

   chmod 644 /etc/motd
   chown root:root /etc/motd
   ```

3. **SSH 설정 적용**
   ```bash
   # /etc/ssh/sshd_config 편집
   vi /etc/ssh/sshd_config

   # 추가/수정:
   Banner /etc/issue.net

   # 서비스 재시작
   systemctl restart sshd
   ```

4. **FTP 배너 설정** (vsftpd의 경우)
   ```bash
   # /etc/vsftpd/vsftpd.conf
   ftpd_banner=WARNING: Authorized access only! All activities are monitored.

   systemctl restart vsftpd
   ```

### 4. 참고 자료

- CIS Benchmark for Linux: 로그인 배너 권고
- NIST SP 800-53: AC-8 (시스템 사용 통지)
- 법적 효력: 경고 메시지의 법적 근거

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.