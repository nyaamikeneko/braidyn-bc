# 要件定義書
# GLM-HMM Analysis: Requirement Definition Document (Ver.5.0)

設計のみ・未実装（notebooks・srcに対応する実装なし、2026-08-31時点）。[docs/RQ.md](RQ.md) のRQ2（学習ダイナミクス）・RQ1（生物学的妥当性）を検証するための拡張。試行の切り出し方（Window定義）と30Hzの前処理は [requirements_ver4.md](requirements_ver4.md) をそのまま継承し、本書では **Ver.4からの差分（観測モデルの2系統化、Second Pullの吸収、入力の行動限定、日をまたいだ動的学習、皮質を用いた独立検証）のみ** を定義する。

## 1. プロジェクト概要 (Overview)
* 目的: Ver.4（試行単位・二値行動・日ごと独立学習）を、Day 1–15の学習過程を貫くDynamic GLM-HMMへ拡張し、皮質活動を独立検証チャンネルとして統合することで、内的従事状態の学習ダイナミクス（RQ2）と生物学的妥当性（RQ1）を定量検証する。観測モデルは二値と4値の**2系統を切り替え可能に実装**し、どちらが状態構造をよく説明するかを比較する。
* 分析対象: 個体内、Day 1–15の全task-day（Dynamic GLM-HMMではセッション＝dayとして扱う）。
* 採用モデル: Dynamic GLM-HMM（動的部分はCuturela et al. 2024, [reference/cuturela2024_internal_states_early.md](../reference/cuturela2024_internal_states_early.md) 準拠）。
* **観測モデル（2系統、切り替え可能）**:
  * **系統A（Bernoulli）**: 二値（試行内にActionが有るか無いか）。Ver.4の目的変数をそのまま引き継ぐ。
  * **系統B（Categorical）**: 4値（Success / No Reaction / Short Pull / No Sound Pull）。多値emissionはHulsey et al. 2024の3値拡張（[reference/hulsey2024_arousal_movement.md](../reference/hulsey2024_arousal_movement.md)）に着想を得て4値へ拡張するが、識別性の扱いは異なる（5.1節）。

  試行系列・入力変数・動的パラメータ構造・皮質パイプラインは両系統で完全に共通にし、**差分を観測モデルだけに閉じる**。こうすると5.5節のtest log-likelihood比較が、他の設計差に汚染されずに「二値か4値か」だけの比較になる。
* 分析単位: 1試行（1 Trial）を1データポイントとする。
* **Ver.4との違い**:
  1. 観測モデル: Bernoulli固定 → BernoulliとCategorical（4値）の2系統。系統Aを既定とし、系統Bを並行して学習・比較する。
  2. 試行系列: Second Pullを独立した試行として扱わない（Ver.4は1行として持つ）。それ以外の系列の作り方はVer.4と同じ。
  3. 入力変数: 行動4次元（Bias / Stimulus / Action History / Reward History）のみ。Ver.4 4.3節の顔・身体9次元は使わない。
  4. 状態推定: 「日ごと独立学習」→「Dynamic GLM-HMM」（GLM重み・遷移行列が日をまたいで緩やかに変化し、状態ラベルが日をまたいで対応する）。
  5. 皮質活動の統合: 新規。GLM-HMMの入力には使わず、独立の生物学的妥当性検証チャンネル（RQ1）として用いる。手法の主参照はAloor et al. 2026。

## 2. 試行定義とデータ抽出（Ver.4からの差分）

各試行タイプのWindow定義・判別方法は [requirements_ver4.md](requirements_ver4.md) 2.1節をそのまま用いる（音提示試行は `trial_outcome` が `success` ならSuccess、それ以外は `pull_onset` の有無でShort Pull／No Reactionを判別する。`miss` / `failure` の文字列で分けてはならない）。

### 2.1 試行系列（両系統で共通）

