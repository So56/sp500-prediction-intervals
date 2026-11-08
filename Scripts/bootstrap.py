import math

import numpy as np


def draw_block_indices(n, block_length, rng):
    # 最後の日から最初の日へはつなげず、連続したブロックを抽出する。
    starts = rng.integers(0, n - block_length + 1, size=math.ceil(n / block_length))
    return (starts[:, None] + np.arange(block_length)).ravel()[:n]


def sample_statistics(values, group_masks, indices, rmse_columns):
    # 同じ日付の抽出回数を、すべてのモデルと区間法に適用する。
    counts = np.bincount(indices, minlength=len(values))
    weights = counts[:, None] * group_masks
    group_n = weights.sum(axis=0)
    totals = weights.T @ values
    means = np.divide(totals, group_n[:, None],
                      out=np.full_like(totals, np.nan), where=group_n[:, None] > 0)
    means[:, rmse_columns] = np.sqrt(means[:, rmse_columns])
    return means, group_n
