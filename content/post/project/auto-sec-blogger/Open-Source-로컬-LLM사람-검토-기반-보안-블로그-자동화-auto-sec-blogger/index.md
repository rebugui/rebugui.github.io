---
title: "[Open Source] 로컬 LLM·사람 검토 기반 보안 블로그 자동화 (auto-sec-blogger)"
date: 2026-06-04T21:48:43+09:00
draft: false
categories: ["project/auto-sec-blogger"]
tags: ["project/auto-sec-blogger"]
author: "Intelligence Agent"
---

## 📋 개요

보안·기술 뉴스를 자동으로 수집하고, **로컬 LLM(Ollama Gemma4)** 으로 글 초안을 작성한 뒤, **사람이 검토·승인한 글만** GitHub Pages 블로그에 발행하는 지능형 에이전트 **auto-sec-blogger**를 소개합니다. 지금 보고 계신 이 블로그가 바로 이 도구로 운영됩니다.
> **GitHub 저장소:** [https://github.com/rebugui/auto-sec-blogger](https://github.com/rebugui/auto-sec-blogger)

## 🎯 제작 배경

매일 쏟아지는 보안 뉴스를 사람이 일일이 정리해 글로 쓰는 것은 비효율적입니다. 그렇다고 LLM에 전부 맡겨 자동 발행하면 품질·사실성 관리가 어렵습니다. 그래서 **생성은 자동, 공개는 사람 승인**이라는 Human-in-the-Loop 원칙으로 설계했고, 클라우드 비용·프라이버시를 피하려 **외부 호출 없는 로컬 모델**을 사용합니다.

## 🏗️ 파이프라인 구조

```plain text
뉴스 수집 (Google News · arXiv · HackerNews · Hada.io)
    ↓
Ollama Gemma4 평가/선별 (카테고리별 점수 · round-robin)
    ↓
Ollama Gemma4 글 작성 (멀티 페르소나: 보안/AI/DevOps/CVE)
    ↓
Notion 저장 (초안 작성중 → 검토중)
    ↓
[사람 검토] 검토중 → 검토 완료 로 승인
    ↓
Hugo content/post 생성 → git push → GitHub Pages 배포
```

**핵심 설계**
- **로컬 LLM**: `gemma4:e4b` (OpenAI 호환 `localhost:11434`), 외부 클라우드 호출 없음
- **견고한 선별**: 카테고리 후보 제한 + 청크 분할 + `json_mode` + 복구 파싱으로 LLM 응답 잘림에 대비
- **멀티 페르소나 작성**: 보안·AI/ML·DevOps·CVE 전문가 톤, Mermaid 다이어그램·표 포함
- **상태 관리**: Notion에서 초안→검토중→검토 완료→게시 완료 추적, 중복 발행 방지

## ⚖️ 라이선스 / 발행 대상

**MIT License**. 발행 대상은 **GitHub Pages(Hugo)** 전용입니다. 네이버·티스토리 자동 발행도 검토했으나, 두 플랫폼 모두 글쓰기 시 캡차(네이버 자동등록방지 / 티스토리 DKAPTCHA 지도 캡차)로 봇 발행을 차단해 제외했습니다.

## ⚠️ 주의사항
- 로컬 Gemma4 작성은 느릴 수 있어 스케줄러 타임아웃을 넉넉히(예: 1800초) 두는 것이 좋습니다.
- Notion 토큰·블로그 DB ID·GitHub 토큰 등 환경 변수 설정이 선행돼야 합니다.
- 완전 자동 발행을 원하면 `AUTO_PUBLISH_STATUS=검토중`으로 바꿀 수 있으나, 품질 관리를 위해 사람 검토를 권장합니다.

## 🚀 실행 방법

```bash
# 설치
pip3 install -r scripts/requirements.txt
ollama pull gemma4:e4b

# 파이프라인 (Notion 초안까지)
python3 scripts/intelligence_pipeline.py --max-articles 3

# 승인된 글 발행 (1건 테스트)
AUTO_PUBLISH_MAX=1 python3 scripts/auto_publish_approved.py
```

## 💬 피드백

개선 제안·버그·풀 리퀘스트를 환영합니다. **[GitHub Issues](https://github.com/rebugui/auto-sec-blogger/issues)** 로 알려 주세요.