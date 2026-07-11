"""Where exactly do the constraints land? Read the per-merge deltas from the
20k feedback run and report fertilities at key V, the first legal V, and how
many EN merges the last few thousandths of English fertility cost (the lever
if legality must move before V=10,000)."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, "train20k.json"), encoding="utf-8"))
langs = ["en", "hi", "te", "kn"]
T0, W, deltas = d["T0"], d["W"], d["deltas"]
order = [d["order"][i:i+2] for i in range(0, len(d["order"]), 2)]
n = len(deltas["en"])

def ferts_at(V):
    m = V - 256
    return {l: (T0[l] - sum(deltas[l][:m])) / W[l] for l in langs}

for V in (9744, 10000, 10256, 12000, 14000, 15000, 16000, 16256, 16672):
    if V - 256 <= n:
        f = ferts_at(V)
        gap = max(f.values()) - min(f.values())
        print(f"V={V:>6}  " + "  ".join(f"{l}={f[l]:.4f}" for l in langs) +
              f"  score={1000/gap:,.0f}")

# first V where en<1.2 and hi/te/kn<2.0 (running, no re-summing)
T = dict(T0); legal = None
en_merge_count = 0; en_curve = []   # (en merges spent, en fert)
for i in range(n):
    for l in langs: T[l] -= deltas[l][i]
    if order[i] == "en":
        en_merge_count += 1
        en_curve.append((en_merge_count, T["en"] / W["en"]))
    f = {l: T[l] / W[l] for l in langs}
    if legal is None and f["en"] < 1.2 and all(f[l] < 2.0 for l in langs[1:]):
        legal = 256 + i + 1
        print(f"\nfirst fully-legal V = {legal}  " +
              "  ".join(f"{l}={f[l]:.4f}" for l in langs))
print(f"total en merges: {en_merge_count}")
for target in (1.20, 1.198, 1.196, 1.194, 1.192, 1.19):
    hit = next((m for m, f in en_curve if f <= target), None)
    print(f"en merges to reach fert {target}: {hit}")
