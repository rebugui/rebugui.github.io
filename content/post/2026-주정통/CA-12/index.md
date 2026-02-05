---
title: "[2026 주요정보통신기반시설] CA-12 통신구간암호화설정"
slug: "2026-주정통/CA-12"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "클라우드 시스템 간 암호화 통신 여부 점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Cloud
---

# CA-12 통신구간암호화설정

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | CA-12 |
| **점검내용** | 클라우드 시스템 간 암호화 통신 여부 점검 |
| **점검대상** | 클라우드 플랫폼 |
| **판단기준** | 양호: 클라우드 리소스 통신 구간에 암호화가 적용된 경우 |
| **판단기준** | 취약: 클라우드 리소스 통신 구간에 암호화가 적용되지 않은 경우 |
| **조치방법** | 클라우드 리소스 통신하는 주요 구간은 암호화된 통신 수단 설정 |

---
## 상세 설명

### 1. 항목 개요

클라우드 환경에서 데이터는 다양한 통신 구간을 이동합니다. 사용자에서 웹 서버, 웹 서버에서 데이터베이스, 마이크로서비스 간 통신, 외부 API 연동 등 모든 구간에서 암호화되지 않은 통신은 중간자 공격(Man-in-the-Middle Attack), 패킷 스니핑, 데이터 탈취 등의 위협에 노출됩니다.

### 2. 왜 이 항목이 필요한가요?

**보안 위협 시나리오:**
1. **패킷 스니핑**: 공격자가 네트워크 트래픽을 가로채어 민감 데이터 탈취
2. **중간자 공격**: 통신 경로에 개입하여 데이터 변조 및 전송
3. **세션 하이재킹**: 암호화되지 않은 세션 쿠키 탈취
4. **크리덼셜 유출**: 데이터베이스 접속 정보가 평문으로 전송되어 유출

**실제 사례**
- 2018년: 호텔 WiFi 네트워크에서 암호화되지 않은 통신을 스니핑하여 고객 정보 대규모 유출
- 클라우드 환경에서 데이터베이스 연결이 암호화되지 않아 접속 정보 유출

### 3. 점검 대상

- 웹 서버 ↔ 데이터베이스 간 통신
- 마이크로서비스 간 통신
- 로드 밸런서 ↔ 웹 서버 간 통신
- 원격 접속 (SSH, RDP)
- API Gateway ↔ 백엔드 서비스 간 통신
- VPC 간 통신
- 온프레미스 ↔ 클라우드 간 통신

### 4. 판단 기준

| 구분 | 기준 |
|------|------|
| **양호** | 모든 통신 구간에 적절한 암호화가 적용된 경우 |
| **취약** | 하나 이상의 통신 구간에 암호화가 적용되지 않은 경우 |

### 5. 점검 방법

#### Step 1: 웹 서버 HTTPS/TLS 설정 확인

```bash
# 웹 서버 SSL/TLS 인증서 확인
openssl s_client -connect example.com:443 -servername example.com

# SSL Labs 평가
# https://www.ssllabs.com/ssltest/

# TLS 버전 및 암호화 스위트 확인
nmap --script ssl-enum-ciphers -p 443 example.com
```

#### Step 2: 데이터베이스 연결 암호화 확인

```bash
# MySQL - SSL 연결 확인
mysql -h db.example.com -u username -p --ssl --ssl-mode=REQUIRED

# MySQL 서버 SSL 설정 확인
mysql -e "SHOW VARIABLES LIKE '%ssl%';"

# PostgreSQL - SSL 연결 확인
psql "host=db.example.com user=username dbname=mydb sslmode=require"

# PostgreSQL SSL 설정 확인
psql -c "SHOW ssl;"
```

#### Step 3: 로드 밸런서 암호화 설정 확인

```bash
# AWS - ALB/ELB 리스너 확인
aws elbv2 describe-listeners --load-balancer-arn lb-arn

# SSL/TLS 정책 확인
aws elbv2 describe-listeners --load-balancer-arn lb-arn \
  --query "Listeners[?Protocol=='HTTPS'].{Protocol:Protocol,SslPolicy:SslPolicy}"
```

