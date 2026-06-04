---
title: "[2026 주요정보통신기반시설] U-12 세션 종료 시간 설정"
slug: "2026-주정통/U-12"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "사용자쉘에대한환경설정파일에서SessionTimeout설정여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-12 세션 종료 시간 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-12 |
| **점검내용** | 사용자쉘에대한환경설정파일에서SessionTimeout설정여부점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX등 |
| **양호기준** | Session Timeout이600초(10분)이하로설정된경우 |
| **취약기준** | Session Timeout이600초(10분)이하로설정되지않은경우 |
| **조치방법** | 600초(10분)동안입력이없는경우접속된Session을끊도록설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: Session Timeout이 600초(10분) 이하로 설정된 경우
- **취약**: Session Timeout이 600초(10분) 이하로 설정되지 않은 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| TMOUT=600 설정 | 양호 | 10분 타임아웃 |
| TMOUT=300 설정 | 양호 | 5분 타임아웃 (더 보안) |
| TMOUT=3600 설정 | 취약 | 1시간 (너무 김) |
| TMOUT 미설정 | 취약 | 무제한 세션 |
| 모니터링 서버 | 주의 | 예외 처리 필요 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| 일반 사용자 | TMOUT | 600초 (10분) | 표준 |
| 관리자 계정 | TMOUT | 300초 (5분) | 높은 보안 필요 |
| 공용 PC | TMOUT | 180~300초 (3~5분) | 물리적 접근 위험 높음 |
| 모니터링 서버 | TMOUT | 0 (무제한) 또는 3600초 | 예외 처리 필요 |

### 2. 점검 방법

#### Solaris, Linux, AIX, HP-UX 점검

사용자 쉘의 환경 설정 파일에서 Session Timeout 값이 설정되어 있는지 확인해야 합니다.

```bash
# sh, ksh, bash 쉘의 환경 설정 파일 확인
grep TMOUT /etc/profile
grep TMOUT ~/.bash_profile
grep TMOUT ~/.bashrc

# csh 쉘의 환경 설정 파일 확인
grep autologout /etc/csh.cshrc
```

**양호 출력 예시:**
```text
$ grep TMOUT /etc/profile
TMOUT=600
export TMOUT

$ echo $TMOUT
600
```

**취약 출력 예시:**
```text
$ grep TMOUT /etc/profile
# (출력 없음 - 설정되지 않음)

$ echo $TMOUT

# 또는 너무 긴 시간 설정
TMOUT=7200  # 2시간 - 취약
```

#### SSH 설정도 함께 확인

```bash
# SSH 서버 설정 확인
cat /etc/ssh/sshd_config | grep -E 'ClientAlive'

# 양호한 설정 예시
ClientAliveInterval 300
ClientAliveCountMax 3
```

### 3. 조치 방법

#### sh, ksh, bash 쉘 (시스템 전체 적용) 설정

1. **/etc/profile 설정**
   ```bash
   vi /etc/profile

   # 다음 내용 추가 또는 수정 (파일 끝부분에)
   # Session Timeout 설정 (10분)
   TMOUT=600
   export TMOUT

   # 또는 readonly로 설정하여 사용자가 변경 못하게
   readonly TMOUT
   export TMOUT

   # 설정 적용 (현재 세션)
   source /etc/profile
   ```

2. **사용자별 개별 설정**
   ```bash
   # 사용자 홈 디렉터리의 .bash_profile 또는 .bashrc에 추가
   vi ~/.bash_profile

   # 추가
   TMOUT=600
   export TMOUT

   # 또는 SSH 접속 시에만 적용
   if [ "$SSH_CONNECTION" ]; then
       TMOUT=600
       export TMOUT
   fi
   ```

#### csh 쉘 설정

```bash
# /etc/csh.cshrc 또는 /etc/csh.login 파일에 autologout 값 설정
vi /etc/csh.cshrc

# 다음 내용 추가 (분 단위)
set autologout=10

# 설정 적용
source /etc/csh.cshrc
```

#### SSH 서버 설정 (추천 보안 강화)

```bash
# /etc/ssh/sshd_config 파일 편집
vi /etc/ssh/sshd_config

# 다음 설정 추가 또는 수정
# 300초(5분)마다 클라이언트 생존 확인
ClientAliveInterval 300

# 3회 연속 응답 없으면 연결 종료 (총 15분)
ClientAliveCountMax 3

# SSH 데몬 재시작
systemctl restart sshd
# 또는
service sshd restart
```

#### 특정 사용자 예외 처리

```bash
# 모니터링 등 특수 목적 사용자 예외
vi /etc/profile

# 일반 사용자에만 적용
if [ "$USER" != "monitor" ] && [ "$USER" != "nagios" ]; then
    TMOUT=600
    export TMOUT
fi
```

### 4. 참고 자료

- [OpenSSH Manual - sshd_config](https://man.openbsd.org/sshd_config)
- [Bash Reference Manual - Bash Variables](https://www.gnu.org/software/bash/manual/)
- [CIS Benchmark - Set Session Timeout](https://www.cisecurity.org/cis-benchmarks/)
- [NIST AC-12 - Session Termination](https://csrc.nist.gov/projects/risk-management/risk-management-encyclopedia)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.