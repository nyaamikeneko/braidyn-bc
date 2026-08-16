# reference/ — 先行文献

本研究（[docs/RQ.md](../docs/RQ.md)）の背景となる先行文献をまとめたフォルダです。GLM-HMM による内部状態推定、マウスの表情からの潜在変数推定、報酬なし自発行動の構造化など、テーマ別に関連論文を集めています。

一覧は [README.md の「参考文献」節](../README.md#参考文献) にも表示しています。各ファイルは書誌情報・要旨（日本語要約）・本研究との関連メモの3部構成です。全10本を1ファイルにまとめた [all_references.md](all_references.md) もあります。

`#1` の Kondo et al. 2025（本リポジトリが解析対象とするデータセットの記述論文）のみ、全文PDF・Supplementary Information の原本を [sources/](sources/) に保存しています。

## 一覧

| # | ファイル | タイトル | 著者（筆頭） | 誌名・年 |
| :-- | :--- | :--- | :--- | :--- |
| 1 | [kondo2025_braidynbc_dataset.md](kondo2025_braidynbc_dataset.md) | Multimodal dataset linking wide-field calcium imaging to behavior changes in operant lever-pull task in mice | Kondo, M. | Scientific Data, 2025 |
| 2 | [ashwood2022_discrete_strategies.md](ashwood2022_discrete_strategies.md) | Mice alternate between discrete strategies during perceptual decision-making | Ashwood, Z. C. | Nature Neuroscience, 2022 |
| 3 | [cuturela2024_internal_states_early.md](cuturela2024_internal_states_early.md) | Internal states emerge early during learning of a perceptual decision-making task | Cuturela, L. I. (IBL) | bioRxiv, 2024 |
| 4 | [bruijns2025_infinite_hmm.md](bruijns2025_infinite_hmm.md) | Infinite hidden Markov models can dissect the complexities of learning | Bruijns, S. A. (IBL) | Nature Neuroscience, 2025 |
| 5 | [mohammadi2025_internal_state_switches.md](mohammadi2025_internal_state_switches.md) | Identifying the factors governing internal state switches during nonstationary sensory decision-making | Mohammadi, Z. | Nature Communications, 2025 |
| 6 | [cazettes2023_foraging_reservoir.md](cazettes2023_foraging_reservoir.md) | A reservoir of foraging decision variables in the mouse brain | Cazettes, F. | Nature Neuroscience, 2023 |
| 7 | [cazettes2025_facial_expressions.md](cazettes2025_facial_expressions.md) | Facial expressions in mice reveal latent cognitive variables and their neural correlates | Cazettes, F. | Nature Neuroscience, 2025 |
| 8 | [tlaie2025_facial_features_mice_monkeys.md](tlaie2025_facial_features_mice_monkeys.md) | Inferring internal states across mice and monkeys using facial features | Tlaie, A. | Nature Communications, 2025 |
| 9 | [markowitz2023_spontaneous_behaviour.md](markowitz2023_spontaneous_behaviour.md) | Spontaneous behaviour is structured by reinforcement without explicit reward | Markowitz, J. E. | Nature, 2023 |
| 10 | [shuto2025_hmm_depth_locomotion.md](shuto2025_hmm_depth_locomotion.md) | Hidden Markov models reveal behavioral state dynamics in depth-related locomotion in mice | Shuto, H. | PLOS ONE, 2025 |

## テーマ別のつながり

```
データ出所
 └─ #1 Kondo et al. 2025 ...... 本リポジトリが使う NWB/CSV データセットの記述論文（レバー引き課題、25匹、Day1-15）

GLM-HMM による内部状態推定（本研究の手法的支柱）
 ├─ #2 Ashwood et al. 2022 .... Bernoulli GLM-HMM で Engaged/Biased 状態を発見した原著（README・要件定義が準拠）
 ├─ #3 Cuturela et al. 2024 ... 内部状態が学習のごく初期から出現することを示す
 ├─ #4 Bruijns et al. 2025 .... 状態数を固定しない無限HMMで学習曲線の段階を記述
 └─ #5 Mohammadi et al. 2025 .. 状態遷移そのものを入力依存にし、遷移を駆動する要因（報酬・刺激）を分離

内部状態の生物学的実体（RQ1: Biological Validity 関連）
 ├─ #6 Cazettes et al. 2023 ... 前頭皮質(M2)が複数の意思決定変数を同時に保持する「貯蔵庫」であることを示す
 ├─ #7 Cazettes et al. 2025 ... 表情が、今使っていない潜在的な意思決定変数まで同時に符号化する
 ├─ #8 Tlaie et al. 2025 ...... 表情特徴から内部状態を推定するモデルがマウス・サルで共通に機能する
 └─ #10 Shuto et al. 2025 ..... HMMで移動行動から resting/exploring/navigating の状態遷移を抽出（応用例）

脳-身体カップリングの神経基盤（RQ2: Learning Dynamics 関連）
 └─ #9 Markowitz et al. 2023 .. 明示的報酬がなくても線条体ドパミンが自発行動を強化学習的に構造化する
```
