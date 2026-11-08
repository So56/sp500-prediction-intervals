# Comparing Forecasting Models and Prediction Interval Methods Across Market Volatility Regimes

This undergraduate thesis project compares four forecasting models and four methods for constructing nominal 90% prediction intervals for next-day S&P 500 log returns. It evaluates all 16 combinations on the same data and examines how point forecast accuracy, interval coverage, width and interval score vary across market volatility regimes.

The interval score (IS) penalises wide intervals and returns that fall outside them. The analysis ranks combinations by mean IS and separately records whether empirical coverage reaches 90%.

## Start here

- [Results and discussion](reports/results_v0_2.md) — Results for all 16 combinations and approximate 95% confidence intervals for selected performance differences.
- [Research design](research_design.md) — Forecast timing, predictors, interval construction and evaluation criteria.
- [Predictor definitions](reports/feature_definitions.md) — How the four predictors are constructed and why they were included.
- [Original improvement plan](research_improvement_plan.md) — The plan recorded before implementation.

The linked documents are in Japanese.

## Study design

The data are daily S&P 500 closing values and Cboe Volatility Index (VIX) values from Federal Reserve Economic Data (FRED). Forecasts use information available by the close of the previous trading day.

| Item | Setting |
| --- | --- |
| Target variable | Next-trading-day S&P 500 log return, expressed as a percentage |
| Training | 2017-01-03 to 2018-12-31, 502 trading days |
| Calibration | 2019-01-02 to 2019-12-31, 252 trading days |
| Test | 2020-01-02 to 2026-10-28, 1,715 trading days |
| Nominal coverage | 90% (α = 0.10) |
| Rolling window | 252 trading days |
| High-VIX test days | Previous trading day's VIX close was at least 30, 149 days |
| Other test days | Previous trading day's VIX close was below 30, 1,566 days |

The point forecast models are a driftless random walk, the historical mean, a first-order autoregression (AR(1)) and multiple linear regression. The random walk predicts a zero return. The historical mean uses the average return in the training period. AR(1) uses the previous day's return. Multiple linear regression uses that return, the cumulative log return over the previous five trading days, the sample standard deviation of returns over the previous 20 trading days and the previous day's VIX close. Both regressions are fitted by ordinary least squares on the training data, and their coefficients are fixed for calibration and testing.

The four interval methods are fixed conformal prediction (CP), rolling CP, fixed normal and rolling normal. All intervals are centred on the point forecast. Fixed methods use the 252 forecast errors from the 2019 calibration period. Rolling methods use the 252 most recent observed errors and add each day's error after that day's interval is issued. CP uses an order statistic of absolute forecast errors. The normal approximation uses the 95th percentile of the standard normal distribution multiplied by the sample standard deviation of signed forecast errors.

Point forecast accuracy is measured by root mean squared error (RMSE) and mean absolute error (MAE). Intervals are evaluated by empirical coverage, mean width and mean IS. Approximate 95% confidence intervals for selected performance differences use a paired moving-block bootstrap. Each comparison uses the same sampled blocks for both methods. The main block length is 10 trading days, with sensitivity checks at 5 and 20 days and 5,000 resamples per length.

## Key findings

- Six combinations reached 90% empirical coverage over the full test period. The driftless random walk with rolling CP had the lowest mean IS and covered 90.32% of returns.
- On the 149 high-VIX days, the highest empirical coverage was 68.46%, for AR(1) with rolling normal intervals. That combination also had the lowest mean IS on those days. Both rolling methods gave wider AR(1) intervals, higher coverage and lower mean scores than their fixed counterparts.
- On the other test days, the driftless random walk with fixed normal intervals had the lowest mean IS and covered 84.93% of returns. Among combinations that reached 90% coverage, the driftless random walk with rolling CP had the lowest mean IS and covered 92.66% of returns.

## Data and reproducibility

The original project archive is preserved in `validation/baseline_v0_1.zip`. The bundled raw data, `data/raw/SP500.csv` and `data/raw/VIXCLS.csv`, are byte-for-byte identical to the files in that archive.

The analysis reproduces the nine combinations from the earlier project. The method identifiers previously recorded as `fixed`, `rolling` and `normal` are now `fixed_cp`, `rolling_cp` and `fixed_normal`, respectively.

## Run the analysis in VS Code and PowerShell

