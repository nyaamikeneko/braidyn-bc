# Mice alternate between discrete strategies during perceptual decision-making

- **タイトル和訳**: マウスは知覚的意思決定の最中、離散的な複数の戦略を交互に切り替える
- **著者**: Zoe C. Ashwood, Nicholas A. Roy, Iris R. Stone, International Brain Laboratory, Anne E. Urai, Anne K. Churchland, Alexandre Pouget, Jonathan W. Pillow
- **誌名**: Nature Neuroscience, 25, 201–212 (2022)
- **DOI**: [10.1038/s41593-021-01007-z](https://doi.org/10.1038/s41593-021-01007-z)
- **リンク**: [Nature](https://www.nature.com/articles/s41593-021-01007-z) / [PubMed](https://pubmed.ncbi.nlm.nih.gov/35132235/) / [bioRxiv preprint](https://www.biorxiv.org/content/10.1101/2020.10.19.346353) / [Pillow Lab PDF](https://pillowlab.princeton.edu/pubs/Ashwood2022_NatNeurosci.pdf)
- **原本**: bioRxiv preprint v4（2021-12-13投稿版、Methods章を含む全文）を [reference/sources/](sources/) に保存している。
  - [ashwood2022_discrete_strategies_biorxiv_v4.pdf](sources/ashwood2022_discrete_strategies_biorxiv_v4.pdf)（下記「モデルの定義」節はこのPDFのMethods 4.1節に基づく）

## Figure 1

![Figure 1](images/ashwood2022_discrete_strategies_fig1.jpg)

*出典: Ashwood et al. (2022) Nature Neuroscience, [10.1038/s41593-021-01007-z](https://doi.org/10.1038/s41593-021-01007-z)（個人の研究メモ用途での引用）*

## 要旨（原文PDFに基づく）

- **問題提起**
  - 知覚意思決定の古典的解析は、動物が単一で一貫した戦略を使う、あるいは戦略が時間とともに緩やかに進化すると仮定してきた。
  - 本研究は、これらの仮定を置かずに「離散的に切り替わる複数戦略の混在」を検出できる枠組みを提示する。
    - げっ歯類実験で頻繁に観察される「lapse（脱落・不注意な誤答）」現象に対する代替説明を検証する。
- **タスク**
  - International Brain Laboratory (IBL) の視覚検出課題。
    - 0〜100%のコントラストを持つGaborグレーティング刺激が画面の左右いずれかに提示され、マウスはホイールを回してどちら側かを報告する。
    - 正しい方向に回すと水報酬、誤ると音のノイズバースト＋1秒のタイムアウト。
  - ブロック構造:
    - 各セッション最初の90試行は刺激が左右等確率（0.5）。
    - 以降は一方の側に偏ったブロック構造（確率0.8、20〜100試行ごとにランダムに交代）。
    - 解析には、バイアスが入りにくい各セッション最初の90試行（等確率区間）のみを使用。
  - 同じ枠組みをヒトの類似課題データにも適用している。
- **数理モデル**
  - Bernoulli GLMを観測モデルとするInput-Output HMM（GLM-HMM）。
    - 4次元デザイン行列（刺激コントラスト・バイアス項・前試行の選択・win-stay-lose-switch）を入力とし、状態ごとに異なるGLM重みで選択確率を予測する（定式化は下記「モデルの定義」節）。
  - 状態数の決定:
    - 5-fold cross-validationでtest set log-likelihoodを比較。
    - IBLマウス37匹のデータでは3状態でプラトーに達し、以降の解析はすべて3状態モデルで実施。
- **結果**
  - 感覚刺激への重みが大きく正答率が高い単一の「Engaged」状態（例示個体で90%正答）。
  - 刺激への重みが小さくbias重みが大きい2つの「Biased」状態（同58〜60%正答）。
  - 状態は数十〜数百試行にわたって持続し、しばしば1セッション内で複数回切り替わる。
    - 期待滞在時間の中央値: Engagedで24試行、Biasedで12〜13試行。
    - 56セッション中71%で状態変化が発生。
    - マウスは全試行の69%をEngaged状態で、31%をBiased状態で過ごした（例示個体）。
- **lapseモデルとの対比**
  - 状態の滞在時間はHMMの性質上、幾何分布 $p(\text{dwell}=t) = (1-A_{kk})A_{kk}^{t-1}$ に従う。
  - 古典的lapseモデル（lapse率20%と仮定）での期待滞在時間はわずか1.25試行。
    - GLM-HMMが捉える「持続的な状態」がlapseモデルの想定と本質的に異なることを示す論拠。
  - 著者らは、マウスはランダムにlapseするのではなく、持続的なEngaged状態とBiased（Disengaged）状態の間を切り替えると結論づけている。

## モデルの定義（Methods 4.1 より）

**GLM-HMM（Bernoulli GLM を観測モデルとする Input-Output HMM）の生成モデル**は、以下のパラメータで構成される（Methods 4.1.1、式5–6）。

- 遷移行列 $A \in \mathbb{R}^{K \times K}$
- 状態ごとのGLM重み $\{w_k\}_{k=1}^{K}$、 $w_k \in \mathbb{R}^{M}$
- 初期状態分布 $\pi \in \mathbb{R}^{K}$

これらのパラメータ $\Theta = \{\pi, A, \{w_k\}\}$ を、選択データ（session単位）に対するMAP推定（事前分布込みの対数事後確率最大化）で学習する。実装上はEMアルゴリズムを用い、Eステップで前向き後向きアルゴリズムにより状態の事後確率を計算し、MステップでGLM重みをBFGS法（scipy.optimize）で更新する（GLM重みに関するECLLは凹関数であるため大域最適解に収束することが保証される）。事前分布は、GLM重みに独立な平均0・分散 $\sigma^2$ のガウス分布、遷移行列の各行と初期状態分布に集中度パラメータ $\alpha$ のディリクレ分布を仮定する。$\sigma^2 \in \{0.5, 0.75, 1, 2, 3\}$、$\alpha \in \{1, 2\}$ のグリッドサーチをheld-out validation setの性能で評価して選択し、IBLマウスでは $\alpha=2$・$\sigma^2=2$（Odoemene et al. データでは $\alpha=0.75$・$\sigma^2=2$）が選ばれた（Methods 4.1.1）。

**多段階フィッティング手順**（Methods 4.1.5、Algorithm 1）: 動物間で意味的に対応する状態を後から並べ替えなくて済むよう、以下の3段階でフィットする。

1. 全動物（IBLでは37匹）のデータを1つの系列に連結し、GLM（1状態のGLM-HMMに相当）を最尤推定（MLE）で適合する。
2. そのGLM重みにガウスノイズ（$\sigma_{\text{init}}=0.2$）を加えてK状態GLM-HMMを初期化し、再び連結データ全体に適合する（＝"global fit"）。遷移行列は対角優位（$0.95 \times I$ にノイズを加えて正規化）で初期化する。$K$ ごとに20通りの乱数初期値でEMを実行し、学習セットの対数尤度が最良のものを採用する。
3. 各動物のGLM-HMMを、その $K$ に対するglobal fitの最良パラメータで初期化し、個別にEMで収束まで適合する。この初期化により、動物間で状態のラベル（並び順）を事後的に対応付ける必要がなくなる。Fig. 4・Fig. 5に示される個体別パラメータはこの手順で得られたもの。

公開コード（[zashwood/glm-hmm](https://github.com/zashwood/glm-hmm)）では、この3段階のうち事前分布の扱いが段階によって異なる。global fit（`2_fit_models/fit_global_glmhmm/1_run_inference_global_fit_ibl.py`）は `transition_alpha=1`（フラットなディリクレ事前分布）・`prior_sigma=100`（ほぼ無情報なガウス事前分布）に固定しており、コード中のコメントも `# perform mle => set transition_alpha to 1` と明記している。EMアルゴリズム自体はMAP推定の枠組み（4.1.1–4.1.4節）のままだが、事前分布をほぼ無効化することでMLEに近い挙動にしている。一方、個別動物のfit（`2_fit_models/fit_individual_glmhmm/1_run_inference_ibl_individual.py`）はグリッドサーチで選んだハイパーパラメータ（IBLで $\alpha=2$・$\sigma^2=2$）をそのまま使う「典型的な」MAP推定である。この事前分布の違いは論文本文（Methods 4.1.5）自体には明記されておらず、公開コードで確認できる（2026-09-01 GitHub `main`ブランチで確認）。

**入力（デザイン行列）の4列**（Methods 4.4、IBLデータでの標準設定・ $M=4$）:

| 列 | 内容 | 役割 |
| :--- | :--- | :--- |
| 1 | 刺激強度（z-score化） | 感覚刺激への依存度を学習する重み |
| 2 | 定数1（bias項） | 左右いずれかへの内在的バイアス |
| 3 | 前試行の選択（ $2y_{t-1}-1 \in \{-1,1\}$） | 大きいと「perseveration（同じ選択の連続）」を生む |
| 4 | win-stay-lose-switch（前試行の報酬×前試行の選択） | 大きいと「報酬を得たら同じ選択を繰り返し、得られなければ切り替える」戦略を生む |

**状態数 $K$ の決定**: 5-fold cross-validationでtest set log-likelihood（bits/trial、null Bernoulliモデル相対）を比較し、改善が頭打ちになる点で選択する。IBLマウス37匹のデータでは $K=3$ で頭打ちになり、以降の解析はすべて3状態モデルで実施された（Methods、Fig. 2b, Fig. 4a）。

**3状態の解釈**（IBLデータでの結果）:

- **Engaged**: 刺激への重みが大きい。正答率が高い（例示個体で90%）。期待滞在時間の中央値は24試行。
- **Biased-left / Biased-right**: 刺激への重みが小さく、bias重みが大きい。正答率が低い（例示個体で58–60%）。期待滞在時間の中央値は12–13試行。

状態の滞在時間（dwell time）はHMMの性質上、幾何分布 $p(\text{dwell}=t) = (1-A_{kk})A_{kk}^{t-1}$ に従う。古典的lapseモデル（lapse率20%と仮定）での期待滞在時間はわずか1.25試行であり、GLM-HMMが捉える「持続的な状態」がlapseモデルの想定と本質的に異なることを示す一つの論拠になっている。
