---
title: "[2026 주요정보통신기반시설] CI-15 파일다운로드(File Download)"
slug: "2026-주정통/CI-15"
date: 2026-02-05T09:56:13+09:00
lastmod: 2026-02-05T09:56:13+09:00
description: "웹사이트에서 허용된 경로 외 다른 경로의 파일 접근 및 다운로드 가능 여부 점검"
categories:
  - 2026 주정통 가이드라인
tags:
  - 2026 주정통 가이드라인
  - Web
---

# 파일다운로드(File Download)

## 가이드라인 원문

| 항목 | 내용 |
|------|------|
| **항목코드** | CI-15 |
| **점검내용** | 웹사이트에서 허용된 경로 외 다른 경로의 파일 접근 및 다운로드 가능 여부 점검 |
| **점검대상** | 웹 애플리케이션 소스코드, 웹 애플리케이션서버, 웹방화벽 |
| **양호기준** | 입력값이 검증되어 허용된 경로와 파일만 접근 가능하고, 경로 조작 및 임의 시스템 파일 다운로드가 불가능하며, 다운로드 디렉터리 외의 접근과 상위 디렉터리 접근이 차단된 경우 |
| **취약기준** | 입력값이 검증없이 처리되어 임의의 경로로 접근이 가능하거나 비인가된 파일을 다운로드할 수 있는 경우 |
| **조치방법** | 다운로드 시 허용된 경로 이외의 디렉터리와 파일에 접근할 수 없도록 구현하고, 서버사이드에서 ../..와 같은 경로이동 관련 문자열에 대해 입력값 검증을 수행하여 비인가된 접근을 차단함 |

---

## 상세 설명

### 1. 판단 기준

#### 기본 판단 기준
- **양호**: 입력값이 검증되어 허용된 경로와 파일만 접근 가능하고, 경로 조작 및 임의 시스템 파일 다운로드가 불가능하며, 다운로드 디렉터리 외의 접근과 상위 디렉터리 접근이 차단된 경우
- **취약**: 입력값이 검증 없이 처리되어 임의의 경로로 접근이 가능하거나 비인가된 파일을 다운로드할 수 있는 경우

#### 경계 케이스 (Edge Case) 처리 방법
- 일반적인 경우 영향 없음
- URL 인코딩, 이중 인코딩, Unicode 인코딩 등 다양한 인코딩 우회 기법 차단 필요

#### 권장 설정값
- 파일명 대신 파일 ID/토큰 사용 권장
- 경로 정규화 후 검증
- 화이트리스트 기반 파일명 검증

### 2. 점검 방법

#### Step 1: 파일 경로 파라미터 확인
```
웹 사이트 내 파일 다운로드 기능 식별 후 파일 다운로드 요청 및 응답 패킷 내 URL 파라미터, POST 데이터, 쿠키 등을 통해 파일 이름 및 경로 노출 여부 확인
```

#### Step 2: 경로 조작 테스트
```
파일 다운로드 시 요청 패킷 내 파일 경로를 상대 경로(../../ 또는 ..\..\)로 변조하여 요청할 경우 정상적으로 해당 경로 내 파일 다운로드 여부 확인
```

#### Step 3: 인코딩 우회 테스트
```
변조한 파일 경로를 인코딩(또는 치환, 종단 문자 추가)을 적용하여 우회 가능 여부 확인
```

### 3. 조치 방법

#### 1. 파일 ID/토큰 사용

```java
// 파일명 대신 ID 사용
@GetMapping("/download/{id}")
public ResponseEntity<Resource> downloadFile(@PathVariable Long id) {
    FileEntity file = fileRepository.findById(id)
        .orElseThrow(() -> new FileNotFoundException());

    // 경로 조정 방지를 위해 ID로만 조회
    Path filePath = Paths.get(file.getStoredPath());
    Resource resource = new UrlResource(filePath.toUri());

    return ResponseEntity.ok()
        .header(HttpHeaders.CONTENT_DISPOSITION,
                "attachment; filename=\"" + file.getOriginalName() + "\"")
        .body(resource);
}
```

#### 2. 특수문자 필터링

**Java 예시:**
```java
public class FileDownloadUtil {
    public static boolean isValidFileName(String fileName) {
        // 영문, 숫자, 일부 특수문자만 허용
        return fileName != null &&
               fileName.matches("^[a-zA-Z0-9._-]+$");
    }

    public static boolean isAllowedExtension(String filePath) {
        String extension = filePath.substring(
            filePath.lastIndexOf(".") + 1
        ).toLowerCase();

        Set<String> allowedExtensions = Set.of("pdf", "jpg", "png");
        return allowedExtensions.contains(extension);
    }
}
```

