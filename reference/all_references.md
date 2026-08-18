# 先行文献まとめ

[reference/README.md](README.md) の一覧にある10本の先行文献を、1ファイルに集約したものです。論文間・本リポジトリとの関連性は [reference/relations.md](relations.md) を参照してください。

論文PDFを [sources/](sources/) に保存している6本（#1, #2, #3, #4, #7, #8）は個別ファイルがあり、要旨（原文PDFに基づく箇条書き）とモデル定義・メソッドの詳細はそちらに記載しています。ここでは書誌情報と要約のみを示します。PDF未保存の4本（#5, #6, #9, #10）は、この一覧が唯一の情報源です。

---

## 1. Multimodal dataset linking wide-field calcium imaging to behavior changes in operant lever-pull task in mice

*マウスのオペラント・レバー引き課題における広視野カルシウムイメージングと行動変化を結びつけたマルチモーダルデータセット*

Kondo, M. et al. — Scientific Data 12, 1264 (2025). DOI: [10.1038/s41597-025-05482-y](https://doi.org/10.1038/s41597-025-05482-y) — 個別ファイル: [kondo2025_braidynbc_dataset.md](kondo2025_braidynbc_dataset.md)（原本PDFあり）

![Figure 1](images/kondo2025_braidynbc_dataset_fig1.jpg)

### 要約

- **問題**
  - 運動学習の神経メカニズム・急速な学習効果・長期適応を調べるには、神経活動・身体運動・環境パラメータを同時かつ長期的に記録したデータセットが必要。
- **手法**
  - 頭部固定マウスのレバー引き課題（2週間・15セッション）を、以下と同時記録:
    - 広視野カルシウムイメージング（大脳皮質全体）
    - 身体・顔・眼球運動ビデオグラフィ（DeepLabCut）
    - レバー位置・報酬・環境パラメータ
  - NWB形式に整形し、FAIR原則に準拠して公開。
- **結果**
  - マウス25匹、375セッション中364セッションでデータ収集に成功。
  - 応答率は訓練を通じて上昇し、DeepLabCut・皮質領域レジストレーションの妥当性を検証済み。

---

## 2. Mice alternate between discrete strategies during perceptual decision-making

*マウスは知覚的意思決定の最中、離散的な複数の戦略を交互に切り替える*

Ashwood, Z. C. et al. (International Brain Laboratory) — Nature Neuroscience 25, 201–212 (2022). DOI: [10.1038/s41593-021-01007-z](https://doi.org/10.1038/s41593-021-01007-z) — 個別ファイル: [ashwood2022_discrete_strategies.md](ashwood2022_discrete_strategies.md)（原本PDFあり）

![Figure 1](images/ashwood2022_discrete_strategies_fig1.jpg)

### 要約

- **問題**
  - 知覚意思決定の古典的解析は、動物が単一で一貫した戦略を使う、あるいは緩やかに進化すると仮定してきた。
  - 離散的に切り替わる複数戦略の混在を検出できる枠組みを提示し、「lapse」現象への代替説明を検証する。
- **手法**
  - IBLの視覚検出課題（Gaborグレーティング、コントラスト0〜100%）のマウス・ヒトデータに、Bernoulli GLMを観測モデルとするGLM-HMMを適用。
  - 4次元デザイン行列（刺激・バイアス・前試行の選択・win-stay-lose-switch）を入力に、5-fold cross-validationで状態数を選択。
- **結果**
  - IBLマウス37匹で3状態が最適。
    - 感覚刺激に強く依存し正答率が高い「Engaged」状態（例示個体で90%）。
    - 刺激依存が弱くバイアスが大きい2つの「Biased」状態（同58〜60%）。
  - 状態は数十〜数百試行持続し、げっ歯類実験で観察される「lapse」現象への代替説明を与える。

---

## 3. Internal states emerge early during learning of a perceptual decision-making task

*知覚的意思決定課題の学習の初期段階から内部状態が出現する*

Cuturela, L. I. et al. (International Brain Laboratory) — bioRxiv preprint (2024). DOI: [10.1101/2024.11.30.626182](https://doi.org/10.1101/2024.11.30.626182) — 個別ファイル: [cuturela2024_internal_states_early.md](cuturela2024_internal_states_early.md)（原本PDFあり）

![Figure 1](images/cuturela2024_internal_states_early_fig1.jpg)

### 要約

- **問題**
  - Ashwood et al. (2022) のGLM-HMMは学習後の定常状態を前提とし、学習過程そのもの（いつ・どう複数戦略が出現するか）は扱えない。
- **手法**
  - GLM重み・遷移行列がセッション間で緩やかに変化できる「dynamic GLM-HMM」を提案。
  - IBLの2値強制選択視覚課題（32匹、基本課題〜フル課題）に個体ごとに適用。
- **結果**
  - 2セッション目の時点で既に3状態モデルが1状態モデルを上回る。
  - 学習の非常に早い段階からEngaged/Biased状態を切り替えており、成績向上は「刺激感度の増加」と「Engaged状態のoccupancy増加」の組み合わせで説明される。

---

## 4. Infinite hidden Markov models can dissect the complexities of learning

*無限隠れマルコフモデルは学習の複雑性を解剖できる*

Bruijns, S. A. et al. (International Brain Laboratory), Dayan, P. — Nature Neuroscience 29, 186–194 (2026年1月号 / 2025年12月30日オンライン公開). DOI: [10.1038/s41593-025-02130-x](https://doi.org/10.1038/s41593-025-02130-x) / [bioRxiv preprint](https://www.biorxiv.org/content/10.1101/2023.12.22.573001) — 個別ファイル: [bruijns2025_infinite_hmm.md](bruijns2025_infinite_hmm.md)（原本PDFあり）

![Figure 1](images/bruijns2025_infinite_hmm_fig1.jpg)

### 要約

- **問題**
  - 課題の随伴性を学習する過程は個体ごとに独特で、探索と適応を繰り返しながら方略を何度も修正する。
  - こうした学習曲線を定量化するには、新しい行動の出現（急な変化）と既存行動の緩やかな適応の両方を捉えられるモデルが必要。
- **手法**
  - 動的な無限隠れセミマルコフモデル（diHMM）を提案。
    - 潜在状態が行動の1コンポーネント（ロジスティック回帰で表される方略）に対応する。
    - 階層ディリクレ過程により状態数を固定せず、既存のどの状態にも当てはまらない急な変化が起きたら新しい状態を導入する（fast process）。
    - 状態ごとのGLM重みはガウシアンランダムウォークでセッション間を緩やかにドリフトする（slow process）。
    - 状態の持続時間は幾何分布ではなく負の二項分布で明示的にモデル化するセミマルコフ構造を採用。
- **結果**
  - IBLの視覚検出課題を学習するマウス134匹（平均24.4セッション、総計>1.9M試行）に適用。
    - ほぼ全個体が3段階（未分化で誤りがちな初期行動→片側のみの部分的理解→左右両方の完全な理解）を経て進行するが、各段階に要するセッション数・状態構成は個体間で大きくばらつく。
    - 新しい状態の導入はセッション開始時に集中しやすい。
    - 学習初期の応答バイアスはその後のバイアスを予測しない。

---

## 5. Identifying the factors governing internal state switches during nonstationary sensory decision-making

*非定常な感覚性意思決定における内部状態切り替えを支配する要因の同定*

Mohammadi, Z., Ashwood, Z. C., Pillow, J. W. — Nature Communications (2025). DOI: [10.1038/s41467-025-66738-0](https://doi.org/10.1038/s41467-025-66738-0)

![Figure 1](images/mohammadi2025_internal_state_switches_fig1.jpg)

### 要約

- **問題**
  - マウスは知覚意思決定の際、1セッション内で複数の戦略を切り替えることが知られているが、非定常な環境下での切り替え行動や、切り替えを支配する要因は不明だった。
- **手法**
  - 入力依存の遷移を持つ内部状態モデル。
    - 各状態の刺激依存選択をモデル化する Bernoulli GLM 群。
    - 状態間の入力依存遷移をモデル化する multinomial GLM。
  - 刺激統計が非定常な二値意思決定課題（IBL）のデータセットに適用。
- **結果**
  - マウスの行動は4状態モデルで精度良く説明できた。
    - 左右にわずかなバイアスを持ちつつ成績の良い2つの「Engaged」状態。
    - より大きな左右バイアスを持ち成績の低い2つの「Disengaged」状態。
  - マウスは刺激ブロックの偏りに応じたバイアス戦略を優先的に用いる。
  - 過去の選択・刺激がバイアス方向の状態間遷移を、過去の報酬がEngaged/Disengaged間の遷移を予測する。
    - 過去の報酬が多いほどDisengaged状態への遷移が起きやすく、満腹（satiety）と関連する可能性。

---

## 6. A reservoir of foraging decision variables in the mouse brain

*マウス脳内における採食意思決定変数の貯蔵庫*

Cazettes, F. et al. — Nature Neuroscience 26(5), 840–849 (2023). DOI: [10.1038/s41593-023-01305-8](https://doi.org/10.1038/s41593-023-01305-8)

![Figure 1](images/cazettes2023_foraging_reservoir_fig1.jpg)

### 要約

同グループによる [cazettes2025_facial_expressions.md](cazettes2025_facial_expressions.md)（表情側の報告）と対をなす、神経活動側の報告。

- **問題**
  - マウスは採食課題中に複数の意思決定変数（decision variables, DV）を使い分け、セッション内で戦略を切り替える。この使い分けを支える神経基盤は不明だった。
- **手法**
  - 採食課題中のマウス前頭皮質からニューロン集団活動を記録。
  - 光遺伝学的操作で二次運動皮質（M2）の必要性を検証。
- **結果**
  - M2が異なるDVの使い分けに必要であることが示された。
  - M2の活動は、現在の行動を最もよく説明するDVだけでなく、その時点では使われていない別のDV群も同時に符号化していた。
    - M2は複数タスクに対応可能な計算の「貯蔵庫（reservoir）」を常時保持している。
  - この神経多重化は、学習や環境変化への適応を有利にすると考察されている。

---

## 7. Facial expressions in mice reveal latent cognitive variables and their neural correlates

*マウスの表情は潜在的な認知変数とその神経相関を明らかにする*

Cazettes, F. et al. — Nature Neuroscience (2025). DOI: [10.1038/s41593-025-02071-5](https://doi.org/10.1038/s41593-025-02071-5) — 個別ファイル: [cazettes2025_facial_expressions.md](cazettes2025_facial_expressions.md)（原本PDFあり）

![Figure 1](images/cazettes2025_facial_expressions_fig1.jpg)

### 要約

- **問題**
  - 表情が「身体の生体力学的な結合による連動」なのか「真に内部状態を反映する」のかを判別するのは難しい。
- **手法**
  - 採食課題中のマウスで、LM-HMMによる戦略推定・GLMによる表情復号・二次運動皮質（M2）の光遺伝学的操作を組み合わせる。
- **結果**
  - 現在使用中の意思決定変数（DV）だけでなく、その時点では表出されていない独立したDVまでも表情から復号できた。
  - 表情に表出されるDVの少なくとも一部がM2由来であることを示した。

---

## 8. Inferring internal states across mice and monkeys using facial features

*顔特徴を用いたマウスとサルにまたがる内部状態の推定*

Tlaie, A. et al. — Nature Communications 16, 5168 (2025). DOI: [10.1038/s41467-025-60296-1](https://doi.org/10.1038/s41467-025-60296-1) — 個別ファイル: [tlaie2025_facial_features_mice_monkeys.md](tlaie2025_facial_features_mice_monkeys.md)（原本PDFあり）

![Figure 1](images/tlaie2025_facial_features_mice_monkeys_fig1.jpg)

### 要約

- **問題**
  - 内部認知状態が種を超えて共通の実体を持つかは不明。
- **手法**
  - マウス・マカクザルに同一のVR採食課題を課し、顔特徴からMarkov-Switching Linear Regression（MSLR）で内部状態を推定。
- **結果**
  - 両種共通して「注意（attentive）」「衝動的（impulsive）」「不注意（inattentive）」の3プロファイルが見られた。
  - 表情が種を超えて共通の内部状態を反映することを示した。

---

## 9. Spontaneous behaviour is structured by reinforcement without explicit reward

*自発行動は明示的な報酬なしに強化によって構造化される*

Markowitz, J. E. et al., Linderman, S. W., Datta, S. R. — Nature 614(7946), 108–117 (2023). DOI: [10.1038/s41586-022-05611-2](https://doi.org/10.1038/s41586-022-05611-2)

![Figure 1](images/markowitz2023_spontaneous_behaviour_fig1.jpg)

### 要約

著者に本リポジトリが使う `ssm` ライブラリの開発者 Scott W. Linderman が含まれる。

- **問題**
  - 課題構造・感覚手がかり・外因性報酬が一切ない自由行動下でも、行動が体系的に構造化されるかは不明だった。
- **手法**
  - マウスの自発的な行動（モーションモジュール列）と背側線条体（DLS）のドパミン変動を同時記録し、光遺伝学的操作で因果性を検証。
- **結果**
  - ドパミン変動は行動モジュールの使用頻度・出現順序を変化させ、後続の行動選択を予測できた。
  - 光遺伝学的操作により、ドパミンが特定の行動モジュールを強化し、行動配列の多様性を増加させることを確認。
  - 強化学習モデルによる解析から、ドパミン変動が報酬信号の代替として機能し、線条体が行動モジュールを動的に組み立てていることが示唆された。

---

## 10. Hidden Markov models reveal behavioral state dynamics in depth-related locomotion in mice

*隠れマルコフモデルはマウスの奥行き関連移動行動における行動状態動態を明らかにする*

Shuto, H. et al. — PLOS ONE 20(8), e0329367 (2025). DOI: [10.1371/journal.pone.0329367](https://doi.org/10.1371/journal.pone.0329367)

![Figure 1](images/shuto2025_hmm_depth_locomotion_fig1.jpg)

### 要約

- **問題**
  - 視覚的な奥行き手がかりに対するマウスの行動応答を、離散的な行動状態として定量化したい。
- **手法**
  - 円形装置と隠れマルコフモデル（HMM）解析を組み合わせ、野生型マウスと網膜変性モデル（rd1-2J）を比較。
- **結果**
  - マウスは奥行き手がかりに応じて「静止（resting）」「探索（exploring）」「移動（navigating）」の3状態間を遷移することが示された。
  - 奥行き知覚には最適な空間周波数帯（6〜8 cm相当）があり、複数の空間手がかりを統合した処理が行われている。
  - 初期の強い崖回避反応が時間とともにより繊細な行動適応へ変化する。
  - 野生型と網膜変性モデルの比較により、これらの行動パターンが視覚処理を特異的に反映することが確認された。
