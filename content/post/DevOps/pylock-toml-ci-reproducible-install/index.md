{
  "title": "pylock.toml을 복사하면 CI에도 같은 패키지가 설치될까?",
  "slug": "pylock-toml-ci-reproducible-install",
  "date": "2026-11-23T08:33:42.611276+09:00",
  "draft": false,
  "categories": [
    "DevOps"
  ],
  "ai_generated": true,
  "content_origin": "AI 자체 작성",
  "author": "Intelligence Agent",
  "native_run_id": "20261123T080128+0900-52bb75cc",
  "source_content_sha256": "2a42c9c5018cc447de33b44114a788785b91da219ef25a7548e6857f59c96217",
  "native_review_sha256": "e9277ee591487c3b8aa3ac144b527f5487b434e5e9234350beea91087f6a5b9c"
}

# pylock.toml을 복사하면 CI에도 같은 패키지가 설치될까?

pylock.toml을 저장소에 넣는 것만으로는 부족하다. 파일이 CI의 Python 버전과 플랫폼을 대상으로 만들어졌고, CI의 설치 도구가 그 형식을 읽어야 한다. 조건을 모두 충족해도 macOS와 Linux의 패키지 목록이 꼭 같을 필요는 없다. 잠금 파일은 다른 환경에 같은 목록을 강제하는 대신, **각 환경에서 무엇을 설치할지** 미리 기록할 수 있기 때문이다.

## 파일을 거부하는 것과 패키지를 건너뛰는 것은 다르다

프로젝트의 의존성 선언이 ‘어떤 패키지가 필요하고 어느 버전까지 허용하는가’를 적는 곳이라면, 잠금 파일은 그 요구를 풀어서 얻은 설치 후보를 기록하는 곳이다. [PyPA의 `pylock.toml` 규격](https://packaging.python.org/en/latest/specifications/pylock-toml/)은 파일 전체가 맞는 환경과 패키지 하나가 필요한 환경을 따로 표현한다.

- 파일의 `requires-python`은 대상 Python 버전 조건을, `environments`는 파일과 호환되는 환경 조건을 표현한다. 지정된 Python 조건을 충족하지 못하거나, 지정된 환경 조건 중 어느 것도 맞지 않으면 규격상 설치 오류다.
- 패키지 항목의 `packages.marker`는 그 패키지를 설치할 조건이다. 조건이 거짓이면 그 항목을 건너뛴다. 파일 전체가 잘못됐다는 뜻은 아니다.

가령 macOS와 Linux를 모두 대상으로 잠근 가상의 프로젝트에서, macOS에서만 쓰는 패키지에 해당 조건을 붙였다고 하자. Linux CI에 그 패키지가 없는 건 정상이다. 반대로 파일 전체의 `environments`가 macOS만 허용한다면 Linux에서 설치가 거부되는 게 맞다. 두 경우를 구분하면 패키지가 빠졌다고 의존성 선언부터 고치거나, 설치가 거부됐다고 기존 잠금을 무시하고 새 버전을 고르는 일을 피할 수 있다.

## 버전이 같아도 내려받는 파일은 다를 수 있다

패키지 이름과 버전이 같아도 운영체제별로 다른 wheel을 설치할 수 있다. wheel은 설치할 수 있게 꾸린 배포 파일이다. 예를 들어 한 패키지 버전에 macOS용 wheel과 Linux용 wheel이 둘 다 잠겨 있다면, 두 환경의 버전 목록이 같아도 내려받는 파일은 다르다.

[규격의 설치 절](https://packaging.python.org/en/latest/specifications/pylock-toml/#installation)은 알맞은 wheel을 찾고 파일을 가져와 검증하는 단계를 구분한다. 호환 wheel 항목이 없으면 잠금 파일에 있는 소스 배포본(sdist)으로 넘어가 빌드할 수 있다. 그마저 없다면 오류다. 반면 호환 wheel을 골랐는데 다운로드에 실패한 상황은 별개다. 내려받을 수 있는 파일에 맞춰 wheel 선택을 바꾸라는 규칙이 아니다. 소스 배포본의 해시가 일치하더라도, 그 해시가 서로 다른 환경에서 빌드한 결과물까지 같다고 보장하는 것은 아니다.

## 만드는 명령과 읽는 명령을 따로 확인한다

[pip의 `pip lock` 문서](https://pip.pypa.io/en/stable/cli/pip_lock/)는 이 명령을 실험 기능으로 표시하고, 생성한 파일의 유효성을 실행한 Python 버전과 플랫폼에서만 보장한다. macOS에서 만든 파일이 Linux에서 반드시 실패한다는 뜻은 아니다. 다만 파일 이름만 보고 Linux CI에서도 유효하다고 가정할 근거는 없다. 설치 쪽은 별도로 봐야 한다. [pip 26.3의 `pip install` 문서](https://pip.pypa.io/en/stable/cli/pip_install/)는 `-r`로 `pylock.toml`을 읽는 경로를 설명하고, 이 형식 지원 역시 실험적이라고 명시한다. CI 이미지의 pip 버전이 다르면 그 버전의 문서를 확인한다.

uv로 프로젝트를 관리한다면 파일 이름만 바꿔서는 안 된다. [uv 문서](https://docs.astral.sh/uv/concepts/projects/layout/)에 따르면 프로젝트 인터페이스는 uv 전용 교차 플랫폼 잠금 파일인 `uv.lock`을 사용한다. 다른 설치 흐름에 표준 형식이 필요하면 `uv export -o pylock.toml`로 내보낼 수 있다. uv에서 그 표준 파일을 적용하는 문서상 경로는 `uv pip sync pylock.toml`이다. 프로젝트의 `uv sync`가 `pylock.toml`을 대신 쓴다는 뜻은 아니다.

## CI에는 어떤 파일을 넘길까?

배포 대상이 Linux 한 곳이라면, 우선 그 대상과 같은 Python 버전·플랫폼에서 잠금 파일을 만들고 빈 가상 환경에 적용해 보는 편이 단순하다. macOS 개발 환경까지 한 파일로 관리하려면, 잠금 생성 도구가 두 대상을 다룰 수 있는지 확인하고 CI에서 두 환경을 각각 검증한다. 그게 어렵다면 대상별 잠금 파일을 유지하는 편이 명확하다. 팀 전체가 uv 프로젝트 인터페이스만 쓴다면 표준 파일을 하나 더 관리할 이유부터 따져 본다.

설치가 어긋났을 때는 **CI의 Python·플랫폼이 파일 범위에 드는가 → 설치 도구가 그 파일을 읽는가 → 필요한 패키지와 호환 배포 파일이 잠겨 있는가** 순서로 확인하면 된다. 첫 번째 문제에 패키지 버전을 바꿔 봐야 해결되지 않고, 두 번째 문제에 잠금을 다시 만들어 봐야 같은 도구는 여전히 파일을 못 읽는다.
