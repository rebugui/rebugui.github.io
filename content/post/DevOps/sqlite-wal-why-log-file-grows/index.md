{
  "title": "SQLite WAL에서 조회는 되는데 로그 파일은 왜 커질까?",
  "slug": "sqlite-wal-why-log-file-grows",
  "date": "2026-11-20T04:25:59.246802+00:00",
  "draft": false,
  "categories": [
    "DevOps"
  ],
  "ai_generated": true,
  "content_origin": "AI 자체 작성",
  "author": "Intelligence Agent",
  "native_run_id": "20261120T125452+0900-445fb9c2",
  "source_content_sha256": "cfeb0dbf552836b92d8563746e9852d65864ca85d197ed0849fdc2e3052e9d0f",
  "native_review_sha256": "02b59f189d74adf50af1fbe99bf44ead61d6dcbb189bbe6e7a5cf7fd50cc0843"
}

# SQLite WAL에서 조회는 되는데 로그 파일은 왜 커질까?

SQLite의 WAL 모드에서는 CSV를 내보내는 동안에도 다른 연결이 데이터를 저장할 수 있다. 그런데 내보내기가 같은 읽기 트랜잭션을 오래 붙들고 있으면, SQLite는 그 조회에 필요한 이전 상태를 보존하느라 로그를 끝까지 정리하지 못할 수 있다. 그 사이 쓰기가 계속되면 `-wal` 파일이 커진다. 조회와 저장이 동시에 된다는 말이 로그까지 제때 정리된다는 뜻은 아니다. [SQLite의 WAL 동시성 설명](https://sqlite.org/wal.html#concurrency)

## 커밋과 본 파일 반영은 다른 일이다

기본 롤백 저널 방식에서는 바뀌기 전 내용을 저널에 보관하고 데이터베이스 본 파일을 수정한다. 문제가 생기면 저널을 이용해 원래 상태로 되돌린다. WAL(Write-Ahead Log) 모드는 반대로 바뀐 페이지를 별도 로그에 먼저 붙인다. 커밋 표시도 여기에 남기므로, 본 파일에 아직 반영되지 않았더라도 새 읽기 트랜잭션은 커밋된 값을 읽을 수 있다. 나중에 로그의 변경분을 본 파일로 옮기는 일이 **체크포인트**다. [WAL의 동작 방식](https://sqlite.org/wal.html#how_wal_works)

읽기 트랜잭션은 시작할 때 마지막으로 유효한 커밋의 위치를 기억한다. 페이지가 필요하면 그 경계까지의 WAL에서 가장 최근 사본을 찾고, 없으면 본 파일에서 읽는다. 이렇게 한 번 정한 경계를 유지하면 첫 행을 읽을 때와 마지막 행을 읽을 때 서로 다른 시점의 데이터가 섞이지 않는다. 이를 **스냅샷 격리**라고 한다. [WAL의 읽기 경계](https://sqlite.org/wal.html#concurrency) · [SQLite의 격리 설명](https://sqlite.org/isolation.html)

같은 서버에서 두 연결이 주문 DB를 쓴다고 가정해 보자. 연결 A는 `BEGIN` 뒤 첫 `SELECT`로 주문 내역을 읽기 시작한다. 연결 B는 주문 상태를 ‘접수’에서 ‘발송’으로 바꾸고 커밋한다. A가 같은 트랜잭션에서 상태를 다시 조회하면 여전히 ‘접수’가 보인다. A가 읽기 트랜잭션을 끝내고 새로 조회하면 ‘발송’이 보인다. 여기서 기준은 기본 `BEGIN`을 호출한 시점이 아니라 첫 조회로 읽기 트랜잭션이 시작된 시점이다. [격리 문서의 두 연결 예제](https://sqlite.org/isolation.html) · [트랜잭션 시작 규칙](https://sqlite.org/lang_transaction.html)

## 파일이 그대로인 것과 계속 커지는 건 다르다

체크포인트는 읽기가 진행 중이어도 가능한 분량을 본 파일에 반영한다. 다만 읽는 연결의 경계를 넘어 본 파일을 덮어쓰면 그 연결이 아직 읽어야 할 페이지가 바뀔 수 있다. 그래서 체크포인트는 안전한 지점에서 멈춘다. 내보내기가 CSV를 한 줄씩 만들면서 조회 커서를 계속 열어 두고, 그동안 다른 요청이 주문을 계속 저장한다면 WAL에 변경분이 쌓일 수 있다. [WAL 파일이 커지는 조건](https://sqlite.org/wal.html#avoiding_excessively_large_wal_files)

파일 크기를 한 번 재는 것만으로는 정체를 알 수 없다. SQLite는 일반적인 체크포인트 뒤에 파일을 줄이는 대신, 조건이 맞으면 앞부분부터 다시 쓴다. 파일이 크더라도 크기가 더 늘지 않는다면 이미 확보한 공간을 재사용 중일 수 있다. 쓰기가 이어질 때 계속 커진다면 **읽기 트랜잭션이 끝나는 시각**을 기록하고, 그 전후로 파일 크기 추이가 달라지는지 보자. 크기가 당장 줄지 않더라도 증가가 멈추는지 볼 수 있다. 명시적으로 `BEGIN`을 했다면 커서만 닫는 것과 트랜잭션을 끝내는 것은 다르다. 반대로 명시적 `BEGIN`이 없어도 마지막 SQL 문이 아직 끝나지 않았다면 암묵적 트랜잭션이 남아 있을 수 있다. 긴 읽기가 없다면 큰 쓰기 트랜잭션이나 자동 체크포인트 설정도 확인할 만하다. [WAL 파일 재사용과 증가 원인](https://sqlite.org/wal.html#avoiding_excessively_large_wal_files) · [암묵적·명시적 트랜잭션](https://sqlite.org/lang_transaction.html)

## WAL로 줄일 수 있는 대기인지부터 보자

같은 서버에서 조회와 저장이 자주 겹친다면 WAL을 검토할 만하다. 반대로 저장 요청끼리 줄을 서는 게 문제라면 WAL로 바꿔도 한 번에 한 연결만 쓸 수 있다. 그때는 먼저 쓰기 트랜잭션이 얼마나 오래 열려 있는지 살펴보자. WAL에서도 일부 상황에서는 조회가 `SQLITE_BUSY`를 반환할 수 있으므로 잠금 오류 처리를 없애지는 않는다. [동시 쓰기 제약](https://sqlite.org/wal.html#concurrency) · [WAL의 `SQLITE_BUSY` 예외](https://sqlite.org/wal.html#sometimes_queries_return_sqlite_busy_in_wal_mode)

운영 방식도 함께 확인해야 한다. 여러 서버가 네트워크 파일시스템에서 같은 SQLite 파일을 직접 여는 구성에는 WAL을 적용하지 않는다. 또 WAL이 남아 있는 상태에서 백업한다고 본 파일만 떼어 복사하면 이미 커밋한 변경이 빠질 수 있다. 단일 서버에서 읽기와 쓰기가 겹쳐 생기는 대기를 줄이는 것이 목표라면, 적용 전후에 저장 대기와 `-wal` 크기 추이를 함께 보고 긴 조회가 언제 끝나는지 기록하는 편이 설정 효과를 판단하기 쉽다. [WAL 적용 조건](https://sqlite.org/wal.html#overview) · [WAL 파일과 복사 주의사항](https://sqlite.org/wal.html#the_wal_file)
