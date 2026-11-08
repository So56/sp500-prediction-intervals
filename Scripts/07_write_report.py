import pandas as pd

from settings import GROUPS, METHODS, MODELS, project_dir


evaluation_dir = project_dir / "outputs" / "evaluation"
points = pd.read_csv(evaluation_dir / "point_summary.csv")
summary = pd.read_csv(evaluation_dir / "interval_summary.csv")
selection = pd.read_csv(evaluation_dir / "selection_summary.csv")
differences = pd.read_csv(evaluation_dir / "bootstrap/paired_differences.csv")
main = differences.loc[differences["block_length"] == 10]
labels = dict(zip(MODELS, ["Random Walk", "Historical Mean", "AR(1)", "重回帰"]))
methods = dict(zip(METHODS, ["Fixed CP", "Rolling CP", "Fixed Normal", "Rolling Normal"]))
groups = dict(zip(GROUPS, ["全Test", "高VIX", "非高VIX"]))


def markdown_table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    lines += ["| " + " | ".join(map(str, row)) + " |" for row in rows]
    return "\n".join(lines)


sections = ["""# 16通りの比較結果 v0.2

同じSP500.csv・VIXCLS.csvを用いて、4モデル×4区間法を比較した。
Trainingは2017–2018年（502日）、Calibrationは2019年（252日）、Testは2020-01-02〜2026-10-28（1,715日）。
高VIXは前営業日のVIXが30以上の149日、非高VIXは1,566日。区間の名目Coverageは90%、Rolling Windowは252営業日。

## 評価基準

点予測はRMSEを主指標、MAEを補助指標とする。予測区間は平均Interval Score（IS）が小さいほど良いとし、経験的Coverageが90%以上かを別に表示する。
幅が狭いだけでは良いと判定しない。目標到達候補がない場合は、その区分に適切な組み合わせが見つかったとは結論しない。
以下の順位は、この観測期間内での点推定による順位である。

## 点予測
"""]
rows = []
for group in GROUPS:
    for model in MODELS:
        row = points.loc[(points["group"] == group) & (points["model"] == model)].iloc[0]
        rows.append([groups[group], labels[model], int(row["n"]), f'{row["mae"]:.6f}', f'{row["rmse"]:.6f}'])
sections.append(markdown_table(["区分", "モデル", "日数", "MAE", "RMSE"], rows))
sections.append("""
今回の重回帰は、前日リターン・直近5日累積リターン・直近20日実現ボラティリティ・前日のVIXを使ったが、RMSEの点推定はAR(1)より大きかった。
重回帰に説明変数を加えれば改善する、という結果にはならなかった。変数や期間をこのTestの成績に合わせて選び直していない。

## 市場区分ごとの候補
""")
rows = []
for row in selection.itertuples():
    scope = "全候補の最小IS" if row.scope == "all_candidates" else "Coverage 90%以上の最小IS"
    if row.candidate_n:
        rows.append([groups[row.group], scope, labels[row.model] + " ＋ " + methods[row.method],
                     f"{100 * row.coverage:.2f}%", f"{row.width:.6f}", f"{row.interval_score:.6f}"])
    else:
        rows.append([groups[row.group], scope, "該当なし", "—", "—", "—"])
sections.append(markdown_table(["区分", "基準", "組み合わせ", "Coverage", "平均幅", "平均IS"], rows))
sections.append("""
全TestではRandom Walk＋Rolling CPのISが最小で、Coverageも点推定では90%以上だった。ただし他の基準モデルとの差は小さく、一意の統計的優位性を示したとは言わない。

高VIXでは全16通りが目標未達だった。AR(1)＋Rolling NormalのISが最小でも、その組み合わせが90%の信頼性を達成したとは解釈できない。

非高VIXではRandom Walk＋Fixed NormalのISが最小だったがCoverageは90%未満だった。目標到達候補に限定するとRandom Walk＋Rolling CPが最小ISとなった。
これは「ISが最小」と「Coverage目標を満たす」を分ける必要を示している。両市場区分で目標を満たす候補はなかった。

## 16通りの数値
""")
for group in GROUPS:
    rows = []
    for model in MODELS:
        for method in METHODS:
            row = summary.loc[(summary["group"] == group) & (summary["model"] == model)
                              & (summary["method"] == method)].iloc[0]
            rows.append([labels[model], methods[method], f'{100 * row["coverage"]:.2f}%',
                         f'{row["width"]:.6f}', f'{row["interval_score"]:.6f}',
                         "到達" if row["target_reached"] else "未達"])
    sections.append("\n### " + groups[group] + "\n")
    sections.append(markdown_table(["モデル", "区間法", "Coverage", "平均幅", "平均IS", "90%目標"], rows))

