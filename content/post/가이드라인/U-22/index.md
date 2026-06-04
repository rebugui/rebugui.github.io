---
title: "[2026 주요정보통신기반시설] U-22 /etc/services 파일 소유자 및 권한 설정"
slug: "2026-주정통/U-22"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "/etc/services 파일 권한 적절성 여부 점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-22 /etc/services 파일 소유자 및 권한 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-22 |
| **점검내용** | /etc/services 파일 권한 적절성 여부 점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX 등 |
| **양호기준** | /etc/services 파일의 소유자가 root(또는 bin, sys)이고, 권한이 644 이하인 경우 |
| **취약기준** | /etc/services 파일의 소유자가 root(또는 bin, sys)가 아니거나, 권한이 644 이하가 아닌 경우 |
| **조치방법** | /etc/services 파일 소유자 및 권한 변경 설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 파일의 소유자가 root(또는 bin, sys)이고, 권한이 644 이하인 경우
- **취약**: 파일의 소유자가 root(또는 bin, sys)가 아니거나, 권한이 644 보다 높은 경우 (예: 666, 777)

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| 권한이 600인 경우 | 양호 | 644보다 더 엄격한 권한으로 허용 (단, 일부 애플리케이션에서 읽기 불가능할 수 있음) |
| 권한이 640인 경우 | 양호 | 그룹만 읽기 가능하며 안전함 |
| 심볼릭 링크인 경우 | 주의 | 원본 파일의 권한을 확인해야 함 |
| 소유자가 bin 또는 sys인 경우 | 양호 | Solaris 등 일부 유닉스 시스템에서는 정상적인 소유자 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| Linux/Solaris/AIX/HP-UX | 파일 소유자 | root | bin 또는 sys도 허용 |
| Linux/Solaris/AIX/HP-UX | 파일 권한 | 644 (rw-r--r--) | 모든 사용자가 읽기 가능, 소유자만 쓰기 가능 |
| Linux/Solaris/AIX/HP-UX | 최소 권한 | 640 (rw-r-----) | 일부 애플리케이션에서 문제될 수 있음 |

### 2. 점검 방법

#### Linux, Solaris, AIX, HP-UX 점검

시스템의 `/etc/services` 파일 권한과 소유자를 확인합니다.

```bash
ls -l /etc/services
```

**양호 출력 예시:**
```text
-rw-r--r-- 1 root root 670293 Jan 20 10:00 /etc/services
```
(소유자 root, 권한 644)

**취약 출력 예시:**
```text
-rw-rw-rw- 1 root root 670293 Jan 20 10:00 /etc/services
```
(권한 666 - 누구나 수정 가능)

**취약 출력 예시 2:**
```text
-rwxrwxrwx 1 user root 670293 Jan 20 10:00 /etc/services
```
(소유자가 root가 아님, 권한 777)

### 3. 조치 방법

#### Linux, Solaris, AIX, HP-UX 설정

1. **파일 소유자를 root로 변경**
   ```bash
   chown root /etc/services
   ```

2. **파일 권한을 644로 변경**
   ```bash
   chmod 644 /etc/services
   ```

### 4. 참고 자료

- **CIS Benchmarks**: 6.1.2 Ensure permissions on /etc/services are configured
- **NIST 800-53**: CM-7 (Least Functionality), SC-7 (Network Protection)
- **IANA Port Numbers**: https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml
- **man page**: `man services`

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.