---
title: "[2026 주요정보통신기반시설] U-57 Ftpusers 파일 설정"
slug: "2026-주정통/U-57"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "FTP서비스에root계정접근제한설정여부점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-57 Ftpusers 파일 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-57 |
| **점검내용** | FTP서비스에root계정접근제한설정여부점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX등 |
| **양호기준** | root계정접속을차단한경우 |
| **취약기준** | root계정접속을허용한경우 |
| **조치방법** | FTP서비스를사용하지않는경우서비스중지및비활성화설정, FTP서비스사용시root계정으로직접접속할수없도록설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: /etc/ftpusers에 root가 등록된 경우
- **취약**: root가 FTP로 직접 접속 가능한 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| root 접속 차단됨 | 양호 | 530 메시지 |
| root 접속 가능 | 취약 | 비밀번호 노출 |
| ftpusers 파일 없음 | 취약 | 기본 동작 허용 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| Linux | /etc/ftpusers | root, bin, daemon 등 | ftpusers |
| Solaris | /etc/ftpd/ftpusers | root 등 | ftpusers |

### 2. 점검 방법

#### Linux 점검

```bash
# 1. ftpusers 파일 확인
echo "=== 1. ftpusers ==="
cat /etc/ftpusers 2>/dev/null
cat /etc/vsftpd/ftpusers 2>/dev/null

# 2. root 접속 테스트 (로컬)
echo "=== 2. Root FTP Test ==="
(echo "user root"; echo "pass"; echo "quit") | nc localhost 21 2>/dev/null | head -5
```

**양호 출력 예시:**
```text
=== 1. ftpusers ===
root
bin
daemon
```

**취약 출력 예시:**
```text
=== 1. ftpusers ===
(파일 없음 또는 root 없음)
```

### 3. 조치 방법

#### ftpusers 설정

```bash
# /etc/ftpusers 생성 (vsftpd, proftpd 공통)
cat > /etc/ftpusers << 'EOF'
root
bin
daemon
adm
sync
shutdown
halt
mail
news
uucp
operator
games
nobody
EOF

chmod 644 /etc/ftpusers
chown root:root /etc/ftpusers

# vsftpd 추가 설정
vi /etc/vsftpd/vsftpd.conf
# userlist_enable=YES
# userlist_file=/etc/vsftpd/user_list
# userlist_deny=NO

systemctl restart vsftpd
```

### 4. 참고 자료

- CIS Benchmark for Linux: root FTP 차단 권고
- NIST SP 800-53: AC-2 (계정 관리)
- man pages: ftpusers(5), vsftpd.conf(5)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.