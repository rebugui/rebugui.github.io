---
title: "[2026 주요정보통신기반시설] U-33 숨겨진 파일 및 디렉터리 검색 및 제거"
slug: "2026-주정통/U-33"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "숨겨진 파일 및 디토리 내의 심스러운 파일 존재 여부 점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
draft: true
---

# U-33 숨겨진 파일 및 디렉터리 검색 및 제거

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-33 |
| **점검내용** | 숨겨진 파일 및 디토리 내의 심스러운 파일 존재 여부 점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX 등 |
| **양호기준** | 불필요하거나 의심스러운 숨겨진 파일 및 디토리를 제거한 경우 |
| **취약기준** | 불필요하거나 의심스러운 숨겨진 파일 및 디토리를 제거하지 않은 경우 |
| **조치방법** | ls -al 명령어로 숨겨진 파일 존재 파악 후 불법적이거나 의심스러운 파일을 제거 설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 불필요하거나 의심스러운 숨겨진 파일(.* 파일)이 존재하지 않는 경우
- **취약**: 불필요하거나 의심스러운 숨겨진 파일이 존재하는 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| .bashrc, .profile, .ssh | 정상 | 사용자 설정 파일 |
| ... (점 3개) | 취약 | 의심스러운 숨김 기법 |
| .. (점 2개 + 공백) | 취약 | 의심스러운 숨김 기법 |
| . (점 1개 + 공백) | 취약 | 의심스러운 숨김 기법 |
| /dev/.hidden/ | 취약 | 루트킷 은신처 |
| /tmp/.update/ | 취약 | 악성코드 가능성 |
| /var/tmp/.hidden/ | 취약 | 악성코드 가능성 |
| .X11-unix, .ICE-unix | 정상 | X11 관련 정상 파일 |
| .config, .cache, .local | 정상 | 사용자 설정 디렉터리 |
| .vim, .mozilla | 정상 | 애플리케이션 설정 |

#### 권장 설정값

| 검색 위치 | 제외 패턴 (정상 파일) | 점검 대상 |
|------------|---------------|------|
| /tmp | .X11-unix, .ICE-unix, .Test-unix | 그 외 .* 파일/디렉터리 |
| /var/tmp | .X11-unix, .ICE-unix | 그 외 .* 파일/디렉터리 |
| /dev | (정상 디바이스 파일) | 일반 파일(Regular File) |
| /home | .bash*, .profil*, .ssh, .config, .cache, .local, .vim, .mozilla | ... , .. , .[공백] |
| /root | .bash*, .profil*, .ssh, .vim | 그 외 의심스러운 파일 |

### 2. 점검 방법

#### Linux, Solaris, AIX, HP-UX 점검

의심스러운 위치에서 숨겨진 파일과 디렉터리를 검색합니다.

```bash
# 1. 의심스러운 숨겨진 디렉터리 검색
for dir in /tmp /var/tmp /dev /home /root; do
    if [ -d "$dir" ]; then
        find "$dir" -name ".*" -type d 2>/dev/null | while read hidden_dir; do
            # 정상적인 디렉터리 제외
            if [[ ! "$hidden_dir" =~ \.(ssh|git|config|cache|local|bash|vim|mozilla|X11|ICE) ]]; then
                echo "의심 디렉터리: $hidden_dir"
                ls -ld "$hidden_dir"
            fi
        done
    fi
done

# 2. 특수한 이름의 숨겨진 파일 검색 (점 3개, 공백 포함 등)
find /tmp /var/tmp /dev /home -name "..." -o -name ".. " -o -name ". " 2>/dev/null

# 3. /dev 내 일반 파일(Regular File) 검색
find /dev -type f 2>/dev/null

# 4. 최근 생성된 숨겨진 파일 검색 (7일 이내)
find /tmp /var/tmp /dev -name ".*" -mtime -7 -ls 2>/dev/null
```

**양호 출력 예시:**
```text
(의심스러운 파일 없음 또는 .X11-unix, .ICE-unix 등 정상 파일만 출력)
```

**취약 출력 예시:**
```text
의심 디렉터리: /tmp/..
drwxr-xr-x 2 root root 4096 Jan 20 10:00 /tmp/..
의심 디렉터리: /dev/.hidden
drwx------ 2 root root 4096 Jan 20 10:00 /dev/.hidden
의심 파일: /home/user/...
```

### 3. 조치 방법

#### 1. 의심 파일 식별 및 분석

```bash
# 파일 정보 확인
ls -la /path/to/.suspicious_file
file /path/to/.suspicious_file

# 내용 확인 (텍스트 파일인 경우)
strings /path/to/.suspicious_file | head -20
```

#### 2. 안전한 삭제

```bash
# 파일 삭제 전 백업 (법적 증거 보존)
mv /path/to/.malicious /tmp/.malicious.backup_$(date +%Y%m%d)

# 분석 후 악성 파일 확인 시 삭제
rm -f /path/to/.malicious
rm -rf /path/to/.malicious_dir
```

#### 3. 일괄 정리 스크립트

```bash
#!/bin/bash
# /tmp와 /var/tmp의 의심스러운 숨겨진 파일 정리

SAFE_PATTERNS=(".X11-unix" ".ICE-unix" ".Test-unix")

for dir in /tmp /var/tmp; do
    find "$dir" -name ".*" -type f 2>/dev/null | while read file; do
        # 안전한 패턴 확인
        is_safe=false
        for safe in "${SAFE_PATTERNS[@]}"; do
            if [[ "$file" == *"$safe"* ]]; then
                is_safe=true
                break
            fi
        done

        if [ "$is_safe" = false ]; then
            echo "의심 파일: $file"
            # 분석을 위해 보고만 (실제 삭제 시 주의)
        fi
    done
done
```

### 4. 참고 자료

- **CIS Controls**: CC7.4 정기적으로 시스템에서 비인가 파일 검색
- **NIST 800-53**: SI-7 (악성코드 탐지 및 제거 절차)
- **ISO 27001:2013**: A.12.2.1 (악성 소프트웨어 방어)
- **K-ISMS**: 2.9.1 (악성프로그램 방지)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.