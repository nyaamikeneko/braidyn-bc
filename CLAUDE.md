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

- **config値はモジュール属性として参照する**: `src/data_loader.py` と `src/glmhmm_ver4.py` は `from config import DATA_NWB_ROOT` ではなく `import config` して `config.DATA_NWB_ROOT` を都度参照する設計。理由: notebook側で `v4.DATA_NWB_ROOT = ...` のように上書きしても、`importlib.reload(v4)` すると `from import` していた場合は config.py の既定値で上書きが消えてしまう。新しいモジュールを追加するときも同じパターンを踏襲すること。
- **ssm ライブラリのキーワード引数は `inputs=`**: `model.log_likelihood()` / `model.log_probability()` は `input=x` ではなく `inputs=x`（複数形）を期待する。単数形で書くと `TypeError` になる。
- **ssm は手動インストールが必要**: pip に無いので `git clone https://github.com/lindermanlab/ssm && cd ssm && pip install -e .` が要る（ノート `11` / `12` / `2b` に手順あり）。ローカルでは WSL 上に作った `.venv-wsl`（`ssm` / `bdbc_nwb_explorer` / `pynwb` インストール済み）を使えば Windows ネイティブでのビルド失敗を避けられる。
- **NWBファイル名探索のフォールバックを部分一致にすると誤爆する**: `src/glmhmm_ver4.py` の `find_nwb_file()` は完全一致（`{mouse_id}_*_{task_day}.nwb`）が失敗すると `*{task_day}*.nwb` でフォールバック検索する。単純な部分文字列一致にすると `task-day1` が `task-day15` にヒットしてしまう（day1用のNWBが存在しないのに、代わりにday15のNWBを誤って読み込む）ため、日番号の直後に数字が続かないことを保証する正規表現を使っている。日番号を含む文字列マッチを書くときは同じ罠に注意する。
- **ノートブックのローカル実行はClaude Code経由が簡単**: Cursor/VS CodeでWSLカーネルに接続してセルを対話実行させる方法は、Cursorだと「インタープリタパスを入力」の選択肢がカーネルピッカーに出てこないことがある（拡張機能都合、原因未特定）。詰まったら `wsl -d Ubuntu -e bash -lc "cd /mnt/c/Users/<user>/braidyn-bc && <repo>/.venv-wsl/bin/python -m jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=1800 notebooks/XX.ipynb"` で直接実行するのが早い。出力（print・図）は `.ipynb` のJSONにインライン保存されるので、Cursor側はリモート接続なしで開くだけで見える。実行時間の目安: 複数日×複数モデルを学習するノート14で約6〜7分（`--ExecutePreprocessor.timeout` は余裕を持って1800秒程度に設定）。
- **WSLのext4.vhdxは中でファイルを消しても自動で縮まない**: ノート15のようにWSLホーム上でGBクラスの一時ファイルを扱うと、削除後もホストCドライブの空きは戻らない。戻すにはWindows側で `wsl --shutdown` してから `Optimize-VHD -Path <ext4.vhdx> -Mode Full`（Hyper-Vが無い環境では `diskpart` の `select vdisk file=...` → `compact vdisk`）を実行する。
- **`failure`（Short Pull）は「引き足りなかった」を意味しない**: 課題側は接触が1〜2フレーム（33〜67ms）途切れた時点で試行を確定させるため、行動としては閾値以上引けている試行が`failure`になる。`VG1GC-66`全日で、Short Pullのうち測定`pull_duration`が閾値`pull_duration_for_success`を下回るのは184/509（36.1%）だけで、残りは閾値以上引けている（内訳は接触途切れ97.2%、引き始めの遅れによる締め切り超過2.8%）。報酬条件は「連続接触で閾値ぶん保持」かつ「cueから1.0秒以内に達成」で、1.0秒は離す締め切りではない（成功試行の90.3%は1.0秒を過ぎても握り続けているが、条件達成は全件0.8秒以内）。`failure`を一律の失敗として集計すると解釈を誤る。詳細は[docs/data.md](docs/data.md)の「`trial_outcome` と報酬条件の解釈」。
- **CSVとNWBで`trial_outcome`のmiss/failureの意味が正反対**: NWB公式trialsテーブルはmiss=無反応（`pull_onset`無し）/failure=短い押下（`pull_onset`有り）だが、`trials_L1L2.csv`の`trial_outcome`列はその逆の使い方をしている（`VG1GC-66`全日で確認: 同じ試行群がNWBではmiss、CSVではfailureと呼ばれる。押下有りの群は両ソースとも`pull_onset`保有率100%、無反応の群は0%）。このため`extract_trials()`は文字列ラベルではなく`pull_onset`の有無でShort Pull/No Reactionを判定する。miss/failureの文字列を直接使う集計を書くときは、どちらのソース由来かを必ず確認すること。
- **`NOISE_REMOVE_LIMIT`以下の短い押下は成功試行でも`cleaned_lever`から消える**: Success/Short Pull試行には実際の押下が`NOISE_REMOVE_LIMIT=2`フレーム（約67ms）以下しか続かないものがあり（`first_diff`が0.03〜0.07秒程度の「一瞬だけ触れて成功判定される」試行。day1の`t_onset=228.297607`で実測確認）、`cleaned_lever`上ではこの押下が存在しない。このため`_action_end_time()`はonset行で`cleaned_lever=0`かつ生の`state_lever=1`のとき生信号にフォールバックして離脱時刻を測り、生信号にも押下が無ければ`t_onset`をそのまま返す（`compute_pull_window()`がduration<=0をNaNに落とす）。このフォールバックが無いと探索が無関係などこか先の押下まで暴走し、`pull_duration`が数秒〜二十数秒の異常値になる（導入前は`VG1GC-66`全日でSuccessの185/1293件・約14%が該当、最大22.9秒）。なおギャップ埋めで橋渡しされた保持が公式ウィンドウ終端（`t_end`）を超えて続く試行は少数（day3で12件、day6で3件など）正当に存在するので、`pull_end > t_end`は必ずしも異常を意味しない。
- **`_action_end_time()`とCSVの`stop_time`/`diff_value`は定義上1フレームずれる**: 前者は「離した最初のフレーム」を、後者はその1フレーム後を基準にしている。系統的な+1/30秒のズレなので分析結果への影響は無視できるが、CSVの生値と突き合わせてデバッグする際は混乱の元になる。
- **`GAP_FILL_LIMIT`はpull durationの分布を大きく動かす**: 既定の2フレーム（約67ms）を0/1/2で振ると（`VG1GC-66`全日プール）、検出される押下イベント数が7159→6186件（-14%）、平均pull durationが0.48→0.68秒（+40%）まで変わる。マウスの生レバー信号は保持中に数十msの瞬間的なドロップアウトを頻繁に起こしており（day1で確認した試行の58%が影響を受ける）、この定数は単なるノイズ除去のパラメータ以上に分析結果を左右する。
- **顔特徴の集計窓長はtrial_typeと強く相関し、生の特徴量に対して窓長そのものの影響も残る**: `attach_face_features()`の集計窓（`t_start`〜`t_end`）はSuccess（約2.4秒）/No Reaction（ほぼ常に1.0秒＝cue窓そのもの）/Short Pull（0.13〜2.9秒、平均約0.8秒）/No Sound Pull（0.1〜6.6秒、中央値約0.27秒）で長さが大きく異なる。窓長と生の顔特徴量の相関（pooled、`VG1GC-66`全日）はx_jaw_spd +0.40、x_pupil +0.35など無視できない大きさで、trial_typeで統制した後（within-group demeaning）もx_pupilは大部分消える（0.35→0.09）が、x_ear_pos/x_jaw_spd/x_nose_spdなどは統制後も相関が残る（0.25〜0.29）。つまり窓長の影響はtrial_typeを介した間接効果だけでは説明できない。GLM-HMMの状態が顔特徴と相関して見えるとき、trial_type由来か窓長由来かの切り分けが必要で、狭い窓（`pull_end`列を使った`t_onset`〜`pull_end`）を試すには`aggregate_face_window()`を再利用できる。

