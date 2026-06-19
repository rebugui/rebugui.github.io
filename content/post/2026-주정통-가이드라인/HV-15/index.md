---
title: "[2026 주요정보통신기반시설] HV-15 시스템 주요 이벤트 로그 설정"
slug: "2026-주정통/HV-15"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "시스템주요이벤트로그가설정여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Virtualization
draft: true
---

# HV-15 시스템 주요 이벤트 로그 설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | HV-15 |
| **점검내용** | 시스템주요이벤트로그가설정여부점검 |
| **점검대상** | VMware ESXi, vCenter, KVM 등 |
| **판단기준** | 양호: 로그기록정책이내부정책에부합하게설정된경우 |
| **판단기준** | 취약: 로그기록정책이내부정책에부합하게설정되지않은경우 |
| **조치방법** | 로그기록정책을내부정책에부합하게설정 |

---
## 상세 설명

### 1. 항목 개요

시스템 주요 이벤트 로그 설정은 가상화 장비에서 발생하는 보안, 성능, 장애 관련 이벤트를 적절한 수준으로 기록하는 것을 의미합니다. 로그 레벨이 너무 낮으면 중요한 이벤트를 누락할 수 있고, 너무 높으면 로그 파일이 커져 성능에 영향을 줄 수 있습니다.

적절한 로그 레벨 설정은 보안 사고 탐지, 시스템 문제 해결, 성능 모니터링에 필수적입니다.

### 2. 왜 이 항목이 필요한가요?

**로깅 수준의 중요성:**

1. **보안 사고 탐지**
   - 로그인 실패, 권한 변경 등 보안 이벤트 기록
   - 비정상 행위 탐지
   - 침해 경로 추적

2. **시스템 문제 해결**
   - 장애 발생 원인 파악
   - 에러 추적
   - 성능 병목 지점 식별

3. **규정 준수**
   - 감사 추적
   - 법적 증거 확보
   - 보안 인증 요구사항 충족

**로깅 수준별 특징:**

| 수준 | 설명 | 용도 |
|------|------|------|
| Error | 오류만 기록 | 문제 발생 시 원인 파악 |
| Warning | 경고, 오류 기록 | 잠재적 문제 탐지 |
| Info | 일반 정보 기록 | 시스템 상태 모니터링 |
| Verbose | 상세 정보 기록 | 상세한 문제 해결 |
| Trivia | 모든 정보 기록 | 심층 분석 (성능 저하 위험) |

### 3. 점검 대상

- VMware ESXi
- VMware vCenter
- KVM (RHEL, CentOS, Ubuntu 등)

### 4. 판단 기준

- **양호**: 로그 기록 정책이 내부 정책에 부합하게 설정된 경우
  - 일반적으로 `Warning` 또는 `Information` 수준 권장

- **취약**: 로그 기록 정책이 내부 정책에 부합하게 설정되지 않은 경우
  - `None`, `Quiet`, `Panic` 수준은 취약

### 5. 점검 방법

#### VMware ESXi

1. Web 콘솔 접속
   ```
   https://<VMware ESXi IP>
   ```

2. **호스트** > **관리** > **시스템** > **고급 설정**으로 이동

3. `Config.HostAgent.log.level` 설정값 확인

**양호 기준:**
- `Config.HostAgent.log.level`: `info`, `warning`, `verbose`

**취약 기준:**
- `Config.HostAgent.log.level`: `none`, `quiet`, `panic`

#### VMware vCenter

**vCenter 6.5:**
1. vSphere Client 접속
2. **호스트 및 클러스터** > [vCenter 서버] > **구성** > **설정** > **고급 설정**
3. `config.log.level` 확인

**vCenter 8.0:**
1. vSphere Client 접속
2. **호스트 및 클러스터** > [vCenter 서버] > **구성** > **설정** > **고급 설정**
3. `config.log.level` 확인

#### KVM

1. libvirt 설정 파일 확인
   ```bash
   cat /etc/libvirt/libvirtd.conf | grep log_level
   ```

**libvirt 로그 레벨:**
- 0: DEBUG (모든 항목)
- 1: INFO (디버그가 아닌 모든 항목)
- 2: WARNING (경고 및 오류)
- 3: ERROR (오류만)
- 4: NONE (기록하지 않음)

### 6. 조치 방법

#### VMware ESXi

1. **관리** > **시스템** > **고급 설정**으로 이동

2. `Config.HostAgent.log.level` 선택 후 **옵션 편집** 클릭

3. 값 설정:
   ```
   info
   ```

4. **저장** 클릭

**VMware ESXi 로그 레벨:**

| 로깅 수준 | 설명 |
|-----------|------|
| None | 로그 기록하지 않음 (권장하지 않음) |
| Quiet | 최소한의 로그 항목만 기록 |
| Panic | 패닉 로그만 기록 |
| Error | 패닉 및 에러 로그만 기록 |
| Warning | 패닉, 에러 및 경고 로그 기록 (권장) |
| Information | 패닉, 에러, 경고 및 정보 로그 기록 (권장) |
| Verbose | 상세 정보 포함 (성능 저하 가능성) |
| Trivia | 모든 정보 기록 (성능 저하 위험) |

