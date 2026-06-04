---
title: "[2026 주요정보통신기반시설] U-31 홈디렉터리 소유자 및 권한 설정"
slug: "2026-주정통/U-31"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "홈디렉토리의 소유자 외 타사용자가 해당 홈디렉토리를 수정할 수 없도록 제한 설정 여부 점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-31 홈디렉터리 소유자 및 권한 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-31 |
| **점검내용** | 홈디렉토리의 소유자 외 타사용자가 해당 홈디렉토리를 수정할 수 없도록 제한 설정 여부 점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX 등 |
| **양호기준** | 홈디렉토리 소유자가 해당 계정이고, 타사용자 쓰기 권한이 제거된 경우 |
| **취약기준** | 홈디렉토리 소유자가 해당 계정이 아니거나, 타사용자 쓰기 권한이 부여된 경우 |
| **조치방법** | 사용자별 홈디렉토리 소유주를 해당 계정으로 변경하고, 타사용자의 쓰기 권한 제거 설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 홈 디렉터리의 소유자가 해당 계정이고, 타 사용자(Group, Other)의 쓰기 권한이 제거된 경우 (권한 755, 750, 700 등)
- **취약**: 홈 디렉터리의 소유자가 해당 계정이 아니거나, 타 사용자(Group, Other)의 쓰기 권한이 부여된 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| 권한이 700 (drwx------) | 양호 | 소유자만 접근 가능 |
| 권한이 750 (drwxr-x---) | 양호 | 소유자와 그룹만 접근 가능 |
| 권한이 755 (drwxr-xr-x) | 양호 | 모두가 읽기/실행 가능, 쓰기는 소유자만 |
| 권한이 775 (drwxrwxr-x) | 취약 | 그룹 쓰기 권한 있음 |
| 권한이 777 (drwxrwxrwx) | 취약 (매우 위험) | 모두가 읽기/쓰기/실행 가능 |
| 소유자가 root인 일반 사용자 홈 | 취약 | 소유자를 해당 사용자로 변경 필요 |
| /root 홈 디렉터리 | 권장 700 | 관리자 홈은 최고 보안 권장 |
| 웹 서버 public_html | 예외 | 웹 서비스를 위해 755 필요할 수 있음 |
| NFS 마운트된 홈 디렉터리 | 주의 | NFS 서버 측 권한도 확인 필요 |

#### 권장 설정값

| 홈 디렉터리 유형 | 권장 소유자 | 권장 권한 | 비고 |
|------------|------------|---------------|------|
| 일반 사용자 홈 | 해당 사용자 | 755 (rwxr-xr-x) 또는 750 | 표준 |
| 일반 사용자 홈 (보안 강화) | 해당 사용자 | 700 (rwx------) | 프라이버시 강화 |
| 관리자 (root) 홈 | root | 700 (rwx------) | 최고 보안 |
| 웹 서비스 계정 홈 | 해당 사용자 | 755 | 웹 접근 필요 시 |
| 공유 폴더 홈 | 해당 사용자 | 750 | 그룹 공유 필요 시 |

### 2. 점검 방법

#### Linux, Solaris, AIX, HP-UX 점검

`/etc/passwd` 파일에 등록된 사용자들의 홈 디렉터리 권한을 점검합니다.

```bash
# 일반 사용자 (UID 1000 이상) 홈 디렉터리 확인
cat /etc/passwd | awk -F: '$3 >= 1000 {print $1, $6}' | while read user homedir; do
    if [ -d "$homedir" ]; then
        ls -ld "$homedir"
    fi
done

# 또는 간단한 확인
ls -ld /home/*
ls -ld /root
```

**양호 출력 예시:**
```text
drwx------ 2 user1 user1 4096 Jan 20 10:00 /home/user1
drwxr-xr-x 2 user2 user2 4096 Jan 20 10:00 /home/user2
drwx------ 5 root root 4096 Jan 20 10:00 /root
```

**취약 출력 예시:**
```text
drwxrwxrwx 2 user1 user1 4096 Jan 20 10:00 /home/user1
```
(권한 777 - 누구나 접근 및 수정 가능)

**취약 출력 예시 2:**
```text
drwxrwxr-x 2 root user1 4096 Jan 20 10:00 /home/user1
```
(소유자가 root가 아닌 경우)

### 3. 조치 방법

#### Linux, Solaris, AIX, HP-UX 설정

1. **소유자 변경 (필요 시)**
   ```bash
   chown user1:user1 /home/user1
   ```

2. **권한 변경 (타 사용자 쓰기 권한 제거)**
   - 일반적인 권장 설정: 750 (rwxr-x---) 또는 755 (rwxr-xr-x)
   - 보안성이 높은 설정: 700 (rwx------)

   ```bash
   chmod 750 /home/user1
   # 또는
   chmod 755 /home/user1
   # 또는 (최고 보안)
   chmod 700 /home/user1
   ```

3. **일괄 조치 스크립트**
   ```bash
   # 모든 사용자 홈 디렉터리 소유자 및 권한 정리
   for user in $(cut -d: -f1,3,6 /etc/passwd | awk -F: '$2 >= 1000 {print $1":"$3}'); do
       username=$(echo "$user" | cut -d: -f1)
       uid=$(echo "$user" | cut -d: -f2)
       homedir=$(getent passwd "$username" | cut -d: -f6)

       if [ -d "$homedir" ]; then
           echo "조치 중: $username ($homedir)"
           chown "$username":"$username" "$homedir"
           chmod 750 "$homedir"
       fi
   done

   # root 홈 디렉터리
   if [ -d /root ]; then
       chown root:root /root
       chmod 700 /root
   fi
   ```

### 4. 참고 자료

- **CIS Benchmarks**: 6.1.11 Ensure home directory permissions
- **NIST 800-53**: AC-3 (Access Enforcement), AC-6 (Least Privilege)
- **man page**: `usermod`, `chmod`

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.