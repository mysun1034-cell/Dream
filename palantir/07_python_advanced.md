# Python 심화: 문제 해결 알고리즘과 운영 가능한 서비스

**구성:** 10강 · 연습문제 20개 · DS/FDSE 역할별 적용 과제

Python 중급과 SQL 중급을 선행합니다. 알고리즘, 동시성, 서비스 경계, 재처리와 운영을 배웁니다. 짧은 예제를 대규모 운영 시스템 전체와 혼동하지 마세요.

**사용 방법:** 모든 명령은 압축을 푼 폴더의 `lab/`에서 실행합니다. 아직 환경을 만들지 않았다면 [환경과 데이터 사전](#book-02)을 먼저 읽으세요. 각 강의의 설명형 해설은 본문에, 연습문제 정답은 [해설집](#book-09)에 있습니다.

## 강의 지도

- [PY-A01 시간 복잡도·해시 조회·직접 JOIN 구현: 느림을 구조로 고치기](#py-a01)
- [PY-A02 그래프·BFS·방문 집합: 영향 범위와 의존성 찾기](#py-a02)
- [PY-A03 정렬·힙·구간 겹침: 최소 필요 인력 계산하기](#py-a03)
- [PY-A04 async·await·이벤트 루프·동시성 제한: 누가 기다리고 누가 일하는가](#py-a04)
- [PY-A05 ETL·멱등성·격리·증분 처리: 두 번 돌려도 망가지지 않는 배치](#py-a05)
- [PY-A06 FastAPI·입력 검증·권한·페이지 조회: 분석을 서비스로](#py-a06)
- [PY-A07 레이어·Protocol·의존성 주입: 바꾸기 쉬운 구조 만들기](#py-a07)
- [PY-A08 프로파일링·메모리·CPU와 I/O: 추측 대신 측정하기](#py-a08)
- [PY-A09 로그·지표·추적·보안: 장애가 났을 때 설명 가능한 서비스](#py-a09)
- [PY-A10 분산 집계·재결합·Foundry 연결 사고: 로컬에서 플랫폼으로](#py-a10)

---

<a id="py-a01"></a>
## PY-A01 · 시간 복잡도·해시 조회·직접 JOIN 구현: 느림을 구조로 고치기

**학습 목표:** 중첩 반복을 키 기반 조회로 바꾸고 계산 비용을 설명한다.

**실행 구분:** Python 3.12 이상 대상; 제작 환경 Python 3.13.5에서 실행 확인

### 1. 용어부터 이해하기

시간 복잡도는 입력 크기가 커질 때 연산량이 어떻게 늘어나는지 표현한다. O(n)은 입력에 비례, O(nm)은 두 크기의 곱에 비례한다. 해시 기반 딕셔너리는 일반적인 조건에서 평균적으로 빠른 키 조회를 제공한다.

### 2. 비유로 잡는 그림

방문마다 직원 명부를 처음부터 다시 훑는 대신, 직원 번호별 색인을 한 번 만들어 두는 방식이다.

### 3. 원리와 업무에서의 의미

방문 n건마다 직원 m명을 순회하면 비교가 대략 n×m번 필요하다. 직원 ID→직원 행 딕셔너리를 만든 뒤 방문을 한 번 순회하면 평균적인 비용은 O(m+n)이고 색인 메모리는 O(m)이다. 출력까지 고려하면 결과 행 수의 비용도 들어간다.

하지만 딕셔너리를 만드는 것만으로 SQL JOIN을 완전히 구현한 것은 아니다. 오른쪽 키가 중복이면 뒤의 행이 앞의 행을 덮어쓴다. N:1을 전제로 한다면 고유성을 먼저 검증하고, N:N이 필요하면 키마다 행 리스트를 저장해야 한다.

이 강의는 담당자가 배정된 방문만 연결하는 INNER JOIN을 구현한다. 예정 방문의 worker_id는 빈 문자열이므로 매칭되지 않는다. 알고리즘 문제에서도 입력 가정·중복·누락·시간·메모리를 먼저 설명한 뒤 코드를 쓴다.

### 4. 따라 하는 예제

```bash
python -m examples.PY_A01
```

```python
from course_lib import read_csv

workers = read_csv("workers")
visits = read_csv("visits")
by_id = {}
for worker in workers:
    key = worker["worker_id"]
    if key in by_id:
        raise ValueError("duplicate worker key")
    by_id[key] = worker
joined = []
for visit in visits:
    worker = by_id.get(visit["worker_id"])
    if worker is not None:
        joined.append((int(visit["visit_id"]), worker["worker_name"]))
print(len(joined))
print(joined[:3])
```

### 5. 결과와 코드 해설

```text
21
[(1, 'Worker-01'), (2, 'Worker-02'), (3, 'Worker-01')]
```

색인을 만드는 반복과 방문을 연결하는 반복이 분리되어 있다. 매칭된 21행을 출력한다. 직원 이름이 None인지가 아니라 조회된 직원 객체가 존재하는지를 검사한다. 자료를 SQL에서 이미 연결할 수 있다면 DB에서 처리하는 것이 더 적절할 수 있으므로 네트워크·메모리 비용까지 비교한다.

### 6. 자주 하는 실수

Big-O만 보고 실제 성능을 단정하지 않는다. 작은 입력에서는 상수 비용, 큰 입력에서는 메모리·입출력·캐시·데이터 분포가 중요하다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** 빠른 시제품과 확장 가능한 구현 사이의 투자 우선순위를 설명한다.

**FDSE 관점:** 시간·공간 복잡도, 키 계약, 출력 grain을 명시하며 구현한다.

### 8. 직접 풀어 보기

**PY-A01-1. 직원 ID 중복을 허용하는 N:N 연결의 색인은 어떤 구조여야 하는가?**

힌트: 키 하나가 여러 행을 가리켜야 한다.

[풀이 확인](#py-a01-1)

**PY-A01-2. 방문이 100만 건이고 직원이 1000명이면 단순 중첩 반복의 비교 규모는?**

힌트: n×m과 n+m을 비교한다.

[풀이 확인](#py-a01-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://docs.python.org/3.12/library/stdtypes.html#mapping-types-dict)

---

<a id="py-a02"></a>
## PY-A02 · 그래프·BFS·방문 집합: 영향 범위와 의존성 찾기

**학습 목표:** 데이터 의존성을 그래프로 표현하고 영향 범위를 순회한다.

**실행 구분:** Python 3.12 이상 대상; 제작 환경 Python 3.13.5에서 실행 확인

### 1. 용어부터 이해하기

그래프(graph)는 정점과 연결선으로 관계를 표현한다. BFS는 가까운 정점부터 넓게 탐색하는 방식이다. 큐(queue)는 먼저 들어온 항목을 먼저 꺼낸다. 방문 집합은 반복 탐색과 순환을 막는다.

### 2. 비유로 잡는 그림

고객 데이터가 잘못되었을 때 영향을 받는 방문·청구·입금 보고서를 연결 지도로 따라간다.

### 3. 원리와 업무에서의 의미

테이블 사이의 의존성, 사용자 작업 단계, 시스템 연결은 그래프로 모델링할 수 있다. 이 강의는 “고객 → 방문 → 청구 → 입금 보고”라는 학습용 의존성을 사용한다. 실제 외래키 관계와 데이터 파이프라인 의존성은 같은 뜻이 아니므로 어떤 그래프인지 먼저 정한다.

BFS는 deque에 시작 정점을 넣고 앞에서 하나씩 꺼낸다. 새로 발견한 이웃은 큐 뒤에 넣는다. seen은 큐에 넣는 순간 표시해야 같은 정점이 여러 경로에서 반복 추가되는 것을 줄일 수 있다.

인접 리스트 표현에서 모든 관련 정점과 간선을 한 번씩 보면 O(V+E)다. BFS는 가중치가 없는 그래프에서 최단 간선 수 경로를 찾는 데 적합하다. 이동 시간처럼 가중치가 있으면 BFS만으로 최단 시간을 보장하지 않는다.

### 4. 따라 하는 예제

```bash
python -m examples.PY_A02
```

```python
from collections import deque

def affected(graph: dict[str, list[str]], start: str) -> list[str]:
    if start not in graph:
        raise ValueError("unknown start")
    queue = deque([start])
    seen = {start}
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph.get(node, []):
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    return order

graph = {"clients": ["visits"], "workers": ["visits"],
         "visits": ["invoices"], "invoices": ["payments"], "payments": []}
print(affected(graph, "clients"))
```

### 5. 결과와 코드 해설

```text
['clients', 'visits', 'invoices', 'payments']
```

순회 결과는 clients,visits,invoices,payments다. workers는 clients에서 도달하는 하위 의존성이 아니므로 나오지 않는다. 영향 분석의 방향이 중요하다. 시작 데이터의 출처를 찾는 역방향 탐색과 결과물의 영향을 찾는 순방향 탐색은 다르다.

### 6. 자주 하는 실수

관계가 있다는 이유만으로 데이터 접근이 허용되는 것은 아니다. 그래프 탐색에서도 사용자 권한과 민감 정보 범위를 지켜야 한다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** 고객 문제를 관계·흐름·의존성으로 설명한다.

**FDSE 관점:** 순환·분리된 정점·다중 경로·경로 복원을 테스트한다.

### 8. 직접 풀어 보기

**PY-A02-1. payments에서 clients로 되돌아가는 간선을 추가하면 무한 반복하는가?**

힌트: seen이 이미 방문한 정점을 막는다.

[풀이 확인](#py-a02-1)

**PY-A02-2. 최단 경로 자체를 돌려주려면 무엇을 추가로 저장해야 하는가?**

힌트: 각 정점에 처음 도달한 직전 정점을 기록한다.

[풀이 확인](#py-a02-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://docs.python.org/3.12/library/collections.html#collections.deque)

---

<a id="py-a03"></a>
## PY-A03 · 정렬·힙·구간 겹침: 최소 필요 인력 계산하기

**학습 목표:** 시간 구간이 겹치는 최대 개수를 계산하고 모델의 한계를 설명한다.

**실행 구분:** Python 3.12 이상 대상; 제작 환경 Python 3.13.5에서 실행 확인

### 1. 용어부터 이해하기

힙(heap)은 최소값 또는 최대값을 효율적으로 꺼내는 자료구조다. 구간(interval)은 시작과 끝 사이의 범위다. 탐욕법(greedy)은 현재 단계의 선택 규칙을 반복하는 방식이다.

### 2. 비유로 잡는 그림

방문을 시작 시간순으로 보면서 이미 끝난 업무의 자리를 비우고, 동시에 필요한 자리가 최대 몇 개인지 센다.

### 3. 원리와 업무에서의 의미

모든 직원의 자격이 같고 이동 시간이 없으며 한 방문에 직원 한 명이 필요하다고 단순화하면, 최소 필요 인력은 동시에 겹치는 방문의 최대 개수와 같다. 이는 실제 현장 배정 문제 전체를 해결한 것이 아니라 명시적인 단순 모델의 결과다.

시작순으로 정렬하고 진행 중인 방문의 종료 시각을 최소 힙에 넣는다. 다음 방문 시작 전에 끝난 모든 항목을 제거하고 새 종료 시각을 추가한다. 힙 크기의 최대값이 동시에 진행되는 최대 방문 수다.

구간은 [start,end)로 취급하므로 60분에 끝난 업무와 60분에 시작한 업무는 겹치지 않는다. 이동 시간·직원 자격·휴식·우선순위·공정성·사용자 수정은 실제 배정 제약으로 추가되어야 한다. 이 조건이 달라지면 단순 최적성 주장도 성립하지 않을 수 있다.

### 4. 따라 하는 예제

```bash
python -m examples.PY_A03
```

```python
import heapq

def required_workers(intervals: list[tuple[int, int]]) -> int:
    if any(end <= start for start, end in intervals):
        raise ValueError("each interval must have positive duration")
    active_ends = []
    peak = 0
    for start, end in sorted(intervals):
        while active_ends and active_ends[0] <= start:
            heapq.heappop(active_ends)
        heapq.heappush(active_ends, end)
        peak = max(peak, len(active_ends))
    return peak

print(required_workers([(0, 60), (30, 90), (60, 120)]))
print(required_workers([]))
```

### 5. 결과와 코드 해설

```text
2
0
```

첫 방문은 1명, 30분에는 두 방문이 겹쳐 2명, 60분에는 첫 방문이 끝나 다시 2명으로 유지된다. 결과는 2다. 빈 입력은 0이다. 정렬과 힙 연산으로 시간 O(n log n), 최악의 추가 공간 O(n)이다.

### 6. 자주 하는 실수

실제 배정 최적화라고 과장하지 않는다. 인원 하한을 구하는 단순 모델과 자격·이동·교대 제약이 있는 배정은 다르다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** 어떤 단순화가 의사결정에 허용되는지 사용자와 합의한다.

**FDSE 관점:** 구간 경계·빈 입력·잘못된 시간·성능·추가 제약을 테스트한다.

### 8. 직접 풀어 보기

**PY-A03-1. [(0,10),(10,20),(20,30)]의 필요 인력은?**

힌트: 끝 시각과 시작 시각이 같으면 이전 업무를 제거한다.

[풀이 확인](#py-a03-1)

**PY-A03-2. 직원마다 자격이 다르면 위 결과 2명이 충분함을 보장하는가?**

힌트: 동시 방문 수 외의 제약을 찾는다.

[풀이 확인](#py-a03-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://docs.python.org/3.12/library/heapq.html)

---

<a id="py-a04"></a>
## PY-A04 · async·await·이벤트 루프·동시성 제한: 누가 기다리고 누가 일하는가

**학습 목표:** 대기 중인 코루틴과 실행 가능한 다른 작업을 구분한다.

**실행 구분:** Python 3.12 이상 대상; 제작 환경 Python 3.13.5에서 실행 확인

### 1. 용어부터 이해하기

코루틴(coroutine)은 중단·재개 가능한 비동기 작업이다. 이벤트 루프(event loop)는 실행 가능한 작업과 입출력 완료를 조정한다. Task는 스케줄링된 코루틴이다. 세마포어는 동시에 들어갈 수 있는 작업 수를 제한한다.

### 2. 비유로 잡는 그림

요리사가 타이머를 걸어 둔 냄비 앞에서 멈춰 서는 대신 다른 준비된 요리를 한다. 냄비별 절차는 기다리고 조정자는 다른 일을 선택한다.

### 3. 원리와 업무에서의 의미

async def를 붙였다고 함수가 자동으로 백그라운드에서 병렬 실행되는 것은 아니다. 함수를 호출하면 코루틴 객체가 만들어지고, await하거나 Task로 스케줄링해야 진행한다. await에서 실제 기다림이 필요할 때 현재 코루틴은 중단되고 이벤트 루프가 실행 가능한 다른 작업을 진행시킬 수 있다.

`await a(); await b()`는 보통 a가 끝난 뒤 b를 시작하는 순차 흐름이다. 여러 코루틴을 TaskGroup에 등록하면 함께 진행할 수 있다. 하나의 이벤트 루프 스레드에서 동시에 Python 코드를 여러 줄 실행한다는 뜻이 아니라, 기다림 사이에 실행을 번갈아 하는 것이다.

비동기 함수 안에서 time.sleep이나 동기 DB 호출 같은 blocking 작업을 직접 오래 실행하면 이벤트 루프가 막힐 수 있다. 비동기 드라이버, 적절한 스레드 위임, 작업 분리를 고려한다. 동시 요청 수를 무한히 늘리지 말고 서비스 용량·타임아웃·취소를 함께 설계한다.

### 4. 따라 하는 예제

```bash
python -m examples.PY_A04
```

```python
import asyncio

async def fetch_one(visit_id: int, gate: asyncio.Semaphore) -> int:
    async with gate:
        await asyncio.sleep(0.01)  # 외부 대기를 흉내 냄; 실제 HTTP 호출 아님
        return visit_id * 10

async def main() -> None:
    gate = asyncio.Semaphore(2)
    async with asyncio.TaskGroup() as group:
        tasks = [group.create_task(fetch_one(i, gate)) for i in [1, 2, 3]]
    print([task.result() for task in tasks])

if __name__ == "__main__":
    asyncio.run(main())
```

### 5. 결과와 코드 해설

```text
[10, 20, 30]
```

main은 세 작업을 등록한다. 세마포어 때문에 fetch_one의 내부 대기 구간에는 최대 두 작업만 들어간다. 한 작업이 기다리는 동안 다른 준비된 작업이 진행된다. TaskGroup 블록을 정상적으로 벗어나면 작업들이 끝났으므로 결과를 읽을 수 있다. 출력은 입력 순서로 [10,20,30]이다.

### 6. 자주 하는 실수

Notebook처럼 이미 이벤트 루프가 실행 중인 환경에서 asyncio.run을 중첩하면 오류가 날 수 있다. 스크립트는 asyncio.run, 해당 환경의 최상위 비동기 지원에서는 await main()을 사용한다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** 동시 요청으로 처리량을 높일 때 고객 시스템에 가하는 부담을 평가한다.

**FDSE 관점:** 대기/CPU 작업 구분, 동시성 상한, 오류 전파, 취소와 정리를 구현한다.

### 8. 직접 풀어 보기

**PY-A04-1. 세마포어 값을 1로 바꾸면 어떤 점이 달라지는가?**

힌트: 동시에 대기 구간에 들어가는 작업 수를 본다.

[풀이 확인](#py-a04-1)

**PY-A04-2. await은 누가 기다린다는 뜻인지 두 문장으로 설명하라.**

힌트: 현재 코루틴과 이벤트 루프를 분리해 말한다.

[풀이 확인](#py-a04-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://docs.python.org/3.12/library/asyncio-task.html)
- [공식 문서 2](https://docs.python.org/3.12/library/asyncio-sync.html)
- [공식 문서 3](https://fastapi.tiangolo.com/async/)

---

<a id="py-a05"></a>
## PY-A05 · ETL·멱등성·격리·증분 처리: 두 번 돌려도 망가지지 않는 배치

**학습 목표:** 원본 이벤트를 검증하고 재실행 시 중복 상태를 만들지 않는다.

**실행 구분:** Python 3.12 이상 대상; 제작 환경 Python 3.13.5에서 실행 확인

### 1. 용어부터 이해하기

ETL은 추출·변환·적재다. 멱등성(idempotency)은 같은 작업을 다시 적용해도 의도한 최종 효과가 반복 증식하지 않는 성질이다. 격리(quarantine)는 잘못된 행을 이유와 함께 따로 보관하는 처리다. 워터마크는 처리한 범위의 경계다.

### 2. 비유로 잡는 그림

같은 수정 신청서가 두 번 와도 고객 상태를 두 개 만들지 않고, 잘못된 신청서는 보완함에 남긴다.

### 3. 원리와 업무에서의 의미

배치는 실패한 지점에서 다시 실행될 수 있다. INSERT만 반복하면 같은 방문의 상태가 중복된다. 제공된 etl.py는 visit_id를 기본키로 사용하고 더 최신 updated_at 또는 동률 우선 이벤트만 갱신한다. 적재와 격리를 한 트랜잭션으로 처리한다.

원본 6행 중 정상 입력은 3행, 잘못된 ID·상태·시각은 각각 1행으로 총 3행이다. 정상 세 행에는 같은 방문 101의 수정이 있어 최종 상태는 2행이다. 재실행해도 현재 상태와 격리 행 수가 늘지 않는다. 이것은 작은 단일 DB 배치의 결과이지 분산 시스템 전체의 exactly-once 보장이 아니다.

실제 시스템에는 같은 event_id인데 내용이 다른 충돌, 원천 삭제, 같은 시각의 버전 순서, 이벤트가 늦게 오는 경우가 있다. 이 예제의 event_id 사전순 동률 규칙은 결정적 학습 규칙일 뿐 업무상 최신을 증명하지 않는다. 원천 버전 계약과 감사 이력을 추가해야 한다.

### 4. 따라 하는 예제

```bash
python -m examples.PY_A05
```

```python
import sqlite3
import tempfile
from pathlib import Path
from etl import load_events

source = Path("data/raw_events.csv")
with tempfile.TemporaryDirectory() as folder:
    db_path = Path(folder) / "events.db"
    first = load_events(source, db_path)
    second = load_events(source, db_path)
    assert first == second
    print(second)
    with sqlite3.connect(db_path) as conn:
        print(conn.execute("SELECT visit_id,status,event_id FROM event_state ORDER BY visit_id").fetchall())
```

### 5. 결과와 코드 해설

```text
{'valid_input': 3, 'invalid_input': 3, 'state_rows': 2}
[(101, 'completed', 'e3'), (102, 'planned', 'e2')]
```

임시 폴더를 만들므로 실습을 반복해도 기존 결과에 의존하지 않는다. 두 실행의 반환값은 valid_input=3, invalid_input=3, state_rows=2로 같다. visit_id101은 e3, 102는 e2가 남는다. 다음 단계로 etl.py 내부의 검증·정렬·UPSERT·격리·트랜잭션 순서를 읽는다.

### 6. 자주 하는 실수

단순히 “마지막 발생 시각보다 큰 것만 읽기”는 늦게 도착한 과거 이벤트를 놓칠 수 있다. 수신 시각·재처리 창·중복 제거·삭제 이벤트를 함께 설계한다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** 어떤 오류가 전체 배치를 중단시킬지, 어떤 오류는 격리할지 정한다.

**FDSE 관점:** 재실행·부분 실패·충돌·워터마크 갱신 원자성을 테스트한다.

### 8. 직접 풀어 보기

**PY-A05-1. 워터마크를 적재 전에 먼저 저장하면 어떤 손실이 생길 수 있는가?**

힌트: 워터마크 저장 후 배치가 실패했다고 가정한다.

[풀이 확인](#py-a05-1)

**PY-A05-2. 중복 이벤트 때문에 상태 행 수가 2인 것은 원본 6행 중 4행을 잃었다는 뜻인가?**

힌트: 정상 수정본·격리 행·현재 상태를 구분한다.

[풀이 확인](#py-a05-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://www.postgresql.org/docs/16/sql-insert.html)
- [공식 문서 2](https://docs.python.org/3.12/library/sqlite3.html)

---

<a id="py-a06"></a>
## PY-A06 · FastAPI·입력 검증·권한·페이지 조회: 분석을 서비스로

**학습 목표:** 데이터 조회 기능을 HTTP 계약으로 노출하고 실패 경로를 검증한다.

**실행 구분:** Python 3.12 이상 대상; 제작 환경 Python 3.13.5에서 실행 확인

### 1. 용어부터 이해하기

엔드포인트(endpoint)는 요청을 받는 API 경로다. 입력 검증은 값의 형식·범위를 검사한다. 인증(authentication)은 누구인지, 인가(authorization)는 무엇을 해도 되는지 확인한다. 커서 페이지 조회는 마지막 본 키 이후를 읽는다.

### 2. 비유로 잡는 그림

분석가의 개인 장부 조회 함수를 여러 사용자가 이용하는 창구로 만들되, 창구마다 접근 가능한 서류를 제한한다.

### 3. 원리와 업무에서의 의미

제공된 api.py는 GET /health와 GET /visits를 구현한다. branch_id 범위·limit 1~100·after_id>=0을 검사하고, 데모 키에 연결된 허용 지점을 서버에서 확인한다. 사용자가 branch_id를 바꿔 보내도 허용되지 않으면 403이다.

데모 키는 학습용 고정 문자열이며 실제 인증 시스템이 아니다. 운영에는 신뢰 가능한 신원 검증, 키·토큰 수명 관리, TLS, 비밀 관리, 감사·속도 제한 등이 필요하다. CORS는 브라우저의 교차 출처 정책이지 사용자 인증이나 데이터 권한 검사를 대체하지 않는다.

SQLite 조회는 동기 함수이므로 이 예제의 엔드포인트도 일반 def로 작성했다. 무조건 async def를 붙여 동기 I/O를 직접 실행하는 것보다 사용 도구와 실행 모델을 맞추는 것이 중요하다. FastAPI의 동기 경로 처리와 비동기 경로 처리 차이는 공식 문서를 함께 읽는다.

### 4. 따라 하는 예제

```bash
python -m examples.PY_A06
```

```python
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)
allowed = client.get("/visits?branch_id=1&limit=2",
                     headers={"X-Demo-Key": "demo-branch-a"})
forbidden = client.get("/visits?branch_id=2",
                       headers={"X-Demo-Key": "demo-branch-a"})
print(allowed.status_code, [row["visit_id"] for row in allowed.json()])
print(forbidden.status_code)
```

### 5. 결과와 코드 해설

```text
200 [1, 2]
403
```

TestClient는 로컬 테스트에서 앱을 호출하므로 서버를 외부에 열지 않는다. 첫 응답은 200과 방문 ID[1,2], 두 번째는 403이다. 실제 로컬 서버는 `python -m uvicorn api:app --host 127.0.0.1 --port 8000`으로 실행한다. 테스트용 고정 키를 운영 보안으로 설명하지 않는다.

### 6. 자주 하는 실수

파라미터화한 SQL이라고 권한이 안전한 것은 아니다. 정상 형식의 다른 branch_id를 넣는 요청이 대표적인 별도 권한 테스트다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** 사용자별 업무 흐름과 접근 가능 데이터 범위를 설계한다.

**FDSE 관점:** API 스키마·에러 코드·권한 실패·페이지 중복·입력 상한을 구현한다.

### 8. 직접 풀어 보기

**PY-A06-1. limit=101과 허용되지 않은 지점 요청은 각각 어떤 상태 코드가 예상되는가?**

힌트: 입력 형식 실패와 권한 실패를 분리한다.

[풀이 확인](#py-a06-1)

**PY-A06-2. after_id 기반 조회가 안정적이기 위한 전제와 한계를 설명하라.**

힌트: 정렬 키의 불변성과 조회 중 데이터 변경을 생각한다.

[풀이 확인](#py-a06-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://fastapi.tiangolo.com/tutorial/testing/)
- [공식 문서 2](https://fastapi.tiangolo.com/tutorial/query-params-str-validations/)
- [공식 문서 3](https://fastapi.tiangolo.com/async/)

---

<a id="py-a07"></a>
## PY-A07 · 레이어·Protocol·의존성 주입: 바꾸기 쉬운 구조 만들기

**학습 목표:** 업무 규칙을 DB·API 구현과 분리해 테스트한다.

**실행 구분:** Python 3.12 이상 대상; 제작 환경 Python 3.13.5에서 실행 확인

### 1. 용어부터 이해하기

레이어(layer)는 책임별 코드 구분이다. Protocol은 필요한 메서드 형태를 표현하는 구조적 타입 계약이다. 의존성 주입(dependency injection)은 필요한 부품을 내부에서 고정 생성하지 않고 밖에서 전달하는 방식이다.

### 2. 비유로 잡는 그림

같은 계산기에 실제 DB 서랍 또는 테스트용 가짜 서랍을 꽂아 사용할 수 있게 만든다.

### 3. 원리와 업무에서의 의미

고객의 업무 규칙을 바꾸는 일과 DB 접속 방법을 바꾸는 일은 서로 다르다. 서비스 함수가 특정 DB 연결을 직접 만들면 테스트마다 DB가 필요하고 변경 범위가 넓어진다. 저장소 인터페이스를 받아 사용하면 계산 로직과 저장 방법을 분리할 수 있다.

Protocol은 “이 객체는 count_completed(branch_id)를 제공한다”는 약속을 표현한다. 상속 계층을 강제로 만들지 않고도 같은 형태의 객체를 전달할 수 있다. 타입 검사 도구의 도움을 받기 위한 선언이며 런타임 보안을 대신하지 않는다.

계층을 너무 많이 만들면 단순 기능도 추적하기 어려워진다. 바뀔 가능성이 실제로 있는 경계, 외부 I/O, 테스트 대체 지점에 적용한다. 핵심은 복잡한 이름이 아니라 어떤 변경을 어디에 가둘 것인지 설명하는 것이다.

### 4. 따라 하는 예제

```bash
python -m examples.PY_A07
```

```python
from typing import Protocol

class VisitRepository(Protocol):
    def count_completed(self, branch_id: int) -> int: ...

class MemoryVisitRepository:
    def __init__(self, counts: dict[int, int]):
        self._counts = dict(counts)

    def count_completed(self, branch_id: int) -> int:
        return self._counts.get(branch_id, 0)

def branch_summary(repo: VisitRepository, branch_id: int) -> dict:
    if branch_id <= 0:
        raise ValueError("invalid branch")
    return {"branch_id": branch_id, "completed": repo.count_completed(branch_id)}

repo = MemoryVisitRepository({1: 6, 2: 9, 3: 3})
print(branch_summary(repo, 2))
```

### 5. 결과와 코드 해설

```text
{'branch_id': 2, 'completed': 9}
```

서비스 함수는 저장소가 메모리인지 PostgreSQL인지 모른다. 필요한 계약만 호출한다. 테스트에는 MemoryVisitRepository를 사용하고 실제 실행에서는 파라미터화된 SQL을 사용하는 구현을 넣을 수 있다. DB별 SQL 차이는 저장소 구현 안에 둔다.

### 6. 자주 하는 실수

데이터 접근 권한을 단순히 저장소 교체로 해결했다고 주장하지 않는다. 인증된 사용자 맥락이 어느 레이어에서 검증되는지 별도로 정해야 한다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** 업무 규칙 변경과 기술 교체를 구분해 요구사항을 관리한다.

**FDSE 관점:** 도메인·서비스·저장소·API 경계를 설계하고 대체 가능한 테스트를 작성한다.

### 8. 직접 풀어 보기

**PY-A07-1. DB 없이 지점2 결과를 테스트하는 코드를 작성하라.**

힌트: 메모리 저장소에 이미 기대값을 넣을 수 있다.

[풀이 확인](#py-a07-1)

**PY-A07-2. 모든 함수에 인터페이스와 클래스를 만들면 더 좋은 설계인가?**

힌트: 얻는 변경 격리와 늘어나는 복잡도를 비교한다.

[풀이 확인](#py-a07-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://docs.python.org/3.12/library/typing.html#typing.Protocol)

---

<a id="py-a08"></a>
## PY-A08 · 프로파일링·메모리·CPU와 I/O: 추측 대신 측정하기

**학습 목표:** 병목을 구분하고 올바른 최적화 도구를 선택한다.

**실행 구분:** Python 3.12 이상 대상; 제작 환경 Python 3.13.5에서 실행 확인

### 1. 용어부터 이해하기

프로파일링(profiling)은 시간·호출·메모리 사용을 측정하는 작업이다. CPU-bound는 계산, I/O-bound는 파일·DB·네트워크 대기가 주요 병목인 작업이다. 처리량과 지연시간은 다른 성능 지표다.

### 2. 비유로 잡는 그림

주방이 느릴 때 요리사가 부족한지, 오븐이 느린지, 주문 전달이 막혔는지 먼저 측정한다.

### 3. 원리와 업무에서의 의미

async는 대기 시간을 활용하는 구조이지 모든 계산을 빠르게 하는 주문이 아니다. 일반적인 CPython 3.12의 GIL 환경에서 CPU 중심 Python 코드를 스레드로 늘린다고 자동으로 병렬 가속되지 않는다. 프로세스 분리·벡터화·네이티브 연산 등을 검토하되 직렬화·메모리·시작 비용도 포함한다.

반대로 DB가 느린데 Python 반복을 미세 최적화해도 전체 성능은 크게 바뀌지 않을 수 있다. 먼저 네트워크 대기, DB 계획, 직렬화, 애플리케이션 계산 시간을 나누어 측정한다. 최신 Python의 실행 모드 차이가 있으므로 자신의 환경을 기록한다.

cProfile은 함수별 호출 시간 분포를 살피는 도구다. 아래는 합성 반복 계산을 측정해 호출이 기록되었는지 확인한다. 절대 시간 출력은 기기마다 달라지므로 교재에서 특정 성능 숫자를 약속하지 않는다. 정확성 테스트를 통과한 상태에서 최적화 전후를 비교한다.

### 4. 따라 하는 예제

```bash
python -m examples.PY_A08
```

```python
import cProfile
import pstats
import io

def aggregate(values: list[int]) -> dict[int, int]:
    totals = {}
    for value in values:
        group = value % 10
        totals[group] = totals.get(group, 0) + value
    return totals

profiler = cProfile.Profile()
profiler.enable()
result = aggregate(list(range(10000)))
profiler.disable()
report = io.StringIO()
pstats.Stats(profiler, stream=report).sort_stats("cumulative").print_stats(5)
print(sum(result.values()))
print("aggregate" in report.getvalue())
```

### 5. 결과와 코드 해설

```text
49995000
True
```

0부터 9999까지의 합은 49995000이며 프로파일에 aggregate 함수가 기록되어 True를 출력한다. 실제 분석에서는 report.getvalue()를 출력해 누적 시간과 자기 시간을 비교한다. 이 예제는 단순 연산으로 도구 사용을 보여 주는 것이지 실제 서비스 병목을 재현한 것은 아니다.

### 6. 자주 하는 실수

한 번의 짧은 실행만으로 “3배 빨라졌다”고 주장하지 않는다. 입력·환경·반복 수·예열·분포·측정 범위를 함께 기록한다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** 사용자 체감 지연과 비용 개선 중 무엇이 우선인지 정한다.

**FDSE 관점:** 병목 분해·대표 부하·p50/p95·메모리·회귀 검증으로 최적화한다.

### 8. 직접 풀어 보기

**PY-A08-1. 외부 API 대기가 대부분인 경우와 순수 Python 대규모 계산이 대부분인 경우에 먼저 고려할 방법은?**

힌트: 작업 병목의 종류에 따라 도구가 다르다.

[풀이 확인](#py-a08-1)

**PY-A08-2. 캐시를 넣으면 왜 데이터 정확성 문제가 생길 수 있는가?**

힌트: 캐시 키와 만료·권한 맥락을 생각한다.

[풀이 확인](#py-a08-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://docs.python.org/3.12/library/profile.html)
- [공식 문서 2](https://docs.python.org/3.12/library/concurrent.futures.html)
- [공식 문서 3](https://docs.python.org/3.12/library/threading.html)

---

<a id="py-a09"></a>
## PY-A09 · 로그·지표·추적·보안: 장애가 났을 때 설명 가능한 서비스

**학습 목표:** 민감정보를 노출하지 않으면서 실패를 추적할 수 있는 기록을 만든다.

**실행 구분:** Python 3.12 이상 대상; 제작 환경 Python 3.13.5에서 실행 확인

### 1. 용어부터 이해하기

로그(log)는 사건 기록, 운영 지표(metric)는 건수·시간 같은 수치, 추적(trace)은 요청이 여러 단계에서 거친 경로다. 요청 ID는 한 실행을 연결하는 식별자다. 최소 권한은 필요한 접근만 부여하는 원칙이다.

### 2. 비유로 잡는 그림

택배 상자의 내용 전체를 공개하지 않고 송장 번호로 이동 경로와 실패 지점을 추적한다.

### 3. 원리와 업무에서의 의미

에러가 발생했을 때 고객은 “실패했습니다”보다 영향 범위·현재 상태·대안·복구 여부를 알고 싶어 한다. FDSE는 요청 ID, 단계, 처리 건수, 실패 분류를 기록하고 DS는 사용자에게 이해 가능한 상황 설명과 대응을 정리한다.

로그에는 고객 원문, 환자 정보, 인증 토큰, 전체 요청 본문을 무조건 넣지 않는다. 필요한 최소 메타데이터만 남기고 민감한 데이터의 원문은 접근 통제된 별도 저장소와 보존 정책으로 관리한다. 오류 메시지에 SQL·연결 문자열이 그대로 노출되지 않도록 한다.

지연시간만 보지 말고 오류율·신선도·격리율·중복·권한 거부·비용도 관찰한다. “오류율 0%”라도 데이터 갱신이 멈췄다면 서비스가 정상은 아니다. 목표값·알림 수신자·대응 절차가 없으면 지표 대시보드만으로 운영이 완성되지 않는다.

### 4. 따라 하는 예제

```bash
python -m examples.PY_A09
```

```python
import json

def safe_event(request_id: str, stage: str, input_rows: int,
               output_rows: int, error_code: str | None = None) -> str:
    if input_rows < 0 or output_rows < 0:
        raise ValueError("negative row count")
    return json.dumps({"request_id": request_id, "stage": stage,
                       "input_rows": input_rows, "output_rows": output_rows,
                       "error_code": error_code}, sort_keys=True)

print(safe_event("demo-001", "normalize", 6, 3, "3_ROWS_QUARANTINED"))
```

### 5. 결과와 코드 해설

```text
{"error_code": "3_ROWS_QUARANTINED", "input_rows": 6, "output_rows": 3, "request_id": "demo-001", "stage": "normalize"}
```

이 기록은 오류 행의 실제 내용을 출력하지 않고 실행 ID·단계·건수·분류를 남긴다. 운영에서는 검증된 구조화 로깅 도구와 타임스탬프·환경·서비스 버전 등도 추가한다. 로그가 생성된다는 사실과 로그가 적절하게 보호·검색·보존된다는 사실은 다르다.

### 6. 자주 하는 실수

고객이 보낸 문자열을 로그·화면·SQL에 넣을 때 각각의 출력 맥락에 맞는 처리가 필요하다. 한 번의 “정리”로 모든 주입·노출 문제가 해결되지는 않는다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** 장애 시 고객에게 알려야 할 영향·우회 방법·복구 검증을 정한다.

**FDSE 관점:** 최소 권한·감사·관측·알림·비밀 관리·데이터 보존을 설계한다.

### 8. 직접 풀어 보기

**PY-A09-1. 정상 입력 3행과 현재 상태 2행을 보고 1행 손실이라고 알림을 보내도 되는가?**

힌트: 이벤트 grain과 상태 grain을 구분한다.

[풀이 확인](#py-a09-1)

**PY-A09-2. 서비스 요청 성공률이 높아도 오래된 데이터를 반환하는 문제를 찾으려면 어떤 지표가 필요한가?**

힌트: 마지막 처리 시각과 원천 수신 시각을 비교한다.

[풀이 확인](#py-a09-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://docs.python.org/3.12/library/logging.html)
- [공식 문서 2](https://www.postgresql.org/docs/16/user-manag.html)

---

<a id="py-a10"></a>
## PY-A10 · 분산 집계·재결합·Foundry 연결 사고: 로컬에서 플랫폼으로

**학습 목표:** 부분 결과를 안전하게 합치고 플랫폼 개념과 로컬 구현을 대응시킨다.

**실행 구분:** Python 3.12 이상 대상; 제작 환경 Python 3.13.5에서 실행 확인

### 1. 용어부터 이해하기

분산 처리(distributed processing)는 여러 실행 단위가 데이터를 나눠 처리하는 방식이다. 부분 집계(partial aggregation)는 조각별 요약이다. 셔플(shuffle)은 키별로 데이터를 다시 모으는 재분배다. 데이터 계보(lineage)는 결과가 어떤 입력·변환에서 왔는지 나타낸다.

### 2. 비유로 잡는 그림

각 지점이 지연 건수와 측정 가능 건수를 보내면 본사는 두 합계를 더해 전체 비율을 계산한다.

### 3. 원리와 업무에서의 의미

분산 분석에서 평균의 평균은 위험하다. 각 조각이 평균만 보내면 원래 행 수를 잃는다. 평균은 합계와 건수, 지연율은 지연 건수와 측정 가능 건수처럼 합칠 수 있는 충분한 중간 상태를 저장한다.

로컬 pandas 결과를 대규모 Spark 처리로 옮길 때는 collect/toPandas로 전체 데이터를 다시 한 컴퓨터에 모으는지, 키별 groupby가 셔플을 만드는지, 특정 키에 데이터가 몰리는지 확인해야 한다. 아래 코드는 분산 시스템을 흉내 낸 로컬 부분 집계이며 실제 Spark 실행을 주장하지 않는다.

Palantir의 Ontology는 데이터·모델을 업무 객체·관계·행동과 연결하는 플랫폼 계층으로 설명된다. 로컬의 고객·방문·직원 모델을 객체/속성/관계 후보로 정리하고, 방문 재배정은 권한·검증·감사를 가진 행동으로 설계한다. SQL 표를 만들었다는 이유만으로 실제 Foundry Ontology를 구현했다고 표현하지 않는다.

### 4. 따라 하는 예제

```bash
python -m examples.PY_A10
```

```python
from course_lib import read_csv, kpi

rows = read_csv("visits")
partitions = [rows[:8], rows[8:16], rows[16:]]
partials = [kpi(part) for part in partitions]
late = sum(p["late"] for p in partials)
eligible = sum(p["eligible"] for p in partials)
combined_rate = late / eligible if eligible else None
single = kpi(rows)
assert combined_rate == single["late_rate"]
print({"partitions": len(partitions), "late": late,
       "eligible": eligible, "late_rate": combined_rate})
```

### 5. 결과와 코드 해설

```text
{'partitions': 3, 'late': 6, 'eligible': 15, 'late_rate': 0.4}
```

세 조각에서 각각 계산한 분자·분모를 더해 6/15=0.4를 얻는다. 이 방식은 조각별 입력이 중복·누락 없이 원본을 분할한다는 전제가 있다. 동일 이벤트가 여러 조각에 들어가면 먼저 중복 규칙을 적용해야 한다. 플랫폼에서도 숫자 보존과 업무 계약이 우선이다.

### 6. 자주 하는 실수

Foundry·Spark·AIP 이름을 붙이는 것과 실제 사용·운영 경험은 다르다. 포트폴리오에는 실행한 부분과 설계한 대응 관계를 명확히 구분한다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** 문제→객체→지표→행동→성과 검증으로 배포 스토리를 만든다.

**FDSE 관점:** 분산 처리 비용·재실행·권한·계보·확장 경계를 설명한다.

### 8. 직접 풀어 보기

**PY-A10-1. 각 파티션의 지연율만 저장하면 전체 지연율을 항상 복원할 수 있는가?**

힌트: 분모 크기가 다를 때를 생각한다.

[풀이 확인](#py-a10-1)

**PY-A10-2. 방문 재배정을 단순 DB UPDATE가 아니라 업무 행동으로 설계할 때 필요한 항목은?**

힌트: 누가·무엇을·언제·어떤 조건에서·실패 시를 묻는다.

[풀이 확인](#py-a10-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://spark.apache.org/docs/latest/sql-performance-tuning.html)
- [공식 문서 2](https://www.palantir.com/docs/foundry/ontology/overview/)
- [공식 문서 3](https://www.palantir.com/docs/foundry/transforms-python/overview/)



---
