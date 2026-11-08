from io import BytesIO
from pathlib import Path
from statistics import NormalDist
from zipfile import ZipFile
import hashlib
import json
import math
import platform
import sys

import matplotlib
import numpy as np
import pandas as pd


project = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project / "Scripts"))
from bootstrap import draw_block_indices, sample_statistics
from intervals import conformal_halfwidth, interval_scores, rolling_halfwidths, rolling_normal_stats
from settings import ALPHA, FEATURES, GROUPS, METHODS, MODELS, WINDOW


checks = []


def check(name, condition, detail=""):
    if not condition:
        raise AssertionError(name + ": " + str(detail))
    checks.append({"name": name, "passed": True, "detail": detail})


def same_table(name, new, old, keys):
    new = new.sort_values(keys).reset_index(drop=True)[old.columns]
    old = old.sort_values(keys).reset_index(drop=True)
    pd.testing.assert_frame_equal(new, old, check_dtype=False, check_exact=False, atol=1e-10, rtol=1e-10)
    check(name, True, f"{len(old)} rows; atol=rtol=1e-10")


archive = project / "validation" / "baseline_v0_1.zip"
baseline_hashes = json.loads((project / "validation" / "baseline_hashes.json").read_text())
with ZipFile(archive) as baseline:
    prefix = "market-volatility-comparison/"
    for name, digest in baseline_hashes.items():
        check("baseline preserved: " + name,
              hashlib.sha256(baseline.read(prefix + name)).hexdigest() == digest)
    for name in ["SP500.csv", "VIXCLS.csv"]:
        check("raw bytes unchanged: " + name,
              (project / "data" / "raw" / name).read_bytes() == baseline.read(prefix + "data/raw/" + name))

    def read_baseline(name):
        return pd.read_csv(BytesIO(baseline.read(prefix + name)))

    data = pd.read_csv(project / "data/processed/analysis_dataset.csv")
    same_table("original dataset columns", data, read_baseline("data/processed/analysis_dataset.csv"), ["date"])
    same_table("original split summary", pd.read_csv(project / "reports/split_summary.csv"),
               read_baseline("reports/split_summary.csv"), ["split"])
    predictions = pd.read_csv(project / "outputs/modeling/point_predictions.csv")
    original_models = MODELS[:3]
    same_table("original point predictions", predictions.loc[predictions["model"].isin(original_models)],
               read_baseline("outputs/modeling/point_predictions.csv"), ["model", "date"])
    intervals = pd.read_csv(project / "outputs/modeling/prediction_intervals.csv")
    old_intervals = read_baseline("outputs/modeling/prediction_intervals.csv")
    mapping = {"fixed": "fixed_cp", "rolling": "rolling_cp", "normal": "fixed_normal"}
    old_intervals["method"] = old_intervals["method"].map(mapping)
    old_subset = intervals.loc[intervals["model"].isin(original_models)
                               & intervals["method"].isin(mapping.values())]
    same_table("original nine daily intervals", old_subset, old_intervals, ["model", "method", "date"])
    summary = pd.read_csv(project / "outputs/evaluation/interval_summary.csv")
    old_summary = read_baseline("outputs/evaluation/interval_summary.csv")
    old_summary["method"] = old_summary["method"].map(mapping)
    same_table("original nine interval summaries",
               summary.loc[summary["model"].isin(original_models) & summary["method"].isin(mapping.values())],
               old_summary, ["group", "model", "method"])
    point_summary = pd.read_csv(project / "outputs/evaluation/point_summary.csv")
    same_table("original point summaries", point_summary.loc[point_summary["model"].isin(original_models)],
               read_baseline("outputs/evaluation/point_summary.csv"), ["group", "model"])

# 生の価格から、予測日より前の説明変数を別の方法で確認する
raw = pd.read_csv(project / "data/raw/SP500.csv", na_values=".").dropna(subset=["SP500"])
raw = raw.loc[raw["observation_date"].between("2016-10-31", "2026-10-28")].reset_index(drop=True)
returns = (100 * np.log(raw["SP500"]).diff()).to_numpy()
positions = dict(zip(raw["observation_date"], range(len(raw))))
expected = []
for date in data["date"]:
    i = positions[date]
    cumulative = 100 * np.log(raw.loc[i - 1, "SP500"] / raw.loc[i - 6, "SP500"])
    expected.append([returns[i - 1], cumulative, np.std(returns[i - 20:i], ddof=1)])
check("all lagged return features use t-1 or earlier",
      np.allclose(data[FEATURES[:3]], expected, atol=1e-10, rtol=1e-10))
