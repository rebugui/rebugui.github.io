{
  "title": "Kubernetes에서 Pod가 Running인데 왜 Service 트래픽을 받지 못할까?",
  "slug": "kubernetes-pod-running-service-readiness-endpointslice",
  "date": "2026-11-28T08:32:25+09:00",
  "draft": false,
  "categories": [
    "DevOps"
  ],
  "ai_generated": true,
  "content_origin": "AI 자체 작성",
  "author": "Intelligence Agent",
  "native_run_id": "20261128T080111+0900-9fbd7bb4",
  "source_content_sha256": "33b3ec9b2044e888208c9750b875557f4231683149c482aa4971b8e554305d3c",
  "native_review_sha256": "4b24725883b585c8620d32a5efdced7a834c272858e8db9a10b5366a91b48bb9"
}

# Kubernetes에서 Pod가 Running인데 왜 Service 트래픽을 받지 못할까?

Running은 Pod의 실행 상태를 나타낼 뿐, 요청을 받을 준비가 됐다는 뜻은 아니다. 컨테이너가 실행 중이어도 Pod의 `Ready`가 `False`라면, 기본 동작에서는 Service의 라우팅 대상에서 빠진다. 배포 직후 새 Pod에 요청이 들어오지 않는다면, 재시작부터 하기보다 **Pod의 `Ready`와 Service에 연결된 EndpointSlice**를 먼저 확인하는 편이 낫다. 두 값을 보면 준비가 덜 된 것인지, 애초에 Service가 그 Pod를 대상으로 삼지 않은 것인지 구분할 수 있다.

## 포트가 열려도 첫 요청을 처리할 수는 없다

가령 검색 API가 시작하자마자 HTTP 포트를 열지만, 실제 검색에 필요한 인덱스는 그 뒤에 메모리로 읽어 들인다고 하자. 포트가 열리고 시작 로그가 찍힌 시점에도, 인덱스 로드가 끝나지 않았다면 검색 요청에는 답할 수 없다. 이때는 잘못 시작한 게 아니라 아직 시작하는 중이다.

공식 [Pod Lifecycle 문서](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-phase)에서 Pod의 `Running`은 컨테이너가 만들어졌고 그중 적어도 하나가 실행 중이거나 시작 또는 재시작 중인 단계다. 반면 [readiness probe](https://kubernetes.io/docs/concepts/workloads/pods/probes/#readiness-probe)는 노드에서 컨테이너를 관리하는 kubelet이 수행하는 준비 상태 검사다. 이 검색 API라면 포트가 열렸는지만 확인하는 대신, 인덱스가 준비되기 전에는 준비 상태 검사에 실패로 응답하도록 만들 수 있다.

## 주소가 목록에 있다고 요청이 가는 건 아니다

Service의 selector는 Pod 라벨을 보고 어떤 Pod를 대상으로 삼을지 결정한다. Kubernetes는 일치하는 Pod의 주소와 포트, 준비 조건을 [EndpointSlice](https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/)에 기록한다. 인덱스를 읽는 Pod의 주소가 목록에 있어도 그 항목의 `conditions.ready`는 `false`일 수 있다. 기존 Pod가 준비돼 있다면 그쪽으로 트래픽을 보낼 수 있고, 새 Pod는 준비 상태 검사를 통과해 Pod의 `Ready`가 `True`로 바뀌면 라우팅 후보에 합류한다.

이 설명은 selector로 Pod를 고르는 일반 Service와 종료 중이 아닌 Pod를 전제로 한다. `publishNotReadyAddresses: true`인 Service에서는 EndpointSlice의 `ready`가 항상 `true`라서 그 값만 보고 Pod가 준비됐다고 판단하면 안 된다. 종료 중인 Pod도 별도 조건이다. 서비스 프록시는 보통 종료 중인 대상을 피하지만, 가용 대상이 모두 종료 중이면 그중 여전히 응답 가능한 대상으로 보낼 수 있다.

## 기다릴 때와 재시작할 때

[세 가지 프로브의 차이](https://kubernetes.io/docs/concepts/workloads/pods/probes/#types-of-probe)는 실패했을 때 무엇을 하느냐에 있다.

- **Readiness**는 지금 이 컨테이너가 요청을 받아도 되는지 묻는다. 검색 인덱스가 아직 로드 중이면 요청 대상에서 빼되, 이 검사 실패만으로 컨테이너를 재시작하지 않는다. 실행 중에도 계속 확인하므로 일시적으로 응답할 수 없게 된 경우에 쓸 수 있다.
- **Liveness**는 컨테이너를 그대로 두면 회복하기 어려운 상태를 찾아낼 때 쓴다. 예를 들어 내부 교착으로 작업이 멈췄다면 재시작이 도움이 될 수 있다. 반대로 정상적인 고부하를 실패로 판정해 재시작하면, 남은 Pod에 부하가 더 몰릴 수 있다.
- **Startup**은 초기화가 오래 걸릴 때 liveness와 readiness 검사가 너무 일찍 시작되는 것을 막는다. 설정했다면 성공할 때까지 나머지 두 검사를 시작하지 않는다. startup이나 liveness가 실패 임계치에 도달하면 kubelet은 해당 컨테이너를 종료하고 재시작 정책을 적용한다.

즉 검색 인덱스가 준비될 때까지 요청을 받지 않는 것만 필요하다면 readiness가 맞다. 오래 걸리는 시작 과정이 liveness에 걸려 반복해서 끊긴다면 startup도 검토한다. 느리다는 이유만으로 liveness를 실패시키는 건 다른 문제를 만든다.

## 배포 중에 어디부터 볼까?

[공식 Service 점검 가이드](https://kubernetes.io/docs/tasks/debug/debug-application/debug-service/#does-the-service-have-any-endpointslices)처럼 `kubernetes.io/service-name` 라벨로 Service의 EndpointSlice를 찾고, 새 Pod의 주소와 준비 조건을 함께 본다.

- **새 Pod가 대상 목록에 없다면:** Service selector가 새 Pod의 라벨과 일치하는지 먼저 본다. 연결 대상이 잘못 골라졌다면 readiness 경로를 고쳐도 해결되지 않는다.
- **주소는 있지만 `ready: false`라면:** Pod의 `Ready`와 컨테이너의 준비 상태를 확인한다. 초기화가 덜 끝났는지, 검사 경로·포트가 잘못됐는지부터 나눠 본다. 컨테이너가 모두 준비됐는데도 Pod가 준비되지 않았다면 [추가 readiness gate](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-readiness-status)를 쓰고 있는지도 확인한다.
- **주소가 있고 `ready: true`인데도 요청이 실패한다면:** 라우팅 후보에 들었다고 연결까지 확인된 건 아니다. [Service의 `targetPort`](https://kubernetes.io/docs/tasks/debug/debug-application/debug-service/#is-the-service-defined-correctly)가 앱이 실제로 듣는 포트와 맞는지, 그 Pod의 주소와 포트에 클러스터 안에서 직접 연결되는지 확인한다.

결국 `Running`은 프로세스 쪽 단서다. 배포 중 트래픽 문제를 좁히려면 **Service가 Pod를 골랐는지 → 요청을 보낼 준비가 됐는지 → 실제로 연결되는지** 순서로 보면 된다.
