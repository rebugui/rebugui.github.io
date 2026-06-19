---
title: "[2026 주요정보통신기반시설] N-10 로그온 시 경고 메시지 설정"
slug: "2026-주정통/N-10"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "터미널 접속 화면에 비인가자의 불법 접근에 대한 경고 메시지를 표시하도록 설정되어 있는지 점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Network
draft: true
---

# N-10 로그온 시 경고 메시지 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | N-10 |
| **점검내용** | 터미널 접속 화면에 비인가자의 불법 접근에 대한 경고 메시지를 표시하도록 설정되어 있는지 점검 |
| **점검대상** | Cisco, Alteon, Juniper 등 |
| **양호기준** | 로그온 시 접근에 대한 경고 메시지를 설정한 경우 |
| **취약기준** | 로그온 시 접근에 대한 경고 메시지를 설정하지 않거나 시스템 관련 정보가 노출되는 경우 |
| **조치방법** | 네트워크 장비 접속 시 경고 메시지 설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준

**양호**
- 로그온 시 접근에 대한 경고 메시지를 설정한 경우
- 시스템 정보 노출 없이 경고 메시지만 표시되는 경우

**취약**
- 로그온 시 접근에 대한 경고 메시지를 설정하지 않은 경우
- 시스템 관련 정보가 노출되는 경우

#### 경계 케이스 (Edge Case) 처리 방법

1. **기본 배너 제거**
   - 위험: 기본 배너에 장비 모델, OS 버전 정보 포함
   - 조치: 벤더 기본 배너 제거 후 보안 경고 메시지 설정

2. **다국어 지원**
   - 국내 관리자: 국문 메시지
   - 해외 관리자: 영문 메시지 또는 이중 언어 지원

3. **법적 효력**
   - 법적 검토: 기관 법무팀과 메시지 내용 검토
   - 표준 문구: 법적 효력을 고려한 문구 사용

#### 권장 설정값

**경고 메시지 포함 요소:**
1. 접근 권한 명시: "Authorized Access Only"
2. 모니터링 경고: "All access is monitored and logged"
3. 법적 조치 경고: 불법 접근 시 법적 조치 가능성 명시
4. 동의 의미: 접속 시 모니터링에 동의하는 것으로 간주

**제거할 정보:**
- 장비 제조사 및 모델명
- 운영체제 버전
- 네트워크 토폴로지 정보
- 기타 시스템 내부 정보

### 2. 점검 방법

**Cisco IOS 장비:**

```bash
# Step 1) 배너 설정 내용 확인
Router> enable
Router# show running-config

# 다음 배너 설정을 확인합니다:
# - banner motd: Message of the Day
# - banner login: 로그인 전 표시
# - banner exec: 로그인 후 표시

# 배너 내용 확인
Router# show banner motd
Router# show banner login
Router# show banner exec
```

**Radware Alteon 장비:**

```bash
# Step 1) banner 설정 내용 확인
Main# /cfg/dump

# banner <string> 설정을 확인합니다.
```

**Juniper Junos 장비:**

```bash
# Step 1) login message 설정 확인
user@host> configure
[edit]
user@host# show system login

# message 설정을 확인합니다.
```

### 3. 조치 방법

**Cisco IOS:**

```bash
# Step 1) 배너 설정
Router# config terminal

# MOTD 배너 설정
Router(config)# banner motd #
Enter TEXT message. End with the character '#'.
******************************************************************
* Authorized Access Only                                       *
* All access is monitored and logged.                          *
* Unauthorized access is prohibited and violators will be      *
* prosecuted to the full extent of the law.                    *
******************************************************************
#

# Login 배너 설정 (로그인 전 표시)
Router(config)# banner login #
Enter TEXT message. End with the character '#'.
Authorized Access Only. Unauthorized access will be prosecuted.
#

# 참고: # 문자는 구분자(delimiter)로 사용되며, 다른 문자도 사용 가능합니다.
```

**Radware Alteon:**

```bash
# Step 1) Banner 설정
Main# /cfg
Main# /sys
Main# /banner Authorized Access Only. All access is monitored and logged.
Main# apply
Main# save
```

**Juniper Junos:**

```bash
# Step 1) Login message 설정
user@host> configure
[edit system login]
user@host# set message "Authorized Access Only. All access is monitored and logged. Unauthorized access is prohibited and violators will be prosecuted."
[edit system login]
user@host# commit
```

### 4. 참고 자료

**권장 메시지 예시 (국문):**

```
******************************************************************
* 이 시스템은 승인된 사용자만 접근할 수 있습니다.           *
* 모든 접속은 모니터링되며 기록됩니다.                       *
* 불법 접속 시 법적 조치를 취할 수 있습니다.                  *
******************************************************************
```

**권장 메시지 예시 (영문):**

```
******************************************************************
* Authorized Access Only                                       *
* All access is monitored and logged.                          *
* Unauthorized access is prohibited and violators will be      *
* prosecuted to the full extent of the law.                    *
******************************************************************
```

**주의사항:**
1. 시스템 정보 노출 금지: 배너에 장비 모델, OS 버전, IP 주소 등 포함하지 않기
2. 법적 검토: 기관의 법무팀과 검토하여 적절한 문구 사용
3. 메시지 길이: 사용자 경험을 저해하지 않는 적절한 길이
4. 국문/영문: 관리자에 따라 적절한 언어로 작성
5. 일관성: 모든 네트워크 장비와 시스템에 일관된 메시지 적용
6. 정기적 검토: 기관 보안 정책 변경에 따라 메시지 업데이트

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.