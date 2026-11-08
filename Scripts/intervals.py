import math

import numpy as np


def interval_scores(lower, upper, actual, alpha):
    # 幅に加え、区間を外れたときの距離を評価する。
    return (upper - lower + (2 / alpha) * np.maximum(lower - actual, 0)
            + (2 / alpha) * np.maximum(actual - upper, 0))


def conformal_halfwidth(scores, alpha):
    # 補間せず、有限標本補正を含む順位のスコアを選ぶ。
    k = math.ceil((len(scores) + 1) * (1 - alpha))
    if k > len(scores):
        return np.inf
    return np.sort(scores)[k - 1]


def rolling_halfwidths(calibration_scores, test_scores, window, alpha):
    history = list(calibration_scores)
    widths = []
    for score in test_scores:
        # 当日の誤差を追加する前に、過去の誤差だけで幅を決める。
        widths.append(conformal_halfwidth(history[-window:], alpha))
        history.append(score)
    return np.array(widths)


def rolling_normal_stats(calibration_errors, test_errors, window):
    history = list(calibration_errors)
    means = []
    sigmas = []
    for error in test_errors:
        # 当日の誤差を追加する前に、過去252日の平均と標準偏差を求める。
        past = history[-window:]
        means.append(np.mean(past))
        sigmas.append(np.std(past, ddof=1))
        history.append(error)
    return np.array(means), np.array(sigmas)
