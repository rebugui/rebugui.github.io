---
title: "[2026 주요정보통신기반시설] U-40 NFS 접근 통제"
slug: "2026-주정통/U-40"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "NFS(Network FileSystem)의접근통제설정적용여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-40 NFS 접근 통제

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-40 |
| **점검내용** | NFS(Network FileSystem)의접근통제설정적용여부점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX등 |
| **양호기준** | 접근통제가설정되어있으며NFS설정파일접근권한이644이하인경우 |
| **취약기준** | 접근통제가설정되어있지않고NFS설정파일접근권한이644를초과하는경우 |
| **조치방법** | NFS서비스를사용하지않는경우서비스중지및비활성화설정, 불가피하게사용시접근통제설정및NFS설정파일접근권한644설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: /etc/exports에 IP 기반 접근 제어가 설정되고, root_squash 옵션이 적용된 경우
- **취약**: /etc/exports에 * (모든 호스트) 허용이거나 no_root_squash 옵션이 사용된 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| * (모든 호스트) 허용 | 취약 | 누구나 마운트 가능 |
| no_root_squash 사용 | 취약 | root 권한 전이 허용 |
| 특정 IP 대역만 허용 | 양호 | 네트워크 접근 제어 |
| all_squash 사용 | 양호 | 모든 사용자 익명화 |
| /etc/exports 권한 644 | 양호 | root만 수정 가능 |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| NFSv3/NFSv4 | /etc/exports 권한 | 644 (root:root) | NFS 공유 설정 |
| NFSv3/NFSv4 | root_squash | 항상 적용 | root 권한 매핑 |
| NFSv3/NFSv4 | 접근 제어 | IP 기반 명시적 지정 | 네트워크 제한 |
| NFSv4 | Kerberos | sec=krb5 | 암호화 인증 |

### 2. 점검 방법

#### Linux 점검

NFS 접근 통제 설정을 확인하여 무단 접속을 방지하고 root 권한 전이를 차단해야 합니다.

```bash
# 1. /etc/exports 내용 확인
echo "=== 1. NFS Exports ==="
cat /etc/exports

# 2. /etc/exports 권한 확인
echo "=== 2. /etc/exports Permissions ==="
ls -l /etc/exports
stat -c "%a %U:%G" /etc/exports 2>/dev/null || stat -f "%Lp %Su:%Sg" /etc/exports

# 3. 현재 내보내기 목록 확인
echo "=== 3. Export List ==="
exportfs -v

# 4. 마운트된 NFS 확인
echo "=== 4. Mounted NFS ==="
mount | grep nfs
```

**양호 출력 예시:**
```text
=== 1. NFS Exports ===
/export/data 192.168.1.0/24(ro,root_squash,sync)
/export/backup 192.168.1.10(rw,root_squash,sync)
=== 2. /etc/exports Permissions ===
-rw-r--r-- 1 root root 123 Jan 20 10:00 /etc/exports
644 root:root
=== 3. Export List ===
/export/data 192.168.1.0/24(ro,wdelay,root_squash,...)
```

**취약 출력 예시:**
```text
=== 1. NFS Exports ===
/share *(rw,no_root_squash,sync)
=== 2. /etc/exports Permissions ===
-rw-rw-rw- 1 root root 123 Jan 20 10:00 /etc/exports
666 root:root
```

### 3. 조치 방법

#### Linux (exports) 설정

1. **/etc/exports 보안 설정**
   ```bash
   # 양호한 exports 설정 예시
   cat > /etc/exports << 'EOF'
   # 내부 네트워크에만 읽기 전용
   /export/data 192.168.1.0/24(ro,root_squash,sync)

   # 특정 서버에만 쓰기 허용
   /export/backup 192.168.1.10(rw,root_squash,sync)

   # 모든 사용자를 익명으로 매핑 (높은 보안)
   /export/public 192.168.1.0/24(ro,all_squash,anonuid=65534,anongid=65534,sync)
   EOF

   # 설정 적용
   exportfs -ra
   ```

2. **권한 설정**
   ```bash
   chown root:root /etc/exports
   chmod 644 /etc/exports
   ```

3. **확인**
   ```bash
   exportfs -v
   ```

4. **서비스 재시작**
   ```bash
   systemctl restart nfs-server
   ```

### 4. 참고 자료

- CIS Benchmark for Linux: NFS 접근 제어 권고
- NIST SP 800-53: AC-3 (접근 제어 정책)
- NFSv4 RFC 5661: 보안 사양
- man pages: exports(5), exportfs(8), nfsd(8)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.