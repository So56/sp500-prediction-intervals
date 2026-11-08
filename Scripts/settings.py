from pathlib import Path


# 分析に使う設定
project_dir = Path(__file__).resolve().parent.parent

RAW_START = "2016-10-31"
RAW_END = "2026-10-28"
TRAIN_START = "2017-01-01"
CALIBRATION_START = "2019-01-01"
TEST_START = "2020-01-01"

ALPHA = 0.10
WINDOW = 252
VIX_THRESHOLD = 30

MODELS = ["random_walk", "historical_mean", "ar1", "multiple_regression"]
METHODS = ["fixed_cp", "rolling_cp", "fixed_normal", "rolling_normal"]
GROUPS = ["overall", "high_vix", "non_high_vix"]

FEATURES = ["return_lag1_pct", "return_5d_lag1_pct", "volatility_20d_lag1", "vix_lag1"]

# Bootstrapの主設定と感度分析
BLOCK_LENGTHS = [10, 5, 20]
BOOTSTRAP_REPS = 5000
BOOTSTRAP_SEED = 202701
