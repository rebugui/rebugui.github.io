---
title: "[2026 주요정보통신기반시설] U-09 계정이 존재하지 않는 GID 금지"
slug: "2026-주정통/U-09"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "그룹설정파일(/etc/group)에불필요한그룹이존재여부점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-09 계정이 존재하지 않는 GID 금지

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-09 |
| **점검내용** | 그룹설정파일(/etc/group)에불필요한그룹이존재여부점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX등 |
| **양호기준** | 시스템관리나운용에불필요한그룹이제거된경우 |
| **취약기준** | 시스템관리나운용에불필요한그룹이존재하는경우 |
| **조치방법** | 불필요한그룹이존재하는경우관리자와검토하여제거하도록설정 ※ /etc/group파일과/etc/passwd파일을비교하여점검하기를권고함 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 시스템 관리나 운용에 불필요한 그룹이 제거된 경우
- **취약**: 시스템 관리나 운용에 불필요한 그룹이 존재하는 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| 구성원이 없는 그룹 | 취약 | 제거 권장 |
| 사용자 모두 삭제된 그룹 | 취약 | 제거 필요 |
| 파일 소유 그룹(구성원 없음) | 취약 | 소유권 변경 후 제거 |
| 시스템 기본 그룹(daemon 등) | 양호 | 유지 필요 |
| 서비스 그룹(www-data 등) | 양호 | 사용 중이면 유지 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| 모든 OS | 불필요한 그룹 점검 | 월 1회 | /etc/group 확인 |
| 모든 OS | /etc/group과 /etc/passwd 비교 | 정기적 수행 | 사용자 없는 그룹 확인 |
| 모든 OS | GID 재사용 방지 | 삭제된 GID 재할당 금지 | 정책 수립 |

### 2. 점검 방법

#### Solaris, Linux, AIX, HP-UX 점�

시스템에는 사용자 계정이 없는 불필요한 그룹이 존재하지 않는지 확인해야 합니다.

```bash
# 1. 모든 그룹 목록 확인
cat /etc/group

# 2. 사용자가 없는 그룹 확인
for group in $(awk -F: '{print $1}' /etc/group); do
    if ! grep -q "^$group:" /etc/passwd; then
        echo "Group '$group' has no user account"
    fi
done

# 3. 구성원이 없는 그룹 확인
awk -F: '$4 == "" {print $1":"$3}' /etc/group

# 4. 특정 그룹의 소유 파일 확인
find / -type f -group unused 2>/dev/null
```

**양호 출력 예시:**
```text
# 구성원이 없는 그룹 확인
(출력 없음)
```

**취약 출력 예시:**
```text
# 사용자가 없는 그룹
Group 'unused' has no user account
Group 'oldproject' has no user account

# 구성원이 없는 그룹
unused:1002
oldproject:1003
temp:1004
```

#### GID 충돌 확인

```bash
# 사용되지 않는 GID 확인
awk -F: '{print $4}' /etc/passwd | sort -u > /tmp/used_gids.txt
awk -F: '{print $3}' /etc/group | sort -u > /tmp/all_gids.txt
comm -13 /tmp/used_gids.txt /tmp/all_gids.txt
```

### 3. 조치 방법

#### Solaris, Linux, HP-UX 설정

1. **제거할 그룹 확인**
   ```bash
   groupdel unusedgrp  # 존재하지 않는 그룹으로 테스트
   ```

2. **불필요한 그룹 제거**
   ```bash
   groupdel unused
   groupdel oldproject
   ```

3. **여러 그룹 일괄 제거**
   ```bash
   while read groupname; do
       if groupdel "$groupname" 2>/dev/null; then
           echo "[SUCCESS] $groupname 그룹 제거 완료"
       else
           echo "[FAIL] $groupname 그룹 제거 실패"
       fi
   done < /tmp/groups_to_remove.txt
   ```

#### AIX 설정

1. **SMIT를 통한 그룹 제거 (권장)**
   ```bash
   smit remove_group
   ```

2. **chgroup 명령어로 제거**
   ```bash
   chgroup -R -f unused
   ```

### 4. 참고 자료

- [Red Hat - Managing Groups in Linux](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/)
- [Ubuntu - User and Group Management](https://ubuntu.com/server/docs/security-users)
- [CIS Benchmark - Ensure no unnecessary accounts exist](https://www.cisecurity.org/cis-benchmarks/)
- [NIST AC-2(2) - Employ automated mechanisms to manage group accounts](https://csrc.nist.gov/projects/risk-management/risk-management-encyclopedia)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.