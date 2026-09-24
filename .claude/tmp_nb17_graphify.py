# -*- coding: utf-8 -*-
"""Replace table-heavy prints in notebook 17 with graphical outputs."""
import json
from pathlib import Path

NB = Path("notebooks/17_ver5_pre_implementation_checks.ipynb")
nb = json.loads(NB.read_text(encoding="utf-8"))


def set_source(i, source: str):
    # notebook stores source as list of lines ending with \n (except possibly last)
    lines = source.split("\n")
    nb["cells"][i]["source"] = [ln + "\n" for ln in lines[:-1]] + ([lines[-1]] if lines[-1] != "" else [])
    # clear stale outputs so re-run is obvious; keep structure
    if nb["cells"][i]["cell_type"] == "code":
        nb["cells"][i]["outputs"] = []
        nb["cells"][i]["execution_count"] = None


# ---------------------------------------------------------------------------
# Cell 8: day_stats — keep compute, drop wide table (plotted in cell 10)
# ---------------------------------------------------------------------------
set_source(8, r'''rows = []
for day in DAYS:
    g = tr[tr['task_day'] == day]
    n = len(g)
    n_pull = int((g['trial_type'] != 'No Reaction').sum())
    n_succ = int((g['trial_type'] == 'Success').sum())
    thr = g['pull_duration_for_success'].dropna()
    rows.append({
        'task_day': day,
        'n_trials': n,
        'p_no_reaction': (g['trial_type'] == 'No Reaction').mean(),
        'p_success_all': n_succ / n,
        'p_success_given_pull': (n_succ / n_pull) if n_pull else np.nan,
        'n_pull': n_pull,
        'thr_median': float(thr.median()) if len(thr) else np.nan,
        'thr_min': float(thr.min()) if len(thr) else np.nan,
        'thr_max': float(thr.max()) if len(thr) else np.nan,
    })
day_stats = pd.DataFrame(rows)
day_stats['day_idx'] = np.arange(1, len(day_stats) + 1)
day_stats['day_num'] = day_stats['task_day'].str.extract(r'(\d+)$').astype(int)
print(f'day_stats: {len(day_stats)} days, {int(day_stats["n_trials"].sum())} trials total')
''')

# ---------------------------------------------------------------------------
# Cell 9: trend correlations → bar charts
# ---------------------------------------------------------------------------
set_source(9, r'''def trend(y, x):
    y = np.asarray(y, dtype=float); x = np.asarray(x, dtype=float)
    ok = np.isfinite(y) & np.isfinite(x)
    rho, p_s = stats.spearmanr(x[ok], y[ok])
    r, p_p = stats.pearsonr(x[ok], y[ok])
    return rho, p_s, r, p_p

metrics = ['p_no_reaction', 'p_success_all', 'p_success_given_pull', 'thr_median', 'n_trials']
trend_rows = []
for m in metrics:
    rho, ps, r, pp = trend(day_stats[m], day_stats['day_idx'])
    trend_rows.append({'metric': m, 'spearman': rho, 'p_spearman': ps, 'pearson': r, 'p_pearson': pp})
trend_df = pd.DataFrame(trend_rows)

dnr = day_stats['p_no_reaction'].to_numpy()
dnr_delta = np.abs(np.diff(dnr))

fig, axes = plt.subplots(1, 2, figsize=(12, 3.6))
colors = ['#d62728' if p < 0.05 else '#4c72b0' for p in trend_df['p_spearman']]
axes[0].barh(trend_df['metric'], trend_df['spearman'], color=colors)
axes[0].axvline(0, color='k', lw=.8)
axes[0].set_xlim(-1, 1)
axes[0].set_xlabel('Spearman ρ vs day index')
axes[0].set_title('Monotonic trend across days (red: p<0.05)')
for y, row in trend_df.iterrows():
    axes[0].text(row['spearman'] + (0.03 if row['spearman'] >= 0 else -0.03), y,
                 f"p={row['p_spearman']:.3f}", va='center',
                 ha='left' if row['spearman'] >= 0 else 'right', fontsize=8)

day_mid = day_stats['day_num'].to_numpy()
pair_labels = [f'{a}→{b}' for a, b in zip(day_mid[:-1], day_mid[1:])]
axes[1].bar(np.arange(len(dnr_delta)), dnr_delta, color='#ff7f0e')
axes[1].axhline(dnr_delta.mean(), color='k', ls='--', label=f'mean {dnr_delta.mean():.3f}')
axes[1].set_xticks(np.arange(len(dnr_delta)))
axes[1].set_xticklabels(pair_labels, rotation=45, ha='right', fontsize=8)
axes[1].set_ylabel('|Δ No-Reaction rate|')
axes[1].set_title(f'Adjacent-day NR jumps (max {dnr_delta.max():.3f})')
axes[1].legend(fontsize=8); axes[1].grid(axis='y', alpha=.3)
plt.tight_layout(); plt.show()
''')

# ---------------------------------------------------------------------------
# Cell 10: expand to 4 panels including n_trials
# ---------------------------------------------------------------------------
set_source(10, r'''fig, axes = plt.subplots(1, 4, figsize=(16, 3.6))
x = day_stats['day_idx']
labels = day_stats['day_num'].astype(str)

axes[0].bar(x, day_stats['n_trials'], color='#7f7f7f')
axes[0].set_title('n trials'); axes[0].set_ylabel('trials')
axes[1].plot(x, day_stats['p_no_reaction'], 'o-', color='#d62728')
axes[1].set_title('No Reaction rate'); axes[1].set_ylim(0, 1)
axes[2].plot(x, day_stats['p_success_all'], 'o-', color='#2ca02c', label='all trials')
axes[2].plot(x, day_stats['p_success_given_pull'], 's--', color='#1f77b4', label='given pull')
axes[2].set_title('Success rate'); axes[2].set_ylim(0, 1); axes[2].legend(fontsize=8)
axes[3].plot(x, day_stats['thr_median'], 'o-', color='#9467bd')
axes[3].fill_between(x, day_stats['thr_min'], day_stats['thr_max'], alpha=.2, color='#9467bd')
axes[3].set_title('pull_duration_for_success')
axes[3].set_ylabel('seconds')
for ax in axes:
    ax.set_xticks(x); ax.set_xticklabels(labels); ax.set_xlabel('task day'); ax.grid(alpha=.3)
plt.tight_layout(); plt.show()
''')

