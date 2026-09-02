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
- **報酬閾値`pull_duration_for_success`は固定値ではなく、成功率で上下する適応的な値**: 課題側が直近20試行の成功率80%で+50ms（上限400ms、20試行の不応期あり）、セッション内は単調非減少、次セッションの初期値は前セッション終端値−100ms、という規則で動かしている（論文Methods "Tone-triggered lever-pull task"。要約は[reference/kondo2025_braidynbc_dataset.md](reference/kondo2025_braidynbc_dataset.md)、実測値と帰結は[docs/data.md](docs/data.md)）。`VG1GC-66`の実測でも day1 0.00秒 → day5–7 0.40秒 → day13 0.10秒 と鋸歯状に動く。帰結は2つ。(1) **成功率は学習曲線にならない**（上達すると閾値が上がって難度で相殺される。論文自身が学習指標に使うのはセッション終端の`Tpull_final`）。ただし片方向のラチェットなので成功率が80%に保たれるわけではなく、`VG1GC-66`のday別成功率は中央値0.566・範囲0.280–0.883、20試行移動窓が0.8以上だった割合は13.7%。成功率（全試行）のday index相関はSpearman −0.354（p=.215）、`Tpull_final`で見ても −0.125（p=.671）で、**この個体はどちらの指標でも単調な学習傾向を示さない**（`Tpull_final`はday5–7に上限0.40へ達したあと後退する）。(2) **`success`／報酬の意味がdayをまたいで不変ではない**ので、Reward Historyやday別GLM重みをday間比較する解析はこの閾値の動きを含む。閾値0の試行（`VG1GC-66`で68件）は閾値比較から外す。
- **GLM-HMMの初期状態分布$\pi$の扱いは、セッション数が少ないと結果を数nats動かす**: `ssm`（Ashwood系譜）は$\pi$を推定するが、Cuturela et al. 2024とその公開実装は$z_1^s \sim U(\{1,\dots,K\})$と一様固定する（公開実装はセッション数20未満での推定を例外で禁止している）。`VG1GC-66`の14 day・2359試行では、`ssm`の静的フィットの解を一様$\pi$で評価し直すとdata log-likelihoodが6.82 nats悪化した。dayごとに状態がほぼ固定される解では「その日がどの状態で始まるか」を$\pi$が担うためで、$\pi$の扱いが違う実装どうしで対数尤度を直接比較すると、モデルの優劣を取り違える。詳細は[docs/requirements_ver5.md](docs/requirements_ver5.md) 5.2節。
- **CSVとNWBで`trial_outcome`のmiss/failureの意味が正反対**: NWB公式trialsテーブルはmiss=無反応（`pull_onset`無し）/failure=短い押下（`pull_onset`有り）だが、`trials_L1L2.csv`の`trial_outcome`列はその逆の使い方をしている（`VG1GC-66`全日で確認: 同じ試行群がNWBではmiss、CSVではfailureと呼ばれる。押下有りの群は両ソースとも`pull_onset`保有率100%、無反応の群は0%）。このため`extract_trials()`は文字列ラベルではなく`pull_onset`の有無でShort Pull/No Reactionを判定する。miss/failureの文字列を直接使う集計を書くときは、どちらのソース由来かを必ず確認すること。
- **`NOISE_REMOVE_LIMIT`以下の短い押下は成功試行でも`cleaned_lever`から消える**: Success/Short Pull試行には実際の押下が`NOISE_REMOVE_LIMIT=2`フレーム（約67ms）以下しか続かないものがあり（`first_diff`が0.03〜0.07秒程度の「一瞬だけ触れて成功判定される」試行。day1の`t_onset=228.297607`で実測確認）、`cleaned_lever`上ではこの押下が存在しない。このため`_action_end_time()`はonset行で`cleaned_lever=0`かつ生の`state_lever=1`のとき生信号にフォールバックして離脱時刻を測り、生信号にも押下が無ければ`t_onset`をそのまま返す（`compute_pull_window()`がduration<=0をNaNに落とす）。このフォールバックが無いと探索が無関係などこか先の押下まで暴走し、`pull_duration`が数秒〜二十数秒の異常値になる（導入前は`VG1GC-66`全日でSuccessの185/1293件・約14%が該当、最大22.9秒）。なおギャップ埋めで橋渡しされた保持が公式ウィンドウ終端（`t_end`）を超えて続く試行は少数（day3で12件、day6で3件など）正当に存在するので、`pull_end > t_end`は必ずしも異常を意味しない。
- **`_action_end_time()`とCSVの`stop_time`/`diff_value`は定義上1フレームずれる**: 前者は「離した最初のフレーム」を、後者はその1フレーム後を基準にしている。系統的な+1/30秒のズレなので分析結果への影響は無視できるが、CSVの生値と突き合わせてデバッグする際は混乱の元になる。
- **`GAP_FILL_LIMIT`はpull durationの分布を大きく動かす**: 既定の2フレーム（約67ms）を0/1/2で振ると（`VG1GC-66`全日プール）、検出される押下イベント数が7159→6186件（-14%）、平均pull durationが0.48→0.68秒（+40%）まで変わる。マウスの生レバー信号は保持中に数十msの瞬間的なドロップアウトを頻繁に起こしており（day1で確認した試行の58%が影響を受ける）、この定数は単なるノイズ除去のパラメータ以上に分析結果を左右する。
- **顔特徴の集計窓は「窓長のアーティファクト」と「行動そのものの効果」を分けて見る**: `attach_face_features()`の既定窓（`t_start`〜`t_end`）はSuccess（約2.4秒＝約74フレーム）/No Reaction（1.0秒＝31フレーム）/Short Pull（0.13〜2.9秒、平均約0.8秒）/No Sound Pull（0.1〜6.6秒、中央値約0.27秒、最少2フレーム）で長さが大きく異なり、窓長と生の顔特徴量の相関（pooled、`VG1GC-66`全日6745試行）はx_jaw_spd +0.41、x_pupil +0.35と無視できない。`face_window_bounds(window="onset_fixed")`のpull onset固定窓（`[t_onset-0.2, t_onset+0.8]`秒、pullが無い試行はcue onset基準。全試行30フレーム前後）で切り出すと窓長・フレーム数の差が構造的に消えるため、そこで残る相関は窓長由来ではあり得ない。実測では運動系特徴の相関はむしろ強まる（`pull_duration`との相関: x_jaw_spd 0.43→0.58、x_ear_pos 0.35→0.44。trial_type統制後も0.29→0.32 / 0.30→0.29。trial_typeによる分散説明率η²も x_jaw_spd 0.14→0.42）ので、これは集計のサンプル数ノイズではなくレバー引きと顔・身体の動きの実際の共変動。例外はx_pupilで、`pull_duration`との相関0.28→0.00、η² 0.12→0.00とほぼ完全に消える（既定窓ではSuccessの窓が報酬フェーズまで伸びるので、窓長が報酬後の散瞳を拾っていた）。集計窓は`attach_face_features(..., window=...)`と`process_session(..., face_window=...)`／`process_mouse(..., face_window=...)`で切り替える（既定は`"trial"`＝Ver.4仕様）。検証はノート16の2.7節。

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
