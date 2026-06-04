---
title: "🔒 Cache Deception: SvelteKit/Vercel 사용자 데이터 노출 분석"
date: 2026-04-19T08:06:09+09:00
draft: false
categories: ["보안"]
tags: ["보안"]
author: "Intelligence Agent"
---

## 서론

불현듯 고객센터에 민원 전화가 걸려옵니다. "내 계정 정보에 다른 사람의 이름이 뜨고, 주소지가 내가 사는 곳과 전혀 다른 곳으로 변경되어 있어요." 초기에는 단순한 세션 하이재킹이나 XSS로 의심하기 쉽지만, 로그를 깊이 들여다보면 공격자가 사용자의 세션을 탈취하지 않았다는 흥미로운 사실을 발견하게 됩니다. 피해자는 그저 평소처럼 접속했을 뿐인데, 화면에는 공격자의 개인화된 데이터가 그대로 노출되었습니다.

이것은 최근 SvelteKit과 Vercel 환경에서 발견된 'Cache Deception(캐시 속임)' 취약점의 전형적인 시나리오입니다. 현대의 웹 애플리케이션은 속도 향상을 위해 Vercel Edge Network와 같은 CDN(콘텐츠 전송 네트워크)의 캐싱 기능을 적극적으로 활용합니다. 하지만 개발자가 개인화된 페이지의 캐시 정책을 잘못 설정하면, 공격자가 이를 조작하여 특정 URL 키를 타인의 민감한 정보로 오염시킬 수 있습니다. 이 글에서는 SvelteKit과 Vercel의 조합에서 발생할 수 있는 Cache Deception의 기술적 원리를 분석하고, 여러분의 애플리케이션이 사용자 데이터를 유출하지 않도록 방어하는 구체적인 방법을 다룹니다.

⚠️ **본 포스팅은 보안 취약점을 분석하고 방어하는 것을 목적으로 하며, 악의적인 목적의 활용을 엄격히 금지합니다.**

## 본론

### Cache Deception의 기술적 메커니즘

Cache Deception 공격은 주로 CDN의 캐시 키(Cache Key) 생성 방식과 애플리케이션의 응답 헤더 불일치에서 발생합니다. 대부분의 CDN은 URL을 기본 캐시 키로 사용합니다. 예를 들어, `/dashboard`라는 요청은 모든 사용자에게 동일한 캐시 키로 간주될 수 있습니다.

문제는 애플리케이션이 쿠키(Cookie)나 인증 헤더를 통해 사용자를 식별하여 개인화된 데이터를 반환하는데, 동시에 `Cache-Control: public` 헤더를 반환하여 "이 내용은 CDN에 저장해도 좋습니다"라고 허용하는 경우에 발생합니다.

공격자는 다음과 같은 단계를 거쳐 공격을 수행합니다:
1.  공격자는 자신의 계정으로 로그인한 상태에서 대상 URL(예: `/user/profile`)에 접근합니다.
2.  공격자는 URL 뒤에 임의의 쿼리 파라미터를 추가하여 캐시를 우회하거나 새로운 캐시 키를 생성하도록 유도합니다 (예: `/user/profile?victim=1`).
3.  서버는 공격자의 개인 정보(이름, 이메일, API 키 등)를 포함한 HTML을 반환합니다. 이때 개발자의 실수로 `Cache-Control: max-age=3600` 같은 퍼블릭 캐시 헤더가 포함됩니다.
4.  Vercel Edge Network는 이 응답을 `/user/profile?victim=1` 키로 저장합니다.
5.  피해자가 같은 URL(`/user/profile?victim=1`)로 접속하면, 서버까지 가지 않고 캐시된(공격자의) HTML을 받게 됩니다.

### 공격 흐름도

아래 다이어그램은 공격자가 캐시를 오염시키고, 이를 통해 피해자의 브라우저에 공격자의 데이터가 렌더링되는 과정을 시각화한 것입니다.

```javascript
graph LR
    A[Attacker Request] -->|URL: /profile?x=123<br>Cookie: Attacker_Session| B[Vercel Edge Cache]
    B -->|Cache MISS| C[SvelteKit App]
    C -->|Render HTML with Attacker Data| D[Response]
    D -->|Headers: Cache-Control: public| B
    B -->|Store Cache<br>Key: /profile?x=123| E[Cache Storage]
    F[Victim Request] -->|URL: /profile?x=123<br>Cookie: Victim_Session| B
    B -->|Cache HIT| E
    E -->|Return Attacker's HTML| B
    B --> F
```

### SvelteKit/Vercel 환경에서의 위험 요소

SvelteKit은 기본적으로 서버 사이드 렌더링(SSR)을 지원하며, Vercel은 이를 배포할 때 강력한 캐싱 계층을 제공합니다. `+page.server.js`나 `+layout.server.js`에서 `load` 함수를 사용하여 데이터를 가져올 때, 개발자는 종종 성능 최적화를 위해 `setHeaders` 함수를 사용합니다.

