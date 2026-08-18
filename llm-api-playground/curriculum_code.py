"""각 항목 화면에 붙는 예제 코드. 모든 줄에 한글 주석."""

CODES: dict[tuple[str, str], str] = {}


def put(lec: str, item: str, src: str) -> None:
    CODES[(lec, item)] = src.strip("\n") + "\n"


put(
    "core01",
    "bottleneck",
    """
import torch                          # 숫자 덩어리(텐서)를 다루는 도구를 불러온다
x = torch.randn(10, 64)               # 단어 10개, 각 단어는 숫자 64개짜리 벡터
h = torch.zeros(64)                   # RNN이 들고 다니는 메모 한 장(은닉 상태)
for t in range(10):                   # 단어를 앞에서부터 하나씩 넣는다
    h = torch.tanh(x[t] + h)          # 지금 단어와 이전 메모를 섞어 한 장으로 덮어쓴다
# 루프가 끝나면 h 하나에 문장 전체가 눌려 있다. 앞 단어 정보는 흐려진다.
""",
)
put(
    "core01",
    "score",
    """
import torch                          # 텐서 계산 도구
q = torch.randn(64)                   # 지금 내가 찾는 것(질의 벡터)
K = torch.randn(10, 64)               # 볼 대상 10개의 이름표
score = K @ q                         # 각 이름표와 질의를 곱해 점수 10개를 낸다
print(score.shape)                    # 결과 모양은 (10,) — 단어마다 점수 하나
""",
)
put(
    "core01",
    "softmax",
    """
import torch                          # 텐서 계산 도구
import torch.nn.functional as F       # softmax 가 들어 있는 상자
score = torch.tensor([2.0, 1.0, 0.1]) # 세 자리에 준 날것 점수
w = F.softmax(score, dim=0)           # 점수를 비율로 바꾼다. dim=0 은 이 한 줄 전체
print(w)                              # 예: 큰 점수가 더 큰 비율
print(w.sum())                        # 합은 반드시 1.0 이어야 한다
""",
)
put(
    "core01",
    "weighted",
    """
import torch                          # 텐서 계산 도구
w = torch.tensor([0.7, 0.2, 0.1])     # 세 자리를 보는 비율(합 1)
V = torch.tensor([                    # 세 자리가 들고 있는 내용
    [1.0, 0.0],                       # 1번 자리의 내용
    [0.0, 1.0],                       # 2번 자리의 내용
    [1.0, 1.0],                       # 3번 자리의 내용
])
out = w @ V                           # 비율로 내용을 섞는다(가중합)
print(out)                            # 멀리 있는 단어도 한 번에 섞여 나온다
""",
)
put(
    "core01",
    "cross",
    """
import torch                          # 텐서 계산 도구
Q = torch.randn(4, 64)                # 도착 문장 4단어 — 나는 무엇을 찾나
K = torch.randn(6, 64)                # 출발 문장 6단어 — 나는 무엇인가
V = torch.randn(6, 64)                # 출발 문장 6단어 — 들고 있는 내용
score = Q @ K.T                       # 도착 단어마다 출발 단어 전체에 점수를 낸다
# 두 문장 사이를 건너보므로 cross-attention 이다.
""",
)
put(
    "core02",
    "bae",
    """
s1 = "배가 아파서 병원에 갔다"          # 아픈 배 — 문맥이 '아파서'
s2 = "항구에서 배를 타고 섬으로 갔다"    # 타는 배 — 문맥이 '타고'
s3 = "달고 시원한 배를 깎아 먹었다"      # 먹는 배 — 문맥이 '깎'
print(s1, s2, s3)                     # 글자 '배'는 같지만 같이 있는 단어가 뜻을 정한다
""",
)
put(
    "core02",
    "qkv",
    """
import torch                          # 텐서 계산 도구
import torch.nn as nn                 # 선형층(W)을 만드는 도구
x = torch.randn(5, 64)                # 한 문장 단어 5개
Wq = nn.Linear(64, 64, bias=False)    # 질의로 바꾸는 안경
Wk = nn.Linear(64, 64, bias=False)    # 이름표로 바꾸는 안경
Wv = nn.Linear(64, 64, bias=False)    # 내용으로 바꾸는 안경
Q = Wq(x)                             # 나는 무엇을 찾나
K = Wk(x)                             # 나는 무엇인가
V = Wv(x)                             # 내가 들고 있는 정보
""",
)
put(
    "core02",
    "formula",
    """
import torch                          # 텐서 계산 도구
import torch.nn.functional as F       # softmax
Q = torch.randn(5, 64)                # 질의 5개
K = torch.randn(5, 64)                # 이름표 5개
V = torch.randn(5, 64)                # 내용 5개
d_k = Q.size(-1)                      # 마지막 축 크기 = 64
score = Q @ K.T                       # ① 짝마다 점수 (5x5)
score = score / (d_k ** 0.5)          # ② √d_k 로 나눠 흩어짐을 되돌린다
w = F.softmax(score, dim=-1)          # ③ 각 행의 합이 1이 되게 비율로
out = w @ V                           # ④ 그 비율로 내용을 섞는다
""",
)
put(
    "core02",
    "sqrt",
    """
import torch                          # 텐서 계산 도구
d_k = 64                              # 벡터 길이
q = torch.randn(d_k)                  # 평균 0, 분산 1 짜리 질의
k = torch.randn(d_k)                  # 같은 성질의 이름표
dot = (q * k).sum()                   # 그냥 내적 — 분산이 대략 d_k
scaled = dot / (d_k ** 0.5)           # √d_k 로 나누면 분산이 다시 1 근처
print(float(dot), float(scaled))      # 안 나눈 값이 훨씬 크다
""",
)
put(
    "core02",
    "mha",
    """
import torch.nn as nn                 # 멀티헤드 구현이 들어 있는 상자
mha = nn.MultiheadAttention(          # 파이토치 공식 멀티헤드
    embed_dim=64,                     # 전체 차원 d
    num_heads=4,                      # 헤드 4개로 쪼갠다 → 헤드당 16
    batch_first=True,                 # 배치가 맨 앞 축
)
# 헤드를 늘려도 d 를 나누므로 Wq/Wk/Wv 총 파라미터는 거의 같다.
""",
)
put(
    "core02",
    "pos",
    """
# 셀프 어텐션 식에는 i, j 의 '몇 번째'가 숫자로 안 들어간다.
s1 = ["나는", "밥을", "먹었다"]         # 순서 A
s2 = ["밥을", "나는", "먹었다"]         # 단어는 같고 순서만 다름
print(s1, s2)                         # 사람 눈엔 다르지만, 위치 없이 섞으면 구분이 약하다
# 그래서 다음에 위치 인코딩을 더한다.
""",
)
put(
    "core04",
    "repr",
    """
from transformers import AutoModel    # 허브에서 몸통을 불러오는 도구
model = AutoModel.from_pretrained(    # 사전학습된 BERT 몸통
    "klue/bert-base"                  # 만든사람/모델이름
)
print(model.config.hidden_size)       # 768 — 토큰 하나당 표현 숫자 개수
# 단어 점수로 바꾸는 마지막 층이 머리(head)다. 몸통만 열면 머리가 없다.
""",
)
put(
    "core04",
    "special",
    """
from transformers import AutoTokenizer  # 글을 토큰 번호로 바꾸는 도구
tok = AutoTokenizer.from_pretrained("klue/bert-base")  # BERT 용 토크나이저
ids = tok("배가 아프다")                 # 문장을 넣는다
print(tok.convert_ids_to_tokens(ids["input_ids"]))  # [CLS] 배 ##가 ... [SEP]
# [CLS] 는 맨 앞(문장 대표), [SEP] 는 끝(또는 두 문장 사이)
""",
)
put(
    "core04",
    "family",
    """
# 같은 블록, 다른 질문
family = {                            # 가계도를 표로 적는다
    "BERT": "인코더만 / 가린 단어 맞히기",  # 양쪽으로 읽고 빈칸
    "GPT": "디코더만 / 다음 단어 맞히기",   # 앞만 보고 다음을 예언
    "BART": "양쪽 / 망가뜨린 문장 복원",    # 읽고 다시 쓰기(요약)
}
print(family["BERT"])                 # 한 줄로 차이를 꺼낸다
""",
)
put(
    "core04",
    "decoder2",
    """
import torch                          # 마스크를 만들 도구
L = 5                                 # 단어 5개
causal = torch.triu(                  # 위쪽 삼각형
    torch.ones(L, L), diagonal=1      # 대각선 위는 1
)
print(causal)                         # 1 인 칸은 '뒤 단어' — 보면 안 된다
# 디코더는 이 마스크로 뒤를 가린다. 인코더 K·V 를 보는 층이 cross-attention 이다.
""",
)
put(
    "core04",
    "subword",
    """
from transformers import AutoTokenizer  # 토크나이저
tok = AutoTokenizer.from_pretrained("klue/bert-base")  # BERT 사전
print(tok.tokenize("플레이잉"))          # ['플레', '##이', '##잉'] 처럼 조각날 수 있다
print(tok.unk_token)                   # 목록에 없는 글자는 [UNK]
# ## 는 '앞 조각에 이어 붙는다'는 표시다.
""",
)
put(
    "core04",
    "hub",
    """
# 주소 = 만든사람 / 모델이름
name = "klue/bert-base"               # 허브에서 이 문자열로 찾는다
print("라이선스는 모델 카드부터 읽는다")  # klue/bert-base 는 CC-BY-SA 4.0
print(name)                           # 코드에 쓸 때는 이 한 줄
""",
)
put(
    "core05",
    "next",
    """
import torch                          # 이어 붙일 때 쓴다
ids = torch.tensor([[10, 21, 7]])     # 지금까지 고른 토큰 번호들
next_id = torch.tensor([[33]])        # 방금 1등으로 고른 다음 토큰
ids = torch.cat([ids, next_id], dim=1)  # 뒤에 붙인다
# generate() 는 이 세 줄(점수→고르기→붙이기)의 반복이다.
""",
)
put(
    "core05",
    "greedy",
    """
import torch                          # argmax 가 있는 곳
logits = torch.tensor([0.1, 2.5, 0.4])  # 세 단어의 점수
next_id = int(logits.argmax())        # 가장 큰 칸의 번호만 고른다 = greedy
print(next_id)                        # 항상 같은 입력이면 항상 같은 출력
# 다음 1등이 또 그 말이면 문장이 맴돈다.
""",
)
put(
    "core05",
    "temp",
    """
import torch                          # 지수와 나눗셈
import torch.nn.functional as F       # softmax
logits = torch.tensor([2.0, 1.0, 0.2])  # 원래 점수
for T in (0.2, 1.0, 1.5):             # 온도를 바꿔 본다
    p = F.softmax(logits / T, dim=0)  # 점수를 T 로 나누고 비율로
    print(T, p)                       # T 가 작으면 1등이 더 압도적
""",
)
put(
    "core05",
    "topk",
    """
# top-k : 확률 상위 k 개만 남긴다
# top-p : 큰 것부터 더해 p 에 닿을 때까지 남긴다
k = 5                                 # 개수를 고정
p = 0.9                               # 확률 합을 고정
print("top_k", k, "top_p", p)         # 둘 다 '이상한 꼬리'를 자르는 칼이다
""",
)
put(
    "core05",
    "hallu",
    """
prompt = "오늘 아침 날씨는"            # 사실 질문이지만
# 모델은 창밖을 못 본다. 그럴듯한 예보 문장만 이어 붙인다.
print(prompt, "→ 그럴듯하지만 사실인지는 모름")  # 이게 환각이다
""",
)
put(
    "core05",
    "limit",
    """
window = 1024                         # 이 모델이 한 번에 넣을 수 있는 토큰 수
print("컨텍스트 윈도우", window)        # 넘치면 앞부분을 잘라야 한다
# 관련 문서만 찾아 넣으면 RAG. 학습(파인튜닝)은 이 과목에서 안 했다.
""",
)
put(
    "api01",
    "stateless",
    """
from openai import OpenAI             # OpenAI 창구 도구 상자
client = OpenAI()                     # 환경변수에서 키를 찾는다
r1 = client.chat.completions.create(  # 첫 호출 — 홍길동이라고 말한다
    model="gpt-5.4-nano",             # 수업용 나노 모델
    messages=[{"role": "user", "content": "내 이름은 홍길동이야."}],
)
r2 = client.chat.completions.create(  # 완전 별도 호출
    model="gpt-5.4-nano",             # 같은 모델이어도
    messages=[{"role": "user", "content": "내 이름이 뭐야?"}],
)
print(r2.choices[0].message.content)  # 서버에 기억이 없어서 모른다
""",
)
put(
    "api01",
    "roles",
    """
messages = [                          # 대화 녹취록 한 권
    {"role": "system", "content": "짧게 답해."},   # 지시 — 배열 맨 앞, 무대 뒤
    {"role": "user", "content": "안녕"},           # 내가 한 말
    {"role": "assistant", "content": "안녕!"},     # 모델이 한 말
]
print([m["role"] for m in messages])  # 신분은 이 셋뿐이다
""",
)
put(
    "api01",
    "persona",
    """
from openai import OpenAI             # SDK
client = OpenAI()                     # 키는 환경변수
API_MODEL = "gpt-5.4-nano"            # 수업 모델
question = "감기는 왜 걸려?"           # 질문은 하나로 고정
sys_msg = "너는 초등학생에게 설명하는 선생님이야. 쉬운 말로 짧게."  # 지시만 바뀐다
r = client.chat.completions.create(   # 한 번 호출
    model=API_MODEL,                  # 모델
    messages=[                        # 배열 맨 앞에 지시가 탄다
        {"role": "system", "content": sys_msg},
        {"role": "user", "content": question},
    ],
)
print(r.choices[0].message.content)   # 같은 질문, 다른 말투
""",
)
put(
    "api01",
    "resend",
    """
from openai import OpenAI             # SDK
client = OpenAI()                     # 클라이언트
API_MODEL = "gpt-5.4-nano"            # 모델 이름
messages = [{"role": "user", "content": "내 이름은 홍길동이야."}]  # 첫 말
r = client.chat.completions.create(model=API_MODEL, messages=messages)  # 1번째 호출
messages.append({"role": "assistant", "content": r.choices[0].message.content})  # 모델 답도 기록
messages.append({"role": "user", "content": "내 이름이 뭐야?"})  # 새 질문을 뒤에
r = client.chat.completions.create(model=API_MODEL, messages=messages)  # 배열 통째로 다시
print(r.choices[0].message.content)   # 이제 홍길동을 말할 수 있다
""",
)
put(
    "api01",
    "tokens",
    """
print(r.usage.prompt_tokens)          # 이번에 보낸 토큰(입력) — 대화가 길수록 커진다
print(r.usage.completion_tokens)      # 이번에 받은 토큰(출력) — 답 길이에 비례
print(r.usage.total_tokens)           # 둘의 합 — 요금의 재료
# 멀티턴에서 폭주하는 쪽은 하필 입력(prompt_tokens)이다.
""",
)
put(
    "api01",
    "finish",
    """
print(r.choices[0].finish_reason)     # stop 이면 할 말 다 하고 멈춤
print(r.choices[0].message.content)   # 본문. 비어 있으면 아래를 본다
# length 이면 예산을 다 씀. nano 는 생각에 예산을 다 써서 답이 비기도 한다.
""",
)
put(
    "api01",
    "bowls",
    """
messages = []                         # 그릇 1 — 노트북 변수
# while True: messages.append(...)    # 그릇 2 — 터미널 chat.py
import streamlit as st                # 그릇 3 — 브라우저
if "messages" not in st.session_state:  # 재실행에도 살아남는 옷장
    st.session_state.messages = []    # 배열은 같고 사는 집만 다르다
""",
)
put(
    "api02",
    "need",
    """
review = "배송은 느렸지만 물건은 기대 이상."  # 분석할 문장
text = "평점으로 치면 별 4~5 느낌"     # 모델이 사람처럼 쓴 답
# text 에서 숫자만 자르면 다음 호출에 문장이 달라져 깨진다.
print(text)                           # 좋은 분석, 코드는 평균을 못 낸다
""",
)
put(
    "api02",
    "jobj",
    """
import json                           # 문자열을 딕셔너리로 바꾸는 도구
from openai import OpenAI             # SDK
client = OpenAI()                     # 키는 환경변수
review = "배송은 느렸지만 기대 이상."    # 리뷰
r = client.chat.completions.create(   # JSON 봉투만 강제
    model="gpt-5.4-nano",             # 모델
    messages=[{"role": "user", "content": f"이 리뷰를 JSON으로 분석해. {review}"}],  # 반드시 JSON 이라는 단어
    response_format={"type": "json_object"},  # 유효한 JSON 까지만 보장
)
data = json.loads(r.choices[0].message.content)  # 글자 → 딕셔너리
print(data.keys())                    # 키 이름은 호출마다 흔들릴 수 있다
""",
)
put(
    "api02",
    "strict",
    """
import json                           # loads 용
from openai import OpenAI             # SDK
client = OpenAI()                     # 클라이언트
review = "배송은 느렸지만 기대 이상."    # 리뷰
schema = {                            # 답의 설계도
    "type": "object",                 # 최상위는 딕셔너리
    "properties": {                   # 칸 목록
        "sentiment": {"type": "string", "description": "긍정/부정/중립"},  # 설명은 모델이 읽는 힌트
        "rating": {"type": "integer", "description": "1~5"},
        "summary": {"type": "string", "description": "한 문장"},
    },
    "required": ["sentiment", "rating", "summary"],  # 세 칸 필수
    "additionalProperties": False,    # 다른 칸 금지
}
r = client.chat.completions.create(   # 이번엔 모양까지 계약
    model="gpt-5.4-nano",
    messages=[{"role": "user", "content": f"이 리뷰를 분석해: {review}"}],
    response_format={"type": "json_schema", "json_schema": {"name": "review_analysis", "strict": True, "schema": schema}},
)
print(json.loads(r.choices[0].message.content))  # 키가 항상 같다
""",
)
put(
    "api02",
    "pyd",
    """
from openai import OpenAI             # SDK
from pydantic import BaseModel        # 모양을 클래스로 적는 도구
client = OpenAI()                     # 클라이언트

class ReviewAnalysis(BaseModel):      # 최상위 이름은 영문
    sentiment: str                    # 문자열 칸
    rating: int                       # 정수 칸
    summary: str                      # 문자열 칸

r = client.chat.completions.parse(    # create 가 아니라 parse
    model="gpt-5.4-nano",
    messages=[{"role": "user", "content": "이 리뷰를 분석해: 기대 이상"}],
    response_format=ReviewAnalysis,   # 클래스를 그대로 넘긴다
)
obj = r.choices[0].message.parsed     # 이미 파이썬 객체
print(obj.rating)                     # json.loads 없이 칸을 연다
""",
)
put(
    "api02",
    "four",
    """
import json                           # arguments 가 JSON 문자열이라서
from openai import OpenAI             # SDK
client = OpenAI()                     # 클라이언트
messages = [{"role": "user", "content": "서울 날씨 알려줘"}]  # 금요일과 같은 배열
r = client.chat.completions.create(   # ① 설명서를 실어 보낸다
    model="gpt-5.4-nano",
    messages=messages,
    tools=tools,                      # 함수 사용법(오전의 그 스키마)
)
msg = r.choices[0].message            # ② 요청서. content 는 None 일 수 있다
print(r.choices[0].finish_reason)     # tool_calls 면 말로 답한 게 아니다
tc = msg.tool_calls[0]                # 첫 장 요청서
args = json.loads(tc.function.arguments)  # ③ 문자열 → 딕셔너리
result = get_weather(**args)          # 실행은 내 파이썬
messages.append(msg)                  # 요청서 자체를 기록에 남긴다
messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})  # ④ 짝을 맞춰 재투입
""",
)
put(
    "api02",
    "calc",
    """
import re                             # 문자열이 허용 꼴인지 검사
def calc(expression: str) -> str:     # 모델이 준 수식 문자열을 받는다
    ok = re.fullmatch(r"[0-9+\\-*/(). %]+", expression)  # 숫자와 사칙만
    if not ok or "**" in expression or len(expression) > 80:  # 거듭제곱·긴 문자열 거절
        return "허용되지 않는 수식"     # 문으로 막는다
    return str(eval(expression, {"__builtins__": {}}, {}))  # 내장 함수 없이 계산
print(calc("3+5*2"))                  # 내 코드가 실행한다. 모델은 요청만 한다
""",
)
put(
    "api02",
    "loop",
    """
for _ in range(5):                    # 상한 5바퀴 — 무한 왕복 방지
    r = client.chat.completions.create(model=API_MODEL, messages=messages, tools=tools)
    msg = r.choices[0].message        # 이번 응답
    if not msg.tool_calls:            # 요청서가 없으면 말로 끝난 것
        break                         # 루프 탈출
    messages.append(msg)              # 요청서 묶음을 기록
    for tc in msg.tool_calls:         # 여러 장이면 전부 처리. [0] 만 보면 깨진다
        args = json.loads(tc.function.arguments)  # 인자 파싱
        result = TOOL_FUNCS[tc.function.name](**args)  # 내 함수 실행
        messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
answer = msg.content or "(상한에 걸렸다)"  # None 이 배열에 들어가면 다음 턴 400
""",
)


from curriculum_code_more import register as register_more
from curriculum_code_fill import register as register_fill

register_more(put)
register_fill(put)


def code_for(lecture_id: str, item_id: str | None) -> str:
    if item_id:
        return CODES.get((lecture_id, item_id), "")
    from curriculum import LECTURES

    chunks: list[str] = []
    for lec in LECTURES:
        if lec["id"] != lecture_id:
            continue
        for it in lec.get("items", []):
            src = CODES.get((lecture_id, it["id"]), "").rstrip()
            if src:
                chunks.append(f"# --- {it['title']} ---\n{src}\n")
        break
    return "\n".join(chunks)
