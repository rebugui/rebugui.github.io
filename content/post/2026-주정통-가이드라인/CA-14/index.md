---
title: "[2026 주요정보통신기반시설] CA-14 인스턴스로깅설정"
slug: "2026-주정통/CA-14"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "인스턴스 로깅 설정 여부 점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Cloud
draft: true
---

# CA-14 인스턴스로깅설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | CA-14 |
| **점검내용** | 인스턴스 로깅 설정 여부 점검 |
| **점검대상** | 클라우드 플랫폼 |
| **판단기준** | 양호: 인스턴스 로깅 설정이 기관 정책에 따라 설정된 경우 |
| **판단기준** | 취약: 인스턴스 로깅 설정이 기관 정책에 따라 설정되지 않은 경우 |
| **조치방법** | 인스턴스 로깅 설정 |

---
## 상세 설명

### 1. 항목 개요

클라우드 인스턴스(EC2, VM, GCE 등) 내부에서 발생하는 시스템 로그, 애플리케이션 로그, 보안 로그를 수집하고 중앙에서 관리하는 것은 보안 모니터링과 운영 효율성에 필수적입니다. 인스턴스 로깅을 통해 비정상적인 로그인 시도, 프로세스 실행, 리소스 사용 등을 모니터링할 수 있습니다.

### 2. 왜 이 항목이 필요한가요?

**보안 위협 시나리오:**
1. **비인가 접속 탐지**: 실패한 SSH 로그인 시도, 비정상 IP에서의 접속
2. **악성 프로세스 탐지**: 의심스러운 프로세스 실행, 파일 변조
3. **시스템 이상 징후**: CPU/메모리 과다 사용, 디스크 공간 부족
4. **사고 조사**: 침해사고 발생 시 공격자의 활동 내역 분석

**실제 사례**
- 암호화폐화 채굴 악성코드가 인스턴스에서 실행되었는데 로그가 없어 탐지 지연
- SSH 무차별 대입 공격이 30일간 지속되었는데 로그 분석을 못해 탐지 실패

### 3. 점검 대상

- 모든 클라우드 인스턴스 (EC2, Azure VM, GCE 등)
- 시스템 로그 (/var/log, /var/adm 등)
- 애플리케이션 로그 (Apache, Nginx, Tomcat 등)
- 보안 로그 (auth.log, secure 등)
- 감사 로그 (auditd)

### 4. 판단 기준

| 구분 | 기준 |
|------|------|
| **양호** | 인스턴스 로깅이 기관 정책(로그 수집 주기, 보관 기간 등)에 따라 설정된 경우 |
| **취약** | 인스턴스 로깅이 비활성화되거나 기관 정책에 맞지 않게 설정된 경우 |

### 5. 점검 방법

#### Step 1: 로그 데몬 동작 확인

```bash
# Linux - rsyslog 동작 확인
systemctl status rsyslog
ps aux | grep rsyslog

# 로그 파일 확인
ls -lh /var/log/
tail -f /var/log/syslog
tail -f /var/log/auth.log

# systemd journal 확인
journalctl --since "1 hour ago"
```

```bash
# Windows - 이벤트 로그 서비스 확인
Get-Service | Where-Object {$_.Name -like "*event*"}
Get-WinEvent -ListLog Application, System, Security
```

#### Step 2: CloudWatch Logs Agent 설치 확인

```bash
# AWS - CloudWatch Agent 설치 확인
# Amazon Linux 2
rpm -q amazon-cloudwatch-agent

# Ubuntu
dpkg -l | grep amazon-cloudwatch-agent

# CloudWatch Agent 상태 확인
systemctl status amazon-cloudwatch-agent

# CloudWatch Agent 설정 확인
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config
```

### 6. 조치 방법

#### Step 1: AWS CloudWatch Agent 설치 및 설정

```bash
# Amazon Linux 2
sudo yum install -y amazon-cloudwatch-agent

# Ubuntu/Debian
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i -E ./amazon-cloudwatch-agent.deb

# CloudWatch Agent 설정 마법사 실행
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard
```

```json
// /opt/aws/amazon-cloudwatch-agent/etc/config.json
{
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/log/syslog",
            "log_group_name": "EC2Syslog",
            "log_stream_name": "{instance_id}"
          },
          {
            "file_path": "/var/log/auth.log",
            "log_group_name": "EC2AuthLog",
            "log_stream_name": "{instance_id}"
          },
          {
            "file_path": "/var/log/nginx/access.log",
            "log_group_name": "WebAccessLog",
            "log_stream_name": "{instance_id}"
          },
          {
            "file_path": "/var/log/nginx/error.log",
            "log_group_name": "WebErrorLog",
            "log_stream_name": "{instance_id}"
          }
        ]
      }
    }
  },
  "metrics": {
    "metrics_collected": {
      "cpu": {
        "measurement": ["cpu_usage_active", "cpu_usage_idle"],
        "metrics_collection_interval": 60
      },
      "disk": {
        "measurement": ["disk_used_percent"],
        "metrics_collection_interval": 60
      },
      "mem": {
        "measurement": ["mem_used_percent"],
        "metrics_collection_interval": 60
      }
    }
  }
}
```

