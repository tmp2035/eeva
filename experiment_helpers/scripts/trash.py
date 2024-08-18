# resraw experiments
path = Path("../run_results/")
paths = [ p for p in path.rglob("") if p.parts[-1].startswith("scan")][1:]
for p in paths:
   print(p)
   os.system(f"python3 ./scripts/redraw.py {p}") 

# prepare for latex

from scripts import to_tex
path = Path("/runs/run_results/")
paths = [ p for p in path.rglob("") if p.parts[-1].startswith("zero")][:]
print(paths)
to_save = Path("../run_plots/")


to_tex.prepare_for_tex(paths, to_save)


# 
path = Path("/runs/run_results/")
paths = [ p for p in path.rglob("") if p.parts[-1].startswith("")][1:]
to_save = Path("../run_plots/")
parts = ["Barplot_image", "pair"]
to_tex.copy_reg_expression(paths, to_save, parts)