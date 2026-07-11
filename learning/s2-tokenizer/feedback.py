"""Feedback BPE — merge selection driven by the SCORE, not by raw frequency.

Vanilla BPE always merges the globally most frequent pair: that optimizes
compression. Rohan's score = 1000 / (max fertility - min fertility) rewards
UNIFORMITY across languages, and gaming it is allowed. So this trainer picks
each merge FOR the language that currently needs it:

  Phase 1 (legality)  while any language breaks its limit (en<=1.19,
                      hi/te/kn<=2.0), feed the worst violator — measured as
                      fertility/limit, so "30x over" beats "1.1x over".
  Phase 2 (score)     English is FROZEN: it is the fertility minimum, and
                      because the score is a SPREAD, improving the minimum
                      widens the gap. Feed whichever of hi/te/kn currently
                      has the max fertility -> the max falls -> gap shrinks
                      from the top while en holds the floor at ~1.19.

Within the target language we still take its most frequent pair (classic BPE,
just scoped to one corpus), so merges stay real, ordered, and truncatable:
the first V-256 merges ARE the vocab-V tokenizer (BPE's prefix property).

While training we also record, per merge step, how many tokens that merge
removed from each language's ACTUAL page. Cumulative-summing those deltas
gives tokens(lang, V) for EVERY V in one pass — the widget's live slider
reads that array instead of re-encoding 200KB of text per tick. Training
applies merges in learned order, which provably equals greedy encode-by-rank
(a new pair can only involve the just-created token, whose rank is higher),
and export.py re-verifies that equality with real encode() calls.
"""
import os, json, time, heapq, collections
import bpe

HERE = os.path.dirname(os.path.abspath(__file__))
LANGS = ["en", "hi", "te", "kn"]
# URGENCY drives phase-1 scheduling; en's is set BELOW its real gate (1.2) so its
# merges land early and en is already parked at FREEZE by V=10,000. hi/te/kn need
# ~275 more merges than fit before 10k (measured), so their strict gate opens at
# ~10.28k regardless of ordering — a corpus capacity wall, not a tuning miss.
URGENCY = {"en": 1.15, "hi": 2.0, "te": 2.0, "kn": 2.0}
FREEZE = {"en": 1.19}    # once at/below this, a language is never fed again —
                         # it is the fertility MINIMUM, and the score is a spread:
                         # improving the minimum widens the gap and LOWERS it
VOCAB_SIZE = 20000       # 256 byte tokens + 19,744 learned merges


def load_texts():
    texts = {}
    for l in LANGS:
        with open(os.path.join(HERE, "data", f"india_{l}.txt"), encoding="utf-8") as f:
            texts[l] = bpe.clean(f.read())
    return texts


