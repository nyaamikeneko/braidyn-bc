# braidyn-bc

マウスの聴覚 Go/Wait（レバー引き）課題データから、学習に伴う内部状態の遷移と、皮質活動（中枢）・表情（末梢）の結合を解析するリポジトリです。

行動ログから GLM-HMM で潜在状態（Engaged / Random など）を推定し、その状態が脳活動や表情データにも実体として現れるかを検証します。研究上の問いと仮説は [docs/RQ.md](docs/RQ.md) にまとめています。

各ノートブックと `docs/` の詳細な説明は [docs/catalog.md](docs/catalog.md) を参照してください。

## 研究の流れ

1. **探索的解析 (EDA)** — 試行数、レバー引き長、音あり/なしでの脳活動を可視化する。
2. **内部状態の推定** — 行動時系列から Bernoulli GLM-HMM を学習し、潜在状態をデコードする。
3. **マルチモーダル検証** — 推定状態を皮質活動・表情特徴で再構成し、脳–身体カップリングを定量する。
4. **ミス試行の分解** — 学習初期の「脳は従事しているが身体が追いつかない」ミスと、後期の「両者とも非従事」ミスを区別する。

現在の実装中心は GLM-HMM です。時間ビン単位（Ver.3、ノート `10`–`12`）に加え、試行単位（Ver.4、ノート `14`）がある。

## リポジトリ構成

```
braidyn-bc/
├── README.md                 # 本ファイル
├── config.py                 # データパス（ローカル / Colab）
├── src/
│   ├── data_loader.py        # NWB / CSV 読み込み
│   └── glmhmm_ver4.py        # Ver.4 試行抽出・学習・可視化
├── notebooks/                # 解析ノート（番号順）
├── docs/
│   ├── catalog.md            # ノート・docs の説明
│   ├── data.md               # データ配置と CSV バックアップ
│   ├── RQ.md                 # 研究質問・仮説
│   ├── requirements_glmhmm.md    # GLM-HMM 要件 Ver.3（時間ビン）
│   └── requirements_ver4.md      # GLM-HMM 要件 Ver.4（試行単位）
├── reference/                 # 先行文献の要約
└── .gitignore
```

生データ（NWB・CSV）はこのリポジトリには含まれません。Google Drive 上の共有フォルダを参照します。配置と個人バックアップは [docs/data.md](docs/data.md) を見てください。

## データ

| 種別 | 内容 | パス変数 |
| :--- | :--- | :--- |
| NWB | セッション単位の神経画像・試行・表情など | `config.DATA_NWB_ROOT` |
| CSV | 30 Hz の行動時系列（`trials_L1L2.csv`） | `config.DATA_CSV_ROOT` |
| CSV バックアップ | 上記 CSV のみの個人コピー | `config.DATA_CSV_BACKUP_ROOT`（`マイドライブ/braidyn-bc-backup/hackathon_data`） |

対象は約 24 匹（CSV がある個体）、課題日 Day 1–15 です。代表セッション例:

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
   - CSV: `/content/drive/MyDrive/hackathon_data`（無ければ `/content/drive/MyDrive/braidyn-bc-backup/hackathon_data`）

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

### ローカル（WSL、動作確認済み）

`ssm` は Windows ネイティブだとビルドに MSVC が必要で失敗しやすいので、WSL 上での実行を確認済み（2026-08-16）。