### 6. 조치 방법

#### Step 1: HTTPS/TLS 설정

**Apache HTTP Server:**
```apache
# /etc/httpd/conf.d/ssl.conf
<VirtualHost _default_:443>
    ServerName example.com
    DocumentRoot /var/www/html

    # SSL 엔진 활성화
    SSLEngine on

    # 인증서 경로
    SSLCertificateFile /etc/pki/tls/certs/example.com.crt
    SSLCertificateKeyFile /etc/pki/tls/private/example.com.key
    SSLCertificateChainFile /etc/pki/tls/certs/example.com-chain.crt

    # 보안 강화 (TLS 1.2 이상만 허용)
    SSLProtocol all -SSLv2 -SSLv3 -TLSv1 -TLSv1.1
    SSLCipherSuite HIGH:!aNULL:!MD5

    # HSTS 활성화
    Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
</VirtualHost>
```

**Nginx:**
```nginx
# /etc/nginx/conf.d/ssl.conf
server {
    listen 443 ssl http2;
    server_name example.com;

    # 인증서 경로
    ssl_certificate /etc/nginx/ssl/example.com.crt;
    ssl_certificate_key /etc/nginx/ssl/example.com.key;

    # 보안 강화
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # SSL 세션 캐시
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # HSTS 활성화
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    location / {
        root /var/www/html;
    }
}

# HTTP를 HTTPS로 리디렉션
server {
    listen 80;
    server_name example.com;
    return 301 https://$server_name$request_uri;
}
```

#### Step 2: 데이터베이스 연결 암호화

**MySQL/MariaDB:**
```ini
# /etc/my.cnf.d/server.cnf
[mysqld]
# SSL 활성화
require-secure-transport=ON
ssl-ca=/etc/mysql/ssl/ca-cert.pem
ssl-cert=/etc/mysql/ssl/server-cert.pem
ssl-key=/etc/mysql/ssl/server-key.pem

# 강력한 암호화만 허용
tls-version=TLSv1.2,TLSv1.3
```

```bash
# MySQL 클라이언트 SSL 강제 연결
mysql -h db.example.com -u username -p --ssl-mode=REQUIRED
```

**PostgreSQL:**
```ini
# /var/lib/pgsql/data/postgresql.conf
ssl = on
ssl_cert_file = 'server.crt'
ssl_key_file = 'server.key'
ssl_ca_file = 'ca.crt'
ssl_ciphers = 'HIGH:!aNULL'
ssl_min_protocol_version = 'TLSv1.2'
```

```ini
# /var/lib/pgsql/data/pg_hba.conf
# SSL 연결만 허용
hostssl all all 0.0.0.0/0 md5
```

#### Step 3: 로드 밸런서 HTTPS 설정

```bash
# AWS - ALB HTTPS 리스너 생성
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:region:account-id:loadbalancer/app/mylb/1234567890123456 \
  --protocol HTTPS \
  --port 443 \
  --ssl-policy ELBSecurityPolicy-TLS-1-2-2017-01 \
  --certificates CertificateArn=arn:aws:acm:region:account-id:certificate/certificate-id

# HTTP를 HTTPS로 리디렉션
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:region:account-id:loadbalancer/app/mylb/1234567890123456 \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=redirect,Config="{\"Protocol\":\"HTTPS\",\"Port\":\"443\",\"StatusCode\":\"HTTP_301\"}"
```

#### Step 4: SSH/RDP 암호화

**SSH 강화 설정:**
```bash
# /etc/ssh/sshd_config
# 프로토콜 버전 2만 사용
Protocol 2

# 약한 암호화 알고리즘 제거
Ciphers aes256-gcm@openssh.com,chacha20-poly1305@openssh.com,aes256-ctr
MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com

# 키 교환 알고리즘
KexAlgorithms curve25519-sha256,curve25519-sha256@libssh.org,diffie-hellman-group-exchange-sha256

# 로그인 재시도 제한
MaxAuthTries 3

# 루트 로그인 비활성화
PermitRootLogin no

# 암호 인증 비활성화 (키 기반 인증만)
PasswordAuthentication no
```

