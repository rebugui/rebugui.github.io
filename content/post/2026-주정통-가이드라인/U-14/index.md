---
title: "[2026 주요정보통신기반시설] U-14 root 홈, 패스 디렉터리 권한 및 패스 설정"
slug: "2026-주정통/U-14"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "root 계정의PATH환경변수에'.'(마침표)이포함여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
draft: true
---

# U-14 root 홈, 패스 디렉터리 권한 및 패스 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-14 |
| **점검내용** | root 계정의PATH환경변수에'.'(마침표)이포함여부점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX등 |
| **양호기준** | PATH환경변수에'.'이맨앞이나중간에포함되지않은경우 |
| **취약기준** | PATH환경변수에'.'이맨앞이나중간에포함된경우 |
| **조치방법** | root 계정의환경설정파일(/.profile, /.bashrc 등)과 시스템환경설정파일(/etc/profile등)에설정된PATH환경변수에서현재디렉터리를나타내는'.'을PATH환경변수의마지막으로이동하도록설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: PATH 환경변수에 '.'이 맨 앞이나 중간에 포함되지 않은 경우
- **취약**: PATH 환경변수에 '.'이 맨 앞이나 중간에 포함된 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| PATH=.:/usr/bin:/bin | 취약 | '.'이 맨 앞에 위치 |
| PATH=/usr/bin:.:/bin | 취약 | '.'이 중간에 위치 |
| PATH=/usr/bin:/bin | 양호 | '.'이 없음 |
| PATH=/usr/bin:/bin:. | 주의 | '.'이 끝에 위치 (권장하지 않음) |
| PATH=/usr/bin:/bin:. | 취약 | 끝에 있어도 보안 위험 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| root 계정 | PATH | /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin | '.' 제거 |
| 일반 사용자 | PATH | /usr/local/bin:/usr/bin:/bin:/usr/local/games:/usr/games | '.' 제거 |
| /etc/profile | PATH | . 제거 또는 맨 뒤로 이동 | 시스템 전체 적용 |

### 2. 점검 방법

#### Solaris, Linux, AIX, HP-UX 점검

PATH 환경변수에 현재 디렉터리를 나타내는 '.'이 맨 앞이나 중간에 포함되어 있지 않은지 확인해야 합니다.

```bash
# PATH 환경변수 확인
echo $PATH

# 환경설정 파일 확인
grep PATH /root/.bash_profile
grep PATH /root/.profile
grep PATH /etc/profile
```

**양호 출력 예시:**
```text
$ echo $PATH
/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# '.'이 없거나, 끝에 있어도 사용하지 않음
```

**취약 출력 예시:**
```text
$ echo $PATH
.:/usr/bin:/bin
# '.'이 맨 앞에 위치 (취약)

$ echo $PATH
/usr/bin:.:/bin
# '.'이 중간에 위치 (취약)
```

#### 환경설정 파일 확인

```bash
# /etc/profile 확인
grep -n "PATH" /etc/profile | grep "^\s*PATH="

# 사용자별 설정 확인
grep -n "PATH" /root/.bash_profile | grep "^\s*PATH="
grep -n "PATH" /root/.profile | grep "^\s*PATH="
```

### 3. 조치 방법

#### Solaris, Linux, AIX, HP-UX 공통 설정

1. **환경설정 파일 내 PATH 변숫값 수정**
   ```bash
   # 상대 경로 삭제 또는 PATH 끝으로 이동
   vi /root/.bash_profile
   # 또는
   vi /root/.profile

   # PATH 수정 (취약 예시)
   # PATH=.:/usr/bin:/bin

   # PATH 수정 (양호 예시) - 상대 경로 삭제
   # PATH=/usr/bin:/bin:/usr/local/bin

   # 또는 상대 경로를 끝으로 이동
   # PATH=/usr/bin:/bin:/usr/local/bin:.

   # 설정 적용
   source /root/.bash_profile
   ```

2. **/etc/profile 수정 (시스템 전체 적용)**
   ```bash
   vi /etc/profile

   # PATH 설정 수정
   # 변경 전: PATH=.:/usr/bin:/bin
   # 변경 후: PATH=/usr/bin:/bin:/usr/local/bin

   source /etc/profile
   ```

### 4. 참고 자료

**Shell종류별 환경설정 파일:**

| Shell종류 | 시스템 전체 | 사용자별 |
|-----------|-----------|----------|
| Bourne Shell(sh) | /etc/profile | $HOME/.profile |
| C Shell(csh) | /etc/csh.cshrc, /etc/csh.login | $HOME/.cshrc, $HOME/.login |
| Korn Shell(ksh) | /etc/profile | $HOME/.profile, $HOME/.kshrc |
| Bash Shell(bash) | /etc/profile, $HOME/.bash_profile, $HOME/.bashrc | /etc/bash.bashrc |

- [CIS Benchmark - Ensure PATH does not include '.'](https://www.cisecurity.org/cis-benchmarks/)
- [NIST CM-6 - Configuration Settings](https://csrc.nist.gov/projects/risk-management/risk-management-encyclopedia)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.