# ---------------------------------------------------------------------------
# Cell 11: session-level → plots (day6 highlighted)
# ---------------------------------------------------------------------------
set_source(11, r'''# セッションレベルの点検（day6の外れ値性を含む）
rows = []
for _, srow in sess_raw.iterrows():
    day = srow['task_day']
    g = tr[tr['task_day'] == day]
    dur_min = float(srow['session_min'])
    thirds = np.array_split(g['trial_type'].to_numpy(), 3)
    nr3 = [float((t == 'No Reaction').mean()) for t in thirds]
    rows.append({
        'task_day': day, 'session_min': dur_min, 'n_trials': len(g),
        'trials_per_min': len(g) / dur_min,
        'frac_ITI_time': float(srow['frac_ITI_time']),
        'NR_1st': nr3[0], 'NR_2nd': nr3[1], 'NR_3rd': nr3[2],
    })
sess = pd.DataFrame(rows)
sess['day_num'] = sess['task_day'].str.extract(r'(\d+)$').astype(int)
sess['z_trials_per_min'] = (sess['trials_per_min'] - sess['trials_per_min'].mean()) / sess['trials_per_min'].std(ddof=0)
is_d6 = sess['task_day'].str.endswith('day6')

fig, axes = plt.subplots(1, 3, figsize=(14, 3.6))
x = np.arange(len(sess))
lab = sess['day_num'].astype(str)
c_bar = ['#d62728' if f else '#4c72b0' for f in is_d6]

axes[0].bar(x, sess['trials_per_min'], color=c_bar)
axes[0].axhline(sess['trials_per_min'].mean(), color='k', ls='--', lw=.8)
axes[0].set_ylabel('trials / min')
axes[0].set_title('Session pace (red = day6)')
for i, z in enumerate(sess['z_trials_per_min']):
    if abs(z) >= 2:
        axes[0].annotate(f'z={z:.1f}', (i, sess['trials_per_min'].iloc[i]),
                         textcoords='offset points', xytext=(0, 4), ha='center', fontsize=8, color='#d62728')

axes[1].plot(x, sess['NR_1st'], 'o-', label='1st third', color='#1f77b4')
axes[1].plot(x, sess['NR_2nd'], 's-', label='2nd third', color='#ff7f0e')
axes[1].plot(x, sess['NR_3rd'], '^-', label='3rd third', color='#d62728')
axes[1].set_ylim(0, 1); axes[1].set_ylabel('No-Reaction rate')
axes[1].set_title('NR rate within session thirds')
axes[1].legend(fontsize=8)

axes[2].bar(x, sess['frac_ITI_time'], color=c_bar)
axes[2].set_ylim(0, 1); axes[2].set_ylabel('fraction of session')
axes[2].set_title('ITI time fraction')

for ax in axes:
    ax.set_xticks(x); ax.set_xticklabels(lab, fontsize=8); ax.set_xlabel('task day'); ax.grid(alpha=.3)
plt.tight_layout(); plt.show()
print(f'day6: trials/min={float(sess.loc[is_d6, "trials_per_min"].iloc[0]):.1f} '
      f'(z={float(sess.loc[is_d6, "z_trials_per_min"].iloc[0]):.2f}), '
      f'NR thirds={sess.loc[is_d6, ["NR_1st","NR_2nd","NR_3rd"]].iloc[0].round(3).tolist()}')
''')

# ---------------------------------------------------------------------------
# Cell 13: stair compute + brief print (plot in 14)
# ---------------------------------------------------------------------------
set_source(13, r'''rows = []
for day in DAYS:
    g = tr[tr['task_day'] == day].sort_values('t_start')
    succ = (g['trial_type'] == 'Success').astype(int).to_numpy()
    thr = g['pull_duration_for_success'].to_numpy(dtype=float)
    roll = pd.Series(succ).rolling(20).mean().dropna()
    thr_ok = thr[np.isfinite(thr)]
    n_inc = int((np.diff(thr_ok) > 1e-9).sum()) if len(thr_ok) > 1 else 0
    rows.append({
        'task_day': day,
        'success_rate': succ.mean(),
        'roll20_median': float(roll.median()) if len(roll) else np.nan,
        'roll20_max': float(roll.max()) if len(roll) else np.nan,
        'frac_roll20_ge80': float((roll >= 0.8).mean()) if len(roll) else np.nan,
        'Tpull_init': float(np.nanmin(thr_ok)) if len(thr_ok) else np.nan,
        'Tpull_final': float(np.nanmax(thr_ok)) if len(thr_ok) else np.nan,
        'n_increments': n_inc,
    })
stair = pd.DataFrame(rows)
stair['day_idx'] = np.arange(1, len(stair) + 1)

print(f'全day平均の成功率（全音提示試行）: {tr["trial_type"].eq("Success").mean():.3f}')
print(f'day別 成功率の中央値: {stair["success_rate"].median():.3f} '
      f'（最小 {stair["success_rate"].min():.3f} / 最大 {stair["success_rate"].max():.3f}）')
print(f'20試行移動窓の成功率が0.8以上だった割合: 全day平均 {stair["frac_roll20_ge80"].mean():.3f}')
print(f'Tpull の引き上げ回数: 合計 {stair["n_increments"].sum()} 回 / day中央値 {stair["n_increments"].median():.0f}')

rho, ps, r, pp = trend(stair['Tpull_final'], stair['day_idx'])
print(f'Tpull_final の day index 相関: Spearman {rho:+.3f} (p={ps:.3f}) / Pearson {r:+.3f} (p={pp:.3f})')
''')

# ---------------------------------------------------------------------------
# Cell 14: expand staircase plots
# ---------------------------------------------------------------------------
set_source(14, r'''fig, axes = plt.subplots(1, 3, figsize=(14, 3.4))
x = stair['day_idx']
lab = day_stats['day_num'].astype(str)

axes[0].plot(x, stair['success_rate'], 'o-', color='#2ca02c', label='session success rate')
axes[0].plot(x, stair['roll20_median'], 's--', color='#8c564b', label='median rolling-20')
axes[0].axhline(0.8, color='r', ls=':', label='staircase criterion 0.8')
axes[0].set_ylim(0, 1); axes[0].set_title('success rate vs staircase criterion')
axes[0].legend(fontsize=7); axes[0].set_ylabel('rate')

axes[1].plot(x, stair['Tpull_final'], 'o-', color='#9467bd', label='Tpull_final')
axes[1].plot(x, stair['Tpull_init'], 's--', color='#c5b0d5', label='Tpull_initial')
axes[1].axhline(0.4, color='r', ls=':', label='cap 0.40 s')
axes[1].set_title('Tpull trajectory'); axes[1].legend(fontsize=7); axes[1].set_ylabel('seconds')

axes[2].bar(x - .15, stair['frac_roll20_ge80'], width=.3, color='#2ca02c', label='frac roll20≥0.8')
axes[2].bar(x + .15, stair['n_increments'] / max(stair['n_increments'].max(), 1),
            width=.3, color='#9467bd', label='n_increments (norm)')
axes[2].set_ylim(0, 1.05)
axes[2].set_title('How often staircase fires')
axes[2].legend(fontsize=7)
for i, n in enumerate(stair['n_increments']):
    axes[2].text(x.iloc[i] + .15, stair['n_increments'].iloc[i] / max(stair['n_increments'].max(), 1) + .02,
                 str(int(n)), ha='center', fontsize=7, color='#9467bd')

for ax in axes:
    ax.set_xticks(x); ax.set_xticklabels(lab); ax.set_xlabel('task day'); ax.grid(alpha=.3)
plt.tight_layout(); plt.show()
''')

