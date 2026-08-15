# braidyn-bc

マウスの聴覚 Go/Wait（レバー引き）課題データから、学習に伴う内部状態の遷移と、皮質活動（中枢）・表情（末梢）の結合を解析するリポジトリです。

行動ログから GLM-HMM で潜在状態（Engaged / Random など）を推定し、その状態が脳活動や表情データにも実体として現れるかを検証します。研究上の問いと仮説は [docs/RQ.md](docs/RQ.md) にまとめています。

各ノートブックと `docs/` の詳細な説明は [docs/catalog.md](docs/catalog.md) を参照してください。

## 研究の流れ

1. **探索的解析 (EDA)** — 試行数、レバー引き長、音あり/なしでの脳活動を可視化する。
2. **内部状態の推定** — 行動時系列から Bernoulli GLM-HMM を学習し、潜在状態をデコードする。
3. **マルチモーダル検証** — 推定状態を皮質活動・表情特徴で再構成し、脳–身体カップリングを定量する。
4. **ミス試行の分解** — 学習初期の「脳は従事しているが身体が追いつかない」ミスと、後期の「両者とも非従事」ミスを区別する。

現在の実装中心は GLM-HMM の入力作成と 1 個体モデルです。要件は時間ビン単位（Ver.3）から試行単位（Ver.4）へ移行中です。

## リポジトリ構成

```
braidyn-bc/
├── README.md                 # 本ファイル
├── config.py                 # データパス（ローカル / Colab）
├── src/
│   └── data_loader.py        # NWB / CSV 読み込み
├── notebooks/                # 解析ノート（番号順）
├── docs/
│   ├── catalog.md            # ノート・docs の説明
│   ├── RQ.md                 # 研究質問・仮説
│   ├── requirements_glmhmm.md    # GLM-HMM 要件 Ver.3（時間ビン）
│   └── requirements_ver4.md      # GLM-HMM 要件 Ver.4（試行単位）
└── .gitignore
```

生データ（NWB・CSV）はこのリポジトリには含まれません。Google Drive 上の共有フォルダを参照します。

## データ

| 種別 | 内容 | パス変数 |
| :--- | :--- | :--- |
| NWB | セッション単位の神経画像・試行・表情など | `config.DATA_NWB_ROOT` |
| CSV | 30 Hz の行動時系列（`trials_L1L2.csv`） | `config.DATA_CSV_ROOT` |

対象は約 16 匹、課題日 Day 1–15 です。代表セッション例:

- マウス `VG1GC-105` / `task-day8`
- マウス `VG1GC-66` / `task-day15`

CSV の主な列:

- `t`, `state_lever`, `state_task`
- `pull_onset`, `reaction_time`, `diff_value`, `first_diff`
- `pull_duration_for_success`, `trial_outcome`

`state_task` は 0（音なし）、1（音提示）、2（報酬フェーズ）です。

## 環境

ノートブック先頭の共通セルが、Colab とローカル（VS Code / Cursor）を自動判別します。

### Colab

1. ノートブックを開く。
2. 先頭セルを実行する（Drive マウント、本リポジトリの clone/pull、依存関係のインストール）。
3. `config.py` は `COLAB_GPU` 環境変数を見て次のパスを使います。
   - NWB: `/content/drive/MyDrive/braidyn-bc/data`
   - CSV: `/content/drive/MyDrive/hackathon_data`

### ローカル

1. プロジェクトルート、または `notebooks/` からノートを開く。
2. `config.py` の Windows パスが、自分の Drive ショートカットと一致しているか確認する。
3. 依存関係を入れる。

```text
pynwb
pandas
numpy
matplotlib
seaborn
scipy
git+https://github.com/BraiDyn-BC/bdbc-nwb-explorer.git
```

GLM-HMM の学習には [lindermanlab/ssm](https://github.com/lindermanlab/ssm) が必要です。ノート `11` / `12` / `2b` 内で clone して editable install する手順があります。

```text
git clone https://github.com/lindermanlab/ssm
cd ssm
pip install -e .
```

## 推奨する読み順

| 段階 | ファイル | 内容 |
| :--- | :--- | :--- |
| 研究計画 | `docs/RQ.md` | 問い・仮説・解析フェーズ |
| データ確認 | `notebooks/01_data_loading.ipynb` | NWB / CSV の読み方 |
| 行動 EDA | `08`, `09`, `06`, `04` | 引き長・試行数・セッション内タイミング |
| 脳活動 EDA | `02`, `03` | レバー onset / 音提示まわりの ROI |
| 要件（現行） | `docs/requirements_ver4.md` | 試行単位 GLM-HMM |
| 要件（実装済み） | `docs/requirements_glmhmm.md` | 10 Hz ビン単位 GLM-HMM |
| 入力作成 | `notebooks/10_setup_GLM-HMM_input_data.ipynb` | 整形・ビン・履歴・ITI 分割 |
| モデル | `notebooks/11_build_GLM-HMM_model_for1mouse.ipynb` | 1 個体学習と解釈 |
| 表情拡張 | `notebooks/12_setup_input_data_ver2.ipynb` | ビデオ特徴を入力に追加 |
| 参考実装 | `notebooks/2b Input Driven Observations (GLM-HMM).ipynb` | Ashwood らの ssm チュートリアル |

## 主要モジュール

- `config.py` — 実行環境に応じて `DATA_NWB_ROOT` と `DATA_CSV_ROOT` を定義する。
- `src/data_loader.py`
  - `load_nwb_session(session_id, nwb_filename)` — `bdbc_nwb_explorer` で NWB を読む。
  - `load_trials_csv(session_id, task_day_dir, csv_name="trials_L1L2.csv")` — 行動 CSV を読む。

## ライセンス・出典

- 課題データは BraiDyn-BC プロジェクトの共有データです。
- GLM-HMM は Ashwood et al. (2022) および [ssm](https://github.com/lindermanlab/ssm) の Input Driven Observations に準拠します。
