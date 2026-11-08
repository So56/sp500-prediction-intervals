import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

from settings import ALPHA, GROUPS, METHODS, MODELS, project_dir


evaluation_dir = project_dir / "outputs" / "evaluation"
figure_dir = project_dir / "outputs" / "figures"
figure_dir.mkdir(parents=True, exist_ok=True)
point_summary = pd.read_csv(evaluation_dir / "point_summary.csv")
summary = pd.read_csv(evaluation_dir / "interval_summary.csv")
daily = pd.read_csv(evaluation_dir / "daily_evaluation.csv", parse_dates=["date"])
model_labels = ["Random Walk", "Historical Mean", "AR(1)", "Multiple regression"]
method_labels = ["Fixed CP", "Rolling CP", "Fixed Normal", "Rolling Normal"]
group_labels = ["All Test", "High VIX", "Non-high VIX"]
colors = ["#377eb8", "#e69f00", "#009e73", "#cc79a7"]
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})


def save_figure(fig, name):
    fig.tight_layout()
    fig.savefig(figure_dir / f"{name}.png", dpi=180)
    fig.savefig(figure_dir / f"{name}.pdf")
    plt.close(fig)


# 点予測の精度
fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
positions = np.arange(len(MODELS))
for ax, metric in zip(axes, ["mae", "rmse"]):
    for g, (group, label) in enumerate(zip(GROUPS, group_labels)):
        values = point_summary.loc[point_summary["group"] == group].set_index("model")
        ax.bar(positions + (g - 1) * 0.24, values.reindex(MODELS)[metric],
               width=0.24, label=label, color=colors[g])
    ax.set_xticks(positions, model_labels, rotation=12)
    ax.set_ylabel(f"{metric.upper()} (return pp)")
axes[0].legend()
save_figure(fig, "point_accuracy")

# 16通りの結果。Coverageの色は90%からのずれを表す。
fig, axes = plt.subplots(3, 3, figsize=(14, 12))
for g, (group, group_label) in enumerate(zip(GROUPS, group_labels)):
    part = summary.loc[summary["group"] == group]
    for j, metric in enumerate(["coverage", "width", "interval_score"]):
        ax = axes[g, j]
        values = part.pivot(index="model", columns="method", values=metric)
        values = values.reindex(index=MODELS, columns=METHODS).to_numpy()
        if metric == "coverage":
            display = values * 100
            ax.imshow((values - (1 - ALPHA)) * 100, cmap="RdBu", vmin=-35, vmax=35)
            title = "Coverage (%) | target 90"
        else:
            display = values
            ax.imshow(values, cmap="Blues", vmin=0)
            title = "Width (return pp)" if metric == "width" else "Interval score (lower is better)"
        for i in range(len(MODELS)):
            for k in range(len(METHODS)):
                ax.text(k, i, f"{display[i, k]:.2f}", ha="center", va="center",
                        bbox={"facecolor": "white", "alpha": 0.85, "edgecolor": "none"})
        ax.set_xticks(range(len(METHODS)), method_labels, rotation=25, ha="right", fontsize=8)
        ax.set_yticks(range(len(MODELS)), model_labels, fontsize=8)
        ax.set_title(f"{group_label}: {title}", fontsize=10)
save_figure(fig, "sixteen_combinations")

# AR(1)の幅と直近126営業日のCoverage
fig, axes = plt.subplots(2, 1, figsize=(11, 6), sharex=True)
for method, label, color in zip(METHODS, method_labels, colors):
    part = daily.loc[(daily["model"] == "ar1") & (daily["method"] == method)].sort_values("date")
    axes[0].plot(part["date"], part["width"], label=label, color=color, linewidth=1)
    axes[1].plot(part["date"], part["covered"].rolling(126).mean() * 100,
                 color=color, linewidth=1)
axes[0].set_ylabel("Width (return pp)")
axes[0].legend()
axes[0].set_title("AR(1): interval width and recent coverage")
axes[1].axhline((1 - ALPHA) * 100, color="gray", linestyle="--")
axes[1].set_ylabel("126-session coverage (%)")
save_figure(fig, "ar1_width_and_coverage")

# 幅とCoverageの関係。モデルを形、区間法を色で区別する。
markers = ["o", "^", "s", "D"]
fig, axes = plt.subplots(1, 3, figsize=(13, 5))
for ax, group, label in zip(axes, GROUPS, group_labels):
    part = summary.loc[summary["group"] == group].set_index(["model", "method"])
    for model, marker in zip(MODELS, markers):
        for method, color in zip(METHODS, colors):
            row = part.loc[(model, method)]
            ax.scatter(row["width"], row["coverage"] * 100, marker=marker,
                       color=color, s=60, alpha=0.75)
    ax.axhline(90, color="gray", linestyle="--", linewidth=1)
    ax.set_title(label)
    ax.set_xlabel("Average width (return pp)")
axes[0].set_ylabel("Empirical coverage (%)")
handles = [Line2D([], [], marker=marker, color="gray", linestyle="none", label=label)
           for marker, label in zip(markers, model_labels)]
handles += [Line2D([], [], color=color, label=label) for color, label in zip(colors, method_labels)]
fig.legend(handles=handles, loc="lower center", ncol=4, fontsize=9)
fig.tight_layout(rect=(0, 0.16, 1, 1))
fig.savefig(figure_dir / "coverage_width.png", dpi=180)
fig.savefig(figure_dir / "coverage_width.pdf")
plt.close(fig)

# 事前に決めた20比較のIS差と、主Block長10の近似95%信頼区間
differences = pd.read_csv(evaluation_dir / "bootstrap" / "paired_differences.csv")
differences = differences.loc[(differences["block_length"] == 10)
                              & (differences["metric"] == "interval_score")]
short_models = dict(zip(MODELS, ["RW", "Mean", "AR1", "MR"]))
short_methods = dict(zip(METHODS, ["F-CP", "R-CP", "F-N", "R-N"]))
fig, axes = plt.subplots(1, 3, figsize=(14, 10), sharey=True)
labels = []
for ax, group, title in zip(axes, GROUPS, group_labels):
    part = differences.loc[differences["group"] == group].reset_index(drop=True)
    positions = np.arange(len(part))
    if not labels:
        for row in part.itertuples():
            a = short_models[row.model_a] + "/" + short_methods[row.method_a]
            b = short_models[row.model_b] + "/" + short_methods[row.method_b]
            labels.append(a + " - " + b)
    ax.hlines(positions, part["ci_lower"], part["ci_upper"], color=colors[0])
    ax.scatter(part["difference_a_minus_b"], positions, color=colors[0], s=20)
    ax.axvline(0, color="gray", linestyle="--")
    ax.set_title(title)
    ax.set_xlabel("IS difference A - B (return pp)")
    ax.grid(axis="y", alpha=0.15)
axes[0].set_yticks(np.arange(len(labels)), labels, fontsize=8)
axes[0].invert_yaxis()
fig.suptitle("Pre-specified comparisons: paired block bootstrap 95% intervals\n"
             "Block length 10; negative difference favors A; intervals are pointwise", fontsize=11)
fig.tight_layout(rect=(0, 0, 1, 0.94))
fig.savefig(figure_dir / "paired_is_differences.png", dpi=180)
fig.savefig(figure_dir / "paired_is_differences.pdf")
plt.close(fig)
print("図を保存しました。")
