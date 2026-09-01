# 設計メモ: 自発押下の状態依存Poisson emission

[requirements_ver5.md](requirements_ver5.md) 7節の「今後の拡張」に対応する設計メモ。未実装・未採用で、Ver.5本体の要件ではない。**Ver.5を実装し、その4.3節の記述量で状態間に自発押下レートの差が見えた場合に、この設計に進む**。

Ver.5は試行系列を音提示試行のみに限り、音提示外の自発押下をモデルから外した（[requirements_ver5.md](requirements_ver5.md) 2.1・2.2節）。`VG1GC-66` 全14日で4386件ある自発押下は、その結果モデルに寄与していない。本メモは、それを**状態依存のレートを持つ点過程**としてemissionに戻す方法を定義する。

## 1. なぜ「入力」ではなく「emission」なのか

自発押下を回帰子（入力）として観測GLMに足す方式も取りうるが、採らない。Ver.5を厳密な特殊ケースとして含む形にしたいため。

emissionとして足すと、Ver.5は「レート $\lambda_k$ が状態に依存しない（$\lambda_k \equiv \lambda$）」場合に一致する。したがって両者のheld-out尤度の比較が、そのまま**「自発押下レートは内部状態に依存するか」という問いの検定**になる。入力として足した場合は両者が入れ子でなくなり、この比較ができない。

## 2. 観測量の定義

Ver.5 4.3節の記述量をそのまま使う。試行 $t$（day $s$、音提示試行）について:

* $\Delta_t^s$: 試行 $t$ の直前ITIの長さ〔秒〕。

  $$\Delta_t^s = \left|\left\{\tau \in \left(t_{\text{end}}^{(t-1)},\, t_{\text{start}}^{(t)}\right)\ :\ \texttt{state\_task}(\tau)=0\right\}\right|$$

* $\tilde\Delta_t^s$: 有効露出時間。押下を保持している間は新たなonsetが起こりえないので、その分を除く。

  $$\tilde\Delta_t^s = \Delta_t^s - \left|\left\{\tau\ \text{同区間}\ :\ \texttt{cleaned\_lever}(\tau)=1\right\}\right|$$

* $n_t^s$: 同区間に含まれる自発押下のonset数。

`state_task == 0` に限ることで報酬フェーズ（`state_task == 2`）を除外する。そこには `VG1GC-66` 全14日で501件のonsetがあり（Success 1293件の約39%に後続の押し直しがある）、報酬摂取に伴う運動であって自発押下ではないため、$n_t$ にも $\tilde\Delta_t$ にも算入しない。

「直前」のITIを採るのは、状態 $z_t$ がcueに先立つ構えとして $n_t$ と $y_t$ の両方を生むという因果の向きに合わせるため。Hulsey et al. 2024が刺激直前の瞳孔・運動指標を使い、Aloor et al. 2026がbaseline窓を取るのと同じ位置づけになる。

## 3. 生成モデル

潜在過程は [requirements_ver5.md](requirements_ver5.md) 5.2節から変更しない。

$$z_1^s \sim U(\{1,\dots,K\}),\qquad p(z_t^s=j \mid z_{t-1}^s=i) = P_{ij}^s$$

emissionを、状態で条件付けた独立性のもとで結合する。

$$p\left(y_t^s,\, n_t^s \;\middle|\; x_t^s,\, \tilde\Delta_t^s,\, z_t^s=k\right) \;=\; \underbrace{p_{\mathrm{cue}}\!\left(y_t^s \mid x_t^s,\, w_k^s\right)}_{\text{Ver.5 5.1節（系統A / B）}} \;\cdot\; \underbrace{p_{\mathrm{ITI}}\!\left(n_t^s \mid \lambda_k^s\, \tilde\Delta_t^s\right)}_{\text{本メモ}}$$

$$p_{\mathrm{ITI}}(n \mid \mu) = \frac{\mu^{n} e^{-\mu}}{n!},\qquad \mu_{t,k}^s = \lambda_k^s\,\tilde\Delta_t^s$$

$\lambda_k^s > 0$ は状態 $k$・day $s$ における自発押下レート〔回/秒〕で、**状態あたりスカラー1個**。cue側のemissionは系統A（Bernoulli）・系統B（3値Categorical）のどちらでもよく、この拡張は両系統に同じ形で乗る。

条件付き独立は仮定であって自明ではない。検証法は7節に置く。

## 4. 対数尤度

