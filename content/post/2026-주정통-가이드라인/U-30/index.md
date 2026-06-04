---
title: "[2026 주요정보통신기반시설] U-30 UMASK 설정 관리"
slug: "2026-주정통/U-30"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "시스템 UMASK 값이 022 이상 설정 여부 점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-30 UMASK 설정 관리

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-30 |
| **점검내용** | 시스템 UMASK 값이 022 이상 설정 여부 점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX 등 |
| **양호기준** | UMASK 값이 022 이상으로 설정된 경우 |
| **취약기준** | UMASK 값이 022 미만으로 설정된 경우 |
| **조치방법** | 설정 파일에 UMASK 값을 022로 설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: UMASK 값이 022 이상인 경우 (예: 022, 027, 077 등)
- **취약**: UMASK 값이 022 미만인 경우 (예: 000, 002 등)

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| UMASK 022 | 양호 | 표준 보안 설정 |
| UMASK 027 | 양호 | 그룹도 쓰기 불가 - 더 보수적 |
| UMASK 077 | 양호 | 소유자만 접근 - 최고 보안 |
| UMASK 002 | 취약 | 기타 사용자 쓰기 가능 |
| UMASK 000 | 취약 (매우 위험) | 모두가 읽기/쓰기 가능 |
| 사용자별 .bashrc에 UMASK 002 | 취약 | 시스템 전체 설정보다 우선함 |
| /etc/profile과 /etc/bashrc 충돌 | 주의 | bashrc 설정이 우선적용될 수 있음 |
| FTP 서버 계정 | 예외 | 파일 공유를 위해 002 필요할 수 있음 |

#### 권장 설정값

| 환경 | 설정 파일 | 권장 UMASK | 생성 파일 권한 | 생성 디렉터리 권한 |
|------------|------------|---------------|------|------|
| Linux 시스템 전체 | /etc/profile, /etc/bashrc | 022 | 644 (rw-r--r--) | 755 (rwxr-xr-x) |
| Linux 시스템 전체 (보안 강화) | /etc/profile, /etc/bashrc | 027 | 640 (rw-r-----) | 750 (rwxr-x---) |
| Linux 시스템 전체 (최고 보안) | /etc/profile, /etc/bashrc | 077 | 600 (rw-------) | 700 (rwx------) |
| Solaris | /etc/profile, /etc/default/login | 022 | 644 | 755 |
| AIX | /etc/profile, /etc/security/user | 022 | 644 | 755 |
| HP-UX | /etc/profile, /etc/default/security | 022 | 644 | 755 |

### 2. 점검 방법

#### Solaris, Linux, AIX, HP-UX 점검

1. **현재 쉘에서의 확인**
   ```bash
   # 현재 적용된 UMASK 값 확인
   umask

   # 결과 예시:
   # 0022 (양호)
   # 0002 (취약 - 기타 사용자에게 쓰기 권한 부여됨)
   ```

2. **설정 파일 확인**
   ```bash
   # 전역 설정 파일 확인
   grep -i umask /etc/profile
   grep -i umask /etc/bashrc
   grep -i umask /etc/csh.login
   grep -i umask /etc/csh.cshrc
   grep -i umask /etc/login.defs  # (Linux)
   grep -i umask /etc/default/login # (Solaris)

   # 사용자별 설정 파일 확인 (필요 시)
   cat ~/.bash_profile
   cat ~/.profile
   cat ~/.cshrc
   cat ~/.login
   ```

**양호 출력 예시:**
```text
umask 022
```

**취약 출력 예시:**
```text
umask 000
```
또는
```text
umask 002
```

### 3. 조치 방법

#### Solaris 설정

1. **`/etc/profile` 수정**
   ```bash
   vi /etc/profile

   # 다음 내용 추가 또는 수정
   umask 022
   export umask
   ```

2. **`/etc/default/login` 수정**
   ```bash
   vi /etc/default/login

   # 다음 내용 추가 또는 수정
   UMASK=022
   ```

#### Linux 설정

1. **`/etc/profile` 수정**
   ```bash
   vi /etc/profile

   # 맨 하단에 추가
   umask 022
   export umask
   ```

2. **`/etc/bashrc` 수정 (RedHat 계열)**
   ```bash
   vi /etc/bashrc

   # umask 000 또는 002로 되어 있는 부분을 022로 수정
   ```

3. **`/etc/login.defs` 수정 (일부 배포판)**
   ```bash
   vi /etc/login.defs

   UMASK 022
   ```

#### AIX 설정

1. **`/etc/profile` 수정**
   ```bash
   vi /etc/profile

   umask 022
   export umask
   ```

2. **`/etc/security/user` 수정**
   ```bash
   vi /etc/security/user

   default:
       umask = 022
   ```

#### HP-UX 설정

1. **`/etc/profile` 수정**
   ```bash
   vi /etc/profile

   umask 022
   export umask
   ```

2. **`/etc/default/security` 수정**
   ```bash
   vi /etc/default/security

   UMASK=022
   ```

### 4. 참고 자료

- **CIS Benchmarks**: 5.1.7 Ensure default umask for users is 027 or more restrictive
- **NIST 800-53**: AC-6 (Least Privilege), CM-6 (Configuration Settings)
- **man page**: `man umask`

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.