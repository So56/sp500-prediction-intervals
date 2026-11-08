import numpy as np
import pandas as pd

from settings import (
    CALIBRATION_START, FEATURES, RAW_END, RAW_START, TEST_START,
    TRAIN_START, VIX_THRESHOLD, project_dir,
)


# データの読み込み
raw_dir = project_dir / "data" / "raw"
sp500 = pd.read_csv(
    raw_dir / "SP500.csv", na_values=".", parse_dates=["observation_date"]
).rename(columns={"observation_date": "date", "SP500": "sp500_close"})
vix = pd.read_csv(
    raw_dir / "VIXCLS.csv", na_values=".", parse_dates=["observation_date"]
).rename(columns={"observation_date": "date", "VIXCLS": "vix_close"})

market = sp500.dropna(subset=["sp500_close"]).merge(
    vix, on="date", how="left", validate="one_to_one"
).sort_values("date").reset_index(drop=True)
market = market.loc[market["date"].between(RAW_START, RAW_END)].copy()

# リターンと前営業日の情報を作る
if market["vix_close"].isna().any() or (market["sp500_close"] <= 0).any():
    raise ValueError("VIXの欠損またはS&P 500の終値を確認してください。")

market["return_pct"] = 100 * np.log(market["sp500_close"]).diff()
market["return_lag1_pct"] = market["return_pct"].shift(1)
market["vix_lag1"] = market["vix_close"].shift(1)
market["forecast_origin_date"] = market["date"].shift(1)

# 移動集計も前営業日までのリターンから作る
market["return_5d_lag1_pct"] = market["return_pct"].shift(1).rolling(5).sum()
market["volatility_20d_lag1"] = market["return_pct"].shift(1).rolling(20).std(ddof=1)

analysis = market.loc[market["date"] >= TRAIN_START].copy()
if analysis[["return_pct"] + FEATURES].isna().any().any():
    raise ValueError("分析開始日前のデータが十分にあるか確認してください。")

# 前営業日のVIXが30以上ならHigh-VIX
analysis["high_vix_30"] = analysis["vix_lag1"] >= VIX_THRESHOLD
analysis["split"] = "training"
analysis.loc[analysis["date"] >= CALIBRATION_START, "split"] = "calibration"
analysis.loc[analysis["date"] >= TEST_START, "split"] = "test"

summary = analysis.groupby("split").agg(
    first_date=("date", "min"), last_date=("date", "max"),
    n=("date", "size"), high_vix_days=("high_vix_30", "sum"),
).reindex(["training", "calibration", "test"])
summary["high_vix_share"] = summary["high_vix_days"] / summary["n"]

# CSV保存
processed_dir = project_dir / "data" / "processed"
report_dir = project_dir / "reports"
processed_dir.mkdir(parents=True, exist_ok=True)
report_dir.mkdir(parents=True, exist_ok=True)
analysis.to_csv(processed_dir / "analysis_dataset.csv", index=False)
summary.to_csv(report_dir / "split_summary.csv")
print(summary.to_string())