If you received the project as a ZIP, extract it to a separate location and open the extracted project folder in VS Code. From the project root, run the following commands in PowerShell. The analysis has been tested with Python 3.12.14 and with Python 3.13.14 on Windows.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe Scripts/run_all.py
.\.venv\Scripts\python.exe validation/verify_analysis.py
```

To run individual files from VS Code, open the Command Palette, choose `Python: Select Interpreter` and select `.venv\Scripts\python.exe`. If you see `ModuleNotFoundError: No module named 'numpy'`, install the dependencies with the command above and run the script using that same interpreter. When launched from the system Python, `run_all.py` uses the project's virtual environment if it exists.

The project includes the results and figures for direct reading. Rerunning the analysis overwrites the corresponding output files in this project folder.

## Run the scripts individually

| Order | Script | Purpose |
| --- | --- | --- |
| 1 | `Scripts/01_prepare_data.py` | Read the raw data and construct lagged and rolling predictors. |
| 2 | `Scripts/02_fit_models.py` | Fit the four models on the training data and save point forecasts and errors. |
| 3 | `Scripts/03_build_intervals.py` | Construct four types of prediction intervals for each model. |
| 4 | `Scripts/04_evaluate.py` | Produce 12 point forecast summaries and 48 interval summaries, then identify the lowest-scoring combinations with and without the coverage requirement. |
| 5 | `Scripts/06_bootstrap.py` | Estimate uncertainty using 5,000 paired moving-block resamples for each block length of 10, 5 and 20 trading days. |
| 6 | `Scripts/05_make_figures.py` | Generate comparison figures and confidence interval plots. |
| 7 | `Scripts/07_write_report.py` | Generate the Japanese results report from the saved outputs. |
| 8 | `validation/verify_analysis.py` | Verify reproduction of the nine baseline combinations, forecast timing and numerical results. |

Run `06_bootstrap.py` before `05_make_figures.py` because the figures use the bootstrap output. To run only the data preparation step, use the following command.

```powershell
.\.venv\Scripts\python.exe Scripts/01_prepare_data.py
```

The scripts follow a read, compute and save sequence and include short Japanese comments. Shared settings are in `Scripts/settings.py`. Functions for prediction intervals and interval scores are in `Scripts/intervals.py`. Bootstrap sampling and aggregation functions are in `Scripts/bootstrap.py`. Read scripts 01 through 04 in order to follow the analysis from the raw data to the results tables.

## Main outputs

| Path | Contents |
| --- | --- |
| `data/processed/analysis_dataset.csv` | Analysis dataset, including the five-day cumulative return and 20-day volatility predictors. |
| `outputs/modeling/model_coefficients.csv` | Coefficients for all four models, with zeros for unused predictors. |
| `outputs/modeling/training_feature_correlations.csv` | Correlations among the four predictors in the training data. |
| `outputs/modeling/training_feature_summary.csv` | Summary statistics for the training predictors. |
| `outputs/modeling/point_predictions.csv` | Point forecasts and forecast errors for calibration and testing. |
| `outputs/modeling/prediction_intervals.csv` | Daily intervals and error-history details for 16 combinations over 1,715 test days. |
| `outputs/evaluation/point_summary.csv` | MAE and RMSE for four models across the full test period, high-VIX days and other days. |
| `outputs/evaluation/interval_summary.csv` | Coverage, mean width, mean IS and coverage target status for 16 combinations across the same three groups. |
| `outputs/evaluation/selection_summary.csv` | Lowest mean IS among all combinations and among those meeting the coverage target, by group. |
| `outputs/evaluation/regime_target_status.csv` | Whether each combination reached 90% coverage in both VIX groups. |
| `outputs/evaluation/bootstrap/metric_intervals.csv` | Approximate 95% confidence intervals for individual metrics at three block lengths. |
| `outputs/evaluation/bootstrap/paired_differences.csv` | Selected paired performance differences and approximate 95% confidence intervals. |
| `outputs/evaluation/bootstrap/settings.json` | Resampling settings, hashes of the sampled date indices and group sizes. |
| `outputs/figures/` | Five figures in PNG and PDF formats. |
| `reports/results_v0_2.md` | Results tables and discussion in Japanese. |
| `validation/verification.json` | Verification results, raw data hashes and runtime environment. |

Coverage and miss rates are stored as proportions from 0 to 1 in CSV files and shown as percentages in the figures and report. MAE, RMSE, interval width and IS are expressed in return percentage points.

`target_reached` records whether empirical coverage was at least 90% in the evaluated sample. `is_rank` and `rmse_rank` rank point estimates. `zero_excluded` records whether an approximate 95% confidence interval excludes zero. The reported intervals are unadjusted for multiple comparisons.

## Verification

The checks cover reproduction of the original nine combinations, including point forecasts, daily intervals and summary metrics. They also verify dates and row counts, the timing of predictors, fixed model coefficients, the absence of look-ahead in error histories, interval endpoints, numerical examples of the interval score, and paired bootstrap aggregation and sampled indices.

The verification script targets the default experiment. If you change the dates, window length or model set, review checks that depend on the original settings, including the 1,715-day test count and comparisons with the original results.

## Limitations and future work

The results are exploratory because part of the test period had already been examined. The usual split-conformal guarantee is marginal and relies on exchangeability, which may be difficult to justify in financial time series with serial dependence and changing volatility. The normal approximation omits uncertainty in the fitted coefficients. The bootstrap uses saved results with the fitted models held fixed, and its confidence intervals can be sensitive to block length and the small number of high-volatility episodes.

The 2019 calibration period contained no high-VIX days. Future work will compare several forecast start dates while keeping training and calibration window lengths fixed. It will examine how the share and recency of high-VIX days in those windows relate to subsequent forecast performance, and how performance changes with the rolling window length.

