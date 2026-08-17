# matplotlib · plotly 데이터 시각화 — 260520

> 2026-05-20 · Python 기반 데이터 분석 및 데이터 시각화를 위한 Streamlit 웹 대시보드
> 원본: learner-guide.html · ES LMS

---

matplotlib · plotly 데이터 시각화 — 260520

# matplotlib · plotly 데이터 시각화

2026-05-20 (수) · 학습자 가이드

## 오늘 목표

- 질문 유형에 따라 차트를 선택할 수 있다

- matplotlib fig/ax 구조로 5종 기본 차트를 그린다

- plotly express로 인터랙티브 차트를 만들고 HTML로 저장한다

📌 오늘 노트북과 HTML 파일을 어제 만든 GitHub 저장소에 commit하면 포트폴리오가 쌓입니다.

## 0. 환경 설정

uv python pin 3.12
uv add pandas matplotlib plotly nbformat jupyter ipykernel

⚠️ Python 3.14.x는 VSCode Jupyter 표시 오류가 있습니다. uv python pin 3.12으로 버전을 고정하세요.

## 1. 차트 선택 기준

차트는 질문에서 시작한다. "무엇을 보여주고 싶은가?"를 먼저 결정하라.

| 질문 유형 | 알고 싶은 것 | 차트

| 분포 | 값이 어떻게 퍼져 있는가? | 히스토그램, 박스플롯

| 비교 | A vs B 어느 쪽이 큰가? | 막대그래프

| 관계 | X커지면 Y도 커지는가? | 산점도

| 구성 | 전체에서 각 부분 몇 %? | 파이차트

| 추세 | 시간에 따라 어떻게 변했나? | 꺾은선그래프

💡 파이차트는 범주가 5개 이하일 때만. 그 이상이면 막대그래프가 낫다.

## 2. matplotlib 기초

### 한글 폰트 설정 (항상 첫 번째 셀)

import matplotlib.pyplot as plt
import platform

if platform.system() == 'Windows':
plt.rc('font', family='Malgun Gothic')
elif platform.system() == 'Darwin':
plt.rc('font', family='AppleGothic')
else:
plt.rc('font', family='NanumGothic') # Ubuntu: sudo apt install fonts-nanum
plt.rc('axes', unicode_minus=False)

⚠️ 이 셀이 없으면 한글이 □□□□로 나옵니다. 항상 첫 번째 셀에서 실행!

### fig / ax 구조

# ✅ 객체형 (권장)
fig, ax = plt.subplots(figsize=(8, 5)) # fig=도화지, ax=그림 영역
ax.hist(data, bins=20)
ax.set_title('제목')
ax.set_xlabel('x축 레이블')
ax.set_ylabel('y축 레이블')
plt.tight_layout()
plt.show()

# PNG로 저장
plt.savefig('chart.png', dpi=150, bbox_inches='tight')

### 데이터 준비

import pandas as pd
TITANIC_URL = 'https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv'
titanic = pd.read_csv(TITANIC_URL)
titanic_clean = titanic.copy()
titanic_clean['Age'] = titanic_clean['Age'].fillna(titanic_clean['Age'].median())

### 히스토그램 — 분포

fig, ax = plt.subplots(figsize=(8, 5))
ax.hist(titanic_clean['Age'], bins=25, color='steelblue', edgecolor='white', alpha=0.8)
ax.set_xlabel('나이'); ax.set_ylabel('승객 수')
ax.set_title('타이타닉 승객 나이 분포')
plt.tight_layout(); plt.show()

💡 bins = 막대 수. 10 / 25 / 50으로 바꿔보며 차이를 확인해보세요.

### 막대그래프 — 비교

surv_class = titanic.groupby('Pclass')['Survived'].sum()

fig, ax = plt.subplots(figsize=(7, 5))
ax.bar(surv_class.index, surv_class.values,
color=['#2563eb','#ea580c','#16a34a'], edgecolor='white')
ax.set_title('등급별 생존자 수')
ax.set_xticks([1,2,3]); ax.set_xticklabels(['1등급','2등급','3등급'])
plt.tight_layout(); plt.show()

### 산점도 — 관계

colors = titanic_clean['Survived'].map({0: 'gray', 1: 'steelblue'})

fig, ax = plt.subplots(figsize=(8, 5))
ax.scatter(titanic_clean['Age'], titanic_clean['Fare'],
c=colors, alpha=0.4, s=30)
ax.set_xlabel('나이'); ax.set_ylabel('요금')
ax.set_title('나이 vs 요금 (색상=생존여부)')
plt.tight_layout(); plt.show()

### 박스플롯 — 분포 + 이상치

data_by_class = [titanic[titanic['Pclass']==c]['Fare'].dropna() for c in [1,2,3]]

fig, ax = plt.subplots(figsize=(7, 5))
ax.boxplot(data_by_class, tick_labels=['1등급','2등급','3등급'])
ax.set_ylabel('요금'); ax.set_title('등급별 요금 분포')
plt.tight_layout(); plt.show()

💡 박스 = 중간 50% (Q1~Q3). 수염 밖 점(●) = 이상치.

### 파이차트 — 구성

class_counts = titanic['Pclass'].value_counts().sort_index()

fig, ax = plt.subplots(figsize=(6, 6))
ax.pie(class_counts.values, labels=['1등급','2등급','3등급'],
autopct='%1.1f%%', startangle=90,
wedgeprops=dict(edgecolor='white'))
ax.set_title('객실 등급별 승객 비율')
plt.tight_layout(); plt.show()

