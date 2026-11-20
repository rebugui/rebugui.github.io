{
  "title": "개인 기술 블로그를 GitHub Pages로 운영해도 될까: 선택 전에 확인할 조건",
  "slug": "github-pages-personal-blog-selection",
  "date": "2026-11-20T12:40:23.682640+09:00",
  "draft": false,
  "categories": [
    "DevOps"
  ],
  "ai_generated": true,
  "content_origin": "AI 자체 작성",
  "author": "Intelligence Agent",
  "native_run_id": "20261120T120139+0900-94455b2019",
  "source_content_sha256": "eaae707a4273b203c40c4befe5824fd87d02aa06122dafb72bf79ffee7dda1f3",
  "native_review_sha256": "49b5c214713415cc08afe6e551936e23ea6e4ead37308ca5500f6b5535d3c7c8"
}

# 개인 기술 블로그를 GitHub Pages로 운영해도 될까: 선택 전에 확인할 조건

공개할 기술 글을 Markdown과 Git으로 관리하고, 독자는 글과 코드 예제를 읽기만 하면 된다면 GitHub Pages로 시작해도 좋습니다. 반대로 로그인한 독자마다 다른 글을 보여 주거나, 댓글을 직접 받아 저장해야 한다면 Pages만으로는 부족합니다. [GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)는 미리 만들어 둔 파일을 제공하는 호스팅이지, 독자가 접속할 때마다 내 서버 코드를 실행해 주는 서비스는 아니기 때문입니다.

## 글을 올릴 때 한 번, 읽을 때는 파일만

예를 들어 네트워크 공부 노트를 쓰는 블로그를 가정해 봅시다. 글 하나에 `DNS` 태그를 달면, 배포 전에 빌드 도구가 Markdown을 글 본문의 HTML로 바꾸고 태그별 글 목록도 HTML로 만들어 둡니다. 다음 날 누군가 `DNS` 목록을 열면 Pages는 그 파일을 보냅니다. 그때마다 데이터베이스에서 글을 다시 찾거나 HTML을 새로 조립하지 않습니다. 여기서 ‘정적’이라는 말은 글을 수정할 수 없다는 뜻이 아니라, **독자가 요청하기 전에 응답할 파일을 준비해 둔다**는 뜻입니다.