$$\ell_{t,k}^{s} \;=\; \log p_{\mathrm{cue}}\!\left(y_t^s \mid x_t^s, w_k^s\right) \;+\; n_t^s \log \lambda_k^s \;-\; \lambda_k^s \tilde\Delta_t^s \;+\; \underbrace{n_t^s \log \tilde\Delta_t^s - \log n_t^s!}_{k\ \text{に依存しない}}$$

最後の2項は状態 $k$ に依存しないため、前向き後向きで状態事後確率を計算する際には約分されて消える（E-stepの実装では省略してよい）。ただし **[requirements_ver5.md](requirements_ver5.md) 5.5節のtest log-likelihood比較では絶対値が必要なので必ず加算する**。ここを落とすと系統間・モデル間の比較が壊れる。

## 5. パラメータ推定

### 5.1 静的な場合（day独立）の閉形式解

E-stepで得た事後確率を $\gamma_{t,k}^s = p(z_t^s=k \mid \text{全観測})$ とすると、ECLLのうち $\lambda_k^s$ を含む項は

$$Q(\lambda_k^s) = \sum_{t=1}^{T_s} \gamma_{t,k}^s\left(n_t^s \log \lambda_k^s - \lambda_k^s \tilde\Delta_t^s\right)$$

$$\frac{\partial Q}{\partial \lambda_k^s} = \frac{\sum_t \gamma_{t,k}^s\, n_t^s}{\lambda_k^s} - \sum_t \gamma_{t,k}^s\, \tilde\Delta_t^s = 0
\quad\Longrightarrow\quad
\hat{\lambda}_k^{s} = \frac{\displaystyle\sum_{t} \gamma_{t,k}^{s}\, n_t^{s}}{\displaystyle\sum_{t} \gamma_{t,k}^{s}\, \tilde\Delta_t^{s}}$$

事後確率で重み付けした総押下数を、事後確率で重み付けした総露出時間で割った値。BFGSを呼ばずM-stepに1行加えるだけで済む。

### 5.2 動的な場合（dayをまたぐ緩やかな変化）

[requirements_ver5.md](requirements_ver5.md) 5.2節のガウスランダムウォークを**対数レート**に置く。

$$\eta_k^s \equiv \log \lambda_k^s, \qquad \eta_k^{s} \sim \mathcal{N}\!\left(\eta_k^{s-1},\ \alpha_\lambda^2\right)$$

対数スケールを採る理由: (1) 正値制約が自動的に満たされる、(2) ガウス事前分布の台と一致する、(3) レートにとって自然な変化は乗法的であり、「2倍になった」が水準に依らず同じ大きさの一歩になる。

day $s$ のM-step目的関数と2階微分:

$$\tilde{Q}(\eta_k^s) = \sum_{t} \gamma_{t,k}^{s}\left(n_t^{s}\,\eta_k^{s} - e^{\eta_k^{s}}\tilde\Delta_t^{s}\right) \;-\; \frac{\left(\eta_k^{s}-\eta_k^{s-1}\right)^2}{2\alpha_\lambda^2} \;-\; \frac{\left(\eta_k^{s+1}-\eta_k^{s}\right)^2}{2\alpha_\lambda^2}$$

$$\frac{\partial^2 \tilde{Q}}{\partial (\eta_k^{s})^{2}} = -\,e^{\eta_k^{s}}\sum_{t}\gamma_{t,k}^{s}\tilde\Delta_t^{s} \;-\; \frac{2}{\alpha_\lambda^{2}} \;<\; 0$$

狭義凹なので最大値は一意で、1次元Newtonが数反復で収束する。さらに $w_k^s$ と $\eta_k^s$ は目的関数に加法的に入り共有パラメータを持たないため、cue側のECLLが $w$ について凹である限り（Ashwood et al. 2022がBernoulli GLMについて示している）、**M-step全体が $(w_k^s, \eta_k^s)$ について同時に凹**であり大域最適が保証される。Ver.5系統Aの性質がそのまま保たれる。

極限では、$\alpha_\lambda \to \infty$ でday独立となり5.1節の閉形式が戻り、$\alpha_\lambda \to 0$ で全day共通の単一 $\lambda_k$（全dayプールの閉形式）になる。中間だけ数値解を要する。$\alpha_\lambda$ は $\alpha$・$\kappa$ と同様に [requirements_ver5.md](requirements_ver5.md) 5.5節のグリッドサーチに1次元加える。

### 5.3 過分散が残る場合の差し替え

Poissonを負の二項分布に置き換え、$\phi$ は全状態共通の大域パラメータ1個とする。

$$p_{\mathrm{ITI}}(n \mid \mu, \phi) = \frac{\Gamma(n+\phi)}{\Gamma(\phi)\, n!}\left(\frac{\phi}{\phi+\mu}\right)^{\phi}\left(\frac{\mu}{\phi+\mu}\right)^{n},\qquad \mathrm{Var}(n) = \mu + \frac{\mu^2}{\phi}$$

