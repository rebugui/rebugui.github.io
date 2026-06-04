---
title: "[2026 주요정보통신기반시설] U-26 /dev에 존재하지 않는 device 파일 점검"
slug: "2026-주정통/U-26"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "/dev 디렉터리 내 존재하지 않는 device 파일 점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-26 /dev에 존재하지 않는 device 파일 점검

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-26 |
| **점검내용** | /dev 디렉터리 내 존재하지 않는 device 파일 점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX 등 |
| **양호기준** | /dev 디렉터리에 대한 파일 점검 후 존재하지 않는 device 파일을 제거한 경우 |
| **취약기준** | /dev 디렉터리에 대한 파일 미점검 또는 존재하지 않는 device 파일을 방치한 경우 |
| **조치방법** | major, minor number를 가지지 않는 device 파일 제거 설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: `/dev` 디렉터리에 device 파일(Block/Character Device 등)이 아닌 일반 파일이 존재하지 않는 경우
- **취약**: `/dev` 디렉터리에 device 파일이 아닌 일반 파일이 존재하거나, 의심스러운 파일이 발견된 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| /dev/MAKEDEV 스크립트 | 정상 | 구형 시스템의 정상 스크립트 |
| /dev/shm 내 파일 | 정상 | 공유 메모리 영역 |
| /dev/.udev 디렉터리 | 정상 | udev 관련 임시 파일 |
| /dev/sd*와 같은 일반 파일 | 취약 | 디스크 파티션 이름 위조 가능성 |
| /dev/.hidden/ | 취약 | 루트킷 은신처 |
| /dev/tcp (일반 파일) | 취약 | 백도어 가능성 |
| /dev/.. (공백 포함) | 취약 | 숨김 기법 |

#### 권장 설정값

| 파일 유형 | 검색 위치 | 허용 여부 | 비고 |
|------------|------------|---------------|------|
| Character Device | /dev/* | 허용 | c로 시작하는 파일 |
| Block Device | /dev/* | 허용 | b로 시작하는 파일 |
| Symbolic Link | /dev/* | 허용 | l로 시작하는 파일 |
| Directory | /dev/* | 허용 | d로 시작하는 파일 (/dev/shm 등) |
| 일반 파일 (Regular File) | /dev/* | 제거 | f로 시작하는 파일 |
| Socket | /dev/* | 허용 | s로 시작하는 파일 |
| FIFO (Named Pipe) | /dev/* | 허용 | p로 시작하는 파일 |

### 2. 점검 방법

#### Linux, Solaris, AIX, HP-UX 점검

`/dev` 디렉터리 내에서 '일반 파일(Regular File)'을 검색합니다.

```bash
find /dev -type f -exec ls -l {} \;
```

- `-type f`: 디렉터리(`d`), 블록 디바이스(`b`), 문자 디바이스(`c`), 소켓(`s`), 파이프(`p`) 등이 아닌 **일반 파일**만 검색합니다.

**양호 출력 예시:**
```text
(출력 내용 없음 - 일반 파일이 없어야 함)
```

**취약 출력 예시:**
```text
-rw-r--r-- 1 root root 12345 Jan 20 10:00 /dev/.hidden
-rwxr-xr-x 1 root root 5678 Jan 20 10:00 /dev/tcp0
-rw------- 1 root root 9012 Jan 20 10:00 /dev/sda1
```
(/dev 내에 일반 파일이 존재함 - 루트킷/백도어 가능성)

### 3. 조치 방법

#### 의심 파일 확인 및 삭제

1. **file 명령어로 파일의 종류를 재확인**
   ```bash
   file /dev/suspect_file
   ```

2. **파일의 생성 시간, 내용을 확인하여 악성 여부를 판단**
   ```bash
   ls -l /dev/suspect_file
   stat /dev/suspect_file
   ```

3. **내용 확인 (텍스트 파일인 경우)**
   ```bash
   strings /dev/suspect_file | head -20
   ```

4. **불필요하거나 악성 파일로 판단되면 삭제**
   ```bash
   rm /dev/suspect_file
   ```

5. **숨겨진 디렉터리 삭제**
   ```bash
   rm -rf /dev/.hidden/
   ```

### 4. 참고 자료

- **CIS Benchmarks**: 6.1.14 Find unauthorized device files
- **NIST 800-53**: CM-6 (Configuration Settings), SI-4 (System Monitoring)
- **Linux Device Files**: https://www.kernel.org/doc/html/latest/admin-guide/devices.html
- **man page**: `man find`, `man file`

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.