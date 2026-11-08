# Results for the 16 Combinations v0.2

We compared 4 models × 4 interval methods using the same SP500.csv and VIXCLS.csv files.
The training period was 2017–2018 (502 days), calibration covered 2019 (252 days), and the test period ran from 2020-01-02 to 2026-10-28 (1,715 days).
There were 149 high-VIX days, defined by a VIX value of at least 30 on the previous trading day, and 1,566 lower-VIX days. Nominal interval coverage was 90%, and the rolling window was 252 trading days.

## Evaluation Criteria

RMSE is the primary metric for point forecasts, with MAE as a secondary metric. Prediction intervals are evaluated by mean interval score (IS), where lower is better; whether empirical coverage reaches 90% is reported separately.
Narrower intervals alone are not considered better. If no candidate meets the coverage target, we do not conclude that a suitable combination has been found for that regime.
All rankings below are based on point estimates for the observed study period.

## Point Forecasts

| Regime | Model | Days | MAE | RMSE |
| --- | --- | --- | --- | --- |
| Full test period | Random Walk | 1715 | 0.831254 | 1.271564 |
| Full test period | Historical Mean | 1715 | 0.829672 | 1.270860 |
| Full test period | AR(1) | 1715 | 0.828941 | 1.268045 |
| Full test period | Multiple Regression | 1715 | 0.830602 | 1.277232 |
| High VIX | Random Walk | 149 | 2.095387 | 2.946440 |
| High VIX | Historical Mean | 149 | 2.094027 | 2.945210 |
| High VIX | AR(1) | 149 | 2.084231 | 2.930794 |
| High VIX | Multiple Regression | 149 | 2.094528 | 2.956612 |
| Lower VIX | Random Walk | 1566 | 0.710975 | 0.971955 |
| Lower VIX | Historical Mean | 1566 | 0.709372 | 0.971302 |
| Lower VIX | AR(1) | 1566 | 0.709504 | 0.971422 |
| Lower VIX | Multiple Regression | 1566 | 0.710344 | 0.977141 |

Multiple regression used the previous day's return, the cumulative return over the previous 5 days, realized volatility over the previous 20 days, and the previous day's VIX. Its RMSE point estimate was higher than that of AR(1).
The results did not show an improvement from adding predictors. Neither predictors nor time periods were reselected to fit the performance observed on this test set.

## Candidate Combinations by Market Regime

| Regime | Criterion | Combination | Coverage | Mean width | Mean IS |
| --- | --- | --- | --- | --- | --- |
| Full test period | Lowest IS among all candidates | Random Walk + Rolling CP | 90.32% | 3.701477 | 5.921426 |
| Full test period | Lowest IS among candidates with coverage ≥ 90% | Random Walk + Rolling CP | 90.32% | 3.701477 | 5.921426 |
| High VIX | Lowest IS among all candidates | AR(1) + Rolling Normal | 68.46% | 5.096894 | 17.748680 |
| High VIX | Lowest IS among candidates with coverage ≥ 90% | None | — | — | — |
| Lower VIX | Lowest IS among all candidates | Random Walk + Fixed Normal | 84.93% | 2.586589 | 4.468677 |
| Lower VIX | Lowest IS among candidates with coverage ≥ 90% | Random Walk + Rolling CP | 92.66% | 3.619644 | 4.632523 |

Over the full test period, Random Walk + Rolling CP had the lowest IS and a coverage point estimate above 90%. However, differences from the other baseline models were small, so this does not establish that the combination was uniquely superior in statistical terms.

All 16 combinations fell short of the target on high-VIX days. Although AR(1) + Rolling Normal had the lowest IS, it did not achieve 90% coverage.

On lower-VIX days, Random Walk + Fixed Normal had the lowest IS, but its coverage was below 90%. Among candidates that met the coverage target, Random Walk + Rolling CP had the lowest IS.
This illustrates why the lowest IS and attainment of the coverage target must be reported separately. No candidate met the target in both market regimes.

## Detailed Results for All 16 Combinations

### Full Test Period

