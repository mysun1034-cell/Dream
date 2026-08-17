"""Generate Ch.01 Jupyter notebooks under ml/notebooks/ch01/."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "notebooks" / "ch01"

KERNEL = {
    "kernelspec": {
        "display_name": "Dream (.venv)",
        "language": "python",
        "name": "ml-dl-study",
    },
    "language_info": {
        "name": "python",
        "pygments_lexer": "ipython3",
        "version": "3.11.0",
    },
}


def nb(cells: list) -> dict:
    return {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": KERNEL,
        "cells": cells,
    }


def md(source: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source.splitlines(keepends=True),
    }


def code(source: str) -> dict:
    return {
        "cell_type": "code",
        "metadata": {},
        "source": source.splitlines(keepends=True),
        "outputs": [],
        "execution_count": None,
    }


FISH_DATA = """
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)


def make_fish_3d(n_per_class=25):
    domi = pd.DataFrame({
        "length": rng.normal(35, 3, n_per_class),
        "weight": rng.normal(700, 80, n_per_class),
        "fin": rng.normal(12, 1.5, n_per_class),
        "species": "domi",
    })
    bream = pd.DataFrame({
        "length": rng.normal(28, 2, n_per_class),
        "weight": rng.normal(180, 30, n_per_class),
        "fin": rng.normal(8, 1.2, n_per_class),
        "species": "bream",
    })
    return pd.concat([domi, bream], ignore_index=True)


def make_fish_4d(n_per_class=25):
    df = make_fish_3d(n_per_class)
    df["age"] = np.where(
        df["species"] == "domi",
        rng.normal(3, 1, len(df)),
        rng.normal(2, 0.8, len(df)),
    )
    return df


def make_fish_5d(n_per_class=25):
    df = make_fish_4d(n_per_class)
    df["brightness"] = np.where(
        df["species"] == "domi",
        rng.normal(0.7, 0.1, len(df)),
        rng.normal(0.4, 0.1, len(df)),
    )
    return df
"""


def notebook_01_01() -> dict:
    return nb([
        md(
            """# Ch.01-01 AI / ML / DL 개념 정리

> **교재:** 혼자 공부하는 머신러닝+딥러닝 · Ch.01-1  
> **노드:** #N01 · 코드 없음 — 관계만 잡기

---

## 1. 포함 관계

```
AI ⊃ ML ⊃ DL
```

| 개념 | 한 줄 정의 | 예시 |
|------|-----------|------|
| **AI** | 사람처럼 판단·추론·행동하는 시스템 | 규칙 기반 챗봇, 체스 AI, ChatGPT |
| **ML** | **데이터에서 패턴을 학습**하는 AI | k-NN, 결정 트리, 추천 |
| **DL** | **인공신경망을 깊게 쌓은** ML | CNN, Transformer(LLM) |

---

## 2. 헷갈림 방지 체크

- [ ] ChatGPT = AI이면서 ML이면서 DL(LLM) — **O**
- [ ] 모든 AI가 ML — **X** (if-else 규칙도 AI)
- [ ] 모든 ML이 DL — **X** (k-NN, 트리는 DL 아님)

---

## 3. 규칙 vs ML vs DL (도메인 연결)

| 방식 | EDENING 예 | 케어링크(ERP) 예 |
|------|-----------|-----------------|
| **규칙** | 정답 키, 채점 로직 | 결재 라우팅, 한도 검사 |
| **ML** | 오답 유형 분류 | 매출 예측, 이상 거래 탐지 |
| **DL/LLM** | 설명·피드백 **문구** (채점 X) | 매뉴얼 Q&A, 상품 설명 |

> EDENING 규칙: **채점·숙련도·복습일정에 LLM 사용 금지** — 서버가 단일 진실.

---

## 4. 나만의 한 문장 (작성란)

| 개념 | 내 말로 1문장 |
|------|--------------|
| AI | |
| ML | |
| DL | |

---

## 5. 확인 문제 (스스로 답하기)

1. DL ⊂ ML ⊂ AI 관계를 그림으로 그려보기.
2. 규칙 기반과 ML의 차이는?
3. LLM은 AI·ML·DL 중 어디에 해당?
4. ERP tabular 데이터 예측에 ML이 먼저인 이유는?
5. EDENING에서 채점에 LLM을 쓰면 안 되는 이유는?

---

## 6. 다음 절

→ **01-02** Jupyter 환경 점검  
→ **01-03** 첫 ML 코드 (k-NN · 도미 vs 빙어)
"""
        )
    ])


def notebook_01_02() -> dict:
    return nb([
        md(
            """# Ch.01-02 Jupyter 환경 점검

