---
title: "[2026 주요정보통신기반시설] U-55 FTP 계정 Shell 제한"
slug: "2026-주정통/U-55"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "FTP기본계정에쉘설정여부점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-55 FTP 계정 Shell 제한

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-55 |
| **점검내용** | FTP기본계정에쉘설정여부점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX등 |
| **양호기준** | FTP 계정에/bin/false(/sbin/nologin)쉘이부여된경우 |
| **취약기준** | FTP 계정에/bin/false(/sbin/nologin)쉘이부여되어있지않은경우 |
| **조치방법** | FTP서비스를사용하지않는경우서비스중지및비활성화설정, FTP 서비스사용시FTP계정에/bin/false쉘부여설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: FTP 계정의 쉘이 /sbin/nologin인 경우
- **취약**: FTP 계정이 /bin/bash 등으로 시스템 접속 가능한 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| 쉘이 /bin/bash | 취약 | SSH 로그인 가능 |
| 쉘이 /sbin/nologin | 양호 | FTP만 가능 |
| ftp 계정 없음 | 양호 | 서비스 미사용 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| Linux | FTP 사용자 쉘 | /sbin/nologin | usermod |
| Linux | /etc/shells | /sbin/nologin 포함 | 쉘 목록 |

### 2. 점검 방법

#### Linux 점검

```bash
# 1. FTP 계정 쉘 확인
echo "=== 1. FTP User Shells ==="
grep "^ftp" /etc/passwd
getent passwd ftp

# 2. /etc/shells 확인
echo "=== 2. /etc/shells ==="
grep nologin /etc/shells
```

**양호 출력 예시:**
```text
=== 1. FTP User Shells ===
ftp:x:14:50:FTP User:/var/ftp:/sbin/nologin
```

**취약 출력 예시:**
```text
=== 1. FTP User Shells ===
ftp:x:14:50:FTP User:/var/ftp:/bin/bash
```

### 3. 조치 방법

#### Shell 변경

```bash
# FTP 사용자 쉘 변경
usermod -s /sbin/nologin ftp

# /etc/passwd 확인
grep "^ftp" /etc/passwd

# /etc/shells에 추가 (필요 시)
echo "/sbin/nologin" >> /etc/shells
```

### 4. 참고 자료

- CIS Benchmark for Linux: FTP 제한 권고
- NIST SP 800-53: AC-6 (최소 권한)
- man pages: usermod(8), nologin(8)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.