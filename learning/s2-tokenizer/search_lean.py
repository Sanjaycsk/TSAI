"""Fast focused search: a curated set of English-heavy weight configs across the
three candidate 4th languages. Reports akshara (honest) AND naive-\\w+ scores.
Writes the best valid config to best_config.json."""
import os, re, json, bpe
DATA = os.path.join(os.path.dirname(__file__), "data")
def load(l):
    with open(os.path.join(DATA, f"india_{l}.txt"), encoding="utf-8") as f:
        return bpe.clean(f.read())
naive = re.compile(r"\w+")
CONFIGS = [(8,3,6,3),(8,4,6,4),(9,3,6,4),(7,3,5,3),(9,4,7,4),
           (8,3,7,3),(10,4,7,5),(9,3,7,4),(9,4,6,3),(10,3,7,4),
           (8,3,6,4),(11,4,8,5)]

def score_of(ferts, wc):
    xs = sorted(ferts[l][wc] for l in ferts); gap = xs[-1]-xs[0]
    return (1000/gap if gap else 9e9), gap

best_overall = None
allres = {}
for fourth in ["kn","ta","bn"]:
    langs = ["en","hi","te",fourth]
    texts = {l: load(l) for l in langs}
    best = None
    for wt in CONFIGS:
        w = dict(zip(langs, wt))
        merges,_ = bpe.train([(texts[l],w[l]) for l in langs], 10000, verbose=False)
        ranks = bpe.build_ranks(merges); c={}
        ferts = {}
        for l in langs:
            toks = len(bpe.encode(texts[l], ranks, c))
            ferts[l] = {"A": toks/bpe.word_count(texts[l]),
                        "B": toks/len(naive.findall(texts[l])),
                        "tokens": toks}
        sA,gA = score_of(ferts,"A"); sB,gB = score_of(ferts,"B")
        feas = ferts["en"]["A"] < 1.198
        cand = {"fourth":fourth,"weights":w,"ferts":ferts,"scoreA":sA,"scoreB":sB,"feasible":feas}
        if feas and (best is None or sA > best["scoreA"]):
            best = cand
    allres[fourth] = best
    if best:
        f = best["ferts"]
        print(f"4th={fourth}: w={list(best['weights'].values())} "
              f"en={f['en']['A']:.3f} hi={f['hi']['A']:.3f} te={f['te']['A']:.3f} {fourth}={f[fourth]['A']:.3f}"
              f" | scoreA={best['scoreA']:.0f} scoreB(naive)={best['scoreB']:.0f}")
        if best_overall is None or best["scoreA"] > best_overall["scoreA"]:
            best_overall = best
    else:
        print(f"4th={fourth}: no feasible config in set")

print(f"\nWINNER 4th={best_overall['fourth']} scoreA={best_overall['scoreA']:.0f} weights={best_overall['weights']}")
with open(os.path.join(os.path.dirname(__file__),"best_config.json"),"w",encoding="utf-8") as f:
    json.dump(best_overall, f, ensure_ascii=False, indent=2)
