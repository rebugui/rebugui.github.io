---
title: "[2026 주요정보통신기반시설] U-41 불필요한 automountd 제거"
slug: "2026-주정통/U-41"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "automountd서비스데몬의실행여부점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-41 불필요한 automountd 제거

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-41 |
| **점검내용** | automountd서비스데몬의실행여부점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX등 |
| **양호기준** | automountd서비스가비활성화된경우 |
| **취약기준** | automountd서비스가활성화된경우 |
| **조치방법** | automountd서비스비활성화설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: autofs(automountd) 서비스가 비활성화된 경우
- **취약**: autofs(automountd) 서비스가 활성화된 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| 자동 마운트 필요 (NFS 홈 디렉터리) | 주의 | 사용 시 보안 설정 필요 |
| /etc/auto.master 존재 | 주의 | automountd 사용 중 |
| autofs 활성화 상태 | 취약 | RPC 취약점 노출 |
| systemd의 automount 사용 | 주의 | 다른 서비스일 수 있음 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| Linux | autofs | disabled (systemctl) | 자동 마운트 |
| Solaris | system/filesystem/autofs | disabled (svcadm) | 자동 마운트 |
| AIX | automount | off (chsubserver) | 자동 마운트 |

### 2. 점검 방법

#### Linux 점검

automountd 서비스는 RPC 기반으로 취약점이 있으며, 사용하지 않는다면 비활성화해야 합니다.

```bash
# 1. autofs 서비스 상태 확인
echo "=== 1. autofs Service ==="
systemctl is-active autofs 2>/dev/null
systemctl is-enabled autofs 2>/dev/null

# 2. 프로세스 확인
echo "=== 2. automount Process ==="
ps -ef | grep -E "automount|automountd" | grep -v grep

# 3. 설정 파일 확인
echo "=== 3. auto.master ==="
ls -l /etc/auto.master 2>/dev/null
cat /etc/auto.master 2>/dev/null | head -10
```

**양호 출력 예시:**
```text
=== 1. autofs Service ===
autofs: inactive (dead)
autofs: disabled
=== 2. automount Process ===
(프로세스 없음)
=== 3. auto.master ===
ls: /etc/auto.master: No such file or directory
```

**취약 출력 예시:**
```text
=== 1. autofs Service ===
autofs: active (running)
autofs: enabled
=== 2. automount Process ===
root   1234  1  0  Jan20 ?  00:00:00 /usr/sbin/automount
```

#### Solaris 점검

```bash
# SMF 서비스 상태 확인
svcs -a | grep autofs

# 또는
svcs system/filesystem/autofs
```

### 3. 조치 방법

#### Linux (systemd) 설정

1. **autofs 서비스 중지**
   ```bash
   # 서비스 중지
   systemctl stop autofs

   # 부팅 시 비활성화
   systemctl disable autofs
   ```

2. **확인**
   ```bash
   systemctl status autofs
   ```

#### Solaris (SMF) 설정

1. **autofs 서비스 비활성화**
   ```bash
   svcadm disable system/filesystem/autofs

   # 상태 확인
   svcs system/filesystem/autofs
   ```

### 4. 참고 자료

- CIS Benchmark for Linux: 불필요한 서비스 비활성화 권고
- NIST SP 800-53: CM-7 (시스템 최소화)
- autofs(8) man page: 자동 마운트 설정

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.