---
title: "[2026 주요정보통신기반시설] U-39 불필요한 NFS 서비스 비활성화"
slug: "2026-주정통/U-39"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "불필요한NFS서비스사용여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Unix
---

# U-39 불필요한 NFS 서비스 비활성화

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | U-39 |
| **점검내용** | 불필요한NFS서비스사용여부점검 |
| **점검대상** | SOLARIS, LINUX, AIX, HP-UX등 |
| **양호기준** | 불필요한NFS서비스관련데몬이비활성화된경우 |
| **취약기준** | 불필요한NFS서비스관련데몬이활성화된경우 |
| **조치방법** | NFS서비스를사용하지않는경우서비스중지및비활성화설정 (로컬서버에마운트되어있는디렉터리제거및공유디렉터리제거후서비스중지가능) |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: NFS 서비스(nfsd, rpcbind, mountd 등)가 비활성화된 경우
- **취약**: NFS 서비스가 활성화되어 있는 경우

#### 경계 케이스 (Edge Case) 처리 방법

| 상황 | 판단 기준 | 설명 |
|------|----------|------|
| 파일 공유가 필요한 서버 | 주의 | NFSv4 + Kerberos 권장 |
| 내부 네트워크에서만 사용 | 주의 | 방화벽 접근 제어 필요 |
| 로컬에 마운트된 NFS 존재 | 취약 | 사용 중인 NFS 서비스 |
| rpcbind만 활성화 | 주의 | 다른 RPC 서비스 사용 가능성 |
| NFSv4 사용 | 양호 | 암호화 지원 (Kerberos) |

#### 권장 설정값

| 환경 | 항목 | 권장 설정 | 비고 |
|------|------------|---------------|------|
| Linux | nfs-server | disabled (systemctl) | NFS 서버 |
| Linux | rpcbind | disabled (systemctl) | RPC 매핑 서비스 |
| Linux | rpc-statd | disabled (systemctl) | 파일 잠금 상태 |
| Linux | rpc-idmapd | disabled (systemctl) | ID 매핑 |
| Solaris | network/nfs/server | disabled (svcadm) | NFS 서버 |

### 2. 점검 방법

#### Linux 점검

NFS 서비스는 암호화되지 않은 평문 통신을 하며 IP 기반 인증만 수행하므로 취약점이 많습니다. 사용하지 않는다면 반드시 비활성화해야 합니다.

```bash
# 1. NFS 서비스 상태 확인
echo "=== 1. NFS Services Status ==="
systemctl is-active nfs-server rpcbind rpc-statd rpc-idmapd 2>/dev/null
systemctl is-enabled nfs-server rpcbind rpc-statd rpc-idmapd 2>/dev/null

# 2. 프로세스 확인
echo "=== 2. NFS Processes ==="
ps -ef | grep -E "nfsd|rpcbind|rpc.mountd|rpc.statd" | grep -v grep

# 3. 포트 listening 확인
echo "=== 3. NFS Ports ==="
netstat -tuln | grep -E ":(111|2049|20048)"
# 111: rpcbind, 2049: nfs, 20048: mountd

# 4. 마운트된 NFS 확인
echo "=== 4. Mounted NFS ==="
mount | grep nfs
df -h -t nfs4 2>/dev/null
```

**양호 출력 예시:**
```text
=== 1. NFS Services Status ===
nfs-server: inactive (dead)
rpcbind: inactive (dead)
rpc-statd: inactive (dead)
nfs-server: disabled
rpcbind: disabled
=== 2. NFS Processes ===
(프로세스 없음)
=== 3. NFS Ports ===
(해당 포트에서 listening하지 않음)
```

**취약 출력 예시:**
```text
=== 1. NFS Services Status ===
nfs-server: active (exited)
rpcbind: active (running)
nfs-server: enabled
=== 2. NFS Processes ===
root   1234  1  0  Jan20 ?  00:00:00 [nfsd]
=== 3. NFS Ports ===
tcp        0      0 0.0.0.0:2049            0.0.0.0:*                   LISTEN
```

#### Solaris 점검

```bash
# SMF 서비스 상태 확인
svcs -a | grep -E "nfs|rpc"

# 또는
svcs network/nfs/server
svcs network/rpc/bind
```

### 3. 조치 방법

#### Linux (systemd) 설정

1. **NFS 마운트 해제**
   ```bash
   # 현재 마운트된 NFS 확인
   mount | grep nfs

   # 마운트 해제
   umount /mnt/nfs/share

   # /etc/fstab에서 NFS 항목 제거
   vi /etc/fstab
   ```

2. **NFS 서비스 중지**
   ```bash
   # 서비스 중지
   systemctl stop nfs-server
   systemctl stop rpcbind
   systemctl stop rpc-statd
   systemctl stop rpc-idmapd

   # 부팅 시 비활성화
   systemctl disable nfs-server
   systemctl disable rpcbind
   systemctl disable rpc-statd
   systemctl disable rpc-idmapd
   ```

3. **서비스 재시작**
   ```bash
   # 서비스 재시작 (비활성화 확인)
   systemctl status nfs-server
   systemctl status rpcbind
   ```

#### Linux (SysVinit) 설정

1. **서비스 중지**
   ```bash
   service nfs stop
   service rpcbind stop

   # 부팅 시 비활성화
   chkconfig nfs off
   chkconfig rpcbind off
   ```

#### Solaris (SMF) 설정

1. **NFS 서비스 비활성화**
   ```bash
   svcadm disable network/nfs/server
   svcadm disable network/rpc/bind

   # 상태 확인
   svcs network/nfs/server
   svcs network/rpc/bind
   ```

### 4. 참고 자료

- CIS Benchmark for Linux: NFS 서비스 비활성화 권고
- NIST SP 800-53: CM-7 (시스템 최소화)
- NFSv4 RFC 5661: 보안 개선 사항
- man pages: nfsd(8), exportfs(8), exports(5)

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.