# ---------------------------------------------------------------------------
# Cell 16: Short Pull subtypes → pie + stacked bars
# ---------------------------------------------------------------------------
set_source(16, r'''nr_tr = tr[tr['trial_type'] == 'No Reaction']
DEADLINE = float((nr_tr['t_end'] - nr_tr['t_start']).median())
print(f'締め切り（No Reaction試行の窓長の中央値）: {DEADLINE:.4f} 秒')

sp = tr[tr['trial_type'] == 'Short Pull'].copy()
sp['rt'] = sp['t_onset'] - sp['t_start']

def classify(row):
    dur, thr, rt = row['pull_duration'], row['pull_duration_for_success'], row['rt']
    if not np.isfinite(dur):
        return 'unmeasured'
    if np.isfinite(thr) and dur < thr:
        return 'too_short'
    if np.isfinite(thr) and np.isfinite(rt) and (rt + thr) > DEADLINE:
        return 'deadline'
    return 'dropout'

sp['sp_subtype'] = sp.apply(classify, axis=1)
cnt = sp['sp_subtype'].value_counts()
order = [k for k in ['dropout', 'too_short', 'deadline', 'unmeasured'] if k in cnt.index]
ct_day = pd.crosstab(sp['task_day'], sp['sp_subtype']).reindex(index=DAYS, columns=order).fillna(0)
ct_day_frac = ct_day.div(ct_day.sum(axis=1).replace(0, np.nan), axis=0)

sub_colors = {'dropout': '#ff7f0e', 'too_short': '#1f77b4', 'deadline': '#d62728', 'unmeasured': '#7f7f7f'}

fig, axes = plt.subplots(1, 2, figsize=(13, 3.8))
axes[0].pie([cnt[k] for k in order], labels=[f'{k}\n{cnt[k]} ({cnt[k]/len(sp)*100:.1f}%)' for k in order],
            colors=[sub_colors[k] for k in order], startangle=90)
axes[0].set_title(f'Short Pull subtypes (n={len(sp)})')

bottom = np.zeros(len(DAYS))
x = np.arange(len(DAYS))
for k in order:
    axes[1].bar(x, ct_day[k].to_numpy(), bottom=bottom, color=sub_colors[k], label=k)
    bottom += ct_day[k].to_numpy()
axes[1].set_xticks(x)
axes[1].set_xticklabels(day_stats['day_num'].astype(str), fontsize=8)
axes[1].set_xlabel('task day'); axes[1].set_ylabel('Short Pull count')
axes[1].set_title('Subtype counts by day')
axes[1].legend(fontsize=8, ncol=2)
axes[1].grid(axis='y', alpha=.3)
plt.tight_layout(); plt.show()

tr['sp_subtype'] = ''
tr.loc[sp.index, 'sp_subtype'] = sp['sp_subtype']
''')

# ---------------------------------------------------------------------------
# Cell 18: SP duration by day → plots
# ---------------------------------------------------------------------------
set_source(18, r'''rows = []
for day in DAYS:
    g = tr[tr['task_day'] == day]
    sp_d = g[g['trial_type'] == 'Short Pull']
    su_d = g[g['trial_type'] == 'Success']
    thr_med = float(g['pull_duration_for_success'].median())
    ratio = (sp_d['pull_duration'] / sp_d['pull_duration_for_success']).replace([np.inf, -np.inf], np.nan)
    rows.append({
        'task_day': day,
        'Tpull_med': thr_med,
        'n_SP': len(sp_d),
        'SP_dur_med': float(sp_d['pull_duration'].median()) if len(sp_d) else np.nan,
        'SP_dur_ratio_med': float(ratio.median()) if ratio.notna().any() else np.nan,
        'n_Succ': len(su_d),
        'Succ_dur_med': float(su_d['pull_duration'].median()) if len(su_d) else np.nan,
        'frac_dropout': float((sp_d['sp_subtype'] == 'dropout').mean()) if len(sp_d) else np.nan,
        'frac_too_short': float((sp_d['sp_subtype'] == 'too_short').mean()) if len(sp_d) else np.nan,
    })
spday = pd.DataFrame(rows)
spday['day_idx'] = np.arange(1, len(spday) + 1)

fig, axes = plt.subplots(1, 3, figsize=(14, 3.6))
x = spday['day_idx']
lab = day_stats['day_num'].astype(str)

axes[0].plot(x, spday['Tpull_med'], 'o--', color='#9467bd', label='Tpull median')
axes[0].plot(x, spday['SP_dur_med'], 's-', color='#ff7f0e', label='Short Pull dur median')
axes[0].plot(x, spday['Succ_dur_med'], '^-', color='#2ca02c', label='Success dur median')
axes[0].set_ylabel('seconds'); axes[0].set_title('Hold duration vs threshold')
axes[0].legend(fontsize=7)

axes[1].plot(x, spday['SP_dur_ratio_med'], 'o-', color='#1f77b4')
axes[1].axhline(1.0, color='r', ls=':', label='dur = Tpull')
axes[1].set_ylabel('SP dur / Tpull'); axes[1].set_title('Short Pull duration relative to threshold')
axes[1].legend(fontsize=8)

axes[2].plot(x, spday['frac_dropout'], 'o-', color='#ff7f0e', label='dropout')
axes[2].plot(x, spday['frac_too_short'], 's-', color='#1f77b4', label='too_short')
axes[2].set_ylim(0, 1); axes[2].set_ylabel('fraction of SP')
axes[2].set_title('SP subtype mix by day'); axes[2].legend(fontsize=8)

for ax in axes:
    ax.set_xticks(x); ax.set_xticklabels(lab); ax.set_xlabel('task day'); ax.grid(alpha=.3)
plt.tight_layout(); plt.show()

print('day index に対する単調傾向')
for m in ['SP_dur_med', 'SP_dur_ratio_med', 'Succ_dur_med', 'frac_dropout', 'frac_too_short']:
    rho, ps, r, pp = trend(spday[m], spday['day_idx'])
    print(f'  {m:18s} Spearman {rho:+.3f} (p={ps:.3f})')
print('Tpull_med に対する相関')
for m in ['SP_dur_med', 'Succ_dur_med']:
    rho, ps, r, pp = trend(spday[m], spday['Tpull_med'])
    print(f'  {m:18s} Spearman {rho:+.3f} (p={ps:.3f})')
''')

