---
title: "[2026 주요정보통신기반시설] U-27 /.rhosts, hosts.equiv 사용 금지"
slug: "2026-주정통/U-27"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "$HOME/.rhosts 및 /etc/hosts.equiv 파일에 대해 적절한 소유자 및 접근권한 설정 여부 점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-27 $HOME/.rhosts, hosts.equiv 사용 금지

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-27 |
| **점검내용** | $HOME/.rhosts 및 /etc/hosts.equiv 파일에 대해 적절한 소유자 및 접근권한 설정 여부 점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX 등 |
| **양호기준** | rlogin, rsh, rexec 서비스를 사용하지 않거나, 사용 시 아래와 같은 설정이 적용된 경우 1) /etc/hosts.equiv 및 $HOME/.rhosts 파일 소유자가 root 또는 해당 계정인 경우 2) 파일 권한이 600 이하인 경우 3) '+' 설정이 없는 경우 |
| **취약기준** | rlogin, rsh, rexec 서비스를 사용하며 위 설정이 적용되지 않은 경우 1) 파일 소유자가 root 또는 해당 계정이 아닌 경우 2) 권한이 600 이하가 아닌 경우 3) '+' 설정이 있는 경우 |
| **조치방법** | /etc/hosts.equiv, $HOME/.rhosts 파일 소유자 및 권한 변경, 허용 호스트 및 계정 등록 설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: r-command 서비스를 사용하지 않거나, 사용 시 파일 소유자가 root(또는 해당 계정)이고, 권한이 600이며 '+' 설정이 없는 경우
- **취약**: r-command 서비스 사용 시 파일 소유자/권한이 잘못되었거나 '+' 설정이 있는 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| r-command 패키지가 설치되지 않음 | 양호 (권장) | rsh-server, rsh 패키지가 없으면 안전함 |
| /etc/hosts.equiv 파일이 없음 | 양호 | 별도 설정 필요 없음 |
| 파일 내용이 주석(#)만 있음 | 양호 | 실제 허용 설정이 없음 |
| '+ +' 설정이 있음 | 취약 (매우 위험) | 모든 호스트의 모든 사용자 허용 |
| '+' 만 있음 | 취약 (매우 위험) | 모든 호스트 허용 |
| '192.168.1.1 +' | 취약 | 해당 IP의 모든 사용자 허용 |
| 'trusted_host user1' | 주의 | 특정 호스트의 특정 사용자만 허용 |
| 파일 권한이 644 이상 | 취약 | 타 사용자가 읽기 가능하여 정보 노출 |

#### 권장 설정값

| 항목 | 권장 설정 | 비고 |
|------------|---------------|------|
| r-command 서비스 | 비활성화 또는 삭제 | SSH 사용 권장 |
| /etc/hosts.equiv 파일 | 존재하지 않거나 삭제 | 시스템 전체 신뢰 설정 비권장 |
| $HOME/.rhosts 파일 | 존재하지 않거나 삭제 | 개별 신뢰 설정 비권장 |
| 파일 소유자 | root 또는 해당 계정 | |
| 파일 권한 | 600 (rw-------) | root 또는 해당 계정만 접근 |
| '+' 설정 | 금지 | 절대 사용 불가 |

### 2. 점검 방법

#### r-command 서비스 활성화 여부 확인

```bash
# 패키지 확인 (Linux)
rpm -qa | grep -i rsh
dpkg -l | grep -i rsh

# xinetd 서비스 확인
ls -L /etc/xinetd.d/rlogin /etc/xinetd.d/rsh 2>/dev/null
cat /etc/xinetd.d/rlogin 2>/dev/null | grep disable
```

#### 설정 파일 점검

```bash
# /etc/hosts.equiv 점검
ls -l /etc/hosts.equiv 2>/dev/null
cat /etc/hosts.equiv 2>/dev/null

# 사용자별 .rhosts 점검
find /home /root -name .rhosts -exec ls -l {} \; 2>/dev/null
find /home /root -name .rhosts -exec cat {} \; 2>/dev/null
```

**양호 출력 예시:**
```text
ls: cannot access '/etc/hosts.equiv': No such file or directory
(파일이 존재하지 않음)
```

**취약 출력 예시 1:**
```text
-rw-r--r-- 1 root root 50 Jan 20 10:00 /etc/hosts.equiv
```
(권한 644 - 타 사용자 읽기 가능)

**취약 출력 예시 2 (파일 내용):**
```text
+
+ +
192.168.1.100 +
```
('+' 설정 - 모든 호스트 허용)

### 3. 조치 방법

#### 권장: r-command 서비스 제거

r-command 서비스는 근본적으로 취약하므로 SSH(Secure Shell)로 대체하고 서비스를 중지/ 삭제하는 것이 가장 좋습니다.

```bash
# RHEL/CentOS
yum remove rsh-server
# 또는
rpm -e rsh-server

# Debian/Ubuntu
apt-get remove rsh-server
apt-get purge rsh-server

# Solaris
pkgrm SUNWrcmds

# AIX
removep rsh
```

#### 불가피하게 사용 시: 파일 설정 보안 강화

1. **`/etc/hosts.equiv` 파일 소유자 및 권한 변경**
   ```bash
   chown root /etc/hosts.equiv
   chmod 600 /etc/hosts.equiv
   ```

2. **`$HOME/.rhosts` 파일 소유자 및 권한 변경**
   ```bash
   chown [사용자] [홈디렉터리]/.rhosts
   chmod 600 [홈디렉터리]/.rhosts
   ```

3. **`+` 설정 제거**
   ```bash
   # 파일 내 '+' 기호가 포함된 라인을 모두 삭제
   sed -i '/^+/d' /etc/hosts.equiv
   sed -i '/^+/d' ~/.rhosts

   # 반드시 필요한 호스트와 계정만 명시
   # 예: trusted_host.example.com user1
   ```

4. **서비스 비활성화 (xinetd 사용 시)**
   ```bash
   # rsh 서비스 비활성화
   cat > /etc/xinetd.d/rsh << 'EOF'
   service shell
   {
           disable = yes
           socket_type = stream
           wait = no
           user = root
           log_on_success += USERID
           log_on_failure += USERID
           server = /usr/sbin/in.rshd
   }
   EOF

   systemctl restart xinetd
   ```

### 4. 참고 자료

- **CIS Benchmarks**: 9.3.10 Ensure no .rhosts files are present
- **NIST 800-53**: AC-3 (Access Enforcement), IA-2 (Identification and Authentication)
- **SSH替代方案**: OpenSSH 사용 권장
- **man page**: `man rhosts`, `man rsh`

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.