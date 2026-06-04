---
title: "[2026 주요정보통신기반시설] S-11 보안장비 로그 보관"
slug: "2026-주정통/S-11"
date: 2026-02-05T09:56:12+09:00
lastmod: 2026-02-05T09:56:12+09:00
description: "로그 보관 정책에 따라 적절하게 로그를 보관하는지 점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Security
---

# S-11 보안장비 로그 보관

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | S-11 |
| **점검내용** | 로그 보관 정책에 따라 적절하게 로그를 보관하는지 점검 |
| **점검대상** | 방화벽, VPN, IDS, IPS, Anti-DDoS, 웹방화벽 등 |
| **양호기준** | 정책에 따라 로그 보관 설정된 경우 |
| **취약기준** | 로그 보관 정책이 없고 관리되지 않은 경우 |
| **조치방법** | 보안장비 로그를 정기적으로 분석 및 검토 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준

**양호**
- 정책에 따라 로그 보관 설정된 경우 (최소 3개월 이상)
- 법적 요구사항을 준수하는 보관 기간 설정

**취약**
- 로그 보관 정책이 없고 관리되지 않은 경우
- 로그 보관 기간이 법적 최소 기준 미충족

#### 경계 케이스 (Edge Case) 처리 방법

1. **저장 공간 부족**
   - 로그 로테이션 설정으로 자동 삭제
   - 중요 로그는 별도 백업

2. **장비 교체 시**
   - 로그 백업 후 이전
   - 로그 보관 연장 조치

#### 권장 설정값

- 법적 최소 기준: 3개월 이상
- 권장 보관 기간: 6개월 ~ 1년
- 침해사고 로그: 2년 이상

### 2. 점검 방법

**Step 1) 보안 장비의 보관된 로그 날짜 확인**

```bash
# 현재 로그 보관 기간 확인
# 방화벽 예시 (Cisco ASA)
show logging | include Jan
show logging | include Feb
show logging | include Mar

# 로그 파일 확인
dir log:
# -rw-r--r-- 1048576 Jan 01 00:00:00 2024 syslog.log
# -rw-r--r-- 1048576 Jan 02 00:00:00 2024 syslog.log
```

**Step 2) 보안 장비 로그 보관 설정에서 로그 저장기간 확인 및 변경**

```bash
# Web 방화벽 예시
# System > Configuration > Log Settings > Retention
# Log Retention Period: 90 days
```

### 3. 조치 방법

**Step 1) 로그 보관 기간 설정**

기관 정책과 법적 요구사항에 맞게 로그 보관 기간을 설정합니다.

**방화벽 로그 보관 설정 예시:**

```bash
# 1. 로그 파일 보관 기간 설정
# System > Configuration > Log > Retention Policy
- Retention Period: 90 days (최소 3개월)
- Max Log Size: 10GB
- Auto Archive: Enable
- Archive Location: /var/log/archive

# 2. 로그 회전 설정
# Log Rotation: Daily
# Compressed Archive: Enable
# Archive Retention: 90 days
```

**Web 방화벽 로그 보관 설정 예시:**

```bash
# 1. 로그 보관 정책 설정
# Log > Configuration > Log Storage
- Local Storage: Enable
- Retention Period: 90 days
- Max Storage: 20GB
- Auto Delete Old Logs: Enable

# 2. 로그 아카이빙
# Log > Configuration > Archive
- Archive to External Storage: Enable
- Archive Schedule: Daily
- Archive Format: Compressed (gzip)
- Archive Retention: 1 year
```

**Step 2) 별도의 장비에 보관**

별도의 로그 서버나 저장매체에 로그를 백업하여 장기 보관합니다.

```bash
# 1. Syslog 서버로 전송
# System > Configuration > Remote Logging
- Syslog Server: 192.168.100.10
- Protocol: TCP (신뢰성)
- Port: 514
- Facility: local0

# 2. 외부 저장소로 백업
# System > Maintenance > Backup
- Backup Location: NAS / FTP / SFTP
- Backup Schedule: Daily
- Backup Retention: 1 year
```

**Step 3) 로그 보관 정책 수립**

```bash
# 로그 보관 정책 예시
1. 보관 기간
   - 법적 최소 기준: 3개월
   - 기관 정책: 6개월 ~ 1년
   - 중요 로그: 2년 이상 (사고 관련)

2. 보관 방법
   - 로컬 저장소: 3개월
   - 백업 저장소: 1년
   - 장기 보관: 2년 이상 (별도 미디어)

3. 로그 분류
   - 보안 로그: 장기 보관
   - 시스템 로그: 중기 보관
   - 일반 로그: 단기 보관

4. 삭제 정책
   - 자동 삭제: 보관 기간 경과 후
   - 수동 삭제: 기록 유지 후 승인
   - 영구 보관: 사고 관련 로그
```

### 4. 참고 자료

**법적 근거**

정보통신망법 제45조 (로그의 기록·보관):
- 일반 시스템: 최소 1개월 이상
- 정보보호시스템(보안 장비): 최소 3개월 이상
- 권장: 6개월 ~ 1년 (기관 정책에 따름)

**로그 보관 주기별 권장사항**

| 로그 유형 | 최소 보관 기간 | 권장 보관 기간 | 비고 |
|----------|---------------|---------------|------|
| 보안 장비 로그 | 3개월 | 6개월 ~ 1년 | 법적 최소 기준 |
| 침해사고 로그 | 1년 | 2년 이상 | 법적 증거 자료 |
| 시스템 로그 | 1개월 | 3개월 | 일반 운영 로그 |
| 감사 로그 | 1년 | 3년 이상 | 관리자 활동 로그 |

**주의사항**
- 일반적인 경우 영향이 없습니다.
- 로그 저장 공간을 충분히 확보하세요 (로그 용량 급증 대비).
- 디스크 용량을 주기적으로 모니터링하세요.
- 로그 파일 백업을 정기적으로 수행하세요.
- 개인정보가 포함된 로그는 별도 보호 조치를 취하세요.
- 기관의 로그 보관 정책을 준수하세요.
- 별도의 장비에 보관할 경우 보안을 강화하세요.

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.