* 対象は Success / No Reaction / Short Pull / No Sound Pull の4タイプ。Ver.4と同じく、Window開始時刻（音提示試行は `t_start`、No Sound Pull は `t_onset`）の昇順に並べた**単一の系列**として試行インデックス $k$ を振る（`extract_trials()` の既存挙動）。同時刻の場合は音提示試行を先に置く。
* **Second Pull は独立した試行として扱わない**（Ver.4からの変更点）。同一音刺激内の2回目以降の押下は、それが属する音提示試行のラベル（Success または Short Pull）に吸収される。系統Bでは4カテゴリに収める必要があり、系統Aでも系列を揃えて比較するため、両系統で同じ扱いにする。
  * **Window境界**: 吸収してもラベルの元になった音提示試行の `t_start`〜`t_end`（[requirements_ver4.md](requirements_ver4.md) 2.1節）は変更しない。Second Pullの押下時刻・終了時刻まで `t_end` を延長することはしない。6.2節の皮質デコード特徴量が基準にする「pull onset」は、Second Pullではなく元の音提示試行の `pull_onset`（最初の押下）を指す。Second Pullで生じた延長分の情報は捨てる（本Verのスコープ外）。
* **クラス不均衡**: No Sound Pull が試行数の大半を占める。`VG1GC-66` 全14日で音提示試行2359件に対しNo Sound Pull 4386件（全6745試行の65%）。さらにこの件数は前処理定数に強く依存し、`NOISE_REMOVE_LIMIT=0` にすると7730件（+76%）まで増える。系統Bではカテゴリの偏りとして、系統Aでは $y=1$ の偏りとして効くので、占有率・重み推定の解釈時にはこの不均衡と前処理定数への感度の両方を確認する。

### 2.2 検討したが不採用の入力

* **顔・身体の9次元（Ver.4 4.3節）**: 不採用。顔特徴を状態定義側の入力に入れると、皮質と顔の対応（RQ1、H2）を後段で調べる際に、顔が状態の定義にも検証にも現れる循環になる。行動のみで状態を定義することで、皮質と顔の**両方**を独立検証チャンネルとして使えるようにする。顔特徴は6.8節（H1）と7節（今後の拡張）で、モデル外の観測量として用いる。
* **Win-stay-lose-switch（Ashwood 2022式、$2y_{t-1}-1$ × 前試行報酬の1ラグ積）**: 不採用。本タスクはレバーを引く/引かないのGo/No-Go型で、2択（2AFC）課題のような「切り替え先」が存在しないため構造的に馴染まない。既存のAction History / Reward History（指数減衰）が同種の役割を果たす。
* **Consecutive Failures（Cazettes 2025式、報酬で即時リセットされるハードリセット型カウンタ）**: 不採用。既存のReward History（指数減衰）と数学的に異なる推論型変数だが、入力次元を増やさずDynamic化と観測モデル2系統の実装に注力するため見送る。H1（運動的特徴 vs 内部状態的特徴の皮質相関シフト）の検証を強化する目的で将来再検討しうる。

## 3. データ前処理仕様

[requirements_ver4.md](requirements_ver4.md) 3節（30Hzのギャップ埋め・ノイズ除去・Onset検出、保持時間測定時の生信号フォールバック、CSVとNWBの `merge_asof` 結合、試行ベースの構造化）をそのまま継承する（変更なし）。

## 4. 入出力変数定義 (Design Matrix)

### 4.1 目的変数 (Output: $y_k$) — 観測モデルごとに2通り

両系統とも、試行タイプの判定は2節（＝Ver.4 2.1節）に一致する。同じ試行テーブルから目的変数だけを作り分ける。

* **系統A（Bernoulli）**: $y_k^{A} \in \{0,1\}$。試行 $k$ のWindow内にAction（Onset）が存在すれば1、無ければ0。試行タイプで言えば No Reaction のみ0、他の3タイプは1。Ver.4 4.1節と同じ定義。
* **系統B（Categorical）**: $y_k^{B} \in \{\text{Success},\ \text{No Reaction},\ \text{Short Pull},\ \text{No Sound Pull}\}$。ラベルそのものを目的変数とし、「Actionの有無」へ潰さない。
  * 参照カテゴリ: **No Reaction**（5.1節の識別性制約でGLM重みを0に固定する基準）。押下を伴わない唯一のカテゴリであり、他の3カテゴリを「何もしない」からの逸脱として解釈できる。
* 系統Aは系統Bの粗視化になっている（$y_k^A = \mathbb{1}[y_k^B \neq \text{No Reaction}]$）。この包含関係が5.5節の周辺化による比較を可能にする。

補助量（両系統で共通。History計算に使うもので、目的変数そのものではない）:

