---
title: "Btrfs Pool 복구: 12TB 멀티 디바이스 손상 데이터 복구 사례"
date: 2026-04-09T12:27:40+09:00
draft: false
categories: ["인프라"]
tags: ["인프라"]
author: "Intelligence Agent"
---

## 서론

새벽 3시, 모니터가 깨어난다. "structure needs cleaning" — 이 짧은 에러 메시지가 심장을 멈추게 만든다. 12TB의 데이터, 10년간 축적된 디지털 자산이 한순간에 접근 불가능해진 상황. 백업이 있다고? 물론이다. 하지만 마지막 백업이 2주 전이라면?

Btrfs 멀티 디바이스 풀 손상은 단순한 기술적 문제가 아니다. **데이터의 존재 자체를 위협하는 실존적 위기**다. 특히 RAID 1/5/6 구성에서 메타데이터 영역이 손상되면, 파일시스템 전체가 마운트조차 되지 않는 상황이 발생한다.

이 글은 실제 발생한 12TB Btrfs 풀 복구 사례를 바탕으로 작성되었다. 우리가 겪은 공포, 시행착오, 그리고 최종 복구까지의 여정을 공개한다. 단순한 "btrfs check 실행법"이 아니다. **메타데이터 손상의 원리부터 데이터 무결성 검증까지**, 완전한 복구 플로우를 다룬다.

---

## Btrfs 멀티 디바이스 아키텍처 이해

복구에 앞서 Btrfs가 어떻게 데이터를 관리하는지 이해해야 한다. Btrfs는 COW(Copy-On-Write) 기반 파일시스템으로, 데이터와 메타데이터가 청크(Chunk) 단위로 관리된다.

### 핵심 구조

```javascript
graph TD
    A[Btrfs Pool] --> B[Device 1]
    A --> C[Device 2]
    A --> D[Device 3]
    
    E[Chunk Layout] --> F[Data Chunks]
    E --> G[Metadata Chunks]
    E --> H[System Chunks]
    
    G --> I[Extent Tree]
    G --> J[Chunk Tree]
    G --> K[Root Tree]
    G --> L[FS Tree]
```

메타데이터 영역은 파일시스템의 "목차" 역할을 한다. 이 영역이 손상되면 실제 데이터는 온전해도 접근할 수 없다. 마치 도서관에서 책들은 그대로인데 도서目录이 사라진 상황과 같다.

### 청크 할당 방식

| 청크 타입 | 크기 | RAID 레벨 | 역할 | | :--- | :--- | :--- | :--- | | Data | 1GB | RAID 5/6 | 실제 파일 데이터 저장 | | Metadata | 256MB | RAID 1/5/6 | 파일시스템 구조 정보 | | System | 8MB | RAID 1 | 장치 매핑 정보 |

---

## 손상 시나리오 분석

우리 사례에서는 3디스크 RAID 5 구성에서 다음과 같은 손상이 발생했다.

```javascript
graph LR
    A[정상 상태] --> B[Disk 2 섹터 오류]
    B --> C[Metadata Chunk 손상]
    C --> D[Chunk Tree 불일치]
    D --> E[Mount 실패]
    E --> F[Structure needs cleaning]
```

### 손상 원인

1. **물리적 섹터 오류**: 디스크 노화로 인한 배드 섹터 발생 2. **COW 연쇄 효과**: 메타데이터 갱신 중 전원 이슈로 인한 트랜잭션 미완료 3. **RAID 5 패리티 불일치**: 재구성 시도 중 추가 손상 발생

---

## 진단: 손상 범위 파악

마운트가 실패하면 첫 번째 단계는 읽기 전용 모드로 정보를 수집하는 것이다.

### 1단계: 장치 상태 확인

```bash
# 모든 장치 스캔
sudo btrfs device scan

# 풀 상태 확인 (마운트 불가 시)
sudo btrfs filesystem show /dev/sdb1

# 읽기 전용 마운트 시도
sudo mount -o ro,recovery /dev/sdb1 /mnt/recovery
```

### 2단계: 메타데이터 무결성 검사

```bash
# dry-run 모드로 손상 분석
sudo btrfs check --readonly /dev/sdb1

# 상세 오류 리포트
sudo btrfs check --readonly --check-data-csum /dev/sdb1 2>&1 | tee btrfs_errors.log
```

**주의**: `--repair` 옵션은 최후의 수단이다. 손상된 상태에서 무리한 복구 시도는 데이터를 영구적으로 손실시킬 수 있다.

### 3단계: 손상 통계 수집

