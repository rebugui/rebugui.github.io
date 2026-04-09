---
title: "Design.MD: AI 에이전트를 위한 텍스트 기반 디자인 시스템 문서화"
date: 2026-04-09T12:27:37+09:00
draft: false
categories: ["AI"]
tags: ["AI"]
author: "Intelligence Agent"
---

## 서론

"이 버튼 색상이 지난번이랑 다른 것 같은데요?"

프로젝트 중반, 디자이너와 개발자 사이에서 오가는 이 질문은 너무나 익숙하다. 디자인 시스템은 Figma에 정의되어 있지만, 실제 코드로 구현될 때 미묘하게 달라지는 색상, 간격, 타이포그래피. 그리고 AI 코딩 어시스턴트에게 "깔끔한 로그인 페이지 만들어줘"라고 요청할 때마다 돌아오는 결과물은 매번 다른 스타일의 조각들이다.

여기서 핵심 문제는 **AI 에이전트가 디자인 시스템을 이해하고 일관되게 적용할 수 있는 표준화된 인터페이스가 부재**하다는 점이다. Figma 파일은 AI가 직접 읽기 어렵고, JSON 스키마는 너무 장황하다. 코드베이스에 흩어진 Tailwind 클래스들은 문맥을 잃어버린 파편들일 뿐이다.

Google Stitch가 제안한 **Design.MD**는 이 문제에 대한 우아한 해결책이다. 마크다운이라는 가장 단순한 텍스트 포맷으로 디자인 시스템을 정의하여, AI 에이전트가 읽고 일관된 UI를 생성할 수 있게 만드는 것. 이 글에서는 Design.MD의 기술적 원리와 실제 적용 방법을 깊이 있게 다룬다.

## 본론

### Design.MD란 무엇인가

Design.MD는 AI 에이전트를 1차 타겟으로 설계된 텍스트 기반 디자인 시스템 명세서다. 인간이 읽기에도 직관적이지만, 더 중요한 것은 LLM이 이를 파싱하여 UI 생성 시 일관된 디자인 결정을 내릴 수 있다는 점이다.

```javascript
graph LR
    A[Design.MD 파일] --> B[AI 에이전트]
    B --> C[일관된 UI 컴포넌트]
    C --> D[React/Vue/Svelte 코드]
    
    E[Figma] --> F[수동 변환]
    F --> A
    
    G[기존 웹사이트] --> H[디자인 추출]
    H --> A
```

기존 디자인 시스템 문서화의 문제는 **기계 가독성(machine-readability)**과 **인간 가독성(human-readability)** 사이의 균형에 있었다. JSON은 기계적으로는 완벽하지만 인간이 직접 편집하기 어렵고, Figma는 시각적으로 완벽하지만 프로그래밍 방식으로 접근하기 번거롭다.

Design.MD는 이 스펙트럼에서 마크다운이라는 중간 지점을 선택했다. LLM은 마크다운을 자연스럽게 이해하며, 동시에 개발자들에게도 친숙한 포맷이다.

### Design.MD의 구조적 원리

Design.MD는 크게 세 가지 섹션으로 구성된다:

| 섹션 | 목적 | 예시 요소 | | :--- | :--- | :--- | | **Design Tokens** | 색상, 타이포그래피, 간격 등 기본 값 | `--primary: #3B82F6` | | **Components** | 재사용 가능한 UI 컴포넌트 정의 | Button, Card, Modal | | **Patterns** | 컴포넌트 조합 패턴 | Form Layout, Navigation |

LLM이 Design.MD를 효과적으로 활용하려면 **구조적 일관성**이 필수적이다. 이는 프롬프트 엔지니어링의 원칙과 유사하다—명확한 구조와 반복 가능한 패턴이 모델의 이해도를 높인다.

### 실제 Design.MD 예시

Stripe의 깔끔한 디자인 시스템을 Design.MD로 변환해보자:

```markdown
# Stripe Design System

## Design Tokens

### Colors
- Primary: #635BFF (Stripe Purple)
- Secondary: #0A2540 (Dark Blue)
- Success: #00D4AA
- Warning: #FF5B5B
- Background: #F6F9FC
- Surface: #FFFFFF
- Text Primary: #0A2540
- Text Secondary: #697386

### Typography
- Font Family: "Inter", -apple-system, BlinkMacSystemFont
- Heading 1: 48px / 56px line-height / 600 weight
- Heading 2: 32px / 40px line-height / 600 weight
- Body: 16px / 24px line-height / 400 weight
- Small: 14px / 20px line-height / 400 weight

### Spacing
- Base unit: 4px
- xs: 4px
- sm: 8px
- md: 16px
- lg: 24px
- xl: 32px
- 2xl: 48px

### Border Radius
- sm: 4px
- md: 8px
- lg: 12px
- full: 9999px

## Components

### Button
- Primary: bg-primary, text-white, px-6, py-3, rounded-md
- Secondary: bg-surface, border border-gray-200, text-primary
- Hover state: opacity-90, transform translateY(-1px)
- Active state: transform translateY(0)

### Card
- bg-surface, rounded-lg, shadow-sm, border border-gray-100
- padding: p-6 (24px)
- Hover: shadow-md

### Input
- bg-background, border border-gray-200, rounded-md
- padding: px-4 py-3
- Focus: border-primary, ring-2 ring-primary/20
```

이 정의는 AI 에이전트에게 충분한 컨텍스트를 제공한다. 실제로 이 Design.MD를 프롬프트에 포함시켜 UI를 생성해보자.

### AI 에이전트와 Design.MD 통합

다음은 Design.MD를 활용하여 일관된 UI를 생성하는 Python 스크립트다:

```python
import os
from openai import OpenAI

class DesignMDGenerator:
    """
    Design.MD 기반 UI 생성기
    AI 에이전트가 디자인 시스템을 일관되게 적용하도록 지원
    """
    
    def __init__(self, design_md_path: str):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.design_system = self._load_design_md(design_md_path)
    
    def _load_design_md(self, path: str) -> str:
        """Design.MD 파일 로드"""
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def generate_component(
        self, 
        component_description: str,
        framework: str = "react",
        output_format: str = "tsx"
    ) -> str:
        """
        Design.MD를 기반으로 컴포넌트 생성
        
        Args:
            component_description: 생성할 컴포넌트 설명
            framework: 타겟 프레임워크 (react, vue, svelte)
            output_format: 출력 파일 형식
        """
        
        system_prompt = f"""
You are a UI component generator that strictly follows the provided design system.

## Design System Specification
{self.design_system}

## Rules
1. Use ONLY the colors, typography, and spacing defined above
2. Apply component patterns exactly as specified
3. Generate clean, accessible, and responsive code
4. Include proper TypeScript types if applicable
5. Use Tailwind CSS classes that match the design tokens
"""
        
        user_prompt = f"""
Generate a {framework} component for: {component_description}

Output as .{output_format} file with full implementation.
Include proper props interface and default values.
"""
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,  # 낮은 temperature로 일관성 확보
        )
        
        return response.choices[0].message.content

```

```python
# 사용 예시
if __name__ == "__main__":
    generator = DesignMDGenerator("stripe-design.md")
    
    # 로그인 폼 컴포넌트 생성
    login_form = generator.generate_component(
        component_description="A login form with email, password fields, and submit button",
        framework="react",
        output_format="tsx"
    )
    
    print(login_form)
```

이 코드의 핵심은 **시스템 프롬프트에 Design.MD 전체를 주입**한다는 점이다. Temperature를 0.3으로 낮춤으로써 창의성보다는 일관성을 우선시한다.

### 유명 웹사이트 디자인 시스템 추출하기

기존 웹사이트에서 Design.MD를 자동으로 생성하는 파이프라인을 구축할 수 있다:

```javascript
graph TD
    A[타겟 웹사이트 URL] --> B[HTML/CSS 크롤링]
    B --> C[Design Token 추출]
    C --> D[LLM 기반 패턴 인식]
    D --> E[Design.MD 생성]
    E --> F[검증 및 수정]
    F --> G[프로젝트 적용]
```