# ---------------------------------------------------------------------------
# Cell 20: temporal clustering → day-wise bars
# ---------------------------------------------------------------------------
set_source(20, r'''def runs_z(b):
    b = np.asarray(b, dtype=int)
    n = len(b); n1 = int(b.sum()); n0 = n - n1
    if n1 == 0 or n0 == 0 or n < 20:
        return np.nan
    R = 1 + int((np.diff(b) != 0).sum())
    mu = 2 * n1 * n0 / n + 1
    var = (mu - 1) * (mu - 2) / (n - 1)
    if var <= 0:
        return np.nan
    return (R - mu) / np.sqrt(var)

def lag1(b):
    b = np.asarray(b, dtype=float)
    if len(b) < 20 or b.std() == 0:
        return np.nan
    return float(np.corrcoef(b[:-1], b[1:])[0, 1])

def day_stats_seq(seq_by_day):
    rows = []
    for day, b in seq_by_day:
        rows.append({'task_day': day, 'n': len(b), 'lag1': lag1(b), 'runs_z': runs_z(b)})
    return pd.DataFrame(rows)

seq_yA = [(d, tr.loc[tr['task_day'] == d, 'yA'].to_numpy()) for d in DAYS]
pulled = tr[tr['trial_type'] != 'No Reaction']
seq_sp = [(d, (pulled.loc[pulled['task_day'] == d, 'trial_type'] == 'Short Pull').astype(int).to_numpy())
          for d in DAYS]
pulled_nodrop = pulled[pulled['sp_subtype'] != 'dropout']
seq_sp2 = [(d, (pulled_nodrop.loc[pulled_nodrop['task_day'] == d, 'trial_type'] == 'Short Pull').astype(int).to_numpy())
           for d in DAYS]

panels = [
    ('A) yA (cue response)', day_stats_seq(seq_yA), '#1f77b4'),
    ('B) Short Pull | pulled', day_stats_seq(seq_sp), '#ff7f0e'),
    ('C) Short Pull | no dropout', day_stats_seq(seq_sp2), '#2ca02c'),
]

fig, axes = plt.subplots(2, 3, figsize=(14, 6.2), sharex=True)
for j, (label, df, color) in enumerate(panels):
    x = np.arange(len(df))
    lab = [str(int(s.split('day')[-1])) for s in df['task_day']]
    axes[0, j].bar(x, df['lag1'], color=color)
    axes[0, j].axhline(0, color='k', lw=.8)
    axes[0, j].set_title(label); axes[0, j].set_ylabel('lag-1 autocorr')
    axes[0, j].grid(axis='y', alpha=.3)
    mean_ac = np.nanmean(df['lag1'])
    axes[0, j].axhline(mean_ac, color='k', ls='--', lw=.8, label=f'mean {mean_ac:+.2f}')
    axes[0, j].legend(fontsize=7)

    axes[1, j].bar(x, df['runs_z'], color=color)
    axes[1, j].axhline(-1.96, color='r', ls=':', label='z=-1.96')
    axes[1, j].axhline(0, color='k', lw=.8)
    axes[1, j].set_ylabel('runs-test z'); axes[1, j].set_xlabel('task day')
    axes[1, j].set_xticks(x); axes[1, j].set_xticklabels(lab, fontsize=8)
    axes[1, j].grid(axis='y', alpha=.3)
    zs = df['runs_z'].dropna().to_numpy()
    stouffer = zs.sum() / np.sqrt(len(zs)) if len(zs) else np.nan
    p = 2 * stats.norm.sf(abs(stouffer)) if np.isfinite(stouffer) else np.nan
    n_sig = int((zs < -1.96).sum()) if len(zs) else 0
    axes[1, j].set_title(f'Stouffer z={stouffer:+.2f} (p={p:.1e}); {n_sig}/{len(zs)} days clustered')
    axes[1, j].legend(fontsize=7)

plt.tight_layout(); plt.show()

res = {}
for key, (_, df, _) in zip(['yA', 'short', 'short_nodrop'], panels):
    zs = df['runs_z'].dropna().to_numpy()
    stouffer = zs.sum() / np.sqrt(len(zs)) if len(zs) else np.nan
    res[key] = (stouffer, float(np.nanmean(df['lag1'])))
''')

# ---------------------------------------------------------------------------
# Cell 22: CV gains → bar chart
# ---------------------------------------------------------------------------
set_source(22, r'''from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import log_loss

def cv_gain(X, y, label, n_splits=5, seed=0):
    X = np.asarray(X, dtype=float); y = np.asarray(y, dtype=int)
    if len(np.unique(y)) < 2 or min(np.bincount(y)) < n_splits:
        print(f'{label}: サンプル不足でスキップ'); return np.nan, np.nan, np.nan
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    ll_m, ll_b = [], []
    for tr_i, te_i in skf.split(X, y):
        m = LogisticRegression(max_iter=2000, C=1.0)
        m.fit(X[tr_i], y[tr_i])
        ll_m.append(log_loss(y[te_i], m.predict_proba(X[te_i])[:, 1], labels=[0, 1]))
        p = np.clip(y[tr_i].mean(), 1e-6, 1 - 1e-6)
        ll_b.append(log_loss(y[te_i], np.full(len(te_i), p), labels=[0, 1]))
    gain = np.mean(ll_b) - np.mean(ll_m)
    return gain, float(np.mean(ll_b)), float(np.mean(ll_m))

feat = ['x_bias', 'x_hist_z', 'x_rew_z']
gains = [
    ('A) yA\n(all cue trials)', *cv_gain(tr[feat], tr['yA'], 'A')),
    ('B) Short Pull\n(pulled only)', *cv_gain(pulled[feat], (pulled['trial_type'] == 'Short Pull').astype(int), 'B')),
    ('C) Short Pull\n(no dropout)', *cv_gain(pulled_nodrop[feat],
                                             (pulled_nodrop['trial_type'] == 'Short Pull').astype(int), 'C')),
]
gA, gB, gC = gains[0][1], gains[1][1], gains[2][1]

fig, axes = plt.subplots(1, 2, figsize=(11, 3.6))
labels = [g[0] for g in gains]
xi = np.arange(len(gains))
axes[0].bar(xi - 0.175, [g[2] for g in gains], width=0.35, label='intercept-only', color='#c7c7c7')
axes[0].bar(xi + 0.175, [g[3] for g in gains], width=0.35, label='+ History/Reward', color='#1f77b4')
axes[0].set_xticks(xi); axes[0].set_xticklabels(labels, fontsize=8)
axes[0].set_ylabel('CV log-loss (nats/trial)'); axes[0].set_title('3-D input vs intercept-only')
axes[0].legend(fontsize=8); axes[0].grid(axis='y', alpha=.3)

axes[1].bar(xi, [g[1] for g in gains], color=['#1f77b4', '#ff7f0e', '#2ca02c'])
axes[1].axhline(0, color='k', lw=.8)
axes[1].set_xticks(xi); axes[1].set_xticklabels(labels, fontsize=8)
axes[1].set_ylabel('Δ log-loss (nats/trial)'); axes[1].set_title('CV gain from 3-D input')
axes[1].grid(axis='y', alpha=.3)
for i, g in enumerate(gains):
    axes[1].text(i, g[1] + 0.002, f'{g[1]:+.4f}', ha='center', fontsize=9)
plt.tight_layout(); plt.show()
print('（Biasは定数なので実質2次元。改善は nats/試行）')
''')

