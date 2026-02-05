---
title: "[2026 주요정보통신기반시설] U-10 동일한 UID 금지"
slug: "2026-주정통/U-10"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "/etc/passwd파일내UID가동일한사용자계정존재여부점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-10 동일한 UID 금지

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-10 |
| **점검내용** | /etc/passwd파일내UID가동일한사용자계정존재여부점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX등 |
| **양호기준** | 동일한UID로설정된사용자계정이존재하지않는경우 |
| **취약기준** | 동일한UID로설정된사용자계정이존재하는경우 |
| **조치방법** | 동일한UID를가진사용자계정의UID를중복되지않도록변경하도록설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 동일한 UID로 설정된 사용자 계정이 존재하지 않는 경우
- **취약**: 동일한 UID로 설정된 사용자 계정이 존재하는 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| 모든 계정이 고유 UID | 양호 | 정상 상태 |
| 일반 사용자 간 UID 중복 | 취약 | 즉시 수정 필요 |
| 시스템 계정 UID 중복 | 취약 | 수정 필요 |
| root UID(0) 중복 | 취약 | 심각한 보안 위험 |
| UID 중복으로 인한 권한 문제 | 취약 | 파일 소유권 혼란 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| Linux | UID_MIN | 1000 | /etc/login.defs |
| Linux | UID_MAX | 60000 | /etc/login.defs |
| Solaris | 사용자 UID | 100 이상 | 시스템 계정과 분리 |
| AIX | 사용자 UID | 200 이상 | 시스템 계정과 분리 |

### 2. 점검 방법

#### Solaris, Linux, AIX, HP-UX 점�

UID(User Identifier)는 사용자 계정의 고유 식별자로, 중복되면 권한 문제와 감사 추적의 어려움을 초래합니다.

```bash
# /etc/passwd 파일에서 동일한 UID 존재 여부 확인
awk -F: '{print $3}' /etc/passwd | sort | uniq -d

# 중복된 UID와 해당 계정 출력
awk -F: 'count[$3]++ {print $3, $1}' /etc/passwd | sort

# 또는
cut -d: -f1,3 /etc/passwd | sort -t: -k2 -n | uniq -D -f1
```

**양호 출력 예시:**
```text
# 중복된 UID 없음
(출력 없음)
```

**취약 출력 예시:**
```text
# 중복된 UID
1001
1005

# 중복된 UID와 해당 계정
UID: 1001 계정: john
UID: 1001 계정: jane
UID: 1005 계정: temp1
UID: 1005 계정: temp2
```

#### 종합 점검 스크립트

```bash
#!/bin/bash
# 중복 UID 확인
duplicates=$(awk -F: '{print $3}' /etc/passwd | sort | uniq -d)

if [ -z "$duplicates" ]; then
    echo "[양호] 중복된 UID가 없습니다."
else
    echo "[취약] 중복된 UID가 발견되었습니다."
    awk -F: '$3 >= 500 {uid_list[$3] = uid_list[$3] "," $1} END {
        for (uid in uid_list) {
            split(uid_list[uid], users, ",")
            if (length(users) > 1) {
                printf "UID %-6s: ", uid
                for (i = 2; i <= length(users); i++) {
                    printf "%s ", users[i]
                }
                print ""
            }
        }
    }' /etc/passwd
fi
```

### 3. 조치 방법

#### Solaris, Linux, HP-UX 설정

1. **단일 계정 UID 변경**
   ```bash
   # 중복된 UID를 가진 사용자 계정의 UID 변경
   usermod -u <새로운_UID> <username>

   # 예시: jane의 UID를 1001에서 1002로 변경
   usermod -u 1002 jane
   ```

2. **다중 계정 일괄 UID 변경**
   ```bash
   # 사용 가능한 UID 시작 번호
   new_uid=2000

   for dup_uid in $(awk -F: '{print $3}' /etc/passwd | sort | uniq -d); do
       count=0
       awk -F: -v uid=$dup_uid '$3 == uid {print $1}' /etc/passwd | while read user; do
           if [ $count -gt 0 ]; then
               usermod -u $new_uid $user
               new_uid=$((new_uid + 1))
           fi
           count=$((count + 1))
       done
   done
   ```

3. **UID 변경 후 작업**
   ```bash
   # 파일 소유권 확인
   find / -user <username> -ls 2>/dev/null

   # 실행 중인 프로세스 확인
   ps -u <username> -f

   # crontab 확인
   crontab -u <username> -l
   ```

#### AIX 설정

1. **단일 계정 UID 변경**
   ```bash
   chuser id=<새로운_UID> <username>
   ```

2. **일괄 변경 스크립트**
   ```bash
   duplicates=$(awk -F: '{print $3}' /etc/passwd | sort | uniq -d)
   new_uid=2000

   for dup_uid in $duplicates; do
       users=$(awk -F: -v uid=$dup_uid '$3 == uid {print $1}' /etc/passwd | tail -n +2)
       for user in $users; do
           chuser id=$new_uid $user
           new_uid=$((new_uid + 1))
       done
   done
   ```

### 4. 참고 자료

- [Linux Standard Base (LSB)](https://refspecs.linuxfoundation.org/lsb.shtml)
- [Red Hat Account Management Guide](https://access.redhat.com/documentation/)
- [CIS Benchmark - Ensure no duplicate UIDs exist](https://www.cisecurity.org/cis-benchmarks/)
- [NIST AC-2 - Account Management](https://csrc.nist.gov/projects/risk-management/risk-management-encyclopedia)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.