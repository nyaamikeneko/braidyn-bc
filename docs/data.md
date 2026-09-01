# データ配置と CSV バックアップ

生データはこの Git リポジトリには入っていない。ローカル・Colab の実行は現状 Google Drive 上の共有フォルダを `config.py` 経由で読む運用のままだが、**正式な公開先は DANDI Archive・AWS S3・GIN の3系統に再編されている**（2026-08-16確認）。データの正式な引用・再取得にはこちらを使う。

## 0. 正式な公開先（DANDI / AWS S3 / GIN）

Google Drive の NWB フォルダ自体はプロジェクトサイト上にリンクが残っているが、正式なアーカイブではない。

- プロジェクトサイト: https://nakaelab.github.io/braidyn-bc-database/index.html
- 該当データセット解説ページ: https://nakaelab.github.io/braidyn-bc-database/pages/operant-conditioning-process.html
- 論文（Scientific Data誌）: https://www.nature.com/articles/s41597-025-05482-y （→ [reference/kondo2025_braidynbc_dataset.md](../reference/kondo2025_braidynbc_dataset.md)）

| プラットフォーム | 内容 | サイズ目安 | DOI / 引用 | 主な用途 |
| :--- | :--- | :--- | :--- | :--- |
| [DANDI Archive](https://dandiarchive.org/dandiset/001425/)（Dandiset 001425, v0.250705.0947, CC-BY-4.0） | NWB形式の全データ（Raw画像含む） | 8.1 TB（1838ファイル） | 10.48324/dandi.001425/0.250705.0947 | NWB標準ツール（dandi CLI／Python API／fsspecストリーミング）で全データを再現性高く扱う。論文の付随データとして正式引用する場合もこちら |
| AWS S3（バケット `s3://braidyn-bc-buckets`、[ブラウザ表示](https://braidyn-bc-buckets.s3.amazonaws.com/index.html)、[CLIガイド](https://nakaelab.github.io/braidyn-bc-database/pages/aws-cli-guide.html)） | Rawデータ（動画・TIFF等の未加工ファイル）中心。NWBも同梱 | 約1700 GB | なし | 認証不要（`--no-sign-request`）。AWS CLI／boto3で顔・瞳孔・体の動画など生データを直接取得する |
| [GIN](https://gin.g-node.org/BraiDyn-BC/Kondo2025_CuedLeverPullNWB)（G-Node Infrastructure） | NWB形式のみ。Raw imagingデータを除いた軽量版 | 1ファイルあたり約1.7GB（実測、詳細は下記）。25匹×15セッション全体では数十GB規模 | 10.12751/g-node.zbh16l | DataLad／git-annexで、軽量にNWBのみ・行動データや前処理済み信号を扱う。公式サイトのトップ・チュートリアルページには明記がなく、論文本文（Scientific Data誌）で確認できる情報 |

選び方の目安:

- 神経活動の信号解析のみ（dF/F・行動タイムスタンプ等）→ **GIN**（軽量。ΔF/Fは1ファイルあたり58MB程度、詳細は下記）
- 生の動画・画像も使う（顔・瞳孔・体の動画解析など）→ **AWS S3** から必要セッションのみ取得
- NWB全体を再現性重視で厳密に扱う／正式引用 → **DANDI**

**注**: 論文本文（Data Recordsセクション、[reference/kondo2025_braidynbc_dataset.md](../reference/kondo2025_braidynbc_dataset.md)）で明記されているのは DANDI と GIN の2つのみ。AWS S3 はプロジェクトサイトのみで案内されている（論文には記載なし）。

### GIN利用時の実務メモ（1ファイル約1.7GBの場合）

ファイルサイズが1GB程度であれば、Google Colabの一時ディスクよりも、永続化できるローカル環境での作業を基本とする。理由: Colab無料枠のディスクはセッション終了でリセットされ、DataLad/git-annexでの再取得が繰り返し発生しやすく、GINのgit-annex経由の取得は小さなgitオブジェクトのやり取りが多いため、Colabの一時ストレージ・帯域と相性がよくない。探索段階で数ファイルだけ試したい場合、またはGoogle Driveをマウントして永続化する運用にする場合はColabも選択肢。

```bash
pip install datalad
datalad clone https://gin.g-node.org/BraiDyn-BC/Kondo2025_CuedLeverPullNWB
cd Kondo2025_CuedLeverPullNWB

datalad status                     # まずメタデータ・構造のみ確認（実体は落ちない）
find . -name "*.nwb"

datalad get sub-01/ses-01/*.nwb    # 必要なsubject/sessionだけ実体を取得
```

25匹×15セッション分あるため、全部を一度に取得すると数十〜百GB規模になり得る。

### NWBファイルの内部構造とサイズ内訳（実測）

`nwb_manual/VG1GC-66/VG1GC-66_2023-09-08_task-day15.nwb`（GIN由来、ディスク上1.69GB）をh5pyで走査した内訳（2026-08-17確認）。

| グループ | 論理サイズ | 割合 | 内容 |
| :--- | ---: | ---: | :--- |
| `acquisition` | 2333 MB | 82% | 16チャンネル分の生センサー波形 |
| `processing` | 499 MB | 18% | 解析で使う処理済みデータ（内訳は下表） |

`acquisition`（2.3GBの主因）: `tone`/`lever`/`reward`/`lick`/`motion`/`pull_duration`/`state_lever`/`state_task`/`air_pressure`/`CO2_level`/`humidity`/`room_temp`/`LED_B`/`LED_V`/`img_acquisition`/`video_trig` の16チャンネルが、各約5kHz×30分（909万サンプル）の `data`+`timestamps` で1チャンネルあたり145.5MB。動画・イメージングのトリガ/フレームカウンタ（`body_video`/`eye_video`/`face_video`/`widefield_UV`/`widefield_blue`）もここに含まれるが、いずれも1.5MB以下で画素データそのものは含まれない。GINが除外している「Raw imaging」は動画・画素データを指し、この5kHz生波形自体はGIN版にも残っている。

`processing` は3つのモジュールに分かれる: `behavior`（DLCキーポイント等、動画のネイティブレート）、`downsampled`（imagingフレームレート30Hzに揃えた版）、`ophys`（神経活動）。imaging frame rate（30Hz）の実体は `ophys/DfOverF` 自身のサンプリングレートで、`downsampled` 配下の全チャンネルはこれと同じ54000サンプル（30分×30Hz）に揃えてある。

#### `processing/behavior`（動画のネイティブレート、約100.8Hz＝181,451サンプル/30分）

DLCで追跡したキーポイントごとに `data`(x, y)・`confidence`・`timestamps` を持つグループが並ぶ。ノード数は論文Table記載の点数と一致（確認済み）。

| サブグループ | サイズ | ノード数と内容 |
| :--- | ---: | :--- |
| `eye_video_keypoints` | 186 MB | 32点: `medialcorner`/`lateralcorner`（目頭・目尻）＋ `pupiledge01`〜`30`（瞳孔輪郭、楕円フィッティング用） |
| `face_video_keypoints` | 81 MB | 14点: `earlateral`/`earroot`/`eartip`/`eyelateral`/`eyemedial`/`leftpawcenter`/`lickport`/`lowerjaw`/`nosebottom`/`noseright`/`noseroot`/`nosetip`/`rightpawcenter`/`tonguetip` |
| `body_video_keypoints` | 29 MB | 5点: `leftbartip`/`leftpawcenter`/`lickport`/`rightbartip`/`rightpawcenter` |
| `eye_position` | 4.35 MB | `center_x`/`center_y`（瞳孔中心、`eye_video_keypoints`から楕円フィッティングした派生値） |
| `pupil_tracking` | 2.18 MB | `diameter`（瞳孔径、同じく楕円フィッティングの派生値） |

#### `processing/downsampled`（30Hz＝imaging frame rate、54000サンプル/30分）

キーポイント系は `behavior` と同じノード構成を30Hzに間引いたもの。ただし各ノードの `confidence` だけはネイティブレート（181,451サンプル）のまま残っており、サイズが単純な30/100.8倍にならない一因になっている。

| サブグループ | サイズ | 内容 |
| :--- | ---: | :--- |
| `eye_video_keypoints` | 74 MB | `behavior/eye_video_keypoints` の30Hz版（32点、`confidence`のみ元レート） |
| `face_video_keypoints` | 32 MB | 同、`face_video_keypoints`の30Hz版（14点） |
| `body_video_keypoints` | 12 MB | 同、`body_video_keypoints`の30Hz版（5点） |
| `eye_position` | 1.30 MB | `center_x`/`center_y`の30Hz版 |
| `pupil_tracking` | 0.65 MB | `diameter`の30Hz版 |
| `CO2_level`/`air_pressure`/`humidity`/`lever`/`lick`/`lick_rate`/`motion`/`reward`/`room_temp`/`state_lever`/`state_task`/`tone` | 各0.86 MB（計10.3 MB） | `acquisition`の同名チャンネルを30Hzに間引いたもの |
| `trials` | 0.01 MB | 163試行×7フィールド（`id`/`pull_duration_for_success`/`pull_onset`/`reaction_time`/`start_time`/`stop_time`/`trial_outcome`）。`src/glmhmm_ver4.py`が読む試行情報の本体。各フィールドの意味は[下記](#trial_outcome-と報酬条件の解釈)を参照 |

#### `processing/ophys`（30Hz、54000サンプル/30分）

| サブグループ | サイズ | 内容 |
| :--- | ---: | :--- |
| `DfOverF` | 58 MB | ROIごとのΔF/F。`dFF`（ヘモダイナミクス補正済み本体）/`dFF_B`（470nm生）/`dFF_V`（405nm生）の3系統、各`(54000, 44)`＝44 ROI（片半球22×両半球） |
| `ImageSegmentation` | 7 MB | 44 ROIのマスク・座標定義 |

`src/glmhmm_ver4.py` の13次元モデル（顔特徴＋pupil）と神経活動（`ophys/DfOverF`）が実際に読むのは `processing/downsampled` と `processing/ophys` の2モジュールのみ（計約195MB）。`bdbc_nwb_explorer.read_nwb()` はデフォルト（`downsampled=True`）でこの2モジュールしか読まない（`read_acquisition()`/`read_video_tracking()`/`read_trials()`/`read_roi_dFF()` のいずれも同様）ため、`acquisition`（5kHz生波形、2.3GB）と `processing/behavior`（動画ネイティブレートのキーポイント、302MB）は読み込み経路に一切含まれない。この2つを除いた軽量版NWBを作るユーティリティが `src/nwb_shrink.py`（`strip_to_downsampled_and_ophys()`）で、GINから取得したNWBをローカル(WSL)で軽量化してDriveへ保存する手順が `notebooks/15_gin_fetch_processing_only.ipynb` にある。

### `trial_outcome` と報酬条件の解釈

`trial_outcome`（`success`/`failure`/`miss`）は課題制御システム側が確定させた値で、本リポジトリは判定を行わず読み込むだけである（`src/glmhmm_ver4.py` の `official_sound_trials()`）。同名の列がハッカソンCSV `trials_L1L2.csv` にもあるが、そちらは`miss`と`failure`の使い方がNWBと正反対なので、2つを混ぜてはならない（[CLAUDE.md](../CLAUDE.md)の既知の落とし穴を参照）。`src/glmhmm_ver4.py` は `success` か否かの判定にのみこの列を使い、残り2タイプは `pull_onset` の有無で判別している。

報酬条件の実態は `VG1GC-66` 全日の実測から次のように読み取れる。

- **報酬には「連続接触」で `pull_duration_for_success` 秒ぶん保持することが要る。** 課題側は接触が途切れた時点で試行を確定させる。実測では成功試行340件中、閾値ぶん引き切った時点が cue から1.0秒を超えたものは0件だった。
- **1.0秒の窓は「離す締め切り」ではなく「保持条件を達成する締め切り」。** 成功試行の90.3%は1.0秒を過ぎてもレバーを握り続けている（引き終わりは平均1.86秒、最大6.87秒）が、条件達成自体は全件0.8秒以内に済んでいる。無反応（NWBの`miss`）試行の `stop_time - start_time` がほぼ厳密に1.0秒なのはこの締め切りそのもの。
- **`failure` は「引き足りなかった」を意味しない。** 閾値を測定保持時間で下回るのは36.1%にとどまり、残りは行動としては閾値以上引けている。内訳は、接触が1〜2フレーム（33〜67ms）途切れたため連続保持と見なされなかったものが大半（97.2%）で、引き始めが遅く締め切りまでに条件を満たせなかったものが2.8%。この途切れがセンサー由来か握りの微小な緩みかは、このデータからは区別できない（33〜67msは意図的な離して掴み直しには短すぎる）。

したがって `failure` 試行を一律に「引き方の失敗」として扱うと解釈を誤る。`pull_duration` と `pull_duration_for_success`、`reaction_time` を突き合わせれば、締め切り超過／接触途切れ／本当に引き足りない、の3類型に分解できる。

### `pull_duration_for_success`（= 論文の `T_pull`）は固定値ではない

**報酬閾値は課題側が成功率に応じて上下させる適応的な値（staircase）で、セッション内でもセッション間でも変わる。** 規則は論文Methods "Tone-triggered lever-pull task"（[reference/kondo2025_braidynbc_dataset.md](../reference/kondo2025_braidynbc_dataset.md) の「記録系」節に全文の要約）に明記されている。

- 初回セッションの初期値は 1ms。
- 直近20試行の成功率が80%に達すると +50ms（上限400ms）。引き上げには20試行の不応期がある。
- **セッション内では決して短くならない**（単調非減少）。
- **次セッションの初期値は前セッションの終端値 `Tpull_final` − 100ms**。したがってセッション間では下がる。

`VG1GC-66` 全14日の実測値（`pull_duration_for_success` の中央値、秒）:

| day | 1 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 閾値 | 0.00 | 0.05 | 0.15 | 0.40 | 0.40 | 0.40 | 0.30 | 0.20 | 0.25 | 0.15 | 0.15 | 0.10 | 0.20 | 0.20 |

（2026-09-02 実測、[notebooks/17_ver5_pre_implementation_checks.ipynb](../notebooks/17_ver5_pre_implementation_checks.ipynb) 2節）。すべて50msの倍数、上限0.40秒、day内は非減少、day間で約100ms下がる——論文の規則と整合する。day1が0.00なのは初期値1msが記録精度で丸まったもので、この日は「触れれば成功」に近く、押下試行内の成功率は100%になる。

**帰結として次の3点に注意する。**

- **`success` / 報酬の意味がdayをまたいで不変ではない。** day1の成功とday6の成功は要求が違う。Reward History（Ver.4 4.2節・Ver.5 4.2節）やday別GLM重みをday間で比較する解析は、この閾値の動きに汚染される。
- **成功率は学習曲線として使えない。** staircaseが成功率をおよそ80%に保つよう働くので、成功率は設計上おおむね安定する。論文自身も学習の指標には成功率ではなく `Tpull_final` を使い、その時系列で個体を2クラスタに分けている。`VG1GC-66` でも成功率（全試行）のday index相関は Spearman −0.354（p=.215）で単調傾向が無い一方、押下試行内の成功率は −0.670（p=.009）と下がる。後者は学習の否定ではなく閾値ランプの反映と読む。
- **閾値0の試行は閾値比較から外す。** `pull_duration_for_success == 0` の試行では「閾値以上引けたか」の比較が自明に真になる。`VG1GC-66` では68件（day1・day3の整形期）が該当する。

### GIN版とGoogle Drive版NWBの関係

`nwb_manual` にあるNWBファイルはGIN版を取得して手動配置したもの。したがって両者の内容差分を別途確認する必要はない。

### その他の関連リソース

| リソース | URL |
| :--- | :--- |
| Pythonチュートリアル一覧（Google Drive） | https://drive.google.com/drive/folders/1f5MBwx0tfmJQgbwJ24MVGnka4QZQzfJI |
| 解析用データパイプライン（GitHub） | https://github.com/BraiDyn-BC/bdbc-data-pipeline |
| NWB探索ツール（GitHub） | https://github.com/BraiDyn-BC/bdbc-nwb-explorer |
| Matsuzaki Lab 独自配布ページ | https://mmlab-repo.m.u-tokyo.ac.jp/r/Matsuzaki/BraiDyn-BC_CuedLeverPull |

---

## 1. このリポジトリでの現状の使い方（Google Drive 共有フォルダ）

現状のノートブック・`config.py` は上記の正式アーカイブを自動で参照する仕組みにはなっておらず、従来どおり Google Drive 上の共有フォルダを直接参照している。ただし共有フォルダの中身自体は空ではない: NWB（`nwb_manual`）はGIN版を取得して手動配置したもので正式アーカイブ由来だが、CSV（`trials_L1L2.csv`）はハッカソンで作成した抽出物で正式アーカイブには存在しない。`config.py`／ノートブックからGIN等を自動取得する仕組みへの移行は未着手（2026-08-16時点）。

### ソース（共有フォルダ）

| 種別 | 中身 | Colab | ローカル（このマシン） |
| :--- | :--- | :--- | :--- |
| CSV | 30 Hz 行動ログ `trials_L1L2.csv` | `/content/drive/MyDrive/hackathon_data` | `G:\.shortcut-targets-by-id\1fI6PWRHgihU6asA4OyW-_rN-JII33Fkj\hackathon_data`（2026-08-16 存在確認済み） |
| NWB | 神経画像・公式試行・表情 | `/content/drive/MyDrive/nwb_manual`（GIN版を取得して手動配置） | `G:\マイドライブ\nwb_manual`（2026-08-21確認。`VG1GC-66` の全14 task-day分（`task-day1`, `3`–`15`）が`nwb_shrink`ワークフロー（[ノート15](../notebooks/15_gin_fetch_processing_only.ipynb)）経由で軽量化版として存在。内部構造は[上記](#gin利用時の実務メモ1ファイル約1gbの場合)を参照） |

`trials_L1L2.csv` はハッカソンで作成した抽出物で、論文のNWBファイルそのものではない。音なし条件も含む、すべてのレバー引き試行についてレバー引き時間を計算している。CSV は 25 匹中 24 匹に `trials_L1L2.csv` がある（`VG1GC-48` のみ 0 日）。個体によって欠ける課題日がある。注意: このCSVの `trial_outcome` 列は miss/failure の使い方がNWB公式trialsテーブルと正反対（`VG1GC-66`全日で確認: 同じ試行群がNWBではmiss=無反応、CSVではfailureと呼ばれる）。このため `src/glmhmm_ver4.py` は文字列ラベルではなく `pull_onset` の有無で試行タイプを判定する（詳細は[CLAUDE.md](../CLAUDE.md)の既知の落とし穴を参照）。

共有フォルダ本来の NWB 置き場（`...\braidyn-bc\data` のショートカット先）は `data/` も `.nwb` も無く空だが、手動で集めた `nwb_manual` フォルダは Colab・ローカル（WSL / Windows）のどちらからも `config.py` が優先的に見に行く（`src/glmhmm_ver4.py` の `find_nwb_file()`）。2026-08-21時点では `VG1GC-66` の全14 task-day分が利用可能で、13 次元（顔特徴）学習も全日で行える（[ノート16](../notebooks/16_glmhmm_ver4_faceB_alldays.ipynb)）。ローカル実行の手順は [README.md](../README.md) の「ローカル（WSL、動作確認済み）」を参照。

### 個人バックアップ（CSV のみ）

共有が外れても 4 次元 GLM-HMM 用の行動 CSV が残るよう、`trials_L1L2.csv` だけをマイドライブへ複製した。

- 保存先: `マイドライブ/braidyn-bc-backup/hackathon_data/`
- 件数: 347 ファイル、約 0.6 GB
- 構成: `hackathon_data/<マウスID>/task-dayN/trials_L1L2.csv`（共有フォルダと同じ）
- 対象外: NWB、動画、imaging、`hackathon_data` 内の他ファイル

#### コピーのやり方

Drive API や Colab アップロードは使っていない。Windows 上で Google Drive デスクトップがマウントした `G:` 同士を、Python の `shutil.copy2` でファイルコピーした。

1. 入力: 共有ショートカット `hackathon_data` を再帰し、名前が `trials_L1L2.csv` のファイルだけ集める。
2. 出力: `G:\マイドライブ\braidyn-bc-backup\hackathon_data\` の下に、マウス ID と `task-day` の相対パスをそのまま再現する。
3. 各ファイルを `copy2`（時刻メタデータ付き）で複製する。サイズ一致ならスキップ。
4. Drive デスクトップがマイドライブへの書き込みをクラウドへ同期する。別途「アップロード」操作はしていない。

`config.py` は共有の `DATA_CSV_ROOT` が無いとき、このバックアップを使う。
