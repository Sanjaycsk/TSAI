"""Frontier run: English first (urgency 1.05 -> fed with top priority until it
freezes at exactly 1.19), then every remaining merge goes to the current max
among hi/te/kn with a floor-discovery freeze (1.195). Where the Indic trio
lands at V=10,000 is the LOWEST parking spot the corpus supports with en=1.19
— the honest menu for the score dial."""
import json, os, collections
import feedback3 as fb

URGENCY = {"en": 1.05, "hi": 1.79, "te": 1.79, "kn": 1.79}
FREEZE = {"en": 1.19, "hi": 1.195, "te": 1.195, "kn": 1.195}

texts = fb.load_texts()
out = fb.train_v3(texts, vocab_size=10000, urgency=URGENCY, freeze=FREEZE)
fert = {l: (out["T0"][l] - sum(out["deltas"][l])) / out["W"][l] for l in fb.LANGS}
xs = sorted(fert.values()); gap = xs[-1] - xs[0]
print("\nfinal fertilities (strict):", {l: round(fert[l], 4) for l in fb.LANGS})
print(f"score = 1000/{gap:.4f} = {1000/gap:,.0f}")
print("merges fed:", dict(collections.Counter(out["order"])))
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "train10k_v3b.json")
with open(path, "w", encoding="utf-8") as f:
    json.dump({"merges": [[a, b] for a, b in out["merges"]],
               "deltas": out["deltas"], "order": "".join(out["order"]),
               "T0": out["T0"], "W": out["W"]}, f, ensure_ascii=False)
print(f"wrote {path}")