# ---------------------------------------------------------------------------
# Cell 25: retention + state×type heatmap
# ---------------------------------------------------------------------------
set_source(25, r'''print(f'閾値 P(z)>={P_THRESHOLD} の残存率')
overall = (trA['p_max'] >= P_THRESHOLD).mean()
print(f'  全体: {overall:.3f}  ({int((trA["p_max"] >= P_THRESHOLD).sum())} / {len(trA)} 試行)')
ret = trA.groupby('task_day', sort=False)['p_max'].apply(lambda s: (s >= P_THRESHOLD).mean())
kept = trA[trA['p_max'] >= P_THRESHOLD]
ct_state_type = pd.crosstab(kept['state'], kept['trial_type']).reindex(
    index=range(NUM_STATES), columns=SOUND_TYPES).fillna(0)

fig, axes = plt.subplots(1, 2, figsize=(12, 3.6))
x = np.arange(len(DAYS))
axes[0].bar(x, ret.reindex(DAYS).to_numpy(), color='#4c72b0')
axes[0].axhline(overall, color='r', ls='--', label=f'overall {overall:.3f}')
axes[0].set_ylim(0, 1.05); axes[0].set_ylabel('retention rate')
axes[0].set_title(f'P(z)≥{P_THRESHOLD} retention by day')
axes[0].set_xticks(x); axes[0].set_xticklabels(day_stats['day_num'].astype(str), fontsize=8)
axes[0].set_xlabel('task day'); axes[0].legend(fontsize=8); axes[0].grid(axis='y', alpha=.3)

im = axes[1].imshow(ct_state_type.to_numpy(), aspect='auto', cmap='Blues')
axes[1].set_xticks(range(len(SOUND_TYPES))); axes[1].set_xticklabels(SOUND_TYPES, fontsize=8)
axes[1].set_yticks(range(NUM_STATES)); axes[1].set_yticklabels([f'state {k}' for k in range(NUM_STATES)])
axes[1].set_title('Kept trials: state × trial type')
for i in range(NUM_STATES):
    for j in range(len(SOUND_TYPES)):
        axes[1].text(j, i, int(ct_state_type.iloc[i, j]), ha='center', va='center', fontsize=9,
                     color='white' if ct_state_type.iloc[i, j] > ct_state_type.to_numpy().max() / 2 else 'black')
plt.colorbar(im, ax=axes[1], fraction=0.046, pad=0.04)
plt.tight_layout(); plt.show()
''')

# ---------------------------------------------------------------------------
# Cell 26: balancing — keep compute, drop wide table (cell 28 plots)
# ---------------------------------------------------------------------------
set_source(26, r'''# 6.4節のバランシング（day内で状態×試行タイプを釣り合わせる）後に何試行使えるか
rows = []
for d in DAYS:
    g = kept[kept['task_day'] == d]
    ct = pd.crosstab(g['trial_type'], g['state'])
    ct = ct.reindex(index=SOUND_TYPES, columns=range(NUM_STATES), fill_value=0)
    per_type_min = ct.min(axis=1)
    usable = int((per_type_min * NUM_STATES).sum())
    rows.append({
        'task_day': d,
        'n_all': int((trA['task_day'] == d).sum()),
        'n_kept': len(g),
        'n_states_present': int((ct.sum(axis=0) > 0).sum()),
        'min_cell': int(ct.values.min()),
        'usable_balanced': usable,
        'usable_per_state': usable // NUM_STATES,
    })
bal = pd.DataFrame(rows)
print(f'day別 balanced 使用可能試行数: 中央値 {bal["usable_balanced"].median():.0f}, '
      f'最小 {bal["usable_balanced"].min()}, 最大 {bal["usable_balanced"].max()}')
print(f'全day合計: {bal["usable_balanced"].sum()} 試行')
print(f'min_cell=0 のday数: {(bal["min_cell"] == 0).sum()} / {len(bal)}')
print(f'day内に出現した状態数の中央値: {bal["n_states_present"].median():.0f}')
''')

# ---------------------------------------------------------------------------
# Cell 27: occupancy → stacked bars + run-length
# ---------------------------------------------------------------------------
set_source(27, r'''# 閾値をかけない状態占有（day別）。状態がday単位に分かれてしまっていないかの確認。
occ = pd.crosstab(trA['task_day'], trA['state']).reindex(DAYS)
occ_frac = occ.div(occ.sum(axis=1), axis=0)
n_states_day = (occ > 0).sum(axis=1)
dom = occ_frac.max(axis=1)

runs = []
for d in DAYS:
    z = trA.loc[trA['task_day'] == d, 'state'].to_numpy()
    if len(z) == 0:
        continue
    cut = np.flatnonzero(np.diff(z) != 0) + 1
    for seg in np.split(z, cut):
        runs.append((int(seg[0]), len(seg)))
rdf = pd.DataFrame(runs, columns=['state', 'run_len'])
n_switch = len(rdf) - len(DAYS)
med_switch = int(np.median([((np.diff(trA.loc[trA['task_day'] == d, 'state'].to_numpy()) != 0).sum()) for d in DAYS]))

fig, axes = plt.subplots(1, 3, figsize=(14, 3.6))
x = np.arange(len(DAYS))
lab = day_stats['day_num'].astype(str)
bottom = np.zeros(len(DAYS))
state_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
for k in range(NUM_STATES):
    vals = occ_frac[k].to_numpy() if k in occ_frac.columns else np.zeros(len(DAYS))
    axes[0].bar(x, vals, bottom=bottom, color=state_colors[k % len(state_colors)], label=f'state {k}')
    bottom += vals
axes[0].set_ylim(0, 1); axes[0].set_ylabel('occupancy'); axes[0].set_title('State occupancy by day (no threshold)')
axes[0].legend(fontsize=7, ncol=NUM_STATES); axes[0].set_xticks(x); axes[0].set_xticklabels(lab, fontsize=8)
axes[0].set_xlabel('task day'); axes[0].grid(axis='y', alpha=.3)

axes[1].bar(x, n_states_day.to_numpy(), color='#4c72b0')
axes[1].axhline(1, color='r', ls=':')
axes[1].set_ylabel('# states present'); axes[1].set_title(
    f'Dominant occupancy ≥0.9: {int((dom >= 0.9).sum())}/{len(dom)} days')
axes[1].set_xticks(x); axes[1].set_xticklabels(lab, fontsize=8); axes[1].set_xlabel('task day')
axes[1].grid(axis='y', alpha=.3)

for k in sorted(rdf['state'].unique()):
    vals = rdf.loc[rdf['state'] == k, 'run_len']
    axes[2].scatter(np.full(len(vals), k) + np.random.default_rng(0).normal(0, 0.05, len(vals)),
                    vals, alpha=.7, s=40, color=state_colors[k % len(state_colors)], label=f'state {k}')
axes[2].set_xticks(range(NUM_STATES)); axes[2].set_xlabel('state'); axes[2].set_ylabel('run length (trials)')
axes[2].set_title(f'Viterbi run lengths (switches total {n_switch}, day median {med_switch})')
axes[2].grid(axis='y', alpha=.3)
plt.tight_layout(); plt.show()

print(f'最頻状態の占有率: 中央値 {dom.median():.3f} / 最小 {dom.min():.3f} / 最大 {dom.max():.3f}')
print(f'1状態が90%以上を占めるday: {int((dom >= 0.9).sum())} / {len(dom)}')
''')

