"""추가 수업 항목의 줄마다 주석이 달린 예제."""


def register(put):
    put(
        "st01",
        "what",
        """
import streamlit as st                 # 웹 화면을 만드는 도구
st.title("첫 대시보드")                # 큰 제목
st.write("파이썬 파일이 곧 화면이다")  # 본문 한 줄
# Flask처럼 HTML을 안 써도 된다
""",
    )
    put(
        "st01",
        "rerun",
        """
import streamlit as st                 # 클릭하면 이 파일을 처음부터 다시 실행한다
n = st.slider("개수", 1, 10)           # 슬라이더를 움직이면 rerun
st.write(n * 2)                        # 다시 계산된 값이 그려진다
# 일반 변수 n 은 다음 클릭에 다시 만들어진다
""",
    )
    put(
        "st01",
        "widget",
        """
import streamlit as st                 # 위젯
import pandas as pd                    # 표
df = pd.DataFrame({"survived": [0, 1, 1], "pclass": [3, 1, 2]})  # 작은 표
cls = st.sidebar.selectbox("객실", [1, 2, 3])  # 사이드바에서 고른 값
st.dataframe(df[df.pclass == cls])     # 그 값으로 걸러 보여 준다
""",
    )
    put(
        "st01",
        "layout",
        """
import streamlit as st                 # 레이아웃
a, b, c = st.columns(3)                # 가로 세 칸
a.metric("승객", 891)                  # 큰 숫자
tab1, tab2 = st.tabs(["표", "설명"])   # 탭으로 화면을 가른다
""",
    )
    put(
        "st01",
        "cache",
        """
import streamlit as st                 # 캐시
import pandas as pd                    # CSV

@st.cache_data                         # 같은 파일이면 다시 안 읽는다
def load(path):                        # 경로를 인자로
    return pd.read_csv(path)           # 디스크 I/O

df = load("titanic.csv")               # rerun 해도 캐시에서 꺼낸다
""",
    )
    put(
        "st02",
        "board",
        """
import streamlit as st                 # 전자칠판
if "count" not in st.session_state:    # 처음 한 번만
    st.session_state.count = 0         # 칸을 만든다
if st.button("+1"):                    # 눌러도 파일이 다시 돈다
    st.session_state.count += 1        # 칠판의 숫자만 살아남는다
st.write(st.session_state.count)       # 일반 변수 count=0 이면 항상 0
""",
    )
    put(
        "st02",
        "key",
        """
import streamlit as st                 # key 가 있으면 위젯 값이 칠판에 자동 저장
st.checkbox("좋아요", key="liked")     # session_state['liked']
liked = st.session_state.get("liked", False)  # 없으면 False
st.write("좋아요" if liked else "아직")
""",
    )
    put(
        "st02",
        "pages",
        """
import streamlit as st                 # 여러 페이지
home = st.Page("home.py", title="홈")  # 파일 하나가 페이지
dash = st.Page("dash.py", title="대시보드")
pg = st.navigation([home, dash])       # 사이드에 목록
pg.run()                               # session_state 는 페이지가 달라도 같다
""",
    )
    put(
        "st02",
        "form",
        """
import streamlit as st                 # 제출 전에 계산하지 않기
with st.form("filter"):                # 이 안은 제출할 때만 rerun
    q = st.text_input("검색")          # 타이핑마다 안 돈다
    ok = st.form_submit_button("적용")
if ok:                                 # 제출됐을 때만
    st.write("검색:", q)
up = st.file_uploader("CSV")           # 사용자가 파일을 올린다
""",
    )
    put(
        "st02",
        "deploy",
        """
# requirements.txt 예시 (이 파일과 app.py 를 같은 폴더에)
# streamlit
# pandas
# plotly
# GitHub 에 push 한 뒤 share.streamlit.io 에서 Main file: app.py
print("data/ 폴더도 저장소에 같이 올린다")  # 없으면 배포 서버가 CSV 를 못 찾는다
""",
    )
    put(
        "ml01",
        "three",
        """
# AI 가 제일 큰 원, 그 안에 ML, 그 안에 DL
print("규칙 기반: 나쁜 단어 목록")     # 사람이 규칙을 쓴다
print("ML: 스팸 10만 통을 보여 준다")  # 예시로 경계를 찾는다
print("DL: 층을 쌓아 특성을 스스로")   # ML 의 한 갈래
""",
    )
    put(
        "ml01",
        "kinds",
        """
tasks = {                              # 세 학습
    "지도": "정답 y 가 있다",          # 분류·회귀
    "비지도": "y 없이 묶음",           # 군집·차원축소
    "강화": "보상으로 행동",           # 이번 주 범위 밖
}
print(tasks["지도"])
""",
    )
    put(
        "ml01",
        "pipe",
        """
from sklearn.neighbors import KNeighborsClassifier  # 모델
from sklearn.model_selection import train_test_split
X, y = [[1, 2], [2, 3], [8, 9], [9, 8]], [0, 0, 1, 1]  # 특성과 정답
Xtr, Xte, ytr, yte = train_test_split(X, y, random_state=42)
kn = KNeighborsClassifier(n_neighbors=3)  # 1. 만들기
kn.fit(Xtr, ytr)                       # 2. 학습
print(kn.score(Xte, yte))              # 3. 평가 — 모델이 바뀌어도 이 세 줄
""",
    )
    put(
        "ml01",
        "split",
        """
from sklearn.model_selection import train_test_split
X = [[1], [2], [3], [4]]               # 네 점
y = [0, 0, 1, 1]
# 전체를 fit 하고 같은 걸로 score 하면 외운 점수가 나온다
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.5, random_state=0)
print(len(Xtr), len(Xte))              # 시험지는 숨긴다
""",
    )
    put(
        "ml01",
        "knn",
        """
from sklearn.neighbors import KNeighborsClassifier
# 전학생을 제일 가까운 k 명으로 분류
kn = KNeighborsClassifier(n_neighbors=3)
kn.fit([[10, 20], [12, 22], [80, 90]], [0, 0, 1])  # 0=작은생선, 1=큰생선
print(kn.predict([[11, 21]]))          # 작은 쪽 이웃이 많다
""",
    )
    put(
        "ml01",
        "scale",
        """
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
X = [[8, 10], [44, 1000]]              # cm 와 g — 무게가 거리를 독점
Xtr, Xte = train_test_split(X, random_state=0)
ss = StandardScaler()
ss.fit(Xtr)                            # 평균·표준편차는 훈련만
print(ss.transform(Xte))               # 테스트는 그 자로만 잰다
""",
    )
    put(
        "ml02",
        "leak",
        """
from sklearn.preprocessing import StandardScaler
# 나쁜 예: ss.fit(전체 X)  → 시험 평균을 미리 봄
ss = StandardScaler()
train = [[1.0], [2.0], [3.0]]
test = [[10.0]]
ss.fit(train)                          # 올바른 예 — 훈련만
print(ss.transform(test))              # transform 만
""",
    )
    put(
        "ml02",
        "knnr",
        """
from sklearn.neighbors import KNeighborsRegressor
knr = KNeighborsRegressor(n_neighbors=3)
knr.fit([[10], [20], [30]], [100, 200, 300])  # 본 범위 8~44 라고 치자
print(knr.predict([[100]]))            # 50cm 밖 — 이웃이 끝쪽뿐이라 외삽 실패
""",
    )
    put(
        "ml02",
        "line",
        """
from sklearn.linear_model import LinearRegression
lr = LinearRegression()
lr.fit([[10], [20], [30]], [100, 200, 300])
print(lr.coef_, lr.intercept_)         # 무게 ≈ w*길이 + b
print(lr.predict([[100]]))             # 직선은 범위 밖도 이어진다
""",
    )
    put(
        "ml02",
        "poly",
        """
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
poly = PolynomialFeatures(degree=5, include_bias=False)  # 특성 폭발
X = [[8], [20], [30], [44]]
Xp = poly.fit_transform(X)             # 열 개수가 확 는다
lr = LinearRegression().fit(Xp, [80, 200, 400, 900])
print(Xp.shape)                        # 훈련은 잘 맞아도 테스트는 무너질 수 있다
""",
    )
    put(
        "ml02",
        "reg",
        """
from sklearn.linear_model import Ridge, Lasso
from sklearn.preprocessing import StandardScaler
X = [[1.0, 2.0], [2.0, 4.0], [3.0, 5.0]]
y = [1.0, 2.0, 2.8]
Xs = StandardScaler().fit_transform(X)  # 규제 전 스케일 필수
print(Ridge(alpha=1.0).fit(Xs, y).coef_)   # 계수를 작게
print(Lasso(alpha=0.1).fit(Xs, y).coef_)   # 일부는 0 (특성 선택)
""",
    )
    put(
        "ml03",
        "sig",
        """
import numpy as np
from scipy.special import expit        # 시그모이드
z = np.array([-4.0, 0.0, 4.0])         # 직선 값 (−∞~∞)
print(expit(z))                        # 0~1 확률로 눌린다
""",
    )
    put(
        "ml03",
        "ce",
        """
# 시그모이드는 비선형이라 MSE 언덕이 울퉁불퉁해질 수 있다
# 분류에는 Cross-Entropy: 정답을 자신 있게 틀리면 손실이 크다
print("맞힘 0.9 → 손실 작음")
print("틀림 0.9 → 손실 큼 (놀람)")
""",
    )
    put(
        "ml03",
        "acc",
        """
# 타이타닉 891명, 생존 342 (38%)
pred_all_dead = [0] * 891              # 무조건 사망
acc = (891 - 342) / 891                # 약 0.62
print(acc, "생존자 Recall = 0")        # 정확도만 보면 속는다
""",
    )
    put(
        "ml03",
        "prf",
        """
from sklearn.metrics import precision_score, recall_score, f1_score
y = [1, 1, 0, 0, 1]
p = [1, 0, 0, 0, 1]                    # 생존자 한 명 놓침
print(precision_score(y, p), recall_score(y, p), f1_score(y, p))
""",
    )
    put(
        "ml03",
        "bv",
        """
# train 낮고 test 낮음 → High Bias → 모델이 너무 단순
# train 높고 test 낮음 → High Variance → 외움
print("표의 네 칸으로 다음 행동을 고른다")
""",
    )
    put(
        "ml04",
        "gini",
        """
# 방 어지러움: 한 색만 있으면 0, 반반이면 최대
# 질문 "숨을 쉬나요?" 는 정보 이득이 거의 0
print("다리가 4개인가요? → 한 번에 많이 가름")
""",
    )
    put(
        "ml04",
        "scale0",
        """
from sklearn.tree import DecisionTreeClassifier
X = [[1, 1000], [2, 1100], [10, 100], [11, 90]]
y = [0, 0, 1, 1]
dt = DecisionTreeClassifier(max_depth=2, random_state=42)
dt.fit(X, y)                           # 스케일 없이 그대로
print(dt.predict([[1.5, 1050]]))       # 임계값 예/아니오
""",
    )
    put(
        "ml04",
        "prune",
        """
from sklearn.tree import DecisionTreeClassifier
dt = DecisionTreeClassifier(max_depth=3, random_state=42)
# max_depth 없으면 샘플마다 질문을 만들어 훈련 99%
print(dt.max_depth)                    # 가지치기 손잡이
""",
    )
    put(
        "ml04",
        "rf",
        """
from sklearn.ensemble import RandomForestClassifier
rf = RandomForestClassifier(n_estimators=100, random_state=42)
# 복원 추출 + 특성 일부 → 나무가 서로 달라야 한다
print(rf.n_estimators, "그루의 다수결")
""",
    )
    put(
        "ml04",
        "cv",
        """
from sklearn.model_selection import GridSearchCV
from sklearn.tree import DecisionTreeClassifier
gs = GridSearchCV(
    DecisionTreeClassifier(random_state=42),
    {"max_depth": [2, 3, 5]},          # 메뉴 조합
    cv=5,                              # 다섯 조각으로 시식
)
print(gs)                              # best_estimator_ 는 이미 학습됨
""",
    )
    put(
        "ml05",
        "unsup",
        """
# 지도학습 (x, y) / 오늘 (x,) 만
print("정답을 맞히는 게 아니라 덩어리를 찾는다")
""",
    )
    put(
        "ml05",
        "km",
        """
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs
X, _ = make_blobs(n_samples=90, centers=3, random_state=42)
km = KMeans(n_clusters=3, n_init=10, random_state=42)
km.fit(X)                              # 초기화→배정→이동→반복
print(km.labels_[:5], km.cluster_centers_.shape)
""",
    )
    put(
        "ml05",
        "elbow",
        """
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs
X, _ = make_blobs(n_samples=90, centers=3, random_state=42)
for k in range(2, 6):
    km = KMeans(n_clusters=k, n_init=10, random_state=42).fit(X)
    print(k, km.inertia_)              # 팔꿈치에서 K 를 고른다
""",
    )
    put(
        "ml05",
        "out",
        """
from sklearn.cluster import KMeans
import numpy as np
X = np.array([[0.0, 0.0], [0.1, 0.1], [10.0, 10.0]])
km = KMeans(n_clusters=1, n_init=10, random_state=0).fit(X)
d = km.transform(X).min(axis=1)        # 가장 가까운 중심까지
print(d)                               # 큰 값이 이상 후보
""",
    )
    put(
        "ml05",
        "pca",
        """
from sklearn.decomposition import PCA
import numpy as np
X = np.random.randn(30, 20)            # 특성 20
pca = PCA(n_components=3)
Z = pca.fit_transform(X)               # 분산이 큰 축 3개
print(Z.shape, pca.explained_variance_ratio_.sum())
""",
    )
    put(
        "dl01",
        "perc",
        """
import numpy as np
def sigmoid(z):
    return 1 / (1 + np.exp(-z))        # 확률로 누르기
def perceptron(x, w, b):
    return sigmoid(np.dot(w, x) + b)   # 가중합 + 활성화
print(perceptron([1, 1], [1.0, 1.0], -1.5) > 0.5)  # AND
""",
    )
    put(
        "dl01",
        "xor",
        """
# AND/OR 는 직선으로 가른다. XOR 은 점이 엇갈려 직선 하나로는 불가
print("은닉층이 공간을 구부려야 XOR 이 된다")
""",
    )
    put(
        "dl01",
        "act",
        """
# 선형 ∘ 선형 = 선형. 층을 쌓은 이유가 사라진다
print("그래서 층 사이에 ReLU/시그모이드가 있다")
""",
    )
    put(
        "dl01",
        "flat",
        """
import numpy as np
img = np.zeros((28, 28))               # 한 장
vec = img.reshape(-1)                  # 784
print(img.shape, vec.shape)            # 자리 정보는 여기서 버린다
""",
    )
    put(
        "dl01",
        "keras",
        """
import keras
keras.utils.set_random_seed(42)        # 재현
model = keras.Sequential([
    keras.layers.Input(shape=(784,)),
    keras.layers.Dense(10, activation="softmax"),
])
model.compile(loss="sparse_categorical_crossentropy", metrics=["accuracy"])
print(model.count_params())            # 784*10 + 10
""",
    )
    put(
        "dl02",
        "bp",
        """
# 순전파: x → 은닉 → 예측 → Loss
# 역전파: Loss → ∂L/∂W2 → ∂L/∂W1
print("각 가중치가 손실에 기여한 정도")
""",
    )
    put(
        "dl02",
        "vg",
        """
print(0.25 ** 4)                       # 시그모이드 도함수 최대 0.25
# 은닉을 쌓을수록 앞층 기울기가 죽는다
""",
    )
    put(
        "dl02",
        "relu",
        """
import numpy as np
def relu(z):
    return np.maximum(0, z)            # 음수 0, 양수 그대로
print(relu(np.array([-2.0, 3.0])))
""",
    )
    put(
        "dl02",
        "opt",
        """
# W ← W − α * 기울기
print("sgd: 같은 보폭 / adam: 파라미터마다 보폭")
# model.compile(optimizer="adam", ...)
""",
    )
    put(
        "dl02",
        "dnn",
        """
import keras
model = keras.Sequential([
    keras.layers.Input(shape=(784,)),
    keras.layers.Dense(100, activation="relu"),  # 은닉
    keras.layers.Dense(10, activation="softmax"),
])
print(model.summary())
""",
    )
    put(
        "dl03",
        "curve",
        """
# history.history['loss'] 와 ['val_loss']
# val 이 내려가다 올라가면 그 지점이 과적합 시작
print("에폭을 늘린다고 val 이 계속 좋아지지 않는다")
""",
    )
    put(
        "dl03",
        "drop",
        """
import keras
layer = keras.layers.Dropout(0.3)      # 학습 때 30% 뉴런을 끈다
print(layer.rate, "테스트 때는 끄지 않는다")
""",
    )
    put(
        "dl03",
        "inv",
        """
# 학습 때 70%만 켜면 출력이 0.7배가 된다
# inverted: 학습 때 1/0.7 로 미리 보정 → 테스트 때 손대지 않음
print("기댓값을 학습 쪽에서 맞춘다")
""",
    )
    put(
        "dl03",
        "es",
        """
import keras
es = keras.callbacks.EarlyStopping(patience=3, restore_best_weights=True)
print(es.patience)                     # val 이 3번 안 좋아지면 멈춘다
""",
    )
    put(
        "dl03",
        "ckpt",
        """
import keras
cb = keras.callbacks.ModelCheckpoint("best-model.keras")
print(cb.filepath)                     # 정점 가중치를 파일로
""",
    )
    put(
        "dl04",
        "flatbad",
        """
# 28x28 에서 (0,1)과 (0,2)는 이웃
# Flatten 하면 인덱스 1 과 2 는 이웃이지만, (0,27)과 (1,0)은 실제론 이웃인데 벡터에선 멀다
print("공간 구조가 사라진다")
""",
    )
    put(
        "dl04",
        "conv",
        """
import keras
conv = keras.layers.Conv2D(32, kernel_size=3, padding="same", activation="relu")
# 3x3 돋보기 32개
print("필터를 밀며 특성 맵을 만든다")
""",
    )
    put(
        "dl04",
        "share",
        """
# Dense(32, 784): 784*32 + 32 = 25120
# Conv2D(32, 3x3): (3*3*1 + 1)*32 = 320
print(320, "같은 필터를 전 칸에 공유")
""",
    )
    put(
        "dl04",
        "pad",
        """
# padding='same' → 테두리 0, 가로세로 유지
# stride=2 → 두 칸씩, 출력 대략 절반
print("출력 크기 ≈ (입력 - 커널 + 2패딩)/보폭 + 1")
""",
    )
    put(
        "dl04",
        "pool",
        """
import keras
pool = keras.layers.MaxPooling2D(2)    # 2x2 최댓값
print("해상도는 반, '있었나'는 남긴다")
""",
    )
    put(
        "dl05",
        "vis",
        """
# conv.weights[0].shape → (3, 3, 1, 32)
print("32개 필터를 작은 이미지로 그려 학습 전후를 비교")
""",
    )
    put(
        "dl05",
        "fn",
        """
import keras
x = keras.Input(shape=(28, 28, 1))
h = keras.layers.Conv2D(32, 3, padding="same")(x)
model = keras.Model(x, h)              # 끝이 아니라 중간 출력
print("Sequential 은 맨 끝만 준다")
""",
    )
    put(
        "dl05",
        "aug",
        """
import keras
aug = keras.layers.RandomFlip("horizontal")
print("본 적 없는 각도를 학습 때 만들어 낸다")
""",
    )
    put(
        "dl05",
        "tl",
        """
# base = MobileNetV2(include_top=False, weights="imagenet")
# base.trainable = False
# 그 위에 GlobalAvgPool + Dense(10)
print("남이 익힌 눈 + 내 머리")
""",
    )
    put(
        "dl05",
        "det",
        """
# from ultralytics import YOLO
# YOLO("yolov8n.pt")(사진경로)
print("분류: 라벨 하나 / 탐지: 상자 여러 개")
""",
    )
    put(
        "mini1",
        "cover",
        """
# 둘 다 main 에 push 하면 나중 사람이 앞 커밋을 덮는다
print("main 직접 push 금지")
""",
    )
    put(
        "mini1",
        "br",
        """
# git pull origin main
# git switch -c feat/yh-readme
print("가지는 내 책상, main 은 발표본")
""",
    )
    put(
        "mini1",
        "pr",
        """
# git add README.md
# git commit -m "docs: 소개 추가"
# git push origin feat/yh-readme
print("GitHub 에서 Compare & pull request")
""",
    )
    put(
        "mini1",
        "flow",
        """
# 아침 pull → 가지 → add/commit → push → PR → merge → 다시 pull
print("팀원 merge 후 내 컴퓨터도 pull 해야 최신이다")
""",
    )
    put(
        "mini1",
        "rule",
        """
# 1 main 직접 금지  2 작업 전 최신화
# 3 같은 줄을 동시에 안 고침  4 가지 이름은 영문
print("feat/이름-작업")
""",
    )
    put(
        "mini1b",
        "look",
        """
import pandas as pd
df = pd.DataFrame({"age": [22, None, 38], "survived": [0, 1, 1]})
print(df.shape, df.dtypes, df.isna().sum())  # 먼저 본다
print(df["survived"].value_counts(normalize=True))
""",
    )
    put(
        "mini1b",
        "miss",
        """
import pandas as pd
df = pd.DataFrame({"age": [22, None, 38]})
print(df["age"].median())              # 왜 비었는지 보고 채움/삭제를 고른다
""",
    )
    put(
        "mini1b",
        "enc",
        """
import pandas as pd
s = pd.Series(["male", "female", "male"])
print(pd.get_dummies(s, dtype=int))    # 글자 → 숫자. 훈련에 없던 값은 규칙을 미리
""",
    )
    put(
        "mini1b",
        "prep",
        """
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
X = [[1.0], [2.0], [3.0], [10.0]]
Xtr, Xte = train_test_split(X, random_state=0)
ss = StandardScaler().fit(Xtr)         # 훈련만 fit
print(ss.transform(Xte))
""",
    )
    put(
        "sai01",
        "arch",
        """
// 사용자 → Controller → Service → ChatClient → Gemini
// 예전이면 마지막이 DB 였다
System.out.println("답이 비결정적일 수 있다");
""",
    )
    put(
        "sai01",
        "why",
        """
// 프로바이더마다 JSON 이 다르다
// ChatClient 가 그 차이를 숨긴다
System.out.println("설정만 바꾸고 코드는 그대로");
""",
    )
    put(
        "sai01",
        "chat",
        """
// ChatClient chatClient = builder.build();
// return chatClient.prompt()
//     .system("초등 선생님처럼")
//     .user(message)
//     .call()
//     .content();
System.out.println("체이닝: 역할 → 질문 → 호출 → 문자열");
""",
    )
    put(
        "sai01",
        "tok",
        """
// 토큰 = 과금·한도의 단위. 입력+출력
// gemini 무료 티어는 RPM/RPD 가 작다
System.out.println("한글은 자주 여러 토큰");
""",
    )
    put(
        "sai01",
        "temp",
        """
// temperature 낮음 → 뾰족한 분포 → 뻔하지만 안전
// 높음 → 평평 → 다양, 이상해질 수 있음
System.out.println("다음 토큰을 얼마나 흩을지");
""",
    )
    put(
        "sai02",
        "tpl",
        """
// .user(u -> u.text("다음 문의를 {audience}가 읽게 요약: {text}")
//              .param("audience", audience)
//              .param("text", text))
System.out.println("문자열 + 대신 {변수}");
""",
    )
    put(
        "sai02",
        "ask",
        """
// "JSON으로만 답하세요" → 마크다운이 섞이기도 한다
System.out.println("부탁이지 계약이 아니다");
""",
    )
    put(
        "sai02",
        "ent",
        """
// public record InquiryResult(String category, String priority, String reason) {}
// return chatClient.prompt().user(text).call().entity(InquiryResult.class);
System.out.println("코드가 result.priority() 를 바로 읽는다");
""",
    )
    put(
        "sai02",
        "list",
        """
// List<MovieRecommendation> list =
//     chatClient.prompt().user(mood).call().entity(new ParameterizedTypeReference<>() {});
System.out.println("한 건 record / 여러 건 List");
""",
    )
    put(
        "sai02",
        "nat",
        """
// .entity(InquiryResult.class, spec -> spec.useProviderStructuredOutput())
System.out.println("생성 단계부터 스키마 강제 — 오늘은 눈으로");
""",
    )
    put(
        "sai03",
        "adv",
        """
// public class MaxCharLengthAdvisor implements CallAdvisor { ... }
// chatClientBuilder.defaultAdvisors(maxLen, counter, logger)
System.out.println("호출 앞뒤에 끼우는 인터셉터");
""",
    )
    put(
        "sai03",
        "order",
        """
// getOrder() 가 작을수록 전처리는 먼저, 후처리는 나중
System.out.println("양파 껍질");
""",
    )
    put(
        "sai03",
        "mem",
        """
// MessageWindowChatMemory + MessageChatMemoryAdvisor
// "내 이름은 민준" 을 다음 호출 messages 에 다시 넣는다
System.out.println("모델이 기억하는 게 아니다");
""",
    )
    put(
        "sai03",
        "cid",
        """
// spec.param(ChatMemory.CONVERSATION_ID, conversationId)
// id 가 없으면 런타임 예외
System.out.println("어느 창의 대화인지");
""",
    )
    put(
        "sai03",
        "jdbc",
        """
// InMemory: 프로세스 종료면 리셋
// JDBC 저장소: 같은 conversationId 로 재시작 뒤에도 이어짐
System.out.println("영속 기억");
""",
    )
    put(
        "sai04",
        "mp",
        """
// POST /api/image-analysis  Content-Type: multipart/form-data
System.out.println("파일은 JSON 이 아니다");
""",
    )
    put(
        "sai04",
        "media",
        """
// UserMessage.builder().text("이 사진에 뭐가 보이나요?").media(media).build()
System.out.println("메시지에 칸이 하나 늘었다");
""",
    )
    put(
        "sai04",
        "three",
        """
// 이미지 image/png · PDF application/pdf · 오디오 audio/wav
// toResource(file) 은 같고 MIME 만 다르다
System.out.println("세 파일이 같은 패턴");
""",
    )
    put(
        "sai04",
        "ec",
        """
// .entity(ReceiptInfo.class)  → 코드가 쓸 칸
// .content()                  → 사람이 읽을 글
System.out.println("언제 어느 쪽인지 고른다");
""",
    )
    put(
        "sai04",
        "replay",
        """
// 같은 conversationId 로 다음 질문을 하면
// 이전 이미지·PDF 가 다시 실릴 수 있다
System.out.println("기억은 요약이 아니라 재생, 토큰이 커진다");
""",
    )
    put(
        "sai05",
        "req",
        """
// @Tool(description = "현재 시각을 반환한다")
// public String now() { return LocalDateTime.now().toString(); }
// .tools(dateTimeTools)
System.out.println("모델은 요청만, 실행은 이 메서드");
""",
    )
    put(
        "sai05",
        "desc",
        """
// 모델은 자바 소스를 안 본다
System.out.println("description 이 도구 설명서다");
""",
    )
    put(
        "sai05",
        "mcp",
        """
// .tools((Object[]) catalog.filesystemTools())
// 파일 읽기를 앱마다 안 짠다
System.out.println("남이 띄운 도구 서버에 붙는다");
""",
    )
    put(
        "sai05",
        "boot",
        """
// MCP 서버(npx/uvx)가 안 뜨면 컨텍스트 로딩 실패
// Day1 채팅 엔드포인트까지 같이 죽는다
System.out.println("선택 도구가 필수 의존이 되면 위험");
""",
    )
    put(
        "sai05",
        "exp",
        """
// @Tool 은 우리 앱이 소비
// @McpTool 은 우리 메서드를 서버로 노출
System.out.println("같은 프로토콜의 반대쪽");
""",
    )
    put(
        "sai06",
        "flux",
        """
// String answer = chatClient.prompt().user(q).call().content();
// Flux<String> tokens = chatClient.prompt().user(q).stream().content();
System.out.println("마지막 한 줄만 상자에서 벨트로");
""",
    )
    put(
        "sai06",
        "sse",
        """
// @GetMapping(value="/api/chat/stream", produces=TEXT_EVENT_STREAM_VALUE)
// EventSource 는 GET, 끝나면 자동 재연결
System.out.println("완료 시 연결을 닫고 재구독을 끈다");
""",
    )
    put(
        "sai06",
        "two",
        """
// SPRING_AI_CHAT_MEMORY : LLM 최근 윈도우
// chat_history          : 화면 복원용 전체
System.out.println("목적이 다르니 테이블을 나눈다");
""",
    )
    put(
        "sai06",
        "cors",
        """
// 5173 React / 8080 API / 5432 Postgres
// registry.addMapping("/api/**").allowedOrigins("http://localhost:5173")
System.out.println("브라우저가 다른 포트를 치려면 허용이 필요하다");
""",
    )
    put(
        "sai06",
        "dock",
        """
# compose.yaml
# services:
#   db:
#     image: postgres:16
print("PC 마다 설치하지 않고 상자 하나로 같은 버전")
""",
    )
    put(
        "mini2",
        "strat",
        """
# main  = 발표
# dev   = 통합
# feat/이니셜-작업 = 할 일 하나
print("PR 의 base 는 dev")
""",
    )
    put(
        "mini2",
        "sync",
        """
# git fetch origin
# git merge origin/dev
print("PR 전에 충돌을 내 자리에서 먼저 만난다")
""",
    )
    put(
        "mini2",
        "conf",
        """
# <<<<<<< HEAD
# 내 코드
# =======
# 팀원 코드
# >>>>>>> feat/other
print("git merge --abort 면 시작 전으로")
""",
    )
    put(
        "mini2",
        "rev",
        """
# Files changed → 줄 번호 옆 + → 댓글
print("Approve 또는 Request changes")
""",
    )
    put(
        "mini2",
        "issue",
        """
# Issue #12 → 브랜치 12-login-api → PR 본문에 Fixes #12
print(".env 와 키는 .gitignore — 한 번 push 되면 히스토리에 남는다")
""",
    )
    put(
        "ptn01",
        "env",
        """
import torch                           # WSL 안 uv 환경에서
print(torch.__version__)
print(torch.cuda.is_available())       # 오전의 목표. False 여도 에러가 안 날 수 있다
""",
    )
    put(
        "ptn01",
        "ten",
        """
import torch
x = torch.ones(2, 3)                   # 2행 3열
print(x.shape)                         # 모양
print(x * 2)                           # 칸마다
print(x @ x.T)                         # 행렬곱 — * 와 다르다
""",
    )
    put(
        "ptn01",
        "ag",
        """
import torch
x = torch.tensor(3.0, requires_grad=True)
y = x ** 2
y.backward()
print(x.grad)                          # 6
y2 = x ** 2
y2.backward()
print(x.grad)                          # 12 — 누적된다. 그래서 zero_grad
""",
    )
    put(
        "ptn01",
        "loop",
        """
# pred = model(xb)                     # 1 순전파
# loss = criterion(pred, yb)           # 2 손실
# optimizer.zero_grad()                # 3 이전 기울기 삭제
# loss.backward()                      # 4 기울기
# optimizer.step()                     # 5 가중치 한 걸음
print("Keras fit() 이 숨겼던 다섯 줄")
""",
    )
    put(
        "ptn01",
        "trap",
        """
import torch.nn as nn
crit = nn.CrossEntropyLoss()           # 안에 로그소프트맥스
# 앞에 Softmax 를 또 붙이면 안 된다
# optimizer = Adam(model.parameters())  # parameters() 빠지면 학습이 안 된다
print(crit)
""",
    )
    put(
        "ptn02",
        "tok",
        """
# en.split() 은 don't 를 한 덩어리로 남기기도 한다
# 한국어 '학교에서는' 은 붙어 있다 — Kiwi 형태소
print(["학교", "에서", "는"])          # 교착어
""",
    )
    put(
        "ptn02",
        "voc",
        """
word2idx = {"<pad>": 0, "<unk>": 1}    # 자리를 먼저 예약
for w in ["학교", "파이썬", "배우"]:
    word2idx[w] = len(word2idx)
print(word2idx.get("텐서플로우", 1))   # 없으면 unk=1
""",
    )
    put(
        "ptn02",
        "pad",
        """
import torch
from torch.nn.utils.rnn import pad_sequence
seqs = [torch.tensor([1, 2, 3]), torch.tensor([4, 5])]
print(pad_sequence(seqs, batch_first=True, padding_value=0))
# DataLoader 는 collate_fn 으로 이 작업을 한다
""",
    )
    put(
        "ptn02",
        "emb",
        """
import torch.nn as nn
emb = nn.Embedding(num_embeddings=20, embedding_dim=8, padding_idx=0)
# (배치, 길이) 정수 → (배치, 길이, 8) 벡터
print(emb.weight.shape)                # 룩업 테이블
""",
    )
    put(
        "ptn02",
        "sub",
        """
# '텐서플로우' 가 사전에 없으면 오늘은 <unk>
# 서브워드는 텐/서/플로우 처럼 있는 조각으로 자른다
print("토큰 수 = 돈")
""",
    )
    put(
        "ptn03",
        "order",
        """
# sum(임베딩) 은 순서를 지운다
print("개가 사람을 물었다 vs 사람이 개를 물었다")
print("가방 모델이면 같은 벡터")
""",
    )
    put(
        "ptn03",
        "hid",
        """
import torch
h = torch.zeros(8)                     # 빈 줄거리
print(h.shape, "다음 단어와 섞여 갱신된다")
""",
    )
    put(
        "ptn03",
        "eq",
        """
import torch
Wx = torch.randn(4, 8)
Wh = torch.randn(4, 4)
b = torch.zeros(4)
x_t = torch.randn(8)
h = torch.zeros(4)
h = torch.tanh(Wx @ x_t + Wh @ h + b)  # 그 식
print(h)
""",
    )
    put(
        "ptn03",
        "lpad",
        """
# RNN 은 마지막 h 로 판단한다
# [pad pad 내용] 이어야 내용이 맨 뒤
# [내용 pad pad] 면 빈칸을 읽고 끝난다
print("앞쪽 패딩")
""",
    )
    put(
        "ptn03",
        "van",
        """
print(0.9 ** 30)                       # 같은 W_h 를 거리만큼 곱한다
print("앞 단어 기울기가 0 으로 간다")
""",
    )
    put(
        "ptn04",
        "mul",
        """
print("0.9**30 =", 0.9 ** 30)          # 사라진다
print("더하는 길을 낸다")
""",
    )
    put(
        "ptn04",
        "gate",
        """
import torch
z = torch.tensor(1.0)
print(torch.sigmoid(z))                # 비율 0~1 — 게이트
print(torch.tanh(z))                   # 값 -1~1 — 후보. 섞지 말 것
""",
    )
    put(
        "ptn04",
        "cell",
        """
# c_t = f * c_prev + i * c_tilde
print("곱해서 누르는 길 + 더해서 흐르는 길")
""",
    )
    put(
        "ptn04",
        "ret",
        """
import torch.nn as nn
lstm = nn.LSTM(8, 16, batch_first=True)
# output, (h_n, c_n) = lstm(x)
print("RNN/GRU 는 h 하나, LSTM 은 (h, c) 튜플")
""",
    )
    put(
        "ptn04",
        "seed",
        """
# 같은 LSTM 을 시드 42,43,44 로 세 번
# 차이 > 흔들림*2 일 때만 "낫다" 고 말한다
print("한 번 돌린 숫자로 우열을 말하지 않는다")
""",
    )
    put(
        "ptn04",
        "gru",
        """
import torch.nn as nn
print("GRU 게이트 2개, 셀 상태 없음")
print(nn.GRU(8, 16))                   # 반환은 RNN 처럼 h 하나
""",
    )
