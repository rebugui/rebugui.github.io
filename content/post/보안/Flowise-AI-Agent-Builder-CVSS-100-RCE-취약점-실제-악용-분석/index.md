---
title: "Flowise AI Agent Builder: CVSS 10.0 RCE 취약점 실제 악용 분석"
date: 2026-04-09T12:27:35+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

```plain text
# Nginx Reverse Proxy 설정으로 접근 제한
server {
    listen 443 ssl;
    server_name flowise.internal.company.com;
    
    # 내부 네트워크에서만 접근 허용
    allow 10.0.0.0/8;
    allow 172.16.0.0/12;
    allow 192.168.0.0/16;
    deny all;
    
    # Basic Auth 추가
    auth_basic "Flowise Admin";
    auth_basic_user_file /etc/nginx/.htpasswd;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Step 3: 환경 변수 보안 강화**

```bash
# .env 파일 보안 설정
FLOWISE_USERNAME=admin
FLOWISE_PASSWORD=$(openssl rand -base64 32)
FLOWISE_SECRET_KEY=$(openssl rand -hex 32)

# 파일 권한 제한
chmod 600 .env
chown flowise:flowise .env
```

**Step 4: 입력 검증 미들웨어 추가**

```javascript
// custom-middleware.js
// Flowise 앞단에 배치하여 악성 패턴 차단

const express = require('express');
const app = express();

const BLOCK_PATTERNS = [
  /\$\{.*\}/,  // Expression language
  /__proto__/,
  /require\s*\(/,
  /eval\s*\(/,
  /exec\s*\(/,
  /child_process/
];

app.use(express.json());

app.use((req, res, next) => {
  const bodyString = JSON.stringify(req.body);
  
  for (const pattern of BLOCK_PATTERNS) {
    if (pattern.test(bodyString)) {
      console.error(`[SECURITY] Blocked malicious request from ${req.ip}`);
      return res.status(400).json({ error: 'Invalid input' });
    }
  }
  next();
});

// Flowise로 프록시
app.use('/', require('http-proxy-middleware').createProxyMiddleware({
  target: 'http://localhost:3000',
  changeOrigin: true
}));

app.listen(8080);
```

### 종합 보안 체크리스트

| 항목 | 상태 | 비고 | | :--- | :--- | :--- | | Flowise 최신 버전 적용 | ☐ | 보안 패치 포함 버전 확인 | | 인터넷 직접 노출 차단 | ☐ | VPN/VPC 내부 배치 | | 인증 활성화 | ☐ | FLOWISE_USERNAME/PASSWORD 설정 | | Rate Limiting 적용 | ☐ | 무차별 대입 공격 방지 | | 로깅 및 모니터링 | ☐ | 비정상 요청 탐지 | | API Key 로테이션 | ☐ | 장앤 경우 즉시 교체 | | 정기 보안 스캔 | ☐ | 월 1회 이상 취약점 점검 |

---

## 침해 사고 대응 절차

이미 공격을 받았다는 의심이 든다면 다음 절차를 따르라:

```javascript
graph TD
    A[침해 의심 탐지] --> B[서버 격리]
    B --> C[메모리 덤프 확보]
    C --> D[로그 백업]
    D --> E[악성 프로세스 종료]
    E --> F[시스템 재구축]
    F --> G[포렌식 분석]
    G --> H[재발 방지 조치]
```

### 즉각적 대응 명령어

```bash
# 1. 네트워크 격리
sudo iptables -A INPUT -j DROP
sudo iptables -A OUTPUT -j DROP

# 2. 실행 중인 의심 프로세스 확인
ps aux | grep -E 'xmrig|minerd|kdevtmpfsi'

# 3. 외부 연결 확인
netstat -tulpn | grep ESTABLISHED

# 4. 메모리 덤프
grep -E '(curl|wget|bash)' /proc/*/comm 2>/dev/null

# 5. 로그 보존
tar -czvf /secure/location/incident_logs.tar.gz /var/log/ ~/.flowise/
```

---

## 결론

Flowise AI Agent Builder의 CVSS 10.0 RCE 취약점은 **AI/ML 인프라 보안의 새로운 시대**를 보여준다. 우리는 LLM, 벡터 데이터베이스, AI Agent 플랫폼들이 가진 강력한 기능만큼이나 강력한 공격 표면에 노출되어 있다.

이 취약점이 특히 위험한 이유:

1. **낮은 진입 장벽** - 공격자가 높은 기술력 없이도 악용 가능 2. **높은 보상** - LLM API Key, 대화 기록, 사용자 데이터 등 가치 있는 자산 3. **광범위한 노출** - 12,000개 이상의 인스턴스가 인터넷에 공개

보안 전문가로서 강조하고 싶은 것은 **AI 도구의 '편의성'이 '안전성'을 압도해서는 안 된다**는 점이다. Flowise와 같은 도구를 사용할 때는 반드시:
- **기본적으로 내부 네트워크에서만 접근 가능하도록 구성**
- **강력한 인증 메커니즘 적용**
- **정기적인 보안 업데이트 및 감사**

---

### 참고 자료
- [

---

**출처**: [https://news.google.com/rss/articles/CBMiggFBVV95cUxOMmV2elZDZ1d0eWFXU2prMHQweUZ4b2tPbEk1cWtFY0ktWHgxcXZ0XzlGdUc4em50UVBDMmtyaC1QMF80UjNjTVpjSVpLckFvUG9xUDloVkFOLWNPcDN5OTA2YkZRVmF1YzlXVG5mdzc5dTR2LUVxRkdKNy1WeWhaV3p3?oc=5](https://news.google.com/rss/articles/CBMiggFBVV95cUxOMmV2elZDZ1d0eWFXU2prMHQweUZ4b2tPbEk1cWtFY0ktWHgxcXZ0XzlGdUc4em50UVBDMmtyaC1QMF80UjNjTVpjSVpLckFvUG9xUDloVkFOLWNPcDN5OTA2YkZRVmF1YzlXVG5mdzc5dTR2LUVxRkdKNy1WeWhaV3p3?oc=5)