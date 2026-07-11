"""Coordinate-ascent tuner: maximize score = 1000/(Xmax-Xmin) subject to the hard
constraint English fertility < 1.2. Sweeps one language's weight at a time,
keeps the best, repeats. Far more sample-efficient than a full grid."""
import sys, os, time, bpe
DATA = os.path.join(os.path.dirname(__file__), "data")
def load(l):
    with open(os.path.join(DATA, f"india_{l}.txt"), encoding="utf-8") as f:
        return bpe.clean(f.read())

FOURTH = sys.argv[1] if len(sys.argv) > 1 else "kn"
EN_MAX = 1.195                      # keep a safety margin below 1.2
langs = ["en", "hi", "te", FOURTH]
texts = {l: load(l) for l in langs}
CACHE_EVAL = {}
_seen = {}

def evaluate(w):
    key = tuple(w[l] for l in langs)
    if key in _seen:
        return _seen[key]
    corpora = [(texts[l], w[l]) for l in langs]
    merges, vocab = bpe.train(corpora, vocab_size=10000, verbose=False)
    ranks = bpe.build_ranks(merges); c = {}
    ferts = {l: bpe.fertility(texts[l], ranks, c)[0] for l in langs}
    xs = sorted(ferts.values()); gap = xs[-1] - xs[0]
    score = 1000 / gap if gap else 1e9
    feasible = ferts["en"] < EN_MAX
    # objective: feasibility dominates; then score; infeasible ranked by -en
    obj = (1e9 + score) if feasible else (-(ferts["en"]))
    _seen[key] = (obj, score, ferts, feasible)
    return _seen[key]

w = {"en": 5, "hi": 2, "te": 5, FOURTH: 1}
best = evaluate(w)
t0 = time.time()
RANGES = {"en": range(3, 13), "hi": range(1, 7), "te": range(3, 13), FOURTH: range(1, 6)}
for rnd in range(3):
    improved = False
    for l in langs:
        base = dict(w)
        for val in RANGES[l]:
            cand = dict(base); cand[l] = val
            res = evaluate(cand)
            if res[0] > best[0]:
                best, w, improved = res, cand, True
    print(f"round {rnd}: w={ {l:w[l] for l in langs} }  "
          f"en={best[2]['en']:.3f} score={best[1]:.0f} feasible={best[3]}  ({time.time()-t0:.0f}s)")
    if not improved:
        break

obj, score, ferts, feasible = best
print(f"\nBEST for 4th={FOURTH}:  weights={ {l:w[l] for l in langs} }")
for l in langs:
    print(f"   {l}: {ferts[l]:.4f}")
print(f"   English<1.2: {'OK' if feasible else 'FAIL'}   score={score:.0f}   ({len(_seen)} trainings)")
