---
title: "[2026 주요정보통신기반시설] U-23 SUID, SGID, Sticky bit 설정 파일 점검"
slug: "2026-주정통/U-23"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "불필요하거나 악의적인 파일에 SUID, SGID, Sticky bit 설정 여부 점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
draft: true
---

# U-23 SUID, SGID, Sticky bit 설정 파일 점검

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-23 |
| **점검내용** | 불필요하거나 악의적인 파일에 SUID, SGID, Sticky bit 설정 여부 점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX 등 |
| **양호기준** | 주요 실행파일의 권한에 SUID와 SGID에 대한 설정이 부여되어 있지 않은 경우 (불필요한 경우 제거) |
| **취약기준** | 주요 실행파일의 권한에 SUID와 SGID에 대한 설정이 부여된 경우 (불필요한 경우 미제거) |
| **조치방법** | 불필요한 SUID, SGID 권한 제거 또는 해당 파일 제거 설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 시스템 운영에 불필요한 파일에 SUID/SGID 설정이 제거되어 있는 경우
- **취약**: 시스템 운영에 불필요한 파일에 SUID/SGID 설정이 되어 있는 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| /usr/bin/passwd에 SUID 설정 | 정상 (필수) | 비밀번호 변경을 위해 root 권한이 필요함 |
| /bin/ping에 SUID 설정 | 정상 (일반) | ICMP 패킷 전송을 위해 root 권한 필요 (최신 리눅스는 capabilities 사용) |
| /bin/su에 SUID 설정 | 정상 (필수) | 사용자 전환을 위해 root 권한 필요 |
| /usr/bin/sudo에 SUID 설정 | 정상 (필수) | 권한 상승을 위해 root 권한 필요 |
| /usr/bin/newgrp에 SGID 설정 | 제거 권장 | 일반 사용자에게 불필요할 수 있음 |
| /tmp 디렉터리의 Sticky bit | 정상 (필수) | 다른 사용자의 파일 삭제 방지 |
| 홈 디렉터리에 숨겨진 SUID 파일 | 취약 | 루트킷/백도어 가능성 높음 |
| /dev/ 디렉터리 내 일반 파일에 SUID | 취약 | 악성 파일 가능성极高 |
| /var/tmp, /tmp 내 SUID 파일 | 취약 | 악성 파일 가능성极高 |

#### 권장 설정값 (반드시 제거해야 할 불필요 SUID/SGID 파일 목록)

| 파일 경로 | 권한 | 설명 | 조치 |
|------------|------------|---------------|------|
| /usr/bin/newgrp | SGID | 그룹 변경, 일반 사용자 불필요 | 제거 권장 |
| /sbin/dump | SUID | 백업 도구, 일반 사용자 불필요 | 제거 권장 |
| /sbin/restore | SUID | 백업 복구, 일반 사용자 불필요 | 제거 권장 |
| /usr/bin/lpq | SUID | 프린터 큐, 대체책 존재 | 제거 권장 |
| /usr/bin/lprm | SUID | 프린터 삭제, 대체책 존재 | 제거 권장 |
| /usr/bin/lpd | SUID | 프린터 데몬, 사용자 실행 불필요 | 제거 권장 |
| /usr/bin/uucp* | SUID/SGID | UUCP 프로토콜, 레거시 | 제거 권장 |

#### 반드시 유지해야 할 필수 SUID 파일

| 파일 경로 | 권한 | 설명 |
|------------|------------|---------------|------|
| /usr/bin/passwd | SUID | 비밀번호 변경 (필수) |
| /bin/su | SUID | 사용자 전환 (필수) |
| /usr/bin/sudo | SUID | 권한 상승 (필수) |
| /bin/ping | SUID | 네트워크 확인 (일반) |
| /usr/bin/gpasswd | SUID | 그룹 비밀번호 (일반) |

### 2. 점검 방법

#### Linux, Solaris, AIX, HP-UX 점검

시스템 전체에서 SUID 또는 SGID가 설정된 파일을 검색합니다.

```bash
find / -user root -type f \( -perm -04000 -o -perm -02000 \) -xdev -exec ls -al {} \;
```

- `-perm -04000`: SUID 설정된 파일 검색
- `-perm -02000`: SGID 설정된 파일 검색
- `-xdev`: 다른 파일 시스템(파티션)으로 건너뛰지 않음

**양호 출력 예시:**
```text
-rwsr-xr-x 1 root root 67936 Jan 20 10:00 /usr/bin/passwd
-rwsr-xr-x 1 root root 143120 Jan 20 10:00 /usr/bin/sudo
-rwsr-xr-x 1 root root 42280 Jan 20 10:00 /bin/su
-rwsr-xr-x 1 root root 72632 Jan 20 10:00 /bin/ping
```
(필수 SUID 파일만 존재)

**취약 출력 예시:**
```text
-rwsr-xr-x 1 root root 67936 Jan 20 10:00 /usr/bin/passwd
-rwsr-xr-x 1 root root 42280 Jan 20 10:00 /bin/su
-rwsr-xr-x 1 root root 12345 Jan 20 10:00 /tmp/.hidden/backdoor
-rwsr-xr-x 1 root root 52160 Jan 20 10:00 /usr/bin/newgrp
```
(/tmp/.hidden/backdoor - 의심스러운 백도어, newgrp - 불필요한 SGID)

### 3. 조치 방법

#### 불필요한 SUID/SGID 제거

1. **파일의 특수 권한(SUID, SGID) 제거**
   ```bash
   chmod -s /usr/sbin/usernetctl
   ```

2. **권한을 직접 지정**
   ```bash
   chmod 755 /usr/bin/newgrp
   ```

3. **특정 그룹만 실행 가능하도록 제한**
   ```bash
   chgrp admin /usr/sbin/usernetctl
   chmod 4750 /usr/sbin/usernetctl
   ```

4. **불필요한 파일 삭제**
   ```bash
   rm /tmp/.hidden/backdoor
   rm -rf /dev/.hidden/
   ```

### 4. 참고 자료

- **CIS Benchmarks**: 6.1.11 Find SUID/SGID files and system files
- **NIST 800-53**: AC-3 (Access Enforcement), AC-6 (Least Privilege)
- **Linux Capabilities**: https://man7.org/linux/man-pages/man7/capabilities.7.html
- **man page**: `man chmod`, `man find`

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.