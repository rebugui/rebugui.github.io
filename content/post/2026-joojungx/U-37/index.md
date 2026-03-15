---
title: "[2026 주요정보통신기반시설] U-37 crontab 설정 파일 권한 설정 미흡"
slug: "2026-주정통/U-37"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "crontab및at서비스관련파일의권한적절성여부점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-37 crontab 설정 파일 권한 설정 미흡

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-37 |
| **점검내용** | crontab및at서비스관련파일의권한적절성여부점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX등 |
| **양호기준** | crontab및at명령어에일반사용자실행권한이제거되어있으며,cron및at관련파일권한이640이하인경우 |
| **취약기준** | crontab및at명령어에일반사용자실행권한이부여되어있으며,cron및at관련파일권한이640이상인경우 |
| **조치방법** | crontab및at명령어파일권한750이하,cron및at관련파일소유자및파일권한640이하설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: /etc/crontab 권한이 640 이하이고, cron.allow 파일이 존재하는 경우
- **취약**: /etc/crontab 권한이 644 이상이거나, cron.allow 파일이 없는 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| /etc/cron.deny만 존재 | 취약 | allow 우선 원칙 적용 필요 |
| /etc/cron.allow 존재 | 양호 | 명시적 허용 정책 |
| /var/spool/cron 권한 700 | 양호 | root만 접근 가능 |
| /etc/cron.d 권한 750 | 양호 | root 그룹만 접근 |
| crontab 명령어에 SUID 비트 | 주의 | 권한 상승 위험 확인 필요 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| Linux | /etc/crontab | 600 (root:root) | 시스템 cron 설정 |
| Linux | /var/spool/cron | 700 (root:root) | 사용자 cron 디렉터리 |
| Linux | /etc/cron.d | 750 (root:root) | 추가 cron 파일 |
| Linux | /etc/cron.allow | 640 (root:root) | cron 사용 허가 목록 |
| Linux | /etc/at.allow | 640 (root:root) | at 사용 허가 목록 |

### 2. 점검 방법

#### Linux 점검

cron 및 at 스케줄러 설정 파일의 권한을 점검하여 일반 사용자가 예약 작업을 임의로 수정하거나 다른 사용자의 작업을 확인할 수 없는지 확인해야 합니다.

```bash
# /etc/crontab 권한 확인
echo "=== 1. /etc/crontab ==="
ls -l /etc/crontab
stat -c "%a %U:%G" /etc/crontab 2>/dev/null || stat -f "%Lp %Su:%Sg" /etc/crontab

# /etc/cron.d 권한 확인
echo "=== 2. /etc/cron.d ==="
ls -ld /etc/cron.d
stat -c "%a %U:%G" /etc/cron.d 2>/dev/null || stat -f "%Lp %Su:%Sg" /etc/cron.d

# /var/spool/cron 권한 확인
echo "=== 3. /var/spool/cron ==="
ls -ld /var/spool/cron
stat -c "%a %U:%G" /var/spool/cron 2>/dev/null || stat -f "%Lp %Su:%Sg" /var/spool/cron

# cron.allow 확인
echo "=== 4. cron/at 접근 제어 ==="
ls -l /etc/cron.allow /etc/at.allow 2>/dev/null
cat /etc/cron.allow 2>/dev/null
cat /etc/at.allow 2>/dev/null
```

**양호 출력 예시:**
```text
=== 1. /etc/crontab ===
-rw------- 1 root root 451 Jan 20 10:00 /etc/crontab
600 root:root
=== 2. /etc/cron.d ===
drwxr-x--- 2 root root 4096 Jan 20 10:00 /etc/cron.d
750 root:root
=== 3. /var/spool/cron ===
drwx------ 2 root root 4096 Jan 20 10:00 /var/spool/cron
700 root:root
=== 4. cron/at 접근 제어 ===
-rw-r----- 1 root root 6 Jan 20 10:00 /etc/cron.allow
root
```

**취약 출력 예시:**
```text
=== 1. /etc/crontab ===
-rw-r--r-- 1 root root 451 Jan 20 10:00 /etc/crontab
644 root:root
=== 2. /etc/cron.d ===
drwxrwxrwx 2 root root 4096 Jan 20 10:00 /etc/cron.d
777 root:root
=== 4. cron/at 접근 제어 ===
ls: /etc/cron.allow: No such file or directory
```

#### Solaris, AIX, HP-UX 점검

```bash
# cron 설정 파일 확인
ls -l /etc/crontab
ls -ld /var/spool/cron/crontabs

# 접근 제어 확인
ls -l /etc/cron.allow /etc/cron.deny
```

### 3. 조치 방법

#### Linux 설정

1. **cron/at 사용 제한**
   ```bash
   # cron.allow 생성 (root만 허용)
   echo "root" > /etc/cron.allow
   chmod 640 /etc/cron.allow
   chown root:root /etc/cron.allow

   # at.allow 생성
   echo "root" > /etc/at.allow
   chmod 640 /etc/at.allow
   chown root:root /etc/at.allow

   # cron.deny, at.deny 삭제 (allow가 우선)
   rm -f /etc/cron.deny /etc/at.deny
   ```

2. **설정 파일 권한 강화**
   ```bash
   # /etc/crontab
   chown root:root /etc/crontab
   chmod 600 /etc/crontab

   # /etc/cron.d
   chown root:root /etc/cron.d
   chmod 750 /etc/cron.d

   # /etc/cron.* 디렉터리
   for dir in /etc/cron.hourly /etc/cron.daily /etc/cron.weekly /etc/cron.monthly; do
       chown root:root "$dir"
       chmod 755 "$dir"
   done

   # /var/spool/cron
   chown root:root /var/spool/cron
   chmod 700 /var/spool/cron
   ```

3. **기존 cron 작업 감사**
   ```bash
   # 모든 사용자의 cron 작업 확인
   for user in $(cut -d: -f1 /etc/passwd); do
       CRON_FILE="/var/spool/cron/$user"
       if [ -f "$CRON_FILE" ]; then
           echo "=== $user의 cron 작업 ==="
           cat "$CRON_FILE"
       fi
   done
   ```

4. **서비스 재시작**
   ```bash
   # cron 서비스 재시작
   systemctl restart cron
   # 또는
   systemctl restart crond
   ```

### 4. 참고 자료

- CIS Benchmark for Linux: cron 설정 파일 권한 권고
- NIST SP 800-53: AC-6 (최소 권한 원칙)
- KISA 보안 가이드라인: 스케줄러 권한 관리
- man pages: cron(8), crontab(1), at(1)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.