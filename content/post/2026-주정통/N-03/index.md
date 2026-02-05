---
title: "[2026 주요정보통신기반시설] N-03 암호화된 비밀번호 사용"
slug: "2026-주정통/N-03"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "계정 비밀번호 암호화 설정이 적용되어 있는지 점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Network
---

# N-03 암호화된 비밀번호 사용

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | N-03 |
| **점검내용** | 계정 비밀번호 암호화 설정이 적용되어 있는지 점검 |
| **점검대상** | Cisco, Juniper 등 |
| **양호기준** | 비밀번호 암호화 설정을 적용한 경우 |
| **취약기준** | 비밀번호 암호화 설정을 적용하지 않은 경우 |
| **조치방법** | 비밀번호 암호화 설정 적용 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준

**양호**
- 비밀번호 암호화 설정을 적용한 경우

**취약**
- 비밀번호 암호화 설정을 적용하지 않은 경우

#### 경계 케이스 (Edge Case) 처리 방법

1. **enable vs enable secret**
   - enable password: 평문 저장 (취약)
   - enable secret: MD5 해시 (양호)
   - 우선순위: enable secret가 높음

2. **Password-Encryption 서비스**
   - service password-encryption: 양방향 암호화 (V5)
   - 양방향은 복호화 가능하지만 평문보다 안전

#### 권장 설정값

- enable secret 사용 (일방향 암호화)
- username secret 사용
- service password-encryption 활성화

### 2. 점검 방법

**Cisco IOS 장비:**

```bash
# Step 1) enable secret 사용 확인
Router> enable
Router# show running-config

# `enable secret` 명령어로 설정된 비밀번호가 있는지 확인합니다.
# 이는 MD5 해싱을 사용하여 일방향 암호화된 비밀번호입니다.

# Step 2) 계정명 secret 사용 확인
Router# show running-config

# 사용자 계정이 `username <사용자> secret <비밀번호>` 형태로 설정되어 있는지 확인합니다.

# Step 3) Password-Encryption 서비스 동작 확인
Router# show running-config

# `service password-encryption` 설정이 있는지 확인합니다.
# 이 서비스는 구성 파일의 평문 비밀번호를 양방향 암호화로 저장합니다.
```

**Juniper Junos 장비:**

```bash
# Step 1) root authentication 설정 확인
user@host> configure
[edit]
user@host# show

# Juniper 장비는 기본적으로 비밀번호를 암호화하여 저장합니다.
# `plain-text-password` 옵션을 사용하면 입력한 비밀번호를 자동으로 암호화합니다.
```

### 3. 조치 방법

**Cisco IOS:**

```bash
# Step 1) enable secret 설정
# `enable secret` 명령어를 사용하여 enable 비밀번호를 일방향 암호화로 저장합니다.
Router# config terminal
Router(config)# enable secret <비밀번호>
Router(config)# end

# 주의: `enable secret`와 `enable password` 명령어로 각각 비밀번호를 사용하는 경우
# `enable secret` 명령어의 우선순위가 높습니다. 보안상 두 비밀번호는 서로 다르게 입력해야 합니다.

# Step 2) username secret 설정
# `username secret` 명령어를 사용하여 로컬 사용자 비밀번호를 일방향 암호화로 저장합니다.
Router# config terminal
Router(config)# username <사용자 이름> secret <비밀번호>

# Step 3) Password-Encryption 서비스 설정
# `service password-encryption` 명령어를 활성화하면 설정 파일의 모든 평문 비밀번호를
# 양방향 암호화 (Cisco 고유 알고리즘, V5)로 변환하여 저장합니다.
Router# config terminal
Router(config)# service password-encryption
```

### 4. 참고 자료

**암호화 방식 비교:**

| 방식 | 명령어 | 암호화 형태 | 보안 수준 |
|------|--------|-------------|-----------|
| 평문 | enable password | 없음 | 매우 낮음 |
| 양방향 | service password-encryption | Cisco V5 | 중간 |
| 일방향 | enable secret | MD5 해시 | 높음 |

**주의사항:**
1. enable secret와 enable password를 같이 설정하는 경우 각각 다른 비밀번호를 사용해야 합니다.
2. Password-Encryption 서비스는 기존 평문 비밀번호만 암호화하며, 새로 설정하는 비밀번호는 secret 명령을 사용해야 합니다.

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.