화면까지 가만히 있어야 하는 건 아닙니다. 같은 블로그에서 글 제목과 주소를 담은 검색용 색인을 미리 만들어 두면, 브라우저의 JavaScript가 그 파일을 받아 검색어와 맞는 글을 골라낼 수 있습니다. 반면 한 독자가 단 댓글을 다음 독자도 보게 하려면 누군가 댓글을 받아 저장하고 다시 내줘야 합니다. Pages는 [PHP·Ruby·Python 같은 서버 측 언어의 실행을 지원하지 않으므로](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site#static-site-generators), 그런 댓글은 별도 서비스에 맡기거나 백엔드를 갖춘 호스팅을 선택해야 합니다. 댓글이 부가 기능이라면 글을 굳이 옮길 필요는 없지만, 로그인과 데이터 처리가 블로그의 핵심이라면 처음부터 서버 구성을 함께 보는 편이 낫습니다.

## 원고가 비공개여도 글은 공개될 수 있다

저장소 설정은 **누가 원고를 볼 수 있나**, 사이트 설정은 **누가 게시된 글을 읽을 수 있나**의 문제입니다. [GitHub의 요금제별 지원 범위](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages#who-can-use-this-feature)에 따르면 개인 GitHub Free로 Pages를 쓰려면 공개 저장소가 필요하고, GitHub Pro는 비공개 저장소에서도 게시할 수 있습니다. 그렇다고 Pro에서 비공개 저장소를 선택한 순간 독자에게도 문이 닫히지는 않습니다. [공식 사이트 생성 안내](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site#creating-your-site)는 비공개 저장소에서 배포하더라도 사이트가 인터넷에 공개된다고 경고합니다. 원고 저장소만 숨기고 게시된 글은 공개하려는 경우라면 두 설정의 차이가 오히려 원하는 동작입니다.

[사이트 자체의 접근 제어](https://docs.github.com/en/pages/getting-started-with-github-pages/changing-the-visibility-of-your-github-pages-site#about-access-control-for-github-pages-sites)는 별도 조건입니다. GitHub Enterprise Cloud 조직이 소유한 비공개 또는 내부 저장소에서 게시하는 **프로젝트 사이트**에 적용할 수 있으며, 조직 사이트에는 이 접근 제어를 적용할 수 없습니다. 비공개로 게시된 프로젝트 사이트는 원본 저장소의 읽기 권한이 있는 사람이 볼 수 있습니다. Enterprise Managed Users를 쓰는 환경은 Pages 사이트를 비공개로만 게시할 수 있고, 접근도 엔터프라이즈 구성원으로 제한됩니다. 개인 Pro에서 원고를 숨길 수 있다는 설명을, 특정 독자에게만 글을 보여 줄 수 있다는 뜻으로 읽으면 안 됩니다.

## 배포 방법은 글을 만드는 방식에 맞춘다

별도 전처리가 없고 Jekyll 기본 흐름이 맞으면 브랜치 배포부터 검토할 만합니다. [소스 브랜치에서 게시할 때는 기본으로 Jekyll을 사용합니다](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site#static-site-generators). 반대로 다른 생성기를 쓰거나 글 목록과 검색 색인을 만드는 단계를 배포에 넣어야 한다면, [커스텀 GitHub Actions 워크플로](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)에서 빌드한 파일 묶음(아티팩트)을 올리고 배포할 수 있습니다. 이때 먼저 확인할 것은 배포용 파일 묶음입니다. [사이트의 진입 파일은 그 묶음의 최상위에 있어야 합니다](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site#creating-your-site). Actions에서 실행되는 것은 배포 전 작업이지, 독자가 사이트를 열 때 동작하는 서버가 아닙니다.

## 큰 파일이 많다면 글과 다운로드를 나눈다

텍스트보다 실습 영상이나 데이터셋이 큰 블로그라면, 저장소 크기만 보고 판단하지 말고 실제로 게시할 파일을 보세요. [공식 사용 한도](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits#usage-limits)는 **게시된 사이트**를 최대 1 GB로 제한하고, 배포가 10분을 넘으면 타임아웃된다고 명시합니다. 저장소의 1 GB 권장치와는 다른 기준입니다. 월 100 GB 대역폭은 소프트 한도이므로 대용량 다운로드가 잦을 것으로 예상한다면 글은 Pages에 두고 파일 배포처는 따로 두는 편이 낫습니다. 시간당 10회 빌드도 소프트 한도이며, 커스텀 Actions로 빌드하고 게시할 때는 이 빌드 횟수 제한이 적용되지 않습니다. 그 예외가 사이트 크기나 대역폭, 배포 시간까지 풀어 주는 건 아닙니다.

용도 자체도 확인해야 합니다. 같은 [사용 한도 안내](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits#usage-limits)는 온라인 사업이나 전자상거래 사이트, 상업 거래를 돕거나 상용 SaaS를 제공하는 것이 주목적인 사이트를 Pages의 용도로 허용하지 않습니다. 결제나 비밀번호처럼 민감한 정보를 보내는 용도로도 쓰지 말라고 합니다. 페이지를 기술적으로 만들 수 있는지와 그 용도로 운영해도 되는지는 다른 문제입니다.

결정이 애매하다면 대표 글 한 편을 골라 글 본문, 이미지, 목록이 담긴 배포 파일을 만들어 보세요. 게시 전에 결과물에 초안이나 공개하면 안 되는 첨부가 섞였는지 확인합니다. 그 파일을 모두 공개해도 괜찮고 독자가 글과 예제를 읽는 데 별도 서버가 필요 없다면 Pages로 시작해도 됩니다. 읽을 사람을 제한해야 한다면 접근 제어부터, 독자의 입력을 받아 저장해야 한다면 그 데이터를 처리할 백엔드부터 정하세요.

_이 글은 AI가 작성한 초안입니다._


이 글은 AI를 사용해 생성되었습니다.
