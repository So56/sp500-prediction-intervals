# Research Design v0.2: 4 Models × 4 Interval Methods

## Objective and Research Questions

Using daily S&P 500 log returns, we compare forecasting models, interval construction methods, and approaches to updating the error history across the full test period, high-VIX days, and lower-VIX days.

- RQ1: How does the point forecast accuracy of the four models vary by market regime?
- RQ2: How do the 16 interval combinations differ in coverage, width, and interval score?
- RQ3: How do the differences between Fixed and Rolling methods, and between CP and Normal methods, vary by market regime?

Any use of "optimal" is limited to the study period, candidate methods, and prespecified evaluation criteria. We make no claim of universal optimality for future periods.

## Forecast Timing and Data

After the close of the previous trading day, we forecast the return through the close of the current trading day.
The target is `r_t = 100 × log(P_t / P_(t-1))`; predictors and VIX regime labels use only information available through t−1.
We use the original SP500.csv and VIXCLS.csv files without modifying them or obtaining additional data.
The training period is 2017–2018, calibration covers 2019, and the test period runs from 2020-01-02 to 2026-10-28.
All fitted model parameters are held fixed after training, and all methods are compared on the same 1,715 test days.

High VIX is defined as `VIX_(t-1) >= 30`, and lower VIX as a value below 30. There are 5 high-VIX days in training, 0 in calibration, and 149 in testing.

## Point Forecast Models

| Model | Forecast |
| --- | --- |
| Random Walk | `r_hat_t = 0`, corresponding to a random walk in log prices without drift |
| Historical Mean | Mean return over the training period |
| AR(1) | `beta0 + beta1 × r_(t-1)` |
| Multiple Regression | `beta0 + beta1 × lag1 + beta2 × return5 + beta3 × vol20 + beta4 × vix_lag1` |

Multiple regression is estimated by OLS with an intercept. The predictor return5 is the sum of returns from t−5 through t−1, and vol20 is the sample standard deviation of returns from t−20 through t−1 (ddof=1).
The 5-day and 20-day windows are prespecified as interpretable initial choices and are not adjusted in response to the results.
Correlations and coefficients are recorded, but predictors are not reselected based on test performance or p-values. Coefficients, including those on VIX, are not interpreted as causal effects.
Multiple regression forecasts the mean return; adding volatility as a predictor does not directly change the interval width.

## Interval Methods: Construction and History Updates

For each model, the signed forecast error is `e_t = r_t - r_hat_t`.

| Interval method | Error history | Half-width |
| --- | --- | --- |
| Fixed CP | All of 2019 | Absolute error at rank `ceil((n+1)×0.90)` in ascending order |
| Rolling CP | The most recent 252 days before the forecast date | The same order statistic with a finite-sample correction |
| Fixed Normal | All of 2019 | `z_0.95 × sd(e)` |
| Rolling Normal | The most recent 252 days before the forecast date | `z_0.95 × sd(e)` |

All intervals are centered on the corresponding model's point forecast. Normal methods use ddof=1 and a z-value of approximately 1.644854.
The center is not adjusted for the mean error; the mean and standard deviation of the error history are saved.
These are normal-approximation intervals based on an approximately zero mean error, rather than exact finite-sample regression prediction intervals that account for coefficient uncertainty and related factors. The standard deviation is not divided by sqrt(n), as it would be for a confidence interval for a mean.

Rolling methods add the current day's realized error to the history only after issuing that day's interval. CP and Normal methods use the same 252 days.
Comparisons within Fixed or within Rolling isolate differences in interval construction, while Fixed versus Rolling comparisons within the same construction method assess history updates.
Differences between CP and Normal reflect assumptions such as the zero mean approximation as well as distributional shape.

## Evaluation Criteria

RMSE is the primary metric for point forecasts, with MAE as a secondary metric. For intervals, the primary metric is the interval score (IS) defined below.[1]

`IS = (U-L) + (2/alpha)×max(L-r,0) + (2/alpha)×max(r-U,0)`

We set alpha=0.10; a lower mean IS is better. Coverage, mean width, and the proportions of observations falling below and above the interval are also reported.
We distinguish the lowest IS among all candidates from the lowest IS among candidates with empirical coverage of at least 90%.
If no candidate satisfies the latter criterion, we report "No candidate meets the target." The 90% threshold is a descriptive criterion applied to point estimates, rather than a guarantee of future coverage or a certification standard.
The full test period, high-VIX days, and lower-VIX days are evaluated separately; no aggregate score combines these overlapping groups.

## Uncertainty in Differences

We use the percentile method with a paired, non-circular moving block bootstrap to estimate pointwise approximate 95% confidence intervals (CIs).
The primary block length is 10 days, with sensitivity analyses at 5 and 20 days and 5,000 replications for each. PCG64 is initialized with seed=202701 for each block length.
Contiguous blocks are sampled from the full test series, and the concatenated sample is truncated to the first 1,715 days. The same sampled date indices are applied to every method and to the VIX regime labels.
Regime-specific denominators are recalculated in each sample; high-VIX days are not sampled independently.
We record the SHA-256 hash of the sampled indices, excerpts of the indices from the first 3 replications, the range of day counts in each regime, and the number of replications with 0 days in a regime.

For point forecasts, the primary comparison is Multiple Regression − AR(1); differences relative to the two baseline models are also saved.
For intervals, we compare Multiple Regression − AR(1) under each interval method, and Fixed CP − Fixed Normal, Rolling CP − Rolling Normal, Rolling CP − Fixed CP, and Rolling Normal − Fixed Normal for each model.
Differences are defined as A−B. A negative difference in RMSE, MAE, width, or IS means that A has a lower value. The sign of a coverage difference indicates an increase or decrease in coverage and does not, by itself, indicate better or worse performance.
When a CI spans 0, we describe the difference as not clearly distinguishable; this does not establish equivalence.
No adjustment is made for multiple comparisons, and these CIs are not intended to establish that a selected method is uniquely best.

The bootstrap resamples daily evaluations of the fitted forecasts and intervals. It does not capture uncertainty in the full procedure, including model refitting.
Given nonstationarity in financial time series and the concentration of high-VIX observations in a few crises, stable results across block lengths do not establish the validity of the CIs.

## Scope of Conclusions and Next Steps

Standard conformal coverage guarantees require conditions such as exchangeability, which are not assumed to hold automatically for financial time series. Simply using a rolling history does not guarantee 90% coverage within each VIX regime.[2]
Some results from this test period have already been inspected, so this comparison is descriptive and exploratory.
RQ4, which varies the proportion and timing of high-VIX observations in training and calibration and the window length, has not been carried out. Subsequent parameter selection will require time-ordered validation and a final evaluation on a new, previously unexamined period.

## References

[1] Gneiting, T. & Raftery, A. E. (2007). Strictly Proper Scoring Rules, Prediction, and Estimation. JASA, 102(477), 359–378. Section 6.2, equation (43).\
https://sites.stat.washington.edu/people/raftery/Research/PDF/Gneiting2007jasa.pdf

[2] Barber, R. F., Candès, E. J., Ramdas, A. & Tibshirani, R. J. (2023). Conformal Prediction Beyond Exchangeability. Annals of Statistics, 51(2), 816–845.\
https://www.stat.cmu.edu/~ryantibs/papers/nexcp.pdf
