def balancing_table(sm):
    t2 = tr.copy()
    t2['state'] = sm['z']
    t2['p_max'] = sm['pmax']
    kept = t2[t2['p_max'] >= P_THRESHOLD]
    rows = []
    for d in DAYS:
        g = kept[kept['task_day'] == d]
        ct = pd.crosstab(g['trial_type'], g['state'])
        ct = ct.reindex(index=SOUND_TYPES, columns=range(K), fill_value=0)
        rows.append({
            'task_day': d,
            'n_all': int((t2['task_day'] == d).sum()),
            'n_kept': len(g),
            'min_cell': int(ct.values.min()),
            'usable_balanced': int((ct.min(axis=1) * K).sum()),
        })
    return pd.DataFrame(rows)


bal = balancing_table(sm)
print(f'P(z)>={P_THRESHOLD} 残存率 {(sm["pmax"] >= P_THRESHOLD).mean():.3f}')
print(bal.to_string(index=False))
print(f'balanced 使用可能試行: 全 day 計 {int(bal["usable_balanced"].sum())} / '
      f'min_cell=0 の day {int((bal["min_cell"] == 0).sum())}/{len(bal)}')

fig, axes = plt.subplots(1, 2, figsize=(11.2, 3.8))
ax = axes[0]
ax.bar(range(len(DAYS)), bal['n_kept'], color='#4c72b0', label=f'P(z)≥{P_THRESHOLD}')
ax.plot(range(len(DAYS)), bal['n_all'], 'o--', color='#333333', ms=4, label='音提示試行')
ax.set_xticks(range(len(DAYS)))
ax.set_xticklabels(DAY_LABELS, fontsize=8)
ax.set_ylabel('試行数')
ax.set_title('確信度で残る試行')
ax.legend(frameon=False, fontsize=9)

ax = axes[1]
ax.bar(range(len(DAYS)), bal['usable_balanced'], color='#dd8452')
ax.set_xticks(range(len(DAYS)))
ax.set_xticklabels(DAY_LABELS, fontsize=8)
ax.set_ylabel('試行数')
ax.set_title('状態×試行タイプを釣り合わせたあと')
fig.tight_layout()
plt.show()