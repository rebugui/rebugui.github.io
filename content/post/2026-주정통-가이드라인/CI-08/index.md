---
title: "[2026 주요정보통신기반시설] CI-08 서버사이드요청위조(Server-Side Request Forgery, SSRF)"
slug: "2026-주정통/CI-08"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "입력값을 통해 외부에서 직접적인 접근이 제한된 내부 서버 자원에 접근하여 악의적인 요청을 처리하거나 중요정보의 유출 여부 점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Web
---

# 서버사이드요청위조(Server-Side Request Forgery, SSRF)

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | CI-08 |
| **점검내용** | 입력값을 통해 외부에서 직접적인 접근이 제한된 내부 서버 자원에 접근하여 악의적인 요청을 처리하거나 중요정보의 유출 여부 점검 |
| **점검대상** | 웹 애플리케이션 소스코드, 웹 애플리케이션서버, 웹방화벽, API서버 |
| **양호기준** | 외부 입력값이 화이트리스트 방식으로 검증되어, 허용된 URL 또는 IP 범위내에서만 처리될 경우 |
| **취약기준** | 외부 입력값이 검증이 이루어지지 않고 처리되어 허용되지 않는 자원에 임의적인 접근 및 요청이 가능한 경우 |
| **조치방법** | 입력값 검증 및 화이트리스트를 적용하여 허용된 URL과 IP주소만 접근 가능하도록 설정하며, 네트워크를 분리하여 내부자원에 대한 비인가 접근을 차단 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 외부 입력값이 화이트리스트 방식으로 검증되어, 허용된 URL 또는 IP 범위 내에서만 처리될 경우
- **취약**: 외부 입력값이 검증이 이루어지지 않고 처리되어 허용되지 않는 자원에 임의적인 접근 및 요청이 가능한 경우

#### 경계 케이스 (Edge Case) 처리 방법
- 일반적인 경우 영향 없음
- URL 필터링 시 비즈니스 로직에 필요한 모든 URL을 화이트리스트에 등록
- 내부 서비스 간 통신에도 동일한 검증 적용

#### 권장 설정값
- HTTP와 HTTPS 스키마만 허용
- 사설 IP 대역 차단: 192.168.x.x, 10.x.x.x, 172.16-31.x.x
- localhost, 127.0.0.1 차단
- 클라우드 메타데이터 IP 차단: 169.254.169.254 (AWS), metadata.google.internal (GCP)

### 2. 점검 방법

#### Step 1: 내부 서버 접근 테스트
```
사용자 입력을 통해 서버 간 통신이 이루어지는 지점에서 허용되지 않은 주소값을 입력하여 응답, 지연 시간 등을 분석해 취약점 가능성 확인
```

**테스트 패턴:**
```
http://localhost/admin
http://127.0.0.1:8080
http://192.168.1.1
http://169.254.169.254/latest/meta-data/  // AWS
http://metadata.google.internal  // GCP
```

#### Step 2: 우회 기법 테스트
```
습득한 정보를 바탕으로 우회 기법, 포트 스캔, 내부 정보 탈취 등 익스플로잇 시도 및 영향 평가
```

### 3. 조치 방법

#### 1. 화이트리스트 방식 URL 검증

**Java 예시:**
```java
public boolean isUrlAllowed(String urlString) {
    try {
        URL url = new URL(urlString);
        String protocol = url.getProtocol();

        // HTTP와 HTTPS 스키마만 허용
        if (!("http".equalsIgnoreCase(protocol) || "https".equalsIgnoreCase(protocol))) {
            return false;
        }

        String host = url.getHost();
        int port = url.getPort() == -1 ? url.getDefaultPort() : url.getPort();

        // 화이트리스트 확인
        return allowedDomains.contains(host) ||
               (allowedIPsAndPorts.containsKey(host) &&
                allowedIPsAndPorts.get(host).contains(port));
    } catch (Exception e) {
        return false;
    }
}
```

#### 2. 내부 네트워크 대역 차단

```java
// 사설 IP 대역 차단
private boolean isPrivateIP(String ip) {
    return ip.startsWith("192.168.") ||
           ip.startsWith("10.") ||
           ip.startsWith("172.16.") ||
           ip.equals("127.0.0.1") ||
           ip.equals("localhost") ||
           ip.startsWith("169.254.");  // 링크 로컬
}

// AWS/GCP 메타데이터 IP 차단
private boolean isMetadataEndpoint(String host) {
    return host.equals("169.254.169.254") ||  // AWS
           host.equals("metadata.google.internal");  // GCP
}
```

#### 3. 프로토콜 제한

**차단해야 할 프로토콜:**
- `file://` - 로컬 파일 접근
- `ftp://` - FTP 파일 전송
- `gopher://` - 임의 데이터 전송
- `dict://` - 사전 프로토콜
- `http://` 내부 IP - 내부 네트워크 접근

#### 4. PHP 설정

**php.ini 설정:**
```ini
allow_url_fopen=Off      ; 원격 URL 파일 접근 비활성화
allow_url_include=Off    ; 원격 URL include 비활성화
```

#### 5. 네트워크 분리

- 웹 서버와 데이터베이스 서버를 별도 네트워크에 배치
- DMZ 구성으로 인터넷과 내부망 분리
- 방화벽 규칙으로 서버 간 통신 제한

### 4. 참고 자료

**클라우드 메타데이터 엔드포인트:**

| 클라우드 | 메타데이터 URL |
|----------|----------------|
| AWS | http://169.254.169.254/latest/meta-data/ |
| GCP | http://metadata.google.internal/computeMetadata/v1/ |
| Azure | http://169.254.169.254/metadata/instance?api-version=2021-02-01 |
| DigitalOcean | http://169.254.169.254/metadata/v1/ |

**OWASP SSRF Prevention Cheat Sheet:**
1. URL 입력값 화이트리스트 검증
2. 내부 네트워크 대역 차단
3. 프로토콜 제한 (HTTP/HTTPS만 허용)
4. 네트워크 분리
5. DNS 리바인딩 방지

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.