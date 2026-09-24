import sys, io, contextlib, time
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path('external/dynamic_glmhmm/code').resolve()))
import dynamic_glmhmm
from utils import reshapeSigma

nb = pd.read_pickle('data/cache/ver5_note18.pkl')
p, pi, w = nb['final_fixed']['par']
print('cached partial train LL', nb['final_fixed']['ll_par'])

tr_all = pd.read_pickle('data/cache/ver5_trials_VG1GC-66.pkl')
SOUND = ['Success', 'Short Pull', 'No Reaction']
out = []
for day, g in tr_all.groupby('task_day', sort=False):
    g = g[g['trial_type'].isin(SOUND)].sort_values('t_start').reset_index(drop=True).copy()
    a = (g['trial_type'] != 'No Reaction').astype(int).to_numpy()
    rw = (g['trial_type'] == 'Success').astype(int).to_numpy()
    n = len(g); h = np.zeros(n); r = np.zeros(n)
    for k in range(1, n):
        h[k] = a[k-1] + 0.65*h[k-1]; r[k] = rw[k-1] + 0.80*r[k-1]
    g['x_hist'] = h; g['x_rew'] = r; g['yA'] = 1 - a; g['k'] = np.arange(n)
    out.append(g)
t0 = pd.concat(out, ignore_index=True)
H0 = t0.loc[t0.k >= 20, 'x_hist'].mean(); R0 = t0.loc[t0.k >= 20, 'x_rew'].mean()
out = []
for day, g in tr_all.groupby('task_day', sort=False):
    g = g[g['trial_type'].isin(SOUND)].sort_values('t_start').reset_index(drop=True).copy()
    a = (g['trial_type'] != 'No Reaction').astype(int).to_numpy()
    rw = (g['trial_type'] == 'Success').astype(int).to_numpy()
    n = len(g); h = np.zeros(n); r = np.zeros(n); h[0], r[0] = H0, R0
    for k in range(1, n):
        h[k] = a[k-1] + 0.65*h[k-1]; r[k] = rw[k-1] + 0.80*r[k-1]
    g['x_bias'] = 1.0; g['x_hist'] = h; g['x_rew'] = r; g['yA'] = 1 - a
    out.append(g)
tr = pd.concat(out, ignore_index=True)
for c in ['x_hist', 'x_rew']:
    tr[c+'_z'] = (tr[c]-tr[c].mean())/tr[c].std(ddof=0)
days = list(dict.fromkeys(tr['task_day']))
x = tr[['x_bias', 'x_hist_z', 'x_rew_z']].to_numpy(float)
y = tr['yA'].to_numpy().astype(int)
sess = [0] + list(np.cumsum([int((tr.task_day == d).sum()) for d in days]))
N, D = x.shape; K = 3
m = dynamic_glmhmm.dynamic_GLMHMM(N, K, D, 2)
t = time.time()
with contextlib.redirect_stdout(io.StringIO()):
    p2, pi2, w2, ll = m.fit(x, y, np.ones(N), p, pi, w, sigma=reshapeSigma(1.0, K, D),
                            sessInd=sess, maxIter=100, tol=1e-3, L2penaltyW=0,
                            priorDirP=[10, 1], model_type='partial', fit_init_states=False)
ll = ll[ll != 0]
print(f'continued EM: {len(ll)} iters, {time.time()-t:.0f}s')
print('LL trace (first 5):', np.round(ll[:5], 3))
print('LL trace (last 3):', np.round(ll[-3:], 3), ' gain from cached:', round(ll[-1]-ll[0], 3))
print('max |dW|', np.abs(w2-w).max().round(3), ' max |dP|', np.abs(p2-p).max().round(4))
