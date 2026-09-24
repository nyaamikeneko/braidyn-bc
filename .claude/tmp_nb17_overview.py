# -*- coding: utf-8 -*-
import json
from pathlib import Path

nb = json.loads(Path("notebooks/17_ver5_pre_implementation_checks.ipynb").read_text(encoding="utf-8"))
parts = []
for i in [10, 14, 28, 42, 47, 50, 52, 54]:
    c = nb["cells"][i]
    parts.append("=" * 70)
    parts.append(f"CELL {i}")
    parts.append("".join(c["source"]))
    parts.append("")
Path(".claude/tmp_nb17_plot_cells.txt").write_text("\n".join(parts), encoding="utf-8")
print("ok")
