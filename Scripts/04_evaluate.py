import numpy as np
import pandas as pd

from intervals import interval_scores
from settings import ALPHA, GROUPS, project_dir


output_dir = project_dir / "outputs" / "evaluation"
output_dir.mkdir(parents=True, exist_ok=True)
predictions = pd.read_csv(project_dir / "outputs" / "modeling" / "point_predictions.csv")
points = predictions.loc[predictions["split"] == "test"].copy()
daily = pd.read_csv(
    project_dir / "outputs" / "modeling" / "prediction_intervals.csv",
    parse_dates=["date"],
)

# 点予測の誤差と、予測区間の評価
points["absolute_error"] = points["error_pct"].abs()
points["squared_error"] = points["error_pct"] ** 2
y = daily["return_pct"]
daily["covered"] = ((daily["lower"] <= y) & (y <= daily["upper"])).astype(float)
daily["width"] = daily["upper"] - daily["lower"]
daily["interval_score"] = interval_scores(daily["lower"], daily["upper"], y, ALPHA)
daily["lower_miss"] = (y < daily["lower"]).astype(float)
daily["upper_miss"] = (y > daily["upper"]).astype(float)

point_records = []
interval_records = []
for group in GROUPS:
    point_part = points
    interval_part = daily
    if group != "overall":
        high = group == "high_vix"
        point_part = points.loc[points["high_vix_30"] == high]
        interval_part = daily.loc[daily["high_vix_30"] == high]

    point_summary = point_part.groupby("model").agg(
        n=("date", "size"), mae=("absolute_error", "mean"),
        mse=("squared_error", "mean"),
    ).reset_index()
    point_summary["rmse"] = np.sqrt(point_summary.pop("mse"))
    point_summary["rmse_rank"] = point_summary["rmse"].rank(method="min").astype(int)
    point_summary.insert(0, "group", group)
    point_records.append(point_summary)

    interval_summary = interval_part.groupby(["model", "method"]).agg(
        n=("date", "size"), coverage=("covered", "mean"),
        width=("width", "mean"), interval_score=("interval_score", "mean"),
        lower_miss=("lower_miss", "mean"), upper_miss=("upper_miss", "mean"),
    ).reset_index()
    interval_summary["coverage_gap"] = interval_summary["coverage"] - (1 - ALPHA)
    interval_summary["target_reached"] = interval_summary["coverage"] >= (1 - ALPHA)
    interval_summary["is_rank"] = interval_summary["interval_score"].rank(method="min").astype(int)
    interval_summary.insert(0, "group", group)
    interval_records.append(interval_summary)

point_summary = pd.concat(point_records, ignore_index=True)
interval_summary = pd.concat(interval_records, ignore_index=True)

# 市場区分ごとに、最小ISと目標到達候補の最小ISを区別する
selection_records = []
for group in GROUPS:
    part = interval_summary.loc[interval_summary["group"] == group]
    eligible = part.loc[part["target_reached"]]
    for scope, candidates in [("all_candidates", part), ("target_reached_only", eligible)]:
        row = {"group": group, "scope": scope, "candidate_n": len(candidates)}
        if len(candidates):
            best = candidates.loc[candidates["interval_score"].idxmin()]
            for column in ["model", "method", "coverage", "width", "interval_score"]:
                row[column] = best[column]
            row["status"] = "observed_minimum"
        else:
            row["status"] = "no_candidate_reached_target"
        selection_records.append(row)
selection = pd.DataFrame(selection_records)

# 両市場区分での目標到達も、点推定による表示として記録する
regimes = interval_summary.loc[interval_summary["group"] != "overall"]
both = regimes.groupby(["model", "method"])["target_reached"].all()
both.rename("target_reached_in_both_regimes").to_csv(output_dir / "regime_target_status.csv")

# 年ごとの違いも確認する
daily["year"] = daily["date"].dt.year
annual = daily.groupby(["year", "model", "method"]).agg(
    n=("date", "size"), coverage=("covered", "mean"),
    width=("width", "mean"), interval_score=("interval_score", "mean"),
).reset_index()

point_summary.to_csv(output_dir / "point_summary.csv", index=False)
interval_summary.to_csv(output_dir / "interval_summary.csv", index=False)
annual.to_csv(output_dir / "annual_summary.csv", index=False)
selection.to_csv(output_dir / "selection_summary.csv", index=False)
daily.to_csv(output_dir / "daily_evaluation.csv", index=False)
print(point_summary.round(4).to_string(index=False))
print(selection.round(4).to_string(index=False))