Colab/로컬 `.venv`에서 아래 셀을 **위에서 아래로** 실행해 환경을 확인합니다.

**커널:** Dream (.venv) · `ml-dl-study`
"""
        ),
        code(
            """import sys
import platform

print("Python:", sys.version.split()[0])
print("Platform:", platform.platform())
print("Executable:", sys.executable)
"""
        ),
        code(
            """import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import sklearn

print("numpy     ", np.__version__)
print("pandas    ", pd.__version__)
print("matplotlib", matplotlib.__version__)
print("sklearn   ", sklearn.__version__)
"""
        ),
        code(
            """# 간단한 scatter — matplotlib 정상 동작 확인
rng = np.random.default_rng(0)
x = rng.normal(0, 1, 50)
y = 2 * x + rng.normal(0, 0.5, 50)

fig, ax = plt.subplots(figsize=(5, 3.5))
ax.scatter(x, y, alpha=0.7, c="steelblue", edgecolors="white", linewidths=0.5)
ax.set_title("Environment OK — matplotlib scatter")
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
"""
        ),
        md(
            """## 통과 기준

- [ ] 모든 import 성공
- [ ] scatter plot 표시
- [ ] 커널 **Dream (.venv)** 선택됨

다음: **01-03_interactive_3d_features.ipynb**
"""
        ),
    ])


def notebook_01_03() -> dict:
    return nb([
        md(
            """# Ch.01-03 인터랙티브 3D feature + k-NN

**feature 3개:** 길이 · 무게 · 지느러미 길이  
**label:** 도미(domi) / 빙어(bream) — 색으로 표시

1. plotly **3D scatter** (드래그=회전)
2. **k-NN** — `NEW_FISH` 좌표를 바꿔 예측 + 이웃 k개 표시
3. **2D scatter** — feature 2개만 쓴 경우와 비교
"""
        ),
        code(FISH_DATA + "\ndf = make_fish_3d()\ndf.head()\n"),
        code(
            """import plotly.express as px

fig = px.scatter_3d(
    df,
    x="length",
    y="weight",
    z="fin",
    color="species",
    color_discrete_map={"domi": "orange", "bream": "steelblue"},
    title="3 features = 3D space (rotate with mouse)",
    labels={"length": "length (cm)", "weight": "weight (g)", "fin": "fin (cm)"},
    opacity=0.85,
)
fig.update_traces(marker=dict(size=5, line=dict(width=0.5, color="black")))
fig.show()
"""
        ),
        md(
            """## k-NN — NEW_FISH 좌표를 바꿔 보세요

아래 `NEW_FISH = [length, weight, fin]` 값을 수정한 뒤 셀을 다시 실행합니다.
"""
        ),
        code(
            """from sklearn.neighbors import KNeighborsClassifier
import plotly.graph_objects as go

NEW_FISH = [25, 150, 8.5]  # <-- 바꿔 보세요
K = 3

feature_cols = ["length", "weight", "fin"]
X = df[feature_cols].values
y = df["species"].values

model = KNeighborsClassifier(n_neighbors=K)
model.fit(X, y)
pred = model.predict([NEW_FISH])[0]
distances, indices = model.kneighbors([NEW_FISH])

print(f"NEW_FISH = {NEW_FISH}")
print(f"k-NN (k={K}) prediction: {pred}")
print("Neighbors:")
for rank, (idx, dist) in enumerate(zip(indices[0], distances[0]), 1):
    row = df.iloc[idx]
    print(f'  {rank}. {row["species"]:5s}  dist={dist:.2f}  {row[feature_cols].to_dict()}')

fig = go.Figure()
for species, color in [("domi", "orange"), ("bream", "steelblue")]:
    sub = df[df["species"] == species]
    fig.add_trace(
        go.Scatter3d(
            x=sub["length"],
            y=sub["weight"],
            z=sub["fin"],
            mode="markers",
            name=species,
            marker=dict(size=5, color=color, opacity=0.75, line=dict(width=0.5, color="black")),
        )
    )

