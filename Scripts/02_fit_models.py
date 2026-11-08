import numpy as np
import pandas as pd

from settings import FEATURES, MODELS, project_dir


data = pd.read_csv(
    project_dir / "data" / "processed" / "analysis_dataset.csv",
    parse_dates=["date", "forecast_origin_date"],
).sort_values("date")
output_dir = project_dir / "outputs" / "modeling"
output_dir.mkdir(parents=True, exist_ok=True)

# Trainingデータだけで平均と係数を推定する
train = data.loc[data["split"] == "training"]
mean_return = train["return_pct"].mean()
X = np.column_stack([np.ones(len(train)), train["return_lag1_pct"]])
beta0, beta1 = np.linalg.lstsq(X, train["return_pct"], rcond=None)[0]
X_multiple = np.column_stack([np.ones(len(train)), train[FEATURES]])
beta_multiple = np.linalg.lstsq(X_multiple, train["return_pct"], rcond=None)[0]

coefficients = pd.DataFrame([
    {"model": "random_walk", "intercept": 0.0, "lag1_coefficient": 0.0},
    {"model": "historical_mean", "intercept": mean_return, "lag1_coefficient": 0.0},
    {"model": "ar1", "intercept": beta0, "lag1_coefficient": beta1},
])
extra_columns = ["return5_coefficient", "volatility20_coefficient", "vix_coefficient"]
coefficients[extra_columns] = 0.0
coefficients.loc[len(coefficients)] = ["multiple_regression"] + beta_multiple.tolist()

# Training内の相関と、説明変数の大きさを記録する
train[FEATURES].corr().to_csv(output_dir / "training_feature_correlations.csv")
train[FEATURES].describe().to_csv(output_dir / "training_feature_summary.csv")

# CalibrationとTestでは係数を更新しない
future = data.loc[data["split"].isin(["calibration", "test"])].copy()
records = []
for model in MODELS:
    part = future.copy()
    part["model"] = model
    if model == "random_walk":
        # 価格のRandom Walkを仮定すると、翌日のリターン予測は0になる。
        part["prediction_pct"] = 0.0
    elif model == "historical_mean":
        part["prediction_pct"] = mean_return
    elif model == "ar1":
        part["prediction_pct"] = beta0 + beta1 * part["return_lag1_pct"]
    else:
        X_future = np.column_stack([np.ones(len(part)), part[FEATURES]])
        part["prediction_pct"] = X_future @ beta_multiple
    part["error_pct"] = part["return_pct"] - part["prediction_pct"]
    part["score_abs"] = part["error_pct"].abs()
    records.append(part)

predictions = pd.concat(records, ignore_index=True)
predictions.to_csv(output_dir / "point_predictions.csv", index=False)
coefficients.to_csv(output_dir / "model_coefficients.csv", index=False)
print(coefficients.to_string(index=False))