# ---------------------------------------------------------------------------
# Cell 28: keep hist + usable trials; add n_states overlay note already covered
# ---------------------------------------------------------------------------
set_source(28, r'''fig, axes = plt.subplots(1, 2, figsize=(11, 3.4))
axes[0].hist(trA['p_max'], bins=40, color='#4c72b0')
axes[0].axvline(P_THRESHOLD, color='r', ls='--', label=f'threshold {P_THRESHOLD}')
axes[0].set_xlabel('max posterior P(z)'); axes[0].set_ylabel('trials'); axes[0].legend(fontsize=8)
axes[0].set_title('state confidence (static fit, K=%d)' % NUM_STATES)

xi = np.arange(len(bal))
axes[1].bar(xi - .2, bal['n_all'], width=.4, label='all trials', color='#c7c7c7')
axes[1].bar(xi + .2, bal['usable_balanced'], width=.4, label='after threshold+balancing', color='#d62728')
axes[1].set_xticks(xi); axes[1].set_xticklabels(day_stats['day_num'].astype(str), fontsize=8)
axes[1].set_xlabel('task day'); axes[1].set_ylabel('trials'); axes[1].legend(fontsize=8)
axes[1].set_title('usable trials per day for cortical decoding')
plt.tight_layout(); plt.show()
''')

# ---------------------------------------------------------------------------
# Cell 32: category probs + crosstab heatmap
# ---------------------------------------------------------------------------
set_source(32, r'''# 状態ごとのカテゴリ確率（入力を平均値に固定したときの予測分布）と、系統Bの残存率
x_mean = np.array([1.0, 0.0, 0.0])   # bias=1, z化した2列の平均=0
W = modelB.observations.Wk           # (K, C-1, M)
logits = np.concatenate([W @ x_mean, np.zeros((W.shape[0], 1))], axis=1)   # 末尾に参照カテゴリの0
probs = np.exp(logits - logits.max(axis=1, keepdims=True))
probs /= probs.sum(axis=1, keepdims=True)
prob_df = pd.DataFrame(probs, columns=['Success', 'Short Pull', 'No Reaction'],
                       index=[f'state {k}' for k in range(NUM_STATES)])

zB, pB = v4.decode_states(modelB, ysB, xs)
trB = v4.attach_decoded_states(tr, zB, pB)
pcolsB = [c for c in trB.columns if c.startswith('p_state_')]
trB['p_max'] = trB[pcolsB].max(axis=1)
keptB = trB[trB['p_max'] >= P_THRESHOLD]
ctB = pd.crosstab(keptB['state'], keptB['trial_type']).reindex(
    index=range(NUM_STATES), columns=SOUND_TYPES).fillna(0)

fig, axes = plt.subplots(1, 2, figsize=(12, 3.8))
x = np.arange(NUM_STATES)
w = 0.25
for j, col in enumerate(prob_df.columns):
    axes[0].bar(x + (j - 1) * w, prob_df[col], width=w, label=col)
axes[0].set_xticks(x); axes[0].set_xticklabels(prob_df.index)
axes[0].set_ylim(0, 1); axes[0].set_ylabel('probability')
axes[0].set_title('Predicted category probs at mean input')
axes[0].legend(fontsize=8); axes[0].grid(axis='y', alpha=.3)

im = axes[1].imshow(ctB.to_numpy(), aspect='auto', cmap='Greens')
axes[1].set_xticks(range(len(SOUND_TYPES))); axes[1].set_xticklabels(SOUND_TYPES, fontsize=8)
axes[1].set_yticks(range(NUM_STATES)); axes[1].set_yticklabels([f'state {k}' for k in range(NUM_STATES)])
axes[1].set_title(f'System B kept trials (retention={(trB["p_max"] >= P_THRESHOLD).mean():.3f})')
for i in range(NUM_STATES):
    for j in range(len(SOUND_TYPES)):
        axes[1].text(j, i, int(ctB.iloc[i, j]), ha='center', va='center', fontsize=9,
                     color='white' if ctB.iloc[i, j] > ctB.to_numpy().max() / 2 else 'black')
plt.colorbar(im, ax=axes[1], fraction=0.046, pad=0.04)
plt.tight_layout(); plt.show()
print(f'系統B の P(z)>={P_THRESHOLD} 残存率: {(trB["p_max"] >= P_THRESHOLD).mean():.3f} '
      f'(系統A: {(trA["p_max"] >= P_THRESHOLD).mean():.3f})')
''')

