---
title: "[2026 주요정보통신기반시설] CI-14 악성파일업로드(Malicious File Upload)"
slug: "2026-주정통/CI-14"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "웹애플리케이션내 업로드기능 이용시 악성 파일의 업로드 및 실행 가능 여부 점검"
categories: ["2026 주정통 가이드라인"]
tags:
  - 2026 주정통 가이드라인
  - Web
draft: true
---

# 악성파일업로드(Malicious File Upload)

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | CI-14 |
| **점검내용** | 웹애플리케이션내 업로드기능 이용시 악성 파일의 업로드 및 실행 가능 여부 점검 |
| **점검대상** | 웹 애플리케이션 소스코드, 웹 애플리케이션서버, 웹방화벽 |
| **양호기준** | 업로드되는 파일에 대한 확장자 검증이 이루어지는 경우 |
| **취약기준** | 업로드되는 파일에 대한 확장자 검증이 이루어지지 않고 업로드 경로 접근 시 정상적으로 실행이 가능한 경우 |
| **조치방법** | 업로드되는 파일에 대한 확장자 검증 및 실행권한 제거 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 업로드되는 파일에 대해 확장자 검증이 이루어지는 경우
- **취약**: 업로드되는 파일에 대해 확장자 검증이 이루어지지 않고 업로드 경로 접근 시 정상적으로 실행이 가능한 경우

#### 경계 케이스 (Edge Case) 처리 방법
- 일반적인 경우 영향 없음
- Content-Type 헤더는 사용자가 조작 가능하므로 신뢰하면 안 됨
- 파일 확장자만으로는 부족하며 파일 내용(Magic Bytes)도 확인 필요

#### 권장 설정값
- 화이트리스트 기반 확장자 검증
- 파일명 난수화 (UUID 사용)
- 웹 루트 외부 저장
- 파일 크기 제한 (10MB 권장)

### 2. 점검 방법

#### Step 1: 파일 확장자 검증 확인
```
파일 업로드 기능 이용 시 파일 확장자(.exe, .bat, .sh, .dll 등) 검증 여부 확인
```

#### Step 2: 악성 파일 업로드 시도
```
임의 악성 파일에 대하여 정상적으로 업로드 가능 여부 확인
```

#### Step 3: 업로드된 파일 실행 테스트
```
업로드된 파일 경로 접근 시 파일이 정상적으로 실행되는지 확인
```

### 3. 조치 방법

#### 1. 파일명 정규화 및 검증

**Java 예시:**
```java
private static final String[] ALLOWED_EXTENSIONS =
    {"jpg", "png", "pdf", "txt"};

// 파일명 정규화
private static String normalizeFilename(String filename) {
    if (filename == null) return null;

    String name = URLDecoder.decode(filename, StandardCharsets.UTF_8);
    name = Normalizer.normalize(name, Normalizer.Form.NFC);
    name = name.replace("\0", "");  // NULL 바이트 제거
    name = name.replaceAll("[<>:\"/\\\\|?*]", "");
    name = name.replaceAll("^[.\\s]+|[.\\s]+$", "");

    return name;
}

// 확장자 추출 및 이중 확장자 차단
private static String getExtension(String filename) {
    String safe = normalizeFilename(filename);
    int dotCount = safe.length() - safe.replace(".", "").length();

    // 이중 확장자 차단
    if (dotCount != 1) return "";

    int idx = safe.lastIndexOf('.');
    if (idx == -1) return "";

    return safe.substring(idx + 1).toLowerCase();
}
```

#### 2. MIME 타입 검증

```java
private static final Set<String> ALLOWED_MIME = Set.of(
    "image/jpeg",
    "image/png",
    "application/pdf",
    "text/plain"
);

// Apache Tika를 이용한 MIME 타입 검증
Tika tika = new Tika();
String mime = tika.detect(file.getInputStream());

if (!ALLOWED_MIME.contains(mime)) {
    throw new IOException("허용되지 않은 파일 유형");
}
```

#### 3. 파일명 난수화

```java
public String saveFile(MultipartFile file, String uploadDir) throws IOException {
    String original = file.getOriginalFilename();
    String ext = getExtension(original);

    if (!ALLOWED_EXTENSIONS.contains(ext)) {
        throw new IOException("허용되지 않은 확장자");
    }

    // 파일명 난수화 (UUID 사용)
    String newName = UUID.randomUUID().toString().replace("-", "") + "." + ext;

    // 저장 경로 (웹 루트 외부 권장)
    Path savePath = Paths.get(uploadDir, newName);
    file.transferTo(savePath.toFile());

    return newName;
}
```

#### 4. 파일 크기 제한

```java
// Spring Boot 설정
spring.servlet.multipart.max-file-size=10MB
spring.servlet.multipart.max-request-size=10MB

// 또는 코드에서 검증
if (file.getSize() > 10 * 1024 * 1024) {
    throw new IOException("파일 크기 초과 (최대 10MB)");
}
```

#### 5. 업로드 디렉터리 보안

```java
// 웹 루트 외부에 저장 권장
String uploadDir = "/var/uploads/files";

// 업로드된 파일의 실행 권한 제거
Path uploadedFile = Paths.get(uploadDir, filename);
Files.setPosixFilePermissions(uploadedFile,
    PosixFilePermissions.fromString("rw-r-----"));
```

#### 6. 웹 서버 설정

**Apache 설정:**
```apache
# 업로드 디렉터리에서 PHP 실행 비활성화
<Directory "/var/www/html/uploads">
    php_flag engine off
    <FilesMatch "\.php$">
        Order Allow,Deny
        Deny from all
    </FilesMatch>
</Directory>
```

**Nginx 설정:**
```nginx
location /uploads/ {
    # PHP 실행 비활성화
    location ~ \.php$ {
        deny all;
    }
}
```

### 4. 참고 자료

**차단해야 할 파일 확장자:**

**실행 파일:**
- `.exe`, `.dll`, `.bat`, `.cmd`, `.msi`
- `.sh`, `.bash`, `.ksh`
- `.app`, `.deb`, `.rpm`

**스크립트 파일:**
- `.php`, `.phtml`, `.php3`, `.php4`, `.php5`
- `.jsp`, `.jspx`, `.jsw`
- `.asp`, `.aspx`, `.asa`
- `.pl`, `.py`, `.rb`

**기타 위험 파일:**
- `.htaccess`, `.htpasswd`
- `.ini`, `.conf`, `.config`
- `.jar`, `.war`, `.ear`

**허용할 수 있는 확장자 예시:**
- 이미지: `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`
- 문서: `.pdf`, `.docx`, `.xlsx`, `.pptx`
- 텍스트: `.txt`, `.csv`, `.md`

**우회 기법 대응:**
- 이중 확장자: `image.php.jpg` 차단
- NULL 바이트: `shell.php%00.jpg` 제거
- URL 인코딩: 디코딩 후 검증

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.