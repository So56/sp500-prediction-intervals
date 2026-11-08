# 16通りの比較結果 v0.2

同じSP500.csv・VIXCLS.csvを用いて、4モデル×4区間法を比較した。
Trainingは2017–2018年（502日）、Calibrationは2019年（252日）、Testは2020-01-02〜2026-10-28（1,715日）。
高VIXは前営業日のVIXが30以上の149日、非高VIXは1,566日。区間の名目Coverageは90%、Rolling Windowは252営業日。

## 評価基準

点予測はRMSEを主指標、MAEを補助指標とする。予測区間は平均Interval Score（IS）が小さいほど良いとし、経験的Coverageが90%以上かを別に表示する。
幅が狭いだけでは良いと判定しない。目標到達候補がない場合は、その区分に適切な組み合わせが見つかったとは結論しない。
以下の順位は、この観測期間内での点推定による順位である。

## 点予測


| 区分 | モデル | 日数 | MAE | RMSE |
| --- | --- | --- | --- | --- |
| 全Test | Random Walk | 1715 | 0.831254 | 1.271564 |
| 全Test | Historical Mean | 1715 | 0.829672 | 1.270860 |
| 全Test | AR(1) | 1715 | 0.828941 | 1.268045 |
| 全Test | 重回帰 | 1715 | 0.830602 | 1.277232 |
| 高VIX | Random Walk | 149 | 2.095387 | 2.946440 |
| 高VIX | Historical Mean | 149 | 2.094027 | 2.945210 |
| 高VIX | AR(1) | 149 | 2.084231 | 2.930794 |
| 高VIX | 重回帰 | 149 | 2.094528 | 2.956612 |
| 非高VIX | Random Walk | 1566 | 0.710975 | 0.971955 |
| 非高VIX | Historical Mean | 1566 | 0.709372 | 0.971302 |
| 非高VIX | AR(1) | 1566 | 0.709504 | 0.971422 |
| 非高VIX | 重回帰 | 1566 | 0.710344 | 0.977141 |


今回の重回帰は、前日リターン・直近5日累積リターン・直近20日実現ボラティリティ・前日のVIXを使ったが、RMSEの点推定はAR(1)より大きかった。
重回帰に説明変数を加えれば改善する、という結果にはならなかった。変数や期間をこのTestの成績に合わせて選び直していない。

## 市場区分ごとの候補


| 区分 | 基準 | 組み合わせ | Coverage | 平均幅 | 平均IS |
| --- | --- | --- | --- | --- | --- |
| 全Test | 全候補の最小IS | Random Walk ＋ Rolling CP | 90.32% | 3.701477 | 5.921426 |
| 全Test | Coverage 90%以上の最小IS | Random Walk ＋ Rolling CP | 90.32% | 3.701477 | 5.921426 |
| 高VIX | 全候補の最小IS | AR(1) ＋ Rolling Normal | 68.46% | 5.096894 | 17.748680 |
| 高VIX | Coverage 90%以上の最小IS | 該当なし | — | — | — |
| 非高VIX | 全候補の最小IS | Random Walk ＋ Fixed Normal | 84.93% | 2.586589 | 4.468677 |
| 非高VIX | Coverage 90%以上の最小IS | Random Walk ＋ Rolling CP | 92.66% | 3.619644 | 4.632523 |


全TestではRandom Walk＋Rolling CPのISが最小で、Coverageも点推定では90%以上だった。ただし他の基準モデルとの差は小さく、一意の統計的優位性を示したとは言わない。

高VIXでは全16通りが目標未達だった。AR(1)＋Rolling NormalのISが最小でも、その組み合わせが90%の信頼性を達成したとは解釈できない。

非高VIXではRandom Walk＋Fixed NormalのISが最小だったがCoverageは90%未満だった。目標到達候補に限定するとRandom Walk＋Rolling CPが最小ISとなった。
これは「ISが最小」と「Coverage目標を満たす」を分ける必要を示している。両市場区分で目標を満たす候補はなかった。

## 16通りの数値



### 全Test


