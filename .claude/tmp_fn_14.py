def decode_params(P, pi, W):
    m = dynamic_glmhmm.dynamic_GLMHMM(N, K, D, C)
    with quiet():
        gamma = m.posterior_likelihood_of_each_state(P, pi, W, X, Y, np.ones(N), SESS)
    return gamma, gamma.argmax(axis=1), gamma.max(axis=1)


def degeneracy_one(P, pi, W):
    finite = bool(np.isfinite(P).all() and np.isfinite(pi).all() and np.isfinite(W).all())
    absorb_days = []
    if finite:
        for s in range(len(DAYS)):
            M = P[SESS[s]]
            if np.isnan(M).any():
                absorb_days.append(s)
            elif np.any(np.diag(M) >= ABSORB_DIAG):
                absorb_days.append(s)
    clock_states = []
    same_order = False
    pos_txt = []
    order = None
    if finite and not np.isnan(P).any():
        gamma, z, pmax = decode_params(P, pi, W)
        orders = []
        for k in range(K):
            chunks = []
            for s in range(len(DAYS)):
                sl = slice(SESS[s], SESS[s + 1])
                rel = np.linspace(0, 1, SESS[s + 1] - SESS[s], endpoint=False)
                chunks.append(rel[z[sl] == k])
            v = np.concatenate(chunks) if chunks else np.array([])
            if v.size == 0:
                pos_txt.append('n=0')
                continue
            pos_txt.append(f'{v.mean():.2f}±{v.std():.2f}')
            if v.size >= POS_MIN_N and (v.mean() < POS_MEAN_LO or v.mean() > POS_MEAN_HI) and v.std() < POS_SD_MAX:
                clock_states.append(k)
        for s in range(len(DAYS)):
            zi = z[SESS[s]:SESS[s + 1]]
            n = len(zi)
            cuts = [0, n // 3, 2 * n // 3, n]
            thirds = []
            for a, b in zip(cuts[:-1], cuts[1:]):
                if b > a:
                    thirds.append(int(np.bincount(zi[a:b], minlength=K).argmax()))
            orders.append(tuple(thirds))
        same_order = len(set(orders)) == 1 and len(set(orders[0])) > 1
        order = orders[0] if orders else None
    else:
        z = pmax = None
    ok = finite and not absorb_days and not clock_states and not same_order
    return dict(ok=ok, finite=finite, n_absorb_days=len(absorb_days),
                clock_states=clock_states, same_order=same_order,
                pos=' / '.join(pos_txt), order=order, z=z, pmax=pmax)


NB19.setdefault('degen', {})
rows = []
for i, lab in enumerate(KAPPA_LABELS):
    fold_ok = []
    for f in range(FOLDS):
        ck = f'{f}:{lab}'
        if ck not in NB19['degen']:
            packed = NB19['dyn_folds'][str(f)]
            NB19['degen'][ck] = degeneracy_one(packed['allP'][i], packed['allpi'][i], packed['allW'][i])
            # 系列そのものは大きいのでキャッシュから落とす（再計算は前向き1回）
            NB19['degen'][ck] = {k: v for k, v in NB19['degen'][ck].items() if k not in ('z', 'pmax')}
            save_cache()
        d = NB19['degen'][ck]
        fold_ok.append(d['ok'])
        rows.append({
            'kappa': lab, 'fold': f, 'pass': d['ok'], 'finite': d['finite'],
            'absorb_days': d['n_absorb_days'], 'clock': ','.join(map(str, d['clock_states'])) or '—',
            'same_order': d['same_order'], 'pos': d['pos'],
        })
    print(f'κ={lab:>5}  通過 {sum(fold_ok)}/{FOLDS}')

degen_df = pd.DataFrame(rows)
print(degen_df.drop(columns='pos').to_string(index=False))
print('状態別の day 内位置（fold 0）:')
print(degen_df[degen_df['fold'] == 0][['kappa', 'pos']].to_string(index=False))