# ---------------------------------------------------------------------------
# Cell 36: synthetic recovery — add weight trajectory plot
# ---------------------------------------------------------------------------
set_source(36, r'''from itertools import permutations

def simulate_dyn(S=14, T=170, K=2, D=3, C=2, alpha_true=0.30, seed=0):
    rng = np.random.default_rng(seed)
    Wt = np.zeros((S, K, C - 1, D))
    Wt[0, 0, 0] = [2.0, 0.5, 0.0]     # よく引く状態
    Wt[0, 1, 0] = [-1.5, 0.0, 0.0]    # 引かない状態
    for s in range(1, S):
        Wt[s] = Wt[s - 1] + rng.normal(0, alpha_true, Wt[s - 1].shape)
    Pt = np.array([[0.95, 0.05], [0.10, 0.90]])
    ys_s, xs_s, zs_s = [], [], []
    for s in range(S):
        X = np.column_stack([np.ones(T), rng.normal(0, 1, T), rng.normal(0, 1, T)])
        z = np.empty(T, dtype=int); z[0] = rng.integers(K)
        for t in range(1, T):
            z[t] = rng.choice(K, p=Pt[z[t - 1]])
        logit = np.stack([X @ Wt[s, k, 0] for k in range(K)], axis=1)[np.arange(T), z]
        pull = (rng.random(T) < 1.0 / (1.0 + np.exp(-logit))).astype(int)
        ys_s.append(1 - pull)          # クラス0=引いた, クラス1(=参照)=引かない
        xs_s.append(X); zs_s.append(z)
    return ys_s, xs_s, zs_s, Wt, Pt

def best_perm_acc(z_true, z_hat, K):
    a = np.concatenate(z_true); b = np.concatenate(z_hat)
    best, arg = -1.0, None
    for perm in permutations(range(K)):
        acc = float((np.array(perm)[b] == a).mean())
        if acc > best:
            best, arg = acc, perm
    return best, arg

sy, sx, sz, W_true, P_true = simulate_dyn()
print('合成データ: %d day × %d 試行, K=2, 真のalpha=0.30' % (len(sy), len(sy[0])))

s_std = fit_dyn_glmhmm(sy, sx, K=2, C=2, model_type='standard', sigma0=2.0, seed=0)
s_par = fit_dyn_glmhmm(sy, sx, K=2, C=2, model_type='partial', alpha_w=0.3, sigma0=2.0,
                       W_init=s_std['W'], P_init=s_std['P'], seed=0)
s_dyn = fit_dyn_glmhmm(sy, sx, K=2, C=2, model_type='dynamic', alpha_w=0.3, kappa=100.0,
                       sigma0=2.0, W_init=s_par['W'], P_init=s_par['P'], A_global=s_par['A'], seed=0)

rec_rows = []
for nm, ft in [('standard', s_std), ('partial', s_par), ('dynamic', s_dyn)]:
    zh, _ = decode(ft, sy, sx)
    acc, _ = best_perm_acc(sz, zh, 2)
    rec_rows.append({'model': nm, 'log_post': ft['lps'][-1], 'n_iter': ft['n_iter'], 'acc': acc})
    print(f'  {nm:8s} log posterior {ft["lps"][-1]:9.2f}  {ft["n_iter"]:3d} iters  状態復元 {acc:.3f}')

zh, _ = decode(s_par, sy, sx)
_, perm = best_perm_acc(sz, zh, 2)
W_hat = s_par['W'][:, np.argsort(np.array(perm))]
mae = np.abs(W_hat - W_true).mean()
corr = np.corrcoef(W_true.ravel(), W_hat.ravel())[0, 1]
print(f'  partial の重み軌跡: 平均絶対誤差 {mae:.3f} '
      f'(真の値の範囲 {W_true.min():.2f}..{W_true.max():.2f})、真値との相関 {corr:.3f}')

rec = pd.DataFrame(rec_rows)
fig, axes = plt.subplots(1, 3, figsize=(14, 3.6))
axes[0].bar(rec['model'], rec['acc'], color=['#7f7f7f', '#1f77b4', '#9467bd'])
axes[0].set_ylim(0, 1); axes[0].set_ylabel('state recovery accuracy')
axes[0].set_title('Decoded-state accuracy'); axes[0].grid(axis='y', alpha=.3)

# weight trajectories: bias weight (dim 0) for each state
days = np.arange(W_true.shape[0])
for k in range(2):
    axes[1].plot(days, W_true[:, k, 0, 0], '--', color=state_colors[k], label=f'true state {k}')
    axes[1].plot(days, W_hat[:, k, 0, 0], '-', color=state_colors[k], alpha=.85, label=f'hat state {k}')
axes[1].set_xlabel('session'); axes[1].set_ylabel('bias weight')
axes[1].set_title(f'partial weight traj (MAE={mae:.3f}, r={corr:.3f})')
axes[1].legend(fontsize=7, ncol=2); axes[1].grid(alpha=.3)

axes[2].scatter(W_true.ravel(), W_hat.ravel(), alpha=.5, s=18, color='#1f77b4')
lim = [min(W_true.min(), W_hat.min()), max(W_true.max(), W_hat.max())]
axes[2].plot(lim, lim, 'r--', lw=1)
axes[2].set_xlabel('true W'); axes[2].set_ylabel('recovered W')
axes[2].set_title('Weight recovery scatter'); axes[2].grid(alpha=.3)
plt.tight_layout(); plt.show()
''')

# ---------------------------------------------------------------------------
# Cell 37: alpha grid → errorbar plot
# ---------------------------------------------------------------------------
set_source(37, r'''# 合成データでのalphaグリッド（真値0.30が選ばれるか）
sfolds = [block_folds(len(y), n_folds=5, block=10, seed=0) for y in sy]
print('合成データ 5-fold CV（model_type="partial"）')
rows = []
for a in [0.01, 0.1, 0.3, 1.0, 10.0]:
    sc = []
    for f in range(5):
        fit = fit_dyn_glmhmm(sy, sx, K=2, C=2, model_type='partial', alpha_w=a, sigma0=2.0,
                             masks=[fo != f for fo in sfolds],
                             W_init=s_std['W'], P_init=s_std['P'], num_iters=80, seed=0)
        sc.append(test_loglik(fit, sy, sx, [fo == f for fo in sfolds]))
    rows.append({'alpha': a, 'test_ll': np.mean(sc), 'se': np.std(sc) / np.sqrt(len(sc))})
    print(f'  alpha={a:6.2f}  test LL/試行 {np.mean(sc):+.4f}  SE {rows[-1]["se"]:.4f}')
synth_alpha = pd.DataFrame(rows)

fig, ax = plt.subplots(figsize=(5.5, 3.4))
ax.errorbar(synth_alpha['alpha'], synth_alpha['test_ll'], yerr=synth_alpha['se'], marker='o', color='#1f77b4')
ax.axvline(0.30, color='r', ls='--', label='true α=0.30')
best_a = float(synth_alpha.loc[synth_alpha['test_ll'].idxmax(), 'alpha'])
ax.axvline(best_a, color='#2ca02c', ls=':', label=f'best CV α={best_a:g}')
ax.set_xscale('log'); ax.set_xlabel('alpha'); ax.set_ylabel('test LL / trial')
ax.set_title('Synthetic partial: alpha grid'); ax.legend(fontsize=8); ax.grid(alpha=.3)
plt.tight_layout(); plt.show()
print('真のalphaは0.30。alpha=0.01（ほぼ静的）が明確に劣ることが確認できればよい。')
''')

# ---------------------------------------------------------------------------
# Cell 47: drop table, keep stacked occupancy plot + switches
# ---------------------------------------------------------------------------
set_source(47, r'''occ_df = pd.DataFrame(sm_dyn['occ'], index=DAYS,
                      columns=[f'state {k}' for k in range(NUM_STATES)])
occ_df['switches'] = sm_dyn['switches']

fig, axes = plt.subplots(1, 3, figsize=(14, 3.6))
for ax, sm, ttl in [(axes[0], sm_std, 'standard'), (axes[1], sm_dyn, 'dynamic')]:
    bottom = np.zeros(len(DAYS))
    for k in range(NUM_STATES):
        ax.bar(np.arange(len(DAYS)), sm['occ'][:, k], bottom=bottom,
               color=state_colors[k % len(state_colors)], label=f'state {k}')
        bottom += sm['occ'][:, k]
    ax.set_xticks(np.arange(len(DAYS)))
    ax.set_xticklabels(day_stats['day_num'].astype(str), fontsize=8)
    ax.set_xlabel('task day'); ax.set_ylabel('state occupancy'); ax.set_ylim(0, 1)
    ax.set_title(f'{ttl}  (within-day switches: {sm["switches"].sum()})')
    ax.legend(fontsize=7, ncol=NUM_STATES); ax.grid(axis='y', alpha=.3)

axes[2].bar(np.arange(len(DAYS)), sm_dyn['switches'], color='#9467bd')
axes[2].set_xticks(np.arange(len(DAYS)))
axes[2].set_xticklabels(day_stats['day_num'].astype(str), fontsize=8)
axes[2].set_xlabel('task day'); axes[2].set_ylabel('# switches')
axes[2].set_title('Dynamic: within-day state switches')
axes[2].grid(axis='y', alpha=.3)
plt.tight_layout(); plt.show()
''')

