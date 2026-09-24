from pathlib import Path

root = Path("external/dynamic_glmhmm/code")
needles = [
    "def fit_eval_CV_dynamic_model",
    "def fit(",
    "model_type == 'dynamic'",
    "model_type=='dynamic'",
    "row sum",
    "np.sum",
    "alpha",
    "priorDirP",
]
files = [
    root / "dynamic_glmhmm.py",
    root / "fit_cluster_dynamicGLMHMM.py",
    root / "analysis_utils.py",
    root / "utils.py",
]
out = []
for f in files:
    lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
    out.append(f"\n##### {f.name} {len(lines)} lines")
    for i, line in enumerate(lines, 1):
        if line.startswith("def ") or line.startswith("class "):
            out.append(f"{i}: {line}")
Path(".claude/tmp_dyn_defs.txt").write_text("\n".join(out), encoding="utf-8")
print("ok")
