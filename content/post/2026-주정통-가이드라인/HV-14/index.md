---
title: "[2026 주요정보통신기반시설] HV-14 원격 로그 서버 이용"
slug: "2026-주정통/HV-14"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "원격로그서버를이용한로그저장여부점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Virtualization
draft: true
---

# HV-14 원격 로그 서버 이용

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | HV-14 |
| **점검내용** | 원격로그서버를이용한로그저장여부점검 |
| **점검대상** | VMware ESXi, vCenter, XenServer, KVM, Nutanix 등 |
| **판단기준** | 양호: 원격로그서버또는스토리지가연동설정된경우 |
| **판단기준** | 취약: 원격로그서버또는스토리지가연동설정되지않은경우 |
| **조치방법** | 원격로그서버또는스토리지연동설정 |

---
## 상세 설명

### 1. 항목 개요

원격 로그 서버(Remote Log Server)는 시스템에서 발생하는 로그를 네트워크를 통해 중앙의 로그 서버로 전송하여 저장하는 보안 기능입니다. 가상화 장비의 로그를 원격 서버에 저장하면 시스템 장애, 침해 사고, 데이터 유출 시에도 로그가 보존되어 사고 조사와 보안 대응이 가능합니다.

### 2. 왜 이 항목이 필요한가요?

**원격 로그 서버의 중요성:**

1. **로그 유실 방지**
   - 시스템 장애 시 로그 손실 방지
   - 침해자가 로그 삭제 방지
   - 하드웨어 고장 시 로그 보존

2. **중앙 집중式 로그 관리**
   - 다수 시스템 로그 통합 관리
   - 효율적인 로그 분석
   - SIEM(Security Information and Event Management) 연동

3. **보안 사고 조사**
   - 침해 경로 추적
   - 포렌식 분석
   - 법적 증거 확보

**위험 시나리오:**

```
해커 → 가상화 장비 침해
→ 침해 흔적 삭제 (로그 파일 삭제)
→ 시스템 재부팅 (메모리 로그 소멸)
→ 관리자가 침해 사실 인지 못함
→ 지속적 백도어 유지
→ 결제 정보, 개인정보 유출
```

**실제 사고 사례:**
- 랜섬웨어 감염 후 로그 삭제로 초기 침킹 경로 파악 불가
- 관리자 실수로 로그 파일 삭제
- 디스크 장애로 모든 로그 소실

### 3. 점검 대상

- VMware ESXi
- VMware vCenter
- Citrix XenServer
- KVM (RHEL, CentOS, Ubuntu 등)
- Nutanix AHV

### 4. 판단 기준

- **양호**: 원격 로그 서버 또는 스토리지가 연동 설정된 경우
- **취약**: 원격 로그 서버 또는 스토리지가 연동 설정되지 않은 경우

### 5. 점검 방법

#### VMware ESXi

1. **관리** > **시스템** > **고급 설정**으로 이동

2. `Syslog.global.logHost` 설정값 확인

**양호 기준:**
```
Syslog.global.logHost = tcp://192.168.1.10:514 또는
Syslog.global.logHost = ssl://syslog.example.com:6514
```

**취약 기준:**
```
Syslog.global.logHost = <blank>
```

#### VMware vCenter