**RDP 암호화 강화:**
```powershell
# PowerShell - RDP TLS 1.2 강제
Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp' -Name 'SecurityLayer' -Value 2
Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp' -Name 'UserAuthentication' -Value 1

# RDP 암호화 수준 설정
Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp' -Name 'MinEncryptionLevel' -Value 4
```

#### Step 5: VPC 피어링 암호화

```bash
# AWS - 암호화된 VPC 피어링 연결 생성
aws ec2 create-vpc-peering-connection \
  --vpc-id vpc-aaaaaaaa \
  --peer-vpc-id vpc-bbbbbbbb \
  --peer-region ap-northeast-2

# AWS Transit Gateway를 통한 암호화된 연결
aws ec2 create-transit-gateway \
  --description "Encrypted transit gateway" \
  --options AmazonSideAsn=64512,AutoAcceptSharedAttachments=enable,DefaultRouteTableAssociation=enable,DefaultRouteTablePropagation=enable,VpnEcmpSupport=enable,DnsSupport=enable
```

#### Step 6: VPN 연결 암호화

```bash
# AWS - Site-to-Site VPN 생성 (IPsec IKEv2)
aws ec2 create-vpn-connection \
  --type ipsec.1 \
  --customer-gateway-id cgw-xxxxxxxx \
  --vpn-gateway-id vgw-xxxxxxxx \
  --vpn-connection-options "TunnelOptions=[{TunnelInsideCidr=169.254.1.0/30},{TunnelInsideCidr=169.254.2.0/30}]"

# IKEv2, 강력한 암호화 사용 (기본값)
# Phase 1: IKE SA Encryption: AES256, SHA256, DH Group 14
# Phase 2: IPsec SA Encryption: AES256, SHA256, DH Group 14
```

### 7. 암호화 강도 권고사항

| 구분 | 권고사항 |
|------|---------|
| **블록 암호 알고리즘** | SEED, ARIA, AES (키 길이 128bits 이상) |
| **공개키 암호 알고리즘** | RSA (키 길이 2048bits 이상), ECDSA |
| **해시 알고리즘** | SHA-256 이상 |
| **TLS 버전** | TLS 1.2 이상 (TLS 1.3 권장) |
| **키 교환** | ECDHE, DHE (Perfect Forward Secrecy 제공) |
| **암호화 스위트** | HIGH:!aNULL:!MD5:!3DES |

### 8. 조치 시 주의사항

| 주의사항 | 설명 |
|----------|------|
| **성능 영향** | 암호화는 CPU 사용량 증가, 일반적으로 1-5% 성능 저하 |
| **인증서 관리** | 만료 전 인증서 갱신, ACM 활용 권장 |
| **호환성 확인** | 레거시 클라이언트와의 호환성 확인 필요 |
| **HSTS 주의** | 한 번 활성화하면 되돌리기 어려움, 테스트 후 적용 |
| **모니터링** | SSL/TLS 연결 실패 모니터링 |

### 9. 참고 자료

- **Mozilla SSL Configuration Generator**: https://ssl-config.mozilla.org/
- **OWASP TLS Cheat Sheet**: https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Protection_Cheat_Sheet.html
- **AWS SSL/TLS Best Practices**: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/secure-connections-supported-protocols-ciphers.html

---

## 요약

**통신구간암호화설정**은 클라우드 환경의 모든 네트워크 통신을 보호하는 필수 항목입니다. HTTPS/TLS, 데이터베이스 SSL, VPN, SSH 등 모든 통신 경로에서 암호화를 적용하여 중간자 공격, 패킷 스니핑, 데이터 유출 등의 위협으로부터 데이터를 보호해야 합니다. 최신 TLS 1.2 이상을 사용하고 강력한 암호화 알고리즘을 적용하세요.

**핵심 액션 아이템**
1. 웹 서버 HTTPS/TLS 강제 적용 (HTTP → HTTPS 리디렉션)
2. 데이터베이스 연결 SSL/TLS 활성화
3. 로드 밸런서 HTTPS 리스너 설정
4. SSH/RDP 보안 설정 강화
5. VPN/Transit Gateway를 통한 안전한 VPC 연결
