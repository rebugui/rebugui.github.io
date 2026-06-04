---
title: "[2026 주요정보통신기반시설] S-12 보안장비 정책 백업 설정"
slug: "2026-주정통/S-12"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "보안장비 설정 정보가 저장된 파일을 백업하는지 점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Security
---

# S-12 보안장비 정책 백업 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | S-12 |
| **점검내용** | 보안장비 설정 정보가 저장된 파일을 백업하는지 점검 |
| **점검대상** | 방화벽, VPN, IDS, IPS, Anti-DDoS, 웹방화벽 등 |
| **양호기준** | 보안장비에 적용된 정책을 별도의 파일로 보관하고 있는 경우 |
| **취약기준** | 보안장비에 적용된 정책을 별도의 파일로 보관하고 있지 않은 경우 |
| **조치방법** | 보안장비에 적용된 정책을 별도의 파일로 보관 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준

**양호**
- 보안장비에 적용된 정책을 별도의 파일로 보관하고 있는 경우
- 정기적인 백업 일정 수립 및 이행

**취약**
- 보안장비에 적용된 정책을 별도의 파일로 보관하고 있지 않은 경우
- 백업 파일이 없거나 오래된 경우

#### 경계 케이스 (Edge Case) 처리 방법

1. **자동 백업 미지원 장비**
   - 수동 백업 절차 수립
   - 정기적인 백업 알림 설정

2. **클라우드 환경**
   - 스냅샷 기능 활용
   - 구성 내보내기/가져오기 기능 사용

#### 권장 설정값

- 백업 주기: 일일 1회 (최소), 주간 1회 (권장)
- 보관 기간: 최소 30개 이상의 백업 버전
- 백업 위치: 로컬 + 원격 저장소 (이중화)

### 2. 점검 방법

**Step 1) 보안 장비에 적용된 정책을 별도의 파일로 보관하는지 확인**

```bash
# 1. 백업 파일 존재 여부 확인
# 백업 서버나 저장소에 최신 백업 파일이 있는지 확인

# 2. 백업 주기 확인
# 마지막 백업 일자 확인
ls -l /backup/firewall/
# -rw-r--r-- 1 admin admin 1048576 Jan 20 10:00 firewall-config-20240120.cfg

# 3. 백업 파일 검증
# 백업 파일이 정상적으로 열리는지 확인
```

**Step 2) 보안 장비 설정 메뉴에서 정책 백업 설정 확인**

```bash
# Web 방화벽 예시
# System > Maintenance > Backup
# Last Backup: 2024-01-20 10:00:00
# Backup Schedule: Daily
# Backup Location: /backup/config
```

### 3. 조치 방법

**Step 1) 정책 백업 설정 및 별도의 파일로 보관**

장비별로 제공하는 백업 기능을 사용하여 설정을 백업합니다.

**방화벽 설정 백업 예시 (Cisco ASA):**

```bash
# 1. TFTP 서버로 백업
copy running-config tftp:
# Address or name of remote host? 192.168.1.100
# Destination filename? firewall-config-20240120.cfg

# 2. 로컬 플래시 메모리에 백업
copy running-config flash:backup.cfg

# 3. USB로 백업
copy running-config usb:/backup.cfg

# 4. 자동 백업 설정
# System > Configuration > Backup
# Auto Backup: Enable
# Backup Schedule: Daily
# Backup Location: tftp://192.168.1.100
# Retention: 30 days
```

**Web 방화벽 설정 백업 예시:**

```bash
# 1. Web GUI에서 백업
# System > Maintenance > Backup & Restore
# - Backup Type: Full Configuration
# - Include Policy: Enable
# - Include Certificate: Enable
# - Backup Location: Local / FTP / SFTP

# 2. 예약 백업 설정
# System > Maintenance > Scheduled Backup
# - Schedule: Daily 02:00
# - Destination: ftp://backup-server:/backup
# - Filename Format: firewall-YYYYMMDD.cfg
# - Retention: 30 versions
```

**Step 2) 백업 파일 저장 위치 선정**

```bash
# 1. 로컬 저장소 (장비 내부)
# 장비 내부 플래시 메모리
# 단점: 장비 교체 시 사용 불가

# 2. 네트워크 저장소 (권장)
# - TFTP/FTP/SFTP 서버
# - NAS (Network Attached Storage)
# - SAN (Storage Area Network)

# 3. 클라우드 저장소 (유의 필요)
# - AWS S3
# - Azure Blob Storage
# - 보안 암호화 필수

# 4. 이동식 미디어
# - USB
# - 외장 하드디스크
# - 주기적인 오프사이트 백업 권장
```

**Step 3) 백업 주기 및 버전 관리**

```bash
# 1. 백업 주기 설정
- 실시간 백업: 설정 변경 시 즉시
- 일일 백업: 매일 정해진 시간 (권장)
- 주간 백업: 매주 일요일
- 월간 백업: 매월 1일

# 2. 백업 버전 관리
# 최소 30개 이상의 백업 버전 보관
# 버전별 파일명 예시:
# - firewall-config-20240120.cfg  (일일 백업)
# - firewall-config-weekly-20240120.cfg  (주간 백업)
# - firewall-config-monthly-202401.cfg  (월간 백업)

# 3. 백업 라벨링
# - 변경 사항 설명
# - 백업 실행자
# - 백업 일시
```

### 4. 참고 자료

**백업 정책 수립 가이드**

```bash
# 1. 백업 대상
- 보안 정책 (룰셋)
- 네트워크 설정 (IP, 라우팅)
- 인증서 및 키
- 사용자 계정 정보
- 시스템 설정

# 2. 백업 주기
- 자동 백업: 매일 새벽 2시간
- 수동 백업: 주요 설정 변경 전후

# 3. 보관 기간
- 일일 백업: 30일
- 주간 백업: 3개월
- 월간 백업: 1년

# 4. 저장 위치
- 1차: 로컬 네트워크 (NAS)
- 2차: 원격 데이터 센터
- 3차: 오프사이트 (클라우드 또는 물리적 격리)

# 5. 암호화
- 백업 파일 암호화 (AES-256)
- 전송 구간 암호화 (SFTP, HTTPS)
```

**주의사항**
- 일반적인 경우 영향이 없습니다.
- 백업 파일은 안전한 곳에 보관하세요 (접근 통제 필수).
- 정기적으로 백업 파일을 검증하세요.
- 백업 파일에 민감 정보(비밀번호, 키)가 포함되어 있으므로 암호화하세요.
- 장비 교체 시 백업 파일을 사용하여 즉시 복구할 수 있어야 합니다.
- 백업 복구 절차를 문서화하고 정기적으로 훈련하세요.
- 각 벤더마다 설정 방법이 상이하므로 매뉴얼을 참조하세요.

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.