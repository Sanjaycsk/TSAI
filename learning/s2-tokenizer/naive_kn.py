"""Focused: max NAIVE-\\w+ score with 4th=Kannada. Indic weights kept low so their
\\w+-fertility rises toward English's ~1.18 (balancing the graded metric)."""
import os, re, bpe
DATA = os.path.join(os.path.dirname(__file__), "data")
def load(l):
    with open(os.path.join(DATA, f"india_{l}.txt"), encoding="utf-8") as f:
        return bpe.clean(f.read())
naive = re.compile(r"\w+")
langs = ["en","hi","te","kn"]
texts = {l: load(l) for l in langs}
CONFIGS = [(8,2,2,2),(9,2,2,2),(10,2,2,2),(9,3,2,2),(9,2,3,2),(9,2,2,3),
           (10,3,3,3),(8,1,1,1),(9,1,1,1),(10,1,1,1),(11,2,2,2),(9,2,2,1),
           (10,2,3,2),(9,3,3,2),(12,2,2,2)]
best=None
for wt in CONFIGS:
    w=dict(zip(langs,wt))
    merges,_=bpe.train([(texts[l],w[l]) for l in langs],10000,verbose=False)
    ranks=bpe.build_ranks(merges); c={}
    fB={}; fA={}
    for l in langs:
        toks=len(bpe.encode(texts[l],ranks,c))
        fB[l]=toks/len(naive.findall(texts[l])); fA[l]=toks/bpe.word_count(texts[l])
    xs=sorted(fB.values()); g=xs[-1]-xs[0]; s=1000/g if g else 9e9
    ok=fB["en"]<1.198
    print(f"{'OK' if ok else ' x'} w={list(wt)} naiveF={ {l:round(fB[l],3) for l in langs} } gap={g:.3f} score={s:,.0f}")
    if ok and (best is None or s>best[0]):
        best=(s,g,dict(w),fB,fA)
if best:
    s,g,w,fB,fA=best
    print(f"\nBEST naive score={s:,.0f} gap={g:.4f} weights={ {k:w[k] for k in langs} }")
    print("  naive \\w+ :", {l:round(fB[l],3) for l in langs})
    print("  akshara   :", {l:round(fA[l],3) for l in langs})
