# 先行文献まとめ

[reference/README.md](README.md) の一覧にある10本の先行文献を、1ファイルに集約したものです。論文間・本リポジトリとの関連性は [reference/relations.md](relations.md) を参照してください。

論文PDFを [sources/](sources/) に保存している5本（#1, #2, #3, #7, #8）は個別ファイルがあり、要旨（原文PDFに基づく箇条書き）とモデル定義・メソッドの詳細はそちらに記載しています。ここでは書誌情報と要約のみを示します。PDF未保存の5本（#4, #5, #6, #9, #10）は、この一覧が唯一の情報源です。

---

## 1. Multimodal dataset linking wide-field calcium imaging to behavior changes in operant lever-pull task in mice

*マウスのオペラント・レバー引き課題における広視野カルシウムイメージングと行動変化を結びつけたマルチモーダルデータセット*

Kondo, M. et al. — Scientific Data 12, 1264 (2025). DOI: [10.1038/s41597-025-05482-y](https://doi.org/10.1038/s41597-025-05482-y) — 個別ファイル: [kondo2025_braidynbc_dataset.md](kondo2025_braidynbc_dataset.md)（原本PDFあり）

![Figure 1](images/kondo2025_braidynbc_dataset_fig1.jpg)

*出典: Kondo et al. (2025) Scientific Data, [10.1038/s41597-025-05482-y](https://doi.org/10.1038/s41597-025-05482-y)（個人の研究メモ用途での引用）*

本リポジトリが解析対象とする NWB / CSV データそのものの記述論文。頭部固定マウスのレバー引き課題（2週間・15セッション）を、広視野カルシウムイメージング・身体表情ビデオグラフィ・環境パラメータと同時記録したマルチモーダルデータセット。詳細は [kondo2025_braidynbc_dataset.md](kondo2025_braidynbc_dataset.md) を参照。

---

## 2. Mice alternate between discrete strategies during perceptual decision-making

*マウスは知覚的意思決定の最中、離散的な複数の戦略を交互に切り替える*

Ashwood, Z. C. et al. (International Brain Laboratory) — Nature Neuroscience 25, 201–212 (2022). DOI: [10.1038/s41593-021-01007-z](https://doi.org/10.1038/s41593-021-01007-z) — 個別ファイル: [ashwood2022_discrete_strategies.md](ashwood2022_discrete_strategies.md)（原本PDFあり）

![Figure 1](images/ashwood2022_discrete_strategies_fig1.jpg)

*出典: Ashwood et al. (2022) Nature Neuroscience, [10.1038/s41593-021-01007-z](https://doi.org/10.1038/s41593-021-01007-z)（個人の研究メモ用途での引用）*

マウス・ヒトの意思決定課題データが、複数戦略の入れ替わりによって駆動されることをGLM-HMMで示した研究。感覚刺激に強く依存する「Engaged」状態と、頻繁に誤答する「Biased」状態を同定し、げっ歯類実験で観察される「lapse」現象への代替説明を与える。本リポジトリのGLM-HMM実装が直接準拠する原著論文。詳細は [ashwood2022_discrete_strategies.md](ashwood2022_discrete_strategies.md) を参照。

---

## 3. Internal states emerge early during learning of a perceptual decision-making task

*知覚的意思決定課題の学習の初期段階から内部状態が出現する*

Cuturela, L. I. et al. (International Brain Laboratory) — bioRxiv preprint (2024). DOI: [10.1101/2024.11.30.626182](https://doi.org/10.1101/2024.11.30.626182) — 個別ファイル: [cuturela2024_internal_states_early.md](cuturela2024_internal_states_early.md)（原本PDFあり）

![Figure 1](images/cuturela2024_internal_states_early_fig1.jpg)

*出典: Cuturela et al. (2024) bioRxiv preprint, [10.1101/2024.11.30.626182](https://doi.org/10.1101/2024.11.30.626182)（個人の研究メモ用途での引用）*

Ashwood et al. (2022) のGLM-HMMを学習過程へ拡張した「dynamic GLM-HMM」を提案。マウスは学習の非常に早い段階（2セッション目以降）から既にEngaged/Biased状態を切り替えており、成績向上は刺激感度の増加とEngaged状態のoccupancy増加の組み合わせで説明されることを示した。詳細は [cuturela2024_internal_states_early.md](cuturela2024_internal_states_early.md) を参照。

---

## 4. Infinite hidden Markov models can dissect the complexities of learning

*無限隠れマルコフモデルは学習の複雑性を解剖できる*

Bruijns, S. A. et al. (International Brain Laboratory), Dayan, P. — Nature Neuroscience 29, 186–194 (2026年1月号 / 2025年12月30日オンライン公開). DOI: [10.1038/s41593-025-02130-x](https://doi.org/10.1038/s41593-025-02130-x) / [bioRxiv preprint](https://www.biorxiv.org/content/10.1101/2023.12.22.573001)

![Figure 1](images/bruijns2025_infinite_hmm_fig1.jpg)

*出典: Bruijns et al. (2025) Nature Neuroscience, [10.1038/s41593-025-02130-x](https://doi.org/10.1038/s41593-025-02130-x)（個人の研究メモ用途での引用）*

### 要約

課題の随伴性を学習する過程は難しく、個体ごとに独特な様式で学習が進み、探索と適応を繰り返しながら方略を何度も修正する。こうした学習曲線を定量的に特徴づけるには、新しい行動の出現と、既存の行動のゆるやかな変化の両方を捉えられるモデルが必要である。本研究は、潜在状態が行動の特定の構成要素に対応する「動的な無限隠れセミマルコフモデル（infinite HSMM）」を提案する。このモデルは、新しい状態を導入することで新規行動の出現を、既存状態内のダイナミクスによってより穏やかな適応を、それぞれ記述できる。100匹超のマウスがコントラスト検出課題を学習する行動データにモデルを適合させたところ、個体間で大きな差が見られたものの、多くのマウスが課題理解の3段階を経て進行すること、新しい行動はセッション開始時に生じやすいこと、学習初期の応答バイアスはその後のバイアスを予測しないこと、が明らかになった。

---

## 5. Identifying the factors governing internal state switches during nonstationary sensory decision-making

*非定常な感覚性意思決定における内部状態切り替えを支配する要因の同定*

Mohammadi, Z., Ashwood, Z. C., Pillow, J. W. — Nature Communications (2025). DOI: [10.1038/s41467-025-66738-0](https://doi.org/10.1038/s41467-025-66738-0)

![Figure 1](images/mohammadi2025_internal_state_switches_fig1.jpg)

*出典: Mohammadi et al. (2025) Nature Communications, [10.1038/s41467-025-66738-0](https://doi.org/10.1038/s41467-025-66738-0)。CC BY 4.0。*

### 要約

近年の研究により、マウスは知覚意思決定の際に単一で安定した戦略に依存するのではなく、1セッション内で複数の戦略を切り替えることが明らかになっている。しかし、この切り替え行動は非定常な環境下ではまだ特徴づけられておらず、切り替えを支配する要因も不明だった。本研究は、入力依存の遷移を持つ内部状態モデルでこの問いに取り組む。手法は、各状態における刺激依存の選択をモデル化する Bernoulli GLM 群と、状態間の入力依存遷移をモデル化する multinomial GLM を組み合わせた隠れマルコフモデル（HMM）。刺激統計が非定常な二値意思決定課題を行う International Brain Laboratory (IBL) のデータセットに適用した結果、マウスの行動は4状態モデルで精度良く説明できた。このモデルは、左右にわずかなバイアスを持ちながら成績の良い2つの「Engaged」状態と、より大きな左右バイアスを持ち成績の低い2つの「Disengaged」状態から成る。マウスは左バイアスの刺激ブロックでは左バイアス戦略を、右バイアスのブロックでは右バイアス戦略を優先的に用いており、Disengaged 状態でも事前確率の高い側へ選択を偏らせることである程度の成績を保てることが分かった。さらに、過去の選択・刺激がバイアス方向（左/右）の状態間遷移を予測し、過去の報酬が Engaged/Disengaged 間の遷移を予測すること、特に過去の報酬が多いほど Disengaged 状態への遷移が起きやすく、これは満腹（satiety）と関連している可能性があることを示した。

---

## 6. A reservoir of foraging decision variables in the mouse brain

*マウス脳内における採食意思決定変数の貯蔵庫*

Cazettes, F. et al. — Nature Neuroscience 26(5), 840–849 (2023). DOI: [10.1038/s41593-023-01305-8](https://doi.org/10.1038/s41593-023-01305-8)

![Figure 1](images/cazettes2023_foraging_reservoir_fig1.jpg)

*出典: Cazettes et al. (2023) Nature Neuroscience, [10.1038/s41593-023-01305-8](https://doi.org/10.1038/s41593-023-01305-8)（個人の研究メモ用途での引用）*

### 要約

複数の意思決定変数（decision variables, DV）を使い分けられる採食課題中のマウス前頭皮質からニューロン集団活動を記録した研究。行動には複数の戦略とセッション内での戦略切り替えが見られた。光遺伝学的操作により、二次運動皮質（M2）が異なる意思決定変数の使い分けに必要であることが示された。さらに、M2の活動は、現在の行動を最もよく説明する意思決定変数だけでなく、その時点では使われていない別の意思決定変数群も同時に符号化していた——つまり M2 は複数タスクに対応可能な計算の「貯蔵庫（reservoir）」を常時保持している。この神経多重化は、学習や環境変化への適応を有利にすると考察されている。同グループによる [cazettes2025_facial_expressions.md](cazettes2025_facial_expressions.md)（表情側の報告）と対をなす。

---

## 7. Facial expressions in mice reveal latent cognitive variables and their neural correlates

*マウスの表情は潜在的な認知変数とその神経相関を明らかにする*

Cazettes, F. et al. — Nature Neuroscience (2025). DOI: [10.1038/s41593-025-02071-5](https://doi.org/10.1038/s41593-025-02071-5) — 個別ファイル: [cazettes2025_facial_expressions.md](cazettes2025_facial_expressions.md)（原本PDFあり）

![Figure 1](images/cazettes2025_facial_expressions_fig1.jpg)

*出典: Cazettes et al. (2025) Nature Neuroscience, [10.1038/s41593-025-02071-5](https://doi.org/10.1038/s41593-025-02071-5)（bioRxivプレプリント版より取得。個人の研究メモ用途での引用）*

採食課題中のマウスで、現在使用中の意思決定変数（DV）だけでなく、その時点では表出されていない独立したDVまでも表情から復号できることを、LM-HMMによる戦略推定・GLMによる表情復号・二次運動皮質（M2）の光遺伝学的操作で示した研究。本研究のMain RQ「HMM/状態空間モデルと身体データの統合方法」に対する中心的な参考文献。詳細は [cazettes2025_facial_expressions.md](cazettes2025_facial_expressions.md) を参照。

---

## 8. Inferring internal states across mice and monkeys using facial features

*顔特徴を用いたマウスとサルにまたがる内部状態の推定*

Tlaie, A. et al. — Nature Communications 16, 5168 (2025). DOI: [10.1038/s41467-025-60296-1](https://doi.org/10.1038/s41467-025-60296-1) — 個別ファイル: [tlaie2025_facial_features_mice_monkeys.md](tlaie2025_facial_features_mice_monkeys.md)（原本PDFあり）

![Figure 1](images/tlaie2025_facial_features_mice_monkeys_fig1.jpg)

*出典: Tlaie et al. (2025) Nature Communications, [10.1038/s41467-025-60296-1](https://doi.org/10.1038/s41467-025-60296-1)。CC BY 4.0。*

マウス・マカクザルに同一のVR採食課題を課し、顔特徴からMarkov-Switching Linear Regression（MSLR）で内部状態（注意/衝動的/不注意）を推定した研究。表情が種を超えて共通の内部状態を反映することを示す。表情特徴を予測変数、行動指標を出力として状態依存回帰で結びつける点が、本リポジトリのGLM-HMM（表情特徴を選択GLMの入力共変量とする設計）と対照的。詳細は [tlaie2025_facial_features_mice_monkeys.md](tlaie2025_facial_features_mice_monkeys.md) を参照。

---

## 9. Spontaneous behaviour is structured by reinforcement without explicit reward

*自発行動は明示的な報酬なしに強化によって構造化される*

Markowitz, J. E. et al., Linderman, S. W., Datta, S. R. — Nature 614(7946), 108–117 (2023). DOI: [10.1038/s41586-022-05611-2](https://doi.org/10.1038/s41586-022-05611-2)

![Figure 1](images/markowitz2023_spontaneous_behaviour_fig1.jpg)

*出典: Markowitz et al. (2023) Nature, [10.1038/s41586-022-05611-2](https://doi.org/10.1038/s41586-022-05611-2)（個人の研究メモ用途での引用）*

### 要約

課題構造・感覚手がかり・外因性報酬が一切ない自由行動下でも、マウスの自発的な行動（モーションモジュール列）はドパミン変動によって体系的に構造化されることを示した研究。背側線条体（DLS）のドパミン変動は行動モジュールの使用頻度・出現順序を変化させ、後続の行動選択を予測できた。光遺伝学的操作により、ドパミンが特定の行動モジュールを強化し、行動配列の多様性を増加させることを確認。強化学習モデルによる解析から、ドパミン変動が報酬信号の代替として機能し、線条体が行動モジュールを動的に組み立てていることが示唆された。著者に本リポジトリが使う `ssm` ライブラリの開発者 Scott W. Linderman が含まれる。

---

## 10. Hidden Markov models reveal behavioral state dynamics in depth-related locomotion in mice

*隠れマルコフモデルはマウスの奥行き関連移動行動における行動状態動態を明らかにする*

Shuto, H. et al. — PLOS ONE 20(8), e0329367 (2025). DOI: [10.1371/journal.pone.0329367](https://doi.org/10.1371/journal.pone.0329367)

![Figure 1](images/shuto2025_hmm_depth_locomotion_fig1.jpg)

*出典: Shuto et al. (2025) PLOS ONE, [10.1371/journal.pone.0329367](https://doi.org/10.1371/journal.pone.0329367)。CC BY 4.0。*

### 要約

視覚的な奥行き手がかりに対するマウスの応答を調べるため、円形装置と隠れマルコフモデル（HMM）解析を組み合わせた研究。マウスは奥行き手がかりに応じて「静止（resting）」「探索（exploring）」「移動（navigating）」の3つの行動状態間を遷移することが示された。奥行き知覚には最適な空間周波数帯（6〜8 cm相当）があり、単純な回避行動ではなく複数の空間手がかりを統合した処理が行われていること、初期の強い崖回避反応が時間とともにより繊細な行動適応へ変化することが明らかになった。野生型マウスと網膜変性モデル（rd1-2J）の比較により、これらの行動パターンが視覚処理を特異的に反映することが確認された。