* 行動有無 $a_k \in \{0,1\}$: $y_k^B$ が No Reaction 以外なら1、No Reaction なら0（＝ $y_k^A$ と同値）。
* 報酬 $Reward_k \in \{0,1\}$: $y_k^B$ が Success なら1、それ以外は0。

### 4.2 入力変数 (Input Regressors: $x_k$) — 4次元

[requirements_ver4.md](requirements_ver4.md) 4.2節の4変数のみを用いる。2.1節の試行インデックス $k$ で計算し、両系統で同一の入力を使う。

1. **Bias** $x_{bias,k}$: 常に1。
2. **Stimulus** $x_{stim,k}$: 音提示試行（Success / No Reaction / Short Pull）は1、No Sound Pull は0。
3. **Action History** $x_{hist,k}$: $h_k = a_{k-1} + \alpha_{act} \cdot h_{k-1}$。4.1節の補助量 $a$ を用いる（系統Aでは $a = y^A$ なのでVer.4 4.2節の定義と一致し、系統Bでも同じ値になる。したがって入力は両系統で完全に同一）。当該試行 $k$ の行動は含めない。
4. **Reward History** $x_{rew,k}$: $r_k = Reward_{k-1} + \alpha_{rew} \cdot r_{k-1}$。

減衰率 $\alpha_{act}$ / $\alpha_{rew}$ は [requirements_ver4.md](requirements_ver4.md) 5節の範囲を継承する。

## 5. Dynamic GLM-HMMの定式化（観測モデル2系統）

Cuturela et al. 2024の"dynamic GLM-HMM"に準拠し、セッション $s$ をtask-day（$s=1,\dots,15$）に対応させる。5.2節以降の動的構造・推論・ハイパーパラメータ選択は両系統で共通で、差分は5.1節の観測モデルとそれに伴う重みの形だけ。

### 5.1 観測モデル

#### 系統A: Bernoulli（Ver.4継承、Cuturela et al. 2024と同形）

試行 $t$・day $s$ における二値行動 $y_t^s\in\{0,1\}$ は、状態 $z_t^s=k$ のもとで、4次元の共変量ベクトル $x_t^s$（4.2節）と状態別GLM重み $w_k^s$ のロジスティック関数で決まる。

$$p(y_t^s \mid x_t^s, z_t^s=k) = \frac{\exp(-(1-y_t^s)\, w_k^s \cdot x_t^s)}{1 + \exp(-w_k^s \cdot x_t^s)}$$

* 自由パラメータは状態あたり $D=4$ 個。$K=3$ なら1 dayあたり12個。
* Cuturela et al. 2024の公開実装がそのまま対応する形なので、実装リスクが最も低い。既定の系統とする。

#### 系統B: Categorical（4値）

試行タイプ $y_t^s \in \{1,\dots,C\}$（$C=4$）が、状態別・カテゴリ別GLM重み $w_{k,c}^s$ の多項ロジット（softmax）で決まる。

$$p(y_t^s = c \mid x_t^s, z_t^s=k) = \frac{\exp\!\left(w_{k,c}^s \cdot x_t^s\right)}{\sum_{c'=1}^{C}\exp\!\left(w_{k,c'}^s \cdot x_t^s\right)}, \qquad w_{k,\,\text{No Reaction}}^s \equiv 0$$

* 参照カテゴリ（No Reaction）の重みを0に固定するのは識別性のため。自由パラメータは状態あたり $(C-1)\times D = 3\times4 = 12$ 個で系統Aの3倍。$K=3$ なら1 dayあたり36個。
* 状態の解釈は「引きやすさの違い」から「4タイプの出方の違い」に広がる。同じ「引く」でもSuccessに至りやすい状態とShort Pullに落ちやすい状態を区別できる点が、系統Aに対する利得になる。
* $C=2$（No Reaction vs それ以外）に落とすと、パラメータ化こそ違うが系統Aと同じ分布族になる。つまり系統Bは系統Aの厳密な一般化で、$C$ を切り替える実装として両者を1本のコードで扱える。
* **Hulsey et al. 2024との違い**: Hulsey et al. 2024の多項GLM-HMM（[reference/hulsey2024_arousal_movement.md](../reference/hulsey2024_arousal_movement.md) 41-46行）は、全カテゴリ（L/R/No response）が独自の重み $w_c^{(k)}$ を持つ**対称パラメータ化**で、識別性は特定カテゴリの固定ではなく、重みに課す平均0・分散2のガウス事前分布（MAP推定）に委ねている。本Verの参照カテゴリ固定はこれとは異なる識別性の扱いであり、Hulseyのコード（`ssm`改変版）をそのまま流用する前提を置いてはならない。参照カテゴリ固定を選ぶ理由は、上記の $C=2$ 一般化関係が厳密に成り立つ（系統Aとの検証テストに使える）ため。

