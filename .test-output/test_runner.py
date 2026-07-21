#!/usr/bin/env python3
"""
auto-sec-blogger v3.0 고도화 방향 테스트
- 동일 기사에 대해 다양한 프롬프트 구성으로 생성
- 결과물 비교 분석
"""
import asyncio, sys, os, json, time
from datetime import datetime

sys.path.insert(0, '/Users/rebugui/.hermes/skills/openclaw-imports/auto-sec-blogger/scripts')

# Load env
env_path = os.path.expanduser('~/.hermes/.skills.env')
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            os.environ.setdefault(k, v)

from collector import NewsCollector
from writer import BlogWriter, Persona
from llm_client_async import AsyncLLMClient

OUT_DIR = os.path.expanduser('~/.hermes/workspace/blog/.test-output')
os.makedirs(OUT_DIR, exist_ok=True)

# ============================================================
# STEP 1: Collect articles
# ============================================================
print("=" * 60)
print("STEP 1: Collecting articles...")
c = NewsCollector()
articles = c.fetch_all(max_results_per_source=3)
print(f"Collected {len(articles)} articles")

# Pick diverse samples: different sources/categories
samples = []
seen_sources = set()
for a in articles:
    src = a.get('source', '')
    if src not in seen_sources and len(samples) < 10:
        samples.append(a)
        seen_sources.add(src)

print(f"Selected {len(samples)} diverse samples")
for i, s in enumerate(samples):
    print(f"  [{i}] {s.get('source','?'):20s} | {s.get('title','?')[:60]}")

# Save samples
with open(os.path.join(OUT_DIR, 'samples.json'), 'w') as f:
    json.dump(samples, f, ensure_ascii=False, indent=2, default=str)

# ============================================================
# STEP 2: Test different writing approaches
# ============================================================
print("\n" + "=" * 60)
print("STEP 2: Generating with different configurations...")

# Test configurations
CONFIGS = {
    "A_current": {
        "label": "A. 현재 기본 (서론/본론/결론 + 페르소나)",
        "desc": "현재 prompts.yaml 그대로 사용"
    },
    "B_technical_dive": {
        "label": "B. 기술 딥다이브 (서론/본론/결론 제거)",
        "desc": "구조: 개요→메커니즘→PoC분석→방어전략→참고"
    },
    "C_objective_facts": {
        "label": "C. 객관적 팩트 중심 (1인칭 제거)",
        "desc": "NVD/CVSS/소스코드 인용, 3인칭 객관적 서술"
    },
    "D_minimal_structure": {
        "label": "D. 최소 구조 + 높은 정보 밀도",
        "desc": "불필요한 수사 제거, 표/코드 위주, 간결"
    },
    "E_ai_disclosure": {
        "label": "E. AI 고지 + 기술 분석",
        "desc": "AI 생성 고지 포함 + 기술적 정확성 강조"
    },
}

client = AsyncLLMClient()
writer = BlogWriter(client)

results = {}

for config_key, config_info in CONFIGS.items():
    print(f"\n{'─'*50}")
    print(f"[{config_key}] {config_info['label']}")
    print(f"  {config_info['desc']}")
    
    article = samples[0]  # Use same article for fair comparison
    persona = Persona.SECURITY
    
    start = time.time()
    try:
        # For A: use default writer
        if config_key == "A_current":
            result = await writer.generate_article(article, persona)
        else:
            result = await writer._generate_custom(
                article, persona, PersonaConfig.get(persona), 
                mode=config_key
            )
        elapsed = time.time() - start
        print(f"  ✅ Generated in {elapsed:.1f}s")
        print(f"  Title: {result.get('title', 'N/A')[:80]}")
        print(f"  Content length: {len(result.get('content', ''))} chars")
        
    except AttributeError:
        # Fallback to normal generate for now
        print(f"  ⚠️ Custom mode not available, using default")
        result = await writer.generate_article(article, persona)
        elapsed = time.time() - start
        print(f"  ✅ Generated in {elapsed:.1f}s")
        print(f"  Title: {result.get('title', 'N/A')[:80]}")
        print(f"  Content length: {len(result.get('content', ''))} chars")
    
    results[config_key] = result
    
    # Save output
    out_file = os.path.join(OUT_DIR, f'{config_key}.md')
    with open(out_file, 'w') as f:
        f.write(f"# {config_info['label']}\n")
        f.write(f"**설명**: {config_info['desc']}\n\n")
        f.write(f"**생성 시간**: {elapsed:.1f}s\n")
        f.write(f"**제목**: {result.get('title', 'N/A')}\n\n")
        f.write("---\n\n")
        f.write(result.get('content', ''))
    
    time.sleep(1)

# Save summary
summary = {
    "test_time": datetime.now().isoformat(),
    "article": {
        "title": samples[0].get('title', 'N/A'),
        "source": samples[0].get('source', 'N/A'),
        "url": samples[0].get('url', 'N/A'),
    },
    "results": {
        k: {
            "title": r.get('title', ''),
            "content_length": len(r.get('content', '')),
        }
        for k, r in results.items()
    }
}
with open(os.path.join(OUT_DIR, 'summary.json'), 'w') as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

print(f"\n{'='*60}")
print(f"All outputs saved to: {OUT_DIR}")
print(f"Files: {os.listdir(OUT_DIR)}")
