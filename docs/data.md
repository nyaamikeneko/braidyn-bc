# データ配置と CSV バックアップ

生データはこの Git リポジトリには入っていない。Google Drive 上の共有フォルダを `config.py` 経由で読む。

## ソース（共有フォルダ）

| 種別 | 中身 | Colab | ローカル（このマシン） |
| :--- | :--- | :--- | :--- |
| CSV | 30 Hz 行動ログ `trials_L1L2.csv` | `/content/drive/MyDrive/hackathon_data` | `G:\.shortcut-targets-by-id\1fI6PWRHgihU6asA4OyW-_rN-JII33Fkj\hackathon_data` |
| NWB | 神経画像・公式試行・表情 | `/content/drive/MyDrive/braidyn-bc/data` | 設定上は `...\1DtufNi90fhQp6kIcuS0MxtTz-Uk5LSS9\braidyn-bc\data` だが、このショートカット先に `data/` も `.nwb` も無い |

CSV は 25 匹中 24 匹に `trials_L1L2.csv` がある（`VG1GC-48` のみ 0 日）。個体によって欠ける課題日がある。

NWB がローカルで読めないのはパス設定の問題で、読み込みコードの不具合ではない。13 次元（顔特徴）は NWB の `entries` が必要なので、NWB が見える環境（Colab など）で回す。

## 個人バックアップ（CSV のみ）

共有が外れても 4 次元 GLM-HMM 用の行動 CSV が残るよう、`trials_L1L2.csv` だけをマイドライブへ複製した。

- 保存先: `マイドライブ/braidyn-bc-backup/hackathon_data/`
- 件数: 347 ファイル、約 0.6 GB
- 構成: `hackathon_data/<マウスID>/task-dayN/trials_L1L2.csv`（共有フォルダと同じ）
- 対象外: NWB、動画、imaging、`hackathon_data` 内の他ファイル

### コピーのやり方

Drive API や Colab アップロードは使っていない。Windows 上で Google Drive デスクトップがマウントした `G:` 同士を、Python の `shutil.copy2` でファイルコピーした。

1. 入力: 共有ショートカット `hackathon_data` を再帰し、名前が `trials_L1L2.csv` のファイルだけ集める。
2. 出力: `G:\マイドライブ\braidyn-bc-backup\hackathon_data\` の下に、マウス ID と `task-day` の相対パスをそのまま再現する。
3. 各ファイルを `copy2`（時刻メタデータ付き）で複製する。サイズ一致ならスキップ。
4. Drive デスクトップがマイドライブへの書き込みをクラウドへ同期する。別途「アップロード」操作はしていない。

`config.py` は共有の `DATA_CSV_ROOT` が無いとき、このバックアップを使う。