- `config.py` は `WSL_DISTRO_NAME` 環境変数を見て `/mnt/g/マイドライブ/...` を使う分岐を持つ（[実行環境の分岐](#環境)参照）。
- リポジトリ直下の `.venv-wsl` に `ssm` / `bdbc_nwb_explorer` / `pynwb` をインストール済み。WSL上でこの venv を Jupyter カーネルに選べば追加インストールなしで動く。
- データも Google Drive デスクトップ経由でローカルから見えることを確認済み: NWB は `G:\マイドライブ\nwb_manual\VG1GC-66\`（`task-day15` の1件）、CSV は `G:\.shortcut-targets-by-id\1fI6PWRHgihU6asA4OyW-_rN-JII33Fkj\hackathon_data`（`config.py` の Windows/WSL 分岐が指すパスと一致）。

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
| 試行単位 | `notebooks/14_glmhmm_ver4_trials.ipynb` | Ver.4。日ごとに独立学習。4 次元は K=3、13 次元は K=2/K=3 |
| 参考実装 | `notebooks/2b Input Driven Observations (GLM-HMM).ipynb` | Ashwood らの ssm チュートリアル |

## 主要モジュール

- `config.py` — 実行環境に応じて `DATA_NWB_ROOT` と `DATA_CSV_ROOT` を定義する。共有 CSV が無いときはマイドライブのバックアップを使う。
- `src/data_loader.py`
  - `load_nwb_session(session_id, nwb_filename)` — `bdbc_nwb_explorer` で NWB を読む。
  - `load_trials_csv(session_id, task_day_dir, csv_name="trials_L1L2.csv")` — 行動 CSV を読む。
- `src/glmhmm_ver4.py` — Ver.4 の試行抽出、履歴、顔特徴、学習、可視化。

## 参考文献

本研究の背景となる先行文献は [reference/](reference/) にまとめています。各論文の要約は個別の md ファイル、または全10本をまとめた [reference/all_references.md](reference/all_references.md) を参照してください。

| # | タイトル | 著者（筆頭） | 誌名・年 |
| :-- | :--- | :--- | :--- |
| 1 | [Multimodal dataset linking wide-field calcium imaging to behavior changes in operant lever-pull task in mice](reference/kondo2025_braidynbc_dataset.md) | Kondo, M. | Scientific Data, 2025 |
| 2 | [Mice alternate between discrete strategies during perceptual decision-making](reference/ashwood2022_discrete_strategies.md) | Ashwood, Z. C. | Nature Neuroscience, 2022 |
| 3 | [Internal states emerge early during learning of a perceptual decision-making task](reference/cuturela2024_internal_states_early.md) | Cuturela, L. I. (IBL) | bioRxiv, 2024 |
| 4 | [Infinite hidden Markov models can dissect the complexities of learning](reference/bruijns2025_infinite_hmm.md) | Bruijns, S. A. (IBL) | Nature Neuroscience, 2025 |
| 5 | [Identifying the factors governing internal state switches during nonstationary sensory decision-making](reference/mohammadi2025_internal_state_switches.md) | Mohammadi, Z. | Nature Communications, 2025 |
| 6 | [A reservoir of foraging decision variables in the mouse brain](reference/cazettes2023_foraging_reservoir.md) | Cazettes, F. | Nature Neuroscience, 2023 |
| 7 | [Facial expressions in mice reveal latent cognitive variables and their neural correlates](reference/cazettes2025_facial_expressions.md) | Cazettes, F. | Nature Neuroscience, 2025 |
| 8 | [Inferring internal states across mice and monkeys using facial features](reference/tlaie2025_facial_features_mice_monkeys.md) | Tlaie, A. | Nature Communications, 2025 |
| 9 | [Spontaneous behaviour is structured by reinforcement without explicit reward](reference/markowitz2023_spontaneous_behaviour.md) | Markowitz, J. E. | Nature, 2023 |
| 10 | [Hidden Markov models reveal behavioral state dynamics in depth-related locomotion in mice](reference/shuto2025_hmm_depth_locomotion.md) | Shuto, H. | PLOS ONE, 2025 |

## ライセンス・出典

- 課題データは BraiDyn-BC プロジェクトの共有データです（[reference/kondo2025_braidynbc_dataset.md](reference/kondo2025_braidynbc_dataset.md)）。
- GLM-HMM は Ashwood et al. (2022) および [ssm](https://github.com/lindermanlab/ssm) の Input Driven Observations に準拠します。
