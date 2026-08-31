# LLM · Transformer · vLLM · EDENING 연결 학습 노트

이 문서는 첨부된 학습 대화를 줄이거나 요약하지 않고, 설명의 의존관계를 따라 다시 배열한 통합본이다. 먼저 Transformer가 어떻게 정보를 처리하는지 이해하고, 그 위에서 LLM 추론과 KV Cache가 왜 중요한지 연결한 다음, vLLM의 서빙 구조·OpenAI 호환 API·GPU 운영·EDENING 적용·Stripe 사례로 이어진다.

원문 표현, 예시, 수치, 질문과 답변, 주의사항은 가능한 한 그대로 보존했다. 다만 읽는 흐름을 만들기 위해 장의 순서와 장 사이의 연결 문장만 추가했다. 첨부 당시의 전체 원문은 [vLLM 학습 원문 보존본](vllm-study-source.txt)에서 확인할 수 있다.

## 전체 연결 흐름

1. Attention → Self-Attention → Transformer → GPT/LLM
2. Prefill·Decode와 KV Cache → 여러 요청을 다루는 서빙 문제
3. PagedAttention·Continuous Batching·Prefix Caching → vLLM
4. OpenAI SDK와 vLLM API → 모델 서버 연결 방식
5. GPU 구매·임대와 EDENING의 하이브리드 운영
6. Stripe 사례를 통한 비용·호출량·LLM 플랫폼 해석

---

## 1. Attention에서 Transformer까지: LLM의 계산 구조

Transformer를 서빙하는 엔진을 이해하려면 먼저 Transformer가 토큰 사이의 정보를 어떻게 교환하고, 다음 토큰을 어떻게 만들어 내는지부터 연결해야 한다.

기존 모델의 문제: 문장을 하나의 벡터에 압축해야 했다
초기의 신경망 번역 모델은 대략 다음처럼 움직였다.

영어 문장 전체
     ↓
Encoder
     ↓
하나의 고정된 문맥 벡터 c
     ↓
Decoder
     ↓
한국어 번역문
예를 들어 다음 영어 문장을 번역한다고 하자.

The student who met the teacher yesterday submitted the assignment.

기존 Encoder는 이 문장 전체 정보를 하나의 벡터 c 안에 압축해야 했다. 그리고 Decoder는 한국어 단어를 하나씩 만들 때 계속 같은 c를 사용했다.

"그"를 만들 때도       → 같은 c
"학생은"을 만들 때도   → 같은 c
"과제를" 만들 때도     → 같은 c
"제출했다" 만들 때도   → 같은 c
문장이 길어질수록 하나의 벡터에 모든 세부 정보를 담는 것이 병목이 될 수 있었다.

Bahdanau 등의 대표적인 초기 Attention 연구는 Decoder가 출력 단어를 만들 때마다 입력 문장의 각 부분을 다르게 참고하도록 만들었다. 즉, 하나의 고정된 문맥 벡터가 아니라 출력 시점마다 별도의 문맥 벡터 cᵢ를 계산한 것이다. 

Attention의 핵심 아이디어
번역기가 지금 한국어 단어 “과제를” 만들고 있다고 하자.

그러면 입력 문장에서 다음처럼 중요도를 매길 수 있다.

영어 입력	현재 중요도
The	0.01
student	0.04
who	0.01
met	0.02
the teacher	0.02
yesterday	0.05
submitted	0.20
the assignment	0.65
그다음 입력 단어들의 정보를 중요도에 따라 섞는다.

c
i
=
∑
j
α
i
j
h
j
c 
i
​
 = 
j
∑
​
 α 
ij
​
 h 
j
​
 
h
j
h 
j
​
 : 입력의 j번째 위치가 가진 정보
α
i
j
α 
ij
​
 : 출력 i번째 단어를 만들 때 입력 j번째 위치를 얼마나 참고할지
c
i
c 
i
​
 : 현재 출력에 필요한 문맥 정보
즉 Attention은 다음 계산이다.

여러 정보에 관련도 점수를 매기고, 그 점수를 가중치로 삼아 필요한 정보를 섞어 가져오는 것

2. Query, Key, Value란 무엇인가
Transformer에서는 Attention을 Query, Key, Value, 즉 Q·K·V로 설명한다.

도서관 검색으로 비유하면 쉽다.

요소	도서관 비유	신경망에서의 의미
Query, Q	내가 찾고 있는 책의 조건	현재 위치가 원하는 정보
Key, K	각 책의 제목·분류·검색 태그	각 위치가 어떤 정보와 관련 있는지 나타내는 주소
Value, V	책의 실제 내용	실제로 전달할 정보
예를 들어 내가 이렇게 검색한다고 하자.

Query: "초등학생에게 과거시제를 설명하는 자료"
도서관의 모든 책은 Key를 가지고 있다.

책 A Key: 초등 영어, 과거시제, 문법
책 B Key: 성인 회화, 비즈니스 영어
책 C Key: 초등 영어, 현재진행형
Query와 Key가 잘 맞으면 높은 점수를 받는다.

Query와 책 A의 Key → 매우 비슷함
Query와 책 B의 Key → 별로 비슷하지 않음
Query와 책 C의 Key → 일부만 비슷함
그 후 높은 점수를 받은 책의 Value, 즉 실제 내용을 많이 가져온다.

중요한 차이는 이것이다.

Key는 “나를 언제 선택해야 하는가”를 나타내고, Value는 “선택됐을 때 무엇을 전달할 것인가”를 나타낸다.

Key와 Value가 같은 역할이라면 굳이 두 개로 나눌 이유가 없다.

3. Attention 계산식
Transformer의 대표적인 Attention 공식은 다음과 같다.

Attention
(
Q
,
K
,
V
)
=
softmax
(
Q
K
T
d
k
)
V
Attention(Q,K,V)=softmax( 
d 
k
​
 
​
 
QK 
T
 
​
 )V
처음 보면 복잡하지만, 실제로는 네 단계다.

1. Q와 K를 비교한다.
2. 비교 점수를 적당한 크기로 조절한다.
3. Softmax로 중요도 비율을 만든다.
4. 중요도만큼 V를 섞는다.
Transformer 논문은 Query와 모든 Key의 내적을 계산하고, 이를 
d
k
d 
k
​
 
​
 로 나눈 뒤 Softmax를 적용하여 Value의 가중치를 얻는 Scaled Dot-Product Attention을 사용했다. 

3.1 
Q
K
T
QK 
T
 : Query와 Key의 관련도 비교
한 개의 Query 
q
i
q 
i
​
 와 한 개의 Key 
k
j
k 
j
​
 를 비교할 때는 내적을 사용한다.

s
i
j
=
q
i
⋅
k
j
s 
ij
​
 =q 
i
​
 ⋅k 
j
​
 
두 벡터가 비슷한 방향을 향할수록 내적값이 커지는 경향이 있다.

Query와 Key가 잘 맞음    → 높은 점수
Query와 Key가 덜 맞음    → 낮은 점수
Query와 Key가 반대 성격  → 음수 점수 가능
문장에 토큰이 4개라면 모든 토큰이 모든 토큰과 비교되어 다음과 같은 점수 행렬이 생긴다.

Q
K
T
=
[
q
1
k
1
q
1
k
2
q
1
k
3
q
1
k
4
q
2
k
1
q
2
k
2
q
2
k
3
q
2
k
4
q
3
k
1
q
3
k
2
q
3
k
3
q
3
k
4
q
4
k
1
q
4
k
2
q
4
k
3
q
4
k
4
]
QK 
T
 = 
​
  
q 
1
​
 k 
1
​
 
q 
2
​
 k 
1
​
 
q 
3
​
 k 
1
​
 
q 
4
​
 k 
1
​
 
​
  
q 
1
​
 k 
2
​
 
q 
2
​
 k 
2
​
 
q 
3
​
 k 
2
​
 
q 
4
​
 k 
2
​
 
​
  
q 
1
​
 k 
3
​
 
q 
2
​
 k 
3
​
 
q 
3
​
 k 
3
​
 
q 
4
​
 k 
3
​
 
​
  
q 
1
​
 k 
4
​
 
q 
2
​
 k 
4
​
 
q 
3
​
 k 
4
​
 
q 
4
​
 k 
4
​
 
​
  
​
 
행 하나는 다음 질문에 대응한다.

“현재 토큰이 문장 속 각 토큰을 얼마나 참고해야 하는가?”

3.2 왜 
d
k
d 
k
​
 
​
 로 나누는가
Key와 Query의 차원이 커지면 내적값도 커질 가능성이 높다.

예를 들어 각 벡터에 숫자가 64개라면 64개 곱셈 결과를 더한다.

q
⋅
k
=
q
1
k
1
+
q
2
k
2
+
⋯
+
q
64
k
64
q⋅k=q 
1
​
 k 
1
​
 +q 
2
​
 k 
2
​
 +⋯+q 
64
​
 k 
64
​
 
차원이 커지면서 점수의 절댓값이 과도하게 커지면 Softmax 결과가 지나치게 극단적으로 변할 수 있다.

점수: [1, 2, 3]
→ Softmax가 비교적 완만함

점수: [10, 20, 30]
→ 가장 큰 값에 거의 전부 몰림
이 상태에서는 Softmax의 기울기가 작아져 학습이 어려워질 수 있다. Transformer는 이를 완화하기 위해 내적값을 
d
k
d 
k
​
 
​
 로 나눈다. 원 논문은 Query와 Key 성분의 분산을 가정하면 내적의 분산이 
d
k
d 
k
​
 에 비례한다고 설명한다. 

3.3 Softmax: 점수를 비율로 바꾸기
Softmax는 점수를 모두 양수로 바꾸고 합이 1이 되도록 만든다.

예를 들어 점수가 다음과 같다고 하자.

철수는:  1.8
사과를:  2.4
먹었다:  0.7
마침표: -0.3
Softmax 후에는 이런 비율이 될 수 있다.

철수는: 0.31
사과를: 0.56
먹었다: 0.10
마침표: 0.03
합계:   1.00
이 값이 Attention Weight다.

3.4 Value를 가중합한다
현재 토큰이 먹었다라고 하자.

Attention 결과는 다음처럼 계산된다.

z
먹었다
=
0.31
v
철수는
+
0.56
v
사과를
+
0.10
v
먹었다
+
0.03
v
마침표
z 
먹었다
​
 =0.31v 
철수는
​
 +0.56v 
사과를
​
 +0.10v 
먹었다
​
 +0.03v 
마침표
​
 
그러면 먹었다의 새로운 표현 안에는 다음 정보가 들어올 수 있다.

누가 먹었는가?   → 철수
무엇을 먹었는가? → 사과
행동은 무엇인가? → 먹었다
물론 위 숫자는 설명을 위한 가상 값이다. 실제 모델은 학습을 통해 수백·수천 차원의 벡터와 가중치를 결정한다.

4. Self-Attention이란 무엇인가
Attention은 Query와 Key·Value가 어디에서 오느냐에 따라 종류가 달라진다.

일반 Attention 또는 Cross-Attention
Query     → 출력 문장 또는 다른 정보원
Key/Value → 입력 문장
예를 들어 번역 Decoder가 영어 원문을 참고하는 경우다.

한국어 출력 쪽의 상태 → Query
영어 입력 쪽의 상태   → Key, Value
Self-Attention
Query     → 같은 문장
Key       → 같은 문장
Value     → 같은 문장
즉, 같은 입력 
X
X에서 Q, K, V가 모두 만들어진다.

Q
=
X
W
Q
Q=XW 
Q
​
 
K
=
X
W
K
K=XW 
K
​
 
V
=
X
W
V
V=XW 
V
​
 
여기서 Self는 모델이 자아성찰을 한다는 뜻이 아니다.

한 문장 또는 한 시퀀스가 자기 내부의 다른 위치를 참고한다는 뜻이다.

