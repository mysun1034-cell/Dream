"""One-off render for 02-01 NumPy table viz PNGs."""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

X = np.array([[25, 150], [28, 200], [30, 180]])
labels = ["빙어", "도미", "도미"]
feature_names = ["길이 (cm)", "무게 (g)"]

fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
ax0 = axes[0]
ax0.axis("off")
ax0.set_title("NumPy 표 X  —  shape (3, 2)", fontsize=13, fontweight="bold", pad=12)
cell_text = [[str(v) for v in row] for row in X]
row_labels = [f"생선 {i} ({labels[i]})" for i in range(3)]
table = ax0.table(
    cellText=cell_text,
    colLabels=feature_names,
    rowLabels=row_labels,
    loc="center",
    cellLoc="center",
)
table.auto_set_font_size(False)
table.set_fontsize(11)
table.scale(1.2, 1.8)
for (r, c), cell in table.get_celld().items():
    if r == 0:
        cell.set_facecolor("#4472C4")
        cell.set_text_props(color="white", fontweight="bold")
    elif c == -1:
        cell.set_facecolor("#D9E2F3")
        cell.set_text_props(fontweight="bold")
    else:
        cell.set_facecolor("#FFF2CC" if r % 2 else "#FFE699")

ax1 = axes[1]
im = ax1.imshow(X, cmap="YlOrRd", aspect="auto")
ax1.set_xticks([0, 1])
ax1.set_xticklabels(feature_names)
ax1.set_yticks([0, 1, 2])
ax1.set_yticklabels(row_labels)
ax1.set_title("같은 데이터 — 색 = 숫자 크기", fontsize=13, fontweight="bold")
for i in range(3):
    for j in range(2):
        ax1.text(j, i, str(X[i, j]), ha="center", va="center", fontsize=14, fontweight="bold")
plt.colorbar(im, ax=ax1, fraction=0.046, pad=0.04)
plt.tight_layout()
out1 = "ml/images/numpy_table_01.png"
plt.savefig(out1, dpi=150, bbox_inches="tight")
plt.close()

fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))


def draw_grid(ax, title, highlight_cells, subtitle):
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.set_xticks([0, 1])
    ax.set_xticklabels(feature_names)
    ax.set_yticks([0, 1, 2])
    ax.set_yticklabels([f"행{i}" for i in range(3)])
    for i in range(3):
        for j in range(2):
            face = "#FF6B6B" if (i, j) in highlight_cells else "#E8E8E8"
            ax.add_patch(
                mpatches.Rectangle(
                    (j - 0.45, 2.45 - i),
                    0.9,
                    0.9,
                    facecolor=face,
                    edgecolor="#333",
                    lw=2,
                )
            )
            ax.text(j, 2 - i, str(X[i, j]), ha="center", va="center", fontsize=16, fontweight="bold")
    ax.set_xlim(-0.7, 1.7)
    ax.set_ylim(-0.3, 3.2)
    ax.text(0.5, -0.15, subtitle, transform=ax.transAxes, ha="center", fontsize=10, color="#555")


draw_grid(axes[0], "X[0]  — 첫 번째 생선 (한 행)", {(0, 0), (0, 1)}, f"= {list(X[0])}")
draw_grid(axes[1], "X[:, 0]  — 모든 생선의 '길이'만", {(0, 0), (1, 0), (2, 0)}, f"= {list(X[:, 0])}")
plt.tight_layout()
out2 = "ml/images/numpy_table_02_index.png"
plt.savefig(out2, dpi=150, bbox_inches="tight")
plt.close()

fig, ax = plt.subplots(figsize=(6, 5))
colors = ["#5B9BD5" if lb == "빙어" else "#ED7D31" for lb in labels]
ax.scatter(X[:, 0], X[:, 1], s=200, c=colors, edgecolors="white", linewidths=2)
for i in range(3):
    ax.annotate(
        f"생선{i}\n{labels[i]}",
        (X[i, 0], X[i, 1]),
        textcoords="offset points",
        xytext=(8, 8),
        fontsize=10,
    )
ax.set_xlabel(feature_names[0])
ax.set_ylabel(feature_names[1])
ax.set_title("표의 두 열 = scatter (Ch.1)")
ax.grid(True, alpha=0.3)
out3 = "ml/images/numpy_table_03_scatter.png"
plt.savefig(out3, dpi=150, bbox_inches="tight")
plt.close()
print("saved", out1, out2, out3)
