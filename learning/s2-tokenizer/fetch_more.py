"""Fetch extra training text per language: a batch of random Wikipedia articles.
This is legit ("build tokenizer using anything") and, for agglutinative Indic
languages, teaches the vocab general morphemes that then tokenize unseen
India-page words efficiently. We still EVALUATE only on the India page."""
import json, os, time, urllib.parse, urllib.request

LANGS = ["en", "hi", "te", "kn", "ta", "bn"]
OUT = os.path.join(os.path.dirname(__file__), "data")
UA = "ERA-V5-Tokenizer-Assignment/1.0 (learning project; csanjaykumar17@gmail.com)"
TARGET_CHARS = 400_000   # aim for ~400k chars of extra text per language

def api(lang, params):
    url = f"https://{lang}.wikipedia.org/w/api.php?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.load(r)

for lang in LANGS:
    chunks, total, tries = [], 0, 0
    while total < TARGET_CHARS and tries < 40:
        tries += 1
        try:
            data = api(lang, {
                "action": "query", "format": "json", "formatversion": "2",
                "generator": "random", "grnnamespace": "0", "grnlimit": "12",
                "prop": "extracts", "explaintext": "1", "exlimit": "max",
            })
            for p in data.get("query", {}).get("pages", []):
                ex = p.get("extract", "")
                if len(ex) > 400:            # skip stubs
                    chunks.append(ex); total += len(ex)
        except Exception as e:
            print(f"{lang}: try {tries} failed {e}")
        time.sleep(0.3)
    path = os.path.join(OUT, f"extra_{lang}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(chunks))
    print(f"{lang}: {total:,} chars from {len(chunks)} articles -> {path}")
