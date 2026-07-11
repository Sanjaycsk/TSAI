"""Fuse BOTH runs into one widget dataset (widget_data_v4.json):

  v2 — word-scope feedback BPE  (the attempt that hit the 2.06 wall; curves to V=16,762)
  v3 — sentence-scope feedback BPE (the final: en 1.19, indic 1.73; extended past
       10k so the chart can show where the three Indic curves converge)

Safety proofs before anything ships:
  * the extended v3 run's first 9,744 merges are BYTE-IDENTICAL to the verified
    v3c submission run (trainer determinism -> slider<=10k IS the submitted tokenizer)
  * v3ext curves == real sentence-scope encoder at 3 truncations (v2 was proved in export2)
"""
import os, re, json, datetime, bpe
from feedback3 import LANGS, load_texts

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

HERE = os.path.dirname(os.path.abspath(__file__))
sub = json.load(open(os.path.join(HERE, "train10k_v3c.json"), encoding="utf-8"))
ext = json.load(open(os.path.join(HERE, "train_v3ext.json"), encoding="utf-8"))
v2d = json.load(open(os.path.join(HERE, "tokenizer_data.json"), encoding="utf-8"))

assert ext["merges"][:len(sub["merges"])] == sub["merges"], \
    "extended run diverged from the submitted prefix!"
print(f"prefix determinism: first {len(sub['merges']):,} merges identical [OK]")

texts = load_texts()
naive = re.compile(r"\w+")
W = ext["W"]
WB = {l: len(naive.findall(texts[l])) for l in LANGS}
merges3 = [tuple(m) for m in ext["merges"]]
n3 = len(merges3); VMAX3 = 256 + n3

def cumtok(run, l, V):
    return run["T0"][l] - sum(run["deltas"][l][:V - 256])

ranks3 = bpe.build_ranks(merges3)
print("v3ext parity (curve == sentence-scope encoder):")
for V in (2000, 10000, VMAX3):
    rv = {p: r for p, r in ranks3.items() if r < V - 256}
    cache = {}
    for l in LANGS:
        enc = len(encode_v3(texts[l], rv, cache))
        assert enc == cumtok(ext, l, V), f"MISMATCH V={V} {l}"
    print(f"  V={V:>6} exact [OK]")

def curve_score(run, V, denom):
    f = [cumtok(run, l, V) / denom[l] for l in LANGS]
    return 1000 / (max(f) - min(f))

# landmarks for the projection chart
peak3 = max(((curve_score(ext, 256 + i, W), 256 + i) for i in range(1, n3 + 1)), key=lambda x: x[0])
land3 = {"peak": {"score": round(peak3[0]), "V": peak3[1]}, "vmax": VMAX3}
def stats_at(run, V):
    return {l: {"tokens": cumtok(run, l, V), "fertA": cumtok(run, l, V) / W[l],
                "fertB": cumtok(run, l, V) / WB[l]} for l in LANGS}

data = {
    "meta": {"name": "TokenSangam", "generated": datetime.date.today().isoformat(),
             "source": "Wikipedia 'India' article (en/hi/te/kn), cleaned",
             "submit_V": 10000},
    "langs": [{"code": "en", "name": "English", "badge": "Aa"}, {"code": "hi", "name": "Hindi", "badge": "अ"},
              {"code": "te", "name": "Telugu", "badge": "అ"}, {"code": "kn", "name": "Kannada", "badge": "ಅ"}],
    "texts": texts, "W": W, "WB": WB,
    "v2": {"merges": v2d["merges"], "deltas": v2d["deltas"], "T0": v2d["T0"],
           "vmax": v2d["meta"]["vmax"], "peak": {"score": round(v2d["meta"]["peakA"]["score"]),
           "V": v2d["meta"]["peakA"]["V"]}, "stats10k": stats_at(v2d, 10000),
           "score10k": {"A": round(curve_score(v2d, 10000, W)), "B": round(curve_score(v2d, 10000, WB))}},
    "v3": {"merges": ext["merges"], "deltas": ext["deltas"], "T0": ext["T0"],
           "order": ext["order"], "vmax": VMAX3, "peak": land3["peak"],
           "stats10k": stats_at(ext, 10000),
           "score10k": {"A": round(curve_score(ext, 10000, W)), "B": round(curve_score(ext, 10000, WB))}},
}
out = os.path.join(HERE, "widget_data_v4.json")
json.dump(data, open(out, "w", encoding="utf-8"), ensure_ascii=False)
print(f"\nwrote {out} ({os.path.getsize(out):,} bytes)")
print(f"v3 @10k strict: " + " ".join(f"{l}={data['v3']['stats10k'][l]['fertA']:.4f}" for l in LANGS)
      + f"  score {data['v3']['score10k']['A']}")
print(f"v3 projection: peak {land3['peak']['score']:,} @ V={land3['peak']['V']:,}, ends {VMAX3:,}")
print(f"v2 @10k strict score {data['v2']['score10k']['A']}; peak {data['v2']['peak']['score']:,} @ {data['v2']['peak']['V']:,}")