| モデル | 区間法 | Coverage | 平均幅 | 平均IS | 90%目標 |
| --- | --- | --- | --- | --- | --- |
| Random Walk | Fixed CP | 80.17% | 2.466826 | 6.289311 | 未達 |
| Random Walk | Rolling CP | 90.32% | 3.701477 | 5.921426 | 到達 |
| Random Walk | Fixed Normal | 81.05% | 2.586589 | 6.177919 | 未達 |
| Random Walk | Rolling Normal | 90.20% | 3.909079 | 5.935124 | 到達 |
| Historical Mean | Fixed CP | 79.88% | 2.476438 | 6.278800 | 未達 |
| Historical Mean | Rolling CP | 90.20% | 3.701975 | 5.928477 | 到達 |
| Historical Mean | Fixed Normal | 81.22% | 2.586589 | 6.176570 | 未達 |
| Historical Mean | Rolling Normal | 90.26% | 3.909079 | 5.940344 | 到達 |
| AR(1) | Fixed CP | 79.83% | 2.470476 | 6.269168 | 未達 |
| AR(1) | Rolling CP | 90.26% | 3.713128 | 5.922937 | 到達 |
| AR(1) | Fixed Normal | 81.22% | 2.583511 | 6.164155 | 未達 |
| AR(1) | Rolling Normal | 90.20% | 3.902939 | 5.926368 | 到達 |
| 重回帰 | Fixed CP | 80.06% | 2.475176 | 6.334861 | 未達 |
| 重回帰 | Rolling CP | 89.74% | 3.738174 | 5.991448 | 未達 |
| 重回帰 | Fixed Normal | 81.92% | 2.630495 | 6.194767 | 未達 |
| 重回帰 | Rolling Normal | 89.62% | 3.923518 | 5.993490 | 未達 |


### 高VIX


| モデル | 区間法 | Coverage | 平均幅 | 平均IS | 90%目標 |
| --- | --- | --- | --- | --- | --- |
| Random Walk | Fixed CP | 40.27% | 2.466826 | 24.737768 | 未達 |
| Random Walk | Rolling CP | 65.77% | 4.561544 | 19.467884 | 未達 |
| Random Walk | Fixed Normal | 40.27% | 2.586589 | 24.142169 | 未達 |
| Random Walk | Rolling Normal | 67.79% | 5.113824 | 17.892160 | 未達 |
| Historical Mean | Fixed CP | 39.60% | 2.476438 | 24.645242 | 未達 |
| Historical Mean | Rolling CP | 66.44% | 4.566420 | 19.449670 | 未達 |
| Historical Mean | Fixed Normal | 40.94% | 2.586589 | 24.099259 | 未達 |
| Historical Mean | Rolling Normal | 68.46% | 5.113824 | 17.875396 | 未達 |
| AR(1) | Fixed CP | 40.27% | 2.470476 | 24.502179 | 未達 |
| AR(1) | Rolling CP | 66.44% | 4.587146 | 19.320287 | 未達 |
| AR(1) | Fixed Normal | 40.94% | 2.583511 | 23.945380 | 未達 |
| AR(1) | Rolling Normal | 68.46% | 5.096894 | 17.748680 | 未達 |
| 重回帰 | Fixed CP | 42.28% | 2.475176 | 24.711581 | 未達 |
| 重回帰 | Rolling CP | 65.10% | 4.599218 | 19.476847 | 未達 |
| 重回帰 | Fixed Normal | 45.64% | 2.630495 | 23.983958 | 未達 |
| 重回帰 | Rolling Normal | 67.11% | 5.138795 | 17.873360 | 未達 |


### 非高VIX


