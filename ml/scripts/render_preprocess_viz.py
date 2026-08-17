"""Render Ch.02-02 preprocessing viz PNGs."""
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

X = np.array([
    [25, 150], [26, 145], [24, 155], [27, 148],
    [28, 200], [30, 180], [29, 210], [31, 195],
    [25, 152], [26, 140], [28, 205], [30, 190],
])
y = np.array([0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1])
feature_names = ["길이 (cm)", "무게 (g)"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

# --- split viz ---
fig, ax = plt.subplots(figsize=(7, 5))
ax.scatter(
    X_train[:, 0], X_train[:, 1],
    c=["#5B9BD5" if v == 0 else "#ED7D31" for v in y_train],
    s=120, marker="o", edgecolors="white", linewidths=2, label="train",
)
ax.scatter(
    X_test[:, 0], X_test[:, 1],
    c=["#5B9BD5" if v == 0 else "#ED7D31" for v in y_test],
    s=180, marker="s", edgecolors="black", linewidths=2, label="test",
)
ax.set_xlabel(feature_names[0])
ax.set_ylabel(feature_names[1])
ax.set_title("train_test_split")
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("ml/images/preprocess_01_split.png", dpi=150, bbox_inches="tight")
plt.close()

# --- scale before/after ---
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
for ax, data, title, xl, yl in [
    (axes[0], X_train, "전처리 전", feature_names[0], feature_names[1]),
    (axes[1], X_train_scaled, "StandardScaler 후", "길이 (scaled)", "무게 (scaled)"),
]:
    ax.scatter(
        data[:, 0], data[:, 1],
        c=["#5B9BD5" if v == 0 else "#ED7D31" for v in y_train],
        s=100, edgecolors="white",
    )
    ax.set_xlabel(xl)
    ax.set_ylabel(yl)
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.set_aspect("equal", adjustable="box")
plt.suptitle("스케일링 후 두 축 범위가 비슷해짐", fontsize=12, y=1.02)
plt.tight_layout()
plt.savefig("ml/images/preprocess_02_scale.png", dpi=150, bbox_inches="tight")
plt.close()

# --- distance bar ---
a = np.array([25, 150])
b = np.array([28, 150])
c = np.array([25, 200])


def dist(p, q):
    return np.sqrt(((p - q) ** 2).sum())


fig, ax = plt.subplots(figsize=(5, 4))
bars = ax.bar(
    ["길이 3cm\n차이", "무게 50g\n차이"],
    [dist(a, b), dist(a, c)],
    color=["#4472C4", "#C00000"],
)
ax.set_ylabel("유클리드 거리")
ax.set_title("스케일 안 맞으면 무게가 거리 지배")
for bar, val in zip(bars, [dist(a, b), dist(a, c)]):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1, f"{val:.0f}", ha="center")
plt.tight_layout()
plt.savefig("ml/images/preprocess_03_distance.png", dpi=150, bbox_inches="tight")
plt.close()
print("saved preprocess_01~03.png")