$\phi \to \infty$ でPoissonに戻るので、推定された $\phi$ が大きければPoissonで十分という判定にもなる。6節の実測ではday別レートを許せば過分散はほぼ解消するので、既定はPoisson、負の二項は感度チェックの位置づけ。

## 6. Poisson仮定の実測による検証

`VG1GC-66` 全14日・音提示試行2359件で確認した値（2026-09-01 実測）。

**露出と観測数**

| 量 | 平均 | 中央値 | 5%点 | 最大 |
| :--- | ---: | ---: | ---: | ---: |
| 直前ITI長 $\Delta_t$〔秒〕 | 8.90 | 4.97 | 3.30 | 128.8 |
| 自発押下数 $n_t$ | 1.85 | 0 | 0 | 75 |

$n_t = 0$ が1215件（51.5%）。保持による不感時間は全ITI時間の9.3%で、$\tilde\Delta$ への補正は小さいが必要。

**過分散**

| 条件 | Pearson分散比 |
| :--- | ---: |
| 全日プール・単一 $\lambda$ | 1.42 |
| day別 $\lambda$（day5, 7, 8, 10） | 0.90〜1.03 |
| day別 $\lambda$（day11, 12, 14, 15） | 0.51〜0.75 |
| day別 $\lambda$（day1, day9＝押下レート最大の2日） | 1.70, 1.96 |

プール時の1.42はday間のレート差でほぼ説明され、day別に $\lambda$ を持たせると分散比は1前後まで落ちる。後半のdayはむしろ1未満（過小分散）で、これは保持による不応期の残りと解釈でき、負の二項分布では扱えない側の逸脱である。**5.2節の動的 $\lambda_k^s$ を前提とすればPoissonが素直**という判断の根拠になる。

**状態依存性が存在するか（$n_t$ 単独の予備検査）**

$n_t$ に2成分Poisson混合（露出 $\tilde\Delta_t$ をオフセットに置く）を当てると:

$$\lambda_{\text{low}} = 0.169\ \text{回/秒},\qquad \lambda_{\text{high}} = 0.519\ \text{回/秒}\ (3.1\ \text{倍}),\qquad \Delta\mathrm{BIC} = +612$$

単一レートは強く棄却される。この検査はcue応答を無視しているため「同じ潜在状態が両方を生む」ことの証明ではないが、$n_t$ が単一の均質な過程ではなく、状態依存の $\lambda_k$ を置く余地があることの直接の根拠にはなる。

## 7. 得られるもの

状態が**2次元の署名 $(w_k, \lambda_k)$** を持つようになる。

| | cue応答 $w_k$ | 自発レート $\lambda_k$ | 解釈 |
| :--- | :--- | :--- | :--- |
| Engaged | 高 | 低 | 課題に従事し、無駄打ちしない |
| Impulsive / Random | 低〜中 | 高 | 引くがcueと無関係 |
| Quiet disengaged | 低 | 低 | 何もしていない |

Ver.5（および Ver.4）では自発押下がモデルに入らないため、下2行はどちらも「cueに応答しない状態」として1つに畳まれる。$\lambda$ を分離すると区別でき、これは [RQ.md](RQ.md) のRQ3・H3（学習初期のMismatch と 後期のJoint Disengagement の区別）を直接オペレーショナライズする。H3の「脳は従事しているが身体制御が乖離」は「$\lambda$ が高いのにcue応答が低い」として表現される。

**条件付き独立の検証**: 学習後、各状態内で「cue応答の残差」と「$n_t$ のPearson残差 $(n_t - \hat\lambda_k\tilde\Delta_t)/\sqrt{\hat\lambda_k\tilde\Delta_t}$」の相関を取る。ゼロから有意にずれるなら3節の仮定が破れているので、9節の $\lambda$ のGLM化が要る。

**モデル外の外部検証**: [reference/kondo2025_braidynbc_dataset.md](../reference/kondo2025_braidynbc_dataset.md) によれば resting-state セッションでも自発レバー引きが見られ、課題セッションの方が引き頻度は高い。resting-state は**cueが一切無い条件での単一レート測定**なので、そこで推定した $\lambda$ が低従事状態の $\hat\lambda_k$ 近傍に落ちるかを確認できる。GLM-HMMを一切使わない独立チェックであり、RQ1の生物学的妥当性検証（皮質デコード）と同じ役割を行動側で果たす。

## 8. 実装の粒度

