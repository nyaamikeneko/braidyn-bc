def state_summary(P, pi, W, label):
    gamma, z, pmax = decode_params(P, pi, W)
    occ = np.zeros((len(DAYS), K))
    switches, runs = [], []
    pos_by_state = [[] for _ in range(K)]
    for i in range(len(DAYS)):
        sl = slice(SESS[i], SESS[i + 1])
        zi = z[sl]
        for k in range(K):
            occ[i, k] = (zi == k).mean()
        switches.append(int((np.diff(zi) != 0).sum()))
        cut = np.flatnonzero(np.diff(zi) != 0) + 1
        runs += [len(s) for s in np.split(zi, cut)]
        rel = np.linspace(0, 1, len(zi), endpoint=False)
        for k in range(K):
            pos_by_state[k].append(rel[zi == k])
    dom = occ.max(axis=1)
    print(f'[{label}]')
    print(f'  1状態が90%以上のday: {int((dom >= 0.9).sum())}/{len(DAYS)}'
          f'  (最頻状態占有率の中央値 {np.median(dom):.3f})')
    print(f'  day内の状態切り替え: 合計 {sum(switches)} 回 / day中央値 {int(np.median(switches))}'
          f'  / day別 {switches}')
    print(f'  state run長: 中央値 {int(np.median(runs))} 試行 / 最大 {max(runs)}')
    print(f'  p_max 平均 {pmax.mean():.3f} / P(z)>={P_THRESHOLD} 残存率 {(pmax >= P_THRESHOLD).mean():.3f}')
    print('  day内の正規化位置（状態別 平均±sd）:')
    for k in range(K):
        v = np.concatenate(pos_by_state[k]) if pos_by_state[k] else np.array([])
        desc = f'{v.mean():.3f} ± {v.std():.3f}' if v.size else 'n/a'
        print(f'    state {k}: n={int((z == k).sum()):4d}  pos {desc}')
    wmax = np.abs(W[:, :, :, 1]).max()
    print(f'  |W| の最大 {wmax:.2f}')
    print()
    return dict(gamma=gamma, z=z, pmax=pmax, occ=occ, switches=np.array(switches), dom=dom)


sm = state_summary(final_P, final_pi, final_W, f'κ={KAPPA_BEST}')

BINS = 80
raster = np.full((len(DAYS), BINS), np.nan)
for i in range(len(DAYS)):
    zi = sm['z'][SESS[i]:SESS[i + 1]]
    for b in range(BINS):
        a = int(b / BINS * len(zi))
        c = int((b + 1) / BINS * len(zi))
        chunk = zi[a:max(c, a + 1)]
        raster[i, b] = np.bincount(chunk, minlength=K).argmax()

fig, axes = plt.subplots(2, 1, figsize=(10.5, 6.2), sharex=False,
                         gridspec_kw={'height_ratios': [1.3, 1]})
ax = axes[0]
cmap = plt.matplotlib.colors.ListedColormap(STATE_COLORS)
ax.imshow(raster, aspect='auto', cmap=cmap, vmin=-0.5, vmax=K - 0.5, interpolation='nearest')
ax.set_yticks(range(len(DAYS)))
ax.set_yticklabels(DAY_LABELS, fontsize=8)
ax.set_xlabel('day 内の位置（各 day を 80 分割し、その区間の最頻状態）')
ax.set_title(f'MAP 状態の並び（κ={KAPPA_BEST}）')
handles = [plt.matplotlib.patches.Patch(color=STATE_COLORS[k], label=f'state {k}') for k in range(K)]
ax.legend(handles=handles, frameon=False, ncol=K, loc='upper right')

ax = axes[1]
bottom = np.zeros(len(DAYS))
for k in range(K):
    ax.bar(np.arange(len(DAYS)), sm['occ'][:, k], bottom=bottom, color=STATE_COLORS[k], width=0.85, label=f'state {k}')
    bottom += sm['occ'][:, k]
ax.axhline(0.9, color='black', lw=0.8, ls='--')
ax.set_xticks(range(len(DAYS)))
ax.set_xticklabels(DAY_LABELS, fontsize=8)
ax.set_ylim(0, 1)
ax.set_ylabel('占有率')
ax.set_title('破線は「1状態が 90%」')
ax.legend(frameon=False, ncol=K, loc='upper right')
fig.tight_layout()
plt.show()