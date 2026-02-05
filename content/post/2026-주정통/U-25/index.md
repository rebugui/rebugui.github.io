---
title: "[2026 주요정보통신기반시설] U-25 world writable 파일 점검"
slug: "2026-주정통/U-25"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "불필요한 world writable 파일 여부 점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-25 world writable 파일 점검

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-25 |
| **점검내용** | 불필요한 world writable 파일 여부 점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX 등 |
| **양호기준** | world writable 파일이 존재하지 않거나, 존재 시 설정 이유를 인지하고 있는 경우 |
| **취약기준** | world writable 파일이 존재하나 설정 이유를 인지하지 못하고 있는 경우 |
| **조치방법** | world writable 파일 존재 여부를 확인하고 불필요한 경우 제거 설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 시스템 운영에 반드시 필요한 경우를 제외하고 World Writable 파일이 존재하지 않는 경우
- **취약**: 시스템 운영과 무관하게 World Writable 파일이 존재하는 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| /dev/null, /dev/zero | 정상 | 디바이스 파일은 world writable 필요 |
| /tmp 디렉터리 내 파일 | 주의 | 임시 파일이지만 일반 파일은 점검 필요 |
| /dev/shm 내 파일 | 주의 | 공유 메모리이지만 일반 파일은 점검 필요 |
| 소켓 파일 (.socket) | 정상 | 소켓은 제외 |
| 파이프 파일 (fifo) | 정상 | 파이프는 제외 |
| 로그 파일에 world writable | 취약 | 권한 조정 필요 |
| 설정 파일에 world writable | 취약 | 반드시 제거 필요 |
| 실행 파일에 world writable | 취약 | 매우 위험, 즉시 제거 |
| /proc, /sys 내 파일 | 제외 | 가상 파일 시스템으로 제외 |

#### 권장 설정값

| 파일 유형 | 위치 | 권장 권한 | 비고 |
|------------|------------|---------------|------|
| 설정 파일 | /etc/*.conf | 644 (rw-r--r--) 또는 640 | 일반 사용자 쓰기 불가 |
| 실행 파일 | /usr/bin/* | 755 (rwxr-xr-x) 또는 750 | 일반 사용자 쓰기 불가 |
| 로그 파일 | /var/log/* | 644 또는 600 | 일반 사용자 쓰기 불가 |
| 임시 디렉터리 | /tmp | 1777 (sticky bit) | 디렉터리는 sticky bit 필수 |
| 데이터베이스 파일 | /var/lib/* | 660 또는 600 | 소유자와 그룹만 접근 |

### 2. 점검 방법

#### Linux, Solaris, AIX, HP-UX 점검

시스템 전체에서 일반 파일(File)이면서 기타 사용자(Other)에게 쓰기(Writable) 권한이 있는 파일을 검색합니다.

```bash
find / -type f -perm -002 -exec ls -l {} \;
```

- `-type f`: 디렉터리가 아닌 일반 파일만 검색
- `-perm -002`: Others 권한에 Write 비트(2)가 설정된 파일 검색

**더 정제된 검색 명령어:**
```bash
# 가상 파일 시스템 제외하고 검색
find / -path /proc -prune -o -path /sys -prune -o -type f -perm -002 -ls

# 특정 디렉터리만 검색
find /etc /home /var -type f -perm -002 -ls
```

**양호 출력 예시:**
```text
(출력 없음 또는 /dev 관련 항목만 출력)
```

**취약 출력 예시:**
```text
-rwxrwxrwx 1 root root 1234 Jan 20 10:00 /etc/app/config.conf
-rw-rw-rw- 1 root root 5678 Jan 20 10:00 /home/user/.bashrc
-rwxrwxrwx 1 root root 9012 Jan 20 10:00 /usr/local/bin/script.sh
```

### 3. 조치 방법

#### 불필요한 World Writable 권한 제거

1. **해당 파일의 Others 쓰기 권한 제거**
   ```bash
   chmod o-w /path/to/vulnerable_file
   ```

2. **그룹 쓰기 권한도 제거 (필요 시)**
   ```bash
   chmod go-w /path/to/vulnerable_file
   ```

3. **안전한 권한으로 설정**
   ```bash
   # 설정 파일
   chmod 644 /etc/app/config.conf

   # 실행 파일
   chmod 755 /usr/local/bin/script.sh

   # 사용자 환경 파일
   chmod 644 /home/user/.bashrc
   ```

4. **불필요한 파일 삭제**
   ```bash
   rm /path/to/unnecessary_file
   ```

5. **일괄 조치 스크립트**
   ```bash
   # World writable 파일에서 Others 쓰기 권한 일괄 제거
   find /etc /home /usr/local -type f -perm -002 -exec chmod o-w {} \;

   # /dev 제외하고 검색 및 조치
   find / -path /dev -prune -o -type f -perm -002 -exec chmod o-w {} \;
   ```

### 4. 참고 자료

- **CIS Benchmarks**: 6.1.10 Find world-writable files
- **NIST 800-53**: AC-6 (Least Privilege), CM-6 (Configuration Settings)
- **man page**: `man find`, `man chmod`

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.