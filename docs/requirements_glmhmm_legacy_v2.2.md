> **Legacy**: この文書は Ver.2.2 時点の要件定義で、[requirements_glmhmm.md](requirements_glmhmm.md)（Ver.3）に置き換えられた旧仕様です。参照用に保存しています。

# GLM-HMM Analysis: Requirement Definition Document (Ver.2.2)

## 1. プロジェクト概要 (Overview)

* **目的**: マウスの聴覚Go/Wait課題データから、潜在的な内部状態（戦略）の遷移を説明するGLM-HMMモデルを構築する。
* **分析対象**: 16匹のマウス、Day1-15の時系列行動データ。
* **採用モデル**: **Bernoulli GLM-HMM** (Ashwood et al., 2022 準拠)。
* 観測モデル: ベルヌーイ分布（行動の有無 0/1）。
* 潜在状態: 離散的な状態遷移（2～3状態を想定）。



## 2. 実験パラダイムと行動定義 (Task & Behavior)

* **タスク構造**:
* 音提示あり ( $Stimulus=1$) → 一定時間以上のレバー引きで報酬。
* 音提示なし ( $Stimulus=0$) → レバーを引いても報酬なし（自発的な引き）。
* **No-Go刺激は存在しない**（Silence vs Sound のみ）。


* **試行の分類**:
* **Success (報酬あり)**: 音提示中に閾値以上の長さでレバーを引き、報酬を得たケース。
* **No Reaction (無反応)**: 音提示があったがレバーを引かなかったケース。（旧名称: Miss）
* *補足*: 解析（プロット）上は「音刺激開始時間」をイベント発生点とするが、モデル学習上は「音提示中の全区間」として扱う（後述）。


* **Unrewarded Pull (非報酬レバー引き)**: 音提示中にレバーを引いたが、報酬が出なかったケース。（旧名称: Short Pull等を統合）
* **Short Pull**: 引き時間が短く報酬条件を満たさなかったもの。
* **Second Pull**: 同一音刺激内で既に報酬を得た後の、2回目以降の引き（報酬は出ない）。





## 3. データ前処理仕様 (Data Preprocessing)

### 3.1. 時間分解能 (Time-binning)

* **元データ**: 約30Hz (0.033s/frame)。
* **処理**: 3フレームを1ビンにダウンサンプリングし、OR論理で結合。
* **Bin Width**: **0.1 sec (100ms)**。
* **結合ルール**: ビン内にイベント（音、行動開始）が1フレームでも含まれれば `1` とする。

### 3.2. データの不均衡処理 (Handling Imbalance)

* **ITIカット (Truncation)**:
* 音刺激も行動もない状態（Silence & No Action）が **10秒** 以上続いた場合、その中間を削除してデータを短縮・連結する。
* 連結点にはマスク処理（Masking）またはリスト分割を行い、HMMの遷移計算が連続しないようにする。



### 3.3. レバー引きの定義 (Lever Action)

* **検出基準**: レバー変位の開始（Onset）を検出。
* **閾値 (Threshold)**: 継続時間 **0.04 sec (40ms)** 以上を有効な引きとする。それ未満はノイズとして $0$ 扱い。

## 4. 入出力変数定義 (Design Matrix)

### 4.1. 目的変数 (Output: $y_t$)

* **型**: Binary (0 or 1).
* **$y_t = 1$ の条件**:
* 有効なレバー引き（Onset）があったビン。
* **Success** および **Unrewarded Pull (Short / Second)** のすべてを含む。


* **$y_t = 0$ の条件**:
* レバーを引いていない (**No Reaction** 含む)。
* または、引き継続中（Hold状態）。
* または、ノイズ（<0.04s）。



### 4.2. 入力変数 (Input Regressors: $x_t$)

以下の4つの列（Covariates）を作成する。

1. **Bias (バイアス項)**
* 値: 常に `1`。
* 役割: 音がない時の基礎的なレバー引き確率（衝動性）を学習。


2. **Stimulus (音刺激項)**
* 値: 音が提示されているビンは `1`、それ以外は `0`。
* **データ表現 (Continuous Representation)**:
* 音刺激開始の瞬間だけでなく、**音が提示されている期間のすべてのビン**において `1` とする。


* **学習ロジック**:
* **No Reaction** の場合: $x_{stim}=1$ かつ $y_t=0$ のデータが連続して入力される。モデルはこの「音があるのに引かない」状態の積み重ねから、抑制状態を学習する。


* 役割: 音への感度を学習。


3. **Action History (行動履歴項)**
* 実装: **指数減衰 (Exponential Decay)**。
* 定義: $h_t = y_{t-1} + \alpha_{act} \cdot h_{t-1}$ （必ず1ラグずらすこと）
* 役割: 不応期や慣性の学習。Success, Unrewarded Pull を問わず、引いた事実は履歴に残る。


4. **Reward History (報酬履歴項)**
* 実装: **指数減衰 (Exponential Decay)**。
* 定義: $r_t = Reward_{t-1} + \alpha_{rew} \cdot r_{t-1}$ （必ず1ラグずらすこと）
* **重要**: $Reward_{t-1}=1$ となるのは **Success** の次時点のみ。
* **Unrewarded Pull (Short / Second)** の場合、引いていても報酬は出ていないため、 $Reward_{t-1}=0$ として処理される。



## 5. ハイパーパラメータ設定 (Parameters)

実装に使用する具体的な数値。

| Parameter | Value | Logic / Derivation |
| --- | --- | --- |
| **Time Bin** | **0.1 s** | Downsampling 30Hz by factor of 3 |
| **Threshold** | **0.04 s** | Noise filtering threshold |
| **Action Window** | **1.0 s** | Decays to 10% at 1.0s (10 bins) |
| **Action Alpha ( $\alpha_{act}$)** | **~0.80** | $\exp(\ln(0.1)/10)$ |
| **Reward Window** | **4.0 s** | Decays to 10% at 4.0s (40 bins) |
| **Reward Alpha ( $\alpha_{rew}$)** | **~0.94** | $\exp(\ln(0.1)/40)$ |
| **States (K)** | **2, 3** | Compare Log-likelihood or CV score |

## 6. 解析フロー (Workflow)

1. **Preprocessing**: 生データを読み込み、上記ルール（特にStimulusの連続性とHistoryのシフト）でBinningと変形を行う。
2. **Train GLM-HMM**: `ssm` ライブラリ等を使用し、全個体または個体ごとに学習。
* *注意*: 初期値依存を避けるため、複数のランダムシードで試行する。


3. **State Decoding**: 事後確率を用いて各時刻の潜在状態を推定。
4. **Analysis**: 状態ごとの重み（Weights）を比較し、「Engaged」「Impulsive」「Disengaged」等の解釈を行う。