### 5.2 動的パラメータ（dayをまたぐ緩やかな変化、両系統で共通）

$$w_{\theta}^{s} \sim \mathcal{N}(w_{\theta}^{s-1},\ \alpha^2) \qquad P_i^{s} \sim \mathrm{Dir}(\kappa A_i + 1)$$

* $w_\theta^s$: day $s$ のGLM重み。添字 $\theta$ は系統Aでは（状態 $k$、入力次元 $d$）、系統Bでは（状態 $k$、カテゴリ $c$、入力次元 $d$）を指す。いずれも前dayの重みを中心とするガウス事前分布に従い、dayをまたいで緩やかに変化する。系統AはCuturela et al. 2024の式1そのもの、系統Bはそれにカテゴリ添字を加えた形。
* $\alpha$: 変動幅ハイパーパラメータ。Cuturela et al. 2024は状態・次元ごとの $\alpha_{k,d}$ を定義しているが、グリッドサーチでは単一スカラーを用いている。本Verも単一スカラーに束ねる（系統Bはパラメータ数が3倍なので、個別に持つとグリッドサーチが現実的でない）。
* $P^s$: day $s$ の $K\times K$ 遷移行列。大域推定遷移行列 $A$ を中心としたディリクレ事前分布から生成され、$\kappa$（濃度パラメータ）が大きいほど大域行列に近づく。
* 極限 $\alpha\to0,\ \kappa\to\infty$ で全dayが同一パラメータとなり、全日共通の単一（静的）GLM-HMMと等価になる。

### 5.3 状態数K

Ver.4と同様に固定し、cross-validationで選択する（既定値3）。dayごとに変えない。

### 5.4 推論

* **実装のベース**: Cuturela et al. 2024の公開実装を出発点とする（リポジトリURLは [reference/cuturela2024_internal_states_early.md](../reference/cuturela2024_internal_states_early.md) に未記録。参照時に確認して追記する）。
* **2系統の切り分け方**: 観測モデルを差し替え可能なコンポーネントとして切り出し、EMの骨格（前向き後向き、遷移行列の更新、day間の事前分布）を共有する。観測モデル側が提供するのは次の2つだけ。
  1. 対数観測尤度 $\log p(y_t^s \mid x_t^s, z_t^s=k)$（E-stepが使う）。
  2. 重みに関するECLLの勾配（M-stepのBFGSが使う）。

  系統Aはこの2つが公開実装のものと一致するため、そのまま利用できる。系統Bは同じインタフェースに多項ロジット版を実装する。系統Bを $C=2$ で走らせた結果が系統Aと一致することを、実装の検証テストに使う（5.1節の一般化関係）。
* **初期値**: 全15日を連結した静的GLM-HMMを学習し、day別パラメータの初期値とする（Cuturela et al. 2024と同じ手続き）。系統Aの静的モデルは `ssm` の標準機能で学習できる。系統Bは `ssm` がcategorical/multinomial GLM-HMMを標準搭載していないため、上記の自前実装で静的モデル（$\alpha\to0$, $\kappa\to\infty$ に相当）を学習する。
* **MAP推定 + EM**: dayごとに前向き後向きアルゴリズムでExpected Complete-Data Log-Likelihood（ECLL）を計算するEステップと、ECLL＋式5.2の対数事前分布を最大化するMステップを繰り返す。GLM重みはscipy.optimizeのBFGS法、遷移行列は各行の和が1という制約下でラグランジュ未定乗数法により閉形式で更新する。
* **完全分離への対処（系統Bのみ）**: $x_{stim,k}=0$ であることとNo Sound Pullであることは定義上一対一に対応する（音提示外の押下だけがNo Sound Pull）ため、Stimulus次元で完全分離が起き、正則化なしでは対応する重みが発散する。5.2節のガウス事前分布がMAP推定の正則化として働くが、初日（$s=1$）には前dayが無いため別途 $\mathcal{N}(0,\sigma_0^2)$ を置く必要がある。$\sigma_0$ は他のハイパーパラメータと同様にグリッドサーチで決める。系統Aでは No Sound Pull も $y=1$ に潰れるため、この問題は起きない。

