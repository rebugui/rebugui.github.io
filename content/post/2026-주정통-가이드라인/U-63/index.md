---
title: "[2026 주요정보통신기반시설] U-63 sudo 명령어 접근 관리"
slug: "2026-주정통/U-63"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "/etc/sudoers 파일 권한 적절성 여부 점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
draft: true
---

# U-63 sudo 명령어 접근 관리

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-63 |
| **점검내용** | /etc/sudoers 파일 권한 적절성 여부 점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX 등 |
| **양호기준** | /etc/sudoers 파일의 소유자가 root이고 권한이 0440(읽기 전용) 또는 그보다 높은 보안 수준으로 설정된 경우 |
| **취약기준** | /etc/sudoers 파일의 소유자가 root가 아니거나 권한이 0440 또는 그보다 높은 보안 수준으로 설정되어 있지 않은 경우 |
| **조치방법** | /etc/sudoers 파일 및 관련 파일의 소유자 및 권한 변경 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: /etc/sudoers 소유자가 root:root이고 권한이 440인 경우
- **취약**: /etc/sudoers 소유자가 root가 아니거나 권한이 444 이상인 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| ALL=(ALL) NOPASSWD: ALL | 취약 | 비밀번호 없는 무제한 sudo |
| 특정 명령어만 허용 | 양호 | 최소 권한 원칙 |
| sudo 로깅 활성화 | 양호 | 감사 추적 가능 |
| 권한 644 이상 | 취약 | 일반 사용자 수정 가능 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| Linux | /etc/sudoers 권한 | 440 (root:root) | visudo로만 수정 |
| Linux | Defaults logfile | /var/log/sudo.log | 로깅 |
| Linux | Defaults log_output | True | 명령 출력 로깅 |
| Linux | 사용자 권한 | 특정 명령어만 | ALL=(ALL) ALL 금지 |

### 2. 점검 방법

#### Linux, Solaris 점검

sudo는 일반 사용자가 root 권한으로 특정 명령어를 실행할 수 있게 하는 기능입니다. 파일 권한이 느슨하면 권한 상승 공격에 악용될 수 있습니다.

```bash
# 1. sudoers 파일 권한 확인
echo "=== 1. /etc/sudoers Permissions ==="
ls -l /etc/sudoers
stat -c "%a %U:%G" /etc/sudoers 2>/dev/null || stat -f "%Lp %Su:%Sg" /etc/sudoers

# 2. sudoers.d 디렉터리 확인
echo "=== 2. /etc/sudoers.d ==="
ls -ld /etc/sudoers.d 2>/dev/null

# 3. sudo 설정 확인 (취약한 설정)
echo "=== 3. Sudo Configuration ==="
grep -v "^#" /etc/sudoers | grep -v "^$" | grep -E "NOPASSWD|ALL"

# 4. sudo 로깅 확인
echo "=== 4. Sudo Logging ==="
grep -E "logfile|log_output" /etc/sudoers
```

**양호 출력 예시:**
```text
=== 1. /etc/sudoers Permissions ===
-r--r----- 1 root root 1234 Jan 20 10:00 /etc/sudoers
440 root:root
=== 3. Sudo Configuration ===
(취약한 설정 없음)
=== 4. Sudo Logging ===
Defaults    logfile="/var/log/sudo.log"
Defaults    log_output
```

**취약 출력 예시:**
```text
=== 1. /etc/sudoers Permissions ===
-rw-r--r-- 1 root root 1234 Jan 20 10:00 /etc/sudoers
644 root:root
=== 3. Sudo Configuration ===
user ALL=(ALL) NOPASSWD: ALL
```

### 3. 조치 방법

#### 파일 권한 설정

1. **sudoers 파일 권한 변경**
   ```bash
   # 소유자 및 권한 설정
   chown root:root /etc/sudoers
   chmod 440 /etc/sudoers

   # sudoers.d 디렉터리 (사용 시)
   chown root:root /etc/sudoers.d
   chmod 750 /etc/sudoers.d

   # 확인
   ls -l /etc/sudoers
   ls -ld /etc/sudoers.d
   ```

2. **visudo로 sudoers 수정**
   ```bash
   # visudo 실행 (유일한 안전한 수정 방법)
   visudo

   # 추가/수정할 설정:
   # 로깅 설정
   Defaults    logfile="/var/log/sudo.log"
   Defaults    log_output

   # 최소 권한 부여 예시:
   # 특정 서비스 재시작만 허용
   john ALL=(root) /usr/bin/systemctl restart apache2

   # 그룹으로 권한 부여 (비밀번호 필요)
   %wheel ALL=(ALL) ALL

   # 절대 사용하지 말아야 할 취약한 설정:
   # user ALL=(ALL) NOPASSWD: ALL  # 취약!
   ```

3. **로그 파일 생성**
   ```bash
   touch /var/log/sudo.log
   chown root:root /var/log/sudo.log
   chmod 600 /var/log/sudo.log
   ```

4. **설정 확인**
   ```bash
   # 문법 확인
   visudo -c

   # 테스트
   sudo -l
   ```

### 4. 참고 자료

- CIS Benchmark for Linux: sudo 권한 관리 권고
- NIST SP 800-53: AC-6 (최소 권한 원칙)
- man pages: sudoers(5), visudo(8), sudo(8)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.