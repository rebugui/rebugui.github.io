---
title: "[2026 주요정보통신기반시설] D-12 안전한 리스너 비밀번호 설정 및 사용"
slug: "2026-주정통/D-12"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "오라클데이터베이스Listener의비밀번호설정여부점검"
categories: ["가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Database
---

# 안전한 리스너 비밀번호 설정 및 사용

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | D-12 |
| **점검내용** | 오라클데이터베이스Listener의비밀번호설정여부점검 |
| **점검대상** | Oracle DB |
| **양호기준** | Listener의비밀번호가설정된경우 |
| **취약기준** | Listener의비밀번호가설정되어있지않은경우 |
| **조치방법** | Listener비밀번호설정 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: Listener의 비밀번호가 설정된 경우
- **취약**: Listener의 비밀번호가 설정되어 있지 않은 경우

#### 경계 케이스 (Edge Case) 처리 방법
- **비밀번호 미설정**: 취약 판단
- **비밀번호 설정 완료**: 양호 판단
- **Oracle 12c R2 이상**: IP 접속 제한으로 대체

#### 권장 설정값
- **Listener 비밀번호**: 설정 (11g R2 이하)
- **IP 접속 제한**: 설정 (12c R2 이상)

### 2. 점검 방법

```bash
# Listener 상태 확인
lsnrctl status

# 비밀번호 설정 여부 확인
# Listener 설정이 비밀번호로 보호되어 있는지 확인
```

### 3. 조치 방법

#### Step 1) Listener 비밀번호 설정

```bash
# LSNRCTL 유틸리티 실행
lsnrctl

# 비밀번호 변경
LSNRCTL> change_password
Old password: <Old Password>  # 첫 설정 시 Enter
New password: <New password>
Reenter new password: <New password>

# Password change for LISTENER
# The command completed successfully
```

#### Step 2) 비밀번호 설정 저장

```bash
LSNRCTL> set password
Password: <설정한 비밀번호>

# 설정 저장
LSNRCTL> save_config
```

#### Step 3) Listener 매개변수 설정

```bash
# listener.ora 파일 편집
vi $ORACLE_HOME/network/admin/listener.ora
```

**다음 옵션 추가:**
```ini
PASSWORDS_<listener_name> = <Encrypted Password>
ADMIN_RESTRICTIONS_<listener_name> = ON
```

#### Step 4) Listener 재시작

```bash
# Listener 중지
lsnrctl stop

# Listener 시작
lsnrctl start

# 또는 재시작 없이 설정 적용
lsnrctl reload

# 상태 확인
lsnrctl status
```

### 4. 참고 자료

#### Listener 보안 강화

**ADMIN_RESTRICTIONS 설정:**
- `ON`: LSNRCTL 명령어로는 설정 변경 불가 (listener.ora 직접 수정만 가능)
- `OFF`: LSNRCTL 명령어로 설정 변경 가능

**IP 접속 제한과 병행:**
```ini
# sqlnet.ora
tcp.validnode_checking = yes
tcp.invited_nodes = (127.0.0.1, 허용_IP)
```

#### Oracle 버전별 주의사항

**Oracle 12c Release 2 이후:**
- Oracle 12c R2부터는 Listener 비밀번호 기능이 제거됨
- 대신 Oracle Connection Manager (CMAN) 또는 방화벽을 사용한 네트워크 보안 권장
- IP 접속 제한(sqlnet.ora) 및 OS 인증을 통한 보안 강화 필요

**비밀번호 관리:**
- Listener 비밀번호는 Oracle OS 사용자와 별도로 관리
- 주기적인 비밀번호 변경 권장
- 비밀번호는 암호화되어 listener.ora에 저장

#### 보안 위협

**비밀번호 미설정 시 위험:**
- DoS 공격: Listener 중지로 서비스 거부
- 정보 유출: Listener 설정 및 상태 정보 노출
- 설정 변경: listener.ora 파일 무단 변경

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.