Transformer 논문은 Encoder Self-Attention에서 Q, K, V가 모두 이전 층의 같은 출력에서 오며, 각 위치가 모든 위치를 참고할 수 있다고 정의했다. 반면 Encoder-Decoder Attention에서는 Query가 Decoder에서 오고 Key와 Value는 Encoder 출력에서 온다. 

5. Self-Attention이 문맥을 만드는 과정
다음 문장을 보자.

배가 아파서 배를 먹지 못했다.

두 개의 배가 등장한다.

첫 번째 배 → 신체의 배
두 번째 배 → 과일인 배
처음 단어를 벡터로 바꾸는 임베딩 단계에서는 같은 토큰 배가 기본적으로 비슷한 출발점을 가질 수 있다. 여기에 위치 정보는 다르지만, 아직 문장의 의미를 충분히 반영한 것은 아니다.

Self-Attention을 거치면 첫 번째 배는 다음 단어를 강하게 참고할 수 있다.

첫 번째 배
   ↓
"아파서"를 많이 참고
   ↓
신체 부위의 의미가 강화됨
두 번째 배는 다음 단어를 참고할 수 있다.

두 번째 배
   ↓
"먹지"를 많이 참고
   ↓
먹는 과일의 의미가 강화됨
따라서 같은 글자였더라도 Attention 이후에는 서로 다른 문맥 벡터가 된다.

처리 전:
배₁ ≈ 배₂

처리 후:
배₁ = 신체·통증 문맥을 반영한 벡터
배₂ = 음식·섭취 문맥을 반영한 벡터
이것이 Transformer가 단어를 고정된 사전 뜻으로만 처리하지 않고, 문맥 속 의미로 재표현하는 핵심 과정이다.

6. Q, K, V는 누가 만드는가
각 토큰에는 처음에 하나의 벡터가 있다.

예를 들어 토큰이 4개이고 벡터 크기가 8이라면:

X
∈
R
4
×
8
X∈R 
4×8
 
          차원 8개
철수는  [........]
사과를  [........]
먹었다  [........]
.       [........]
이 하나의 입력 벡터에 서로 다른 학습 행렬을 곱해 Q, K, V를 만든다.

X × WQ → Q
X × WK → K
X × WV → V
왜 같은 입력에서 세 가지를 따로 만드는가?

같은 사람이 회의에서 세 역할을 가질 수 있다고 생각하면 된다.

Query 역할:
"나는 지금 어떤 정보가 필요한가?"

Key 역할:
"다른 사람이 나를 어떤 질문에 참고하면 되는가?"

Value 역할:
"내가 선택됐을 때 실제로 전달할 내용은 무엇인가?"
WQ, WK, WV는 학습되는 파라미터다. 사람이 문법 규칙을 직접 넣는 것이 아니라, 훈련 중 오차를 줄이는 방향으로 값이 조정된다.

7. 행렬 크기로 보면 정확히 무엇이 일어나는가
토큰 4개, 모델 차원 8, Attention Head 하나의 차원 4라고 하자.

X   : 4 × 8
WQ  : 8 × 4
WK  : 8 × 4
WV  : 8 × 4
곱하면:

Q = XWQ : 4 × 4
K = XWK : 4 × 4
V = XWV : 4 × 4
그다음:

Q     : 4 × 4
Kᵀ    : 4 × 4
QKᵀ   : 4 × 4
이 4 × 4가 모든 토큰 쌍의 관계를 담은 Attention Score 행렬이다.

                참고 대상
             철수는 사과를 먹었다  .
질문 철수는     □     □     □    □
주체 사과를     □     □     □    □
토큰 먹었다     □     □     □    □
     .          □     □     □    □
Softmax를 행별로 적용한 후 Value와 곱한다.

Attention Weight : 4 × 4
V                : 4 × 4
결과              : 4 × 4
각 토큰마다 문장 전체를 참고한 새로운 벡터 하나가 나온다.

8. 실제 코드로 보면 네 줄이다
핵심 계산만 쓰면 다음과 같다.

scores = Q @ K.transpose(-2, -1)
scores = scores / math.sqrt(d_k)
weights = torch.softmax(scores, dim=-1)
output = weights @ V
각 줄은 다음 의미다.

scores = Q @ K.transpose(-2, -1)
현재 Query와 모든 Key를 비교한다.

scores = scores / math.sqrt(d_k)
값이 지나치게 커지지 않도록 조절한다.

weights = torch.softmax(scores, dim=-1)
각 Query가 모든 Key에 배분할 중요도 비율을 만든다.

output = weights @ V
중요도에 따라 실제 정보인 Value를 섞는다.

Mask까지 넣으면 대략 다음 구조가 된다.

scores = Q @ K.transpose(-2, -1)
scores = scores / math.sqrt(d_k)

scores = scores.masked_fill(mask == 0, float("-inf"))

weights = torch.softmax(scores, dim=-1)
output = weights @ V
9. Masked Self-Attention은 무엇인가
GPT처럼 다음 토큰을 예측하는 모델은 미래의 정답을 미리 보면 안 된다.

문장이 다음과 같다고 하자.

철수는 사과를 먹었다
철수는 위치에서 다음 단어를 예측할 때 사과를 먹었다를 미리 보면 부정행위다.

그래서 미래 위치를 가린다.

현재 위치	볼 수 있는 토큰
철수는	철수는
사과를	철수는, 사과를
먹었다	철수는, 사과를, 먹었다
행렬로 나타내면 다음과 같다.

               참고할 위치
              1   2   3   4
현재 위치 1   ○   ×   ×   ×
현재 위치 2   ○   ○   ×   ×
현재 위치 3   ○   ○   ○   ×
현재 위치 4   ○   ○   ○   ○
금지된 위치의 점수를 -∞로 만든다.

Softmax(-∞) ≈ 0
따라서 미래 토큰에 부여되는 Attention Weight는 0이 된다.

Transformer의 Decoder는 이 방식으로 현재 위치가 이후 위치를 참고하지 못하도록 한다. 이를 통해 위치 
i
i의 예측은 
i
i보다 앞에 있는 출력에만 의존한다. 

Padding Mask도 있다
문장 길이가 서로 다르면 짧은 문장 뒤에 [PAD]를 붙여 길이를 맞추기도 한다.

문장 A: 나는 학교에 갔다
문장 B: 안녕 [PAD] [PAD] [PAD]
모델이 [PAD]를 실제 정보처럼 참고해서는 안 된다.

그래서 Padding 위치도 Attention Score를 -∞로 만들어 무시한다.

즉 Mask에는 대표적으로 두 목적이 있다.

Causal Mask  → 미래를 보지 못하게 함
Padding Mask → 빈칸을 보지 못하게 함
10. Full Self-Attention과 Causal Self-Attention의 차이
Full 또는 Bidirectional Self-Attention
모든 위치가 앞뒤를 모두 볼 수 있다.

"나는 [MASK]에 갔다"

[MASK]는
앞의 "나는"도 보고
뒤의 "갔다"도 본다.
문장 이해와 표현 생성에 유리하다.

BERT는 모든 층에서 좌우 문맥을 함께 조건으로 사용하는 깊은 양방향 Transformer 표현을 학습하도록 설계됐다. 

Causal Self-Attention
현재와 과거만 볼 수 있다.

입력: 나는 학교에
예측: 갔다
GPT 계열의 언어모델은 Transformer Decoder 구조와 Masked Self-Attention을 사용해 이전 토큰을 바탕으로 다음 토큰을 예측한다. 초기 GPT 논문에서도 다층 Transformer Decoder와 Masked Self-Attention을 사용한다고 명시했다. 

중요한 구분은 이것이다.

Self-Attention 자체가 양방향인 것이 아니라, 어떤 Mask를 사용하느냐에 따라 양방향 또는 단방향이 된다.

11. Multi-Head Attention은 무엇인가
Attention Head 하나만 있으면 모든 관계를 하나의 시각으로 압축해야 한다.

하지만 문장에는 여러 관계가 동시에 존재한다.

철수가 어제 학교에서 영희에게 책을 주었다.

이 문장에는 다음과 같은 관계가 있다.

주체 관계: 철수 ↔ 주었다
시간 관계: 어제 ↔ 주었다
장소 관계: 학교에서 ↔ 주었다
수여 대상: 영희에게 ↔ 주었다
목적어 관계: 책을 ↔ 주었다
Multi-Head Attention은 서로 다른 WQ, WK, WV를 사용하는 Attention을 여러 개 병렬로 계산한다.

head
i
=
Attention
(
Q
W
i
Q
,
K
W
i
K
,
V
W
i
V
)
head 
i
​
 =Attention(QW 
i
Q
​
 ,KW 
i
K
​
 ,VW 
i
V
​
 )
그 결과를 이어 붙인다.

MultiHead
(
Q
,
K
,
V
)
=
Concat
(
head
1
,
…
,
head
h
)
W
O
MultiHead(Q,K,V)=Concat(head 
1
​
 ,…,head 
h
​
 )W 
O
 
Transformer 원 논문은 서로 다른 학습된 선형 투영으로 Q, K, V를 여러 번 변환하고, 각 Attention 결과를 이어 붙인 뒤 다시 투영했다. 이를 통해 서로 다른 위치와 표현 공간의 정보를 동시에 참고할 수 있도록 했다. 

여러 명의 분석관으로 비유할 수 있다
Head 1: 주어와 동사의 관계를 주로 본다.
Head 2: 가까운 단어를 주로 본다.
Head 3: 대명사가 누구를 가리키는지 본다.
Head 4: 시간 표현을 본다.
...
다만 이것은 이해를 위한 비유다.

실제 모델에서 특정 Head가 반드시 “주어 담당”, “대명사 담당”처럼 깔끔하게 나뉘는 것은 아니다. 여러 Head와 여러 층의 정보가 함께 작동한다.

Multi-Head의 본질은 여러 종류의 관계를 서로 다른 투영 공간에서 동시에 탐색하는 것이다.

12. 위치 정보가 왜 필요한가
Self-Attention은 기본적으로 모든 토큰을 한꺼번에 비교한다. 그런데 Q·K·V 계산만으로는 단어의 순서를 충분히 알 수 없다.

다음 두 문장은 단어 종류는 비슷하지만 의미가 반대다.

개가 사람을 물었다.
사람이 개를 물었다.
위치 정보가 없다면 모델은 단어들의 집합만 보게 된다.

{개, 사람, 물었다}
그래서 입력 임베딩에 위치 벡터를 더한다.

x
i
=
TokenEmbedding
(
t
o
k
e
n
i
)
+
PositionEncoding
(
i
)
x 
i
​
 =TokenEmbedding(token 
i
​
 )+PositionEncoding(i)
"개"라는 단어 정보
+
"1번째 위치"라는 정보
=
실제 Transformer 입력
원래 Transformer는 사인·코사인 함수를 사용하는 Positional Encoding을 입력 임베딩에 더했다. 논문은 순환이나 합성곱이 없기 때문에 토큰의 절대적 또는 상대적 순서 정보를 별도로 넣어야 한다고 설명한다. 

13. 이제 Transformer 전체를 보자
Transformer는 Self-Attention 하나만을 뜻하지 않는다.

원래 Transformer는 다음 부품으로 구성된다.

1. Token Embedding
2. Positional Encoding
3. Multi-Head Attention
4. Feed-Forward Network
5. Residual Connection
6. Layer Normalization
7. 여러 층의 반복
8. 출력 Linear + Softmax
원 논문의 Transformer는 왼쪽 Encoder와 오른쪽 Decoder로 구성되며, Encoder와 Decoder 모두 Attention과 Position-wise Feed-Forward Network를 여러 층 쌓는다. 

14. Transformer Encoder 구조
Encoder Layer 하나는 크게 두 부분이다.

입력 X
  ↓
Multi-Head Self-Attention
  ↓
Add & Norm
  ↓
Feed-Forward Network
  ↓
Add & Norm
  ↓
