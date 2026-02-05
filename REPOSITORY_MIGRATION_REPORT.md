# GitHub Pages 저장소 마이그레이션 보고서

**작성일**: 2026년 2월 5일
**담당자**: Claude (AI Assistant)
**승인자**: openclaw

---

## 1. 개요

### 1.1 마이그레이션 목적

Google AdSense 승인을 위해 GitHub Pages의 Project Site에서 User Site로 전환하여 최상위 도메인 사용

### 1.2 변경 전후 비교

| 항목 | 변경 전 (Project Site) | 변경 후 (User Site) |
|------|----------------------|-------------------|
| **저장소 이름** | `hate-coding-turtle` | `rebugui.github.io` |
| **URL** | `https://rebugui.github.io/hate-coding-turtle/` | `https://rebugui.github.io/` |
| **경로 구조** | `/hate-coding-turtle/2026-주정통/c-01/` | `/2026-주정통/c-01/` |
| **AdSense** | ❌ 미지원 (하위 경로) | ✅ 지원 (최상위 도메인) |
| **포스트 수** | 382개 | 382개 (동일) |
| **테마** | hugo-theme-stack | hugo-theme-stack (동일) |

---

## 2. 마이그레이션 절차

### 2.1 새 저장소 생성

1. **GitHub 저장소 생성**
   - 저장소 이름: `rebugui.github.io`
   - 접근 권한: Public
   - 초기화: README 없이 빈 저장소로 생성

2. **로컬 클론**
   ```bash
   cd /Users/nabang/Documents/OpenClaw
   git clone https://github.com/rebugui/rebugui.github.io.git
   ```

### 2.2 파일 복사

**복사 명령어:**
```bash
rsync -av --exclude='.git' \
  --exclude='public' \
  --exclude='resources' \
  --exclude='node_modules' \
  /Users/nabang/Documents/OpenClaw/security-blog/ \
  /Users/nabang/Documents/OpenClaw/rebugui.github.io/
```

**복사된 파일:**
- 총 927개 파일
- 컨텐츠: 382개 포스트
- 설정: hugo.toml, config/_default/
- 리소스: assets/, static/
- 워크플로우: .github/workflows/deploy.yml

### 2.3 설정 변경

#### 2.3.1 baseURL 업데이트

**파일 1: hugo.toml**
```toml
# 변경 전
baseURL = 'https://rebugui.github.io/hate-coding-turtle/'

# 변경 후
baseURL = 'https://rebugui.github.io/'
```

**파일 2: config/_default/hugo.toml**
```toml
# 변경 전
baseURL = "https://rebugui.github.io/hate-coding-turtle/"

# 변경 후
baseURL = "https://rebugui.github.io/"
```

#### 2.3.2 robots.txt 업데이트

**파일: static/robots.txt**
```txt
# 변경 전
Sitemap: https://rebugui.github.io/hate-coding-turtle/sitemap.xml

# 변경 후
Sitemap: https://rebugui.github.io/sitemap.xml
```

### 2.4 테마 서브모듈 설정

**서브모듈 추가:**
```bash
git submodule add --force \
  https://github.com/rebugui/hugo-theme-stack.git \
  themes/hugo-theme-stack
```

**테마 구성:**
- Hugo Theme Stack v4.0.0-beta.5
- 포크된 저장소: `rebugui/hugo-theme-stack`
- 커스텀 코드 포함:
  - Google Analytics 4 (G-BDJ5ZPHH5Z)
  - Google AdSense (ca-pub-7440869759073353)

### 2.5 AdSense 설정 추가

#### 2.5.1 AdSense 코드

**파일: themes/hugo-theme-stack/layouts/_partials/head/custom.html**
```html
<!-- Google Analytics 4 -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-BDJ5ZPHH5Z"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-BDJ5ZPHH5Z');
</script>

<!-- Google AdSense -->
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-7440869759073353"
     crossorigin="anonymous"></script>
```

#### 2.5.2 ads.txt 파일

**파일: static/ads.txt**
```txt
google.com, pub-7440869759073353, DIRECT, f08c47fec0942fa0
```

### 2.6 Git 커밋 및 푸시

**초기 커밋:**
```bash
git add -A
git commit -m "Initial commit: Migrate from hate-coding-turtle"
git push -u origin main
```

**ads.txt 추가 커밋:**
```bash
git add static/ads.txt
git commit -m "feat: Add ads.txt for AdSense verification"
git push origin main
```

---

## 3. 컨텐츠 구조

### 3.1 포스트 구조

```
content/post/
├── 2026-주정통/
│   ├── C-01/  (제어시스템)
│   ├── D-01/  (데이터베이스)
│   ├── U-01/  (사용자)
│   ├── W-01/  (웹)
│   ├── PC-01/ (PC/윈도우)
│   ├── N-01/  (네트워크)
│   ├── CI-01/ (애플리케이션)
│   ├── WEB-01/ (웹 보안)
│   ├── S-01/  (서버)
│   ├── CA-01/ (클라우드)
│   ├── HV-01/ (가상화)
│   └── M-01/  (이동통신망)
├── examples/
└── security/
```

### 3.2 URL 구조

**변경 전:**
```
https://rebugui.github.io/hate-coding-turtle/2026-주정통/c-01/
```

**변경 후:**
```
https://rebugui.github.io/2026-주정통/c-01/
```

---

## 4. 기술 설정

### 4.1 Hugo 설정

**버전:** Hugo v0.155.2

