"""Balance the 3 Indic languages (equalize their fertility) with English pinned
feasible. Kannada is small, so boosting its weight is cheap in absolute merges."""
import os, re, json, bpe
DATA = os.path.join(os.path.dirname(__file__), "data")
def load(l):
    with open(os.path.join(DATA, f"india_{l}.txt"), encoding="utf-8") as f:
        return bpe.clean(f.read())
naive = re.compile(r"\w+")

# (en,hi,te,4th) — push weight toward the most-starved (kn), then bn variants
CONFIGS = {
 "kn": [(10,2,6,8),(10,2,7,9),(11,2,7,10),(10,3,7,9),(12,2,8,11),
        (11,3,8,10),(10,2,6,10),(12,3,8,12),(11,2,8,11),(13,3,9,12)],
 "bn": [(14,3,8,5),(16,3,9,6),(14,2,8,5),(16,2,9,6),(18,3,10,7),
        (15,3,9,6),(20,3,11,7)],
}
def score(ferts, k):
    xs = sorted(ferts[l][k] for l in ferts); g = xs[-1]-xs[0]
    return (1000/g if g else 9e9)

best = None
for fourth, cfgs in CONFIGS.items():
    langs = ["en","hi","te",fourth]
    texts = {l: load(l) for l in langs}
    for wt in cfgs:
        w = dict(zip(langs, wt))
        merges,_ = bpe.train([(texts[l],w[l]) for l in langs], 10000, verbose=False)
        ranks = bpe.build_ranks(merges); c={}
        ferts = {}
        for l in langs:
            toks = len(bpe.encode(texts[l], ranks, c))
            ferts[l] = {"A":toks/bpe.word_count(texts[l]),
                        "B":toks/len(naive.findall(texts[l])), "tokens":toks}
        feas = ferts["en"]["A"] < 1.198
        sA = score(ferts,"A")
        f=ferts
        flag = "OK " if feas else " x "
        print(f"{flag}4th={fourth} w={list(wt)} en={f['en']['A']:.3f} hi={f['hi']['A']:.3f} "
              f"te={f['te']['A']:.3f} {fourth}={f[fourth]['A']:.3f} | A={sA:.0f} B={score(ferts,'B'):.0f}")
        if feas and (best is None or sA > best["scoreA"]):
            best = {"fourth":fourth,"weights":w,"ferts":ferts,"scoreA":sA,"scoreB":score(ferts,'B'),"feasible":True}

if best:
    print(f"\nWINNER 4th={best['fourth']} scoreA={best['scoreA']:.0f} weights={best['weights']}")
    with open(os.path.join(os.path.dirname(__file__),"best_config.json"),"w",encoding="utf-8") as f:
        json.dump(best, f, ensure_ascii=False, indent=2)
