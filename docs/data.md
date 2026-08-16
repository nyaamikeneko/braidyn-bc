# データ配置と CSV バックアップ

生データはこの Git リポジトリには入っていない。ローカル・Colab の実行は現状 Google Drive 上の共有フォルダを `config.py` 経由で読む運用のままだが、**正式な公開先は DANDI Archive・AWS S3・GIN の3系統に再編されている**（2026-08-16確認）。データの正式な引用・再取得にはこちらを使う。

## 0. 正式な公開先（DANDI / AWS S3 / GIN）

以前は Google Drive 上の NWB を直接参照していたが、現在は正式な永続アーカイブとして DANDI Archive・AWS S3・GIN の3系統に再編されている。Google Drive の NWB フォルダ自体はプロジェクトサイト上にリンクが残っているが、正式なアーカイブではない。

- プロジェクトサイト: https://nakaelab.github.io/braidyn-bc-database/index.html
- 該当データセット解説ページ: https://nakaelab.github.io/braidyn-bc-database/pages/operant-conditioning-process.html
- 論文（Scientific Data誌）: https://www.nature.com/articles/s41597-025-05482-y （→ [reference/kondo2025_braidynbc_dataset.md](../reference/kondo2025_braidynbc_dataset.md)）

| プラットフォーム | 内容 | サイズ目安 | DOI / 引用 | 主な用途 |
| :--- | :--- | :--- | :--- | :--- |
| [DANDI Archive](https://dandiarchive.org/dandiset/001425/)（Dandiset 001425, v0.250705.0947, CC-BY-4.0） | NWB形式の全データ（Raw画像含む） | 8.1 TB（1838ファイル） | 10.48324/dandi.001425/0.250705.0947 | NWB標準ツール（dandi CLI／Python API／fsspecストリーミング）で全データを再現性高く扱う。論文の付随データとして正式引用する場合もこちら |
| AWS S3（バケット `s3://braidyn-bc-buckets`、[ブラウザ表示](https://braidyn-bc-buckets.s3.amazonaws.com/index.html)、[CLIガイド](https://nakaelab.github.io/braidyn-bc-database/pages/aws-cli-guide.html)） | Rawデータ（動画・TIFF等の未加工ファイル）中心。NWBも同梱 | 約1700 GB | なし | 認証不要（`--no-sign-request`）。AWS CLI／boto3で顔・瞳孔・体の動画など生データを直接取得する |
| [GIN](https://gin.g-node.org/BraiDyn-BC/Kondo2025_CuedLeverPullNWB)（G-Node Infrastructure） | NWB形式のみ。Raw imagingデータを除いた軽量版 | 数十GB規模（未確認。取得前に`datalad status`で確認） | 10.12751/g-node.zbh16l | DataLad／git-annexで、軽量にNWBのみ・行動データや前処理済み信号を扱う。公式サイトのトップ・チュートリアルページには明記がなく、論文本文（Scientific Data誌）で確認できる情報 |

選び方の目安:

- 神経活動の信号解析のみ（dF/F・行動タイムスタンプ等）→ **GIN**（軽量）
- 生の動画・画像も使う（顔・瞳孔・体の動画解析など）→ **AWS S3** から必要セッションのみ取得
- NWB全体を再現性重視で厳密に扱う／正式引用 → **DANDI**

### GIN利用時の実務メモ（1ファイル約1GBの場合）

ファイルサイズが1GB程度であれば、Google Colabの一時ディスクよりも、永続化できるローカル環境での作業を基本とする。理由: Colab無料枠のディスクはセッション終了でリセットされ、DataLad/git-annexでの再取得が繰り返し発生しやすく、GINのgit-annex経由の取得は小さなgitオブジェクトのやり取りが多いため、Colabの一時ストレージ・帯域と相性がよくない。探索段階で数ファイルだけ試したい場合、またはGoogle Driveをマウントして永続化する運用にする場合はColabも選択肢。

```bash
pip install datalad
datalad clone https://gin.g-node.org/BraiDyn-BC/Kondo2025_CuedLeverPullNWB
cd Kondo2025_CuedLeverPullNWB

datalad status                     # まずメタデータ・構造のみ確認（実体は落ちない）
find . -name "*.nwb"

datalad get sub-01/ses-01/*.nwb    # 必要なsubject/sessionだけ実体を取得
```

25匹×15セッション分あるため、全部を一度に取得すると数十〜百GB規模になり得る。事前に`datalad status`で構造を把握し、必要な範囲を絞ってから`get`することを推奨。

### 未確認・要フォローアップ事項

- GINリポジトリの正確な合計サイズ（サイト上に明記なし。取得前に`datalad status`で確認要）
- Google Drive版NWBとDANDI/GIN版NWBの内容差分の有無（バージョン更新が反映されているか）
- resting-state／sensory stimセッションのGIN収録範囲（論文では4セッションのresting-state記載あり）

### その他の関連リソース

| リソース | URL |
| :--- | :--- |
| Pythonチュートリアル一覧（Google Drive） | https://drive.google.com/drive/folders/1f5MBwx0tfmJQgbwJ24MVGnka4QZQzfJI |
| 解析用データパイプライン（GitHub） | https://github.com/BraiDyn-BC/bdbc-data-pipeline |
| NWB探索ツール（GitHub） | https://github.com/BraiDyn-BC/bdbc-nwb-explorer |
| Matsuzaki Lab 独自配布ページ | https://mmlab-repo.m.u-tokyo.ac.jp/r/Matsuzaki/BraiDyn-BC_CuedLeverPull |

---

## 1. このリポジトリでの現状の使い方（Google Drive 共有フォルダ）

現状のノートブック・`config.py` は上記の正式アーカイブではなく、従来どおり Google Drive 上の共有フォルダを直接参照している。正式アーカイブへの移行は未着手（2026-08-16時点）。

### ソース（共有フォルダ）

| 種別 | 中身 | Colab | ローカル（このマシン） |
| :--- | :--- | :--- | :--- |
| CSV | 30 Hz 行動ログ `trials_L1L2.csv` | `/content/drive/MyDrive/hackathon_data` | `G:\.shortcut-targets-by-id\1fI6PWRHgihU6asA4OyW-_rN-JII33Fkj\hackathon_data`（2026-08-16 存在確認済み） |
| NWB | 神経画像・公式試行・表情 | `/content/drive/MyDrive/nwb_manual`（手動配置分） | `G:\マイドライブ\nwb_manual`（2026-08-16確認。`VG1GC-66\VG1GC-66_2023-09-08_task-day15.nwb` の1件のみ存在） |

CSV は 25 匹中 24 匹に `trials_L1L2.csv` がある（`VG1GC-48` のみ 0 日）。個体によって欠ける課題日がある。

共有フォルダ本来の NWB 置き場（`...\braidyn-bc\data` のショートカット先）は `data/` も `.nwb` も無く空だが、手動で集めた `nwb_manual` フォルダは Colab・ローカル（WSL / Windows）のどちらからも `config.py` が優先的に見に行く（`src/glmhmm_ver4.py` の `find_nwb_file()`）。2026-08-16時点では `VG1GC-66` の `task-day15` のみが利用可能で、13 次元（顔特徴）学習はこの日に限られる。ローカル実行の手順は [README.md](../README.md) の「ローカル（WSL、動作確認済み）」を参照。

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
