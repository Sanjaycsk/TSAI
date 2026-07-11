"""Train on India page + regional pages; EVALUATE on the India page only.
Compare against the India-only baseline. Goal: all akshara fertilities < 1.8,
English < 1.2. Indic corpora = (india_weight, regional_weight)."""
import os, re, bpe
DATA = os.path.join(os.path.dirname(__file__), "data")
def rd(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return bpe.clean(f.read())
naive = re.compile(r"\w+")

india = {l: rd(f"india_{l}.txt") for l in ["en","hi","te","kn"]}
regio = {l: rd(f"regional_{l}.txt") for l in ["hi","te","kn"]}

def run(cfg, label):
    # cfg: {lang: (india_w, regional_w)}; english regional_w ignored
    corpora = [(india["en"], cfg["en"][0])]
    for l in ["hi","te","kn"]:
        iw, rw = cfg[l]
        corpora.append((india[l], iw))
        if rw: corpora.append((regio[l], rw))
    merges,_ = bpe.train(corpora, 10000, verbose=False)
    ranks = bpe.build_ranks(merges); c={}
    fA={}; fB={}
    for l in ["en","hi","te","kn"]:
        toks=len(bpe.encode(india[l], ranks, c))
        fA[l]=toks/bpe.word_count(india[l]); fB[l]=toks/len(naive.findall(india[l]))
    xs=sorted(fA.values()); gap=xs[-1]-xs[0]; s=1000/gap if gap else 0
    xsB=sorted(fB.values()); gB=xsB[-1]-xsB[0]; sB=1000/gB if gB else 0
    allunder=all(v<1.8 for v in fA.values())
    print(f"{label:<26} en={fA['en']:.3f} hi={fA['hi']:.3f} te={fA['te']:.3f} kn={fA['kn']:.3f}"
          f" | <1.8:{'Y' if allunder else 'n'} scoreA={s:,.0f} scoreB={sB:,.0f}")
    return fA

# baseline: india only (current shipped weights)
run({"en":(11,0),"hi":(2,0),"te":(7,0),"kn":(10,0)}, "BEFORE (india only)")
# with regional data, a few india:regional splits
run({"en":(11,0),"hi":(3,2),"te":(6,3),"kn":(7,3)}, "regional A")
run({"en":(11,0),"hi":(4,2),"te":(7,4),"kn":(8,4)}, "regional B")
run({"en":(11,0),"hi":(3,3),"te":(6,5),"kn":(7,5)}, "regional C (heavy)")
run({"en":(12,0),"hi":(4,3),"te":(8,5),"kn":(9,5)}, "regional D")
run({"en":(11,0),"hi":(3,1),"te":(6,2),"kn":(7,2)}, "regional E (light)")
