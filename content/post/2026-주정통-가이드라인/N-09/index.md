---
title: "[2026 주요정보통신기반시설] N-09 불필요한 보조 입출력 포트 사용 금지"
slug: "2026-주정통/N-09"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "사용하지 않는 보조(AUX) 포트 및 콘솔 점검. 장비 관리나 운용에 쓰이지 않는 포트 및 인터페이스가 비활성화되어 있는지 점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Network
---

# N-09 불필요한 보조 입출력 포트 사용 금지

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | N-09 |
| **점검내용** | 사용하지 않는 보조(AUX) 포트 및 콘솔 점검. 장비 관리나 운용에 쓰이지 않는 포트 및 인터페이스가 비활성화되어 있는지 점검 |
| **점검대상** | Cisco, Juniper 등 |
| **양호기준** | 불필요한 포트 및 인터페이스 사용을 제한한 경우 |
| **취약기준** | 불필요한 포트 및 인터페이스 사용을 제한하지 않은 경우 |
| **조치방법** | 불필요한 포트 및 인터페이스 사용 제한 또는 비활성화 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준

**양호**
- 불필요한 포트 및 인터페이스 사용을 제한한 경우
- AUX 포트가 비활성화된 경우
- 사용하지 않는 인터페이스가 shutdown된 경우

**취약**
- 불필요한 포트 및 인터페이스 사용을 제한하지 않은 경우
- AUX 포트가 활성화된 경우

#### 경계 케이스 (Edge Case) 처리 방법

1. **콘솔 포트 관리**
   - 일반적: 로컬 관리에 필요하므로 활성화 유지
   - 비상시: 물리적 보안이 확보된 위치에서만 사용
   - 대체안: SSH 등 원격 관리 방법 확보 시 비활성화 고려

2. **AUX 포트 사용**
   - 모뎀 연결: 원격 접속에 사용 중인 경우 활성화 유지
   - 미사용: 반드시 비활성화하여 물리적 접근 차단

3. **인터페이스 shutdown**
   - 현재 미사용: 즉시 shutdown
   - 향후 사용 예정: 설정 후 비활성화, 문서화

#### 권장 설정값

- AUX 포트: 사용하지 않는 경우 반드시 비활성화
- 콘솔 포트: 물리적 보안 확보 시 사용, 그 외 비활성화 고려
- 미사용 인터페이스: shutdown으로 비활성화
- 물리적 보안: 장비실 출입 통제, CCTV 설치

### 2. 점검 방법

**Cisco IOS 장비:**

```bash
# Step 1) 불필요한 포트 및 인터페이스 사용 확인
Router> enable
Router# show running-config

# 또는
Router# show line

# 불필요한 보조 입출력 포트의 상태를 확인합니다:
# - Up: 활성화
# - Down: 비활성화

# AUX 라인 설정 확인
Router# show line aux 0

# 인터페이스 상태 확인
Router# show ip interface brief
```

**Juniper Junos 장비:**

```bash
# Step 1) 불필요한 포트 및 인터페이스 사용 확인
user@host> configure
[edit]
user@host# show

# [edit system ports] 레벨에서 auxiliary 포트 설정을 확인합니다.
user@host# show system ports auxiliary

# 인터페이스 상태 확인
user@host> show interfaces terse
```

### 3. 조치 방법

**Cisco IOS:**

```bash
# Step 1) AUX 포트 접속 차단
Router# config terminal
Router(config)# line aux 0

# 다음 설정 중 하나 또는 모두를 적용합니다:

# 1) 비밀번호 제거
Router(config-line)# no password

# 2) 입력 차단
Router(config-line)# transport input none

# 3) 명령 실행 차단
Router(config-line)# no exec

# 4) 즉시 타임아웃 (1초)
Router(config-line)# exec-timeout 0 1

# 완전한 보안 설정 예시:
Router(config)# line aux 0
Router(config-line)# no password
Router(config-line)# transport input none
Router(config-line)# no exec
Router(config-line)# exec-timeout 0 1
Router(config-line)# exit

# Step 2) 미사용 인터페이스 비활성화
Router(config)# interface <interface-name>
Router(config-if)# shutdown
```

**Juniper Junos:**

```bash
# Step 1) 보조(AUX) 포트 비활성화 설정
user@host> configure
[edit system ports]
user@host# set auxiliary disable
[edit system ports]
user@host# commit

# Step 2) 미사용 인터페이스 비활성화
[edit interfaces]
user@host# set <interface-name> disable
user@host# commit
```

### 4. 참고 자료

**AUX 포트란?**
- 정의: 모뎀 연결을 위한 보조 포트
- 용도: 원격 전화 접속, null modem 케이블 연결
- 위험: 물리적 접근 경로가 될 수 있음

**보안 위협:**
1. 물리적 접근 위험: 공격자가 모뎀 연결로 원격 접근 가능
2. 무단 접근: 비밀번호 없이 장비 접근 위험
3. Null Modem 케이블: 다른 장비와 연결하여 무단 접근

**주의사항:**
1. 필요한 포트 확인 후 비활성화
2. 콘솔 포트는 물리적 보안 확보 시 사용 권장
3. AUX 포트 비활성화 전 SSH 등 대안 확인
4. 비상시 장비 복구를 위해 콘솔 포트는 보안된 위치 유지 권장
5. 정기적 점검으로 불필요한 포트 활성화 확인
6. 물리적 보안(출입 통제, CCTV)과 병행
7. 비활성화 포트 문서화

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.