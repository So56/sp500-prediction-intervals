# Research Improvement Plan v0.2

Created: November 6, 2026\
Topic: Comparing forecasting models and prediction interval methods across market volatility regimes\
Status: Planning only. No analysis code has been changed, models fitted, new intervals calculated, or bootstrap analysis performed as part of this plan.

## 1. Proposed Changes and Objectives

The plan has three main changes:

1. Add a multiple regression model alongside the existing Random Walk, Historical Mean, and AR(1) models.
2. Split the existing Normal interval method into Fixed Normal and Rolling Normal.
3. Evaluate point forecast accuracy, overall interval performance, and attainment of the coverage target separately, without changing the criteria after inspecting the results.

We will compare 4 point forecast models and 16 prediction interval combinations: 4 models × 4 interval methods. Random Walk and Historical Mean will remain as baselines for assessing whether more complex models add value.

| Point forecast model | Fixed CP | Rolling CP | Fixed Normal | Rolling Normal |
| --- | --- | --- | --- | --- |
| Random Walk: forecast return of 0 | Compare | Compare | Compare | Compare |
| Historical Mean: training mean | Compare | Compare | Compare | Compare |
| AR(1): intercept + previous trading day's return | Compare | Compare | Compare | Compare |
| Multiple Regression: intercept + 4 predictors | Add | Add | Add | Add |

## 2. Existing Data and Comparison Settings

We reviewed the research design and the code for preprocessing, modeling, interval construction, and evaluation in the existing `market_volatility_comparison_v0_1.zip` archive. We also checked the previously saved summaries by period. The settings and counts below come from those files and have not been recalculated for this plan.

| Item | Setting |
| --- | --- |
| Raw data | Use the existing SP500.csv and VIXCLS.csv files; obtain no additional data |
| Target variable | Daily S&P 500 log return: `r_t = 100 × log(P_t / P_(t-1))` |
| Forecast timing | After the previous trading day's close, forecast the return through the current day's close |
| Training | 2017-01-03 to 2018-12-31: 502 days |
| Calibration | 2019-01-02 to 2019-12-31: 252 days |
| Test | 2020-01-02 to 2026-10-28: 1,715 days |
| Target coverage | 90%: `alpha = 0.10` |
| Rolling window | 252 trading days |
| High VIX | VIX of at least 30 on the trading day before the forecast date |
| Lower VIX | VIX below 30 on the trading day before the forecast date |
| Updates to coefficients and means | Held fixed after training; rolling updates change the interval width |

The existing summaries report 149 high-VIX days in testing, 5 in training, and 0 in calibration. High-VIX results are affected by both the number of observations and their concentration in a few crises. Multiple regression forecasts during high-VIX periods may involve extrapolation to conditions poorly represented in training.

## 3. Proposed Multiple Regression Model

### 3.1 Predictors

We propose the following 4 predictors for the primary specification. All can be derived from the same 2 raw data sources.

| Predictor | Information used to forecast date t | Rationale |
| --- | --- | --- |
| Previous trading day's return | `r_(t-1)` | Maintain a link to the existing AR(1) model and capture short-term persistence or reversal |
| Cumulative return over the previous 5 trading days | `r_(t-5) + ... + r_(t-1)` | Capture recent upward or downward movements that a single day's return cannot represent |
| Realized volatility over the previous 20 trading days | Sample standard deviation of `r_(t-20), ..., r_(t-1)`, with ddof=1 | Measure the magnitude of past realized price movements |
| Previous trading day's VIX | `VIX_(t-1)` | Add an options-based measure of market uncertainty |

The forecast equation will be:

`r_hat_t = beta0 + beta1 × lag1_t + beta2 × return5_t + beta3 × vol20_t + beta4 × vix_lag1_t`

We will use ordinary least squares (OLS) with an intercept, estimated with `numpy.linalg.lstsq` as in the existing AR(1) model. No additional machine learning library or complex class structure is needed.

The 5-day and 20-day windows are interpretable initial choices corresponding approximately to one trading week and one trading month. We do not claim that these lengths are optimal and will not adjust them based on the current test results.

### 3.2 Implementation Requirements and Interpretation

