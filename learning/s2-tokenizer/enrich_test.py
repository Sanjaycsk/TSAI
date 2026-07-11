"""Does extra training data lower India-page fertility (same 10k budget)?
Compare: train on India page ONLY  vs  India page + extra random articles.
Evaluate fertility on the India page either way."""
import os, bpe
DATA = os.path.join(os.path.dirname(__file__), "data")
def rd(p):
    with open(os.path.join(DATA, p), encoding="utf-8") as f:
        return bpe.clean(f.read())
names = {"en":"English","hi":"Hindi","te":"Telugu","kn":"Kannada","ta":"Tamil","bn":"Bengali"}
print(f"{'lang':<9}{'India-only':>12}{'India+extra':>13}{'change':>9}")
for l in ["en","hi","te","kn","ta","bn"]:
    india = rd(f"india_{l}.txt")
    extra = rd(f"extra_{l}.txt")
    # floor: India only
    m1,_ = bpe.train([(india,1)], 10000, verbose=False)
    f1 = bpe.fertility(india, bpe.build_ranks(m1))[0]
    # India (weighted up so it still dominates) + extra
    m2,_ = bpe.train([(india,3),(extra,1)], 10000, verbose=False)
    f2 = bpe.fertility(india, bpe.build_ranks(m2))[0]
    print(f"{names[l]:<9}{f1:>12.4f}{f2:>13.4f}{f2-f1:>+9.4f}")