def train_feedback(texts, vocab_size=VOCAB_SIZE, urgency=URGENCY,
                   freeze=FREEZE, log_every=2000):
    langs = list(texts.keys())
    frozen = set()       # languages permanently retired from feeding

    # --- dedupe word-chunks GLOBALLY but keep per-language UNWEIGHTED counts ---
    # (a chunk like " India" appears in the Hindi page too; a merge that helps
    #  it must be credited to every language containing it)
    vocab = [bpe.BYTE_ENCODER[b] for b in range(256)]
    tok2id = {t: i for i, t in enumerate(vocab)}
    widx, words, wlf = {}, [], []          # wlf[i] = {lang: raw count}
    for l in langs:
        for w, c in collections.Counter(bpe.pretokenize(texts[l])).items():
            i = widx.get(w)
            if i is None:
                ids = [tok2id[ch] for ch in bpe.word_to_byte_chars(w)]
                if not ids:
                    continue
                i = widx[w] = len(words)
                words.append(ids)
                wlf.append({})
            wlf[i][l] = c

    # --- live fertility bookkeeping: constant denominators, incremental T ---
    W = {l: bpe.word_count(texts[l]) for l in langs}
    T = {l: 0 for l in langs}              # current token count per language
    for i, ids in enumerate(words):
        for l, c in wlf[i].items():
            T[l] += len(ids) * c
    T0 = dict(T)                           # byte-level starting point (V=256)

    # --- per-language pair counts + lazy max-heaps (bpe.py's trick, x4) ---
    pc = {l: {} for l in langs}
    pair_words = collections.defaultdict(set)
    for i, ids in enumerate(words):
        lf = wlf[i]
        for pair in zip(ids, ids[1:]):
            pair_words[pair].add(i)
            for l, c in lf.items():
                pc[l][pair] = pc[l].get(pair, 0) + c
    heaps = {l: [(-c, a, b) for (a, b), c in pc[l].items()] for l in langs}
    for l in langs:
        heapq.heapify(heaps[l])

    merges, order = [], []                 # order[i] = lang merge i was aimed at
    deltas = {l: [] for l in langs}        # deltas[l][i] = tokens merge i removed
    n_merges = vocab_size - 256
    t_start = time.time()

    for step in range(n_merges):
        fert = {l: T[l] / W[l] for l in langs}
        for l, thr in freeze.items():
            if l not in frozen and fert[l] <= thr:
                frozen.add(l)
        live = [l for l in langs if l not in frozen]
        viol = [l for l in live if fert[l] > urgency[l]]
        if viol:   # Phase 1: worst violator relative to its own urgency limit
            target = max(viol, key=lambda l: fert[l] / urgency[l])
        elif live: # Phase 2: hammer the current maximum among live languages
            target = max(live, key=lambda l: fert[l])
        else:
            target = None

        # pop the target's most frequent still-valid pair (lazy heap); if its
        # corpus is fully merged, fall back to the next-worst live language.
        # When EVERY live language is out of pairs (hi/te/kn fully merged,
        # ~V=16.7k), unfreeze the frozen ones to fill the remaining budget —
        # the slider then shows the score DECAYING as English improves, the
        # visible proof that feeding the minimum was always the wrong move.
        best = None
        tried = ([target] if target else []) + \
                sorted((x for x in live if x != target), key=lambda x: -fert[x]) + \
                sorted(frozen, key=lambda x: -fert[x])
        for l in tried:
            h = heaps[l]
            while h:
                negc, a, b = heapq.heappop(h)
                if pc[l].get((a, b), 0) == -negc:
                    best, target = (a, b), l
                    break
            if best:
                break
        if best is None:
            break

        a, b = best
        new_id = len(vocab)
        vocab.append(vocab[a] + vocab[b])
        tok2id[vocab[new_id]] = new_id
        merges.append((vocab[a], vocab[b]))

        step_delta = {l: 0 for l in langs}
        for i in list(pair_words[best]):
            ids, lf = words[i], wlf[i]
            # retire this word's old pair contributions
            for pair in zip(ids, ids[1:]):
                pair_words[pair].discard(i)
                if not pair_words[pair]:
                    pair_words.pop(pair, None)
                for l, c in lf.items():
                    nc = pc[l].get(pair, 0) - c
                    if nc <= 0:
                        pc[l].pop(pair, None)
                    else:
                        pc[l][pair] = nc
                        heapq.heappush(heaps[l], (-nc,) + pair)
            # rebuild the word with (a,b) -> new_id
            merged, j = [], 0
            while j < len(ids):
                if j < len(ids) - 1 and ids[j] == a and ids[j + 1] == b:
                    merged.append(new_id); j += 2
                else:
                    merged.append(ids[j]); j += 1
            removed = len(ids) - len(merged)
            words[i] = merged
            for l, c in lf.items():
                T[l] -= removed * c
                step_delta[l] += removed * c
            # add the new pair contributions
            for pair in zip(merged, merged[1:]):
                pair_words[pair].add(i)
                for l, c in lf.items():
                    nc = pc[l].get(pair, 0) + c
                    pc[l][pair] = nc
                    heapq.heappush(heaps[l], (-nc,) + pair)
        pair_words.pop(best, None)
        for l in langs:
            pc[l].pop(best, None)
            deltas[l].append(step_delta[l])
        order.append(target)

        if (step + 1) % log_every == 0:
            f = {l: T[l] / W[l] for l in langs}
            print(f"  V={step + 257:>6}  " +
                  "  ".join(f"{l}={f[l]:.3f}" for l in langs) +
                  f"   ({time.time() - t_start:.0f}s)", flush=True)

    return {"merges": merges, "vocab": vocab, "deltas": deltas, "order": order,
            "T0": T0, "W": W, "urgency": urgency, "freeze": freeze}


if __name__ == "__main__":
    import sys
    smoke = "--smoke" in sys.argv
    size = 2000 if smoke else VOCAB_SIZE
    texts = load_texts()
    print(f"feedback-BPE training to vocab {size} ...")
    out = train_feedback(texts, vocab_size=size)
    fert = {l: (out["T0"][l] - sum(out["deltas"][l])) / out["W"][l] for l in LANGS}
    fed = collections.Counter(out["order"])
    print("final fertilities:", {l: round(fert[l], 4) for l in LANGS})
    print("merges fed to    :", dict(fed))
    if not smoke:
        path = os.path.join(HERE, "train20k.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"merges": [[a, b] for a, b in out["merges"]],
                       "deltas": out["deltas"], "order": "".join(out["order"]),
                       "T0": out["T0"], "W": out["W"],
                       "urgency": out["urgency"], "freeze": out["freeze"]},
                      f, ensure_ascii=False)
        print(f"wrote {path} ({os.path.getsize(path):,} bytes)")
