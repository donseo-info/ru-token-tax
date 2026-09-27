"""Сколько токенов стоит один и тот же текст на русском и английском в разных моделях.

  ./download_tokenizers.sh                       # один раз, открытые токенизаторы
  python measure.py                              # только локальные токенизаторы
  python measure.py --api models.json            # + закрытые модели через OpenAI-совместимые API

Локальные токенизаторы считаются напрямую. Закрытые модели — по разнице usage двух запросов:
  токены(текст) = usage(база + "\\n\\n" + текст) − usage(база)
так вычитаются шаблон чата и системные промты шлюзов. max_tokens=16, ответ не важен.

models.json — список {"model": "...", "base_url": "https://…/v1", "key_env": "ИМЯ_ПЕРЕМЕННОЙ_С_КЛЮЧОМ"}.
Результат: results.json и таблица в консоль. Корпус — corpus/corpus.json (можно заменить своим).
"""
import argparse, json, os, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
BASE_MSG = "Ответь одним словом: ок."


def local_tokenizers():
    import tiktoken
    from tokenizers import Tokenizer
    import sentencepiece as spm
    tk = os.path.join(HERE, "tokenizers")
    out = {
        "OpenAI o200k (GPT-4o…GPT-6)": lambda s, e=tiktoken.get_encoding("o200k_base"): len(e.encode(s)),
        "OpenAI cl100k (GPT-4, 3.5)": lambda s, e=tiktoken.get_encoding("cl100k_base"): len(e.encode(s)),
    }
    for name, f in [("GigaChat 3", "ai-sage_GigaChat3-10B-A1.8B__tokenizer.json"), ("DeepSeek V3", "deepseek-ai_DeepSeek-V3__tokenizer.json"),
                    ("Qwen 3", "Qwen_Qwen3-8B__tokenizer.json")]:
        p = os.path.join(tk, f)
        if os.path.exists(p):
            t = Tokenizer.from_file(p)
            out[name] = lambda s, t=t: len(t.encode(s, add_special_tokens=False).ids)
    p = os.path.join(tk, "yandex_YandexGPT-5-Lite-8B-instruct__tokenizer.model")
    if os.path.exists(p):
        sp = spm.SentencePieceProcessor(model_file=p)
        out["YandexGPT 5 Lite"] = lambda s, sp=sp: len(sp.encode(s))
    return out


def prompt_tokens(m, text):
    content = BASE_MSG if text is None else BASE_MSG + "\n\n" + text
    body = json.dumps({"model": m["model"], "max_tokens": 16, "temperature": 0,
                       "messages": [{"role": "user", "content": content}]}).encode()
    headers = {"Authorization": "Bearer " + os.environ[m["key_env"]], "Content-Type": "application/json"}
    err = ""
    for i in range(3):
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request(m["base_url"].rstrip("/") + "/chat/completions", body, headers), timeout=120))
            return r["usage"]["prompt_tokens"]
        except Exception as e:
            err = str(e)[:120]; time.sleep(2 + 3 * i)
    return "ERR " + err


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default=os.path.join(HERE, "corpus", "corpus.json"))
    ap.add_argument("--api", help="models.json с закрытыми моделями")
    ap.add_argument("--out", default=os.path.join(HERE, "results.json"))
    a = ap.parse_args()
    corpus = json.load(open(a.corpus))
    keys = [f"{g}.{lang}" for g in corpus for lang in ("ru", "en")]
    text = lambda k: corpus[k.split(".")[0]][k.split(".")[1]]
    res = {"chars": {k: len(text(k)) for k in keys}, "local": {}, "api": {}}
    for name, f in local_tokenizers().items():
        res["local"][name] = {k: f(text(k)) for k in keys}
    if a.api:
        models = json.load(open(a.api))
        jobs = [(m, None) for m in models] + [(m, k) for m in models for k in keys]
        with ThreadPoolExecutor(10) as ex:
            for (m, k), v in zip(jobs, ex.map(lambda j: prompt_tokens(j[0], None if j[1] is None else text(j[1])), jobs)):
                res["api"].setdefault(m["model"], {})[k or "_base"] = v
        for d in res["api"].values():
            b = d.pop("_base")
            for k, v in d.items():
                d[k] = v - b if isinstance(v, int) and isinstance(b, int) else v
    json.dump(res, open(a.out, "w"), ensure_ascii=False, indent=1)

    prose = [g for g in corpus if g != "code"]
    print(f"{'токенизатор / модель':<32}" + "".join(f"{g:>13}" for g in corpus) + f"{'RU/EN':>7}{'симв/ток RU':>12}{'EN':>6}")
    for n, d in list(res["local"].items()) + list(res["api"].items()):
        ok = all(isinstance(d.get(k), int) for k in keys)
        cells = "".join(f"{str(d[g + '.ru']) + '/' + str(d[g + '.en']) if ok else 'ERR':>13}" for g in corpus)
        if ok:
            ru = sum(d[g + ".ru"] for g in prose); en = sum(d[g + ".en"] for g in prose)
            cr = sum(res["chars"][g + ".ru"] for g in prose); ce = sum(res["chars"][g + ".en"] for g in prose)
            print(f"{n[:31]:<32}{cells}{ru / en:>7.2f}{cr / ru:>12.2f}{ce / en:>6.2f}")
        else:
            print(f"{n[:31]:<32}{cells}")


if __name__ == "__main__":
    sys.exit(main())
