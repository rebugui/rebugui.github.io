---
title: "[2026 주요정보통신기반시설] U-08 관리자 그룹에 최소한의 계정 포함"
slug: "2026-주정통/U-08"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "시스템관리자그룹에최소한(root계정과시스템관리에허용된계정)의계정만존재여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
draft: true
---

# U-08 관리자 그룹에 최소한의 계정 포함

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-08 |
| **점검내용** | 시스템관리자그룹에최소한(root계정과시스템관리에허용된계정)의계정만존재여부점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX등 |
| **양호기준** | 관리자그룹에불필요한계정이등록되어있지않은경우 |
| **취약기준** | 관리자그룹에불필요한계정이등록된경우 |
| **조치방법** | 관리자그룹에등록된계정확인후불필요한계정제거하도록설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 관리자 그룹(root 그룹, GID 0)에 불필요한 계정이 등록되어 있지 않은 경우
- **취약**: 관리자 그룹에 불필요한 계정이 등록된 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| root만 GID 0에 포함 | 양호 | 최소한의 구성 |
| root + 1~2명의 관리자 | 양호 | 허용 가능한 범위 |
| 일반 사용자가 GID 0에 포함 | 취약 | 제거 필요 |
| 서비스 계정이 GID 0에 포함 | 취약 | 제거 필요 |
| 퇴직자가 GID 0에 포함 | 취약 | 즉시 제거 필요 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| 모든 OS | root 그룹 구성원 | root만 포함 | 최소 권한 원칙 |
| 대형 시스템 | root 그룹 구성원 | root + 1~3명 | 허용 가능 |
| 일반 사용자 | 보조 그룹 | wheel 그룹 | su 사용 허용 |

### 2. 점검 방법

#### Solaris, Linux, AIX, HP-UX 점검

관리자 그룹(GID 0, root 그룹)은 시스템의 모든 파일과 설정에 접근할 수 있는 매우 중요한 권한을 가집니다.

```bash
# 1. /etc/group 파일에서 root 그룹 확인
cat /etc/group | grep '^root:'

# 2. GID 0인 모든 그룹 찾기
awk -F: '$3 == 0' /etc/group

# 3. 특정 사용자의 그룹 확인
groups admin1

# 또는
id admin1
```

**양호 출력 예시:**
```text
# root 그룹 확인
root:x:0:root

# 사용자 그룹 확인
uid=1000(admin1) gid=1000(admin1) groups=1000(admin1),10(wheel)
# GID 0(root) 미포함
```

**취약 출력 예시:**
```text
# root 그룹 확인
root:x:0:root,admin1,admin2,user1,developer
# 불필요한 계정 다수 포함

# 사용자 그룹 확인
uid=1000(admin1) gid=1000(admin1) groups=1000(admin1),0(root),10(wheel)
# GID 0(root) 포함
```

#### GID 0인 모든 사용자 찾기

```bash
# 모든 사용자의 그룹 정보에서 GID 0 확인
for user in $(cut -d: -f1 /etc/passwd); do
    groups $user 2>/dev/null | grep -q '\b0\b' && echo "$user is in GID 0"
done
```

### 3. 조치 방법

#### Solaris, Linux, HP-UX 설정

1. **제거할 계정 확인**
   ```bash
   grep '^root:' /etc/group
   grep admin1 /etc/passwd
   ```

2. **gpasswd 명령어로 계정 제거**
   ```bash
   # root 그룹에서 불필요한 계정 제거
   gpasswd -d admin1 root
   ```

3. **여러 계정 일괄 제거**
   ```bash
   for user in admin1 admin2 developer; do
       gpasswd -d $user root
       echo "$user을 root 그룹에서 제거"
   done
   ```

#### AIX 설정

1. **chgrpmem 명령어로 계정 제거**
   ```bash
   chgrpmem -m - admin1 root
   ```

2. **SMIT를 통한 제거 (권장)**
   ```bash
   smit chgroup
   ```

#### 계정의 보조 그룹 재설정

```bash
# wheel 그룹에만 속하도록 변경 (admin1이 관리자인 경우)
usermod -G wheel admin1

# 또는 일반 사용자로 변경
usermod -G admin1 admin1
```

### 4. 참고 자료

- [Red Hat - Managing Groups in Linux](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/)
- [Ubuntu - Users and Groups](https://ubuntu.com/server/docs/security-users)
- [CIS Benchmark - Ensure no local interactive user has .rhosts files](https://www.cisecurity.org/cis-benchmarks/)
- [NIST AC-6 - Least Privilege](https://csrc.nist.gov/projects/universal-cybersecurity-controls/least-privilege)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.