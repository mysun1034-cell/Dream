"""Streamlit · ML · DL · 미니 · Spring AI · PyTorch NLP 슬라이드."""

MORE_LECTURES = [
    {
        "id": "st01",
        "track": "Streamlit",
        "title": "Day 1 · 첫 앱과 위젯",
        "date": "5/21",
        "one_liner": "파이썬 파일을 위에서 아래로 다시 실행하면 웹 화면이 된다. 그게 Streamlit이다.",
        "explain": """HTML을 안 쓰고도 탐색 결과를 팀에 보여줄 때 쓴다.
Flask는 집 전체를 직접 짓는 것이고, Streamlit은 **조립식 부스**다.

버튼을 누르면 파일이 **처음부터 다시** 돈다. 이게 top-to-bottom rerun이다.
위젯 값이 변수가 되고, 그 변수로 표를 거르고, 화면에 다시 그린다.

- `st.sidebar` 는 설정 패널
- `st.columns` / `st.tabs` 는 자리를 나눈다
- `@st.cache_data` 는 같은 데이터를 매번 다시 안 읽게 한다

미션은 타이타닉 필터 대시보드. 패턴은 하나다.
**위젯 → 변수 → 필터 → 출력.**""",
        "quiz_topic": "Streamlit rerun, 위젯-필터 패턴, cache_data, Flask와의 차이.",
        "items": [
            {"id": "what", "title": "왜 Streamlit인가", "body": "파이썬 스크립트를 웹으로 보여 주는 조립식 부스. 데이터 탐색을 팀에 공유할 때."},
            {"id": "rerun", "title": "위에서 아래로 다시", "body": "버튼·슬라이더가 바뀌면 파일을 처음부터 다시 실행한다. 일반 변수는 그때 리셋된다."},
            {"id": "widget", "title": "위젯 → 필터", "body": "사이드바에서 고른 값이 변수가 되고, 그 값으로 표를 거른다."},
            {"id": "layout", "title": "칸과 탭", "body": "columns는 가로 분할, tabs는 화면을 갈라 둔다. metric은 큰 숫자 한 칸."},
            {"id": "cache", "title": "@st.cache_data", "body": "같은 CSV를 rerun마다 다시 읽지 않는다. 인자가 같으면 저장된 결과를 꺼낸다."},
        ],
    },
    {
        "id": "st02",
        "track": "Streamlit",
        "title": "Day 2 · session_state와 배포",
        "date": "5/22",
        "one_liner": "화이트보드는 rerun마다 지워진다. 전자칠판이 session_state다.",
        "explain": """카운터를 `count = 0` 으로 쓰면 버튼을 눌러도 항상 0이다.
화면이 다시 그려질 때 변수가 처음부터니까.

`st.session_state` 는 그 사람 탭이 열려 있는 동안 남는 **전자칠판**이다.
키를 먼저 만들고(`if 'count' not in ...`) 그다음에 더한다.

여러 화면이면 `st.Page` + `st.navigation`.
페이지가 달라도 session_state는 **같은 옷장**이다.

`st.form` 은 슬라이더를 움직일 때마다 계산하지 말고, 제출할 때 한 번만.
배포는 `requirements.txt` 를 GitHub에 올리고 share.streamlit.io 에 연결한다.""",
        "quiz_topic": "session_state와 일반 변수 차이, 멀티페이지 공유, form, Community Cloud.",
        "items": [
            {"id": "board", "title": "전자칠판", "body": "일반 변수는 화이트보드라 rerun마다 지워진다. session_state만 남는다."},
            {"id": "key", "title": "key= 와 get", "body": "위젯에 key를 주면 값이 자동으로 칠판에 적힌다. 없으면 .get으로 기본값을."},
            {"id": "pages", "title": "여러 페이지", "body": "st.Page + st.navigation. 홈에서 저장한 값을 대시보드에서 그대로 읽는다."},
            {"id": "form", "title": "form과 파일", "body": "form은 제출 전까지 rerun을 묶는다. file_uploader로 CSV를 받는다."},
            {"id": "deploy", "title": "배포", "body": "requirements.txt + GitHub push + share.streamlit.io. data 폴더도 같이 올린다."},
        ],
    },
    {
        "id": "ml01",
        "track": "머신러닝",
        "title": "Day 1 · 지도학습과 k-NN",
        "date": "5/26",
        "one_liner": "규칙을 사람이 쓰지 않고, 예시를 보여 이웃을 보고 고른다.",
        "explain": """스팸을 단어 목록으로 막으면 새 말이 나올 때마다 목록을 고친다.
10만 통을 보여 주고 **스스로 경계**를 찾게 하는 쪽이 머신러닝이다.

세 갈래:

- 지도학습: 정답 라벨이 있다. 분류(도미/빙어)와 회귀(집값)
- 비지도학습: 라벨 없이 묶음·축을 찾는다
- 강화학습: 보상으로 행동을 고친다

파이프라인은 항상 같다. 데이터 → 특성 → 훈련/테스트 분리 → `fit` → `predict` → `score`.
k-NN은 전학생을 **제일 가까운 k명**으로 분류하는 것이다.
거리로 판단하니 길이(cm)와 무게(g)를 그대로 두면 무게가 이긴다. 그래서 StandardScaler.""",
        "quiz_topic": "AI/ML/DL, 지도학습 파이프라인, train_test_split, k-NN, 스케일.",
        "items": [
            {"id": "three", "title": "세 동심원", "body": "AI 안에 ML, ML 안에 DL. ML은 예시로 규칙을 찾는다."},
            {"id": "kinds", "title": "세 학습", "body": "지도는 정답이 있다. 비지도는 구조만. 강화는 보상."},
            {"id": "pipe", "title": "fit · predict · score", "body": "모델이 바뀌어도 sklearn 세 메서드는 같다."},
            {"id": "split", "title": "왜 나누나", "body": "시험지를 미리 보여 주고 점수 내면 1.0이 나온다. 그게 일반화가 아니다."},
            {"id": "knn", "title": "가까운 k명", "body": "새 생선의 길이와 무게 옆 이웃을 본다. k가 커지면 다수결이 둔해진다."},
            {"id": "scale", "title": "거리의 함정", "body": "단위가 다르면 큰 숫자가 거리를 독점한다. 평균 0 표준편차 1로 맞춘다."},
        ],
    },
    {
        "id": "ml02",
        "track": "머신러닝",
        "title": "Day 2 · 회귀와 규제",
        "date": "5/27",
        "one_liner": "직선을 긋고, 구부리고, 너무 구부러지면 벌점을 준다.",
        "explain": """k-NN 회귀는 이웃 무게의 평균이다. 훈련 범위 밖(50cm 농어)은 **외삽을 못 한다**.
선형 회귀는 `무게 = w×길이 + b`. 범위를 벗어나도 직선이 이어진다.

오차를 제곱해 더하는 게 MSE. 부호가 서로 지우지 못하게.
산 내려가듯 기울기를 따라 w를 고치는 게 경사 하강법이다.

길이만으로 안 구부러지면 길이²를 특성으로 넣는다(다항).
degree=5 로 특성을 55개 만들면 훈련은 외우고 테스트 R²는 −144가 된다.

규제: 계수에 벌점. Ridge(L2)는 계수를 작게, Lasso(L1)는 0으로 만들어 특성을 고른다.
스케일은 **훈련으로만** fit 한다. 테스트까지 섞어 맞추면 Data Leakage.""",
        "quiz_topic": "k-NN 회귀 외삽, 선형/다항, MSE, Ridge/Lasso, Data Leakage.",
        "items": [
            {"id": "leak", "title": "Data Leakage", "body": "스케일러를 전체 데이터로 fit 하면 시험지 평균을 미리 본 것이다. 훈련만 fit, 테스트는 transform."},
            {"id": "knnr", "title": "이웃의 평균", "body": "k-NN 회귀는 가까운 무게를 평균한다. 본 적 없는 긴 농어는 못 그린다."},
            {"id": "line", "title": "직선과 MSE", "body": "최적의 기울기와 절편. 오차를 제곱하는 이유 중 하나는 플러스 마이너스가 상쇄되지 않게."},
            {"id": "poly", "title": "구부리다 외움", "body": "특성을 너무 늘리면 훈련 점을 통과하는 구불구불. 테스트는 망한다."},
            {"id": "reg", "title": "Ridge와 Lasso", "body": "Ridge는 계수를 작게. Lasso는 일부 계수를 0으로. 규제 전에 스케일링이 필수."},
        ],
    },
    {
        "id": "ml03",
        "track": "머신러닝",
        "title": "Day 3 · 분류 지표와 편차",
        "date": "5/28",
        "one_liner": "정확도 90%여도 생존자를 전부 놓칠 수 있다. 표의 네 칸을 봐야 한다.",
        "explain": """로지스틱 회귀는 직선으로 z를 만들고, 시그모이드로 0~1 확률을 만든다.
이름이 회귀여도 **하는 일은 분류**다. 여러 종이면 소프트맥스.

정확도의 함정: 타이타닉에서 무조건 ‘사망’이라고 하면 62%다.
생존자 342명을 전부 놓친다. Recall=0.

혼동 행렬 네 칸: TP FP FN TN.
Precision은 양성으로 찍은 것 중 진짜. Recall은 진짜 양성 중 찾아낸 것.
한쪽을 올리면 다른 쪽이 내려가는 경우가 많다. F1은 둘의 조화평균.

학습 점수는 높은데 테스트가 낮으면 High Variance(외움).
둘 다 낮으면 High Bias(너무 단순).""",
        "quiz_topic": "로지스틱/시그모이드/소프트맥스, 혼동행렬, Precision Recall, bias variance.",
        "items": [
            {"id": "sig", "title": "시그모이드", "body": "직선 z는 −∞~∞. 확률은 0~1이어야 해서 S자 곡선으로 눌러 담는다."},
            {"id": "ce", "title": "왜 Cross-Entropy", "body": "시그모이드에 MSE를 얹으면 손실 언덕이 울퉁불퉁해진다. 놀란 정도를 재는 쪽이 맞다."},
            {"id": "acc", "title": "정확도의 함정", "body": "다수 클래스만 맞춰도 점수가 나온다. 생존자를 전부 놓쳐도 62%."},
            {"id": "prf", "title": "Precision · Recall", "body": "찍은 것 중 맞음 / 실제 중 찾아냄. 의료는 보통 놓침(FN)이 더 무섭다."},
            {"id": "bv", "title": "Bias / Variance", "body": "둘 다 낮음=단순. 훈련만 높음=외움. 표로 다음 행동을 고른다."},
        ],
    },
    {
        "id": "ml04",
        "track": "머신러닝",
        "title": "Day 4 · 트리와 교차검증",
        "date": "5/29",
        "one_liner": "스무고개로 방을 나누고, 나무 여러 그루가 투표한다.",
        "explain": """결정 트리는 ‘다리가 4개인가요?’처럼 **한 번에 많이 갈라지는 질문**을 고른다.
Gini/Entropy는 방이 얼마나 섞였는지. 정보 이득이 큰 질문이 이긴다.
임계값 비교라 **스케일링이 필요 없다**.

가지를 안 자르면 와인 6497병마다 질문을 만들어 훈련 99.7%. High Variance.
`max_depth=3` 이 가지치기다.

랜덤 포레스트는 나무를 다양하게(복원 추출 + 특성 일부) 키워 다수결.
똑같은 나무 1000그루는 의미 없다. 핵심은 다양성.

한 번 나눠 본 테스트 36개는 주사위 36번이다.
K-Fold는 자리를 바꿔 가며 여러 번 본다. GridSearchCV는 메뉴 조합을 그 자리에서 시식한다.""",
        "quiz_topic": "Gini, max_depth, 랜덤포레스트 다양성, K-Fold, GridSearchCV.",
        "items": [
            {"id": "gini", "title": "방의 어지러움", "body": "한 색만 있으면 불순도 0. 반반이면 최대. 좋은 질문은 한 번에 많이 가른다."},
            {"id": "scale0", "title": "스케일 없어도", "body": "숫자 크기 비교가 아니라 임계값 예/아니오. StandardScaler가 답을 안 바꾼다."},
            {"id": "prune", "title": "가지치기", "body": "깊이 제한이 없으면 훈련 점을 외운다. max_depth가 가장 흔한 손잡이."},
            {"id": "rf", "title": "여러 의사", "body": "배깅은 독립적으로 보고 다수결. 부스팅은 앞 사람의 오답 노트."},
            {"id": "cv", "title": "K-Fold와 그리드", "body": "한 조각 hold-out은 흔들린다. 파라미터 조합 × 폴드를 자동으로 돈다."},
        ],
    },
    {
        "id": "ml05",
        "track": "머신러닝",
        "title": "Day 5 · 군집·PCA·이상",
        "date": "6/01",
        "one_liner": "정답이 없어도 가까운 것끼리 모으고, 분산이 큰 방향으로 납작하게 만든다.",
        "explain": """지도학습은 (x, y)였다. 오늘은 x만 있다.
과일 사진 300장을 사람이 손으로 나누려면 픽셀 1만 개를 눈으로 비교해야 한다.

K-Means: 치킨집 K개를 아무 데나 두고, 손님을 가까운 집에 보내고, 집을 손님 가운데로 옮긴다. 반복.
K는 엘보우(inertia가 꺾이는 팔꿈치)로 고른다.

이상 탐지: 가장 가까운 중심까지 거리가 유난히 먼 점이 이상이다.

PCA: 1만 픽셀을 ‘정보가 많이 남는 축’ 50개로 줄인다.
다음 주인 딥러닝은 이 특성을 **사람이 안 고르고** 층이 찾는다.""",
        "quiz_topic": "비지도학습, K-Means 4단계, 엘보우, PCA 차원축소, 이상탐지.",
        "items": [
            {"id": "unsup", "title": "라벨이 없다", "body": "정답을 맞히는 게 아니라 덩어리와 축을 찾는다."},
            {"id": "km", "title": "치킨집 네 걸음", "body": "초기화 → 배정 → 중심 이동 → 반복. 손님(점)은 가장 가까운 집으로."},
            {"id": "elbow", "title": "엘보우", "body": "K를 늘릴수록 inertia는 줄어든다. 팔꿈치에서 멈춘다."},
            {"id": "out", "title": "먼 점이 이상", "body": "transform으로 중심까지 거리. 최솟값이 큰 샘플이 이상치 후보다."},
            {"id": "pca", "title": "납작하게", "body": "분산이 큰 방향으로 축을 돌려 차원을 줄인다. 시간은 줄고 패턴은 남는다."},
        ],
    },
    {
        "id": "dl01",
        "track": "딥러닝",
        "title": "Day 1 · 퍼셉트론과 Keras",
        "date": "6/02",
        "one_liner": "뉴런 하나는 가중합 다음에 활성화다. AND는 되고 XOR은 직선 하나로 안 된다.",
        "explain": """어제까지는 사람이 특성을 골랐다. 오늘부터는 층이 중간 표현을 만든다.

퍼셉트론: `z = w·x + b` 를 시그모이드에 넣으면 확률.
편향만 바꿔 AND가 OR가 된다. XOR은 점이 엇갈려 **직선 하나로는 불가**.
그래서 은닉층을 쌓는다(MLP). 활성화를 빼면 층 두 개도 층 하나와 같다.

Keras 5단계: 정의 → 컴파일 → 학습 → 평가 → 예측.
Fashion MNIST 28×28은 Flatten으로 784칸이 된다.
단층 소프트맥스는 로지스틱 회귀와 식이 같다. 그래서 점수도 비슷하다.""",
        "quiz_topic": "퍼셉트론, XOR, 활성화가 필요한 이유, Flatten, Keras 5단계.",
        "items": [
            {"id": "perc", "title": "뉴런 한 개", "body": "가중합 + 편향 → 활성화. numpy 몇 줄이면 AND 게이트가 된다."},
            {"id": "xor", "title": "XOR은 안 된다", "body": "결정 경계가 직선이라 엇갈린 네 점을 못 가른다. 은닉층이 구부린다."},
            {"id": "act", "title": "활성화가 없으면", "body": "선형 뒤에 선형은 선형. 층을 쌓은 이유가 사라진다."},
            {"id": "flat", "title": "Flatten", "body": "28×28 사진을 784 줄로 편다. 자리(공간) 정보는 여기서 버린다."},
            {"id": "keras", "title": "레고 다섯 칸", "body": "Sequential 정의, compile, fit, evaluate, predict. 시드는 재현용."},
        ],
    },
    {
        "id": "dl02",
        "track": "딥러닝",
        "title": "Day 2 · 역전파와 옵티마이저",
        "date": "6/04",
        "one_liner": "틀린 정도는 뒤에서 앞으로 흘러 각 가중치의 몫이 된다.",
        "explain": """순전파는 입력에서 예측까지. 역전파는 손실에서 가중치까지.
연쇄 법칙: 은닉층 몫은 출력층을 통과해서 온다.

시그모이드 도함수 최댓값이 0.25라, 층을 쌓을수록 기울기가 **0.25ⁿ** 으로 죽는다.
은닉층은 ReLU(`max(0,z)`). 출력층만 문제에 맞는 함수.

옵티마이저는 `W ← W − α∇L`.
SGD는 보폭이 전 파라미터에 같고, Adam은 파라미터마다 보폭을 조절한다.
같은 2층 네트워크에서 Adam이 보통 더 빨리 내려간다.""",
        "quiz_topic": "역전파 흐름, vanishing gradient, ReLU, SGD vs Adam.",
        "items": [
            {"id": "bp", "title": "뒤에서 앞으로", "body": "Loss → 출력층 기울기 → 은닉층 기울기. 각 W가 손실에 기여한 정도."},
            {"id": "vg", "title": "기울기 소멸", "body": "시그모이드를 은닉에 쌓으면 0.25가 곱해져 앞층이 안 배운다."},
            {"id": "relu", "title": "ReLU", "body": "음수는 0, 양수는 그대로. 기울기가 안 죽고 계산이 싸다."},
            {"id": "opt", "title": "보폭을 누가", "body": "SGD는 같은 α. Adam은 모멘텀+적응 보폭. compile의 optimizer 한 줄."},
            {"id": "dnn", "title": "은닉층 하나", "body": "784→100→10. Day1 단층보다 표현이 늘어 val이 보통 올라간다."},
        ],
    },
    {
        "id": "dl03",
        "track": "딥러닝",
        "title": "Day 3 · 과적합과 Dropout",
        "date": "6/05",
        "one_liner": "에폭을 늘린다고 검증이 계속 좋아지지 않는다. 곡선의 반전을 본다.",
        "explain": """훈련 정확도만 올리면 노이즈까지 외운다.
학습 곡선에서 val_loss가 내려가다 다시 올라가는 지점이 과적합의 시작이다.

Dropout(0.3): 학습 때 뉴런 30%를 끈다. 한 뉴런에 기대지 못하게.
테스트 때는 끄지 않는다. 학습 때 미리 보정해 두므로(inverted) 기댓값이 맞는다.

EarlyStopping은 val이 안 좋아지면 멈춘다. patience는 몇 번 참을지.
ModelCheckpoint는 그 사이 제일 좋았던 가중치를 파일로 남긴다.""",
        "quiz_topic": "학습 곡선, Dropout, inverted dropout, EarlyStopping, 체크포인트.",
        "items": [
            {"id": "curve", "title": "곡선의 반전", "body": "train loss는 계속 내려가도 val loss가 돌아서면 외우기 시작한 것."},
            {"id": "drop", "title": "랜덤으로 끄기", "body": "학습 때만 일부 뉴런을 끈다. 앙상블과 비슷한 효과. 파라미터는 안 는다."},
            {"id": "inv", "title": "왜 inverted", "body": "보정을 테스트가 아니라 학습 때 한다. 테스트 분포가 그대로다."},
            {"id": "es", "title": "일찍 멈추기", "body": "patience만큼 기다려 보고 복원한다. 에폭 수를 손으로 안 고른다."},
            {"id": "ckpt", "title": "제일 좋은 몸", "body": "매 에폭 저장해 두면, 멈춘 순간이 아니라 정점이 파일에 있다."},
        ],
    },
    {
        "id": "dl04",
        "track": "딥러닝",
        "title": "Day 4 · CNN 기초",
        "date": "6/08",
        "one_liner": "사진을 한 줄로 펴면 이웃 픽셀이 남남이 된다. 필터가 자리를 지키며 훑는다.",
        "explain": """Dense+Flatten은 28×28을 784로 펴서 ‘이 픽셀 옆이 어디인지’를 버린다.
합성곱은 3×3 돋보기를 밀며 ‘이 자리에 이 무늬가 있나’를 계산한다.

같은 필터를 그림 전체에 쓰므로 파라미터가 적다.
784×32 vs 3×3×32. 그걸 가중치 공유라고 한다.

padding='same' 은 테두리에 0을 붙여 크기를 지킨다.
stride=2 는 두 칸씩 뛰어 출력이 반이 된다.
MaxPooling은 2×2에서 최댓값만 남겨 또 반으로.

얕은 층은 에지, 깊은 층은 무늬. 입력은 (28,28,1) 4차원이어야 한다.""",
        "quiz_topic": "Flatten의 한계, 합성곱과 가중치 공유, padding/stride, MaxPool.",
        "items": [
            {"id": "flatbad", "title": "펴면 자리를 잃는다", "body": "이웃한 픽셀이 벡터에서는 멀리 떨어진다. 공간 구조가 사라진다."},
            {"id": "conv", "title": "돋보기 슬라이딩", "body": "작은 필터를 겹쳐 곱해 더한다. 결과가 특성 맵."},
            {"id": "share", "title": "가중치 공유", "body": "위치마다 새 가중치를 두지 않는다. 같은 3×3을 전 칸에 쓴다."},
            {"id": "pad", "title": "패딩과 보폭", "body": "same은 크기 유지. stride 2는 해상도 절반."},
            {"id": "pool", "title": "최댓값만", "body": "2×2에서 가장 큰 반응만 남긴다. ‘여기 있었나’를 남긴다."},
        ],
    },
    {
        "id": "dl05",
        "track": "딥러닝",
        "title": "Day 5 · 전이학습과 탐지",
        "date": "6/09",
        "one_liner": "남이 익힌 눈을 빌려 내 분류 머리만 갈아 끼운다.",
        "explain": """어제 CNN이 0.91이 나왔다면, 32개 필터가 **무엇을 보는지** 그림으로 꺼낼 수 있다.
Sequential은 맨 끝만 준다. 중간 층을 보려면 함수형 API로 입출력을 직접 잇는다.

데이터 증강: 뒤집고 돌려서 본 적 없는 각도를 만든다.
전이학습: ImageNet으로 익은 MobileNet 몸을 얼리고(`trainable=False`) 내 10클래스 머리만 학습.
Fine-Tuning: 나중에 뒤쪽 층을 아주 작은 학습률로 살짝 푼다.

분류는 ‘이 사진은 무엇인가’ 답 하나.
탐지는 ‘어디에 무엇이’라 상자 개수가 가변이다. YOLO는 그 추론을 몇 줄로 돌린다.""",
        "quiz_topic": "필터 시각화, 함수형 API, 증강, 전이학습 vs 파인튜닝, 분류 vs 탐지.",
        "items": [
            {"id": "vis", "title": "필터를 본다", "body": "Conv 가중치 shape (3,3,1,32). 학습 전후를 그림으로 비교한다."},
            {"id": "fn", "title": "함수형 API", "body": "중간 층 출력이 필요하면 Model(입력, 그 층 출력)으로 새 모델을 만든다."},
            {"id": "aug", "title": "데이터 증강", "body": "회전·뒤집기. 본 방향만 잘하던 모델이 다른 각도에도 버틴다."},
            {"id": "tl", "title": "몸통은 얼리고", "body": "include_top=False 로 머리를 떼고, 내 Dense만 학습한다."},
            {"id": "det", "title": "상자까지", "body": "분류는 라벨 하나. 탐지는 클래스+좌표. 개수가 이미지마다 다르다."},
        ],
    },
    {
        "id": "mini1",
        "track": "미니프로젝트",
        "title": "미니1 · Git 협업 킥오프",
        "date": "6/10",
        "one_liner": "main에 직접 쓰지 않는다. 내 가지에서 작업하고 PR로 합친다.",
        "explain": """혼자 Git은 `add/commit` 이면 된다. 네 명이 같은 README를 고치면
나중에 push한 사람이 앞사람을 **덮어쓴다**.

해결: `main` 은 발표본, 작업은 `feat/이름-작업` 가지.
흐름: pull로 최신화 → 가지 생성 → 커밋 → push → Pull Request → merge → 다시 pull.

충돌을 줄이는 규칙: main 직접 push 금지, 작업 전 항상 최신화, 같은 줄을 동시에 안 고친다.
브랜치 이름은 영문. 한글 가지 이름은 도구가 깨질 수 있다.""",
        "quiz_topic": "브랜치, PR, clone/collaborator, main 직접 push 금지.",
        "items": [
            {"id": "cover", "title": "덮어쓰기", "body": "main에 둘이 직접 push하면 나중 커밋이 앞 작업을 지운다."},
            {"id": "br", "title": "내 작업 공간", "body": "git switch -c feat/이름-작업. main은 팀의 최종본."},
            {"id": "pr", "title": "Pull Request", "body": "내 가지를 main에 합쳐 달라는 요청. 합치기 전에 눈이 한 번 더 본다."},
            {"id": "flow", "title": "하루 루프", "body": "아침 pull → 가지 → add/commit → push → PR → merge 후 다시 pull."},
            {"id": "rule", "title": "충돌 예방", "body": "직접 push 금지, 최신화, 파일/줄을 나눠 맡기. 해결법은 다음 시간."},
        ],
    },
    {
        "id": "mini1b",
        "track": "미니프로젝트",
        "title": "미니1 · EDA와 전처리",
        "date": "6/11",
        "one_liner": "모델을 돌리기 전에 표를 읽고, 새는 정보 없이 숫자로 바꾼다.",
        "explain": """미니1 오후의 일: 데이터를 **눈으로 읽고** 모델이 먹을 수 있게 손질한다.

빠진 값, 이상한 범위, 범주형 문자, 훈련/테스트 분포 차이.
전처리는 훈련으로만 규칙을 배우고 테스트에는 그 규칙만 적용한다.
스케일·인코더를 전체에 fit 하면 Day2에서 말한 Leakage다.

제출 노트북에는 ‘무엇을 봤고 왜 그렇게 고쳤는지’가 코드만큼 중요하다.""",
        "quiz_topic": "EDA 순서, 결측, 인코딩, 스케일, 전처리 leakage.",
        "items": [
            {"id": "look", "title": "먼저 본다", "body": "shape, dtypes, 결측, 기초통계, 타깃 비율. 그래프는 가설을 확인하는 도구."},
            {"id": "miss", "title": "빈칸", "body": "왜 비었는지에 따라 삭제/채움이 갈린다. 테스트에만 있는 방식이면 안 된다."},
            {"id": "enc", "title": "글자를 숫자로", "body": "범주는 원-핫 또는 순서 인코딩. 훈련에 없던 값은 미리 규칙을 정한다."},
            {"id": "prep", "title": "손질은 훈련만", "body": "scaler·encoder는 train으로 fit. test/val은 transform만."},
        ],
    },
    {
        "id": "sai01",
        "track": "Spring AI",
        "title": "Day 1 · ChatClient",
        "date": "7/02",
        "one_liner": "컨트롤러가 DB 대신 모델을 호출한다. ChatClient가 그 문이다.",
        "explain": """지금까지는 사용자 → 컨트롤러 → 서비스 → DB.
오늘은 서비스 옆에 **AI 모델**이 붙는다.

프로바이더마다 JSON이 다른데, Spring AI가 ChatClient로 그 차이를 숨긴다.
의존성만 넣으면 Builder 빈이 자동으로 생긴다.

체이닝: `.system()` 역할, `.user()` 질문, `.call().content()` 문자열.
토큰은 돈이다. 입력과 출력 모두 센다.
temperature는 다음 토큰을 얼마나 다양하게 고를지.""",
        "quiz_topic": "AI 아키텍처, ChatClient vs ChatModel, system/user, 토큰, temperature.",
        "items": [
            {"id": "arch", "title": "세 칸", "body": "프론트 → 백엔드 → 모델. DB CRUD와 달리 답이 비결정적일 수 있다."},
            {"id": "why", "title": "왜 프레임워크", "body": "OpenAI/Gemini JSON이 다르다. ChatClient 한 인터페이스로 흡수한다."},
            {"id": "chat", "title": "체이닝", "body": "prompt().system().user().call().content(). 빈은 Builder로 만든다."},
            {"id": "tok", "title": "토큰 = 돈", "body": "한글은 자주 여러 조각. RPM/RPD 한도를 넘기면 호출이 거절된다."},
            {"id": "temp", "title": "temperature", "body": "낮으면 뻔하고 안전. 높으면 다양. 모델 옵션의 맛보기."},
        ],
    },
    {
        "id": "sai02",
        "track": "Spring AI",
        "title": "Day 2 · 구조화 출력",
        "date": "7/03",
        "one_liner": "‘JSON으로 해 줘’는 부탁이다. record + entity()가 계약이다.",
        "explain": """문자열을 `+` 로 이어 프롬프트를 만들면 읽기 어렵고 값이 어디에 들어갔는지 안 보인다.
SQL에 `?` 를 쓰듯 `{audience}` 자리를 만들고 `.param()` 으로 채운다.

상담원이 읽는 요약은 문자열로 충분하다.
코드가 `if (priority == HIGH)` 하려면 필드가 고정돼야 한다.

`.entity(InquiryResult.class)` 는 스키마 지시문을 붙이고 JSON을 record로 바꾼다.
그래도 모델이 어기면 변환 예외. 100%는 아니다.
목록이면 `List<MovieRecommendation>`.""",
        "quiz_topic": "PromptTemplate, 부탁 vs 계약, entity(), record, BeanOutputConverter.",
        "items": [
            {"id": "tpl", "title": "템플릿", "body": "{변수} 자리를 두고 param으로 채운다. 프롬프트와 자바가 안 섞인다."},
            {"id": "ask", "title": "부탁의 한계", "body": "JSON으로만 이라고 해도 마크다운이 섞이거나 키가 흔들린다."},
            {"id": "ent", "title": "entity()", "body": "record를 넘기면 지시+파싱. 코드가 바로 필드를 읽는다."},
            {"id": "list", "title": "여러 건", "body": "List<Record> 또는 List<String>. 받는 모양에 맞춰 컨버터가 갈린다."},
            {"id": "nat", "title": "네이티브", "body": "useProviderStructuredOutput는 생성 단계부터 스키마를 강제한다. 오늘은 눈으로."},
        ],
    },
    {
        "id": "sai03",
        "track": "Spring AI",
        "title": "Day 3 · Advisor와 기억",
        "date": "7/06",
        "one_liner": "모델은 기억을 안 한다. 앱이 이전 말을 다시 넣고, Advisor가 앞뒤를 가로챈다.",
        "explain": """같은 ChatClient 호출마다 로그·길이 제한을 붙이려면 서비스마다 복붙하게 된다.
Advisor는 스프링 인터셉터처럼 **호출 앞뒤**에 끼워진다. order가 작을수록 전처리가 먼저(양파).

‘내 이름은 민준’ 다음에 ‘내 이름이 뭐야’ — Memory 없으면 모른다.
MessageChatMemoryAdvisor가 최근 N개를 다시 실어 보낸다.
conversationId가 없으면 예외. 대화 묶음의 이름이다.

In-Memory는 서버가 죽으면 사라진다.
JDBC/H2로 바꾸면 재시작 뒤에도 같은 id로 이어진다.""",
        "quiz_topic": "Advisor 전후처리, Chat Memory, conversationId, InMemory vs JDBC.",
        "items": [
            {"id": "adv", "title": "가로채기", "body": "요청/응답을 가로채 길이 제한, 호출 횟수, 로그, 금칙어를 붙인다."},
            {"id": "order", "title": "양파 순서", "body": "getOrder()가 작을수록 전처리는 먼저, 후처리는 나중에."},
            {"id": "mem", "title": "기억은 앱이", "body": "모델 능력이 아니다. 이전 messages를 매번 다시 넣는다."},
            {"id": "cid", "title": "conversationId", "body": "어느 창의 대화인지. 빼먹으면 메모리 Advisor가 바로 예외."},
            {"id": "jdbc", "title": "재시작 뒤에도", "body": "메모리 저장소는 프로세스가 끝이면 리셋. JDBC면 같은 id로 복원."},
        ],
    },
    {
        "id": "sai04",
        "track": "Spring AI",
        "title": "Day 4 · 멀티모달",
        "date": "7/07",
        "one_liner": "UserMessage에 파일 칸이 하나 늘었을 뿐이다. 이미지·PDF·오디오가 같은 패턴이다.",
        "explain": """파일은 JSON이 아니라 multipart로 온다.
`UserMessage` 에 `media` 리스트를 붙인다. MIME + 바이트.

이미지 영수증 → `ReceiptInfo` record.
PDF → `PdfSummary`. 오디오는 MIME만 다르다.
세 갈래 코드가 같고 화이트리스트와 record만 다르다.

`.entity()` 는 프로그램이 쓸 칸. `.content()` 는 사람이 읽을 글.
Memory는 요약만 남기는 게 아니다. 다음 턴에 **원본 미디어까지** 다시 실릴 수 있다.""",
        "quiz_topic": "multipart, Media/MIME, 이미지·PDF·오디오 동일 패턴, entity vs content.",
        "items": [
            {"id": "mp", "title": "multipart", "body": "파일은 쿼리스트링이 아니다. boundary로 나뉜 바이너리 파트."},
            {"id": "media", "title": "media 한 칸", "body": "텍스트 + MIME + Resource. 새 API가 아니라 메시지 확장."},
            {"id": "three", "title": "세 파일이 같다", "body": "toResource → UserMessage.media → entity(record). MIME만 갈린다."},
            {"id": "ec", "title": "entity vs content", "body": "DB/분기는 record. 사람이 읽거나 구조가 비면 자유 텍스트."},
            {"id": "replay", "title": "기억은 재생", "body": "다음 질문에 이전 이미지·PDF가 다시 붙을 수 있다. 토큰이 커진다."},
        ],
    },
    {
        "id": "sai05",
        "track": "Spring AI",
        "title": "Day 5 · 도구와 MCP",
        "date": "7/08",
        "one_liner": "모델은 지금 시각을 모른다. 요청만 하고, 실행은 @Tool 메서드가 한다.",
        "explain": """‘지금 몇 시야?’ — 모델은 시계가 없다.
`@Tool` 메서드를 `.tools(...)` 에 실으면, 모델이 호출을 **요청**하고 앱이 실행한 뒤 다시 넣는다.
왕복 루프는 Spring AI가 돌린다. description만 보고 도구를 고른다.

로컬 도구는 앱마다 다시 짠다. MCP는 남이 띄운 도구 서버에 붙는 표준.
클라이언트는 부팅 때 서버에 연결한다. 서버가 안 뜨면 **앱 전체가 안 뜬다**.

반대 방향: `@McpTool` 로 우리 메서드를 서버로 노출할 수 있다.""",
        "quiz_topic": "Tool Calling 왕복, @Tool description, MCP client/server, 부팅 실패.",
        "items": [
            {"id": "req", "title": "실행은 앱이", "body": "모델은 요청서만. @Tool 메서드가 실제 시각·고객등급·사내규정을 가져온다."},
            {"id": "desc", "title": "설명서가 선택", "body": "모델은 자바 코드를 안 본다. description이 언제 쓸지 알려 준다."},
            {"id": "mcp", "title": "바퀴를 안 만든다", "body": "파일/웹 fetch를 앱마다 안 짠다. MCP 서버에 붙는다."},
            {"id": "boot", "title": "서버가 죽으면", "body": "MCP Client가 부팅 연결에 실패하면 컨텍스트가 실패해 전 엔드포인트가 죽는다."},
            {"id": "exp", "title": "우리가 서버", "body": "@Tool은 소비. @McpTool은 노출. 같은 스택의 반대쪽."},
        ],
    },
    {
        "id": "sai06",
        "track": "Spring AI",
        "title": "Day 6 · 스트리밍 통합",
        "date": "7/09",
        "one_liner": "답이 다 끝날 때까지 기다리지 않는다. 토큰이 나오는 대로 흘린다.",
        "explain": """`.call()` 은 상자. `.stream()` 은 컨베이어의 `Flux<String>`.
브라우저는 SSE(EventSource)로 한 방향으로 받는다.

함정: SSE가 앞 공백을 자르기도 하고, 연결이 끝나면 EventSource가 **같은 답을 다시** 받으러 간다.

대화는 두 테이블. LLM 윈도우(최근 N개)와 사람이 볼 전체 이력.
개발 중에는 5173(React) / 8080(API) / 5432(Postgres). 포트가 달라 CORS가 필요하다.
Docker로 Postgres 버전을 고정한다. 이 앱이 미니2 출발점이다.""",
        "quiz_topic": "call vs stream, Flux, SSE 함정, 이중 저장, CORS, Docker DB.",
        "items": [
            {"id": "flux", "title": "상자 vs 벨트", "body": "String은 다 담긴 뒤. Flux는 생기는 대로. 체이닝 마지막만 바꾼다."},
            {"id": "sse", "title": "SSE", "body": "서버→브라우저 한 방향. GET. 완료 후 자동 재연결을 직접 끊어야 한다."},
            {"id": "two", "title": "기억 둘", "body": "SPRING_AI_CHAT_MEMORY는 최근 창. chat_history는 화면 복원용 전체."},
            {"id": "cors", "title": "포트가 셋", "body": "화면·API·DB가 다르다. 브라우저가 8080을 치려면 CORS 허용."},
            {"id": "dock", "title": "상자 속 DB", "body": "PC마다 Postgres를 안 깐다. compose 한 줄로 같은 버전을 띄운다."},
        ],
    },
    {
        "id": "mini2",
        "track": "미니프로젝트",
        "title": "미니2 · 충돌과 리뷰",
        "date": "7/10",
        "one_liner": "작업은 dev에서 따고, 충돌은 사고가 아니라 Git이 사람에게 묻는 것이다.",
        "explain": """미니1은 main+feature였다. 미니2는 **main + dev + feature**.
발표본이 main, 통합이 dev, 할 일 하나가 feature.

PR 전에 `fetch` + `merge origin/dev` 로 충돌을 미리 만난다.
충돌 마커 `<<<<<<<` 는 내 것/상대 것. VSCode 버튼으로 고르거나 손으로 남긴다.
잘못하면 `git merge --abort`.

코드는 올리는 순간 팀 것. Files changed에서 줄 댓글.
Issue는 번호 붙은 할 일, Project Board는 칸반.
`.env` / 키는 `.gitignore`. 한 번 푸시된 비밀은 히스토리에 남는다.""",
        "quiz_topic": "main/dev/feature, fetch+merge, 충돌 마커, PR 리뷰, Issue, 키 유출.",
        "items": [
            {"id": "strat", "title": "세 층", "body": "feature → PR → dev. main은 마일스톤/발표 때."},
            {"id": "sync", "title": "최신화가 먼저", "body": "오래 안 당기면 충돌이 커진다. pull 한 방보다 fetch와 merge를 나눠 본다."},
            {"id": "conf", "title": "마커 읽기", "body": "<<<<<<< HEAD는 내 쪽. 둘을 살릴지 한쪽만 살릴지 사람이 정한다."},
            {"id": "rev", "title": "한 쌍의 눈", "body": "Approve / Request changes. 줄 단위 댓글이 리뷰다."},
            {"id": "issue", "title": "티켓과 칸반", "body": "Issue는 할 일 하나. 보드에서 Todo/진행/완료. 키는 커밋하지 않는다."},
        ],
    },
    {
        "id": "ptn01",
        "track": "PyTorch NLP",
        "title": "Day 1 · 텐서와 학습 루프",
        "date": "7/21",
        "one_liner": "Keras의 fit()이 숨겼던 다섯 줄을 내가 쓴다.",
        "explain": """환경은 WSL 안의 uv. `torch.cuda.is_available()` 이 오전의 목표다.
드라이버가 못 받는 CUDA를 깔면 에러 없이 False만 나온다.

텐서는 NumPy에 GPU와 기울기 추적이 붙은 것.
`*` 는 칸마다 곱, `@` 는 행렬곱. 딥러닝 코드의 절반은 shape 맞추기다.

autograd: `backward()` 가 기울기를 채운다. 기울기는 **누적**되니 다음 배치 전에 `zero_grad()`.

학습 5단계: forward → loss → zero_grad → backward → step.
`nn.CrossEntropyLoss` 는 이미 로그소프트맥스를 품는다. softmax를 한 번 더 씌우면 안 된다.""",
        "quiz_topic": "왜 PyTorch, 텐서/device, autograd 누적, 학습 루프 5단계, CrossEntropy.",
        "items": [
            {"id": "env", "title": "방 안의 방", "body": "WSL Ubuntu + uv venv. cuda.is_available()이 오늘 오전의 한 줄."},
            {"id": "ten", "title": "텐서", "body": "다차원 배열 + GPU + 기울기. shape를 못 맞추면 학습이 시작도 안 한다."},
            {"id": "ag", "title": "기울기는 누적", "body": "backward를 두 번 하면 grad가 더해진다. 그래서 매번 zero_grad."},
            {"id": "loop", "title": "다섯 줄", "body": "예측, 손실, 기울기 리셋, backward, optimizer.step. fit()의 속살."},
            {"id": "trap", "title": "두 함정", "body": "softmax+CrossEntropy 중복. optimizer에 parameters()를 안 넘김."},
        ],
    },
    {
        "id": "ptn02",
        "track": "PyTorch NLP",
        "title": "Day 2 · 텍스트를 숫자로",
        "date": "7/22",
        "one_liner": "자르고, 번호를 붙이고, 길이를 맞추고, 벡터로 바꾼다.",
        "explain": """어제 모델에 넣은 건 꽃잎 길이였다. 오늘은 문장이다.
영어 `split()` 은 그럭저럭. 한국어 ‘학교에서는’은 붙어 있어 교착어 형태소(Kiwi)가 필요하다.

사전: 0은 `<pad>`, 1은 `<unk>`. 처음 보는 말은 1.
길이가 다른 문장을 그냥 스택하면 오류. `pad_sequence` + `collate_fn`.

정수는 이름표일 뿐. one-hot은 차원이 폭발하고 단어 사이 각도가 전부 0.
`nn.Embedding` 은 룩업 테이블. 학습되면 비슷한 말이 비슷한 방향을 본다.
현대 LLM은 형태소 대신 데이터에서 익힌 서브워드.""",
        "quiz_topic": "토큰화(교착어), pad/unk, collate_fn, 임베딩 vs one-hot, 서브워드.",
        "items": [
            {"id": "tok", "title": "무엇으로 자르나", "body": "단어/글자/형태소. 한국어는 조사가 붙어 split이 깨진다."},
            {"id": "voc", "title": "0과 1을 비운다", "body": "pad와 unk를 예약. 빈도 순으로 번호를 붙인다. OOV는 1."},
            {"id": "pad", "title": "길이 맞추기", "body": "짧은 문장 뒤를 0으로. DataLoader는 collate_fn이 있어야 배치가 산다."},
            {"id": "emb", "title": "이름표가 벡터로", "body": "one-hot은 비슷함이 0. Embedding은 학습되면 dog-cat이 가까워진다."},
            {"id": "sub", "title": "서브워드", "body": "없는 단어를 있는 조각으로. 토큰 수가 곧 돈이다."},
        ],
    },
    {
        "id": "ptn03",
        "track": "PyTorch NLP",
        "title": "Day 3 · RNN과 순서",
        "date": "7/23",
        "one_liner": "같은 단어를 더하면 개가 사람을 문 것과 사람이 개를 문 것이 같아진다.",
        "explain": """순서가 뜻을 바꾼다. 가방 모델(합)은 순서를 지운다.
RNN은 지금까지의 줄거리 `h` 를 다음 단어와 섞는다.
`h_t = tanh(W_x x_t + W_h h_{t-1} + b)`
가중치는 시간마다 새로 생기지 않는다. 같은 W를 반복한다.

마지막 은닉으로 긍정/부정을 본다. 그래서 **앞쪽 패딩**을 써서 내용이 맨 뒤에 오게 한다.
뒤쪽 패딩이면 빈칸을 읽고 판단한다.

문장이 길어지면 앞 단어 기울기가 지수적으로 죽는다. 그게 내일 문(gate)의 이유다.""",
        "quiz_topic": "순차 데이터, RNN 식, 가중치 공유, 앞쪽 패딩, 기울기 소실.",
        "items": [
            {"id": "order", "title": "순서가 뜻", "body": "같은 토큰을 더하면 두 문장이 같은 벡터. 순서를 읽는 장치가 필요하다."},
            {"id": "hid", "title": "은닉 상태", "body": "지금까지 읽은 요약. 다음 단어와 함께 새 요약이 된다."},
            {"id": "eq", "title": "식 하나", "body": "tanh(Wx xt + Wh h_prev + b). 펼치면 같은 셀이 시간에 늘어서 있다."},
            {"id": "lpad", "title": "앞쪽 패딩", "body": "마지막 h로 분류하므로 실제 내용이 뒤에 와야 한다."},
            {"id": "van", "title": "앞을 잊는다", "body": "Wh를 거리만큼 곱하면 |β|<1 일 때 앞 신호가 0으로 간다."},
        ],
    },
    {
        "id": "ptn04",
        "track": "PyTorch NLP",
        "title": "Day 4 · LSTM과 GRU",
        "date": "7/24",
        "one_liner": "같은 수를 30번 곱하면 사라진다. 더해서 흐르는 길에 수도꼭지를 단다.",
        "explain": """0.9를 30번 곱하면 0.04. RNN의 `W_h` 반복이 그것이다.
LSTM은 셀 상태 `c` 라는 **덧셈 고속도로**를 만들고, 게이트로 얼마나 남길지 정한다.

forget / input / output. 게이트는 시그모이드(0~1 비율). tanh와 섞지 말 것.
`c_t = f⊙c_{t-1} + i⊙c̃`

`nn.LSTM` 은 `(h_n, c_n)` 튜플. `nn.RNN`/`nn.GRU` 는 `h_n` 만.
한 번 돌린 숫자로 우열을 말하면 안 된다. 같은 모델을 여러 시드에 돌려 **흔들림보다 큰 차이**만 믿는다.

GRU는 문을 두 개로 줄이고 c를 안 둔다. 현장에서는 둘 다 돌려 본다.""",
        "quiz_topic": "셀 상태, 게이트 3개, LSTM 반환 튜플, 시드 비교, GRU.",
        "items": [
            {"id": "mul", "title": "곱하면 사라진다", "body": "0.9³⁰ ≈ 0.04. 더하는 길을 내야 앞 기억이 남는다."},
            {"id": "gate", "title": "수도꼭지 셋", "body": "forget 남길까, input 새것을 넣을까, output 지금 내보낼까. 값은 sigmoid."},
            {"id": "cell", "title": "셀 상태", "body": "밖으로 안 나가고 안에서 더해져 흐른다. 기울기가 곱만으로 안 죽는다."},
            {"id": "ret", "title": "반환이 다르다", "body": "LSTM은 (h, c). 그대로 h만 받으면 분류 머리가 튜플을 받는다."},
            {"id": "seed", "title": "흔들림보다 큰가", "body": "세 시드 평균과 잡음을 잰 뒤, 차이가 잡음보다 커야 ‘낫다’고 말한다."},
            {"id": "gru", "title": "문 두 개", "body": "reset+update. 셀 상태 없이 h 하나. 가볍지만 항상 빠르거나 정확하진 않다."},
        ],
    },
]
