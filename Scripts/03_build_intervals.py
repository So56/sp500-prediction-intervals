from statistics import NormalDist

import pandas as pd

from intervals import conformal_halfwidth, rolling_halfwidths, rolling_normal_stats
from settings import ALPHA, METHODS, MODELS, WINDOW, project_dir


output_dir = project_dir / "outputs" / "modeling"
predictions = pd.read_csv(
    output_dir / "point_predictions.csv",
    parse_dates=["date", "forecast_origin_date"],
).sort_values(["model", "date"])
z = NormalDist().inv_cdf(1 - ALPHA / 2)
records = []
settings = []

for model in MODELS:
    part = predictions.loc[predictions["model"] == model]
    calibration = part.loc[part["split"] == "calibration"]
    test = part.loc[part["split"] == "test"].copy().reset_index(drop=True)
    if len(calibration) < WINDOW or calibration["date"].max() >= test["date"].min():
        raise ValueError("Calibrationの長さとTestとの時間順序を確認してください。")

    q_fixed = conformal_halfwidth(calibration["score_abs"], ALPHA)
    q_rolling = rolling_halfwidths(
        calibration["score_abs"], test["score_abs"], WINDOW, ALPHA
    )
    # 正規近似では誤差の平均を0と仮定し、Calibration誤差の標準偏差を使う。
    # 平均の信頼区間ではないので、標準偏差をsqrt(n)で割らない。
    sigma = calibration["error_pct"].std(ddof=1)
    q_normal = z * sigma
    rolling_mean, rolling_sigma = rolling_normal_stats(
        calibration["error_pct"], test["error_pct"], WINDOW
    )
    widths = {
        "fixed_cp": q_fixed, "rolling_cp": q_rolling,
        "fixed_normal": q_normal, "rolling_normal": z * rolling_sigma,
    }

    # どの誤差が幅の計算に使われたかを記録する
    history_dates = pd.concat([calibration["date"], test["date"]], ignore_index=True)
    history_high = pd.concat([
        calibration["high_vix_30"], test["high_vix_30"]
    ], ignore_index=True)
    for method in METHODS:
        result = test.copy()
        result["method"] = method
        result["halfwidth"] = widths[method]
        result["lower"] = result["prediction_pct"] - result["halfwidth"]
        result["upper"] = result["prediction_pct"] + result["halfwidth"]
        if method.startswith("rolling"):
            stops = range(len(calibration), len(calibration) + len(test))
            result["history_start"] = [history_dates.iloc[i - WINDOW] for i in stops]
            result["history_end"] = result["forecast_origin_date"]
            result["history_n"] = WINDOW
            result["history_high_vix_share"] = [
                history_high.iloc[i - WINDOW:i].mean() for i in stops
            ]
            result["history_error_mean"] = rolling_mean
            result["history_error_std"] = rolling_sigma
        else:
            result["history_start"] = calibration["date"].min()
            result["history_end"] = calibration["date"].max()
            result["history_n"] = len(calibration)
            result["history_high_vix_share"] = calibration["high_vix_30"].mean()
            result["history_error_mean"] = calibration["error_pct"].mean()
            result["history_error_std"] = sigma
        records.append(result)

    settings.append({
        "model": model, "alpha": ALPHA, "rolling_window": WINDOW,
        "calibration_n": len(calibration), "test_n": len(test),
        "fixed_cp_halfwidth": q_fixed, "fixed_normal_halfwidth": q_normal,
        "normal_sigma": sigma, "normal_z": z,
        "calibration_mean_error": calibration["error_pct"].mean(),
    })

intervals = pd.concat(records, ignore_index=True)
intervals.to_csv(output_dir / "prediction_intervals.csv", index=False)
pd.DataFrame(settings).to_csv(output_dir / "interval_settings.csv", index=False)
print(pd.DataFrame(settings).round(6).to_string(index=False))
