# 要件定義書
# GLM-HMM Analysis: Requirement Definition Document (Ver.5.0)

設計のみ・未実装（notebooks・srcに対応する実装なし、2026-08-28時点）。[docs/RQ.md](RQ.md) のRQ2（学習ダイナミクス）・RQ1（生物学的妥当性）を検証するための拡張。試行定義・前処理・入力変数は [requirements_ver4.md](requirements_ver4.md) をそのまま継承し、本書では **Ver.4からの差分（日をまたいだ動的学習、皮質を用いた独立検証）のみ** を定義する。

## 1. プロジェクト概要 (Overview)
* 目的: Ver.4（試行単位、日ごと独立学習）を、Day 1–15の学習過程を貫くDynamic GLM-HMMへ拡張し、皮質活動を独立検証チャンネルとして統合することで、内的従事状態の学習ダイナミクス（RQ2）と生物学的妥当性（RQ1）を定量検証する。
* 分析対象: 個体内、Day 1–15の全task-day（Dynamic GLM-HMMではセッション＝dayとして扱う）。
* 採用モデル: Bernoulli GLM-HMMのDynamic拡張（Cuturela et al. 2024, [reference/cuturela2024_internal_states_early.md](../reference/cuturela2024_internal_states_early.md) 準拠）。
* 観測モデル: ベルヌーイ分布（Ver.4と同一）。
* 分析単位: 1試行（1 Trial）を1データポイントとする（Ver.4と同一）。
* **Ver.4との違い**:
  1. 状態推定: 「日ごと独立学習」→「Dynamic GLM-HMM」（GLM重み・遷移行列が日をまたいで緩やかに変化し、状態ラベルが日をまたいで対応する）。
  2. 皮質活動の統合: 新規。GLM-HMMの入力には使わず、独立の生物学的妥当性検証チャンネル（RQ1）として用いる。
  3. 試行定義・前処理・入力変数（Bias/Stimulus/Action History/Reward History＋顔9次元の13次元）は変更なし。Win-stay-lose-switch（Ashwood式1ラグ積）とConsecutive Failures（Cazettes式ハードリセットカウンタ）は検討したうえで不採用（3節参照）。

## 2. 試行定義とデータ抽出、3. データ前処理仕様、4.1〜4.2 出力・入力変数
[requirements_ver4.md](requirements_ver4.md) の2節・3節・4.1節・4.2節・4.3節をそのまま継承する（変更なし）。

### 2.1 検討したが不採用の入力（差分の記録）
* **Win-stay-lose-switch（Ashwood 2022式、$2y_{t-1}-1$ × 前試行報酬の1ラグ積）**: 不採用。本タスクはレバーを引く/引かないのGo/No-Go型で、2択（2AFC）課題のような「切り替え先」が存在しないため構造的に馴染まない。既存のAction History / Reward History（指数減衰）が同種の役割を果たす。
* **Consecutive Failures（Cazettes 2025式、報酬で即時リセットされるハードリセット型カウンタ）**: 不採用。既存のReward History（指数減衰）と数学的に異なる推論型変数だが、入力次元を増やさずDynamic GLM-HMMの実装に注力するため見送った。H1（運動的特徴 vs 内部状態的特徴の皮質相関シフト）の検証を強化する目的で将来再検討しうる。

## 5. Dynamic GLM-HMMの定式化（Ver.4からの主要な拡張）

Cuturela et al. 2024の"dynamic GLM-HMM"に準拠し、セッション $s$ をtask-day（$s=1,\dots,15$）に対応させる。

### 5.1 観測モデル
試行 $t$・day $s$ における二値行動 $y_t^s\in\{0,1\}$ は、状態 $z_t^s=k$ のもとで、13次元の共変量ベクトル $x_t^s$（[requirements_ver4.md](requirements_ver4.md) 4.2–4.3節）と状態別GLM重み $w_k^s$ のロジスティック関数で決まる（Ver.4と同じBernoulli GLMの枠組み）。

$$p(y_t^s \mid x_t^s, z_t^s=k) = \frac{\exp(-(1-y_t^s)\, w_k^s \cdot x_t^s)}{1 + \exp(-w_k^s \cdot x_t^s)}$$

### 5.2 動的パラメータ（dayをまたぐ緩やかな変化）

$$w_{k,d}^{s} \sim \mathcal{N}(w_{k,d}^{s-1},\ \alpha_{k,d}^2) \qquad P_i^{s} \sim \mathrm{Dir}(\kappa A_i + 1)$$

* $w_{k,d}^s$: day $s$・状態 $k$・入力次元 $d$（13次元のいずれか）のGLM重み。前dayの重みを中心とするガウス事前分布に従い、dayをまたいで緩やかに変化する。
* $\alpha_{k,d}$: 状態・次元ごとの変動幅ハイパーパラメータ。大きいほどday間で重みが大きく変化できる。
* $P^s$: day $s$の $K\times K$ 遷移行列。大域推定遷移行列 $A$ を中心としたディリクレ事前分布から生成され、$\kappa$（濃度パラメータ）が大きいほど大域行列に近づく。
* 極限 $\alpha_{k,d}\to0,\ \kappa\to\infty$ で全dayが同一パラメータとなり、Ver.4の静的GLM-HMM（ただし日ごと独立ではなく全日共通の単一モデル）と等価になる。

### 5.3 状態数K
Ver.4と同様に固定し、cross-validationで選択する（既定値3）。dayごとに変えない。

