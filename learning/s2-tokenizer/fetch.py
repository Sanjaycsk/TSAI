"""
Fetch the "India" Wikipedia article as clean plain text, in several languages.

Why plain-text extracts (not raw HTML)?  The assignment says *cleaning the data
is part of the task*.  Wikipedia's `extracts` API with `explaintext=1` returns
the article body with all markup, tables, references and infoboxes stripped —
i.e. the human-readable prose.  That is exactly the "cleaned wiki article" the
instructor said they will evaluate on, so we train on the same kind of text.

We grab a few candidate 4th languages (Kannada, Tamil, Bengali) so we can pick
whichever one lets the tokenizer balance best across all four.
"""
import json, os, time, urllib.parse, urllib.request

# (lang code, that wiki's own title for the India article)
PAGES = {
    "en": "India",
    "hi": "भारत",
    "te": "భారతదేశం",
    "kn": "ಭಾರತ",
    "ta": "இந்தியா",
    "bn": "ভারত",
}

OUT = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(OUT, exist_ok=True)

# Wikipedia blocks requests without a descriptive User-Agent.
UA = "ERA-V5-Tokenizer-Assignment/1.0 (learning project; csanjaykumar17@gmail.com)"

def fetch(lang, title):
    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "explaintext": "1",       # give us plain text, no HTML
        "exsectionformat": "plain",
        "redirects": "1",         # follow "भारत" -> canonical page if needed
        "titles": title,
        "formatversion": "2",
    }
    url = f"https://{lang}.wikipedia.org/w/api.php?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.load(r)
    pages = data["query"]["pages"]
    extract = pages[0].get("extract", "")
    return extract

for lang, title in PAGES.items():
    try:
        text = fetch(lang, title)
        path = os.path.join(OUT, f"india_{lang}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        # crude word count (unicode word chars) just for a sanity read-out
        import re
        words = len(re.findall(r"\w+", text, flags=re.UNICODE))
        print(f"{lang}: {len(text):>8,} chars  {words:>7,} words  -> {path}")
    except Exception as e:
        print(f"{lang}: FAILED  {e}")
    time.sleep(0.5)
