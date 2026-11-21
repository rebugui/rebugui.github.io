{
  "title": "PostgreSQL에서 복합 인덱스가 있는데 왜 ORDER BY에 정렬이 붙을까?",
  "slug": "postgresql-composite-index-order-by-sort",
  "date": "2026-11-22T08:32:41+09:00",
  "draft": false,
  "categories": [
    "IT"
  ],
  "ai_generated": true,
  "content_origin": "AI 자체 작성",
  "author": "Intelligence Agent",
  "native_run_id": "20261122T080123+0900-cb17fcce",
  "source_content_sha256": "b71d5344a0af5d3cbd26f6cabb7bab564cea486b4e357f3267ab239a6ef48736",
  "native_review_sha256": "a3a72359c57d4a5e80d40993ae03d6c6f13918dc7be01a56b7fe502cd5bc2386"
}

# PostgreSQL에서 복합 인덱스가 있는데 왜 ORDER BY에 정렬이 붙을까?

복합 인덱스에 정렬에 필요한 열이 모두 있어도, 그 인덱스를 읽는 순서가 쿼리에서 요청한 순서와 다르면 스캔만으로는 정렬을 대신할 수 없습니다. 가령 `(customer_id, placed_at DESC, id DESC)` B-tree 인덱스는 고객 한 명의 최근 주문을 꺼내는 데 맞습니다. 같은 인덱스를 앞에서부터 읽으면 전체 주문의 최신순이 아니라 고객별 묶음이 나옵니다. 고객 조건 하나를 뺀 쿼리에서 `Sort`가 생겼다면, 먼저 이 차이를 확인해 보세요.

## 고객 한 명의 최신순과 전체 최신순

`orders`에 주문 번호 `id`가 기본 키이고, `customer_id`와 `placed_at`은 `NULL`이 아니라고 가정하겠습니다. 고객 상세 화면에서 최근 주문 20건을 보여 준다면 이런 쿼리를 씁니다.

```sql
SELECT id, placed_at
FROM orders
WHERE customer_id = 42
ORDER BY placed_at DESC, id DESC
LIMIT 20;
```

같은 시각에 주문이 여럿이면 `id DESC`로 표시 순서를 정합니다. `(customer_id, placed_at DESC, id DESC)` B-tree는 먼저 고객 번호로 항목을 묶고, 같은 고객 안에서 주문 시각과 번호 순으로 항목을 배치합니다. `customer_id = 42`가 있으면 그 고객의 구간으로 바로 들어갈 수 있습니다. 그 구간을 앞에서부터 읽으면 요청한 순서와 같으므로, 플래너가 이 경로를 택할 경우 따로 정렬하지 않고 필요한 행을 가져올 수 있습니다. [복합 인덱스 문서](https://www.postgresql.org/docs/18/indexes-multicolumn.html)와 [인덱스 정렬 문서](https://www.postgresql.org/docs/18/indexes-ordering.html)에 나오는 선행 열 조건과 스캔 순서를 이 예에 적용한 것입니다.

운영 화면에서 `WHERE customer_id = 42`만 빼면 전체 주문 중 최근 20건을 요청하게 됩니다. 그런데 인덱스 순서로는 고객 42의 오래된 주문까지 지난 뒤 고객 43의 더 최근 주문을 만날 수 있습니다. 반대로 읽어도 고객 묶음을 통째로 읽는다는 점은 그대로입니다. 전체 최신순을 그대로 읽을 인덱스가 필요하다면 `(placed_at DESC, id DESC)`가 비교할 후보입니다.

## 뒤쪽 열로 찾을 수 있어도 최신순은 아닙니다

첫 열에 조건이 없으면 복합 인덱스를 전혀 못 쓰는 걸까요? [PostgreSQL 18의 skip scan 설명](https://www.postgresql.org/docs/18/indexes-multicolumn.html)은 `(x, y)` 인덱스에 `WHERE y = 7700`만 있는 예를 듭니다. 서로 다른 `x` 값이 적어 인덱스 대부분을 건너뛸 수 있다고 플래너가 판단하면, `x` 값별로 `y = 7700`인 위치를 다시 찾아갈 수 있습니다.

이건 뒤쪽 열의 조건에 맞는 행을 **찾는** 방법입니다. 고객마다 기간 조건에 맞는 주문을 찾아낼 수 있다고 해서 서로 다른 고객의 주문이 시각순으로 합쳐지지는 않습니다. 인덱스가 조건 검색에 쓰이는지와 정렬까지 대신하는지는 따로 판단해야 합니다.

## 실행 계획에서 `Limit` 아래를 보세요

두 쿼리에 `EXPLAIN`을 붙여 `Limit`에 행이 어디서 오는지 비교해 보세요. 원하는 인덱스를 써서 정렬 없이 가져오는 계획이라면 `Limit` 아래에 정렬 노드 없이 해당 인덱스 스캔이 나타날 수 있습니다. `Sort`가 보이면 그 노드 아래에서 어떤 스캔이 행을 공급하는지 봅니다. `LIMIT 20`은 반환할 행 수를 제한할 뿐, 정렬 전에 20건만 읽는다는 뜻은 아닙니다. 반대로 순서가 맞는 인덱스를 이용하면 필요한 행을 얻은 시점에 스캔을 멈출 수 있습니다. 테이블에서 많은 행을 가져오는 쿼리라면 순차 스캔과 정렬이 더 저렴할 수도 있습니다. [PostgreSQL의 `ORDER BY`와 `LIMIT` 설명](https://www.postgresql.org/docs/18/indexes-ordering.html)이 두 경로를 비교합니다.

테스트 환경에서 실제로 얼마나 읽는지 비교하려면 `EXPLAIN (ANALYZE, BUFFERS)`를 써 보세요. `ANALYZE` 옵션은 쿼리를 실제로 실행합니다. 계획의 `rows`는 노드가 내보내는 행 수(예상 또는 실제)이지, 검사한 행의 수가 아닙니다. 노드가 여러 번 실행되면 실제 `rows`는 실행 1회당 평균입니다. `Sort`가 있는 계획에서는 바로 아래 노드의 `rows`와 `loops`를 확인하고, 두 계획에서 버퍼의 `hit`와 `read`도 비교하세요. [실행 계획 읽기 문서](https://www.postgresql.org/docs/18/using-explain.html)에 각 수치의 뜻이 나와 있습니다.

고객별 최근 주문이 느리면 고객 번호가 첫 열인 후보부터 확인하고, 전체 최근 주문이 느리면 주문 시각이 첫 열인 후보를 따로 비교해 보세요. 두 화면에 같은 열이 나온다는 이유로 같은 인덱스를 고르기보다, **어느 범위에서 어떤 순서로 몇 건을 읽는지**부터 적으면 후보가 좁혀집니다.
