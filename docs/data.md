# データ配置と CSV バックアップ

生データはこの Git リポジトリには入っていない。Google Drive 上の共有フォルダを `config.py` 経由で読む。

## ソース（共有フォルダ）

| 種別 | 中身 | Colab | ローカル（このマシン） |
| :--- | :--- | :--- | :--- |
| CSV | 30 Hz 行動ログ `trials_L1L2.csv` | `/content/drive/MyDrive/hackathon_data` | `G:\.shortcut-targets-by-id\1fI6PWRHgihU6asA4OyW-_rN-JII33Fkj\hackathon_data`（2026-08-16 存在確認済み） |
| NWB | 神経画像・公式試行・表情 | `/content/drive/MyDrive/nwb_manual`（手動配置分） | `G:\マイドライブ\nwb_manual`（2026-08-16確認。`VG1GC-66\VG1GC-66_2023-09-08_task-day15.nwb` の1件のみ存在） |

CSV は 25 匹中 24 匹に `trials_L1L2.csv` がある（`VG1GC-48` のみ 0 日）。個体によって欠ける課題日がある。

共有フォルダ本来の NWB 置き場（`...\braidyn-bc\data` のショートカット先）は `data/` も `.nwb` も無く空だが、手動で集めた `nwb_manual` フォルダは Colab・ローカル（WSL / Windows）のどちらからも `config.py` が優先的に見に行く（`src/glmhmm_ver4.py` の `find_nwb_file()`）。2026-08-16時点では `VG1GC-66` の `task-day15` のみが利用可能で、13 次元（顔特徴）学習はこの日に限られる。ローカル実行の手順は [README.md](../README.md) の「ローカル（WSL、動作確認済み）」を参照。

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