# ---------------------------------------------------------------------------
# Cell 50: balancing → bars + heatmap
# ---------------------------------------------------------------------------
set_source(50, r'''def balancing_table(sm, label):
    z_all = np.concatenate(sm['z'])
    keep = sm['pmax'] >= P_THRESHOLD
    t2 = tr.copy()
    t2['state_dyn'] = z_all
    t2['p_max_dyn'] = sm['pmax']
    kept2 = t2[keep]
    rows = []
    for d in DAYS:
        g = kept2[kept2['task_day'] == d]
        ct = pd.crosstab(g['trial_type'], g['state_dyn'])
        ct = ct.reindex(index=SOUND_TYPES, columns=range(NUM_STATES), fill_value=0)
        usable = int((ct.min(axis=1) * NUM_STATES).sum())
        rows.append({'task_day': d, 'n_kept': len(g), 'min_cell': int(ct.values.min()),
                     'usable_balanced': usable})
    bt = pd.DataFrame(rows)
    print(f'[{label}] 残存率 {keep.mean():.3f}')
    print(f'  balanced 使用可能試行: 中央値 {bt["usable_balanced"].median():.0f} / '
          f'全day計 {bt["usable_balanced"].sum()} / min_cell=0 のday {int((bt["min_cell"] == 0).sum())}/{len(bt)}')
    return bt, t2, keep

bal_dyn, tr_dyn, keep_dyn = balancing_table(sm_dyn, f'dynamic (alpha={ALPHA_BEST}, kappa={KAPPA_BEST})')
ct_dyn = pd.crosstab(tr_dyn.loc[keep_dyn, 'state_dyn'],
                     tr_dyn.loc[keep_dyn, 'trial_type']).reindex(
    index=range(NUM_STATES), columns=SOUND_TYPES).fillna(0)

fig, axes = plt.subplots(1, 2, figsize=(12, 3.6))
x = np.arange(len(DAYS))
axes[0].bar(x, bal_dyn['n_kept'], color='#c7c7c7', label='kept (P≥threshold)')
axes[0].bar(x, bal_dyn['usable_balanced'], color='#d62728', label='usable after balancing')
axes[0].set_xticks(x); axes[0].set_xticklabels(day_stats['day_num'].astype(str), fontsize=8)
axes[0].set_xlabel('task day'); axes[0].set_ylabel('trials')
axes[0].set_title('Dynamic fit: cortical-decoding trial budget')
axes[0].legend(fontsize=8); axes[0].grid(axis='y', alpha=.3)

im = axes[1].imshow(ct_dyn.to_numpy(), aspect='auto', cmap='Purples')
axes[1].set_xticks(range(len(SOUND_TYPES))); axes[1].set_xticklabels(SOUND_TYPES, fontsize=8)
axes[1].set_yticks(range(NUM_STATES)); axes[1].set_yticklabels([f'state {k}' for k in range(NUM_STATES)])
axes[1].set_title('Dynamic kept: state × trial type')
for i in range(NUM_STATES):
    for j in range(len(SOUND_TYPES)):
        axes[1].text(j, i, int(ct_dyn.iloc[i, j]), ha='center', va='center', fontsize=9,
                     color='white' if ct_dyn.iloc[i, j] > ct_dyn.to_numpy().max() / 2 else 'black')
plt.colorbar(im, ax=axes[1], fraction=0.046, pad=0.04)
plt.tight_layout(); plt.show()
''')

# ---------------------------------------------------------------------------
# Cell 48: add pi comparison bar chart
# ---------------------------------------------------------------------------
set_source(48, r'''# 感度確認: 初期状態分布を一様に固定（Cuturela式）した場合
par_u = fit_dyn_glmhmm(ys_dyn, xs_dyn, K=NUM_STATES, C=2, model_type='partial',
                       alpha_w=ALPHA_BEST, sigma0=PRIOR_SIGMA, fit_pi=False,
                       W_init=W_SSM, P_init=P_SSM, seed=0)
dyn_u = fit_dyn_glmhmm(ys_dyn, xs_dyn, K=NUM_STATES, C=2, model_type='dynamic',
                       alpha_w=ALPHA_BEST, kappa=KAPPA_BEST, sigma0=PRIOR_SIGMA, fit_pi=False,
                       W_init=par_u['W'], P_init=par_u['P'], A_global=par_u['A'], seed=0)
sm_par_u = state_summary(par_u, 'partial（一様pi固定、Cuturela式）')
sm_dyn_u = state_summary(dyn_u, 'dynamic（一様pi固定、Cuturela式）')

ll_cmp = pd.DataFrame([
    {'model': 'partial', 'fit_pi': par_fit['lls'][-1], 'uniform_pi': par_u['lls'][-1]},
    {'model': 'dynamic', 'fit_pi': dyn_fit['lls'][-1], 'uniform_pi': dyn_u['lls'][-1]},
])
print('pi の扱いによる data log-likelihood の差:')
print(f'  partial: 推定pi {par_fit["lls"][-1]:.2f} vs 一様pi {par_u["lls"][-1]:.2f}  '
      f'(Δ={par_fit["lls"][-1] - par_u["lls"][-1]:+.2f})')
print(f'  dynamic: 推定pi {dyn_fit["lls"][-1]:.2f} vs 一様pi {dyn_u["lls"][-1]:.2f}  '
      f'(Δ={dyn_fit["lls"][-1] - dyn_u["lls"][-1]:+.2f})')

fig, ax = plt.subplots(figsize=(5.5, 3.4))
x = np.arange(len(ll_cmp))
ax.bar(x - .15, ll_cmp['fit_pi'], width=.3, label='estimated π (ssm-style)', color='#1f77b4')
ax.bar(x + .15, ll_cmp['uniform_pi'], width=.3, label='uniform π (Cuturela)', color='#ff7f0e')
ax.set_xticks(x); ax.set_xticklabels(ll_cmp['model'])
ax.set_ylabel('data log-likelihood'); ax.set_title('Effect of initial-state prior π')
ax.legend(fontsize=8); ax.grid(axis='y', alpha=.3)
for i, row in ll_cmp.iterrows():
    ax.annotate(f'Δ={row["fit_pi"]-row["uniform_pi"]:+.1f}',
                (i, max(row['fit_pi'], row['uniform_pi'])),
                textcoords='offset points', xytext=(0, 6), ha='center', fontsize=8)
plt.tight_layout(); plt.show()
''')

# Ensure state_colors exists early (cell 3 imports)
src3 = "".join(nb["cells"][3]["source"])
if "state_colors" not in src3:
    src3 = src3.rstrip() + "\n\nstate_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']\n"
    set_source(3, src3)

NB.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
print("updated", NB)
print("modified cells:", sorted({8, 9, 10, 11, 13, 14, 16, 18, 20, 22, 25, 26, 27, 28, 32, 36, 37, 47, 48, 50, 3}))
