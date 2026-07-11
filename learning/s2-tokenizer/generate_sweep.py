"""Precompute fertility + score at a range of vocab sizes (for the widget's
educational slider). Same weights/data as the final 10k tokenizer. Evaluated on
the India page. The SUBMITTED tokenizer stays 10k; this only illustrates the wall."""
import os, json, bpe
DATA = os.path.join(os.path.dirname(__file__), "data")
def rd(l):
    with open(os.path.join(DATA,f"india_{l}.txt"),encoding="utf-8") as f: return bpe.clean(f.read())
langs=["en","hi","te","kn"]; W={"en":11,"hi":2,"te":7,"kn":10}
texts={l:rd(l) for l in langs}
SIZES=[10000,11000,12000,13000,14000,15000,16000,18000,20000]
sweep=[]
for V in SIZES:
    merges,_=bpe.train([(texts[l],W[l]) for l in langs], V, verbose=False)
    ranks=bpe.build_ranks(merges); c={}
    f={l:len(bpe.encode(texts[l],ranks,c))/bpe.word_count(texts[l]) for l in langs}
    xs=sorted(f.values()); gap=xs[-1]-xs[0]; s=1000/gap if gap else 0
    sweep.append({"vocab":V,"fert":{l:round(f[l],4) for l in langs},"score":round(s)})
    print(f"{V}: en={f['en']:.3f} hi={f['hi']:.3f} te={f['te']:.3f} kn={f['kn']:.3f} score={s:,.0f}")
json.dump(sweep, open(os.path.join(os.path.dirname(__file__),"vocab_sweep.json"),"w"), ensure_ascii=False)
print("saved vocab_sweep.json")