### 5.5 ハイパーパラメータ・状態数の選択と、2系統の比較

* **系統ごとのハイパーパラメータ選択**: 状態数 $K\in\{1,\dots,5\}$ と変動幅 $\alpha$ をグリッドサーチし、held-outデータのtest log-likelihoodをcross-validationで比較して選ぶ。遷移行列側の $\kappa$、系統Bの初日の事前分散 $\sigma_0$ も同様。$K$ は系統ごとに独立に選ぶ（4値の方が多い状態数を要求する可能性があり、揃える理由がない）。
* **系統AとBの比較**: 目的変数の台が違うため、test log-likelihoodをそのまま並べても比較にならない。系統Bの予測分布を「Action有無」へ周辺化し（$p(y^A=0) = p(y^B=\text{No Reaction})$）、系統Aと同じ台の上でheld-out log-likelihoodを比較する。系統Bが4タイプの区別に使ったパラメータが、二値の予測精度も改善しているかを見る指標になる。
* **周辺化で測れないもの**: 系統Bの本来の利得（SuccessとShort Pullを分ける状態が見つかるか）は周辺化すると消える。そのため比較は上記の数値指標だけで決めず、状態別の試行タイプ構成（`plot_state_behavior()` 相当）と、6節の皮質デコード精度——どちらの系統の状態がより皮質からデコードしやすいか——を併せて判断する。皮質デコード精度は状態定義に皮質を使っていないため、系統選択の外部基準として使える。

## 6. 皮質活動を用いた独立検証パイプライン（RQ1・RQ2）

皮質活動（`processing/ophys/DfOverF`、44 ROIのΔF/F）はDynamic GLM-HMMの入力には一切使わない。Phase 1（5節）で得た状態を目的変数として、皮質からの独立デコーディングを行う。**手法の主参照はAloor et al. 2026**（[reference/aloor2026_stochastic_choices.md](../reference/aloor2026_stochastic_choices.md)、GLM-HMM状態を広視野イメージングからデコードする直接の先例）。Cazettes et al. 2025（[reference/cazettes2025_facial_expressions.md](../reference/cazettes2025_facial_expressions.md)）は副系統（手法2）として、結論が手法選択に依存しないことの確認に用いる。

### 6.1 デコード対象

Phase 1で得た試行ごとの状態。Aloorに倣い $P(z)\geq0.8$ を閾値として離散状態に割り当て、閾値未満の試行はデコード解析から除外する。観測モデル2系統（5.1節）それぞれの状態に対して同じ手続きを実行し、どちらの状態がより皮質からデコードしやすいかを5.5節の系統比較の外部基準にする。

### 6.2 デコード入力

`ophys/DfOverF`（44 ROI、30Hz）。

* **locaNMFは適用しない**。Aloorは生ピクセルの広視野データをlocaNMFで73〜80成分に分解するが、本データセットのNWBには画素データが含まれず、既に44 ROI（片半球22×両半球）へ集約済みのΔF/Fしか無い（[data.md](data.md)）。ROI分解が上流で済んでいるため、Aloorのパイプラインのうち次元圧縮の段は不要かつ適用不可能。44 ROIをそのまま特徴の空間次元として扱う。
* **特徴量の構成**: Aloorの構成（基準イベントから±窓を0.25秒ビンで区切り、ビンごとの成分平均を試行×ビンの母集団ベクトルにする）を踏襲する。基準イベントは pull onset（押下の無いNo Reactionは cue onset）とする。窓幅・ビン幅はEDAで確定する。Ver.4 2.1節の試行タイプ別Windowで集約する方式（試行タイプごとに窓長が違う）は採らない。窓長が試行タイプと強く相関し、集約値に窓長そのものの影響が残るため（[CLAUDE.md](../CLAUDE.md) の顔特徴の集計窓の項）。

### 6.3 デコードモデル

