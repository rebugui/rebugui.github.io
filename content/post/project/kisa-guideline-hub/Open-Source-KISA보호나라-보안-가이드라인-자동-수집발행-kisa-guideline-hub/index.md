---
title: "[Open Source] KISA·보호나라 보안 가이드라인 자동 수집·발행 (kisa-guideline-hub)"
date: 2026-06-04T21:48:28+09:00
draft: false
categories: ["project/kisa-guideline-hub"]
tags: ["project/kisa-guideline-hub"]
author: "Intelligence Agent"
---

## 📋 개요

**KISA(한국인터넷진흥원)** 와 **보호나라(KRCERT)** 의 보안 가이드라인을 자동으로 수집해 Notion에 정리·발행하는 시스템 **kisa-guideline-hub**를 소개합니다. 일반 보안 뉴스와 달리 **LLM 처리 없이 원문 그대로** 발행하고, **PDF 첨부**를 지원하는 것이 특징입니다.
> **GitHub 저장소:** [https://github.com/rebugui/kisa-guideline-hub](https://github.com/rebugui/kisa-guideline-hub)

## 🎯 제작 배경

보안 가이드라인은 뉴스처럼 요약·재가공하기보다 **원문과 PDF를 정확히 보존**하는 것이 중요합니다. KISA·보호나라에 흩어진 가이드라인을 주기적으로 모아 한 Notion DB에 축적하면, 컴플라이언스 업무에서 빠르게 참조할 수 있습니다.

## 🏗️ 동작 방식

```plain text
KISA 크롤러 (가이드라인 수집)
    ↓
보호나라(Boho) 크롤러 (가이드라인 + PDF 다운로드)
    ↓
temp_downloads/ 에 PDF 저장
    ↓
Notion(가이드라인 전용 DB)에 발행 + PDF 파일 블록 첨부
```

**핵심 기능**
- **수집**: KISA 가이드라인 + 보호나라 가이드라인(PDF 포함)
- **직접 발행**: LLM 요약 없이 원문 그대로 Notion 발행
- **PDF 첨부**: Notion 파일 블록으로 PDF 업로드(최대 20MB)
- **중복 방지**: URL 기반 자동 중복 체크로 여러 번 실행해도 안전
- **별도 DB**: 가이드라인 전용 `GUIDE_DATABASE_ID`(미설정 시 뉴스 DB 공유)
> 이 도구는 security-news-feed의 KISA·Boho 크롤러 모듈을 재사용합니다.

## ⚖️ 라이선스

**MIT License** — 자유롭게 사용·수정·배포할 수 있습니다.

## ⚠️ 주의사항
- Notion API 키와 (선택) 가이드라인 전용 DB ID가 필요합니다.
- PDF 업로드는 Notion 파일 크기 제한(최대 20MB)을 따릅니다.
- KISA·보호나라 웹사이트 구조가 바뀌면 수집이 실패할 수 있습니다.

## 🚀 실행 방법

```bash
# 수집만
python3 scripts/publish_guidelines.py --collect

# 발행만
python3 scripts/publish_guidelines.py --publish

# 전체 (수집 + 발행)
python3 scripts/publish_guidelines.py --full
```

## 💬 피드백

버그·기능 제안·풀 리퀘스트를 환영합니다. **[GitHub Issues](https://github.com/rebugui/kisa-guideline-hub/issues)** 로 알려 주세요.