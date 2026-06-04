---
title: "[2026 주요정보통신기반시설] HV-16 비휘발성 경로 내 로그 파일 저장"
slug: "2026-주정통/HV-16"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "비휘발성경로에로그파일저장여부점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Virtualization
---

# HV-16 비휘발성 경로 내 로그 파일 저장

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | HV-16 |
| **점검내용** | 비휘발성경로에로그파일저장여부점검 |
| **점검대상** | VMware ESXi 등 |
| **판단기준** | 양호: 로그파일경로가존재하며,해당경로가비휘발성경로에저장된경우 |
| **판단기준** | 취약: 로그파일경로가존재하지않거나,휘발성경로에저장되지않은경우 |
| **조치방법** | 로그파일경로를비휘발성로그파일경로로설정 |

---
## 상세 설명

### 1. 항목 개요

VMware ESXi는 기본적으로 `/scratch`라는 휘발성 저장소에 로그를 저장합니다. `/scratch`는 RAM 디스크 기반으로, 시스템 재시작 시 모든 내용이 소멸됩니다. 또한 일정 시간(기본 24시간)이 지나면 로그가 자동으로 삭제됩니다.

비휘발성 경로(영구 저장소)에 로그를 저장하면 시스템 재시작 후에도 로그가 보존되어 침해 사고 조사와 장애 원인 파악이 가능합니다.

### 2. 왜 이 항목이 필요한가요?

**휘발성 저장소의 문제점:**

1. **시스템 재시작 시 로그 소멸**
   - ESXi 재부팅 시 /scratch 내용 삭제
   - 장애 발생 원인 파악 불가
   - 침해 사고 추적 불가

2. **자동 로그 삭제**
   - 기본 24시간 경과 후 로그 삭제
   - 주말/공휴일 장애 대응 시 로그 소실

3. **원격 로그 서버 미전달 로그**
   - vmksummary.log, dvs.log, vmkernel.log 등 일부 로그는 원격 서버로 전달 안 됨
   - ESXi 호스트 로그만으로 분석 필요

**위험 시나리오:**

```
해커 → ESXi 침해
→ 백도어 설치
→ 관리자 장애 감지 → ESXi 재부팅
→ /scratch 로그 소멸
→ 침해 흔적 사라짐
→ 백도어 지속적 유지
→ 결제 정보 유출 지속
```

**실제 사고 사례:**
- 랜섬웨어 감염 후 관리자가 ESXi 재부팅 → 침킹 경로 추적 불가
- 주말에 장애 발생 → 월요일 확인 시 로그 소실

### 3. 점검 대상

- VMware ESXi

### 4. 판단 기준

- **양호**: 로그 파일 경로가 존재하며, 해당 경로가 비휘발성 경로에 저장된 경우
- **취약**: 로그 파일 경로가 존재하지 않거나, 휘발성 경로(/scratch 등)에 저장된 경우

### 5. 점검 방법

#### VMware ESXi

1. Web 콘솔 접속
   ```
   https://<VMware ESXi IP>
   ```

2. **호스트** > **관리** > **시스템** > **고급 설정**으로 이동

3. `Syslog.global.LogDir` 설정값 확인

**양호 기준:**
```
Syslog.global.LogDir = /vmfs/volumes/datastore1/systemlogs
```

**취약 기준:**
```
Syslog.global.LogDir = /scratch/log
또는
Syslog.global.LogDir = <blank>
```

### 6. 조치 방법

#### VMware ESXi

**1) Web 콘솔 설정**

1. **호스트** > **관리** > **시스템** > **고급 설정**으로 이동

2. `Syslog.global.LogDir` 선택 후 **옵션 편집** 클릭

3. 비휘발성 경로 입력:
   ```
   /vmfs/volumes/datastore1/systemlogs
   ```

4. **저장** 클릭

**2) CLI 설정**

```bash
# 로그 디렉터리 설정
vim-cmd hostsvc/advopt/update Syslog.global.LogDir string /vmfs/volumes/datastore1/systemlogs

# 설정 확인
vim-cmd hostsvc/advopt/query Syslog.global.LogDir
```

**3) 디렉터리 생성**

