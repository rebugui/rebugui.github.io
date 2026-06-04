---
title: "[2026 주요정보통신기반시설] U-16 /etc/passwd 파일 소유자 및 권한 설정"
slug: "2026-주정통/U-16"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "/etc/passwd파일권한적절성여부점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-16 /etc/passwd 파일 소유자 및 권한 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-16 |
| **점검내용** | /etc/passwd파일권한적절성여부점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX등 |
| **양호기준** | /etc/passwd파일의소유자가root이고,권한이644이하인경우 |
| **취약기준** | /etc/passwd파일의소유자가root가아니거나,권한이644이하가아닌경우 |
| **조치방법** | /etc/passwd파일소유자및권한변경설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: `/etc/passwd` 파일의 소유자가 root이고, 권한이 644 이하인 경우
- **취약**: `/etc/passwd` 파일의 소유자가 root가 아니거나, 권한이 644 이하가 아닌 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| 소유자 root, 권한 644 | 양호 | 정상적인 설정 |
| 소유자 root, 권한 600 | 양호 | 더 보안 강화된 설정 |
| 소유자가 root가 아님 | 취약 | 즉시 수정 필요 |
| 권한 666 | 취약 | 모든 사용자 쓰기 가능 |
| 권한 777 | 취약 | 심각한 보안 위험 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| 모든 OS | 소유자 | root | root만 소유자 |
| 모든 OS | 권한 | 644 (rw-r--r--) | 소유자는 읽기/쓰기, 다른 사용자는 읽기만 |

### 2. 점검 방법

#### Solaris, Linux, AIX, HP-UX 점검

`/etc/passwd` 파일은 시스템의 모든 사용자 계정 정보를 담고 있는 중요한 파일입니다.

```bash
# /etc/passwd 파일 소유자 및 권한 확인
ls -l /etc/passwd
```

**양호 출력 예시:**
```text
-rw-r--r-- 1 root root 2048 Jan 20 10:00 /etc/passwd
# 소유자: root, 권한: 644 (양호)
```

**취약 출력 예시:**
```text
-rw-rw-rw- 1 root root 2048 Jan 20 10:00 /etc/passwd
# 권한: 666 (취약)

-rw-r--r-- 1 admin1 root 2048 Jan 20 10:00 /etc/passwd
# 소유자: admin1 (취약)
```

### 3. 조치 방법

#### Solaris, Linux, AIX, HP-UX 공통 설정

1. **/etc/passwd 파일 소유자 및 권한 확인**
   ```bash
   ls -l /etc/passwd
   ```

2. **/etc/passwd 파일 소유자 및 권한 변경**
   ```bash
   chown root /etc/passwd
   chmod 644 /etc/passwd
   ```

3. **변경 확인**
   ```bash
   ls -l /etc/passwd
   ```

### 4. 참고 자료

**/etc/passwd 파일 구조:**
```
username:password:UID:GID:GECOS:home_directory:shell
```

| 필드 | 설명 |
|------|------|
| username | 사용자 계정명 |
| password | 'x'로 표시 (실제 비밀번호는 /etc/shadow) |
| UID | 사용자 식별 번호 |
| GID | 그룹 식별 번호 |
| GECOS | 사용자 정보 (이름, 전화번호 등) |
| home_directory | 홈 디렉터리 경로 |
| shell | 로그인 쉘 |

**권한 644 의미:**
- 6 (rw-): 소유자는 읽기, 쓰기 가능
- 4 (r--): 그룹은 읽기만 가능
- 4 (r--): 기타 사용자는 읽기만 가능

- [CIS Benchmark - Ensure permissions on /etc/passwd are configured](https://www.cisecurity.org/cis-benchmarks/)
- [NIST AC-6 - Least Privilege](https://csrc.nist.gov/projects/universal-cybersecurity-controls/least-privilege)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.