vix = pd.read_csv(project / "data/raw/VIXCLS.csv", na_values=".").set_index("observation_date")["VIXCLS"]
expected_vix = data["forecast_origin_date"].map(vix)
check("lagged VIX and regime", np.allclose(data["vix_lag1"], expected_vix)
      and np.array_equal(data["high_vix_30"], expected_vix >= 30))
check("all predictors complete", np.isfinite(data[FEATURES].to_numpy()).all())
check("predictions have one row per model/date", not predictions.duplicated(["model", "date"]).any())
check("intervals have one row per combination/date", not intervals.duplicated(["model", "method", "date"]).any())
test_dates = data.loc[data["split"] == "test", "date"].tolist()
check("1715 common test dates", len(test_dates) == 1715 and len(intervals) == 1715 * 16)
check("all interval bounds finite and ordered", np.isfinite(intervals[["lower", "upper"]]).all().all()
      and (intervals["lower"] <= intervals["upper"]).all())
check("interval centers equal point predictions",
      np.allclose((intervals["lower"] + intervals["upper"]) / 2, intervals["prediction_pct"]))

# 重回帰の推定に使うのはTrainingだけ。予測値を係数から再構成する。
train = data.loc[data["split"] == "training"]
X = np.column_stack([np.ones(len(train)), train[FEATURES]])
beta = np.linalg.lstsq(X, train["return_pct"], rcond=None)[0]
saved_beta = pd.read_csv(project / "outputs/modeling/model_coefficients.csv").set_index("model")
check("multiple regression uses training coefficients",
      np.allclose(beta, saved_beta.loc["multiple_regression"].to_numpy(dtype=float)))
check("training design full rank", np.linalg.matrix_rank(X) == X.shape[1])
multiple = predictions.loc[predictions["model"] == "multiple_regression"]
X_future = np.column_stack([np.ones(len(multiple)), multiple[FEATURES]])
check("multiple predictions use frozen coefficients", np.allclose(multiple["prediction_pct"], X_future @ beta))

z = NormalDist().inv_cdf(1 - ALPHA / 2)
for model in MODELS:
    part = predictions.loc[predictions["model"] == model].sort_values("date")
    calibration = part.loc[part["split"] == "calibration"]
    test = part.loc[part["split"] == "test"]
    errors = np.r_[calibration["error_pct"], test["error_pct"]]
    dates = pd.concat([calibration["date"], test["date"]], ignore_index=True)
    by_method = {}
    for method in METHODS:
        result = intervals.loc[(intervals["model"] == model) & (intervals["method"] == method)].sort_values("date")
        check(model + "/" + method + " common dates", result["date"].tolist() == test_dates)
        check(model + "/" + method + " past history", (result["history_end"] < result["date"]).all())
        by_method[method] = result.reset_index(drop=True)
    for fixed, rolling in [("fixed_cp", "rolling_cp"), ("fixed_normal", "rolling_normal")]:
        check(model + "/" + fixed + " constant halfwidth", by_method[fixed]["halfwidth"].nunique() == 1)
        check(model + "/" + fixed + " first-day equality",
              np.isclose(by_method[fixed].loc[0, "halfwidth"], by_method[rolling].loc[0, "halfwidth"]))
    history_columns = ["history_start", "history_end", "history_n", "history_high_vix_share",
                       "history_error_mean", "history_error_std"]
    pd.testing.assert_frame_equal(by_method["rolling_cp"][history_columns], by_method["rolling_normal"][history_columns])
    check(model + " rolling histories match", True)
    manual_cp, manual_normal, starts, ends = [], [], [], []
    for i in range(len(calibration), len(errors)):
        past = errors[i - WINDOW:i]
        k = math.ceil((WINDOW + 1) * (1 - ALPHA))
        manual_cp.append(sorted(abs(past))[k - 1])
        manual_normal.append(z * np.std(past, ddof=1))
        starts.append(dates.iloc[i - WINDOW])
        ends.append(dates.iloc[i - 1])
    check(model + " all rolling CP widths", np.allclose(manual_cp, by_method["rolling_cp"]["halfwidth"]))
    check(model + " all rolling Normal widths", np.allclose(manual_normal, by_method["rolling_normal"]["halfwidth"]))
    check(model + " rolling dates and count", by_method["rolling_cp"]["history_start"].tolist() == starts
          and by_method["rolling_cp"]["history_end"].tolist() == ends
          and (by_method["rolling_cp"]["history_n"] == WINDOW).all())
    # 当日以降の実現誤差を変えても、その日までの幅が変わらない。
    altered = test["error_pct"].to_numpy().copy()
    cut = len(altered) // 2
    altered[cut:] += 10000
    cp_after = rolling_halfwidths(abs(calibration["error_pct"]), abs(altered), WINDOW, ALPHA)
    _, std_after = rolling_normal_stats(calibration["error_pct"], altered, WINDOW)
    check(model + " future-error invariance CP", np.allclose(cp_after[:cut + 1], manual_cp[:cut + 1]))
    check(model + " future-error invariance Normal", np.allclose(z * std_after[:cut + 1], manual_normal[:cut + 1]))