| Model | Interval method | Coverage | Mean width | Mean IS | 90% target |
| --- | --- | --- | --- | --- | --- |
| Random Walk | Fixed CP | 80.17% | 2.466826 | 6.289311 | Not met |
| Random Walk | Rolling CP | 90.32% | 3.701477 | 5.921426 | Met |
| Random Walk | Fixed Normal | 81.05% | 2.586589 | 6.177919 | Not met |
| Random Walk | Rolling Normal | 90.20% | 3.909079 | 5.935124 | Met |
| Historical Mean | Fixed CP | 79.88% | 2.476438 | 6.278800 | Not met |
| Historical Mean | Rolling CP | 90.20% | 3.701975 | 5.928477 | Met |
| Historical Mean | Fixed Normal | 81.22% | 2.586589 | 6.176570 | Not met |
| Historical Mean | Rolling Normal | 90.26% | 3.909079 | 5.940344 | Met |
| AR(1) | Fixed CP | 79.83% | 2.470476 | 6.269168 | Not met |
| AR(1) | Rolling CP | 90.26% | 3.713128 | 5.922937 | Met |
| AR(1) | Fixed Normal | 81.22% | 2.583511 | 6.164155 | Not met |
| AR(1) | Rolling Normal | 90.20% | 3.902939 | 5.926368 | Met |
| Multiple Regression | Fixed CP | 80.06% | 2.475176 | 6.334861 | Not met |
| Multiple Regression | Rolling CP | 89.74% | 3.738174 | 5.991448 | Not met |
| Multiple Regression | Fixed Normal | 81.92% | 2.630495 | 6.194767 | Not met |
| Multiple Regression | Rolling Normal | 89.62% | 3.923518 | 5.993490 | Not met |

### High VIX

| Model | Interval method | Coverage | Mean width | Mean IS | 90% target |
| --- | --- | --- | --- | --- | --- |
| Random Walk | Fixed CP | 40.27% | 2.466826 | 24.737768 | Not met |
| Random Walk | Rolling CP | 65.77% | 4.561544 | 19.467884 | Not met |
| Random Walk | Fixed Normal | 40.27% | 2.586589 | 24.142169 | Not met |
| Random Walk | Rolling Normal | 67.79% | 5.113824 | 17.892160 | Not met |
| Historical Mean | Fixed CP | 39.60% | 2.476438 | 24.645242 | Not met |
| Historical Mean | Rolling CP | 66.44% | 4.566420 | 19.449670 | Not met |
| Historical Mean | Fixed Normal | 40.94% | 2.586589 | 24.099259 | Not met |
| Historical Mean | Rolling Normal | 68.46% | 5.113824 | 17.875396 | Not met |
| AR(1) | Fixed CP | 40.27% | 2.470476 | 24.502179 | Not met |
| AR(1) | Rolling CP | 66.44% | 4.587146 | 19.320287 | Not met |
| AR(1) | Fixed Normal | 40.94% | 2.583511 | 23.945380 | Not met |
| AR(1) | Rolling Normal | 68.46% | 5.096894 | 17.748680 | Not met |
| Multiple Regression | Fixed CP | 42.28% | 2.475176 | 24.711581 | Not met |
| Multiple Regression | Rolling CP | 65.10% | 4.599218 | 19.476847 | Not met |
| Multiple Regression | Fixed Normal | 45.64% | 2.630495 | 23.983958 | Not met |
| Multiple Regression | Rolling Normal | 67.11% | 5.138795 | 17.873360 | Not met |

### Lower VIX

| Model | Interval method | Coverage | Mean width | Mean IS | 90% target |
| --- | --- | --- | --- | --- | --- |
| Random Walk | Fixed CP | 83.97% | 2.466826 | 4.533998 | Not met |
| Random Walk | Rolling CP | 92.66% | 3.619644 | 4.632523 | Met |
| Random Walk | Fixed Normal | 84.93% | 2.586589 | 4.468677 | Not met |
| Random Walk | Rolling Normal | 92.34% | 3.794451 | 4.797449 | Met |
| Historical Mean | Fixed CP | 83.72% | 2.476438 | 4.531291 | Not met |
| Historical Mean | Rolling CP | 92.46% | 3.619725 | 4.641978 | Met |
| Historical Mean | Fixed Normal | 85.06% | 2.586589 | 4.471282 | Not met |
| Historical Mean | Rolling Normal | 92.34% | 3.794451 | 4.804761 | Met |
| AR(1) | Fixed CP | 83.59% | 2.470476 | 4.534354 | Not met |
| AR(1) | Rolling CP | 92.53% | 3.629968 | 4.648221 | Met |
| AR(1) | Fixed Normal | 85.06% | 2.583511 | 4.472327 | Not met |
| AR(1) | Rolling Normal | 92.27% | 3.789338 | 4.801512 | Met |
| Multiple Regression | Fixed CP | 83.65% | 2.475176 | 4.586374 | Not met |
| Multiple Regression | Rolling CP | 92.08% | 3.656248 | 4.708354 | Met |
| Multiple Regression | Fixed Normal | 85.38% | 2.630495 | 4.502181 | Not met |
| Multiple Regression | Rolling Normal | 91.76% | 3.807888 | 4.863157 | Met |

## Uncertainty in Differences

We used a paired moving block bootstrap with a primary block length of 10 days and sensitivity analyses at 5 and 20 days, with 5,000 replications for each. Contiguous, non-circular blocks were sampled from the full test series, and the same sampled date indices were applied to every method.
VIX regime labels were resampled with the observations, and metrics were then calculated separately by regime. Models were not refitted in the bootstrap. The intervals below are pointwise approximate 95% confidence intervals from the percentile method under the primary setting.