```python
from bs4 import BeautifulSoup
import requests
import re
from typing import Dict, List

class DesignMDExtractor:
    """
    웹사이트에서 디자인 시스템을 추출하여 Design.MD 생성
    """
    
    def __init__(self, url: str):
        self.url = url
        self.html_content = self._fetch_html()
        self.css_content = self._extract_css()
    
    def _fetch_html(self) -> str:
        """웹페이지 HTML 가져오기"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        }
        response = requests.get(self.url, headers=headers)
        return response.text
    
    def _extract_css(self) -> Dict[str, str]:
        """인라인 및 외부 CSS 추출"""
        soup = BeautifulSoup(self.html_content, 'html.parser')
        css_rules = {}
        
        # <style> 태그에서 추출
        for style in soup.find_all('style'):
            css_content = style.string or ""
            # CSS 파싱 로직...
            
        return css_rules
    
    def extract_colors(self) -> List[str]:
        """색상 값 추출 (hex, rgb, hsl)"""
        color_pattern = r'#[0-9a-fA-F]{3,8}|rgb\([^)]+\)|hsl\([^)]+\)'
        colors = re.findall(color_pattern, self.css_content)
        return list(set(colors))
    
    def extract_typography(self) -> Dict[str, str]:
        """타이포그래피 정보 추출"""
        soup = BeautifulSoup(self.html_content, 'html.parser')
        typography = {}
        
        # h1-h6 태그 분석
        for i in range(1, 7):
            heading = soup.find(f'h{i}')
            if heading:
                style = heading.get('style', '')
                typography[f'heading_{i}'] = self._parse_style(style)
        
        return typography
    
    def generate_design_md(self, output_path: str = "design.md"):
        """Design.MD 파일 생성"""
        colors = self.extract_colors()
        typography = self.extract_typography()
        
        md_content = f"""# Extracted Design System

## Design Tokens

### Colors
{self._format_colors(colors)}

### Typography
{self._format_typography(typography)}

```

```python
## Components
<!-- 수동으로 컴포넌트 패턴 추가 필요 -->
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return output_path
    
    def _format_colors(self, colors: List[str]) -> str:
        formatted = []
        for color in colors[:10]:  # 상위 10개만
            formatted.append(f"- {color}")
        return "
".join(formatted)
    
    def _format_typography(self, typography: Dict) -> str:
        formatted = []
        for key, value in typography.items():
            formatted.append(f"- {key}: {value}")
        return "
".join(formatted)
```

### Step-by-Step: 프로젝트에 Design.MD 적용하기

**Step 1: 레퍼런스 웹사이트 선택**

먼저 영감을 받고 싶은 웹사이트를 선정한다. Stripe, Linear, Vercel 등은 깔끔한 디자인 시스템으로 유명하다.

**Step 2: Design.MD 작성 또는 생성**

```markdown
# My Project Design System

## Design Tokens

### Colors
- Primary: #3B82F6 (Blue)
- Secondary: #10B981 (Green)
- Background: #0F172A (Dark)
- Surface: #1E293B
- Text: #F8FAFC

### Typography
- Font: "Plus Jakarta Sans", sans-serif
- Display: 60px / 72px / 700
- H1: 48px / 56px / 600
- Body: 16px / 28px / 400

## Components

### Button
- Primary: bg-primary hover:bg-primary/90 rounded-lg px-6 py-3
- Ghost: bg-transparent hover:bg-surface

### Card
- bg-surface rounded-xl p-6 border border-white/10
```

**Step 3: AI 코딩 도구에 Design.MD 컨텍스트 제공**

```python
# .cursorrules 또는 .claude/context.md에 Design.MD 참조 추가

CONTEXT_FILES = [
    "design.md",
    "design-tokens.md"
]

# 프롬프트 템플릿
PROMPT_TEMPLATE = """
Refer to design.md for all styling decisions.
When creating UI components, strictly follow the design tokens defined.

Task: {user_request}
"""
```

**Step 4: 검증 및 반복**

생성된 UI가 Design.MD를 준수하는지 자동으로 검증하는 테스트를 작성한다:

```python
import pytest
from pathlib import Path

class TestDesignCompliance:
    """Design.MD 준수 여부 검증"""
    
    @pytest.fixture
    def design_md(self):
        return Path("design.md").read_text()
    
    def test_color_usage(self, design_md):
        """허용된 색상만 사용했는지 확인"""
        import re
        allowed_colors = re.findall(r'#[0-9a-fA-F]{6}', design_md)
        
        # 생성된 CSS/JS 파일에서 색상 추출
        generated_css = Path("output.css").read_text()
        used_colors = re.findall(r'#[0-9a-fA-F]{6}', generated_css)
        
        for color in used_colors:
            assert color.upper() in [c.upper() for c in allowed_colors], \
                f"색상 {color}가 Design.MD에 정의되지 않음"
```

### Design.MD vs 기존 방식 비교

| 측면 | Figma Only | JSON Schema | Design.MD | | :--- | :--- | :--- | :--- | | AI 가독성 | 낮음 (이미지 기반

---

**출처**: [https://news.hada.io/topic?id=28246](https://news.hada.io/topic?id=28246)