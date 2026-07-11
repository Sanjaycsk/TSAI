"""
Train the shared 10k-vocab BPE on 4 India-Wikipedia pages and report fertility
per language + the assignment score. Weights let us hand more of the shared
budget to harder scripts to balance fertilities (the real tuning lever).

Usage:
  python tune.py                      # equal weights, langs en,hi,te,kn
  python tune.py en=1 hi=6 te=9 kn=12 # custom weights (lang=weight ...)
  python tune.py ... --fourth ta      # pick the 4th language
  python tune.py ... --save tok.json  # export the tokenizer
"""
import sys, os, json, time
import bpe

DATA = os.path.join(os.path.dirname(__file__), "data")
LANG_NAMES = {"en": "English", "hi": "Hindi", "te": "Telugu",
              "kn": "Kannada", "ta": "Tamil", "bn": "Bengali"}

def load(lang):
    with open(os.path.join(DATA, f"india_{lang}.txt"), encoding="utf-8") as f:
        return bpe.clean(f.read())

def main():
    weights = {}
    fourth = "kn"
    vocab_size = 10000
    save = None
    for arg in sys.argv[1:]:
        if arg.startswith("--fourth"):
            fourth = arg.split("=", 1)[1] if "=" in arg else None
        elif arg == "--fourth":
            pass
        elif arg.startswith("--save"):
            save = arg.split("=", 1)[1]
        elif arg.startswith("--vocab"):
            vocab_size = int(arg.split("=", 1)[1])
        elif "=" in arg:
            k, v = arg.split("=")
            weights[k] = float(v)

    langs = ["en", "hi", "te", fourth]
    texts = {l: load(l) for l in langs}
    corpora = [(texts[l], weights.get(l, 1.0)) for l in langs]

    t0 = time.time()
    merges, vocab = bpe.train(corpora, vocab_size=vocab_size, verbose=False)
    ranks = bpe.build_ranks(merges)
    dt = time.time() - t0

    print(f"\ntrained {len(vocab)} tokens ({len(merges)} merges) in {dt:.1f}s"
          f"   weights={ {l: weights.get(l,1.0) for l in langs} }")
    print(f"{'lang':<9}{'weight':>7}{'tokens':>9}{'words':>9}{'fertility':>11}")
    ferts = {}
    cache = {}
    for l in langs:
        fert, toks, words = bpe.fertility(texts[l], ranks, cache)
        ferts[l] = fert
        print(f"{LANG_NAMES[l]:<9}{weights.get(l,1.0):>7}{toks:>9,}{words:>9,}{fert:>11.4f}")

    xs = sorted(ferts.values())
    xmin, xmax = xs[0], xs[-1]
    gap = xmax - xmin
    score = 1000 / gap if gap > 0 else float("inf")
    en_ok = ferts["en"] < 1.2
    print(f"\ngap (Xmax-Xmin) = {gap:.4f}   ->  score = {score:,.1f}")
    print(f"English < 1.2 ?  {ferts['en']:.4f}  {'OK' if en_ok else 'FAIL — must fix'}")

    if save:
        out = {
            "meta": {
                "vocab_size": len(vocab),
                "langs": langs,
                "weights": {l: weights.get(l, 1.0) for l in langs},
                "fertility": {l: ferts[l] for l in langs},
                "score": score,
            },
            "vocab": vocab,                                  # id -> token string
            "merges": ["".join(m) for m in merges],    # ordered merge list
        }
        with open(save, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False)
        print(f"saved -> {save}  ({os.path.getsize(save):,} bytes)")

if __name__ == "__main__":
    main()
