"""Train the FINAL tokenizer from the winning config and export everything the
widget needs: vocab, merges (as pairs, so JS can recover split points), the
cleaned India-page texts, and stats under BOTH word-count conventions."""
import os, re, json, datetime, bpe
HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, "data")

# --- winning configuration (from search_balance.py) ---
FOURTH = "kn"
WEIGHTS = {"en": 11, "hi": 2, "te": 7, "kn": 10}
LANG_META = {
    "en": ("English", "Aa", "Latin"),
    "hi": ("Hindi", "अ", "Devanagari"),
    "te": ("Telugu", "అ", "Telugu"),
    "kn": ("Kannada", "ಅ", "Kannada"),
    "ta": ("Tamil", "அ", "Tamil"),
    "bn": ("Bengali", "অ", "Bengali"),
}
langs = ["en", "hi", "te", FOURTH]

def load(l):
    with open(os.path.join(DATA, f"india_{l}.txt"), encoding="utf-8") as f:
        return bpe.clean(f.read())

texts = {l: load(l) for l in langs}

print("training final tokenizer...")
merges, vocab = bpe.train([(texts[l], WEIGHTS[l]) for l in langs], 10000, verbose=False)
ranks = bpe.build_ranks(merges)
print(f"  {len(vocab)} tokens, {len(merges)} merges")

naive = re.compile(r"\w+")
cache = {}
stats = {}
for l in langs:
    toks = len(bpe.encode(texts[l], ranks, cache))
    wA = bpe.word_count(texts[l])
    wB = len(naive.findall(texts[l]))
    stats[l] = {"tokens": toks, "wordsA": wA, "wordsB": wB,
                "fertA": toks / wA, "fertB": toks / wB}

def score(key):
    xs = sorted(stats[l][key] for l in langs)
    gap = xs[-1] - xs[0]
    return (1000 / gap) if gap else 0.0, gap
scoreA, gapA = score("fertA")
scoreB, gapB = score("fertB")

# sanity: no UNK possible (byte-level) — assert every byte value is a base token
assert len({vocab[i] for i in range(256)}) == 256, "base byte vocab incomplete!"

data = {
    "meta": {
        "vocab_size": len(vocab),
        "n_merges": len(merges),
        "fourth": FOURTH,
        "weights": WEIGHTS,
        "scoreA": scoreA, "gapA": gapA,
        "scoreB": scoreB, "gapB": gapB,
        "generated": datetime.date.today().isoformat(),
        "source": "Wikipedia 'India' article (en, hi, te, kn), cleaned (whitespace collapsed)",
    },
    "langs": [{"code": l, "name": LANG_META[l][0], "badge": LANG_META[l][1],
               "script": LANG_META[l][2], "weight": WEIGHTS[l]} for l in langs],
    "vocab": vocab,
    "merges": [[a, b] for (a, b) in merges],
    "stats": stats,
    "texts": texts,
    # educational: fertility/score vs vocab size (submitted tokenizer stays 10k)
    "sweep": json.load(open(os.path.join(HERE, "vocab_sweep.json"), encoding="utf-8")),
}
out = os.path.join(HERE, "tokenizer_data.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False)
print(f"wrote {out}  ({os.path.getsize(out):,} bytes)")

# public tokenizer.json (vocab + merges + meta) -> assignment/ so Netlify serves a
# direct, public download link. `decoded` maps each byte-token back to readable text.
ASSIGN = os.path.abspath(os.path.join(HERE, "..", "..", "assignment"))
BDEC = {c: b for b, c in bpe.BYTE_ENCODER.items()}
def decode_tok(t):
    return bytes(BDEC[ch] for ch in t).decode("utf-8", "replace")
pub = {
    "meta": data["meta"],
    "note": "Byte-level BPE. vocab[i] is the token string in GPT-2 byte-char encoding; "
            "decoded[i] is its readable form. merges are applied in order.",
    "vocab": vocab,
    "decoded": [decode_tok(t) for t in vocab],
    "merges": [[a, b] for (a, b) in merges],
}
pubpath = os.path.join(ASSIGN, "tokenizer.json")
with open(pubpath, "w", encoding="utf-8") as f:
    json.dump(pub, f, ensure_ascii=False)
print(f"wrote {pubpath}  ({os.path.getsize(pubpath):,} bytes)")

print(f"\n{'lang':<9}{'tokens':>8}{'wordsA':>8}{'fertA':>8}{'wordsB':>8}{'fertB':>8}")
for l in langs:
    s = stats[l]
    print(f"{LANG_META[l][0]:<9}{s['tokens']:>8,}{s['wordsA']:>8,}{s['fertA']:>8.3f}"
          f"{s['wordsB']:>8,}{s['fertB']:>8.3f}")
print(f"\nEnglish < 1.2 (akshara): {stats['en']['fertA']:.4f}  "
      f"{'OK' if stats['en']['fertA'] < 1.2 else 'FAIL'}")
print(f"score A (akshara, honest) = {scoreA:,.0f}   gap={gapA:.4f}")
print(f"score B (naive \\w+)       = {scoreB:,.0f}   gap={gapB:.4f}")