#### VMware vCenter

**vCenter 6.5:**
1. **호스트 및 클러스터** > [vCenter 서버] > **구성** > **설정** > **고급 설정**

2. `config.log.level` 선택 후 **편집** 클릭

3. 값 설정: `info`

4. **저장** 후 vCenter 서비스 재시작

**vCenter 8.0:**
1. **호스트 및 클러스터** > [vCenter 서버] > **구성** > **설정** > **고급 설정**

2. `config.log.level` 선택 후 **편집** 클릭

3. 값 설정: `info`

4. **저장** 후 vCenter 서비스 재시작

#### KVM

1. libvirt 설정 파일 수정
   ```bash
   vi /etc/libvirt/libvirtd.conf
   ```

2. log_level 설정 추가/수정:
   ```
   log_level = 1
   ```

3. libvirt 데몬 재시작
   ```bash
   systemctl restart libvirtd
   ```

**libvirt 로그 레벨:**

| 레벨 | 로깅 수준 | 설명 |
|------|-----------|------|
| 4 | ERROR | 오류 메시지만 기록 |
| 3 | WARNING | 경고 및 오류를 기록 (권장) |
| 2 | INFO | 디버그 항목이 아닌 모든 항목을 기록 (권장) |
| 1 | DEBUG | 디버그 항목 및 모든 항목을 기록 |

### 7. 로그 파일 위치

#### VMware ESXi

| 로그 파일 | 설명 |
|-----------|------|
| /var/log/vmkernel.log | VMkernel 로그 |
| /var/log/hostd.log | 관리 서버 로그 |
| /var/log/vpxa.log | vCenter Agent 로그 |
| /var/log/auth.log | 인증 로그 |

#### KVM

| 로그 파일 | 설명 |
|-----------|------|
| /var/log/libvirt/libvirtd.log | libvirt 로그 |
| /var/log/messages | 시스템 로그 |
| /var/log/secure | 인증 로그 |
| /var/log/audit/audit.log | 감사 로그 |

### 8. 로그 관리 모범 사례

**1) 로그 레벨 선택 가이드**

| 환경 | 권장 로그 레벨 |
|------|----------------|
| 운영 환경 (Production) | Warning 또는 Info |
| 개발/테스트 환경 | Info 또는 Verbose |
| 문제 해결 중 | Verbose (일시적) |
| 높은 보안 요구 | Info (보안 이벤트 포함) |

**2) 로그 회전 (Log Rotation)**

```bash
# ESXi 로그 회전 설정
vi /etc/logrotate.conf

# 설정 예
/var/log/vmkernel.log {
    weekly
    rotate 4
    compress
    missingok
    notifempty
}
```

**3) 로그 모니터링**

- 정기적 로그 검토 (일일/주간)
- 자동화된 로그 분석 도구 사용
- 비정상 패턴 탐지

**4) 로그 보관**

- 보안 로그: 최소 1년
- 감사 로그: 최소 3년
- 시스템 로그: 최소 6개월

### 9. 로그 분석 도구

**오픈 소스:**
- **ELK Stack**(Elasticsearch, Logstash, Kibana)
- **Graylog**
- **Splunk**(Free Tier)

**명령줄 도구:**
```bash
# grep
grep "error" /var/log/vmkernel.log

# tail (실시간 모니터링)
tail -f /var/log/hostd.log

# less (로그 파일 탐색)
less /var/log/vpxa.log
```

### 10. 주요 로그 검토 항목

**보안 관련:**
- 로그인 실패
- 권한 변경
- 계정 생성/삭제
- 방화벽 규칙 변경

**시스템 관련:**
- 서비스 중지/시작
- 장애 발생
- 리소스 부족

**성능 관련:**
- CPU/메모리 사용률
- 디스크 I/O 병목
- 네트워크 지연

### 11. 주의사항

- **Verbose** 및 **Trivia** 수준은 성능 저하를 일으킬 수 있음
- 로그 파일 크기 정기적 모니터링 필요
- 로그 파일 디스크 공간 충분히 확보
- 너무 낮은 로그 레벨(`None`, `Quiet`)은 보안 위협
- 문제 해결 시 일시적으로 로그 레벨 상향 후 복구

## 요약

시스템 주요 이벤트 로그는 **Info(정보) 또는 Warning(경고) 수준**으로 설정하는 것을 권장합니다. 너무 낮은 수준은 중요한 이벤트를 누락할 수 있고, 너무 높은 수준(Verbose, Trivia)은 성능 저하를 일으킬 수 있습니다. 내부 보안 정책에 맞는 **적절한 로깅 수준**을 설정하고 정기적으로 로그를 검토해야 합니다.
