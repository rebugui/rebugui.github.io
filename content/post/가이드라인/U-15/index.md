---
title: "[2026 주요정보통신기반시설] U-15 파일 및 디렉터리 소유자 설정"
slug: "2026-주정통/U-15"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "소유자가존재하지않는파일및디렉터리의존재여부점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-15 파일 및 디렉터리 소유자 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-15 |
| **점검내용** | 소유자가존재하지않는파일및디렉터리의존재여부점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX등 |
| **양호기준** | 소유자가존재하지않는파일및디렉터리가존재하지않는경우 |
| **취약기준** | 소유자가존재하지않는파일및디렉터리가존재하는경우 |
| **조치방법** | 소유자가존재하지않는파일및디렉터리제거또는소유자변경설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 소유자가 존재하지 않는 파일 및 디렉터리가 존재하지 않는 경우
- **취약**: 소유자가 존재하지 않는 파일 및 디렉터리가 존재하는 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| no user 파일 없음 | 양호 | 정상 상태 |
| no user 파일 존재 | 취약 | 제거 또는 소유자 변경 필요 |
| no group 파일 없음 | 양호 | 정상 상태 |
| no group 파일 존재 | 취약 | 제거 또는 그룹 변경 필요 |
| 퇴직자 파일 남음 | 취약 | 보안 위험 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| 모든 OS | no user 파일 점검 | 주 1회 | find 명령어 활용 |
| 모든 OS | no group 파일 점검 | 주 1회 | find 명령어 활용 |
| 모든 OS | 퇴직자 처리 | 즉시 | 소유자 변경 또는 제거 |

### 2. 점검 방법

#### Solaris, Linux, AIX, HP-UX 점검

소유자가 존재하지 않는 파일 및 디렉터리(no user, no group)를 식별하고 관리해야 합니다.

```bash
# 소유자와 그룹이 존재하지 않는 파일 및 디렉터리 확인
find / \( -nouser -o -nogroup \) -xdev -ls 2>/dev/null

# 또는
find / -nouser -o -nogroup 2>/dev/null

# 특정 디렉터리만 검색
find /home -nouser -o -nogroup 2>/dev/null

# 소유자가 없는 파일만
find / -nouser -ls 2>/dev/null

# 그룹이 없는 파일만
find / -nogroup -ls 2>/dev/null
```

**양호 출력 예시:**
```text
# 검색 결과 없음
(출력 없음)
```

**취약 출력 예시:**
```text
# no user 파일 발견
123456    0 -rw-r-----   1 1001    wheel        0 Jan 20 10:00 /tmp/orphaned_file
# UID 1001인 사용자가 존재하지 않음
```

#### 종합 점검 스크립트

```bash
#!/bin/bash
# no user/nogroup 파일 점검

echo "===== 소유자가 없는 파일 점검 ====="

# no user 파일 찾기
echo "소유자가 없는 파일:"
find / -nouser -ls 2>/dev/null | head -20

# no group 파일 찾기
echo "그룹이 없는 파일:"
find / -nogroup -ls 2>/dev/null | head -20
```

### 3. 조치 방법

#### Solaris, Linux, AIX, HP-UX 공통 설정

1. **파일 목록 확인**
   ```bash
   find / \( -nouser -o -nogroup \) -xdev -ls 2>/dev/null
   ```

2. **불필요한 파일 또는 디렉터리 제거**
   ```bash
   rm <filename>
   rm -r <directory_name>
   ```

3. **사용 중인 파일 및 디렉터리의 경우 소유자 및 그룹 변경**
   ```bash
   # 소유자 변경
   chown <username> <filename_or_directory>

   # 그룹 변경
   chgrp <groupname> <filename_or_directory>

   # 예시: root 소유자로 변경
   chown root /tmp/orphaned_file
   chgrp root /tmp/orphaned_file

   # 또는 한 번에 변경
   chown root:root /tmp/orphaned_file
   ```

4. **일괄 처리 스크립트**
   ```bash
   # no user 파일을 root 소유로 일괄 변경
   find / -nouser -exec chown root:root {} \; 2>/dev/null

   # no group 파일을 root 그룹으로 일괄 변경
   find / -nogroup -exec chgrp root {} \; 2>/dev/null
   ```

### 4. 참고 자료

- **-nouser**: 소유자가 존재하지 않는 파일
- **-nogroup**: 그룹이 존재하지 않는 파일
- **-xdev**: 다른 파일 시스템은 검색하지 않음

**점검 예시:**
```bash
$ ls -l /tmp/orphaned_file
-rw-r--r-- 1 1001 1001 0 Jan 20 10:00 /tmp/orphaned_file
# UID 1001과 GID 1001이 존재하지 않는 경우 숫자로 표시됨
```

- [CIS Benchmark - Find no user files](https://www.cisecurity.org/cis-benchmarks/)
- [NIST AC-3 - Access Enforcement](https://csrc.nist.gov/projects/risk-management/risk-management-encyclopedia)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.