neighbor_df = df.iloc[indices[0]]
fig.add_trace(
    go.Scatter3d(
        x=neighbor_df["length"],
        y=neighbor_df["weight"],
        z=neighbor_df["fin"],
        mode="markers",
        name=f"k={K} neighbors",
        marker=dict(size=9, color="lime", symbol="diamond", line=dict(width=1.5, color="black")),
    )
)
fig.add_trace(
    go.Scatter3d(
        x=[NEW_FISH[0]],
        y=[NEW_FISH[1]],
        z=[NEW_FISH[2]],
        mode="markers+text",
        name=f"NEW_FISH -> {pred}",
        text=["NEW"],
        textposition="top center",
        marker=dict(size=12, color="red", symbol="x", line=dict(width=2, color="darkred")),
    )
)
fig.update_layout(
    title=f"3D k-NN: NEW_FISH predicted as {pred}",
    scene=dict(
        xaxis_title="length (cm)",
        yaxis_title="weight (g)",
        zaxis_title="fin (cm)",
    ),
    margin=dict(l=0, r=0, b=0, t=40),
)
fig.show()
"""
        ),
        md(
            """## 2D vs 3D — 같은 데이터, feature 2개만 그린 경우

k-NN **계산**은 3차원 거리를 쓰지만, 사람은 2D scatter로 자주 그립니다.
"""
        ),
        code(
            """import plotly.express as px

fig2d = px.scatter(
    df,
    x="length",
    y="weight",
    color="species",
    color_discrete_map={"domi": "orange", "bream": "steelblue"},
    title="2 features only (length, weight) — 3rd feature fin is hidden",
    labels={"length": "length (cm)", "weight": "weight (g)"},
)
fig2d.add_scatter(
    x=[NEW_FISH[0]],
    y=[NEW_FISH[1]],
    mode="markers+text",
    name="NEW_FISH (2D projection)",
    text=["NEW"],
    textposition="top center",
    marker=dict(size=14, color="red", symbol="x"),
)
fig2d.show()
"""
        ),
    ])


def notebook_01_04() -> dict:
    return nb([
        md(
            """# Ch.01-04 인터랙티브 4D · 5D feature

| 차원 | 시각화 | k-NN |
|------|--------|------|
| **4D** | scatter_matrix + 6 panel pair plot | 4 feature 거리 |
| **5D** | parallel coordinates | 5 feature 거리 |

> 4D·5D **공간**을 한 장에 그릴 수는 없지만, **거리 계산**은 동일합니다.
"""
        ),
        code(FISH_DATA + "\ndf4 = make_fish_4d()\ndf5 = make_fish_5d()\ndf4.head()\n"),
        md("## §1 scatter_matrix (4D)\n"),
        code(
            """import plotly.express as px

fig_matrix = px.scatter_matrix(
    df4,
    dimensions=["length", "weight", "fin", "age"],
    color="species",
    color_discrete_map={"domi": "orange", "bream": "steelblue"},
    title="4D: scatter_matrix (pair-wise 2D slices)",
    opacity=0.8,
)
fig_matrix.update_traces(diagonal_visible=False, showupperhalf=False, marker=dict(size=4))
fig_matrix.update_layout(height=700)
fig_matrix.show()
"""
        ),
        md("## §2 6 panel 4D pair plot\n"),
        code(
            """from itertools import combinations

import plotly.graph_objects as go
from plotly.subplots import make_subplots

names = ["length", "weight", "fin", "age"]
pairs = list(combinations(range(4), 2))
fig = make_subplots(
    rows=2,
    cols=3,
    subplot_titles=[f"{names[i]} vs {names[j]}" for i, j in pairs],
)

for ax_idx, (i, j) in enumerate(pairs, start=1):
    row = (ax_idx - 1) // 3 + 1
    col = (ax_idx - 1) % 3 + 1
    for species, color in [("domi", "orange"), ("bream", "steelblue")]:
        sub = df4[df4["species"] == species]
        fig.add_trace(
            go.Scatter(
                x=sub[names[i]],
                y=sub[names[j]],
                mode="markers",
                name=species,
                marker=dict(size=6, color=color, opacity=0.75, line=dict(width=0.3, color="black")),
                showlegend=(ax_idx == 1),
            ),
            row=row,
            col=col,
        )

fig.update_layout(title="4 features: 6 pair-wise 2D slices", height=550)
fig.show()
"""
        ),
        md("## §3 parallel coordinates (5D)\n"),
        code(
            """import plotly.express as px

fig_par = px.parallel_coordinates(
    df5,
    dimensions=["length", "weight", "fin", "age", "brightness"],
    color=df5["species"].map({"domi": 0, "bream": 1}),
    color_continuous_scale=[[0, "orange"], [1, "steelblue"]],
    labels={"color": "species code"},
    title="5 features: parallel coordinates (each line = one fish)",
)
fig_par.update_layout(height=450)
fig_par.show()
"""
        ),
        md(
            """## §4 k-NN in 4D and 5D

