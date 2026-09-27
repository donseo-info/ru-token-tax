"""Обложка статьи 1600×900: python cover.py → charts/00-cover.png"""
import os, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import tiktoken
from tokenizers import Tokenizer

HERE = os.path.dirname(os.path.abspath(__file__))
BG, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#898781"
ORANGE, TINTS = "#eb6834", ["#cde2fb", "#9ec5f4"]
plt.rcParams["font.family"] = "Helvetica"

phrase = "Кэширование промптов"
cl = tiktoken.get_encoding("cl100k_base"); o2 = tiktoken.get_encoding("o200k_base")
giga = Tokenizer.from_file(os.path.join(HERE, "tokenizers", "ai-sage_GigaChat3-10B-A1.8B__tokenizer.json"))
rows = [("GPT-4", [cl.decode_single_token_bytes(i).decode("utf-8", "replace") for i in cl.encode(phrase)]),
        ("GPT-5", [o2.decode_single_token_bytes(i).decode("utf-8", "replace") for i in o2.encode(phrase)]),
        ("GigaChat", [phrase[a:b] for a, b in giga.encode(phrase, add_special_tokens=False).offsets])]

fig = plt.figure(figsize=(16, 9), dpi=100); fig.patch.set_facecolor(BG)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 16); ax.set_ylim(0, 9); ax.axis("off")
ax.text(0.9, 7.6, "Сколько стоит русский текст", fontsize=46, fontweight="bold", color=INK, va="center")
ax.text(0.9, 6.75, "в токенах разных моделей — замер 11 токенизаторов", fontsize=30, color=INK2, va="center")
ax.text(0.9, 4.1, "×3,9", fontsize=150, fontweight="bold", color=ORANGE, va="center")
ax.text(0.95, 2.35, "столько токенов Claude Opus 5 тратит\nна русский текст по сравнению с GPT-5.5", fontsize=24, color=INK, va="center", linespacing=1.4)
x0 = 8.4
for r, (name, toks) in enumerate(rows):
    y = 5.2 - r * 1.25
    ax.text(x0, y + 0.55, f"{name} · {len(toks)} токенов", fontsize=20, color=INK2, va="center")
    x = x0
    for i, t in enumerate(toks):
        s = t.replace(" ", "·") if t.strip() else "·"
        w = 0.24 * len(s) + 0.16
        ax.add_patch(FancyBboxPatch((x, y - 0.3), w, 0.6, boxstyle="round,pad=0.01,rounding_size=0.08", fc=TINTS[i % 2], ec=BG, lw=3))
        ax.text(x + w / 2, y, s, ha="center", va="center", fontsize=24, color=INK)
        x += w + 0.05
ax.text(0.9, 0.55, "github.com/donseo-info/ru-token-tax", fontsize=16, color=MUTED, va="center")
fig.savefig(os.path.join(HERE, "charts", "00-cover.png"), facecolor=BG); print("charts/00-cover.png")
