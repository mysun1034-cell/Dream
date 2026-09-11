# Python 중급: 데이터 분석을 재현 가능한 프로그램으로

**구성:** 10강 · 연습문제 20개 · DS/FDSE 역할별 적용 과제

Python 기본 10강을 마친 뒤 진행합니다. 파일을 한 번 읽는 수준에서 벗어나 입력 계약·검증·테스트·API 연동을 갖춘 프로그램을 만듭니다.

**사용 방법:** 모든 명령은 압축을 푼 폴더의 `lab/`에서 실행합니다. 아직 환경을 만들지 않았다면 [환경과 데이터 사전](#book-02)을 먼저 읽으세요. 각 강의의 설명형 해설은 본문에, 연습문제 정답은 [해설집](#book-09)에 있습니다.

## 강의 지도

- [PY-I01 함수 계약·기본 인자·args와 kwargs: 유연함에 경계 세우기](#py-i01)
- [PY-I02 클래스·dataclass·조합: 업무 객체를 코드로 표현하기](#py-i02)
- [PY-I03 이터레이터·제너레이터·청크: 전부 메모리에 올리지 않기](#py-i03)
- [PY-I04 pandas·DataFrame·필터·groupby: 표를 코드로 분석하기](#py-i04)
- [PY-I05 merge·grain·결측 키: JOIN 오류를 Python에서도 막기](#py-i05)
- [PY-I06 datetime·시간대·관측 시점: 같은 순간을 같은 값으로](#py-i06)
- [PY-I07 Python과 SQL 연결: 파라미터·트랜잭션·연결 수명](#py-i07)
- [PY-I08 HTTP·API·페이지네이션·타임아웃: 외부 데이터를 끝까지 읽기](#py-i08)
- [PY-I09 pytest·경계값·회귀 테스트: 맞다는 주장을 증명하기](#py-i09)
- [PY-I10 재현 가능한 분석·불확실성·비교: 숫자를 의사결정으로](#py-i10)

---

<a id="py-i01"></a>
## PY-I01 · 함수 계약·기본 인자·args와 kwargs: 유연함에 경계 세우기

**학습 목표:** 필수 입력·선택 설정·추가 메타데이터를 분리한다.

**실행 구분:** Python 3.12 이상 대상; 제작 환경 Python 3.13.5에서 실행 확인

### 1. 용어부터 이해하기

함수 계약(contract)은 입력·출력·오류 조건의 약속이다. *args는 추가 위치 인자를 튜플로, **kwargs는 추가 키워드 인자를 딕셔너리로 모은다. keyword-only 인자는 이름을 붙여 전달해야 한다.

### 2. 비유로 잡는 그림

정해진 주문 항목은 신청서 본문에, 추적 번호 같은 부가 설명은 메모 칸에 적는 방식이다.

### 3. 원리와 업무에서의 의미

인자가 많아질수록 호출 문장이 뜻을 드러내야 한다. `classify(15,10)`보다 `classify(15,threshold=10)`은 두 숫자의 역할을 쉽게 읽을 수 있다. 함수 인자 목록에서 단독 `*` 뒤에 둔 인자는 이름을 붙여 전달해야 한다.

**kwargs는 무엇이든 받아도 된다는 면허가 아니다. 핵심 업무 입력까지 모두 kwargs에 숨기면 오타와 필수 값 누락을 찾기 어렵다. 핵심 필드는 명시하고 부가 메타데이터처럼 확장 가능한 부분만 제한적으로 받는다.

기본 인자에 빈 리스트·딕셔너리를 직접 넣으면 여러 호출이 같은 객체를 공유할 수 있다. 함수 내부에서 새 값을 만들거나 불변 기본값을 사용한다. 반환값에는 계산 결과와 설명용 메타데이터를 구분해서 넣는다.

### 4. 따라 하는 예제

```bash
python -m examples.PY_I01
```

```python
def describe_delay(delay: float | None, *, threshold: float = 10,
                   **metadata: str) -> dict:
    if threshold < 0:
        raise ValueError("threshold must be nonnegative")
    label = "unknown" if delay is None else ("late" if delay > threshold else "on_time")
    return {"label": label, "threshold": threshold, "metadata": dict(metadata)}

print(describe_delay(15, threshold=10, source="csv", rule_version="v1"))
```

### 5. 결과와 코드 해설

```text
{'label': 'late', 'threshold': 10, 'metadata': {'source': 'csv', 'rule_version': 'v1'}}
```

delay는 위치로 전달할 수 있지만 threshold는 이름을 써야 한다. source와 rule_version은 metadata 딕셔너리에 모인다. dict(metadata)는 부가 정보를 별도 객체로 반환한다. 이 함수는 완료 여부가 이미 확인된 지연값을 받는 계약이다.

### 6. 자주 하는 실수

`threshold=10`을 `treshold=10`으로 오타 내면 kwargs로 들어갈 수 있다. 핵심 설정 오타를 막으려면 허용 메타데이터 키를 검증하거나 별도의 명시적 dict 인자를 사용한다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** 고객에게 규칙 버전과 근거를 설명할 수 있는 메타데이터를 정한다.

**FDSE 관점:** 유연한 인터페이스와 엄격한 검증 사이의 균형을 설계한다.

### 8. 직접 풀어 보기

**PY-I01-1. source와 rule_version 외의 메타데이터 키를 거부하도록 검사 코드를 작성하라.**

힌트: 집합 차집합으로 알 수 없는 키를 찾는다.

[풀이 확인](#py-i01-1)

**PY-I01-2. *args와 **kwargs의 차이를 함수 호출 예로 설명하라.**

힌트: 위치와 이름이 있는 입력을 비교한다.

[풀이 확인](#py-i01-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://docs.python.org/3.12/tutorial/controlflow.html#more-on-defining-functions)

---

<a id="py-i02"></a>
## PY-I02 · 클래스·dataclass·조합: 업무 객체를 코드로 표현하기

**학습 목표:** 데이터와 규칙을 갖는 객체를 만들고 무분별한 상속을 피한다.

**실행 구분:** Python 3.12 이상 대상; 제작 환경 Python 3.13.5에서 실행 확인

### 1. 용어부터 이해하기

클래스(class)는 객체의 구조와 동작을 정의한다. 인스턴스(instance)는 그 정의로 만든 개별 객체다. dataclass는 데이터 저장용 클래스의 반복 코드를 줄인다. 조합(composition)은 다른 객체를 부품처럼 사용하는 방식이다.

### 2. 비유로 잡는 그림

Visit는 방문 기록의 양식이고, visit_id=101인 객체는 실제로 작성된 기록 한 장이다.

### 3. 원리와 업무에서의 의미

딕셔너리는 간단하지만 어떤 키가 있는지 항상 확인해야 한다. dataclass는 필드를 선언해 방문의 모양을 명확히 한다. `self`는 현재 객체 자신을 가리키는 관례적인 매개변수 이름이다. 메서드 안에서 self.status를 읽으면 그 방문의 상태를 읽는 것이다.

`frozen=True`는 필드 재대입을 막아 값 객체처럼 사용하기 쉽게 한다. 깊은 내부 객체까지 모두 불변으로 바꾸지는 않는다. 이 강의의 필드는 정수·문자열·선택적 숫자로 구성되어 단순하다. 타입 힌트만으로 값이 검증되지 않으므로 __post_init__에서 업무 조건을 검사한다.

상속은 모든 데이터 모델을 거대한 계층으로 만드는 도구가 아니다. 저장소·계산 규칙·알림 전송은 별도 부품으로 조합하면 교체와 테스트가 쉬워진다. 객체지향의 목표는 클래스를 많이 만드는 것이 아니라 책임과 변경 범위를 명확히 하는 것이다.

### 4. 따라 하는 예제

```bash
python -m examples.PY_I02
```

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Visit:
    visit_id: int
    status: str
    delay: float | None

    def __post_init__(self) -> None:
        if self.visit_id <= 0:
            raise ValueError("visit_id must be positive")
        if self.status not in {"completed", "planned", "cancelled"}:
            raise ValueError("unknown status")

    def is_measurable(self) -> bool:
        return self.status == "completed" and self.delay is not None

visit = Visit(101, "completed", 15)
print(visit.visit_id, visit.is_measurable())
```

### 5. 결과와 코드 해설

```text
101 True
```

@dataclass는 클래스를 가공하는 데코레이터다. 반복적인 생성자 코드를 자동으로 만들어 준다. __post_init__은 초기화 후 검증에 쓰인다. visit.is_measurable()을 호출하면 현재 visit가 self로 전달된다. 출력은 101 True다.

### 6. 자주 하는 실수

일반 dataclass는 잘못된 문자열 숫자를 자동 변환하지 않는다. 외부 입력 경계 검증과 내부 도메인 객체의 역할을 구분한다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** 현장 용어인 방문·직원·배정을 객체와 속성으로 정리한다.

**FDSE 관점:** 불변 값 객체, 상태 전이 규칙, 저장소 책임을 분리한다.

### 8. 직접 풀어 보기

**PY-I02-1. Visit(102,"planned",None)의 측정 가능 여부를 예측하라.**

힌트: 상태와 값 존재를 모두 검사한다.

[풀이 확인](#py-i02-1)

**PY-I02-2. Visit 클래스 안에 DB 비밀번호·HTTP 요청·보고서 출력까지 모두 넣으면 어떤 문제가 생기는가?**

힌트: 변경 이유와 테스트 비용을 생각한다.

[풀이 확인](#py-i02-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://docs.python.org/3.12/tutorial/classes.html)
- [공식 문서 2](https://docs.python.org/3.12/library/dataclasses.html)

---

<a id="py-i03"></a>
## PY-I03 · 이터레이터·제너레이터·청크: 전부 메모리에 올리지 않기

**학습 목표:** 파일을 한 행씩 처리하고 필요한 중간 상태만 보관한다.

**실행 구분:** Python 3.12 이상 대상; 제작 환경 Python 3.13.5에서 실행 확인

### 1. 용어부터 이해하기

이터레이터(iterator)는 다음 값을 차례로 제공하는 객체다. 제너레이터(generator)는 yield로 값을 순차 제공하는 함수다. 청크(chunk)는 일정 크기로 나눈 데이터 묶음이다.

### 2. 비유로 잡는 그림

상자 100만 개를 방에 한꺼번에 들이는 대신 컨베이어에서 한 개씩 검사한다.

### 3. 원리와 업무에서의 의미

list(csv.DictReader(...))는 모든 행을 메모리에 올린다. 작은 예제에는 편하지만 큰 파일에는 부담이 된다. 제너레이터는 현재 필요한 값만 제공해 전체 입력을 리스트로 만들지 않고 처리할 수 있다.

yield는 값을 한 번 내보낸 뒤 함수의 상태를 유지한다. 다음 값을 요청하면 이전 위치에서 계속 실행한다. return이 함수의 종료라면 yield는 다음 요청까지 잠시 중단하는 지점이다. async의 대기와는 다른 문법·목적이므로 혼동하지 않는다.

한 행씩 읽어도 모든 고유 고객을 set에 쌓으면 메모리는 고객 수에 비례해 늘어난다. “제너레이터를 썼으니 무조건 O(1) 메모리”가 아니다. 입력 보관과 중간 집계 상태를 따로 계산해야 한다. 연결·파일은 순회를 마칠 때까지 살아 있어야 한다.

### 4. 따라 하는 예제

```bash
python -m examples.PY_I03
```

```python
import csv
from pathlib import Path

def iter_visit_ids(path: Path):
    with path.open(encoding="utf-8", newline="") as file:
        for row in csv.DictReader(file):
            yield int(row["visit_id"])

ids = iter_visit_ids(Path("data/visits.csv"))
print(next(ids))
print(next(ids))
print(sum(1 for _ in ids))
```

### 5. 결과와 코드 해설

```text
1
2
22
```

제너레이터를 만드는 순간에는 본문 전체를 실행하지 않는다. next를 호출해 1,2를 받은 뒤 남은 순회를 세면 22다. 같은 이터레이터는 이미 소비한 값을 자동으로 다시 제공하지 않는다. 두 번 분석하려면 파일을 다시 읽거나 필요한 결과를 저장한다.

### 6. 자주 하는 실수

`with open` 밖에서 파일에 연결된 이터레이터를 반환하면 파일이 이미 닫힐 수 있다. 위처럼 파일 수명과 yield 순회를 같은 함수 안에 둔다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** 대용량 자료에서 전체 집계와 표본 탐색의 목적을 구분한다.

**FDSE 관점:** 입력·집계 상태·출력 버퍼를 나누어 메모리 사용을 추정한다.

### 8. 직접 풀어 보기

**PY-I03-1. 1~24까지 방문 ID의 합을 제너레이터로 계산하라.**

힌트: 새 이터레이터를 만들어야 한다.

[풀이 확인](#py-i03-1)

**PY-I03-2. 고유 고객 ID가 1천만 개이면 set을 사용하는 중복 제거의 메모리는 일정한가?**

힌트: 보관하는 고유값 수를 센다.

[풀이 확인](#py-i03-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://docs.python.org/3.12/tutorial/classes.html#generators)
- [공식 문서 2](https://docs.python.org/3.12/library/itertools.html)

---

<a id="py-i04"></a>
## PY-I04 · pandas·DataFrame·필터·groupby: 표를 코드로 분석하기

**학습 목표:** CSV를 표로 읽고 조건별 집계를 만든다.

**실행 구분:** Python 3.12 이상 대상; 제작 환경 Python 3.13.5에서 실행 확인

### 1. 용어부터 이해하기

DataFrame은 행과 이름 있는 열을 가진 pandas의 표 구조다. Series는 한 열 같은 1차원 자료다. 벡터화(vectorization)는 여러 값에 대한 연산을 배열·열 단위로 표현하는 방식이다.

### 2. 비유로 잡는 그림

Excel 표의 필터와 피벗을 클릭 기록 대신 다시 실행할 수 있는 코드로 적는 것이다.

### 3. 원리와 업무에서의 의미

pandas는 SQL을 대체해야 하는 도구가 아니다. DB에서 필요한 행만 가져와 Python의 분석·시각화 도구와 연결할 때 유용하다. 대용량 DB 표를 무조건 전부 내려받는 대신 집계와 필터를 DB에 맡길 수 있다.

`df.loc[조건, 열]`은 행·열 선택을 명시한다. 조건 여러 개를 연결할 때는 and/or가 아니라 원소별 연산자 &와 |를 사용하고 각 비교를 괄호로 감싼다. `df[조건]["열"]=...`처럼 연쇄 대입하기보다 .loc 또는 새 복사본을 사용한다.

groupby는 그룹을 만들고 agg는 요약 연산을 정한다. 결과 열에 의미 있는 이름을 붙이면 데이터 계약이 읽기 쉬워진다. 이 교재의 실행 검증은 pandas 2.2.3으로 했으며 버전별 동작 차이는 출처·검증 문서에 적는다.

### 4. 따라 하는 예제

```bash
python -m examples.PY_I04
```

```python
import pandas as pd

visits = pd.read_csv("data/visits.csv")
completed = visits.loc[visits["status"].eq("completed")].copy()
summary = completed.groupby("branch_id", as_index=False).agg(
    completed_visits=("visit_id", "size"),
    completed_fee_cents=("fee_cents", "sum"),
)
print(summary.sort_values("branch_id").to_dict("records"))
```

### 5. 결과와 코드 해설

```text
[{'branch_id': 1, 'completed_visits': 6, 'completed_fee_cents': 63000}, {'branch_id': 2, 'completed_visits': 9, 'completed_fee_cents': 126000}, {'branch_id': 3, 'completed_visits': 3, 'completed_fee_cents': 51000}]
```

read_csv가 파일을 DataFrame으로 만든다. eq는 ==와 같은 원소별 비교를 반환한다. copy로 분석용 표를 명시적으로 분리했다. size는 그룹 행 수다. count는 선택 열의 결측값을 제외하므로 둘의 의미를 구분한다. 지점별 완료 수는 6,9,3이다.

### 6. 자주 하는 실수

행마다 apply를 쓰기 전에 열 단위 연산으로 표현 가능한지 확인한다. 그러나 더 짧은 코드가 항상 더 정확하거나 더 빠른 것은 아니므로 측정한다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** SQL 결과와 pandas 결과를 같은 지표 정의로 대조한다.

**FDSE 관점:** 입력 자료형, 결측 처리, 정렬, 결과 스키마를 명시한다.

### 8. 직접 풀어 보기

**PY-I04-1. 취소 방문의 지점별 건수를 pandas로 계산하라.**

힌트: 상태 필터를 바꾸고 size를 사용한다.

[풀이 확인](#py-i04-1)

**PY-I04-2. CSV의 visit_id가 숫자처럼 보여도 고객의 외부 ID라면 정수로 바꿔도 되는가?**

힌트: 선행 0과 계산 필요성을 생각한다.

[풀이 확인](#py-i04-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://pandas.pydata.org/docs/user_guide/10min.html)
- [공식 문서 2](https://pandas.pydata.org/docs/user_guide/groupby.html)

---

<a id="py-i05"></a>
## PY-I05 · merge·grain·결측 키: JOIN 오류를 Python에서도 막기

**학습 목표:** 키의 대응 수를 검증하며 두 표를 연결한다.

**실행 구분:** Python 3.12 이상 대상; 제작 환경 Python 3.13.5에서 실행 확인

### 1. 용어부터 이해하기

merge는 pandas의 열 기반 표 연결이다. validate는 기대하는 1:1·N:1 등의 관계를 검사한다. indicator는 각 행이 어느 표에서 왔는지 표시한다.

### 2. 비유로 잡는 그림

방문 장부에 지점 이름을 붙이기 전에 지점 번호가 한 번씩만 있는지 확인한다.

### 3. 원리와 업무에서의 의미

SQL에서 잘못된 JOIN은 pandas에서도 그대로 잘못된다. 왼쪽 방문은 지점당 여러 행, 오른쪽 지점은 ID당 한 행이어야 하므로 validate="many_to_one"을 쓴다. 오른쪽 키가 중복되면 오류가 나도록 하는 것이다.

pandas의 merge는 양쪽 결측 키를 서로 매칭할 수 있어 일반적인 SQL의 NULL equality join과 다르다. 필수 키 결측은 연결 전에 거부하거나 격리한다. 단순히 SQL 코드를 pandas로 옮겼다는 이유로 결과가 동일하다고 가정하지 않는다.

연결 후 행 수가 예상대로인지, 미매칭 행이 있는지, 합계가 보존되는지 확인한다. 무작정 drop_duplicates를 붙이면 데이터 손실이나 관계 오류가 가려질 수 있다. key uniqueness와 business grain을 함께 검증한다.

### 4. 따라 하는 예제

```bash
python -m examples.PY_I05
```

```python
import pandas as pd

visits = pd.read_csv("data/visits.csv")
branches = pd.read_csv("data/branches.csv")
assert visits["branch_id"].notna().all()
assert branches["branch_id"].notna().all()
joined = visits.merge(branches, on="branch_id", how="left",
                      validate="many_to_one", indicator=True)
assert len(joined) == len(visits)
assert joined["_merge"].eq("both").all()
print(len(joined), int(joined["fee_cents"].sum()))
```

### 5. 결과와 코드 해설

```text
24 324000
```

assert는 개발·테스트에서 기대가 틀리면 실패시키는 문장이다. 운영 입력 검증에는 최적화 실행에서 제거될 수 있는 assert 대신 명시적 예외도 고려한다. merge 관계 검증을 통과하면 24행과 전체 fee 합계 324000을 유지한다.

### 6. 자주 하는 실수

validate="many_to_many"는 연결 폭증을 막아 주는 강한 검증이 아니다. 정말 N:N 관계가 필요한지와 출력 grain을 따로 확인한다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** 어떤 미매칭 데이터를 보고에서 제외할지 임의로 결정하지 않는다.

**FDSE 관점:** 행 수·합계·키 고유성·미매칭 비율을 연결 테스트에 넣는다.

### 8. 직접 풀어 보기

**PY-I05-1. branches에 첫 행을 복제해 붙이고 merge를 다시 실행하면 어떤 결과를 기대해야 하는가?**

힌트: many_to_one 계약을 일부러 깨 본다.

[풀이 확인](#py-i05-1)

**PY-I05-2. 두 표의 branch_id가 모두 결측일 때 SQL과 pandas 결과가 달라질 수 있는 이유는?**

힌트: NULL 매칭 규칙을 비교한다.

[풀이 확인](#py-i05-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://pandas.pydata.org/docs/user_guide/merging.html)
- [공식 문서 2](https://pandas.pydata.org/docs/reference/api/pandas.merge.html)

---

<a id="py-i06"></a>
## PY-I06 · datetime·시간대·관측 시점: 같은 순간을 같은 값으로

**학습 목표:** UTC와 현지 시간을 변환하고 지연 분을 정확히 계산한다.

**실행 구분:** Python 3.12 이상 대상; 제작 환경 Python 3.13.5에서 실행 확인

### 1. 용어부터 이해하기

naive datetime은 시간대 정보가 없고 aware datetime은 시간대 정보가 있다. UTC는 비교 기준 시각이다. 관측 시점(as-of)은 결과를 판단하는 기준 순간이다.

### 2. 비유로 잡는 그림

서울 시계와 런던 시계의 숫자가 다르다고 두 사건의 선후 관계가 바로 정해지는 것은 아니다.

### 3. 원리와 업무에서의 의미

"2026-08-01 09:00"만 있으면 어느 지역 시간인지 모른다. API·배치에서는 오프셋이나 명시적인 시간대 계약이 필요하다. 저장·비교 기준과 사용자에게 보여 주는 시간대를 분리한다.

`fromisoformat`은 오프셋이 포함된 문자열을 aware datetime으로 읽는다. 서로 다른 오프셋의 시각을 빼도 같은 시간축에서 계산할 수 있다. 하루의 시작·월말 집계는 업무 시간대로 변환한 뒤 구간을 정해야 한다.

이 실습은 8월 1일 00:00 UTC와 09:15 +09:00을 비교한다. 화면 숫자만 빼면 9시간 15분처럼 보이지만 실제 차이는 15분이다. 서머타임 전환 지역에서는 겹치거나 없는 현지 시간이 생길 수 있으므로 naive 시각에 시간대 표식만 붙이는 접근을 일반적인 변환으로 사용하지 않는다.

### 4. 따라 하는 예제

```bash
python -m examples.PY_I06
```

```python
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

planned = datetime.fromisoformat("2026-08-01T00:00:00+00:00")
actual = datetime.fromisoformat("2026-08-01T09:15:00+09:00")
delay = (actual - planned).total_seconds() / 60
print(delay)
print(planned.astimezone(ZoneInfo("Asia/Seoul")).isoformat())
print(actual.astimezone(timezone.utc).isoformat())
```

### 5. 결과와 코드 해설

```text
15.0
2026-08-01T09:00:00+09:00
2026-08-01T00:15:00+00:00
```

total_seconds는 시간 차이를 초로 바꾸고 /60은 분으로 변환한다. astimezone은 같은 순간을 다른 지역의 시계로 표현한다. replace(tzinfo=...)로 표식을 교체하는 것과 구분해야 한다. 결과는 15분, 서울 09:00, UTC 00:15다.

### 6. 자주 하는 실수

날짜별 집계를 UTC로 할지 영업지의 현지 날짜로 할지 정하지 않으면 같은 사건이 다른 월에 들어갈 수 있다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** 보고 기간·현지 영업일·관측 마감 시점을 합의한다.

**FDSE 관점:** 타임스탬프 형식·시간대 필수·경계값·DST 테스트를 설계한다.

### 8. 직접 풀어 보기

**PY-I06-1. 2026-08-31 16:00 UTC는 서울 기준 어느 날짜인가?**

힌트: 9시간을 더하되 월이 바뀌는지 본다.

[풀이 확인](#py-i06-1)

**PY-I06-2. naive datetime 두 개를 빼면 오류 없이 숫자가 나오는데 왜 위험할 수 있는가?**

힌트: 숫자가 나오는 것과 시간대 계약이 맞는 것은 다르다.

[풀이 확인](#py-i06-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://docs.python.org/3.12/library/datetime.html)
- [공식 문서 2](https://docs.python.org/3.12/library/zoneinfo.html)

---

<a id="py-i07"></a>
## PY-I07 · Python과 SQL 연결: 파라미터·트랜잭션·연결 수명

**학습 목표:** 사용자 값을 SQL 코드와 분리하고 연결을 안전하게 정리한다.

**실행 구분:** Python 3.12 이상 대상; 제작 환경 Python 3.13.5에서 실행 확인

### 1. 용어부터 이해하기

드라이버(driver)는 Python과 DB 사이에서 명령·값을 전달하는 라이브러리다. 파라미터 바인딩은 값을 SQL 구조와 분리해 전달하는 방식이다. 연결(connection)은 DB와 통신하는 세션이다.

### 2. 비유로 잡는 그림

사용자에게 SQL 문장 편집권을 주는 대신, 정해진 신청서의 값 칸만 채우게 한다.

### 3. 원리와 업무에서의 의미

`f"... WHERE status='{user_input}'"`처럼 입력값을 SQL 문자열에 붙이면 그 값이 명령 구조로 해석될 위험이 있다. SQLite에서는 ? 자리표시자와 별도 튜플을 사용한다. PostgreSQL의 psycopg에서는 %s와 별도 튜플을 사용하며, Python의 % 문자열 포맷과 혼동하지 않는다.

자리표시자는 값에 사용한다. 표 이름·정렬 방향 같은 SQL 구조를 값처럼 바인딩할 수는 없다. 그런 구조는 미리 정한 허용 목록에서 고르거나 드라이버의 안전한 식별자 조합 도구를 사용한다.

sqlite3 연결의 with는 트랜잭션 성공·실패 처리를 관리하지만 연결 자체를 자동으로 닫는 의미는 아니다. 여기서는 contextlib.closing으로 연결 수명을 감싼다. 읽기 전용 함수는 read-only 연결을 쓰도록 제공했다. SQL 주입 방지와 사용자 권한 확인은 별개의 문제다.

### 4. 따라 하는 예제

```bash
python -m examples.PY_I07
```

```python
from course_lib import query

status = "completed"
rows = query("SELECT visit_id FROM visits WHERE status=? ORDER BY visit_id", (status,))
print(len(rows))
malicious_value = "completed' OR 1=1 --"
print(query("SELECT visit_id FROM visits WHERE status=?", (malicious_value,)))
```

### 5. 결과와 코드 해설

```text
18
[]
```

(status,)의 쉼표는 한 요소짜리 튜플을 만든다. 첫 조회는 18행이다. 두 번째 입력은 SQL 구조가 아니라 상태 문자열 값으로 처리되어 0행이다. query 보조 함수의 내부에서 연결을 열고 닫는다. 코드를 읽어 호출자의 책임과 보조 함수 책임을 구분하자.

### 6. 자주 하는 실수

파라미터화해도 사용자가 다른 지점 ID를 넣어 조회하는 권한 문제는 남는다. 인증된 신원과 허용 범위를 서버에서 따로 검사한다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** 어떤 사용자가 어느 데이터까지 볼 수 있는지 정의한다.

**FDSE 관점:** 바인딩·트랜잭션·연결 풀·타임아웃·권한 검사를 독립적으로 설계한다.

### 8. 직접 풀어 보기

**PY-I07-1. branch_id=2의 완료 방문 수를 파라미터로 조회하라.**

힌트: 값 두 개에 자리표시자 두 개를 사용한다.

[풀이 확인](#py-i07-1)

**PY-I07-2. psycopg로 전환할 때 SELECT의 값 자리는 어떻게 쓰는가?**

힌트: 자리표시자 문법이 드라이버마다 다르다.

[풀이 확인](#py-i07-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://docs.python.org/3.12/library/sqlite3.html)
- [공식 문서 2](https://www.psycopg.org/psycopg3/docs/basic/params.html)

---

<a id="py-i08"></a>
## PY-I08 · HTTP·API·페이지네이션·타임아웃: 외부 데이터를 끝까지 읽기

**학습 목표:** 여러 페이지의 응답을 모으고 무한 요청을 막는다.

**실행 구분:** Python 3.12 이상 대상; 제작 환경 Python 3.13.5에서 실행 확인

### 1. 용어부터 이해하기

HTTP는 요청과 응답으로 통신하는 규약이다. API는 프로그램 간 사용 약속이다. 페이지네이션은 결과를 여러 묶음으로 나누는 방식이다. 타임아웃은 응답 대기의 상한이다.

### 2. 비유로 잡는 그림

한 번에 서류 100장만 주는 창구에서 “다음 묶음 표”를 받아 반복해서 가져오는 과정이다.

### 3. 원리와 업무에서의 의미

API 호출이 성공해도 첫 페이지만 읽으면 데이터가 빠진다. 응답의 next_cursor가 없을 때 끝나도록 반복하고, 최대 페이지 수와 반복 커서 검사를 두어 잘못된 서버 응답 때문에 끝없이 돌지 않게 한다.

HTTP 200은 통신 차원의 성공일 뿐 JSON 모양과 데이터의 정확성까지 보장하지 않는다. 상태 코드 확인 후 items와 next_cursor 같은 응답 계약을 검사한다. 실제 네트워크에서는 연결·읽기 타임아웃, 재시도 가능한 오류, rate limit도 다룬다.

아래 코드는 실제 인터넷에 접속하지 않고 httpx.MockTransport로 두 페이지짜리 API를 만든다. 페이지 제어 로직은 실행 검증하지만 실제 서버 지연·네트워크 타임아웃을 검증한 것은 아니다. 재시도는 읽기 요청 등 안전한 작업과 상태 코드 정책을 확인한 뒤 제한된 횟수로 한다.

### 4. 따라 하는 예제

```bash
python -m examples.PY_I08
```

```python
import httpx

def handler(request: httpx.Request) -> httpx.Response:
    cursor = request.url.params.get("cursor")
    body = {"items": [1, 2], "next_cursor": "page2"} if cursor is None else {"items": [3], "next_cursor": None}
    return httpx.Response(200, json=body)

def fetch_all(client: httpx.Client) -> list[int]:
    items, seen = [], set()
    cursor = None
    for _ in range(5):
        response = client.get("/visits", params={} if cursor is None else {"cursor": cursor})
        response.raise_for_status()
        body = response.json()
        if not isinstance(body.get("items"), list):
            raise ValueError("invalid items")
        items.extend(body["items"])
        cursor = body.get("next_cursor")
        if cursor is None:
            return items
        if not isinstance(cursor, str) or cursor in seen:
            raise ValueError("invalid or repeated cursor")
        seen.add(cursor)
    raise RuntimeError("page limit exceeded")

with httpx.Client(base_url="https://training.invalid", timeout=5,
                  transport=httpx.MockTransport(handler)) as client:
    print(fetch_all(client))
```

### 5. 결과와 코드 해설

```text
[1, 2, 3]
```

첫 응답은 [1,2]와 page2 커서를 준다. 다음 요청에 커서를 넣으면 [3]과 끝 표시 None을 받는다. 결과는 [1,2,3]이다. 사용 중인 도메인은 MockTransport로 가로채므로 외부 요청이 나가지 않는다. 반복 커서와 최대 페이지 수 초과는 실패로 처리한다.

### 6. 자주 하는 실수

결제·메일 전송 같은 변경 요청을 무조건 재시도하면 중복 효과가 생긴다. 멱등 키·수신자 중복 제거·트랜잭션 설계를 함께 고려한다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** 데이터 지연·일부 누락이 의사결정에 주는 영향을 설명한다.

**FDSE 관점:** 페이지 계약·상태 코드·타임아웃·중복·재시도 예산을 테스트한다.

### 8. 직접 풀어 보기

**PY-I08-1. 두 번째 응답도 next_cursor="page2"를 반환하면 어떻게 되는가?**

힌트: seen 집합의 목적을 확인한다.

[풀이 확인](#py-i08-1)

**PY-I08-2. 429 응답과 400 응답을 모두 즉시 10번 재시도해야 하는가?**

힌트: 일시적인 제한과 잘못된 요청을 구분한다.

[풀이 확인](#py-i08-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://www.python-httpx.org/advanced/transports/)
- [공식 문서 2](https://www.python-httpx.org/advanced/timeouts/)

---

<a id="py-i09"></a>
## PY-I09 · pytest·경계값·회귀 테스트: 맞다는 주장을 증명하기

**학습 목표:** 핵심 업무 규칙을 자동 테스트로 고정한다.

**실행 구분:** pytest 예제; 제작 환경에서 6개 테스트 통과

### 1. 용어부터 이해하기

단위 테스트는 작은 함수의 행동을 검사한다. 통합 테스트는 여러 부품의 연결을 검사한다. 회귀 테스트는 이전에 고친 오류의 재발을 막는다. fixture는 테스트 준비 데이터를 제공한다.

### 2. 비유로 잡는 그림

수동 검수표를 프로그램으로 만들어 변경할 때마다 같은 기준으로 다시 확인한다.

### 3. 원리와 업무에서의 의미

정상 사례 하나가 통과해도 함수가 맞다는 증거는 약하다. 지연 규칙은 10분 바로 아래·정확히 10분·바로 위·결측·취소·빈 집단을 검사해야 한다. 테스트 입력을 왜 선택했는지 설명할 수 있어야 한다.

pytest의 parametrize는 같은 검증을 여러 입력에 적용한다. 테스트 이름은 실패했을 때 무엇이 깨졌는지 드러나게 짓는다. 외부 API는 mock으로 고정하고 DB 변경은 임시 DB에서 검증해 서로 영향을 주지 않게 한다.

커버리지 수치가 높아도 잘못된 기대값을 적으면 틀린 업무 규칙을 보증한다. DS와 함께 기준 예제를 합의하고 FDSE는 이를 실행 가능한 테스트로 고정한다. 운영 입력 검증과 개발 테스트의 assert는 책임이 다르다.

### 4. 따라 하는 예제

```bash
python -m pytest examples/PY_I09.py -q
```

```python
import pytest
from course_lib import classify_visit, kpi

@pytest.mark.parametrize("delay,expected", [
    (0, "on_time"), (10, "on_time"), (10.1, "late"), (None, "unknown"),
])
def test_completed_delay(delay, expected):
    assert classify_visit("completed", delay) == expected

def test_empty_population():
    assert kpi([])["late_rate"] is None

def test_unknown_status_is_rejected():
    with pytest.raises(ValueError):
        classify_visit("typo", 5)
```

### 5. 결과와 코드 해설

```text
6 passed (제작 환경 실행 결과; 소요 시간은 환경마다 다름)
```

parametrize의 네 행이 네 테스트로 실행된다. 추가 두 테스트를 합쳐 여섯 건이다. pytest.raises는 해당 예외가 나야 성공이다. 이 파일은 일반 print 예제가 아니라 pytest로 실행한다. `python -m pytest examples/PY_I09.py -q`를 사용한다.

### 6. 자주 하는 실수

테스트에서 실제 운영 API·DB를 호출하지 않는다. 외부 서비스 상태 때문에 결과가 달라지는 테스트와 고정된 로직 테스트를 구분한다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** 수용 기준을 실제 입력·기대 결과 쌍으로 작성한다.

**FDSE 관점:** 경계값·오류 경로·권한 실패·재실행 결과를 자동화한다.

### 8. 직접 풀어 보기

**PY-I09-1. cancelled 상태가 delay=30이어도 excluded인지 테스트를 추가하라.**

힌트: 새 테스트 함수는 test_로 시작한다.

[풀이 확인](#py-i09-1)

**PY-I09-2. 개발자가 지연 기준을 >10에서 >=10으로 바꾸면 어느 테스트가 잡는가?**

힌트: 경계값 10의 기대값을 찾는다.

[풀이 확인](#py-i09-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://docs.pytest.org/en/stable/how-to/parametrize.html)
- [공식 문서 2](https://docs.pytest.org/en/stable/how-to/assert.html)

---

<a id="py-i10"></a>
## PY-I10 · 재현 가능한 분석·불확실성·비교: 숫자를 의사결정으로

**학습 목표:** 분모·결측·가중치·인과 주장의 한계를 함께 보고한다.

**실행 구분:** Python 3.12 이상 대상; 제작 환경 Python 3.13.5에서 실행 확인

### 1. 용어부터 이해하기

기술 통계는 관측 데이터의 요약이다. 상관은 함께 변하는 패턴이고 인과는 한 변화가 다른 변화를 일으키는 관계다. 기준선(baseline)은 개선을 비교할 출발점이다.

### 2. 비유로 잡는 그림

성적표에 평균만 쓰는 대신 응시자 수·결시자·시험 난이도까지 함께 적는 것이다.

### 3. 원리와 업무에서의 의미

학습 자료의 지연율은 측정 가능한 완료 방문 15건 중 6건, 즉 40%다. 완료했지만 시간이 없는 3건이 모두 정시라면 완료 18건 전체의 지연 비율은 6/18, 모두 지연이라면 9/18이다. 이는 결측에 관한 최악·최선 가정 범위이지 통계적 신뢰구간이 아니다.

지점별 비율을 단순 평균 내면 각 지점에 같은 가중치를 준다. 전체 방문의 지연율을 원하면 분자 합/분모 합을 써야 한다. 어떤 평균이 맞는지는 질문에 달려 있으며 고객에게 계산 단위를 설명해야 한다.

“배정 알고리즘을 바꾼 후 지연이 줄었다”만으로 원인을 확정할 수 없다. 고객 구성·날씨·시기·인력·기록 누락이 달라졌을 수 있다. 비교 설계를 정하고 관측 가능한 교란 요인을 확인한다. 본 과정은 DS를 통계 연구자로 축소하지 않지만, 근거의 강도를 구분하는 능력은 반드시 훈련한다.

### 4. 따라 하는 예제

```bash
python -m examples.PY_I10
```

```python
from course_lib import kpi, read_csv

result = kpi(read_csv("visits"))
late, completed, unknown = result["late"], result["completed"], result["unknown"]
lower = late / completed
upper = (late + unknown) / completed
print(f"observed={result['late_rate']:.1%}")
print(f"missingness bounds={lower:.1%} to {upper:.1%}")
branches = [(1, 2), (0, 18)]  # (late, eligible)
print(sum(a / b for a, b in branches) / len(branches))
print(sum(a for a, b in branches) / sum(b for a, b in branches))
```

### 5. 결과와 코드 해설

```text
observed=40.0%
missingness bounds=33.3% to 50.0%
0.25
0.05
```

관측 지연율은 40%, 결측을 포함한 완료 전체의 가능한 범위는 약 33.3~50.0%다. 두 예시 지점의 비율 단순 평균은 25%지만 전체 비율은 5%다. 출력값만 제시하지 말고 각 수치가 어떤 질문의 답인지 설명한다.

### 6. 자주 하는 실수

합성 데이터에서 계산한 40%는 실제 CareLink 성과도, Palantir 사례의 수치도 아니다. 포트폴리오에서 실제 개선 효과처럼 쓰지 않는다.

### 7. 같은 기술, 두 역할의 질문

**DS 관점:** 관측·가정·추론·권고를 분리한 1쪽 메모를 작성한다.

**FDSE 관점:** 입력 버전·규칙 버전·실행 환경·검증 결과를 기록해 분석을 재현한다.

### 8. 직접 풀어 보기

**PY-I10-1. 결측 완료 방문이 3건이 아니라 0건이면 가능한 범위는 어떻게 되는가?**

힌트: 분모도 completed=15인 일관된 사례를 생각한다.

[풀이 확인](#py-i10-1)

**PY-I10-2. “지점 B가 더 나쁘니 직원을 늘리자”에 앞서 필요한 확인을 세 가지 써라.**

힌트: 비교 집단·누락·행동 가능성을 확인한다.

[풀이 확인](#py-i10-2)


### 9. 통과 확인과 공식 참고자료

코드를 보지 않고 핵심 용어를 설명하고, 입력 또는 조건을 하나 바꿔 결과를 먼저 예상하세요. 정답이 같아도 분모·키·시간·권한의 전제가 틀렸다면 다시 점검합니다.

- [공식 문서 1](https://www.postgresql.org/docs/16/functions-aggregate.html)
- [공식 문서 2](https://pandas.pydata.org/docs/user_guide/missing_data.html)



---
