# Multimodal dataset linking wide-field calcium imaging to behavior changes in operant lever-pull task in mice

- **著者**: Masashi Kondo, Keisuke Sehara, Rie Harukuni, Ryo Aoki, Shoya Sugimoto, Yasuhiro R. Tanaka, Masanori Matsuzaki, Ken Nakae
- **誌名**: Scientific Data, Volume 12, Article 1264 (2025)
- **DOI**: [10.1038/s41597-025-05482-y](https://doi.org/10.1038/s41597-025-05482-y)
- **リンク**: [Nature](https://www.nature.com/articles/s41597-025-05482-y) / [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12307678/) / [bioRxiv preprint](https://www.biorxiv.org/content/10.1101/2025.02.03.631599)

## Figure 1

![Figure 1](images/kondo2025_braidynbc_dataset_fig1.jpg)

*出典: Kondo et al. (2025) Scientific Data, [10.1038/s41597-025-05482-y](https://doi.org/10.1038/s41597-025-05482-y)（個人の研究メモ用途での引用）*

## 要旨（要約）

頭部固定したマウスがレバーを引いて水報酬を得るオペラント課題を、2週間・15セッションにわたって訓練しながら、広視野カルシウムイメージングによる大脳皮質全体の神経活動と、身体・表情・眼球運動の高速ビデオグラフィ、環境パラメータを同時に記録したマルチモーダルデータセット。NWB (Neurodata Without Borders) 形式に整形されており、FAIR原則に準拠する。運動学習に伴う神経メカニズム、セッション内の急速な学習効果、長期的な行動適応、神経回路ダイナミクスを調べるためのリソースとして提供されている。

## この研究との関連

**本リポジトリが解析対象とする NWB / CSV データそのものの記述論文である可能性が高い。**

- 課題設計（頭部固定・レバー引き・水報酬）、対象マウス数（25匹）が [docs/data.md](../docs/data.md) の「CSV は25匹中24匹に `trials_L1L2.csv` がある」という記述と一致する。
- セッション構成（2週間・15セッション）は、本リポジトリの `Day 1–15` という課題日レンジと一致する。
- `state_lever` / `state_task` / `pull_onset` などの CSV 列や、NWB 内の imaging・trials・表情データは、この論文のデータ構造を踏まえて設計されていると考えられる。
- データの取得元・前処理仕様（`merge_asof` での CSV/NWB 統合など、[docs/requirements_glmhmm.md](../docs/requirements_glmhmm.md) 3.2節）を理解する上で、この論文の Methods を一次情報として参照する価値が高い。