1. vCenter Server 관리 페이지 접속 (https://<주소>:5480/)

2. **Syslog** > Syslog 설정 여부 확인

#### KVM

1. `/etc/rsyslog.conf` 파일 확인
   ```bash
   cat /etc/rsyslog.conf | grep -v "^#" | grep "@@"
   ```

2. 원격 로그 전송 지시어 확인

#### XenServer

1. Remote Log Server 사용 유무 확인

2. UDP 514 포트 확인
   ```bash
   netstat -an | grep "udp" | grep "514"
   ```

#### Nutanix

1. Controller VM 접속
   ```bash
   ncli rsyslog-config list
   ```

2. RSyslog 상태 확인

### 6. 조치 방법

#### VMware ESXi

1. **관리** > **시스템** > **고급 설정**으로 이동

2. `Syslog.global.logHost` 선택 후 **옵션 편집** 클릭

3. 원격 로그 서버 입력:
   ```
   tcp://192.168.1.10:514
   ssl://syslog.example.com:6514
   udp://192.168.1.10:514
   ```

**Syslog 설정 예시:**

| 프로토콜 | 예시 | 설명 |
|---------|------|------|
| TCP | tcp://10.0.1.10:3555 | TCP 및 Port 3555 사용 |
| UDP | udp://10.0.1.10 | UDP 및 Port 514 사용 |
| SSL/TLS | ssl://syslog.com | SSL(TLS) 및 Port 6514 사용 |
| IPv6 | tcp://[2001:db8::1]:514 | IPv6 주소 사용 |

#### VMware vCenter

1. vCenter Server 관리 페이지 접속

2. **Syslog** > **Syslog 설정** 클릭

3. 원격 로그 서버 설정:
   ```
   URL: syslog://192.168.1.10:514
   ```

4. **저장** 후 서비스 재시작

#### KVM

1. `/etc/rsyslog.conf` 파일 수정
   ```bash
   vi /etc/rsyslog.conf
   ```

2. 다음 설정 추가:
   ```
   *.* @@192.168.1.10:514
   ```

3. 방화벽 설정
   ```bash
   firewall-cmd --add-port=514/tcp --permanent
   firewall-cmd --reload
   ```

4. 서비스 재시작
   ```bash
   systemctl restart rsyslog
   ```

#### XenServer

1. `/etc/syslog.conf` 파일 수정
   ```bash
   vi /etc/syslog.conf
   ```

2. 다음 설정 추가:
   ```
   *.* @192.168.1.10:514
   ```

3. syslog 서비스 재시작
   ```bash
   service syslog restart
   ```

#### Nutanix

1. Controller VM 접속

2. 원격 로그 서버 설정:
   ```bash
   ncli rsyslog-config add-server \
       name=logcenter \
       ip-address=192.168.1.10 \
       port=514 \
       network-protocol=tcp \
       relp-enabled=no
   ```

3. 로그 레벨 설정:
   ```bash
   ncli rsyslog-config add-module \
       module-name=syslog_module \
       level=info \
       server-name=logcenter
   ```

### 7. 원격 로그 서버 솔루션

**오픈 소스:**
- **rsyslog**: 가장 널리 사용되는 syslog 서버
- **syslog-ng**: 고급 기능의 syslog 서버
- **Graylog**: 로그 관리 플랫폼
- **ELK Stack**(Elasticsearch, Logstash, Kibana): 로그 분석 플랫폼

**상용 솔루션:**
- **Splunk**: 기업용 로그 분석 플랫폼
- **QRadar**: IBM SIEM 솔루션
- **LogRhythm**: SIEM 플랫폼

**클라우드 기반:**
- **AWS CloudWatch Logs**
- **Azure Monitor Logs**
- **Google Cloud Logging**

### 8. 로그 보관 정책

**로그 보관 기간:**
- 보안 로그: 최소 1년 (권장 3년 이상)
- 감사 로그: 최소 3년 (법적 요구사항)
- 시스템 로그: 최소 6개월

**로그 백업:**
- 일일 자동 백업
- 읽기 전용 저장소
- 지역 간 복제
- WORM(Write Once Read Many) 저장소

### 9. 로그 전송 보안

**1) TLS/SSL 암호화 권장**
```
ssl://syslog.example.com:6514
```

**2) IPsec VPN**
- 로그 서버 간 VPN 터널 구성

**3) 네트워크 분리**
- 관리 네트워크에 로그 서버 배치

### 10. 로그 모니터링

**1) 실시간 모니터링**
- 로그 전송 상태 확인
- 로그 서버 디스크 사용량 모니터링

**2) 알림 설정**
- 로그 전송 실패 시 알림
- 로그 서버 장애 시 알림

**CLI 확인:**

```bash
# ESXi 로그 전송 확인
esxcli system syslog config get

# KVM 로그 전송 확인
logger "test message"
# 로그 서버에서 메시지 확인
```

### 11. 주의사항

- 원격 로그 서버는 **별도의 보안 구성** 필요
- 로그 전송은 **TLS/SSL 암호화** 권장
- 로그 서버 **디스크 용량** 충분히 확보
- 로그 **보관 정책** 수립 필요
- 정기적 **로그 백업** 수행

## 요약

모든 가상화 장비는 **원격 로그 서버와 연동**하여 로그를 중앙 저장해야 합니다. 권장 설정은 **TLS/SSL 암호화된 TCP 전송**이며, 로그는 최소 **1년 이상 보관**해야 합니다. 원격 로그 서버는 침해 사고 조사와 보안 포렌식의 필수 요소입니다.