#### 3. 경로 정규화

**ASP.NET 예시:**
```csharp
public IActionResult Download(string filename) {
    // 파일명 정규화
    string safeName = Path.GetFileName(filename);

    // 지정된 업로드 폴더와 결합
    string uploadsFolder = Path.Combine(_environment.WebRootPath, "uploads");
    string filePath = Path.GetFullPath(Path.Combine(uploadsFolder, safeName));

    // 해당 파일이 업로드 폴더 내 존재하는지 검증
    if (!filePath.StartsWith(uploadsFolder, StringComparison.OrdinalIgnoreCase)) {
        return BadRequest("Invalid file path.");
    }

    byte[] fileBytes = System.IO.File.ReadAllBytes(filePath);
    return File(fileBytes, "application/octet-stream", safeName);
}
```

**PHP 예시:**
```php
// 파일 다운로드 요청 처리
if (isset($_GET['file'])) {
    $file = filter_input(INPUT_GET, 'file', FILTER_SANITIZE_STRING);
    $filePath = realpath('../uploads/' . $file);

    // 파일 경로가 지정된 디렉토리 내에 있는지 확인
    if ($filePath && strpos($filePath, realpath('../uploads/')) === 0) {
        downloadFile($filePath);
    } else {
        echo "잘못된 파일 경로입니다.";
        exit;
    }
}
```

#### 4. 화이트리스트 방식 검증

```java
private final Map<String, String> allowedFiles = Map.of(
    "report1", "/documents/reports/2024/report1.pdf",
    "report2", "/documents/reports/2024/report2.pdf",
    "manual", "/documents/manual.pdf"
);

@GetMapping("/download")
public ResponseEntity<Resource> download(@RequestParam String fileId) {
    String filePath = allowedFiles.get(fileId);

    if (filePath == null) {
        return ResponseEntity.notFound().build();
    }

    Resource resource = new UrlResource("file:" + filePath);
    return ResponseEntity.ok()
        .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + fileId + ".pdf\"")
        .body(resource);
}
```

#### 5. 웹 서버 설정

**Apache 설정:**
```apache
# 상위 디렉터리 접근 차단
<Directory "/var/www/html">
    Options -Indexes
    AllowOverride None
    Require all granted
</Directory>
```

**Nginx 설정:**
```nginx
# 상위 디렉터리 접근 차단
location ~ /\. {
    deny all;
}
```

### 4. 참고 자료

**운영체제별 중요 시스템 파일:**

| OS | 파일 경로 | 설명 |
|----|----------|------|
| Linux | /etc/passwd | 시스템 사용자 계정 리스트 |
| Linux | /etc/shadow | 사용자 비밀번호 해시 |
| Linux | /etc/hosts | 호스트명과 IP 매핑 |
| Linux | /var/log/message | 시스템 로그 |
| Windows | C:\Windows\System32\config\SAM | 사용자 계정 및 암호 해시 |
| Windows | C:\Windows\System32\drivers\etc\hosts | 호스트 파일 |

**우회 기법 대응:**

| 인코딩 방식 | 사용 예시 | 디코딩 결과 |
|------------|----------|-----------|
| URL 인코딩 | %2e%2e%2f | ../ |
| 더블 URL 인코딩 | %252e%252e%252f | ../ |
| 16비트 유니코드 | %u002e | . |
| 역슬래시 | ..\\..\\ | ../ (Windows) |

**검증 체크리스트:**
1. [ ] ../, ..\\ 등 상위 경로 이동 문자열 필터링
2. [ ] 절대 경로 입력 차단
3. [ ] 경로 정규화 후 검증
4. [ ] 파일명 화이트리스트 사용 권장
5. [ ] 다운로드 디렉터리 범위 내에 있는지 확인
6. [ ] URL 인코딩 디코딩 후 검증

### 5. 스크립트
- [취약점 점검 스크립트](https://rebugui.tistory.com/1192)
  - 이 스크립트는 KISA 주요정보통신기반시설 기술적 취약점 분석·평가 가이드라인(2026)을 준수하여 제작된 자동 점검 도구입니다. 복잡한 단일 파일 방식이 아닌 모듈화된 구조로 설계되어 유지보수가 쉽고 확장이 용이합니다.
  - 다양한 환경에서 테스트를 진행했으나, 혹시 점검 로직에 이슈가 발견되거나 개선이 필요한 경우 적극적인 제보를 부탁드립니다.