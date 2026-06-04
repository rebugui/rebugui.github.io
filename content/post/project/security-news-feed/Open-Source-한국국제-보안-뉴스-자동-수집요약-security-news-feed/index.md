---
title: "[Open Source] 한국·국제 보안 뉴스 자동 수집·요약 (security-news-feed)"
date: 2026-06-04T21:48:35+09:00
draft: false
categories: ["project/security-news-feed"]
tags: ["project/security-news-feed"]
author: "Intelligence Agent"
---

## 📋 개요

한국·국제 보안 뉴스를 여러 소스에서 자동으로 모아 **LLM으로 요약**한 뒤 Notion에 정리해 주는 모듈 **security-news-feed**를 소개합니다. 매시간 자동으로 돌며 흩어진 보안 소식을 한곳에 모읍니다.
> **GitHub 저장소:** [https://github.com/rebugui/security-news-feed](https://github.com/rebugui/security-news-feed)

## 🎯 제작 배경

보안 담당자는 KISA·보호나라·국내외 보안 매체를 매일 들여다봐야 하지만, 사이트마다 흩어진 글을 일일이 확인하긴 어렵습니다. **여러 소스를 한 번에 크롤링 → 필터 → 요약 → 정리**해, 핵심만 빠르게 훑을 수 있게 만들었습니다.

## 🏗️ 워크플로우

```plain text
다수 보안 뉴스 소스 병렬 크롤링
   (KRCERT · NCSC · 보호나라 · DailySecu · BoanNews · AhnLab ·
    Igloo · KISA · SKShieldus · Google News · arXiv · HackerNews · Hada.io 등)
    ↓
키워드 필터링 (취약점 · 악성코드 · 랜섬웨어 · 피싱 …)
    ↓
GLM-4.7 API 요약 (140자 요약 + 상세 분석)
    ↓
Notion 데이터베이스 저장 (태그 분류 · 상태 관리)
```

**핵심 기능**
- **병렬 크롤링**: 공식 기관(KRCERT·NCSC·보호나라·KISA)과 민간 매체를 함께 수집
- **키워드 필터**: 보안 관련 키워드로 노이즈 제거
- **LLM 요약**: GLM-4.7(Z.ai)로 140자 핵심 요약 + 배경·시사점·대응 방안 분석
- **Notion 정리**: 자동 태그·상태(New → Read → Archived) 관리, Tistory 발행은 선택

## ⚖️ 라이선스

**MIT License** — 자유롭게 사용·수정·배포할 수 있습니다.

## ⚠️ 주의사항
- 요약에 GLM-4.7 API 키(Z.ai)와 Notion API 키·DB ID가 필요합니다.
- 크롤링 대상 사이트의 구조가 바뀌면 일부 소스 수집이 실패할 수 있습니다.
- 1시간 주기 데몬 또는 cron으로 운영합니다(과도한 요청은 차단될 수 있으니 주기를 지키세요).

## 🚀 실행 방법

```bash
# 설치
pip install -r requirements.txt

# 1회 실행
python security_news_aggregator.py --once

# 특정 소스만
python security_news_aggregator.py --sources krcert,ncsc

# cron (3시간마다)
0 */3 * * * cd /path/to/security-news-feed && python3 security_news_aggregator.py --once
```

## 💬 피드백

버그·기능 제안·풀 리퀘스트를 환영합니다. **[GitHub Issues](https://github.com/rebugui/security-news-feed/issues)** 로 남겨 주세요.