[requirements_ver5.md](requirements_ver5.md) 5.4節が「観測モデルは (1) 対数観測尤度、(2) 重みに関するECLLの勾配 の2つだけを提供する差し替え可能コンポーネント」と定めているので、その枠に収まる。

1. **対数観測尤度**: 既存の返り値に $n_t\log\lambda_k - \lambda_k\tilde\Delta_t$ を加算（絶対尤度を返すモードでは $n_t\log\tilde\Delta_t - \log n_t!$ も）。
2. **勾配**: $\dfrac{\partial}{\partial \eta_k^s} = \sum_t \gamma_{t,k}^s\left(n_t^s - e^{\eta_k^s}\tilde\Delta_t^s\right)$（＋5.2節の事前分布項）。

$\alpha_\lambda \to \infty$（day独立）に限れば5.1節の閉形式だけで済み、勾配の実装も不要。

**パラメータ数**: 状態あたりday あたり、cue側 $D=3$ ＋ ITI側1個。$K=3$ で系統Aなら1 dayあたり12個（＋遷移行列6個）。Ver.5系統Aの9個から3個増える。

**注意点**

* **各dayの第1試行**には直前のcue試行が無いので、$\tilde\Delta_1$ はセッション開始時刻から $t_{\text{start}}^{(1)}$ までで取る。$\tilde\Delta_t = 0$ になると $\mu=0$ となり $n_t>0$ の尤度が $-\infty$ に落ちるため、$\tilde\Delta_t = 0$ の行では必ず $n_t = 0$ であることをassertする。
* **$n_t$ は前処理定数に依存する**。`NOISE_REMOVE_LIMIT=0` にすると自発押下は4386→7730件（+76%）に増え（[CLAUDE.md](../CLAUDE.md)）、$\hat\lambda_k$ は概ね比例して動く。検証すべき量は **$\lambda_{\text{high}}/\lambda_{\text{low}}$ の比と状態occupancy** で、これらが定数変更に対して頑健であることを感度解析として報告する。Ver.4方式ではこの感度が系列長を通じて全パラメータに漏れていたので（[requirements_ver5.md](requirements_ver5.md) 2.2節）、影響範囲の限定でもある。
* **報酬フェーズの501件**は2節の定義で $n_t$ から除外される。RQ3の観点では「報酬後にどれだけ押し直すか」も状態の指標になりうるので、第2のレート $\lambda_k^{\text{rew}}$ として同じ形で足す余地がある（パラメータ +1/状態）。本メモでは扱わない。

## 9. さらなる拡張

$\lambda$ 自体をGLMにできる。

$$\log \lambda_{t,k}^{s} = v_k^{s} \cdot u_t^{s}$$

$u_t$ にBias・Reward Historyなどを入れる。Poisson GLMなので $v$ について凹性が保たれ、5.2節の性質は変わらない（1次元Newtonが $\dim(v)$ 次元のBFGSになるだけ）。「報酬後は自発押下が減る」といった仮説を検定したいときに使う。既定は $u_t \equiv 1$（＝3節のスカラー $\lambda_k$）。

## 10. 検討したが採らない代替案: ITIの固定幅ビン化

自発押下をモデルに戻す方法としては、ITIを固定幅 $W$ のビンに離散化して押下の無いビンを $y=0$ の試行として系列に加える案もある。これは本メモの離散近似にあたる。Poissonのもとで1ビンに1回以上の押下がある確率は $p_k = 1 - e^{-\lambda_k W}$ なので、ビン化データの対数尤度は

$$n\log\!\left(1-e^{-\lambda W}\right) - \lambda W\left(N_{\text{bins}} - n\right)$$

となり、$W \to 0$ で $\log(1-e^{-\lambda W}) \to \log(\lambda W)$、$W\,N_{\text{bins}} \to \Delta$ より、$k$ に依らない項を除いて4節のPoisson対数尤度に一致する。

ビン化案の問題は $W$ が恣意的で、しかも $P(y=1 \mid \text{ITIビン})$ を直接決めてしまうことにある。`VG1GC-66` 全14日での実測（2026-09-01）:

| $W$〔秒〕 | ビン数 | $y=1$ 率 |
| ---: | ---: | ---: |
| 0.5 | 41269 | 0.104 |
| 1.0 | 19952 | 0.202 |
| 2.4 | 9214 | 0.453 |
| 5.0 | 2804 | 0.839 |

この $W$ 依存は離散化誤差そのものであり、点過程として扱う本メモの定式化では存在しない。ビン化案は、本メモを実装した結果が $W$ に依らないことを確認する感度チェックとしてのみ意味を持つ。
