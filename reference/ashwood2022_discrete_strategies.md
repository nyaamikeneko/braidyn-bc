# Mice alternate between discrete strategies during perceptual decision-making

- **著者**: Zoe C. Ashwood, Nicholas A. Roy, Iris R. Stone, International Brain Laboratory, Anne E. Urai, Anne K. Churchland, Alexandre Pouget, Jonathan W. Pillow
- **誌名**: Nature Neuroscience, 25, 201–212 (2022)
- **DOI**: [10.1038/s41593-021-01007-z](https://doi.org/10.1038/s41593-021-01007-z)
- **リンク**: [Nature](https://www.nature.com/articles/s41593-021-01007-z) / [PubMed](https://pubmed.ncbi.nlm.nih.gov/35132235/) / [bioRxiv preprint](https://www.biorxiv.org/content/10.1101/2020.10.19.346353) / [Pillow Lab PDF](https://pillowlab.princeton.edu/pubs/Ashwood2022_NatNeurosci.pdf)
- **原本**: bioRxiv preprint v4（2021-12-13投稿版、Methods章を含む全文）を [reference/sources/](sources/) に保存している。
  - [ashwood2022_discrete_strategies_biorxiv_v4.pdf](sources/ashwood2022_discrete_strategies_biorxiv_v4.pdf)（下記「モデルの定義」節はこのPDFのMethods 4.1節に基づく）

## Figure 1

![Figure 1](images/ashwood2022_discrete_strategies_fig1.jpg)

*出典: Ashwood et al. (2022) Nature Neuroscience, [10.1038/s41593-021-01007-z](https://doi.org/10.1038/s41593-021-01007-z)（個人の研究メモ用途での引用）*

## 要旨（Semantic Scholar 経由で取得した原文の要約訳）

知覚意思決定の古典的モデルは、被験者が単一で一貫した戦略を使う、あるいは戦略が時間とともにゆっくり進化すると仮定してきた。本研究はこの通念が誤りであることを示す新しい解析を提示する。マウスとヒトの意思決定課題データを解析した結果、選択行動が複数の戦略の入れ替わり（interleaved）によって駆動されていることが分かった。これらの戦略は隠れマルコフモデル（HMM）の状態として特徴づけられ、数十〜数百試行にわたって持続したのち切り替わり、しばしば1セッション内で複数回切り替わる。マウス間で一貫して同定された戦略は、感覚刺激に強く依存する単一の「Engaged（従事）」状態と、頻繁に誤答する複数の「Biased（バイアス）」状態だった。この結果は、げっ歯類の行動実験でしばしば観察される「lapse（脱落）」現象に対する強力な代替説明を与え、標準的な成績指標が試行間の大きな戦略変化を覆い隠している可能性を示唆する。著者らは、マウスは lapse するのではなく、持続的な Engaged 状態と Disengaged 状態の間を切り替えると結論づけている。

## モデルの定義（Methods 4.1 より）

**GLM-HMM（Bernoulli GLM を観測モデルとする Input-Output HMM）の生成モデル**は、以下のパラメータで構成される（Methods 4.1.1、式5–6）。

- 遷移行列 $A \in \mathbb{R}^{K \times K}$
- 状態ごとのGLM重み $\{w_k\}_{k=1}^{K}$、$w_k \in \mathbb{R}^{M}$
- 初期状態分布 $\pi \in \mathbb{R}^{K}$

これらのパラメータ $\Theta = \{\pi, A, \{w_k\}\}$ を、選択データ（session単位）に対するMAP推定（事前分布込みの対数事後確率最大化）で学習する。実装上はEMアルゴリズムを用い、Eステップで前向き後向きアルゴリズムにより状態の事後確率を計算し、MステップでGLM重みをBFGS法（scipy.optimize）で更新する（GLM重みに関するECLLは凹関数であるため大域最適解に収束することが保証される）。事前分布は、GLM重みに独立な平均0のガウス分布、遷移行列の各行と初期状態分布にディリクレ分布を仮定する。

**入力（デザイン行列）の4列**（Methods 4.4、IBLデータでの標準設定・$M=4$）:

| 列 | 内容 | 役割 |
| :--- | :--- | :--- |
| 1 | 刺激強度（z-score化） | 感覚刺激への依存度を学習する重み |
| 2 | 定数1（bias項） | 左右いずれかへの内在的バイアス |
| 3 | 前試行の選択（$2y_{t-1}-1 \in \{-1,1\}$） | 大きいと「perseveration（同じ選択の連続）」を生む |
| 4 | win-stay-lose-switch（前試行の報酬×前試行の選択） | 大きいと「報酬を得たら同じ選択を繰り返し、得られなければ切り替える」戦略を生む |

**状態数 $K$ の決定**: 5-fold cross-validationでtest set log-likelihood（bits/trial、null Bernoulliモデル相対）を比較し、改善が頭打ちになる点で選択する。IBLマウス37匹のデータでは $K=3$ で頭打ちになり、以降の解析はすべて3状態モデルで実施された（Methods、Fig. 2b, Fig. 4a）。

**3状態の解釈**（IBLデータでの結果）:

- **Engaged**: 刺激への重みが大きい。正答率が高い（例示個体で90%）。期待滞在時間の中央値は24試行。
- **Biased-left / Biased-right**: 刺激への重みが小さく、bias重みが大きい。正答率が低い（例示個体で58–60%）。期待滞在時間の中央値は12–13試行。

状態の滞在時間（dwell time）はHMMの性質上、幾何分布 $p(\text{dwell}=t) = (1-A_{kk})A_{kk}^{t-1}$ に従う。古典的lapseモデル（lapse率20%と仮定）での期待滞在時間はわずか1.25試行であり、GLM-HMMが捉える「持続的な状態」がlapseモデルの想定と本質的に異なることを示す一つの論拠になっている。

## この研究との関連

**本リポジトリの GLM-HMM 実装（Ver.3 / Ver.4）が直接準拠する原著論文。**

- [docs/requirements_glmhmm.md](../docs/requirements_glmhmm.md) 冒頭に「採用モデル: Bernoulli GLM-HMM (Ashwood et al., 2022 準拠)」と明記されている。
- README.md の「ライセンス・出典」節で「GLM-HMM は Ashwood et al. (2022) および [ssm](https://github.com/lindermanlab/ssm) の Input Driven Observations に準拠します」と述べている。
- 本研究の RQ1（[docs/RQ.md](../docs/RQ.md)）「内部状態（Engaged vs Random）の生物学的妥当性」は、この論文が定義した Engaged/Biased 状態の枠組みをそのまま踏襲している。
- ssm ライブラリ（`lindermanlab/ssm`）の Input Driven Observations 実装は、この論文の著者グループ（Pillow Lab / Linderman Lab）が公開したもの。
- **デザイン行列の対応**: `src/glmhmm_ver4.py` の `BEHAVIOR_COLS`（`x_bias` / `x_stim` / `x_hist` / `x_rew` の4列）は、上記「モデルの定義」節の4列（Bias / Stimulus / 前試行の選択 / win-stay-lose-switch）と同じ4カテゴリ（bias・刺激・行動履歴・報酬履歴）に対応する構成を取る。ただし `x_hist` / `x_rew` は1試行ラグの離散変数ではなく指数減衰する履歴変数（[docs/requirements_glmhmm.md](../docs/requirements_glmhmm.md) 4.2節に元の定義がある。同文書はVer.3＝時間ビン単位向けの要件定義だが、この履歴変数の設計自体はVer.4でも試行単位で踏襲されている）である点が Ashwood et al. の1ラグ共変量と異なる。
- **状態数 $K$ の対応**: `src/glmhmm_ver4.py` の既定値 `NUM_STATES = 3` は、Ashwood et al. がIBLマウス37匹のcross-validationで選んだ $K=3$ と同じ値。本リポジトリの4次元入力モデルはこの既定値を踏襲し、13次元入力モデル（表情特徴込み）ではK=2とK=3を比較している（README.md「解析パイプライン」表を参照）。Ashwood et al. のような動物ごとの系統的なcross-validationによる$K$選択は行っていない。