**주요 설정:**
```toml
baseURL = 'https://rebugui.github.io/'
languageCode = 'ko-kr'
title = '코딩이 싫은 거북이'
theme = 'hugo-theme-stack'

defaultContentLanguage = 'ko'
hasCJKLanguage = true

[permalinks]
    post = '/:slug/'
```

### 4.2 GitHub Actions

**워크플로우:** `.github/workflows/deploy.yml`

**배포 프로세스:**
1. Hugo 빌드 (`hugo --minify`)
2. GitHub Pages에 배포
3. 자동화된 CI/CD

### 4.3 SEO 설정

**robots.txt:**
```txt
User-agent: *
Allow: /

Sitemap: https://rebugui.github.io/sitemap.xml
```

**sitemap.xml:**
- 자동 생성 (Hugo)
- 모든 포스트 URL 포함
- 382개 페이지 인덱싱

---

## 5. AdSense 통합

### 5.1 AdSense 계정 정보

- **Publisher ID:** `ca-pub-7440869759073353`
- **사이트 URL:** `https://rebugui.github.io/`
- **상태:** 검토 대기 중

### 5.2 검증 방법

Google은 다음 방법으로 사이트 소유권을 확인:
1. ✅ AdSense 코드 스니펫 (`<head>` 태그)
2. ✅ ads.txt 파일

### 5.3 승인 요구사항

- ✅ 충분한 콘텐츠 (382개 포스트)
- ✅ 정기적인 업데이트
- ✅ 원저작 콘텐츠
- ✅ 명확한 네비게이션
- ✅ 이용약관/개인정보처리방침 (필요 시 추가)

---

## 6. 이전 저장소 처리

### 6.1 hate-coding-turtle 저장소

**상태:** 백업용으로 유지

**URL:** https://rebugui.github.io/hate-coding-turtle/

**용도:**
- 백업 보관
- 롤백 옵션
- 참고용

### 6.2 데이터 동기화

**권장 작업流程:**
1. `rebugui.github.io`를 주 저장소로 사용
2. 새 포스트는 `rebugui.github.io`에 추가
3. 필요시 `hate-coding-turtle`에도 복사 (백업)

---

## 7. 확인 사항

### 7.1 배포 확인

**GitHub Actions:**
- URL: https://github.com/rebugui/rebugui.github.io/actions
- 상태: ✅ 성공

**사이트 접근:**
- 메인: https://rebugui.github.io/
- 예시 포스트: https://rebugui.github.io/2026-주정통/c-01/

### 7.2 코드 확인

**AdSense 코드:**
```bash
curl -s "https://rebugui.github.io/" | grep "pagead2.googlesyndication.com"
```
결과: ✅ 확인됨

**ads.txt:**
```bash
curl -s "https://rebugui.github.io/ads.txt"
```
결과: ✅ 확인됨

---

## 8. 향후 작업

### 8.1 AdSense 승인 대기

- 예상 기간: 2-3일
- 확인 방법: AdSense 대시보드

### 8.2 추가 페이지 작성 (선택)

AdSense 승인을 위해 필요할 수 있는 페이지:
- 개인정보처리방침
- 이용약관
- 문의하기 페이지

### 8.3 모니터링

정기적으로 확인할 항목:
- [ ] AdSense 승인 상태
- [ ] Google Search Console 인덱싱
- [ ] 사이트 속도 및 성능
- [ ] 모바일 최적화

---

## 9. 롤백 절차

문제 발생 시 이전 저장소로 복구:

### 9.1 DNS 롤백

필요 없음 (GitHub Pages 자동 관리)

### 9.2 콘텐츠 복구

```bash
# 이전 저장소에서 복사
rsync -av /Users/nabang/Documents/OpenClaw/security-blog/content/ \
  /Users/nabang/Documents/OpenClaw/rebugui.github.io/content/
```

### 9.3 설정 복구

```bash
# baseURL 되돌리기
baseURL = 'https://rebugui.github.io/hate-coding-turtle/'
```

---

## 10. 결론

### 10.1 성공 요인

✅ 모든 콘텐츠 성공적으로 마이그레이션
✅ URL 구조 개선 (간결해짐)
✅ AdSense 요구사항 충족
✅ SEO 설정 완료
✅ 자동화된 배포 프로세스 유지

### 10.2 기대 효과

1. **AdSense 승인**: 최상위 도메인 사용으로 승인 가능
2. **URL 간소화**: `/hate-coding-turtle/` 경로 제거
3. **SEO 개선**: 깔끔한 URL 구조
4. **관리 용이성**: User Site 표준 준수

### 10.3 다음 단계

1. AdSense 검토 완료 대기 (2-3일)
2. Google Search Console에 새 사이트 등록
3. 필요시 추가 페이지 작성 (개인정보처리방침 등)
4. 정기적인 콘텐츠 업데이트

---

## 11. 참고 자료

### 11.1 관련 링크

- GitHub Pages 문서: https://docs.github.com/en/pages
- Hugo 문서: https://gohugo.io/
- AdSense 정책: https://support.google.com/adsense/

### 11.2 주요 파일 위치

- 설정: `hugo.toml`, `config/_default/hugo.toml`
- 콘텐츠: `content/post/`
- 테마: `themes/hugo-theme-stack/`
- 정적 파일: `static/`
- 워크플로우: `.github/workflows/deploy.yml`

---

**보고서 종결**

**승인자:** openclaw
**작성자:** Claude (AI Assistant)
**날짜:** 2026년 2월 5일
