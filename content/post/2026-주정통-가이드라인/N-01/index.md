---
title: "[2026 주요정보통신기반시설] N-01 비밀번호 설정"
slug: "2026-주정통/N-01"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "관리 터미널(콘솔, SSH, https 등)을 통해 네트워크 장비 접근 시 기본 비밀번호(기본 관리자 계정도 함께 변경하도록 권고)를 사용하는지 점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Network
---

# N-01 비밀번호 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | N-01 |
| **점검내용** | 관리 터미널(콘솔, SSH, https 등)을 통해 네트워크 장비 접근 시 기본 비밀번호(기본 관리자 계정도 함께 변경하도록 권고)를 사용하는지 점검 |
| **점검대상** | Cisco, Alteon, Passport, Juniper, Piolink 등 |
| **양호기준** | 기본비밀번호를 변경한 경우 |
| **취약기준** | 기본비밀번호를 변경하지 않거나 비밀번호를 설정하지 않은 경우 |
| **조치방법** | 기본비밀번호를 관리기관의 비밀번호 작성규칙을 준용하여 변경 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준

**양호**
- 기본비밀번호를 변경한 경우
- 관리자 계정도 함께 변경한 경우

**취약**
- 기본비밀번호를 변경하지 않거나 비밀번호를 설정하지 않은 경우

#### 경계 케이스 (Edge Case) 처리 방법

1. **레거시 장비**
   - 비밀번호 변경 기능 제한: 최대한 강력한 비밀번호 설정
   - 별도 인증 방식: AAA 서버 연동 권장

2. **다중 관리자 환경**
   - 개별 계정 생성 필수
   - 계정별 비밀번호 관리

#### 권장 설정값

- 최소 8자리 이상 (권장: 12자리 이상)
- 영문 대문자, 소문자, 숫자, 특수문자 조합
- 개인정보 포함 금지
- 사전에 있는 단어 금지

### 2. 점검 방법

**Cisco IOS 장비:**

```bash
# Step 1) enable 비밀번호 설정 확인
Router> enable
Router# show running-config

# Step 2) VTY, 콘솔, 보조(AUX) 포트의 로그인 인증 방식 및 비밀번호 설정 확인
# - login: 라인 비밀번호 인증
# - login local: 로컬 사용자 인증
# - login authentication: AAA 인증
# - no login: 인증 없이 사용자 모드 접근
```

**Radware Alteon 장비:**

```bash
# Step 1) admpw 설정 확인
Main# /cfg/dump

# Step 2) 관리자 비밀번호 변경
Main# /cfg/sys/access/user/admpw
Main# apply
Main# save
```

**Passport 장비:**

```bash
# Step 1) 비밀번호 설정 확인
# show config

# Step 2) 계정별 비밀번호 변경
# config cli password ro <계정명>
# config cli password rw <계정명>
# config cli password rwa <계정명>
```

**Juniper Junos 장비:**

```bash
# Step 1) root authentication 설정 확인
user@host> configure
[edit]
user@host# show

# Step 2) 루트 사용자 계정의 비밀번호 변경
user@host> configure
[edit]
user@host# set system root-authentication plain-test-passwd
```

### 3. 조치 방법

**Cisco IOS 비밀번호 변경:**

```bash
# Enable 비밀번호 설정
Router# config terminal
Router(config)# enable secret <비밀번호>

# 콘솔 비밀번호 설정
Router(config)# line console 0
Router(config-line)# password <비밀번호>
Router(config-line)# login

# VTY 비밀번호 설정
Router(config)# line vty 0 4
Router(config-line)# password <비밀번호>
Router(config-line)# login

# 로컬 사용자 계정 생성
Router(config)# username <사용자명> secret <비밀번호>
Router(config)# username <사용자명> privilege 15
```

**주요 네트워크 장비별 기본 비밀번호:**
- Cisco: cisco/cisco
- Juniper: root/123456
- Alteon: admin/admin
- Passport: admin/admin

### 4. 참고 자료

**비밀번호 작성규칙 예시**
1. 사용자 계정(아이디)과 동일하지 않은 것
2. 개인 신상 및 부서 명칭 등과 관계가 없는 것
3. 일반 사전에 등록된 단어의 사용을 피할 것
4. 동일한 단어 또는 숫자를 반복하여 사용하지 말 것
5. 사용된 비밀번호는 재사용하지 말 것

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.