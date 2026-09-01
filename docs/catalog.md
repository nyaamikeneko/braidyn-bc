# ノートブックとドキュメントの説明

`docs/` と `notebooks/` の対応表です。セットアップは [README.md](../README.md)、データ配置は [data.md](data.md) を見てください。

---

## 要件定義の3系統

GLM-HMM の仕様は3つあります。**同じモデル名でも、1データポイントの取り方・状態推定の粒度が違います。**（さらに古い [Ver.2.2](requirements_glmhmm_legacy_v2.2.md) は Ver.3 に置き換えられたレガシー版として参考保存）

| | [requirements_glmhmm.md](requirements_glmhmm.md) **Ver.3** | [requirements_ver4.md](requirements_ver4.md) **Ver.4** | [requirements_ver5.md](requirements_ver5.md) **Ver.5** |
| :--- | :--- | :--- | :--- |
| 立場 | ノート `10` / `11` / `12` が実装している仕様 | ノート `14` / `16` と `src/glmhmm_ver4.py` が実装 | 設計のみ・未実装（対応するノート・srcなし） |
| 1行の意味 | 0.1 秒の時間ビン | 定義された1試行 | 1試行。ただし**音提示試行のみ**（音提示外の自発押下は系列に入れない） |
| 時系列の扱い | 30 Hz → 10 Hz にビニング。長い無反応は ITI カット | ビニングも ITI カットもしない。試行ウィンドウ外は捨てる | ビニングしない。音提示試行のウィンドウ外は捨てる（ITI は自発押下レートの記述量としてのみ参照） |
| \(y\) | そのビンにレバー onset があるか | その試行ウィンドウに Action があるか | **2系統を切り替え可能**。系統A: 二値（cue に応答したか＝No Reaction か否か）／系統B: 3値カテゴリカル（Success / Short Pull / No Reaction） |
| History | 前の**時間ビン** \(t-1\) | 前の**試行** \(k-1\) | 前の**音提示試行** \(k-1\)（両系統で共通）。系列が変わったので Ver.4 の同名入力とは分布が別物 |
| 試行タイプ | ビン列なのでタイプ分けしない | Success / No Reaction / Short Pull / Second Pull / No Sound Pull | Success / Short Pull / No Reaction の3タイプ。Second Pull は属する音提示試行に吸収し、No Sound Pull は系列から除外。系統Bではこの3タイプがそのまま \(y\) のカテゴリ |
| 状態推定の単位 | セッション内で1本のHMM | **day単位で独立**に1本のHMM（状態ラベルはdayをまたいで対応しない） | **Day 1–15を貫くDynamic GLM-HMM**（GLM重み・遷移行列がdayをまたいで緩やかに変化し、状態ラベルが対応する） |
| 皮質活動の扱い | 未使用 | 未使用 | GLM-HMMの入力には使わず、独立の生物学的妥当性検証チャンネルとして使用 |
| 共通部分 | 30 Hz のギャップ埋め・短引き除去、CSV と NWB の `merge_asof`、入力は Bias / Stimulus / Action History / Reward History | 同左（顔9次元を加えた13次元の拡張あり） | 30 Hz の前処理と `merge_asof` は同左。入力は行動3次元（Bias / Action History / Reward History）で、Stimulus は系列が音提示試行だけになり定数化するため落とす。顔9次元も不採用で、皮質と並ぶ独立検証チャンネルに回す |

Ver.3 は「時刻ごとの引きやすさ」を、Ver.4 は「試行ごとの戦略」を状態として切り出す想定です。`11` で時間ビンだと状態が運動量に entangle した、という反省が Ver.4 側にあります。Ver.5 は Ver.4 の「日ごと独立学習」だと学習ダイナミクス（[RQ.md](RQ.md) の RQ2）を検証できないという制約を受け、Dynamic GLM-HMM（Cuturela et al. 2024 準拠）で日をまたぐ状態ラベルの対応を確保し、皮質活動を独立検証チャンネルとして統合する拡張。

Ver.5 は試行系列も変えています。Ver.4 は音提示外の自発押下（No Sound Pull）を1試行1行として持ちますが、この試行は「押下が起きたこと」で定義されるため \(x_{stim}=0\) の行が定義上すべて \(y=1\) になり、Bias と Stimulus の重みが識別されない・Action History が上限に飽和する、といった帰結を生みます（実測値は [requirements_ver5.md](requirements_ver5.md) 2.2節）。Ver.5 は系列を音提示試行だけに限ることでこれを構造的に取り除き、Stimulus を入力から落とします。自発押下は捨てるのではなく、状態を事後的に特徴づける記述量として残し、状態依存レートを持つ Poisson emission として明示的にモデル化する拡張を [design_iti_poisson_emission.md](design_iti_poisson_emission.md) に設計だけ用意してあります。

観測モデルは2系統（二値／試行タイプの3値）用意して切り替え可能にし、どちらが状態構造をよく説明するかを比較できるようにする。3値は Success に至る状態と Short Pull に落ちる状態を区別するための拡張。顔特徴は入力から外し、皮質・表情の両方を検証側に置く。皮質解析の主参照は Aloor et al. 2026。

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
                          → 16（学習Bのみ・全task-dayに拡張）