```bash
# 로그 저장용 디렉터리 생성
mkdir -p /vmfs/volumes/datastore1/systemlogs

# 권한 설정
chmod 755 /vmfs/volumes/datastore1/systemlogs
```

### 7. 비휘발성 저장소 구성

**VMware VMFS 데이터스토어:**

```
/vmfs/volumes/<datastore_name>/systemlogs
```

**NFS 공유:**

```
/vmfs/volumes/<nfs_share>/systemlogs
```

**예시:**
```
/vmfs/volumes/datastore1/systemlogs
/vmfs/volumes/Backup-Storage/systemlogs
/vmfs/volumes/NFS-Logs/systemlogs
```

### 8. 로그 파일 구조

**비휘발성 경로 설정 후 로그 파일:**

```
/vmfs/volumes/datastore1/systemlogs/
├── vmkernel.log
├── hostd.log
├── vpxa.log
├── fdm.log
├── dvs.log
├── vmkwarning.log
└── vmksummary.log
```

### 9. 스토리지 용량 계획

**로그 파일 크기 추정:**

| 로그 파일 | 일일 증가량 | 월간 예상 |
|-----------|-------------|----------|
| vmkernel.log | 10~50 MB | 300~1500 MB |
| hostd.log | 5~20 MB | 150~600 MB |
| vpxa.log | 5~10 MB | 150~300 MB |
| 기타 로그 | 10~30 MB | 300~900 MB |
| **총계** | **30~110 MB** | **900~3300 MB** |

**권장 스토리지:**
- 최소 10 GB
- 권장 50 GB 이상
- 로그 회전 설정 필수

### 10. 로그 회전 설정

**1) 로그 크기 제한**

```bash
# 로그 파일 최대 크기 설정
vim-cmd hostsvc/advopt/update Syslog.global.logSizeDefault long 10240
# 10 MB
```

**2) 로그 파일 개수 제한**

```bash
# 보관 로그 파일 수 설정
vim-cmd hostsvc/advopt/update Syslog.global.logSizeNum long 10
# 최대 10개 파일 보관
```

### 11. 모니터링

**1) 디스크 사용량 확인**

```bash
# 로그 디렉터리 크기 확인
du -sh /vmfs/volumes/datastore1/systemlogs

# 데이터스토어 사용량 확인
df -h /vmfs/volumes/datastore1
```

**2) 로그 파일 확인**

```bash
# 로그 파일 목록
ls -lh /vmfs/volumes/datastore1/systemlogs/

# 최신 로그 확인
tail -f /vmfs/volumes/datastore1/systemlogs/vmkernel.log
```

### 12. 주의사항

- **비휘발성 경로**는 VMFS 데이터스토어 또는 NFS 공유 권장
- **디스크 용량** 충분히 확보 (최소 10 GB)
- **로그 회전** 설정으로 디스크 부족 방지
- **정기적 백업**으로 로그 이중 보호
- **원격 로그 서버(HV-14)**와 함께 사용 권장
- 변경 후 로그 파일 생성 확인 필수

### 13. 로그 백업 전략

**1) 정기적 백업**

```bash
# 로그 디렉터리 백업 스크립트
#!/bin/bash
LOG_DIR="/vmfs/volumes/datastore1/systemlogs"
BACKUP_DIR="/vmfs/volumes/backup-storage/logs"
DATE=$(date +%Y%m%d)

tar -czf $BACKUP_DIR/logs-$DATE.tar.gz $LOG_DIR
find $BACKUP_DIR -name "logs-*.tar.gz" -mtime +30 -delete
```

**2) rsync 동기화**

```bash
# 로그 서버로 동기화
rsync -avz /vmfs/volumes/datastore1/systemlogs/ \
    backup-server:/backup/esxi-logs/
```

## 요약

VMware ESXi 로그는 기본적으로 휘발성 `/scratch` 경로에 저장되어 재부팅 시 소멸됩니다. 반드시 **비휘발성 경로(/vmfs/volumes/datastoreX/systemlogs)**로 로그 저장 위치를 변경해야 합니다. 최소 **10 GB 이상의 스토리지**를 확보하고, **원격 로그 서버(HV-14)**와 함께 사용하여 로그를 이중 보호하는 것을 권장합니다.
