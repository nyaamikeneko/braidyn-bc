# Inferring internal states across mice and monkeys using facial features

- **著者**: Alejandro Tlaie, Muad Y. Abd El Hay, Berkutay Mert, Robert Taylor, Pierre-Antoine Ferracci, Katharine Shapcott, Mina Glukhova, Jonathan W. Pillow, Martha N. Havenith, Marieke L. Schölvinck
- **誌名**: Nature Communications, 16, Article 5168 (2025)
- **DOI**: [10.1038/s41467-025-60296-1](https://doi.org/10.1038/s41467-025-60296-1)
- **リンク**: [Nature](https://www.nature.com/articles/s41467-025-60296-1) / [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12137566/) / [PubMed](https://pubmed.ncbi.nlm.nih.gov/40467558/)
- **原本**: 出版版の全文・Supplementary Informationを [reference/sources/](sources/) に保存している。
  - [tlaie2025_facial_features_mice_monkeys_fulltext.pdf](sources/tlaie2025_facial_features_mice_monkeys_fulltext.pdf)（下記「モデルの定義」節はこのPDFのMethods "Markov-switching linear regression" / "Model tuning" / "ARHMM" 節に基づく）
  - [tlaie2025_facial_features_mice_monkeys_supplement.pdf](sources/tlaie2025_facial_features_mice_monkeys_supplement.pdf)（Supplementary Figures）

## Figure 1

![Figure 1](images/tlaie2025_facial_features_mice_monkeys_fig1.jpg)

*出典: Tlaie et al. (2025) Nature Communications, [10.1038/s41467-025-60296-1](https://doi.org/10.1038/s41467-025-60296-1)。CC BY 4.0。*

## 要旨（要約）

内部認知状態が種を超えて共通性を持つかを検証するため、マウスとマカクザルに同一の自然主義的な視覚採食課題をバーチャルリアリティ環境で行わせた研究。顔の映像特徴（サルは18特徴、マウスは9特徴）を用いて Markov-Switching Linear Regression（MSLR）モデルを学習し、動物がいつ刺激に反応するかを予測する内部状態を推定した。反応時間のみで学習したにもかかわらず、モデルは課題成績も予測できた。推定された内部状態は、成績との関係性がマウスとサルで共通しており（速い反応・高成績の「注意」状態、速いが不正解が多い「衝動的」状態、遅く成績も悪い「不注意」状態）、対応する表情パターンにも部分的な重なりが見られた。表情が種を超えて共通の内部状態を反映することを示唆する。

## モデルの定義（Methods "Markov-switching linear regression" / "Model tuning" / "ARHMM" より）

**MSLR（Markov-Switching Linear Regression）** は、離散マルコフ連鎖の状態ごとに異なる線形回帰を対応させる状態空間モデル。実装には `ssm` ではなく [Dynamax](https://github.com/probml/dynamax)（JAX製の状態空間モデルライブラリ）を用いている。

- 離散潜在状態 $z_t \in \{0, \dots, S-1\}$ がマルコフ連鎖として遷移する（遷移行列はDirichlet事前分布）。
- 入力（predictor）$x_t \in \mathbb{R}^M$: 試行 $t$ の**刺激提示前**の表情特徴（マウス9次元・サル18次元。各顔キーポイントの垂直・水平位置の中央値と速度）。
- 出力（emission）$y_t \in \mathbb{R}^N$: 同じ試行の反応時間（RT、$N=1$）。
- 状態 $z_t=s$ が与えられたときの emission 分布: $y_t \mid z_t=s, x_t \sim \mathcal{N}(W_s x_t + b_s,\ \Sigma_s)$、$W_s \in \mathbb{R}^{N \times M}$（状態ごとの回帰重み）、$b_s \in \mathbb{R}^N$（バイアス）、$\Sigma_s \in \mathbb{R}^{N \times N}$（emission共分散）。
- つまり **「どの表情特徴がRTを予測するか」という回帰係数そのものが、隠れ状態によって切り替わる**モデル。ある状態では眉の動きがRTを予測し、別の状態では鼻のsniffingが予測する、といった対応を想定している。

**学習**: EMアルゴリズムを50反復、パラメータ初期値を変えて10回リピートし最良解を採用。訓練:テスト = 80:20。セッションをまたぐ結合時は50試行分の予測変数・出力を0にする強制遷移を挟み、状態確率をリセットする。

**ハイパーパラメータ探索（Model tuning）**: Dirichlet事前分布の濃度パラメータ $\alpha$（遷移行列の疎さ）と、stickiness パラメータ $\kappa$（対角成分への自己バイアス項、状態が長く持続しやすくする）をグリッドサーチし、cross-validated $R^2$ で選択。

**状態数 $S$ の決定**: cross-validated $R^2$ が頭打ちになる点を、CV性能曲線の有限差分（finite difference）で検出して選択（Ashwood et al. 2022 のプラトー検出と同じ発想）。サルは $S=4$、マウスは $S=3$ が最適だった。

**対照実験（ARHMM）**: 表情特徴の代わりに前試行のRT（$t-1$）のみを入力としたAuto-Regressive HMMを比較対象として学習し、facial-features版のMSLRが全状態でARHMMを上回ることを確認（表情が単なる試行履歴の代理変数ではないことの根拠）。

**GLM-HMMとの相互検証**: Discussionで、同じデータに対して個体・セッションごとにGLM-HMM（行動選択ベース、Ashwood et al. 2022と同じ枠組み）を学習しても類似した結果が得られたと報告している（本文参照文献73）。

## この研究との関連

**本研究の Main RQ「HMM/状態空間モデルと身体データ（表情）の統合方法」に対する、直接的な方法論的参考文献。**

- 本リポジトリの GLM-HMM（[ashwood2022_discrete_strategies.md](ashwood2022_discrete_strategies.md) 準拠）は、表情特徴を**選択GLMの入力共変量**として使う設計（`notebooks/14_glmhmm_ver4_trials.ipynb` の13次元入力＝4次元行動変数＋9次元顔特徴）。一方MSLRは、表情特徴を**予測変数（predictor）**、行動指標（RT）を**出力（emission）**とし、状態ごとに両者を結ぶ回帰係数を切り替える。同じ「HMM×身体データ」でも、身体データを (a) 状態を決めるGLMの入力にするか、(b) 状態依存の回帰で行動を予測する側の入力にするか、という2つの統合方向がある点に注意。本リポジトリのVer.4拡張を設計・解釈する際は、どちらの統合方向を取っているかを明示すると良い。
- マウスで用いる顔特徴数（9）が本リポジトリの顔特徴次元と一致する点は、特徴選定の参考になる可能性がある。
- 「注意／衝動的／不注意」という3状態の解釈は、本研究のミス試行分解（RQ3, H3: Mismatch vs Joint Disengagement）における状態のラベリングと比較可能な参照枠を与える。
- ARHMM対照実験の設計（身体データなしのRT自己回帰HMMと比較する）は、本リポジトリで「表情特徴を加えることの寄与」を検証する際の対照群の組み方として直接転用できる。
- 実装ライブラリはssmではなくDynamax（JAX）である点に注意。本リポジトリはssm（`docs/`・`src/glmhmm_ver4.py` 参照）を使用しており、直接のコード流用はできない。
