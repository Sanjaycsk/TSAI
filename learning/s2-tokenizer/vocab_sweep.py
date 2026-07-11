"""What does MORE vocab buy? (Demonstration only — the assignment caps vocab at
10k, so this is 'what a real model does', not what we submit.) Same weights,
sweep vocab size, keep English < 1.2, watch Telugu/Kannada fall."""
import os, bpe
DATA = os.path.join(os.path.dirname(__file__), "data")
def rd(l):
    with open(os.path.join(DATA,f"india_{l}.txt"),encoding="utf-8") as f: return bpe.clean(f.read())
langs=["en","hi","te","kn"]; W={"en":11,"hi":2,"te":7,"kn":10}
texts={l:rd(l) for l in langs}
print(f"{'vocab':>7}{'en':>8}{'hi':>8}{'te':>8}{'kn':>8}{'gap':>8}{'score':>9}")
for V in [10000,12000,15000,20000,30000,50000]:
    merges,_=bpe.train([(texts[l],W[l]) for l in langs], V, verbose=False)
    ranks=bpe.build_ranks(merges); c={}
    f={l:len(bpe.encode(texts[l],ranks,c))/bpe.word_count(texts[l]) for l in langs}
    xs=sorted(f.values()); gap=xs[-1]-xs[0]; s=1000/gap if gap else 0
    print(f"{V:>7}{f['en']:>8.3f}{f['hi']:>8.3f}{f['te']:>8.3f}{f['kn']:>8.3f}{gap:>8.3f}{s:>9,.0f}")