다음 Encoder Layer
수식으로 단순화하면 다음과 같다.

h
1
=
LayerNorm
(
x
+
MultiHeadAttention
(
x
)
)
h 
1
​
 =LayerNorm(x+MultiHeadAttention(x))
h
2
=
LayerNorm
(
h
1
+
FFN
(
h
1
)
)
h 
2
​
 =LayerNorm(h 
1
​
 +FFN(h 
1
​
 ))
원래 Transformer는 이를 다음 공식으로 표현했다.

LayerNorm
(
x
+
Sublayer
(
x
)
)
LayerNorm(x+Sublayer(x))
여기서 Sublayer는 Multi-Head Attention 또는 FFN이다. 

15. Attention과 FFN은 역할이 다르다
이 차이가 굉장히 중요하다.

Attention: 토큰끼리 정보를 교환한다
"먹었다"가
"철수는"과 "사과를"의 정보를 가져온다.
Attention은 문장 속 서로 다른 위치를 섞는다.

Attention = 토큰 간 통신

FFN: 가져온 정보를 각 토큰 내부에서 가공한다
Attention으로 정보를 받아온 뒤, 각 토큰의 벡터를 별도로 변환한다.

FFN = 각 토큰의 개별 사고

원래 Transformer의 FFN은 다음 형태다.

FFN
(
x
)
=
max
⁡
(
0
,
x
W
1
+
b
1
)
W
2
+
b
2
FFN(x)=max(0,xW 
1
​
 +b 
1
​
 )W 
2
​
 +b 
2
​
 
첫 번째 Linear Layer로 차원을 확장하고, ReLU를 적용한 다음 두 번째 Linear Layer로 원래 차원으로 줄인다. 같은 층 안에서는 모든 토큰 위치에 동일한 FFN 파라미터를 적용하지만, 토큰들은 서로 섞이지 않고 각자 통과한다. 

회의와 개인 업무로 기억하면 된다
Self-Attention:
회의를 열어 다른 단어들의 정보를 가져온다.

FFN:
회의가 끝난 뒤 각 단어가 받은 정보를 자기 방식으로 가공한다.
그리고 이 과정을 여러 층 반복한다.

회의 → 개별 가공
회의 → 개별 가공
회의 → 개별 가공
...
한 번의 Attention으로 모든 언어 관계가 완성되는 것이 아니라, 여러 층을 거치며 표현이 계속 갱신된다.

16. Residual Connection은 무엇인가
Residual Connection은 입력을 Sublayer 출력에 그대로 더하는 것이다.

y
=
x
+
Sublayer
(
x
)
y=x+Sublayer(x)
왜 그냥 Sublayer 출력만 쓰지 않을까?

Sublayer가 현재 정보를 잘못 변형하더라도 원래 입력 x가 남아 있게 하기 위해서다.

문서 수정으로 비유하면:

기존 문서 전체를 지우고 새로 작성
→ 정보 손실 위험이 큼

기존 문서 + 수정사항
→ 원본을 보존하면서 개선
Residual Connection은 다음 역할을 한다.

기존 정보의 보존
깊은 층으로 정보가 흐를 경로 제공
기울기가 역방향으로 전달될 경로 제공
각 층이 전체 표현이 아니라 수정분을 학습할 수 있게 함
그래서 Transformer의 Sublayer는 기존 벡터를 완전히 교체한다기보다, 기존 벡터에 수정사항을 추가하는 것으로 생각할 수 있다.

17. Layer Normalization은 무엇인가
Residual로 값을 계속 더하면 벡터 크기와 분포가 층마다 달라질 수 있다.

Layer Normalization은 토큰 하나의 Hidden Dimension들을 기준으로 값을 정규화한다.

예를 들어 한 토큰 벡터가 다음처럼 생겼다면:

[4.2, -1.1, 8.7, 0.3, ...]
평균과 분산을 이용해 일정한 범위로 정리한 뒤, 학습 가능한 Scale과 Bias를 적용한다.

입력 크기가 층마다 지나치게 흔들리는 것을 완화
학습을 안정화
깊은 구조에서 값의 스케일을 관리
원래 Transformer 그림의 Add & Norm은 다음 순서다.

Sublayer 계산
→ 원래 입력 더하기
→ LayerNorm
즉 원 논문 기준으로는:

LayerNorm
(
x
+
Sublayer
(
x
)
)
LayerNorm(x+Sublayer(x))
이다. 이후 Transformer 변형에서는 LayerNorm의 위치가 달라진 구조도 있지만, 원 논문 그림은 위와 같은 순서다. 

18. Transformer Decoder 구조
원래 Transformer Decoder Layer에는 세 가지 주요 Sublayer가 있다.

출력 쪽 입력
   ↓
Masked Multi-Head Self-Attention
   ↓
Add & Norm
   ↓
Encoder-Decoder Cross-Attention
   ↓
Add & Norm
   ↓
Feed-Forward Network
   ↓
Add & Norm
각 역할은 다음과 같다.

① Masked Self-Attention
지금까지 생성된 출력 단어들만 본다.

나는 학교에
→ 미래 단어는 보지 못함
② Cross-Attention
Decoder가 Encoder의 입력 문장 표현을 본다.

Decoder 상태 → Query
Encoder 출력 → Key, Value
번역이라면 한국어를 생성하는 Decoder가 영어 원문을 참고하는 단계다.

③ FFN
참고한 정보를 각 출력 위치 안에서 비선형적으로 가공한다.

원래 Transformer Decoder는 Encoder의 두 Sublayer에 Encoder 출력을 참조하는 Multi-Head Attention Sublayer를 추가하고, 미래 위치를 보지 못하도록 Decoder Self-Attention을 Masking했다. 

19. Encoder-only, Decoder-only, Encoder-Decoder
원래 Transformer의 Encoder와 Decoder를 어떻게 조합하느냐에 따라 대표적인 모델 종류가 나뉜다.

구조	대표 예	Attention 방식	주된 성격
Encoder-only	BERT	양방향 Self-Attention	문장 표현·분류·이해
Decoder-only	GPT	Causal Self-Attention	다음 토큰 예측·텍스트 생성
Encoder-Decoder	원래 Transformer, T5	Encoder Self-Attention + Decoder Self-Attention + Cross-Attention	입력을 다른 출력으로 변환
BERT는 좌우 문맥을 함께 보는 깊은 양방향 Transformer Encoder를 사용한다. GPT는 Masked Self-Attention을 사용하는 Transformer Decoder를 언어모델로 사용한다. T5는 입력을 Encoder로 처리하고 별도의 Decoder가 텍스트 출력을 생성하는 Encoder-Decoder 계열이다. 

Encoder-only
문장 전체
   ↓
앞뒤 문맥을 모두 보는 Encoder
   ↓
각 토큰 또는 문장 전체의 표현
   ↓
분류·검색·개체 인식 등
예:

이 리뷰는 긍정인가?
이 두 문장은 같은 의미인가?
문장에서 사람 이름은 무엇인가?
Decoder-only
현재까지의 토큰
   ↓
미래를 가린 Decoder
   ↓
다음 토큰 확률
   ↓
한 토큰 선택
   ↓
입력 뒤에 붙이고 반복
GPT 같은 생성형 언어모델의 기본 구조다.

Encoder-Decoder
입력 문장
   ↓
Encoder가 전체 입력 표현
   ↓
Decoder가 Cross-Attention으로 참고
   ↓
출력 문장을 하나씩 생성
번역, 요약, 문장 변환과 자연스럽게 맞는다.

20. GPT가 실제 답을 만드는 과정
사용자가 다음을 입력했다고 하자.

철수는 사과를

1단계: 토큰화
["철수", "는", "사과", "를"]
실제 토큰 분할은 사용하는 Tokenizer에 따라 다를 수 있다.

2단계: 임베딩과 위치 정보
토큰 임베딩 + 위치 정보
각 토큰이 벡터가 된다.

3단계: 여러 Transformer Block 통과
Masked Self-Attention
→ Residual/Norm
→ FFN
→ Residual/Norm
이 과정을 여러 층 반복한다.

4단계: 마지막 위치의 벡터 사용
현재 마지막 토큰인 를 위치의 벡터에는 앞 문맥 정보가 들어 있다.

철수
사과
목적격 조사
문장 구조
학습된 언어 패턴
5단계: 모든 어휘에 대한 점수 생성
먹었다:  8.3
샀다:    5.2
보았다:  3.8
달렸다: -1.2
...
6단계: 확률 변환 후 다음 토큰 선택
먹었다: 72%
샀다:   14%
보았다:  6%
...
선택된 토큰을 뒤에 붙인다.

철수는 사과를 먹었다
그다음 다시 다음 토큰을 예측한다.

철수는 사과를 먹었다 .
이것이 Autoregressive Generation이다.

21. 훈련과 생성은 병렬성에서 다르다
훈련 시
정답 문장 전체를 이미 알고 있다.

입력: [나는] [학교에] [갔다]
정답: [학교에] [갔다]  [.]
Causal Mask를 사용하면 각 위치가 미래 정답을 보지 못하게 하면서도, GPU에서는 여러 위치의 계산을 큰 행렬 연산으로 동시에 수행할 수 있다.

실제 생성 시
두 번째 토큰을 생성하려면 첫 번째 토큰이 먼저 결정되어야 한다.

1. "나는" 다음 토큰 생성
2. 생성된 토큰을 입력에 추가
3. 그다음 토큰 생성
4. 반복
따라서 Transformer는 RNN보다 훈련을 병렬화하기 좋지만, Decoder-only 모델의 실제 Autoregressive 생성 자체는 여전히 토큰 순서대로 진행된다. 원 Transformer 논문도 Decoder가 이전에 생성한 기호를 입력으로 받아 출력 시퀀스를 한 요소씩 생성한다고 설명한다. 

22. KV Cache와 vLLM이 여기서 연결된다
GPT가 다음 문장을 생성한다고 하자.

나는 오늘 학교에
이제 갔다를 생성하려 한다.

Self-Attention에는 앞 토큰들의 Key와 Value가 필요하다.

K나는, K오늘, K학교에
V나는, V오늘, V학교에
이 값들은 이전 단계에서 이미 계산했다. 다음 토큰을 생성할 때 전부 다시 계산하면 낭비다.

그래서 이전 토큰의 Key와 Value를 저장한다.

KV Cache
=
이전에 계산한 모든 토큰의 Key와 Value
새 토큰이 들어오면 새 Query를 만들고 저장된 Key들과 비교한다.

새 Query
   ↓
기존 Key들과 Attention 계산
   ↓
기존 Value들을 가중합
정확히는 Transformer의 각 층과 Attention 구조에 필요한 K·V가 저장된다.

vLLM의 PagedAttention은 모델의 Attention 원리를 바꾸는가
아니다.

Transformer Attention:
Q, K, V를 어떻게 계산하고 섞는가

vLLM PagedAttention:
계산된 K와 V를 GPU 메모리에 어떻게 효율적으로 저장하고 꺼내는가
vLLM은 요청별 KV Cache를 일정한 블록으로 나누고, 물리적으로 연속되지 않은 메모리에도 저장할 수 있도록 관리한다. 이는 KV Cache의 메모리 단편화와 낭비를 줄이기 위한 서빙 최적화다. 

따라서 이름은 모두 Attention이지만 층위가 다르다.

Self-Attention은 모델의 정보처리 계산이고, PagedAttention은 그 계산을 서비스할 때 KV Cache 메모리를 관리하는 기술이다.

23. Transformer가 강력했던 이유
① 모든 토큰이 직접 연결될 수 있다
Full Self-Attention에서는 한 층 안에서 먼 위치의 토큰끼리도 직접 정보를 주고받을 수 있다.

문장 첫 단어 ↔ 문장 마지막 단어
RNN처럼 중간 Hidden State를 순서대로 여러 번 거칠 필요가 없다.