```bash
# CloudWatch Agent 시작
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -m ec2 -a start
```

#### Step 2: SSH 로그인 감시

```bash
# /etc/rsyslog.d/ssh.conf 추가
if $programname == 'sshd' then /var/log/sshd.log
& stop

# rsyslog 재시작
systemctl restart rsyslog

# 로그 로테이트 설정
cat > /etc/logrotate.d/ssh <<EOF
/var/log/sshd.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    copytruncate
}
EOF
```

```bash
# fail2ban 설치 (SSH 무차별 대입 공격 방지)
sudo apt-get install fail2ban

# /etc/fail2ban/jail.local
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3

# fail2ban 시작
systemctl enable fail2ban
systemctl start fail2ban
```

#### Step 3: auditd를 통한 시스템 감사

```bash
# auditd 설치
sudo apt-get install auditd

# 감사 규칙 추가
# /etc/audit/rules.d/audit.rules

# 시스템 호출 감시
-a always,exit -F arch=b64 -S execve -F auid>=1000 -F auid!=4294967295 -k exec

# 파일 접근 감시
-w /etc/passwd -p wa -k identity
-w /etc/shadow -p wa -k identity
-w /etc/sudoers -p wa -k sudoers

# 관리 명령 감시
-a always,exit -F arch=b64 -S mount -F auid>=1000 -F auid!=4294967295 -k mount
-a always,exit -F arch=b64 -S umount2 -F auid>=1000 -F auid!=4294967295 -k mount

# auditd 재시작
systemctl restart auditd

# 감사 로그 확인
ausearch -k exec
aureport --tty
```

#### Step 4: Azure VM Diagnostic Extensions

```bash
# Azure CLI - 진단 확장 설치
az vm extension set \
  --resource-group myResourceGroup \
  --vm-name myVM \
  --name IaaSDiagnostics \
  --publisher Microsoft.Azure.Diagnostics \
  --version 1.* \
  --protected-settings '{
    "storageAccountName": "mystorageaccount",
    "storageAccountKey": "storageKey",
    "storageAccountEndPoint": "https://core.windows.net"
  }' \
  --settings '{
    "EventSource": {
      "SystemEvents": ["System"]
    },
    "LinuxEvents": {
      "SyslogEvents": ["Syslog"]
    }
  }'
```

#### Step 5: GCP Logging Agent

```bash
# Google Ops Agent 설치 (Cloud Logging + Monitoring)
curl -sSO https://dl.google.com/cloudagents/add-google-cloud-ops-agent-repo.sh
sudo bash add-google-cloud-ops-agent-repo.sh --also-install

# 설정 파일
cat > /etc/google-cloud-ops-agent/config.yaml <<EOF
logging:
  logs:
  - name: syslog
    path: /var/log/syslog
  - name: apache-access
    path: /var/log/apache2/access.log
  - name: apache-error
    path: /var/log/apache2/error.log

metrics:
  service:
    endpoints:
  - host: localhost
    port: 9090
EOF

# 에이전트 재시작
systemctl restart google-cloud-ops-agent
```

### 7. 로그 보관 및 정책 설정

```bash
# 로그 보관 기간 설정 (CloudWatch Logs)
aws logs put-retention-policy \
  --log-group-name EC2Syslog \
  --retention-in-days 90

# 로그 내보내기 (S3로 아카이브)
aws logs create-export-task \
  --log-group-name EC2Syslog \
  --from 1698796800000 \
  --to 1698883200000 \
  --destination bucket-name \
  --destination-prefix logs/
```

### 8. 조치 시 주의사항

| 주의사항 | 설명 |
|----------|------|
| **스토리지 용량** | 로그가 디스크를 가득 채우지 않도록 로테이트 설정 |
| **개인정보 보호** | 로그에 민감 정보가 포함되지 않도록 주의 |
| **로그 암호화** | 로그 전송 시 TLS 사용, 저장 시 암호화 |
| **성능 영향** | 과도한 로깅은 시스템 성능 저하 |
| **비용 관리** | CloudWatch Logs 비용 최적화 |

### 9. 참고 자료

- **AWS CloudWatch Logs Documentation**: https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/
- **Linux auditd Documentation**: https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/
- **fail2ban Documentation**: https://fail2ban.readthedocs.io/

---

## 요약

**인스턴스로깅설정**은 클라우드 인스턴스 내부에서 발생하는 모든 활동을 기록하고 모니터링하는 핵심 항목입니다. CloudWatch Agent, Azure Monitor, GCP Logging Agent 등을 활용하여 시스템 로그, 애플리케이션 로그, 보안 로그를 중앙에서 수집하고 분석하세요. fail2ban, auditd 등을 활용하여 실시간으로 보안 위협을 탐지하고 대응할 수 있어야 합니다.

**핵심 액션 아이템**
1. CloudWatch/Ops Agent 설치 및 로그 수집 설정
2. 시스템 로그(auth.log, syslog) 중앙 집중화
3. SSH 무차별 대입 공격 탐지 (fail2ban)
4. auditd를 통한 시스템 감사
5. 로그 보관 기간 설정 및 정기적 검토
