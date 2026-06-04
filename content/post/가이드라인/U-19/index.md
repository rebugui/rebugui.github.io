---
title: "[2026 주요정보통신기반시설] U-19 /etc/hosts 파일 소유자 및 권한 설정"
slug: "2026-주정통/U-19"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "/etc/hosts파일의권한적절성여부점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-19 /etc/hosts 파일 소유자 및 권한 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-19 |
| **점검내용** | /etc/hosts파일의권한적절성여부점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX등 |
| **양호기준** | /etc/hosts파일의소유자가root이고,권한이644이하인경우 |
| **취약기준** | /etc/hosts파일의소유자가root가아니거나,권한이644이하가아닌경우 |
| **조치방법** | /etc/hosts파일소유자및권한변경설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: `/etc/hosts` 파일의 소유자가 root이고, 권한이 644 이하인 경우 (단, 일반 사용자의 쓰기 권한은 반드시 제거되어야 함)
- **취약**: `/etc/hosts` 파일의 소유자가 root가 아니거나, 일반 사용자에게 쓰기 권한이 부여된 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| 소유자 root, 권한 644 | 양호 | 일반 사용자 읽기 허용 |
| 소유자 root, 권한 600 | 양호 | 일반 사용자 접근 불가 |
| 소유자 root, 권한 666 | 취약 | 누구나 수정 가능 |
| 일반 사용자 쓰기 권한 있음 | 취약 | 제거 필요 |
| 소유자가 root가 아님 | 취약 | 즉시 수정 필요 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| 모든 OS | 소유자 | root | root만 소유자 |
| 모든 OS | 권한 | 600 또는 644 | 쓰기 권한은 root에게만 |
| 웹 서버 등 | 권한 | 644 | 일부 서비스에서 읽기 필요 |

### 2. 점검 방법

#### Solaris, Linux, AIX, HP-UX 점검

`/etc/hosts` 파일은 DNS보다 우선적으로 참조되는 중요한 네트워크 설정 파일입니다.

```bash
# /etc/hosts 파일 소유자 및 권한 확인
ls -l /etc/hosts
```

**양호 출력 예시:**
```text
-rw-r--r-- 1 root root ...  (644) -> 양호 (일반 사용자 읽기 허용)
-rw------- 1 root root ...  (600) -> 양호 (일반 사용자 접근 불가)
```

**취약 출력 예시:**
```text
-rw-rw-rw- 1 root root ...  (666) -> 취약 (누구나 수정 가능)
-rw-r--r-- 1 admin1 root ...  -> 취약 (소유자가 root가 아님)
```

### 3. 조치 방법

#### Solaris, Linux, AIX, HP-UX 공통 설정

1. **소유자 변경**
   ```bash
   chown root /etc/hosts
   ```

2. **권한 변경**
   ```bash
   # 일반적인 웹 서버 등의 경우 읽기가 필요할 수 있음 -> 644
   chmod 644 /etc/hosts

   # 보안 강화 (일반 사용자가 이 파일을 읽을 필요가 없는 경우 -> 600)
   # chmod 600 /etc/hosts
   ```

3. **변경 확인**
   ```bash
   ls -l /etc/hosts
   ```

### 4. 참고 자료

- **DNS 조회 순서**: `/etc/nsswitch.conf` (Linux/Solaris) 또는 `/etc/netsvc.conf` (AIX) 파일에서 `hosts: files dns`와 같이 설정된 경우 `/etc/hosts` 파일을 먼저 참조합니다.

| 항목 | /bin/false | /sbin/nologin |
|-----|-----------|--------------|
| 메시지 출력 | 없음 | "This account is currently not available." |
| 로그 기록 | 기본 없음 | 있음 (syslog) |
| FTP 접속 | 불가 | 일부 설정에서 가능 |
| 사용자 경험 | 연결이 끊김 | 명확한 거부 메시지 |

- [CIS Benchmark - Ensure /etc/hosts permissions](https://www.cisecurity.org/cis-benchmarks/)
- [NIST SC-8, SC-12 - Transmission Confidentiality, Cryptographic Key Management](https://csrc.nist.gov/projects/risk-management/risk-management-encyclopedia)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.