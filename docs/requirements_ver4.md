# 要件定義書
# GLM-HMM Analysis: Requirement Definition Document (Ver.4.0)

## 1. プロジェクト概要 (Overview)
* 目的: マウスの聴覚Go/Wait課題データから、潜在的な内部状態（戦略）の遷移を説明するGLM-HMMモデルを構築する。
* 分析対象: 16匹のマウス、Day1-15の行動データ。
* 採用モデル: Bernoulli GLM-HMM。
* 観測モデル: ベルヌーイ分布（1試行における行動の有無 0/1）。
* 分析単位: 1試行（1 Trial）を1データポイントとして扱う。

## 2. 試行定義とデータ抽出 (Trial Definitions)
時系列データから以下の定義に基づき、各試行を抽出して1行のデータポイント（ $y_k, x_k$）とする。

### 2.1. 試行タイプ別の時間範囲と変数
各試行のラベル付けおよび変数の対応は以下の通りとする。

| 試行タイプ | 定義・時間範囲（Window） | x_stim | y | Reward |
| :--- | :--- | :--- | :--- | :--- |
| Success | 音提示中にレバーを引き報酬を得たケース（stim開始 〜 reward終了） | 1 | 1 | 1 |
| No Reaction | 音提示があったがレバーを引かなかったケース（stim提示期間） | 1 | 0 | 0 |
| Short Pull | 引き時間が短く報酬条件を満たさなかったもの（stim開始 〜 action終了） | 1 | 1 | 0 |
| Second Pull | 同一音刺激内での2回目以降のレバー引き（action開始 〜 action終了） | 1 | 1 | 0 |
| No Sound Pull | 音提示外のレバー引き（action開始 〜 action終了） | 0 | 1 | 0 |

音提示試行（上表の上位3タイプ）の判別は、`trial_outcome` が `success` か否かと、`pull_onset` が記録されているか否かで行う。`success` 以外は `pull_onset` があれば Short Pull、無ければ No Reaction とする。`trial_outcome` の `miss` / `failure` という文字列でこの2タイプを分けてはならない。NWB公式trialsテーブルとハッカソンCSV（`trials_L1L2.csv`）でこの2語の使い方が正反対であり、どちらのソースから読んだかで意味が反転するため（`pull_onset` の有無は両ソースで一貫している）。

## 3. データ前処理仕様 (Data Preprocessing)

### 3.1. 生データの整形 (30Hz Cleaning)
分析精度向上のため、試行抽出前に30Hz段階で時系列を整形する。

1. Gap Filling (穴埋め):
レバーが一瞬離れたと検知された区間（0 の連続が 2フレーム以下）を 1 で埋める。
2. Noise Removal (ノイズ除去):
レバー引きが極めて短い区間（1 の連続が 2フレーム以下）を 0 に置換する。
3. Onset Detection:
整形済みデータの差分を取り、0から1へ変化した点を Action の開始とする。

Noise Removal は本物の押下も消しうる点に注意する。音提示試行の中には実際の押下が2フレーム以下しか続かないもの（一瞬触れただけで成功判定される試行）があり、これらは整形済みデータ上に存在しなくなる。そのため保持時間の測定では、`pull_onset` の時点で整形済みデータが0かつ生データが1のとき、生データ側で解放時刻を求める。生データにも押下が無い場合は測定不能として欠損にする。整形済みデータのみで解放時刻を探すと、その試行とは無関係な後続の押下まで探索が及び、保持時間が数秒〜数十秒の異常値になる。

この救済は外部に `pull_onset` の記録がある音提示試行にのみ適用される。音提示外の短い押下は Onset Detection 自体が整形済みデータに依存するため、2フレーム以下のものは No Sound Pull / Second Pull として検出されない。

### 3.2. 異種データの統合 (Data Merging)
CSV（行動）とNWB（報酬）を pandas.merge_asof を使用し、direction='nearest' で結合する。許容誤差は 1フレーム分（約0.033s）とする。

### 3.3. 試行ベースの構造化
* ビニング処理の廃止: 10Hzへのダウンサンプリングは行わず、2.1項の定義に従って試行単位のイベントとして集約する。
* ITIカットの廃止: 試行単位の入力に移行するため、無反応区間の自動カットは行わない。定義された試行範囲外のデータは分析対象から除外する。

## 4. 入出力変数定義 (Design Matrix)

### 4.1. 目的変数 (Output: $y_k$)
* 型: Binary (0 or 1)
* 定義: 試行 $k$ において、定義された時間範囲内に Action (Onset) が存在すれば 1、存在しなければ 0。

