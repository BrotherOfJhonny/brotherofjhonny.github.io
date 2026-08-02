#!/usr/bin/env python3
"""Miniatura do post sobre cadeia de suprimentos no npm.

Conceito: um terminal rodando `npm install`, com a linha do post-install
acesa em vermelho. É o momento exato em que o ataque acontece, e qualquer
pessoa que já usou npm reconhece a tela.

Arte 100% gerada aqui. Nenhum logotipo, captura de tela ou material de
terceiros.
"""
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = "/home/kali/Desktop/blog-src/assets/img/npm-supply-chain"
W, H = 1200, 630

BG = (10, 13, 19)
BG2 = (18, 23, 33)
TERM_BG = (22, 27, 38)
TERM_BAR = (32, 39, 52)
BORDER = (52, 64, 84)

WHITE = (233, 239, 247)
GREY = (138, 150, 168)
GREEN = (63, 210, 141)
BLUE = (88, 166, 255)
RED = (255, 74, 74)
AMBER = (255, 190, 60)

F_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
F_MONOB = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def build():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    for y in range(H):
        d.line([(0, y), (W, y)], fill=lerp(BG2, BG, y / H))

    # grade técnica discreta
    grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grid)
    for x in range(0, W, 44):
        gd.line([(x, 0), (x, H)], fill=BLUE + (14,))
    for y in range(0, H, 44):
        gd.line([(0, y), (W, y)], fill=BLUE + (14,))
    img = Image.alpha_composite(img.convert("RGBA"), grid).convert("RGB")
    d = ImageDraw.Draw(img)

    # ------------------------------------------------------------ título --
    d.rectangle([0, 0, 12, H], fill=RED)
    f_t = ImageFont.truetype(F_BOLD, 52)
    d.text((60, 56), "Você nunca instalou", font=f_t, fill=WHITE)
    d.text((60, 116), "esse pacote.", font=f_t, fill=RED)

    f_s = ImageFont.truetype(F_MONO, 24)
    d.text((62, 188), "mas ele roda na sua máquina", font=f_s, fill=GREY)

    # ---------------------------------------------------------- terminal --
    TX, TY, TW, TH = 60, 250, W - 120, 300

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        [TX + 6, TY + 10, TX + TW + 6, TY + TH + 10], radius=14, fill=(0, 0, 0, 170))
    img = Image.alpha_composite(img.convert("RGBA"),
                                shadow.filter(ImageFilter.GaussianBlur(18))).convert("RGB")
    d = ImageDraw.Draw(img)

    d.rounded_rectangle([TX, TY, TX + TW, TY + TH], radius=14,
                        fill=TERM_BG, outline=BORDER, width=2)
    d.rounded_rectangle([TX, TY, TX + TW, TY + 40], radius=14, fill=TERM_BAR)
    d.rectangle([TX, TY + 28, TX + TW, TY + 42], fill=TERM_BAR)
    for i, cor in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        cx = TX + 24 + i * 24
        d.ellipse([cx - 6, TY + 14, cx + 6, TY + 26], fill=cor)
    d.text((TX + 110, TY + 12), "bash", font=ImageFont.truetype(F_MONO, 16), fill=GREY)

    fm = ImageFont.truetype(F_MONO, 21)
    fmb = ImageFont.truetype(F_MONOB, 21)
    x, y, lh = TX + 26, TY + 62, 33

    d.text((x, y), "$", font=fmb, fill=GREEN)
    d.text((x + 22, y), "npm install", font=fmb, fill=WHITE)
    y += lh + 4

    d.text((x, y), "added 1247 packages in 12s", font=fm, fill=GREY); y += lh
    d.text((x, y), "42 packages are looking for funding", font=fm, fill=GREY); y += lh + 6

    # linha destacada: o momento do ataque
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle(
        [x - 12, y - 8, TX + TW - 26, y + 34], radius=8, fill=RED + (70,))
    img = Image.alpha_composite(img.convert("RGBA"),
                                glow.filter(ImageFilter.GaussianBlur(16))).convert("RGB")
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x - 12, y - 8, TX + TW - 26, y + 34], radius=8,
                        outline=RED, width=2)
    rotulo = "> postinstall:"
    d.text((x, y), rotulo, font=fmb, fill=RED)
    # Mede o rótulo em vez de fixar o deslocamento, senão os textos colam.
    d.text((x + d.textlength(rotulo, font=fmb) + 12, y),
           "node ./setup.js", font=fmb, fill=AMBER)
    y += lh + 12

    d.text((x, y), "# nenhum comando seu. nenhum aviso.", font=fm, fill=GREY)

    # --------------------------------------------------------- rodapé ----
    d.text((60, H - 46), "BrotherOfJhonny",
           font=ImageFont.truetype(F_BOLD, 22), fill=BLUE)
    t = "cadeia de suprimentos"
    fr = ImageFont.truetype(F_MONO, 19)
    d.text((W - 60 - d.textlength(t, font=fr), H - 44), t, font=fr, fill=GREY)

    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, "capa.png")
    img.save(p, "PNG", optimize=True)
    print(f"  capa  {p}  ({os.path.getsize(p)//1024} KB)")


if __name__ == "__main__":
    build()
