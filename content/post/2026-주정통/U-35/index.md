---
title: "[2026 주요정보통신기반시설] U-35 공유 서비스에 대한 익명 접근 제한 설정"
slug: "2026-주정통/U-35"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "공유 서비스의 익명 접근 제한 설정 여부 점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-35 공유 서비스에 대한 익명 접근 제한 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-35 |
| **점검내용** | 공유 서비스의 익명 접근 제한 설정 여부 점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX 등 |
| **양호기준** | 공유 서비스에 대해 익명 접근을 제한한 경우 |
| **취약기준** | 공유 서비스에 대해 익명 접근을 허용한 경우 |
| **조치방법** | 공유 서비스의 익명 접근 제한 설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: FTP, Samba, NFS 등 공유 서비스에서 익명(Anonymous/Guest) 접속이 차단된 경우
- **취약**: FTP, Samba, NFS 등 공유 서비스에서 익명(Anonymous/Guest) 접속이 허용된 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| FTP anonymous_enable=YES | 취약 | 익명 FTP 로그인 허용됨 |
| FTP anonymous_enable=NO | 양호 | 익명 FTP 차단됨 |
| Samba guest ok=yes | 취약 | 게스트 접속 허용됨 |
| Samba map to guest=never | 양호 | 게스트 매핑 비활성화 |
| NFS exports에 * (모든 호스트) | 취약 | 모든 호스트에 NFS 열려있음 |
| NFS exports에 특정 IP/대역 | 양호 | 특정 호스트만 NFS 접근 허용 |
| WebDAV 인증 없음 | 취약 | 공용 웹 공유 허용됨 |
| public FTP가 필요한 경우 | 예외 | 쓰기 권한은 반드시 제거 필요 |

#### 권장 설정값

| 서비스 | 설정 항목 | 권장 설정 | 비고 |
|------------|------------|---------------|------|
| vsFTPd | anonymous_enable | NO | 익명 로그인 차단 |
| ProFTPD | <Anonymous> 섹션 | 주석 처리 또는 삭제 | |
| Samba | guest ok | no | 각 공유에 개별 설정 |
| Samba (global) | map to guest | never | |
| NFS (/etc/exports) | 접근 허용 호스트 | 특정 IP 또는 네트워크 대역 | root_squash 필수 |
| WebDAV | 인증 | Basic 또는 Digest 인증 필수 | |

### 2. 점검 방법

#### FTP (vsFTPd) 점검

```bash
# vsFTPd 설정 확인
if [ -f /etc/vsftpd/vsftpd.conf ]; then
    grep "anonymous_enable" /etc/vsftpd/vsftpd.conf
fi
```

**양호 출력 예시:**
```text
anonymous_enable=NO
```

**취약 출력 예시:**
```text
anonymous_enable=YES
```

#### Samba 점검

```bash
# Samba 설정 확인
if [ -f /etc/samba/smb.conf ]; then
    grep -E "guest ok|map to guest|public" /etc/samba/smb.conf
fi
```

**양호 출력 예시:**
```text
map to guest = never
[share]
    guest ok = no
```

**취약 출력 예시:**
```text
map to guest = bad user
[public]
    guest ok = yes
```

#### NFS 점검

```bash
# NFS exports 확인
if [ -f /etc/exports ]; then
    grep -v "^#" /etc/exports | grep -v "^$"
fi
```

**양호 출력 예시:**
```text
/export/data 192.168.1.0/24(ro,root_squash,sync)
/backup       192.168.1.10(rw,root_squash,sync)
```

**취약 출력 예시:**
```text
/share *(rw,no_root_squash)
```
(모든 호스트(*)에 열려있음)

### 3. 조치 방법

#### 1. vsFTPd 익명 접속 차단

```bash
# /etc/vsftpd/vsftpd.conf 수정
sed -i 's/^anonymous_enable=YES/anonymous_enable=NO/' /etc/vsftpd/vsftpd.conf

# 추가 보안 설정
cat >> /etc/vsftpd/vsftpd.conf << 'EOF'
# 익명 로그인 완전 차단
no_anon_password=YES
anon_root=/dev/null
EOF

systemctl restart vsftpd
```

#### 2. ProFTPD 익명 접속 차단

```bash
# /etc/proftpd/proftpd.conf에서 <Anonymous> 섹션 주석 처리
sed -i '/<Anonymous/,/<\/Anonymous>/s/^/#/' /etc/proftpd/proftpd.conf

systemctl restart proftpd
```

#### 3. Samba Guest 접속 차단

```bash
# /etc/samba/smb.conf 수정
sed -i 's/guest ok = yes/guest ok = no/g' /etc/samba/smb.conf
sed -i 's/public = yes/public = no/g' /etc/samba/smb.conf

# global 섹션에 추가
sed -i '/\[global\]/a guest account = nobody\nmap to guest = never' /etc/samba/smb.conf

systemctl restart smb nmb
```

#### 4. NFS 접근 제한

```bash
# /etc/exports 수정
cat > /etc/exports << 'EOF'
/export/data 192.168.1.0/24(ro,root_squash,sync)
/backup       192.168.1.10(rw,root_squash,sync)
EOF

# 설정 적용
exportfs -ra
systemctl restart nfs-server
```

### 4. 참고 자료

- **CIS Controls**: CC14.4 공유 폴더 접근 제어 구성
- **NIST 800-53**: AC-3 (접근 제어 정책 시행)
- **ISO 27001:2013**: A.9.4.1 (사용자 접근 권한 관리)
- **K-ISMS**: 2.7.2 (공유폴더 접근통제)
- **PCI DSS**: 2.2.4 (시스템 간 공유 폴더 제한)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.