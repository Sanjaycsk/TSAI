"""Randomized search + coordinate polish for the best HONEST (akshara-aware) score
with English < 1.2, across candidate 4th languages. Writes the winner to
best_config.json for the exporter to use."""
import os, json, random, time, bpe
DATA = os.path.join(os.path.dirname(__file__), "data")
def load(l):
    with open(os.path.join(DATA, f"india_{l}.txt"), encoding="utf-8") as f:
        return bpe.clean(f.read())
EN_MAX = 1.198
random.seed(7)

def run_for(fourth):
    langs = ["en","hi","te",fourth]
    texts = {l: load(l) for l in langs}
    seen = {}
    def ev(w):
        key = tuple(w[l] for l in langs)
        if key in seen: return seen[key]
        merges,_ = bpe.train([(texts[l], w[l]) for l in langs], 10000, verbose=False)
        ranks = bpe.build_ranks(merges); c={}
        ferts = {l: bpe.fertility(texts[l], ranks, c)[0] for l in langs}
        xs = sorted(ferts.values()); gap = xs[-1]-xs[0]
        score = 1000/gap if gap else 1e9
        feas = ferts["en"] < EN_MAX
        obj = (1e9+score) if feas else -ferts["en"]
        seen[key] = (obj, score, ferts, feas, dict(w))
        return seen[key]
    best = (-9e9,)
    # random phase
    for _ in range(45):
        w = {"en":random.randint(5,12),"hi":random.randint(2,7),
             "te":random.randint(4,12),fourth:random.randint(1,9)}
        r = ev(w)
        if r[0] > best[0]: best = r
    # coordinate polish
    w = dict(best[4])
    for _ in range(3):
        for l in langs:
            for val in range(1,13):
                cand = dict(w); cand[l]=val
                r = ev(cand)
                if r[0] > best[0]: best, w = r, cand
    return best, len(seen)

results = {}
t0=time.time()
for fourth in ["kn","ta","bn"]:
    best, n = run_for(fourth)
    obj, score, ferts, feas, w = best
    results[fourth] = {"score":score,"ferts":ferts,"feasible":feas,"weights":w}
    print(f"4th={fourth}: score={score:7.0f} feasible={feas}  "
          f"en={ferts['en']:.3f} hi={ferts['hi']:.3f} te={ferts['te']:.3f} {fourth}={ferts[fourth]:.3f}"
          f"  w={ {k:w[k] for k in ['en','hi','te',fourth]} }  ({n} trainings, {time.time()-t0:.0f}s)")

# pick best feasible by score
best4 = max(results, key=lambda k: (results[k]["feasible"], results[k]["score"]))
out = {"fourth":best4, **results[best4], "all":results}
with open(os.path.join(os.path.dirname(__file__),"best_config.json"),"w",encoding="utf-8") as f:
    json.dump(out,f,ensure_ascii=False,indent=2)
print(f"\nWINNER: 4th={best4}  score={results[best4]['score']:.0f}  weights={results[best4]['weights']}")
