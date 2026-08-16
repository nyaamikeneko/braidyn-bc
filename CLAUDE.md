# CLAUDE.md

このファイルは Claude Code 向けの作業メモです。人間向けの説明は `README.md` と `docs/catalog.md` を参照してください。

## リポジトリの性格

マウス行動データの GLM-HMM 解析リポジトリ。実装の中心は `notebooks/` の Jupyter ノートブックで、`src/` は共通ロジック（データ読み込み、Ver.4 モデル）を切り出したもの。データ本体（NWB・CSV）はリポジトリに含まれず、Google Drive を参照する。

## 実行環境の分岐（`config.py`）

`config.py` は実行環境を自動判定してデータパスを切り替える。

- Colab: `COLAB_GPU` 環境変数の有無で判定
- WSL: `WSL_DISTRO_NAME` 環境変数の有無で判定（`/mnt/g/マイドライブ/...`）
- Windows ローカル: 上記どちらでもない場合（`G:/マイドライブ/...`）

パスが存在しない場合は例外を出さず警告を print するだけなので、データ未読み込みのままセルが進んでしまうことがある。パス関連の不具合を疑うときは、まず `config.py` の分岐とその環境の Drive マウント状況を確認する。

## 既知の落とし穴

- **config値はモジュール属性として参照する**: `src/data_loader.py` と `src/glmhmm_ver4.py` は `from config import DATA_NWB_ROOT` ではなく `import config` して `config.DATA_NWB_ROOT` を都度参照する設計（2026-08-16修正）。理由: notebook側で `v4.DATA_NWB_ROOT = ...` のように上書きしても、`importlib.reload(v4)` すると `from import` していた場合は config.py の既定値で上書きが消えてしまう。新しいモジュールを追加するときも同じパターンを踏襲すること。
- **ssm ライブラリのキーワード引数は `inputs=`**: `model.log_likelihood()` / `model.log_probability()` は `input=x` ではなく `inputs=x`（複数形）を期待する。単数形で書くと `TypeError` になる。
- **ssm は手動インストールが必要**: pip に無いので `git clone https://github.com/lindermanlab/ssm && cd ssm && pip install -e .` が要る（ノート `11` / `12` / `2b` に手順あり）。

## Claude作業ログの置き場所

Claude Code が生成する作業ログ・変更メモは `.claude/changes/` に置く（2026-08-16に `docs/claude-changes/` → `claude-changes/` を経て移動）。研究成果物ではなくClaude自身の作業記録なので、リポジトリ直下ではなく `.claude/` 配下にまとめる。

## その他

- 現在の実装の主軸は Ver.4（試行単位、`notebooks/14_glmhmm_ver4_trials.ipynb`、`src/glmhmm_ver4.py`）。Ver.3（時間ビン単位）は `docs/requirements_glmhmm.md` に要件があるが実装は古い。
- 研究上の問い・仮説は `docs/RQ.md`、データ配置の詳細は `docs/data.md` を参照。