② 행렬 연산에 적합하다
모든 Query와 Key를 QKᵀ라는 큰 행렬곱으로 계산할 수 있다.

GPU는 이런 대규모 행렬 연산을 매우 잘 처리한다.

③ 역할이 분리되어 있다
Attention → 토큰 간 정보 교환
FFN       → 토큰 내부 정보 변환
Position  → 순서 제공
Residual  → 기존 정보 보존
LayerNorm → 값의 안정화
각 부품이 비교적 명확한 역할을 갖는다.

④ 같은 구조를 반복해서 크게 확장할 수 있다
Transformer Block × N
층 수, Hidden Dimension, Head 수, FFN 크기 등을 늘려 모델 규모를 확장할 수 있다.

원 Transformer 논문은 순환과 합성곱을 제거하고 Attention을 중심으로 구성함으로써 훈련 시 더 높은 병렬성을 확보하는 구조를 제시했다. 

24. Transformer의 한계도 있다
① 기본 Full Attention은 문장이 길어질수록 비싸진다
토큰 수가 
n
n개면 모든 토큰 쌍을 비교한다.

n
×
n
n×n
1,000토큰  → 약 100만 개 관계
10,000토큰 → 약 1억 개 관계
표준 Self-Attention의 주요 계산량은 대략 다음과 같다.

O
(
n
2
d
)
O(n 
2
 d)
원 논문의 복잡도 비교표도 Self-Attention의 층당 복잡도를 
O
(
n
2
d
)
O(n 
2
 d)로 제시했다. 

② 순서를 별도로 넣어야 한다
Self-Attention만으로는 토큰 순서를 충분히 알 수 없으므로 위치 정보가 필요하다.

③ 생성은 여전히 순차적이다
다음 토큰이 결정되어야 그다음 토큰을 만들 수 있다.

④ Attention이 사실성을 보장하지 않는다
Attention은 관련 정보를 섞는 계산 방식이다.

사실 검증
논리적 정당성
환각 방지
교육적으로 올바른 설명
이런 것들을 자동으로 보장하는 장치는 아니다. 그것은 훈련 데이터, 학습 목표, 후속 훈련, RAG, 출력 검증 같은 다른 설계와 관련된다.

25. 자주 생기는 오해
오해	실제
Attention은 인간처럼 의식적으로 집중한다	벡터 유사도와 가중합 계산이다
Self-Attention은 AI가 자기 생각을 성찰한다	같은 시퀀스 내부 위치를 참고한다
Q·K·V는 실제 질문·정답 문장이다	각 층에서 학습된 선형변환으로 만들어지는 벡터다
Attention Weight가 곧 모델 판단의 완전한 이유다	한 Head·한 층의 중간 가중치일 뿐이다
Head 하나마다 문법 기능 하나가 정해진다	사람이 기능을 지정하지 않으며 역할이 섞일 수 있다
Transformer가 곧 LLM이다	Transformer는 구조이고, LLM은 그 구조를 대규모 데이터로 학습한 언어모델이다
GPT는 문장 전체를 양방향으로 본다	일반적으로 미래 위치를 가리는 Causal Attention을 쓴다
vLLM의 PagedAttention이 모델을 더 똑똑하게 만든다	KV Cache를 효율적으로 관리하는 서빙 기술이다
특히 Attention Weight를 그대로 “이 단어 때문에 이런 결정을 했다”라고 해석하면 조심해야 한다. 최종 출력에는 Value 변환, 여러 Head의 결합, Residual, FFN, 이후 여러 층의 계산이 모두 관여하기 때문이다.

26. 전체 과정을 하나의 그림으로 압축하면
문장
"철수는 사과를 먹었다"
        ↓
Tokenizer
        ↓
Token Embedding + Position
        ↓
┌────────────────────────────┐
│ Multi-Head Self-Attention  │  ← 토큰끼리 정보 교환
│ Add & LayerNorm            │
│ Feed-Forward Network       │  ← 각 토큰 내부 정보 가공
│ Add & LayerNorm            │
└────────────────────────────┘
        ↓
      여러 층 반복
        ↓
문맥이 반영된 토큰 표현
        ↓
Linear
        ↓
Softmax
        ↓
다음 토큰 확률 또는 다른 예측
Decoder-only LLM이라면 이 과정을 다음 토큰마다 반복한다.

프롬프트
  ↓
Transformer
  ↓
다음 토큰
  ↓
프롬프트 뒤에 추가
  ↓
Transformer
  ↓
그다음 토큰
최종 정리
Attention
관련도 계산
→
중요도 비율
→
Value 가중합
관련도 계산→중요도 비율→Value 가중합
필요한 정보를 골라서 가져오는 계산

Self-Attention
Q
=
X
W
Q
,
K
=
X
W
K
,
V
=
X
W
V
Q=XW 
Q
​
 ,K=XW 
K
​
 ,V=XW 
V
​
 
문장의 각 토큰이 같은 문장의 다른 토큰을 참고해 문맥적 표현을 만드는 것

Multi-Head Attention
서로 다른 투영 공간에서 여러 종류의 관계를 동시에 찾는 것

Transformer Block
Self-Attention
+ FFN
+ Residual Connection
+ LayerNorm
+ Position 정보
토큰 간 소통과 토큰 내부 가공을 반복하는 구조

GPT 같은 LLM
Causal Self-Attention을 사용하는 Transformer Block을 많이 쌓고, 다음 토큰 예측을 대규모 데이터로 학습한 모델

vLLM
이 Transformer 모델을 바꾸는 것이 아니라, Transformer가 생성 중 사용하는 KV Cache와 GPU 요청을 효율적으로 관리하는 실행·서빙 엔진

가장 기억하기 좋은 표현은 이것이다.

Attention은 “누구 말을 들을지” 정하고, Value는 “그 사람에게서 무슨 내용을 받을지” 결정한다. Self-Attention은 문장 안의 단어들이 서로 회의하는 것이고, Transformer는 그 회의와 개별 사고를 여러 층 반복하는 조직이다.






소스


---

## 2. Transformer 추론을 GPU에서 운영하기: vLLM

앞 장의 Transformer가 실제 답변을 만드는 모델 구조라면, 이제 여러 사용자의 요청이 GPU에서 충돌하지 않도록 실행하는 계층을 살펴본다. 다음 내용은 vLLM이 모델 자체가 아니라 추론·서빙 엔진이라는 구분에서 출발한다.

6m 12s 동안 처리함
vLLM이란 무엇인가
핵심부터 말하면,

vLLM은 LLM 자체가 아니라, Llama·Qwen 같은 대규모 언어모델을 GPU에서 빠르고 효율적으로 실행해 API로 제공하는 추론·서빙 엔진이다.

예를 들어 Qwen은 두뇌, GPU는 두뇌가 계산하는 기계, vLLM은 여러 사용자의 요청을 받아 GPU가 쉬지 않고 효율적으로 일하도록 관리하는 운영 시스템에 가깝다. vLLM은 UC Berkeley의 Sky Computing Lab에서 시작됐으며, 현재는 오픈소스 프로젝트로 개발되고 있다. 

1. vLLM의 위치부터 정확히 잡자
LLM 서비스를 만들 때 각 부품의 역할은 다음과 같다.

사용자
  ↓
EDENING 같은 웹·앱
  ↓
FastAPI / Spring Boot / LangChain
  ↓
vLLM API 서버
  ↓
Qwen / Llama / Gemma 등의 모델
  ↓
GPU
여기서:

Qwen, Llama, Gemma: 실제 답변을 만드는 모델
vLLM: 모델을 GPU에 올리고 요청을 처리하는 서버
LangChain: RAG나 도구 호출 같은 전체 작업 흐름을 구성
FastAPI·Spring Boot: 회원, 권한, 결제, 학습 기록 등 서비스 로직 담당
벡터 데이터베이스: 관련 문서를 검색
GPU: 실제 행렬 계산 수행
따라서 vLLM은 다음 중 어느 것도 아니다.

새로운 언어모델
모델 훈련 도구
파인튜닝 도구
벡터 데이터베이스
RAG 프레임워크
OpenAI처럼 모델 사용량을 판매하는 클라우드 서비스
vLLM은 RAG에서도 모델 추론, 임베딩, 재정렬 같은 개별 추론 작업을 맡을 수 있지만, 문서 분할·검색·프롬프트 조립 등 전체 RAG 파이프라인을 구성해 주지는 않는다. 

2. 왜 그냥 모델을 실행하지 않고 vLLM을 쓰는가
Hugging Face Transformers로도 모델을 실행할 수 있다.

model.generate(...)
개인 실습에서 질문 하나를 넣고 답변 하나를 받는 정도라면 이것으로 충분하다.

하지만 실제 서비스에서는 상황이 달라진다.

학생 A: 짧은 질문, 20토큰 답변
학생 B: 긴 문서 입력, 500토큰 답변
학생 C: 대화를 10번 이어감
학생 D: 중간에 연결 종료
학생 E: 방금 새로 접속
요청마다 입력 길이와 출력 길이가 다르고, 요청이 들어오는 시점도 다르다. 단순하게 처리하면 GPU 메모리가 낭비되고, 한 요청이 끝날 때까지 다른 요청이 기다리며, GPU 사용률도 떨어질 수 있다.

vLLM은 이 문제를 다음 기술로 해결한다.

PagedAttention
Continuous Batching
KV Cache 관리
Prefix Caching
양자화와 다중 GPU 병렬 처리
3. 가장 중요한 개념: KV Cache
LLM은 답변을 한 번에 완성하지 않는다.

예를 들어:

사용자: 대한민국의 수도는?
모델은 다음처럼 한 토큰씩 생성한다.

대한
대한민국
대한민국의
대한민국의 수도
대한민국의 수도는
대한민국의 수도는 서울
...
새 토큰을 만들 때마다 앞에서 읽었던 모든 토큰의 계산을 처음부터 반복한다면 엄청나게 비효율적이다.

그래서 LLM은 이전 토큰에 대해 계산한 Attention의 Key와 Value 값을 GPU 메모리에 저장한다. 이것이 KV Cache다.

쉽게 표현하면:

KV Cache는 모델이 앞에서 읽은 내용을 다시 계산하지 않도록 보관하는 계산 메모장이다.

문제는 대화가 길어질수록 KV Cache가 커지고, 동시 사용자가 많아질수록 사용자마다 별도의 KV Cache가 필요하다는 것이다.

긴 문맥
×
많은 동시 사용자
×
큰 모델
=
엄청난 GPU 메모리 사용
그래서 LLM 서빙에서는 모델 가중치뿐 아니라 KV Cache를 얼마나 효율적으로 관리하느냐가 대단히 중요하다.

4. PagedAttention이 무엇인가
기존 방식에서는 한 사용자의 KV Cache가 커질 것을 예상해 GPU 메모리의 연속된 공간을 크게 예약하는 경우가 많았다.

그런데 실제 생성 길이는 알 수 없다.

사용자 A: 1,000토큰을 예상했지만 80토큰에서 종료
사용자 B: 300토큰을 예상했지만 700토큰까지 생성
사용자 C: 생성 도중 연결 종료
이렇게 되면 빈 공간이 여기저기 생긴다. 이를 메모리 단편화라고 한다.

vLLM의 PagedAttention은 운영체제의 가상 메모리 방식에서 아이디어를 가져왔다.

기존 방식
A 요청: [████████████          ]
B 요청: [██████                ]
C 요청: [████████████████      ]
각 요청에 연속된 큰 공간을 마련한다.

PagedAttention 방식
GPU 메모리 블록

[ A1 ][ B1 ][ C1 ][ A2 ][ C2 ][ B2 ][ A3 ][ 빈칸 ]
KV Cache를 작은 고정 크기 블록으로 나누고, 물리적으로 떨어진 블록도 논리적으로 하나의 연속된 공간처럼 사용한다.

즉:

A 사용자의 KV Cache가 GPU 메모리에서 반드시 한 덩어리로 붙어 있을 필요가 없다.

그래서 필요한 만큼만 블록을 할당하고, 요청이 끝나면 해당 블록을 바로 다른 요청에 사용할 수 있다. 원 논문은 이를 통해 KV Cache 낭비를 거의 없애고 동시 처리 가능한 요청 수를 늘렸다고 설명한다. 2023년 논문의 당시 비교 실험에서는 동일한 지연 수준에서 기존 시스템보다 2~4배 높은 처리량을 보고했지만, 이는 당시 모델·하드웨어·비교 시스템을 기준으로 한 결과이지 모든 환경에서 보장되는 숫자는 아니다. 

5. Continuous Batching이 무엇인가
일반적인 배치 처리는 요청을 일정량 모은 뒤 함께 처리한다.

A, B, C, D 요청을 기다림
→ 네 개를 한꺼번에 처리
→ 모두 끝나야 다음 배치 시작
그런데 B가 짧은 답변을 생성해 먼저 끝나도, 그 자리가 바로 활용되지 않을 수 있다.

vLLM의 Continuous Batching, 즉 연속 배치는 요청이 끝난 자리에 새 요청을 계속 투입한다.

1단계: A B C D
2단계: A B C D
3단계: A E C D    ← B가 끝난 자리에 E 투입
4단계: F E C D    ← A가 끝난 자리에 F 투입
식당으로 비유하면, 모든 손님이 식사를 끝낼 때까지 빈 테이블을 놔두는 것이 아니라 손님이 나가는 즉시 새 손님을 받는 방식이다.

이 방식은 동시 요청이 많을수록 GPU 활용률과 전체 처리량을 높이는 데 유리하다. vLLM의 엔진은 스케줄러가 요청을 지속적으로 선택하고, KV Cache를 관리하며, GPU 작업 프로세스에 실행을 전달하는 구조로 되어 있다. 

6. Prefill과 Decode
LLM 추론은 크게 두 단계로 나뉜다.

Prefill
사용자가 넣은 전체 입력을 읽는 단계다.

"다음 영어 문장에서 틀린 부분을 찾아 설명해줘..."
입력 토큰을 한꺼번에 처리하고 KV Cache를 만든다.

긴 PDF, 긴 대화 기록, 많은 RAG 문서를 넣으면 Prefill 계산량이 커진다.

Decode
답변을 한 토큰씩 생성하는 단계다.

The → sentence → should → use → ...
Prefill보다 한 번의 계산은 작지만, 토큰마다 반복 실행해야 한다.

따라서 서비스 성능을 평가할 때는 단순히 “답변이 몇 초 걸렸다”보다 다음을 구분해야 한다.

TTFT: 첫 번째 토큰이 나오기까지 걸린 시간
TPOT 또는 ITL: 토큰과 토큰 사이의 생성 시간
Throughput: 전체 사용자를 합쳐 초당 몇 토큰을 처리하는지
동시 처리량: 몇 명을 동시에 감당하는지
vLLM은 특히 여러 요청을 함께 처리할 때의 전체 처리량을 높이는 데 강점이 있다.

7. Prefix Caching
EDENING에서 모든 학생에게 다음과 같은 긴 시스템 지시를 보낸다고 가정해 보자.

너는 초등학생의 영어 문장을 교정하는 튜터다.
학습자의 수준은 CEFR A1이다.
정답을 바로 알려주기 전에...
[이하 긴 공통 지시문]
학생마다 질문은 다르지만 앞부분은 같다.

일반적으로는 학생이 요청할 때마다 이 공통 지시문을 다시 계산해야 한다. vLLM의 Automatic Prefix Caching은 이전 요청과 동일한 앞부분이 있다면 기존 KV Cache를 재사용하여 공통 부분의 계산을 건너뛸 수 있다. 

다음과 같은 환경에서 효과가 크다.

모든 사용자에게 동일한 긴 시스템 프롬프트 사용
동일한 문서를 두고 여러 질문을 하는 RAG
멀티턴 대화
동일한 few-shot 예시를 반복 사용
학습 과정별 고정된 교수 지침 사용
다만 Prefix Caching은 주로 입력 처리 비용과 첫 토큰 대기시간을 줄인다. 새로운 답변 토큰을 생성하는 Decode 작업 자체가 사라지는 것은 아니다.

8. vLLM은 OpenAI API처럼 사용할 수 있다
vLLM의 실용적인 장점 중 하나는 OpenAI 호환 API 서버를 제공한다는 점이다.

예를 들어 서버에서 다음 명령을 실행한다.

vllm serve Qwen/Qwen2.5-1.5B-Instruct \
  --api-key local-secret-key
기본적으로 로컬의 8000번 포트에서 서버가 실행된다.

그러면 기존 OpenAI Python SDK를 거의 그대로 사용할 수 있다.

from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="local-secret-key",
)

response = client.chat.completions.create(
    model="Qwen/Qwen2.5-1.5B-Instruct",
    messages=[
        {
            "role": "system",
            "content": "너는 초등학생에게 영어를 가르치는 친절한 선생님이야."
        },
        {
            "role": "user",
            "content": "I go to school yesterday가 왜 틀렸어?"
        }
    ],
    temperature=0.2,
    max_tokens=300,
)

print(response.choices[0].message.content)
기존 OpenAI 코드에서 주로 바뀌는 부분은 이것이다.

base_url="http://localhost:8000/v1"
즉, 애플리케이션 입장에서는:

기존: OpenAI 서버에 요청
변경: 우리가 운영하는 vLLM 서버에 요청
이렇게 교체할 수 있다. 최신 vLLM은 Chat Completions, Completions, Responses, Embeddings 등 여러 API 인터페이스를 지원하지만, 실제 사용 가능한 기능은 올린 모델의 종류와 기능에 따라 달라진다. 

9. 설치와 실행 환경
공식 Quickstart의 기본 전제는 Linux와 Python 3.10~3.13이다. NVIDIA GPU 환경에서는 현재 uv를 이용한 설치가 권장된다. 

uv venv --python 3.12 --seed
source .venv/bin/activate

uv pip install vllm --torch-backend=auto
윈도우 컴퓨터라면 지금 사용 중인 것처럼 WSL2의 Ubuntu 환경에서 실습하는 구성이 자연스럽다.

다만 중요한 것은 설치보다 GPU 메모리다.

대략 모델 가중치만 계산해도:

7B 모델 FP16/BF16 ≈ 14GB
7B 모델 8비트     ≈ 7GB
7B 모델 4비트     ≈ 3.5GB + 추가 오버헤드

14B 모델 FP16/BF16 ≈ 28GB
여기에 다음 메모리가 추가된다.

KV Cache
CUDA 실행 공간
Attention 중간 계산
동시 사용자 요청
긴 문맥
CUDA Graph
멀티모달 입력
따라서 “7B 모델이 14GB니까 16GB GPU에 무조건 들어간다”라고 판단하면 안 된다.

vLLM은 FP8, INT8, INT4 등 다양한 양자화 방식을 지원한다. 양자화는 메모리 사용량을 줄여 더 큰 모델을 실행할 수 있게 하지만, 하드웨어·양자화 형식에 따라 속도나 정확도의 손실이 생길 수 있으므로 실제 벤치마크가 필요하다. 

현재 공식 문서상 NVIDIA CUDA, AMD ROCm, Intel GPU, CPU, Apple Silicon 등 다양한 플랫폼을 지원하지만, 처음 배우고 실제 GPU 서버를 구성하는 목적이라면 Linux와 NVIDIA CUDA 조합이 가장 이해하기 쉬운 출발점이다. 

10. 모델이 GPU 한 장에 안 들어가면
vLLM은 여러 GPU를 이용한 분산 추론도 지원한다.

Tensor Parallelism
하나의 모델 층에 있는 행렬 계산을 여러 GPU가 나눠 처리한다.

하나의 거대한 모델
 ├─ GPU 0: 일부 행렬
 ├─ GPU 1: 일부 행렬
 ├─ GPU 2: 일부 행렬
 └─ GPU 3: 일부 행렬
예:

vllm serve 모델이름 \
  --tensor-parallel-size 4
Pipeline Parallelism
모델의 층을 구간별로 나눈다.

GPU 0: 1~10층
GPU 1: 11~20층
GPU 2: 21~30층
GPU 3: 31~40층
Data Parallelism
같은 모델을 여러 벌 올리고, 요청 자체를 여러 GPU 그룹에 분산한다.

모델 서버 A ← 사용자 요청 일부
모델 서버 B ← 사용자 요청 일부
모델 서버 C ← 사용자 요청 일부
모델 크기, GPU 간 연결 속도, 동시 사용자 수에 따라 적절한 방식이 다르다. GPU를 늘린다고 성능이 정확히 두 배씩 증가하는 것은 아니다. GPU 간 통신 비용이 추가되기 때문이다.

11. vLLM을 사용하면 답변 품질도 좋아지는가
원칙적으로는 아니다.

답변 품질을 결정하는 핵심은 다음이다.

어떤 모델을 사용하는가
모델의 파라미터 규모와 학습 품질
프롬프트가 적절한가
RAG 검색 결과가 정확한가
파인튜닝이 잘됐는가
temperature와 sampling 설정이 적절한가
vLLM은 주로 다음을 개선한다.

GPU 메모리 효율
동시 처리량
토큰 생성 속도
서버 운영 효율
API 제공 편의성
여러 GPU 활용
즉,

vLLM은 모델을 더 똑똑하게 만드는 기술이 아니라, 이미 있는 모델을 더 효율적으로 일하게 만드는 기술이다.

다만 같은 모델이라도 실행 엔진, 정밀도, 양자화, sampling 설정, chat template 차이 때문에 결과가 완전히 동일하지는 않을 수 있다.

12. EDENING에 적용하면 어떤 모습인가
예를 들어 EDENING이 자체 영어 교정 모델을 운영한다고 가정하자.

① 학생이 영어 문장을 입력
      ↓
② Spring Boot가 사용자·학습 단계·권한 확인
      ↓
③ RAG가 관련 문법 설명과 학습 이력 검색
      ↓
④ 시스템 프롬프트 + 검색 자료 + 학생 문장을 조립
      ↓
⑤ vLLM의 OpenAI 호환 API에 요청
      ↓
⑥ vLLM이 Qwen 등의 모델을 GPU에서 실행
      ↓
⑦ 생성된 답변을 Spring Boot가 검증·저장
      ↓
⑧ React 화면에 스트리밍
여기서 vLLM은 ⑤~⑥을 담당한다.

vLLM이 담당하지 않는 것은:

학생 수준 판단
교육과정 선택
개인정보 동의 확인
학습 기록 저장
금칙어 검증
정답 기준 관리
RAG 문서 검색
AI 출력 품질 게이트
아동 안전정책 적용
이것들은 EDENING 애플리케이션 계층에서 별도로 설계해야 한다.

13. 언제 vLLM을 선택해야 하는가
vLLM이 유리한 상황
오픈소스 모델을 직접 운영하고 싶다.
데이터가 외부 모델 사업자로 나가지 않아야 한다.
사내망·온프레미스 환경이 필요하다.
동시 요청이 많다.
GPU를 지속적으로 활용할 만큼 트래픽이 있다.
특정 모델이나 양자화 모델을 직접 선택하고 싶다.
장기적으로 모델 호출비를 통제해야 한다.
API 사업자의 정책 변경에 대한 의존도를 낮추고 싶다.
당장 vLLM이 불리할 수 있는 상황
아직 사용자가 거의 없다.
어떤 모델이 필요한지도 확정되지 않았다.
GPU 서버 운영자가 없다.
장애 대응, 모니터링, 보안 패치를 맡을 사람이 없다.
최고 수준의 모델 품질이 필요하다.
사용량이 들쑥날쑥하여 GPU가 대부분 놀게 된다.
MVP를 빨리 검증하는 것이 우선이다.
GPU 서버는 요청이 없어도 비용이 발생할 수 있다. 따라서 트래픽이 적은 초기 단계에서는 관리형 API가 오히려 단순하고 경제적일 수 있다. 반대로 일정한 대규모 트래픽이 확보되면 직접 운영이 유리해질 가능성이 커진다.

