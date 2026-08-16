# ノートブックとドキュメントの説明

`docs/` と `notebooks/` の対応表です。セットアップは [README.md](../README.md)、データ配置は [data.md](data.md) を見てください。

---

## 要件定義の2系統

GLM-HMM の仕様は2つあります。**同じモデル名でも、1データポイントの取り方が違います。**

| | [requirements_glmhmm.md](requirements_glmhmm.md) **Ver.3** | [requirements_ver4.md](requirements_ver4.md) **Ver.4** |
| :--- | :--- | :--- |
| 立場 | ノート `10` / `11` / `12` が実装している仕様 | ノート `14` と `src/glmhmm_ver4.py` が実装 |
| 1行の意味 | 0.1 秒の時間ビン | 定義された1試行 |
| 時系列の扱い | 30 Hz → 10 Hz にビニング。長い無反応は ITI カット | ビニングも ITI カットもしない。試行ウィンドウ外は捨てる |
| \(y\) | そのビンにレバー onset があるか | その試行ウィンドウに Action があるか |
| History | 前の**時間ビン** \(t-1\) | 前の**試行** \(k-1\) |
| 試行タイプ | ビン列なのでタイプ分けしない | Success / No Reaction / Short Pull / Second Pull / No Sound Pull |
| 共通部分 | 30 Hz のギャップ埋め・短引き除去、CSV と NWB の `merge_asof`、入力は Bias / Stimulus / Action History / Reward History | 同左 |

Ver.3 は「時刻ごとの引きやすさ」を、Ver.4 は「試行ごとの戦略」を状態として切り出す想定です。`11` で時間ビンだと状態が運動量に entangle した、という反省が Ver.4 側にあります。

---

## ノートブックのつながり

番号は作業順です。先頭2セルは共通（環境セットアップ → `data_loader` で代表セッションを読む）。

```
01 データ読み込み
 │
 ├─ 脳活動 EDA ──────── 02（レバー引き時）→ 03（音提示時）
 │
 ├─ 行動 EDA ────────── 04（音なしの日次）
 │                      05（試行ごとの引き長）
 │                      06（セッション内のタイミング）
 │                      08（引き長の本格EDA）
 │                      09（試行分類の定義固め）
 │
 ├─ 脇道 ────────────── 07（SARSA。本番モデルには未使用）
 │
 └─ GLM-HMM（Ver.3）── 09 の分類 → 10（入力作成）
                                    → 11（1個体学習）
                                    → 12（表情特徴を追加）
                         2b は ssm の参照実装
                         13 は作業用の空ノート
                         14 は Ver.4（試行単位。4 次元と 13 次元）
```

- `01` が入口。NWB / CSV の読み方だけ確認する。
- `02` と `03` は imaging を使う枝。レバー onset と音提示で皮質を切り、互いに条件を重ねる。
- `04`〜`09` は行動ログの枝。`04`/`05`/`08` が引き長、`06`/`09` が試行の種類と時刻。`08` と `09` の定義が、あとの入力作成に残る。
- `07` は強化学習の試作で、`10` 以降にはつながっていない。
- `10` が Ver.3 の入力、`11` がその学習。`11` の課題（状態が運動量になる）を受けて `12` が表情を足す。
- `14` が Ver.4。CSV の試行単位で 4 次元を学習し、NWB があれば顔 9 次元を足して 13 次元も学習する。

---

## 各ノートの内容

### 01_data_loading.ipynb

読み込み確認。`session.trials` / `entries` / imaging の中身を見る。

### 02_brain_activity_lever_pull_effect.ipynb

レバー引き瞬間の ROI 活動。音あり / なしを比較し、`pull_onset` と imaging 時刻のずれも見る。

### 03_brain_activity_sound_effects.ipynb

音提示まわりの ROI。成功 / 失敗、個体→集団、刺激前区間の検定まで広げる。

### 04_trial_num_and_pull_length_while_no_cue.ipynb

音なしレバー引きの、Day 1–15 の試行数と引き長。

### 05_pull_length_for_every_trials.ipynb

セッション内の引き長を、試行ごと・日ごとに散布する。

### 06_trials_num_and_ratio.ipynb

セッション内で、音あり / なし試行がいつ起きているか。回数と割合。

### 07_SARSA_model.ipynb

音の有無を状態にした SARSA。Q と引き長・pull 率を突き合わせる試作。

### 08_eda_pull_length.ipynb

`diff_value` の分布、下限カットの影響、複数マウスの日次平均。短引きノイズの閾値決めに使う。

### 09_eda_trials_num.ipynb

成功 / 失敗 / 音なし引き などの分類と、時刻カラムの照合。`10` のイベント定義の前段。

### 10_setup_GLM-HMM_input_data.ipynb

Ver.3 どおりに `train_ys` / `train_xs` を作る。整形 → 10 Hz ビン → History → ITI 分割。学習はしない。

### 11_build_GLM-HMM_model_for1mouse.ipynb

`10` の入力で 1 個体を学習する。正則化・History の有無を試し、状態解釈の問題をメモする。表情拡張の方針は `12` へ。

### 12_setup_input_data_ver2.ipynb

行動 4 次元に顔・身体 9 次元を足して再学習する。`11` の続き。

### 13_note.ipynb

セットアップだけの作業用ノート。

### 14_glmhmm_ver4_trials.ipynb

Ver.4。30 Hz 整形のあと試行を切り出し、**HMMは日ごとに独立して学習する**（日をまたぐ状態遷移・パラメータ共有はしない）。行動 4 次元は K=3 固定、顔つき 13 次元は K=2 と K=3 の両方を日ごとに学習して比較する（K=3 だと1状態が縮退することがあるため）。対象は既定 `VG1GC-66` の全日、顔つき 13 次元は NWB がある日のみ。引き長（`diff_value`）は入力に使わない。

### 2b Input Driven Observations (GLM-HMM).ipynb

ssm 公式チュートリアル。人工データ。`11` / `12` の API 参照。

---

## ソースコード

- `config.py` — Colab / ローカルで NWB・CSV のルートを切り替える。共有 CSV が無いときは `braidyn-bc-backup` を使う。
- `src/data_loader.py` — `load_nwb_session`, `load_trials_csv`。
- `src/glmhmm_ver4.py` — Ver.4 パイプライン。
- [data.md](data.md) — 共有フォルダの場所と CSV バックアップの手順。
