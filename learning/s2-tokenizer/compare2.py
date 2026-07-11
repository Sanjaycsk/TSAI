"""India-only, rebalanced weights: how low can the 3 Indic languages go while
English stays < 1.2? Also test India+regional with a HIGH english weight (to keep
english feasible) to see if regional data still helps once english is protected."""
import os, re, bpe
DATA = os.path.join(os.path.dirname(__file__), "data")
def rd(n):
    with open(os.path.join(DATA,n),encoding="utf-8") as f: return bpe.clean(f.read())
naive=re.compile(r"\w+")
india={l:rd(f"india_{l}.txt") for l in ["en","hi","te","kn"]}
regio={l:rd(f"regional_{l}.txt") for l in ["hi","te","kn"]}

def measure(corpora,label):
    merges,_=bpe.train(corpora,10000,verbose=False)
    ranks=bpe.build_ranks(merges); c={}
    fA={l:len(bpe.encode(india[l],ranks,c))/bpe.word_count(india[l]) for l in ["en","hi","te","kn"]}
    xs=sorted(fA.values()); gap=xs[-1]-xs[0]; s=1000/gap if gap else 0
    under=sum(v<1.8 for v in fA.values())
    ok=fA["en"]<1.2
    print(f"{label:<24} en={fA['en']:.3f} hi={fA['hi']:.3f} te={fA['te']:.3f} kn={fA['kn']:.3f}"
          f" | en<1.2:{'Y' if ok else 'N'} <1.8:{under}/4 score={s:,.0f}")

print("--- india only, rebalanced ---")
for wt in [(11,5,8,7),(11,4,9,7),(11,5,9,8),(12,5,9,8),(11,6,9,8),(12,6,10,9),(13,6,10,9)]:
    measure([(india[l],w) for l,w in zip(["en","hi","te","kn"],wt)], f"india {wt}")

print("--- india+regional, english protected (high en weight) ---")
for enw,iw,rw in [(20,6,2),(24,7,3),(28,8,3),(24,6,2)]:
    corpora=[(india["en"],enw)]
    for l in ["hi","te","kn"]:
        corpora.append((india[l],iw)); corpora.append((regio[l],rw))
    measure(corpora, f"reg en{enw} i{iw} r{rw}")
