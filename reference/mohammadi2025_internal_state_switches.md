# Identifying the factors governing internal state switches during nonstationary sensory decision-making

- **著者**: Zeinab Mohammadi, Zoe C. Ashwood, Jonathan W. Pillow
- **誌名**: Nature Communications (2025)
- **DOI**: [10.1038/s41467-025-66738-0](https://doi.org/10.1038/s41467-025-66738-0)
- **リンク**: [Nature](https://www.nature.com/articles/s41467-025-66738-0) / [PubMed](https://pubmed.ncbi.nlm.nih.gov/41310378/) / [bioRxiv preprint](https://www.biorxiv.org/content/10.1101/2024.02.02.578482) / [Pillow Lab abstract](https://pillowlab.princeton.edu/pubs/abs_Mohammadi_NatComs2025.html)

## 要旨（Semantic Scholar 経由で取得した原文の要約訳）

近年の研究により、マウスは知覚意思決定の際に単一で安定した戦略に依存するのではなく、1セッション内で複数の戦略を切り替えることが明らかになっている。しかし、この切り替え行動は非定常な環境下ではまだ特徴づけられておらず、切り替えを支配する要因も不明だった。本研究は、入力依存の遷移を持つ内部状態モデルでこの問いに取り組む。手法は、各状態における刺激依存の選択をモデル化する Bernoulli GLM 群と、状態間の入力依存遷移をモデル化する multinomial GLM を組み合わせた隠れマルコフモデル（HMM）。刺激統計が非定常な二値意思決定課題を行う International Brain Laboratory (IBL) のデータセットに適用した結果、マウスの行動は4状態モデルで精度良く説明できた。このモデルは、左右にわずかなバイアスを持ちながら成績の良い2つの「Engaged」状態と、より大きな左右バイアスを持ち成績の低い2つの「Disengaged」状態から成る。マウスは左バイアスの刺激ブロックでは左バイアス戦略を、右バイアスのブロックでは右バイアス戦略を優先的に用いており、Disengaged 状態でも事前確率の高い側へ選択を偏らせることである程度の成績を保てることが分かった。さらに、過去の選択・刺激がバイアス方向（左/右）の状態間遷移を予測し、過去の報酬が Engaged/Disengaged 間の遷移を予測すること、特に過去の報酬が多いほど Disengaged 状態への遷移が起きやすく、これは満腹（satiety）と関連している可能性があることを示した。

## この研究との関連

- Ashwood et al. (2022) の GLM-HMM（[ashwood2022_discrete_strategies.md](ashwood2022_discrete_strategies.md)）を「状態遷移も入力依存にする」方向へ拡張した直接の後継研究。本リポジトリの Ver.3/Ver.4 入力変数（Bias / Stimulus / Action History / Reward History）のうち、Reward History が従事度（Engaged/Random）の切り替えを駆動するという知見は、この論文の「過去の報酬が Engagement の切り替えを駆動する」という結果と整合的。
- 本研究の RQ3（[docs/RQ.md](../docs/RQ.md)）「ミス試行の質的分解」において、状態遷移の駆動要因（刺激 vs 報酬）を切り分ける視点は、この論文の分析枠組みと同型。
