# 研究設計 v0.2：4モデル×4区間法

## 目的とResearch Questions

S&P 500の日次対数リターンを対象に、予測モデル、区間構築方式、誤差履歴の更新方法による違いを、全体・高VIX・非高VIXで比較する。

- RQ1：4モデルの点予測精度は、市場区分ごとにどう異なるか。
- RQ2：16通りの区間は、Coverage・幅・Interval Scoreの点でどう異なるか。
- RQ3：FixedとRolling、CPとNormalの差は、市場区分によってどう変わるか。

「最適」は、この対象期間・比較候補・事前の評価基準の範囲での表現とする。将来に普遍的な最適性は主張しない。

## 予測時点とデータ

前営業日の引け後に、当日の引けまでのリターンを予測する。
`r_t = 100 × log(P_t / P_(t-1))` とし、説明変数とVIX区分はt−1までで作る。
元のSP500.csvとVIXCLS.csvを追加取得・変更せず用いる。
Trainingは2017–2018年、Calibrationは2019年、Testは2020-01-02〜2026-10-28。
全モデルの学習値をTraining後に固定し、全手法を同じTestの1,715日で比較する。

高VIXは `VIX_(t-1) >= 30`、非高VIXは30未満。Trainingの高VIX日は5日、Calibrationでは0日、Testでは149日である。

## 点予測モデル

| モデル | 予測式 |
| --- | --- |
| Random Walk | `r_hat_t = 0`。対数価格のドリフトなしRandom Walkに対応 |
| Historical Mean | Trainingリターンの平均 |
| AR(1) | `beta0 + beta1 × r_(t-1)` |
| 重回帰 | `beta0 + beta1 × lag1 + beta2 × return5 + beta3 × vol20 + beta4 × vix_lag1` |

重回帰は切片付きOLS。return5はt−5〜t−1のリターンの和、vol20はt−20〜t−1の標本標準偏差（ddof=1）。
5日・20日は説明しやすい初期設定として事前指定し、今回の成績を見て変更しない。
相関・係数は記録するが、Testの成績やp値で説明変数を選び直さない。VIX等の係数を因果効果とは解釈しない。
重回帰は平均の予測モデルであり、ボラティリティを説明変数に加えただけで区間幅が直接変わるものではない。

## 区間法：構築方式×履歴更新

各モデルの符号付き誤差を `e_t = r_t - r_hat_t` とする。

| 区間法 | 誤差履歴 | 半幅 |
| --- | --- | --- |
| Fixed CP | 2019年全体 | 絶対誤差の `ceil((n+1)×0.90)` 番目 |
| Rolling CP | 予測日前の直近252日 | 同じ有限標本補正付き順位 |
| Fixed Normal | 2019年全体 | `z_0.95 × sd(e)` |
| Rolling Normal | 予測日前の直近252日 | `z_0.95 × sd(e)` |

すべて同じモデルの点予測を中心にする。Normalではddof=1、zは約1.644854を用いる。
誤差平均による中心補正は加えず、履歴の平均と標準偏差を保存する。
これはゼロ平均近似に基づく正規近似区間であり、係数不確実性等を含めた厳密な有限標本の回帰予測区間ではない。平均の信頼区間のようにsdをsqrt(n)で割らない。

Rollingは区間を出した後に当日の実現誤差を履歴へ追加する。CPとNormalで同じ252日を使う。
Fixed同士またはRolling同士の比較で区間構築方式を比較し、同じ方式のFixed対Rollingで履歴更新を比較する。
CP対Normalの差には、分布形だけでなくゼロ平均近似等の仮定の違いも含まれる。

## 評価基準

点予測はRMSEを主指標、MAEを補助指標とする。区間は次のISを主指標とする。[1]

`IS = (U-L) + (2/alpha)×max(L-r,0) + (2/alpha)×max(r-U,0)`

alpha=0.10とし、平均ISは小さいほど良い。Coverage・平均幅・上下別外れ率を併記する。
全候補の最小ISと、経験的Coverageが90%以上の候補だけでの最小ISを区別する。
後者に候補がなければ「目標到達候補なし」とする。90%は点推定についての記述的基準であり、将来の保証や認証基準ではない。
全体・高VIX・非高VIXを別々に判定し、それらを重複して足した合計点は作らない。

## 差の不確実性

paired non-circular moving block bootstrapのpercentile法で、点ごとの近似95%CIを求める。
主Block長は10、感度分析は5・20、各5,000回。各Block長でseed=202701のPCG64を初期化する。
全時系列から連続ブロックを抽出して先頭1,715日に切りそろえ、同じ日付indexを全手法とVIX区分へ適用する。
各抽出で区分別の分母を再計算し、高VIX日だけを独立に抽出しない。
抽出indexのSHA-256、先頭3反復のindex抜粋、区分の日数の範囲と0日になった反復数を記録する。

点予測は重回帰−AR(1)を主比較とし、基準2モデルとの差も保存する。
区間は、各区間法での重回帰−AR(1)と、各モデルでのFixed CP−Fixed Normal、Rolling CP−Rolling Normal、Rolling CP−Fixed CP、Rolling Normal−Fixed Normalを比較する。
差はA−B。RMSE・MAE・幅・ISでは負が小さいことを表す。Coverageの正負は包含率の増減であり、それだけで良し悪しを表さない。
CIが0をまたぐ場合は差を明確に識別できないと説明し、同等性が証明されたとは言わない。
多重比較補正はしておらず、選択後の一意の最良性を認定するためのCIではない。

再標本化するのは学習済み予測・区間の日別評価であり、再学習を伴う手順全体の不確実性ではない。
金融時系列の非定常性、一部の危機への集中があるため、Block長感度が安定してもCIの妥当性が証明されたとは扱わない。

## 結論の範囲と次段階

Conformalの通常のCoverage保証には交換可能性等の条件があり、金融時系列で自動的に成立するとは扱わない。単純なRolling化でVIX別の90%Coverageが保証されるわけでもない。[2]
今回のTestは既に一部確認しており、記述的・探索的な比較である。
Training・Calibrationの高VIX割合や位置、Window長を変えるRQ4は未実行。次の設定選択には時系列Validationと、新たな未確認期間での最終評価を設計する。

## 参考資料

[1] Gneiting, T. & Raftery, A. E. (2007). Strictly Proper Scoring Rules, Prediction, and Estimation. JASA, 102(477), 359–378. Section 6.2, equation (43).  
https://sites.stat.washington.edu/people/raftery/Research/PDF/Gneiting2007jasa.pdf

[2] Barber, R. F., Candès, E. J., Ramdas, A. & Tibshirani, R. J. (2023). Conformal Prediction Beyond Exchangeability. Annals of Statistics, 51(2), 816–845.  
https://www.stat.cmu.edu/~ryantibs/papers/nexcp.pdf