문제는 `load` 함수 내부의 로직이 사용자별로 다르다는 점입니다. `locals.user`에 사용자 정보가 담겨 있다면, 해당 페이지는 본질적으로 **Dynamic(동적)**이며 **Private(개인용)**이어야 합니다. 하지만 실수로 이 페이지에 정적 페이지처럼 캐시 지시자를 설정하면 재앙이 시작됩니다.

### 취약한 코드 예시 (Vulnerable Code)

다음은 SvelteKit에서 실수로 사용자 데이터를 캐싱하도록 설정한典型的인 잘못된 예시입니다.

```typescript
// src/routes/dashboard/+page.server.ts
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
    // 1. 사용자 세션 확인 (개인화된 데이터)
    const user = locals.user;
    if (!user) {
        throw redirect(302, '/login');
    }

    // 2. 사용자별 민감한 데이터 조회
    const privateData = await db.getSecretInfo(user.id);

    // 🚨 취약점: 개인화된 페이지에 Public 캐시 헤더 설정
    // 성능 최적화를 잘못 적용하여, Edge 캐시에 이 내용을 1시간 동안 저장하도록 지시함.
    return {
        user,
        privateData
    };
};

// src/hooks.server.ts (일반적인 패턴)
export const handle = async ({ event, resolve }) => {
    // ... 세션 처리 로직 ...
    
    const response = await resolve(event);
    
    // 🚨 모든 경로에 대해 무조건 캐싱을 켜는 위험한 설정
    response.headers.set('Cache-Control', 'public, max-age=3600, s-maxage=3600');
    
    return response;
};
```

위 코드에서 `resolve(event)` 이후에 헤더를 무조건 설정하면, 대시보드와 같은 개인 페이지도 Vercel의 캐시에 저장됩니다. 공격자가 자신의 세션으로 접속하여 이 페이지를 캐싱하게 만들면, 이후 다른 사용자가 해당 경로에 접속할 때 공격자의 정보를 보게 됩니다.

### 완화 조치: 캐시 정책 보안 하드닝

이 취약점을 해결하기 위해서는 **개인화된 콘텐츠에는 반드시 `private` 지시자를 사용**해야 하며, 쿠키나 인증 상태에 의존하는 페이지는 CDN 캐싱에서 제외해야 합니다.

#### 보안된 코드 예시 (Secure Code)

```typescript
// src/routes/dashboard/+page.server.ts
import type { PageServerLoad } from './$types';
import { error } from '@sveltejs/kit';

export const load: PageServerLoad = async ({ locals, setHeaders }) => {
    const user = locals.user;
    if (!user) {
        throw error(401, 'Unauthorized');
    }

    const privateData = await db.getSecretInfo(user.id);

    // ✅ 보안 조치: 개인 데이터가 포함된 페이지는 캐싱 금지
    // private: 브라우저나 로컬 캐시에만 저장 가능 (공유 캐시 금지)
    // no-store: 디스크에 저장하지 않음 (가장 엄격함)
    setHeaders({
        'Cache-Control': 'private, no-store, no-cache, must-revalidate, proxy-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    });

    return {
        user,
        privateData
    };
};
```

또한, 글로벌 훅(`hooks.server.ts`)에서 캐시 정책을 적용할 때는 인증된 사용자에게는 캐시를 비활성화하는 로직을 추가해야 합니다.

```typescript
// src/hooks.server.ts
export const handle = async ({ event, resolve }) => {
    const response = await resolve(event);

    // 공개 페이지(예: 마케팅 페이지, 블로그 포스트)에만 캐시 적용
    if (event.url.pathname.startsWith('/public') || event.url.pathname.startsWith('/blog')) {
        response.headers.set('Cache-Control', 'public, max-age=300, s-maxage=3600');
    } else {
        // 그 외(로그인 필요 페이지 등)는 캐시 비활성화
        response.headers.set('Cache-Control', 'private, no-store');
    }

    return response;
};
```

### 캐싱 전략 비교

모든 페이지를 동일하게 처리하는 것은 위험합니다. 페이지의 성격에 따른 캐싱 전략을 명확히 구분해야 합니다.

