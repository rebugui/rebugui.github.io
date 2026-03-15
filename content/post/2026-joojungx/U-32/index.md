---
title: "[2026 주요정보통신기반시설] U-32 홈디렉터리로 지정한 디렉터리의 존재 관리"
slug: "2026-주정통/U-32"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "사용자 계정과 홈디렉토리의 일치 여부 점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-32 홈디렉터리로 지정한 디렉터리의 존재 관리

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-32 |
| **점검내용** | 사용자 계정과 홈디렉토리의 일치 여부 점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX 등 |
| **양호기준** | 홈디렉토리가 존재하지 않는 계정이 발견되지 않는 경우 |
| **취약기준** | 홈디렉토리가 존재하지 않는 계정이 발견된 경우 |
| **조치방법** | 홈디렉토리가 존재하지 않는 계정에 홈디렉토리 설정 또는 계정 제거 설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: `/etc/passwd`에 명시된 홈 디렉터리가 실재(존재)하는 경우
- **취약**: `/etc/passwd`에 명시된 홈 디렉터리가 존재하지 않는 계정이 있는 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| 홈 디렉터리가 존재함 | 양호 | 정상 |
| 홈 디렉터리가 /인데 존재하지 않음 | 취약 | 로그인 시 루트(/)에 위치하게 됨 |
| nologin/false 쉘을 가진 계정 | 제외 | 로그인하지 않는 서비스 계정 |
| 홈 디렉터리가 /nonexistent인 계정 | 제외 | 의도적으로 홈 없음 (일부 서비스) |
| NFS 마운트된 홈 | 점검 필요 | 마운트 상태도 확인 |
| symlink인 홈 디렉터리 | 점검 필요 | 원본 경로의 존재 여부 확인 |
| /home 없음 but /root 있음 | 양호 | 각 계정별로 확인 필요 |

#### 권장 설정값

| 항목 | 권장 설정 | 비고 |
|------------|---------------|------|
| 홈 디렉터리 위치 | /home/username 또는 /root | 표준 |
| 홈 디렉터리 권한 | 700 또는 750 | 소유자만 접근 권장 |
| 홈 디렉터리 소유자 | 해당 계정 | |
| 스켈레톤 파일 | /etc/skel/ | 계정 생성시 복사됨 |

### 2. 점검 방법

#### Linux, Solaris, AIX, HP-UX 점검

`/etc/passwd`에 등록된 사용자 중 실제 로그인 가능한 계정의 홈 디렉터리 존재 여부를 확인합니다.

```bash
# 홈 디렉터리가 존재하지 않는 계정 찾기
cat /etc/passwd | while IFS=: read -r username x uid gid gecos homedir shell; do
    # nologin/false 제외
    if [[ ! "$shell" =~ *(nologin|false)* ]]; then
        if [ ! -d "$homedir" ]; then
            echo "취약: $username (UID: $uid, 홈: $homedir, 쉘: $shell)"
        fi
    fi
done

# 또는 간단한 확인
for user in $(cut -d: -f1 /etc/passwd); do
    homedir=$(getent passwd "$user" | cut -d: -f6)
    if [ ! -d "$homedir" ]; then
        echo "$user: $homedir (존재하지 않음)"
    fi
done
```

**양호 출력 예시:**
```text
(출력 없음 - 모든 계정의 홈 디렉터리가 존재)
```

**취약 출력 예시:**
```text
취약: testuser (UID: 1001, 홈: /home/testuser, 쉘: /bin/bash)
취약: appuser (UID: 1002, 홈: /var/lib/app, 쉘: /bin/sh)
```

### 3. 조치 방법

#### 1. 계정이 불필요한 경우 (권장)

```bash
# 계정 완전 삭제 (홈 디렉터리 포함)
userdel -r username

# 또는 계정 잠금
usermod -L username  # 비밀번호 잠금
chage -E 0 username  # 계정 만료
```

#### 2. 계정이 필요한 경우

```bash
# 홈 디렉터리 생성
mkdir -p /home/username

# 기본 설정 파일 복사
cp -a /etc/skel/. /home/username/

# 소유자 및 권한 설정
chown -R username:groupname /home/username
chmod 750 /home/username

# /etc/passwd에 홈 디렉터리 경로 업데이트 (필요 시)
usermod -d /home/username username
```

#### 3. 일괄 조치 스크립트

```bash
#!/bin/bash
# 홈 디렉터리가 없는 모든 계정에 대해 자동 조치

for user in $(cat /etc/passwd | awk -F: '$3 >= 1000 && $7 !~ /(nologin|false)/ {print $1}'); do
    HOME_DIR=$(getent passwd "$user" | cut -d: -f6)

    if [ ! -d "$HOME_DIR" ]; then
        echo "조치 중: $user ($HOME_DIR)"

        # 홈 디렉터리 생성
        mkdir -p "$HOME_DIR"
        cp -a /etc/skel/. "$HOME_DIR/"
        chown -R "$user":"$(id -gn $user)" "$HOME_DIR"
        chmod 750 "$HOME_DIR"

        echo "완료: $user"
    fi
done
```

### 4. 참고 자료

- **CIS Controls**: CC5.1 비인가 계정 제거 및 비활성화
- **NIST 800-53**: AC-2 (계정 관리)
- **ISO 27001:2013**: A.9.2.3 (사용자 등록 및 등록 말소 절차)
- **K-ISMS**: 2.6.2 (사용자 계정 관리)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.