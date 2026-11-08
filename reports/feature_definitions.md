# Predictors for Multiple Regression

Let t denote the forecast date. Only information available after the close of the previous trading day is used.
The target variable is `return_pct = 100 × log(P_t / P_(t-1))`.

| CSV column | Definition | Calculation | Purpose |
| --- | --- | --- | --- |
| return_lag1_pct | r_(t-1) | return_pct.shift(1) | Capture persistence or reversal in the previous day's return |
| return_5d_lag1_pct | r_(t-5)+...+r_(t-1) | return_pct.shift(1).rolling(5).sum() | Capture price movements over several days |
| volatility_20d_lag1 | Sample standard deviation of r_(t-20) through r_(t-1) | return_pct.shift(1).rolling(20).std(ddof=1) | Measure the magnitude of recent realized price movements |
| vix_lag1 | VIX_(t-1) | vix_close.shift(1) | Add a measure of uncertainty derived from the options market |

Rolling features are calculated from the historical raw data before the training split is applied. Features for the first training observations in 2017 use historical data from 2016, but only target observations from 2017–2018 are used to estimate the coefficients.
The five-day cumulative return is the sum of daily log returns, rather than simple returns. The 20-day standard deviation retains the units of daily returns and is not annualized.
The 5-day and 20-day windows are prespecified initial choices; no claim is made that they are optimal.

The model is fitted by ordinary least squares (OLS), with an intercept, using the training data only. The same coefficients are used for calibration and testing. Features are used without standardization. Because the predictors have different units, coefficient magnitudes alone should not be used to compare their importance.
The previous day's return may be correlated with the five-day cumulative return, and VIX may be correlated with realized volatility. Training correlations and summary statistics are saved in `outputs/modeling`.
VIX and realized volatility provide information about the magnitude of price movements, but may not improve forecasts of mean returns.
Adding multiple regression allows us to assess the value of using more information within the same OLS framework. Individual coefficients are not interpreted as causal effects.
