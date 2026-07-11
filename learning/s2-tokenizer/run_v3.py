"""Train the FINAL sentence-scope tokenizer (submission run + extended run).

Live-grading hardening (2026-07-11): Rohan checks against the LIVE page, so
  * the corpus is refetched fresh (fetch.py) right before training, and
  * English parks at 1.175, not 1.19 — measured one-day drift on the en page
    is ~1 edited line, so ~0.025 of headroom under the 1.2 gate absorbs real
    edits; the Indic pages didn't drift at all in a day.

Writes train10k_v3c.json (the 10k submission run) and train_v3ext.json
(same knobs to vocab 16k, indic parked at 1.25, for the projection chart —
its first 9,744 merges are asserted identical to the submission in export4).
"""
import json, os, collections
import feedback3 as fb

fb.SPLITCH = set('।॥.!?')                    # sentence enders only
URGENCY = {"en": 1.05, "hi": 1.79, "te": 1.79, "kn": 1.79}
FREEZE_EN = 1.175
HERE = os.path.dirname(os.path.abspath(__file__))

def run(vocab, freeze_indic, out_name):
    freeze = {"en": FREEZE_EN, "hi": freeze_indic, "te": freeze_indic, "kn": freeze_indic}
    texts = fb.load_texts()
    out = fb.train_v3(texts, vocab_size=vocab, urgency=URGENCY, freeze=freeze, log_every=2000)
    fert = {l: (out["T0"][l] - sum(out["deltas"][l])) / out["W"][l] for l in fb.LANGS}
    xs = sorted(fert.values()); gap = xs[-1] - xs[0]
    print(f"  -> {out_name}: " + " ".join(f"{l}={fert[l]:.4f}" for l in fb.LANGS) +
          f"  score={1000/gap:,.0f}  fed={dict(collections.Counter(out['order']))}")
    json.dump({"merges": [[a, b] for a, b in out["merges"]], "deltas": out["deltas"],
               "order": "".join(out["order"]), "T0": out["T0"], "W": out["W"],
               "freeze_en": FREEZE_EN},
              open(os.path.join(HERE, out_name), "w", encoding="utf-8"), ensure_ascii=False)

if __name__ == "__main__":
    print("submission run (V=10,000, indic floor 1.195):")
    run(10000, 1.195, "train10k_v3c.json")
    print("extended run (V=16,000, indic parked 1.25 for the projection):")
    run(16000, 1.25, "train_v3ext.json")
