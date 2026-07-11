"""Same tokenizer, two word-counting conventions:
  (A) akshara-aware  [\p{L}\p{M}\p{N}]+   -> भारत = 1 word   (linguistically correct)
  (B) naive stdlib   re.findall(r"\w+")    -> भारत = भ + रत   (splits on matras)
The instructor re-runs with THEIR convention, so we need to see both."""
import os, re, regex, bpe
DATA = os.path.join(os.path.dirname(__file__), "data")
def rd(l):
    with open(os.path.join(DATA, f"india_{l}.txt"), encoding="utf-8") as f:
        return bpe.clean(f.read())
langs = ["en","hi","te","kn"]
texts = {l: rd(l) for l in langs}
# a reasonable English-heavy weighting
merges,_ = bpe.train([(texts["en"],7),(texts["hi"],3),(texts["te"],5),(texts["kn"],3)],
                     10000, verbose=False)
ranks = bpe.build_ranks(merges); cache={}
naive = re.compile(r"\w+")
print(f"{'lang':<9}{'tokens':>8}{'wordsA':>8}{'fertA':>8}{'wordsB':>8}{'fertB':>8}")
fA={}; fB={}
for l in langs:
    toks = len(bpe.encode(texts[l], ranks, cache))
    wA = bpe.word_count(texts[l])                 # akshara-aware
    wB = len(naive.findall(texts[l]))             # naive \w+
    fA[l]=toks/wA; fB[l]=toks/wB
    print(f"{l:<9}{toks:>8,}{wA:>8,}{toks/wA:>8.3f}{wB:>8,}{toks/wB:>8.3f}")
for tag,f in [("A akshara",fA),("B naive-\\w+",fB)]:
    xs=sorted(f.values()); gap=xs[-1]-xs[0]
    print(f"  {tag:<12} gap={gap:.4f} score={1000/gap:,.0f}  en={f['en']:.3f} ({'OK' if f['en']<1.2 else 'FAIL'})")
