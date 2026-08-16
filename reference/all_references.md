# 先行文献まとめ

[reference/README.md](README.md) の一覧にある10本の先行文献を、1ファイルに集約したものです。各論文の個別ファイルは `reference/<ファイル名>.md` を参照してください。

---

## 1. Multimodal dataset linking wide-field calcium imaging to behavior changes in operant lever-pull task in mice

- **タイトル訳**: マウスのオペラント・レバー引き課題における広視野カルシウムイメージングと行動変化を結びつけたマルチモーダルデータセット
- **著者**: Masashi Kondo, Keisuke Sehara, Rie Harukuni, Ryo Aoki, Shoya Sugimoto, Yasuhiro R. Tanaka, Masanori Matsuzaki, Ken Nakae
- **雑誌**: Scientific Data, Volume 12, Article 1264 (2025)
- **DOI**: [10.1038/s41597-025-05482-y](https://doi.org/10.1038/s41597-025-05482-y)
- **個別ファイル**: [kondo2025_braidynbc_dataset.md](kondo2025_braidynbc_dataset.md)

### 要約

頭部固定したマウスがレバーを引いて水報酬を得るオペラント課題を、2週間・15セッションにわたって訓練しながら、広視野カルシウムイメージングによる大脳皮質全体の神経活動と、身体・表情・眼球運動の高速ビデオグラフィ、環境パラメータを同時に記録したマルチモーダルデータセット。NWB (Neurodata Without Borders) 形式に整形されており、FAIR原則に準拠する。運動学習に伴う神経メカニズム、セッション内の急速な学習効果、長期的な行動適応、神経回路ダイナミクスを調べるためのリソースとして提供されている。本リポジトリが解析対象とする NWB / CSV データそのものの記述論文である可能性が高い。

---

## 2. Mice alternate between discrete strategies during perceptual decision-making

- **タイトル訳**: マウスは知覚的意思決定の最中、離散的な複数の戦略を交互に切り替える
- **著者**: Zoe C. Ashwood, Nicholas A. Roy, Iris R. Stone, International Brain Laboratory, Anne E. Urai, Anne K. Churchland, Alexandre Pouget, Jonathan W. Pillow
- **雑誌**: Nature Neuroscience, 25, 201–212 (2022)
- **DOI**: [10.1038/s41593-021-01007-z](https://doi.org/10.1038/s41593-021-01007-z)
- **個別ファイル**: [ashwood2022_discrete_strategies.md](ashwood2022_discrete_strategies.md)

### 要約

知覚意思決定の古典的モデルは、被験者が単一で一貫した戦略を使う、あるいは戦略が時間とともにゆっくり進化すると仮定してきたが、本研究はこの通念が誤りであることを示す。マウスとヒトの意思決定課題データを解析した結果、選択行動が複数の戦略の入れ替わり（interleaved）によって駆動されていることが分かった。これらの戦略は HMM の状態として特徴づけられ、数十〜数百試行持続したのち切り替わり、しばしば1セッション内で複数回切り替わる。マウス間で一貫して同定された戦略は、感覚刺激に強く依存する単一の「Engaged（従事）」状態と、頻繁に誤答する複数の「Biased（バイアス）」状態だった。この結果は、げっ歯類実験でしばしば観察される「lapse」現象への強力な代替説明を与える。手法は、状態ごとに異なるベルヌーイ GLM をパラメータとして持つ隠れマルコフモデル（HMM; いわゆる GLM-HMM）で、本リポジトリの GLM-HMM 実装が直接準拠する原著論文。

---

## 3. Internal states emerge early during learning of a perceptual decision-making task

- **タイトル訳**: 知覚的意思決定課題の学習の初期段階から内部状態が出現する
- **著者**: Lenca I. Cuturela, International Brain Laboratory, Jonathan W. Pillow ほか
- **雑誌**: bioRxiv preprint（2024年12月投稿）
- **DOI**: [10.1101/2024.11.30.626182](https://doi.org/10.1101/2024.11.30.626182)
- **個別ファイル**: [cuturela2024_internal_states_early.md](cuturela2024_internal_states_early.md)

### 要約

近年の研究により、動物は知覚意思決定課題の遂行中、複数の内部状態（戦略）の間を頻繁に切り替えることが示されているが、これらの状態が学習のいつ、どのように出現するかは未解明だった。本研究は動的な潜在状態モデルを、マウスが視覚性意思決定課題を学習する過程の訓練データに適用した。結果、マウスは学習の非常に早い段階から既に明確な「Engaged」状態と「Biased」状態を示し、2セッション目以降で複数の状態が確認された。さらにモデルは、訓練を通じた成績の緩やかな向上が (1) 全ての状態で刺激への感度が増加すること、(2) 正答率の高い Engaged 状態で過ごす時間の割合がバイアス状態に対して相対的に増加すること、の2要因の組み合わせから生じることを明らかにした。

---

## 4. Infinite hidden Markov models can dissect the complexities of learning

- **タイトル訳**: 無限隠れマルコフモデルは学習の複雑性を解剖できる
- **著者**: Sebastian A. Bruijns, International Brain Laboratory (Kcénia Bougrova, Inês C. Laranjeira, Petrina Y. P. Lau, Guido T. Meijer, Nathaniel J. Miska, Jean-Paul Noel, Alejandro Pan-Vazquez, Noam Roth, Karolina Z. Socha, Anne E. Urai ほか), Peter Dayan
- **雑誌**: Nature Neuroscience, 29, 186–194 (2026年1月号 / 2025年12月30日オンライン公開)
- **DOI**: [10.1038/s41593-025-02130-x](https://doi.org/10.1038/s41593-025-02130-x)
- **個別ファイル**: [bruijns2025_infinite_hmm.md](bruijns2025_infinite_hmm.md)

### 要約

課題の随伴性を学習する過程は難しく、個体ごとに独特な様式で学習が進み、探索と適応を繰り返しながら方略を何度も修正する。こうした学習曲線を定量的に特徴づけるには、新しい行動の出現と、既存の行動のゆるやかな変化の両方を捉えられるモデルが必要である。本研究は、潜在状態が行動の特定の構成要素に対応する「動的な無限隠れセミマルコフモデル（infinite HSMM）」を提案する。このモデルは、新しい状態を導入することで新規行動の出現を、既存状態内のダイナミクスによってより穏やかな適応を、それぞれ記述できる。100匹超のマウスがコントラスト検出課題を学習する行動データに適用したところ、個体間で大きな差が見られたものの、多くのマウスが課題理解の3段階を経て進行すること、新しい行動はセッション開始時に生じやすいこと、学習初期の応答バイアスはその後のバイアスを予測しないこと、が明らかになった。

---

## 5. Identifying the factors governing internal state switches during nonstationary sensory decision-making

- **タイトル訳**: 非定常な感覚性意思決定における内部状態切り替えを支配する要因の同定
- **著者**: Zeinab Mohammadi, Zoe C. Ashwood, Jonathan W. Pillow
- **雑誌**: Nature Communications (2025)
- **DOI**: [10.1038/s41467-025-66738-0](https://doi.org/10.1038/s41467-025-66738-0)
- **個別ファイル**: [mohammadi2025_internal_state_switches.md](mohammadi2025_internal_state_switches.md)

### 要約

マウスは知覚意思決定の際に単一で安定した戦略に依存するのではなく、1セッション内で複数の戦略を切り替えることが近年示されているが、この切り替え行動は非定常な環境下ではまだ特徴づけられておらず、切り替えを支配する要因も不明だった。本研究は、入力依存の遷移を持つ内部状態モデル（状態ごとの選択を表す Bernoulli GLM 群と、状態間の入力依存遷移を表す multinomial GLM を組み合わせた HMM）でこの問いに取り組む。刺激統計が非定常な IBL のデータセットに適用した結果、マウスの行動は4状態モデル（左右にわずかなバイアスを持つ2つの Engaged 状態と、より大きなバイアスを持つ2つの Disengaged 状態）で精度良く説明できた。過去の選択・刺激がバイアス方向の状態間遷移を、過去の報酬が Engaged/Disengaged 間の遷移を、それぞれ予測すること、特に過去の報酬が多いほど Disengaged 状態への遷移が起きやすく満腹（satiety）と関連する可能性があることを示した。

---

## 6. A reservoir of foraging decision variables in the mouse brain

- **タイトル訳**: マウス脳内における採食意思決定変数の貯蔵庫
- **著者**: Fanny Cazettes, Luca Mazzucato, Masayoshi Murakami, Joao P. Morais, Elisabete Augusto, Alfonso Renart, Zachary F. Mainen
- **雑誌**: Nature Neuroscience, 26(5), 840–849 (2023)
- **DOI**: [10.1038/s41593-023-01305-8](https://doi.org/10.1038/s41593-023-01305-8)
- **個別ファイル**: [cazettes2023_foraging_reservoir.md](cazettes2023_foraging_reservoir.md)

### 要約

複数の意思決定変数（decision variables, DV）を使い分けられる採食課題中のマウス前頭皮質からニューロン集団活動を記録した研究。行動には複数の戦略とセッション内での戦略切り替えが見られた。光遺伝学的操作により、二次運動皮質（M2）が異なる意思決定変数の使い分けに必要であることが示された。さらに、M2の活動は、現在の行動を最もよく説明する意思決定変数だけでなく、その時点では使われていない別の意思決定変数群も同時に符号化していた——つまり M2 は複数タスクに対応可能な計算の「貯蔵庫（reservoir）」を常時保持している。この神経多重化は、学習や環境変化への適応を有利にすると考察されている。

---

## 7. Facial expressions in mice reveal latent cognitive variables and their neural correlates

- **タイトル訳**: マウスの表情は潜在的な認知変数とその神経相関を明らかにする
- **著者**: Fanny Cazettes, Dhruba Banerjee, Elisabete Augusto ほか
- **雑誌**: Nature Neuroscience (2025)
- **DOI**: [10.1038/s41593-025-02071-5](https://doi.org/10.1038/s41593-025-02071-5)
- **個別ファイル**: [cazettes2025_facial_expressions.md](cazettes2025_facial_expressions.md)

### 要約

脳活動は適応的行動を制御する一方、意図しない付随的な（incidental）身体運動も引き起こす。こうした付随運動は内部の認知変数を読み出す手がかりになり得るが、それが単に身体の生体力学的な結合によって課題関連反応と連動しているだけの可能性を排除する必要がある。本研究は、複数の意思決定変数が同時に符号化されながらもある時点では1つしか使われないマウスの採食課題でこの課題に取り組んだ。顔の特徴的なパターンは、現在使用中の意思決定変数だけでなく、その時点では表出されていない独立した意思決定変数までも同時に符号化しており、これらの表情特徴の一部は二次運動皮質（M2）の神経活動に由来することを示した。顔面運動は課題要求に直接関連する範囲を超えた進行中の計算を反映しており、非侵襲的モニタリングによって潜在的な認知状態を明らかにできる可能性を実証している。本研究の Main RQ「皮質活動（中枢）と表情（末梢）の結合」を直接支持する、最も重要な先行研究の一つ。

---

## 8. Inferring internal states across mice and monkeys using facial features

- **タイトル訳**: 顔特徴を用いたマウスとサルにまたがる内部状態の推定
- **著者**: Alejandro Tlaie, Muad Y. Abd El Hay, Berkutay Mert, Robert Taylor, Pierre-Antoine Ferracci, Katharine Shapcott, Mina Glukhova, Jonathan W. Pillow, Martha N. Havenith, Marieke L. Schölvinck
- **雑誌**: Nature Communications, 16, Article 5168 (2025)
- **DOI**: [10.1038/s41467-025-60296-1](https://doi.org/10.1038/s41467-025-60296-1)
- **個別ファイル**: [tlaie2025_facial_features_mice_monkeys.md](tlaie2025_facial_features_mice_monkeys.md)

### 要約

内部認知状態が種を超えて共通性を持つかを検証するため、マウスとマカクザルに同一の自然主義的な視覚採食課題をバーチャルリアリティ環境で行わせた研究。顔の映像特徴（サルは18特徴、マウスは9特徴）を用いて Markov-Switching Linear Regression（MSLR）モデルを学習し、動物がいつ刺激に反応するかを予測する内部状態を推定した。反応時間のみで学習したにもかかわらず、モデルは課題成績も予測できた。推定された内部状態は、成績との関係性がマウスとサルで共通しており（速い反応・高成績の「注意」状態、速いが不正解が多い「衝動的」状態、遅く成績も悪い「不注意」状態）、対応する表情パターンにも部分的な重なりが見られた。表情が種を超えて共通の内部状態を反映することを示唆する。

---

## 9. Spontaneous behaviour is structured by reinforcement without explicit reward

- **タイトル訳**: 自発行動は明示的な報酬なしに強化によって構造化される
- **著者**: Jeffrey E. Markowitz, Winthrop F. Gillis, Maya Jay, Jeffrey Wood, Ryley W. Harris, Robert Cieszkowski, Rebecca Scott, David Brann, Dorothy Koveal, Tomasz Kula, Caleb Weinreb, Mohammed Abdal Monium Osman, Sandra Romero Pinto, Naoshige Uchida, Scott W. Linderman, Bernardo L. Sabatini, Sandeep Robert Datta
- **雑誌**: Nature, 614(7946), 108–117 (2023年1月18日)
- **DOI**: [10.1038/s41586-022-05611-2](https://doi.org/10.1038/s41586-022-05611-2)
- **個別ファイル**: [markowitz2023_spontaneous_behaviour.md](markowitz2023_spontaneous_behaviour.md)

### 要約

課題構造・感覚手がかり・外因性報酬が一切ない自由行動下でも、マウスの自発的な行動（モーションモジュール列）はドパミン変動によって体系的に構造化されることを示した研究。背側線条体（DLS）のドパミン変動は行動モジュールの使用頻度・出現順序を変化させ、後続の行動選択を予測できた。光遺伝学的操作により、ドパミンが特定の行動モジュールを強化し、行動配列の多様性を増加させることを確認。強化学習モデルによる解析から、ドパミン変動が報酬信号の代替として機能し、線条体が行動モジュールを動的に組み立てていることが示唆された。著者に本リポジトリが使う `ssm` ライブラリの開発者 Scott W. Linderman が含まれる。

---

## 10. Hidden Markov models reveal behavioral state dynamics in depth-related locomotion in mice

- **タイトル訳**: 隠れマルコフモデルはマウスの奥行き関連移動行動における行動状態動態を明らかにする
- **著者**: Hironobu Shuto, Toshiki Maeda, Chieko Koike, Masayo Takahashi, Michiko Mandai, Take Matsuyama
- **雑誌**: PLOS ONE, 20(8), e0329367 (2025)
- **DOI**: [10.1371/journal.pone.0329367](https://doi.org/10.1371/journal.pone.0329367)
- **個別ファイル**: [shuto2025_hmm_depth_locomotion.md](shuto2025_hmm_depth_locomotion.md)

### 要約

視覚的な奥行き手がかりに対するマウスの応答を調べるため、円形装置と隠れマルコフモデル（HMM）解析を組み合わせた研究。マウスは奥行き手がかりに応じて「静止（resting）」「探索（exploring）」「移動（navigating）」の3つの行動状態間を遷移することが示された。奥行き知覚には最適な空間周波数帯（6〜8 cm相当）があり、単純な回避行動ではなく複数の空間手がかりを統合した処理が行われていること、初期の強い崖回避反応が時間とともにより繊細な行動適応へ変化することが明らかになった。野生型マウスと網膜変性モデル（rd1-2J）の比較により、これらの行動パターンが視覚処理を特異的に反映することが確認された。
