from pathlib import Path

p = Path("supplement.tex")
lines = [l for l in p.read_text(encoding="utf-8").split("\n") if l != "usepackage[linguistics]{forest}"]
i = next(k for k, l in enumerate(lines) if l.startswith("\\documentclass"))
if not any(l.startswith("\\usepackage[linguistics]{forest}") for l in lines):
    lines.insert(i + 1, "\\usepackage[linguistics]{forest}")
p.write_text("\n".join(lines), encoding="utf-8")
print("documentclass at line", i + 1, "| forest lines:", sum("forest}" in l for l in lines))