`NEW_FISH_*` 좌표를 바꿔 예측을 확인합니다.
"""
        ),
        code(
            """from sklearn.neighbors import KNeighborsClassifier

NEW_FISH_4D = [25, 150, 8.5, 2.5]
NEW_FISH_5D = [25, 150, 8.5, 2.5, 0.45]
K = 3

for name, cols, new_point in [
    ("4D", ["length", "weight", "fin", "age"], NEW_FISH_4D),
    ("5D", ["length", "weight", "fin", "age", "brightness"], NEW_FISH_5D),
]:
    X = df5[cols].values
    y = df5["species"].values
    model = KNeighborsClassifier(n_neighbors=K)
    model.fit(X, y)
    pred = model.predict([new_point])[0]
    dists, idxs = model.kneighbors([new_point])
    print(f"=== {name} k-NN (k={K}) ===")
    print(f"NEW_FISH = {new_point} -> {pred}")
    for rank, (idx, dist) in enumerate(zip(idxs[0], dists[0]), 1):
        row = df5.iloc[idx]
        print(f'  {rank}. {row["species"]:5s} dist={dist:.3f}')
    print()
"""
        ),
    ])


def notebook_01_05() -> dict:
    return nb([
        md(
            """# Ch.01-05 3D에 4D·5D를 "입히기"

| 차원 | 방법 |
|------|------|
| **4D** | 3D (x,y,z) + **색** = 4번째 feature |
| **5D** | 3D + **색**(f4) + **점 크기**(f5) |
| **4D (다른법)** | 3D + **슬라이더/애니메이션** = 4번째 구간별 탐색 |

> 번역이지 4D **공간 체험**은 아닙니다. k-NN 거리는 그림과 무관하게 N차원으로 계산됩니다.
"""
        ),
        code(FISH_DATA + "\ndf4 = make_fish_4d()\ndf5 = make_fish_5d()\ndf4.head()\n"),
        md("## §1 4D — 3D + color (age)\n"),
        code(
            """import plotly.express as px

fig4 = px.scatter_3d(
    df4,
    x="length",
    y="weight",
    z="fin",
    color="age",
    symbol="species",
    color_continuous_scale="Viridis",
    title="4D embedded in 3D: position=f1~f3, color=age (f4)",
    labels={
        "length": "length (cm)",
        "weight": "weight (g)",
        "fin": "fin (cm)",
        "age": "age (yr)",
    },
    opacity=0.9,
)
fig4.update_traces(marker=dict(size=5, line=dict(width=0.4, color="black")))
fig4.show()
"""
        ),
        md("## §2 5D — 3D + color + size (brightness)\n"),
        code(
            """import plotly.express as px

fig5 = px.scatter_3d(
    df5,
    x="length",
    y="weight",
    z="fin",
    color="age",
    size="brightness",
    symbol="species",
    color_continuous_scale="Plasma",
    title="5D embedded in 3D: color=age, size=brightness",
    labels={
        "length": "length (cm)",
        "weight": "weight (g)",
        "fin": "fin (cm)",
        "age": "age (yr)",
        "brightness": "brightness",
    },
    size_max=18,
    opacity=0.9,
)
fig5.update_traces(marker=dict(line=dict(width=0.4, color="black")))
fig5.show()
"""
        ),
        md("## §3 4D — animation slider (age 구간별 slice)\n"),
        code(
            """import plotly.express as px

df_anim = df4.copy()
df_anim["age_bin"] = pd.cut(df_anim["age"], bins=5).astype(str)

fig_anim = px.scatter_3d(
    df_anim,
    x="length",
    y="weight",
    z="fin",
    animation_frame="age_bin",
    color="species",
    color_discrete_map={"domi": "orange", "bream": "steelblue"},
    title="4D via slider: 3D slices by age_bin (4th feature)",
    labels={"length": "length (cm)", "weight": "weight (g)", "fin": "fin (cm)"},
    opacity=0.85,
)
fig_anim.update_traces(marker=dict(size=6, line=dict(width=0.4, color="black")))
fig_anim.show()
"""
        ),
    ])


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    notebooks = {
        "01-01_ai_ml_dl.ipynb": notebook_01_01(),
        "01-02_jupyter_setup.ipynb": notebook_01_02(),
        "01-03_interactive_3d_features.ipynb": notebook_01_03(),
        "01-04_interactive_4d_5d_features.ipynb": notebook_01_04(),
        "01-05_embed_4d_5d_in_3d.ipynb": notebook_01_05(),
    }
    for name, notebook in notebooks.items():
        path = OUT / name
        path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1), encoding="utf-8")
        print(path)


if __name__ == "__main__":
    main()