```

- `01` が入口。NWB / CSV の読み方だけ確認する。
- `02` と `03` は imaging を使う枝。レバー onset と音提示で皮質を切り、互いに条件を重ねる。
- `04`〜`09` は行動ログの枝。`04`/`05`/`08` が引き長、`06`/`09` が試行の種類と時刻。`08` と `09` の定義が、あとの入力作成に残る。
- `07` は強化学習の試作で、`10` 以降にはつながっていない。
- `10` が Ver.3 の入力、`11` がその学習。`11` の課題（状態が運動量になる）を受けて `12` が表情を足す。
- `14` が Ver.4。CSV の試行単位で 4 次元を学習し、NWB があれば顔 9 次元を足して 13 次元も学習する。
- `16` は `14` の学習B（顔つき13次元）だけを、NWBが揃った全task-dayに拡張したもの。

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

セクション7・8で、代表日 (`task-day15`) だけでなく全14日分の GLM 重み・状態デコードを可視化する。実測では、4次元 K=3 固定モデルは**多くの日で3状態のうち1〜2状態しか実際には使われない**（Viterbi 系列で occupancy=0 になる状態がある）。3状態すべてに実質的な占有があるのは `task-day5` くらいで（それでも1状態が約9割を占める）、`task-day8` / `task-day15` は完全に1状態のみに縮退する。原因は、使われない状態が EM で事後責任をほぼ受け取らず、GLM 重みが事前分布（平均0）付近に留まって他状態の重みとほぼ重なってしまうため（`plot_glm_weights` で線が消えて見える）。K=3 を全日に固定で当てはめている以上の設計上の制約であり、バグではない。顔つき13次元モデル（`task-day15`, K=3）は行動4次元よりも縮退しにくく、3状態とも使われる傾向がある。

### 16_glmhmm_ver4_faceB_alldays.ipynb

`14` の学習B（顔つき13次元）だけを取り出し、対象個体の全task-day（NWBが揃った14日）で日ごとに独立学習する。状態数はK=3固定（`14`にあったK=2との比較はしない）。学習Aとの比較・LL比較表は行わない。

学習ループの前に、全日を通した trial type 内訳（積み上げ棒）と、刺激タイプ（Success / Short Pull / Second Pull / No Sound Pull）別の pull duration（`t_onset` から実際にレバーが離されるまでの実測保持時間、`t_start`/`t_end` は使わない。両者とも `src/glmhmm_ver4.py` の `compute_pull_window()` が全trial typeについて計算し、`process_session()` 経由で `trial_df` に `pull_end`/`pull_duration` として自動で乗る）の日変化を確認する。ギャップ埋めで橋渡しされた保持が公式ウィンドウ終端（`t_end`）を超えて続く少数の試行は日ごとの集計から除外している（保持時間の測り方と関連する落とし穴は[CLAUDE.md](../CLAUDE.md)を参照）。

続けて3つの感度チェックを行う。

- `GAP_FILL_LIMIT`（30Hzレバー信号のギャップ埋め上限フレーム数）を0/1/2で振り、全日プールでpull durationの分布がどれだけ動くかをヒストグラムで比較する。
- `attach_face_features()` の集計窓（`t_start`〜`t_end`）の長さがtrial_typeごとにどれだけ違うか、その窓長が生の顔特徴量（z-score化前）とどれだけ相関するかを確認する。比較として、`pull_end` を使った窓（`t_onset`〜`pull_end`、No Reactionのみ従来通り）の長さも並べる。
- 上の窓長バイアスに対処するため、集計窓を `v4.face_window_bounds()` の3方式（A `trial`＝現行のセッションタイム基準、B `pull`＝`t_onset`〜`pull_end`、C `onset_fixed`＝pull onset基準の1.0秒固定窓）で切り出し直して比較する。Cは窓長も窓内フレーム数も全試行で揃うので、窓長そのものが集計値に効く経路が閉じた状態の基準になる。窓長・フレーム数の分布、各方式の特徴量と `pull_duration` の相関、trial_typeによる分散説明率 η²、方式間の一致度を出す。

日ごとの学習後は、GLM重み・遷移行列・状態別行動サマリー（action probability・trial-type mix）に加えて、trial type・stimulus・action history・reward history・state posterior・Viterbi pathを試行インデックスを共有軸とする1枚のパネル図（`v4.plot_day_panel`）にまとめて可視化する。trial typeの色分けでNo Reactionを含む5種類の試行タイプを直接区別できるため、stimulus段は`x_stim=1`の区間だけを青塗りする単純な表示にとどめている。

### 2b Input Driven Observations (GLM-HMM).ipynb

ssm 公式チュートリアル。人工データ。`11` / `12` の API 参照。

---

## ソースコード

- `config.py` — Colab / ローカルで NWB・CSV のルートを切り替える。共有 CSV が無いときは `braidyn-bc-backup` を使う。
- `src/data_loader.py` — `load_nwb_session`, `load_trials_csv`。
- `src/glmhmm_ver4.py` — Ver.4 パイプライン。
- [data.md](data.md) — 正式な公開先（DANDI / AWS S3 / GIN）と、共有フォルダの場所・CSV バックアップの手順。

Ver.5（[requirements_ver5.md](requirements_ver5.md)）に対応する `src/` モジュール・ノートブックはまだ無い。設計段階。その先の拡張案として [design_iti_poisson_emission.md](design_iti_poisson_emission.md)（自発押下の状態依存 Poisson emission）があるが、こちらも設計のみ。
