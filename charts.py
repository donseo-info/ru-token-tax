"""Графики для статьи из results.json: python charts.py → charts/*.png"""
import json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "results.json")))
C = R["chars"]
PROSE = ["tech", "chat", "official"]

SURFACE, INK, INK2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
RU, EN = "#2a78d6", "#eb6834"          # проверено validate_palette.js: CVD ΔE 24.7, normal 33.6
plt.rcParams.update({"font.family": "Helvetica", "font.size": 13, "axes.edgecolor": AXIS, "axes.labelcolor": INK2,
                     "xtick.color": MUTED, "ytick.color": INK2, "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
                     "savefig.facecolor": SURFACE, "axes.spines.top": False, "axes.spines.right": False})


def cpt(d, lang):
    return sum(C[f"{g}.{lang}"] for g in PROSE) / sum(d[f"{g}.{lang}"] for g in PROSE)


SRC = {
    "YandexGPT 5 Lite": R["local"]["YandexGPT 5 Lite"],
    "GigaChat 3": R["local"]["GigaChat 3"],
    "Grok 4.7": R["api"]["grok-4.7"],
    "GPT-5.x / GPT-6 (o200k)": R["local"]["OpenAI o200k (GPT-4o…GPT-6)"],
    "Gemini 3.7 Flash": R["api"]["gemini-3.7-flash"],
    "GLM-5.3": R["api"]["glm-5.3"],
    "DeepSeek V3 / V4": R["local"]["DeepSeek V3"],
    "Qwen 3": R["local"]["Qwen 3"],
    "Kimi K3": R["api"]["kimi-k3"],
    "GPT-4 (cl100k)": R["local"]["OpenAI cl100k (GPT-4, 3.5)"],
    "Claude Opus 5": R["api"]["claude-opus-5"],
}


def chart_cpt():
    names = list(SRC)[::-1]
    ru = [cpt(SRC[n], "ru") for n in names]; en = [cpt(SRC[n], "en") for n in names]
    fig, ax = plt.subplots(figsize=(10, 6.4), dpi=160)
    y = range(len(names))
    for i in y:
        ax.plot([ru[i], en[i]], [i, i], color=GRID, lw=2, zorder=1)
    ax.scatter(en, y, s=90, color=EN, zorder=3, edgecolor=SURFACE, linewidth=2, label="английский")
    ax.scatter(ru, y, s=90, color=RU, zorder=4, edgecolor=SURFACE, linewidth=2, label="русский")
    for i in y:
        ax.text(ru[i] - 0.12 if ru[i] < en[i] else ru[i] + 0.12, i, f"{ru[i]:.2f}".replace(".", ","), va="center",
                ha="right" if ru[i] < en[i] else "left", color=INK, fontsize=12, fontweight="bold")
    ax.set_yticks(list(y)); ax.set_yticklabels(names)
    ax.set_xlim(0, 5.8); ax.set_xlabel("символов текста на один токен (больше — дешевле)")
    ax.xaxis.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True); ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.legend(loc="lower right", frameon=False, fontsize=12, labelcolor=INK2)
    fig.suptitle("Сколько текста помещается в один токен", x=0.02, ha="left", fontsize=17, fontweight="bold", color=INK)
    ax.set_title("Одни и те же тексты на русском и в английском переводе, 11 токенизаторов", loc="left", color=INK2, fontsize=12, pad=10)
    fig.text(0.02, 0.01, "Замер 27.09.2026 · корпус и скрипт: github.com/donseo-info/ru-token-tax", color=MUTED, fontsize=10)
    fig.tight_layout(rect=(0, 0.03, 1, 0.97)); fig.savefig(os.path.join(HERE, "charts", "01-chars-per-token.png")); plt.close(fig)


# цена за 1M входных токенов (медианы по агрегаторам РФ, 27.09.2026) и токенизатор для пересчёта
PRICES = [("GPT-5.5", 552, "GPT-5.x / GPT-6 (o200k)"), ("Claude Opus 5", 549.31, "Claude Opus 5"),
          ("GigaChat 2 Max", 1245.9, "GigaChat 3"), ("Kimi K3", 285, "Kimi K3"),
          ("YandexGPT 5 Lite", 270, "YandexGPT 5 Lite"), ("DeepSeek V4 Pro", 149.46, "DeepSeek V3 / V4")]