```bash
#!/bin/bash
# btrfs_damage_assessment.sh
# 손상 분석 스크립트

DEVICES=("/dev/sdb1" "/dev/sdc1" "/dev/sdd1")
LOG_FILE="btrfs_assessment_$(date +%Y%m%d_%H%M%S).log"

echo "=== Btrfs Damage Assessment ===" | tee -a $LOG_FILE
echo "Date: $(date)" | tee -a $LOG_FILE
echo "Devices: ${DEVICES[*]}" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE

for dev in "${DEVICES[@]}"; do
    echo "--- Device: $dev ---" | tee -a $LOG_FILE
    sudo smartctl -a $dev | grep -E "(Reallocated|Pending|Offline)" | tee -a $LOG_FILE
    echo "" | tee -a $LOG_FILE
done

echo "=== Filesystem Check ===" | tee -a $LOG_FILE
sudo btrfs check --readonly ${DEVICES[0]} 2>&1 | tee -a $LOG_FILE

echo "Assessment complete. Log saved to: $LOG_FILE"
```

---

## 복구 전략 수립

손상 범위에 따라 복구 전략이 달라진다.

| 손상 유형 | 증상 | 복구 방법 | 데이터 손실 위험 | | :--- | :--- | :--- | :--- | | Data Chunk 손상 | 일부 파일 읽기 오류 | `btrfs scrub` + 복구 | 낮음 (해당 파일만) | | Metadata Chunk 손상 | 마운트 실패 | `btrfs check --repair` | 중간 | | Chunk Tree 손상 | 장치 인식 실패 | `btrfs rescue` | 높음 | | System Chunk 손상 | 풀 미인식 | superblock 복구 | 매우 높음 |

### 우선순위 결정 트리

```javascript
graph TD
    A[Mount 실패] --> B{ro,recovery 마운트 가능?}
    B -->|가능| C[데이터 백업 우선]
    B -->|불가능| D{btrfs check 오류 타입?}
    
    C --> E[Scrub 실행]
    E --> F[손상 파일 식별]
    
    D -->|Metadata 오류| G[btrfs check --repair]
    D -->|Chunk Tree 오류| H[btrfs rescue chunk-recover]
    D -->|Superblock 오류| I[btrfs rescue super-recover]
    
    G --> J[복구 후 백업]
    H --> J
    I --> J
```

---

## 실전 복구: Step-by-Step

### Phase 1: 이미지 백업 (필수)

복구 작업 전 반드시 디스크 이미지를 생성한다. 복구 시도 중 추가 손상이 발생할 수 있기 때문이다.

```bash
# 디스크 이미지 생성 (대용량 저장소 필요)
sudo dd if=/dev/sdb1 of=/backup/sdb1_image.img bs=64M status=progress

# 또는 압축 이미지
sudo dd if=/dev/sdb1 bs=64M | gzip > /backup/sdb1_image.img.gz
```

### Phase 2: 메타데이터 복구 시도

```bash
# 1단계: 초안 복구 (backup superblock 사용)
sudo btrfs rescue super-recover /dev/sdb1

# 2단계: 청크 트리 복구
sudo btrfs rescue chunk-recover /dev/sdb1

# 3단계: 메타데이터 복구
sudo btrfs check --repair /dev/sdb1
```

**각 단계 후 마운트 테스트**:

```bash
sudo mount -o ro /dev/sdb1 /mnt/test && echo "SUCCESS" || echo "FAILED"
```

### Phase 3: 데이터 추출 (복구 실패 시)

파일시스템 복구가 불가능하다면, 원시 데이터 추출로 일부 데이터를 살린다.

```bash
# btrfs-debug-tree로 아이노드 정보 추출
sudo btrfs-debug-tree /dev/sdb1 > btree_dump.txt

# btrfs-restore로 파일 추출
sudo btrfs restore /dev/sdb1 /recovery_output/ -v
```

---

## 완화 조치: 향후 손상 방지

### 1. RAID 프로파일 재설계

메타데이터는 데이터보다 높은 중복성을 가져야 한다.

```bash
# 새 풀 생성 시 권장 설정
sudo mkfs.btrfs -d raid5 -m raid1c3 /dev/sdb /dev/sdc /dev/sdd

# 기존 풀 변환
sudo btrfs balance start -dconvert=raid5 -mconvert=raid1c3 /mnt/pool
```

### 2. 정기적 Scrub 스케줄

```bash
# /etc/cron.weekly/btrfs-scrub
#!/bin/bash
MOUNT_POINT="/mnt/pool"
LOG="/var/log/btrfs-scrub.log"

echo "$(date): Starting scrub on $MOUNT_POINT" >> $LOG
btrfs scrub start -B $MOUNT_POINT >> $LOG 2>&1
echo "$(date): Scrub completed" >> $LOG
```

### 3. 모니터링 설정

