import json, os, zipfile, io
SP = os.path.dirname(os.path.abspath(__file__))
C = os.path.expanduser("~/.cache/dlm_dl/coco")
o = json.load(open(f"{SP}/l7_out.json"))
fl = [r for r in o["res"]["test"] if r["foil_cat_present"] and r["image_id"] not in (239537, 142790)]
zf = zipfile.ZipFile(f"{C}/val2017.zip")
from PIL import Image, ImageDraw
for n, r in enumerate(fl):
    print(n, r["image_id"], "|", r["c_pos"], "||", r["c_neg"], "|", r["target_word"], "->", r["foil_word"], "| cats", r["coco_cats"])
cols, W_, H_ = 4, 300, 225
for s in range(0, len(fl), 12):
    ch = fl[s:s + 12]
    rows = (len(ch) + cols - 1) // cols
    S = Image.new("RGB", (cols * W_, rows * H_), "white")
    for k, r in enumerate(ch):
        im = Image.open(io.BytesIO(zf.read(f"val2017/{r['image_id']:012d}.jpg"))).convert("RGB")
        im.thumbnail((W_, H_ - 16))
        S.paste(im, ((k % cols) * W_, (k // cols) * H_ + 16))
        ImageDraw.Draw(S).text(((k % cols) * W_ + 3, (k // cols) * H_ + 2), f"#{s + k} {r['image_id']}", fill="black")
    S.save(f"{SP}/flag{s // 12}.png")
