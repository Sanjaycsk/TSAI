"""Fetch regional Wikipedia pages per language to enrich TRAINING (evaluation
stays on the India page). Idea: state / language pages share huge vocabulary
with the India page (place names, administrative + geographic terms, common
words), so their common morphemes get merged and cut fertility on the India page.
English is already at its floor (1.18), so we don't augment it."""
import json, os, time, urllib.parse, urllib.request

# per-language: that wiki's titles for states + the language's own page + history
PAGES = {
    "te": ["ఆంధ్రప్రదేశ్", "తెలంగాణ", "తెలుగు", "భారతదేశ చరిత్ర", "కర్ణాటక", "తమిళనాడు"],
    "kn": ["ಕರ್ನಾಟಕ", "ಕನ್ನಡ", "ಭಾರತದ ಇತಿಹಾಸ", "ಆಂಧ್ರ ಪ್ರದೇಶ", "ತಮಿಳುನಾಡು", "ಮಹಾರಾಷ್ಟ್ರ"],
    "hi": ["उत्तर प्रदेश", "राजस्थान", "बिहार", "मध्य प्रदेश", "महाराष्ट्र", "हिन्दी", "भारत का इतिहास"],
}
OUT = os.path.join(os.path.dirname(__file__), "data")
UA = "ERA-V5-Tokenizer-Assignment/1.0 (learning project; csanjaykumar17@gmail.com)"

def fetch(lang, title):
    params = {"action": "query", "format": "json", "formatversion": "2",
              "prop": "extracts", "explaintext": "1", "exsectionformat": "plain",
              "redirects": "1", "titles": title}
    url = f"https://{lang}.wikipedia.org/w/api.php?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.load(r)
    return data["query"]["pages"][0].get("extract", "")

for lang, titles in PAGES.items():
    parts, got = [], []
    for t in titles:
        try:
            ex = fetch(lang, t)
            if len(ex) > 300:
                parts.append(ex); got.append(f"{t}({len(ex)//1000}k)")
        except Exception as e:
            got.append(f"{t}:FAIL")
        time.sleep(0.3)
    path = os.path.join(OUT, f"regional_{lang}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(parts))
    print(f"{lang}: {sum(len(p) for p in parts):,} chars | {', '.join(got)}")
