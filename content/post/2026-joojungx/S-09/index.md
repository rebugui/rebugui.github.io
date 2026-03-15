---
title: "[2026 주요정보통신기반시설] S-09 주기적 보안패치 및 벤더권고사항 적용"
slug: "2026-주정통/S-09"
date: 2026-02-05T09:56:12+09:00
lastmod: 2026-02-05T09:56:12+09:00
description: "보안장비 OS 및 보안 기능(IPS, 안티바이러스 등)을 주기적으로 보안 패치 여부 점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Security
---

# S-09 주기적 보안패치 및 벤더권고사항 적용

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | S-09 |
| **점검내용** | 보안장비 OS 및 보안 기능(IPS, 안티바이러스 등)을 주기적으로 보안 패치 여부 점검 |
| **점검대상** | 방화벽, VPN, IDS, IPS, Anti-DDoS, 웹방화벽 등 |
| **양호기준** | 주기적 보안패치 및 벤더권고사항이 적용된 경우 |
| **취약기준** | 주기적 보안패치 및 벤더권고사항이 적용되지 않은 경우 |
| **조치방법** | 벤더사에서 주기적으로 제공하는 장비별 최신 취약점 정보를 파악 후 최신 패치 및 업그레이드를 수행 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준

**양호**
- 주기적 보안패치 및 벤더권고사항이 적용된 경우

**취약**
- 주기적 보안패치 및 벤더권고사항이 적용되지 않은 경우

#### 경계 케이스 (Edge Case) 처리 방법

1. **24시간 운영 시스템**
   - 이중화 구성: 순차적 패치 적용
   - 유지보수 창: 최소 다운타임 시간대 선택

2. **호환성 문제**
   - 테스트 환경에서 검증 후 운영 적용
   - 롤백 계획 필수 수립

#### 권장 설정값

- Critical 취약점: 즉시 (24시간 이내)
- High 취약점: 1주 이내
- Medium 취약점: 1개월 이내
- Low 취약점: 정기 점검 시 (분기/반기)

### 2. 점검 방법

**Step 1) 보안 장비의 최신 패치 현황 파악**

장비의 현재 버전과 최신 버전을 확인합니다.

```bash
# 현재 버전 확인
show version

# 예시 출력
# Software version: 5.2.1
# Last updated: 2023-05-15
```

**Step 2) 벤더사에 문의하여 최신 패치 현황 파악**

벤더사 웹사이트나 기술 지원을 통해 최신 패치 정보를 확인합니다.

```bash
# 주요 벤더사 패치 페이지
- Cisco: https://tools.cisco.com/security/center/
- Palo Alto: https://security.paloaltonetworks.com/
- Fortinet: https://www.fortiguard.com/psirt
- Check Point: https://supportcontent.checkpoint.com/
- SonicWall: https://psirt.sonicwall.com/
```

**Step 3) 주기적으로 업데이트 필요성에 대한 검토 및 조처를 하고 있는지 문서 검토**

다음 문서들을 통해 패치 관리 프로세스를 확인합니다:
- 정기 점검 보고서
- 검토 보고서
- 작업 계획서
- 패치 관리 대장

### 3. 조치 방법

**Step 1) 자동 패치 기능 설정 또는 벤더사에 문의하여 수동으로 패치 수행**

대부분의 최신 보안 장비는 자동 업데이트 기능을 제공합니다.

**자동 업데이트 설정 (Palo Alto 예시):**

```bash
# Device > Software > Check for Updates
# 자동 업데이트 스케줄 설정
# Schedule: 매일 새벽 2시간
# Auto Download: Enable
# Auto Install: Disable (관리자 승인 후 설치 권장)
```

**수동 패치 절차:**

```bash
# 1. 패치 파일 다운로드
# 벤더사 포털에서 최신 패치 다운로드

# 2. 유지보수 창(Maintenance Window) 설정
# 업무 영향이 최소화되는 시간대 선택

# 3. 패치 적용 전 백업
# System > Configuration > Backup

# 4. 테스트 환경에서 패치 검증 (권장)
# 동일 모델의 테스트 장비에서 패치 테스트

# 5. 패치 적용
# System > Software > Install Update

# 6. 장비 재부팅 (필요시)
# 시스템 다운타임 발생

# 7. 동작 확인
# 정책 동작, 로그 기록, 네트워크 연결 등 확인
```

**IPS/안티바이러스 시그니처 업데이트 (IPS 예시):**

```bash
# 1. 자동 업데이트 설정
# Security > Updates > Threat Prevention
# Auto Download: Enable
# Schedule: 매시간 또는 매일

# 2. 수동 업데이트
# Security > Updates > Check Now
# Download & Install

# 3. 업데이트 확인
# show threat-prevention version
# Current version: 8875-6789 (2024-01-15 14:30:00)
```

**Step 2) 패치 적용 일정 수립**

```bash
# 권장 패치 주기
- Critical 취약점: 즉시 (24시간 이내)
- High 취약점: 1주 이내
- Medium 취약점: 1개월 이내
- Low 취약점: 정기 점검 시 (분기/반기)

# 정기 점검 일정 예시
- 주간 점검: 매주 일요일 새벽 2시간
- 월간 점검: 매월 마지막 주 일요일
- 분기 점검: 분기말 정기 점검 시
```

### 4. 참고 자료

- CVE(Common Vulnerabilities and Exposures): https://cve.mitre.org/
- NVD(National Vulnerability Database): https://nvd.nist.gov/
- KISA 취약점 공고: https://www.kisa.or.kr/

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.