def chart_price():
    base_tok = PRICES[0][1]; base_chr = PRICES[0][1] / cpt(SRC[PRICES[0][2]], "ru")
    fig, ax = plt.subplots(figsize=(10, 6.4), dpi=160)
    num = lambda v: f"{v:.2f}×".replace(".", ",")
    # подписи слева: одинаковые/близкие значения сдвигаем, чтобы не налезали (сдвиг в долях лог-шкалы)
    left_nudge = {"Claude Opus 5": None, "Kimi K3": 1.07, "YandexGPT 5 Lite": 0.94}
    for name, p, tok in PRICES:
        a, b = p / base_tok, (p / cpt(SRC[tok], "ru")) / base_chr
        hi = name == "Claude Opus 5"
        col = EN if hi else (INK if name == "GPT-5.5" else RU)
        ax.plot([0, 1], [a, b], color=col, lw=3 if hi else 2, zorder=3 if hi else 2, marker="o", ms=8, mec=SURFACE, mew=2)
        if name == "GPT-5.5":
            ax.text(-0.04, a, f"GPT-5.5 и Claude Opus 5  {num(a)}", ha="right", va="center", color=INK, fontsize=12)
        elif left_nudge.get(name, 1) is not None:
            ax.text(-0.04, a * left_nudge.get(name, 1), f"{name}  {num(a)}", ha="right", va="center", color=INK, fontsize=12)
        ax.text(1.04, b, f"{num(b)}  {name}", ha="left", va="center", color=INK, fontsize=12,
                fontweight="bold" if hi else "normal")
    ax.set_yscale("log"); ax.set_xlim(-0.95, 1.75); ax.set_ylim(0.2, 5)
    ax.set_xticks([0, 1]); ax.set_xticklabels(["по прайсу:\nцена за 1M токенов", "на деле:\nцена за 1 000 символов русского текста"], fontsize=12, color=INK2)
    ax.set_yticks([]); ax.minorticks_off(); ax.spines["left"].set_visible(False); ax.spines["bottom"].set_visible(False)
    ax.tick_params(axis="x", length=0)
    fig.suptitle("Прайс и реальная цена русского текста", x=0.02, ha="left", fontsize=17, fontweight="bold", color=INK)
    ax.set_title("Во сколько раз дороже GPT-5.5 (= 1×), логарифмическая шкала", loc="left", color=INK2, fontsize=12, pad=10)
    fig.text(0.02, 0.01, "Цены: медианы входной цены по российским агрегаторам, 27.09.2026 · github.com/donseo-info/ru-token-tax", color=MUTED, fontsize=10)
    fig.tight_layout(rect=(0, 0.03, 1, 0.97)); fig.savefig(os.path.join(HERE, "charts", "02-price-vs-real.png")); plt.close(fig)


def chart_split():
    import tiktoken
    from tokenizers import Tokenizer
    import sentencepiece as spm
    phrase = "Кэширование промптов снижает стоимость запросов"
    tk = os.path.join(HERE, "tokenizers")
    def hf(fn):
        t = Tokenizer.from_file(os.path.join(tk, fn))
        return lambda s: [s[a:b] for a, b in t.encode(s, add_special_tokens=False).offsets]
    def tik(name):
        e = tiktoken.get_encoding(name)
        return lambda s: [e.decode_single_token_bytes(i).decode("utf-8", "replace") for i in e.encode(s)]
    sp = spm.SentencePieceProcessor(model_file=os.path.join(tk, "yandex_YandexGPT-5-Lite-8B-instruct__tokenizer.model"))
    rows = [("GPT-4 (cl100k)", tik("cl100k_base")), ("DeepSeek V3 / V4", hf("deepseek-ai_DeepSeek-V3__tokenizer.json")),
            ("GPT-5.x / GPT-6 (o200k)", tik("o200k_base")), ("GigaChat 3", hf("ai-sage_GigaChat3-10B-A1.8B__tokenizer.json")),
            ("YandexGPT 5 Lite", lambda s: [p.replace("▁", " ") for p in sp.encode(s, out_type=str)])]
    fig, ax = plt.subplots(figsize=(12, 5.2), dpi=160); ax.axis("off")
    fills = ["#cde2fb", "#9ec5f4"]
    fp = font_manager.FontProperties(family="Helvetica", size=14)
    for r, (name, fn) in enumerate(rows):
        y = len(rows) - r
        toks = fn(phrase)
        ax.text(0, y, name, ha="left", va="center", fontsize=12, color=INK2)
        ax.text(0, y - 0.32, f"{len(toks)} токенов", ha="left", va="center", fontsize=12, color=INK, fontweight="bold")
        x = 2.55
        for i, t in enumerate(toks):
            shown = t.replace(" ", "·") if t.strip() else "·"
            if "�" in shown: shown = "•"          # байтовый кусок буквы (UTF-8 разрезан посередине)
            w = max(0.18, 0.117 * len(shown))
            ax.add_patch(matplotlib.patches.FancyBboxPatch((x, y - 0.3), w, 0.6, boxstyle="round,pad=0.01,rounding_size=0.06",
                                                           fc=fills[i % 2], ec=SURFACE, lw=2))
            ax.text(x + w / 2, y, shown, ha="center", va="center", fontproperties=fp, color=INK)
            x += w + 0.03
    ax.set_xlim(0, 10.5); ax.set_ylim(0.3, len(rows) + 0.7)
    fig.suptitle("Как модели режут одну русскую фразу", x=0.02, ha="left", fontsize=17, fontweight="bold", color=INK)
    fig.text(0.02, 0.9, "Цвета чередуются по токенам, «·» — пробел в начале токена", color=INK2, fontsize=12)
    fig.text(0.02, 0.02, "Открытые токенизаторы; у Claude токенизатор закрыт · github.com/donseo-info/ru-token-tax", color=MUTED, fontsize=10)
    fig.tight_layout(rect=(0, 0.04, 1, 0.9)); fig.savefig(os.path.join(HERE, "charts", "03-split.png")); plt.close(fig)


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "charts"), exist_ok=True)
    chart_cpt(); chart_price(); chart_split()
    print("charts/: 01-chars-per-token.png, 02-price-vs-real.png, 03-split.png")
