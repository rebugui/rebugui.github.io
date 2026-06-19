---
title: "[2026 주요정보통신기반시설] U-13 안전한 비밀번호 암호화 알고리즘 사용"
slug: "2026-주정통/U-13"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "안전한비밀번호암호화알고리즘을사용여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
draft: true
---

# U-13 안전한 비밀번호 암호화 알고리즘 사용

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-13 |
| **점검내용** | 안전한비밀번호암호화알고리즘을사용여부점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX등 |
| **양호기준** | SHA-2이상의안전한비밀번호암호화알고리즘을사용하는경우 |
| **취약기준** | 취약한비밀번호암호화알고리즘을사용하는경우 |
| **조치방법** | SHA-2이상의안전한비밀번호암호화알고리즘적용설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: SHA-2 이상의 안전한 비밀번호 암호화 알고리즘을 사용하는 경우
- **취약**: 취약한 비밀번호 암호화 알고리즘(DES, MD5 등)을 사용하는 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| SHA-512 사용 | 양호 | 매우 안전 |
| SHA-256 사용 | 양호 | 안전 |
| yescrypt 사용 | 양호 | 최신 안전 알고리즘 |
| MD5 사용 | 취약 | 즉시 변경 필요 |
| DES 사용 | 취약 | 심각한 보안 위험 |
| Blowfish 사용 | 양호 | 안전 (일부 OS) |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| Linux (RHEL) | ENCRYPT_METHOD | SHA512 | /etc/login.defs |
| Linux (Debian) | ENCRYPT_METHOD | SHA512 또는 yescrypt | /etc/login.defs |
| Solaris | CRYPT_DEFAULT | 5 또는 6 | /etc/security/policy.conf |
| AIX | pwd_algorithm | ssha512 | chsec 명령어 |
| HP-UX | CRYPT_DEFAULT | 5 또는 6 | /etc/default/security |

### 2. 점검 방법

#### Solaris 점검

```bash
# /etc/passwd 파일 내 암호화 필드 값 확인
cat /etc/passwd | grep root

# 암호화 알고리즘 식별자 확인
# $1$: MD5
# $2$: Blowfish
# $5$: SHA-256
# $6$: SHA-512
```

#### Linux 점검

```bash
# /etc/shadow 파일 내 암호화 필드 값 확인
cat /etc/shadow | grep root

# /etc/login.defs 파일 내 ENCRYPT_METHOD 값 확인
grep ENCRYPT_METHOD /etc/login.defs
```

**양호 출력 예시:**
```text
# SHA-512 알고리즘 사용
root:$6$rounds=5000$GwQn8qJX$...:18532:0:99999:7:::

# /etc/login.defs 설정
ENCRYPT_METHOD SHA512
```

**취약 출력 예시:**
```text
# MD5 알고리즘 사용 (취약)
root:$1$O3JMY.Tw$AdLMzalf/WTtfjtYSNMJF.:18532:0:99999:7:::

# /etc/login.defs 설정
ENCRYPT_METHOD MD5
```

#### AIX 점검

```bash
# /etc/security/passwd 파일 내 비밀번호 암호화 알고리즘 확인
grep password /etc/security/passwd

# password = {algorithm}hash 형식으로 확인
```

#### HP-UX 점검

```bash
# /etc/shadow 파일 내 암호화 필드 값 확인
cat /etc/shadow | grep root

# /etc/default/security 파일 내 CRYPT_DEFAULT 값 확인
grep CRYPT_DEFAULT /etc/default/security
```

### 3. 조치 방법

#### Solaris 설정

```bash
# /etc/security/policy.conf 파일 내 CRYPT_DEFAULT 값 설정
vi /etc/security/policy.conf

# 다음 내용 추가 또는 수정
CRYPT_DEFAULT = 5  # SHA-256
# 또는
CRYPT_DEFAULT = 6  # SHA-512
```

#### Linux (Redhat) 설정

1. **/etc/login.defs 파일 내 ENCRYPT_METHOD 값 설정**
   ```bash
   vi /etc/login.defs

   ENCRYPT_METHOD SHA256
   # 또는
   ENCRYPT_METHOD SHA512
   ```

2. **/etc/pam.d/system-auth 파일 내 안전한 알고리즘 설정**
   ```bash
   vi /etc/pam.d/system-auth

   password sufficient pam_unix.so sha256
   # 또는
   password sufficient pam_unix.so sha512
   ```

#### Linux (Debian) 설정

1. **/etc/login.defs 파일 내 ENCRYPT_METHOD 값 설정**
   ```bash
   vi /etc/login.defs

   ENCRYPT_METHOD SHA256
   # 또는
   ENCRYPT_METHOD SHA512
   # 또는
   ENCRYPT_METHOD yescrypt
   ```

2. **/etc/pam.d/common-password 파일 내 안전한 알고리즘 설정**
   ```bash
   vi /etc/pam.d/common-password

   password [success=2 default=ignore] pam_unix.so sha256
   # 또는
   password [success=2 default=ignore] pam_unix.so sha512
   ```

#### AIX 설정

```bash
# 안전한 암호화 알고리즘 설정
chsec -f /etc/security/login.cfg -s usw -a pwd_algorithm=ssha256
# 또는
chsec -f /etc/security/login.cfg -s usw -a pwd_algorithm=ssha512

# /etc/security/pwdalg.cfg 파일을 참조하여 OS에서 정의된 암호화 알고리즘 확인 가능
cat /etc/security/pwdalg.cfg
```

#### HP-UX 설정

```bash
# /etc/default/security 파일 내 CRYPT_DEFAULT 값 설정
vi /etc/default/security

CRYPT_DEFAULT = 5  # SHA-256
# 또는
CRYPT_DEFAULT = 6  # SHA-512
```

### 4. 조치 시 주의사항

- **비밀번호 재설정 필요**: 비밀번호 암호화 알고리즘을 변경해도 기존 비밀번호는 새 알고리즘으로 자동 변환되지 않음
- **계정별 재설정**: `passwd` 명령을 이용하여 모든 계정의 비밀번호를 재설정해야 새 알고리즘 적용
- **HP-UX 제한사항**: HP-UX 11i v2 이상이며, PHI 및 shadow password를 사용하지 않는 경우 취약

### 5. 참고 자료

**비밀번호 암호화 알고리즘 식별자:**
- `$1$`: MD5 (취약)
- `$2$`: Blowfish
- `$5$`: SHA-256 (안전)
- `$6$`: SHA-512 (안전)

**알고리즘 비교:**

| 알고리즘 | 보안성 | 권장 여부 |
|---------|--------|---------|
| DES | 취약 | 권장하지 않음 |
| MD5 | 취약 | 권장하지 않음 |
| SHA-256 | 안전 | 권장 |
| SHA-512 | 매우 안전 | 권장 |
| yescrypt | 매우 안전 | 권장 (Debian) |

- [FIPS 140-2 - Approved hashing algorithms](https://csrc.nist.gov/publications/detail/fips/140/2/final)
- [CIS Benchmark - Ensure password hashing algorithm is SHA-512](https://www.cisecurity.org/cis-benchmarks/)
- [NIST 800-63B - Memorized secret verifiers](https://pages.nist.gov/800-63-3/)

### 6. 스크립트

- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