sections.append("""
## 差の不確実性

paired moving block bootstrapを実施した。主Block長は10、感度分析は5・20で、各5,000回。非循環の連続ブロックを全Test時系列から抽出し、同じ日付indexを全手法に適用した。
高VIX区分も一緒に抽出してから区分別に集計した。モデルを再学習するBootstrapではない。以下は主設定のpercentile法による、点ごとの近似95%信頼区間である。

差は重回帰−AR(1)。RMSE差が正なら重回帰の誤差が大きい。
""")
rows = []
part = main.loc[(main["comparison"] == "multiple_vs_ar1") & (main["metric"] == "rmse")]
for row in part.itertuples():
    rows.append([groups[row.group], f"{row.difference_a_minus_b:.6f}", f"[{row.ci_lower:.6f}, {row.ci_upper:.6f}]"])
sections.append(markdown_table(["区分", "RMSE差", "近似95%CI"], rows))
sections.append("""
いずれも0をまたぐため、重回帰とAR(1)のRMSE差を明確に識別できない。同等性が証明されたという意味ではない。

区間法の違いは、同じAR(1)について次のようになった。IS差が負ならAの点推定が良い。
""")
rows = []
part = main.loc[(main["metric"] == "interval_score") & (main["model_a"] == "ar1")
                & (main["model_b"] == "ar1")]
for row in part.itertuples():
    rows.append([groups[row.group], methods[row.method_a] + " − " + methods[row.method_b],
                 f"{row.difference_a_minus_b:.6f}", f"[{row.ci_lower:.6f}, {row.ci_upper:.6f}]"])
sections.append(markdown_table(["区分", "比較A−B", "平均IS差", "近似95%CI"], rows))
sections.append("\n### Block長の感度\n\nAR(1)のRolling CP−Fixed CPについて、全Testの平均IS差を比較する。")
rows = []
part = differences.loc[(differences["group"] == "overall") & (differences["metric"] == "interval_score")
                       & (differences["comparison"] == "cp_update") & (differences["model_a"] == "ar1")]
for row in part.sort_values("block_length").itertuples():
    rows.append([row.block_length, f"{row.difference_a_minus_b:.6f}", f"[{row.ci_lower:.6f}, {row.ci_upper:.6f}]"])
sections.append(markdown_table(["Block長", "平均IS差", "近似95%CI"], rows))
sections.append("\nBlock長20ではCIが0をまたぎ、5・10とは0の包含について異なる結果となった。"
                "点推定の改善だけから、結論がBlock長に依存しないとは言わない。")
sections.append("""
全比較とBlock長感度は `outputs/evaluation/bootstrap/paired_differences.csv` に保存した。
多数の比較の点ごとのCIであり、多重比較の補正はしていない。最小値を選んだ後の単純なCIから、16候補中で一意に最良とは主張しない。

## 解釈の範囲

- Normalは誤差平均を0と近似した正規近似区間であり、厳密な有限標本の回帰予測区間ではない。標準偏差はddof=1で計算し、誤差平均による中心補正や係数推定不確実性の補正は行っていない。
- 通常のConformalの保証条件が金融時系列で自動的に成立するとは扱わず、VIX別の90%Coverage保証も主張しない。
- BootstrapのCIは、非定常性や一部の危機への集中の影響を受け得る。Block長感度を確認しても、その妥当性が証明されたとは扱わない。
- Test期間の結果は既に一部見ているため、今回の比較は記述的・探索的評価である。将来の最適手法を確定した結果ではない。
- Training・Calibrationの高VIX割合やWindowを変えるRQ4は、今回実行していない。

## 図と確認先

- `outputs/figures/sixteen_combinations.png`：16通り×3市場区分のCoverage・幅・IS。
- `outputs/figures/coverage_width.png`：平均幅とCoverageの関係。
- `outputs/figures/paired_is_differences.png`：事前指定20比較のIS差とCI。
- `outputs/figures/point_accuracy.png`：4モデルのMAE・RMSE。
- `outputs/figures/ar1_width_and_coverage.png`：AR(1)の幅と126日Coverageの推移。
- `validation/verification.json`：既存9通りの再現、原データ一致、時間順序等の検証記録。

MAE・RMSE・区間幅・ISはリターンのパーセントポイントを単位とする。CSVのCoverageは0〜1、本文と図では%で示した。
""")
report = project_dir / "reports" / "results_v0_2.md"
report.write_text("\n\n".join(sections) + "\n", encoding="utf-8")
print("結果説明を保存しました。")
