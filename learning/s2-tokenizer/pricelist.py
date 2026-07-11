"""Price list: how many TARGETED merges each language needs to reach a given
fertility (from the recorded 20k feedback run). This is the arithmetic that
decides whether ANY budget split can satisfy targets at V=10,000."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, "train20k.json"), encoding="utf-8"))
langs = ["en", "hi", "te", "kn"]
T0, W, deltas = d["T0"], d["W"], d["deltas"]
order = [d["order"][i:i+2] for i in range(0, len(d["order"]), 2)]
n = len(deltas["en"])

T = dict(T0)
spent = {l: 0 for l in langs}
hit = {}   # (lang, target) -> merges spent by that lang when reached
targets = {"en": [1.2, 1.19], "hi": [2.0, 1.8, 1.5], "te": [2.0, 1.8, 1.5], "kn": [2.0, 1.8, 1.5]}
for i in range(n):
    for l in langs:
        T[l] -= deltas[l][i]
    spent[order[i]] += 1
    for l in langs:
        f = T[l] / W[l]
        for t in targets[l]:
            if (l, t) not in hit and f <= t:
                hit[(l, t)] = spent[l]
print("targeted merges needed (word-scope BPE, incl. cross-language spillover credit):")
for l in langs:
    row = "  ".join(f"->{t}: {hit.get((l, t), 'never'):>5}" for t in targets[l])
    print(f"  {l}:  {row}")
need18 = hit[("en", 1.19)] + sum(hit[(l, 1.8)] for l in ["hi", "te", "kn"])
print(f"\nen@1.19 + (hi,te,kn)@1.8 total = {need18:,} targeted merges  vs  9,744 available"
      f"  ->  short by {need18 - 9744:,}")
print(f"40% split gives en {int(0.4 * 9744):,} merges; en needs {hit[('en', 1.19)]:,} to reach 1.19")
