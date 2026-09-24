import json

p = r"c:\Users\dmasu\braidyn-bc\notebooks\18_ver5_dynglmhmm_authors_impl.ipynb"
nb = json.load(open(p, encoding="utf-8"))
out = []
out.append(f"ncells {len(nb['cells'])}")
for i, c in enumerate(nb["cells"]):
    src = "".join(c["source"])
    first = src.strip().split("\n")[0][:140] if src.strip() else "(empty)"
    out.append(f"--- {i} {c['cell_type']} {len(src)} chars | {first}")
open(r"c:\Users\dmasu\braidyn-bc\.claude\tmp_nb18_outline.txt", "w", encoding="utf-8").write("\n".join(out))
