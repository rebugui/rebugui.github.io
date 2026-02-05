# 📘 "코딩이 싫은 거북이" 블로그 운영 가이드

> 작성일: 2026-02-04
> 버전: 1.0
> 운영자: openclaw

---

## 📋 목차

1. [프로젝트 개요](#1-프로젝트-개요)
2. [시스템 요구사항](#2-시스템-요구사항)
3. [디렉토리 구조](#3-디렉토리-구조)
4. [로컬 개발 환경 설정](#4-로컬-개발-환경-설정)
5. [페이지 관리](#5-페이지-관리)
6. [카테고리 관리](#6-카테고리-관리)
7. [태그 관리](#7-태그-관리)
8. [이미지 관리](#8-이미지-관리)
9. [메뉴 관리](#9-메뉴-관리)
10. [설정 변경](#10-설정-변경)
11. [배포 방법](#11-배포-방법)
12. [자주 하는 작업](#12-자주-하는-작업)
13. [트러블슈팅](#13-트러블슈팅)
14. [참고 자료](#14-참고-자료)

---

## 1. 프로젝트 개요

### 1.1 기본 정보

| 항목 | 내용 |
|------|------|
| **블로그 이름** | 코딩이 싫은 거북이 |
| **URL** | https://rebugui.github.io/hate-coding-turtle/ |
| **GitHub 저장소** | https://github.com/rebugui/hate-coding-turtle |
| **플랫폼** | Hugo Static Site Generator |
| **테마** | hugo-theme-stack v4.0.0-beta.5 |
| **언어** | 한국어 (ko-kr) |
| **배포** | GitHub Pages (자동) |

### 1.2 주요 특징

- ✅ 정적 사이트 generator (Hugo)
- ✅ GitHub Pages 자동 배포
- ✅ 다크/라이트 모드 지원
- ✅ 반응형 디자인
- ✅ 검색 기능 내장
- ✅ 이미지 갤러리 지원
- ✅ 코드 하이라이팅

---

## 2. 시스템 요구사항

### 2.1 필수 소프트웨어

```bash
# Hugo 설치 확인
hugo version

# Git 설치 확인
git --version
```

### 2.2 추천 개발 도구

- **에디터**: VS Code, Neovim, 또는 선호하는 텍스트 에디터
- **터미널**: macOS Terminal, iTerm2, etc.

---

## 3. 디렉토리 구조

```
security-blog/
├── .github/
│   └── workflows/
│       └── deploy.yml          # GitHub Actions 배포 설정
├── config/_default/            # Hugo 설정 파일들
│   ├── hugo.toml              # 메인 설정
│   ├── languages.toml         # 언어 설정
│   ├── markup.toml            # 마크업 설정
│   ├── menu.toml              # 소셜 메뉴
│   ├── params.toml            # 테마 파라미터
│   └── related.toml           # 관련 글 설정
├── content/                    # 모든 콘텐츠
│   ├── _index.md              # 홈페이지
│   ├── page/                  # 정적 페이지
│   │   ├── about/            # 소개 페이지
│   │   ├── archives/         # 아카이브
│   │   ├── links/            # 링크 모음
│   │   └── search/           # 검색 페이지
│   ├── post/                  # 블로그 글 (← 새 글은 여기 추가)
│   └── categories/            # 카테고리 페이지
├── static/                     # 정적 파일
│   └── img/
│       └── avatar.png         # 아바타/파비콘
├── hugo.toml                  # 루트 설정 파일
└── themes/                    # 테마 (submodule)
    └── hugo-theme-stack/
```

---

## 4. 로컬 개발 환경 설정

### 4.1 저장소 클론

```bash
# 저장소 클론
git clone https://github.com/rebugui/hate-coding-turtle.git
cd hate-coding-turtle

# 서브모듈 초기화 (테마)
git submodule update --init --recursive
```

### 4.2 로컬 서버 실행

```bash
# 기본 실행 (http://localhost:1313)
hugo server

# 변경사항 자동 반영
hugo server --disableFastRender

# draft 글도 보기
hugo server --buildDrafts
```

### 4.3 빌드 테스트

```bash
# production 빌드 테스트
hugo --minify

# 결과물은 public/ 폴더에 생성
```

---

## 5. 페이지 관리

### 5.1 새 블로그 글 작성

#### 방법 1: Hugo 명령어 사용

```bash
# 새 글 생성
hugo new post/글제목/index.md

# 예시
hugo new post/hugo-블로그-시작하기/index.md
```

#### 방법 2: 수동으로 파일 생성

```
content/post/글제목/index.md
```

### 5.2 글 작성 형식 (Front Matter)

```yaml
---
title: "글 제목"
date: 2026-02-04
lastmod: 2026-02-04
description: "글 요약 설명"
tags:
  - 태그1
  - 태그2
  - 태그3
categories:
  - 카테고리명
---

# 글 내용 시작

여기에 본문을 작성합니다...
```

### 5.3 글 수정

```bash
# 1. 수정할 파일 찾기
ls content/post/

# 2. 에디터로 열어서 수정
code content/post/글제목/index.md

# 3. 로컬에서 확인
hugo server

# 4. 커밋
git add content/post/글제목/index.md
git commit -m "feat: 블로그 글 수정"
git push origin main
```

### 5.4 글 삭제

```bash
# 1. 파일 삭제
rm -rf content/post/글제목/

# 2. 커밋
git add content/post/
git commit -m "delete: 블로그 글 삭제"
git push origin main
```

### 5.5 임시 저장 (Draft)

```yaml
---
title: "아직 공개하지 않을 글"
date: 2026-02-04
draft: true  # ← draft: true 설정
---
```

```bash
# draft 글 보면서 작업하기
hugo server --buildDrafts
```

---

## 6. 카테고리 관리

### 6.1 카테고리 생성

카테고리는 **자동**으로 생성됩니다. 글의 Front Matter에 `categories`를 추가하기만 하면 됩니다.

```yaml
---
categories:
  - 보안
  - CTF
---
```

### 6.2 카테고리 페이지 커스텀 (선택)

```
content/categories/카테고리명/_index.md
```

```yaml
---
title: "카테고리명"
description: "이 카테고리에 대한 설명"
---
```

### 6.3 카테고리 이름 변경

```bash
# 1. 해당 카테고리를 사용하는 모든 글 찾기
grep -r "categories:" content/post/ | grep "옛이름"

# 2. 각 글의 카테고리 이름 수정

# 3. 기존 카테고리 폴더 삭제 (선택)
rm -rf content/categories/옛이름/
```

---

## 7. 태그 관리

### 7.1 태그 추가

```yaml
---
tags:
  - 웹 해킹
  - XSS
  - CVE-2024-xxxx
---
```

### 7.2 태그 사용 현황 확인

```bash
# 모든 태그 찾기
grep -rh "tags:" content/post/ -A 10
```

### 7.3 태그 수정

```bash
# 1. 특정 태그를 사용하는 글 찾기
grep -r "옛태그" content/post/

# 2. 해당 글들의 태그 수정

# 태그는 자동으로 생성/삭제됨
```

---

## 8. 이미지 관리

### 8.1 이미지 추가 방법

#### 방법 1: static 폴더 (권장)

```bash
# 이미지 파일 복사
cp 이미지.png static/img/

# 글에서 사용
![이미지 설명](/img/이미지.png)
```

#### 방법 2: 글과 같은 폴더

```bash
content/post/글제목/
├── index.md
└── image.png

# 글에서 사용
![이미지 설명](image.png)
```

### 8.2 이미지 갤러리 만들기

```markdown
![이미지1](image1.jpg)
![이미지2](image2.jpg)
```

한 줄에 여러 이미지를 double space로 구분하면 갤러리로 자동 변환됩니다.

### 8.3 아바터/파비콘 변경

```bash
# 새 이미지 준비
static/img/avatar.png

# 설정 확인 (config/_default/params.toml)
favicon        = "/img/avatar.png"
[sidebar]
    avatar   = "img/avatar.png"
```

---

## 9. 메뉴 관리

### 9.1 현재 메뉴 구조

메뉴는 **각 페이지의 Front Matter**에서 관리합니다.

```yaml
---
menu:
    main:
        name: Home
        weight: -100
        params:
            icon: home
---
```

### 9.2 새 메뉴 항목 추가

#### 새 페이지 만들기

```bash
# 1. 페이지 생성
hugo new page/새페이지명/index.md

# 2. Front Matter에 메뉴 설정 추가
---
title: "새 페이지"
menu:
    main:
        weight: -60
        params:
            icon: file-text
---
```

### 9.3 메뉴 순서 변경

`weight` 값으로 순서 조절 (낮을수록 왼쪽)

```yaml
weight: -100  # 가장 왼쪽
weight: -90
weight: -80
```

### 9.4 사용 가능한 아이콘

테마는 [Tabler Icons](https://tabler.io/icons)를 사용합니다.

```yaml
icon: home       # 홈
icon: user       # 유저/소개
icon: archive    # 아카이브
icon: search     # 검색
icon: link       # 링크
icon: file-text  # 문서
```

---

## 10. 설정 변경

### 10.1 사이트 기본 정보

파일: `hugo.toml` 또는 `config/_default/hugo.toml`

```toml
baseURL = 'https://rebugui.github.io/hate-coding-turtle/'
languageCode = 'ko-kr'
title = '코딩이 싫은 거북이'
```

### 10.2 사이드바 설정

파일: `config/_default/params.toml`

```toml
[sidebar]
    emoji    = "🐢"
    subtitle = "Clean, responsive Hugo theme"
    avatar   = "img/avatar.png"
```

### 10.3 소셜 링크

파일: `config/_default/menu.toml`

```toml
[[social]]
    identifier = "github"
    name       = "GitHub"
    url        = "https://github.com/rebugui"
    [social.params]
        icon = "brand-github"
```

### 10.4 다크모드 설정

파일: `config/_default/params.toml`

```toml
[colorScheme]
    toggle = true    # 토글 버튼 표시
    default = "auto" # auto, light, dark
```

---

## 11. 배포 방법

### 11.1 자동 배포

main 브랜치에 푸시하면 **자동으로 배포**됩니다.

```bash
git add .
git commit -m "커밋 메시지"
git push origin main
```

### 11.2 배포 확인

- **GitHub Actions**: https://github.com/rebugui/hate-coding-turtle/actions
- **배포된 사이트**: https://rebugui.github.io/hate-coding-turtle/

### 11.3 배포 전 로컬 테스트

```bash
# 1. 빌드 테스트
hugo --minify

# 2. 로컬 서버 확인
hugo server

# 3. 문제 없으면 푸시
git push origin main
```

---

## 12. 자주 하는 작업

### 12.1 새 보안 글 작성

```bash
# 1. 새 글 생성
hugo new post/보안-취약점-분석/index.md

# 2. 파일 수정
code content/post/보안-취약점-분석/index.md

# 3. 로컬 확인
hugo server

# 4. 커밋 및 배포
git add content/post/보안-취약점-분석/
git commit -m "feat: 보안 취약점 분석 글 작성"
git push origin main
```

### 12.2 CTF writeup 업로드

```yaml
---
title: "DreamHack CTF: 문제이름"
date: 2026-02-04
tags:
  - CTF
  - DreamHack
  - pwnable
categories:
  - Writeup
---

## 문제 설명

... (내용) ...
```

### 12.3 코드 블록 사용

````markdown
\```python
def exploit():
    print("Hello, World!")
\```
````

### 12.4 수식 작성 (KaTeX)

```latex
$$
E = mc^2
$$
```

---

## 13. 트러블슈팅

### 13.1 빌드 실패

```bash
# Hugo �시 삭제
rm -rf resources/
rm -rf public/

# 재빌드
hugo --minify
```

### 13.2 변경사항 반영 안됨

```bash
# 브라우저 �시 삭제
# Chrome: Cmd+Shift+R (Mac), Ctrl+Shift+R (Windows)

# Hugo 서버 재시작
hugo server --disableFastRender
```

### 13.3 테마 업데이트

```bash
# 테마 서브모듈 업데이트
cd themes/hugo-theme-stack
git pull origin main
cd ../..

# 변경사항 확인 후 커밋
git add themes/hugo-theme-stack
git commit -m "chore: update theme"
```

### 13.4 Git 충돌 해결

```bash
# 1. 변경사항 저장
git stash

# 2. 최신 코드 가져오기
git pull origin main

# 3. 저장한 변경사항 적용
git stash pop

# 4. 충돌 해결 후 커밋
git add .
git commit -m "resolve merge conflict"
```

---

## 14. 참고 자료

### 14.1 공식 문서

- **Hugo 공식 문서**: https://gohugo.io/documentation/
- **Stack 테마 문서**: https://stack.jimmycai.com/
- **GitHub Pages 문서**: https://docs.github.com/en/pages

### 14.2 유용한 링크

- **Hugo 퀵스타트**: https://gohugo.io/getting-started/quick-start/
- **Markdown 가이드**: https://www.markdownguide.org/
- **Tabler Icons**: https://tabler.io/icons

### 14.3 프로젝트 관련

- **GitHub 저장소**: https://github.com/rebugui/hate-coding-turtle
- **실제 배포 사이트**: https://rebugui.github.io/hate-coding-turtle/

---

## 📞 문제가 생겼을 때

1. 로컬에서 `hugo server`로 먼저 테스트
2. GitHub Actions 배포 로그 확인
3. 위 트러블슈팅 섹션 참고
4. Hugo 공식 문서 검색

---

*이 가이드는 2026-02-04에 작성되었습니다.*
*운영 중 문제가 발생하면 가이드를 업데이트해주세요.*