actual = np.array([0, -1.3, 1.3, 1])
check("interval score anchor examples", np.allclose(interval_scores(-np.ones(4), np.ones(4), actual, ALPHA), [2, 8, 8, 2]))
check("conformal finite sample rank", conformal_halfwidth(np.arange(1, 10), ALPHA) == 9)
check("conformal unattainable finite rank", np.isinf(conformal_halfwidth([1], ALPHA)))
check("summary row counts", len(point_summary) == 12 and len(summary) == 48)
check("point summaries do not duplicate interval methods", sorted(point_summary["n"].unique()) == [149, 1566, 1715])
check("90 percent target rule", np.array_equal(summary["target_reached"], summary["coverage"] >= 0.9))
selection = pd.read_csv(project / "outputs/evaluation/selection_summary.csv")
for row in selection.itertuples():
    pool = summary.loc[summary["group"] == row.group]
    if row.scope == "target_reached_only":
        pool = pool.loc[pool["target_reached"]]
    check(row.group + "/" + row.scope + " candidate count", row.candidate_n == len(pool))
    if len(pool):
        check(row.group + "/" + row.scope + " minimum IS", np.isclose(row.interval_score, pool["interval_score"].min()))
    else:
        check(row.group + " no eligible candidate", row.status == "no_candidate_reached_target")

# Bootstrapの集計を、小さな対応付き標本の直接集計と比較する
small = np.array([[1, 1, 1], [2, 4, 0], [3, 9, 1], [4, 16, 0]], dtype=float)
mask = np.array([False, True, False, True])
group_masks = np.column_stack([np.ones(4, dtype=bool), mask, ~mask])
indices = np.array([0, 0, 1, 3])
stats, counts = sample_statistics(small, group_masks, indices, slice(1, 2))
for g in range(3):
    selected = small[indices][group_masks[indices, g]]
    direct = selected.mean(axis=0)
    direct[1] = np.sqrt(direct[1])
    check("bootstrap paired direct calculation " + GROUPS[g], np.allclose(stats[g], direct) and counts[g] == len(selected))
empty_stats, empty_n = sample_statistics(small, group_masks, np.zeros(4, dtype=int), slice(1, 2))
check("empty bootstrap regime remains undefined", empty_n[1] == 0 and np.isnan(empty_stats[1]).all())

bootstrap_dir = project / "outputs/evaluation/bootstrap"
config = json.loads((bootstrap_dir / "settings.json").read_text())
check("bootstrap input digest", config["input_daily_sha256"] == hashlib.sha256((project / "outputs/evaluation/daily_evaluation.csv").read_bytes()).hexdigest())
metric_ci = pd.read_csv(bootstrap_dir / "metric_intervals.csv")
for row in metric_ci.itertuples():
    table = point_summary if row.kind == "point" else summary
    subset = table.loc[(table["group"] == row.group) & (table["model"] == row.model)]
    if row.kind == "interval":
        subset = subset.loc[subset["method"] == row.method]
    check("bootstrap estimate " + "/".join(map(str, [row.block_length, row.group, row.model, row.method, row.metric])),
          np.isclose(row.estimate, subset.iloc[0][row.metric]) and row.valid_reps == 5000)
for run in config["runs"]:
    rng = np.random.default_rng(run["seed"])
    digest = hashlib.sha256()
    for b in range(run["reps"]):
        ix = draw_block_indices(config["n"], run["block_length"], rng)
        if b < 3:
            check("bootstrap index prefix " + str((run["block_length"], b)), ix[:30].tolist() == run["first_three_index_prefixes"][b])
        digest.update(ix.astype("<i8").tobytes())
    check("bootstrap all index digest " + str(run["block_length"]), digest.hexdigest() == run["all_indices_sha256_little_endian_int64"])
    check("no bootstrap regimes lost " + str(run["block_length"]), all(v == 0 for v in run["zero_group_reps"].values()))

report = {
    "status": "passed", "check_count": len(checks), "checks": checks,
    "baseline_archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
    "raw_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (project / "data/raw").glob("*.csv")},
    "runtime": {"python": platform.python_version(), "numpy": np.__version__,
                "pandas": pd.__version__, "matplotlib": matplotlib.__version__},
    "interpretation": "Numerical and timing checks only; does not establish coverage guarantees or bootstrap validity under nonstationarity.",
}
(project / "validation/verification.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"検証完了: {len(checks)}項目に合格")
