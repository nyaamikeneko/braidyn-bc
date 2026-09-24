import json
from pathlib import Path

p = Path(r"c:\Users\dmasu\braidyn-bc\notebooks\19_ver5_dynglmhmm_dynamic_kappa.ipynb")
nb = json.loads(p.read_text(encoding="utf-8"))
out = Path(r"c:\Users\dmasu\braidyn-bc\.claude\tmp_nb19_outline.txt")
lines_out = [f"n_cells {len(nb['cells'])}"]
for i, c in enumerate(nb["cells"]):
    src = "".join(c.get("source", []))
    lines = [ln for ln in src.strip().splitlines() if ln.strip()]
    head = lines[0][:180] if lines else "(empty)"
    n_out = len(c.get("outputs", []))
    lines_out.append(f"\n===== cell {i} {c['cell_type']} outs={n_out} =====")
    lines_out.append(head)
    if c["cell_type"] == "code":
        for o in c.get("outputs", []):
            if o.get("output_type") == "stream":
                text = "".join(o.get("text", []))
                lines_out.append("--- stdout ---")
                lines_out.append(text[:4000])
            elif o.get("output_type") in ("execute_result", "display_data"):
                data = o.get("data", {})
                if "text/plain" in data:
                    text = "".join(data["text/plain"])
                    if "Figure" in text or text.startswith("<"):
                        lines_out.append("--- display (skipped figure) ---")
                        lines_out.append(text[:200])
                    else:
                        lines_out.append("--- text/plain ---")
                        lines_out.append(text[:4000])
out.write_text("\n".join(lines_out), encoding="utf-8")
print("wrote", out)
