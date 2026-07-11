"""Export + verify the v3c sentence-scope run (train10k_v3c.json).

Same proof obligation as export2.py, with one addition: encode() here must use
the SENTENCE-scope pretokenizer (split after । ॥ . ! ?) — the pretokenizer is
part of the tokenizer, and parity is only meaningful against the real pipeline.
Writes tokenizer_data_v3.json (widget) + assignment/tokenizer_v3.json (staged;
swapped over tokenizer.json only on go-ahead)."""
import os, re, json, datetime, bpe
from feedback3 import LANGS, load_texts

HERE = os.path.dirname(os.path.abspath(__file__))
ASSIGN = os.path.abspath(os.path.join(HERE, "..", "..", "assignment"))
SUBMIT_V = 10000
SPLITCH = set('।॥.!?')

def clauses(text):
    out, cur = [], []
    for ch in text:
        cur.append(ch)
        if ch in SPLITCH:
            out.append("".join(cur)); cur = []
    if cur:
        out.append("".join(cur))
    return out

def encode_v3(text, ranks, cache):
    out = []
    for chunk in clauses(text):
        out.extend(bpe.bpe_word(bpe.word_to_byte_chars(chunk), ranks, cache))
    return out

run = json.load(open(os.path.join(HERE, "train10k_v3c.json"), encoding="utf-8"))
merges = [tuple(m) for m in run["merges"]]
deltas, T0, W = run["deltas"], run["T0"], run["W"]
n = len(merges)
VMAX = 256 + n
texts = load_texts()
naive = re.compile(r"\w+")
WB = {l: len(naive.findall(texts[l])) for l in LANGS}

def curve_tokens(l, V):
    return T0[l] - sum(deltas[l][:V - 256])

ranks = bpe.build_ranks(merges)
print("verifying curve == real sentence-scope encode() at truncated V:")
for V in (2000, 5000, 8456, SUBMIT_V):
    rv = {p: r for p, r in ranks.items() if r < V - 256}
    cache = {}
    for l in LANGS:
        enc = len(encode_v3(texts[l], rv, cache))
        cur = curve_tokens(l, V)
        assert enc == cur, f"MISMATCH V={V} {l}: encode={enc} curve={cur}"
    print(f"  V={V:>6}  exact for all 4 languages")

stats = {}
for l in LANGS:
    t = curve_tokens(l, SUBMIT_V)
    stats[l] = {"tokens": t, "wordsA": W[l], "wordsB": WB[l],
                "fertA": t / W[l], "fertB": t / WB[l]}
def score(key):
    xs = sorted(stats[l][key] for l in LANGS)
    return 1000 / (xs[-1] - xs[0])
sA, sB = score("fertA"), score("fertB")

meta = {
    "name": "TokenSangam",
    "vocab_size": SUBMIT_V, "n_merges_total": n, "vmax": VMAX,
    "trainer": "feedback-BPE v3: sentence-scope (phrase tokens), en frozen at 1.19, "
               "worst-language-first merge selection",
    "pretokenizer": "split after sentence enders (danda/period/!/?); tokens may span words",
    "scoreA": sA, "scoreB": sB,
    "generated": datetime.date.today().isoformat(),
    "source": "Wikipedia 'India' article (en, hi, te, kn), cleaned (whitespace collapsed)",
}
data = {"meta": meta,
        "langs": [{"code": "en", "name": "English", "badge": "Aa"}, {"code": "hi", "name": "Hindi", "badge": "अ"},
                  {"code": "te", "name": "Telugu", "badge": "అ"}, {"code": "kn", "name": "Kannada", "badge": "ಅ"}],
        "merges": [[a, b] for a, b in merges], "deltas": deltas,
        "T0": T0, "W": W, "WB": WB, "order": run["order"], "stats": stats, "texts": texts}
p1 = os.path.join(HERE, "tokenizer_data_v3.json")
json.dump(data, open(p1, "w", encoding="utf-8"), ensure_ascii=False)

vocab = [bpe.BYTE_ENCODER[b] for b in range(256)]
for a, b in merges[:SUBMIT_V - 256]:
    vocab.append(a + b)
BDEC = {c: b for b, c in bpe.BYTE_ENCODER.items()}
pub = {"meta": meta,
       "note": "Byte-level BPE, sentence-scope pretokenization (tokens may span words — "
               "SentencePiece split_by_whitespace=false style). vocab[i] in GPT-2 byte-chars; "
               "decoded[i] readable; merges applied in order.",
       "vocab": vocab,
       "decoded": [bytes(BDEC[c] for c in t).decode("utf-8", "replace") for t in vocab],
       "merges": [[a, b] for a, b in merges[:SUBMIT_V - 256]]}
p2 = os.path.join(ASSIGN, "tokenizer_v3.json")
json.dump(pub, open(p2, "w", encoding="utf-8"), ensure_ascii=False)

print(f"\nwrote {p1} ({os.path.getsize(p1):,} b) and {p2} ({os.path.getsize(p2):,} b)")
print(f"@ V=10,000 strict: " + "  ".join(f"{l}={stats[l]['fertA']:.4f}" for l in LANGS))
print(f"scoreA={sA:,.0f}  scoreB={sB:,.0f}")
