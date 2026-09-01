# Internal states emerge early during learning of a perceptual decision-making task

- **タイトル和訳**: 知覚的意思決定課題の学習の初期段階から内部状態が出現する
- **著者**: Lenca I. Cuturela, International Brain Laboratory, Jonathan W. Pillow ほか
- **誌名**: bioRxiv preprint（2024年12月投稿）
- **DOI**: [10.1101/2024.11.30.626182](https://doi.org/10.1101/2024.11.30.626182)
- **リンク**: [bioRxiv](https://www.biorxiv.org/content/10.1101/2024.11.30.626182) / [PubMed](https://pubmed.ncbi.nlm.nih.gov/39651276/)
- **原本**: bioRxiv preprint v2（2025-09-10投稿版、全文）を [reference/sources/](sources/) に保存している。
  - [cuturela2024_internal_states_early_biorxiv_v2.pdf](sources/cuturela2024_internal_states_early_biorxiv_v2.pdf)
- **公開実装**: [github.com/lenca56/dynamic_glmhmm](https://github.com/lenca56/dynamic_glmhmm)（著者本人によるコード、2026-09-01存在確認済み）。コアクラス`dynamic_GLMHMM`（`code/dynamic_glmhmm.py`）・グリッドサーチとcross-validation（`code/analysis_utils.py`）を含む。詳細は下記「モデルの定義」末尾の実装レベルの節を参照。[docs/requirements_ver5.md](../docs/requirements_ver5.md) 5.4節の実装ベースとして参照している。

## Figure 1

![Figure 1](images/cuturela2024_internal_states_early_fig1.jpg)

*出典: Cuturela et al. (2024) bioRxiv preprint, [10.1101/2024.11.30.626182](https://doi.org/10.1101/2024.11.30.626182)（個人の研究メモ用途での引用）*

## 要旨（原文PDFに基づく）

- **問題提起**
  - [ashwood2022_discrete_strategies.md](ashwood2022_discrete_strategies.md) のGLM-HMMは、十分訓練された（定常状態に達した）マウスのデータに対して複数の離散戦略を検出できる。
    - しかし、状態内のGLM重み・遷移確率をセッションを通じて固定パラメータとして学習するため、学習過程そのもの（訓練初期からいつ・どう複数戦略が出現するか）は扱えない。
  - 本研究はこの限界を克服する動的モデルを開発し、動物が訓練開始時から複数戦略を切り替えるのか、十分な曝露後にのみそうなるのかを検証する。
- **タスク**
  - IBLの2値強制選択視覚課題。左右いずれかにサイン波グレーティング刺激（コントラスト0〜100%）が提示され、マウスはホイールを回してどちら側かを報告する。
  - 訓練は2段階:
    - まず左右等確率（50:50）の基本課題。
    - 次に左右一方に偏ったブロック構造（20:80 / 80:20が試行ブロックごとに交代）のフル課題。
  - IBL傘下3施設の32匹について、基本課題〜フル課題を通した全試行に個体ごとにモデルを独立にフィットしている。
- **数理モデル（dynamic GLM-HMM）**
  - GLM-HMMを「学習過程」へ拡張したモデル（定式化は下記「モデルの定義」節）。
    - GLM重みがセッション間で前セッションの重みを中心としたガウス事前分布に従って緩やかに変化できる。
    - 遷移行列もセッションごとにディリクレ事前分布から生成される。
  - これにより、静的GLM-HMMでは表現できない「学習に伴う戦略の緩やかな変化」を捉える。
- **結果**
  - 2セッション目の時点で既に3状態モデルが1状態モデルを上回る。
  - 学習の非常に早い段階からEngaged状態とBiased状態（左右2つ）が併存。
  - 訓練を通じた成績向上は、次の2要因の組み合わせで説明された。
    - 全状態での刺激感度（GLMの刺激重み）の増加。
    - 正答率の高いEngaged状態で過ごす時間割合（occupancy）の相対的増加。
- **学習達成基準の提案**
  - Engaged状態が一定の正答率に達した時点を「課題を学習した」と定義する新しい基準を提案。
    - この基準では、単純な正答率（内部状態の脱従事を考慮しない従来指標）よりも早期に学習達成と判定されるケースが多いことを示した。

## モデルの定義（Method Details "Dynamic GLM-HMM" / "Inference of dynamic GLM-HMM parameters" より）

[Ashwood et al. (2022)](ashwood2022_discrete_strategies.md) の GLM-HMM は状態内のGLM重みと遷移行列をセッションを通じて固定のパラメータとして学習する（実質的に十分に訓練が進んだ定常状態のデータのみを対象とする）。本論文はこれを **"dynamic GLM-HMM"** として拡張し、遷移行列 $P^s$ と状態別GLM重み $\{w_k^s\}_k$ をセッション $s$ ごとに変化させる。

**選択確率（観測モデル）**: 試行 $t$・セッション $s$ における二値選択 $y_t^s \in \{0,1\}$ は、状態 $z_t^s=k$ のもとで、タスク共変量ベクトル $x_t^s$ と状態別GLM重み $w_k^s$ のロジスティック関数で決まる（Ashwood et al. と同じBernoulli GLMの枠組み）。

$$p(y_t^s \mid x_t^s, z_t^s=k) = \frac{\exp(-(1-y_t^s)\, w_k^s \cdot x_t^s)}{1 + \exp(-w_k^s \cdot x_t^s)}$$

**入力（デザイン行列）の4列**（ $D=4$、Ashwood et al. と同じ4カテゴリ）: 符号付き刺激コントラスト・バイアス項・前試行の報酬付き選択・前試行の選択。

**セッション別遷移行列**: $K \times K$ の $P^s$ は $P^s_{i,j} = p(z_t^s=j \mid z_{t-1}^s=i)$ で、各行の和は1。各セッションの最初の潜在状態は一様分布 $z_1^s \sim U(\{1,\dots,K\})$ から生成される。

**パラメータの動的事前分布**（式1・式2、Method Details "Dynamic GLM-HMM"）:

 $$w_{k,d}^{s} \sim \mathcal{N}(w_{k,d}^{s-1},\ \alpha_{k,d}^2) \tag{1}$$

$$P_i^{s} \overset{\text{i.i.d.}}{\sim} \mathrm{Dir}(\kappa A_i + 1) \tag{2}$$

- $\alpha_{k,d}$（正のハイパーパラメータ）: 状態 $k$・タスク変数 $d$ ごとの重みのセッション間変動幅。大きいほどセッション間で重みが大きく変化できる。**公開実装ではこのハイパーパラメータは引数`sigma`という名前で渡す**（下記「公開実装のコードレベルの詳細」参照。論文の記法とコードの変数名が入れ替わっているので要注意）。
- $\kappa$（非負スカラーのハイパーパラメータ）: ディリクレ分布の集中度。 $A$ は大域推定遷移行列で、 $\kappa$ が大きいほどセッション別遷移行列 $P^s$ は大域行列 $A$ に近づく（閉形式最適化のために選んだ事前分布であり、遷移行列のセッション間の時間的滑らかさを直接課すものではない）。**公開実装ではこのハイパーパラメータは引数`alpha`という名前で渡す**（同上）。
- 極限 $\alpha_{k,d} \to 0,\ \kappa \to \infty$ で、重み・遷移行列がすべてのセッションで一定となり、標準GLM-HMMと等価になる。

**推論（MAP推定 + EM）**: 固定したハイパーパラメータ $K, \{\alpha_{k,d}\}, \kappa$ のもとで、セッション別パラメータ $\Theta = \{P^s, w_k^s\}$ をMAP推定する。Ashwood et al. と同様の入出力HMM向けEMアルゴリズムの派生形を用いる。

- Eステップ: セッションごとに前向き後向きアルゴリズムを実行し、Expected Complete-Data Log-Likelihood（ECLL）を計算する。
- Mステップ: ECLLと式1・式2の対数事前分布を合わせた量を最大化する。重み $w^s$ には閉形式解がないため scipy.optimize の準ニュートン法（BFGS）で最適化し、遷移行列 $P^s$ は各行の和が1という制約下でラグランジュ未定乗数法により閉形式で更新する（重みと遷移行列は独立に最適化できる）。

**ハイパーパラメータ・状態数の選択**: 状態数 $K \in \{1,\dots,5\}$ と重みの変化率 $\alpha$ をグリッドサーチし、held-outデータのtest log-likelihoodをcross-validationで比較。個体・タスク全体で $K=3$、 $\alpha \approx 3$（動物集団平均では $\alpha \approx 3.2$）が最良となり、Ashwood et al. の3状態という結果と一致した。遷移行列側の $\kappa$ は比較的小さい値が選ばれ、セッションをまたいで遷移確率が急に変化する余地を残している（実際に急変することは稀だった）。個体ごとのモデルは、全マウスをプールした大域的な標準GLM-HMMのフィット結果をパラメータ初期値として用いる。

**公開実装のコードレベルの詳細**（`dynamic_glmhmm.py`のクラス`dynamic_GLMHMM`・`analysis_utils.py`のCV関数群より。本文のMethodsに書かれていない実装上の具体を補う）:

- **モデルの3段階（`model_type`引数）**: クラスは`model_type ∈ {'standard', 'partial', 'dynamic'}`を持つ1本の実装で、論文の3つの比較モデルすべてを表現する。`'standard'`は重み・遷移行列とも全セッション共通（$\alpha_{k,d}\to0,\ \kappa\to\infty$ の極限に相当）。`'partial'`は遷移行列を全セッション共通に固定したまま重みだけセッション別にする中間モデル。`'dynamic'`が本文の完全な定式化（重み・遷移行列とも共にセッション別）。READMEに明記されたフィッティング手順は必ずこの順（standard→partial→dynamic）で、後段は前段の最良フィットを初期値にする。
- **重みのMステップは前後両セッションからの二次罰則**: 損失関数`value_weight_loss_function`は、セッション $s$・状態 $k$ の重み $w_k^s$ について、重み付き対数尤度 $\sum_t \gamma_t(k)\log p(y_t\mid x_t, w_k^s)$ に
  $$-\tfrac12(w_k^s-w_k^{s-1})^\top\Sigma_k^{-1}(w_k^s-w_k^{s-1}) - \tfrac12(w_k^s-w_k^{s+1})^\top\Sigma_k^{-1}(w_k^s-w_k^{s+1}), \quad \Sigma_k=\mathrm{diag}(\sigma_{k,1}^2,\dots,\sigma_{k,D}^2)$$
  を足した量を最大化する。式1は片側（前セッションのみ）を条件とするガウス事前分布だが、実装は前後両方のセッションの重みを同時に使う対称なチェーン平滑化になっている（本文の式だけからは読み取れない）。最適化は`scipy.optimize.minimize(method='L-BFGS-B')`（本文中の記載は単に「準ニュートン法（BFGS）」）。セッションは $s=0,1,\dots$ の昇順に逐次更新するため、同一EMイテレーション内で前セッション側の重み（`prevW`）は既に更新済みの値、次セッション側（`nextW`）は前イテレーションの値が使われる（Gauss-Seidel型の非対称な更新順序）。
- **遷移行列のMステップの閉形式（`'dynamic'`）**:
  $$p^s_{i,j} = \frac{\sum_t \zeta_t(i,j) + \kappa A_{i,j}}{\sum_{j'}\sum_t \zeta_t(i,j') + \kappa}$$
  （$\zeta$は式1・式2直前のE-stepで計算される期待遷移カウント、$A$は`'partial'`段で得た大域遷移行列）。これは式2の事前分布 $\mathrm{Dir}(\kappa A_i+1)$ の下でのMAP（事後モード）そのもの——一般に $\mathrm{Dir}(\alpha_j)_{j}$ の事後モードは $(\alpha_j+n_j-1)/(\sum_j\alpha_j+\sum_jn_j-J)$ であり、$\alpha_j=\kappa A_{i,j}+1$ を代入するとちょうど上式に一致する。事前疑似カウントに"+1"を足す式2の設計は、この閉形式が綺麗に導けるように選ばれている。遷移行列が全セッション共通の`'standard'`/`'partial'`では、$\kappa A$ の代わりに固定のディリクレ事前分布（既定は対角10・非対角1、[Ashwood et al. (2022)](ashwood2022_discrete_strategies.md) と同種のsticky prior）を使う。
- **ハイパーパラメータのグリッドサーチと温スタート**: `fit_eval_CV_partial_model`は`sigma`（$\alpha_{k,d}$）を`[0.01, 0.1, 1, 10, 100]`の昇順で振り、各点を1つ小さい`sigma`の最良フィットから初期化する。続く`fit_eval_CV_dynamic_model`系の関数は`alpha`（$\kappa$）を`[10000, 1000, 100, 10, 1, 0]`の降順（大きい`alpha`＝遷移行列がほぼ静的側、から出発）で振り、各点を1つ大きい`alpha`の最良フィットから初期化する。いずれも近傍のハイパーパラメータ値からの温スタートで局所解への収束を安定させる設計であり、グリッド点ごとに独立なランダム再初期化はしていない。
- **cross-validation分割**: `split_data`は各セッションを既定10試行のブロックに区切り、ブロック単位でシャッフルした既定5-foldに振り分ける。連続試行をブロックとして保つことで系列内の時間依存性を壊さず、全セッションがtrain/test双方に必ず現れるようにしている。テストに割り当てた試行は系列から物理的に除去せず、`present`ベクトル（0/1マスク）で「欠測」として前向き後向きアルゴリズムに渡す（欠測時刻は尤度項を1に固定し、状態の不確実性だけを伝播させて尤度計算からは除外する）。`evaluate`関数が計算するtest log-likelihoodは、testマスクが立った試行についてのみ forward pass の正規化係数 $\log c_t = \log p(y_t\mid y_{1:t-1})$ を平均した値（試行あたり平均対数尤度）。
- **2値の実装は多クラスの特殊ケースとして書かれている**: 重み配列は`N x K x D x C`次元で保持され、参照クラス $c=0$ の重みは常に0に固定（`w[:,:,:,0]=0`）し、$c=1$ の重みだけを最適化する2クラスsoftmax（＝ロジスティック回帰）として実装されている。README自身も「観測は現状Bernoulliのみだが3クラス以上の観測に拡張可能」と明記しており、参照カテゴリの重みを0に固定するという識別性の扱いは、[docs/requirements_ver5.md](../docs/requirements_ver5.md) 5.1節の系統B（3値カテゴリカル、参照カテゴリをNo Reactionに固定）と同じ方針である。ただし公開コードが実装済みなのは $C=2$ のみで、$C\geq3$ のsoftmax版は同節向けに新規実装が必要。

**Bruijns et al. (2025) の無限隠れセミマルコフモデル（diHMM、[relations.md](relations.md) 参照）との関係**: dynamic GLM-HMMは、状態数 $K$ を固定し状態滞在時間が幾何分布に従うという条件下での diHMM の特殊ケースとみなせる。diHMMはより柔軟だが、推論にサンプリングと事後的なクラスタリングを要し解釈が難しい。同一データでの直接比較では、ほとんどのセッションで3状態dynamic GLM-HMMの方がheld-outデータのlikelihoodが高かった。