## 3. plotly express 기초

import plotly.express as px

# 기본 패턴
fig = px.차트종류(df, x='컬럼', y='컬럼', title='제목', template='simple_white')
fig.show() # 노트북에서 출력
fig.write_html('파일명.html') # HTML로 저장

### IMDB 데이터 로드

imdb = pd.read_csv('01_sources/imdb_top_1000.csv')
# Released_Year에 'PG' 같은 비숫자 값이 있음 → 안전하게 변환
imdb['Released_Year'] = pd.to_numeric(imdb['Released_Year'], errors='coerce')

### px.histogram — marginal='box'

fig = px.histogram(
imdb, x='IMDB_Rating', nbins=20,
marginal='box', # 상단에 박스플롯 자동 추가
title='IMDB 평점 분포',
template='simple_white'
)
fig.show()

### px.scatter — hover_name

fig = px.scatter(
imdb, x='No_of_Votes', y='IMDB_Rating',
hover_name='Series_Title', # 마우스 올리면 영화 제목
hover_data=['Released_Year', 'Genre'],
title='투표 수 vs IMDB 평점',
template='simple_white', opacity=0.6
)
fig.show()
fig.write_html('imdb_scatter.html')

### px.line / px.bar — 서울 아파트

sa = pd.read_csv('01_sources/seoul_apartment.csv')

monthly = sa.groupby('계약년월')['거래금액(만원)'].mean().reset_index()
monthly.columns = ['계약년월', '평균거래금액']
monthly['계약년월'] = monthly['계약년월'].astype(str) # ← 필수!

fig = px.line(monthly, x='계약년월', y='평균거래금액',
title='서울 아파트 월별 평균 거래가격', template='simple_white')
fig.update_xaxes(tickangle=45, nticks=24)
fig.show()
fig.write_html('seoul_price.html')

⚠️ 계약년월이 int(200811)인 채로 쓰면 x축이 이상해집니다. .astype(str) 먼저!

## 4. 자기주도 미션

BASIC
타이타닉 matplotlib + IMDB plotly

# ── 타이타닉 matplotlib ─────────────────────────
# B1. 나이 히스토그램 (bins=25, 제목·축 레이블 포함)
# B2. 성별 생존자 수 막대그래프
# B3. 나이 vs 요금 산점도 (생존여부 색상 구분)
# B4. 등급별 요금 박스플롯
# B5. 탑승항(Embarked)별 승객 비율 파이차트
# → 각 차트 PNG로 저장

# ── IMDB plotly ──────────────────────────────────
# B6. IMDB_Rating 히스토그램 (marginal='box' 포함)
# B7. 투표 수 vs 평점 scatter (hover_name=영화 제목)
# B8. B7 차트를 HTML로 저장

APPLIED
서울 아파트 plotly 시계열

sa = pd.read_csv('01_sources/seoul_apartment.csv')

# A1. 월별 평균 거래가격 꺾은선그래프 (HTML 저장)
# A2. 월별 거래 건수 막대그래프 (HTML 저장)
# A3. 구별 평균 거래가격 수평 막대그래프
# 힌트: sa['구'] = sa['시군구'].str.split().str[1]

CHALLENGE
IMDB 장르 심화 분석

# Genre = 'Crime, Drama' 형태 → 쪼개서 분석
imdb_genre = imdb.copy()
imdb_genre['Genre'] = imdb_genre['Genre'].str.split(',')
imdb_genre = imdb_genre.explode('Genre')
imdb_genre['Genre'] = imdb_genre['Genre'].str.strip()

# C1. 장르별 평균 IMDB 평점 수평 막대 (10편 이상만)
# C2. 연도별 평균 평점 추이 scatter
# C3. Gross 전처리 후 흥행 vs 평점 scatter
# imdb['Gross_clean'] = imdb['Gross'].str.replace(',','', regex=False).astype(float)

## 막혔을 때 확인 순서

- 오류 메시지 마지막 줄 읽기 (핵심이 있음)

- df.columns, df.dtypes 확인

- 한글 폰트 설정 셀이 먼저 실행됐는지 확인

- plotly 차트가 안 보이면 → uv add nbformat 후 커널 재시작

- 러닝 서포터 → 강사에게 질문

## 제출

git add 260520_visualization.ipynb *.html *.png
git commit -m "feat: matplotlib·plotly 시각화 실습 완료"
git push

GitHub 저장소 URL → LMS 과제 칸에 입력

## 오늘 핵심 API

| | matplotlib | plotly express

| 히스토그램 | ax.hist(data, bins=n) | px.histogram(df, x='col', marginal='box')

| 막대 | ax.bar(x, y) | px.bar(df, x='col', y='col')

| 가로 막대 | ax.barh(y, x) | px.bar(..., orientation='h')

| 산점도 | ax.scatter(x, y, c=colors) | px.scatter(df, x=, y=, hover_name=)

| 박스플롯 | ax.boxplot(data) | px.box(df, y='col')

| 꺾은선 | — | px.line(df, x='col', y='col')

| 저장 | plt.savefig('file.png') | fig.write_html('file.html')

2026-05-20 · 내일(260521): Streamlit 입문 — 오늘 만든 plotly 차트를 st.plotly_chart(fig)로 웹 앱에 올린다.