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
- **ssm は手動インストールが必要**: pip に無いので `git clone https://github.com/lindermanlab/ssm && cd ssm && pip install -e .` が要る（ノート `11` / `12` / `2b` に手順あり）。ローカルでは WSL 上に作った `.venv-wsl`（`ssm` / `bdbc_nwb_explorer` / `pynwb` インストール済み）を使えば Windows ネイティブでのビルド失敗を避けられる。
- **NWBファイル名探索のフォールバックを部分一致にすると誤爆する**: `src/glmhmm_ver4.py` の `find_nwb_file()` は完全一致（`{mouse_id}_*_{task_day}.nwb`）が失敗すると `*{task_day}*.nwb` でフォールバック検索していたが、これは単純な部分文字列一致なので `task-day1` が `task-day15` にヒットしてしまっていた（day1用のNWBが存在しないのに、代わりにday15のNWBを誤って読み込む）。2026-08-16に、日番号の直後に数字が続かないことを保証する正規表現に修正した。日番号を含む文字列マッチを書くときは同じ罠に注意する。
- **ノートブックのローカル実行はClaude Code経由が簡単**: Cursor/VS CodeでWSLカーネルに接続してセルを対話実行させる方法は、Cursorだと「インタープリタパスを入力」の選択肢がカーネルピッカーに出てこないことがある（拡張機能都合、原因未特定）。詰まったら `wsl -d Ubuntu -e bash -lc "cd /mnt/c/Users/<user>/braidyn-bc && <repo>/.venv-wsl/bin/python -m jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=1800 notebooks/XX.ipynb"` で直接実行するのが早い。出力（print・図）は `.ipynb` のJSONにインライン保存されるので、Cursor側はリモート接続なしで開くだけで見える。実行時間の目安: 複数日×複数モデルを学習するノート14で約6〜7分（`--ExecutePreprocessor.timeout` は余裕を持って1800秒程度に設定）。

## Claude作業ログの置き場所

Claude Code が生成する作業ログ・変更メモは `.claude/changes/` に置く（2026-08-16に `docs/claude-changes/` → `claude-changes/` を経て移動）。研究成果物ではなくClaude自身の作業記録なので、リポジトリ直下ではなく `.claude/` 配下にまとめる。

## その他

- 現在の実装の主軸は Ver.4（試行単位、`notebooks/14_glmhmm_ver4_trials.ipynb`、`src/glmhmm_ver4.py`）。Ver.3（時間ビン単位）は `docs/requirements_glmhmm.md` に要件があるが実装は古い。
- 研究上の問い・仮説は `docs/RQ.md`、データ配置の詳細は `docs/data.md` を参照。