### 5.4 推論
* 初期値: 全15日を連結して`ssm`で標準GLM-HMMを学習した結果を、day別パラメータの初期値として用いる（Cuturela et al. 2024と同じ手続き）。
* MAP推定 + EM: dayごとに前向き後向きアルゴリズムでExpected Complete-Data Log-Likelihood（ECLL）を計算するEステップと、ECLL＋式5.2の対数事前分布を最大化するMステップを繰り返す。GLM重みはscipy.optimizeのBFGS法、遷移行列は各行の和が1という制約下でラグランジュ未定乗数法により閉形式で更新する。
* `ssm`ライブラリはday間の動的事前分布をネイティブサポートしないため、M-stepに事前分布項（式5.2）を追加するカスタム実装が必要（Cuturela et al. 2024に公開コードの記載はなく、自前で実装する）。

### 5.5 ハイパーパラメータ・状態数の選択
状態数 $K\in\{1,\dots,5\}$ と変動幅 $\alpha$ をグリッドサーチし、held-outデータのtest log-likelihoodをcross-validationで比較して選ぶ（Cuturela et al. 2024と同じ手続き）。遷移行列側の $\kappa$ も同様にグリッドサーチする。

## 6. 皮質活動を用いた独立検証パイプライン（RQ1・RQ2、新規）

皮質活動（`processing/ophys/DfOverF`、44 ROIのΔF/F）はDynamic GLM-HMMの入力には一切使わない。Phase 1（5節）で得た状態を目的変数として、皮質からの独立デコーディングを行う。方法論はCazettes et al. 2025（[reference/cazettes2025_facial_expressions.md](../reference/cazettes2025_facial_expressions.md)）の表情/神経活動からのDV復号設計を、デコード対象を離散状態に置き換えて踏襲する（Aloor et al. 2026がGLM-HMM状態を広視野イメージングから直接デコードする対応する先例）。

### 6.1 デコード対象
Phase 1で得た試行ごとの状態（離散Viterbi状態、または状態事後確率ベクトル）。

### 6.2 デコード入力
`ophys/DfOverF`（44 ROI）を、[requirements_ver4.md](requirements_ver4.md) 2.1節の試行タイプ別Windowでtrial単位に集約（medianまたはmean、集約方法はEDAで決定）。

### 6.3 デコードモデル
正則化multinomial logistic回帰（elastic net、$\alpha=0.5$、nested cross-validationでハイパーパラメータ選択。Cazettes et al. 2025のGLM設計に準拠）。44 ROIに対しtrial数が少ない（1日あたり約163試行）ため正則化を必須とする。

### 6.4 有意性判定
ラベルをpermutationしたchanceレベルの精度分布を作り、実デコード精度が有意に上回るかを検定する。これがRQ1（生物学的妥当性）の直接の判定基準となる。

### 6.5 ラグ解析（RQ2・H2向け）
Cazettes et al. 2025のsliding-window lag分析（200msビン、75%オーバーラップ）を踏襲し、試行内で時間窓をずらしながら皮質デコード精度がピークになるタイミングを特定する。同じ解析を顔特徴側でも行い、両者のラグを比較する。デコード精度・最適ラグをday indexに回帰し、学習に伴う変化（結合強度の増大、ラグの短縮）を検証する。

### 6.6 運動的特徴 vs 内部状態的特徴（H1向け）
状態のGLM重みのうち、運動的特徴（顔・身体のPosition/Speed）と内部状態的特徴（Action History/Reward History、状態自体の事後確率）のどちらが皮質活動をより強く説明するかを、6.3の回帰を目的変数の切り替えで2系統（(a) 運動的特徴を目的変数、(b) 内部状態的特徴を目的変数）行うことで比較する。両者の説明力（cross-validated $R^2$または分類精度）の優劣がday indexでどうシフトするかを見る。

## 7. Emission拡張の検討（未確定、RQ3向け）

主系統は現行どおりBernoulli（5節のDynamic GLM-HMM）を用いる。RQ3（ミス試行の質的分解）をモデルの尤度自体に組み込む拡張として、Multinomial emission（Success / Short-or-Second Pull / No Reactionを区別する多値出力、Hulsey et al. 2024の3択拡張に準拠）を並行して検討中。適用範囲（Dynamic GLM-HMM全体に適用するか、RQ3専用のpooled/globalモデルに限定するか）は未確定。`ssm`はmultinomial GLM-HMMを標準搭載していないため、採用する場合はHulsey et al. 2024と同様の改造が別途必要になる。

## 8. 実装・解析フロー (Workflow)

1. Load Data: [requirements_ver4.md](requirements_ver4.md) 6節のStep 1–4（Load〜Feature Engineering）をそのまま実行し、13次元の試行系列を全15日分作る。
2. Global Pooled Fit: 全15日を連結し`ssm`で標準GLM-HMMを学習、Dynamic GLM-HMMの初期値を得る。
3. Dynamic GLM-HMM学習: 5.4節の手続きでday別パラメータ $\{P^s, w_k^s\}$ を推定する。
4. State Decoding: dayごとに状態事後確率・Viterbi系列を得る。
5. Cortex Decoding: 6節の手続きで皮質からの独立デコードとラグ解析を行う（RQ1）。
6. Coupling Analysis: 状態確率と皮質デコード確率の時系列相関・ラグをday indexに回帰する（RQ2/H2）。
7. Error Decomposition: 全日データをプールし学習段階別にミス試行を分解する（RQ3/H3）。