14. 실무적으로 가장 중요한 오해
“vLLM을 설치하면 ChatGPT 같은 모델이 생긴다”
아니다. 실행할 모델 가중치를 따로 선택해야 한다.

“vLLM이면 작은 GPU에서도 아무 모델이나 돌아간다”
아니다. PagedAttention은 KV Cache를 효율화하지만, 모델 가중치 자체의 크기를 없애지는 않는다.

“OpenAI 호환 API니까 OpenAI 모델을 직접 돌릴 수 있다”
아니다. OpenAI와 같은 요청 형식을 제공한다는 뜻이다. GPT 계열의 비공개 모델 가중치를 vLLM에 올리는 것은 아니다.

“vLLM이 RAG를 만들어 준다”
아니다. 검색과 프롬프트 조립은 LangChain이나 직접 작성한 애플리케이션이 담당한다.

“성능이 무조건 몇 배 빨라진다”
아니다. 모델, GPU, 입력 길이, 출력 길이, 동시 요청 수, 양자화 방식에 따라 결과가 달라진다. 특히 사용자 한 명이 짧게 질문하는 환경에서는 vLLM의 처리량 장점이 크게 드러나지 않을 수 있다.

15. 한 문장씩 최종 정리
LLM은 답을 만드는 두뇌다.
GPU는 계산을 수행하는 기계다.
KV Cache는 앞서 계산한 대화 내용을 저장하는 메모장이다.
PagedAttention은 그 메모장을 작은 블록으로 나눠 낭비 없이 배치하는 기술이다.
Continuous Batching은 끝난 요청의 자리에 새로운 요청을 즉시 투입하는 방식이다.
vLLM은 이 기술들을 이용해 여러 사용자의 LLM 요청을 빠르게 처리하는 서버 엔진이다.
OpenAI 호환 API 덕분에 기존 OpenAI SDK의 base_url을 바꾸는 방식으로 연결할 수 있다.
EDENING 관점에서는, OpenAI API 대신 자체 오픈소스 모델 서버를 운영할 때 검토해야 할 핵심 기반 기술이다.
가장 정확한 비유는 이것이다.

Qwen이나 Llama가 영어를 가르치는 교사라면, vLLM은 수많은 학생의 질문을 순서대로 배정하고 교사의 기억 공간과 업무 시간을 최대한 효율적으로 활용하는 교무실 운영 시스템이다.




소스


---

## 3. OpenAI와 vLLM, GPU 소유·임대, EDENING의 운영 선택

vLLM이 모델을 실행하는 방식과 OpenAI API가 제공하는 역할을 구분하면, 회사가 반드시 GPU를 구매해야 하는지와 두 방식을 어떻게 함께 쓸 수 있는지가 자연스럽게 이어진다.

Edening에 VLLM을 적용하면 그럼 Openai의 역할은 뭐야? 그리고 이 경우에는 회사가 GPU를 사야한다는 거지?


6m 36s 동안 처리함
응. 다만 정확히는 이렇게 구분해야 해.

vLLM을 쓰면 OpenAI를 대체할 수도 있고, OpenAI와 함께 쓸 수도 있다.
그리고 자체 추론을 하려면 GPU가 필요하지만, 반드시 회사가 GPU를 구매해야 하는 것은 아니다.

1. vLLM을 적용하면 OpenAI는 무슨 역할을 하는가
먼저 각자의 역할은 이렇다.

OpenAI API = 외부 회사가 운영하는 AI 두뇌 서비스
오픈웨이트 모델 = 우리가 내려받아 실행할 수 있는 AI 두뇌
vLLM = 그 AI 두뇌를 서버에서 효율적으로 실행하는 엔진
GPU = 실제 계산을 수행하는 장비
vLLM은 OpenAI의 모델을 호출하는 프로그램이 아니다. Qwen, Llama, Gemma, GPT-OSS 같은 내려받을 수 있는 모델을 회사가 직접 실행하도록 해주는 서버 엔진이다. 또한 OpenAI와 동일한 API 형식을 지원하기 때문에, 기존 OpenAI Python SDK를 그대로 사용하면서 목적지만 사내 vLLM 서버로 바꿀 수 있다. 

예를 들어 코드에 이것이 있어도:

from openai import OpenAI
반드시 OpenAI 서버를 사용하는 것은 아니다.

# OpenAI 서버 사용
client = OpenAI(
    base_url="https://api.openai.com/v1",
    api_key="OPENAI_API_KEY",
)
# EDENING 자체 vLLM 서버 사용
client = OpenAI(
    base_url="https://ai.internal.edening.com/v1",
    api_key="EDENING_INTERNAL_KEY",
)
두 번째 경우 openai 패키지는 단지 호환 클라이언트 프로그램으로 사용될 뿐이며, 요청은 OpenAI가 아니라 EDENING의 vLLM 서버로 간다.

경우 1. vLLM으로 완전히 자체 운영
EDENING
   ↓
자체 vLLM 서버
   ↓
Qwen / Llama / Gemma
   ↓
자체 또는 임대한 GPU
이 경우 OpenAI는 실시간 서비스에 전혀 참여하지 않는다.

학생 문장이 OpenAI로 전송되지 않음
OpenAI API 사용료 없음
OpenAI 장애나 사용량 제한에 영향받지 않음
EDENING이 모델과 서버를 직접 운영
모델 품질, 보안, 장애 대응, 안전 필터도 EDENING 책임
심지어 OpenAI가 공개한 gpt-oss-20b, gpt-oss-120b 같은 오픈웨이트 모델도 vLLM으로 자체 운영할 수 있다. 이 경우 OpenAI는 모델을 만든 회사일 뿐, 학생 요청을 처리하는 서비스 제공자는 아니다. GPT-OSS는 Apache 2.0 기반의 오픈웨이트 모델이며, vLLM도 GPT-OSS 모델 계열을 지원한다. 

경우 2. vLLM과 OpenAI를 함께 사용
나는 EDENING에는 이 구조가 가장 현실적이라고 본다.

학생 요청
   ↓
EDENING AI Gateway
   ├─ 자체 vLLM 모델
   │      └ 단순·반복·대량 작업
   │
   └─ OpenAI API
          └ 복잡·고품질·예외 작업
이때 OpenAI의 역할은 다음과 같다.

① 고난도 답변 담당
자체 모델이 잘 처리하기 어려운 작업만 OpenAI에 보낸다.

예를 들면:

학생 자유작문에 대한 세밀한 피드백
문맥과 의도를 고려한 문법 설명
여러 정답이 가능한 표현 비교
학습자의 오개념 추론
장문의 교육 콘텐츠 검토
복잡한 도구 호출과 다단계 판단
반대로 자체 vLLM은 검증을 통과한 범위에서 다음을 맡을 수 있다.

문장 유형 분류
학습 콘텐츠 태깅
정해진 형식의 힌트 생성
짧은 표현 변환
반복 문제 생성
RAG로 찾은 근거를 정해진 형식으로 정리
내부 저작 보조
중요한 것은 “단순 작업이니 작은 모델도 당연히 잘할 것”이라고 추정하지 않는 것이다. EDENING의 실제 문항과 평가 기준으로 검증한 작업만 자체 모델에 넘겨야 한다.

② 장애 시 백업
자체 GPU 서버 정상 → vLLM 사용
자체 서버 과부하·장애 → OpenAI로 우회
GPU 한 대만 운영하면 그 장비가 고장 났을 때 AI 기능 전체가 멈춘다. OpenAI를 예비 경로로 두면 자체 서버의 장애와 트래픽 폭증에 대응할 수 있다.

③ 품질 평가용 기준 모델
OpenAI를 학생에게 직접 답하는 모델로만 볼 필요는 없다.

다음에도 사용할 수 있다.

자체 모델 출력 평가
정답 예시 작성
골든 테스트셋 구축
콘텐츠 저작자 초안 검토
자체 모델과 OpenAI 모델의 품질 비교
오답 사례 분석
즉 OpenAI를 교사 모델 또는 심사위원 모델로 사용하고, 실제 대량 처리는 자체 모델로 돌리는 구조도 가능하다.

2. 결국 회사가 GPU를 사야 하는가
반드시 사야 하는 것은 아니다
정확한 표현은 다음이다.

vLLM을 직접 운영하려면 계산 장비가 필요하다. 하지만 그 GPU를 소유할지, 임대할지는 별개의 문제다.

선택지는 네 가지다.

방식	회사가 GPU 구매	OpenAI 필요	특징
OpenAI API만 사용	아니오	필수	가장 간단함
클라우드 GPU에 vLLM 설치	아니오	선택	GPU를 시간·월 단위로 임대
전문 추론 업체 사용	아니오	선택	업체가 vLLM과 GPU 운영
사내 GPU 서버에 vLLM 설치	예	선택	완전한 자체 운영
vLLM은 GPU뿐 아니라 일부 CPU와 다양한 가속기도 지원하지만, 학생과 실시간으로 대화하는 상용 LLM 서비스에서는 일반적으로 GPU급 가속 장비가 현실적이다. 지원 하드웨어와 설치 방식은 모델과 vLLM 버전에 따라 확인해야 한다. 

A. GPU를 직접 구매하는 경우
EDENING 서버실 또는 IDC
   ↓
EDENING 소유 GPU 서버
   ↓
vLLM
   ↓
자체 모델
장점:

사용량이 많아져도 API 건당 비용이 없음
데이터 흐름을 가장 강하게 통제 가능
원하는 모델·버전·양자화 방식 사용 가능
장기간 높은 사용률이라면 경제적일 가능성
단점:

GPU 서버 구매비
전력·냉각·서버실 또는 IDC 비용
서버 고장과 교체
24시간 모니터링
보안 패치
모델 업데이트
GPU가 놀아도 감가상각 발생
백업 서버 또는 OpenAI 우회 경로 필요
그리고 “RTX 그래픽카드 한 장 사서 서비스하면 되겠네”라고 생각하면 위험하다. 개인 실험은 가능하지만 상용 서비스는 다음까지 봐야 한다.

모델 가중치 메모리
+ KV Cache
+ 동시 접속자
+ 최대 문맥 길이
+ 운영체제와 CUDA 여유 공간
+ 장애 대비 여분
모델이 간신히 GPU 메모리에 들어가는 것과, 여러 학생에게 안정적으로 서비스할 수 있는 것은 완전히 다른 문제다.

B. GPU를 임대하는 경우
EDENING
   ↓
클라우드 GPU 서버
   ↓
vLLM
   ↓
자체 모델
회사는 GPU를 구매하지 않고 서버 사용료를 낸다.

이 방식의 장점은:

모델을 바꾸기 쉬움
필요할 때 더 큰 GPU를 시험할 수 있음
초기 투자비가 적음
실제 트래픽을 측정한 후 구매 여부를 결정할 수 있음
다만 “자체 모델”이라고 해도 GPU를 클라우드에서 임대한다면 학생 데이터는 해당 클라우드 인프라에서 처리된다. 따라서 OpenAI가 빠지는 것과 외부 사업자가 완전히 빠지는 것은 같은 말이 아니다.

OpenAI API 사용
→ OpenAI가 외부 처리자

클라우드 GPU에서 자체 vLLM 사용
→ OpenAI는 빠지지만 클라우드 사업자는 남음

사내 GPU에서 자체 vLLM 사용
→ 모델 추론 단계의 외부 사업자를 최소화
아동 개인정보 관점에서는 이 세 구조를 구별해야 한다.

3. 자체 vLLM을 쓰면 개인정보 측면에서 무조건 더 좋은가
반은 맞고 반은 틀리다.

