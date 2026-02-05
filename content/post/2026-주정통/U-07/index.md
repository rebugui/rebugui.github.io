---
title: "[2026 주요정보통신기반시설] U-07 불필요한 계정 제거"
slug: "2026-주정통/U-07"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "시스템계정중불필요한계정(퇴직,전직,휴직등의이유로사용하지않는계정및장기적으로사용하지않는계정등)이존재여부점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-07 불필요한 계정 제거

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-07 |
| **점검내용** | 시스템계정중불필요한계정(퇴직,전직,휴직등의이유로사용하지않는계정및장기적으로사용하지않는계정등)이존재여부점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX등 |
| **양호기준** | 불필요한계정이존재하지않는경우 |
| **취약기준** | 불필요한계정이존재하는경우 |
| **조치방법** | 시스템에존재하는계정확인후불필요한계정제거하도록설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 불필요한 계정(퇴직, 전직, 휴직, 장기 미사용 계정 등)이 존재하지 않는 경우
- **취약**: 불필요한 계정이 존재하는 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| 휴면 계정(6개월 이상 미로그인) | 취약 | 제거 또는 비활성화 필요 |
| 서비스 계정(daemon, www-data 등) | 양호 | nologin 설정된 서비스 계정은 유지 |
| 휴직자 계정 | 취약 | 비활성화 권장 |
| 퇴직자 계정 | 취약 | 즉시 제거 필요 |
| 임시 계정(만료됨) | 취약 | 제거 필요 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| 모든 OS | 휴면 계정 점검 주기 | 월 1회 | lastlog 명령어 활용 |
| 모든 OS | 퇴직자 계정 처리 | 즉시 제거 | userdel -r 사용 |
| 모든 OS | 휴직자 계정 처리 | Shell을 nologin으로 변경 | usermod -s /sbin/nologin |
| Linux | UID 1000 이상 점검 | 일반 사용자 계정 확인 | /etc/passwd 확인 |

### 2. 점검 방법

#### Solaris, Linux, AIX, HP-UX 점검

시스템에는 퇴직, 전직, 휴직 등의 이유로 사용하지 않는 계정과 장기적으로 로그인하지 않는 휴면 계정이 존재하지 않는지 확인해야 합니다.

```bash
# 1. /etc/passwd 파일 내 모든 계정 확인
cat /etc/passwd

# 2. 로그인 가능한 계정만 필터링 (nologin/false 제외)
cat /etc/passwd | grep -v '/sbin/nologin' | grep -v '/bin/false'

# 3. lastlog 명령어로 모든 계정의 마지막 로그인 시간 확인
lastlog
```

**양호 출력 예시:**
```text
# 로그인 가능한 계정
root:x:0:0:root:/root:/bin/bash
admin1:x:1000:1000:Admin User:/home/admin1:/bin/bash

# lastlog 출력 (최근 로그인)
admin1   pts/0    192.168.1.100    Mon Jan 20 10:30:15 +0900 2025
```

**취약 출력 예시:**
```text
# 불필요한 계정 존재
root:x:0:0:root:/root:/bin/bash
admin1:x:1000:1000:Admin User:/home/admin1:/bin/bash
old_employee:x:1001:1001:Old Employee:/home/old_employee:/bin/bash
temp_user:x:1002:1002:Temporary User:/home/temp_user:/bin/bash

# lastlog 출력 (장기 미로그인)
old_employee     **Never logged in**
temp_user        Fri Dec  1 09:15:00 +0900 2023  # 1년 이상 경과
```

#### 로그인 기록을 이용한 휴면 계정 점검

```bash
# 180일(6개월) 이상 로그인하지 않은 계정 확인
lastlog | awk '$6 == "**Never" || ($0 ~ /202[0-4]/)' | grep -v root
```

#### 사용자별 프로세스 확인

```bash
# 현재 실행 중인 프로세스로 활성 사용자 확인
ps -eo user | sort | uniq

# 특정 사용자의 실행 중인 프로세스 확인
ps -u olduser -f
```

### 3. 조치 방법

#### Solaris, Linux, HP-UX 설정

1. **제거할 계정 확인**
   ```bash
   id olduser
   lastlog | grep olduser
   ls -la /home/olduser
   ```

2. **계정 비활성화 (잠정 조치)**
   ```bash
   # 계정 잠금 (비밀번호 변경)
   passwd -l olduser

   # 또는 쉘 변경 (로그인 불가)
   usermod -s /sbin/nologin olduser
   ```

3. **계정 제거 (확정 조치)**
   ```bash
   # 계정만 제거 (홈 디렉터리 보존)
   userdel olduser

   # 계정과 홈 디렉터리 함께 제거
   userdel -r olduser
   ```

4. **관련 파일 및 그룹 정리**
   ```bash
   # 사용자 그룹 제거
   groupdel olduser

   # 메일함 제거
   rm /var/spool/mail/olduser

   # crontab 제거
   crontab -u olduser -r
   ```

#### AIX 설정

1. **제거할 계정 확인**
   ```bash
   lsuser -a home shell olduser
   ```

2. **계정 제거**
   ```bash
   # 계정 제거
   rmuser -p olduser

   # -p 옵션: 사용자의 홈 디렉터리도 함께 제거
   ```

#### 복수 계정 일괄 처리

**휴면 계정 일괄 제거 스크립트:**
```bash
#!/bin/bash
# unused_users.txt 파일에 제거할 계정명 목록 작성
USER_LIST="unused_users.txt"

while read -r username; do
    echo "계정 제거 중: $username"
    cp /etc/passwd /etc/passwd.bak.$(date +%Y%m%d)
    userdel -r "$username"
    if [ $? -eq 0 ]; then
        echo "[SUCCESS] $username 계정 제거 완료"
    else
        echo "[FAIL] $username 계정 제거 실패"
    fi
done < "$USER_LIST"
```

#### 기본 계정 처리

```bash
# 기본 계정의 셸을 nologin으로 변경 (권장)
for user in lp uucp games gopher news; do
    if id "$user" &>/dev/null; then
        usermod -s /sbin/nologin "$user"
    fi
done
```

### 4. 참고 자료

- [Red Hat - Managing User Accounts](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/)
- [Ubuntu - User Management](https://ubuntu.com/server/docs/security-users)
- [CIS Benchmark - Ensure no unnecessary accounts exist](https://www.cisecurity.org/cis-benchmarks/)
- [NIST AC-2 - Account Management](https://csrc.nist.gov/projects/risk-management/risk-management-encyclopedia)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.