import json

p = r"c:\Users\dmasu\braidyn-bc\notebooks\18_ver5_dynglmhmm_authors_impl.ipynb"
nb = json.load(open(p, encoding="utf-8"))
print("ncells", len(nb["cells"]))
for i, c in enumerate(nb["cells"]):
    src = "".join(c["source"])
    first = src.strip().split("\n")[0][:140] if src.strip() else "(empty)"
    print(f"--- {i} {c['cell_type']} {len(src)} chars | {first}")
