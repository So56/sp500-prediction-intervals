import hashlib
import json

import numpy as np
import pandas as pd

from bootstrap import draw_block_indices, sample_statistics
from settings import (
    BLOCK_LENGTHS, BOOTSTRAP_REPS, BOOTSTRAP_SEED,
    GROUPS, METHODS, MODELS, project_dir,
)


evaluation_dir = project_dir / "outputs" / "evaluation"
output_dir = evaluation_dir / "bootstrap"
output_dir.mkdir(parents=True, exist_ok=True)
daily = pd.read_csv(evaluation_dir / "daily_evaluation.csv", parse_dates=["date"])
points = pd.read_csv(project_dir / "outputs" / "modeling" / "point_predictions.csv")
points = points.loc[points["split"] == "test"]

# 日付を行、モデル・区間法を列にして、抽出する行を共有する
dates = pd.DatetimeIndex(sorted(daily["date"].unique()))
combinations = pd.MultiIndex.from_product([MODELS, METHODS], names=["model", "method"])
errors = points.pivot(index="date", columns="model", values="error_pct").reindex(columns=MODELS)
errors.index = pd.to_datetime(errors.index)
errors = errors.reindex(dates).to_numpy()
arrays = [np.abs(errors), errors ** 2]
columns = []
for metric in ["mae", "rmse"]:
    columns.extend({"kind": "point", "metric": metric, "model": model, "method": "none"}
                   for model in MODELS)
for metric in ["coverage", "width", "interval_score"]:
    source = "covered" if metric == "coverage" else metric
    table = daily.pivot(index="date", columns=["model", "method"], values=source)
    arrays.append(table.reindex(index=dates, columns=combinations).to_numpy())
    columns.extend({"kind": "interval", "metric": metric, "model": model, "method": method}
                   for model, method in combinations)
values = np.column_stack(arrays)
if not np.isfinite(values).all():
    raise ValueError("日付の対応と、評価指標の欠損を確認してください。")

high = daily.drop_duplicates("date").set_index("date")["high_vix_30"].reindex(dates).to_numpy()
group_masks = np.column_stack([np.ones(len(dates), dtype=bool), high, ~high])
rmse_columns = slice(len(MODELS), 2 * len(MODELS))
observed, observed_n = sample_statistics(values, group_masks, np.arange(len(dates)), rmse_columns)
lookup = {(c["metric"], c["model"], c["method"]): i for i, c in enumerate(columns)}

# 比較する組を先に決める。差はすべてA−Bで記録する。
contrasts = []
for other in ["ar1", "random_walk", "historical_mean"]:
    for metric in ["mae", "rmse"]:
        contrasts.append(("point", "multiple_vs_" + other, metric,
                          "multiple_regression", "none", other, "none"))
interval_pairs = []
for method in METHODS:
    interval_pairs.append(("added_features", "multiple_regression", method, "ar1", method))
for model in MODELS:
    for label, a, b in [
        ("fixed_cp_vs_normal", "fixed_cp", "fixed_normal"),
        ("rolling_cp_vs_normal", "rolling_cp", "rolling_normal"),
        ("cp_update", "rolling_cp", "fixed_cp"),
        ("normal_update", "rolling_normal", "fixed_normal"),
    ]:
        interval_pairs.append((label, model, a, model, b))
for label, model_a, method_a, model_b, method_b in interval_pairs:
    for metric in ["coverage", "width", "interval_score"]:
        contrasts.append(("interval", label, metric, model_a, method_a, model_b, method_b))

metric_records = []
difference_records = []
runs = []
for block_length in BLOCK_LENGTHS:
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    samples = np.empty((BOOTSTRAP_REPS, len(GROUPS), len(columns)))
    sampled_n = np.empty((BOOTSTRAP_REPS, len(GROUPS)), dtype=int)
    index_hash = hashlib.sha256()
    first_indices = []
    for b in range(BOOTSTRAP_REPS):
        indices = draw_block_indices(len(dates), block_length, rng)
        samples[b], sampled_n[b] = sample_statistics(values, group_masks, indices, rmse_columns)
        index_hash.update(indices.astype("<i8").tobytes())
        if b < 3:
            first_indices.append(indices[:30].tolist())
    limits = np.nanquantile(samples, [0.025, 0.975], axis=0)

    for g, group in enumerate(GROUPS):
        for k, column in enumerate(columns):
            metric_records.append({
                "block_length": block_length, "group": group, **column,
                "n": int(observed_n[g]), "estimate": observed[g, k],
                "ci_lower": limits[0, g, k], "ci_upper": limits[1, g, k],
                "valid_reps": int(np.isfinite(samples[:, g, k]).sum()),
            })
        for kind, label, metric, model_a, method_a, model_b, method_b in contrasts:
            a = lookup[(metric, model_a, method_a)]
            other = lookup[(metric, model_b, method_b)]
            differences = samples[:, g, a] - samples[:, g, other]
            lower, upper = np.nanquantile(differences, [0.025, 0.975])
            difference_records.append({
                "block_length": block_length, "group": group, "kind": kind,
                "comparison": label, "metric": metric,
                "model_a": model_a, "method_a": method_a,
                "model_b": model_b, "method_b": method_b,
                "difference_a_minus_b": observed[g, a] - observed[g, other],
                "ci_lower": lower, "ci_upper": upper,
                "zero_excluded": bool(lower > 0 or upper < 0),
                "valid_reps": int(np.isfinite(differences).sum()),
            })
    runs.append({
        "block_length": block_length, "seed": BOOTSTRAP_SEED,
        "bit_generator": "PCG64", "reps": BOOTSTRAP_REPS,
        "first_three_index_prefixes": first_indices,
        "all_indices_sha256_little_endian_int64": index_hash.hexdigest(),
        "zero_group_reps": dict(zip(GROUPS, (sampled_n == 0).sum(axis=0).tolist())),
        "sampled_group_n_min": sampled_n.min(axis=0).tolist(),
        "sampled_group_n_max": sampled_n.max(axis=0).tolist(),
    })
    print(f"Block長{block_length}: {BOOTSTRAP_REPS}回完了", flush=True)

pd.DataFrame(metric_records).to_csv(output_dir / "metric_intervals.csv", index=False)
pd.DataFrame(difference_records).to_csv(output_dir / "paired_differences.csv", index=False)
settings = {
    "method": "paired non-circular moving block bootstrap",
    "ci_method": "percentile", "ci_level": 0.95, "main_block_length": 10,
    "test_start": str(dates.min().date()), "test_end": str(dates.max().date()),
    "n": len(dates), "observed_group_n": dict(zip(GROUPS, observed_n.astype(int).tolist())),
    "resample_scope": "saved test predictions and intervals; models are not refitted",
    "input_daily_sha256": hashlib.sha256((evaluation_dir / "daily_evaluation.csv").read_bytes()).hexdigest(),
    "runs": runs,
}
(output_dir / "settings.json").write_text(json.dumps(settings, ensure_ascii=False, indent=2), encoding="utf-8")