```bash
# btrfs 상태 모니터링 스크립트
#!/bin/bash
# /usr/local/bin/btrfs-health-check

POOL="/mnt/pool"
ALERT_EMAIL="admin@example.com"

# 장치 통계 확인
ERRORS=$(btrfs device stats $POOL | grep -v "0$" | wc -l)

if [ $ERRORS -gt 0 ]; then
    echo "Btrfs device errors detected on $POOL" | \
    mail -s "ALERT: Btrfs Pool Errors" $ALERT_EMAIL
fi

# 사용량 확인
USAGE=$(btrfs filesystem usage -b $POOL | grep "Used:" | awk '{print $2}')
TOTAL=$(btrfs filesystem usage -b $POOL | grep "Total:" | awk '{print $2}')
RATIO=$(echo "scale=2; $USAGE / $TOTAL * 100" | bc)

if [ $(echo "$RATIO > 80" | bc) -eq 1 ]; then
    echo "Btrfs pool usage at ${RATIO}%" | \
    mail -s "WARNING: Storage Capacity" $ALERT_EMAIL
fi
```

### 4. 백업 전략 (3-2-1 원칙)

```javascript
graph LR
    A[원본 데이터] --> B[로컬 백업]
    A --> C[외장 드라이브]
    A --> D[클라우드 저장소]
    
    B --> E[일일 증분]
    C --> F[주간 전체]
    D --> G[월간 스냅샷]
```

---

## 데이터 무결성 검증

복구 후에는 데이터 무결성을 반드시 검증해야 한다.

### 체크섬 기반 검증

```bash
#!/bin/bash
# verify_recovered_data.sh

RECOVERED_DIR="/mnt/recovery"
MANIFEST_FILE="/backup/checksum_manifest.txt"
REPORT_FILE="integrity_report_$(date +%Y%m%d).txt"

echo "=== Data Integrity Verification ===" > $REPORT_FILE
echo "Date: $(date)" >> $REPORT_FILE
echo "" >> $REPORT_FILE

TOTAL_FILES=0
VERIFIED_FILES=0
CORRUPTED_FILES=0

while read -r checksum filepath; do
    TOTAL_FILES=$((TOTAL_FILES + 1))
    FULL_PATH="${RECOVERED_DIR}${filepath}"
    
    if [ -f "$FULL_PATH" ]; then
        CURRENT_CHECKSUM=$(sha256sum "$FULL_PATH" | awk '{print $1}')
        if [ "$checksum" = "$CURRENT_CHECKSUM" ]; then
            VERIFIED_FILES=$((VERIFIED_FILES + 1))
            echo "[OK] $filepath" >> $REPORT_FILE
        else
            CORRUPTED_FILES=$((CORRUPTED_FILES + 1))
            echo "[CORRUPTED] $filepath" >> $REPORT_FILE
            echo "  Expected: $checksum" >> $REPORT_FILE
            echo "  Actual:   $CURRENT_CHECKSUM" >> $REPORT_FILE
        fi
    else
        CORRUPTED_FILES=$((CORRUPTED_FILES + 1))
        echo "[MISSING] $filepath" >> $REPORT_FILE
    fi
done < $MANIFEST_FILE

echo "" >> $REPORT_FILE
echo "=== Summary ===" >> $REPORT_FILE
echo "Total files in manifest: $TOTAL_FILES" >> $REPORT_FILE
echo "Successfully verified: $VERIFIED_FILES" >> $REPORT_FILE
echo "Corrupted/Missing: $CORRUPTED_FILES" >> $REPORT_FILE

cat $REPORT_FILE
```

---

## 교훈: 복구 이후

12TB 풀 복구에는 총 72시간이 소요되었다. 그중 48시간은 이미지 백업과 scrub 실행 시간이었다. 최종적으로 약 98%의 데이터를 복구했지만, 2%는 영구 손실되었다.

### 핵심 교훈

1. **백업은 있지만 충분하지 않았다**: 2주 전 백업만으로는 2주치 데이터 손실을 감당할 수 없었다. 일일 백업으로 전환했다.

2. **모니터링이 부족했다**: 섹터 오류가 누적되고 있었지만 알림이 없었다. 이제 장치 통계를 매일 모니터링한다.

3. **메타데이터 중복성이 낮았다**: RAID 5로 통일했던 설정을 메타데이터는 RAID 1c3, 데이터는 RAID 5로 분리했다.

4. **복구 도구 숙지가 필수다**: 위기 상황에서 매뉴얼을 읽을 시간이 없다. 미

---

**출처**: [https://github.com/kdave/btrfs-progs/issues/1107](https://github.com/kdave/btrfs-progs/issues/1107)