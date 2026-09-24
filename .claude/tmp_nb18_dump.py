import json

p = r"c:\Users\dmasu\braidyn-bc\notebooks\18_ver5_dynglmhmm_authors_impl.ipynb"
nb = json.load(open(p, encoding="utf-8"))
want = [0, 1, 2, 3, 4, 5, 6, 9, 10, 11, 12, 13, 14, 18, 19, 20]
out = []
for i in want:
    src = "".join(nb["cells"][i]["source"])
    out.append(f"\n{'='*20} CELL {i} {nb['cells'][i]['cell_type']} {'='*20}\n")
    out.append(src)
open(r"c:\Users\dmasu\braidyn-bc\.claude\tmp_nb18_src.txt", "w", encoding="utf-8").write("\n".join(out))
print("wrote", len(out))
