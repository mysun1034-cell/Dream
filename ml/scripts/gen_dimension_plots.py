"""Generate 2D–5D feature space visualization images for study notes."""
from __future__ import annotations

from itertools import combinations

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

OUT = "ml/images"


def main() -> None:
    rng = np.random.default_rng(42)

    # 2 features = 2D plane
    fig, ax = plt.subplots(figsize=(5, 4))
    for label, color, name in [(0, "tab:orange", "domi"), (1, "tab:blue", "bream")]:
        n = 25
        if label == 0:
            x = rng.normal(35, 3, n)
            y = rng.normal(700, 80, n)
        else:
            x = rng.normal(28, 2, n)
            y = rng.normal(180, 30, n)
        ax.scatter(x, y, c=color, label=name, alpha=0.8, edgecolors="k", linewidths=0.3)
    ax.set_xlabel("feature 1: length (cm)")
    ax.set_ylabel("feature 2: weight (g)")
    ax.set_title("2 features = 2D plane (x, y axes)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(f"{OUT}/dim2_features.png", dpi=150)
    plt.close(fig)

    # 3 features = 3D space
    fig = plt.figure(figsize=(6, 5))
    ax = fig.add_subplot(111, projection="3d")
    for label, color, name in [(0, "tab:orange", "domi"), (1, "tab:blue", "bream")]:
        n = 20
        if label == 0:
            x = rng.normal(35, 3, n)
            y = rng.normal(700, 80, n)
            z = rng.normal(12, 1.5, n)
        else:
            x = rng.normal(28, 2, n)
            y = rng.normal(180, 30, n)
            z = rng.normal(8, 1.2, n)
        ax.scatter(x, y, z, c=color, label=name, alpha=0.85, edgecolors="k", linewidths=0.2)
    ax.set_xlabel("f1: length")
    ax.set_ylabel("f2: weight")
    ax.set_zlabel("f3: fin length")
    ax.set_title("3 features = 3D space (x, y, z axes)")
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(f"{OUT}/dim3_features.png", dpi=150)
    plt.close(fig)

    # 4 features = pair plot (2D slices)
    names = ["length", "weight", "fin", "age"]
    n = 40
    x0 = np.column_stack([
        rng.normal(35, 3, n),
        rng.normal(700, 80, n),
        rng.normal(12, 1.5, n),
        rng.normal(3, 1, n),
    ])
    x1 = np.column_stack([
        rng.normal(28, 2, n),
        rng.normal(180, 30, n),
        rng.normal(8, 1.2, n),
        rng.normal(2, 0.8, n),
    ])
    x = np.vstack([x0, x1])
    y = np.array([0] * n + [1] * n)
    colors = np.where(y == 0, "tab:orange", "tab:blue")

    fig, axes = plt.subplots(2, 3, figsize=(9, 6))
    for ax, (i, j) in zip(axes.ravel(), combinations(range(4), 2)):
        ax.scatter(x[:, i], x[:, j], c=colors, alpha=0.7, edgecolors="k", linewidths=0.2)
        ax.set_xlabel(names[i])
        ax.set_ylabel(names[j])
    fig.suptitle("4 features: 6 pair-wise 2D slices (no single 4D picture)", y=1.02)
    fig.tight_layout()
    fig.savefig(f"{OUT}/dim4_pairplot.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    # 5 features = parallel coordinates
    n = 30
    x0 = rng.normal(0, 1, (n, 5)) + np.array([2, 2, 2, 1, 1])
    x1 = rng.normal(0, 1, (n, 5)) + np.array([-2, -1, -1, -2, -2])
    x = np.vstack([x0, x1])
    y = np.array([0] * n + [1] * n)
    cols = ["f1", "f2", "f3", "f4", "f5"]

    fig, ax = plt.subplots(figsize=(8, 4))
    x_pos = np.arange(5)
    for row, label in zip(x, y):
        color = "tab:orange" if label == 0 else "tab:blue"
        ax.plot(x_pos, row, c=color, alpha=0.35, linewidth=1)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(cols)
    ax.set_ylabel("scaled value")
    ax.set_title("5 features: parallel coordinates (each line = one sample)")
    ax.legend(
        handles=[
            Line2D([0], [0], color="tab:orange", label="class A"),
            Line2D([0], [0], color="tab:blue", label="class B"),
        ],
        loc="upper right",
    )
    fig.tight_layout()
    fig.savefig(f"{OUT}/dim5_parallel.png", dpi=150)
    plt.close(fig)

    print(f"saved 4 images to {OUT}/")


if __name__ == "__main__":
    main()
