from pathlib import Path
lines = Path("external/dynamic_glmhmm/code/dynamic_glmhmm.py").read_text(encoding="utf-8", errors="replace").splitlines()
keys = ["dynamic", "alpha", "row", "1e-3", "priorDirP", "model_type", "nan", "A_ij", "globalP"]
out = []
for i, line in enumerate(lines, 1):
    low = line.lower()
    if any(k.lower() in line for k in ["model_type", "alpha", "1e-3", "priorDirP", "global transition", "sum(axis", "np.allclose", "row"]):
        out.append(f"{i}: {line}")
Path(".claude/tmp_dyn_hits.txt").write_text("\n".join(out), encoding="utf-8")
print(len(out))