자체 서버에서 처리하면 학생 입력을 외부 모델 API로 보내지 않을 수 있다는 것은 분명한 장점이다.

하지만 그 대신 EDENING이 직접 책임져야 한다.

프롬프트 및 응답 로그 관리
접근권한 통제
암호화
보유·파기
모델 출력 안전성
유해 콘텐츠 차단
장애 대응
취약점 패치
백업 데이터 관리
관리자 열람 기록
OpenAI API를 사용하는 경우 현재 공식 정책상 API 데이터는 명시적으로 학습 공유에 동의하지 않는 한 모델 학습에 사용되지 않는다. 다만 기본 설정에서는 악용 방지 로그에 고객 콘텐츠가 포함될 수 있고 최대 30일 보관될 수 있으며, 승인 대상 고객은 별도의 보존 통제를 신청할 수 있다. 

따라서 판단 기준은 단순히:

외부 API = 위험
자체 서버 = 안전
이 아니다.

정확한 판단은:

외부 사업자의 통제 수준
vs.
EDENING 자체 운영 통제 수준
을 비교해야 한다.

관리되지 않는 사내 GPU 서버는 관리가 잘된 외부 API보다 오히려 위험할 수 있다.

4. EDENING에는 어떤 구성이 가장 적합한가
현재 단계에서 바로 고가 GPU를 구매하는 것은 권하지 않는다.

이유는 네 가지다.

① 아직 자체 모델의 교육 품질이 검증되지 않았다
EDENING은 일반 챗봇이 아니다.

한국 초등학생 대상
영어교육과정 정합성
문법 설명의 정확성
아동 친화적 표현
오개념 방지
정해진 교수법 유지
구조화된 출력
이런 요건을 만족해야 한다.

오픈웨이트 모델이 OpenAI보다 싸다는 이유만으로 투입했다가 설명 정확도가 떨어지면, 절약한 인프라 비용보다 제품 신뢰 훼손이 더 커진다.

② 실제 동시 사용자 수가 없다
필요한 GPU는 회원 수가 아니라 다음으로 계산해야 한다.

피크 시간 동시 요청 수
× 평균 입력 토큰
× 평균 출력 토큰
× 허용 응답시간
× 최대 문맥 길이
사용자 1만 명이어도 하루에 분산되어 짧게 사용하면 작은 서버로 가능할 수 있다. 반대로 사용자 1천 명이어도 저녁 8시에 한꺼번에 접속하면 훨씬 큰 용량이 필요하다.

③ GPU 비용보다 운영인력 비용이 더 중요할 수 있다
자가운영 비용은 GPU 가격만이 아니다.

자가운영 총비용
=
GPU 감가상각
+ 서버·스토리지
+ 전기·IDC
+ 모니터링
+ 장애 대응
+ 보안
+ 모델 평가
+ 담당자 인건비
OpenAI API 비용과 GPU 가격만 비교하면 잘못된 결론이 나온다.

④ 모델과 하드웨어가 빠르게 바뀐다
지금 특정 GPU를 구매했는데 몇 달 뒤 더 작은 모델이 같은 품질을 내거나, 다른 추론 기술이 등장하면 고정자산이 부담이 될 수 있다. 초기에는 임대로 검증하고, 워크로드가 안정된 뒤 구매하는 편이 보수적으로 타당하다.

5. 내가 권하는 EDENING 구조
                    ┌──────────────────────┐
학생 ─ EDENING 백엔드 ─│     AI Gateway       │
                    └──────────┬───────────┘
                               │
               ┌───────────────┴───────────────┐
               │                               │
        자체 vLLM 모델                    OpenAI API
   검증된 반복·대량 작업              고난도·예외·백업 작업
               │                               │
               └───────────────┬───────────────┘
                               ↓
                   교육 품질·안전 검증 게이트
                               ↓
                          학생에게 응답
1단계
현재 OpenAI API 기반 기능은 유지한다.

다만 코드가 OpenAI에 종속되지 않도록 인터페이스를 만든다.

interface LlmProvider {
    LlmResponse generate(LlmRequest request);
}
OpenAiProvider
VllmProvider
이렇게 해두면 업무별로 모델을 전환할 수 있다.

2단계
GPU를 구매하지 않고 임대 환경에서 오픈웨이트 모델을 시험한다.

동일한 EDENING 입력을 다음 양쪽에 넣는다.

OpenAI 모델
vs.
vLLM 자체 모델
평가 기준:

문법적 정확성
교육과정 준수
지시사항 준수
JSON 출력 성공률
유해 응답률
평균 응답시간
동시 요청 처리량
문항당 비용
한국어 설명 자연스러움
학생 수준별 설명 차등화
3단계
검증을 통과한 기능만 자체 모델로 옮긴다.

검증된 기능 → vLLM
애매하거나 고난도 기능 → OpenAI
vLLM 장애·과부하 → OpenAI 자동 우회
4단계
다음 조건이 충족될 때 GPU 구매를 검토한다.

실제 사용량이 안정적으로 측정됨
자체 모델이 EDENING 품질 게이트를 통과함
GPU 사용률이 충분히 지속됨
클라우드 임대비 또는 API 비용보다 총소유비용이 낮음
장애 대응 구조가 준비됨
보안·개인정보 운영체계가 준비됨
고장 시 OpenAI 또는 예비 GPU로 우회 가능함
최종 결론
OpenAI의 역할
vLLM을 사용한다고 OpenAI가 반드시 필요한 것은 아니다.

완전 자체 운영: OpenAI 역할 없음
GPT-OSS 자체 운영: OpenAI는 모델 제작자일 뿐, 요청 처리자는 아님
하이브리드 운영: OpenAI는 고난도 모델, 품질 심사위원, 장애 백업
OpenAI API 중심 운영: OpenAI가 주 모델 및 인프라 제공자
GPU 구매 여부
vLLM 자체 운영에는 GPU급 계산 자원이 사실상 필요하다.
그러나 GPU를 반드시 구매할 필요는 없다.
클라우드 GPU를 임대하거나 전문 추론 서비스를 사용할 수 있다.
OpenAI API만 사용하면 EDENING은 GPU가 필요 없다.
현재 EDENING 단계에서는 구매보다 임대 검증이 타당하다.
가장 중요한 판단은 이것이다.

“vLLM을 도입할까?”가 아니라, “EDENING의 어떤 작업을 자체 모델로 옮겼을 때 품질을 유지하면서 비용·개인정보·운영 안정성이 실제로 개선되는가?”를 먼저 검증해야 한다.

내 판단으로는 OpenAI를 당장 없애는 전면 자체화보다, OpenAI를 고품질 기준점과 백업으로 남겨두고 vLLM을 점진적으로 붙이는 하이브리드 구조가 EDENING에 가장 안전하다.




소스


---

## 4. Stripe 사례로 연결해서 읽기: 대규모 LLM 서빙과 비용 주장

앞의 운영 선택을 실제 기업 사례에 대입하면, 결제회사 Stripe가 왜 LLM 플랫폼을 운영할 수 있는지, vLLM 적용 수치를 어떤 근거 수준으로 읽어야 하는지 구분할 수 있다.

Stripe가 VLLM을 적용해서 다음과 같은 결과를 냈다는데 VLLM이 LLM이 아닌 다른 분야에도 적용된 사례야? 아니면 Stripe가 LLM 서비스도 하니?

73% 서빙 비용 절감

일일 5천만 API 호출 처리
기존 대비 대폭 향상된 응답 지연시간

7m 48s 동안 처리함
결론부터 말하면
Stripe 사례는 vLLM을 결제 처리나 일반적인 사기 탐지 모델에 적용한 사례라기보다, 결제회사인 Stripe가 내부에서 운영하는 LLM 추론 서비스를 vLLM으로 최적화했다는 주장에 가깝다.

Stripe가 OpenAI처럼 범용 LLM API를 외부 고객에게 판매하는 회사는 아니다. 하지만 내부적으로는 여러 LLM을 공통 API로 제공하는 상당한 규모의 사내 LLM 플랫폼을 운영하며, 이를 자사 직원용 도구와 Stripe 제품에 활용하고 있다. 

다만 더 중요한 문제가 있다.

“73% 절감·일일 5천만 호출”이라는 정확한 수치는 아직 신뢰할 만한 공개 1차 자료로 확인되지 않는다.

1. Stripe는 결제회사지만 LLM을 아주 많이 사용한다
Stripe가 공개한 2024년 발표를 보면 다음과 같은 구조가 이미 있었다.

Stripe 내부 직원
    ↓
LLM Explorer
ChatGPT와 비슷한 내부 웹 앱
    ↓
Stripe 사내 LLM API
    ↓
12개 이상의 여러 모델
Stripe는 이 내부 API가 모델 선택, 감사 로그, 보안·개인정보 통제, 재시도와 rate limit 대응 등을 공통으로 처리한다고 설명했다. 당시 이 API는 회사 내부의 60개가 넘는 LLM 애플리케이션을 지원하고 있었다. 

활용 사례도 단순한 사내 챗봇 수준이 아니다.

금융 파트너가 보내는 이메일 해석
분쟁 처리 자동화
장애 알림 생성
판매자 가입 및 위험 검토
Stripe 고객지원·문서 검색 RAG
Radar Assistant의 자연어 기반 사기 방지 규칙 작성
직원의 문서 작성과 코드 작업
Stripe는 2024년 발표에서 판매자 가입 심사에 LLM을 적용했고, LLM을 이용해 지원 가능한 판매자의 80% 이상을 즉시 자동 승인할 수 있었다고 설명했다. 

따라서 Stripe가 LLM 회사는 아니지만, 내부적으로는 사실상 다음과 같은 것을 운영하는 셈이다.

“Stripe 전용 Azure OpenAI/OpenRouter와 비슷한 사내 멀티모델 LLM 게이트웨이”

2. 그렇다고 Stripe의 모든 AI가 LLM인 것은 아니다
Stripe는 전통적인 머신러닝도 아주 많이 사용한다.

예를 들어 Radar는 결제 건마다 1,000개 이상의 특징을 검토해 사기 위험을 판단하며, 결제 승인 경로에서 100밀리초 이내에 결론을 내려야 한다. Stripe는 이를 거래 데이터로 학습한 딥러닝 시스템이라고 설명한다. 이 시스템과 판매자 심사에 사용되는 LLM은 별개의 범주다. 

즉 Stripe의 AI 구조를 구분하면 이렇다.

기능	모델 성격	vLLM 적용 가능성
실시간 카드 사기 탐지	전통적 딥러닝·분류 모델	일반적으로 낮음
결제수단 추천·승인 최적화	추천·예측 모델	일반적으로 낮음
판매자 웹사이트·서류 해석	LLM·멀티모달 모델	높음
고객지원·문서 질의	LLM + RAG	높음
이메일 해석·업무 자동화	LLM	높음
자연어로 사기 방지 규칙 작성	LLM	높음
문장 임베딩·문서 재정렬	Transformer 모델	가능
따라서 “Stripe가 vLLM을 썼다”는 말이 사실이더라도 그것만으로:

Stripe Radar 사기 탐지 모델을 vLLM으로 돌렸다
고 결론 내릴 수는 없다.

오히려 공개된 정보에 따르면 다음이 더 자연스럽다.

Stripe의 사내 LLM 공통 API
또는
여러 LLM 기반 내부·외부 애플리케이션
       ↓
오픈웨이트 모델 추론 일부를 vLLM으로 서빙
3. vLLM은 LLM 이외에는 전혀 못 쓰는가
현재 vLLM은 이름보다 지원 범위가 조금 넓어졌다.

공식 문서상 다음 모델들을 지원한다.

텍스트 생성 LLM
이미지·영상·음성을 입력받는 멀티모달 언어모델
음성인식 모델
임베딩 모델
문서 재정렬 모델
텍스트 분류 모델
보상 모델
문장 유사도·스코어링 모델
최신 vLLM은 생성 모델뿐 아니라 임베딩, 분류, reranking 같은 pooling 모델도 지원한다. 

