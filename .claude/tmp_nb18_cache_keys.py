import pandas as pd

nb = pd.read_pickle('data/cache/ver5_note18.pkl')
for k, v in nb.items():
    if isinstance(v, dict):
        print(k, 'dict', {kk: type(vv).__name__ for kk, vv in v.items()})
    else:
        print(k, type(v).__name__, getattr(v, 'shape', ''))