## Claude作業ログの置き場所

Claude Code が生成する作業ログ・変更メモは `.claude/changes/` に置く。研究成果物ではなくClaude自身の作業記録なので、リポジトリ直下ではなく `.claude/` 配下にまとめる。

## ドキュメント編集時の注意

- `CLAUDE.md` / `README.md` / `docs/*.md` / `reference/*.md` は常にその時点のスナップショットとして読めるように書く（`.claude/changes/` の作業ログは対象外。あちらは変更履歴を記録する場所）。「〜を追加した」「前回の未確認事項は解消した」のような変更履歴の語りは書かない（git log / git diff が担う）。取り消し線での修正履歴表示もしない。
- 事実として確定していることは、根拠を示した上で言い切る。「〜の可能性が高い」「ほぼ確実に」のような、確認済みの事実に対する冗長なヘッジは避ける。
- データの存在確認など、鮮度が意味を持つ事実には確認日を添えてよい（例:「2026-08-16 存在確認済み」）。これは変更履歴の語りではなく、情報自体の一部。

## 先行文献サーベイの運用ルール（`reference/`）

`reference/` 配下のファイル構成・執筆ルールは [reference/README.md](reference/README.md) の「ファイル構成のルール」に定義してあるので、そちらを正とする。要点:

- 個別mdファイル（`<著者><年>_<slug>.md`）は、論文PDFを `reference/sources/` に保存できた論文についてのみ作成する。PDF未入手の論文は [reference/all_references.md](reference/all_references.md) の要約のみで扱い、個別ファイルは作らない。
- 要旨・要約は、太字ラベル付きの箇条書き（`- **問題提起**` など、見出しは使わない）でカテゴリ（問題提起・タスク・数理モデル・論文固有の要素・主要な結果、など）を分け、各カテゴリの内容をその下にインデントしたサブ箇条書きで書く。見出し（`###`/`####`）は使わない（多くのMarkdownレンダラーで見出し要素の上下マージンにより余白が広くなりすぎるため）。伝聞的な一段落要約にせず、フラットな1階層の箇条書きにもしない。この構造化は個別mdの「要旨」・[reference/all_references.md](reference/all_references.md) の「要約」の両方に適用する。
- 個別mdには「モデル定義とメソッド」節を設け、本リポジトリでモデルを構築する際に参照できる粒度（数式・パラメータ・学習法）で書く。
- 論文どうしの関連性・本リポジトリのRQ/実装との技術的対応は、個別mdには一切書かず [reference/relations.md](reference/relations.md) に集約する（Mermaidフローチャート＋クラスタ別解説）。個別mdに「この研究との関連」節は設けない。
- 新しい論文を追加する際もこの構成を踏襲する。

## その他

- 現在の実装の主軸は Ver.4（試行単位、`notebooks/14_glmhmm_ver4_trials.ipynb`、`src/glmhmm_ver4.py`）。Ver.3（時間ビン単位）は `docs/requirements_glmhmm.md` に要件があるが実装は古い。次期仕様 Ver.5（`docs/requirements_ver5.md`、Day 1–15を貫くDynamic GLM-HMM＋皮質による独立検証）は設計のみで、対応する実装はまだない。
- 研究上の問い・仮説は `docs/RQ.md`、データ配置の詳細は `docs/data.md` を参照。
- データセットの一次情報（実験プロトコル、NWBの公式スキーマ、resting-state/sensory-mappingセッションの内訳など）は `reference/kondo2025_braidynbc_dataset.md`（データセット記述論文の要約）を参照。全文PDF・Supplementary Informationの原本は `reference/sources/` にある。
