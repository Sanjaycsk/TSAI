"""Search per-language weights to maximize score = 1000/(Xmax-Xmin) subject to
English fertility < 1.2. Weights hand more of the shared 10k budget to the
languages that need it. Prints configs sorted by score (valid ones first)."""
import sys, os, time, bpe
DATA = os.path.join(os.path.dirname(__file__), "data")
def load(l):
    with open(os.path.join(DATA, f"india_{l}.txt"), encoding="utf-8") as f:
        return bpe.clean(f.read())

FOURTH = sys.argv[1] if len(sys.argv) > 1 else "kn"
langs = ["en", "hi", "te", FOURTH]
texts = {l: load(l) for l in langs}

# (en, hi, te, 4th) weight tuples to try
CONFIGS = [
    (1,1,1,1),
    (3,2,4,1), (4,2,5,1), (4,3,5,1), (5,2,5,1),
    (5,3,6,1), (4,2,4,1), (6,3,6,1), (5,3,5,2),
    (4,2,6,1), (3,2,5,1), (6,4,7,1), (5,3,7,1),
    (4,3,6,1), (5,4,7,2),
]

results = []
for wt in CONFIGS:
    weights = dict(zip(langs, wt))
    corpora = [(texts[l], weights[l]) for l in langs]
    t0 = time.time()
    merges, vocab = bpe.train(corpora, vocab_size=10000, verbose=False)
    ranks = bpe.build_ranks(merges); cache = {}
    ferts = {l: bpe.fertility(texts[l], ranks, cache)[0] for l in langs}
    dt = time.time() - t0
    xs = sorted(ferts.values())
    gap = xs[-1] - xs[0]
    score = 1000 / gap if gap else float("inf")
    en_ok = ferts["en"] < 1.2
    results.append((en_ok, score, wt, ferts, len(vocab), dt))

# valid (English<1.2) first, then by score desc
results.sort(key=lambda r: (r[0], r[1]), reverse=True)
print(f"\n4th language = {FOURTH}")
print(f"{'ok':>3} {'score':>8}  {'weights(en,hi,te,'+FOURTH+')':<20} "
      f"{'en':>7}{'hi':>7}{'te':>7}{FOURTH:>7}  {'vocab':>6}")
for en_ok, score, wt, ferts, vsz, dt in results:
    mark = " ok" if en_ok else "  x"
    print(f"{mark} {score:>8.0f}  {str(wt):<20} "
          f"{ferts['en']:>7.3f}{ferts['hi']:>7.3f}{ferts['te']:>7.3f}{ferts[FOURTH]:>7.3f}  {vsz:>6}")