Differences are defined as Multiple Regression − AR(1). A positive RMSE difference indicates a larger error for multiple regression.

| Regime | RMSE difference | Approximate 95% CI |
| --- | --- | --- |
| Full test period | 0.009187 | [-0.001628, 0.022114] |
| High VIX | 0.025818 | [-0.028358, 0.083215] |
| Lower VIX | 0.005719 | [-0.000937, 0.012453] |

All CIs span 0, so the RMSE differences between multiple regression and AR(1) are not clearly distinguishable. This does not establish equivalence.

The following table compares interval methods for the same AR(1) model. A negative IS difference means that A has the better point estimate.

| Regime | Comparison A−B | Mean IS difference | Approximate 95% CI |
| --- | --- | --- | --- |
| Full test period | Fixed CP − Fixed Normal | 0.105013 | [0.073547, 0.140220] |
| Full test period | Rolling CP − Rolling Normal | -0.003431 | [-0.167525, 0.220310] |
| Full test period | Rolling CP − Fixed CP | -0.346231 | [-0.695803, -0.014911] |
| Full test period | Rolling Normal − Fixed Normal | -0.237787 | [-0.691218, 0.164466] |
| High VIX | Fixed CP − Fixed Normal | 0.556799 | [0.445635, 0.665154] |
| High VIX | Rolling CP − Rolling Normal | 1.571607 | [-0.149914, 3.688263] |
| High VIX | Rolling CP − Fixed CP | -5.181892 | [-6.977649, -3.416559] |
| High VIX | Rolling Normal − Fixed Normal | -6.196700 | [-9.072691, -3.435430] |
| Lower VIX | Fixed CP − Fixed Normal | 0.062027 | [0.036967, 0.089549] |
| Lower VIX | Rolling CP − Rolling Normal | -0.153291 | [-0.207032, -0.104428] |
| Lower VIX | Rolling CP − Fixed CP | 0.113867 | [-0.110561, 0.344512] |
| Lower VIX | Rolling Normal − Fixed Normal | 0.329185 | [0.094642, 0.577372] |

### Sensitivity to Block Length

For AR(1), we compare the mean IS difference (Rolling CP − Fixed CP) over the full test period using different block lengths.

| Block length | Mean IS difference | Approximate 95% CI |
| --- | --- | --- |
| 5 | -0.346231 | [-0.632885, -0.084221] |
| 10 | -0.346231 | [-0.695803, -0.014911] |
| 20 | -0.346231 | [-0.811268, 0.057377] |

With a block length of 20, the CI spans 0, whereas the CIs for lengths of 5 and 10 exclude 0. The improvement in the point estimate alone does not establish that the conclusion is insensitive to block length.

All comparisons and block-length sensitivity results are saved in `outputs/evaluation/bootstrap/paired_differences.csv`.
These are pointwise CIs for multiple comparisons, without a multiplicity adjustment. Simple CIs calculated after selecting the minimum do not establish that a candidate is uniquely best among the 16 combinations.

## Scope of Interpretation

- Normal methods use a normal approximation with the mean error approximated as 0; they are not exact finite-sample regression prediction intervals. Standard deviations use ddof=1, with no adjustment to the center for the mean error or to the interval for coefficient estimation uncertainty.
- The conditions for standard conformal guarantees are not assumed to hold automatically for financial time series. We also make no claim of guaranteed 90% coverage within each VIX regime.
- Bootstrap CIs may be affected by nonstationarity and the concentration of observations in a few crises. Examining sensitivity to block length does not establish their validity.
- Some test-period results had already been inspected, so this comparison is descriptive and exploratory. It does not identify a definitive optimal method for the future.
- RQ4, which varies the proportion of high-VIX observations in training and calibration and the window length, was not carried out in this analysis.

## Figures and Supporting Files

- `outputs/figures/sixteen_combinations.png`: Coverage, width, and IS for 16 combinations across 3 evaluation groups.
- `outputs/figures/coverage_width.png`: Relationship between mean width and coverage.
- `outputs/figures/paired_is_differences.png`: IS differences and CIs for the 20 prespecified comparisons.
- `outputs/figures/point_accuracy.png`: MAE and RMSE for the 4 models.
- `outputs/figures/ar1_width_and_coverage.png`: AR(1) interval width and 126-day coverage over time.
- `validation/verification.json`: Verification records covering reproduction of the 9 existing combinations, raw-data consistency, temporal ordering, and related checks.

MAE, RMSE, interval width, and IS are measured in percentage points of return. Coverage is stored on a 0–1 scale in CSV files and shown as a percentage in the text and figures.
