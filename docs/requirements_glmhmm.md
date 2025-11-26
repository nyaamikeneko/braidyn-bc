# GLM-HMM Analysis: Requirement Definition Document (Ver.3.0)

## 1. プロジェクト概要 (Overview)
* **目的**: マウスの聴覚Go/Wait課題データから、潜在的な内部状態（戦略）の遷移を説明するGLM-HMMモデルを構築する。
* **分析対象**: 16匹のマウス、Day1-15の時系列行動データ。
* **採用モデル**: Bernoulli GLM-HMM (Ashwood et al., 2022 準拠)。
* **観測モデル**: ベルヌーイ分布（行動の有無 0/1）。
* **潜在状態**: 離散的な状態遷移（2～3状態を想定）。

## 2. 実験パラダイムと行動定義 (Task & Behavior)
* **タスク構造**:
    * 音提示あり ($Stimulus=1$): `state_task=1` の区間のみを指す。
    * 報酬フェーズ (`state_task=2`): 音は停止しているため $Stimulus=0$ として扱う。
    * 音提示なし ($Stimulus=0$): 上記以外。
* **イベント定義**:
    * **Action (Onset)**: レバーが「離れた状態(0)」から「引かれた状態(1)」へ変化した瞬間。時系列整形後のデータに基づき定義する。
    * **Reward (Event)**: `trial_outcome=success` となる試行の `pull_onset` 時刻。

## 3. データ前処理仕様 (Data Preprocessing)

### 3.1. 生データの整形 (30Hz Cleaning)
分析精度向上のため、Binning前に30Hz段階で以下の順序で時系列を整形する。実装関数: `process_glmhmm_data_refined`

1.  **Gap Filling (穴埋め)**:
    * レバーが一瞬離れたと検知された区間（$0$ の連続が 2フレーム以下）を $1$ で埋める。センサーノイズによる偽のOnset防止。
2.  **Noise Removal (ノイズ除去)**:
    * 上記処理後、レバー引きが極めて短い区間（$1$ の連続が 2フレーム以下）を $0$ に置換して削除する。
    * 閾値根拠: 2フレーム $\approx$ 0.066s > 0.04s (旧要件)。
3.  **Onset Detection**:
    * 整形済みデータの差分を取り、0から1へ変化した点を $Action=1$ とする。

### 3.2. 異種データの統合 (Data Merging)
* **課題**: CSV（行動）とNWB（報酬）でタイムスタンプが完全に一致しない。
* **解決策**: `pandas.merge_asof` を使用し、`direction='nearest'`（最近傍探索）で結合する。許容誤差（tolerance）は1フレーム分（約0.033s）とする。

### 3.3. 時間分解能 (Time-binning)
* **処理**: 30Hz $\rightarrow$ 10Hz (0.1s/bin) へのダウンサンプリング。
* **集約ルール**: `max` 集約（ビン内に1つでもフラグがあれば1）。実装関数: `create_design_matrix_v2`
* **Reward Debouncing**: ビニングによりRewardフラグが連続してしまった場合、先頭のビンのみ $1$ を残し、以降を $0$ にする（History計算での値の爆発を防ぐため）。

### 3.4. ITIカット (Truncation)
* **条件**: 音刺激もなく($x_{stim}=0$)、行動もない($y=0$)状態が **10秒** 以上続いた場合。
* **処理**: 該当区間でデータを切断し、モデル学習用ライブラリ（ssm等）に合わせて「時系列データのリスト（List of Arrays）」形式に変換する。実装関数: `split_data_by_iti`

## 4. 入出力変数定義 (Design Matrix)

### 4.1. 目的変数 (Output: $y_t$)
* **型**: Binary (0 or 1).
* **定義**: 該当ビン内に有効なOnset（Action）が存在すれば 1。

### 4.2. 入力変数 (Input Regressors: $x_t$)
以下の4つの列（Covariates）を作成する。

1.  **Bias ($x_{bias}$)**
    * 値: 常に 1。
    * 役割: 基礎的なレバー引き確率（衝動性）の学習。
2.  **Stimulus ($x_{stim}$)**
    * 値: `state_task=1` の区間を含むビンは 1。
    * 役割: 音刺激に対する感度の学習。
3.  **Action History ($x_{hist}$)**
    * 定義: $h_t = y_{t-1} + \alpha_{act} \cdot h_{t-1}$
    * 制約: 必ず **1ラグ ($t-1$)** ずらして計算する（自己回帰リーク防止）。
    * 役割: 不応期や慣性（連打癖）の学習。Gap Fillingにより、センサーノイズによる誤った連打判定は排除済み。
4.  **Reward History ($x_{rew}$)**
    * 定義: $r_t = Reward_{t-1} + \alpha_{rew} \cdot r_{t-1}$
    * 制約: $Reward_{t-1}$ はSuccess試行のOnset時点のみ1。Unrewarded Pullでは0。
    * 役割: 過去の報酬体験による強化の学習。

## 5. ハイパーパラメータ設定 (Parameters)

| Parameter | Value | Logic / Note |
| :--- | :--- | :--- |
| **Raw Sampling** | 30 Hz | ~0.033s / frame |
| **Gap Fill Limit** | 2 frames | $\le$ 0.066s の「離し」は無視 |
| **Noise Remove Limit** | 2 frames | $\le$ 0.066s の「引き」は削除 |
| **Bin Width** | 0.1 s | 3 frames aggregation |
| **Action Alpha** ($\alpha_{act}$) | ~0.80 | $\exp(\ln(0.1)/10)$, Window $\approx$ 1.0s |
| **Reward Alpha** ($\alpha_{rew}$) | ~0.94 | $\exp(\ln(0.1)/40)$, Window $\approx$ 4.0s |
| **ITI Cut Threshold** | 10.0 s | Silence & No Action duration |

## 6. 実装・解析フロー (Workflow)

1.  **Load Data**: CSVおよびNWBデータの読み込み。
2.  **Clean & Flag (30Hz)**: `process_glmhmm_data_refined` を実行。時系列整形とAction/Stimulus/Rewardフラグ立て。
3.  **Binning & Features (10Hz)**: `create_design_matrix_v2` を実行。ダウンサンプリングとHistory変数の計算（Lag処理含む）。
4.  **Formatting (List)**: `split_data_by_iti` を実行。ITIでの切断と、ssmライブラリ用フォーマットへの変換。
5.  **Train GLM-HMM**: モデル学習（初期値依存を避けるため複数シードで試行）。
6.  **Decoding & Analysis**: 状態推定と解釈。