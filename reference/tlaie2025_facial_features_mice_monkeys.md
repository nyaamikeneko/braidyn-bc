# Inferring internal states across mice and monkeys using facial features

- **著者**: Alejandro Tlaie, Muad Y. Abd El Hay, Berkutay Mert, Robert Taylor, Pierre-Antoine Ferracci, Katharine Shapcott, Mina Glukhova, Jonathan W. Pillow, Martha N. Havenith, Marieke L. Schölvinck
- **誌名**: Nature Communications, 16, Article 5168 (2025)
- **DOI**: [10.1038/s41467-025-60296-1](https://doi.org/10.1038/s41467-025-60296-1)
- **リンク**: [Nature](https://www.nature.com/articles/s41467-025-60296-1) / [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12137566/) / [PubMed](https://pubmed.ncbi.nlm.nih.gov/40467558/)

## 要旨（要約）

内部認知状態が種を超えて共通性を持つかを検証するため、マウスとマカクザルに同一の自然主義的な視覚採食課題をバーチャルリアリティ環境で行わせた研究。顔の映像特徴（サルは18特徴、マウスは9特徴）を用いて Markov-Switching Linear Regression（MSLR）モデルを学習し、動物がいつ刺激に反応するかを予測する内部状態を推定した。反応時間のみで学習したにもかかわらず、モデルは課題成績も予測できた。推定された内部状態は、成績との関係性がマウスとサルで共通しており（速い反応・高成績の「注意」状態、速いが不正解が多い「衝動的」状態、遅く成績も悪い「不注意」状態）、対応する表情パターンにも部分的な重なりが見られた。表情が種を超えて共通の内部状態を反映することを示唆する。

## この研究との関連

- 表情特徴（9次元）から内部状態を推定する枠組みは、本リポジトリの Ver.4 拡張（顔特徴9次元を含めた13次元入力、`notebooks/14_glmhmm_ver4_trials.ipynb`）と設計思想が近い。マウスで用いる顔特徴数（9）が本リポジトリの顔特徴次元と一致する点は、特徴選定の参考になる可能性がある。
- 「注意／衝動的／不注意」という3状態の解釈は、本研究のミス試行分解（RQ3, H3: Mismatch vs Joint Disengagement）における状態のラベリングと比較可能な参照枠を与える。
- HMM 系列モデル（MSLR）で表情から内部状態を推定するアプローチ自体が、本研究の Phase 2（Multimodal Decoding, [docs/RQ.md](../docs/RQ.md)）の直接的な方法論的参考文献となる。
