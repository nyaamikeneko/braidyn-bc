import json
from pathlib import Path
nb = json.loads(Path(r"notebooks/18_ver5_dynglmhmm_authors_impl.ipynb").read_text(encoding="utf-8"))
parts = []
for i in (21, 23, 27, 29, 32):
    parts.append(f"\n===== CELL {i} =====\n")
    parts.append("".join(nb["cells"][i]["source"]))
Path(".claude/tmp_nb18_plots.txt").write_text("\n".join(parts), encoding="utf-8")
print("ok")