### 4.2. 入力変数 (Input Regressors: $x_k$)
1. Bias ( $x_{bias,k}$)
値: 常に 1。
2. Stimulus ( $x_{stim,k}$)
値: 試行 $k$ の時間範囲内に音刺激（state_task=1）が含まれる場合は 1、含まれない場合は 0。
3. Action History ( $x_{hist,k}$)
定義: $h_k = y_{k-1} + \alpha_{act} \cdot h_{k-1}$
制約: 前の試行（ $k-1$）までの結果を用い、当該試行 $k$ の行動は含めない。
4. Reward History ( $x_{rew,k}$)
定義: $r_k = Reward_{k-1} + \alpha_{rew} \cdot r_{k-1}$
制約: 前の試行（ $k-1$）が Success であったか（Reward=1）を参照する。

### 4.3. 身体・顔部位特徴量の統合（オプション拡張）
ノート `notebooks/12_setup_input_data_ver2.ipynb` で実装されている、ビデオトラッキングによる顔・身体部位の動きを、試行単位の入力変数として追加する拡張。標準の4変数（Bias, Stimulus, Action History, Reward History）に対し、以下の9変数を追加し計13次元とする。

* **対象部位**: 耳先 (eartip)、目頭 (medialcorner)、鼻先 (nosetip)、下顎 (lowerjaw) の4部位、および瞳孔 (pupil)。データソースは `session.entries.data`（`bdbc_nwb_explorer` 経由でNWBから取得するビデオトラッキングデータ）。
* **特徴量**:
    * Position（4特徴量）: 各部位の座標とリックポート固定点（`face_video_lickport_x`/`_y`）とのユークリッド距離。
    * Speed（4特徴量）: 各部位のフレーム間移動距離（座標差分のユークリッドノルム）。
    * Pupil（1特徴量）: 瞳孔径（`face_video_pupildia` または `pupildia` 列）。
* **欠損値処理**: 線形補間 (`interpolate(method='linear')`) の後、前方補完し、残りを0埋め。
* **CSV/NWBデータとの結合**: 30Hzの行動データに対して `pandas.merge_asof(direction='nearest', tolerance=0.034)` で結合する（3.2節の結合と同一の許容誤差）。
* **試行単位への集約**: 10Hzビニングを行わない代わりに、各試行 $k$ の時間範囲（2.1節の試行タイプ別Window）内のフレームに対して、Position・Pupilは `median`（中央値）、Speedは `sum`（合計、試行内の総移動量）で集約し、試行1件につき1つの値 $x_{video,k}$ とする。
* **正規化**: ビデオ特徴量のみ、セッションごとに Z-score 正規化する（`scipy.stats.zscore`、NaNは0埋め）。Bias・Stimulus・History系の入力は正規化しない。
* **ラグ処理**: Action History / Reward History（4.2節）と同様に、前の試行（ $k-1$）の集約値を用いる。当該試行 $k$ 内の運動情報は含めない（同時刻の運動情報の漏れ込み防止）。

## 5. ハイパーパラメータ設定 (Parameters)

| Parameter | Value | Logic / Note |
| :--- | :--- | :--- |
| Raw Sampling | 30 Hz | ~0.033s / frame |
| Gap Fill Limit | 2 frames | センサーノイズ対策 |
| Noise Remove Limit | 2 frames | センサーノイズ対策 |
| Action Alpha ( $\alpha_{act}$) | 0.5 - 0.8 | 過去の行動の減衰率（試行単位） |
| Reward Alpha ( $\alpha_{rew}$) | 0.7 - 0.9 | 過去の報酬の減衰率（試行単位） |

## 6. 実装・解析フロー (Workflow)

1. Load Data: CSVおよびNWBデータの読み込み。
2. Clean & Flag (30Hz): 時系列整形と Onset / Reward フラグの確定。
3. Trial Extraction: 試行定義に基づき、時系列から各試行区間を切り出し $y_k, x_{stim,k}, Reward_k$ を抽出。
4. Feature Engineering: 試行順序に従い、 $\alpha$ を用いた Action History および Reward History を計算。
5. Train GLM-HMM: ssmライブラリ等を用い、試行系列データとして学習。
6. Decoding & Analysis: 各試行の状態推定と行動戦略の解釈。

## 変更履歴

* 2026-08-18: ノート `12_setup_input_data_ver2.ipynb` を参照し、身体・顔部位のビデオ特徴量を試行単位で入力変数として統合する方法を追記（4.3節）。