| モデル | 区間法 | Coverage | 平均幅 | 平均IS | 90%目標 |
| --- | --- | --- | --- | --- | --- |
| Random Walk | Fixed CP | 83.97% | 2.466826 | 4.533998 | 未達 |
| Random Walk | Rolling CP | 92.66% | 3.619644 | 4.632523 | 到達 |
| Random Walk | Fixed Normal | 84.93% | 2.586589 | 4.468677 | 未達 |
| Random Walk | Rolling Normal | 92.34% | 3.794451 | 4.797449 | 到達 |
| Historical Mean | Fixed CP | 83.72% | 2.476438 | 4.531291 | 未達 |
| Historical Mean | Rolling CP | 92.46% | 3.619725 | 4.641978 | 到達 |
| Historical Mean | Fixed Normal | 85.06% | 2.586589 | 4.471282 | 未達 |
| Historical Mean | Rolling Normal | 92.34% | 3.794451 | 4.804761 | 到達 |
| AR(1) | Fixed CP | 83.59% | 2.470476 | 4.534354 | 未達 |
| AR(1) | Rolling CP | 92.53% | 3.629968 | 4.648221 | 到達 |
| AR(1) | Fixed Normal | 85.06% | 2.583511 | 4.472327 | 未達 |
| AR(1) | Rolling Normal | 92.27% | 3.789338 | 4.801512 | 到達 |
| 重回帰 | Fixed CP | 83.65% | 2.475176 | 4.586374 | 未達 |
| 重回帰 | Rolling CP | 92.08% | 3.656248 | 4.708354 | 到達 |
| 重回帰 | Fixed Normal | 85.38% | 2.630495 | 4.502181 | 未達 |
| 重回帰 | Rolling Normal | 91.76% | 3.807888 | 4.863157 | 到達 |


## 差の不確実性

paired moving block bootstrapを実施した。主Block長は10、感度分析は5・20で、各5,000回。非循環の連続ブロックを全Test時系列から抽出し、同じ日付indexを全手法に適用した。
高VIX区分も一緒に抽出してから区分別に集計した。モデルを再学習するBootstrapではない。以下は主設定のpercentile法による、点ごとの近似95%信頼区間である。

差は重回帰−AR(1)。RMSE差が正なら重回帰の誤差が大きい。


| 区分 | RMSE差 | 近似95%CI |
| --- | --- | --- |
| 全Test | 0.009187 | [-0.001628, 0.022114] |
| 高VIX | 0.025818 | [-0.028358, 0.083215] |
| 非高VIX | 0.005719 | [-0.000937, 0.012453] |


いずれも0をまたぐため、重回帰とAR(1)のRMSE差を明確に識別できない。同等性が証明されたという意味ではない。

区間法の違いは、同じAR(1)について次のようになった。IS差が負ならAの点推定が良い。


| 区分 | 比較A−B | 平均IS差 | 近似95%CI |
| --- | --- | --- | --- |
| 全Test | Fixed CP − Fixed Normal | 0.105013 | [0.073547, 0.140220] |
| 全Test | Rolling CP − Rolling Normal | -0.003431 | [-0.167525, 0.220310] |
| 全Test | Rolling CP − Fixed CP | -0.346231 | [-0.695803, -0.014911] |
| 全Test | Rolling Normal − Fixed Normal | -0.237787 | [-0.691218, 0.164466] |
| 高VIX | Fixed CP − Fixed Normal | 0.556799 | [0.445635, 0.665154] |
| 高VIX | Rolling CP − Rolling Normal | 1.571607 | [-0.149914, 3.688263] |
| 高VIX | Rolling CP − Fixed CP | -5.181892 | [-6.977649, -3.416559] |
| 高VIX | Rolling Normal − Fixed Normal | -6.196700 | [-9.072691, -3.435430] |
| 非高VIX | Fixed CP − Fixed Normal | 0.062027 | [0.036967, 0.089549] |
| 非高VIX | Rolling CP − Rolling Normal | -0.153291 | [-0.207032, -0.104428] |
| 非高VIX | Rolling CP − Fixed CP | 0.113867 | [-0.110561, 0.344512] |
| 非高VIX | Rolling Normal − Fixed Normal | 0.329185 | [0.094642, 0.577372] |


### Block長の感度

AR(1)のRolling CP−Fixed CPについて、全Testの平均IS差を比較する。

| Block長 | 平均IS差 | 近似95%CI |
| --- | --- | --- |
| 5 | -0.346231 | [-0.632885, -0.084221] |
| 10 | -0.346231 | [-0.695803, -0.014911] |
| 20 | -0.346231 | [-0.811268, 0.057377] |


Block長20ではCIが0をまたぎ、5・10とは0の包含について異なる結果となった。点推定の改善だけから、結論がBlock長に依存しないとは言わない。


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

