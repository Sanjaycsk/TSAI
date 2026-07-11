"""Export the feedback-BPE run for the live-slider widget.

Reads train20k.json (merges + per-merge per-language token deltas) and:
  1. VERIFIES the delta curves against the real encoder: encode() with the
     merge list truncated at V must reproduce T0 - cumsum(deltas) exactly,
     at several V. This is the proof that "slider at V" == "tokenizer
     trained to V" (BPE's prefix property), and that the widget's instant
     curve math equals what the instructor gets by actually encoding.
  2. Writes tokenizer_data.json for the widget (merges, deltas, texts,
     stats at the 10k submission point, key landmarks).
  3. Writes assignment/tokenizer.json = the SUBMITTED tokenizer, the
     V=10,000 prefix (identical to training to 10k directly).
"""
import os, re, json, datetime, bpe

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
ASSIGN = os.path.abspath(os.path.join(HERE, "..", "..", "assignment"))
SUBMIT_V = 10000
LANGS = ["en", "hi", "te", "kn"]
LANG_META = {
    "en": ("English", "Aa", "Latin"),
    "hi": ("Hindi", "अ", "Devanagari"),
    "te": ("Telugu", "అ", "Telugu"),
    "kn": ("Kannada", "ಅ", "Kannada"),
}

run = json.load(open(os.path.join(HERE, "train20k.json"), encoding="utf-8"))
merges = [tuple(m) for m in run["merges"]]
deltas, T0, W = run["deltas"], run["T0"], run["W"]
n_merges = len(merges)
VMAX = 256 + n_merges

texts = {}
for l in LANGS:
    with open(os.path.join(DATA, f"india_{l}.txt"), encoding="utf-8") as f:
        texts[l] = bpe.clean(f.read())

naive = re.compile(r"\w+")
WB = {l: len(naive.findall(texts[l])) for l in LANGS}
assert all(W[l] == bpe.word_count(texts[l]) for l in LANGS), "word counts drifted"

# --- token counts from the recorded curves ---
def curve_tokens(l, V):
    return T0[l] - sum(deltas[l][:V - 256])

# --- 1) parity: curves == real truncated encoder ---
ranks = bpe.build_ranks(merges)
print("verifying curve == real encode() at truncated V:")
for V in (2000, 6000, SUBMIT_V, 10276, 13000, 16000, VMAX):
    rv = {p: r for p, r in ranks.items() if r < V - 256}
    cache = {}
    for l in LANGS:
        enc = len(bpe.encode(texts[l], rv, cache))
        cur = curve_tokens(l, V)
        assert enc == cur, f"MISMATCH V={V} {l}: encode={enc} curve={cur}"
    print(f"  V={V:>6}  exact for all 4 languages")

# --- score curves + landmarks (strict akshara A and cohort-naive B) ---
def ferts(V, denom):
    return {l: curve_tokens(l, V) / denom[l] for l in LANGS}

def score(f):
    xs = sorted(f.values())
    return 1000 / (xs[-1] - xs[0]) if xs[-1] > xs[0] else 0.0

runT = dict(T0)
peakA = peakB = (0, 0)   # (score, V)
legalA = None
for i in range(n_merges):
    for l in LANGS:
        runT[l] -= deltas[l][i]
    V = 257 + i
    fA = {l: runT[l] / W[l] for l in LANGS}
    fB = {l: runT[l] / WB[l] for l in LANGS}
    sA, sB = score(fA), score(fB)
    if sA > peakA[0]: peakA = (sA, V)
    if sB > peakB[0]: peakB = (sB, V)
    if legalA is None and fA["en"] < 1.2 and all(fA[l] < 2.0 for l in LANGS[1:]):
        legalA = V

# --- stats at the submission point ---
stats = {}
for l in LANGS:
    t = curve_tokens(l, SUBMIT_V)
    stats[l] = {"tokens": t, "wordsA": W[l], "wordsB": WB[l],
                "fertA": t / W[l], "fertB": t / WB[l]}
scoreA10 = score({l: stats[l]["fertA"] for l in LANGS})
scoreB10 = score({l: stats[l]["fertB"] for l in LANGS})

meta = {
    "vocab_size": SUBMIT_V, "n_merges_total": n_merges, "vmax": VMAX,
    "trainer": "feedback-BPE (score-aware merge selection; en frozen at fert<=1.19)",
    "scoreA": scoreA10, "scoreB": scoreB10,
    "peakA": {"score": peakA[0], "V": peakA[1]},
    "peakB": {"score": peakB[0], "V": peakB[1]},
    "legalA_V": legalA,
    "urgency": run["urgency"], "freeze": run["freeze"],
    "generated": datetime.date.today().isoformat(),
    "source": "Wikipedia 'India' article (en, hi, te, kn), cleaned (whitespace collapsed)",
}
data = {
    "meta": meta,
    "langs": [{"code": l, "name": LANG_META[l][0], "badge": LANG_META[l][1],
               "script": LANG_META[l][2]} for l in LANGS],
    "merges": [[a, b] for a, b in merges],
    "deltas": deltas, "T0": T0, "W": W, "WB": WB,
    "order": run["order"],
    "stats": stats,
    "texts": texts,
}
out = os.path.join(HERE, "tokenizer_data.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False)
print(f"\nwrote {out}  ({os.path.getsize(out):,} bytes)")

# --- 3) the submitted tokenizer: the V=10,000 prefix ---
vocab = [bpe.BYTE_ENCODER[b] for b in range(256)]
for a, b in merges[:SUBMIT_V - 256]:
    vocab.append(a + b)
BDEC = {c: b for b, c in bpe.BYTE_ENCODER.items()}
def decode_tok(t):
    return bytes(BDEC[ch] for ch in t).decode("utf-8", "replace")
pub = {
    "meta": {**meta, "note_vocab": f"first {SUBMIT_V - 256} merges of the {VMAX}-token run "
             "(BPE prefix property: identical to training to 10k directly)"},
    "note": "Byte-level BPE. vocab[i] is the token string in GPT-2 byte-char encoding; "
            "decoded[i] is its readable form. merges are applied in order.",
    "vocab": vocab,
    "decoded": [decode_tok(t) for t in vocab],
    "merges": [[a, b] for a, b in merges[:SUBMIT_V - 256]],
}
pubpath = os.path.join(ASSIGN, "tokenizer.json")
with open(pubpath, "w", encoding="utf-8") as f:
    json.dump(pub, f, ensure_ascii=False)
print(f"wrote {pubpath}  ({os.path.getsize(pubpath):,} bytes)")

print(f"\n@ V={SUBMIT_V} (submission):")
for l in LANGS:
    s = stats[l]
    print(f"  {LANG_META[l][0]:<9} tokens={s['tokens']:>7,}  fertA={s['fertA']:.4f}  fertB={s['fertB']:.4f}")
print(f"  scoreA={scoreA10:,.0f}  scoreB={scoreB10:,.0f}")
print(f"landmarks: strict-legal V={legalA}, peakA={peakA[0]:,.0f} @ V={peakA[1]}, "
      f"peakB={peakB[0]:,.0f} @ V={peakB[1]}, vmax={VMAX}")
