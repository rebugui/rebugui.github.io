---
title: "[2026 주요정보통신기반시설] U-67 로그 디렉터리 소유자 및 권한 설정"
slug: "2026-주정통/U-67"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "로그에 대한 접근 통제 및 관리 여부 점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-67 로그 디렉터리 소유자 및 권한 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-67 |
| **점검내용** | 로그에 대한 접근 통제 및 관리 여부 점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX 등 |
| **양호기준** | 디렉터리 내 로그 파일의 소유자가 root이고, 권한이 644 이하인 경우 |
| **취약기준** | 디렉터리 내 로그 파일의 소유자가 root가 아니거나, 권한이 644를 초과하는 경우 |
| **조치방법** | 디렉터리 내 로그 파일 소유자 및 권한 변경 설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 로그 파일 및 디렉터리의 소유자가 root(또는 syslog 계정)이고, 권한이 640(rw-r-----) 또는 600(rw-------) 이하로 설정된 경우
- **취약**: 로그 파일이 일반 사용자에게 읽기/쓰기 권한(Any)이 부여되어 있거나, 소유자가 불분명한 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| 권한 600 또는 640 | 양호 | root만 또는 root 그룹만 |
| 권한 644 | 주의 | others 읽기 가능 |
| 권한 666 이상 | 취약 | 누구나 읽기/쓰기 |
| 소유자 root | 양호 | 정상 |
| 소유자 일반 사용자 | 취약 | 권한 상승 가능 |
| /var/log 권한 755 | 양호 | 디렉터리 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| Linux | /var/log/secure | 600 (root:root) | 인증 로그 |
| Linux | /var/log/messages | 640 (root:root/adm) | 시스템 로그 |
| Linux | /var/log/maillog | 640 (root:root) | 메일 로그 |
| Linux | /var/log/cron | 640 (root:root) | 스케줄 로그 |
| Linux | /var/log/boot.log | 600 (root:root) | 부팅 로그 |
| Linux | /var/log 디렉터리 | 755 (root:root) | 로그 디렉터리 |

### 2. 점검 방법

#### Linux, Solaris, AIX, HP-UX 점검

시스템 로그 파일에는 사용자 접근 기록, 시스템 오류, 보안 이벤트 등 민감한 정보가 담겨 있습니다. 로그 파일의 무결성과 기밀성을 보장하기 위해 권한을 점검해야 합니다.

```bash
# 1. 주요 로그 파일 권한 확인
echo "=== 1. Main Log Files ==="
ls -l /var/log/messages /var/log/secure /var/log/syslog /var/log/maillog /var/log/boot.log 2>/dev/null

# 2. /var/log 디렉터리 권한 확인
echo "=== 2. /var/log Directory ==="
ls -ld /var/log

# 3. 모든 로그 파일 권한 점검
echo "=== 3. All Log Files ==="
find /var/log -type f -name "*.log" -exec ls -l {} \; 2>/dev/null
find /var/log -type f \( -name "messages" -o -name "secure" -o -name "syslog" -o -name "maillog" \) -exec ls -l {} \;

# 4. 권한 644 이상인 로그 파일 찾기
echo "=== 4. Log Files with Excessive Permissions ==="
find /var/log -type f -perm /022 -exec ls -l {} \; 2>/dev/null
```

**양호 출력 예시:**
```text
=== 1. Main Log Files ===
-rw------- 1 root root 123456 Jan 20 10:00 /var/log/secure
-rw-r----- 1 root adm 789012 Jan 20 10:00 /var/log/syslog
-rw-r----- 1 root root 234567 Jan 20 10:00 /var/log/messages
-rw-r----- 1 root root 45678 Jan 20 10:00 /var/log/maillog
=== 2. /var/log Directory ===
drwxr-xr-x 1 root root 4096 Jan 20 10:00 /var/log
=== 4. Log Files with Excessive Permissions ===
(결과 없음)
```

**취약 출력 예시:**
```text
=== 1. Main Log Files ===
-rw-rw-rw- 1 root root 123456 Jan 20 10:00 /var/log/secure
-rw-r--r-- 1 root root 789012 Jan 20 10:00 /var/log/messages
=== 2. /var/log Directory ===
drwxrwxrwx 2 root root 4096 Jan 20 10:00 /var/log
=== 4. Log Files with Excessive Permissions ===
-rw-rw-rw- 1 root root /var/log/secure
```

### 3. 조치 방법

#### 권한 및 소유권 변경

1. **주요 로그 파일 권한 변경**
   ```bash
   # 인증 로그 (가장 중요)
   chown root:root /var/log/secure
   chmod 600 /var/log/secure

   # 시스템 로그
   chown root:root /var/log/messages
   chmod 640 /var/log/messages

   # 메일 로그
   chown root:root /var/log/maillog
   chmod 640 /var/log/maillog

   # 크론 로그
   chown root:root /var/log/cron
   chmod 640 /var/log/cron

   # 부팅 로그
   chown root:root /var/log/boot.log
   chmod 600 /var/log/boot.log

   # 확인
   ls -l /var/log/secure /var/log/messages /var/log/maillog /var/log/cron /var/log/boot.log
   ```

2. **/var/log 디렉터리 권한 설정**
   ```bash
   chown root:root /var/log
   chmod 755 /var/log
   ```

3. **다른 로그 파일들 일괄 변경**
   ```bash
   # 일반 로그 파일 (640)
   find /var/log -type f -name "*.log" -exec chmod 640 {} \;
   find /var/log -type f -name "*.log" -exec chown root:root {} \;

   # 인증 관련 로그 (600)
   find /var/log -type f \( -name "secure" -o -name "auth.log" -o -name "btmp" -o -name "wtmp" \) -exec chmod 600 {} \;
   ```

#### logrotate 설정

logrotate가 실행되면서 로그 파일이 새로 생성될 때 권한이 초기화될 수 있습니다. 생성되는 파일의 권한을 지정해야 합니다.

```bash
# /etc/logrotate.conf 편집
vi /etc/logrotate.conf

# 추가/수정:
create 0640 root root
# 또는 특정 로그에 대해서만:
/var/log/secure {
    create 0600 root root
    ...
}

# 테스트
logrotate -d /etc/logrotate.conf
```

4. **rsyslog가 로그를 기록할 수 있는지 확인**
   ```bash
   # 로그 데몬이 해당 파일에 쓸 수 있는지 확인
   systemctl restart rsyslog

   # 테스트 로그
   logger "Test log message for permission check"
   tail /var/log/messages
   tail /var/log/secure
   ```

### 4. 참고 자료

- CIS Benchmark for Linux: 로그 파일 권한 권고
- NIST SP 800-53: AC-6 (최소 권한), AU-9 (감사 기록 보호)
- man pages: logrotate(8), rsyslog.conf(5)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.