- Calculate rolling features on the raw time series, align them to use values only through t−1, and then split the data into training, calibration, and test sets.
- Use historical data from the previous year to construct predictors for the first training rows of the year. Verify that the 20-day lookback is available; do not silently drop missing rows and thereby change the evaluation dates.
- Estimate coefficients using training data only, without refitting during calibration or testing. Use the same evaluation dates for all models.
- Inspect training correlations and unusually large coefficients. Do not reselect predictors based on test performance or coefficient p-values.
- The previous day's return and the five-day cumulative return contain overlapping information. VIX and realized volatility may also be correlated, so individual coefficients should not be interpreted as causal effects.
- VIX and realized volatility primarily describe the magnitude of price movements. Adding them to a mean return forecast does not guarantee improved accuracy.
- This multiple regression is a model of the conditional mean. Adding volatility as a predictor does not directly change interval width; each interval method determines the width.
- The comparison with AR(1) assesses the value of adding predictors within the same OLS framework. It does not fully separate differences in model structure from differences in the information used.

## 4. A 2×2 Framework for Prediction Intervals

For each model, define the signed forecast error as `e_t = r_t - r_hat_t` and the CP score as `abs(e_t)`. Every interval method uses the same point forecast from the corresponding model as its center.

| Interval method | How the width is determined | Error history |
| --- | --- | --- |
| Fixed CP | Empirical quantile of absolute errors with a finite-sample correction | The full 2019 calibration period |
| Rolling CP | Empirical quantile of absolute errors with a finite-sample correction | The most recent 252 days before the forecast date |
| Fixed Normal | Sample standard deviation of signed errors × approximately 1.645 | The full 2019 calibration period |
| Rolling Normal | Sample standard deviation of signed errors × approximately 1.645 | The most recent 252 days before the forecast date |

CP retains the existing definition: its half-width is the k-th smallest absolute error, where `k = ceil((n + 1) × (1 - alpha))`. Normal also retains the existing definition, `r_hat_t ± z_(1-alpha/2) × s`, where s is the sample standard deviation with ddof=1.

Normal intervals remain centered on the point forecast; adding the mean error to the center is not part of the primary analysis. The mean errors for both fixed and rolling histories will also be saved to assess departures from the zero mean approximation. The sample standard deviation is calculated around the mean error, but the interval center is not adjusted. Systematic forecast bias can therefore affect Normal coverage.

Both Normal methods produce prediction intervals based on a normal approximation. They are distinct from exact finite-sample regression prediction intervals that account for coefficient estimation uncertainty and related factors. Because these are not confidence intervals for a mean, the standard deviation is not divided by sqrt(n).

Rolling methods calculate the current day's width using past errors only, then add the current day's realized error to the history. Rolling CP and Rolling Normal use errors from the same dates. On the first test day, Fixed and Rolling half-widths must match within each construction method.

The comparisons address the following questions:

| Comparison | What it assesses |
| --- | --- |
| Fixed CP vs Fixed Normal | Empirical quantiles versus a normal approximation using the same fixed history |
| Rolling CP vs Rolling Normal | Empirical quantiles versus a normal approximation using the same rolling history |
| Fixed CP vs Rolling CP | The effect of updating the history for CP |
| Fixed Normal vs Rolling Normal | The effect of updating the history for the normal approximation |

The normal approximation also includes assumptions such as an approximately zero mean error. Performance differences from CP should therefore not be attributed solely to whether the error distribution is normal.

## 5. Criteria for Evaluating Combinations

### 5.1 Prespecify the Role of Each Metric

| Evaluation target | Primary metric or criterion | Secondary metrics |
| --- | --- | --- |
| Point forecast accuracy: 4 models | Lower RMSE is better | MAE; explain both rankings if they differ |
| Overall interval performance: 16 combinations | Lower mean interval score is better | Coverage, mean width, and proportions falling below and above the interval |
| Attainment of the target | Whether empirical coverage is at least 90% | Difference from 90% and an approximate 95% confidence interval for coverage |
| Stability across market conditions | Evaluate high-VIX and lower-VIX days separately | Annual results and the number of days in each regime |

RMSE is the primary metric because it penalizes large forecast errors more heavily and provides a single criterion for comparing models that forecast the mean. The same model may not perform best under MAE.

We will use the established interval score, which evaluates both interval width and the distance of observations outside the interval.[1]

`IS_t = (U_t - L_t) + (2 / alpha) × max(L_t - r_t, 0) + (2 / alpha) × max(r_t - U_t, 0)`

For a 90% interval, `2 / alpha = 20`. For example, an interval of width 4 has an IS of 4 if the realized value lies inside it. An interval of width 2 has an IS of 8 if the realized value lies 0.3 beyond one boundary. We will compare mean daily IS across all days or within the relevant market regime.

We will not construct an arbitrarily weighted composite such as "MAE + Coverage + Width." Since point forecast MAE and RMSE do not vary by interval method, the point forecast table will contain only the 4 models.