$L_2$正則化線形SVM（$C=1$、Aloor式）。2-fold cross-validationを20回繰り返した平均デコード精度を報告する。副系統としてCazettes式の正則化multinomial logistic回帰（elastic net、$\alpha=0.5$、nested cross-validation）も並行して回し、両者で結論が一致することを確認する。44 ROI×時間ビンに対し試行数が少ない（音提示試行は1日あたり約170件）ため、いずれの系統でも正則化を必須とする。

### 6.4 試行バランシング

状態occupancyは学習が進むほど偏る。単純にプールすると「学習日による皮質活動の変化」と「状態そのものによる活動の違い」が交絡するため、Aloorに倣い各day内で状態×試行タイプの試行数が釣り合うようサブサンプルしてからデコーダを学習する。

### 6.5 有意性判定

ラベルをpermutationしたchanceレベルの精度分布を作り、実デコード精度が有意に上回るかを検定する。これがRQ1（生物学的妥当性）の直接の判定基準となる。

### 6.6 cross-condition / cross-time decoding

Aloor式。ある条件（例: 報酬あり試行）で学習したデコーダを別条件（報酬なし試行）でテストする、またはある時間ビンで学習したデコーダを別の時間ビンでテストする（train time × test timeの行列を作る）ことで、皮質上の状態表現が課題文脈・時間をまたいで汎化するか、それとも文脈と絡んでいるかを判定する。Aloorではマッチングペニー課題の状態デコーダが報酬あり↔なしをまたいで汎化しなかった。

### 6.7 ラグ解析（Cazettes式、副系統）

Cazettes et al. 2025のsliding-window lag分析（200msビン、75%オーバーラップ）を踏襲し、試行内で時間窓をずらしながら皮質デコード精度がピークになるタイミングを特定する。デコード精度・最適ラグをday indexに回帰し、学習に伴う変化（結合強度の増大、ラグの短縮）を検証する（RQ2・H2）。

### 6.8 運動的特徴 vs 内部状態的特徴（H1向け）

顔・身体特徴（Ver.4 4.3節の9次元）はモデル入力から外れたため、皮質活動の説明対象として独立に使える。皮質活動を入力として、(a) 運動的特徴（顔・身体のPosition/Speed）、(b) 内部状態的特徴（HMM状態の事後確率、Action History / Reward History）のそれぞれを目的変数とする2系統の回帰・分類を行い、説明力（cross-validated $R^2$ または分類精度）の優劣がday indexでどうシフトするかを見る。顔特徴の集計窓は6.2節と同じpull onset基準の固定窓（`face_window_bounds(window="onset_fixed")`）を用い、窓長のアーティファクトを避ける。

**報酬関連の身体信号は、窓長ではなく別特徴として明示的に定義する**。pull onset基準の固定窓は報酬フェーズを構造的に窓の外に置くため、報酬後の散瞳のような信号は上記の9次元には入らない。これを使いたい場合、試行タイプ別Windowに戻して「Successだけ窓が報酬フェーズまで伸びる」状態にしてはならない。その窓では瞳孔特徴が実質「報酬が出たか」の代理変数になり（`VG1GC-66`全日で、既定窓の`x_pupil`はtrial_typeによる分散説明率0.12・`pull_duration`との相関0.28だが、固定窓ではどちらも0.00に落ちる。[CLAUDE.md](../CLAUDE.md)、ノート16の2.7節）、皮質から瞳孔をデコードした結果が「皮質から報酬の有無をデコードした」ことの言い換えになってしまうため。

* **定義**: 結果確定時刻（音提示試行の`stop_time`）を基準イベントとする固定長窓で瞳孔径の`median`を取り、9次元とは別の変数 $x_{pupil,post}$ として扱う。窓幅は6.2節と同様にEDAで確定する。
* **全試行タイプで同じ定義**: Success / Short Pull / No Reaction のいずれにも`stop_time`は存在するので、報酬の有無で欠測にならない。報酬あり試行と報酬なし試行の対比そのものが観測対象になる。音提示外の押下（No Sound Pull）は結果確定時刻を持たないため、この特徴は定義しない。
* **役割**: 状態定義には使わない（モデル入力に入れない）。皮質デコードの目的変数、または報酬応答の記述統計として使う。

## 7. スコープ外（今後の拡張）