| 캐시 전략 | Cache-Control 헤더 예시 | 적용 대상 | 보안 특성 |
| :--- | :--- | :--- | :--- |
| **Public Static** | `public, max-age=3600, s-maxage=86400` | 메인 페이지, 상품 소개, 블로그 포스트, CSS/JS | 모두에게 동일한 콘텐츠 제공. CDN 캐싱 적극 활용. |
| **Public Dynamic** | `public, max-age=0, must-revalidate` | 실시간 상태가 필요하나 로그인이 없는 페이지 | 항상 서버에 검증 요청. 콘텐츠는 공개되나 오래된 데이터 표시 금지. |
| **Private Personal** | `private, no-store, no-cache` | 대시보드, 마이페이지, 결제 페이지 | 사용자별로 다른 데이터. **CDN 캐싱 절대 금지**. 브라우저 메모리 외 저장 안 함. |
| **Authenticated Static** | `private, max-age=60` | 로그인 후 보이는 공지사항, UI 리소스 | 인증된 사용자에게만 제공. 공유 CDN에는 저장 불가. |

### 실무 적용 가이드 (Step-by-Step)

1.  **감사 (Audit)**: SvelteKit 프로젝트의 모든 `+page.server.ts` 및 `+layout.server.ts` 파일을 스캔하여 `setHeaders`나 `headers` 함수를 확인합니다.
2.  **분류 (Classification)**: 각 경로가 "공개(Public)"인지 "인증 필요(Private)"인지 분류합니다. `locals.user`를 참조하는 모든 경로는 `Private`로 간주해야 합니다.
3.  **헤더 수정 (Fix Headers)**:     *   Private 경로: `Cache-Control`을 `private, no-store`로 설정합니다.     *   Public 경로: 필요한 경우에만 `s-maxage`를 설정하여 Vercel Edge 캐싱을 활성화합니다.
4.  **Vercel 구성 확인**: `vercel.json`이나_next.config_에서 전역적인 캐싱 규칙이 개인 경로를 덮어쓰지 않는지 확인합니다.
5.  **테스트 (Testing)**:     *   `curl`이나 Postman을 사용하여 요청을 보냅니다.     *   응답 헤더에 `x-vercel-cache: HIT`가 뜨는지 확인합니다. 개인 페이지에서는 반드시 `MISS` 또는 캐싱되지 않아야 합니다.     *   서로 다른 두 계정(Attacker, Victim)으로 같은 URL에 접속하여 응답 본문이 서로 다른지 확인합니다.

## 결론

Cache Deception 취약점은 코드상의 로직 오류라기보다는 웹의 기본 동작(HTTP 캐싱)을 애플리케이션의 인증 로직과 혼합하여 사용할 때 발생하는 **설계 결함**에 가깝습니다. SvelteKit과 Vercel이라는 편리한 조합을 사용할 때, 우리는 종종 프레임워크가 알아서 최적화해 줄 것이라고 맹신합니다. 하지만 "개인화된 데이터는 절대 공유 캐시에 저장되어서는 안 된다"는 철칙은 개발자가 반드시 인지하고 코드로 강제해야 하는 부분입니다.

보안 전문가로서의 제 인사이트는 **"보안을 위해 성능을 조금 희생하더라도, 개인 정보 관련 경로에서는 캐싱을 `no-store`로 잠그는 것이 현명하다"**는 것입니다. Vercel의 Edge Network는 강력하지만, 잘못된 설정 아래에서는 공격자의 은신처가 될 수 있습니다. 여러분의 SvelteKit 애플리케이션이 사용자의 신뢰를 잃지 않도록, 지금 바로 캐시 헤더를 점검해 보시기 바랍니다.

### 참고자료
- [MDN Web Docs - HTTP Caching](https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching)
- [SvelteKit - Hooks](https://kit.svelte.dev/docs/hooks)
- [Vercel - Caching Documentation](https://vercel.com/docs/concepts/functions/edge-caching)

---

**출처**: [https://news.google.com/rss/articles/CBMivAFBVV95cUxPM19hcDBPVG40SWF5VlZ2MGFQajVEUGtfZTMyaThmRGJPZDIyOWRqNG9iT0dzQjRLcDU5RmFvWUROVjhwWE9qRWtFcGtGZU4wSHZyM0hyekN1blpZeVk3NUpqRmF1bExNbDRCMmQwaEdaOXRMWUhDb3Y2cElTZEVraFJWWVdSZTNwdnN3ek1mN0NUaDRFbm11YW42cmttQWppYWc1cm5jRVdQcnpuejJBOTNwWWtDWkNocUtURg?oc=5](https://news.google.com/rss/articles/CBMivAFBVV95cUxPM19hcDBPVG40SWF5VlZ2MGFQajVEUGtfZTMyaThmRGJPZDIyOWRqNG9iT0dzQjRLcDU5RmFvWUROVjhwWE9qRWtFcGtGZU4wSHZyM0hyekN1blpZeVk3NUpqRmF1bExNbDRCMmQwaEdaOXRMWUhDb3Y2cElTZEVraFJWWVdSZTNwdnN3ek1mN0NUaDRFbm11YW42cmttQWppYWc1cm5jRVdQcnpuejJBOTNwWWtDWkNocUtURg?oc=5)