하지만 여기서 주의해야 한다.

vLLM은 모든 머신러닝 모델을 빠르게 돌리는 범용 엔진이 아니다.

다음 같은 모델을 위한 일반적인 선택은 아니다.

XGBoost
랜덤 포레스트
일반적인 표 형식 데이터 분류 모델
결제 위험 점수용 소형 신경망
전통적인 이미지 CNN
시계열 예측 모델
일반적인 회귀 모델
이런 모델은 보통 다음 계열로 서빙한다.

NVIDIA Triton
TensorRT
ONNX Runtime
KServe
TorchServe
직접 만든 FastAPI/gRPC 추론 서버
vLLM의 핵심 장점인 PagedAttention과 KV Cache 관리는 특히 토큰을 한 개씩 계속 생성하는 자기회귀형 모델에서 효과가 크다.

공식 문서도 임베딩·분류 같은 pooling 모델은 vLLM에서 편의상 지원하지만, Hugging Face Transformers나 Sentence Transformers 대비 성능 향상이 보장되는 것은 아니라고 명시하고 있다. 

따라서 표현을 정확히 하면:

vLLM은 전통적인 의미의 LLM을 넘어 여러 Transformer 기반 생성·임베딩·분류 모델까지 지원하지만, 범용 머신러닝 서빙 엔진은 아니다.

4. 문제는 “Stripe 73% 절감” 수치의 출처다
사용자가 본 문구는 WikiDocs 페이지에 실제로 실려 있다.

Stripe 사례
- 73% 서빙 비용 절감
- 일일 5천만 API 호출
- 응답 지연시간 향상
그 WikiDocs 페이지가 제시하는 출처는 Introl이라는 GPU 인프라 업체의 2026년 블로그 글이다. 

Introl 글은 다음과 같이 주장한다.

Hugging Face Transformers에서 vLLM으로 이전
같은 5천만 건의 일일 호출 처리
GPU 수를 기존의 3분의 1로 축소
비용 73% 절감
그런데 이 주장의 참고문헌은 링크도, 발표자료도, 논문도 아닌 단 한 줄이다.

“Internal case study, Stripe ML Platform, 2024.”

즉 공개되지 않은 Stripe 내부 사례 연구라고만 적혀 있다. 검증 가능한 원문, 실험 조건, 담당자 발표, Stripe 기술 블로그 링크가 없다. 

제가 확인한 공개 자료 범위에서는 다음에서 같은 수치를 직접 확인하지 못했다.

Stripe 공식 기술 블로그
Stripe 공식 발표자료
vLLM 공식 블로그
vLLM 공식 문서
vLLM 논문
Stripe 엔지니어 발표
그래서 이 수치에 붙여야 할 올바른 표시가 있다.

검증 완료된 Stripe 공식 성과가 아니라, 출처를 독립적으로 확인할 수 없는 2차 자료의 주장

5. WikiDocs 설명에는 원출처보다 더 나간 내용도 있다
WikiDocs의 다른 페이지에는 다음과 같은 표까지 들어 있다.

도입 전: 외부 API 의존
도입 후: 5천만 호출 자체 처리

지연시간:
외부 API 지연 → 내부 네트워크 수준
그리고 다음 전략을 썼다고 서술한다.

자체 GPU 클러스터
Prefix Caching
연속 배칭
하지만 정작 이 페이지가 출처로 제시한 Introl 글에는 Stripe가 원래 외부 API를 사용했다거나, Prefix Caching이 Stripe 비용 절감의 직접 원인이었다는 구체적인 근거가 제시되지 않는다. 

즉 다음과 같은 전파가 일어난 것으로 보인다.

공개되지 않은 내부 사례라는 주장
       ↓
Introl 블로그의 73%·5천만 건 서술
       ↓
여러 블로그가 반복 인용
       ↓
WikiDocs가 추가적인 전후 구조까지 구성
그래서 이 자료를 발표나 투자 판단에 그대로 쓰는 것은 위험하다.

6. “일일 5천만 API 호출”은 Stripe 결제 API 호출이 아니다
이 표현을 특히 조심해야 한다.

일반인이 보면 이렇게 이해할 수 있다.

Stripe가 매일 처리하는 결제 API 5천만 건을
vLLM으로 처리했다
하지만 vLLM은 결제 승인 API 서버가 아니다.

사실이라면 더 자연스러운 의미는:

Stripe 내부 ML/LLM 추론 API가
하루에 모델 추론 요청 5천만 건을 받았다
일 가능성이 높다.

다만 공개된 출처에는 다음 정보가 빠져 있다.

어떤 모델이었는가
모델 크기는 몇 B인가
생성형 LLM인가, 분류 모델인가
평균 입력 토큰은 몇 개인가
평균 출력 토큰은 몇 개인가
호출당 응답 길이는 얼마인가
전체 5천만 건이 하나의 모델 요청인가
여러 임베딩·분류 endpoint를 합친 수치인가
기존 GPU와 신규 GPU가 동일한가
비용에 엔지니어 인건비가 포함됐는가
지연시간이 평균인지 P95인지 P99인지
이 정보가 없으면 73%라는 숫자는 사실상 평가할 수 없다.

7. 5천만 호출도 “무슨 호출인가”에 따라 완전히 다르다
하루 5천만 건은 평균으로 계산하면 약 초당 579건이다.

50,000,000 ÷ 86,400초
≈ 초당 579건
하지만 호출 하나가 다음과 같다면:

입력: 거래 설명 20토큰
출력: risk / no-risk 1토큰
매우 짧은 분류 요청이다.

반대로 EDENING처럼:

입력:
시스템 프롬프트 + 학습 이력 + RAG 문서
약 2,000토큰

출력:
설명·예시·피드백
약 500토큰
이면 호출 한 건의 계산량이 수십 배에서 수백 배까지 커질 수 있다.

그래서 LLM 인프라에서는 단순히 호출 수보다 다음이 중요하다.

일일 입력 토큰
일일 출력 토큰
피크 동시 요청 수
초당 출력 토큰
평균 문맥 길이
P95 첫 토큰 지연시간
P95 전체 응답시간
GPU 시간당 실제 가동률
“5천만 API 호출”만으로 성능을 자랑하는 것은 결제 횟수만 말하고 결제 금액은 말하지 않는 것과 비슷하다.

8. Stripe가 LLM 서비스를 하느냐에 대한 정확한 답
외부 고객에게 범용 LLM API를 판매하느냐
공개적으로 확인되는 범위에서는 아니다.
Stripe의 주력은 여전히:

결제
구독·청구
세금
사기 방지
금융 계좌·자금 이동
판매자 플랫폼
에이전트 상거래 인프라
다.

회사 내부에서 LLM 플랫폼을 운영하느냐
그렇다.

2024년부터 공식적으로 확인되는 구조만 보더라도:

여러 모델
      ↓
Stripe 내부 공통 LLM API
      ↓
60개 이상의 사내 LLM 애플리케이션
이 있었다. 

Stripe 제품 안에 LLM 기능을 제공하느냐
그렇다.

문서·고객지원 assistant, 판매자 심사, Radar Assistant, Dashboard assistant 등 여러 형태로 LLM 기능을 Stripe 제품에 포함하고 있다. Stripe는 자연어로 사기 방지 규칙을 작성하는 Radar Assistant도 공식 발표했다. 

따라서 Stripe는 LLM 모델 판매회사는 아니지만, 상당한 규모의 LLM 사용자이자 사내 LLM 플랫폼 운영사다.

9. EDENING 관점에서 이 사례를 어떻게 읽어야 하는가
이 사례를 다음처럼 해석하면 안 된다.

Stripe도 73% 절감했다
→ vLLM은 무조건 싸다
→ EDENING도 GPU를 사야 한다
올바른 해석은 다음이다.

많은 LLM 요청이 지속적으로 들어오는 대규모 기업은
자체 모델을 높은 GPU 가동률로 운영할 수 있다면
vLLM으로 추론 원가를 낮출 가능성이 있다
Stripe와 EDENING의 조건은 크게 다르다.

조건	Stripe	초기 EDENING
요청량	매우 큼	아직 미확정
피크 트래픽	안정적으로 측정 가능	출시 전 또는 초기
GPU 가동률	높게 유지 가능	낮을 가능성
ML 인프라팀	보유	제한적
자체 평가체계	대규모로 구축 가능	구축 중
장애 대응	다중 서버·전문팀	별도 준비 필요
자체 모델 품질 검증	충분한 데이터·인력	먼저 실험 필요
EDENING이 지금 봐야 할 숫자는 Stripe의 73%가 아니다.

① EDENING 한 학습 세션의 평균 입력·출력 토큰
② 하루 총 호출 수
③ 저녁 피크 동시 접속
④ OpenAI 호출당 원가
⑤ 임대 GPU 시간당 원가
⑥ 자체 모델의 교육 품질 통과율
⑦ 서버 운영 인건비
⑧ 유휴 GPU 비용
그 데이터를 확보하기 전에는 OpenAI API가 비싸다는 결론도, vLLM 자체 운영이 싸다는 결론도 아직 성립하지 않는다.

최종 판정
“vLLM이 LLM이 아닌 다른 분야에도 적용된 사례인가?”
비즈니스 분야로 보면 그렇다.
결제·금융·위험관리 분야에서 LLM을 활용한 사례다.

모델 종류로 보면 그렇다고 볼 근거가 없다.
일반 결제 시스템이나 전통적인 사기 탐지 모델을 vLLM으로 서빙했다는 확인된 사례가 아니다. 가장 개연성 높은 해석은 Stripe의 내부 LLM 추론 플랫폼에 적용했다는 것이다.

“Stripe가 LLM 서비스도 하나?”
OpenAI처럼 범용 LLM을 판매하지는 않지만, 사내에서는 여러 모델을 묶은 공통 LLM API를 운영하고, 그 위에서 수십 개의 LLM 애플리케이션을 돌린다. 일부 기능은 Stripe 고객 제품에도 포함된다.

“73% 절감·일일 5천만 호출은 믿어도 되나?”
참고 사례 정도로만 보고, 공식 검증된 수치로 인용하면 안 된다.

공개적으로 추적 가능한 최초 출처가 Stripe나 vLLM이 아니라 제3자 업체의 글이고, 그 글도 링크 없는 “Stripe 내부 사례” 한 줄에 의존하고 있기 때문이다.

내 판단으로는 이 자료의 가장 정확한 표기는 다음이다.

“제3자 자료는 Stripe가 vLLM 이전 후 73% 비용을 절감했다고 주장하지만, Stripe 또는 vLLM이 공개한 검증 가능한 1차 자료는 현재 확인되지 않는다.”






소스
Attention, self attention, Transformer 개념을 자세히 설명해줘.


9m 13s 동안 처리함

먼저 세 개의 관계부터 잡자
세 개는 서로 경쟁하는 개념이 아니라 포함 관계다.

개념	정체	핵심 질문
Attention	필요한 정보를 가중합으로 가져오는 계산 방식	“지금 나에게 무엇이 중요한가?”
Self-Attention	같은 문장 안에서 수행하는 Attention	“이 문장의 다른 단어 중 무엇을 참고할까?”
Transformer	Self-Attention을 중심으로 여러 부품을 쌓은 신경망 구조	“이 정보 교환과 가공을 여러 층 반복하자”
한 문장으로 압축하면 다음과 같다.

Attention은 정보 선택 방식이고, Self-Attention은 문장이 자기 내부를 참고하는 Attention이며, Transformer는 그것을 여러 층 쌓은 전체 모델 구조다.

Attention
   └─ Self-Attention
          └─ Transformer의 핵심 부품
                 └─ GPT, BERT, T5 같은 모델의 기반
1. Attention은 왜 등장했는가