### 5.2 Assessment Procedure

Results for the full test period, high-VIX days, and lower-VIX days will be organized in the following order:

1. Report mean IS, coverage, mean width, the proportions falling below and above the interval, and the number of days for all 16 combinations.
2. Identify the candidate with the lowest mean IS as the candidate with the best overall interval performance during the observed period. This alone does not imply that it achieved 90% coverage.
3. Label candidates with empirical coverage of at least 90% as "Target met based on the point estimate." Among those candidates, identify the one with the lowest mean IS as having the best overall interval performance among candidates that met the target.
4. If there are 0 qualifying candidates, report "No combination met the target in this regime." Also describe the best-performing candidate that fell short, explicitly noting its coverage shortfall.
5. If a candidate achieves at least 90% coverage in both the high-VIX and lower-VIX regimes, it may be labeled "Target met in both market regimes based on the point estimates." This must not be described as a guarantee of future coverage.
6. Avoid claiming unique superiority when differences between candidates are small and uncertainty is substantial.

The 90% threshold is a practical, descriptive criterion aligned with the nominal level in this study, rather than a statistical certification standard. We will not present 89.9% and 90.1% as clearly different levels of performance or relax the primary threshold retrospectively to a value such as 88%. No blanket upper coverage limit will be imposed on candidates above 90%; excessive width will be assessed through IS and mean width.

Mean width will not be ranked on the assumption that narrower is always better. Coverage and IS will be reported alongside it, with a coverage–width scatterplot if helpful. Even at the same coverage, IS can differ because of the distance of observations outside the interval and the timing of increases in width.[1]

High-VIX days are a subset of the full period, so strong overall performance does not establish suitability for high-VIX conditions. We will not create an additional aggregate score combining the full period, high-VIX days, and lower-VIX days.

## 6. Additional Analysis to Avoid Overstating Small Differences

We plan to add approximate 95% confidence intervals for the main comparisons using a paired moving block bootstrap.

| Setting | Plan |
| --- | --- |
| Sampling unit | Blocks of consecutive trading days from the full test series |
| Primary block length | 10 trading days |
| Sensitivity analysis | 5 and 20 trading days |
| Replications | 5,000 for each setting |
| Seed | 202701; initialize separately for each block length and record the settings |
| Pairing across methods | Use the same sampled date indices for all models and interval methods |
| Market regimes | Resample VIX regime labels with the observations, then calculate metrics by regime |
| Recalculation | RMSE, MAE, coverage, mean width, mean IS, and differences for prespecified comparisons |

High-VIX days will not be extracted in advance and sampled independently. The number of high-VIX days is allowed to vary between samples. If a sample contains 0 days in a target regime, its metrics will be treated as undefined and the occurrence recorded; such samples will not be silently redrawn.

The main comparisons will be Multiple Regression − AR(1) under each interval method, and Fixed CP − Fixed Normal, Rolling CP − Rolling Normal, Rolling CP − Fixed CP, and Rolling Normal − Fixed Normal for each model. For point forecasts, Multiple Regression − AR(1) will be the primary comparison, with performance relative to Random Walk and Historical Mean also reported.

For example, if the mean IS difference is defined as "Candidate A − Candidate B," a negative value favors A on the point estimate. If the approximate 95% confidence interval spans 0, we will describe the difference as not clearly distinguishable, rather than as evidence of equivalence.

Simple pairwise confidence intervals calculated after selecting the minimum across many comparisons cannot establish that a candidate is uniquely best among the 16 combinations. The aim is to report differences and uncertainty for prespecified comparisons, rather than use p-values to certify a ranking of every candidate. A confirmatory claim about the best method would require a separate design that addresses multiple comparisons and selection effects.

These intervals describe uncertainty in evaluation metrics conditional on the fitted forecasts and intervals. They do not represent uncertainty in the full training process, since models are not refitted within each bootstrap sample. Given nonstationarity in financial time series and the concentration of observations in a few crises, stable results for block lengths of 5, 10, and 20 do not establish strict validity.

## 7. Implementation Order and Completion Criteria

As in the existing implementation, the main analysis will follow a readable sequence from loading to calculation to saving, using short Japanese comments and a small number of short functions. We will not introduce classes, broad try/except blocks, or excessive abstraction. Checks important to the research, including temporal ordering, missing values, and reproducibility, will be retained, with validation code kept separate from the main analysis.

