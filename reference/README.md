# reference/ — 先行文献

本研究（[docs/RQ.md](../docs/RQ.md)）の背景となる先行文献をまとめたフォルダです。GLM-HMM による内部状態推定、マウスの表情からの潜在変数推定、報酬なし自発行動の構造化など、テーマ別に関連論文を集めています。

一覧は [README.md の「参考文献」節](../README.md#参考文献) にも表示しています。全14本の書誌情報・要約は [all_references.md](all_references.md) に集約し、論文間・本リポジトリとの関連性は [relations.md](relations.md)（フローチャート付き）にまとめています。

## ファイル構成のルール

- **論文PDFを [sources/](sources/) に保存している論文**（`#1` Kondo et al. 2025、`#2` Ashwood et al. 2022、`#3` Cuturela et al. 2024、`#4` Bruijns et al. 2025、`#7` Cazettes et al. 2025、`#8` Tlaie et al. 2025）のみ、個別の `<著者><年>_<slug>.md` ファイルを作成する。内容はタイトル・タイトル和訳・書誌情報・Fig 1・原文PDFに基づく要旨・モデル定義とメソッドの5部構成（「この研究との関連」節は設けない）。
- **要旨・要約の構造化**: 太字ラベル付きの箇条書き（`- **問題提起**`など）でカテゴリ（問題提起・タスク・数理モデル・決定方策など論文固有の要素・主要な結果、など）を分け、各カテゴリの内容はその下にインデントしたサブ箇条書きとして畳み込む（`###`/`####` などの見出しは使わない。見出しにすると、多くのMarkdownレンダラーで見出し要素の上下マージンにより余白が広くなりすぎる）。詳細情報はさらにインデントを深くする（フラットな1階層の箇条書きにしない）。この構造化は個別ファイルの「要旨」と、[all_references.md](all_references.md) の「要約」の両方に適用する。モデル定義はこのリポジトリでモデルを組む際に参照できることを念頭に書く。
- **PDF未保存の論文**（`#5`, `#6`, `#9`, `#10`, `#11`, `#12`, `#13`, `#14`）は個別ファイルを作らず、[all_references.md](all_references.md) の要約のみを情報源とする。PDFを入手した時点で個別ファイル化する。
- **本研究との関連性**（他論文との位置づけ、本リポジトリのRQ・実装との技術的対応）は個別ファイル・all_references.mdのいずれにも書かない。すべて [relations.md](relations.md) に集約する。

この方針は今後の文献サーベイにも適用する（[CLAUDE.md](../CLAUDE.md) 参照）。

## 一覧

| # | ファイル | タイトル | 著者（筆頭） | 誌名・年 |
| :-- | :--- | :--- | :--- | :--- |
| 1 | [kondo2025_braidynbc_dataset.md](kondo2025_braidynbc_dataset.md) | Multimodal dataset linking wide-field calcium imaging to behavior changes in operant lever-pull task in mice | Kondo, M. | Scientific Data, 2025 |
| 2 | [ashwood2022_discrete_strategies.md](ashwood2022_discrete_strategies.md) | Mice alternate between discrete strategies during perceptual decision-making | Ashwood, Z. C. | Nature Neuroscience, 2022 |
| 3 | [cuturela2024_internal_states_early.md](cuturela2024_internal_states_early.md) | Internal states emerge early during learning of a perceptual decision-making task | Cuturela, L. I. (IBL) | bioRxiv, 2024 |
| 4 | [bruijns2025_infinite_hmm.md](bruijns2025_infinite_hmm.md) | Infinite hidden Markov models can dissect the complexities of learning | Bruijns, S. A. (IBL) | Nature Neuroscience, 2025 |
| 5 | [all_references.md](all_references.md#5-identifying-the-factors-governing-internal-state-switches-during-nonstationary-sensory-decision-making) | Identifying the factors governing internal state switches during nonstationary sensory decision-making | Mohammadi, Z. | Nature Communications, 2025 |
| 6 | [all_references.md](all_references.md#6-a-reservoir-of-foraging-decision-variables-in-the-mouse-brain) | A reservoir of foraging decision variables in the mouse brain | Cazettes, F. | Nature Neuroscience, 2023 |
| 7 | [cazettes2025_facial_expressions.md](cazettes2025_facial_expressions.md) | Facial expressions in mice reveal latent cognitive variables and their neural correlates | Cazettes, F. | Nature Neuroscience, 2025 |
| 8 | [tlaie2025_facial_features_mice_monkeys.md](tlaie2025_facial_features_mice_monkeys.md) | Inferring internal states across mice and monkeys using facial features | Tlaie, A. | Nature Communications, 2025 |
| 9 | [all_references.md](all_references.md#9-spontaneous-behaviour-is-structured-by-reinforcement-without-explicit-reward) | Spontaneous behaviour is structured by reinforcement without explicit reward | Markowitz, J. E. | Nature, 2023 |
| 10 | [all_references.md](all_references.md#10-hidden-markov-models-reveal-behavioral-state-dynamics-in-depth-related-locomotion-in-mice) | Hidden Markov models reveal behavioral state dynamics in depth-related locomotion in mice | Shuto, H. | PLOS ONE, 2025 |
| 11 | [all_references.md](all_references.md#11-how-learned-expectations-shape-brain-wide-responses) | How learned expectations shape brain-wide responses | Liu, A. | bioRxiv, 2025 |
| 12 | [all_references.md](all_references.md#12-exploiting-correlations-across-trials-and-behavioral-sessions-to-improve-neural-decoding) | Exploiting correlations across trials and behavioral sessions to improve neural decoding | Zhang, Y. | Neuron, 2026 |
| 13 | [all_references.md](all_references.md#13-decision-making-dynamics-are-predicted-by-arousal-and-uninstructed-movements) | Decision-making dynamics are predicted by arousal and uninstructed movements | Hulsey, D. | Cell Reports, 2024 |
| 14 | [all_references.md](all_references.md#14-behavioural-and-neural-mechanisms-for-stochastic-choices-in-mixed-strategy-games) | Behavioural and neural mechanisms for stochastic choices in mixed-strategy games | Aloor, J. | bioRxiv, 2026 |

テーマ別のつながり・本リポジトリとの技術的対応は [relations.md](relations.md) を参照してください。
