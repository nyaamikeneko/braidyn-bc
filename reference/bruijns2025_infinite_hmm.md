# Infinite hidden Markov models can dissect the complexities of learning

- **著者**: Sebastian A. Bruijns, International Brain Laboratory (Kcénia Bougrova, Inês C. Laranjeira, Petrina Y. P. Lau, Guido T. Meijer, Nathaniel J. Miska, Jean-Paul Noel, Alejandro Pan-Vazquez, Noam Roth, Karolina Z. Socha, Anne E. Urai ほか), Peter Dayan
- **誌名**: Nature Neuroscience, 29, 186–194 (2026年1月号 / 2025年12月30日オンライン公開)
- **DOI**: [10.1038/s41593-025-02130-x](https://doi.org/10.1038/s41593-025-02130-x)
- **リンク**: [Nature](https://www.nature.com/articles/s41593-025-02130-x) / [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12779568/) / [bioRxiv preprint](https://www.biorxiv.org/content/10.1101/2023.12.22.573001)

## Figure 1

![Figure 1](images/bruijns2025_infinite_hmm_fig1.jpg)

*出典: Bruijns et al. (2025) Nature Neuroscience, [10.1038/s41593-025-02130-x](https://doi.org/10.1038/s41593-025-02130-x)（個人の研究メモ用途での引用）*

## 要旨（Semantic Scholar 経由で取得した原文の要約訳）

課題の随伴性を学習する過程は難しく、個体ごとに独特な様式で学習が進み、探索と適応を繰り返しながら方略を何度も修正する。こうした学習曲線を定量的に特徴づけるには、新しい行動の出現と、既存の行動のゆるやかな変化の両方を捉えられるモデルが必要である。本研究は、潜在状態が行動の特定の構成要素に対応する「動的な無限隠れセミマルコフモデル（infinite HSMM）」を提案する。このモデルは、新しい状態を導入することで新規行動の出現を、既存状態内のダイナミクスによってより穏やかな適応を、それぞれ記述できる。100匹超のマウスがコントラスト検出課題を学習する行動データにモデルを適合させたところ、個体間で大きな差が見られたものの、多くのマウスが課題理解の3段階を経て進行すること、新しい行動はセッション開始時に生じやすいこと、学習初期の応答バイアスはその後のバイアスを予測しないこと、が明らかになった。著者らは、学習中の行動を包括的に捉えるための新しいツールを提供するとしている。

## この研究との関連

- 本リポジトリの GLM-HMM は状態数 K を固定（Ver.4 では K=3）して学習するが、この論文は状態数を固定しない無限HMMアプローチを取る。状態数の妥当性を検討する際の比較対象・拡張案として参考になる。
- 「新しい行動はセッション開始時に生じやすい」という知見は、Ver.4（試行単位、`notebooks/14_glmhmm_ver4_trials.ipynb`）で用いる Action History / Reward History のようなセッション内の履歴依存変数の設計に示唆を与える。
- International Brain Laboratory (IBL) による一連の GLM-HMM 関連研究（[ashwood2022_discrete_strategies.md](ashwood2022_discrete_strategies.md)、[cuturela2024_internal_states_early.md](cuturela2024_internal_states_early.md) と同系統）の最新の発展系。