* **皮質→顔デコードによる脳-身体結合の経時変化（H2）**: 状態別に「皮質活動から顔特徴をどれだけ予測できるか」を測り、その精度とラグがdayとともに変化するかを見る解析。本Verでは行動のみで状態を定義してモデルを確立することを優先し、スコープ外とする。顔特徴を状態定義から外したことで、この解析は循環を持たずに実施できる。
* **emissionのさらなる細分化（RQ3向け）**: Short Pullは「引き足りなかった」を意味せず、大半は接触が一瞬途切れた試行で、締め切り超過 / 接触途切れ / 本当に引き足りない の3類型に分解できる（[CLAUDE.md](../CLAUDE.md)、[data.md](data.md)）。この分解をカテゴリとして系統Bのemissionに載せる（$C=6$ に増やす）かは未定。載せずに、推定した状態のもとで事後的に分解する方針も取りうる。

## 8. 実装・解析フロー (Workflow)

Step 1–3は両系統で共通（1本の試行テーブルを作る）。Step 4–7を系統A・Bそれぞれで走らせ、Step 8で比較してから、Step 9以降を採用系統で進める。

1. **Load Data**: [requirements_ver4.md](requirements_ver4.md) 6節のStep 1–3（Load〜Trial Extraction）をそのまま実行し、全15日分の試行を抽出する。
2. **試行系列の確定**: 2.1節に従い、Second Pullを属する音提示試行に吸収し、残る4タイプを時系列順の単一系列として $k$ を振る。
3. **Feature Engineering**: 4.2節の4次元入力と、4.1節の2通りの目的変数（$y^A$, $y^B$）・補助量（$a_k$, $Reward_k$）を計算する。入力は両系統で同一なので1度だけ作る。
4. **Global Pooled Fit**: 全15日を連結して静的GLM-HMMを学習し、Dynamic GLM-HMMの初期値を得る（系統ごとに実施）。
5. **Dynamic GLM-HMM学習**: 5.4節の手続きでday別パラメータ $\{P^s, w^s\}$ を推定する（系統ごとに実施）。
6. **State Decoding**: dayごとに状態事後確率・Viterbi系列を得る（系統ごとに実施）。
7. **Cortex Decoding**: 6節の手続きで皮質からの独立デコードとcross-condition/cross-time解析を行う（RQ1）。系統比較の外部基準として使うため、両系統の状態に対して実施する。
8. **系統の比較**: 5.5節の周辺化test log-likelihood、状態別の試行タイプ構成、Step 7の皮質デコード精度を突き合わせ、主系統を決める。両系統の結果は捨てずに併記する。
9. **Coupling Analysis**: デコード精度・最適ラグをday indexに回帰する（RQ2/H2）。
10. **Error Decomposition**: 全日データをプールし学習段階別にミス試行を分解する（RQ3/H3）。

## 変更履歴

* 2026-08-28: 初版（Ver.4を継承した13次元入力・Bernoulli emissionのDynamic GLM-HMM＋皮質による独立検証）。
* 2026-08-31: 観測モデルを二値（系統A、Ver.4継承）と4値カテゴリカル（系統B、Success / No Reaction / Short Pull / No Sound Pull）の2系統に整理し、試行系列・入力・動的構造・皮質パイプラインを共通化して差分を観測モデルだけに閉じる設計に変更（1・4.1・5.1・5.5・8節）。Second Pullを独立試行から外し、属する音提示試行に吸収（2.1節）。入力を行動4次元のみに限定し顔9次元を不採用に（2.2・4.2節）。Cuturela et al. 2024に公開実装がある前提へ推論節を修正（5.4節）。皮質手法の主参照をAloor et al. 2026に変更し、locaNMFは本データセットに適用不可として除外、Cazettes et al. 2025を副系統に降格（6節）。皮質→顔デコードによる結合解析をスコープ外に整理（7節）。
* 2026-08-31（同日追記）: 系統BをHulsey et al. 2024と比較したところ、参照カテゴリ固定（本Ver）とHulseyの対称パラメータ化＋ガウス事前分布は識別性の扱いが異なると判明し、5.1節に相違点を明記（Hulseyのコードをそのまま流用できる前提を否定）。Second Pull吸収時にWindow境界（`t_end`）を延長しない旨を2.1節に追記。8節冒頭の説明文がステップ番号とずれていたため修正。報酬後の瞳孔を、試行タイプ別Windowの窓長に紛れ込ませず結果確定時刻基準の別特徴として定義する方針を追加（6.8節）。
