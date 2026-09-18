from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
from urllib.request import urlretrieve
import shutil, os

BASE = "https://cjqcyjuxsqtuybjqumlk.supabase.co/storage/v1/object/public/flower-workshop-uploads/"
ITEMS = [
    ("ทดสอบ", "submissions/1bbae870-34ba-44fb-8970-31338028dd56.jpg"),
    ("Blue rosy", "submissions/e1633d2e-90bd-480b-80ac-dba4c01c7368.jpg"),
    ("Lady Pink💕", "submissions/31d786a9-454a-45df-9675-09d2fc9fc9b5.jpg"),
    ("Good Evening", "submissions/00b31580-ed44-4c09-9a1c-e7cd4a5857bb.jpg"),
    ("With Love", "submissions/f24c7135-5937-402f-b7a1-6c93945a6187.jpg"),
    ("I miss my bloom by Nuri♡♡", "submissions/b7bcfce6-51bc-452b-8820-14f608f18e33.jpg"),
    ("Endless Joy", "submissions/d1ab48f6-4f9a-41d0-9f82-f0457798cba6.jpg"),
    ("Onora by orn", "submissions/862e3353-8af9-4fb7-a7bf-49da479add68.jpg"),
    ("เจ้ากุหลาบชมพู", "submissions/25218ae9-f454-4dc4-ba54-80853ce8c092.jpg"),
    ("Little Sunshine", "submissions/70f14c9a-2925-4860-98cd-59c1c424ef93.jpg"),
]

W, H = 1080, 1350
PHOTO = (72, 176, 1008, 1060)
OUT = Path("posters_png")
TMP = Path(".poster_src")
OUT.mkdir(exist_ok=True)
TMP.mkdir(exist_ok=True)

def find_font():
    candidates = [
        "/usr/share/fonts/truetype/noto/NotoSansThai-Regular.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansThai-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    raise FileNotFoundError("No suitable font found")

FONT = find_font()

def font(size):
    return ImageFont.truetype(FONT, size=size)

def fit(img, size, mode="contain"):
    tw, th = size
    iw, ih = img.size
    if mode == "cover":
        scale = max(tw/iw, th/ih)
    else:
        scale = min(tw/iw, th/ih)
    nw, nh = max(1, int(iw*scale)), max(1, int(ih*scale))
    return img.resize((nw, nh), Image.Resampling.LANCZOS)

def rounded_mask(size, radius):
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0,0,size[0],size[1]), radius=radius, fill=255)
    return mask

for idx, (name, path) in enumerate(ITEMS, 1):
    src = TMP / f"{idx:02d}.jpg"
    urlretrieve(BASE + path, src)
    original = Image.open(src).convert("RGB")

    canvas = Image.new("RGB", (W,H), "#F7F4EE")
    draw = ImageDraw.Draw(canvas)

    draw.text((72,66), "MAKE YOUR OWN GIFT BOUQUET", font=font(20), fill="#756F65")
    date_text = "18 SEP 2026"
    bbox = draw.textbbox((0,0), date_text, font=font(20))
    draw.text((1008-(bbox[2]-bbox[0]),66), date_text, font=font(20), fill="#A29B90")
    draw.line((72,116,1008,116), fill="#D8D1C6", width=1)

    x0,y0,x1,y1 = PHOTO
    pw, ph = x1-x0, y1-y0

    bg = fit(original, (pw,ph), "cover")
    bg = bg.filter(ImageFilter.GaussianBlur(28))
    bx = (bg.width-pw)//2
    by = (bg.height-ph)//2
    bg = bg.crop((bx,by,bx+pw,by+ph))
    veil = Image.new("RGB", (pw,ph), "#F7F4EE")
    bg = Image.blend(bg, veil, 0.18)

    photo = fit(original, (pw-40,ph-40), "contain")
    layer = bg.copy()
    px = (pw-photo.width)//2
    py = (ph-photo.height)//2
    layer.paste(photo, (px,py))
    mask = rounded_mask((pw,ph), 32)
    canvas.paste(layer, (x0,y0), mask)

    display_name = name.replace("💕", "♥")
    fs = 58
    while fs > 38:
        f = font(fs)
        bb = draw.textbbox((0,0), display_name, font=f)
        if bb[2]-bb[0] <= 936:
            break
        fs -= 2
    draw.text((72,1120), display_name, font=font(fs), fill="#2F2B26")
    draw.text((72,1203), "FLOWER ARRANGEMENT WORKSHOP · HEAD OFFICE", font=font(18), fill="#8D857A")
    draw.line((72,1272,865,1272), fill="#D8D1C6", width=1)
    count = f"{idx:02d} / {len(ITEMS):02d}"
    bb = draw.textbbox((0,0), count, font=font(16))
    draw.text((1008-(bb[2]-bb[0]),1260), count, font=font(16), fill="#8D857A")

    out = OUT / f"flower-workshop-2026-{idx:02d}.png"
    canvas.save(out, "PNG", optimize=True)

shutil.make_archive("flower-workshop-posters-png", "zip", OUT)
print("Rendered", len(ITEMS), "PNG posters")