| Stage | Task | Completion criteria |
| --- | --- | --- |
| 1 | Preserve v0.1 and the raw data; prepare a working copy for v0.2 | Save reference code, results, and raw data, and record their hashes |
| 2 | Add the 4 models, 4 interval methods, and predictors to `settings.py` and `01_prepare_data.py` | All predictors use information only through t−1; existing training, calibration, and test dates and counts are preserved |
| 3 | Add multiple regression to `02_fit_models.py` | Fit using training data only; save point forecasts, errors, and coefficients for all 4 models |
| 4 | Add Rolling Normal to `intervals.py` and `03_build_intervals.py` | Save all 16 interval combinations, reference histories, error means and standard deviations, and related information |
| 5 | Add the explicit evaluation criteria and assessment rules to `04_evaluate.py` | Save summaries by market regime with 12 point forecast rows and 48 interval rows, target attainment, and IS rankings |
| 6 | Add a short, separate script for bootstrap evaluation | Save CIs for paired metric differences, block-length sensitivity results, and execution settings |
| 7 | Update `05_make_figures.py`, the research design, README, and results report | Create a 4×4 comparison figure, a coverage–width figure, and figures showing differences and CIs for the main comparisons |
| 8 | Verify reproducibility and temporal ordering | Pass the key checks below and save the verification results |

Key checks:

- Reproduce the 9 existing combinations of 3 models × 3 interval methods. The former Normal method is renamed Fixed Normal without changing its calculated values. The former Fixed and Rolling methods are also mapped to names that explicitly identify them as CP.
- Confirm that point forecasts, daily intervals, and summaries for the existing models match the saved v0.1 results within numerical tolerance.
- On the first test day, confirm that the half-widths satisfy Fixed CP = Rolling CP and Fixed Normal = Rolling Normal for each model.
- Confirm that changing realized errors on or after a given date does not change interval widths on or before that date.
- Confirm that Rolling CP and Rolling Normal use histories with the same start dates, end dates, and observation counts.
- Confirm that all 4 models × 4 interval methods are available for every one of the 1,715 days, with no duplicates, missing values, or reversed interval bounds.
- Ensure that point forecast evaluation does not count duplicate rows arising from the 4 interval methods.
- Verify the interval score using simple numerical examples with an observation inside the interval, below the lower bound, and above the upper bound.
- Confirm that the bootstrap uses the same sampled date indices for every method and recalculates regime-specific denominators in every replication.

The main additional outputs will be predictor definitions, multiple regression coefficients, daily intervals for the 16 combinations, point forecast evaluations for the 4 models, interval evaluations for the 16 combinations, target attainment, bootstrap differences and CIs, figures, a results report, and verification records. Coefficient and results tables will be extended only as needed.

## 8. Scope of Conclusions and Future Research

Some results from the current test period have already been inspected, so this comparison is a descriptive and exploratory evaluation of historical data. Prespecifying the evaluation rules now remains useful, but a previously examined period cannot become a completely untouched test set again.

Conclusions will describe which combinations performed well under which market conditions, within the study period, candidate set, and evaluation criteria. We will not claim future optimality or guaranteed 90% coverage in future periods.

Standard conformal coverage guarantees require conditions such as exchangeability, which do not automatically hold for financial time series or VIX-defined subgroups. Switching to a rolling history alone does not guarantee conditional coverage.[2]

RQ4, which changes the proportion of high-VIX observations in training and calibration and the window length, will be planned separately after the basic comparison of 16 combinations is complete. We will avoid selecting one combination from these results, optimizing the period settings on the same test set, and reporting the resulting minimum as performance on untouched data. To evaluate future method selection, we will use time-ordered validation for selection and a final evaluation on a new, previously unexamined period.

## References

[1] Gneiting, T. & Raftery, A. E. (2007). *Strictly Proper Scoring Rules, Prediction, and Estimation*. Journal of the American Statistical Association, 102(477), 359–378. See especially Section 6.2 and equation (43) for the definition of the interval score and its role in evaluation.\
https://sites.stat.washington.edu/people/raftery/Research/PDF/Gneiting2007jasa.pdf

[2] Barber, R. F., Candès, E. J., Ramdas, A. & Tibshirani, R. J. (2023). *Conformal Prediction Beyond Exchangeability*. Annals of Statistics, 51(2), 816–845. Discusses the interpretation of coverage under exchangeability and distribution shift.\
https://www.stat.cmu.edu/~ryantibs/papers/nexcp.pdf

The 4 predictors, 5-day and 20-day windows, labels for attainment of the 90% target, and bootstrap settings are proposals in this plan. The cited papers do not establish that these choices are optimal for this study.
