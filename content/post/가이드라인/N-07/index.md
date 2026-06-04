---
title: "[2026 주요정보통신기반시설] N-07 세션 종료 시간 설정"
slug: "2026-주정통/N-07"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "기관 정책에 맞게 Session Timeout 설정이 적용되어 있는지 점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Network
---

# N-07 세션 종료 시간 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | N-07 |
| **점검내용** | 기관 정책에 맞게 Session Timeout 설정이 적용되어 있는지 점검 |
| **점검대상** | Cisco, Alteon, Juniper, Piolink 등 |
| **양호기준** | Session Timeout 시간을 10분 이하로 설정한 경우 |
| **취약기준** | Session Timeout 시간을 설정하지 않거나 10분 초과로 설정한 경우 |
| **조치방법** | Session Timeout 설정 (10분 이하 권고) |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준

**양호**
- Session Timeout 시간을 10분 이하로 설정한 경우

**취약**
- Session Timeout 시간을 설정하지 않거나 10분 초과로 설정한 경우

#### 경계 케이스 (Edge Case) 처리 방법

1. **장시간 작업 필요 시**
   - 문제: 설정 작업 중 세션이 자동 종료
   - 대책: 작업 전 `no exec-timeout` 일시 설정, 작업 후 즉시 복원
   - 주의: 작업 종료 후 반드시 원래대로 복원

2. **업무 특성 고려**
   - 모니터링 업무: 5분 권장
   - 설정 변경 업무: 필요시 일시 해제 후 복원
   - 보안 우선: 편의성보다 보안 우선

3. **다중 세션 관리**
   - 여러 VTY 세션: 모든 세션에 동일하게 적용
   - 콘솔 포트: Console, VTY, AUX 모두 설정 필요

#### 권장 설정값

- 세션 타임아웃: 5분 (권장), 최대 10분
- 적용 대상: Console, VTY, AUX 모든 라인
- 단위: 분(0-35791), 초(0-59)

### 2. 점검 방법

**Cisco IOS 장비:**

```bash
# Step 1) 각 Line Access의 exec-timeout 설정 확인
Router> enable
Router# show running-config

# 다음 라인의 exec-timeout 설정을 확인합니다:
# - line con 0: 콘솔
# - line vty 0 4: VTY (원격 접속)
# - line aux 0: 보조 포트

# 예시 출력:
# line con 0
#  exec-timeout 5 0
#  login
#
# line vty 0 4
#  exec-timeout 5 0
#  login
#  transport input ssh
```

**Radware Alteon 장비:**

```bash
# Step 1) idle timeout 설정 확인
Main# /cfg
Main# /sys

# idle timeout in minutes 설정을 확인합니다.
# 기본값: 5분
```

**Juniper Junos 장비:**

```bash
# Step 1) idle-timeout 설정 확인
user@host> configure
[edit]
user@host# show

# login class별 idle-timeout 설정을 확인합니다.
# 예시:
# system {
#     login {
#         class operator {
#             idle-timeout 5;
#         }
#     }
# }
```

**Piolink PLOS 장비:**

```bash
# Step 1) terminal timeout 설정 확인
# configure terminal
(config)# show running-config

# terminal timeout 설정을 확인합니다.
```

### 3. 조치 방법

**Cisco IOS:**

```bash
# Step 1) Console 세션 타임아웃 설정
Router# config terminal
Router(config)# line con 0
Router(config-line)# exec-timeout 5 0

# Step 2) VTY 세션 타임아웃 설정
Router(config)# line vty 0 4
Router(config-line)# exec-timeout 5 0

# Step 3) AUX 세션 타임아웃 설정 (사용 시)
Router(config)# line aux 0
Router(config-line)# exec-timeout 5 0

# exec-timeout 파라미터 설명:
# exec-timeout <분> <초>
# - exec-timeout 5 0: 5분 후 세션 종료
# - exec-timeout 10 30: 10분 30초 후 세션 종료
# - exec-timeout 0 0: 타임아웃 비활성화 (권장하지 않음)
```

**Radware Alteon:**

```bash
# Step 1) idle timeout 설정
Main# /cfg
Main# /sys
Main# /idle 5
Main# apply
Main# save

# 기본값: 5분
# 콘솔과 Telnet 모두에 영향을 미칩니다.
```

**Juniper Junos:**

```bash
# Step 1) login class별 idle-timeout 설정
user@host> configure
[edit login]
user@host# set class operator idle-timeout 5
user@host# set class read-only idle-timeout 5
user@host# set class superuser idle-timeout 5

# Step 2) 설정 저장
user@host# commit
```

**Piolink PLOS:**

```bash
# Step 1) terminal timeout 설정
# configure terminal
(config)# terminal timeout 5

# 설정 가능 범위: 1분에서 60분 사이
# 권장: 5분 이하
```

### 4. 참고 자료

**세션 타임아웃 설정의 필요성:**

1. **관리자 부재시 악용 방지**
   - 관리자가 자리를 비운 사이 비인가자 접근 방지
   - 자리를 비울 때는 반드시 로그아웃 필요

2. **책임 소재 명확화**
   - 세션 만료로 세션 하이재킹 방지
   - 감사 로그의 신뢰성 확보

3. **보안 정책 준수**
   - 기관의 정보 보안 정책 준수
   - 규정 준수(Compliance) 요구사항 충족

**장시간 작업 시 대처 방법:**

```bash
# 장시간 작업 전 일시 해제
Router(config)# line vty 0 4
Router(config-line)# no exec-timeout
Router(config-line)# exit

# 작업 수행...

# 작업 후 반드시 복원
Router(config)# line vty 0 4
Router(config-line)# exec-timeout 5 0
```

**권장 설정 요약:**
- 콘솔(Console): 5분
- VTY: 5분
- AUX: 5분 (비활성화되어 있다면 설정 불필요)

**주의사항:**
1. 가이드라인에 따라 10분 이하로 설정
2. 모든 라인(Console, VTY, AUX)에 설정 적용
3. 장비 설정 변경 시 타임아웃 설정 유지 확인
4. 장시간 작업 시에도 작업 후 반드시 복원
5. 기관의 정보 보안 정책 준수

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.