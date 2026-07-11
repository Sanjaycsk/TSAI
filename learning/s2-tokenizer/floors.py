"""Floor test: give the WHOLE 10k vocab to one language's India page and see the
lowest fertility it can reach. If a language's floor is already > 1.2, no amount
of budget-sharing will pull it down to English's target."""
import os, bpe
DATA = os.path.join(os.path.dirname(__file__), "data")
def load(l):
    with open(os.path.join(DATA, f"india_{l}.txt"), encoding="utf-8") as f:
        return bpe.clean(f.read())
names = {"en":"English","hi":"Hindi","te":"Telugu","kn":"Kannada","ta":"Tamil","bn":"Bengali"}
print(f"{'lang':<9}{'uniq-words':>11}{'floor fertility (whole 10k budget)':>36}")
for l in ["en","hi","te","kn","ta","bn"]:
    t = load(l)
    merges, vocab = bpe.train([(t, 1)], vocab_size=10000, verbose=False)
    ranks = bpe.build_ranks(merges)
    fert, toks, words = bpe.fertility(t, ranks)
    uniq = len(set(bpe.pretokenize(t)))
    print(f"{names[l]:<9}{uniq:>11,}{fert:>28.4f}  ({toks:,}/{words:,} tok/word)")
